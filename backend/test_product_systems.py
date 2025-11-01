"""
Test script to check if we can see product systems via IPC
"""
import os
import olca_ipc as ipc
from dotenv import load_dotenv

load_dotenv('../.env')

host = os.getenv('OPENLCA_HOST')
port = int(os.getenv('OPENLCA_PORT'))

print(f"Connecting to OpenLCA at {host}:{port}...")
client = ipc.Client(f'http://{host}:{port}')

print("\nFetching all product systems...")
product_systems = client.get_descriptors(ipc.o.ProductSystem)

print(f"\nFound {len(product_systems)} product systems")

# Look for the glass fibre one
print("\n=== Searching for 'glass fibre' product systems ===")
for ps in product_systems:
    if 'glass' in ps.name.lower() or 'fibre' in ps.name.lower() or 'fiber' in ps.name.lower():
        print(f"\nName: {ps.name}")
        print(f"ID: {ps.id}")

        # Get full details
        full_ps = client.get(ipc.o.ProductSystem, ps.id)
        if hasattr(full_ps, 'process') and full_ps.process:
            print(f"Process ID: {full_ps.process.id}")
            print(f"Process Name: {full_ps.process.name if hasattr(full_ps.process, 'name') else 'N/A'}")

print("\n=== All product systems (first 20) ===")
for i, ps in enumerate(product_systems[:20]):
    print(f"{i+1}. {ps.name}")
