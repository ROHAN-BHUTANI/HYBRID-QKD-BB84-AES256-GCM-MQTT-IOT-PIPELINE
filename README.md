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
                         Privacy Amplification (SHA-256 KDF)
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
| **Module A** | **BB84 QKD Engine** | `qkd/bb84.py` | Simulates single-photon quantum circuits in **IBM Qiskit Aer**, implements basis reconciliation sifting, 25% parameter estimation, 11% QBER threshold enforcement, and **SHA-256 privacy amplification** to produce a 256-bit AES key. |
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
*Created for B.Tech Major Project Phase 2 Prototype Submission (November 2026).*

