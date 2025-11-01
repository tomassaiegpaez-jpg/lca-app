"""
OpenLCA Service
Handles all interactions with OpenLCA via IPC protocol

This service uses the olca-ipc Python package for communication with OpenLCA.
API Documentation: https://greendelta.github.io/openLCA-ApiDoc/
Python Client Docs: https://greendelta.github.io/olca-ipc.py/

Requirements:
- openLCA >= 2.0 with IPC Server enabled
- olca-ipc Python package (works with openLCA 2.x)
- Python >= 3.11
"""
import os
import logging
import olca_ipc as ipc
import olca_schema as o
from olca_schema import RefType
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path

load_dotenv('../.env')

# ISO 14040/14044 Compliant Data Structures

@dataclass
class FunctionalUnit:
    """
    ISO 14044:2006 Section 4.2.3.2 - Functional Unit Definition

    The functional unit defines the quantification of the identified functions (performance
    characteristics) of the product system. It provides a reference to which the inputs and
    outputs are related.
    """
    description: str  # e.g., "Production and delivery of 1 kg of glass fiber composite"
    quantified_performance: str  # What function does the product provide?
    reference_flow: str  # The flow that delivers this function
    amount: float
    unit: str

@dataclass
class SystemBoundary:
    """
    ISO 14044:2006 Section 4.2.3.3 - System Boundary Definition

    The system boundary determines which unit processes shall be included within the LCA.
    """
    description: str  # Description of what is included/excluded
    cut_off_criteria: str  # Rules for excluding inputs/outputs
    included_processes: List[str]  # List of included process types
    excluded_processes: List[str]  # List of excluded processes and rationale

@dataclass
class DataQuality:
    """
    ISO 14044:2006 Section 4.2.3.6 - Data Quality Requirements

    Requirements for data quality shall be specified to enable the goal and scope to be met.
    """
    temporal_coverage: str  # Time period of data (e.g., "2020-2023")
    geographical_coverage: str  # Geographic area (e.g., "European Union")
    technological_coverage: str  # Technology represented (e.g., "Average European technology")
    precision: str  # Statistical variation (e.g., "±10%")
    completeness: str  # % of data collected vs required (e.g., "95%")
    representativeness: str  # Degree data reflects true population
    consistency: str  # Applied methodology uniformity
    reproducibility: str  # Can results be reproduced?
    data_sources: List[str]  # List of data sources
    uncertainty_assessment: Optional[str] = None

@dataclass
class GoalAndScope:
    """
    ISO 14044:2006 Section 4.2 - Goal and Scope Definition

    The goal and scope of an LCA shall be clearly defined and shall be consistent with
    the intended application.
    """
    # Study identification
    study_id: str  # Unique identifier for this study
    created_at: str  # ISO format timestamp
    updated_at: str  # ISO format timestamp

    # Goal definition (ISO 14044:2006 Section 4.2.2)
    study_goal: str  # Intended application
    reasons_for_study: str  # Why is the study being conducted?
    intended_audience: str  # To whom are results communicated?

    # Scope definition (ISO 14044:2006 Section 4.2.3)
    functional_unit: FunctionalUnit
    system_boundary: SystemBoundary
    data_quality_requirements: DataQuality

    # Additional scope elements
    assumptions: List[str]  # Key assumptions made
    limitations: List[str]  # Limitations of the study
    allocation_rules: List[str]  # How co-products are handled

    # Impact assessment method
    impact_method: str  # LCIA method used (e.g., "ILCD 2011 Midpoint")

    # Fields with defaults must come last
    comparative_assertion: bool = False  # Will results be used for public comparative assertions?

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoalAndScope':
        """Create from dictionary"""
        # Convert nested structures
        data['functional_unit'] = FunctionalUnit(**data['functional_unit'])
        data['system_boundary'] = SystemBoundary(**data['system_boundary'])
        data['data_quality_requirements'] = DataQuality(**data['data_quality_requirements'])
        return cls(**data)

class OpenLCAService:
    """Service class for OpenLCA IPC interactions"""

    def __init__(self):
        self.host = os.getenv('OPENLCA_HOST', 'localhost')
        self.port = int(os.getenv('OPENLCA_PORT', 8080))
        self.endpoint = f"http://{self.host}:{self.port}"
        self._client = None

    @property
    def client(self) -> ipc.Client:
        """Lazy initialization of IPC client"""
        if self._client is None:
            self._client = ipc.Client(self.endpoint)
        return self._client

    def _extract_name(self, obj: Any) -> Optional[str]:
        """
        Helper to extract name from an object or return string as-is

        Args:
            obj: Object that may have a name attribute, or is already a string

        Returns:
            Name string or None
        """
        if obj is None:
            return None
        if isinstance(obj, str):
            return obj
        if hasattr(obj, 'name'):
            return obj.name
        return str(obj)

    def check_connection(self) -> Dict[str, Any]:
        """
        Check if OpenLCA is reachable
        Returns connection status information
        """
        try:
            # Try to get a small list of processes to verify connection
            processes = self.client.get_descriptors(ipc.o.Process)
            return {
                "connected": True,
                "endpoint": self.endpoint,
                "process_count": len(processes) if processes else 0
            }
        except Exception as e:
            return {
                "connected": False,
                "endpoint": self.endpoint,
                "error": str(e)
            }

    def get_all_processes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all processes from OpenLCA database

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of process descriptors
        """
        try:
            processes = self.client.get_descriptors(ipc.o.Process)

            if not processes:
                return []

            # Convert to dictionaries
            result = []
            for proc in processes[:limit] if limit else processes:
                result.append({
                    "id": proc.id,
                    "name": proc.name,
                    "category": proc.category if hasattr(proc, 'category') else None,
                    "description": proc.description if hasattr(proc, 'description') else None
                })

            return result
        except Exception as e:
            raise Exception(f"Failed to get processes from OpenLCA: {str(e)}")

    def search_processes(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for processes by name

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching process descriptors
        """
        try:
            all_processes = self.client.get_descriptors(ipc.o.Process)

            if not all_processes:
                return []

            # Simple case-insensitive search
            query_lower = query.lower()
            matches = []

            for proc in all_processes:
                if query_lower in proc.name.lower():
                    matches.append({
                        "id": proc.id,
                        "name": proc.name,
                        "category": proc.category if hasattr(proc, 'category') else None,
                        "description": proc.description if hasattr(proc, 'description') else None
                    })

                    if len(matches) >= limit:
                        break

            return matches
        except Exception as e:
            raise Exception(f"Failed to search processes: {str(e)}")

    def search_product_systems(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for product systems by name

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching product system descriptors
        """
        try:
            all_systems = self.client.get_descriptors(ipc.o.ProductSystem)

            if not all_systems:
                return []

            # Simple case-insensitive search
            query_lower = query.lower()
            matches = []

            for system in all_systems:
                if query_lower in system.name.lower():
                    matches.append({
                        "id": system.id,
                        "name": system.name,
                        "type": "ProductSystem",
                        "category": system.category if hasattr(system, 'category') else None,
                        "description": system.description if hasattr(system, 'description') else None
                    })

                    if len(matches) >= limit:
                        break

            return matches
        except Exception as e:
            raise Exception(f"Failed to search product systems: {str(e)}")

    def get_process_details(self, process_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific process

        Args:
            process_id: The UUID of the process

        Returns:
            Detailed process information
        """
        try:
            # Get the full process object
            process = self.client.get(ipc.o.Process, process_id)

            if not process:
                raise ValueError(f"Process {process_id} not found")

            # Extract relevant information
            details = {
                "id": process.id,
                "name": process.name,
                "category": self._extract_name(process.category) if hasattr(process, 'category') else None,
                "description": process.description if hasattr(process, 'description') else None,
                "process_type": self._extract_name(process.process_type) if hasattr(process, 'process_type') else None,
                "location": self._extract_name(process.location) if hasattr(process, 'location') else None,
                "last_change": process.last_change if hasattr(process, 'last_change') else None,
                "version": process.version if hasattr(process, 'version') else None,
            }

            # Add exchange information (inputs/outputs)
            if hasattr(process, 'exchanges') and process.exchanges:
                details["exchanges"] = []
                for exchange in process.exchanges[:10]:  # Limit to first 10 exchanges
                    exchange_info = {
                        "flow_name": self._extract_name(exchange.flow) if hasattr(exchange, 'flow') else "Unknown",
                        "amount": exchange.amount if hasattr(exchange, 'amount') else None,
                        "unit": self._extract_name(exchange.unit) if hasattr(exchange, 'unit') else None,
                        "is_input": exchange.is_input if hasattr(exchange, 'is_input') else None,
                    }
                    details["exchanges"].append(exchange_info)
                details["total_exchanges"] = len(process.exchanges)

            return details
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Failed to get process details: {str(e)}")

    def get_categories(self) -> List[Dict[str, str]]:
        """
        Get all process categories

        Returns:
            List of category information
        """
        try:
            processes = self.client.get_descriptors(ipc.o.Process)

            # Extract unique categories
            categories = set()
            for proc in processes:
                if hasattr(proc, 'category') and proc.category:
                    categories.add(proc.category)

            return [{"name": cat} for cat in sorted(categories)]
        except Exception as e:
            raise Exception(f"Failed to get categories: {str(e)}")

    def get_impact_methods(self) -> List[Dict[str, str]]:
        """
        Get all available LCIA methods

        Returns:
            List of impact method information
        """
        try:
            methods = self.client.get_descriptors(ipc.o.ImpactMethod)

            return [
                {
                    "id": method.id,
                    "name": method.name,
                    "description": method.description if hasattr(method, 'description') else None
                }
                for method in methods
            ]
        except Exception as e:
            raise Exception(f"Failed to get impact methods: {str(e)}")

    def find_or_create_product_system(self, process_id: str) -> Dict[str, Any]:
        """
        Find existing product system or create one from a process

        Uses the client.create_product_system() method with auto-linking.
        See: https://greendelta.github.io/olca-ipc.py/olca/ipc.html#Client.create_product_system

        Args:
            process_id: UUID of the process

        Returns:
            Dict with product system info and whether it was created

        Raises:
            ValueError: If process not found or product system creation fails
            Exception: For other errors during creation
        """
        logging.info(f"Finding or creating product system for process {process_id}")

        # First check if product systems already exist for this process
        all_systems = self.client.get_descriptors(ipc.o.ProductSystem)

        # Look for product system referencing this process
        for system in all_systems:
            # Get full product system to check reference process
            full_system = self.client.get(ipc.o.ProductSystem, system.id)
            if hasattr(full_system, 'process') and full_system.process:
                if full_system.process.id == process_id:
                    # Validate existing system
                    process_count = len(full_system.processes) if hasattr(full_system, 'processes') else 1
                    logging.info(f"Found existing product system '{system.name}' with {process_count} processes")
                    return {
                        "id": system.id,
                        "name": system.name,
                        "created": False,
                        "mode": "existing",
                        "process_count": process_count
                    }

        # No existing system found, try to create one with auto-linking
        process = self.client.get(ipc.o.Process, process_id)
        if not process:
            raise ValueError(f"Process {process_id} not found in database")

        logging.info(f"Creating product system for process '{process.name}' with auto-linking (prefer default providers)")

        # Use create_product_system to auto-link
        # API signature: create_product_system(process: Ref | Process, config: LinkingConfig)
        # See: https://greendelta.github.io/olca-ipc.py/olca/ipc.html#Client.create_product_system
        try:
            # Create process reference
            process_ref = o.Ref(id=process_id, ref_type=RefType.Process)

            # Create linking configuration
            from olca_schema import LinkingConfig, ProviderLinking
            linking_config = LinkingConfig(
                provider_linking=ProviderLinking.PREFER_DEFAULTS,
                prefer_unit_processes=True
            )

            new_system_ref = self.client.create_product_system(
                process=process_ref,
                config=linking_config
            )
        except AttributeError as e:
            # Handle potential API version mismatch
            raise Exception(
                f"Error calling create_product_system: {e}. "
                "Ensure openLCA >= 2.0 and olca-ipc package is up to date. "
                "See: https://greendelta.github.io/olca-ipc.py/"
            )

        if not new_system_ref or not new_system_ref.id:
            raise ValueError(
                f"Failed to create product system for process '{process.name}'. "
                f"The process may have incomplete input/output definitions or missing upstream processes. "
                f"Try searching for existing product systems instead, or create one manually in openLCA desktop."
            )

        # Validate the created product system
        logging.info(f"Product system created with ID {new_system_ref.id}, validating...")

        try:
            full_system = self.client.get(ipc.o.ProductSystem, new_system_ref.id)
            process_count = len(full_system.processes) if hasattr(full_system, 'processes') else 1

            if process_count == 1:
                logging.warning(
                    f"Product system '{new_system_ref.name}' created but has only 1 process. "
                    f"No upstream processes were linked. Results will only include direct impacts."
                )
                mode = "single_process"
            else:
                logging.info(f"Product system successfully created with {process_count} linked processes")
                mode = "auto_linked"

            return {
                "id": new_system_ref.id,
                "name": new_system_ref.name,
                "created": True,
                "mode": mode,
                "process_count": process_count
            }

        except Exception as e:
            logging.error(f"Failed to validate created product system: {e}")
            # System was created but validation failed - still return it
            return {
                "id": new_system_ref.id,
                "name": new_system_ref.name,
                "created": True,
                "mode": "auto_linked",
                "process_count": None
            }

    def _create_simple_product_system(self, process) -> Any:
        """
        Manually create a simple single-process product system

        Args:
            process: The process object

        Returns:
            Created product system or None
        """
        try:
            # Find the quantitative reference (main output)
            ref_exchange = None
            for exchange in process.exchanges:
                if hasattr(exchange, 'quantitative_reference') and exchange.quantitative_reference:
                    ref_exchange = exchange
                    break

            if not ref_exchange:
                # If no explicit reference, use first output
                for exchange in process.exchanges:
                    if not exchange.is_input:
                        ref_exchange = exchange
                        break

            if not ref_exchange:
                return None

            # Create a minimal product system
            product_system = o.ProductSystem()
            product_system.name = f"{process.name} (Simple System)"
            product_system.process = o.Ref(id=process.id, ref_type=RefType.Process)
            product_system.ref_exchange = o.Ref(id=ref_exchange.id, ref_type=RefType.Exchange)
            product_system.target_amount = 1.0

            if hasattr(ref_exchange, 'flow_property'):
                product_system.target_flow_property = ref_exchange.flow_property

            if hasattr(ref_exchange, 'unit'):
                product_system.target_unit = ref_exchange.unit

            # Insert the product system into the database
            created_system = self.client.insert(product_system)

            return created_system

        except Exception as e:
            import traceback
            print(f"Failed to create simple product system: {e}")
            print("Full traceback:")
            traceback.print_exc()
            return None

    def calculate_lcia(
        self,
        process_id: str,
        impact_method_id: Optional[str] = None,
        amount: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate LCIA for a process by creating a product system with auto-linking

        Creates or finds a product system for the process, then calculates LCIA.
        Uses result.get_total_impacts() to retrieve impact assessment results.
        See: https://greendelta.github.io/olca-ipc.py/olca/ipc.html#Result

        Args:
            process_id: UUID of the process
            impact_method_id: UUID of impact method (uses ReCiPe 2016 Midpoint (H) if None)
            amount: Functional unit amount

        Returns:
            LCIA results with impact categories and values

        Raises:
            ValueError: If process or impact method not found, or product system creation fails
            Exception: For calculation or API errors
        """
        # Get or find default impact method
        if impact_method_id is None:
            methods = self.client.get_descriptors(ipc.o.ImpactMethod)
            recipe_method = next(
                (m for m in methods if "ReCiPe 2016 Midpoint (H)" in m.name),
                None
            )
            if recipe_method:
                impact_method_id = recipe_method.id
            else:
                # Fallback to first available method
                impact_method_id = methods[0].id if methods else None

        if not impact_method_id:
            raise ValueError("No impact method available in database")

        # Get or create product system (will raise exception if fails)
        ps_info = self.find_or_create_product_system(process_id)

        calculation_mode = ps_info["mode"]
        process_count = ps_info.get("process_count")

        logging.info(
            f"Calculating LCIA for product system '{ps_info['name']}' "
            f"(mode: {calculation_mode}, processes: {process_count})"
        )

        # Setup calculation
        setup = o.CalculationSetup()
        setup.target = o.Ref(id=ps_info["id"], ref_type=RefType.ProductSystem)
        setup.impact_method = o.Ref(id=impact_method_id, ref_type=RefType.ImpactMethod)
        setup.amount = amount

        result = self.client.calculate(setup)
        result.wait_until_ready()

        # Get impact results using result.get_total_impacts() method
        try:
            impacts = result.get_total_impacts()
        except Exception as e:
            # Dispose result before re-raising
            result.dispose()
            raise Exception(
                f"Failed to retrieve LCIA results: {e}. "
                "Ensure impact method is compatible with openLCA version."
            )

        impact_results = []
        if impacts:
            for impact in impacts:
                impact_results.append({
                    "category": impact.impact_category.name if hasattr(impact.impact_category, 'name') else "Unknown",
                    "amount": impact.amount if hasattr(impact, 'amount') else 0,
                    "unit": impact.impact_category.ref_unit if hasattr(impact.impact_category, 'ref_unit') else ""
                })

        # Dispose of result to prevent memory leaks
        result.dispose()

        # Get functional unit details from product system
        ps_full = self.client.get(ipc.o.ProductSystem, ps_info["id"])
        functional_unit_text = f"{amount} kg"  # default
        if hasattr(ps_full, 'target_unit') and ps_full.target_unit:
            unit_name = ps_full.target_unit.name if hasattr(ps_full.target_unit, 'name') else "unit"
            functional_unit_text = f"{amount} {unit_name}"

        # Extract diagram data for visualization
        diagram_data = self._extract_diagram_data(ps_full)

        result_data = {
            "process_id": process_id,
            "calculation_mode": calculation_mode,
            "product_system": ps_info["name"],
            "product_system_id": ps_info["id"],
            "impact_method": self._get_method_name(impact_method_id),
            "functional_unit": amount,
            "functional_unit_text": functional_unit_text,
            "impacts": impact_results,
            "diagram": diagram_data
        }

        # Add warning if only single process (incomplete supply chain)
        if process_count == 1:
            result_data["warning"] = (
                "⚠️ Product system has only 1 process - no upstream processes were linked. "
                "Results show direct impacts only, not full supply chain. "
                "Consider searching for existing product systems for more complete results."
            )

        logging.info(f"LCIA calculation complete: {len(impact_results)} impact categories")

        return result_data

    def calculate_lcia_from_product_system(
        self,
        product_system_id: str,
        impact_method_id: Optional[str] = None,
        amount: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate LCIA directly from a product system

        Args:
            product_system_id: UUID of the product system
            impact_method_id: UUID of impact method (uses ReCiPe 2016 Midpoint (H) if None)
            amount: Functional unit amount

        Returns:
            LCIA results with impact categories and values
        """
        import traceback
        try:
            # Get or find default impact method
            if impact_method_id is None:
                methods = self.client.get_descriptors(ipc.o.ImpactMethod)
                recipe_method = next(
                    (m for m in methods if "ReCiPe 2016 Midpoint (H)" in m.name),
                    None
                )
                if recipe_method:
                    impact_method_id = recipe_method.id
                else:
                    # Fallback to first available method
                    impact_method_id = methods[0].id if methods else None

            if not impact_method_id:
                raise ValueError("No impact method available")

            # Get product system name for response
            product_system = self.client.get(ipc.o.ProductSystem, product_system_id)
            if not product_system:
                raise ValueError(f"Product system {product_system_id} not found")

            # Setup calculation with product system
            setup = o.CalculationSetup()
            setup.target = o.Ref(id=product_system_id, ref_type=RefType.ProductSystem)
            setup.impact_method = o.Ref(id=impact_method_id, ref_type=RefType.ImpactMethod)
            setup.amount = amount

            # Run calculation
            result = self.client.calculate(setup)
            result.wait_until_ready()

            # Get impact results using result.get_total_impacts() method
            try:
                impacts = result.get_total_impacts()
            except Exception as e:
                # Dispose result before re-raising
                result.dispose()
                raise Exception(
                    f"Failed to retrieve LCIA results: {e}. "
                    "Ensure impact method is compatible with openLCA version."
                )

            impact_results = []
            if impacts:
                for impact in impacts:
                    impact_results.append({
                        "category": impact.impact_category.name if hasattr(impact.impact_category, 'name') else "Unknown",
                        "amount": impact.amount if hasattr(impact, 'amount') else 0,
                        "unit": impact.impact_category.ref_unit if hasattr(impact.impact_category, 'ref_unit') else ""
                    })

            # Dispose of result to prevent memory leaks
            result.dispose()

            # Get functional unit details from product system
            functional_unit_text = f"{amount} kg"  # default
            if hasattr(product_system, 'target_unit') and product_system.target_unit:
                unit_name = product_system.target_unit.name if hasattr(product_system.target_unit, 'name') else "unit"
                functional_unit_text = f"{amount} {unit_name}"

            # Extract diagram data for visualization
            diagram_data = self._extract_diagram_data(product_system)

            return {
                "product_system_id": product_system_id,
                "calculation_mode": "product_system",
                "product_system": product_system.name,
                "impact_method": self._get_method_name(impact_method_id),
                "functional_unit": amount,
                "functional_unit_text": functional_unit_text,
                "impacts": impact_results,
                "diagram": diagram_data
            }

        except Exception as e:
            print(f"Failed to calculate LCIA from product system: {e}")
            print("Full traceback:")
            traceback.print_exc()
            raise Exception(f"Failed to calculate LCIA from product system: {str(e)}")

    def _get_method_name(self, method_id: str) -> str:
        """Get impact method name by ID"""
        try:
            method = self.client.get(ipc.o.ImpactMethod, method_id)
            return method.name if method else "Unknown"
        except:
            return "Unknown"

    def _extract_diagram_data(self, product_system: Any) -> Dict[str, Any]:
        """
        Extract process network data for diagram visualization

        Args:
            product_system: Full ProductSystem object from openLCA

        Returns:
            Dict with nodes, edges, and metadata for diagram rendering
        """
        try:
            # Build process map and nodes list
            process_map = {}
            nodes = []

            if hasattr(product_system, 'processes') and product_system.processes:
                for proc_ref in product_system.processes:
                    proc_id = proc_ref.id if hasattr(proc_ref, 'id') else None
                    proc_name = proc_ref.name if hasattr(proc_ref, 'name') else 'Unknown'

                    if proc_id:
                        process_map[proc_id] = proc_name

                        # Determine if this is the reference process
                        is_reference = False
                        if hasattr(product_system, 'ref_process') and product_system.ref_process:
                            is_reference = (proc_id == product_system.ref_process.id)

                        nodes.append({
                            "id": proc_id,
                            "label": proc_name,
                            "type": "reference" if is_reference else "process"
                        })

            # Build edges from process links
            edges = []

            if hasattr(product_system, 'process_links') and product_system.process_links:
                for link in product_system.process_links:
                    recipient_id = None
                    provider_id = None
                    flow_name = 'Unknown'

                    # Extract recipient ID
                    if hasattr(link, 'process') and link.process:
                        recipient_id = link.process.id if hasattr(link.process, 'id') else None

                    # Extract provider ID
                    if hasattr(link, 'provider') and link.provider:
                        provider_id = link.provider.id if hasattr(link.provider, 'id') else None

                    # Extract flow name
                    if hasattr(link, 'flow') and link.flow:
                        flow_name = link.flow.name if hasattr(link.flow, 'name') else 'Unknown'

                    if recipient_id and provider_id:
                        edges.append({
                            "from": provider_id,
                            "to": recipient_id,
                            "label": flow_name
                        })

            # Get reference process info
            reference_process_id = None
            reference_process_name = "Unknown"

            if hasattr(product_system, 'ref_process') and product_system.ref_process:
                reference_process_id = product_system.ref_process.id
                reference_process_name = process_map.get(reference_process_id, 'Unknown')

            return {
                "type": "process_network",
                "reference_process_id": reference_process_id,
                "reference_process_name": reference_process_name,
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_processes": len(nodes),
                    "total_links": len(edges),
                    "product_system_name": product_system.name if hasattr(product_system, 'name') else 'Unknown',
                    "product_system_id": product_system.id if hasattr(product_system, 'id') else None
                }
            }

        except Exception as e:
            logging.error(f"Failed to extract diagram data: {e}")
            # Return empty diagram data on error
            return {
                "type": "process_network",
                "reference_process_id": None,
                "reference_process_name": "Error",
                "nodes": [],
                "edges": [],
                "metadata": {
                    "total_processes": 0,
                    "total_links": 0,
                    "error": str(e)
                }
            }

    # ========== ISO 14040/14044 Goal & Scope Management ==========
    # ISO Integration Plan: Phase 1.1 - Goal and Scope Definition System

    def _ensure_studies_dir(self) -> Path:
        """Ensure the studies directory exists"""
        studies_dir = Path(__file__).parent.parent / "studies"
        studies_dir.mkdir(parents=True, exist_ok=True)
        return studies_dir

    def save_goal_and_scope(self, goal_scope: GoalAndScope) -> str:
        """
        Save Goal and Scope definition to JSON file

        ISO 14044:2006 Section 4.2 - Goal and scope shall be clearly defined

        Args:
            goal_scope: GoalAndScope object to save

        Returns:
            study_id of the saved study
        """
        try:
            studies_dir = self._ensure_studies_dir()

            # Update timestamp
            goal_scope.updated_at = datetime.now().isoformat()

            # Save to JSON file
            file_path = studies_dir / f"{goal_scope.study_id}.json"
            with open(file_path, 'w') as f:
                json.dump(goal_scope.to_dict(), f, indent=2)

            logging.info(f"Saved Goal & Scope for study: {goal_scope.study_id}")
            return goal_scope.study_id

        except Exception as e:
            logging.error(f"Failed to save Goal & Scope: {e}")
            raise Exception(f"Failed to save Goal & Scope: {str(e)}")

    def get_goal_and_scope(self, study_id: str) -> Optional[GoalAndScope]:
        """
        Retrieve Goal and Scope definition by study ID

        Args:
            study_id: Unique identifier for the study

        Returns:
            GoalAndScope object or None if not found
        """
        try:
            studies_dir = self._ensure_studies_dir()
            file_path = studies_dir / f"{study_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r') as f:
                data = json.load(f)

            return GoalAndScope.from_dict(data)

        except Exception as e:
            logging.error(f"Failed to load Goal & Scope: {e}")
            return None

    def list_studies(self) -> List[Dict[str, Any]]:
        """
        List all available studies

        Returns:
            List of study summaries (study_id, study_goal, created_at)
        """
        try:
            studies_dir = self._ensure_studies_dir()
            studies = []

            for file_path in studies_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    studies.append({
                        "study_id": data.get("study_id"),
                        "study_goal": data.get("study_goal"),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at")
                    })
                except Exception as e:
                    logging.warning(f"Skipping invalid study file {file_path}: {e}")
                    continue

            # Sort by updated_at (most recent first)
            studies.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return studies

        except Exception as e:
            logging.error(f"Failed to list studies: {e}")
            return []


# Singleton instance
_service_instance = None

def get_openlca_service() -> OpenLCAService:
    """Get singleton instance of OpenLCAService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = OpenLCAService()
    return _service_instance

def check_connection() -> Dict[str, Any]:
    """Helper function for health checks"""
    service = get_openlca_service()
    return service.check_connection()
