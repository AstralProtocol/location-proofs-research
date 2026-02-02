"""
List available WitnessChain provers.

This helps us find an existing prover to trigger a challenge against.
"""

import os
import json
import requests
from dotenv import load_dotenv
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT

load_dotenv()


def list_provers(cookie: str) -> dict:
    """
    Get list of available provers.

    Returns full response for inspection.
    """
    url = f"{API_URL}/{PROOF_TYPE}/provers"

    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json"
    }

    print(f"[provers] GET {url}")

    response = requests.post(url, headers=headers, json={}, timeout=TIMEOUT)

    print(f"[provers] Status: {response.status_code}")

    response.raise_for_status()
    return response.json()


def main():
    # Authenticate
    wallet, cookie = authenticate()

    # List provers
    print("\n=== Fetching provers ===\n")
    response = list_provers(cookie)

    # Save full response
    os.makedirs("proofs", exist_ok=True)
    with open("proofs/provers_response.json", "w") as f:
        json.dump(response, f, indent=2)

    print(f"[provers] Full response saved to proofs/provers_response.json")

    # Parse and display provers
    provers = response.get("result", [])
    if isinstance(provers, dict):
        provers = provers.get("provers", [])

    print(f"\n=== Found {len(provers)} provers ===\n")

    for i, prover in enumerate(provers[:10]):  # Show first 10
        prover_id = prover.get("id", "unknown")
        project = prover.get("projectName", "unknown")
        claims = prover.get("claims", {})
        lat = claims.get("latitude", "?")
        lng = claims.get("longitude", "?")
        last_alive = prover.get("last_alive", "?")

        print(f"{i+1}. {prover_id[:20]}...")
        print(f"   Project: {project}")
        print(f"   Location: ({lat}, {lng})")
        print(f"   Last alive: {last_alive}")
        print()

    if len(provers) > 10:
        print(f"... and {len(provers) - 10} more")

    print("\nUse a prover ID with trigger_challenge.py:")
    print(f"  python scripts/trigger_challenge.py --prover <PROVER_ADDRESS>")


if __name__ == "__main__":
    main()
