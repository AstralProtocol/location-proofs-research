"""
WitnessChain API Authentication

Handles pre-login and login flow to get session cookie.
"""
from __future__ import annotations

import os
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://mainnet.witnesschain.com/proof/v1")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PROOF_TYPE = "pol"  # Proof of Location

TIMEOUT = 120


def get_wallet():
    """Get wallet from private key."""
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY not set in environment")
    return Account.from_key(PRIVATE_KEY)


def authenticate() -> tuple[Account, requests.Session]:
    """
    Full authentication flow using a session to persist cookies.

    Returns (wallet, authenticated_session).
    """
    wallet = get_wallet()
    print(f"\n=== Authenticating as {wallet.address} ===\n")

    # Create session to persist cookies
    session = requests.Session()

    # Step 1: Pre-login
    url = f"{API_URL}/{PROOF_TYPE}/pre-login"
    payload = {
        "publicKey": wallet.address,
        "proof_type": PROOF_TYPE,
        "walletPublicKey": {
            "ethereum": wallet.address
        },
        "keyType": "ethereum",
        "role": "payer",
        "projectName": "WITNESS_CHAIN",
        "claims": {
            "bandwidth": 10
        }
    }

    print(f"[pre-login] POST {url}")
    response = session.post(url, json=payload, timeout=TIMEOUT)

    print(f"[pre-login] Status: {response.status_code}")
    print(f"[pre-login] Response: {response.text[:500]}")
    print(f"[pre-login] Cookies: {session.cookies.get_dict()}")

    response.raise_for_status()
    pre_login_data = response.json()

    message = pre_login_data.get("result", {}).get("message")
    if not message:
        message = pre_login_data.get("message")
    if not message:
        raise ValueError(f"No message in pre-login response: {pre_login_data}")

    print(f"[auth] Message to sign: {message[:100]}...")

    # Step 2: Sign the message
    message_encoded = encode_defunct(text=message)
    signed = wallet.sign_message(message_encoded)

    # Step 3: Login (session automatically includes cookies from pre-login)
    url = f"{API_URL}/{PROOF_TYPE}/login"
    payload = {
        "signature": "0x" + signed.signature.hex()
    }

    print(f"[login] POST {url}")
    response = session.post(url, json=payload, timeout=TIMEOUT)

    print(f"[login] Status: {response.status_code}")
    print(f"[login] Response: {response.text[:500]}")
    print(f"[login] Cookies: {session.cookies.get_dict()}")

    response.raise_for_status()

    print(f"\n=== Authentication successful ===\n")

    return wallet, session


if __name__ == "__main__":
    wallet, session = authenticate()
    print(f"Wallet: {wallet.address}")
    print(f"Session cookies: {session.cookies.get_dict()}")
