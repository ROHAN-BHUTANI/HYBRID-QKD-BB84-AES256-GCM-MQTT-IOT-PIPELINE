# Scientific Experiment Protocol

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Experimental Objectives

This protocol defines the reproducible procedures for collecting empirical datasets across all four Research Questions:
- **EXP-1:** Characterizing BB84 circuit execution time, sifted key yield, and QBER across varying initial qubit block sizes ($N \in \{128, 256, 512, 1024, 2048\}$).
- **EXP-2:** Measuring QBER and key abort probability as a function of Eve's interception density ($p_{\text{eve}} \in [0.0, 1.0]$).
- **EXP-3:** Evaluating QBER and Information Reconciliation success under parameterized Qiskit depolarizing noise ($\lambda \in [0.0, 0.15]$).
- **EXP-4:** Measuring AES-256-GCM encryption and decryption throughput across realistic IoT payload sizes (32 B to 2048 B).
- **EXP-5:** Verifying 100% tamper detection rate under injected bit-flip alterations in ciphertext, nonce, and authentication tag.
- **EXP-6:** Evaluating end-to-end packet delivery latency comparing real network-based MQTT against the local in-memory Queue transport.
- **EXP-7:** Benchmarking system resource consumption (CPU utilization % and RSS memory MB) via `psutil`.

---

## 2. Experimental Execution Steps

### 2.1 Protocol for EXP-1 & EXP-2 (Quantum Sweeps)
1. Initialize Python environment with fixed master random seed (`SEED = 42`).
2. Instantiate `BB84Simulator(AerSimulator())`.
3. For each qubit size $N \in [128, 256, 512, 1024, 2048]$:
   - For Eve disabled ($p_{\text{eve}} = 0.0$) and Eve active ($p_{\text{eve}} \in \{0.2, 0.4, 0.6, 0.8, 1.0\}$):
     - Execute 30 repeated simulation trials.
     - Record: execution time (ms), sifted bits, sample bits, observed errors, estimated QBER, is_valid status, memory footprint.
4. Export raw rows to `experiments/raw_results/qkd_sweeps.csv`.

### 2.2 Protocol for EXP-4 & EXP-5 (Cryptographic Benchmarks)
1. Generate fresh 256-bit AES key.
2. For payload sizes $S \in [32, 64, 128, 256, 512, 1024, 2048]$ bytes:
   - Execute 100 encryption operations; record nanosecond latency.
   - Execute 100 decryption operations; record nanosecond latency.
   - Inject single-bit flips into: (a) ciphertext byte 0, (b) nonce byte 0, (c) tag byte 0.
   - Verify that `InvalidTag` exception is raised in 100% of tampered cases.
3. Export raw rows to `experiments/raw_results/crypto_benchmarks.csv`.

### 2.3 Protocol for EXP-6 (End-to-End Latency: MQTT vs Queue)
1. Start local Mosquitto MQTT broker on port 1883.
2. Execute 50 message publications under `USE_SIMULATED_BROKER = False` (Real MQTT over TCP). Record $\text{Latency}_{\text{E2E}} = t_{\text{received}} - t_{\text{sent}}$.
3. Execute 50 message publications under `USE_SIMULATED_BROKER = True` (In-memory Queue). Record $\text{Latency}_{\text{E2E}}$.
4. Calculate mean, median, standard deviation, and 95% confidence intervals.
5. Export raw rows to `experiments/raw_results/e2e_transport_comparison.csv`.

---

## 3. Data Integrity & Reporting Rules
- No outlier removal without documented justification.
- Raw CSV files must be preserved unaltered in `experiments/raw_results/`.
- Processed statistics (mean, standard deviation, confidence intervals) must be computed programmatically via Python scripts into `experiments/processed_results/`.
