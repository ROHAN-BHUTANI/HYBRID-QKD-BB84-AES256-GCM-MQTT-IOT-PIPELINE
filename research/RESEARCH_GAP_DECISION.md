# Formal Research Gap Decision & Contribution Defense

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date of Decision:** November 2026  
**Status:** **FROZEN & APPROVED**

---

## 1. Decision Statement

Following systematic review of 32 peer-reviewed papers and full-text extraction of priority works, the research team formally **rejects** all naive claims of "first-ever hybrid integration" or "novel physical QKD." 

Instead, the project adopts the following **defensible, scientifically valid research contribution**:

### The Chosen Research Contribution:
> **"Design, Implementation, and Empirical Benchmarking of an End-to-End Quantum-Safe IoT Telemetry Architecture Connecting Qiskit Aer BB84 with Reconciled AES-256-GCM over MQTT."**

Specifically, the project establishes:
1. **A Complete Post-Processing Pipeline:** Bridging quantum circuit simulation in IBM Qiskit Aer to classical cryptography by implementing **Information Reconciliation** (correcting channel noise discrepancies) and **Universal-Hash Privacy Amplification** (deriving a shared 256-bit symmetric key with documented finite-key bounds).
2. **A Hardened Cryptographic IoT Transport:** Binding quantum-derived keys into NIST SP 800-38D AES-256-GCM with strictly unique 96-bit nonces, 128-bit Galois MAC verification, and monotonic anti-replay sequence windows over the MQTT protocol.
3. **An Empirical Comparative Testbed:** Delivering reproducible, sub-millisecond benchmarking that breaks down latency, throughput, and CPU/memory footprint across the entire pipeline, evaluating real MQTT versus in-memory transport and contrasting with pre-shared and post-quantum (ML-KEM/Kyber) baselines.
4. **An Open-Source Research & Educational Platform:** Providing a complete, modular, verified Python codebase with automated unit, integration, and security tests, backed by an interactive Golden-Black telemetry and attack dashboard.

---

## 2. Explicit Boundaries & Non-Claims

To ensure complete academic defensibility, the research paper and project documentation will strictly uphold the following boundaries:
1. **Simulation Fidelity:** We explicitly state that quantum key distribution is simulated using **IBM Qiskit Aer** circuit models. We make zero claims of physical photons, lasers, or optical fibers.
2. **Finite-Key Secrecy:** We explicitly state the mathematical assumptions regarding finite-block lengths ($N \in [128, 2048]$). We do not claim unconditional information-theoretic security across infinite keys, but document the practical bounds of privacy amplification under finite sampling.
3. **Transport Demarcation:** In all experimental tables and graphs, measurements taken using the local in-memory Queue fallback are strictly separated and labeled as `QUEUE_MODE`, while measurements over the network broker are labeled as `MQTT_BROKER_MODE`.
4. **Classical Channel Authentication:** We document that the classical public channel for basis announcement is assumed to be authenticated (e.g., via Wegman-Carter polynomial MACs or pre-shared keys), as is standard in BB84 literature to prevent trivial classical impersonation.

---

## 3. Approval Sign-Off

- **Lead Systems Architect & Applied Cryptographer:** Antigravity Autonomous Research Team
- **Approval Date:** 16 November 2026
- **Status:** APPROVED. Proceed to Requirements Specification and Technical Implementation.
