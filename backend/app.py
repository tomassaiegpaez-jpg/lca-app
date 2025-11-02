"""
FastAPI Backend for LCA Application
Connects to OpenLCA via IPC and provides REST API endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import re
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

app = FastAPI(
    title="LCA API",
    description="Life Cycle Assessment API with OpenLCA integration",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",  # localhost IP variant
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Manager
from services.database_manager import DatabaseManager

# Get config path
config_path = Path(__file__).parent / "config" / "databases.json"
db_manager = DatabaseManager(config_path=str(config_path) if config_path.exists() else None)

# Pydantic models for API requests/responses
class ProcessSummary(BaseModel):
    """Summary information for an OpenLCA process"""
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None

class ProcessDetail(BaseModel):
    """Detailed information for an OpenLCA process"""
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    process_type: Optional[str] = None
    location: Optional[str] = None

class SearchQuery(BaseModel):
    """Search query for processes"""
    query: str
    limit: Optional[int] = 50
    database_id: Optional[str] = None  # If None, use default database

class AnalysisRequest(BaseModel):
    """Request for AI-powered LCA analysis"""
    process_ids: List[str]
    analysis_type: Optional[str] = "environmental_impact"

class LCIARequest(BaseModel):
    """Request for LCIA calculation"""
    process_id: str
    impact_method_id: Optional[str] = None
    amount: Optional[float] = 1.0

class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str
    conversation_id: Optional[str] = None
    database_id: Optional[str] = "elcd"  # Default to ELCD database
    preferred_method_id: Optional[str] = None  # User-selected LCIA method (None = AI will choose)

# ISO 14040/14044 Goal & Scope Models
class FunctionalUnitModel(BaseModel):
    """ISO 14044 Section 4.2.3.2 - Functional Unit"""
    description: str
    quantified_performance: str
    reference_flow: str
    amount: float
    unit: str

class SystemBoundaryModel(BaseModel):
    """ISO 14044 Section 4.2.3.3 - System Boundary"""
    description: str
    cut_off_criteria: str
    included_processes: List[str]
    excluded_processes: List[str]

class DataQualityModel(BaseModel):
    """ISO 14044 Section 4.2.3.6 - Data Quality"""
    temporal_coverage: str
    geographical_coverage: str
    technological_coverage: str
    precision: str
    completeness: str
    representativeness: str
    consistency: str
    reproducibility: str
    data_sources: List[str]
    uncertainty_assessment: Optional[str] = None

class GoalAndScopeModel(BaseModel):
    """ISO 14044 Section 4.2 - Goal and Scope Definition"""
    study_id: str
    created_at: str
    updated_at: str
    study_goal: str
    reasons_for_study: str
    intended_audience: str
    comparative_assertion: bool = False
    functional_unit: FunctionalUnitModel
    system_boundary: SystemBoundaryModel
    data_quality_requirements: DataQualityModel
    assumptions: List[str]
    limitations: List[str]
    allocation_rules: List[str]
    impact_method: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "LCA API",
        "openlca_host": os.getenv("OPENLCA_HOST"),
        "openlca_port": os.getenv("OPENLCA_PORT")
    }

@app.get("/health")
async def health_check():
    """Detailed health check including OpenLCA connectivity"""
    from services.openlca_service import check_connection

    openlca_status = check_connection()

    return {
        "api": "healthy",
        "openlca": openlca_status
    }

# ============================================================================
# Process Endpoints
# ============================================================================

@app.get("/api/processes", response_model=List[ProcessSummary])
async def list_processes(limit: Optional[int] = 100):
    """
    Get list of all processes from OpenLCA

    Args:
        limit: Maximum number of processes to return (default: 100)

    Returns:
        List of process summaries
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        processes = service.get_all_processes(limit=limit)
        return processes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/processes/search", response_model=List[ProcessSummary])
async def search_processes(search_query: SearchQuery):
    """
    Search for processes by name

    Args:
        search_query: Search query with query string, optional limit, and optional database_id

    Returns:
        List of matching processes
    """
    try:
        # If database_id specified, use DatabaseManager
        if search_query.database_id:
            results = db_manager.search_processes(
                query=search_query.query,
                database_id=search_query.database_id,
                limit=search_query.limit
            )
            return results
        else:
            # Default: use existing openlca_service
            from services.openlca_service import get_openlca_service
            service = get_openlca_service()
            processes = service.search_processes(
                query=search_query.query,
                limit=search_query.limit
            )
            return processes
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/processes/{process_id}", response_model=ProcessDetail)
async def get_process(process_id: str):
    """
    Get detailed information about a specific process

    Args:
        process_id: UUID of the process

    Returns:
        Detailed process information
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        process = service.get_process_details(process_id)
        return process
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """
    Get all process categories from OpenLCA

    Returns:
        List of category names
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        categories = service.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Database Management Endpoints
# ============================================================================

@app.get("/api/databases")
async def list_databases():
    """
    List all configured openLCA databases with status.

    Returns:
        List of database configurations with availability status
    """
    try:
        databases = db_manager.list_databases()
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/databases/{database_id}")
async def get_database_info(database_id: str):
    """
    Get detailed information about a specific database.

    Args:
        database_id: Database identifier

    Returns:
        Database configuration and status information
    """
    try:
        info = db_manager.get_database_info(database_id)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/databases/{database_id}/status")
async def check_database_status(database_id: str):
    """
    Check if a database is online and accessible.

    Args:
        database_id: Database identifier

    Returns:
        Database connection status
    """
    try:
        if database_id not in db_manager.databases:
            raise HTTPException(status_code=404, detail=f"Database {database_id} not found")

        config = db_manager.databases[database_id]
        available = db_manager.check_database_availability(database_id)

        status_info = {
            "database_id": database_id,
            "connected": available,
            "endpoint": f"http://{config.host}:{config.port}"
        }

        # If available, get process count
        if available:
            try:
                client = db_manager.get_client(database_id)
                import olca_ipc as ipc
                processes = client.get_descriptors(ipc.o.Process)
                status_info["process_count"] = len(processes)
            except:
                pass

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AI Analysis Endpoints
# ============================================================================

@app.post("/api/analyze/process/{process_id}")
async def analyze_process(
    process_id: str,
    analysis_type: Optional[str] = "environmental_impact"
):
    """
    Get AI-powered analysis of a specific process

    Args:
        process_id: UUID of the process to analyze
        analysis_type: Type of analysis (default: environmental_impact)

    Returns:
        AI-generated analysis of the process
    """
    from services.openlca_service import get_openlca_service
    from services.claude_service import get_claude_service

    try:
        # Get process details from OpenLCA
        openlca_service = get_openlca_service()
        process_data = openlca_service.get_process_details(process_id)

        # Analyze with Claude
        claude_service = get_claude_service()
        analysis = claude_service.analyze_process_impact(
            process_data=process_data,
            analysis_type=analysis_type
        )

        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/compare")
async def compare_processes(analysis_request: AnalysisRequest):
    """
    Compare multiple processes using AI

    Args:
        analysis_request: Contains list of process IDs and comparison criteria

    Returns:
        AI-generated comparison of the processes
    """
    from services.openlca_service import get_openlca_service
    from services.claude_service import get_claude_service

    try:
        # Get process details for all processes
        openlca_service = get_openlca_service()
        processes_data = []

        for process_id in analysis_request.process_ids:
            process_data = openlca_service.get_process_details(process_id)
            processes_data.append(process_data)

        # Compare with Claude
        claude_service = get_claude_service()
        comparison = claude_service.compare_processes(
            processes_data=processes_data,
            comparison_criteria=analysis_request.analysis_type
        )

        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/recommend/{process_id}")
async def get_recommendations(
    process_id: str,
    goal: Optional[str] = "reduce_environmental_impact"
):
    """
    Get AI-powered recommendations for improving a process

    Args:
        process_id: UUID of the process
        goal: Optimization goal (default: reduce_environmental_impact)

    Returns:
        AI-generated recommendations
    """
    from services.openlca_service import get_openlca_service
    from services.claude_service import get_claude_service

    try:
        # Get process details from OpenLCA
        openlca_service = get_openlca_service()
        process_data = openlca_service.get_process_details(process_id)

        # Get recommendations from Claude
        claude_service = get_claude_service()
        recommendations = claude_service.get_recommendations(
            process_data=process_data,
            goal=goal
        )

        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LCIA Calculation Endpoints
# ============================================================================

@app.get("/api/impact-methods")
async def get_impact_methods():
    """
    Get all available LCIA methods from OpenLCA

    Returns:
        List of impact methods with IDs and names
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        methods = service.get_impact_methods()
        return {"methods": methods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/databases/{database_id}/methods")
async def get_database_methods(database_id: str):
    """
    Get all LCIA methods available in a specific database.

    Args:
        database_id: Database identifier

    Returns:
        List of impact methods with IDs, names, and descriptions
    """
    try:
        methods = db_manager.get_impact_methods(database_id)
        return {"methods": methods, "database_id": database_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/databases/{database_id}/methods/{method_id}")
async def get_method_details(database_id: str, method_id: str):
    """
    Get detailed information about a specific LCIA method.

    Args:
        database_id: Database identifier
        method_id: Impact method UUID

    Returns:
        Detailed method information including impact categories
    """
    try:
        details = db_manager.get_method_details(database_id, method_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/methods")
async def get_methods_knowledge():
    """
    Get LCIA methods knowledge base with metadata, guidance, and recommendations.

    Returns:
        Complete method knowledge base including pros/cons, use cases, and selection guidance
    """
    try:
        knowledge = db_manager.get_method_knowledge()
        return knowledge
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Method knowledge base not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/databases")
async def get_databases_guidance():
    """
    Get database guidance knowledge base with metadata and recommendations.

    Returns:
        Complete database guidance including strengths, limitations, and selection criteria
    """
    try:
        guidance = db_manager.get_database_guidance()
        return guidance
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Database guidance not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/databases/{database_id}/recommend-method")
async def recommend_impact_method(
    database_id: str,
    region: Optional[str] = None,
    sector: Optional[str] = None
):
    """
    Get recommended LCIA method for a database based on region and sector.

    Args:
        database_id: Database identifier
        region: Geographic region (e.g., "Europe", "United States")
        sector: Industry sector (e.g., "Food and Agriculture", "Energy")

    Returns:
        Recommended method with reasoning and alternatives
    """
    try:
        recommendation = db_manager.recommend_method(database_id, region, sector)
        return {
            "database_id": database_id,
            "recommendation": recommendation
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lca/calculate")
async def calculate_lcia(request: LCIARequest):
    """
    Calculate LCIA for a process

    Attempts full product system calculation with auto-linking.
    Falls back to direct calculation if product system cannot be created.

    Args:
        request: LCIA calculation parameters

    Returns:
        LCIA results with impact categories and values
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        results = service.calculate_lcia(
            process_id=request.process_id,
            impact_method_id=request.impact_method_id,
            amount=request.amount
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ISO 14040/14044 Goal & Scope Endpoints
# ============================================================================

@app.post("/api/goal-scope")
async def create_goal_scope(goal_scope: GoalAndScopeModel):
    """
    Create or update Goal and Scope definition for an LCA study

    ISO 14044:2006 Section 4.2 - The goal and scope of an LCA shall be
    clearly defined and shall be consistent with the intended application.

    Args:
        goal_scope: Complete Goal and Scope definition

    Returns:
        study_id of the created/updated study
    """
    from services.openlca_service import get_openlca_service, FunctionalUnit, SystemBoundary, DataQuality, GoalAndScope
    from datetime import datetime

    try:
        service = get_openlca_service()

        # Convert Pydantic models to dataclasses
        functional_unit = FunctionalUnit(
            description=goal_scope.functional_unit.description,
            quantified_performance=goal_scope.functional_unit.quantified_performance,
            reference_flow=goal_scope.functional_unit.reference_flow,
            amount=goal_scope.functional_unit.amount,
            unit=goal_scope.functional_unit.unit
        )

        system_boundary = SystemBoundary(
            description=goal_scope.system_boundary.description,
            cut_off_criteria=goal_scope.system_boundary.cut_off_criteria,
            included_processes=goal_scope.system_boundary.included_processes,
            excluded_processes=goal_scope.system_boundary.excluded_processes
        )

        data_quality = DataQuality(
            temporal_coverage=goal_scope.data_quality_requirements.temporal_coverage,
            geographical_coverage=goal_scope.data_quality_requirements.geographical_coverage,
            technological_coverage=goal_scope.data_quality_requirements.technological_coverage,
            precision=goal_scope.data_quality_requirements.precision,
            completeness=goal_scope.data_quality_requirements.completeness,
            representativeness=goal_scope.data_quality_requirements.representativeness,
            consistency=goal_scope.data_quality_requirements.consistency,
            reproducibility=goal_scope.data_quality_requirements.reproducibility,
            data_sources=goal_scope.data_quality_requirements.data_sources,
            uncertainty_assessment=goal_scope.data_quality_requirements.uncertainty_assessment
        )

        # Create GoalAndScope dataclass
        goal_and_scope = GoalAndScope(
            study_id=goal_scope.study_id,
            created_at=goal_scope.created_at if goal_scope.created_at else datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            study_goal=goal_scope.study_goal,
            reasons_for_study=goal_scope.reasons_for_study,
            intended_audience=goal_scope.intended_audience,
            comparative_assertion=goal_scope.comparative_assertion,
            functional_unit=functional_unit,
            system_boundary=system_boundary,
            data_quality_requirements=data_quality,
            assumptions=goal_scope.assumptions,
            limitations=goal_scope.limitations,
            allocation_rules=goal_scope.allocation_rules,
            impact_method=goal_scope.impact_method
        )

        # Save to storage
        study_id = service.save_goal_and_scope(goal_and_scope)

        return {
            "success": True,
            "study_id": study_id,
            "message": "Goal and Scope definition saved successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/goal-scope/{study_id}")
async def get_goal_scope(study_id: str):
    """
    Retrieve Goal and Scope definition by study ID

    Args:
        study_id: Unique identifier for the study

    Returns:
        Complete Goal and Scope definition
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        goal_scope = service.get_goal_and_scope(study_id)

        if goal_scope is None:
            raise HTTPException(status_code=404, detail=f"Study {study_id} not found")

        return goal_scope.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/goal-scope")
async def list_studies():
    """
    List all available LCA studies

    Returns:
        List of study summaries (study_id, study_goal, created_at, updated_at)
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        studies = service.list_studies()
        return studies

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Conversational LCA Assistant
# ============================================================================

# Conversation service for managing rich conversation contexts
from services.conversation_service import ConversationService
conversation_service = ConversationService()

# Load process catalog for AI context
process_catalog = None
def load_process_catalog():
    """Load the process catalog JSON file"""
    global process_catalog
    if process_catalog is None:
        import json
        catalog_path = os.path.join(os.path.dirname(__file__), 'data', 'process_catalog.json')
        try:
            with open(catalog_path, 'r') as f:
                process_catalog = json.load(f)
        except FileNotFoundError:
            process_catalog = []
    return process_catalog

@app.post("/api/lca/chat")
async def lca_chat(chat_message: ChatMessage):
    """
    Conversational LCA assistant

    Guides user through LCA scope definition, searches for processes,
    runs LCIA calculations, and interprets results.

    Args:
        chat_message: User message and optional conversation ID

    Returns:
        AI response with potential actions (search, calculate, etc.)
    """
    from services.claude_service import get_claude_service
    from services.openlca_service import get_openlca_service

    try:
        claude_service = get_claude_service()
        openlca_service = get_openlca_service()

        # Get selected database info
        selected_db_id = chat_message.database_id or "elcd"
        selected_db_info = db_manager.get_database_info(selected_db_id)

        # Check if database is available
        if not selected_db_info["available"]:
            raise HTTPException(
                status_code=400,
                detail=f"Database '{selected_db_info['name']}' is not available. Please ensure the IPC server is running on port {selected_db_info['port']}."
            )

        # Extract chat parameters from request
        preferred_method_id = chat_message.preferred_method_id

        # Get or create conversation with rich context
        conv_id = chat_message.conversation_id
        if conv_id:
            # Existing conversation - validate it exists
            conv = conversation_service.get_conversation(conv_id)
            if not conv:
                raise HTTPException(status_code=404, detail=f"Conversation {conv_id} not found")

            # Update conversation context if database or method changed
            if conv["database_id"] != selected_db_id:
                conversation_service.update_database(
                    conv_id,
                    selected_db_id,
                    reason="User switched database"
                )

            if conv["method_id"] != preferred_method_id:
                # Determine if this is a manual change by user
                is_manual = preferred_method_id is not None
                conversation_service.update_method(
                    conv_id,
                    preferred_method_id,
                    is_manual=is_manual,
                    reason="User changed method selection" if is_manual else "Method reset to auto"
                )

        else:
            # Create new conversation
            conv_id = conversation_service.create_conversation(
                database_id=selected_db_id,
                method_id=preferred_method_id
            )

        # Add user message to conversation
        conversation_service.add_message(
            conv_id,
            role="user",
            content=chat_message.message
        )

        # Build catalog context (simplified for now - could be database-specific)
        catalog_context = f"\n\nYou have access to the **{selected_db_info['name']}** database."
        if 'process_count' in selected_db_info:
            catalog_context += f" It contains {selected_db_info['process_count']} processes."
        catalog_context += f"\n\nDescription: {selected_db_info['description']}"

        # Load knowledge bases for AI guidance
        try:
            method_knowledge = db_manager.get_method_knowledge()
            db_guidance = db_manager.get_database_guidance()
        except Exception as e:
            print(f"Warning: Could not load knowledge bases: {e}")
            method_knowledge = {}
            db_guidance = {}

        # Get available methods for selected database
        try:
            available_methods = db_manager.get_impact_methods(selected_db_id)
            method_recommendation = db_manager.recommend_method(selected_db_id)
        except Exception as e:
            print(f"Warning: Could not get methods for database: {e}")
            available_methods = []
            method_recommendation = {"recommended_method_name": "ReCiPe 2016 Midpoint (H)", "reasoning": "Default method"}

        # Build method context for AI
        method_context = "\n\n# Available LCIA Methods\n\n"
        if preferred_method_id:
            # User has selected a method - AI should use it
            selected_method = next((m for m in available_methods if m['id'] == preferred_method_id), None)
            if selected_method:
                method_context += f"**User has selected**: {selected_method['name']}\n"
                method_context += "You MUST use this method for calculations. Include it in actions:\n"
                method_context += f'ACTION: {{"type": "calculate_lcia_ps", "product_system_id": "uuid", "amount": 1.0, "method_id": "{preferred_method_id}"}}\n\n'
        else:
            # No user selection - provide AI with recommendations
            method_context += f"**Recommended for {selected_db_info['name']}**: {method_recommendation['recommended_method_name']}\n"
            method_context += f"Reasoning: {method_recommendation['reasoning']}\n\n"

            if method_recommendation.get('alternatives'):
                method_context += f"Alternatives: {', '.join(method_recommendation['alternatives'])}\n\n"

        # Add method selection guidance from knowledge base
        if method_knowledge and 'methods' in method_knowledge:
            recommended_method_name = method_recommendation['recommended_method_name']
            method_info = method_knowledge['methods'].get(recommended_method_name, {})

            if method_info:
                method_context += f"**About {recommended_method_name}**:\n"
                method_context += f"- Type: {method_info.get('type', 'N/A')}\n"
                method_context += f"- Regional focus: {method_info.get('regional_focus', 'N/A')}\n"
                if method_info.get('pros'):
                    method_context += f"- Key strengths: {'; '.join(method_info['pros'][:2])}\n"
                method_context += f"\nBest for: {', '.join(method_info.get('use_cases', [])[:3])}\n\n"

        # Add database guidance
        db_context = "\n# About This Database\n\n"
        if db_guidance and 'databases' in db_guidance:
            db_info_knowledge = db_guidance['databases'].get(selected_db_id, {})
            if db_info_knowledge:
                db_context += f"**Strengths**: {', '.join(db_info_knowledge.get('strengths', [])[:3])}\n"
                db_context += f"**Best for**: {', '.join(db_info_knowledge.get('best_for', [])[:3])}\n"
                if db_info_knowledge.get('limitations'):
                    db_context += f"**Note**: {db_info_knowledge['limitations'][0]}\n"

        # Get conversation context to inject into AI prompt
        conv_context = conversation_service.get_context_for_ai(
            conv_id,
            db_name=selected_db_info['name'],
            method_name=next((m['name'] for m in available_methods if m['id'] == preferred_method_id), None) if preferred_method_id else None
        )

        # Build unified system prompt
        def build_system_prompt():
            return f"""You are an expert Life Cycle Assessment (LCA) assistant with access to the {selected_db_info['name']} database.

{catalog_context}
{db_context}
{method_context}

{conv_context}

# Your Role

Help users perform Life Cycle Assessments through natural conversation. Ask clarifying questions when needed, but also infer reasonable information when appropriate. Be helpful, educational, and trustworthy - NEVER make up or estimate impact numbers.

# Key LCA Concepts (explain naturally when relevant)

**Functional Unit**: What the study measures (e.g., "1 kg of glass fiber mat")
**System Boundary**: What's included/excluded in the analysis
**Product System**: A network of linked processes representing a full supply chain
**Process**: A single production step

# Workflow (Follow This Strictly)

1. **Search Strategy**: ALWAYS search PRODUCT SYSTEMS first (they're ready for calculation!)
2. **Wait for Results**: Look for [Action Results: ...] in conversation history
3. **Automatic Fallback**: If product systems return [], immediately search PROCESSES
4. **Ask When Needed**: If multiple options found, ask user to choose
5. **Extract Amounts**: Pull amounts from user queries ("2kg" → amount: 2.0)
6. **Calculate**: Use calculate_lcia_ps for product systems, calculate_lcia for processes

# 🚫 CRITICAL HALLUCINATION PREVENTION 🚫

**NEVER DO THESE:**
1. ❌ Say "Here are the results:" when you haven't seen [Action Results: ...] with calculation data
2. ❌ Describe specific impact numbers (like "4.2 kg CO2-eq") unless they're in [Action Results: ...]
3. ❌ Provide "example" or "typical" values when data isn't found
4. ❌ Say "the calculation shows..." if no calculation happened
5. ❌ Claim you "calculated" or "performed LCIA" if you only searched
6. ❌ Say results are "displayed in the panel" if you didn't see calculation results

**ALWAYS DO THESE:**
1. ✅ Wait for [Action Results: ...] before describing any results
2. ✅ Be honest when searches return empty []
3. ✅ Stop after 2 consecutive empty searches - admit data not found
4. ✅ Distinguish between: "I searched" vs "I calculated" vs "Results show..."
5. ✅ Only mention numbers that appear in [Action Results: ...]

**IF SEARCHES FAIL (2 empty results []):**
- Immediately acknowledge: "I couldn't find data after searching multiple times"
- Suggest alternatives: different keywords, different database
- DO NOT continue or make up information
- Let the system handle the error gracefully

# When to Ask Questions

**ASK when:**
- Multiple search results (>1) found → Present numbered list, ask user to choose
- Amount unclear or missing → "How much would you like to assess?"
- User query is ambiguous → Ask for clarification

**DON'T ASK when:**
- Only 1 search result found → Proceed automatically
- Amount is clear in query ("2kg glass fiber") → Extract and use it
- Automatic fallback needed (PS → Processes) → Just do it
- British spelling needed → Convert silently ("fiber" → "fibre")

# Available Actions

Search for processes:
ACTION: {{"type": "search_processes", "query": "glass fibre"}}

Search for product systems:
ACTION: {{"type": "search_product_systems", "query": "glass fibre"}}

Calculate from process ID:
ACTION: {{"type": "calculate_lcia", "process_id": "uuid-here", "amount": 2.0}}

Calculate from product system ID (PREFERRED):
ACTION: {{"type": "calculate_lcia_ps", "product_system_id": "uuid-here", "amount": 1.0}}

# Critical Rules

**ONE ACTION PER MESSAGE**: Never issue multiple ACTIONs in one response
**NO PREMATURE RESULTS**: Never describe calculation results in the same message as the ACTION
**CHECK HISTORY**: Always check conversation history for [Action Results: ...] before interpreting
**BE TRUTHFUL**: Distinguish between "I'm searching", "I'm calculating", and "Results show"

# Example: Correct Interaction

User: "Calculate impact of 2kg glass fiber"

Turn 1 (You):
"I'll search for glass fibre product systems first.

ACTION: {{"type": "search_product_systems", "query": "glass fibre"}}"

[System adds: [Action Results: {{"type": "search_product_systems", "results": [{{...3 results...}}]}}]]

Turn 2 (You see 3 results):
"I found 3 glass fibre options:
1. Continuous filament glass fibre (assembled rovings) - RER
2. Continuous filament glass fibre (textile glass) - RER
3. Glass fibre reinforced plastic - GLO

Which one would you like to use for your assessment?"

[User responds: "Option 1"]

Turn 3 (You):
"Great! Calculating LCIA for 2kg of continuous filament glass fibre now.

ACTION: {{"type": "calculate_lcia_ps", "product_system_id": "xyz-789", "amount": 2.0}}"

[System adds: [Action Results: {{"type": "calculate_lcia_ps", "results": {{"impacts": [...]}}}}]]

Turn 4 (You NOW see calculation results):
"✅ Calculation complete! The impact assessment for 2kg of continuous filament glass fibre is done. Full results with 14 impact categories are displayed in the right panel →"

# Example: Automatic Fallback

User: "Impact of 1kg copper"

Turn 1 (You):
"Searching for copper product systems.

ACTION: {{"type": "search_product_systems", "query": "copper"}}"

[System adds: [Action Results: {{"type": "search_product_systems", "results": []}}]]

Turn 2 (You see empty [], automatically fallback):
"No product systems found. Searching copper processes instead.

ACTION: {{"type": "search_processes", "query": "copper"}}"

[System adds: [Action Results: {{"type": "search_processes", "results": [{{...5 results...}}]}}]]

Turn 3 (You see 5 results):
"I found 5 copper processes:
1. Copper production, primary - GLO
2. Copper tube manufacturing - RER
3. Copper wire production - RER
4. Copper sheet - GLO
5. Copper scrap recycling - EU

Which process matches your needs?"

# Example: Being Honest About Failure

[After 2 empty searches]

You: "I searched both product systems and processes but couldn't find data for 'unicorn horn' in the {selected_db_info['name']} database.

Would you like to:
- Try a different search term
- Switch to a specialized database (Agribalyse for food, NEEDS for energy)
- Search for a similar material instead"

# Search Tips

- Use BRITISH ENGLISH: "fibre" not "fiber", "aluminium" not "aluminum"
- Be specific: "glass fibre" not just "glass"
- Include region when relevant: "copper RER", "steel GLO"

# Remember

- Be helpful and ask questions when needed
- Infer reasonable information (amounts, common materials)
- NEVER make up numbers or claim you calculated when you didn't
- Always wait for [Action Results: ...] before describing results
- Distinguish: searching ≠ calculating ≠ results ready"""

        # Use unified system prompt
        system_prompt = build_system_prompt()

        # Multi-turn loop: Keep calling Claude until workflow completes or max iterations reached
        # This enables automatic fallback (e.g., product systems → processes)
        max_iterations = 5
        max_empty_searches = 2  # Stop after 2 consecutive empty searches to prevent hallucination
        empty_search_count = 0   # Track consecutive empty search results
        final_action_data = None
        all_messages = []  # Collect all AI messages for potential display

        # Debug data collection
        debug_enabled = os.getenv('DEBUG', 'false').lower() == 'true'
        debug_data = {
            "enabled": debug_enabled,
            "user_message": chat_message.message,
            "iterations": 0,
            "all_messages": [],
            "actions_executed": [],
            "timing": {
                "total_ms": 0,
                "per_iteration_ms": []
            },
            "database_context": {
                "selected_db": selected_db_id,
                "selected_db_name": selected_db_info['name'],
                "method_id": preferred_method_id,
                "method_selection_mode": "manual" if preferred_method_id else "auto"
            },
            "empty_search_progression": [],
            "system_prompt_preview": "",
            "full_conversation_history": []
        }

        loop_start_time = time.time()

        for iteration in range(max_iterations):
            iteration_start_time = time.time()
            # Prepare messages for Claude from conversation service
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_service.get_messages(conv_id)
            ]

            # Get response from Claude
            response = claude_service.client.messages.create(
                model=claude_service.model,
                max_tokens=2048,
                system=system_prompt,
                messages=messages
            )

            # Safely extract assistant message
            if not response.content or len(response.content) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="No response content from AI"
                )

            assistant_message = response.content[0].text
            all_messages.append(assistant_message)

            # Collect debug data for this iteration
            if debug_enabled:
                debug_data["all_messages"].append({
                    "iteration": iteration + 1,
                    "message": assistant_message,
                    "timestamp": time.time()
                })

            # Check if assistant wants to perform an action
            action_data = None

            if "ACTION:" not in assistant_message:
                # No action in this response - workflow complete
                iteration_time = (time.time() - iteration_start_time) * 1000
                if debug_enabled:
                    debug_data["timing"]["per_iteration_ms"].append(round(iteration_time, 2))
                    debug_data["iterations"] = iteration + 1
                break

            # Extract and perform action
            action_match = re.search(r'ACTION:\s*({[^}]+})', assistant_message)
            if not action_match:
                # No valid action found
                break

            try:
                action_data = json.loads(action_match.group(1))

                # Execute action
                if action_data["type"] == "search_processes":
                    print(f"Searching processes in {selected_db_id} for: '{action_data['query']}'")
                    search_results = db_manager.search_processes(
                        query=action_data["query"],
                        database_id=selected_db_id,
                        limit=5
                    )
                    print(f"Found {len(search_results)} results")
                    action_data["results"] = search_results

                    # Track empty searches
                    if len(search_results) == 0:
                        empty_search_count += 1
                        action_data["empty_results"] = True
                    else:
                        empty_search_count = 0  # Reset on successful search

                elif action_data["type"] == "search_product_systems":
                    print(f"Searching product systems in {selected_db_id} for: '{action_data['query']}'")
                    search_results = db_manager.search_product_systems(
                        query=action_data["query"],
                        database_id=selected_db_id,
                        limit=5
                    )
                    action_data["results"] = search_results

                    # Track empty searches
                    if len(search_results) == 0:
                        empty_search_count += 1
                        action_data["empty_results"] = True
                    else:
                        empty_search_count = 0  # Reset on successful search

                elif action_data["type"] == "calculate_lcia":
                    # NOTE: Calculations currently use openlca_service which connects to default database
                    # TODO: Refactor to use database_manager.get_client(selected_db_id)
                    print(f"WARNING: Calculation may not use selected database {selected_db_id}")

                    # Determine method_id: AI specified > User preferred > Recommended
                    method_id = action_data.get("method_id") or preferred_method_id

                    # If still None, use recommended method for this database
                    if method_id is None:
                        # Find recommended method ID by matching name (flexible matching)
                        recommended_name = method_recommendation['recommended_method_name']
                        # Try exact match first
                        matching_method = next(
                            (m for m in available_methods if m['name'] == recommended_name),
                            None
                        )
                        # If no exact match, try fuzzy matching (key parts of name)
                        if not matching_method:
                            # Extract key identifying parts (e.g., "ILCD", "2011", "ReCiPe", "2016", etc.)
                            key_parts = [part for part in recommended_name.split() if len(part) > 3 and not part.startswith('(')]
                            matching_method = next(
                                (m for m in available_methods if all(part in m['name'] for part in key_parts[:3])),
                                None
                            )
                        if matching_method:
                            method_id = matching_method['id']
                            print(f"Using recommended method: {recommended_name} -> Found: {matching_method['name']} (ID: {method_id})")
                        else:
                            print(f"WARNING: Recommended method '{recommended_name}' not found in database. Available methods: {[m['name'] for m in available_methods[:3]]}")

                    lcia_results = openlca_service.calculate_lcia(
                        action_data["process_id"],
                        impact_method_id=method_id,
                        amount=action_data.get("amount", 1.0)
                    )

                    # Construct AI-inferred Goal & Scope
                    goal_scope_data = openlca_service.construct_inferred_goal_scope(
                        user_query=chat_message.message,
                        process_or_ps_name=lcia_results.get("product_system", "Unknown process"),
                        amount=action_data.get("amount", 1.0),
                        impact_method=lcia_results.get("impact_method", "Unknown method"),
                        calculation_type="process"
                    )

                    # Merge Goal & Scope into results
                    lcia_results["goal_scope"] = goal_scope_data["goal_scope"]
                    lcia_results["goal_scope"]["iso_compliance"] = goal_scope_data["iso_compliance"]

                    # Include the actually used method_id for frontend
                    lcia_results["used_method_id"] = method_id

                    action_data["results"] = lcia_results
                    final_action_data = action_data  # Save for return

                elif action_data["type"] == "calculate_lcia_ps":
                    # Determine method_id: AI specified > User preferred > Recommended
                    method_id = action_data.get("method_id") or preferred_method_id

                    # If still None, use recommended method for this database
                    if method_id is None:
                        # Find recommended method ID by matching name (flexible matching)
                        recommended_name = method_recommendation['recommended_method_name']
                        # Try exact match first
                        matching_method = next(
                            (m for m in available_methods if m['name'] == recommended_name),
                            None
                        )
                        # If no exact match, try fuzzy matching (key parts of name)
                        if not matching_method:
                            # Extract key identifying parts (e.g., "ILCD", "2011", "ReCiPe", "2016", etc.)
                            key_parts = [part for part in recommended_name.split() if len(part) > 3 and not part.startswith('(')]
                            matching_method = next(
                                (m for m in available_methods if all(part in m['name'] for part in key_parts[:3])),
                                None
                            )
                        if matching_method:
                            method_id = matching_method['id']
                            print(f"Using recommended method: {recommended_name} -> Found: {matching_method['name']} (ID: {method_id})")
                        else:
                            print(f"WARNING: Recommended method '{recommended_name}' not found in database. Available methods: {[m['name'] for m in available_methods[:3]]}")

                    lcia_results = openlca_service.calculate_lcia_from_product_system(
                        action_data["product_system_id"],
                        impact_method_id=method_id,
                        amount=action_data.get("amount", 1.0)
                    )

                    # Construct AI-inferred Goal & Scope
                    goal_scope_data = openlca_service.construct_inferred_goal_scope(
                        user_query=chat_message.message,
                        process_or_ps_name=lcia_results.get("product_system", "Unknown product system"),
                        amount=action_data.get("amount", 1.0),
                        impact_method=lcia_results.get("impact_method", "Unknown method"),
                        calculation_type="product_system"
                    )

                    # Merge Goal & Scope into results
                    lcia_results["goal_scope"] = goal_scope_data["goal_scope"]
                    lcia_results["goal_scope"]["iso_compliance"] = goal_scope_data["iso_compliance"]

                    # Include the actually used method_id for frontend
                    lcia_results["used_method_id"] = method_id

                    action_data["results"] = lcia_results
                    final_action_data = action_data  # Save for return

            except Exception as e:
                action_data = {"error": str(e)}
                final_action_data = action_data

            # Check if we've hit max empty searches - force honest error response
            if empty_search_count >= max_empty_searches:
                query_term = action_data.get("query", "your query") if action_data else "your query"

                # Build honest error message
                error_msg = f"I searched for '{query_term}' in the {selected_db_info['name']} database but couldn't find any matching data.\n\n"
                error_msg += "**This might be because:**\n"
                error_msg += f"1. This product/material isn't available in {selected_db_info['name']}\n"
                error_msg += "2. The search terms don't match the database terminology\n"
                error_msg += "3. This type of data isn't covered by this database\n\n"

                # Add database-specific suggestions based on query
                query_lower = query_term.lower() if isinstance(query_term, str) else ""
                if any(word in query_lower for word in ["food", "tomato", "vegetable", "fruit", "agriculture", "crop", "farm"]):
                    error_msg += "**💡 Suggestion:** Try the **Agribalyse** database - it specializes in agricultural and food products.\n\n"
                elif any(word in query_lower for word in ["electricity", "energy", "power", "grid"]):
                    error_msg += "**💡 Suggestion:** Try searching for 'electricity mix' with a specific region (e.g., 'electricity mix EU').\n\n"
                elif any(word in query_lower for word in ["transport", "vehicle", "truck", "shipping", "freight"]):
                    error_msg += "**💡 Suggestion:** Try broader terms like 'transport' or 'freight'.\n\n"

                error_msg += "Would you like to try different search terms or switch to another database?"

                # Force error state to stop hallucination
                action_data = {
                    "type": "search_failed",
                    "error": error_msg,
                    "query": query_term,
                    "database": selected_db_info['name'],
                    "empty_search_count": empty_search_count
                }
                final_action_data = action_data

                # Add to conversation and break
                history_content = assistant_message
                history_content += f"\n\n[Action Results: {json.dumps(action_data, default=str)}]"
                conversation_service.add_message(
                    conv_id,
                    role="assistant",
                    content=history_content,
                    action=action_data
                )
                break

            # Track action execution for debug
            if debug_enabled and action_data:
                debug_data["actions_executed"].append({
                    "iteration": iteration + 1,
                    "action": action_data.copy(),
                    "timestamp": time.time()
                })
                debug_data["empty_search_progression"].append({
                    "iteration": iteration + 1,
                    "empty_search_count": empty_search_count
                })

            # Add this turn to conversation history with action results
            history_content = assistant_message
            if action_data:
                history_content += f"\n\n[Action Results: {json.dumps(action_data, default=str)}]"

            conversation_service.add_message(
                conv_id,
                role="assistant",
                content=history_content,
                action=action_data
            )

            # Track iteration timing
            iteration_time = (time.time() - iteration_start_time) * 1000
            if debug_enabled:
                debug_data["timing"]["per_iteration_ms"].append(round(iteration_time, 2))
                debug_data["iterations"] = iteration + 1

            # Break conditions: stop loop if calculation complete or error occurred
            if action_data and (action_data.get("type") in ["calculate_lcia", "calculate_lcia_ps"] or "error" in action_data):
                break

        # Prepare display message: use last assistant message, cleaned
        display_message = all_messages[-1] if all_messages else ""

        # Safety: Remove any [Action Results: ...] blocks that AI might have copied from history
        display_message = re.sub(r'\[Action Results:.*?\}\]\s*', '', display_message, flags=re.DOTALL)
        # Remove ACTION commands from display
        display_message = re.sub(r'\n*ACTION:\s*{[^}]+}\s*', '', display_message)
        display_message = display_message.strip()

        # Finalize debug data
        if debug_enabled:
            loop_end_time = time.time()
            debug_data["timing"]["total_ms"] = round((loop_end_time - loop_start_time) * 1000, 2)

            # Add system prompt preview (first 500 chars)
            debug_data["system_prompt_preview"] = system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt

            # Add full conversation history
            debug_data["full_conversation_history"] = [
                {
                    "role": msg["role"],
                    "content": msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"],
                    "has_action": "ACTION:" in msg.get("content", ""),
                    "has_results": "[Action Results:" in msg.get("content", "")
                }
                for msg in conversation_service.get_messages(conv_id)
            ]

            # Store debug data in conversation service
            conversation_service.add_debug_data(conv_id, debug_data)

        return {
            "conversation_id": conv_id,
            "message": display_message,  # Send cleaned message to user
            "action": final_action_data
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = f"{type(e).__name__}: {str(e)}"
        print(f"Chat endpoint error: {error_details}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_details)


@app.get("/api/debug", response_class=HTMLResponse)
async def debug_home():
    """
    Debug homepage - lists all conversations

    Returns HTML page with links to individual conversation debug pages
    """
    debug_enabled = os.getenv('DEBUG', 'false').lower() == 'true'

    if not debug_enabled:
        return HTMLResponse(content="""
        <html>
            <head><title>Debug Mode Disabled</title></head>
            <body style="font-family: monospace; padding: 20px; background-color: #1e1e1e; color: #d4d4d4;">
                <h1>⚠️ Debug Mode Disabled</h1>
                <p>Set <code>DEBUG=true</code> in <code>backend/.env</code> to enable debug mode.</p>
                <p>Then restart the backend server.</p>
            </body>
        </html>
        """, status_code=200)

    # Get all conversations
    conversations = conversation_service.list_conversations()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LCA Debug Console</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {
                font-family: 'Courier New', monospace;
                padding: 20px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            .header {
                background-color: #2d2d30;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .conversation-list {
                list-style: none;
                padding: 0;
            }
            .conversation-item {
                background-color: #252526;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 5px;
                border-left: 4px solid #007acc;
                transition: background-color 0.2s;
            }
            .conversation-item:hover {
                background-color: #2d2d30;
            }
            .conversation-item a {
                color: #4ec9b0;
                text-decoration: none;
                font-size: 1.1em;
                display: block;
                margin-bottom: 8px;
            }
            .conversation-item a:hover {
                color: #569cd6;
            }
            .meta {
                color: #858585;
                font-size: 0.9em;
            }
            .stat {
                display: inline-block;
                background-color: #3e3e42;
                padding: 4px 8px;
                margin: 3px;
                border-radius: 3px;
                font-size: 0.85em;
            }
            .refresh-notice {
                position: fixed;
                top: 10px;
                right: 10px;
                background-color: #007acc;
                color: white;
                padding: 8px 12px;
                border-radius: 3px;
                font-size: 0.9em;
            }
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #858585;
            }
        </style>
    </head>
    <body>
        <div class="refresh-notice">🔄 Auto-refresh every 5s</div>

        <div class="header">
            <h1>🐛 LCA Debug Console</h1>
            <p>Click on any conversation to see detailed debug information</p>
        </div>
    """

    if not conversations:
        html += """
        <div class="empty-state">
            <h2>No conversations yet</h2>
            <p>Start chatting in the main app to see debug logs here</p>
        </div>
        """
    else:
        html += '<ul class="conversation-list">'
        # Sort by created_at, newest first
        sorted_convs = sorted(conversations, key=lambda c: c.get('created_at', ''), reverse=True)

        for conv in sorted_convs:
            conv_id = conv['id']
            created = conv.get('created_at', 'Unknown')
            messages = conv.get('message_count', 0)
            db = conv.get('database_id', 'unknown')

            # Get debug history count
            debug_history = conversation_service.get_debug_data(conv_id)
            debug_turns = len(debug_history) if debug_history else 0

            html += f"""
            <li class="conversation-item">
                <a href="/api/debug/view/{conv_id}">📝 {conv_id}</a>
                <div class="meta">
                    <span class="stat">💬 {messages} messages</span>
                    <span class="stat">🐛 {debug_turns} debug entries</span>
                    <span class="stat">💾 {db}</span>
                    <span class="stat">🕐 {created[:19]}</span>
                </div>
            </li>
            """

        html += '</ul>'

    html += """
    </body>
    </html>
    """

    return HTMLResponse(content=html, status_code=200)


@app.get("/api/debug/status/{conversation_id}")
async def debug_status(conversation_id: str):
    """
    Quick status check for a conversation - returns turn count for polling
    Used by debug view to detect when new turns are added
    """
    debug_enabled = os.getenv('DEBUG', 'false').lower() == 'true'

    if not debug_enabled:
        raise HTTPException(status_code=403, detail="Debug mode disabled")

    debug_history = conversation_service.get_debug_data(conversation_id)

    if debug_history is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "turn_count": len(debug_history)
    }


@app.get("/api/debug/view/{conversation_id}", response_class=HTMLResponse)
async def debug_conversation(conversation_id: str):
    """
    Debug view for conversation - shows all multi-turn loop details

    Returns HTML page with manual refresh button that highlights when new data arrives
    """
    debug_enabled = os.getenv('DEBUG', 'false').lower() == 'true'

    if not debug_enabled:
        return HTMLResponse(content="""
        <html>
            <head><title>Debug Mode Disabled</title></head>
            <body style="font-family: monospace; padding: 20px;">
                <h1>⚠️ Debug Mode Disabled</h1>
                <p>Set <code>DEBUG=true</code> in <code>backend/.env</code> to enable debug mode.</p>
            </body>
        </html>
        """, status_code=200)

    # Get debug data from conversation service
    debug_history = conversation_service.get_debug_data(conversation_id)

    if debug_history is None:
        return HTMLResponse(content=f"""
        <html>
            <head><title>Conversation Not Found</title></head>
            <body style="font-family: monospace; padding: 20px;">
                <h1>❌ Conversation Not Found</h1>
                <p>No conversation found with ID: <code>{conversation_id}</code></p>
                <p><a href="javascript:history.back()">Go Back</a></p>
            </body>
        </html>
        """, status_code=404)

    # Get conversation info
    conv = conversation_service.get_conversation(conversation_id)

    # Build HTML with improved, clearer debug view
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug: {conversation_id}</title>
        <style>
            body {{
                font-family: 'Courier New', monospace;
                padding: 20px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                max-width: 1400px;
                margin: 0 auto;
            }}
            .back-link {{
                color: #4ec9b0;
                text-decoration: none;
                margin-bottom: 15px;
                display: inline-block;
            }}
            .back-link:hover {{
                color: #569cd6;
            }}
            .context-box {{
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 25px;
                border: 1px solid #4299e1;
            }}
            .user-prompt {{
                background-color: #2d2d30;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #4299e1;
                margin-bottom: 15px;
            }}
            .user-prompt strong {{
                color: #4ec9b0;
                display: block;
                margin-bottom: 8px;
            }}
            .user-prompt-text {{
                color: #f0f0f0;
                font-size: 1.05em;
                line-height: 1.5;
            }}
            .meta-stats {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .stat {{
                background-color: #3e3e42;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 0.9em;
            }}
            .turn-section {{
                background-color: #252526;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                border-left: 4px solid #007acc;
            }}
            .turn-header {{
                color: #4ec9b0;
                margin-top: 0;
                margin-bottom: 15px;
            }}
            .iteration-flow {{
                margin-left: 20px;
                border-left: 2px solid #3e3e42;
                padding-left: 15px;
            }}
            .iteration {{
                margin-bottom: 20px;
                position: relative;
            }}
            .iteration::before {{
                content: '';
                position: absolute;
                left: -18px;
                top: 8px;
                width: 10px;
                height: 10px;
                background-color: #007acc;
                border-radius: 50%;
            }}
            .iteration-label {{
                color: #858585;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .thinking {{
                background-color: #2d2d30;
                padding: 12px;
                border-radius: 4px;
                border-left: 3px solid #fbbf24;
                margin-bottom: 10px;
            }}
            .thinking-label {{
                color: #fbbf24;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .action-call {{
                background-color: #1e1e1e;
                padding: 12px;
                border-radius: 4px;
                border-left: 3px solid #f97316;
                margin-bottom: 10px;
            }}
            .action-label {{
                color: #f97316;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .user-sees {{
                background-color: #1e3a1e;
                padding: 12px;
                border-radius: 4px;
                border-left: 3px solid #10b981;
                margin-bottom: 10px;
            }}
            .user-sees-label {{
                color: #10b981;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .collapsible {{
                background-color: #2d2d30;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 20px;
                user-select: none;
            }}
            .collapsible:hover {{
                background-color: #3e3e42;
            }}
            .collapsible-content {{
                display: none;
                background-color: #1e1e1e;
                padding: 15px;
                border-radius: 4px;
                margin-top: 5px;
            }}
            .collapsible-content.active {{
                display: block;
            }}
            .collapsible::before {{
                content: '▶ ';
                display: inline-block;
                transition: transform 0.2s;
            }}
            .collapsible.active::before {{
                transform: rotate(90deg);
            }}
            pre {{
                margin: 5px 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .refresh-button {{
                position: fixed;
                top: 10px;
                right: 10px;
                background-color: #007acc;
                color: white;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 0.9em;
                z-index: 1000;
                border: 2px solid transparent;
                cursor: pointer;
                font-family: 'Courier New', monospace;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }}
            .refresh-button:hover {{
                background-color: #005a9e;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.4);
            }}
            .refresh-button.has-updates {{
                background-color: #f59e0b;
                border-color: #fbbf24;
                animation: pulse 1.5s ease-in-out infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }}
                50% {{
                    box-shadow: 0 2px 12px rgba(251, 191, 36, 0.6);
                }}
            }}
            .complete-badge {{
                color: #10b981;
                font-weight: bold;
            }}
            .error-badge {{
                color: #ef4444;
                font-weight: bold;
            }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // Collapsible sections
                const collapsibles = document.querySelectorAll('.collapsible');
                collapsibles.forEach(function(collapsible) {{
                    collapsible.addEventListener('click', function() {{
                        this.classList.toggle('active');
                        const content = this.nextElementSibling;
                        content.classList.toggle('active');
                    }});
                }});

                // Refresh button functionality
                const refreshButton = document.getElementById('refresh-button');
                const currentTurnCount = {len(debug_history)};

                // Check for updates every 3 seconds
                setInterval(async function() {{
                    try {{
                        const response = await fetch('/api/debug/status/{conversation_id}');
                        const data = await response.json();

                        if (data.turn_count > currentTurnCount) {{
                            // New data available - highlight button
                            refreshButton.classList.add('has-updates');
                            refreshButton.innerHTML = '🔔 New Updates - Click to Refresh';
                        }}
                    }} catch (error) {{
                        console.error('Error checking for updates:', error);
                    }}
                }}, 3000);

                // Click to refresh
                refreshButton.addEventListener('click', function() {{
                    window.location.reload();
                }});
            }});
        </script>
    </head>
    <body>
        <button id="refresh-button" class="refresh-button">🔄 Refresh</button>

        <a href="/api/debug" class="back-link">← Back to Debug Console</a>

        <div class="context-box">
            <h1 style="margin-top: 0; color: #4ec9b0;">🐛 Debug View</h1>
            <p style="color: #858585; margin-bottom: 5px;">Session: <code>{conversation_id}</code> | Created: {conv['created_at'][:19]}</p>
        </div>
    """

    # Show each turn's debug data with improved layout
    for idx, turn_data in enumerate(debug_history, 1):
        user_msg = turn_data.get('user_message', '[User message not captured]')
        iterations = turn_data.get('iterations', 0)
        total_time = turn_data.get('timing', {}).get('total_ms', 0)
        db_name = turn_data.get('database_context', {}).get('selected_db_name', 'N/A')
        method_mode = turn_data.get('database_context', {}).get('method_selection_mode', 'auto')

        html += f"""
        <div class="turn-section">
            <h2 class="turn-header">Turn {idx}</h2>

            <div class="user-prompt">
                <strong>🎯 User Asked:</strong>
                <div class="user-prompt-text">"{user_msg}"</div>
            </div>

            <div class="meta-stats">
                <div class="stat">📊 Database: {db_name}</div>
                <div class="stat">🔬 Method: {method_mode}</div>
                <div class="stat">⏱️ Total: {total_time:.0f}ms</div>
                <div class="stat">🔄 Iterations: {iterations}</div>
            </div>

            <h3 style="color: #4ec9b0; margin-top: 20px; margin-bottom: 10px;">Multi-Turn Flow:</h3>
            <div class="iteration-flow">
        """

        # Build iteration flow
        all_messages = turn_data.get('all_messages', [])
        actions = turn_data.get('actions_executed', [])

        for i in range(1, iterations + 1):
            iteration_time = turn_data.get('timing', {}).get('per_iteration_ms', [])[i-1] if i <= len(turn_data.get('timing', {}).get('per_iteration_ms', [])) else 0

            html += f"""
            <div class="iteration">
                <div class="iteration-label">Iteration {i} ({iteration_time:.0f}ms)</div>
            """

            # Find AI message for this iteration
            ai_msg = next((m for m in all_messages if m['iteration'] == i), None)
            if ai_msg:
                msg_text = ai_msg['message']

                # Check if message contains ACTION:
                has_action = 'ACTION:' in msg_text

                if has_action:
                    # Show as thinking/reasoning
                    preview = msg_text[:200] + '...' if len(msg_text) > 200 else msg_text
                    html += f"""
                <div class="thinking">
                    <div class="thinking-label">💭 AI Reasoning:</div>
                    <pre>{preview}</pre>
                </div>
                    """
                else:
                    # This is the final user-facing message
                    preview = msg_text[:300] + '...' if len(msg_text) > 300 else msg_text
                    html += f"""
                <div class="user-sees">
                    <div class="user-sees-label">💬 User Sees:</div>
                    <pre>{preview}</pre>
                </div>
                    """

            # Find action for this iteration
            action_entry = next((a for a in actions if a['iteration'] == i), None)
            if action_entry:
                action = action_entry['action']
                action_type = action['type']
                query = action.get('query', 'N/A')

                if action_type.startswith('calculate'):
                    results_info = '<span class="complete-badge">✅ Calculation Complete</span>'
                else:
                    results_count = len(action.get('results', []))
                    is_empty = action.get('empty_results', False)
                    if is_empty:
                        results_info = f'<span class="error-badge">⚠️ {results_count} results (empty)</span>'
                    else:
                        results_info = f'✓ {results_count} results'

                html += f"""
                <div class="action-call">
                    <div class="action-label">🔧 Internal Action:</div>
                    <strong>{action_type}</strong>("{query}")<br>
                    → {results_info}
                </div>
                """

            html += "</div>"

        html += """
            </div>
        """

        # Collapsible sections for detailed data
        html += f"""
            <div class="collapsible">System Prompt ({len(turn_data.get('system_prompt_preview', ''))} chars preview)</div>
            <div class="collapsible-content">
                <pre>{turn_data.get('system_prompt_preview', 'N/A')}</pre>
            </div>

            <div class="collapsible">Full Conversation History</div>
            <div class="collapsible-content">
                <pre>{json.dumps(turn_data.get('full_conversation_history', []), indent=2)}</pre>
            </div>

            <div class="collapsible">Raw Debug Data (JSON)</div>
            <div class="collapsible-content">
                <pre>{json.dumps(turn_data, indent=2, default=str)}</pre>
            </div>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return HTMLResponse(content=html, status_code=200)
