"""
Database Manager Service

Manages multiple openLCA database connections via IPC.
Each database runs on a separate openLCA instance with different port.

Architecture:
- Multiple IPC clients, one per database
- Route requests to appropriate client based on database_id
- Track database status and capabilities
"""

from typing import Dict, List, Optional
import olca_ipc as ipc
from enum import Enum
from dataclasses import dataclass
import json
from pathlib import Path
import logging
import socket
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Database classification"""
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"


@dataclass
class DatabaseConfig:
    """Configuration for a database connection"""
    id: str  # Unique identifier (e.g., "elcd", "ecoinvent_39")
    name: str  # Display name
    host: str
    port: int
    db_type: DatabaseType
    description: str
    requires_license: bool
    license_info: Optional[str] = None
    capabilities: Optional[List[str]] = None  # e.g., ["ReCiPe2016", "CML"]


class DatabaseManager:
    """
    Manages multiple openLCA database connections.

    Each database is accessed via a separate IPC client connection.
    Databases can run on different ports or different hosts.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            config_path: Path to databases.json config file
        """
        self.databases: Dict[str, DatabaseConfig] = {}
        self.clients: Dict[str, ipc.Client] = {}
        self.config_path = config_path

        # Load configuration if path provided
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: str):
        """
        Load database configurations from JSON file.

        Args:
            config_path: Path to databases.json
        """
        try:
            path = Path(config_path)
            if not path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return

            with open(path, 'r') as f:
                config_data = json.load(f)

            for db_config in config_data.get("databases", []):
                self.register_database(DatabaseConfig(
                    id=db_config["id"],
                    name=db_config["name"],
                    host=db_config["host"],
                    port=db_config["port"],
                    db_type=DatabaseType(db_config["db_type"]),
                    description=db_config["description"],
                    requires_license=db_config["requires_license"],
                    license_info=db_config.get("license_info"),
                    capabilities=db_config.get("capabilities", [])
                ))

            logger.info(f"Loaded {len(self.databases)} database configurations")

        except Exception as e:
            logger.error(f"Failed to load database config: {e}")

    def register_database(self, config: DatabaseConfig):
        """
        Register a new database connection.

        Args:
            config: Database configuration
        """
        self.databases[config.id] = config
        logger.info(f"Registered database: {config.id} ({config.name})")

    def get_client(self, database_id: str) -> ipc.Client:
        """
        Get or create IPC client for database.

        Args:
            database_id: Database identifier

        Returns:
            IPC client connected to database

        Raises:
            ValueError: If database_id not found
            ConnectionError: If unable to connect
        """
        if database_id not in self.databases:
            raise ValueError(f"Unknown database: {database_id}")

        # Return existing client if available
        if database_id in self.clients:
            return self.clients[database_id]

        # Create new client
        config = self.databases[database_id]
        endpoint = f"http://{config.host}:{config.port}"

        try:
            client = ipc.Client(endpoint)
            self.clients[database_id] = client
            logger.info(f"Connected to database {database_id} at {endpoint}")
            return client

        except Exception as e:
            logger.error(f"Failed to connect to {database_id}: {e}")
            raise ConnectionError(f"Cannot connect to database {database_id} at {endpoint}")

    def check_database_availability(self, database_id: str, timeout: float = 0.5) -> bool:
        """
        Check if database is available and connected.

        Uses a quick socket connection test with timeout to avoid hanging.

        Args:
            database_id: Database identifier
            timeout: Connection timeout in seconds (default: 0.5)

        Returns:
            True if database is reachable, False otherwise
        """
        if database_id not in self.databases:
            return False

        config = self.databases[database_id]

        # Quick socket connection test
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((config.host, config.port))
            sock.close()
            return result == 0
        except:
            return False

    def list_databases(self) -> List[Dict]:
        """
        List all registered databases with status.

        Returns:
            List of database information dictionaries
        """
        result = []
        for db_id, config in self.databases.items():
            db_info = {
                "id": db_id,
                "name": config.name,
                "type": config.db_type.value,
                "requires_license": config.requires_license,
                "available": self.check_database_availability(db_id),
                "description": config.description,
                "host": config.host,
                "port": config.port
            }

            if config.capabilities:
                db_info["capabilities"] = config.capabilities

            if config.requires_license and config.license_info:
                db_info["license_info"] = config.license_info

            result.append(db_info)

        return result

    def get_database_info(self, database_id: str) -> Dict:
        """
        Get detailed information about a specific database.

        Args:
            database_id: Database identifier

        Returns:
            Database information dictionary

        Raises:
            ValueError: If database_id not found
        """
        if database_id not in self.databases:
            raise ValueError(f"Unknown database: {database_id}")

        config = self.databases[database_id]
        available = self.check_database_availability(database_id)

        info = {
            "id": database_id,
            "name": config.name,
            "type": config.db_type.value,
            "requires_license": config.requires_license,
            "available": available,
            "description": config.description,
            "host": config.host,
            "port": config.port,
            "endpoint": f"http://{config.host}:{config.port}"
        }

        if config.capabilities:
            info["capabilities"] = config.capabilities

        if config.license_info:
            info["license_info"] = config.license_info

        # If available, get process count
        if available:
            try:
                client = self.get_client(database_id)
                processes = client.get_descriptors(ipc.o.Process)
                info["process_count"] = len(processes)
            except:
                pass

        return info

    def search_processes(
        self,
        query: str,
        database_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search processes in a specific database.

        Args:
            query: Search query string
            database_id: Database to search in
            limit: Maximum number of results

        Returns:
            List of matching processes
        """
        client = self.get_client(database_id)
        all_processes = client.get_descriptors(ipc.o.Process)

        query_lower = query.lower()
        matches = []

        for proc in all_processes:
            if query_lower in proc.name.lower():
                matches.append({
                    "id": proc.id,
                    "name": proc.name,
                    "database": database_id,
                    "database_name": self.databases[database_id].name,
                    "category": proc.category if hasattr(proc, 'category') else None
                })

                if len(matches) >= limit:
                    break

        return matches

    def search_product_systems(
        self,
        query: str,
        database_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search product systems in a specific database.

        Args:
            query: Search query string
            database_id: Database to search in
            limit: Maximum number of results

        Returns:
            List of matching product systems
        """
        client = self.get_client(database_id)
        all_systems = client.get_descriptors(ipc.o.ProductSystem)

        query_lower = query.lower()
        matches = []

        for system in all_systems:
            if query_lower in system.name.lower():
                matches.append({
                    "id": system.id,
                    "name": system.name,
                    "database": database_id,
                    "database_name": self.databases[database_id].name,
                    "category": system.category if hasattr(system, 'category') else None
                })

                if len(matches) >= limit:
                    break

        return matches

    def search_across_databases(
        self,
        query: str,
        database_ids: Optional[List[str]] = None,
        limit_per_db: int = 20
    ) -> Dict[str, List]:
        """
        Search processes across multiple databases.

        Args:
            query: Search query string
            database_ids: List of database IDs to search (None = search all)
            limit_per_db: Maximum results per database

        Returns:
            Dictionary mapping database_id to list of results
        """
        if database_ids is None:
            database_ids = list(self.databases.keys())

        results = {}
        for db_id in database_ids:
            try:
                matches = self.search_processes(query, db_id, limit_per_db)
                results[db_id] = {
                    "count": len(matches),
                    "results": matches,
                    "database_name": self.databases[db_id].name
                }
            except Exception as e:
                logger.error(f"Error searching {db_id}: {e}")
                results[db_id] = {
                    "error": str(e),
                    "count": 0,
                    "results": []
                }

        return results

    def get_impact_methods(self, database_id: str) -> List[Dict]:
        """
        Get all LCIA methods available in a specific database.

        Args:
            database_id: Database identifier

        Returns:
            List of impact method dictionaries with id, name, description

        Raises:
            ValueError: If database_id not found
            ConnectionError: If unable to connect to database
        """
        client = self.get_client(database_id)
        methods = client.get_descriptors(ipc.o.ImpactMethod)

        return [
            {
                "id": method.id,
                "name": method.name,
                "description": getattr(method, 'description', None),
                "database_id": database_id,
                "database_name": self.databases[database_id].name
            }
            for method in methods
        ]

    def get_method_details(self, database_id: str, method_id: str) -> Dict:
        """
        Get detailed information about a specific LCIA method.

        Args:
            database_id: Database identifier
            method_id: Impact method UUID

        Returns:
            Dictionary with detailed method information

        Raises:
            ValueError: If database_id not found
            ConnectionError: If unable to connect to database
        """
        client = self.get_client(database_id)

        try:
            # Get full method object
            method = client.get(ipc.o.ImpactMethod, method_id)

            # Extract impact categories
            categories = []
            if hasattr(method, 'impact_categories') and method.impact_categories:
                for cat in method.impact_categories:
                    categories.append({
                        "id": cat.id if hasattr(cat, 'id') else None,
                        "name": cat.name if hasattr(cat, 'name') else str(cat),
                        "ref_unit": cat.ref_unit if hasattr(cat, 'ref_unit') else None
                    })

            return {
                "id": method.id,
                "name": method.name,
                "description": getattr(method, 'description', None),
                "version": getattr(method, 'version', None),
                "database_id": database_id,
                "database_name": self.databases[database_id].name,
                "impact_categories": categories,
                "category_count": len(categories)
            }
        except Exception as e:
            logger.error(f"Failed to get method details for {method_id}: {e}")
            raise

    def get_method_knowledge(self) -> Dict:
        """
        Load LCIA method knowledge base from JSON file.

        Returns:
            Dictionary containing method metadata, guidance, and recommendations

        Raises:
            FileNotFoundError: If knowledge file doesn't exist
        """
        knowledge_path = Path(__file__).parent.parent / "knowledge" / "lcia_methods.json"

        try:
            with open(knowledge_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Method knowledge file not found: {knowledge_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load method knowledge: {e}")
            raise

    def get_database_guidance(self) -> Dict:
        """
        Load database guidance knowledge base from JSON file.

        Returns:
            Dictionary containing database metadata, guidance, and recommendations

        Raises:
            FileNotFoundError: If knowledge file doesn't exist
        """
        knowledge_path = Path(__file__).parent.parent / "knowledge" / "databases_guidance.json"

        try:
            with open(knowledge_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Database guidance file not found: {knowledge_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load database guidance: {e}")
            raise

    def recommend_method(self, database_id: str, region: Optional[str] = None,
                        sector: Optional[str] = None) -> Dict:
        """
        Recommend appropriate LCIA method based on database, region, and sector.

        Args:
            database_id: Database identifier
            region: Geographic region (e.g., "Europe", "United States", "Global")
            sector: Industry sector (e.g., "Food and Agriculture", "Energy")

        Returns:
            Dictionary with recommended method and reasoning

        Raises:
            ValueError: If database_id not found
        """
        if database_id not in self.databases:
            raise ValueError(f"Unknown database: {database_id}")

        try:
            knowledge = self.get_method_knowledge()
            guidance = knowledge.get("selection_guidance", {})

            # Get database-specific recommendations
            by_database = guidance.get("by_database", {}).get(database_id, {})
            preferred_methods = by_database.get("preferred_methods", [])
            db_reasoning = by_database.get("reasoning", "")

            # If no specific recommendation, use defaults
            if not preferred_methods:
                default_method = knowledge.get("default_method", {})
                return {
                    "recommended_method_name": default_method.get("name", "ReCiPe 2016 Midpoint (H)"),
                    "reasoning": default_method.get("reasoning", "Global comprehensive method"),
                    "alternatives": []
                }

            # Primary recommendation
            primary = preferred_methods[0]
            alternatives = preferred_methods[1:] if len(preferred_methods) > 1 else []

            return {
                "recommended_method_name": primary,
                "reasoning": db_reasoning,
                "alternatives": alternatives,
                "region_match": region in guidance.get("by_region", {}) if region else False,
                "sector_match": sector in guidance.get("by_sector", {}) if sector else False
            }

        except Exception as e:
            logger.error(f"Failed to recommend method: {e}")
            # Fallback recommendation
            return {
                "recommended_method_name": "ReCiPe 2016 Midpoint (H)",
                "reasoning": "Default comprehensive global method",
                "alternatives": []
            }

    def close_all(self):
        """Close all database connections."""
        for db_id, client in self.clients.items():
            try:
                # IPC clients don't have explicit close method
                # Just clear the reference
                logger.info(f"Closing connection to {db_id}")
            except Exception as e:
                logger.error(f"Error closing {db_id}: {e}")

        self.clients.clear()
