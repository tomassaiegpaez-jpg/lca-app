"""
Build a searchable catalog of all processes in OpenLCA
"""
import json
import olca_ipc as ipc
import os
from dotenv import load_dotenv

load_dotenv('../.env')

host = os.getenv('OPENLCA_HOST')
port = int(os.getenv('OPENLCA_PORT'))

print(f"Connecting to OpenLCA at {host}:{port}...")
client = ipc.Client(f'http://{host}:{port}')

print("Fetching all processes...")
processes = client.get_descriptors(ipc.o.Process)

print(f"Found {len(processes)} processes")

# Build catalog
catalog = []
for proc in processes:
    catalog.append({
        "id": proc.id,
        "name": proc.name,
        "category": proc.category if hasattr(proc, 'category') else None,
        "description": proc.description if hasattr(proc, 'description') else None
    })

# Sort by name
catalog.sort(key=lambda x: x['name'])

# Save to JSON
output_path = 'data/process_catalog.json'
with open(output_path, 'w') as f:
    json.dump(catalog, f, indent=2)

print(f"✓ Saved {len(catalog)} processes to {output_path}")

# Create a searchable index by keywords
print("\nCreating keyword index...")
keyword_index = {}

for proc in catalog:
    name_lower = proc['name'].lower()
    words = name_lower.split()

    for word in words:
        # Skip very short words
        if len(word) < 3:
            continue

        if word not in keyword_index:
            keyword_index[word] = []

        keyword_index[word].append({
            "id": proc['id'],
            "name": proc['name'],
            "category": proc['category']
        })

# Save keyword index
index_path = 'data/keyword_index.json'
with open(index_path, 'w') as f:
    json.dump(keyword_index, f, indent=2)

print(f"✓ Created keyword index with {len(keyword_index)} keywords")

# Print some statistics
print("\n=== Catalog Statistics ===")
categories = {}
for proc in catalog:
    cat = proc['category'] or 'Uncategorized'
    categories[cat] = categories.get(cat, 0) + 1

print(f"\nTop 10 categories:")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {cat}: {count} processes")

print("\n=== Sample processes ===")
for proc in catalog[:5]:
    print(f"  - {proc['name']}")
    if proc['category']:
        print(f"    Category: {proc['category']}")
