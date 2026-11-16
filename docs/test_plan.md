# Verification and Validation Plan (Test Plan)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Test Strategy & Hierarchy

The testing architecture ensures that every technical claim made in the research paper is validated by executable code:

```
┌─────────────────────────────────────────────────────────────┐
│                      SYSTEM TESTS                           │
│  - Complete End-to-End Pipeline Execution (run_pipeline.py) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION TESTS                        │
│  - QKD Key -> IoT Sensor Client                             │
│  - Sensor Client -> MQTT Broker                             │
│  - MQTT Broker -> Cloud Receiver -> SQLite Storage          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY TESTS                          │
│  - Ciphertext & Tag Tampering (InvalidTag Assertion)        │
│  - Replay Attack Rejection (Sequence Watermark Check)       │
│  - Key Mismatch Decryption Rejection                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       UNIT TESTS                            │
│  - Quantum State Prep (Z & X Bases)                         │
│  - Projective Measurement & Basis Sifting                   │
│  - QBER Calculation & Abort Threshold                      │
│  - Information Reconciliation (Cascade/Parity Check)        │
│  - Universal-Hash Privacy Amplification                     │
│  - AES-256-GCM Encryption / Decryption                      │
│  - 96-Bit Nonce Freshness                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Case Specifications

### 2.1 Unit Tests (`tests/unit/`)
| Test ID | Module Tested | Test Objective | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **UT-Q01** | `qkd.bb84` | Verify $|0\rangle$ state preparation and measurement. | 100% of measurements yield 0 in $Z$ basis across 100 shots. |
| **UT-Q02** | `qkd.bb84` | Verify $|1\rangle$ state preparation and measurement. | 100% of measurements yield 1 in $Z$ basis across 100 shots. |
| **UT-Q03** | `qkd.bb84` | Verify $|+\rangle$ preparation and measurement in $X$ basis. | 100% of measurements yield 0 in $X$ basis (after $H$ rotation). |
| **UT-Q04** | `qkd.bb84` | Verify non-orthogonal basis measurement ($Z$ state in $X$ basis). | Yields 50% 0 and 50% 1 ($\pm 5\%$) across 1000 shots. |
| **UT-Q05** | `qkd.bb84` | Basis sifting logic. | Sifted key retains only positions where Alice and Bob bases match. |
| **UT-Q06** | `qkd.bb84` | QBER estimation under zero noise and zero Eve. | QBER is identically $0.00\%$. |
| **UT-Q07** | `qkd.bb84` | QBER under full intercept-resend attack ($p_{\text{eve}} = 1.0$). | QBER is within $25.0\% \pm 4.0\%$; key is aborted (`is_valid=False`). |
| **UT-Q08** | `qkd.reconciliation` | Reconcile two bitstrings with 5% discrepancy. | Both parties hold 100% identical bitstrings after reconciliation. |
| **UT-Q09** | `qkd.privacy_amplification` | Universal hashing output entropy. | Output is exactly 32 bytes (256 bits). |
| **UT-C01** | `crypto_utils` | Correct AES-256-GCM encryption & decryption round-trip. | Recovered plaintext exactly matches input payload. |
| **UT-C02** | `crypto_utils` | Enforce 96-bit nonce policy. | Generated nonce is exactly 12 bytes; sequential nonces are distinct. |

### 2.2 Security Tests (`tests/security/`)
| Test ID | Module Tested | Test Objective | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **ST-01** | `crypto_utils` | Tamper with 1 byte of ciphertext. | `CryptoUtils.decrypt_payload()` raises `InvalidTag`. |
| **ST-02** | `crypto_utils` | Tamper with 1 byte of authentication tag. | `CryptoUtils.decrypt_payload()` raises `InvalidTag`. |
| **ST-03** | `crypto_utils` | Decrypt with incorrect 256-bit AES key. | Raises `InvalidTag`; zero plaintext leaked. |
| **ST-04** | `cloud_receiver` | Replay an identical previous `reading_id`. | Receiver detects replay, rejects packet, logs `REPLAY_REJECTED`. |
| **ST-05** | `cloud_receiver` | Replay a stale timestamp envelope. | Receiver rejects stale envelope outside freshness window. |

### 2.3 Integration & System Tests (`tests/integration/`, `tests/system/`)
| Test ID | Modules Tested | Test Objective | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **IT-01** | QKD + Crypto | Feed QKD-derived key directly into AES-256-GCM. | Successful encryption and decryption using QKD session key. |
| **IT-02** | Sensor + MQTT + Cloud | Publish reading via simulated broker; receive and decrypt at cloud. | Cloud receiver decrypts payload and saves reading in SQLite. |
| **SY-01** | Full Pipeline | Execute `run_pipeline.py` end-to-end. | Pipeline executes with exit code 0; all audit assertions pass. |

---

## 3. Execution & Reporting Criteria
- Automated execution via `pytest` with verbose reporting: `pytest tests/ -v`.
- Acceptance criteria: 100% of unit, security, and integration tests must pass with zero failures or unexpected errors.
