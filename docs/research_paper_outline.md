# Research Paper Outline & Manuscript Structure

**Proposed Paper Title:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Telemetry over MQTT  
**Target Format:** IEEE Transactions / Conference Double-Column LaTeX  
**Date:** November 2026

---

## 1. Structural Overview & Section Assignments

- **Title & Author Block:** Rohan Bhutani, Anirudh Panwar, Shruti Sharma, Ananya Sharma, and Mohammad Wazid (Supervisor), Department of Computer Science & Engineering, Graphic Era Deemed to be University, Dehradun, India.
- **Abstract (200–250 words):** Context (quantum vulnerability of IoT PKC), problem (lack of post-processing and empirical integration in prior QKD-IoT works), proposed approach (IBM Qiskit Aer BB84 + Information Reconciliation + Universal Hash KDF + AES-256-GCM + MQTT), key experimental results (QBER 0.0% clean, 24.8% Eve, E2E latency < 1 ms in Queue and < 5 ms in MQTT, 100% tamper detection), and impact.
- **Keywords (5–7):** Quantum Key Distribution (QKD), BB84 Protocol, Internet of Things (IoT) Security, AES-256-GCM, MQTT, Information Reconciliation, Post-Quantum Cryptography.

---

## 2. Detailed Section Blueprint

1. **Section I: Introduction**
   - Growth of IoT and criticality of edge telemetry (smart grid, healthcare, industrial control).
   - The quantum computing threat: Shor's algorithm breaking RSA/ECC; the "Harvest Now, Decrypt Later" threat.
   - PQC vs QKD: Computational vs physical information-theoretic foundations.
   - Core research challenge: Bridging quantum key generation with resource-constrained IoT messaging.
   - Summary of major contributions.

2. **Section II: Related Work & Research Gap**
   - Survey of QKD simulation frameworks (Qiskit Aer, NetSquid, QuNetSim).
   - Survey of hybrid QKD-IoT literature and analysis of the "Information Reconciliation void."
   - Survey of IoT transport protocols and MQTT security limitations.
   - Detailed side-by-side comparative table against prior art.
   - Explicit formulation of the research gap.

3. **Section III: Proposed System Architecture**
   - End-to-end system model: Alice (Quantum Simulator), Bob (Cloud Ingestion Node), IoT Sensor Client, MQTT Broker, Cloud Receiver, SQLite Database, and Dashboard.
   - Threat Model: Classical Dolev-Yao network adversary + Quantum Intercept-Resend adversary (Eve).

4. **Section IV: Quantum Key Agreement & Post-Processing Methodology**
   - Mathematical formulation of BB84 state preparation ($Z$ and $X$ bases) and unitary gates in Qiskit.
   - Eve intercept-resend attack model and theoretical derivation of $25\%$ expected error.
   - Classical basis sifting and parameter estimation sampling.
   - Interactive Information Reconciliation protocol (parity search error correction).
   - Universal-hash privacy amplification and finite-key security bounds.

5. **Section V: Application-Layer Cryptographic Binding & MQTT Protocol**
   - Binding the 256-bit derived key into NIST SP 800-38D AES-256-GCM.
   - Nonce management policy (unique 96-bit CSPRNG nonces).
   - Transport envelope format (Base64 JSON over topic `iot/secure/data`).
   - Anti-replay sequence validation and `InvalidTag` tamper detection.

6. **Section VI: Experimental Setup & Implementation Testbed**
   - Hardware and software environment (Qiskit 2.x, Qiskit Aer, Paho-MQTT, SQLite3).
   - Testbed configuration: Real MQTT (Mosquitto) vs In-Memory Queue fallback.
   - Baseline selection: Plaintext MQTT, Pre-shared AES-GCM, and Post-Quantum ML-KEM-512 (Kyber).

7. **Section VII: Experimental Results & Performance Evaluation**
   - BB84 execution time and QBER vs Qubit block size ($N \in [128, 2048]$).
   - QBER vs Eve interception probability ($p_{\text{eve}} \in [0.0, 1.0]$) and statistical threshold verification.
   - Channel noise resilience curves under depolarizing noise.
   - AES-256-GCM encryption and decryption latency vs payload size.
   - End-to-end telemetry latency: MQTT vs Queue.
   - Comparative baseline evaluation (overhead, packet sizes, CPU/RAM footprint).

8. **Section VIII: Security Analysis & Discussion**
   - Resistance to quantum attacks (Grover 128-bit margin, Shor immunity).
   - Resistance to classical attacks (man-in-the-middle bit-flipping, replay, eavesdropping).
   - Discussion of finite-key constraints and hardware scalability.

9. **Section IX: Limitations & Threats to Validity**
   - Honest disclosure of simulation vs optical hardware boundary.
   - Assumption of authenticated classical channels for basis exchange.

10. **Section X: Conclusion & Future Work**
    - Summary of findings.
    - Future roadmap: Integration with hardware optical testbeds and hybrid PQC-QKD protocols.

11. **References:** Real, verified DOI-backed citations from `research/bibliography.bib`.
