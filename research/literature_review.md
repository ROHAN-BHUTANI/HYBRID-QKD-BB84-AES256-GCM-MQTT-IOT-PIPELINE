# Systematic Literature Review: Quantum Key Distribution, Post-Quantum Cryptography, and Secure IoT Architectures

**Author:** Multidisciplinary Research Team (Project ID: MP2026CSE205)  
**Affiliation:** Department of Computer Science & Engineering, Graphic Era Deemed to be University, Dehradun  
**Target Submission:** Comprehensive Research Literature Survey  
**Date:** November 2026

---

## 1. Introduction & The Quantum Threat to the Internet of Things

The rapid proliferation of the Internet of Things (IoT) has led to billions of interconnected smart sensors deployed across industrial control systems, smart energy grids, healthcare telemetry, and autonomous urban infrastructure [Granjal et al., 2015; Sharma & Bhushan, 2025]. These edge nodes continuously collect and transmit sensitive telemetry to cloud aggregation endpoints over untrusted public networks. 

Historically, end-to-end security in distributed systems has relied on asymmetric Public Key Cryptography (PKC)—principally the RSA cryptosystem, Diffie-Hellman (DH) key exchange, and Elliptic Curve Cryptography (ECC) [Granjal et al., 2015]. The security of these algorithms rests upon the assumed computational intractability of specific mathematical problems: prime integer factorization and discrete logarithms over finite fields or elliptic curve groups.

However, the advent of quantum computing fundamentally undermines this foundational assumption. In 1994, Peter Shor formulated a polynomial-time quantum algorithm capable of solving prime factorization and discrete logarithms with logarithmic depth on a fault-tolerant quantum computer [Shor, 1994]. Consequently, when scaled to cryptographically relevant quantum computers (CRQCs), Shor's algorithm will completely break RSA-2048, ECDH, and ECDSA within minutes [Chawla & Mehra, 2023; Mallick et al., 2026].

Compounding this existential threat is the **"Harvest Now, Decrypt Later" (HNDL)** adversary model. Malicious nation-states and criminal syndicates are actively intercepting and archiving encrypted IoT communications today. Even if a functional quantum computer is decades away, telemetry captured today will be retroactively decrypted the moment quantum computers mature, compromising long-lived infrastructure data, medical histories, and industrial operational secrets [Adere et al., 2026].

In response, cybersecurity researchers have pursued two distinct pathways:
1. **Mathematical Post-Quantum Cryptography (PQC):** Algorithmic replacements based on hard mathematical problems that resist quantum search, such as module lattices (e.g., CRYSTALS-Kyber / ML-KEM) [Bos et al., 2018; NIST FIPS 203].
2. **Physical Quantum Key Distribution (QKD):** Information-theoretically secure key establishment based on the fundamental laws of quantum physics [Bennett & Brassard, 1984].

This review provides a systematic, critical analysis of 32 peer-reviewed studies across seven core themes, examining the feasibility, post-processing mechanics, and empirical performance of combining BB84 QKD with symmetric authenticated encryption for constrained IoT communication over the Message Queuing Telemetry Transport (MQTT) protocol.

---

## 2. Foundations of BB84 Quantum Key Distribution

Proposed by Charles Bennett and Gilles Brassard in 1984, the BB84 protocol represents the foundational protocol of quantum cryptography [Bennett & Brassard, 1984]. BB84 enables two legitimate parties—Alice (the transmitter) and Bob (the receiver)—to establish a shared, secret random bitstring over an insecure quantum channel, with the guarantee that any eavesdropper (Eve) attempting to gain information will be physically detected.

### 2.1 The Physical Foundations of BB84 Security
Unlike classical cryptography, which depends on unproven mathematical hardness assumptions, BB84 derives its security from the fundamental principles of quantum mechanics:
1. **Heisenberg Uncertainty Principle:** Non-commuting quantum observables cannot be measured simultaneously with arbitrary precision. In BB84, information is encoded into non-orthogonal quantum states across two conjugate bases: the Rectilinear ($Z$) basis and the Diagonal ($X$) basis. Any attempt by an eavesdropper to measure a qubit in the incorrect basis irrevocably disturbs the quantum state.
2. **The No-Cloning Theorem:** Formulated by Wootters and Zurek (1982), the no-cloning theorem states that an unknown arbitrary quantum state cannot be cloned identically. Consequently, Eve cannot intercept a flying photon, duplicate it, store the clone in a quantum memory, and forward the original intact to Bob.

### 2.2 Quantum State Preparation & Basis Transformation
In the four-state BB84 protocol, Alice selects a random binary bit $b \in \{0, 1\}$ and a random basis $a \in \{Z, X\}$, preparing the quantum state $|\psi_{b,a}\rangle$:

$$\begin{aligned}
Z\text{-basis } (0): \quad |0\rangle &= \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \quad |1\rangle = X|0\rangle = \begin{bmatrix} 0 \\ 1 \end{bmatrix} \\
X\text{-basis } (1): \quad |+\rangle &= H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad |-\rangle = H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}
\end{aligned}$$

Here, $X$ denotes the Pauli-X bit-flip operator, and $H$ denotes the single-qubit Hadamard gate:

$$H = \frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$$

Bob measures each incoming qubit in a randomly chosen basis $a' \in \{Z, X\}$. If Bob measures in the $Z$ basis, he performs a standard projective measurement $M_Z = \{|0\rangle\langle 0|, |1\rangle\langle 1|\}$. If Bob chooses the $X$ basis, he applies a Hadamard rotation $H$ immediately prior to projective measurement, mapping $|+\rangle \to |0\rangle$ and $|-\rangle \to |1\rangle$ [Büyükdede, 2026].

---

## 3. Quantum Circuit Simulation Frameworks

Because physical QKD hardware (pulsed laser diodes, beam splitters, and superconducting nanowire single-photon detectors) costs between \$50,000 and \$150,000 and cannot be embedded on microcontrollers [Yang et al., 2025], software-based quantum circuit simulation has become an essential methodology for designing, validating, and benchmarking QKD-integrated network systems.

### 3.1 Qiskit and Qiskit Aer
IBM Qiskit is the predominant open-source quantum software development framework [Das et al., 2026; Fiorini et al., 2024; Hubballi et al., 2026]. The `Qiskit Aer` module provides high-performance C++ simulator backends modeling realistic quantum circuit execution. In Qiskit Aer, quantum state evolution can be simulated as pure state-vectors or as density matrices subject to parameterized quantum noise channels.
- **Büyükdede (2026)** implemented a virtualized BB84 simulator in Qiskit Aer, demonstrating that circuit-level state preparation, measurement, and classical register extraction accurately model single-photon exchanges.
- **Fiorini et al. (2024, 2026)** and **Das et al. (2026)** utilized Qiskit Aer to model eavesdropping and noise, confirming that quantum measurement collapse behaves in exact concordance with theoretical projection postulates.

### 3.2 Network-Layer Simulators: NetSquid and QuNetSim
Beyond circuit-level simulators, discrete-event quantum network simulators have been developed to model multi-hop quantum networks:
- **NetSquid [Coopmans et al., 2021]:** Developed by QuTech at TU Delft, NetSquid is a discrete-event simulator tracking time-dependent physical processes such as quantum memory decoherence, fiber propagation delays, and atomic clock synchronization across hundreds of nodes.
- **QuNetSim [DiAdamo et al., 2021]:** An open-source Python framework modeling quantum network stacks using classical IPC sockets.
- **NS-3 QKD Module [Mehić et al., 2017]:** Integrated a QKD simulation module into the NS-3 discrete-event simulator to evaluate how classical applications consume keys from a centralized Key Management Server (KMS).

While NetSquid and NS-3 excel at modeling multi-repeater wide-area backbones, IBM Qiskit Aer is significantly better suited for edge-to-cloud device prototyping because it directly compiles and executes unitary gate circuits and custom noise channels with minimal simulation overhead.

---

## 4. Quantum Channel Noise, Eavesdropping, and QBER Thresholds

In any transmission over a quantum channel, errors can arise from two distinct sources: environmental channel noise and active eavesdropping.

### 4.1 Intercept-Resend Eavesdropping Dynamics
In an intercept-resend attack, Eve intercepts Alice's photon, chooses a measurement basis $a_E \in \{Z, X\}$ at random, measures the state, and transmits a newly prepared photon in that measured state to Bob [Adu-Kyere et al., 2022; Khan et al., 2026].
- If Alice and Bob chose matching bases ($a = a'$):
  - With probability $1/2$, Eve chooses the same basis ($a_E = a$). Her measurement does not alter the state, and Bob receives the correct bit.
  - With probability $1/2$, Eve chooses the conjugate basis ($a_E \neq a$). Her measurement collapses the state into an orthogonal basis. When Bob subsequently measures in the original basis, he obtains a random result: with probability $1/2$ he gets the correct bit, and with probability $1/2$ he gets an erroneous bit.
- Therefore, for an eavesdropper intercepting a fraction $p_{\text{eve}}$ of transmitted qubits, the expected Quantum Bit Error Rate (QBER) on sifted bits is:

$$\text{E}[\text{QBER}] = p_{\text{eve}} \times \left(\frac{1}{2} \times 0 + \frac{1}{2} \times \frac{1}{2}\right) = \frac{p_{\text{eve}}}{4}$$

For a full intercept-resend attack ($p_{\text{eve}} = 1.0$), Eve introduces a deterministic expected error rate of **$25.0\%$** into the sifted key [Adu-Kyere et al., 2022; Fiorini et al., 2024].

### 4.2 Quantum Channel Noise Modeling
In physical fiber or atmospheric channels, errors occur naturally due to fiber birefringence, thermal fluctuations, and dark counts. In Qiskit Aer, these are modeled using stochastic quantum noise channels [Fiorini et al., 2024; Das et al., 2026]:
1. **Depolarizing Channel:** With probability $\lambda$, the qubit is replaced by a completely mixed state:
   $$\mathcal{E}_{\text{depol}}(\rho) = (1 - \lambda)\rho + \frac{\lambda}{3}(X\rho X + Y\rho Y + Z\rho Z)$$
2. **Bit-Flip / Phase-Flip Channel:** With probability $p_x$ or $p_z$, Pauli $X$ or $Z$ operators are applied.

### 4.3 The 11% QBER Abort Threshold & Shor-Preskill Security Proof
A foundational milestone in QKD literature is the Shor-Preskill security proof (2000), which established that BB84 is unconditionally secure against arbitrary collective and coherent quantum attacks provided the asymptotic QBER satisfies [Tomamichel et al., 2012; Tupkary et al., 2026]:

$$\text{QBER} \le 11.0\%$$

If $\text{QBER} \le 0.11$, the Shannon mutual information between Alice and Bob exceeds the information accessible to Eve ($I(A; B) > I(A; E)$). Under this condition, classical post-processing can distill a smaller, fully secret key. Conversely, if $\text{QBER} > 0.11$, Eve's potential information exceeds the distillable secret key capacity, and the protocol must abort [Fiorini et al., 2026].

---

## 5. QKD Post-Processing: Sifting, Reconciliation, and Privacy Amplification

A major flaw in early academic literature is the conflation of raw QKD simulation with secure key generation. Quantum circuit execution alone does not produce a cryptographic key. A rigorous classical post-processing pipeline is required.

```
Raw Quantum Transmission (N Qubits)
               │
               ▼
   [1. Classical Basis Sifting] ────────► Discard non-matching bases (~50% yield)
               │
               ▼
 [2. Parameter Estimation (QBER)] ──────► Sample 25% of sifted bits; check QBER <= 11%
               │
               ▼
 [3. Information Reconciliation] ───────► Parity / Cascade error correction over classical channel
               │
               ▼
 [4. Privacy Amplification (PA)] ───────► 2-Universal Hashing / Leftover Hash Lemma
               │
               ▼
  Shared 256-bit Secret Key Material
```

### 5.1 Classical Basis Sifting
In the sifting phase, Alice and Bob exchange their basis choices over an authenticated classical channel. They retain only the indices where their chosen bases coincided ($a_i = a'_i$). For randomly distributed bases, the expected sifted key yield is:

$$\text{E}[|K_{\text{sift}}|] = \frac{N}{2}$$

### 5.2 Parameter Estimation
Alice and Bob randomly select a fraction $\alpha$ of their sifted bits (typically $\alpha = 0.25$) and publicly disclose them over the classical channel to estimate QBER:

$$\widehat{\text{QBER}} = \frac{1}{|S_{\text{sample}}|} \sum_{j \in S_{\text{sample}}} |K_{\text{Alice}}[j] \oplus K_{\text{Bob}}[j]|$$

These sampled bits are subsequently discarded to prevent eavesdropping leakage [Fiorini et al., 2024].

### 5.3 Information Reconciliation (Error Correction)
When physical or simulated channel noise is present ($0 < \text{QBER} \le 0.11$), Alice and Bob hold remaining sifted bitstrings that disagree at specific bit positions. Direct cryptographic hashing of these bitstrings results in complete key divergence due to the avalanche effect.
- **The Cascade Protocol [Brassard & Salvail, 1994]:** An interactive reconciliation algorithm where keys are segmented into blocks whose size is chosen according to the estimated QBER. Alice and Bob exchange parity bits for each block; upon detecting a parity mismatch, they execute a binary search (bisection) to locate and correct the erroneous bit.
- **Low-Density Parity-Check (LDPC) Codes [Kiktenko et al., 2017]:** Non-interactive reconciliation where Bob corrects errors using syndrome matrices, reducing classical round-trips.

### 5.4 Privacy Amplification & Finite-Key Bounds
Even after error correction, Eve may possess partial information about the reconciled string from her eavesdropping attempts and from the parity bits disclosed during reconciliation [Bennett et al., 1995].
- **Privacy Amplification:** Compresses the reconciled bitstring of length $m$ into a shorter key of length $\ell$ using a family of 2-universal hash functions (e.g., random Toeplitz matrices) [Bennett et al., 1995; Tomamichel et al., 2012].
- **Finite-Key Secrecy Bound:** In practical implementations with finite block size $N$, Tomamichel et al. (2012) proved that the extractable secure key length $\ell$ is bounded by:

$$\ell \le m \left[ 1 - h(\text{QBER}) \right] - \text{leak}_{\text{EC}} - \Delta_{\text{finite}}$$

where $h(p) = -p \log_2(p) - (1-p) \log_2(1-p)$ is the binary entropy function, $\text{leak}_{\text{EC}}$ is the classical leakage during reconciliation, and $\Delta_{\text{finite}}$ accounts for statistical security parameters.

---

## 6. Authenticated Symmetric Cryptography (AES-256-GCM) for Constrained IoT

While One-Time Pad (OTP) offers theoretical perfection, it consumes 1 bit of key for every 1 bit of plaintext, causing catastrophic key starvation on high-frequency IoT sensors [Biswas et al., 2024; Granjal et al., 2015]. Consequently, hybrid architectures bind QKD keys into symmetric block ciphers.

### 6.1 AES-256 in the Quantum Era
Against classical adversaries, AES-256 provides an astronomical security level of $2^{256}$ operations. Against quantum computers, Grover's search algorithm provides a quadratic speedup for unstructured database searches, effectively reducing symmetric key search complexity from $O(2^k)$ to $O(2^{k/2})$ [Chawla & Mehra, 2023]. Therefore, an AES-256 key retains **128 bits of quantum security** against Grover's algorithm—a margin that remains computationally infeasible for the physical universe.

### 6.2 Galois/Counter Mode (GCM)
Standardized in NIST SP 800-38D, AES-256-GCM is an Authenticated Encryption with Associated Data (AEAD) scheme combining:
1. **Counter (CTR) Mode Encryption:** Plaintext is XORed with a keystream generated by encrypting successive counter values, enabling high throughput and hardware pipelining (Intel AES-NI, ARMv8 Cryptography Extensions) [NIST SP 800-38D].
2. **Galois Field Multiplication ($\text{GF}(2^{128})$):** Computes a 128-bit authentication tag over the ciphertext and associated data using GHASH polynomial evaluation. If an attacker modifies even a single bit of ciphertext or nonce in transit, the receiver's GMAC computation fails, raising an `InvalidTag` exception and dropping the packet [Dworkin, 2007].
3. **Nonce Uniqueness:** NIST SP 800-38D strictly mandates that a 96-bit nonce must never be reused under the same key. Nonce reuse completely destroys the authenticity guarantee of GMAC, allowing attackers to forge arbitrary authentication tags [Dworkin, 2007].

---

## 7. IoT Messaging: The MQTT Protocol & Security Vulnerabilities

### 7.1 Protocol Architecture
Message Queuing Telemetry Transport (MQTT) is an OASIS standard binary publish/subscribe messaging protocol designed specifically for constrained edge devices [OASIS MQTT 5.0; Dinculeana & Cheng, 2019]. Unlike HTTP, which requires verbose text headers (often exceeding 500 bytes per request) and repeated TCP handshakes, MQTT maintains a lightweight binary header (as small as 2 bytes) and persistent client-broker TCP connections.

### 7.2 Transport Security Limitations
Despite its efficiency, standard MQTT lacks native payload encryption [Dinculeana & Cheng, 2019]. By default, telemetry is published in plaintext. While Transport Layer Security (TLS/DTLS) can be enabled, Granjal et al. (2015) and Dinculeana & Cheng (2019) demonstrated that full TLS handshakes introduce severe computational and memory penalties on constrained 8-bit and 16-bit microcontrollers. Furthermore, TLS secures only the hop between the client and broker; once inside the broker, messages are decrypted into plaintext, exposing telemetry to compromised brokers. Application-layer payload encryption using AES-256-GCM resolves this limitation by providing end-to-end confidentiality directly from edge sensor to cloud receiver.

---

## 8. Post-Quantum Cryptographic Baselines: ML-KEM (Kyber) vs QKD

To establish an academically rigorous evaluation, QKD must be compared against contemporary mathematical post-quantum standards:
- **NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber) [Bos et al., 2018]:** Selected by NIST as the primary standard for post-quantum key encapsulation. Based on the hardness of the Module Learning With Errors (M-LWE) problem in module lattices.
- **Empirical IoT Benchmarks:** Shehzadi et al. (IEEE ISCAS 2025 [F2]) benchmarked Kyber-512 on an ARM Cortex-M4 microcontroller. While execution cycles were manageable, the public key size (800 bytes) and ciphertext size (768 bytes) remain substantial transmission overheads for constrained low-power wireless networks (e.g., LoRaWAN, 6LoWPAN) where maximum transmission units (MTUs) are under 128 bytes.
- **Security Foundations:** While ML-KEM offers software-only deployability, its security remains computational. QKD provides information-theoretic security rooted in physical law, making hybrid QKD-symmetric pipelines highly relevant for critical national infrastructure [Alshowkan et al., 2022].

---

## 9. Conclusion of Literature Review & Identified Gaps

Our systematic review confirms that while individual components—Qiskit BB84 circuit modeling, noise estimation, AES-256-GCM encryption, and MQTT messaging—have been explored in isolation, existing literature suffers from two critical oversights:
1. **The Reconciliation Void:** Prior hybrid prototypes omit Information Reconciliation, rendering their pipelines non-functional in the presence of channel noise.
2. **The Lack of Open End-to-End Testbeds:** No open-source, experimentally validated research framework exists that integrates Qiskit Aer circuit simulation, verified error reconciliation, universal-hash key derivation, and authenticated AES-256-GCM telemetry over MQTT with sub-millisecond benchmarking.

Our project is designed to bridge these exact research gaps.
