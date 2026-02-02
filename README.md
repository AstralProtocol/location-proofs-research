# WitnessChain Integration Test

Testing WitnessChain Proof of Location (PoL) to understand proof format for Astral verification.

## Goal

Capture actual WitnessChain proof data to understand:
- Proof data structure
- Watchtower signatures (if included)
- What can be verified independently

## Setup

```bash
cd /Users/x25bd/Code/astral/witnesschain-test

# Create virtual env
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
```

## Generate a Test Wallet

You need a private key for API auth (no funds needed):

```bash
# Quick way using Python
python3 -c "from eth_account import Account; a = Account.create(); print(f'Address: {a.address}\nPrivate Key: {a.key.hex()}')"
```

Add the private key to `.env`:
```
PRIVATE_KEY=0x...
```

## Usage

### 1. Explore the API

Start by exploring available endpoints:

```bash
python scripts/explore_api.py
```

This calls various endpoints and saves responses to `proofs/`.

### 2. List Available Provers

```bash
python scripts/list_provers.py
```

Find an active prover to challenge.

### 3. Trigger a Challenge

```bash
# Basic challenge
python scripts/trigger_challenge.py --prover <PROVER_ADDRESS>

# With polling for result
python scripts/trigger_challenge.py --prover <PROVER_ADDRESS> --poll
```

## Output

All responses saved to `proofs/` directory as JSON.

## Notes

- The challenge-request-dcl endpoint may require an onchain `submitRequest` first
- If so, we'll need to interact with their L2 contract
- See: https://docs.witnesschain.com/infinity-watch/apis/challenge-apis/getting-started

## What We're Looking For

1. **Proof structure**: What data is returned after a completed challenge?
2. **Signatures**: Are watchtower signatures included? In what format?
3. **Verification**: Can we verify proofs without calling their API?
4. **Onchain data**: What gets recorded onchain vs returned via API?
