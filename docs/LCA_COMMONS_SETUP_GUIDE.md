# LCA Commons 2025 (USLCI) Setup Guide

## Download Complete! ✅

I've downloaded the **USLCI Database (LCA Commons Q3 2025)** for you.

**File location:** `/home/teespy/projects/lca-app/backend/data/uslci_2025_q3.zolca`
**File size:** 20 MB
**Version:** FY25 Q3 (September 2025) - Latest release!

---

## Step-by-Step Setup

### Step 1: Open openLCA Desktop

1. Launch the openLCA desktop application
2. Make sure you have version 2.4.1 or later (this database requires it)

### Step 2: Import the Database

1. In openLCA, go to: **File → Import → Database (from zolca)**

2. Click **Browse** and navigate to:
   ```
   /home/teespy/projects/lca-app/backend/data/uslci_2025_q3.zolca
   ```

3. You'll see import options:
   - Database name: `USLCI 2025 Q3` (or your preferred name)
   - Keep other settings as default

4. Click **Finish**

5. **Wait for import to complete**
   - This may take 2-5 minutes depending on your system
   - You'll see a progress bar
   - The database contains thousands of processes

### Step 3: Activate the Database

1. In the openLCA Navigation panel (left side)
2. Right-click on **"USLCI 2025 Q3"** database
3. Select **Activate database**

### Step 4: Start IPC Server on Port 8085

1. With USLCI database activated, go to:
   **Tools → Developer Tools → IPC Server**

2. In the IPC Server window:
   - **Port:** Enter `8085`
   - Click **Start**

3. You should see:
   ```
   Server is running on port 8085
   ```

4. **Important:** Keep this window open!
   - The server runs as long as openLCA is open
   - If you close openLCA, the server stops
   - You can minimize openLCA, just don't close it

---

## Step 5: Test the Connection

Once the IPC server is running on port 8085, the LCA app will automatically detect it!

### Quick Test:

1. Go back to your browser: http://localhost:5173
2. Look at the database selector in the top-right
3. **Refresh the page** (Ctrl+R or F5)
4. You should see:
   - ✓ ELCD (European) - **ONLINE**
   - ✓ **LCA Commons 2025.1 - ONLINE** ← NEW!
   - ✗ Agribalyse 3.2 - offline
   - ✗ BioEnergieDat - offline
   - ✗ USLCI - offline
   - ✗ NEEDS - offline

**Note:** The app is configured to call this database "LCA Commons 2025.1" (per the config), even though the file is specifically the USLCI database.

---

## What's in USLCI Database?

The USLCI (US Life Cycle Inventory) database contains:

- **1,200+ processes** (as of Q3 2025)
- **US-focused data:** Manufacturing, energy, materials, agriculture, transportation
- **Key sectors:**
  - Cement and concrete production
  - Forestry and forest products
  - Electricity generation (US grid mixes)
  - Agricultural products
  - Transportation fuels
  - Building materials

- **Impact assessment methods:**
  - TRACI 2.2 (US EPA's Tool for Reduction and Assessment of Chemicals)
  - ReCiPe 2016
  - IPCC Global Warming Potential
  - Cumulative Energy Demand

---

## Using LCA Commons in the App

Once connected, you can:

1. **Switch to LCA Commons** using the database selector dropdown
2. **Search for US-specific processes:**
   - "electricity US"
   - "cement production"
   - "transportation diesel"
   - "forestry operations"

3. **Calculate impacts with US-focused data**
   - More accurate for US-based products
   - US grid mixes and regional data
   - TRACI method (EPA recommended for US)

---

## Troubleshooting

### Database selector still shows "offline"

**Solution 1:** Hard refresh the browser
- Press **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac)
- This clears the cache and re-checks all databases

**Solution 2:** Verify IPC server is running
- Check the openLCA IPC Server window
- It should say "Server is running on port 8085"
- If not, click Start again

**Solution 3:** Check port number
- Make sure you entered `8085` in the IPC Server settings
- If you used a different port, update `backend/config/databases.json`

### Import failed

**Common causes:**
- **Old openLCA version:** Update to 2.4.1 or later
- **Corrupted download:** Re-download the file
- **Insufficient disk space:** Free up at least 1GB

### IPC Server won't start

**Solutions:**
- Make sure no other application is using port 8085
- Try a different port (e.g., 8090) and update the config file
- Restart openLCA

---

## Multiple Databases

### Can I have both ELCD and USLCI running simultaneously?

**Short answer:** Not easily with one openLCA instance.

**Details:**
- Each openLCA instance can only run ONE IPC server at a time
- You can only have one database active at a time
- To use both, you'd need to stop one IPC server and start another

**Recommended approach:**
- Use ELCD for European/global data
- Use USLCI for US-specific analyses
- Switch between them as needed

**Advanced option (not recommended for beginners):**
- Run two separate openLCA instances (requires separate installations)
- One on port 8080 (ELCD)
- One on port 8085 (USLCI)
- This is complex and resource-intensive

---

## Configuration File Reference

The database configuration is in:
```
/home/teespy/projects/lca-app/backend/config/databases.json
```

Current USLCI/LCA Commons entry:
```json
{
  "id": "lca_commons",
  "name": "LCA Commons 2025.1",
  "host": "172.26.192.1",
  "port": 8085,
  "db_type": "free",
  "description": "Federal LCA Commons - Free, includes USLCI, Cement & Concrete, Forestry databases",
  "requires_license": false,
  "capabilities": ["TRACI", "ReCiPe2016"]
}
```

If you need to change the port, edit this file and restart the backend.

---

## Summary

✅ **USLCI database downloaded** (20 MB)
✅ **Location:** `/home/teespy/projects/lca-app/backend/data/uslci_2025_q3.zolca`
📋 **Next steps:** Import into openLCA and start IPC server on port 8085

Once you complete the openLCA steps, refresh your browser and "LCA Commons 2025.1" will show as **ONLINE**!

Let me know when you're ready to test it! 🚀
