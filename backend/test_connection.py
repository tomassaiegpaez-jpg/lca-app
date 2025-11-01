#!/usr/bin/env python3
"""
Test script to verify OpenLCA IPC connection from WSL to Windows
"""
import os
from dotenv import load_dotenv
import olca_ipc as ipc

# Load environment variables
load_dotenv('../.env')

host = os.getenv('OPENLCA_HOST')
port = int(os.getenv('OPENLCA_PORT'))

print(f"Attempting to connect to OpenLCA at {host}:{port}...")

try:
    # Create IPC client with full endpoint URL to reach Windows host from WSL
    endpoint = f"http://{host}:{port}"
    print(f"Connecting to: {endpoint}")

    client = ipc.Client(endpoint)

    print("✓ Connection successful!")

    # Test: Get some processes to verify database is loaded
    print("\nQuerying database for processes...")
    processes = client.get_descriptors(ipc.o.Process)

    if not processes:
        print("  ⚠ No processes found. Please ensure ELCD database is imported in OpenLCA.")
    else:
        print(f"  ✓ Found {len(processes)} processes in database")
        print("\nFirst 5 processes:")
        for i, proc in enumerate(processes[:5]):
            print(f"  {i+1}. {proc.name}")

    print("\n✓ OpenLCA IPC is working correctly!")

except ConnectionRefusedError:
    print("✗ Connection refused!")
    print("\nTroubleshooting:")
    print("1. Ensure OpenLCA is running on Windows")
    print("2. Enable IPC Server: Window → Developer tools → IPC Server")
    print("3. Set port to 8080 and click Start")

except Exception as e:
    print(f"✗ Error: {e}")
    print(f"\nException type: {type(e).__name__}")
