# Product Requirements Document (PRD)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Document Version:** 1.0.0  
**Project Team ID:** MP2026CSE205  
**Target Release:** Phase II Research Prototype & Publication Artifacts  
**Status:** Approved & Frozen

---

## 1. Executive Summary & Vision

The objective of this project is to develop, validate, and benchmark a research-grade software prototype demonstrating an end-to-end quantum-safe IoT security pipeline. The product bridges IBM Qiskit Aer BB84 quantum circuit simulation, information reconciliation, and universal-hash privacy amplification with NIST SP 800-38D AES-256-GCM authenticated encryption, delivering protected IoT telemetry over the MQTT protocol to a cloud receiver and real-time monitoring dashboard.

---

## 2. Target Personas & Use Cases

### Personas
- **P1: Quantum & Cybersecurity Researcher:** Needs to evaluate quantum channel parameters (QBER, depolarizing noise, Eve interception density) and measure cryptographic key agreement efficiency.
- **P2: IoT Cloud Systems Engineer:** Needs an ultra-low latency, authenticated telemetry ingestion pipeline with tamper detection and replay protection.
- **P3: Academic Evaluator / Thesis Committee:** Needs reproducible experimental benchmarks, open-source code, and verifiable scientific methodology.

### Core User Scenarios
- **US-1 (Clean Key Agreement):** Alice and Bob execute BB84 in Qiskit Aer across $N$ qubits under zero eavesdropping, sifting matching bases, verifying $\text{QBER} \le 11\%$, reconciling bits, and deriving a 256-bit AES key.
- **US-2 (Active Eavesdropping Abort):** Eve intercepts quantum states, inducing $\approx 25\%$ error on sifted bits; parameter estimation detects $\text{QBER} > 11\%$ and immediately aborts key establishment.
- **US-3 (Authenticated Telemetry Ingestion):** Edge sensor collects environmental data (temperature, humidity, pressure), encrypts with AES-256-GCM using a unique 96-bit nonce, publishes via MQTT, and the cloud receiver verifies the 128-bit authentication tag and persists data in $<1\text{ ms}$.
- **US-4 (Man-in-the-Middle Tamper Alert):** An active attacker alters ciphertext or nonce bytes in transit over MQTT; the cloud receiver detects GMAC verification failure (`InvalidTag`), rejects the payload, and logs an audit alert.

---

## 3. Product Scope & Functional Requirements

| ID | Feature | Priority | Description | Acceptance Criteria |
| :--- | :--- | :---: | :--- | :--- |
| **FR-01** | Qiskit BB84 Circuits | P0 | Quantum state preparation in $Z$ and $X$ bases and projective measurement using Qiskit Aer. | Must execute true unitary gates ($X$, $H$) and measure classical registers. |
| **FR-02** | Configurable Noise & Eve | P0 | Support configurable depolarizing noise channels and parameterized Eve intercept-resend attacks. | Must produce $\approx 25\%$ error under full interception ($p_{\text{eve}} = 1.0$). |
| **FR-03** | Basis Sifting | P0 | Classical basis reconciliation retaining matching basis choices. | Must achieve expected $\approx 50\%$ sifting yield on random bases. |
| **FR-04** | QBER Parameter Estimation | P0 | Random sampling of 25% of sifted bits to estimate error rate against $11\%$ abort cutoff. | Must abort when $\text{QBER} > 0.11$; must discard sampled bits. |
| **FR-05** | Information Reconciliation | P0 | Correct residual bit discrepancies between Alice and Bob before hashing. | Must eliminate bit errors when $\text{QBER} \le 0.11$, ensuring identical keys. |
| **FR-06** | Privacy Amplification | P0 | Derive 256-bit symmetric key using universal hashing bounds. | Output must be 32 bytes (256 bits) with uniform entropy. |
| **FR-07** | AES-256-GCM Encryption | P0 | Authenticated encryption with associated data (NIST SP 800-38D). | 96-bit unique nonce per message; 128-bit authentication tag. |
| **FR-08** | Anti-Replay Protection | P0 | Stateful monotonic sequence tracking on cloud receiver. | Must reject duplicated or out-of-order sequence numbers. |
| **FR-09** | Dual-Mode MQTT Transport | P0 | Real Paho-MQTT connection to Mosquitto + in-memory Queue fallback. | Must operate seamlessly in both modes; transport mode must be explicitly flagged in logs and benchmarks. |
| **FR-10** | SQLite Persistence | P0 | Relational storage for telemetry, QKD sessions, and security alerts. | ACID compliant schema with indexes and foreign keys. |
| **FR-11** | Interactive Web Dashboard| P1 | Golden-Black Flask dashboard displaying live metrics and controls. | Real-time REST polling, attack triggers, latency display. |
| **FR-12** | Benchmarking Suite | P0 | Automated script generating CSV datasets for all RQs. | Must record QKD time, QBER, crypto time, E2E latency, and CPU/RAM. |

---

## 4. Non-Functional Requirements (NFRs)

- **NFR-01 (Performance):** Total end-to-end packet delivery, tag verification, and decryption latency must be $< 1.0\text{ ms}$ in queue mode and $< 10.0\text{ ms}$ over local MQTT.
- **NFR-02 (Security):** 100% rejection rate for tampered ciphertexts and invalid authentication tags (`InvalidTag`).
- **NFR-03 (Reproducibility):** All experimental runs must support deterministic seed setting for statistical auditability.
- **NFR-04 (Portability):** Zero external mandatory OS-specific binary dependencies for fallback execution (pure Python + Qiskit Aer on Windows/Linux/macOS).
- **NFR-05 (Maintainability):** Modular architecture with full type hinting, docstrings, and comprehensive test suite (`tests/`).
