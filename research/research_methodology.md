# Formal Research Methodology & Experimental Framework

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Methodological Overview

This research employs a quantitative, experimental methodology combining:
1. **Quantum Circuit Simulation:** Modeling state-vector evolution, quantum gates, superposition, and projective measurements using IBM Qiskit and Qiskit Aer.
2. **Applied Cryptographic Engineering:** Implementing Information Reconciliation, Universal-Hash Privacy Amplification, and NIST SP 800-38D AES-256-GCM.
3. **Distributed IoT Systems Architecture:** Deploying an end-to-end telemetry pipeline across simulated edge sensors, MQTT message brokers (Eclipse Mosquitto), cloud ingestion services, and persistent SQLite storage.
4. **Empirical Benchmarking & Statistical Evaluation:** Conducting automated parameter sweeps across repeated trials with controlled random seeds, measuring execution latencies, resource footprints, and error rates with 95% confidence intervals.

---

## 2. Threat Model & Security Assumptions

Our threat model integrates both classical and quantum threat models:

### 2.1 The Classical Network Adversary (Dolev-Yao Model)
- **Capabilities:** Controls the classical communication channel between the IoT sensor, MQTT broker, and cloud receiver. The adversary can intercept, re-order, modify, replay, or inject arbitrary packets.
- **Goal:** Recover plaintext telemetry, forge valid sensor readings, or replay stale packets without detection.
- **Countermeasure:** NIST SP 800-38D AES-256-GCM authenticated encryption with strictly unique 96-bit nonces, 128-bit Galois MAC tags, and monotonic sequence number validation on the cloud receiver.

### 2.2 The Quantum Adversary (Eve / Intercept-Resend)
- **Capabilities:** Taps the optical/quantum channel between Alice and Bob during key agreement. Can perform intercept-resend attacks: intercepting flying qubits, measuring them in a chosen basis ($Z$ or $X$), and re-transmitting new qubits to Bob.
- **Goal:** Learn the negotiated key without being detected by Alice and Bob.
- **Physical Law Countermeasure:** Heisenberg Uncertainty Principle & No-Cloning Theorem. Because Eve cannot measure in non-orthogonal bases without disturbing the state, she introduces an expected 25% error on matching bases. Alice and Bob sacrifice a random 25% sample of sifted bits to estimate the Quantum Bit Error Rate (QBER). If $QBER > 11.0\%$, the session is immediately aborted.

### 2.3 Explicit Security Assumptions
1. **Classical Channel Authentication:** The public channel used for basis announcement and sifting is assumed to be authenticated (preventing classical impersonation during the basis exchange).
2. **True Random Number Generation:** Alice and Bob have access to cryptographically secure pseudorandom number generators (CSPRNG via Python `secrets`/`os.urandom`) for basis selection and nonces.
3. **Simulation Boundary:** Qiskit Aer accurately simulates single-qubit state vectors and unitary transformations. Hardware side-channel attacks on physical detectors (e.g., detector blinding, spatial mode attacks) are out of scope for software circuit simulation.

---

## 3. Experimental Design Matrix

| Experiment | Target Hypothesis | Independent Variables | Dependent Variables | Replications | Statistical Metric |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **EXP-1** | $H_1$ (QKD vs Qubits) | $N \in \{128, 256, 512, 1024, 2048\}$, Eve off | Sifted length, remaining length, QBER, QKD latency | 30 trials | Mean, std dev, 95% CI |
| **EXP-2** | $H_1$ (QBER vs Eve) | $p_{\text{eve}} \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$ | QBER, abort rate | 30 trials | Mean, std dev, t-test vs 0.11 |
| **EXP-3** | $H_1$ (Noise Sweeps) | Depolarizing error $\lambda \in [0.0, 0.15]$ | QBER, reconciliation success rate | 30 trials | Mean, std dev, threshold curves |
| **EXP-4** | $H_2$ (AES Latency) | Payload size $\in \{32, 64, 128, 256, 512, 1024, 2048\}$ B | Encryption time (ms), Decryption time (ms) | 100 trials | Mean, median, 99th percentile |
| **EXP-5** | $H_2$ (Tamper Detection)| Bit-flip position in ciphertext / tag | Tag verification failure rate (%) | 100 trials | Detection % (100% target) |
| **EXP-6** | $H_3$ (E2E Latency) | Transport: `MQTT_BROKER_MODE` vs `QUEUE_MODE` | End-to-end packet latency (ms) | 50 trials | Boxplot, mean, std dev |
| **EXP-7** | $H_4$ (Baselines) | Baseline: Plaintext vs PSK vs QKD vs Kyber-512 | Handshake time, message size, CPU/RAM | 20 trials | Relative overhead table |

---

## 4. Hardware & Software Environmental Specifications

All experiments will be conducted and reported with exact environmental parameters:
- **Host CPU:** Intel Core i-series / AMD Ryzen multi-core architecture.
- **Operating System:** Windows 11 AMD64.
- **Python Runtime:** Python 3.12.10 (AMD64).
- **Quantum Simulation Framework:** IBM Qiskit 2.x with Qiskit Aer 0.18.x.
- **Cryptographic Engine:** OpenSSL-backed Python `cryptography` 42.x (NIST SP 800-38D).
- **MQTT Transport:** Eclipse Mosquitto v2.x / Paho-MQTT 2.x.
- **Database Engine:** SQLite 3.x with WAL (Write-Ahead Logging) and ACID compliance.
- **Timing Precision:** `time.perf_counter()` and `time.time_ns()` for nanosecond-precision microbenchmarks.
- **Resource Profiling:** `psutil` sampling RSS memory (MB) and CPU process utilization (%).
