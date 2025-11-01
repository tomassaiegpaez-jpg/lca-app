#!/usr/bin/env python3
"""
Test script to verify process-to-product-system LCIA calculation works end-to-end
"""
import sys
from services.openlca_service import OpenLCAService
import olca_ipc as ipc
import json

def test_process_lcia():
    print("=" * 80)
    print("TEST: Process LCIA Calculation with Auto-Linking")
    print("=" * 80)

    service = OpenLCAService()

    # Test 1: Search for a process
    print("\n[TEST 1] Searching for glass fibre processes...")
    print("-" * 80)
    processes = service.search_processes("glass fibre", limit=10)
    print(f"Found {len(processes)} processes")

    if not processes:
        print("❌ No processes found - test cannot continue")
        return False

    # Get first process that doesn't have a product system
    test_process = None
    for proc in processes:
        # Check if this process has an existing product system
        all_systems = service.client.get_descriptors(ipc.o.ProductSystem)
        has_system = False
        for sys in all_systems:
            full_sys = service.client.get(ipc.o.ProductSystem, sys.id)
            if hasattr(full_sys, 'process') and full_sys.process:
                if full_sys.process.id == proc['id']:
                    has_system = True
                    break

        if not has_system:
            test_process = proc
            break

    if not test_process:
        print("All processes already have product systems. Using first process anyway.")
        test_process = processes[0]

    print(f"\nTest Process: {test_process['name']}")
    print(f"Process ID: {test_process['id']}")

    # Test 2: Find or create product system
    print("\n[TEST 2] Finding or creating product system...")
    print("-" * 80)

    try:
        ps_info = service.find_or_create_product_system(test_process['id'])
        print(f"✓ Product system obtained:")
        print(f"  - ID: {ps_info['id']}")
        print(f"  - Name: {ps_info['name']}")
        print(f"  - Mode: {ps_info['mode']}")
        print(f"  - Process count: {ps_info.get('process_count', 'unknown')}")
        print(f"  - Created: {ps_info.get('created', False)}")
    except Exception as e:
        print(f"❌ Product system creation failed: {e}")
        return False

    # Test 3: Calculate LCIA
    print("\n[TEST 3] Calculating LCIA from process...")
    print("-" * 80)

    try:
        results = service.calculate_lcia(test_process['id'], amount=1.0)
        print(f"✓ LCIA calculation complete:")
        print(f"  - Product system: {results['product_system']}")
        print(f"  - Calculation mode: {results['calculation_mode']}")
        print(f"  - Functional unit: {results['functional_unit']}")
        print(f"  - Impact categories: {len(results['impacts'])}")

        if results.get('warning'):
            print(f"  ⚠️  Warning: {results['warning']}")

        if results['impacts']:
            print("\n  First 3 impacts:")
            for impact in results['impacts'][:3]:
                print(f"    - {impact['category']}: {impact['amount']:.2e} {impact['unit']}")

        print("\n✅ ALL TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ LCIA calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_process_lcia()
    sys.exit(0 if success else 1)
