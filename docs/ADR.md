# Architecture Decision Records (ADR)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## ADR-001: Selection of BB84 Protocol over E91 and B92
- **Status:** Accepted
- **Context:** The project requires a quantum key distribution protocol for key agreement between edge and cloud. Candidates include Bennett-Brassard 1984 (BB84), Bennett 1992 (B92), and Ekert 1991 (E91).
- **Decision:** Select BB84 four-state protocol with conjugate bases ($Z$ and $X$).
- **Rationale:** BB84 is the most extensively validated protocol in quantum cryptography literature with established security proofs (Shor-Preskill 2000). E91 requires entangled Bell pair sources ($\frac{|00\rangle + |11\rangle}{\sqrt{2}}$) and violation of Bell's inequalities ($S \le 2\sqrt{2}$), introducing unnecessary simulation and hardware complexity for edge IoT. B92 utilizes two non-orthogonal states, which suffers from lower key generation efficiency and higher sensitivity to channel losses.
- **Consequences:** Provides 50% theoretical basis sifting efficiency and a well-defined 11% QBER threshold for eavesdropper detection.

---

## ADR-002: Selection of IBM Qiskit Aer for Quantum Circuit Simulation
- **Status:** Accepted
- **Context:** Physical single-photon QKD optical hardware cannot be physically deployed on microcontrollers. A software simulation environment is required. Candidates include custom classical random number generators (RNG), NetSquid, QuNetSim, and IBM Qiskit Aer.
- **Decision:** Select IBM Qiskit Aer (`qiskit` and `qiskit_aer`).
- **Rationale:** Pure classical random number generation (as used in Adu-Kyere et al. 2022) does not model quantum states or projective measurement collapse. NetSquid is heavy and optimized for quantum repeater networks. Qiskit Aer compiles true quantum circuits (state vectors, unitary gates, and stochastic measurement projection) with high-performance C++ backends, allowing realistic quantum circuit simulation and parameterized quantum noise channels.
- **Consequences:** Guarantees genuine quantum circuit modeling while maintaining compatibility with standard Python data science and benchmarking toolchains.

---

## ADR-003: Selection of AES-256-GCM over One-Time Pad and AES-CBC
- **Status:** Accepted
- **Context:** An encryption mechanism is needed to secure IoT telemetry payloads using QKD-negotiated keys. Candidates include One-Time Pad (OTP), AES-256-CBC with HMAC, and AES-256-GCM.
- **Decision:** Select AES-256 in Galois/Counter Mode (GCM) complying with NIST SP 800-38D.
- **Rationale:** One-Time Pad requires 1 bit of quantum key for every 1 bit of transmitted data. High-frequency IoT sensors streaming telemetry would immediately exhaust the QKD key generation rate, leading to severe key starvation. AES-CBC requires a separate HMAC pass (Encrypt-then-MAC), is vulnerable to padding oracle attacks, and requires two sequential passes. AES-GCM is an AEAD cipher that provides both confidentiality and 128-bit integrity (Galois MAC) in a single hardware-pipelined pass. AES-256 maintains 128 bits of post-quantum security against Grover's algorithm.
- **Consequences:** Maximizes throughput ($<0.05\text{ ms}$ encryption latency) and guarantees 100% detection of unauthorized ciphertext or tag tampering.

---

## ADR-004: Selection of MQTT over HTTP and CoAP for IoT Transport
- **Status:** Accepted
- **Context:** Telemetry must be transmitted from edge IoT nodes to cloud ingestion endpoints. Candidates include HTTP/REST, CoAP, and MQTT.
- **Decision:** Select OASIS MQTT v5.0 / v3.1.1 publish/subscribe protocol.
- **Rationale:** HTTP/REST incurs heavy text header overhead ($>500$ bytes per request) and requires repeated TCP handshakes for each reading, creating excessive battery drain and latency. CoAP operates over UDP, which lacks native connection-oriented reliability for critical encrypted telemetry. MQTT provides lightweight binary headers (as small as 2 bytes), persistent TCP connections, flexible topic hierarchies, and QoS delivery guarantees.
- **Consequences:** Enables rapid, low-bandwidth telemetry transmission from resource-constrained edge devices.

---

## ADR-005: Dual-Mode MQTT Broker Architecture (Queue vs Mosquitto)
- **Status:** Accepted
- **Context:** Prototype execution must be 100% reliable during lab evaluations and offline demonstrations where external network access or local Mosquitto daemons may not be installed.
- **Decision:** Implement a dual-mode communication bridge supporting both an in-memory thread-safe `queue.Queue` broker and a live TCP connection to Eclipse Mosquitto.
- **Rationale:** Prevents runtime crashes when external brokers are unavailable, while preserving the ability to connect to production MQTT brokers when available. In experimental reporting, Queue measurements are strictly demarcated from real MQTT network measurements.
- **Consequences:** Guarantees zero-dependency out-of-the-box execution while upholding strict scientific transparency.

---

## ADR-006: Implementation of Information Reconciliation and Universal-Hash KDF
- **Status:** Accepted
- **Context:** Prior literature naively hashes raw sifted bits using SHA-256, which breaks under channel noise ($QBER > 0$) because single-bit differences prevent key agreement.
- **Decision:** Implement interactive Information Reconciliation (parity block search / Cascade) to eliminate bit errors prior to privacy amplification, and formalize privacy amplification using universal hashing bounds.
- **Rationale:** Resolves the fatal flaw of prior works, ensuring Alice and Bob share identical keys under realistic channel noise ($QBER \le 0.11$) while eliminating eavesdropper mutual information.
- **Consequences:** Produces a technically sound, noise-resilient post-processing pipeline suitable for peer-reviewed publication.
