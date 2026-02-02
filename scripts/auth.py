"""
WitnessChain API Authentication

Handles pre-login and login flow to get session cookie.
"""

import os
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://api.witnesschain.com/proof/v1")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PROOF_TYPE = "pol"  # Proof of Location

TIMEOUT = 120


def get_wallet():
    """Get wallet from private key."""
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY not set in environment")
    return Account.from_key(PRIVATE_KEY)


def pre_login(wallet_address: str) -> dict:
    """
    Call pre-login to get message to sign.

    Returns the full response for inspection.
    """
    url = f"{API_URL}/{PROOF_TYPE}/pre-login"

    payload = {
        "walletAddress": wallet_address,
        "role": "payer",  # We're paying for challenges
        "keyType": "ethereum"
    }

    print(f"[pre-login] POST {url}")
    print(f"[pre-login] Payload: {payload}")

    response = requests.post(url, json=payload, timeout=TIMEOUT)

    print(f"[pre-login] Status: {response.status_code}")
    print(f"[pre-login] Response: {response.text[:500]}")

    response.raise_for_status()
    return response.json()


def login(wallet: Account, message: str) -> tuple[dict, str]:
    """
    Sign message and complete login.

    Returns (response_json, session_cookie).
    """
    url = f"{API_URL}/{PROOF_TYPE}/login"

    # Sign the message
    message_encoded = encode_defunct(text=message)
    signed = wallet.sign_message(message_encoded)

    payload = {
        "walletAddress": wallet.address,
        "message": message,
        "signature": signed.signature.hex(),
        "role": "payer",
        "keyType": "ethereum"
    }

    print(f"[login] POST {url}")
    print(f"[login] Wallet: {wallet.address}")

    response = requests.post(url, json=payload, timeout=TIMEOUT)

    print(f"[login] Status: {response.status_code}")
    print(f"[login] Response: {response.text[:500]}")

    response.raise_for_status()

    # Extract session cookie
    cookies = response.cookies.get_dict()
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    print(f"[login] Cookies: {list(cookies.keys())}")

    return response.json(), cookie_header


def authenticate() -> tuple[Account, str]:
    """
    Full authentication flow.

    Returns (wallet, session_cookie).
    """
    wallet = get_wallet()
    print(f"\n=== Authenticating as {wallet.address} ===\n")

    # Pre-login
    pre_login_response = pre_login(wallet.address)
    message = pre_login_response.get("result", {}).get("message")

    if not message:
        # Try alternate response structure
        message = pre_login_response.get("message")

    if not message:
        raise ValueError(f"No message in pre-login response: {pre_login_response}")

    print(f"[auth] Message to sign: {message[:100]}...")

    # Login
    login_response, cookie = login(wallet, message)

    print(f"\n=== Authentication successful ===\n")

    return wallet, cookie


if __name__ == "__main__":
    wallet, cookie = authenticate()
    print(f"Wallet: {wallet.address}")
    print(f"Cookie: {cookie[:50]}...")
