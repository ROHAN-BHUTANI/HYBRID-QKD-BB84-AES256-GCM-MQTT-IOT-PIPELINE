# Related Work Comparative Analysis

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Feature-by-Feature Comparison Matrix

The table below contrasts our proposed research prototype against closely related works across five core dimensions:
- **D1: Quantum Simulation Fidelity:** True quantum circuits (superposition, gates, projection measurement collapse) vs classical random number simulations.
- **D2: Noise & Eavesdropping Modeling:** Configurable channel noise (depolarizing/phase flip) and Eve intercept-resend modeling.
- **D3: Post-Processing & Reconciliation:** Explicit Information Reconciliation (error correction) and mathematically grounded Privacy Amplification.
- **D4: Cryptographic Binding & AEAD:** Authenticated Encryption with Associated Data (AES-256-GCM), unique nonces, and anti-replay protection.
- **D5: IoT Transport & Empirical Testbed:** Actual MQTT pub/sub protocol, cloud receiver, database persistence, and empirical microsecond latency profiling.

| Study | Platform / Tool | Quantum Circuit Simulation? | Channel Noise Modeled? | Eve Intercept Simulated? | Info Reconciliation (Error Correction)? | Privacy Amplification (Universal Hash)? | AEAD Cipher (AES-GCM)? | Transport Protocol | Empirical Latency Measured? | Full Testbed Open Sourced? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Adu-Kyere et al. (2022)** [B1] | Python 3 (custom script) | ❌ No (Classical RNG) | ❌ No | ⚠️ Abstracted | ⚠️ Basic parity | ❌ None | ❌ None (Key only) | None (Local script) | ❌ No | ⚠️ Partial |
| **Coopmans et al. (2021)** [B2] | NetSquid (C++/Python) | ✅ Yes (Discrete-event) | ✅ Yes (Fiber/Mem) | ⚠️ Network layer | ⚠️ Abstracted | ⚠️ Abstracted | ❌ None | Custom Network Stack | ✅ Yes (Network) | ✅ Yes |
| **Fiorini et al. (2024)** [B4] | IBM Qiskit Aer | ✅ Yes (Aer circuits) | ✅ Yes (Depolarizing)| ✅ Yes (p_eve sweep) | ❌ None | ❌ None | ❌ None | None (Standalone sim) | ❌ No | ⚠️ Partial |
| **Fiorini et al. (2026)** [C2] | Qiskit + Python stats | ✅ Yes (Aer circuits) | ✅ Yes (Depolarizing)| ✅ Yes (p_eve sweep) | ❌ None | ❌ None | ❌ None | None (Standalone sim) | ❌ No | ❌ No |
| **Das et al. (2026)** [B6] | IBM Qiskit | ✅ Yes (Aer circuits) | ✅ Yes (Gate/Phase) | ❌ No | ❌ None | ❌ None | ❌ None | None (Standalone sim) | ❌ No | ❌ No |
| **Farooq et al. (2024)** [D3] | Simulation / Analytical | ⚠️ Unclear in abstract | ❌ Unstated | ⚠️ Unstated | ❌ Unstated | ❌ Unstated | ⚠️ AES (Mode unstated)| MQTT (Mosquitto) | ⚠️ Qualitative | ❌ No |
| **Rehman & Alharbi (2025)** [D1] | Python Smart City framework | ⚠️ High-level model | ❌ No | ⚠️ Basic QBER | ❌ None | ⚠️ Simple hash | ✅ Yes (AES-GCM) | HTTP / REST | ✅ Yes (20.3 ms) | ❌ No |
| **Chaturvedi et al. (2025)** [C3] | Qiskit + ECC Python | ✅ Yes (Multi-node) | ✅ Yes (Noise sweep) | ⚠️ Threat resistance | ❌ None | ⚠️ ECC derivation | ❌ No (ECC only) | Simulated Network | ✅ Yes (Network) | ❌ No |
| **Manimozhi & Mugelan (2025)**[C4] | Qiskit + ECC + AES | ✅ Yes (BB84 circuit) | ❌ No | ❌ No | ❌ None | ⚠️ ECC point mapping | ⚠️ AES-CBC/ECB | TCP Sockets | ⚠️ Partial | ❌ No |
| **Kaganurmath et al. (2025)** [E1] | Raspberry Pi testbed | ❌ No (Classical DH) | ❌ N/A | ❌ N/A | ❌ N/A | ❌ N/A | ⚠️ Custom + HMAC | MQTT (v3.1.1/v5.0) | ✅ Yes (0.40 s) | ❌ No |
| **Shehzadi et al. (2025)** [F2] | ARM Cortex-M4 | ❌ No (ML-KEM PQC) | ❌ N/A | ❌ N/A | ❌ N/A | ❌ N/A | ✅ Ascon-128a AEAD | SPI / Serial | ✅ Yes (CPU cycles)| ⚠️ Partial |
| **Proposed Research Prototype** | **IBM Qiskit Aer + Python + Paho** | **✅ Yes (4-state BB84)** | **✅ Yes (Depolarizing)**| **✅ Yes (Configurable)**| **✅ Yes (Parity/Cascade)**| **✅ Yes (Universal Hash Bound)**| **✅ Yes (AES-256-GCM)**| **MQTT (Mosquitto) + Queue**| **✅ Yes (<1 ms E2E)** | **✅ Yes (Full Code)** |

---

## 2. In-Depth Comparative Observations

### 2.1 The "Quantum Simulation vs. Application Cryptography" Schism
Prior literature is sharply divided into two disjoint silos:
1. **Isolated Quantum Physics Simulations:** Works such as Fiorini et al. (2024, 2026), Das et al. (2026), and Hubballi et al. (2026) delve deeply into Qiskit circuit modeling, noise models, and threshold calculations. However, they stop entirely once the sifted bits or raw QBER are calculated. None of these works connect their derived keys to an application-layer cryptographic protocol, an IoT message broker, or a database.
2. **Abstracted IoT Security Frameworks:** Works such as Farooq et al. (2024), Rehman & Alharbi (2025), and Biswas et al. (2024) propose quantum-enhanced IoT architectures. However, they treat QKD as an abstract "black box" oracle that supplies keys on demand, without modeling quantum circuit gates, basis reconciliation, channel noise, or information reconciliation.

### 2.2 The Information Reconciliation Blind Spot
Most existing hybrid prototypes that claim to derive symmetric keys from BB84 (e.g., Manimozhi & Mugelan 2025, Rehman & Alharbi 2025) commit a fatal mathematical error: they execute basis sifting, check QBER, and directly hash remaining bits with SHA-256. As proven in our audit, in any realistic noisy channel ($QBER > 0$), Alice's and Bob's sifted bits differ. Without an explicit **Information Reconciliation** step, the derived keys diverge, causing 100% of decryption attempts to fail. Our work explicitly implements and benchmarks this crucial bridge.

### 2.3 The Transport Reality Gap
Many papers evaluate IoT communication over HTTP/REST (e.g., Rehman & Alharbi 2025) or custom TCP sockets (Manimozhi & Mugelan 2025), which are poorly suited for constrained edge telemetry. While Farooq et al. (2024) and Kaganurmath et al. (2025) target MQTT, they either lack open-source code and empirical sub-millisecond benchmarking (Farooq) or rely on quantum-vulnerable classical Diffie-Hellman handshakes (Kaganurmath).
