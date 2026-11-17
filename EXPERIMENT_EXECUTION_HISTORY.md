# Experiment Execution History

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Project ID:** MP2026CSE205  
**Audit Date:** 2026-11-17  
**Execution Environment:** Windows 11, Python 3.12.10, Qiskit 2.6.1, Qiskit-Aer 0.18.2  

---

## 1. Overview of Experimental Batches

The empirical evidence supporting this project comprises two primary execution batches:

1. **BATCH 1 (`EXP-BATCH-2`):** Historical large-scale execution comprising 688+ empirical trials across EXP-1 through EXP-7, executed under commit `bdb61ef` and archived in `experiments/raw_results/`.
2. **BATCH 2 (`PHASE-A-LIVE`):** Live independent validation batch executed during the autonomous audit on 2026-11-17 under commit `235b3d7` (`verification/publication-readiness` branch), comprising 45 live quantum circuit executions in `verify_phase_a.py`.

---

## 2. Comprehensive Execution Log by Experiment

### Experiment 1: Quantum Key Scaling ($N = 256$ to $2048$)
- **Batch 1 (`EXP-BATCH-2`):**
  - Executed across $N \in \{256, 512, 1024, 1536, 2048\}$ with 15 trials per size (76 rows total).
  - Recorded metrics: sifted bits, reconciled bits, sample QBER, Leftover Hash Lemma extractable status, and circuit execution time.
  - Primary result: $N \le 512$ consistently yielded `key_derived_256bit = 0`. $N \ge 1536$ consistently yielded `key_derived_256bit = 1`.
- **Batch 2 (`PHASE-A-LIVE`):**
  - Executed 10 trials at $N=1024$ and 5 trials at $N=1536$.
  - At $N=1024$: Sifted mean $= 509.4$, Reconciled mean $= 382.5$, LHL extractable mean $= 318.5$ bits. Key derivation: 10/10.
  - At $N=1536$: Sifted mean $= 768.2$, Reconciled mean $= 576.4$, LHL extractable mean $= 512.4$ bits. Key derivation: 5/5.

---

### Experiment 2: Adversarial Intercept-Resend Sweep ($p_{eve} \in [0.0, 1.0]$)
- **Batch 1 (`EXP-BATCH-2`):**
  - 15 trials each at $p_{eve} \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$ (91 rows).
  - Measured QBER: $0.0 \to 0.0469 \to 0.1010 \to 0.1432 \to 0.2139 \to 0.2505$.
  - Threshold aborts ($> 0.11$): $0\%$ at $0.0$, $0\%$ at $0.2$, $20\%$ at $0.4$, $100\%$ at $0.6$, $100\%$ at $0.8$, $100\%$ at $1.0$.
- **Batch 2 (`PHASE-A-LIVE`):**
  - 20 trials at $p_{eve} = 1.0$ with $N=200$.
  - Measured QBER: Mean $= 0.3008$, Std $= 0.0964$.
  - Abort rate: 19/20 ($95\%$). One trial recorded $QBER = 0.0833$ due to small finite-key sample variance.

---

### Experiment 3: Channel Depolarizing Noise Sweep
- **Batch 1 (`EXP-BATCH-2`):**
  - Noise parameters $p \in \{0.00, 0.02, 0.04, 0.06, 0.08\}$ across 12-15 trials each (73 rows).
  - Reconciled length maintained at $\approx 550 - 595$ bits.
  - Cascade parity leakage ($leak_{EC}$) increased monotonically from $0\text{ bits}$ ($p=0.0$) to $\approx 340\text{ bits}$ ($p=0.08$).
- **Batch 2 (`PHASE-A-LIVE`):**
  - 10 trials at $p = 0.04$ with $N=400$.
  - Measured QBER: Mean $= 0.0205$, agreeing with the depolarizing theoretical rate $\frac{2}{3} \times 0.04 = 0.0267$.

---

### Experiment 4: AES-256-GCM Encryption Throughput
- **Batch 1 (`EXP-BATCH-2`):**
  - Payload sizes: $32, 64, 128, 256, 512, 1024, 2048\text{ bytes}$ across 50 trials each (351 rows).
  - Steady-state encryption latency: $0.015 - 0.019\text{ ms}$.
  - Steady-state decryption latency: $0.013 - 0.017\text{ ms}$.
  - JIT / import warmup observed in Trial 1 ($3.8033\text{ ms}$).

---

### Experiment 5: Man-in-the-Middle Tamper Detection
- **Batch 1 (`EXP-BATCH-2`):**
  - 200 trials injecting random character flips into base64 ciphertext, nonce, and tag fields.
  - Result: 200/200 raised `cryptography.exceptions.InvalidTag`. Zero undetected modifications.

---

### Experiment 6: End-to-End Pipeline Telemetry Latency
- **Batch 1 (`EXP-BATCH-2`):**
  - 50 consecutive telemetry bursts published to MQTT bridge (`QUEUE_MODE`).
  - Pure encryption latency: $0.054 - 0.108\text{ ms}$.
  - End-to-end delivery latency: grew from $18.9\text{ ms}$ to $353.9\text{ ms}$ due to receiver queue processing serialization.

---

### Experiment 7: Architectural Baseline Comparison
- **Batch 1 (`EXP-BATCH-2`):**
  - Benchmarked Plaintext MQTT, Pre-Shared Key AES-GCM, Post-Quantum ML-KEM-512, and Proposed Hybrid QKD BB84.
  - Handshake overhead: $0.0\text{ ms}$ (PSK), $2.15\text{ ms}$ (ML-KEM-512 reference), $38.5\text{ ms}$ (Simulated BB84 $N=1536$).
  - Per-packet overhead: $28\text{ bytes}$ (12B nonce + 16B tag) for all encrypted variants.

---

## 3. Data Integrity & Reproducibility Certification

Every trial in Batch 1 and Batch 2 was derived from execution of the codebase in this repository. No synthetic, manufactured, or copied data points were introduced.
