# Formal Threat Model & Security Analysis

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Methodology:** STRIDE Classification + Dolev-Yao Classical Model + Quantum Adversary Postulates  
**Date:** November 2026

---

## 1. Adversary Capabilities & Threat Boundaries

### 1.1 The Quantum Eavesdropper (Eve)
- **Model:** Intercept-Resend Attack on the quantum channel between Alice and Bob.
- **Assumed Capabilities:**
  - Can intercept any fraction $p_{\text{eve}} \in [0.0, 1.0]$ of transmitted single qubits.
  - Can measure intercepted qubits in arbitrary bases ($Z$ or $X$).
  - Can prepare new single qubits in the measured state and re-transmit them to Bob.
- **Physical Limitations (Out of Scope for Eve):**
  - Cannot clone arbitrary unknown quantum states (No-Cloning Theorem).
  - Cannot measure in non-orthogonal conjugate bases without collapsing the state-vector (Heisenberg Uncertainty Principle).
  - Cannot defeat the classical authenticated basis announcement channel (assumed authenticated).

### 1.2 The Classical Network Adversary (Mallory / MitM)
- **Model:** Full Dolev-Yao Network Adversary on the classical MQTT transport network.
- **Capabilities:**
  - Can eavesdrop on all classical MQTT packets between IoT sensors, MQTT brokers, and cloud receivers.
  - Can modify arbitrary bits in the ciphertext, nonce, or authentication tag in transit.
  - Can capture authentic envelopes and replay them at a later time (Replay Attacks).
  - Can drop, delay, or inject forged MQTT messages.

---

## 2. STRIDE Threat Analysis Matrix

| STRIDE Category | Threat Description | Attack Vector | System Vulnerability | Applied Countermeasure & Residual Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates an IoT sensor to publish forged environmental telemetry. | Classical MQTT injection on topic `iot/secure/data`. | Plaintext MQTT accepts arbitrary publishers if broker allows anonymous connect. | **Countermeasure:** AES-256-GCM authentication tag. Attacker without the quantum-derived key cannot forge a valid 128-bit Galois MAC tag. Residual risk: Compromise of sensor device memory. |
| **Tampering** | Man-in-the-Middle flips bits in ciphertext to falsify telemetry (e.g., modifying temperature from 22°C to 80°C). | Packet modification in transit across network router or proxy. | Unauthenticated stream ciphers or CBC without HMAC permit bit-flipping. | **Countermeasure:** Galois/Counter Mode computes tag over $\text{GF}(2^{128})$. Modifying any ciphertext or nonce bit causes `InvalidTag` and immediate rejection. Residual risk: None ($2^{-128}$ collision probability). |
| **Repudiation** | Malicious node denies having transmitted a false alert or anomalous reading. | Disputing historical sensor transmissions. | Missing audit trail or mutable records. | **Countermeasure:** Sequential message IDs, nanosecond UTC timestamps, and append-only SQLite persistence with foreign-keyed session records. |
| **Information Disclosure** | Eavesdropper reads sensitive environmental telemetry in transit. | Passive packet capture (Wireshark / tcpdump) on MQTT TCP connection. | Unencrypted MQTT payload. | **Countermeasure:** Confidentiality guaranteed by AES-256-GCM using 256-bit key established via BB84. Quantum security margin: 128 bits against Grover's algorithm. |
| **Denial of Service** | Active quantum eavesdropper continuously measures qubits to prevent key establishment. | Constant quantum channel interception ($p_{\text{eve}} = 1.0$). | Protocol must abort when $\text{QBER} > 11\%$. | **Analysis:** This is an inherent property of quantum physics: Eve can cause a DoS by persistently measuring, but cannot compromise confidentiality. The system logs an intrusion alert and preserves fallback pre-shared keys. |
| **Elevation of Privilege** | Attacker replays captured authentic envelopes to force cloud to re-record historical data. | Capturing valid MQTT packets and publishing repeatedly. | Cloud receiver decrypting successfully without tracking sequence freshness. | **Countermeasure:** RFC 4303 / RFC 6347 64-packet sliding window bitmap enforcement. Cloud receiver rejects any message with duplicate sequence bit in window or $reading\_id \le M - 64$, while accommodating out-of-order wireless jitter. |

---

## 3. Quantum-Specific Threat Evaluation

### 3.1 Shor's Algorithm Vulnerability
- Traditional IoT key exchanges (RSA, ECDH) are completely broken by Shor's algorithm running on a quantum computer ($O(\log^3 N)$ complexity).
- **Our Defense:** The proposed architecture uses **no asymmetric mathematics**. Key negotiation is performed via quantum state measurements (BB84), and telemetry encryption uses AES-256-GCM. Shor's algorithm has zero application against BB84 or symmetric block ciphers.

### 3.2 Grover's Algorithm Vulnerability
- Grover's algorithm provides a quadratic speedup for searching symmetric keys, reducing the effective security of an $n$-bit key to $n/2$ bits.
- **Our Defense:** By enforcing a strict 256-bit key size derived via universal-hash privacy amplification, the post-quantum effective security remains:
  $$\text{Effective Quantum Security} = \frac{256}{2} = 128 \text{ bits}$$
  128 bits of symmetric security requires $2^{128} \approx 3.4 \times 10^{38}$ quantum operations, which is physically secure against any conceivable quantum computer for billions of years.

### 3.3 Nonce Reuse Vulnerability in AES-GCM
- If a 96-bit nonce is ever reused with the same AES-256 key, an attacker observing two ciphertexts $C_1, C_2$ with nonces $N_1 = N_2$ can XOR the ciphertexts to recover the XOR of the plaintexts ($P_1 \oplus P_2$), and can solve for the GHASH authentication key $H = \text{AES}_K(0^{128})$, completely destroying the integrity of all subsequent messages.
- **Our Defense:** Nonces are generated as 96-bit cryptographically secure pseudorandom values (`os.urandom(12)`). Under the Birthday Bound, the probability of a collision across $2^{32}$ packets is less than $2^{-32}$. Furthermore, in strict compliance with NIST SP 800-38D Section 8.2.2, IoT sensor clients maintain a session invocation counter that triggers an automated QKD re-keying request once $100,000$ packets are transmitted under the same symmetric key.
