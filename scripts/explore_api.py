"""
Explore WitnessChain API endpoints to understand data structures.

This script calls various endpoints and saves all responses for analysis.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT

load_dotenv()


def call_endpoint(session: requests.Session, endpoint: str, payload: dict = None) -> dict:
    """Call an API endpoint using authenticated session."""
    url = f"{API_URL}/{PROOF_TYPE}/{endpoint}"

    print(f"\n[{endpoint}] POST {url}")

    try:
        response = session.post(
            url,
            json=payload or {},
            timeout=TIMEOUT
        )

        return {
            "endpoint": endpoint,
            "url": url,
            "payload": payload,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.json() if response.ok else response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "url": url,
            "payload": payload,
            "error": str(e),
            "success": False
        }


def main():
    # Authenticate (returns session with cookies)
    wallet, session = authenticate()

    print(f"\n{'='*60}")
    print("EXPLORING WITNESSCHAIN API")
    print(f"{'='*60}\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "wallet": wallet.address,
        "api_url": API_URL,
        "proof_type": PROOF_TYPE,
        "endpoints": {}
    }

    # Endpoints to explore
    endpoints = [
        ("provers", {}),
        ("user-info", {}),
        ("statistics", {}),
        ("challenger", {}),
        # These might need specific IDs but let's try with empty payload
        ("prover", {}),
        ("challenge-status", {}),
        ("challenge-status-dcl", {}),
    ]

    for endpoint, payload in endpoints:
        print(f"\n--- Testing: {endpoint} ---")
        result = call_endpoint(session, endpoint, payload)
        results["endpoints"][endpoint] = result

        if result["success"]:
            print(f"[{endpoint}] SUCCESS")
            # Pretty print first 500 chars of response
            response_str = json.dumps(result["response"], indent=2)
            print(f"[{endpoint}] Response preview:\n{response_str[:500]}")
            if len(response_str) > 500:
                print("...")
        else:
            print(f"[{endpoint}] FAILED: {result.get('error', result.get('response', 'unknown'))[:200]}")

    # Save all results
    os.makedirs("proofs", exist_ok=True)
    filename = f"proofs/api_exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"Results saved to {filename}")
    print(f"{'='*60}\n")

    # Summary
    print("SUMMARY:")
    for endpoint, result in results["endpoints"].items():
        status = "OK" if result["success"] else "FAIL"
        print(f"  {endpoint}: {status}")


if __name__ == "__main__":
    main()
