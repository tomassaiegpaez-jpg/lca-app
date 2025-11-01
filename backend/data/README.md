# ELCD Database Files

This directory should contain the ELCD (European Life Cycle Database) files, which are too large to store in the Git repository.

## Required Files

1. **ELCD Database Archive** (`.zolca` file):
   - File: `elcd_3_2_greendelta_v2_18_correction_20220908.zolca` (or similar)
   - Size: ~167 MB
   - Source: Download from [OpenLCA Nexus](https://nexus.openlca.org/databases) or [GreenDelta](https://www.greendelta.com/)

2. **Extracted Database** (`elcd_extracted/` directory):
   - This directory is auto-generated when you extract the `.zolca` file using OpenLCA
   - You can also run the extraction script if available

## Setup Instructions

### Option 1: Download Pre-extracted Database
1. Download the ELCD database from [OpenLCA Nexus](https://nexus.openlca.org/databases)
2. Place the `.zolca` file in this directory
3. Extract it using OpenLCA or the provided extraction tools

### Option 2: Extract from .zolca File
If you already have the `.zolca` file:
1. Place it in this directory: `backend/data/`
2. Open OpenLCA
3. Go to File → Import → Linked data (JSON-LD)
4. Select the `.zolca` file
5. The database will be extracted to `backend/data/elcd_extracted/`

## Note

These files are excluded from version control because:
- They are very large (>100 MB, exceeding GitHub's limits)
- They can be obtained from official sources
- They don't change frequently

If you're setting up this project for the first time, you'll need to download these files separately.
