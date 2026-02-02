"""
Find an online prover and trigger a challenge.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT


def call_endpoint(session, endpoint: str, payload: dict = None) -> dict:
    """Call an API endpoint."""
    url = f"{API_URL}/{PROOF_TYPE}/{endpoint}"
    print(f"\n[POST] {url}")

    response = session.post(url, json=payload or {}, timeout=TIMEOUT)

    try:
        return {"success": response.ok, "data": response.json(), "status": response.status_code}
    except:
        return {"success": response.ok, "text": response.text, "status": response.status_code}


def main():
    wallet, session = authenticate()

    print(f"\n{'='*60}")
    print("FINDING ONLINE PROVERS")
    print(f"{'='*60}")

    # Get all provers
    result = call_endpoint(session, "all-provers", {})
    if not result["success"]:
        print("Failed to get provers!")
        return

    provers = result["data"].get("result", {}).get("provers", [])
    print(f"Got {len(provers)} provers total")

    # Find provers with recent last_alive or websocket_connected_at
    now = datetime.now(timezone.utc)
    online_candidates = []

    for p in provers:
        prover_id = p.get("id", "")
        last_alive = p.get("last_alive")
        ws_connected = p.get("websocket_connected_at")
        
        # Check if recently active
        if last_alive:
            try:
                alive_time = datetime.fromisoformat(last_alive.replace("Z", "+00:00"))
                age_minutes = (now - alive_time).total_seconds() / 60
                if age_minutes < 60:  # Active in last hour
                    online_candidates.append({
                        "id": prover_id,
                        "last_alive": last_alive,
                        "age_minutes": age_minutes,
                        "ws_connected": ws_connected,
                        "data": p
                    })
            except:
                pass

    print(f"\nFound {len(online_candidates)} provers active in last hour")

    if online_candidates:
        # Sort by most recent
        online_candidates.sort(key=lambda x: x["age_minutes"])
        
        print("\nMost recent provers:")
        for c in online_candidates[:10]:
            print(f"  {c['id']}: {c['age_minutes']:.1f} min ago, ws={c['ws_connected']}")

        # Try to challenge the most recent one
        target = online_candidates[0]
        print(f"\nTarget prover: {target['id']}")
        print(f"Last alive: {target['last_alive']} ({target['age_minutes']:.1f} min ago)")

        print("\n--- Triggering challenge ---")
        result = call_endpoint(session, "challenge-request", {"prover": target["id"]})
        print(f"Status: {result['status']}")
        print(f"Response: {json.dumps(result.get('data', result.get('text')), indent=2)}")

        if result["success"]:
            challenge_data = result["data"]
            challenge_id = challenge_data.get("result", {}).get("challenge_id")
            
            if challenge_id:
                print(f"\nChallenge ID: {challenge_id}")
                print("Polling for status (this may take a minute)...")

                for i in range(12):  # Poll for 1 minute
                    time.sleep(5)
                    status_result = call_endpoint(session, "challenge-status", {
                        "challenge_id": challenge_id
                    })
                    
                    if status_result["success"]:
                        status_data = status_result["data"]
                        status = status_data.get("result", {}).get("status")
                        print(f"  [{i+1}] Status: {status}")
                        
                        if status in ["completed", "failed", "verified", "timeout"]:
                            print("\n=== FINAL RESULT ===")
                            print(json.dumps(status_data, indent=2))
                            
                            # Save the proof
                            with open("/Users/x25bd/Code/astral/witnesschain-test/proofs/challenge_result.json", "w") as f:
                                json.dump(status_data, f, indent=2)
                            print("\nSaved to proofs/challenge_result.json")
                            break
                    else:
                        print(f"  [{i+1}] Error: {status_result.get('data', {}).get('error', {}).get('message', 'unknown')}")
    else:
        print("No online provers found!")

        # Let's check what the last_alive values look like
        print("\n--- Checking prover activity ---")
        for p in provers[:5]:
            print(f"  {p.get('id')}: last_alive={p.get('last_alive')}")


if __name__ == "__main__":
    main()
