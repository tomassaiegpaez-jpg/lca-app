# LCA-App Project Context

**Last Updated**: 2025-11-02
**Status**: Operational, Multi-Database Support Fully Implemented
**Current Version**: app.py 1,531 lines | 6 databases | Hallucination prevention active

## Recent Updates (Nov 1-2, 2025)

✅ **Multi-Database Support** - 6 databases (ELCD, Agribalyse, USLCI, LCA Commons, ecoinvent, NEEDS)
✅ **Hallucination Prevention System** - Honest errors after 2 empty searches, prevents AI from fabricating results
✅ **Multi-Turn Conversation Loop** - Max 5 iterations enabling automatic fallback behavior
✅ **Auto/Interactive Mode Switching** - Two AI behavior modes for different user needs
✅ **Knowledge-Based Guidance** - LCIA methods database + database recommendations
✅ **Conversation Context Management** - Rich conversation state tracking (database, method, mode changes)
✅ **Goal & Scope Auto-Inference** - ISO 14044-compliant Goal & Scope generation
✅ **Automatic Fallback Strategy** - Product systems → processes seamless retry
✅ **Database/Method/Mode Selector UI** - New components: DatabaseSelector, MethodSelector, ConversationHeader

## Overview
Full-stack web application for **Life Cycle Assessment (LCA) analysis** that combines:
- **OpenLCA** (via IPC protocol) - Open-source LCA software running on Windows host
- **Claude AI** (Anthropic API) - Intelligent analysis and conversational interface with hallucination prevention
- **React + FastAPI** - Modern web stack with multi-database support
- **Knowledge Bases** - Expert guidance on LCIA methods and database selection

**Purpose**: Help users assess environmental impact of products/processes through an AI-powered conversational interface with support for multiple LCA databases and intelligent workflow automation.

## Architecture

```
Frontend (React/Vite)  ←→  Backend (FastAPI)  ←→  Multiple OpenLCA IPC Servers
      :5173                    :8000                  172.26.192.1:8080-8085
                                  ↓                          (6 databases)
                           Claude API (Anthropic)
                                  ↓
                         Knowledge Bases (JSON)
                      ├─ lcia_methods.json (14KB)
                      └─ databases_guidance.json (18KB)
                                  ↓
                      Conversation Service (context tracking)
                      Database Manager (multi-DB routing)
```

## Tech Stack

**Backend** (`/backend`)
- FastAPI + uvicorn
- olca-ipc (OpenLCA integration)
- anthropic (Claude AI SDK 0.39.0)
- Multiple database support (6 configured databases)
- Knowledge bases (LCIA methods guidance, database recommendations)
- In-memory conversation management

**Frontend** (`/frontend`)
- React 19.1.1 + Vite 7.1.7
- Vanilla CSS (purple/blue gradient theme)
- Component-based architecture
- Multi-panel layout (chat + results)
- Real-time database/method/mode selection

## Key Features Implemented

✅ **Multi-Database Support** (Nov 1, 2025)
- 6 configured databases: ELCD, Agribalyse, USLCI, LCA Commons, ecoinvent, NEEDS
- Database-specific IPC clients (ports 8080-8085)
- Dynamic database switching mid-conversation
- DatabaseManager service for routing requests to correct database
- Database availability checking (socket-based with 2s timeout)
- Database-specific guidance and recommendations

✅ **Hallucination Prevention System** (Nov 2, 2025)
- Tracks consecutive empty search results (`empty_search_count`)
- Forces honest error response after 2 empty searches
- Provides database-specific suggestions (e.g., "Try Agribalyse for food products")
- Prevents AI from fabricating LCIA numbers when data not found
- Enhanced AI system prompts with explicit "NEVER HALLUCINATE" instructions

✅ **Multi-Turn Conversation Loop** (Nov 1-2, 2025)
- Max 5 iterations per user message
- AI can see previous action results and decide next action
- Enables automatic fallback behavior (product systems → processes)
- Action-result-action chaining for seamless workflows
- Loop breaks on completion, max iterations, or forced errors

✅ **Auto/Interactive Mode Switching** (Nov 1-2, 2025)
- **Auto Mode**: AI makes assumptions, proceeds autonomously, minimal interaction
- **Interactive Mode**: AI asks clarifying questions, more conversational, educational
- Different system prompts optimized for each mode
- User-selectable via UI dropdown
- Mode-specific behavior for search results (auto: use first result, interactive: ask which one)

✅ **Knowledge-Based Guidance** (Nov 2, 2025)
- `lcia_methods.json`: Expert knowledge on 15+ LCIA methods (pros/cons, use cases, regional focus)
- `databases_guidance.json`: Database-specific guidance (strengths, limitations, best for)
- AI prompt injection with contextual guidance
- Method recommendation system (`recommend_method()` in DatabaseManager)
- Database-specific search failure suggestions

✅ **Conversation Context Management** (Nov 1, 2025)
- ConversationService: Rich conversation state beyond message history
- Tracks database selection + change history
- Tracks method selection (manual vs automatic)
- Tracks chat mode (auto/interactive)
- Context preserved across database/method changes
- In-memory storage (not persisted yet)

✅ **Goal & Scope Auto-Inference** (Nov 1, 2025)
- ISO 14044-compliant Goal & Scope generated for each calculation
- Inferred from user query, selected process, amount/unit, impact method
- Displayed in Results Panel with full ISO structure
- Fields: Study Goal, Functional Unit, System Boundary, Intended Audience, Assumptions, Limitations

✅ **Automatic Fallback Strategy** (Nov 1-2, 2025)
- Search product systems first (complete supply chains, faster calculation)
- If empty: Automatically search processes
- If processes found: Calculate using `calculate_lcia` (creates product system on-the-fly)
- If processes also empty: Honest error with database suggestions
- Seamless user experience with no manual retry needed

✅ **Process & Product System Management**
- Search across multiple databases
- View detailed process information (exchanges, location, category)
- Support for pre-built product systems (linked process collections)
- Auto-create product systems from unit processes

✅ **LCIA Calculations**
- Calculate Life Cycle Impact Assessment results
- Support for 15+ impact categories (climate change, energy, water, land use, etc.)
- Multiple impact methods (ReCiPe 2016, ILCD 2011, EF 3.0, CML, etc.)
- Manual or automatic method selection
- Results displayed with Goal & Scope, product system diagram, metadata

✅ **AI-Powered Analysis**
- Conversational LCA assistant (Claude Sonnet 3.5)
- Multi-turn conversation with action execution
- Analyze individual processes
- Compare multiple processes
- Generate improvement recommendations
- Action-based execution: `search_processes`, `search_product_systems`, `calculate_lcia`, `calculate_lcia_ps`

✅ **Rich UI Components**
- ChatPanel: Real-time chat with database/mode/method selectors
- ResultsPanel: LCIA results with collapsible sections
- DatabaseSelector: Dropdown with 6 databases + availability indicators
- MethodSelector: LCIA method picker (auto vs manual)
- ConversationHeader: Shows current context (database, method, mode, session ID)
- GoalScopeForm: Manual Goal & Scope entry (if user prefers)
- Action feedback indicators (search results, calculation status, errors)

## Project Structure

```
lca-app/
├── backend/
│   ├── app.py (1531 lines)                       # Main FastAPI app + routes + multi-turn loop
│   ├── services/
│   │   ├── openlca_service.py (~800 lines)       # OpenLCA IPC integration
│   │   ├── claude_service.py (264 lines)         # Claude AI integration
│   │   ├── database_manager.py (400+ lines) NEW  # Multi-database routing + knowledge bases
│   │   └── conversation_service.py (332 lines) NEW # Conversation context management
│   ├── config/
│   │   └── databases.json (104 lines) NEW        # 6 database configurations (ports 8080-8085)
│   ├── knowledge/
│   │   ├── lcia_methods.json (14KB) NEW          # Expert guidance on LCIA methods
│   │   └── databases_guidance.json (18KB) NEW    # Database-specific recommendations
│   ├── studies/                            NEW   # Goal & Scope storage (in-memory)
│   ├── data/
│   │   ├── process_catalog.json                  # ELCD process catalog
│   │   └── keyword_index.json                    # Search optimization
│   ├── test_*.py                                 # Manual test scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx (133 lines)                   # Main React component + state management
│   │   ├── App.css                               # Global styles
│   │   ├── components/
│   │   │   ├── ChatPanel.jsx                     # Chat interface + controls
│   │   │   ├── ChatPanel.css
│   │   │   ├── ResultsPanel.jsx                  # LCIA results display
│   │   │   ├── ResultsPanel.css
│   │   │   ├── DatabaseSelector.jsx       NEW    # Multi-database dropdown
│   │   │   ├── DatabaseSelector.css       NEW
│   │   │   ├── MethodSelector.jsx         NEW    # LCIA method picker
│   │   │   ├── MethodSelector.css         NEW
│   │   │   ├── ConversationHeader.jsx     NEW    # Context display header
│   │   │   ├── ConversationHeader.css     NEW
│   │   │   ├── GoalScopeForm.jsx          NEW    # Manual Goal & Scope entry
│   │   │   └── GoalScopeForm.css          NEW
│   │   └── main.jsx                              # Entry point
│   ├── package.json
│   └── vite.config.js
├── docs/                                    NEW   # Documentation directory
│   ├── DIAGNOSTIC_REPORT.md                      # Bug fixes (Nov 1, 2025)
│   ├── DATABASE_SELECTION_FIXES.md               # Multi-DB implementation
│   ├── DATABASE_SELECTOR_TROUBLESHOOTING.md      # User troubleshooting guide
│   └── LCA_COMMONS_SETUP_GUIDE.md                # Database-specific setup
├── ISO_INTEGRATION_PLAN.md (24KB)                # Phase 1 partially implemented
├── LCI_IMPLEMENTATION_PLAN.md (6KB)              # Not yet implemented
├── .claude/
│   └── README.md                                 # This file (project context for AI)
└── .env                                          # API keys + OpenLCA config
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

**Multi-Database Routes**
- `GET /` - Health check
- `GET /api/databases` - List all configured databases with availability status
- `GET /api/databases/{database_id}/processes` - List processes from specific database
- `POST /api/databases/{database_id}/processes/search` - Search processes in specific database
- `GET /api/databases/{database_id}/product-systems` - List product systems from specific database
- `POST /api/databases/{database_id}/product-systems/search` - Search product systems in specific database
- `GET /api/databases/{database_id}/impact-methods` - Available LCIA methods in specific database

**Conversational LCA (Main Endpoint)**
- `POST /api/lca/chat` - Conversational LCA assistant with multi-turn loop
  - Supports multi-database selection
  - Auto/interactive mode switching
  - Multi-turn conversation (max 5 iterations)
  - Action-based workflow execution
  - Hallucination prevention
  - Automatic fallback (product systems → processes)

**Direct Calculation**
- `POST /api/lca/calculate` - Direct LCIA calculation
- `POST /api/lca/calculate_lcia` - Calculate LCIA for process (creates product system)
- `POST /api/lca/calculate_lcia_ps` - Calculate LCIA for existing product system

**Goal & Scope Management**
- `POST /api/goal-scope` - Create manual Goal & Scope
- `GET /api/goal-scope/{study_id}` - Retrieve Goal & Scope
- `PUT /api/goal-scope/{study_id}` - Update Goal & Scope

**AI Analysis (Legacy)**
- `POST /api/analyze/process/{id}` - AI analysis of single process
- `POST /api/analyze/compare` - Compare multiple processes

**Method Knowledge**
- `GET /api/methods/knowledge` - Get all LCIA methods with expert guidance
- `GET /api/methods/recommend` - Get method recommendation for database/query

## Important Technical Details

**Multi-Turn Conversation Loop** (backend/app.py:1254-1506)
```python
# Flow:
1. User sends message
2. Build AI system prompt (inject knowledge bases, catalog context)
3. AI generates response + action
4. Execute action (search/calculate via DatabaseManager)
5. Append results to conversation history
6. AI sees results, decides next action
7. Loop continues (max 5 iterations)
8. Clean final message (remove ACTION commands)
9. Return to frontend
```

**Hallucination Prevention** (backend/app.py:1231-1465)
```python
max_empty_searches = 2  # Track consecutive empty results
empty_search_count = 0

# After each search:
if len(results) == 0:
    empty_search_count += 1
else:
    empty_search_count = 0  # Reset on success

# Force error after 2 empty searches:
if empty_search_count >= max_empty_searches:
    # Build honest error message
    # Add database-specific suggestions
    # Set action_data["type"] = "search_failed"
    # Break loop to prevent AI from continuing
```

**Auto vs Interactive System Prompts** (backend/app.py:901-1246)
- **Auto Mode** (lines 901-1071): "Make smart assumptions", "Proceed if 1 result", "Automatically extract amounts"
- **Interactive Mode** (lines 1072-1246): "Ask questions when >1 result", "Confirm extracted amounts", "Be educational"
- Both modes have "NEVER HALLUCINATE" instructions
- Prompts inject database guidance and method knowledge

**Database Manager** (backend/services/database_manager.py)
- Manages 6 IPC clients (lazy initialization)
- Routes requests to correct database based on `database_id`
- Loads knowledge bases (LCIA methods, database guidance)
- `recommend_method()`: AI-powered method selection
- `get_database_guidance()`: Inject context into AI prompts

**Conversation Service** (backend/services/conversation_service.py)
```python
class ConversationContext:
    id: str
    database_id: str
    method_id: Optional[str]
    method_selection_mode: str  # "auto" or "manual"
    mode: str  # "auto" or "interactive"
    messages: List[Message]
    database_history: List[DatabaseChange]
    method_history: List[MethodChange]
```
- In-memory storage: `conversations = {}`
- Tracks all context changes
- Not persisted to database yet

**Product System Strategy** (backend/services/openlca_service.py)
1. Search for existing product systems first (faster, complete supply chains)
2. If not found: Search processes
3. For process calculations: Auto-create product system via `create_product_system()`
4. Use `preferred_type="LCI_RESULT"` and `default_providers="prefer"`
5. Fallback to manual simple product system if auto-linking fails

**Action System** (AI generates, backend executes)
```json
{
  "search_processes": {"query": "glass fiber", "limit": 10},
  "search_product_systems": {"query": "cement", "limit": 10},
  "calculate_lcia": {"process_id": "...", "amount": 2, "method_id": "..."},
  "calculate_lcia_ps": {"product_system_id": "...", "amount": 1}
}
```
- AI outputs action in specific format
- Backend parses and executes
- Results appended to conversation with `[Action Results: ...]`
- AI sees results and decides next action

## Current State & Known Issues

### Last Working On (Nov 2, 2025)
**Completed:**
- ✅ Hallucination prevention system (Nov 2) - AI no longer fabricates LCIA results when data not found
- ✅ Multi-turn conversation loop (Nov 1-2) - Automatic fallback from product systems to processes
- ✅ Auto/Interactive mode switching (Nov 1-2) - Two AI behavior modes with different system prompts
- ✅ Phase 3 of hallucination prevention (Nov 2) - Auto-to-interactive fallback suggestion banner in UI
- ✅ Documentation improvements (Nov 2) - Updated .claude/README.md to reflect current state

**Recently Fixed Bugs:**
- ✅ Database availability check hanging (solved with socket timeout, see DIAGNOSTIC_REPORT.md)
- ✅ Chat endpoint crashing due to scope issue (fixed re/json imports)
- ✅ Hardcoded ELCD references (now dynamic database routing)
- ✅ Wrong method being used for calculations (fixed method tracking in conversation context)

### Known Limitations
- Conversations not persisted (lost on server restart)
- No user authentication or multi-user support
- No caching for repeated calculations
- Some databases may have limited method support
- Goal & Scope stored in-memory only (not saved to openLCA)
- No automated test suite yet (manual test scripts only)

### Planned Features/Improvements
**Short-term (next sprint):**
- LCI (Life Cycle Inventory) display feature (see LCI_IMPLEMENTATION_PLAN.md)
- Database persistence for conversations (PostgreSQL/SQLite)
- Caching layer for frequent queries

**Medium-term:**
- Automated testing suite (pytest + frontend tests)
- User authentication and session management
- Batch calculations (multiple products at once)
- Export results to PDF/Excel

**Long-term (from ISO_INTEGRATION_PLAN.md):**
- Complete ISO 14040/14044 compliance (Phases 2-6)
- Life Cycle Interpretation features
- Uncertainty analysis
- Sensitivity analysis
- Monte Carlo simulations

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
| `backend/app.py` | 1531 | Main API + routes + multi-turn loop + chat endpoint |
| `backend/services/openlca_service.py` | ~800 | OpenLCA IPC integration, LCIA calculations, Goal & Scope |
| `backend/services/database_manager.py` | ~400 | Multi-database routing, knowledge bases, method recommendations |
| `backend/services/conversation_service.py` | 332 | Conversation context management, change history tracking |
| `backend/services/claude_service.py` | 264 | Claude AI integration (message generation) |
| `backend/config/databases.json` | 104 | 6 database configurations (names, ports, capabilities) |
| `backend/knowledge/lcia_methods.json` | 14KB | Expert guidance on LCIA methods (pros/cons, use cases) |
| `backend/knowledge/databases_guidance.json` | 18KB | Database-specific recommendations (strengths, limitations) |
| `frontend/src/App.jsx` | 133 | Main React component, state management, API calls |
| `frontend/src/components/ChatPanel.jsx` | ~230 | Chat interface, database/method/mode selectors, input |
| `frontend/src/components/ResultsPanel.jsx` | ~450 | LCIA results display, Goal & Scope, collapsible sections |
| `frontend/src/components/DatabaseSelector.jsx` | ~70 | Multi-database dropdown with availability indicators |
| `frontend/src/components/MethodSelector.jsx` | ~120 | LCIA method picker (auto vs manual selection) |
| `frontend/src/components/ConversationHeader.jsx` | ~50 | Context display (database, method, mode, session ID) |

## Development Notes

**Strengths**
- Clean separation of concerns (services layer with specialized components)
- Comprehensive docstrings and inline documentation
- Proper error handling with HTTPException and try-catch blocks
- Multiple fallback strategies for robustness (product systems → processes)
- Hallucination prevention system ensures honest AI responses
- Rich conversation context tracking (database, method, mode changes)
- Knowledge-based guidance (LCIA methods, databases)
- Component-based frontend architecture
- Multi-database support with dynamic routing
- ISO 14044-compliant Goal & Scope generation

**Recent Improvements (Nov 1-2, 2025)**
- Multi-turn conversation loop enabling complex workflows
- Hallucination prevention (empty search tracking + forced errors)
- Auto/Interactive mode switching for different user needs
- Knowledge base integration for intelligent recommendations
- Database-specific guidance and error messages
- Conversation context management with change history
- Frontend components decomposition (DatabaseSelector, MethodSelector, etc.)

**Areas for Improvement**
- No database persistence (conversations lost on restart) - **PRIORITY**
- No automated test suite (manual test scripts only)
- No logging system configured (print statements only)
- No caching layer (repeated queries hit OpenLCA every time)
- Limited input validation on frontend
- No rate limiting or API authentication
- Goal & Scope not persisted to openLCA database
- No export functionality (PDF, Excel)

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

## Git Workflow Guidelines

### Automatic Commit Strategy

**When to Commit (Claude should commit automatically):**

1. **After completing a logical feature or fix**
   - New component implementation (e.g., DatabaseSelector)
   - Bug fix that resolves a specific issue
   - Documentation updates that describe completed work
   - Configuration changes that affect functionality

2. **After significant refactoring**
   - Code reorganization (e.g., extracting services)
   - Performance improvements
   - Code cleanup that doesn't change behavior

3. **Before switching context**
   - Before starting work on a different feature
   - At natural breakpoints in development
   - When user explicitly requests a commit

4. **Regular checkpoints**
   - After 2-3 hours of work without commits
   - When multiple related changes accumulate
   - After successful testing of new functionality

**When NOT to commit:**
- Mid-implementation (incomplete features)
- Breaking changes (unless explicitly in a feature branch)
- Experimental code that hasn't been tested
- When tests are failing (unless fixing the tests)

### Commit Message Format

Follow conventional commit style:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring without behavior change
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Maintenance tasks (dependencies, build config)
- `style:` Code style changes (formatting, no logic change)

**Example:**
```
feat(debug): Add manual refresh button to debug interface

Replace auto-refresh with manual refresh button that highlights when
new data is detected. This prevents collapsible sections from closing
every 3 seconds while still alerting users to new updates.

- Add /api/debug/status endpoint for polling turn count
- Replace meta refresh tag with JavaScript polling
- Button pulses orange when updates detected
- Collapsible sections remain open between manual refreshes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Branching Strategy

**Main Branch (`main`)**
- Always deployable
- Contains stable, tested code
- Protected (no force push)
- All features merge here via pull requests

**Feature Branches**
Create feature branches for:
- New major features (e.g., `feature/lci-display`)
- Significant refactoring (e.g., `refactor/extract-services`)
- Experimental work (e.g., `experiment/caching-layer`)

**Naming convention:**
```
feature/<feature-name>      # New features
fix/<bug-description>       # Bug fixes
refactor/<what-refactoring> # Code refactoring
docs/<doc-update>           # Documentation
chore/<maintenance-task>    # Chores/maintenance
```

**When to create a branch:**
1. Starting work on a new feature (>1 day of work)
2. Making breaking changes
3. Experimental implementations
4. When user explicitly requests a branch

**When to commit directly to main:**
- Small bug fixes
- Documentation updates
- Minor improvements
- Configuration tweaks
- Work that doesn't risk breaking existing functionality

### Branch Workflow

**Creating a feature branch:**
```bash
git checkout -b feature/new-feature-name
```

**Working on branch:**
```bash
# Make changes
git add <files>
git commit -m "feat: implement feature X"

# Commit regularly on the branch
git commit -m "feat: add tests for feature X"
git commit -m "docs: document feature X"
```

**Merging back to main:**
```bash
# Update branch with latest main
git checkout main
git pull origin main
git checkout feature/new-feature-name
git rebase main  # or merge main into branch

# Run tests, verify everything works

# Merge to main
git checkout main
git merge feature/new-feature-name

# Delete feature branch
git branch -d feature/new-feature-name
```

### When to Use Pull Requests

**Always create PR for:**
- Major features (>100 lines changed)
- Breaking changes
- Architecture changes
- When user requests review

**PR Title format:**
```
[Feature] Add LCI display panel
[Fix] Resolve database selector hanging issue
[Refactor] Extract conversation service
[Docs] Add setup guide
```

**PR Description should include:**
- What changed and why
- How to test the changes
- Any breaking changes
- Related issues/tickets

### Commit Frequency Guidelines

**Optimal frequency:**
- Commit after each logical unit of work (1-3 related files)
- 3-5 commits per hour of active development
- More frequent commits during debugging
- Less frequent commits during planning/design

**Too frequent (avoid):**
- Every line change
- Multiple commits for same logical change
- Commits like "fix typo", "fix another typo"

**Too infrequent (avoid):**
- One commit for entire day's work
- One commit with 20+ files changed
- Mixing unrelated changes in single commit

### Best Practices

1. **Atomic commits** - Each commit should be a self-contained change
2. **Test before commit** - Ensure code works before committing
3. **No sensitive data** - Never commit API keys, credentials
4. **Clean history** - Use `git rebase` to clean up commit history before merging
5. **Sign commits** - Add co-author footer for AI-assisted work
6. **Push regularly** - Push to origin after each significant commit
7. **Branch cleanup** - Delete merged branches promptly

### File Management

**Always commit together:**
- Related frontend + backend changes
- Component + tests
- Code + documentation
- Configuration + README updates

**Separate commits for:**
- Refactoring vs new features
- Bug fixes vs improvements
- Different features
- Code vs documentation-only changes

### Git Commands Reference

```bash
# Status and changes
git status                    # Check working directory
git diff                      # See unstaged changes
git diff --staged             # See staged changes
git log --oneline -10         # Recent commits

# Staging
git add <file>                # Stage specific file
git add .                     # Stage all changes
git add -p                    # Interactive staging

# Committing
git commit -m "message"       # Commit with message
git commit --amend            # Amend last commit (use sparingly)

# Branching
git branch                    # List branches
git checkout -b <branch>      # Create and switch
git branch -d <branch>        # Delete merged branch
git branch -D <branch>        # Force delete

# Remote operations
git push origin main          # Push to remote
git pull origin main          # Pull from remote
git push -u origin <branch>   # Push new branch

# Undoing changes
git restore <file>            # Discard changes
git restore --staged <file>   # Unstage
git reset --soft HEAD~1       # Undo last commit, keep changes
git reset --hard HEAD~1       # Undo last commit, discard changes (DANGER)
```

### Automation Rules for Claude

**Claude should automatically:**
1. ✅ Commit after completing a user-requested feature
2. ✅ Create descriptive commit messages following the format above
3. ✅ Include "Co-Authored-By: Claude" footer
4. ✅ Check `git status` before committing to understand scope
5. ✅ Stage only related files for each commit
6. ✅ Create feature branches for major new features (>200 lines)
7. ✅ Suggest PR creation for breaking changes
8. ✅ Clean up commit history (squash WIP commits) before showing user

**Claude should ask user before:**
1. ❓ Pushing to remote repository
2. ❓ Creating pull requests
3. ❓ Force pushing (should be very rare)
4. ❓ Deleting branches
5. ❓ Rebasing published commits
6. ❓ Amending commits that have been pushed

**Claude should NEVER:**
1. ❌ Commit sensitive data (.env files, API keys)
2. ❌ Force push to main branch
3. ❌ Delete main branch
4. ❌ Commit binary files without approval
5. ❌ Mix unrelated changes in one commit
6. ❌ Use generic commit messages like "fix", "update"

### Current Repository State

**Status as of Nov 2, 2025:**
- Branch: `main`
- Commits ahead of origin: 8 (including latest)
- Last commit: "Add debug interface with manual refresh and improve conversation management"
- Uncommitted changes: .claude/README.md (this file)
- Untracked: LCI_IMPLEMENTATION_PLAN.md

**Next steps:**
- Commit .claude/README.md with git workflow guidelines
- Consider creating feature branch for LCI implementation
- Push accumulated commits to origin

## Additional Context
**[USER: ADD ANY OTHER IMPORTANT CONTEXT HERE]**
