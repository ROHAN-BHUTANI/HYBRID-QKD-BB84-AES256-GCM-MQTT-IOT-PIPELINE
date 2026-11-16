# PROJECT CURRENT-STATE AUDIT

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date of Audit:** 16 November 2026  
**Auditing Team:** Multidisciplinary Research & Systems Engineering Review Team  
**Scope:** Complete repository inspection (`qkd/`, `iot_client/`, `broker/`, `cloud_receiver/`, `dashboard/`, `benchmark/`, `database/`, root scripts, and documentation).

---

## 1. Executive Audit Summary

An exhaustive technical inspection of the repository was conducted to establish a baseline prior to research expansion and publication preparation.

### Status Overview
- **Working Foundation:** The repository possesses a functional prototype pipeline (`run_pipeline.py`) capable of running a simulated BB84 key agreement in Qiskit Aer, encrypting telemetry using AES-256-GCM via the Python `cryptography` library, passing envelopes through an in-memory queue or Paho-MQTT, and verifying authentication tags in a cloud receiver backed by SQLite and a Flask dashboard.
- **Critical Research & Cryptographic Gaps Identified:**
  1. **Absence of Information Reconciliation (Error Correction):** The current BB84 implementation computes QBER on a 25% sample, checks if $QBER \le 0.11$, and directly hashes the remaining sifted bits using SHA-256. Under any nonzero channel noise ($QBER > 0$), Alice's and Bob's remaining bits differ. Hashing differing bitstrings causes an avalanche mismatch, resulting in 100% decryption failures on the receiver.
  2. **Absence of Channel Noise Modeling:** Qiskit Aer is executed as an idealized noiseless circuit unless Eve intercepts. Real quantum channels exhibit depolarizing, bit-flip, and phase-flip errors.
  3. **Oversimplified Privacy Amplification:** SHA-256 is used as a direct digest of remaining bits. This does not follow universal-hashing privacy amplification (e.g., Toeplitz hashing) and fails to account for finite-key bounds.
  4. **Missing Replay Attack Prevention:** The cloud receiver validates the 128-bit authentication tag, but does not maintain a stateful monotonic sequence window, leaving it vulnerable to replayed packets.
  5. **Missing Formal Automated Test Suite:** The workspace contains manual runners (`run_pipeline.py`, `benchmark/runner.py`), but lacks a formal `tests/` directory with unit, integration, and security test suites.
  6. **Missing Systems Engineering Documentation:** No formal PRD, SRS (IEEE 830), threat model (STRIDE/Dolev-Yao), DFDs, ADRs, or Requirements Traceability Matrix (RTM) exist in the repository.
  7. **Missing Publication Artifacts:** Systematic literature review artifacts, PRISMA flow logs, and LaTeX manuscripts are not yet structured into dedicated directories.

---

## 2. Component-by-Component Feature Classification

Every feature in the repository is audited and classified under one of the six mandated categories:
- `IMPLEMENTED AND VERIFIED`
- `IMPLEMENTED BUT NOT VERIFIED`
- `PARTIALLY IMPLEMENTED`
- `SIMULATED OR SIMPLIFIED`
- `MISSING`
- `INCORRECT OR UNSAFE`

| Component | Sub-Feature | Implementation File | Classification | Detailed Technical Evaluation |
| :--- | :--- | :--- | :--- | :--- |
| **QKD Engine** | Z-Basis Preparation ($\|0\rangle, \|1\rangle$) | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Uses Qiskit Pauli-$X$ gate on initialized $|0\rangle$ qubits. Verified functional. |
| **QKD Engine** | X-Basis Preparation ($\|+\rangle, \|-\rangle$) | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Applies Hadamard ($H$) gate after optional $X$ gate. Verified functional. |
| **QKD Engine** | Bob Basis Measurement | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Bob applies $H$ gate before measurement when diagonal basis is chosen. Correct projection. |
| **QKD Engine** | Basis Sifting | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Classical basis comparison retains indices where bases match ($\approx 50\%$ efficiency). |
| **QKD Engine** | Parameter Estimation & QBER | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Randomly samples 25% of sifted bits, calculates error rate against threshold ($0.11$). |
| **QKD Engine** | Eve Intercept-Resend Attack | `qkd/bb84.py` | **IMPLEMENTED AND VERIFIED** | Eve measures in random basis and re-prepares states; induces $\approx 25\%$ error on matching bases. |
| **QKD Engine** | Quantum Channel Noise Models | `qkd/bb84.py` | **MISSING** | No `qiskit_aer.noise` models (depolarizing, thermal relaxation, bit-flip). Execution is noiseless when Eve is off. |
| **QKD Engine** | Information Reconciliation | `qkd/bb84.py` | **MISSING** | No error correction (Cascade, Winnow, LDPC). Fails to reconcile non-identical sifted bits under noise. |
| **QKD Engine** | Privacy Amplification | `qkd/bb84.py` | **INCORRECT OR UNSAFE** | Hashes raw remaining bits with SHA-256. Cryptographically unsound: SHA-256 cannot create 256 bits of secret entropy from a small or noisy key, and fails under nonzero QBER. |
| **QKD Engine** | Authenticated Classical Channel | `qkd/bb84.py` | **SIMULATED OR SIMPLIFIED** | Basis exchange and parameter estimation occur in Python memory without classical authentication (Wegman-Carter). |
| **Cryptography** | AES-256-GCM Encryption | `iot_client/crypto_utils.py` | **IMPLEMENTED AND VERIFIED** | NIST SP 800-38D compliant using `cryptography.hazmat.primitives.ciphers.aead.AESGCM`. |
| **Cryptography** | Unique 96-bit Nonce Policy | `iot_client/crypto_utils.py` | **IMPLEMENTED AND VERIFIED** | Generates fresh 12-byte cryptographically secure pseudorandom nonces via `os.urandom(12)`. |
| **Cryptography** | Tag Verification / Tamper Detection | `iot_client/crypto_utils.py` | **IMPLEMENTED AND VERIFIED** | 128-bit authentication tag verification. Catches `InvalidTag` on altered ciphertext or tag. |
| **Cryptography** | Replay Attack Protection | `cloud_receiver/receiver.py` | **MISSING** | Packets contain `timestamp_ns`, but receiver does not enforce monotonic sequence numbers or freshness windows. |
| **Cryptography** | Key Management & Rotation | `dashboard/app.py` | **PARTIALLY IMPLEMENTED** | Single session key stored in memory; no formal key derivation hierarchy, expiration, or ratcheting. |
| **IoT Sensor** | Telemetry Simulation | `iot_client/sensor_client.py` | **IMPLEMENTED AND VERIFIED** | Generates realistic BME280 temperature, humidity, and barometric pressure readings. |
| **IoT Sensor** | JSON Payload Serialization | `iot_client/sensor_client.py` | **IMPLEMENTED AND VERIFIED** | Serializes payload with timestamp, reading ID, device ID, and telemetry fields. |
| **Communication** | In-Memory Queue Broker | `broker/broker_bridge.py` | **IMPLEMENTED AND VERIFIED** | Thread-safe queue broker providing 100% offline reproducible execution. |
| **Communication** | Real MQTT Client (Paho) | `broker/broker_bridge.py` | **IMPLEMENTED AND VERIFIED** | Supports live Mosquitto / EMQX TCP connections; properly handles connection lifecycle. |
| **Cloud Receiver** | Telemetry Ingestion & Decryption | `cloud_receiver/receiver.py` | **IMPLEMENTED AND VERIFIED** | Subscribes to MQTT data topic, decrypts payload, measures nanosecond latency. |
| **Cloud Receiver** | Security Incident Logging | `cloud_receiver/receiver.py` | **IMPLEMENTED AND VERIFIED** | Logs integrity violations to database upon `InvalidTag`. |
| **Storage** | SQLite Database Schema | `cloud_receiver/database.py` | **IMPLEMENTED AND VERIFIED** | Stores readings, QKD sessions, and alerts. Auto-initializes tables. |
| **Storage** | Database Constraints & Indexes | `cloud_receiver/database.py` | **PARTIALLY IMPLEMENTED** | Basic primary keys exist; lacks foreign keys, compound indexes, and uniqueness constraints. |
| **Dashboard** | Web Interface (Flask) | `dashboard/app.py` | **IMPLEMENTED AND VERIFIED** | Serves Golden & Black UI, REST endpoints for telemetry, alerts, and live action triggers. |
| **Dashboard** | Live Metrics & Controls | `dashboard/templates/index.html`| **IMPLEMENTED AND VERIFIED** | Real-time polling, interactive buttons for QKD (No Eve / With Eve) and data (Valid / Tampered). |
| **Dashboard** | True Quantum Circuit Visualizer | `dashboard/templates/index.html`| **SIMULATED OR SIMPLIFIED** | Renders static CSS/HTML schematic; does not render live Qiskit circuit DAGs or Bloch spheres. |
| **Benchmarking** | Performance Profiling Suite | `benchmark/runner.py` | **IMPLEMENTED AND VERIFIED** | Measures QKD time vs qubits, AES latency vs payload, E2E latency, and CPU/RAM via `psutil`. |
| **Testing** | Automated Test Suite | `tests/` | **MISSING** | No dedicated unit, integration, or security test suite exists in the workspace. |
| **Documentation**| Systems Engineering Specs | `docs/` | **MISSING** | Missing PRD, SRS (IEEE 830), Threat Model, DFDs, ADRs, and Traceability Matrix. |
| **Research** | Literature Review & Gap Analysis | `research/` | **PARTIALLY IMPLEMENTED** | Literature corpus verified in Phase II logs; formal structured research directory not yet assembled. |
| **Paper** | Publication Manuscript | `paper/` | **MISSING** | LaTeX manuscript, BibTeX database, and submission readiness report not yet drafted. |

---

## 3. Detailed Technical Deficiencies and Risks

### 3.1 Cryptographic & Quantum Deficiencies
1. **The Noise Mismatch Problem:**  
   In `qkd/bb84.py`, the remaining sifted bits after parameter estimation are directly hashed:
   $$\text{Key} = \text{SHA-256}(\text{Alice\_remaining\_bits})$$
   $$\text{Bob\_Key} = \text{SHA-256}(\text{Bob\_remaining\_bits})$$
   If any physical channel noise is introduced (e.g., $QBER = 3\%$), Alice and Bob will disagree on $\approx 3\%$ of their sifted bits. Because SHA-256 is a cryptographic hash exhibiting the avalanche effect, a single bit difference causes the two 256-bit outputs to diverge completely. Bob will be unable to decrypt any telemetry transmitted by Alice.
   *Remediation Required:* Implement an Information Reconciliation protocol (e.g., block parity / simplified Cascade error correction) to correct discrepancies on the classical channel before privacy amplification.

2. **Unsound Privacy Amplification Assumption:**  
   Applying SHA-256 to an arbitrary bitstring does not perform privacy amplification in the information-theoretic sense. If the sifted key has length $m < 256$ or contains limited min-entropy after eavesdropping, SHA-256 cannot create 256 bits of secret entropy out of nothing.
   *Remediation Required:* Formalize privacy amplification using universal hashing principles (Toeplitz matrix or finite-key length bound $l \le n[1 - h(\text{QBER})] - \text{leak}_{\text{EC}} - \Delta$) and explicitly document the finite-key assumptions.

3. **Absence of Channel Noise in Simulation:**  
   `BB84Simulator` only simulates errors if `enable_eve=True`. If Eve is off, $QBER$ is identically $0.00\%$. Real quantum communication suffers from optical loss, detector dark counts, and fiber birefringence.
   *Remediation Required:* Integrate configurable depolarizing and phase-flip error channels using `qiskit_aer.noise`.

### 3.2 System & Security Deficiencies
1. **Replay Vulnerability:**  
   `iot_client/sensor_client.py` sends an incrementing `reading_id` and timestamp, but `cloud_receiver/receiver.py` does not store or check the latest seen sequence number per device. An attacker intercepting an authentic ciphertext envelope could replay it repeatedly to flood the cloud database.
   *Remediation Required:* Implement stateful anti-replay verification tracking monotonic sequence numbers within a sliding window.

2. **Transport Distinction:**  
   `broker/broker_bridge.py` contains both `LocalSimulatedClient` and `LiveMQTTClient`. Experiments must explicitly distinguish when the system is operating over in-memory queues versus real TCP-based MQTT to prevent misleading latency claims in the research paper.

---

## 4. Preservation & Migration Strategy

Existing working functionality must be strictly preserved:
- Existing prototypes (`run_pipeline.py`, `dashboard/app.py`, `benchmark/runner.py`) will remain fully operational.
- New research-grade components will be modularized cleanly according to Part 11 of the execution prompt:
  - `qkd/` will be extended with dedicated modules (`alice.py`, `bob.py`, `eve.py`, `channel.py`, `sifting.py`, `qber.py`, `postprocessing/reconciliation.py`, `postprocessing/privacy_amplification.py`).
  - `security/` will provide hardened AES-256-GCM with replay detection.
  - `docs/` will host all systems engineering specifications.
  - `tests/` will provide full unit, integration, and security test coverage.
  - `research/` will house the complete systematic literature review and gap analysis.
  - `paper/` will contain the publication-quality LaTeX manuscript and submission readiness report.

---
*Audit completed by Antigravity Autonomous Research & Systems Engineering Team.*
