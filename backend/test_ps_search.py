"""
Test product system search functionality
"""
from services.openlca_service import get_openlca_service

service = get_openlca_service()

print("Testing product system search for 'glass'...")
results = service.search_product_systems("glass", limit=10)

print(f"\nFound {len(results)} product systems:")
for ps in results:
    print(f"  - {ps['name']} (ID: {ps['id']})")
    print(f"    Type: {ps['type']}")

print("\n\nTesting LCIA calculation from product system...")
if results:
    ps_id = results[0]['id']
    print(f"Calculating LCIA for: {results[0]['name']}")

    try:
        lcia_result = service.calculate_lcia_from_product_system(ps_id)
        print(f"\nCalculation Mode: {lcia_result['calculation_mode']}")
        print(f"Product System: {lcia_result['product_system']}")
        print(f"Impact Method: {lcia_result['impact_method']}")
        print(f"\nImpact Categories ({len(lcia_result['impacts'])} total):")
        for impact in lcia_result['impacts'][:5]:  # Show first 5
            print(f"  - {impact['category']}: {impact['amount']:.3e} {impact['unit']}")
    except Exception as e:
        print(f"Error: {e}")
