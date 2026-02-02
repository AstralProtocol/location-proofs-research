"""
Trigger a WitnessChain Proof of Location challenge.

This captures the full proof result for analysis.
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT

load_dotenv()


def get_prover_info(cookie: str, prover_address: str) -> dict:
    """Get info about a specific prover."""
    url = f"{API_URL}/{PROOF_TYPE}/prover"

    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json"
    }

    payload = {"proverId": prover_address}

    print(f"[prover-info] POST {url}")
    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)

    print(f"[prover-info] Status: {response.status_code}")
    print(f"[prover-info] Response: {response.text[:500]}")

    response.raise_for_status()
    return response.json()


def trigger_challenge(cookie: str, prover_address: str, challenger_count: int = 2) -> dict:
    """
    Trigger a PoL challenge against a prover.

    Note: This uses the DCL (decentralized) challenge endpoint.
    We may need to first submit an onchain request depending on their flow.
    """
    url = f"{API_URL}/{PROOF_TYPE}/challenge-request-dcl"

    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json"
    }

    # Try different payload structures based on what we learned
    payload = {
        "proverId": prover_address,
        "challengerCount": challenger_count,
    }

    print(f"[challenge] POST {url}")
    print(f"[challenge] Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)

    print(f"[challenge] Status: {response.status_code}")
    print(f"[challenge] Response: {response.text}")

    # Don't raise - we want to capture the response even if it fails
    return {
        "status_code": response.status_code,
        "response": response.json() if response.ok else response.text,
        "headers": dict(response.headers)
    }


def check_challenge_status(cookie: str, challenge_id: str) -> dict:
    """Poll for challenge status."""
    url = f"{API_URL}/{PROOF_TYPE}/challenge-status-dcl"

    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json"
    }

    payload = {"challenge_id": challenge_id}

    print(f"[status] POST {url}")
    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)

    print(f"[status] Status: {response.status_code}")
    print(f"[status] Response: {response.text[:1000]}")

    return {
        "status_code": response.status_code,
        "response": response.json() if response.ok else response.text
    }


def poll_until_complete(cookie: str, challenge_id: str, max_attempts: int = 30, interval: int = 10) -> dict:
    """Poll challenge status until complete or timeout."""
    print(f"\n=== Polling for challenge {challenge_id} ===\n")

    all_responses = []

    for attempt in range(max_attempts):
        print(f"[poll] Attempt {attempt + 1}/{max_attempts}")

        result = check_challenge_status(cookie, challenge_id)
        all_responses.append({
            "attempt": attempt + 1,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })

        # Check if complete
        if result["status_code"] == 200:
            response_data = result.get("response", {})
            if isinstance(response_data, dict):
                status = response_data.get("result", {}).get("challenge_status", "")
                state = response_data.get("result", {}).get("state", "")

                print(f"[poll] Challenge status: {status}, state: {state}")

                if status.lower() in ["completed", "done", "finished"] or state.lower() in ["completed", "done"]:
                    print(f"\n=== Challenge completed! ===\n")
                    return {
                        "completed": True,
                        "final_result": result,
                        "all_responses": all_responses
                    }

        print(f"[poll] Waiting {interval}s...")
        time.sleep(interval)

    print(f"\n=== Polling timed out after {max_attempts} attempts ===\n")
    return {
        "completed": False,
        "all_responses": all_responses
    }


def main():
    parser = argparse.ArgumentParser(description="Trigger WitnessChain PoL challenge")
    parser.add_argument("--prover", required=True, help="Prover address to challenge")
    parser.add_argument("--challengers", type=int, default=2, help="Number of challengers")
    parser.add_argument("--poll", action="store_true", help="Poll for result after triggering")
    args = parser.parse_args()

    # Authenticate
    wallet, cookie = authenticate()

    # Get prover info first
    print(f"\n=== Getting prover info for {args.prover} ===\n")
    try:
        prover_info = get_prover_info(cookie, args.prover)
        print(f"[prover] Info: {json.dumps(prover_info, indent=2)[:500]}")
    except Exception as e:
        print(f"[prover] Could not get prover info: {e}")
        prover_info = None

    # Trigger challenge
    print(f"\n=== Triggering PoL challenge ===\n")
    print(f"Prover: {args.prover}")
    print(f"Challengers: {args.challengers}")

    result = trigger_challenge(cookie, args.prover, args.challengers)

    # Save result
    os.makedirs("proofs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"proofs/challenge_{timestamp}.json"

    output = {
        "timestamp": datetime.now().isoformat(),
        "prover": args.prover,
        "challengers": args.challengers,
        "prover_info": prover_info,
        "challenge_result": result
    }

    # If we got a challenge ID and --poll, poll for result
    if args.poll and result["status_code"] == 200:
        response_data = result.get("response", {})
        challenge_id = None

        if isinstance(response_data, dict):
            challenge_id = response_data.get("result", {}).get("challenge_id")
            if not challenge_id:
                challenge_id = response_data.get("challenge_id")

        if challenge_id:
            poll_result = poll_until_complete(cookie, challenge_id)
            output["poll_result"] = poll_result

    with open(filename, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n=== Results saved to {filename} ===")
    print(f"\nTo inspect: cat {filename} | jq .")


if __name__ == "__main__":
    main()
