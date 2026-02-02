"""
Analyze the proof structure from completed challenges.
"""
from __future__ import annotations

import json
from auth import authenticate, API_URL, PROOF_TYPE, TIMEOUT


def main():
    wallet, session = authenticate()

    print(f"\n{'='*60}")
    print("ANALYZING PROOF STRUCTURE")
    print(f"{'='*60}")

    # Get all provers
    url = f"{API_URL}/{PROOF_TYPE}/all-provers"
    response = session.post(url, json={}, timeout=TIMEOUT)
    
    if not response.ok:
        print(f"Failed to get provers: {response.status_code}")
        return

    provers = response.json().get("result", {}).get("provers", [])
    print(f"Got {len(provers)} provers")

    # Find provers with results
    provers_with_results = [p for p in provers if p.get("results")]
    print(f"Found {len(provers_with_results)} provers with challenge results")

    if provers_with_results:
        # Get the first one with the most results
        provers_with_results.sort(key=lambda x: len(x.get("results", [])), reverse=True)
        prover = provers_with_results[0]
        
        print(f"\n--- Prover: {prover['id']} ---")
        print(f"Name: {prover.get('name')}")
        print(f"Number of results: {len(prover.get('results', []))}")

        # Analyze the result structure
        if prover.get("results"):
            result = prover["results"][0]
            
            print(f"\n{'='*60}")
            print("PROOF STRUCTURE (First Result)")
            print(f"{'='*60}")
            print(json.dumps(result, indent=2))

            print(f"\n{'='*60}")
            print("KEY FIELDS IN PROOF")
            print(f"{'='*60}")
            
            for key in sorted(result.keys()):
                value = result[key]
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {type(v).__name__}")
                elif isinstance(value, list):
                    print(f"{key}: list[{len(value)}]")
                else:
                    print(f"{key}: {type(value).__name__} = {str(value)[:100]}")

        # Save full prover data for analysis
        output = {
            "prover_id": prover["id"],
            "prover_name": prover.get("name"),
            "claims": prover.get("claims"),
            "geoip": prover.get("geoip"),
            "results": prover.get("results", [])[:5],  # First 5 results
        }

        with open("/Users/x25bd/Code/astral/witnesschain-test/proofs/proof_structure.json", "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved to proofs/proof_structure.json")


if __name__ == "__main__":
    main()
