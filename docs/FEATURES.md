# LCA Assistant - Features Documentation

Comprehensive guide to all features and capabilities of the LCA Assistant application.

## Table of Contents

1. [Core Features](#core-features)
2. [Multi-Database Support](#multi-database-support)
3. [AI-Powered Conversational Interface](#ai-powered-conversational-interface)
4. [LCIA Calculations](#lcia-calculations)
5. [Hallucination Prevention System](#hallucination-prevention-system)
6. [Multi-Turn Conversation Loop](#multi-turn-conversation-loop)
7. [Auto and Interactive Modes](#auto-and-interactive-modes)
8. [Knowledge-Based Guidance](#knowledge-based-guidance)
9. [ISO 14044 Compliance](#iso-14044-compliance)
10. [User Interface Components](#user-interface-components)

## Core Features

### Process and Product System Search

Search across multiple LCA databases for processes and product systems:

**Process Search:**
- Full-text search across process names and descriptions
- Filter by database, location, and category
- View detailed process information including:
  - Input/output exchanges
  - Geographic location
  - Process category
  - Metadata and documentation

**Product System Search:**
- Search pre-built product systems (complete supply chains)
- Faster calculations compared to building from processes
- View system boundaries and included processes
- Automatic fallback to process search if no product systems found

**Example Queries:**
```
"Find glass fiber production processes"
"Search for cement product systems"
"Show me steel manufacturing in Europe"
```

### Process Analysis

View detailed information about LCA processes:

- **Exchanges**: Input and output flows with amounts and units
- **Location**: Geographic reference (country, region, or global)
- **Category**: Process classification (e.g., Materials/Metals)
- **Documentation**: Process description and data sources
- **Properties**: Technical parameters and assumptions

### Calculation Engine

Perform Life Cycle Impact Assessment (LCIA) calculations:

- **Unit Process Calculations**: Calculate impacts for individual processes
  - Auto-creates product system from process
  - Configurable functional unit (amount and unit)
  - Supports all available LCIA methods

- **Product System Calculations**: Calculate for existing product systems
  - Uses pre-built supply chain networks
  - Faster than unit process calculations
  - Includes all upstream and downstream processes

- **Real-time Execution**: Calculations run immediately with progress indicators
- **Result Caching**: Recent results available for quick reference (session-based)

## Multi-Database Support

### Supported Databases

The application supports **6 LCA databases** simultaneously:

1. **ELCD (European Life Cycle Database)**
   - **Strengths**: European processes, industrial materials, metals, construction
   - **Region**: Europe (EU-27)
   - **Size**: 3,800+ processes
   - **Best For**: European studies, industrial products, policy analysis

2. **Agribalyse**
   - **Strengths**: Food products, agriculture, French farming systems
   - **Region**: France (global agricultural data)
   - **Size**: 2,500+ food products
   - **Best For**: Food LCA, agricultural products, dietary assessments

3. **USLCI (US Life Cycle Inventory)**
   - **Strengths**: US-specific processes, regional data accuracy
   - **Region**: United States
   - **Size**: 1,000+ processes
   - **Best For**: US market studies, North American supply chains

4. **LCA Commons**
   - **Strengths**: US Federal LCA data, publicly available
   - **Region**: United States
   - **Size**: Varies by module
   - **Best For**: US government projects, public sector LCA

5. **ecoinvent**
   - **Strengths**: Most comprehensive global database, high quality
   - **Region**: Global (country-specific data)
   - **Size**: 18,000+ processes
   - **Best For**: Detailed studies, global supply chains, academic research

6. **NEEDS (New Energy Externalities Development for Sustainability)**
   - **Strengths**: Energy systems, power generation, renewable energy
   - **Region**: Europe
   - **Size**: 1,000+ energy processes
   - **Best For**: Energy sector LCA, electricity generation

### Database Switching

**Dynamic Switching:**
- Change databases mid-conversation
- Conversation context preserved across switches
- AI adapts recommendations based on selected database

**Database Selection:**
- Dropdown selector in chat interface
- Real-time availability indicators (green = available, red = offline)
- Automatic suggestions when data not found in current database

**Example Workflow:**
```
User: "Calculate impact of wheat production"
AI: "I couldn't find wheat in ELCD. Would you like to switch to Agribalyse,
     which specializes in agricultural products?"
User: [Switches to Agribalyse]
AI: "Found 15 wheat production processes in Agribalyse..."
```

## AI-Powered Conversational Interface

### Natural Language Processing

Ask questions in plain English (or other languages):

**Supported Query Types:**
- Impact assessments: "What's the environmental impact of 2kg of steel?"
- Process searches: "Find cement production in Germany"
- Comparisons: "Compare carbon fiber and glass fiber"
- Recommendations: "What's the most sustainable packaging material?"
- Methodology questions: "What LCIA method should I use for a European study?"

### Context-Aware Conversations

The AI maintains conversation context:

- **Remembers**: Previous selections, calculations, and preferences
- **Tracks**: Database changes, method selections, mode switches
- **Infers**: Missing information from context (amounts, units, goals)
- **Suggests**: Next steps based on conversation flow

**Example Multi-Turn Conversation:**
```
User: "I want to assess cement production"
AI: "I found 12 cement processes. Which region are you interested in?"
User: "Europe"
AI: "I'll use 'Portland cement, at plant/RER'. How much cement?"
User: "2 tons"
AI: "Calculating LCIA for 2 tons of Portland cement..."
[Results display]
User: "Now compare that with recycled concrete"
AI: "Searching for recycled concrete processes..."
```

### Intelligent Extraction

AI automatically extracts information from your queries:

- **Amounts**: "5kg", "2 tons", "100 liters"
- **Materials**: "glass fiber", "cement", "steel"
- **Locations**: "Germany", "Europe", "US"
- **Intentions**: Compare, calculate, find, analyze

## LCIA Calculations

### Impact Categories

Assess environmental impacts across **15+ categories**:

**Climate & Atmosphere:**
- Climate change (kg CO2 eq)
- Ozone depletion (kg CFC-11 eq)
- Photochemical ozone formation (kg NMVOC eq)

**Resources:**
- Fossil resource scarcity (kg oil eq)
- Mineral resource scarcity (kg Cu eq)
- Water consumption (m³)
- Land use (m² annual crop eq)

**Toxicity & Health:**
- Human toxicity (cancer / non-cancer)
- Freshwater ecotoxicity (CTUe)
- Marine ecotoxicity (CTUe)
- Terrestrial ecotoxicity (CTUe)

**Ecosystems:**
- Freshwater eutrophication (kg P eq)
- Marine eutrophication (kg N eq)
- Terrestrial acidification (kg SO2 eq)
- Ionizing radiation (kBq Co-60 eq)

### LCIA Methods

Choose from multiple assessment methodologies:

**ReCiPe 2016 (Recommended)**
- Comprehensive midpoint and endpoint indicators
- Global applicability
- Well-documented and peer-reviewed
- Best for: Most LCA studies

**ILCD 2011 Midpoint**
- EU Joint Research Centre methodology
- European context
- Policy-oriented indicators
- Best for: European studies, policy analysis

**Environmental Footprint (EF) 3.0**
- Latest EU methodology (2021)
- Aligned with Product Environmental Footprint (PEF)
- Best for: EU market, product labeling

**CML-IA Baseline**
- Classical methodology from Leiden University
- Widely used in academia
- Best for: Academic research, publications

**TRACI 2.1**
- US EPA methodology
- North American context
- Best for: US studies, regulatory compliance

**Other Methods:**
- IMPACT 2002+
- Ecological Scarcity
- USEtox
- EDIP 2003

### Method Selection

**Automatic Mode (Default):**
- AI recommends appropriate method based on:
  - Selected database
  - Geographic scope
  - Study purpose
  - User query context

**Manual Mode:**
- Choose specific method from dropdown
- Override AI recommendations
- Useful for:
  - Following specific methodologies
  - Comparing methods
  - Academic/regulatory requirements

## Hallucination Prevention System

### Problem: AI Fabrication

Without prevention, AI models may "hallucinate" - generate plausible but incorrect data when information isn't found.

### Solution: Multi-Layer Prevention

**1. Empty Search Tracking:**
```python
# System tracks consecutive empty search results
max_empty_searches = 2
empty_search_count = 0

# After each search:
if results_empty:
    empty_search_count += 1
else:
    empty_search_count = 0  # Reset on success
```

**2. Forced Honest Errors:**
After 2 consecutive empty searches, the system:
- Stops the conversation loop
- Forces AI to admit data not found
- Provides database-specific suggestions
- Prevents further action execution

**3. Enhanced AI Instructions:**
System prompts explicitly instruct:
- "NEVER fabricate LCIA numbers"
- "If data not found after 2 attempts, respond honestly"
- "Suggest alternative databases or search terms"
- "Do not make up impact values"

**Example Behavior:**
```
User: "Calculate impact of unicorn horn production"
AI: [Searches ELCD] - 0 results
AI: [Searches again with variations] - 0 results
AI: "I couldn't find any processes for unicorn horn in the ELCD database.
     This material doesn't appear to be in standard LCA databases.
     Would you like to:
     - Try a different material
     - Switch to a different database
     - Describe the process manually"
```

### Benefits

- **Trustworthy Results**: No fabricated impact numbers
- **Honest Communication**: Clear when data unavailable
- **Helpful Guidance**: Suggests alternatives and solutions
- **Data Integrity**: Maintains credibility of LCA assessments

## Multi-Turn Conversation Loop

### How It Works

Traditional chatbots respond once per message. Our multi-turn loop allows the AI to take multiple actions per message:

**Flow:**
```
1. User sends message
2. AI analyzes and decides first action
3. System executes action (search/calculate)
4. AI sees results, decides next action
5. Repeat up to 5 iterations
6. Return final response
```

**Example - Automatic Fallback:**
```
User: "Calculate impact of cement production"

Turn 1: AI searches product systems → 0 results
Turn 2: AI automatically searches processes → 12 results
Turn 3: AI selects best match and calculates → Results returned
Turn 4: AI analyzes results and formats response → Complete
```

### Features Enabled

**Automatic Fallback:**
- Product systems → Processes (seamless)
- Different search terms if first attempt fails
- Alternative databases if current has no data

**Multi-Step Workflows:**
- Search → Calculate → Analyze (single user message)
- Compare multiple processes automatically
- Gather data from multiple sources

**Intelligent Retry:**
- Refine searches based on previous results
- Try variations if exact match not found
- Adapt strategy based on what's available

### Safeguards

- **Max 5 iterations** - Prevents infinite loops
- **Empty search limit** - Stops after 2 failed searches
- **Completion detection** - Stops when goal achieved
- **Error handling** - Breaks loop on critical errors

## Auto and Interactive Modes

### Auto Mode

**Optimized for**: Speed, efficiency, autonomous operation

**Behavior:**
- Makes smart assumptions from context
- Proceeds automatically when 1 result found
- Selects best match when multiple options
- Extracts amounts/units without asking
- Minimal user interaction required

**Best For:**
- Quick assessments
- Routine calculations
- Users familiar with LCA
- Clear, specific requests

**Example:**
```
User: "Calculate impact of 2kg glass fiber"
AI: [Automatically selects best process, uses ReCiPe 2016, calculates]
AI: "Here are the results for 2kg of glass fiber production..."
```

### Interactive Mode

**Optimized for**: Learning, exploration, precision

**Behavior:**
- Asks clarifying questions
- Presents options when multiple results
- Confirms extracted amounts/units
- Explains choices and methodology
- Educational and conversational

**Best For:**
- Learning LCA concepts
- Uncertain requirements
- Exploring databases
- Users new to LCA
- Complex studies

**Example:**
```
User: "Calculate impact of glass fiber"
AI: "I found 8 glass fiber processes. Key options:
     1. Glass fiber mat production, Europe
     2. Glass fiber reinforcement, Global
     3. Chopped glass fiber, RER
     Which would you like to use?"
User: "Number 1"
AI: "How much glass fiber mat do you want to assess?"
User: "2kg"
AI: "Which LCIA method would you like? I recommend ReCiPe 2016
     for comprehensive assessment."
```

### Mode Switching

- Toggle mode anytime via dropdown selector
- Mode preference saved per conversation
- Different system prompts optimized for each mode
- Smooth transition preserves context

## Knowledge-Based Guidance

### LCIA Methods Knowledge Base

**Location**: `backend/knowledge/lcia_methods.json`

**Contains** (14KB):
- Method descriptions and purposes
- Pros and cons of each method
- Appropriate use cases
- Geographic applicability
- Impact categories covered
- Methodological notes

**Example Entry:**
```json
{
  "name": "ReCiPe 2016 Midpoint",
  "description": "Comprehensive impact assessment method",
  "pros": [
    "Covers 18 impact categories",
    "Global applicability",
    "Well-documented methodology"
  ],
  "cons": [
    "Complex for beginners",
    "Requires careful interpretation"
  ],
  "best_for": [
    "Comprehensive product LCA",
    "Academic research",
    "Comparative studies"
  ]
}
```

### Database Guidance Knowledge Base

**Location**: `backend/knowledge/databases_guidance.json`

**Contains** (18KB):
- Database strengths and limitations
- Geographic scope and coverage
- Data quality characteristics
- Typical use cases
- Sector specializations
- Recommendations for specific needs

**Used For:**
- AI-powered database recommendations
- Search failure suggestions
- Method selection guidance
- Context-aware prompts

### Intelligent Recommendations

The system uses knowledge bases to:

**Recommend Methods:**
```python
# AI considers:
- Selected database (e.g., ELCD → recommend ILCD)
- User query context (e.g., food → ReCiPe)
- Geographic scope (e.g., US study → TRACI)
- Study type (e.g., policy → EF 3.0)
```

**Suggest Databases:**
```python
# After empty search in ELCD:
if "food" in query or "agriculture" in query:
    suggest = "Agribalyse"
elif "energy" in query or "electricity" in query:
    suggest = "NEEDS"
elif "US" in query or "United States" in query:
    suggest = "USLCI"
```

## ISO 14044 Compliance

### Goal and Scope Definition

Every calculation automatically generates ISO 14044-compliant Goal & Scope:

**Components:**

1. **Goal of the Study**
   - Auto-inferred from user query
   - Example: "Assess the environmental impact of 2 kg of glass fiber mat production"

2. **Functional Unit**
   - Extracted from calculation parameters
   - Example: "2.0 kg of glass fiber mat"

3. **System Boundary**
   - Based on product system or process scope
   - Example: "Cradle-to-gate: includes raw material extraction, processing, and manufacturing"

4. **LCIA Methodology**
   - Selected or recommended method
   - Example: "ReCiPe 2016 Midpoint (H)"

5. **Intended Audience**
   - Context-based inference
   - Example: "Internal decision-making, product development team"

6. **Key Assumptions**
   - Process-specific parameters
   - Geographic assumptions
   - Technology assumptions

7. **Limitations**
   - Data gaps and uncertainties
   - Scope exclusions
   - Temporal validity

**Display:**
- Shown in Results Panel for every calculation
- Collapsible section for clean interface
- Exportable with results (future feature)

### Compliance Status

**Phase 1** (Implemented):
- ✅ Goal and Scope generation
- ✅ Functional unit definition
- ✅ System boundary documentation
- ✅ LCIA methodology selection

**Phases 2-6** (Planned):
- ⏳ Life Cycle Inventory (LCI) display
- ⏳ Interpretation and analysis tools
- ⏳ Uncertainty analysis
- ⏳ Sensitivity analysis

See [ISO_INTEGRATION_PLAN.md](../ISO_INTEGRATION_PLAN.md) for full roadmap.

## User Interface Components

### ChatPanel

**Location**: Left side of interface

**Components:**
- **ConversationHeader**: Shows current context (database, method, mode, session ID)
- **DatabaseSelector**: Dropdown to choose active database with availability indicators
- **MethodSelector**: Choose LCIA method (auto or manual mode)
- **Mode Toggle**: Switch between Auto and Interactive modes
- **Message Display**: Conversation history with user and AI messages
- **Input Field**: Type natural language queries
- **Send Button**: Submit messages

**Features:**
- Real-time typing indicators
- Error messages with retry options
- Action feedback (searching, calculating, etc.)
- Collapsible selectors for clean interface

### ResultsPanel

**Location**: Right side of interface

**Sections** (all collapsible):

1. **Goal & Scope**
   - ISO 14044-compliant documentation
   - Study parameters and assumptions
   - Expandable for full details

2. **Impact Assessment Results**
   - Impact categories with values and units
   - Color-coded for quick scanning
   - Sortable and filterable

3. **Product System Diagram** (when available)
   - Visual representation of supply chain
   - Expandable for detailed view
   - Process relationships shown

4. **Calculation Metadata**
   - Process/product system used
   - Functional unit
   - LCIA method applied
   - Calculation timestamp
   - Database source

**Features:**
- Expand/collapse all sections with one click
- Clean, readable formatting
- Responsive design for different screen sizes
- Print-friendly layout

### DatabaseSelector

**Features:**
- Dropdown with 6 database options
- Real-time availability checking
- Green (available) / Red (offline) indicators
- Socket-based connection testing (2s timeout)
- Tooltips with database descriptions

**Behavior:**
- Updates conversation context on change
- Preserves history of database switches
- AI aware of current database selection

### MethodSelector

**Modes:**

**Auto Mode (Default):**
- AI selects appropriate method
- Shows "Auto (ReCiPe 2016)" when active
- Changes based on context and database

**Manual Mode:**
- User chooses from available methods
- Dropdown populated from current database
- Overrides AI recommendations
- Useful for specific study requirements

**Features:**
- Toggle between auto and manual
- Method descriptions on hover
- Validation of method availability

### ConversationHeader

**Displays:**
- Current database (e.g., "ELCD 3.2")
- Active LCIA method (e.g., "ReCiPe 2016")
- Chat mode (Auto / Interactive)
- Session ID (for debugging)

**Features:**
- Compact design at top of chat
- Always visible during scroll
- Click to copy session ID

## Additional Features

### Automatic Fallback Strategy

**Product Systems → Processes:**
1. Search product systems first (faster, complete chains)
2. If none found: Automatically search processes
3. If process found: Create product system on-the-fly
4. If neither found: Honest error with suggestions

### Real-time Feedback

**Action Indicators:**
- "Searching processes..." with loading animation
- "Calculating LCIA..." with progress indicator
- "Found X results" with count
- Error messages with retry options

### Conversation Context Management

**Tracks:**
- Message history (user and AI)
- Database selection history with timestamps
- Method selection history (auto vs manual)
- Mode changes (auto vs interactive)
- Calculation results (session-based)

**Benefits:**
- Seamless context across interactions
- Undo/redo capabilities (future)
- Conversation export (future)
- Analytics and insights (future)

### Error Handling

**User-Friendly Messages:**
- Clear explanation of what went wrong
- Suggested actions to resolve
- Database-specific guidance
- Retry options when appropriate

**Example:**
```
Error: "No processes found for 'XYZ' in ELCD"

Suggestions:
- Try different search terms
- Switch to Agribalyse for food products
- Switch to NEEDS for energy systems
- Enable Interactive mode for guided search
```

## Performance Optimization

### Search Optimization

- Keyword indexing for fast full-text search
- Process catalog caching (in-memory)
- Efficient IPC communication with OpenLCA

### Calculation Optimization

- Product system reuse when possible
- Result caching for repeated calculations (session-based)
- Asynchronous calculation execution
- Progress indicators for long operations

### Frontend Optimization

- React component memoization
- Lazy loading of large result sets
- Debounced input for search-as-you-type
- Efficient state management

## Future Features

See [Planned Features](.claude/README.md#planned-featuresimprovements) for full roadmap.

**Short-term:**
- LCI (Life Cycle Inventory) display
- Result export (PDF, Excel, JSON)
- Conversation persistence (database)

**Medium-term:**
- Batch calculations
- Process comparison tools
- Uncertainty analysis
- User authentication

**Long-term:**
- Complete ISO 14040/14044 compliance
- Monte Carlo simulations
- Sensitivity analysis
- Custom impact methods

## Conclusion

The LCA Assistant provides a comprehensive, AI-powered platform for performing Life Cycle Assessments with:

- Natural language interaction
- Multi-database support
- Intelligent guidance
- ISO compliance
- Modern, intuitive interface

For questions or feature requests, please open an issue on GitHub.
