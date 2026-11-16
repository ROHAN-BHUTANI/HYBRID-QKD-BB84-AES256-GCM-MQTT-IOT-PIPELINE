# Rigorous Research Gap Analysis

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Deconstruction of Naive Novelty Claims

In student and early-stage engineering literature, three common novelty claims are frequently asserted:
1. *"First-ever combination of BB84 QKD, AES-256, and IoT."*  
   **Refutation:** This claim is demonstrably false. Farooq, Sharma, and Pradhan (IEEE WPMC 2024 [D3]), Rehman and Alharbi (*Smart Cities* 2025 [D1]), Chaturvedi et al. (*Scientific Reports* 2025 [C3]), and Biswas et al. (IEEE FNWF 2024 [C5]) have already proposed architectures combining QKD and symmetric ciphers for IoT.
2. *"A novel QBER threshold algorithm for eavesdropping detection."*  
   **Refutation:** Fiorini et al. (*Future Internet* 2024 [B4], *Computer Networks* 2026 [C2]) and Hubballi et al. (IEEE NQComp 2026 [B7]) have already formulated analytical and statistical threshold-based eavesdropper detection in Qiskit BB84 under noise.
3. *"Physical Quantum-Secured IoT Device."*  
   **Refutation:** No physical quantum optics, lasers, or single-photon avalanche photodetectors are fabricated in software projects. Claiming hardware quantum properties from a Qiskit software simulation is scientifically misleading.

---

## 2. Identification of Legitimate, Defensible Research Gaps

Through full-text extraction of priority literature and systematic comparison across our 32-paper corpus, four legitimate, unaddressed gaps emerge:

### Gap 1: The Broken Post-Processing Bridge in Hybrid QKD-IoT Literature
Existing literature combining QKD with IoT telemetry consistently omits **Information Reconciliation (Error Correction)**.
- Papers either assume a zero-noise channel ($QBER = 0$) where Alice and Bob magically hold identical sifted bits, OR they check that $QBER \le 11\%$ and directly hash the remaining sifted bits using SHA-256.
- In any physical or simulated channel with noise ($0 < QBER \le 0.11$), Alice and Bob hold bitstrings with a Hamming distance $d_H > 0$. Hashing these bitstrings causes the cryptographic avalanche effect, producing completely disparate keys ($K_{\text{Alice}} \neq K_{\text{Bob}}$) and causing 100% decryption failures at the cloud receiver.
- **The Gap:** No existing open-source hybrid prototype provides an end-to-end, reproducible implementation of a verified Information Reconciliation and Universal Hashing Privacy Amplification bridge connecting Qiskit circuits directly to AES-256-GCM.

### Gap 2: The Empirical End-to-End Performance Void for MQTT-Based QKD Telemetry
While Farooq et al. (2024) conceptually discussed QKD for MQTT, their conference paper provides no publicly available code, no microsecond-level latency breakdown (separating quantum simulation, reconciliation, hashing, encryption, broker transit, and cloud decryption), and no reproducible benchmark suite.
- Furthermore, existing benchmarks of IoT security (e.g., Kaganurmath et al. 2025 [E1], Dinculeana & Cheng 2019 [E2]) focus on classical TLS or Diffie-Hellman handshakes, which introduce hundreds of milliseconds of connection latency and are vulnerable to Shor's algorithm.
- **The Gap:** A lack of rigorous, empirical end-to-end latency, throughput, and CPU/memory profiling comparing QKD-derived symmetric telemetry over real MQTT against classical and post-quantum baselines.

### Gap 3: Absence of Stateful Cryptographic Hardening (Replay & Tamper Detection) in QKD-IoT Demonstrators
Current QKD-IoT prototypes evaluate confidentiality in isolation, ignoring transport-layer vulnerabilities documented in IoT security surveys (Granjal et al. 2015 [E3], Sharma & Bhushan 2025 [E4]).
- In MQTT networks, eavesdroppers can capture valid ciphertexts and replay them to corrupt time-series databases or actuator states.
- Most demonstrators lack explicit stateful anti-replay verification (monotonic sequence tracking within a freshness window) and fail to evaluate how AES-256-GCM's 128-bit Galois Message Authentication Code behaves under active Man-in-the-Middle bit-flipping attacks.
- **The Gap:** A hardened cryptographic envelope specification integrating 96-bit unique nonces, 128-bit GMAC tags, and monotonic sequence windows bound to quantum session keys.

### Gap 4: Lack of a Reproducible, Open-Source Unified Research & Educational Testbed
Survey papers by Raveendra Babu et al. (2024 [D4]), Yang et al. (2025 [D5]), and Mallick et al. (2026 [G1]) repeatedly highlight the absence of accessible, open-source testbeds that allow researchers and students to experiment with both quantum channel dynamics (noise, interception, sifting) and application-layer cloud telemetry in a single, cohesive environment.

---

## 3. Synthesis: The Defensible Core Research Problem

Based on these validated gaps, the defensible research problem is formulated as follows:

> **How can quantum key agreement simulated in IBM Qiskit Aer be rigorously reconciled and amplified to provide quantum-safe, authenticated symmetric encryption (AES-256-GCM) for resource-constrained IoT telemetry over MQTT, and what are the exact computational and latency trade-offs compared to classical and post-quantum key-establishment alternatives?**
