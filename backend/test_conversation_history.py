#!/usr/bin/env python3
"""
Test script to verify conversation history includes action results
"""
import requests
import json
import time

API_URL = "http://localhost:8000/api/lca/chat"

def chat(message, conversation_id=None):
    """Send a chat message and return the response"""
    payload = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id

    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    print("=" * 80)
    print("TEST: Conversation History includes Action Results")
    print("=" * 80)

    # Message 1: Ask Claude to search for glass fibre
    print("\n[TURN 1] User: Calculate the impact of 1kg of glass fibre")
    print("-" * 80)
    response1 = chat("Calculate the impact of 1kg of glass fibre")
    conv_id = response1["conversation_id"]
    print(f"Conversation ID: {conv_id}")
    print(f"Message: {response1['message']}")

    if response1.get("action"):
        print(f"\nAction Type: {response1['action'].get('type')}")
        if response1['action'].get('results'):
            results = response1['action']['results']
            print(f"Results Count: {len(results)}")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. {result.get('name')} (ID: {result.get('id')})")

    print("\n" + "=" * 80)
    time.sleep(1)

    # Message 2: Ask Claude to use the first result
    print("\n[TURN 2] User: Use the first one")
    print("-" * 80)
    response2 = chat("Use the first one", conversation_id=conv_id)
    print(f"Message: {response2['message']}")

    if response2.get("action"):
        print(f"\nAction Type: {response2['action'].get('type')}")
        if response2['action'].get('error'):
            print(f"ERROR: {response2['action']['error']}")
            print("\n❌ TEST FAILED: Claude used wrong ID")
        elif response2['action'].get('results'):
            print(f"✅ TEST PASSED: Calculation completed successfully")
            results = response2['action']['results']
            print(f"Product System: {results.get('product_system')}")
            print(f"Impact Categories: {len(results.get('impacts', []))}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
