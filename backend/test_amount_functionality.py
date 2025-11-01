#!/usr/bin/env python3
"""
Test script to verify that amount parameter correctly scales LCIA results
"""
import sys
from services.openlca_service import OpenLCAService
import json

def test_amount_scaling():
    print("=" * 80)
    print("TEST: Amount Parameter Scaling")
    print("=" * 80)

    service = OpenLCAService()

    # Find a product system to test
    print("\n[TEST 1] Finding a product system to test...")
    print("-" * 80)
    product_systems = service.search_product_systems("glass fibre", limit=1)

    if not product_systems:
        print("❌ No product systems found - cannot test")
        return False

    test_ps = product_systems[0]
    print(f"Using product system: {test_ps['name']}")
    print(f"ID: {test_ps['id']}")

    # Calculate for 1kg
    print("\n[TEST 2] Calculating LCIA for 1kg...")
    print("-" * 80)
    try:
        results_1kg = service.calculate_lcia_from_product_system(
            test_ps['id'],
            amount=1.0
        )
        print(f"✓ Calculation complete for 1kg")
        print(f"  - Impact categories: {len(results_1kg['impacts'])}")
        print(f"  - Functional unit: {results_1kg.get('functional_unit_text', 'N/A')}")

        if results_1kg['impacts']:
            first_impact = results_1kg['impacts'][0]
            print(f"  - First impact: {first_impact['category']}: {first_impact['amount']:.6e} {first_impact['unit']}")
    except Exception as e:
        print(f"❌ Calculation failed for 1kg: {e}")
        return False

    # Calculate for 2kg
    print("\n[TEST 3] Calculating LCIA for 2kg...")
    print("-" * 80)
    try:
        results_2kg = service.calculate_lcia_from_product_system(
            test_ps['id'],
            amount=2.0
        )
        print(f"✓ Calculation complete for 2kg")
        print(f"  - Impact categories: {len(results_2kg['impacts'])}")
        print(f"  - Functional unit: {results_2kg.get('functional_unit_text', 'N/A')}")

        if results_2kg['impacts']:
            first_impact = results_2kg['impacts'][0]
            print(f"  - First impact: {first_impact['category']}: {first_impact['amount']:.6e} {first_impact['unit']}")
    except Exception as e:
        print(f"❌ Calculation failed for 2kg: {e}")
        return False

    # Verify scaling
    print("\n[TEST 4] Verifying 2kg = 2x the impacts of 1kg...")
    print("-" * 80)

    if len(results_1kg['impacts']) != len(results_2kg['impacts']):
        print(f"❌ Impact category count mismatch: {len(results_1kg['impacts'])} vs {len(results_2kg['impacts'])}")
        return False

    all_correct = True
    errors = []

    for i, (impact_1kg, impact_2kg) in enumerate(zip(results_1kg['impacts'], results_2kg['impacts'])):
        category = impact_1kg['category']
        amount_1kg = impact_1kg['amount']
        amount_2kg = impact_2kg['amount']

        # Calculate expected value (2x)
        expected_2kg = amount_1kg * 2.0

        # Check if 2kg value is approximately 2x the 1kg value
        # Special handling for zero values
        if amount_1kg == 0.0 and amount_2kg == 0.0:
            # Both zero is correct (0 × 2 = 0)
            status = "✓"
        elif abs(expected_2kg) < 1e-20:
            # Expected value is effectively zero, check if actual is also near zero
            status = "✓" if abs(amount_2kg) < 1e-20 else "✗"
            if status == "✗":
                all_correct = False
                errors.append(f"  {status} {category}: {amount_1kg:.6e} × 2 = {expected_2kg:.6e} (got {amount_2kg:.6e})")
        else:
            # Normal case: check if within 0.01% tolerance
            if abs(amount_2kg - expected_2kg) < abs(expected_2kg * 0.0001):
                status = "✓"
            else:
                status = "✗"
                all_correct = False
                errors.append(f"  {status} {category}: {amount_1kg:.6e} × 2 = {expected_2kg:.6e} (got {amount_2kg:.6e})")

        if i < 3 or status == "✗":  # Show first 3 and all errors
            print(f"  {status} {category}: {amount_1kg:.6e} × 2 = {amount_2kg:.6e}")

    if errors:
        print("\n❌ ERRORS FOUND:")
        for error in errors:
            print(error)
        return False

    if all_correct:
        print("\n✅ ALL TESTS PASSED!")
        print("   2kg produces exactly 2x the impacts of 1kg")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = test_amount_scaling()
    sys.exit(0 if success else 1)
