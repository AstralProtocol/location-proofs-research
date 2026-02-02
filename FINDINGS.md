# WitnessChain API Testing Findings

**Date:** 2026-02-02  
**Purpose:** Technical validation for Astral Location Services integration

---

## Summary

WitnessChain Proof of Location is viable for infrastructure location verification. We successfully authenticated, queried the network, and retrieved proof data. Triggering new challenges requires POINTS tokens which we do not have access to yet.

---

## What Works

### Authentication
- **Pre-login:** `POST /proof/v1/pol/pre-login` with wallet address
- **Login:** Sign challenge message, submit signature with `0x` prefix
- **Session:** Cookie-based (`requests.Session()` required to persist cookies)

### Working Endpoints
| Endpoint | Method | Returns |
|----------|--------|---------|
| `/pol/pre-login` | POST | Challenge message to sign |
| `/pol/login` | POST | Authenticated session |
| `/pol/user-info` | POST | Account info, detected location |
| `/pol/statistics` | POST | Network stats (4,218 provers, 100k challenges) |
| `/pol/all-provers` | POST | Prover list with historical challenge results |
| `/pol/challengers` | POST | Watchtower network info |
| `/pol/challenge-history` | POST | User's challenge history |

### Broken/Unavailable Endpoints
| Endpoint | Status | Error |
|----------|--------|-------|
| `/pol/provers` | 502 | Bad Gateway (server issue) |
| `/pol/challenge-request-dcl` | 405 | Method not allowed |
| `/pol/challenge-status-dcl` | 405 | Method not allowed |

---

## Proof Structure

Each prover has a `results` array containing challenge results:

```typescript
interface WitnessChainChallengeResult {
  id: string;                      // Challenge ID
  challenge_start_time: string;    // ISO 8601
  
  // Challenger (watchtower) info
  challenger: string;              // 0x address
  challenger_id: string;           // "IPv4/0x..." or "IPv6/0x..."
  challenger_claims: {
    latitude: number;
    longitude: number;
    radius: number;
  };
  
  // Prover's claimed location
  claims: {
    latitude: number;
    longitude: number;
    radius: number;
  };
  
  // Core result
  result: {
    challenge_succeeded: boolean;  // Did latency match claimed location?
    ping_delay: number;            // Microseconds
  };
  
  // Cryptographic proof
  message: string;                 // JSON string that was signed
  signature: string;               // ECDSA signature (0x...)
  
  // Cross-reference with IP geolocation services
  consolidated_result: {
    KnowLoc: boolean;              // WitnessChain algorithm
    KnowLocUncertainty: number;    // Uncertainty in km
    "ipapi.co": boolean;
    ipregistry: boolean;
    maxmind: boolean;
    verified: boolean;             // Final consolidated status
  };
}
```

---

## Blocking Issue

Triggering new challenges requires POINTS tokens:

```
POST /pol/challenge-request { "prover": "IPv4/0x..." }
→ 402: "Payment failed - ERROR_NOT_ENOUGH_BALANCE_IN_FROM for <1:POINTS>"
```

We could not find documentation on how to acquire POINTS or create an API key.

**Action:** Email sent to Ranvir (CEO) asking for API access.

---

## Network Statistics

- **Total provers:** 4,218
- **Total challengers:** 2,937  
- **Online provers:** ~18 (at time of testing)
- **Total challenges:** 100,598
- **Prover countries:** 75 countries globally

---

## Key Technical Details

1. **ID format:** `IPv4/0x{address}` or `IPv6/0x{address}`
2. **Latency-based:** Ping delay in microseconds correlates with physical distance
3. **Multi-source verification:** Cross-references ipapi.co, ipregistry, MaxMind
4. **EigenLayer secured:** AVS contract `0xd25c2c5802198cb8541987b73a8db4c9bcae5cc7`
5. **75 operators, 2.3M ETH restaked**

---

## Files Created

```
witnesschain-test/
├── .env                           # Test wallet private key
├── scripts/
│   ├── auth.py                    # Authentication module
│   ├── explore_api.py             # API endpoint exploration
│   ├── find_provers.py            # Find online provers
│   ├── find_online_prover.py      # Trigger challenge attempt
│   └── analyze_proofs.py          # Proof structure analysis
└── proofs/
    ├── proof_structure.json       # Sample proof data
    └── challengers.json           # Challenger network data
```

---

## Next Steps (when POINTS access resolved)

1. Trigger a live challenge against an online prover
2. Capture the full challenge flow (request → status polling → result)
3. Verify we can independently validate ECDSA signatures
4. Build the verification plugin for Astral

---

## For MVP Without POINTS

We CAN build verification logic using historical proof data:
- Parse `results` array from prover data
- Verify ECDSA signatures
- Check consolidated_result flags
- Compute confidence scores

This lets us build and test the plugin without triggering new challenges.
