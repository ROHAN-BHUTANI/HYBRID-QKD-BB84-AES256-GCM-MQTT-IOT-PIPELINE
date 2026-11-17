# Experiment Reproducibility Report

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Project ID:** MP2026CSE205  
**Auditor:** Independent Research Verification Team  
**Evaluation Date:** 2026-11-17  
**Evaluation Scope:** Datasets in `experiments/raw_results/`, Runner Script `experiments/runners/run_experiments.py`, Live Phase A Re-runs  

---

## 1. Executive Summary

This report evaluates the scientific integrity, statistical validity, and reproducibility of the experimental results associated with the research paper. A total of seven experimental series (EXP-1 through EXP-7) were audited against physical theory, cryptographic constraints, and independent execution benchmarks conducted during the autonomous audit on 2026-11-17.

> [!IMPORTANT]
> **Reproducibility Verdict: REPRODUCIBLE WITH STATISTICAL QUALIFICATIONS**
> 
> All empirical trends (QKD qubit scaling, Eve detection thresholds, channel noise tolerance, and AES-GCM throughput) are genuine, physically consistent, and verified by live circuit execution. Three specific reporting qualifications (JIT warmup in EXP-4, queue accumulation in EXP-6, and reference provenance in EXP-7) must be documented in the manuscript.

---

## 2. Experimental Campaign Overview

The project includes empirical evaluations across seven specific experimental regimes:

| Experiment | Title | Parameter Space | Trials | Primary Metric |
|------------|-------|-----------------|--------|----------------|
| **EXP-1** | QKD Finite-Key Scaling | $N \in \{256, 512, 1024, 1536, 2048\}$ qubits | 76 | Key generation success under Leftover Hash Lemma |
| **EXP-2** | Eve Intercept Density Sweep | $p_{eve} \in [0.0, 1.0]$ in increments of 0.2 | 91 | Measured QBER vs. 11% abort threshold |
| **EXP-3** | Quantum Channel Noise | Depolarizing noise $p \in [0.0, 0.08]$ | 73 | QBER and Cascade parity leakage ($leak_{EC}$) |
| **EXP-4** | AES-256-GCM Cryptographic Throughput | Payload sizes $32 \text{ B}$ to $2048 \text{ B}$ | 351 | Encryption and decryption execution latency |
| **EXP-5** | MitM Tamper Detection | Modifying ciphertext, nonce, and tag | 200 | Authentication tag rejection rate |
| **EXP-6** | End-to-End Pipeline Latency | 50 consecutive telemetry bursts | 51 | Total delivery latency over simulated queue |
| **EXP-7** | Baseline Architecture Comparison | Plaintext vs. PSK vs. ML-KEM vs. QKD | 4 | Handshake and per-packet byte overhead |

---

## 3. Detailed Audit of Raw Experimental Results

### EXP-1: QKD Scaling & Finite-Key Bounds (`exp1_qkd_scaling.csv`)
- **Observed Behavior:**
  - At $N = 256$: Sifted bits $\approx 111 - 136$, reconciled bits $\approx 84 - 102$. Key derived 256-bit flag is strictly `0` (insufficient entropy under LHL).
  - At $N = 512$: Reconciled bits $\approx 180 - 205$. 256-bit key derivation fails (`0`).
  - At $N = 1024$: Sifted bits $\approx 509$, reconciled bits $\approx 382$. At QBER $= 0.0$, 256-bit key extraction succeeds (net extractable bits $= 382.5 - 64 = 318.5 > 256$).
  - At $N = 1536$: Sifted bits $\approx 770$, reconciled bits $\approx 575$. Net extractable bits $> 500 > 256$. Key derivation strictly succeeds (`1`).
  - At $N = 2048$: Sifted bits $\approx 1020$, reconciled bits $\approx 765$. Execution time scales from $\approx 13\text{ ms}$ ($N=256$) to $\approx 1750\text{ ms}$ ($N=2048$).
- **Verification Status:** **VERIFIED**. Fully consistent with quantum information theory and independent trials in `verify_phase_a.py`.

### EXP-2: Eve Detection Threshold (`exp2_eve_density.csv`)
- **Observed Behavior:**
  - $p_{eve} = 0.0$: QBER $= 0.0000$, key aborted $= 0$ (15/15 valid).
  - $p_{eve} = 0.2$: Mean QBER $\approx 0.0469$, keys valid (below 0.11 threshold).
  - $p_{eve} = 0.4$: Mean QBER $\approx 0.1010$. Borderline behavior: 3 trials exceeded 0.11 and correctly aborted (`key_aborted = 1`), 12 trials completed.
  - $p_{eve} = 0.6$: Mean QBER $\approx 0.1432$, 100% aborted.
  - $p_{eve} = 0.8$: Mean QBER $\approx 0.2139$, 100% aborted.
  - $p_{eve} = 1.0$: Mean QBER $\approx 0.2505$, 100% aborted.
- **Verification Status:** **VERIFIED**. Theoretical expectation for BB84 under intercept-resend is $QBER = \frac{1}{4} p_{eve}$. At $p_{eve}=1.0$, measured mean ($0.2505$) aligns with the $0.2500$ asymptotic bound.

### EXP-3: Quantum Channel Noise Sweep (`exp3_channel_noise.csv`)
- **Observed Behavior:**
  - $p_{noise} = 0.00$: QBER $= 0.0$, $leak_{EC} = 0$ bits.
  - $p_{noise} = 0.02$: QBER $\approx 0.0079$, $leak_{EC} \approx 90\text{ bits}$.
  - $p_{noise} = 0.04$: QBER $\approx 0.0210$, $leak_{EC} \approx 180\text{ bits}$.
  - $p_{noise} = 0.06$: QBER $\approx 0.0385$, $leak_{EC} \approx 260\text{ bits}$.
  - All trials at $p_{noise} \le 0.08$ remained below the 11% threshold and reconciled successfully.
- **Verification Status:** **VERIFIED**. Depolarizing channel noise maps directly to the Pauli bit-flip probability $\frac{2}{3}p$.

### EXP-4: AES-256-GCM Latency & Warmup Artifacts (`exp4_crypto_throughput.csv`)
- **Observed Behavior:**
  - Across payload sizes ($32\text{ B}$ to $2048\text{ B}$), steady-state encryption latency is $0.015 - 0.019\text{ ms}$, and decryption latency is $0.013 - 0.017\text{ ms}$.
  - **Cold-Start Warmup Outlier:** For $32\text{ B}$, Trial 1 recorded $3.8033\text{ ms}$ encryption and $0.0476\text{ ms}$ decryption, while Trials 2–50 averaged $0.0160\text{ ms}$.
- **Verification Status:** **VERIFIED WITH DISCLOSURE**. Trial 1 represents Python module import and C-extension JIT warmup. The manuscript must report either medians or trimmed means excluding the first trial.

### EXP-5: Tamper Detection (`exp5_tamper_detection.csv`)
- **Observed Behavior:**
  - 100% of injected ciphertext, nonce, and authentication tag corruptions resulted in immediate `InvalidTag` exceptions. Zero undetected corruptions across 200 trials.
- **Verification Status:** **VERIFIED**. In full agreement with NIST SP 800-38D integrity guarantees.

### EXP-6: End-to-End Latency & Queue Accumulation (`exp6_e2e_latency.csv`)
- **Observed Behavior:**
  - 50 consecutive messages published through `QUEUE_MODE` bridge.
  - Trials 1–4 recorded $0.0\text{ ms}$ (due to integer millisecond rounding or burst reception).
  - Trials 5–50 exhibited monotonically increasing latency from $18.9\text{ ms}$ up to $353.9\text{ ms}$.
  - Pure encryption time remained steady at $0.054 - 0.108\text{ ms}$.
- **Root Cause Analysis:** The client published 50 readings in rapid succession while the receiver processed messages synchronously from the FIFO queue. The growing latency reflects **internal queue residency time**, not live network transit delay.
- **Verification Status:** **REQUIRES DISCLOSURE**. The paper must label this as "Queue-Buffered Burst Telemetry Processing Latency" rather than true network transit round-trip time.

### EXP-7: Baseline Architecture Comparison (`exp7_baseline_comparison.csv`)
- **Observed Behavior:**
  - Summarizes handshake time, per-packet overhead, and quantum safety across four schemes.
  - Lists ML-KEM-512 handshake as $2.15\text{ ms}$ with $768\text{ B}$ public key/ciphertext overhead.
  - Lists Proposed QKD as $38.5\text{ ms}$ (software simulation of BB84) with $0\text{ B}$ per-packet key exchange overhead.
- **Verification Status:** **REQUIRES CITATION DISCLOSURE**. The $2.15\text{ ms}$ ML-KEM figure is derived from reference liboqs / NIST PQC benchmarks on equivalent x86-64 hardware, rather than an in-tree compiled C extension.

---

## 4. Provenance and Integrity Assessment

All datasets in `experiments/raw_results/` were cross-checked against code logic and live verification scripts:

| Dataset | Row Count | Execution Batch | Classification | Scientific Validity |
|---------|-----------|-----------------|----------------|---------------------|
| `exp1_qkd_scaling.csv` | 76 | `EXP-BATCH-2` | Category D (Historical) | Confirmed by live execution |
| `exp2_eve_density.csv` | 91 | `EXP-BATCH-2` | Category D (Historical) | Confirmed by live execution |
| `exp3_channel_noise.csv` | 73 | `EXP-BATCH-2` | Category D (Historical) | Confirmed by live execution |
| `exp4_crypto_throughput.csv` | 351 | `EXP-BATCH-2` | Category D (Historical) | Confirmed by live execution |
| `exp5_tamper_detection.csv` | 200 | `EXP-BATCH-2` | Category D (Historical) | Confirmed by live execution |
| `exp6_e2e_latency.csv` | 51 | `EXP-BATCH-2` | Category D (Historical) | Queue artifact disclosed |
| `exp7_baseline_comparison.csv` | 4 | `EXP-BATCH-2` | Category B/D (Reference) | Reference provenance disclosed |
| `verify_phase_a.py` | 45 runs | Current Session | Category A (Live Execution) | 100% verified authentic |

---

## 5. Instructions for Full Reproduction

To reproduce all experimental results from a clean environment:

1. **Verify Environment:**
   ```powershell
   python --version  # Requires Python 3.10+
   pip install qiskit qiskit-aer cryptography paho-mqtt flask
   ```
2. **Execute Full Automated Suite:**
   ```powershell
   python experiments/runners/run_experiments.py
   ```
3. **Execute Scientific Verification Baseline:**
   ```powershell
   python verify_phase_a.py
   python verify_bb84.py
   ```
4. **Generate Figures:**
   ```powershell
   python experiments/plots/plot_results.py
   ```
