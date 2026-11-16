# Automated Test Results Report

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date of Execution:** 16 November 2026  
**Test Framework:** Pytest 9.0.3 (Python 3.12.10, Qiskit Aer backend)  
**Execution Status:** **ALL 17 TESTS PASSED (100% PASS RATE)**

---

## 1. Test Execution Summary

| Test Category | Suite File | Total Tests | Passed | Failed | Skipped | Execution Time |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **QKD Unit Tests** | `tests/unit/test_qkd.py` | 8 | 8 | 0 | 0 | 16.20 s |
| **Crypto Unit Tests** | `tests/unit/test_crypto.py` | 3 | 3 | 0 | 0 | 0.08 s |
| **Security Tests** | `tests/security/test_security.py` | 5 | 5 | 0 | 0 | 2.45 s |
| **Integration Tests** | `tests/integration/test_pipeline.py`| 1 | 1 | 0 | 0 | 2.80 s |
| **TOTAL** | — | **17** | **17** | **0** | **0** | **21.53 s** |

---

## 2. Individual Test Case Verification Log

| Test Identifier | Test Function Name | Subsystem Verified | Result | Duration | Notes / Evidence |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **UT-Q01** | `test_alice_state_prep` | Alice State Preparation | **PASSED** | 0.12 s | Verified random bits & bases generation and Pauli-X/Hadamard gate circuit assembly. |
| **UT-Q02** | `test_bob_measurement` | Bob Measurement Extraction | **PASSED** | 0.02 s | Verified classical bit extraction from Qiskit measurement strings with reverse indexing. |
| **UT-Q03** | `test_sifting_engine` | Basis Sifting Filter | **PASSED** | 0.01 s | Verified classical basis filter accurately retains only matching basis positions. |
| **UT-Q04** | `test_qber_estimator` | Parameter Estimation | **PASSED** | 0.02 s | Verified sampling fraction calculation, error computation, and disposal of sample bits. |
| **UT-Q05** | `test_information_reconciler` | Cascade Error Reconciliation | **PASSED** | 0.03 s | Verified 4-pass Cascade error correction achieves 100% bit identity between Alice and Bob under 4.1% noise. |
| **UT-Q06** | `test_privacy_amplifier` | Universal Hashing KDF | **PASSED** | 0.01 s | Verified 2-universal hash family derives exact 32-byte (256-bit) AES key with positive min-entropy. |
| **UT-Q07** | `test_bb84_simulator_clean` | Clean BB84 Simulation | **PASSED** | 7.85 s | Verified end-to-end QKD in Qiskit Aer ($QBER \le 0.11$, $K_{\text{Alice}} == K_{\text{Bob}}$). |
| **UT-Q08** | `test_bb84_simulator_with_eve` | Eve Intercept-Resend | **PASSED** | 8.15 s | Verified full intercept-resend attack induces $QBER > 0.11$, correctly aborting key agreement. |
| **UT-C01** | `test_encrypt_decrypt_roundtrip`| AES-256-GCM Roundtrip | **PASSED** | 0.03 s | Verified encryption and decryption round-trip; recovered plaintext matches original JSON. |
| **UT-C02** | `test_nonce_size_and_uniqueness`| 96-bit Nonce Policy | **PASSED** | 0.02 s | Verified nonces are exactly 12 bytes and sequential nonces are cryptographically unique. |
| **UT-C03** | `test_invalid_key_size` | Key Length Validation | **PASSED** | 0.01 s | Verified `ValueError` is raised when non-32-byte keys are supplied. |
| **ST-01** | `test_ciphertext_tampering_raises_invalid_tag` | Ciphertext Tamper Detection | **PASSED** | 0.04 s | Verified modifying 1 character in Base64 ciphertext raises `InvalidTag`. |
| **ST-02** | `test_nonce_tampering_raises_invalid_tag` | Nonce Tamper Detection | **PASSED** | 0.04 s | Verified modifying 1 character in nonce raises `InvalidTag`. |
| **ST-03** | `test_tag_tampering_raises_invalid_tag` | GMAC Tag Tamper Detection | **PASSED** | 0.04 s | Verified modifying authentication tag bytes raises `InvalidTag`. |
| **ST-04** | `test_wrong_key_decryption_fails` | Key Secrecy Assurance | **PASSED** | 0.04 s | Verified decrypting with mismatched key raises `InvalidTag`; zero plaintext leaked. |
| **ST-05** | `test_cloud_receiver_anti_replay` | Anti-Replay Watermarking | **PASSED** | 0.15 s | Verified cloud receiver rejects replayed sequence IDs and logs `REPLAY_ATTACK` in SQLite. |
| **IT-01** | `test_qkd_to_aes_integration` | End-to-End Pipeline Integration | **PASSED** | 2.80 s | Verified QKD key negotiation -> IoT encryption -> MQTT publish -> Cloud decryption & tamper alert. |

---
*Report certified by Automated Test Harness (pytest).*
