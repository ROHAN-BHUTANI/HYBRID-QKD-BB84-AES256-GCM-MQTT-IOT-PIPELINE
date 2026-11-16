# Requirements Traceability Matrix (RTM)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Traceability Matrix Table

| Req ID | Requirement Summary | PRD Ref | Implementation File | Test Case | Experiment Ref | Paper Section | Status |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **REQ-A1** | Qiskit BB84 circuit initialization ($N \in [128, 2048]$) | FR-01 | `qkd/bb84.py`, `qkd/alice.py` | UT-Q01, UT-Q02 | EXP-1 | Section IV-A | Verified |
| **REQ-A2** | Random bit and basis generation ($Z$ and $X$) | FR-01 | `qkd/alice.py`, `qkd/bob.py` | UT-Q01, UT-Q03 | EXP-1 | Section IV-A | Verified |
| **REQ-A3** | State preparation ($X$ and $H$ unitary gates) | FR-01 | `qkd/alice.py` | UT-Q01, UT-Q03 | EXP-1 | Section IV-A | Verified |
| **REQ-A4** | Eve intercept-resend attack with prob $p_{\text{eve}}$ | FR-02 | `qkd/eve.py`, `qkd/bb84.py` | UT-Q07 | EXP-2 | Section IV-B | Verified |
| **REQ-A5** | Bob basis rotation and projective measurement | FR-01 | `qkd/bob.py` | UT-Q04 | EXP-1 | Section IV-A | Verified |
| **REQ-A6** | Classical basis sifting ($\approx 50\%$ yield) | FR-03 | `qkd/sifting.py` | UT-Q05 | EXP-1 | Section IV-C | Verified |
| **REQ-A7** | Parameter estimation sampling & 11% QBER abort | FR-04 | `qkd/qber.py` | UT-Q06, UT-Q07 | EXP-1, EXP-2 | Section IV-C | Verified |
| **REQ-A8** | Information reconciliation (parity error correction) | FR-05 | `qkd/postprocessing/reconciliation.py` | UT-Q08 | EXP-3 | Section IV-D | Verified |
| **REQ-A9** | Universal-hash privacy amplification to 256-bit key | FR-06 | `qkd/postprocessing/privacy_amplification.py`| UT-Q09 | EXP-1 | Section IV-E | Verified |
| **REQ-B1** | NIST SP 800-38D AES-256-GCM authenticated cipher | FR-07 | `iot_client/crypto_utils.py` | UT-C01 | EXP-4 | Section V-A | Verified |
| **REQ-B2** | 96-bit unique CSPRNG nonce generation | FR-07 | `iot_client/crypto_utils.py` | UT-C02 | EXP-4 | Section V-B | Verified |
| **REQ-B3** | 128-bit Galois MAC authentication tag verification | FR-07 | `iot_client/crypto_utils.py` | ST-01, ST-02 | EXP-5 | Section V-A | Verified |
| **REQ-B4** | Instant rejection and alert logging on `InvalidTag` | FR-07 | `cloud_receiver/receiver.py` | ST-01, ST-02 | EXP-5 | Section V-D | Verified |
| **REQ-B5** | Base64 JSON transport envelope packaging | FR-07 | `iot_client/crypto_utils.py` | UT-C01 | EXP-4 | Section V-C | Verified |
| **REQ-C1** | Synthetic BME280 sensor telemetry generation | FR-08 | `iot_client/sensor_client.py` | IT-02 | EXP-6 | Section V-C | Verified |
| **REQ-C2** | In-memory Queue fallback transport (`QUEUE_MODE`) | FR-09 | `broker/broker_bridge.py` | IT-02 | EXP-6 | Section VI-B | Verified |
| **REQ-C3** | Live Paho-MQTT transport (`MQTT_BROKER_MODE`) | FR-09 | `broker/broker_bridge.py` | IT-02 | EXP-6 | Section VI-B | Verified |
| **REQ-C4** | Telemetry publication to `iot/secure/data` | FR-09 | `iot_client/sensor_client.py` | IT-02 | EXP-6 | Section V-C | Verified |
| **REQ-D1** | Cloud receiver topic subscription & ingestion | FR-10 | `cloud_receiver/receiver.py` | IT-02 | EXP-6 | Section V-D | Verified |
| **REQ-D2** | Stateful anti-replay monotonic sequence enforcement | FR-08 | `cloud_receiver/receiver.py` | ST-04, ST-05 | EXP-5 | Section V-D | Verified |
| **REQ-D3** | Nanosecond-resolution end-to-end latency measurement | FR-12 | `cloud_receiver/receiver.py` | EXP-6 | EXP-6 | Section VII-E | Verified |
| **REQ-D4** | Relational persistence in SQLite (`iot_cloud.db`) | FR-10 | `cloud_receiver/database.py` | IT-02 | EXP-6 | Section V-D | Verified |
| **REQ-E1** | Golden-Black Flask monitoring dashboard | FR-11 | `dashboard/app.py`, `index.html` | SY-01 | EXP-7 | Section VI-C | Verified |
| **REQ-F1** | Automated empirical benchmarking suite | FR-12 | `benchmark/runner.py`, `experiments/`| SY-01 | EXP-1..7 | Section VII | Verified |

---
*All 24 system requirements are fully mapped and traced across specifications, implementation files, automated tests, empirical experiments, and research paper manuscript sections.*
