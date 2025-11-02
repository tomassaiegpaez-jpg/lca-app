# LCA Assistant - Troubleshooting Guide

Complete troubleshooting guide for common issues and their solutions.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [OpenLCA Connection Issues](#openlca-connection-issues)
4. [Database Issues](#database-issues)
5. [Frontend Issues](#frontend-issues)
6. [API Errors](#api-errors)
7. [Calculation Errors](#calculation-errors)
8. [Performance Issues](#performance-issues)
9. [Known Bugs and Fixes](#known-bugs-and-fixes)
10. [Getting Help](#getting-help)

## Quick Diagnostics

### Health Check Checklist

Run these quick checks to diagnose common issues:

```bash
# 1. Check backend is running
curl http://localhost:8000/
# Expected: {"status": "healthy", ...}

# 2. Check database availability
curl http://localhost:8000/api/databases
# Expected: List of databases with "available": true

# 3. Check OpenLCA connection (from backend directory)
cd backend
source venv/bin/activate
python test_connection.py
# Expected: "Connected to OpenLCA successfully!"

# 4. Check frontend is running
curl http://localhost:5173/
# Expected: HTML content

# 5. Check for port conflicts
# Linux/macOS:
lsof -i :8000
lsof -i :5173
lsof -i :8080
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :5173
netstat -ano | findstr :8080
```

### Quick Restart

Often resolves transient issues:

```bash
# 1. Stop all services (Ctrl+C in each terminal)

# 2. Restart OpenLCA IPC server
# In OpenLCA: Window → Developer tools → IPC Server → Start

# 3. Restart backend
cd backend
source venv/bin/activate
python app.py

# 4. Restart frontend
cd frontend
npm run dev
```

## Installation Issues

### Python Virtual Environment Not Found

**Symptom:**
```bash
bash: venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Create virtual environment
cd backend
python -m venv venv

# If python3 needed:
python3 -m venv venv

# Verify creation
ls venv/
# Should see: bin/ include/ lib/ pyvenv.cfg
```

---

### pip install Fails

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**

**1. Update pip:**
```bash
pip install --upgrade pip
```

**2. Use specific Python version:**
```bash
# Requires Python 3.11+
python3.11 -m pip install -r requirements.txt
```

**3. Install problematic packages individually:**
```bash
# Often olca-ipc or anthropic
pip install olca-ipc
pip install anthropic
pip install -r requirements.txt
```

**4. Check internet connection:**
```bash
pip install --verbose anthropic
```

---

### ModuleNotFoundError After Installation

**Symptom:**
```python
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Virtual environment not activated

**Solution:**
```bash
# Activate venv FIRST
cd backend
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Verify activation (should show venv)
which python
# Expected: /path/to/backend/venv/bin/python

# Then run app
python app.py
```

---

### npm install Fails

**Symptom:**
```
npm ERR! code ENOTFOUND
```

**Solutions:**

**1. Check Node.js version:**
```bash
node --version
# Required: v18.0.0 or higher

# Update if needed
nvm install 18
nvm use 18
```

**2. Clear npm cache:**
```bash
npm cache clean --force
npm install
```

**3. Delete node_modules and retry:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**4. Use different registry (if corporate network):**
```bash
npm config set registry https://registry.npmjs.org/
npm install
```

## OpenLCA Connection Issues

### Connection Refused Error

**Symptom:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Diagnostic Steps:**

**1. Verify OpenLCA IPC Server is Running:**
- Open OpenLCA application
- Go to: `Window → Developer tools → IPC Server`
- Check that "Server is running" message is shown
- Note the port number (default: 8080)

**2. Check Port Configuration:**
```bash
# In .env file
OPENLCA_PORT=8080  # Must match OpenLCA IPC server port
```

**3. Test Port Accessibility:**
```bash
# Linux/macOS:
nc -zv localhost 8080
# Expected: "Connection to localhost 8080 port [tcp/*] succeeded!"

# Windows:
Test-NetConnection -ComputerName localhost -Port 8080
```

**4. For WSL2 Users:**

WSL2 requires special network configuration:

```bash
# Get Windows host IP from WSL2
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
# Example output: 172.26.192.1

# Update .env
OPENLCA_HOST=172.26.192.1  # Use IP from above, NOT localhost
OPENLCA_PORT=8080
```

**5. Check Windows Firewall (WSL2):**

Windows Firewall may block WSL2 connections:

```powershell
# In PowerShell (Administrator):
New-NetFirewallRule -DisplayName "OpenLCA IPC" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

---

### Database Not Available

**Symptom:**
```json
{
  "databases": [
    {
      "id": "elcd",
      "available": false
    }
  ]
}
```

**Diagnostic Steps:**

**1. Check OpenLCA has Database Open:**
- In OpenLCA Navigation panel, verify database is open
- Database name should be visible (not grayed out)
- Right-click database → Properties to verify

**2. Verify IPC Server Port Matches:**
```bash
# Check backend/config/databases.json
{
  "databases": [
    {
      "id": "elcd",
      "port": 8080  # Must match OpenLCA IPC port
    }
  ]
}
```

**3. Test Connection Manually:**
```bash
cd backend
source venv/bin/activate
python test_connection.py
```

**4. Check for Port Conflicts:**
```bash
# Linux/macOS:
lsof -i :8080
# Windows:
netstat -ano | findstr :8080
```

If another process is using port 8080:
- Stop the conflicting process, OR
- Change OpenLCA IPC server to different port, OR
- Update configuration to match

---

### Timeout Errors

**Symptom:**
```
TimeoutError: Database availability check timed out after 2s
```

**Causes:**
- OpenLCA IPC server slow to respond
- Database very large (loading time)
- Network latency (WSL2)

**Solutions:**

**1. Increase Timeout (temporary):**

Edit `backend/services/database_manager.py`:
```python
# Find check_availability function
sock.settimeout(5.0)  # Increase from 2.0 to 5.0
```

**2. Optimize OpenLCA:**
- Close unnecessary databases
- Increase OpenLCA memory:
  - Edit `openLCA.ini`
  - Set: `-Xmx4G` (4GB RAM) or higher

**3. Verify Database Integrity:**
- In OpenLCA: `Tools → Database validation`
- Repair any issues found

## Database Issues

### "Unable to Load Databases" in Frontend

**Symptom:**
Database selector shows error: "Unable to load databases"

**Diagnostic Steps:**

**1. Verify Backend is Running:**
```bash
curl http://localhost:8000/api/databases
```

If connection fails:
- Check backend terminal for errors
- Restart backend: `python app.py`

**2. Check Browser Console:**
- Open browser DevTools (F12)
- Go to Console tab
- Look for CORS or network errors

**3. Check CORS Configuration:**

Edit `backend/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Verify this matches frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**4. Test Backend Endpoint Directly:**
```bash
curl -v http://localhost:8000/api/databases
```

Look for:
- `200 OK` status
- Valid JSON response
- No error messages

See [DATABASE_SELECTOR_TROUBLESHOOTING.md](DATABASE_SELECTOR_TROUBLESHOOTING.md) for detailed guide.

---

### Process Search Returns Empty

**Symptom:**
Search for processes returns 0 results, but you know they exist

**Solutions:**

**1. Try Different Search Terms:**
```
Instead of: "fiberglass"
Try: "glass fiber", "glass fibre", "GF"
```

**2. Switch Databases:**
- Material might be in different database
- Food products → Agribalyse
- Energy systems → NEEDS
- US processes → USLCI

**3. Check Database Import:**
- Verify database fully imported in OpenLCA
- Go to Navigation panel → Processes
- Manually search in OpenLCA

**4. Enable Interactive Mode:**
- AI will ask clarifying questions
- Helps refine search terms

---

### Wrong Database Selected

**Symptom:**
Calculations using wrong database despite selection

**Cause:** Frontend state not updating backend requests

**Solutions:**

**1. Hard Refresh Frontend:**
```bash
# In browser:
Ctrl+Shift+R  (Linux/Windows)
Cmd+Shift+R   (macOS)
```

**2. Check Conversation Context:**
- Look at ConversationHeader
- Verify correct database shown

**3. Start New Conversation:**
- Refresh page (loses history)
- Select database again

**4. Check Backend Logs:**
```bash
# In backend terminal, look for:
INFO: Using database: elcd
```

## Frontend Issues

### White Screen / Blank Page

**Symptom:**
Browser shows blank page after loading

**Solutions:**

**1. Check Browser Console:**
```
F12 → Console tab
Look for JavaScript errors
```

**2. Verify Frontend is Running:**
```bash
curl http://localhost:5173/
# Should return HTML
```

**3. Clear Browser Cache:**
```
Ctrl+Shift+Delete → Clear cache
```

**4. Check Vite Dev Server:**
```bash
cd frontend
npm run dev

# Look for:
# ✓ ready in XXX ms
# ➜ Local: http://localhost:5173/
```

**5. Rebuild:**
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run dev
```

---

### Results Not Displaying

**Symptom:**
Chat works, but results panel stays empty

**Solutions:**

**1. Check Browser Console:**
Look for:
- JavaScript errors
- React component errors
- Failed API calls

**2. Verify API Response:**
```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/api/lca/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "database_id": "elcd"}'
```

**3. Check ResultsPanel State:**
- Add `console.log(results)` in `ResultsPanel.jsx`
- Verify results object has expected structure

**4. Check CSS:**
- Results might be hidden by CSS
- Inspect element (F12 → Elements)
- Look for `display: none` or `opacity: 0`

---

### Slow UI Response

**Symptom:**
UI feels sluggish or unresponsive

**Solutions:**

**1. Check Backend Response Time:**
```bash
time curl -X POST "http://localhost:8000/api/lca/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "database_id": "elcd"}'
```

If slow (>5 seconds):
- OpenLCA might be slow
- Database too large
- Complex calculations

**2. Check Browser Performance:**
- Open DevTools → Performance tab
- Record interaction
- Look for long tasks

**3. Reduce Data Load:**
- Use `limit` parameter in searches
- Collapse result sections not in use
- Clear conversation history

**4. Optimize Backend:**
- Increase OpenLCA memory
- Use faster database (ELCD faster than ecoinvent)
- Consider caching (future feature)

## API Errors

### 400 Bad Request

**Symptom:**
```json
{
  "detail": "Invalid request body"
}
```

**Causes:**
- Missing required fields
- Wrong data types
- Invalid JSON

**Solution:**
```bash
# Validate JSON
echo '{"message": "test"}' | python -m json.tool

# Check required fields for endpoint
curl http://localhost:8000/docs
```

---

### 404 Not Found

**Symptom:**
```json
{
  "detail": "Process with ID 'xyz' not found"
}
```

**Solutions:**

**1. Verify ID Exists:**
```bash
# Search for process first
curl -X POST "http://localhost:8000/api/databases/elcd/processes/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "glass fiber", "limit": 10}'

# Use ID from search results
```

**2. Check Database:**
- Process might be in different database
- Try searching in OpenLCA manually

**3. Verify Database is Available:**
```bash
curl http://localhost:8000/api/databases
# Check "available": true for target database
```

---

### 500 Internal Server Error

**Symptom:**
```json
{
  "detail": "Internal server error"
}
```

**Diagnostic Steps:**

**1. Check Backend Terminal:**
- Look for full error traceback
- Note which line failed

**2. Common Causes:**

**OpenLCA Connection Lost:**
```
Solution: Restart OpenLCA IPC server
```

**Claude API Error:**
```
Check: ANTHROPIC_API_KEY in .env
Check: API quota not exceeded
Solution: Verify API key, check billing
```

**Calculation Error:**
```
Check: Process has valid reference flow
Check: Method compatible with database
Solution: Try different process/method
```

**3. Enable Debug Logging:**

Edit `backend/app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**4. Test Individual Components:**
```bash
# Test OpenLCA
python backend/test_connection.py

# Test Claude API
python -c "from anthropic import Anthropic; client = Anthropic(); print('OK')"
```

See [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) for specific bug fixes.

## Calculation Errors

### "Product System Could Not Be Created"

**Symptom:**
```
LCIA calculation failed: Product system could not be created
```

**Causes:**
- Process missing reference flow
- Circular dependencies
- Incomplete process data

**Solutions:**

**1. Try Different Process:**
- Search for similar processes
- Use product system instead of process

**2. Check Process in OpenLCA:**
- Open process in OpenLCA
- Verify "Quantitative reference" is set
- Check for red error indicators

**3. Use Existing Product System:**
```python
# Instead of calculate_lcia (creates PS)
# Use calculate_lcia_ps (existing PS)
```

**4. Manual Product System Creation:**
- Create product system in OpenLCA manually
- Right-click process → "Create product system"
- Configure linking options

---

### "Method Not Compatible"

**Symptom:**
```
LCIA method not available for this database
```

**Solutions:**

**1. Check Available Methods:**
```bash
curl "http://localhost:8000/api/databases/elcd/impact-methods"
```

**2. Use Method from List:**
- Copy method ID from response
- Use in calculation request

**3. Import Method to Database:**
- In OpenLCA: `File → Import`
- Import LCIA method package
- Restart IPC server

**4. Use Auto Method Selection:**
```json
{
  "method_selection_mode": "auto"
}
```
AI will pick compatible method automatically.

---

### Results All Zero

**Symptom:**
All impact categories show 0.0

**Causes:**
- Wrong functional unit
- Process has no characterization factors
- Method-database mismatch

**Solutions:**

**1. Check Functional Unit:**
```json
{
  "amount": 1.0,  # Not 0
  "unit": "kg"    # Verify correct unit
}
```

**2. Try Different Method:**
- Some methods missing factors for certain flows
- Use ReCiPe 2016 (most comprehensive)

**3. Verify in OpenLCA:**
- Run same calculation in OpenLCA GUI
- Compare results
- If also zero in OpenLCA, it's a data issue

**4. Check Process Exchanges:**
- Process might have incomplete data
- Elementary flows might be missing
- Try more complete process

## Performance Issues

### Slow Calculations

**Symptom:**
LCIA calculations take >30 seconds

**Solutions:**

**1. Use Product Systems:**
- Pre-built product systems much faster
- Avoid creating PS from unit processes

**2. Increase OpenLCA Memory:**

Edit `openLCA.ini`:
```ini
-Xmx4G  # Increase to 4GB or more
```

**3. Optimize Database:**
- Smaller databases faster (ELCD < ecoinvent)
- Remove unused databases

**4. Use Simpler Methods:**
- ReCiPe faster than IMPACT 2002+
- Midpoint faster than Endpoint

**5. Reduce Calculation Scope:**
- Use "LCI result" instead of "System process"
- Limit supply chain depth

---

### High Memory Usage

**Symptom:**
System running out of memory

**Solutions:**

**1. Limit OpenLCA Memory:**
```ini
# In openLCA.ini
-Xmx2G  # Don't exceed 50% of system RAM
```

**2. Close Unused Databases:**
- Only keep active database open in OpenLCA

**3. Restart Services Periodically:**
```bash
# After many calculations
# Restart backend and OpenLCA
```

**4. Use Single Database Mode:**
- Run one OpenLCA instance
- Switch databases as needed

---

### API Timeouts

**Symptom:**
Requests timeout after 30-60 seconds

**Solutions:**

**1. Increase Timeout:**

Edit `frontend/src/App.jsx`:
```javascript
const response = await fetch('/api/lca/chat', {
  signal: AbortSignal.timeout(120000)  // 2 minutes
});
```

**2. Use Async Calculation Pattern:**
- Submit calculation
- Poll for results
- Display progress indicator

**3. Break into Smaller Requests:**
- Instead of comparing 10 processes
- Compare 2-3 at a time

## Known Bugs and Fixes

### Bug: Database Availability Check Hangs

**Fixed**: November 1, 2025

**Symptom:** `/api/databases` endpoint hangs indefinitely

**Solution:** Implemented socket-based check with 2s timeout

**Reference:** [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) line 45-78

---

### Bug: Chat Endpoint Crashes with "module object is not callable"

**Fixed**: November 1, 2025

**Symptom:** `TypeError: 'module' object is not callable`

**Solution:** Fixed scope issue with `re` and `json` imports

**Reference:** [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) line 112-145

---

### Bug: Wrong LCIA Method Used

**Fixed**: November 1, 2025

**Symptom:** Calculations use incorrect method despite selection

**Solution:** Proper method tracking in ConversationContext

**Reference:** [DATABASE_SELECTION_FIXES.md](DATABASE_SELECTION_FIXES.md)

---

### Known Issue: Conversations Not Persisted

**Status**: Not yet fixed

**Symptom:** Conversation history lost on server restart

**Workaround:** Keep backend running during work session

**Planned Fix:** Database persistence (next sprint)

---

### Known Issue: No Result Export

**Status**: Not yet implemented

**Symptom:** Can't download results as PDF/Excel

**Workaround:** Copy results from UI

**Planned Fix:** Export functionality (short-term roadmap)

## Getting Help

### Before Asking for Help

1. **Check this guide** - Most issues covered here
2. **Review error messages** - Often self-explanatory
3. **Check browser console** - F12 → Console for frontend issues
4. **Check backend logs** - Terminal running `python app.py`
5. **Try quick restart** - See [Quick Restart](#quick-restart)

### Information to Provide

When reporting issues, include:

```
**Environment:**
- OS: [e.g., Ubuntu 22.04, Windows 11, WSL2]
- Python version: [python --version]
- Node version: [node --version]
- OpenLCA version: [e.g., 2.0.3]

**Error:**
- What you were trying to do
- Full error message
- Backend terminal output
- Browser console errors (if applicable)

**Steps to Reproduce:**
1. Start backend
2. Open frontend
3. Click X
4. Error appears

**Configuration:**
- Database: [e.g., ELCD, Agribalyse]
- Mode: [Auto or Interactive]
- Method: [e.g., ReCiPe 2016]
```

### Where to Get Help

1. **Documentation:**
   - [SETUP.md](SETUP.md) - Installation
   - [FEATURES.md](FEATURES.md) - Features
   - [API.md](API.md) - API reference
   - [RECENT_FEATURES.md](RECENT_FEATURES.md) - New features

2. **GitHub Issues:**
   - Search existing issues first
   - Open new issue with template
   - Include all requested information

3. **OpenLCA Forum:**
   - For OpenLCA-specific questions
   - https://ask.openlca.org/

4. **Anthropic Support:**
   - For Claude API issues
   - https://support.anthropic.com/

### Debug Mode

Enable verbose logging for detailed diagnostics:

**Backend:**
```python
# Edit backend/app.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Frontend:**
```javascript
// Edit frontend/src/App.jsx
// Add before return statement:
console.log('State:', { databases, results, messages });
```

Run with debug output and include in issue report.

## Additional Resources

- **OpenLCA Documentation**: https://www.openlca.org/learning/
- **OpenLCA IPC API**: https://greendelta.github.io/openLCA-ApiDoc/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Anthropic API**: https://docs.anthropic.com/

---

**Last Updated**: November 2, 2025

**Still having issues?** Open an issue on GitHub with detailed information.
