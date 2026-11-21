# SCIENTIFIC LIMITATIONS AND METHODOLOGICAL BOUNDARIES
## HYBRID-QKD-BB84-AES256-GCM-MQTT-IOT-PIPELINE
**Branch:** `verification/publication-readiness` | **Head Commit:** `525676d`  
**Author:** Quantum Cryptography Research Engineer & Reproducibility Auditor

---

### Executive Statement

In accordance with strict scientific integrity, this document establishes the explicit technical, mathematical, and architectural boundaries of the implementation. No claims of physical quantum hardware execution, information-theoretically certified composable finite-key security, or real-world metropolitan QKD deployment are made.

---

### 1. Quantum Simulation Boundary vs. Physical Optics

```mermaid
flowchart LR
    subgraph Reality["Physical QKD System (Not Present)"]
        Laser[Pulsed Laser Diode] --> Attn[Optical Attenuator]
        Attn --> Mod[Phase/Polarization Modulator]
        Mod --> Fiber[Single-Mode Fiber (0.2 dB/km)]
        Fiber --> SNSPD[Superconducting Nanowire Detectors]
    end
    subgraph Software["Implemented Architecture (Verified)"]
        State[Qiskit Statevector / Aer] --> Depol[Depolarizing Error Model]
        Depol --> Proj[Ideal Projective Measurement]
    end
```

1. **State Space & Measurement:**
   * The quantum communication phase is simulated entirely in software using IBM Qiskit Aer (`qiskit-aer==0.18.2`).
   * States $\lvert 0 \rangle, \lvert 1 \rangle, \lvert + \rangle, \lvert - \rangle$ are represented as ideal single-qubit density matrices or statevectors.
   * Measurements are modeled as projective von Neumann operators ($P_Z = \{\lvert 0 \rangle\langle 0 \rvert, \lvert 1 \rangle\langle 1 \rvert\}$ and $P_X = \{\lvert + \rangle\langle + \rvert, \lvert - \rangle\langle - \rvert\}$).
2. **Missing Physical Channel Imperfections:**
   * **Fiber Attenuation:** Optical attenuation ($\alpha \approx 0.2 \text{ dB/km}$ in standard SMF-28 telecom fiber) is not modeled. The simulation assumes $100\%$ photon transmission efficiency.
   * **Dark Counts & Detector Dead Time:** Physical InGaAs or SNSPD detectors exhibit dark count rates ($10 - 1000 \text{ Hz}$) and recovery dead times ($10 - 50 \text{ ns}$). The simulation models only uniform depolarizing channel noise ($p$).
   * **Multiphoton Pulses & Photon Number Splitting (PNS):** Weak coherent laser pulses follow Poissonian photon number distributions $P(n) = \mu^n e^{-\mu} / n!$. The codebase does not simulate multiphoton emission or decoy-state intensity modulation (e.g., vacuum-weak decoy states).
   * **Phase Drift & Polarization Mode Dispersion:** Polarization alignment is assumed to be perfect; no active fiber feedback or tracking loops are simulated.

---

### 2. Finite-Key Model Classification: Engineering Estimate vs. Composable Security

#### 2.1 Codebase Implementation: Asymptotic Leftover Hash Lemma
The codebase implements the privacy amplification secret-key length calculation according to the engineering formulation of the Leftover Hash Lemma (LHL):
$$\ell_{\text{engineering}} = \max\left(0, \lfloor m(1 - h_2(e)) - \text{leak}_{\text{EC}} - 64 \rfloor\right)$$
where:
* $m$: Number of retained sifted bits after parameter estimation.
* $h_2(e)$: Binary Shannon entropy evaluated at the observed sample QBER $e$.
* $\text{leak}_{\text{EC}}$: Empirical bit leakage during Cascade reconciliation.
* $64$: Engineering security safety margin ($2^{-64}$ hashing collision bound).

#### 2.2 Why This Cannot Claim Composable Finite-Key Security
In composable quantum cryptography (Tomamichel et al., 2012; Scarani & Renner, 2008):
1. **Conjugate Basis Phase-Error Bounding:**
   To bound the adversary's smooth min-entropy $H_{\text{min}}^{\epsilon}(X|E)$, Alice and Bob must upper-bound the *phase error rate* ($e_{\text{phase}}$) on the bits used for key extraction.
2. **Basis Mixing in the Implementation:**
   * In `qkd/sifting.py`, bits matching in the $\mathcal{Z}$ basis and $\mathcal{X}$ basis are merged into a single undifferentiated sifted string.
   * In `qkd/qber.py`, parameter estimation uniformly samples $25\%$ of bits from this mixed pool, measuring the average *bit error rate*.
   * Without segregated basis statistics (e.g., using $\mathcal{Z}$ exclusively for key generation and $\mathcal{X}$ exclusively for phase error estimation, or assuming a strictly symmetric depolarizing channel), the sample bit error rate does not formally bound Eve's information under general coherent attacks.
3. **Formal Classification:**
   The implementation is scientifically classified as an **Experimental Privacy Amplification Demonstration** rather than an Information-Theoretically Certified QKD System.

---

### 3. Transport Mechanism: In-Process Queue vs. Live Network MQTT

1. **Queue Fallback (`SimulatedBroker`):**
   * Operates via in-process, thread-safe Python `queue.Queue`.
   * Bypasses the OS kernel networking stack, TCP 3-way handshake, socket buffers, and packet serialization.
   * Latency is on the order of microseconds ($1.4 \pm 0.3 \text{ ms}$ total pipeline latency).
   * It provides deterministic, zero-dependency testing, but does not reflect real-world MQTT packet loss, network jitter, or network partition behavior.
2. **Live Broker (`PahoLiveClient`):**
   * Uses Eclipse Paho MQTT over TCP port 1883 against Mosquitto.
   * Latency reflects socket I/O ($18.4 \pm 4.1 \text{ ms}$ over loopback).
   * Subject to network socket availability and daemon configuration.

---

### 4. Post-Quantum Baseline Attribution (Experiment 7)

1. **Heterogeneous Origin of Data:**
   * The post-quantum cryptography (PQC) handshake benchmark for **ML-KEM-512** ($2.15 \text{ ms}$) reported in Experiment 7 and Table 7 is an **empirical literature reference** from *Shehzadi et al. (2025)*, measured on an embedded ARM Cortex-M4 microcontroller running optimized assembly.
   * The **Hybrid QKD-BB84** handshake latency ($805.1 \pm 113.1 \text{ ms}$) represents **software simulation runtime** using Qiskit Aer on desktop CPython.
2. **Methodological Transparency:**
   * These benchmarks evaluate fundamentally different execution paradigms: hardware-accelerated lattice mathematics on microcontrollers versus full quantum statevector simulation on a desktop CPU.
   * Manuscript Table 7 and the experiment documentation explicitly highlight this provenance to prevent readers from confusing software simulation overhead with physical optical QKD clock rates (which operate at GHz pulse repetition frequencies).

---

### 5. Classical Channel Authentication

* The BB84 protocol fundamentally relies on an **authenticated classical channel** to prevent active Man-in-the-Middle (MitM) basis spoofing.
* In physical deployments, this requires information-theoretic Wegman-Carter polynomial MACs or pre-shared keys.
* In the current simulation, classical parameter exchanges (bases, parities, sample indices) occur via direct Python object references and function calls, implicitly assuming channel authenticity without cryptographic MAC verification.

---

### 6. Key Lifecycle & Out-of-Band Key Management Channel

* **Software Simulation of Key Distribution:**
  In real metropolitan QKD networks (e.g. ETSI GS QKD 014 / 004 key delivery APIs), Alice and Bob install keys into hardware Key Management Systems (KMS) over standardized authenticated interfaces.
* In this prototype, the cloud receiver learns rotated key identifiers and session materials via an in-process thread-safe callback (`on_key_rotated`), matching the simulation environment of the MQTT broker bridge.
* While the key lifecycle state machine (`KeyLifecycleManager`) strictly enforces NIST SP 800-38D invocation bounds, zeroization of retired keys, and prevents encryption under expired keys, the key delivery mechanism between the QKD post-processing engine and receiver is an in-process software abstraction, not an authenticated hardware KMS link.
