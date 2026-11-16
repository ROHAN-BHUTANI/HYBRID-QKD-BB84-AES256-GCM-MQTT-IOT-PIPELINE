# Software Requirements Specification (SRS)

**Standard:** IEEE Std 830-1998 Format  
**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Document Version:** 1.0.0  
**Project Team ID:** MP2026CSE205  
**Date:** November 2026

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the Hybrid BB84 QKD + AES-256-GCM Secure Cloud IoT Communication Platform. It defines functional, performance, security, and interface specifications for researchers, developers, and academic evaluators.

### 1.2 Scope
The software system comprises:
1. A quantum circuit simulation module running IBM Qiskit Aer to model BB84 key agreement, quantum noise, and eavesdropping attacks.
2. A classical post-processing subsystem performing basis sifting, QBER parameter estimation, interactive information reconciliation (error correction), and universal-hash privacy amplification.
3. An IoT sensor client providing synthetic BME280 telemetry and NIST SP 800-38D AES-256-GCM authenticated encryption.
4. An MQTT communication bridge providing dual-mode message transport (real Mosquitto broker client and in-memory queue fallback).
5. A cloud receiver subsystem enforcing authentication tag verification, anti-replay sequence checking, and SQLite persistence.
6. A real-time Flask web dashboard and an automated empirical benchmarking suite.

### 1.3 Definitions, Acronyms, and Abbreviations
- **AEAD:** Authenticated Encryption with Associated Data
- **AES-GCM:** Advanced Encryption Standard in Galois/Counter Mode
- **BB84:** Bennett-Brassard 1984 Quantum Key Distribution Protocol
- **CSPRNG:** Cryptographically Secure Pseudorandom Number Generator
- **KDF:** Key Derivation Function
- **MitM:** Man-in-the-Middle
- **MQTT:** Message Queuing Telemetry Transport
- **NIST:** National Institute of Standards and Technology
- **QBER:** Quantum Bit Error Rate
- **QKD:** Quantum Key Distribution
- **QoS:** Quality of Service

---

## 2. Overall Description

### 2.1 Product Perspective
The product is a self-contained, modular Python platform integrating quantum computing simulation with modern edge-to-cloud IoT security pipelines:

```
[Qiskit Aer BB84] ──► [Post-Processing (Reconcile + Hash)] ──► [256-Bit Secret Key]
                                                                        │
┌───────────────────────────────────────────────────────────────────────┘
▼
[IoT Edge Sensor] ──► [AES-256-GCM Encrypt] ──► [MQTT Bridge] ──► [Cloud Receiver] ──► [SQLite DB]
                                                                                            │
                                                                                            ▼
                                                                                   [Flask Dashboard]
```

### 2.2 Operating Environment
- **Operating Systems:** Windows 10/11 (AMD64), Linux (Ubuntu 22.04+), macOS (Apple Silicon / Intel).
- **Python Version:** Python 3.10 to 3.12.
- **Dependencies:** `qiskit>=1.0.0`, `qiskit-aer>=0.15.0`, `cryptography>=42.0.0`, `paho-mqtt>=2.0.0`, `flask>=3.0.0`, `psutil>=5.9.0`.

---

## 3. Specific System Requirements

### 3.1 External Interface Requirements
- **User Interface (UI):** Web-based responsive dashboard accessible via HTTP on port 5000.
- **Hardware Interfaces:** None (pure software simulation).
- **Software Interfaces:**
  - IBM Qiskit Aer C++ simulator engine via Python bindings.
  - SQLite3 relational database engine (`iot_cloud.db`).
  - Eclipse Mosquitto MQTT broker via standard TCP port 1883.
- **Communications Interfaces:** TCP/IP socket communication supporting MQTT v3.1.1 and v5.0 protocols.

### 3.2 Functional Requirements

#### Section 3.2.1: Quantum Simulation Engine (Module A)
- **REQ-A1:** The system shall initialize $N$ single-qubit quantum circuits, where $N \in \{128, 256, 512, 1024, 2048\}$.
- **REQ-A2:** For each qubit $i$, Alice shall generate a random bit $b_i \in \{0, 1\}$ and random basis $a_i \in \{0, 1\}$ (0: Rectilinear $Z$, 1: Diagonal $X$).
- **REQ-A3:** Alice shall apply a Pauli-$X$ gate if $b_i = 1$, and a Hadamard gate $H$ if $a_i = 1$.
- **REQ-A4:** The system shall support an optional Eve intercept-resend attack with configurable probability $p_{\text{eve}} \in [0.0, 1.0]$. When intercepting, Eve shall measure in a random basis and re-prepare the collapsed state.
- **REQ-A5:** Bob shall generate an independent random basis $a'_i \in \{0, 1\}$ and measure each qubit. If $a'_i = 1$, Bob shall apply an $H$ gate prior to computational basis measurement.
- **REQ-A6:** The basis sifting procedure shall retain indices where $a_i = a'_i$.
- **REQ-A7:** The parameter estimation procedure shall select a random 25% sample of sifted bits, compute $\text{QBER}$, and compare against threshold $\tau = 0.11$. If $\text{QBER} > \tau$, the session shall abort and emit an alert.
- **REQ-A8:** The system shall implement Information Reconciliation (parity-based error correction) to correct discrepancies on the remaining sifted bits when $\text{QBER} \le \tau$.
- **REQ-A9:** The system shall implement Universal-Hash Privacy Amplification to compress the reconciled bits into an exact 256-bit symmetric key.

#### Section 3.2.2: Cryptographic Subsystem (Module B)
- **REQ-B1:** The system shall implement AES-256 in Galois/Counter Mode (GCM) adhering strictly to NIST SP 800-38D.
- **REQ-B2:** The system shall generate a fresh, cryptographically secure 96-bit nonce (`os.urandom(12)`) for every encryption operation.
- **REQ-B3:** The system shall compute a 128-bit authentication tag over the ciphertext and optional associated data.
- **REQ-B4:** The receiver shall verify the authentication tag prior to releasing any decrypted plaintext. Any mismatch shall raise `InvalidTag`.
- **REQ-B5:** The system shall serialize the cryptographic envelope into JSON with Base64-encoded binary fields (`nonce`, `ciphertext`, `tag`).

#### Section 3.2.3: IoT Telemetry & Messaging Subsystem (Module C & D)
- **REQ-C1:** The IoT client shall generate synthetic BME280 sensor readings containing timestamp, reading ID, temperature, humidity, and barometric pressure.
- **REQ-C2:** The system shall provide an in-memory queue broker (`QUEUE_MODE`) for offline execution.
- **REQ-C3:** The system shall provide a Paho-MQTT client (`MQTT_BROKER_MODE`) connecting to an external Mosquitto broker on TCP 1883.
- **REQ-C4:** All telemetry payloads shall be published to the topic `iot/secure/data`.

#### Section 3.2.4: Cloud Receiver & Persistence Subsystem (Module E & F)
- **REQ-D1:** The cloud receiver shall subscribe to `iot/secure/data` and ingest incoming envelopes.
- **REQ-D2:** The cloud receiver shall enforce anti-replay protection by verifying that `reading_id` is strictly monotonically increasing per device.
- **REQ-D3:** The cloud receiver shall compute end-to-end latency in nanoseconds using high-resolution monotonic clocks.
- **REQ-D4:** Authenticated readings, QKD diagnostic sessions, and security alerts shall be persisted in SQLite tables `sensor_readings`, `qkd_sessions`, and `security_alerts`.

---

## 4. Verification & Traceability Matrix Reference
Every functional requirement specified herein maps bijectively to the Requirements Traceability Matrix (`docs/RTM.md`) and the test suite (`tests/`).
