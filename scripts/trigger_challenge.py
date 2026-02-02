"""
Trigger a Proof of Location challenge against a prover.
"""
from __future__ import annotations

import json
import time
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT


def call_endpoint(session, endpoint: str, payload: dict = None) -> dict:
    """Call an API endpoint."""
    url = f"{API_URL}/{PROOF_TYPE}/{endpoint}"
    print(f"\n[POST] {url}")
    if payload:
        print(f"Payload: {json.dumps(payload, indent=2)}")

    response = session.post(url, json=payload or {}, timeout=TIMEOUT)

    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:2000]}")
        return {"success": response.ok, "data": data, "status": response.status_code}
    except:
        print(f"Text: {response.text[:500]}")
        return {"success": response.ok, "text": response.text, "status": response.status_code}


def main():
    wallet, session = authenticate()

    print(f"\n{'='*60}")
    print("TRIGGERING PROOF OF LOCATION CHALLENGE")
    print(f"{'='*60}")

    # First, get a list of provers
    print("\n--- Getting provers ---")
    result = call_endpoint(session, "all-provers", {})

    if not result["success"]:
        print("Failed to get provers!")
        return

    provers = result["data"].get("result", {}).get("provers", [])
    print(f"\nFound {len(provers)} provers")

    if not provers:
        print("No provers available!")
        return

    # Find an active/online prover (preferably one with recent activity)
    target_prover = None
    for p in provers[:50]:
        prover_id = p.get("id", "")
        if p.get("results"):
            target_prover = p
            print(f"\nFound prover with results: {prover_id}")
            break

    if not target_prover:
        target_prover = provers[0]

    prover_id = target_prover.get("id")
    print(f"\nTarget prover: {prover_id}")
    print(f"Prover details: {json.dumps(target_prover, indent=2)[:1500]}")

    # Try to trigger a challenge
    print("\n--- Triggering challenge ---")

    payloads = [
        {"prover": prover_id},
        {"prover_id": prover_id},
        {"id": prover_id},
        {"prover": prover_id.replace("IPv4/", "").replace("IPv6/", "")},
    ]

    for payload in payloads:
        print(f"\n--- Trying payload: {payload} ---")
        result = call_endpoint(session, "challenge-request", payload)
        if result["success"]:
            print("Challenge initiated!")
            challenge_data = result["data"]

            challenge_id = challenge_data.get("result", {}).get("challenge_id")
            if challenge_id:
                print(f"\nChallenge ID: {challenge_id}")
                print("Polling for status...")

                for i in range(10):
                    time.sleep(5)
                    status_result = call_endpoint(session, "challenge-status", {
                        "challenge_id": challenge_id
                    })
                    if status_result["success"]:
                        status_data = status_result["data"]
                        status = status_data.get("result", {}).get("status")
                        print(f"Status [{i}]: {status}")
                        if status in ["completed", "failed", "verified"]:
                            print("\nFinal result:")
                            print(json.dumps(status_data, indent=2))
                            break
            return

    print("\nAll challenge attempts failed!")


if __name__ == "__main__":
    main()
