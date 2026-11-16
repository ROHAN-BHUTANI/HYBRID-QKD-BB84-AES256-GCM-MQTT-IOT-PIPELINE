# Formal Research Questions & Experimental Hypotheses

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Research Questions Formulation

### Research Question 1 (RQ1: Quantum Key Agreement & Channel Dynamics)
> **RQ1:** How effectively can simulated BB84 key agreement establish secret key material under varying quantum channel noise levels and eavesdropping interception densities, and what is the resulting key distillation efficiency after information reconciliation?

### Research Question 2 (RQ2: Cryptographic Binding & Tamper Detection)
> **RQ2:** What is the computational and memory overhead of binding reconciled BB84 keys into AES-256-GCM for IoT telemetry payloads, and does Galois/Counter Mode provide 100% detection of active Man-in-the-Middle ciphertext and nonce tampering?

### Research Question 3 (RQ3: Transport & End-to-End Latency Trade-offs)
> **RQ3:** What is the end-to-end packet transmission and decryption latency when transmitting QKD-secured telemetry over real network-based MQTT compared to a local in-memory queue fallback?

### Research Question 4 (RQ4: Comparative Baseline Evaluation)
> **RQ4:** How does the proposed hybrid QKD-AES architecture compare against conventional pre-shared key AES-GCM and post-quantum key encapsulation mechanisms (ML-KEM-512 / Kyber) in terms of key negotiation latency, packet transmission overhead, and security guarantees?

---

## 2. Experimental Hypotheses & Variables

### Hypothesis 1 ($H_1$ for RQ1):
- **Null Hypothesis ($H_{1,0}$):** The introduction of an intercept-resend attack with interception probability $p_{\text{eve}} = 1.0$ does not produce a statistically significant increase in QBER over a noiseless baseline ($p_{\text{eve}} = 0.0$).
- **Alternative Hypothesis ($H_{1,1}$):** Full intercept-resend eavesdropping ($p_{\text{eve}} = 1.0$) induces an expected QBER of approximately $25.0\% \pm 3.0\%$ on matching basis measurements, statistically exceeding the $11.0\%$ abort threshold ($p < 0.001$), reliably triggering key abortion.
- **Variables:**
  - *Independent:* Number of initial qubits $N \in \{128, 256, 512, 1024, 2048\}$, Eve interception probability $p_{\text{eve}} \in [0.0, 1.0]$, depolarizing noise parameter $\lambda \in [0.0, 0.15]$.
  - *Dependent:* Sifted key length, sample error rate (QBER), post-reconciliation key yield, protocol execution time.
  - *Controlled:* Aer simulator backend seed, single-photon basis definitions ($Z$ and $X$), parameter estimation fraction ($25\%$).

### Hypothesis 2 ($H_2$ for RQ2):
- **Null Hypothesis ($H_{2,0}$):** Man-in-the-Middle bit-flipping modifications in transmitted AES-256-GCM ciphertexts are not detected with 100% accuracy by the cloud receiver.
- **Alternative Hypothesis ($H_{2,1}$):** Any single-bit or multi-bit modification in the ciphertext, nonce, or authentication tag results in a cryptographic `InvalidTag` exception with 100% detection rate across all trials, with encryption and decryption execution latency remaining below $0.5\text{ ms}$ for standard IoT payloads ($\le 1\text{ KB}$).
- **Variables:**
  - *Independent:* Payload size (bytes: 32, 64, 128, 256, 512, 1024, 2048), injected tampering bit-flips.
  - *Dependent:* Encryption time (ms), decryption time (ms), tamper detection rate (%).
  - *Controlled:* 256-bit AES key size, 96-bit nonce length, 128-bit authentication tag length.

### Hypothesis 3 ($H_3$ for RQ3):
- **Null Hypothesis ($H_{3,0}$):** End-to-end telemetry delivery latency over real MQTT (Mosquitto) does not differ significantly from local in-memory Queue execution.
- **Alternative Hypothesis ($H_{3,1}$):** Real MQTT communication incurs a measurable network TCP stack overhead ($\approx 1.5 - 5.0\text{ ms}$), but maintains sub-10ms delivery latency, while in-memory Queue execution delivers sub-millisecond latency ($< 0.5\text{ ms}$).
- **Variables:**
  - *Independent:* Transport mode (`MQTT_BROKER_MODE` vs `QUEUE_MODE`), QoS level (0 vs 1).
  - *Dependent:* End-to-end latency (nanoseconds converted to ms), packet loss rate.
  - *Controlled:* Payload schema, client hardware platform, database persistence logic.

### Hypothesis 4 ($H_4$ for RQ4):
- **Null Hypothesis ($H_{4,0}$):** Proposed QKD-derived key transmission exhibits higher per-message communication bandwidth overhead than post-quantum key encapsulation mechanisms.
- **Alternative Hypothesis ($H_{4,1}$):** Because QKD keys are established out-of-band or at session initialization, per-message payload overhead in the proposed architecture is only 28 bytes (12-byte nonce + 16-byte GMAC tag), whereas ML-KEM-512 incurs an encapsulated ciphertext transmission overhead of 768 bytes per key exchange transaction.
- **Variables:**
  - *Independent:* Key establishment mechanism (Pre-shared key vs BB84 QKD vs ML-KEM-512).
  - *Dependent:* Handshake latency, per-message byte overhead, computational cycle cost.
  - *Controlled:* Symmetric cipher used for payload encryption (AES-256-GCM).
