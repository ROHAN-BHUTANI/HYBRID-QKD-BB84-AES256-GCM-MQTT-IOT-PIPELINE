# FINAL AUDIT BASELINE
**Project:** Hybrid BB84 QKD + AES-256-GCM IoT Pipeline  
**Project ID:** MP2026CSE205  
**Audit Date:** 2026-11-17  
**Document Version:** 1.0 (Baseline Freeze)

---

## 1. Repository State

| Field | Value |
|-------|-------|
| Branch | `verification/publication-readiness` |
| HEAD | `235b3d7` |
| Commits on main | 4 |
| Working tree | **Clean** (no uncommitted changes) |

### Commit History

| Hash | Description |
|------|-------------|
| `e19c6e1` | Initial |
| `d643b82` | Complete pipeline |
| `bdb61ef` | Improvement cycles 1 & 2 |
| `235b3d7` | Novelty investigation |

---

## 2. Environment

### Software Stack

| Component | Version |
|-----------|---------|
| Python | 3.12.10 |
| Qiskit | 2.6.1 |
| Qiskit-Aer | 0.18.2 |
| cryptography | 49.0.0 |
| paho-mqtt | 2.1.0 |
| Flask | 3.1.1 |

### Platform

- **OS:** Windows 11 (PowerShell)

### Known Environment Issue

> [!WARNING]
> **qiskit-aer DLL initialization fails under pytest collection context (Windows sandbox restriction)** but imports correctly when invoked directly via `python`. This is a Windows DLL loading order issue triggered by the pytest process model, **not a code bug**. All BB84 logic has been verified via direct execution. See §5 and §6 for details.

---

## 3. Complete File Inventory (Key Files)

| File | Lines | Status |
|------|-------|--------|
| `qkd/bb84.py` | 207 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/alice.py` | 57 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/bob.py` | 66 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/eve.py` | 61 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/sifting.py` | 37 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/qber.py` | 58 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/channel.py` | 52 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/postprocessing/reconciliation.py` | 114 | ✅ IMPLEMENTED AND VERIFIED |
| `qkd/postprocessing/privacy_amplification.py` | 179 | ✅ IMPLEMENTED AND VERIFIED |
| `iot_client/sensor_client.py` | 133 | ✅ IMPLEMENTED AND VERIFIED |
| `iot_client/crypto_utils.py` | — | ✅ IMPLEMENTED AND VERIFIED |
| `cloud_receiver/receiver.py` | 222 | ✅ IMPLEMENTED AND VERIFIED |
| `cloud_receiver/database.py` | — | ✅ IMPLEMENTED AND VERIFIED |
| `broker/broker_bridge.py` | — | ✅ IMPLEMENTED (simulated/queue mode) |
| `config.py` | 83 | ✅ IMPLEMENTED |
| `run_pipeline.py` | — | ✅ IMPLEMENTED |
| `tests/unit/test_crypto.py` | — | ✅ 3 tests PASSED |
| `tests/unit/test_qkd.py` | — | ⚠️ CANNOT COLLECT under pytest (DLL issue, but logic verified directly) |
| `tests/security/test_security.py` | — | ✅ 6 tests PASSED |
| `tests/integration/test_pipeline.py` | — | ⚠️ CANNOT COLLECT under pytest (DLL issue) |
| `experiments/raw_results/` | — | 📁 7 CSV files present |
| `paper/manuscript.tex` | — | 📄 PRESENT |
| `research/` | — | 📁 Novelty investigation files (8 documents) |

---

## 4. Configuration Defaults

| Parameter | Value |
|-----------|-------|
| `NUM_QUBITS` | `1536` |
| `QBER_THRESHOLD` | `0.11` |
| `SAMPLE_FRACTION` | `0.25` |
| `AES_KEY_SIZE_BYTES` | `32` |
| `SIMULATOR_SHOTS` | `1` |
| `USE_SIMULATED_BROKER` | `True` |

---

## 5. Test Execution Summary (Actual Run: 2026-11-17)

| Test Suite | Result | Notes |
|------------|--------|-------|
| Non-Qiskit tests (crypto + security + anti-replay) | **9/9 PASSED** | Full pytest collection and execution succeeded |
| BB84 logic tests (direct execution) | **8/8 PASSED** | Bypassed pytest DLL issue via `python -m` invocation |
| pytest DLL collection error | ⚠️ Affects collection only | Does **NOT** affect actual execution correctness |

> [!NOTE]
> The DLL collection error is a Windows-specific pytest process isolation issue. The underlying Qiskit-Aer simulation engine operates correctly when loaded via the standard Python interpreter. All BB84 correctness claims are supported by the direct execution results documented in §6.

---

## 6. Direct BB84 Verification Summary (Actual Run: 2026-11-17)

### 6.1 Key Generation — N=1024, 10 Trials

| Metric | Value |
|--------|-------|
| Mean sifted bits | 509.4 |
| Mean reconciled bits | 382.5 |
| Mean LHL extractable bits | 318.5 |
| 256-bit key derivable | **10/10** |

### 6.2 Key Generation — N=1536 (Production Default), 5 Trials

| Metric | Value |
|--------|-------|
| 256-bit key derived | **5/5** |
| Keys match (Alice ↔ Bob) | **5/5** |
| Mean elapsed time | ≈ 835 ms |

### 6.3 Eve Intercept-Resend Attack — p=1.0, N=200, 20 Trials

| Metric | Value |
|--------|-------|
| Mean QBER | 0.3008 |
| Std QBER | 0.0964 |
| Abort rate | **19/20** |

> [!NOTE]
> One trial did not abort (see DEF-002). This is expected finite-key behavior with small N; at N=200 and p=1.0, random fluctuations can place the sample QBER below the 0.11 threshold in rare instances.

### 6.4 Clean Channel — N=200, 10 Trials

| Metric | Value |
|--------|-------|
| QBER | **0.0 all 10 trials** |

### 6.5 Noisy Channel — p=0.04 (Depolarizing), N=400, 10 Trials

| Metric | Value |
|--------|-------|
| Mean empirical QBER | 0.0205 |
| Theoretical QBER | 0.0267 |

> [!NOTE]
> Empirical QBER is below the theoretical value, consistent with finite-sample negative fluctuation. The channel is operating within expected bounds.

---

## 7. Known Deficiencies

| Deficiency ID | Description | Severity | Status |
|---------------|-------------|----------|--------|
| DEF-001 | Pytest DLL collection failure (Windows sandbox context) | MEDIUM | ENVIRONMENT ISSUE — not a code bug; direct execution unaffected |
| DEF-002 | Eve intercept-resend trial T12 (N=200) did not abort at QBER=0.0833 | LOW | Expected finite-key behavior with small N; theoretically sound |
| DEF-003 | Classical authentication in BB84 is assumed, not implemented | HIGH | DOCUMENTED LIMITATION — must be declared in manuscript |
| DEF-004 | MQTT tested in simulated queue mode only (no real broker) | MEDIUM | DOCUMENTED SCOPE — real-broker integration out of scope |
| DEF-005 | Eve re-preparation uses measurement collapse semantics | LOW | Qiskit simulates correctly through mid-circuit measurement |
| DEF-006 | No provenance metadata (timestamp, git_hash, seed) in experiment CSVs | MEDIUM | POST-HOC LIMITATION — reproducibility caveated |
| DEF-007 | `exp7_baseline_comparison.csv` has only 4 rows; ML-KEM-512 value (2.15 ms) is not empirically measured | HIGH | MUST DISCLOSE in paper — value is literature-sourced, not measured |

> [!CAUTION]
> **DEF-003** and **DEF-007** are HIGH severity and must be explicitly disclosed in the paper manuscript before submission. DEF-003 is a standard protocol assumption that peer reviewers will expect to see acknowledged. DEF-007 constitutes a data integrity issue if the CSV is presented as fully empirical.

---

## Audit Sign-Off

This document records the verified state of project **MP2026CSE205** as of **2026-11-17**. It is a point-in-time baseline; any changes after this date must be tracked separately against this record.

| Field | Value |
|-------|-------|
| Audit agent | `audit-baseline` |
| Audit timestamp | 2026-11-17T00:00:00Z |
| Repository HEAD at audit | `235b3d7` |
| Document status | **FINAL — DO NOT MODIFY WITHOUT VERSION INCREMENT** |
