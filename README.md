# LCA Assistant

> AI-powered Life Cycle Assessment tool combining OpenLCA with Claude AI

An intelligent conversational interface for performing Life Cycle Assessments (LCA) with support for multiple databases, automatic fallback strategies, and ISO 14044-compliant reporting.

## Features

- 🔄 **Multi-Database Support** - Switch between 6 LCA databases (ELCD, Agribalyse, USLCI, LCA Commons, ecoinvent, NEEDS)
- 🤖 **AI-Guided Workflow** - Claude AI assistant with hallucination prevention and intelligent recommendations
- 📊 **ISO 14044 Compliance** - Auto-generated Goal & Scope for every calculation
- 🎯 **Dual Modes** - Auto mode for speed, Interactive mode for learning
- 📈 **Complete LCIA** - 15+ impact categories with multiple assessment methods
- 🔍 **Smart Fallback** - Automatic retry from product systems to processes
- 💡 **Knowledge-Based Guidance** - Expert recommendations for methods and databases
- 🎨 **Modern UI** - Real-time chat interface with results visualization

## Quick Start

### Prerequisites

- **OpenLCA** 2.0+ installed with IPC Server enabled
- **Python** 3.11+
- **Node.js** 18+
- **Anthropic API Key** (Claude AI)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd lca-app

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start backend
python app.py
# Backend runs on http://localhost:8000

# Frontend setup (in a new terminal)
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### OpenLCA Setup

1. Open OpenLCA desktop application
2. Import at least one database (ELCD recommended for testing)
3. Go to: `Window → Developer tools → IPC Server`
4. Start server on port `8080` (ELCD) or other ports per `backend/config/databases.json`
5. Verify connection: `python backend/test_connection.py`

## Usage

### Basic Workflow

1. Open http://localhost:5173 in your browser
2. Select a database from the dropdown (ELCD, Agribalyse, etc.)
3. Choose a mode:
   - **Auto**: AI makes smart assumptions, proceeds automatically
   - **Interactive**: AI asks questions when clarification needed
4. Ask in natural language: *"Calculate the environmental impact of producing 2kg of glass fiber"*
5. View results in the right panel with impact categories and Goal & Scope

### Example Queries

```
"I want to assess the impact of cement production"
"Calculate LCIA for 5kg of steel"
"What's the environmental footprint of 1 ton of concrete?"
"Compare glass fiber and carbon fiber"
```

### Multi-Database Selection

Different databases have different strengths:
- **ELCD**: European processes, industrial materials
- **Agribalyse**: Food and agriculture products
- **USLCI**: US-specific processes
- **LCA Commons**: US Federal LCA data
- **ecoinvent**: Comprehensive global database
- **NEEDS**: Energy systems

The AI will suggest switching databases if data isn't found in your current selection.

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[Features](docs/FEATURES.md)** - Complete feature documentation
- **[Architecture](.claude/README.md)** - System design and technical details
- **[Recent Features](docs/RECENT_FEATURES.md)** - Nov 2025 updates (hallucination prevention, multi-turn loop)
- **[API Reference](docs/API.md)** - API endpoint documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Architecture

```
Frontend (React/Vite)  ←→  Backend (FastAPI)  ←→  OpenLCA IPC Servers
      :5173                    :8000                  :8080-8085
                                  ↓
                           Claude AI API
                                  ↓
                         Knowledge Bases
                    (Methods + Database Guidance)
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- olca-ipc (OpenLCA integration)
- anthropic (Claude AI SDK)
- In-memory conversation management

**Frontend:**
- React 19 + Vite 7
- Component-based architecture
- Vanilla CSS with purple/blue gradient theme

## Recent Updates (Nov 1-2, 2025)

✅ **Hallucination Prevention** - AI no longer fabricates results when data not found
✅ **Multi-Turn Conversation Loop** - Automatic fallback behavior (max 5 iterations)
✅ **Auto/Interactive Modes** - Two AI behavior modes for different user needs
✅ **Knowledge-Based Guidance** - Expert recommendations for methods and databases
✅ **Conversation Context** - Rich state tracking (database, method, mode changes)
✅ **Database-Specific Suggestions** - Intelligent error messages with recommendations

## Project Status

**Current Version**: v0.2.0 (Multi-Database Support)
**Status**: Operational, under active development
**Last Updated**: November 2, 2025

### What's Working

- Multi-database support (6 databases)
- AI-powered conversational interface
- LCIA calculations with 15+ impact categories
- Goal & Scope auto-generation
- Automatic fallback strategies
- Hallucination prevention
- Real-time database/method/mode switching

### Known Limitations

- Conversations not persisted (lost on restart)
- No user authentication
- No automated test suite
- No caching (repeated queries hit OpenLCA)
- No export functionality (PDF/Excel)

See [Planned Features](.claude/README.md#planned-featuresimprovements) for roadmap.

## Contributing

Contributions are welcome! Please:

1. Check existing issues or create a new one
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Troubleshooting

### Database selector shows "Unable to load databases"
- Check that backend is running on http://localhost:8000
- Verify OpenLCA IPC server is started
- Check ports in `backend/config/databases.json` match OpenLCA
- See [DATABASE_SELECTOR_TROUBLESHOOTING.md](docs/DATABASE_SELECTOR_TROUBLESHOOTING.md)

### Chat returns 500 error
- Check OpenLCA IPC connection: `python backend/test_connection.py`
- Verify ANTHROPIC_API_KEY is set in `.env`
- Check backend logs for detailed error messages
- See [DIAGNOSTIC_REPORT.md](docs/DIAGNOSTIC_REPORT.md)

### No results found
- Try different search terms
- Check if database has relevant data
- Switch to different database (AI will suggest appropriate options)
- Use Interactive mode for guided assistance

## License

[Add your license here]

## Acknowledgments

- **OpenLCA** - Open-source LCA software (https://www.openlca.org/)
- **Anthropic** - Claude AI API
- **GreenDelta** - OpenLCA IPC API and documentation

## Contact

[Add your contact information here]

---

**Built with ❤️ for sustainable engineering and environmental assessment**
