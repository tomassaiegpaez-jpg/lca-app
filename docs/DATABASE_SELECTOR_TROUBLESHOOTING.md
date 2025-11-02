# Database Selector Troubleshooting Guide

## Current Status

✅ **Backend is working**: The `/api/databases` endpoint returns correct data
✅ **CORS is configured**: Proper headers are being sent
✅ **ELCD database is detected**: Shows as `available: true`
✅ **Chat calculations work**: Backend communication is functional

❌ **Database selector shows**: "Unable to load databases"

---

## Diagnostic Steps

### Step 1: Open Browser Console
1. Open your browser to http://localhost:5173
2. Press **F12** (or right-click → Inspect)
3. Go to the **Console** tab
4. Look for messages starting with `[DatabaseSelector]`

You should see something like:
```
[DatabaseSelector] Fetching from http://localhost:8000/api/databases
[DatabaseSelector] Response status: 200
[DatabaseSelector] Received data: {databases: Array(6)}
[DatabaseSelector] Successfully loaded 6 databases
```

### Step 2: Check for Errors

If you see **RED error messages**, please note what they say. Common issues:

#### Error: "Failed to fetch" or "Network error"
**Possible causes:**
- Browser is blocking the request
- Backend not accessible from browser
- Firewall or antivirus blocking connection

**Fix:**
Try accessing http://localhost:8000/api/databases directly in your browser. You should see JSON data.

#### Error: "CORS policy"
**Fix:** The CORS configuration should be correct, but if you see this, the backend may need to be restarted:
```bash
# Kill the backend process and restart
pkill -f uvicorn
cd /home/teespy/projects/lca-app/backend
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Error: "Invalid response format"
This means the backend is returning unexpected data. Check the backend logs.

---

## Quick Tests

### Test 1: Direct Backend Access
Open this URL in your browser:
```
http://localhost:8000/api/databases
```

**Expected result:** JSON data showing 6 databases, with ELCD marked as available.

**If this works:** The backend is fine. The issue is in the frontend component.

**If this doesn't work:** The backend might not be accessible from your browser (different network context).

---

### Test 2: Check Network Tab
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Look for a request to `databases`
5. Click on it to see:
   - Status code (should be 200)
   - Response data
   - Any error messages

---

## Common Scenarios

### Scenario A: Request not even made
If you don't see `[DatabaseSelector] Fetching...` in console:
- The component might not be rendering
- JavaScript error preventing execution
- Check for any RED errors in console

### Scenario B: Request made but fails
If you see the fetch attempt but it fails:
- Check the exact error message
- Check Network tab for HTTP status code
- Could be a CORS issue or backend not responding

### Scenario C: Request succeeds but shows error anyway
If console shows "Successfully loaded" but UI shows error:
- This would be very strange
- Possible React state issue
- Try hard refresh (Ctrl+Shift+R)

---

## Temporary Workaround

If the selector doesn't work but calculations do, you can:
1. Ignore the selector (it will default to ELCD anyway)
2. The chat interface will use ELCD database
3. Calculations will work normally

The database selector is just a UI convenience - the underlying functionality works fine.

---

## System Information Needed

If the issue persists, please provide:

1. **Browser console output** (copy all `[DatabaseSelector]` messages and any errors)
2. **Network tab screenshot** (showing the request to /api/databases)
3. **What happens when you visit** http://localhost:8000/api/databases **directly**
4. **Your operating system** and browser version

---

## Next Steps

1. ✅ I've added detailed logging to the DatabaseSelector component
2. ✅ Frontend will now show specific error messages (not just "Unable to load databases")
3. 📋 Please refresh the page and check browser console
4. 📋 Share what you see in the console

The logging will tell us exactly where and why it's failing!
