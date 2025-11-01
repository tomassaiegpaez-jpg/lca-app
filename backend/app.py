"""
FastAPI Backend for LCA Application
Connects to OpenLCA via IPC and provides REST API endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
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
        search_query: Search query with query string and optional limit

    Returns:
        List of matching processes
    """
    from services.openlca_service import get_openlca_service

    try:
        service = get_openlca_service()
        processes = service.search_processes(
            query=search_query.query,
            limit=search_query.limit
        )
        return processes
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
# Conversational LCA Assistant
# ============================================================================

# In-memory conversation storage (replace with database in production)
conversations = {}

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

        # Get or create conversation history
        conv_id = chat_message.conversation_id or f"conv_{len(conversations)}"
        if conv_id not in conversations:
            conversations[conv_id] = []

        # Add user message to history
        conversations[conv_id].append({
            "role": "user",
            "content": chat_message.message
        })

        # Load process catalog for context
        catalog = load_process_catalog()

        # Group processes by category for better context
        categories_sample = {}
        for proc in catalog:
            cat = proc.get('category', 'Uncategorized')
            if cat not in categories_sample:
                categories_sample[cat] = []
            if len(categories_sample[cat]) < 3:  # Max 3 examples per category
                categories_sample[cat].append(proc['name'])

        # Build catalog context
        catalog_context = "\n\nAvailable Process Categories and Examples:\n"
        for cat, examples in sorted(categories_sample.items())[:15]:  # Top 15 categories
            catalog_context += f"\n{cat}:\n"
            for ex in examples:
                catalog_context += f"  - {ex}\n"

        # Build system prompt for LCA assistant
        system_prompt = f"""You are an expert Life Cycle Assessment (LCA) assistant with access to the ELCD database containing 608 processes.

{catalog_context}

CRITICAL RULES - READ CAREFULLY:
1. ALWAYS use ACTION commands to search and calculate - NEVER explain what results "would be"
2. When user asks for a calculation, you MUST output the ACTION command
3. Keep your responses BRIEF - detailed results are shown in a separate panel
4. After ACTION execution, provide a SHORT interpretation (2-3 sentences max)

YOUR WORKFLOW (FOLLOW THIS ORDER):
1. When user mentions a material → FIRST search for PRODUCT SYSTEMS (they're ready for calculation!)
2. If product systems found → Use calculate_lcia_ps with product_system_id
3. If NO product systems → THEN search for PROCESSES
4. If only processes found → Use calculate_lcia with process_id (will try to create product system)
5. When calculation completes → Briefly interpret key findings
6. NEVER make up numbers or explain hypothetical results

WHY PRODUCT SYSTEMS FIRST:
- Product systems are pre-built networks of linked processes
- They calculate faster and more reliably
- They have names ending in "- RER", "- GLO", etc. (geographic scope)
- ALWAYS prefer product systems over individual processes!

AVAILABLE ACTIONS (YOU MUST USE THESE):

Search for processes:
ACTION: {{"type": "search_processes", "query": "glass fiber"}}

Search for product systems:
ACTION: {{"type": "search_product_systems", "query": "glass fiber"}}

Calculate from process ID:
ACTION: {{"type": "calculate_lcia", "process_id": "uuid-here", "amount": 1.0}}

Calculate from product system ID (PREFERRED):
ACTION: {{"type": "calculate_lcia_ps", "product_system_id": "uuid-here", "amount": 1.0}}

EXTRACTING AMOUNTS FROM USER QUERIES (CRITICAL):
- When user specifies an amount like "2kg", "500g", "10 units", extract the numeric value
- Include the amount in your calculation ACTION: "amount": 2.0
- If no amount is specified, use 1.0 as default
- IMPORTANT: Different amounts produce proportionally different results (2kg = 2x the impact of 1kg)
- Examples:
  * "2kg of glass fiber" → "amount": 2.0
  * "0.5 kg of steel" → "amount": 0.5
  * "10 MJ of electricity" → "amount": 10.0
  * "glass fiber" (no amount) → "amount": 1.0

SEARCH GUIDELINES (CRITICAL):
- Database uses BRITISH ENGLISH: "fibre" not "fiber", "aluminium" not "aluminum"
- Match keywords to actual process names listed above
- For glass: "glass fibre" (British spelling!)
- For plastics: "PET", "Polyethylene", "Polypropylene"
- For metals: "Aluminium" (British!), "Steel", "Copper"
- For electricity: Include region/country
- Use specific keywords from process names, not generic terms

EXAMPLE CORRECT INTERACTION:
User: "Calculate impact of 2kg glass fiber"
You: "I'll search for glass fibre product systems first (they're ready for calculation).

ACTION: {{"type": "search_product_systems", "query": "glass fibre"}}"

[After search returns 2 product systems including ID xyz-789 named "Continuous filament glass fibre (assembled rovings), at plant - RER"]
You: "Found product system 'Continuous filament glass fibre (assembled rovings) - RER'. Calculating LCIA for 2kg now.

ACTION: {{"type": "calculate_lcia_ps", "product_system_id": "xyz-789", "amount": 2.0}}"

[After calculation completes with results]
You: "Calculation complete for 2kg! Main impacts: Climate change 23.6 kg CO2-eq, Energy use 362 MJ. Full results displayed in panel →"

FALLBACK EXAMPLE (when no product systems exist):
User: "Calculate impact of 1kg aluminum"
You: "Searching for aluminium product systems first.

ACTION: {{"type": "search_product_systems", "query": "aluminium"}}"

[Returns 0 results]
You: "No product systems found. Searching for aluminium processes instead.

ACTION: {{"type": "search_processes", "query": "aluminium"}}"

[Returns process ID abc-123]
You: "Found process. Creating product system and calculating LCIA for 1kg.

ACTION: {{"type": "calculate_lcia", "process_id": "abc-123", "amount": 1.0}}"

[System creates product system with auto-linking and calculates successfully]
You: "Product system created with 15 linked processes. Calculation complete for 1kg! Results displayed in panel →"

HANDLING ERRORS:
When product system creation fails, explain what happened and suggest alternatives:

Example error response:
[Action fails with error: "Failed to create product system - missing upstream processes"]
You: "❌ Unable to create product system automatically - the process has incomplete input definitions or missing upstream processes in the database.

Suggestions:
1. Try searching for existing product systems with similar keywords (e.g., 'aluminium RER' or 'aluminium GLO')
2. Check if there's a more specific process name in the database
3. You can create a product system manually in the openLCA desktop application

Would you like to try searching with different keywords?"

IMPORTANT NOTES:
- Product system creation with auto-linking may fail for some processes (incomplete data, missing providers)
- When this happens, provide clear explanation and actionable suggestions
- Never make up calculation results - if it fails, acknowledge the failure
- Single-process systems (no upstream links) show direct impacts only - not full supply chain

REMEMBER:
- ALWAYS use ACTION commands
- Results are shown in UI - you just provide brief context
- Be concise and action-oriented
- Handle failures gracefully with helpful guidance"""

        # Prepare messages for Claude
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversations[conv_id]
        ]

        # Get response from Claude
        response = claude_service.client.messages.create(
            model=claude_service.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages
        )

        assistant_message = response.content[0].text

        # Check if assistant wants to perform an action
        action_data = None
        display_message = assistant_message  # Message to display to user

        if "ACTION:" in assistant_message:
            # Extract and parse action
            import json
            import re
            action_match = re.search(r'ACTION:\s*({[^}]+})', assistant_message)
            if action_match:
                # Strip ACTION text from display message
                display_message = re.sub(r'\n*ACTION:\s*{[^}]+}\s*', '', assistant_message).strip()

                try:
                    action_data = json.loads(action_match.group(1))

                    # Execute action
                    if action_data["type"] == "search_processes":
                        print(f"Searching processes for: '{action_data['query']}'")
                        search_results = openlca_service.search_processes(
                            action_data["query"],
                            limit=5
                        )
                        print(f"Found {len(search_results)} results")
                        action_data["results"] = search_results

                    elif action_data["type"] == "search_product_systems":
                        search_results = openlca_service.search_product_systems(
                            action_data["query"],
                            limit=5
                        )
                        action_data["results"] = search_results

                    elif action_data["type"] == "calculate_lcia":
                        lcia_results = openlca_service.calculate_lcia(
                            action_data["process_id"],
                            impact_method_id=action_data.get("method_id"),
                            amount=action_data.get("amount", 1.0)
                        )
                        action_data["results"] = lcia_results

                    elif action_data["type"] == "calculate_lcia_ps":
                        lcia_results = openlca_service.calculate_lcia_from_product_system(
                            action_data["product_system_id"],
                            impact_method_id=action_data.get("method_id"),
                            amount=action_data.get("amount", 1.0)
                        )
                        action_data["results"] = lcia_results

                except Exception as e:
                    action_data = {"error": str(e)}

        # Add assistant response to history WITH action results so Claude can reference them
        history_content = assistant_message
        if action_data:
            # Append action results to history for context in next turn
            import json
            history_content += f"\n\n[Action Results: {json.dumps(action_data, default=str)}]"

        conversations[conv_id].append({
            "role": "assistant",
            "content": history_content
        })

        return {
            "conversation_id": conv_id,
            "message": display_message,  # Send cleaned message to user
            "action": action_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
