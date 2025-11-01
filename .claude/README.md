# LCA-App Project Context

## Overview
Full-stack web application for **Life Cycle Assessment (LCA) analysis** that combines:
- **OpenLCA** (via IPC protocol) - Open-source LCA software running on Windows host
- **Claude AI** (Anthropic API) - Intelligent analysis and conversational interface
- **React + FastAPI** - Modern web stack

**Purpose**: Help users assess environmental impact of products/processes through an AI-powered conversational interface.

## Architecture

```
Frontend (React/Vite)  ←→  Backend (FastAPI)  ←→  OpenLCA IPC Server (Windows)
      :5173                    :8000                  172.26.192.1:8080
                                  ↓
                           Claude API (Anthropic)
```

## Tech Stack

**Backend** (`/backend`)
- FastAPI + uvicorn
- olca-ipc (OpenLCA integration)
- anthropic (Claude AI SDK)
- 608 processes from ELCD database (cataloged in `data/process_catalog.json`)

**Frontend** (`/frontend`)
- React 19.1.1 + Vite 7.1.7
- Vanilla CSS (purple/blue gradient theme)
- Single-page chat interface

## Key Features Implemented

✅ **Process Management**
- List/search 608 processes from OpenLCA
- View detailed process information (exchanges, location, category)
- Support for product systems (linked process collections)

✅ **LCIA Calculations**
- Calculate Life Cycle Impact Assessment results
- Support multiple impact methods (default: ReCiPe 2016 Midpoint H)
- Auto-create product systems with fallback strategies

✅ **AI-Powered Analysis**
- Conversational LCA assistant (Claude)
- Analyze individual processes
- Compare multiple processes
- Generate improvement recommendations
- Action-based execution: `search_processes`, `search_product_systems`, `calculate_lcia`, `calculate_lcia_ps`

✅ **Rich UI**
- Real-time chat interface
- Embedded visualization of search/calculation results
- LCIA results tables with impact categories

## Project Structure

```
lca-app/
├── backend/
│   ├── app.py (540 lines)                    # Main FastAPI app + routes
│   ├── services/
│   │   ├── openlca_service.py (578 lines)    # OpenLCA IPC integration
│   │   └── claude_service.py (264 lines)     # Claude AI integration
│   ├── data/
│   │   ├── process_catalog.json              # 608 processes from ELCD
│   │   └── keyword_index.json                # Search optimization
│   ├── test_*.py                             # Manual test scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx (204 lines)               # Main React component
│   │   ├── App.css                           # Component styles
│   │   └── main.jsx                          # Entry point
│   ├── package.json
│   └── vite.config.js
└── .env                                      # API keys + OpenLCA config
```

## How to Run

**Prerequisites**
- OpenLCA running on Windows with IPC Server enabled (port 8080)
- ELCD database imported into OpenLCA
- Python 3.x with venv
- Node.js/npm

**Backend**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Runs on http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

**Environment Variables** (`.env`)
```
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENLCA_HOST=172.26.192.1
OPENLCA_PORT=8080
```

## API Endpoints

**Core Routes**
- `GET /` - Health check
- `GET /api/processes` - List all processes
- `POST /api/processes/search` - Search by name
- `POST /api/lca/chat` - Conversational LCA assistant (main endpoint)
- `POST /api/lca/calculate` - Direct LCIA calculation
- `POST /api/analyze/process/{id}` - AI analysis
- `POST /api/analyze/compare` - Compare processes
- `GET /api/impact-methods` - Available LCIA methods

## Important Technical Details

**Product System Strategy** (backend/services/openlca_service.py:300-400)
1. Search for existing product systems
2. Attempt auto-linking via `create_product_system()`
3. Fallback to manual simple product system creation
4. Return calculation instructions if all fail

**Conversation Management** (backend/app.py)
- In-memory storage: `conversations = {}`
- Each conversation_id maps to list of messages
- Not persisted to database yet

**Claude System Prompt** (backend/app.py:20-100)
- Includes full catalog of 608 processes with categories
- Action format specifications
- LCIA method recommendations
- Instructions for distinguishing processes vs product systems

## Current State & Known Issues

### Last Working On
**[USER: ADD WHAT YOU WERE WORKING ON HERE]**
<!-- Examples:
- Fixing bug with product system creation for XYZ processes
- Adding new feature for batch calculations
- Improving error handling when OpenLCA connection fails
- Optimizing search performance
-->

### Known Bugs/Issues
**[USER: ADD ANY KNOWN BUGS HERE]**
<!-- Examples:
- Search returns duplicate results when...
- LCIA calculation fails for processes with...
- Frontend doesn't handle error state when...
-->

### Planned Features/Improvements
**[USER: ADD PLANNED WORK HERE]**
<!-- Examples:
- Database integration for conversation persistence
- User authentication
- Unit test suite
- Caching for repeated calculations
- Better error messages on frontend
-->

## Testing

**Manual Test Scripts** (in `/backend`)
- `test_connection.py` - Verify OpenLCA IPC connectivity
- `test_product_systems.py` - List/search product systems
- `test_ps_search.py` - End-to-end LCIA calculation test

**Run Tests**
```bash
cd backend
source venv/bin/activate
python test_connection.py
python test_ps_search.py
```

**Note**: No automated test suite yet (pytest in requirements but no tests written)

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app.py` | 540 | Main API, routes, conversation management |
| `backend/services/openlca_service.py` | 578 | OpenLCA integration, LCIA calculations |
| `backend/services/claude_service.py` | 264 | Claude AI integration |
| `frontend/src/App.jsx` | 204 | React chat interface |

## Development Notes

**Strengths**
- Clean separation of concerns (services layer)
- Comprehensive docstrings
- Proper error handling with HTTPException
- Multiple fallback strategies for robustness

**Areas for Improvement**
- No database persistence (conversations lost on restart)
- No automated tests
- Frontend could use component decomposition
- No logging system configured
- Limited input validation

## OpenLCA IPC API Integration

### Official Documentation
- **API Docs**: https://greendelta.github.io/openLCA-ApiDoc/
- **Python Client**: https://greendelta.github.io/olca-ipc.py/olca/ipc.html
- **Schema Reference**: http://greendelta.github.io/olca-schema/
- **Q&A Forum**: https://ask.openlca.org/

### Requirements
- **openLCA**: Version 2.0 or higher
- **Python**: 3.11 or higher
- **olca-ipc**: Latest version from PyPI

### Recent API Fixes (2025-11-01)

**Fixed Critical Issues:**

1. **`create_product_system()` call** (`openlca_service.py:307-312`)
   - **Before**: Incorrectly passed `Ref` object
   - **After**: Now correctly passes string `process_id` with proper parameters
   - Parameters: `default_providers="prefer"`, `preferred_type="LCI_RESULT"`

2. **Ref object creation** (`openlca_service.py:388-389, 456-457, 554-556`)
   - **Before**: Used string literals `ref_type='ProductSystem'`
   - **After**: Now correctly uses `RefType` enum: `ref_type=RefType.ProductSystem`
   - Added import: `from olca_schema import RefType`
   - Fixes AttributeError: 'str' object has no attribute 'value'

3. **Impact results retrieval** (`openlca_service.py:465, 564`)
   - **Correct API**: Use `result.get_total_impacts()` (method on result object)
   - **Not**: `client.lcia(result)` (this method doesn't exist)
   - Added error handling for API version compatibility

4. **Result disposal** (`openlca_service.py:484, 583`)
   - **Correct API**: Use `result.dispose()` (method on result object)
   - **Not**: `client.dispose(result)` (this method doesn't exist)

5. **Better error handling**
   - Added try-catch blocks around critical API calls
   - Proper disposal of results even when errors occur (prevents memory leaks)
   - Helpful error messages referencing official documentation

6. **Updated documentation**
   - Added API references to docstrings
   - Included version requirements in module header
   - Added links to official documentation

### Key API Methods Used

```python
from olca_schema import RefType

# Data retrieval
client.get_descriptors(ModelType)  # Get lightweight references
client.get(ModelType, id)          # Get full object

# Product system creation
client.create_product_system(
    process_id: str,
    default_providers: "prefer" | "only" | "ignore",
    preferred_type: "LCI_RESULT" | "SYSTEM_PROCESS"
)

# Creating Ref objects (IMPORTANT: use RefType enum!)
setup.target = o.Ref(id=ps_id, ref_type=RefType.ProductSystem)
setup.impact_method = o.Ref(id=method_id, ref_type=RefType.ImpactMethod)

# Calculation
result = client.calculate(setup)
result.wait_until_ready()
impacts = result.get_total_impacts()  # Get LCIA results from result object
result.dispose()                       # Clean up (prevent memory leaks!)
```

### Starting OpenLCA IPC Server

**Before running the app:**
1. Open OpenLCA on Windows
2. Go to: `Window` → `Developer tools` → `IPC Server`
3. Start server on port `8080`
4. Verify connection: `python backend/test_connection.py`

## Additional Context
**[USER: ADD ANY OTHER IMPORTANT CONTEXT HERE]**
