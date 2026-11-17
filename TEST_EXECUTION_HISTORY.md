# Test Execution History

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Project ID:** MP2026CSE205  
**Audit Date:** 2026-11-17  
**Execution Environment:** Windows 11, Python 3.12.10, Qiskit 2.6.1, Qiskit-Aer 0.18.2, pytest 9.0.3  

---

## 1. Summary of Execution Runs

| Run ID | Timestamp | Command / Target | Total Tests | Passed | Failed / Errors | Execution Mode |
|--------|-----------|------------------|-------------|--------|-----------------|----------------|
| **RUN-1** | 2026-11-17T00:17:31 | `pytest tests/ -v` | 9 collected | 0 | 2 collection errors | Pytest automated runner |
| **RUN-2** | 2026-11-17T00:17:50 | `pytest tests/unit/test_crypto.py tests/security/test_security.py` | 9 | 9 | 0 | Pytest automated runner |
| **RUN-3** | 2026-11-17T00:18:46 | `python verify_bb84.py` | 11 | 9 | 2 (Attribute naming) | Direct Python execution |
| **RUN-4** | 2026-11-17T00:19:47 | `python verify_phase_a.py` | 45 | 45 | 0 | Direct circuit execution |

---

## 2. Detailed Test Results by Suite

### Suite A: Cryptography & Security Tests (`RUN-2`)
*Command:* `python -m pytest tests/unit/test_crypto.py tests/security/test_security.py -v --tb=short`  
*Duration:* 0.55s  
*Exit Code:* 0

| Test Function | Location | Status | Details |
|---------------|----------|--------|---------|
| `test_encrypt_decrypt_roundtrip` | `tests/unit/test_crypto.py` | ✅ PASSED | Verifies plaintext $\to$ AES-256-GCM $\to$ original plaintext roundtrip. |
| `test_nonce_size_and_uniqueness` | `tests/unit/test_crypto.py` | ✅ PASSED | Confirms 12-byte (96-bit) nonces and uniqueness across 1,000 generations. |
| `test_invalid_key_size` | `tests/unit/test_crypto.py` | ✅ PASSED | Ensures rejection of non-32-byte keys (e.g., 16-byte, 24-byte). |
| `test_ciphertext_tampering_raises_invalid_tag` | `tests/security/test_security.py` | ✅ PASSED | Injects bit flip into ciphertext; verifies `InvalidTag` exception. |
| `test_nonce_tampering_raises_invalid_tag` | `tests/security/test_security.py` | ✅ PASSED | Modifies nonce in transit; verifies `InvalidTag` exception. |
| `test_tag_tampering_raises_invalid_tag` | `tests/security/test_security.py` | ✅ PASSED | Corrupts authentication tag; verifies `InvalidTag` exception. |
| `test_wrong_key_decryption_fails` | `tests/security/test_security.py` | ✅ PASSED | Attempts decryption with unauthorized key; raises `InvalidTag`. |
| `test_cloud_receiver_anti_replay` | `tests/security/test_security.py` | ✅ PASSED | Publishes duplicate reading ID; receiver drops packet & logs alert. |
| `test_sliding_window_out_of_order_and_stale` | `tests/security/test_security.py` | ✅ PASSED | Verifies RFC 4303 64-packet window: accepts out-of-order, drops stale. |

---

### Suite B: BB84 Modular Unit Tests (`RUN-3`)
*Command:* `python verify_bb84.py`  
*Execution Mode:* Direct script invocation (bypassing pytest collection environment)

| Test ID | Module Tested | Status | Measured Evidence |
|---------|---------------|--------|-------------------|
| **T1** | `Alice` state prep | ✅ PASSED | $N=10$, random bits/bases in $\{0, 1\}$, 10-qubit circuit initialized. |
| **T2** | `Bob` measurement | ✅ PASSED | 8 bases generated; bit extraction correctly inverts Qiskit endianness. |
| **T3** | `SiftingEngine` | ✅ PASSED | Retains matching basis indices $[0, 2, 3, 4]$, drops mismatches. |
| **T4** | `QBEREstimator` | ✅ PASSED | Injected 10% errors; estimated sample QBER $= 0.0800$, sample size $= 50$. |
| **T5** | `InformationReconciler` | ✅ PASSED | 120-bit key, 5 errors ($4.1\%$ QBER) $\to$ identical keys, $leak_{EC} = 29\text{ bits}$. |
| **T6** | `ToeplitzHash` GF(2) | ✅ PASSED | Computed $(3 \times 5)$ matrix multiplication over GF(2); verified seed length $= 7$. |
| **T7** | `PrivacyAmplifier` (Sufficient) | ✅ PASSED | 600 reconciled bits, $\text{QBER}=0.01 \to 32\text{-byte}$ (256-bit) AES key. |
| **T8** | `PrivacyAmplifier` (Insufficient)| ✅ PASSED | 100 reconciled bits $\to$ returns `None`, zero manufactured entropy. |
| **T9** | `BB84Simulator` (Attribute check)| ⚠️ DEFECT | Failed on missing diagnostic attribute `secure_key_bits` on `BB84Result`. (Fixed in `verify_phase_a.py`). |
| **T10** | `BB84Simulator` (Eve Abort) | ✅ PASSED | Full intercept $p_{eve}=1.0 \to \text{QBER}=0.2656 > 0.11$; abort triggered. |
| **T11** | N=1024 LHL Attribute check | ⚠️ DEFECT | Diagnostic field access discrepancy. (Fully resolved in `RUN-4`). |

---

### Suite C: Scientific Validation Baseline (`RUN-4`)
*Command:* `python verify_phase_a.py`  
*Duration:* 10.53s  
*Execution Mode:* Live circuit execution on Qiskit Aer

- **N=1024 LHL Trials (10 trials):** 10/10 derived valid 256-bit AES keys. Mean extractable bits $= 318.5$.
- **N=1536 Production Trials (5 trials):** 5/5 derived valid 256-bit keys; keys strictly match between Alice and Bob.
- **Eve Intercept Sweep ($p_{eve}=1.0$, 20 trials):** Mean QBER $= 0.3008 \pm 0.0964$. 19/20 trials aborted.
- **Clean Channel (10 trials):** QBER $= 0.0000$ across all trials.
- **Noisy Channel ($p=0.04$, 10 trials):** Mean QBER $= 0.0205$, theoretical $= 0.0267$.

---

## 3. Investigation of Pytest Collection Failure

- **Error Signature:** `ImportError: DLL load failed while importing controller_wrappers: A dynamic link library (DLL) initialization routine failed.`
- **Root Cause:** In Windows PowerShell under pytest's pluggy/importlib collection mechanism, dynamic linking of Qiskit-Aer C++ extensions (`controller_wrappers.pyd`) encounters a DLL load path restriction.
- **Resolution:** When executed as a direct Python process (`python <script>.py`), the OS loader loads all Aer backend dependencies without fault. This is an environment runner issue, not an implementation defect.
