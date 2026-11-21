# RESEARCH REPRODUCIBILITY AUDIT AND STATUS
## HYBRID-QKD-BB84-AES256-GCM-MQTT-IOT-PIPELINE
**Branch:** `verification/publication-readiness` | **Head Commit:** `525676d`  
**Auditor:** Research Reproducibility Lead & QA Lead

---

### Reproducibility Verification Summary

This document certifies the exact software environment, raw dataset provenance, determinism controls, and step-by-step verification procedures required to reproduce every empirical result in this project.

```mermaid
flowchart TD
    Env[Environment & Python 3.12] --> Tests[Unit & Integration Test Suite (18/18 Pass)]
    Tests --> RawData[Raw Experiment Datasets (Exp 1-7 CSVs)]
    RawData --> VerifScripts[Independent Verification Scripts]
    VerifScripts --> PaperTables[Manuscript Tables 1-8]
```

---

### 1. Host Runtime & Environment Specification

| Parameter | Specification | Verified Status |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Enterprise (10.0.26100) / Linux (Ubuntu 22.04 LTS compatible) | Pass |
| **CPython Interpreter** | Python 3.12.10 (tags/v3.12.10:00f043d, AMD64, 64-bit) | Pass |
| **Quantum Framework** | `qiskit==2.6.1`, `qiskit-aer==0.18.2` | Pass |
| **Cryptographic Engine** | `cryptography==49.0.0` (OpenSSL 3.x backend) | Pass |
| **MQTT Client** | `paho-mqtt==2.1.0` | Pass |
| **Scientific Stack** | `numpy==2.4.4`, `scipy==1.17.1`, `pandas==3.0.2`, `matplotlib==3.10.9` | Pass |
| **Web Service Stack** | `flask==3.1.3`, `werkzeug==3.1.3`, `jinja2==3.1.6` | Pass |
| **Test Runner** | `pytest==9.0.3` | Pass |

---

### 2. Test Suite Execution & Status

Execution of the entire test suite confirms **18 passed tests in 9.16 seconds**:

```powershell
python -m pytest tests/ -v
```

#### Test Execution Manifest:
* `tests/unit/test_qkd.py`:
  * `test_alice_state_preparation`: PASS (basis rotation correctness)
  * `test_bob_measurement`: PASS (projective measurement statistics)
  * `test_sifting_efficiency`: PASS (sifting retention $\approx 50\%$)
  * `test_qber_noise_correlation`: PASS (QBER matches depolarizing noise)
  * `test_cascade_reconciliation`: PASS (100% error-free key correction)
  * `test_privacy_amplification_entropy`: PASS (Toeplitz compression)
* `tests/unit/test_crypto.py`:
  * `test_aes_gcm_encrypt_decrypt`: PASS (NIST vector roundtrip)
  * `test_nonce_uniqueness`: PASS (monotonic counter verification)
  * `test_tampered_ciphertext_rejected`: PASS (tag mismatch raises `InvalidTag`)
  * `test_hkdf_derivation`: PASS (RFC 5869 context separation)
  * `test_payload_serialization`: PASS (JSON payload encoding/decoding)
* `tests/integration/test_pipeline.py`:
  * `test_end_to_end_simulated_pipeline`: PASS (5-frame QKD-to-DB flow)
  * `test_qkd_session_rekey_flow`: PASS (session transition)
  * `test_corrupt_packet_pipeline_handling`: PASS (rejection of corrupted payload)
* `tests/security/test_security.py`:
  * `test_eve_intercept_resend_detection`: PASS (QBER threshold abort at $\alpha=1.0$)
  * `test_replay_attack_prevention`: PASS (duplicate nonce rejection)
  * `test_unauthenticated_header_tampering`: PASS (AAD modification rejection)
  * `test_mitm_classical_channel_abort`: PASS (key mismatch rejection)

---

### 3. Raw Data Provenance & Verification Matrix

All reported plots and manuscript tables derive directly from preserved raw CSV datasets in `experiments/raw_results/`:

| Dataset File | Trials | Key Variables Measured | Provenance & Generator | Manuscript Table / Figure |
| :--- | :--- | :--- | :--- | :--- |
| `exp1_qkd_scaling.csv` | 250 | $N \in [512, 8192]$, duration, sifted bits | Measured via `run_experiments.py` (Exp 1) | Table 1, Fig 3 |
| `exp2_qber_noise.csv` | 250 | $p \in [0.0, 0.20]$, measured QBER, abort | Measured via `run_experiments.py` (Exp 2) | Table 2, Fig 4 |
| `exp3_cascade_efficiency.csv` | 250 | Error rate, parity leakage, $f_{\text{EC}}$ | Measured via `run_experiments.py` (Exp 3) | Table 3, Fig 5 |
| `exp4_privacy_amplification.csv` | 250 | Block size, PA duration, throughput | Measured via `run_experiments.py` (Exp 4) | Table 5, Fig 6 |
| `exp5_aes_overhead.csv` | 500 | Payload size (32B-4KB), enc/dec latency | Measured via `run_experiments.py` (Exp 5) | Table 6, Fig 7 |
| `exp6_e2e_latency.csv` | 500 | Frame latency, queue vs socket | Measured via `run_experiments.py` (Exp 6) | Table 7, Fig 8 |
| `exp7_baseline_comparison.csv` | 100 | QKD vs ML-KEM-512 vs ECDH vs RSA | Hybrid (Local Qiskit + Shehzadi et al. 2025) | Table 7, Fig 9 |

#### Independent Re-Verification Scripts:
1. **Eve Interception Statistics:**
   * Script: `verify_eve_statistics_comprehensive.py`
   * Output: `empirical_eve_detection_verified.csv`
   * Trials: 490 total runs across 7 configurations ($\alpha \in [0.0, 1.0]$).
   * Verified: Interception rates $\ge 0.50$ yield $100\%$ detection.
2. **Finite-Key Derivation Spectrum:**
   * Script: `finite_key_derivation.py`
   * Output: `finite_key_derivation_spectrum.csv`
   * Verified: All 36 configurations calculated independently from first principles. Resolves transcription error in previous report for $N=8192, \text{QBER}=0.04$ ($\ell_{\text{engineering}} = 1400$, $\ell_{\text{composable}} = 334$).

---

### 4. Turnkey Step-by-Step Reproduction Guide

#### Step 1: Clone Repository & Check Out Branch
```bash
git checkout verification/publication-readiness
```

#### Step 2: Establish Virtual Environment & Install Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### Step 3: Run Full Verification Test Suite
```bash
python -m pytest tests/ -v
```

#### Step 4: Verify Finite-Key Mathematical Spectrum
```bash
python finite_key_derivation.py
```

#### Step 5: Verify Eve Statistical Distribution
```bash
python verify_eve_statistics_comprehensive.py
```

#### Step 6: Execute End-to-End Pipeline Demonstration
```bash
python run_pipeline.py
```

#### Step 7: Launch Interactive Web Dashboard
```bash
python dashboard/app.py
# Open browser at http://localhost:5000
```
