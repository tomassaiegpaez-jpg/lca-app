# LCA Assistant - Setup Guide

Complete installation and configuration guide for the LCA Assistant application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [OpenLCA Setup](#openlca-setup)
3. [Backend Installation](#backend-installation)
4. [Frontend Installation](#frontend-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Multi-Database Setup](#multi-database-setup)
8. [Common Issues](#common-issues)

## Prerequisites

### Required Software

- **OpenLCA** 2.0 or higher
  - Download from: https://www.openlca.org/download/
  - Windows 10/11 recommended for best compatibility

- **Python** 3.11 or higher
  - Download from: https://www.python.org/downloads/
  - Ensure pip is installed
  - Add Python to PATH during installation

- **Node.js** 18 or higher
  - Download from: https://nodejs.org/
  - LTS version recommended
  - Includes npm package manager

- **Anthropic API Key**
  - Sign up at: https://console.anthropic.com/
  - Create an API key for Claude access
  - Free tier available with rate limits

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for databases
- **Network**: Internet connection for API calls
- **OS**: Windows 10/11, Linux (WSL2), or macOS

## OpenLCA Setup

### 1. Install OpenLCA

1. Download OpenLCA installer for your platform
2. Run installer with default settings
3. Launch OpenLCA application

### 2. Import LCA Database

You need at least one LCA database. For testing, start with ELCD:

1. Download ELCD database (zolca format):
   - Option A: Via OpenLCA menu: `File → Import → Linked Data (JSON-LD)`
   - Option B: Download from: https://nexus.openlca.org/databases

2. Import the database:
   - In OpenLCA, go to `File → Restore database`
   - Select the downloaded .zolca file
   - Wait for import to complete (may take 5-15 minutes)

3. Verify import:
   - Check that database appears in Navigation panel
   - Expand database to see Processes, Flows, etc.

### 3. Enable IPC Server

The IPC (Inter-Process Communication) server allows external applications to communicate with OpenLCA:

1. In OpenLCA menu bar: `Window → Developer tools → IPC Server`
2. Set port to `8080` (or note custom port for configuration)
3. Click **Start** button
4. Verify "Server is running" message appears
5. Keep OpenLCA running with IPC server active

**Note**: You'll need to start the IPC server each time you launch OpenLCA.

### 4. Multi-Database Configuration (Optional)

For multiple databases, start separate OpenLCA instances:

| Database | Port | Setup |
|----------|------|-------|
| ELCD | 8080 | Primary instance |
| Agribalyse | 8081 | Second instance on different port |
| USLCI | 8082 | Third instance |
| LCA Commons | 8083 | Fourth instance |
| ecoinvent | 8084 | Fifth instance |
| NEEDS | 8085 | Sixth instance |

See [LCA_COMMONS_SETUP_GUIDE.md](LCA_COMMONS_SETUP_GUIDE.md) for database-specific instructions.

## Backend Installation

### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd lca-app
```

### 2. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal prompt.

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- uvicorn (ASGI server)
- olca-ipc (OpenLCA client)
- anthropic (Claude AI SDK)
- Other supporting packages

### 4. Configure Environment

Create a `.env` file in the `backend/` directory:

```bash
# Copy example file if available, or create new file
touch .env
```

Add the following configuration:

```env
# Anthropic API Key (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# OpenLCA IPC Configuration
OPENLCA_HOST=172.26.192.1  # For WSL2, use Windows host IP
OPENLCA_PORT=8080           # Match OpenLCA IPC server port

# Optional: Logging level
LOG_LEVEL=INFO
```

**Finding Windows host IP for WSL2:**
```bash
# In WSL2 terminal:
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

**For native Linux/macOS:**
```env
OPENLCA_HOST=localhost
```

### 5. Verify Backend Setup

```bash
# Still in backend/ directory with venv activated
python test_connection.py
```

Expected output:
```
Connected to OpenLCA successfully!
Database: ELCD 3.2
Processes found: 3841
```

If you see errors, see [Common Issues](#common-issues) below.

### 6. Start Backend Server

```bash
# Start FastAPI server
python app.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Backend is now running at http://localhost:8000

## Frontend Installation

### 1. Navigate to Frontend Directory

Open a **new terminal** (keep backend running):

```bash
cd lca-app/frontend
```

### 2. Install Dependencies

```bash
# Install Node.js packages
npm install
```

This installs:
- React 19
- Vite 7 (build tool)
- Supporting UI libraries

### 3. Start Development Server

```bash
# Start Vite dev server
npm run dev
```

You should see:
```
  VITE v7.1.7  ready in 543 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Frontend is now running at http://localhost:5173

## Configuration

### Database Configuration

Edit `backend/config/databases.json` to add or modify databases:

```json
{
  "databases": [
    {
      "id": "elcd",
      "name": "ELCD 3.2",
      "description": "European Life Cycle Database",
      "port": 8080,
      "host": "172.26.192.1",
      "capabilities": {
        "has_product_systems": true,
        "has_lcia_methods": true,
        "regions": ["EU"]
      }
    }
  ]
}
```

### Knowledge Base Configuration

The application uses JSON knowledge bases for guidance:

- `backend/knowledge/lcia_methods.json` - LCIA method guidance
- `backend/knowledge/databases_guidance.json` - Database recommendations

These files are pre-configured and typically don't need editing.

## Verification

### 1. Test Backend Health

```bash
# In a new terminal:
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "LCA API is running"
}
```

### 2. Test Database Connection

```bash
curl http://localhost:8000/api/databases
```

You should see a list of configured databases with availability status.

### 3. Test Frontend

1. Open browser to http://localhost:5173
2. You should see the LCA Assistant interface
3. Database selector should show available databases
4. Chat input should be enabled

### 4. End-to-End Test

1. In the web interface, select a database (e.g., ELCD)
2. Type a query: "Calculate the impact of 1kg of glass fiber"
3. Press Enter or click Send
4. Verify:
   - AI responds with search results
   - Results panel shows impact categories
   - Goal & Scope section is populated

## Multi-Database Setup

### Running Multiple OpenLCA Instances

To use multiple databases simultaneously:

1. **Copy OpenLCA Installation** (recommended approach):
   ```bash
   # On Windows, copy entire OpenLCA folder
   C:\OpenLCA\ → C:\OpenLCA_DB2\
   ```

2. **Start First Instance** (port 8080):
   - Open first OpenLCA with ELCD database
   - Enable IPC server on port 8080

3. **Start Second Instance** (port 8081):
   - Open second OpenLCA from copied folder
   - Open Agribalyse database
   - Enable IPC server on port 8081

4. **Repeat for Additional Databases**

### Alternative: Single Instance with Database Switching

If you can't run multiple instances:

1. Use single OpenLCA instance
2. Import all databases
3. Switch databases in OpenLCA as needed
4. Restart IPC server after switching

**Note**: This approach requires manual switching and IPC server restarts.

## Common Issues

### "Connection refused" Error

**Symptom**: Backend can't connect to OpenLCA

**Solutions**:
1. Verify OpenLCA IPC server is running
2. Check port number matches configuration
3. For WSL2, verify Windows host IP is correct:
   ```bash
   cat /etc/resolv.conf | grep nameserver
   ```
4. Check Windows firewall isn't blocking port

### "Unable to load databases"

**Symptom**: Frontend shows error loading databases

**Solutions**:
1. Verify backend is running (http://localhost:8000)
2. Check browser console for errors (F12 → Console)
3. Test backend endpoint: `curl http://localhost:8000/api/databases`
4. See [DATABASE_SELECTOR_TROUBLESHOOTING.md](DATABASE_SELECTOR_TROUBLESHOOTING.md)

### Import Errors (Python)

**Symptom**: `ModuleNotFoundError` when starting backend

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Port Already in Use

**Symptom**: `Address already in use` error

**Solutions**:
1. Check if another process is using the port:
   ```bash
   # Linux/macOS:
   lsof -i :8000
   # Windows:
   netstat -ano | findstr :8000
   ```
2. Kill existing process or use different port
3. For backend, edit port in `app.py`
4. For frontend, Vite will auto-increment port

### ANTHROPIC_API_KEY Error

**Symptom**: `API key not found` error

**Solutions**:
1. Verify `.env` file exists in `backend/` directory
2. Check API key format starts with `sk-ant-api03-`
3. Ensure no extra spaces in `.env` file
4. Restart backend after editing `.env`

## Next Steps

After successful setup:

1. Read [FEATURES.md](FEATURES.md) for feature documentation
2. Review [API.md](API.md) for API endpoint reference
3. Check [RECENT_FEATURES.md](RECENT_FEATURES.md) for latest updates
4. Join community or report issues

## Additional Resources

- **OpenLCA Documentation**: https://www.openlca.org/learning/
- **OpenLCA IPC API**: https://greendelta.github.io/openLCA-ApiDoc/
- **Anthropic API Docs**: https://docs.anthropic.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/

## Support

For issues not covered here:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) for known bugs
3. Open an issue on GitHub with:
   - Error messages
   - System information
   - Steps to reproduce
