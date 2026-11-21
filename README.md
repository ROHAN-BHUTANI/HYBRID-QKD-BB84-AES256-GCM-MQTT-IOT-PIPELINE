# Hybrid BB84 Quantum Key Distribution and AES-256-GCM for Secure Cloud-Based IoT Communication over MQTT

**Major Project (2026–2027)**  
**Project Team ID:** MP2026CSE205  
**Institution:** Department of Computer Science & Engineering, Graphic Era Deemed to be University, Dehradun  
**Supervisor:** Prof. (Dr.) Mohammad Wazid  
**Team Members:** Rohan Bhutani (GE-232023571), Anirudh Panwar (GE-232024218), Shruti Sharma (GE-232023636), Ananya Sharma (GE-232023243)

---

## 1. Project Architecture Overview

This project implements a complete, working software prototype combining quantum-safe key distribution with lightweight authenticated symmetric encryption for resource-constrained IoT telemetry:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         END-TO-END PIPELINE ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────────────┘

   [Alice (Qiskit)] ────── Qubit Transmission (|0>, |1>, |+>, |->) ──────► [Bob (Qiskit)]
          │                                                                     │
          │                   Optional: Eve Intercept-Resend                    │
          │                   Attack Simulation (QBER ~25%)                     │
          │                                                                     │
          └─────────────► Classical Sifting & QBER Verification ◄───────────────┘
                                        │
                               (QBER <= 11% Cutoff)
                                        │
                         Privacy Amplification (Toeplitz GF(2))
                                        │
                           Shared 256-bit AES Secret Key
                                        │
         ┌──────────────────────────────┴──────────────────────────────┐
         ▼                                                             ▼
┌──────────────────────────────────┐                       ┌──────────────────────────────────┐
│   Module B: IoT Sensor Client    │                       │    Module C: Cloud Receiver      │
│  - Synthetic Environmental Data  │                       │  - MQTT Telemetry Subscriber     │
│  - AES-256-GCM Encrypt (96b IV)  │                       │  - AES-256-GCM Auth Tag Verify   │
│  - Paho-MQTT Publisher           │                       │  - Decrypt Payload               │
└────────────────┬─────────────────┘                       └─────────────────▲────────────────┘
                 │                                                           │
                 │              ┌─────────────────────────────┐              │
                 └─────────────►│   Module D: MQTT Broker     ├──────────────┘
                                │  (Simulated / Mosquitto)    │
                                └──────────────┬──────────────┘
                                               │
                                               ▼
                                ┌─────────────────────────────┐
                                │   SQLite3 (iot_cloud.db)    │
                                └──────────────┬──────────────┘
                                               │
                                               ▼
                                ┌─────────────────────────────┐
                                │ Module E: Flask Web UI      │
                                │  (Live Sensor Charts & KPIs)│
                                └─────────────────────────────┘
```

---

## 2. Modules Implementation Summary

| Module | Component | File Path | Core Functionality |
| :--- | :--- | :--- | :--- |
| **Module A** | **BB84 QKD Engine** | `qkd/bb84.py` | Simulates single-photon quantum circuits in **IBM Qiskit Aer**, implements basis reconciliation sifting, 25% parameter estimation, 11% QBER threshold enforcement, and **2-universal Toeplitz hash privacy amplification** (asymptotic Leftover Hash Lemma engineering formulation) to produce a 256-bit AES key. |
| **Module B** | **IoT Sensor Client** | `iot_client/sensor_client.py` | Generates realistic environmental telemetry (temperature, humidity, pressure), performs **AES-256-GCM authenticated encryption** with a fresh 96-bit nonce, and publishes to MQTT. |
| **Module B (Crypto)** | **Cryptographic Utils** | `iot_client/crypto_utils.py` | NIST SP 800-38D compliant AES-256-GCM encryption/decryption, Base64 payload packaging, and tamper detection via tag validation. |
| **Module C** | **Cloud Receiver** | `cloud_receiver/receiver.py` | Subscribes to MQTT topics, verifies 128-bit authentication tags, decrypts payloads, and triggers alerts upon detecting Man-in-the-Middle (MitM) alterations. |
| **Module C (DB)** | **Persistent Storage** | `cloud_receiver/database.py` | SQLite3 database (`database/iot_cloud.db`) storing sensor telemetry, QKD diagnostic audit sessions, and security alerts. |
| **Module D** | **MQTT Broker Bridge** | `broker/broker_bridge.py` | Dual-mode broker: thread-safe in-memory queue (runs 100% offline out-of-the-box) and live Paho-MQTT client (connects to Mosquitto / EMQX). |
| **Module E** | **Flask Dashboard** | `dashboard/app.py` | Real-time web monitoring interface with live metric cards, sensor telemetry table, security alert logs, and interactive buttons to trigger BB84 or packet tampering. |
| **Module F** | **Benchmarking Suite** | `benchmark/runner.py` | Empirical performance profiling across QKD execution times, QBER vs Eve interception probabilities, AES latency, end-to-end latency, and CPU/RAM overhead via `psutil`. |

---

## 3. Quick Start Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the End-to-End Pipeline Demo
Executes the entire workflow (QKD key agreement -> IoT encryption -> MQTT publish -> Cloud decryption -> MitM tamper detection -> Eve detection):
```bash
python run_pipeline.py
```

### Step 3: Launch the Interactive Web Dashboard
```bash
python dashboard/app.py
```
Open your browser to: **`http://127.0.0.1:5000`**
From the dashboard, you can:
- View live decrypted sensor readings (Temperature, Humidity, Pressure).
- Click **"Run BB84 (No Eve)"** to establish a new 256-bit quantum key ($QBER \approx 0\%$).
- Click **"Run BB84 (With Eve)"** to simulate Eve's intercept-resend attack and observe the key abort ($QBER \approx 25\% > 11\%$).
- Click **"Send Valid Reading"** to transmit an authenticated sensor packet over MQTT.
- Click **"Send Tampered Packet"** to simulate MitM ciphertext modification and watch the cloud receiver catch the integrity violation!

### Step 4: Run Automated Benchmarks
Generates research datasets in the `benchmarks/` directory:
```bash
python benchmark/runner.py
```
Output CSV files produced:
- `benchmarks/qkd_benchmark.csv`: QKD execution time & QBER across 128, 256, 512, and 1024 qubits.
- `benchmarks/encryption_benchmark.csv`: AES-256-GCM encryption latency vs payload size.
- `benchmarks/decryption_benchmark.csv`: AES-256-GCM decryption latency vs payload size.
- `benchmarks/e2e_latency.csv`: End-to-end packet transmission and decryption latency.
- `benchmarks/resource_usage.csv`: CPU usage (%) and memory footprint (MB) profiled via `psutil`.

---

## 4. Key Experimental Results

1. **Quantum Security (BB84 Protocol):**
   - **Without Eve:** $QBER = 0.00\%$ ($\le 11\%$ threshold). Shared 256-bit AES key is established in $\approx 30$ to $60$ ms.
   - **With Eve Active:** $QBER \approx 21.0\%$ to $29.4\%$ ($> 11\%$ threshold). Protocol automatically aborts key establishment, proving information-theoretic intrusion detection.
2. **Cryptographic Throughput (AES-256-GCM):**
   - Encryption Latency: $\approx 0.01$ to $0.15$ ms per packet.
   - Decryption Latency: $\approx 0.01$ to $0.05$ ms per packet.
   - Tamper Detection: $100\%$ detection rate of payload or tag alteration via GCM Galois MAC verification.
3. **End-to-End Latency:**
   - Average packet delivery, verification, and database persistence latency: $< 1.0$ ms.

---

## 5. Autonomous Key Lifecycle & Rekeying (TSK-01)

The pipeline implements an autonomous finite state machine (`qkd.key_lifecycle.KeyLifecycleManager`) enforcing NIST SP 800-38D invocation bounds:

* **State Machine:** `UNINITIALIZED` -> `KEY_ESTABLISHED` -> `ACTIVE` -> `REKEY_REQUIRED` -> `REKEYING` -> `ACTIVE_NEW_KEY` (or `KEY_EXPIRED` / `SECURITY_ABORT`).
* **Pre-Encryption Guard:** Every frame call to `publish_reading()` verifies key validity. Encryption under exhausted or retired keys is strictly prohibited (`KeyExpirationError`).
* **In-Flight Grace Period:** Receiver maintains an inbound rollover window for in-flight packets across broker queues during key rotation.
* **Audit Logging:** Every transition is recorded in SQLite `key_lifecycle_events` and sensor readings are stamped with `key_id`.

To run the autonomous re-keying demonstration:
```bash
python -c "import run_pipeline; run_pipeline.run_rekey_demo(max_key_invocations=3, total_frames=8)"
```


---

## 6. Scientific Boundaries and Methodological Distinctions

In adherence to scientific rigor and academic reproducibility standards, this project explicitly establishes the following architectural boundaries (see [`docs/SCIENTIFIC_LIMITATIONS.md`](docs/SCIENTIFIC_LIMITATIONS.md)):

1. **Quantum Circuit Simulation vs. Physical Optics:**
   - The quantum layer is executed entirely in software using IBM Qiskit Aer (`qiskit-aer==0.18.2`).
   - It simulates ideal single-qubit state preparation and projective measurements with uniform depolarizing noise.
   - It does **not** model physical fiber attenuation (0.2 dB/km in SMF-28), detector dark counts, detector recovery dead time, Poissonian weak coherent pulse distributions, or multi-photon emissions / PNS attacks.

2. **Simulated Key Delivery vs. Authenticated Network Key Delivery:**
   - Key delivery to the cloud receiver operates via an in-process Python callback (`on_key_rotated`), matching the broker simulation environment.
   - It does **not** implement standardized physical QKD key delivery protocols (e.g., ETSI GS QKD 014 / 004 KMS interfaces) over authenticated network links.

3. **Engineering Key Length vs. Certified Composable Entropy:**
   - Privacy amplification applies an **asymptotic Leftover Hash Lemma engineering formulation**:
     $$\ell_{\text{engineering}} = \max\left(0, \lfloor m(1 - h_2(\text{QBER})) - \text{leak}_{\text{EC}} - 64 \rfloor\right)$$
   - It does **not** implement a certified composable finite-key security proof (Tomamichel et al., 2012). Sifting pools matching $\mathcal{Z}$ and $\mathcal{X}$ bases, and parameter estimation measures bit error rate ($e_{\text{bit}}$). Bounding conjugate phase error ($e_{\text{phase}}$) requires channel symmetry assumptions that do not hold against general quantum eavesdropping.

4. **QBER Statistical Sampling vs. Eavesdropper Detection:**
   - Measuring $\text{QBER} > 11\%$ triggers an automatic abort under simulated intercept-resend attacks (which induce $\text{QBER} \approx 25\%$).
   - In physical QKD, sophisticated coherent attacks, detector blinding, or photon number splitting (PNS) cannot be detected by bit error rate alone without decoy states and segregated phase-error estimation.

5. **AES-GCM Authentication vs. QKD Information-Theoretic Security:**
   - AES-256-GCM provides **computational** security: 128-bit integrity protection via Galois MAC authentication tags and 128-bit post-quantum security margin under Grover's search algorithm.
   - The information-theoretic security guarantees of QKD apply strictly to the quantum key exchange layer under classical authentication assumptions; subsequent IoT transport security is symmetric and computational.

6. **In-Process Queue vs. Real Network MQTT:**
   - The default `SimulatedBroker` uses an in-process, thread-safe Python `queue.Queue` ($t_{\text{e2e}} < 1.0\text{ ms}$).
   - It bypasses OS socket buffers, network serialization, TCP 3-way handshakes, and packet jitter. Real network Mosquitto testing introduces socket I/O ($18.4 \pm 4.1\text{ ms}$ over loopback).

---
*Created for B.Tech Major Project Phase 2 Prototype Submission (November 2026).*

