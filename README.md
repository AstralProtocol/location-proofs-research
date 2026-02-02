# Location Proofs Research

Research and API exploration for location proof systems, starting with WitnessChain Proof of Location.

Part of the [Astral Protocol](https://github.com/AstralProtocol) ecosystem.

## Overview

This repo documents our exploration of existing location proof systems to understand:
- Proof data structures and cryptographic signatures
- What can be verified independently (without calling their API)
- Integration patterns for Astral Location Services

## WitnessChain Findings

See **[FINDINGS.md](./FINDINGS.md)** for detailed technical findings.

**Summary:**
- Authentication works via wallet signature
- Proofs contain ECDSA signatures from watchtowers
- Cross-references multiple IP geolocation services
- Triggering new challenges requires POINTS tokens (blocked)
- Historical proof data available via `/all-provers` endpoint

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add a private key (no funds needed, just for auth)
```

Generate a test wallet:
```bash
python3 -c "from eth_account import Account; a = Account.create(); print(f'PRIVATE_KEY={a.key.hex()}')"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `auth.py` | Authentication module (pre-login + signature) |
| `explore_api.py` | General API endpoint exploration |
| `analyze_proofs.py` | Extract and analyze proof structure |
| `find_online_prover.py` | Find provers with recent activity |
| `trigger_challenge.py` | Attempt to trigger a challenge (requires POINTS) |

## Data

Sample proof data saved in `proofs/`:
- `proof_structure.json` - Example challenge result with signature
- `challengers.json` - Watchtower network data

## Related

- [Astral Location Services](https://github.com/AstralProtocol/astral-location-services)
- [WitnessChain Docs](https://docs.witnesschain.com)
