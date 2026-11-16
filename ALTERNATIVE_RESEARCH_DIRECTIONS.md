# Feasible Alternative Research Directions
## Strategic Research Pivots for Undergraduate and Early-Stage Graduate Investigations

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Scope:** Identifying high-impact, scientifically sound research questions that elevate the project beyond a basic "pipeline integration" into a peer-reviewed publication.  
**Constraint:** Must remain 100% executable within classical Python / Qiskit / MQTT simulation environments without requiring physical optical quantum hardware.

---

## Direction 1: Finite-Key Budgeting and Asymmetric Refresh Rate Optimization for Constrained IoT Telemetry

### 1. The Core Scientific Problem
In classical QKD theory, the asymptotic secret key rate assumes an infinite block length ($N \to \infty$). However, IoT edge devices operate under severe memory and transmission constraints, forcing key generation into small blocks ($N \le 2048$ qubits). Under the finite-key analysis of Tomamichel et al. (2012), statistical fluctuations in parameter estimation and privacy amplification extractable length penalties:
$$\ell \le \left\lfloor m \cdot [1 - h_2(\text{QBER})] - \text{leak}_{\text{EC}} - \Delta_{\text{finite}}(N, \epsilon_{\text{sec}}) \right\rfloor$$
where $\Delta_{\text{finite}}$ is the finite-size security penalty for secrecy parameter $\epsilon_{\text{sec}} = 10^{-10}$. In our empirical tests (EXP-1), block sizes $N \in \{256, 512\}$ resulted in an **entropy deficit ($\ell < 256$)**, producing zero usable keys, while $N \ge 1024$ succeeded.
Currently, no existing QKD-IoT literature establishes an **optimal key budgeting model** that balances the quantum generation cost against session-key consumption rates for varying IoT sensor transmission cadences (e.g., 1 Hz, 10 Hz, 100 Hz).

### 2. Research Questions
- What is the exact critical block threshold $N_{\text{crit}}$ required to yield a 256-bit symmetric key under finite-key security as a function of channel depolarizing noise $\lambda \in [0, 0.11]$?
- How does an asymmetric key refresh policy (refreshing keys based on packet volume vs. elapsed time) impact the risk of key exhaustion (starvation) in battery-powered edge nodes?

### 3. Proposed Methodology & Experimental Design
1. Simulate block sweeps $N \in \{512, 768, 1024, 1536, 2048, 4096\}$ across noise levels $\lambda \in \{0.00, 0.02, 0.04, 0.06, 0.08, 0.10\}$.
2. Model an IoT key pool buffer (capacity $C = 10$ keys) and measure buffer starvation probability under simulated sensor burst rates ($1$ to $50$ msgs/sec).
3. Derive an analytical Pareto frontier mapping key generation latency against transmission reliability.

### 4. Feasibility & Required Resources
- **Feasibility:** Very High. All required modules (`qkd/bb84.py`, `qkd/postprocessing/privacy_amplification.py`, `benchmark/runner.py`) are already implemented.
- **Compute:** Standard laptop / workstation running Python 3.12 (approx. 30 minutes of runtime for 1,000 trials).
- **Target Venues:** IEEE Internet of Things Journal, IEEE Transactions on Quantum Engineering, MDPI Sensors.

---

## Direction 2: Empirical Profiling of Cascade Information Reconciliation Efficiency vs. Leakage under Simulated Quantum Channel Noise

### 2. The Core Scientific Problem
Information reconciliation over a public classical channel inevitably leaks mutual information to an eavesdropper:
$$\text{leak}_{\text{EC}} = \sum_{i=1}^{M_{\text{passes}}} \text{bits\_disclosed}_i$$
Standard theoretical models approximate leakage using the Shannon limit: $\text{leak}_{\text{EC}} = f \cdot m \cdot h_2(\text{QBER})$, assuming an efficiency factor $f \approx 1.15$ to $1.25$. However, in finite discrete-variable BB84 simulations, $f$ fluctuates wildly depending on the initial block size $k_1$ and permutation patterns, often exceeding $f > 1.80$ when $QBER > 6\%$. Excessive leakage directly shrinks the final extractable key length $\ell$ during privacy amplification, potentially aborting the key exchange even when $QBER < 11\%$.

### 2. Research Questions
- What is the exact empirical leakage efficiency $f(\text{QBER}, k_1)$ of 4-pass permutation Cascade across varying block lengths under Qiskit Aer depolarizing noise?
- How should the initial block size $k_1$ dynamically adapt to estimated $\text{QBER}$ to maximize the final key generation rate $\ell / N$?

### 3. Proposed Methodology & Experimental Design
1. Instrument `CascadeReconciler` to log bit disclosures, parity exchange rounds, and back-tracking passes.
2. Sweep initial block sizes $k_1 \in \{4, 8, 12, 16, 24, 32\}$ across $\text{QBER} \in [0.01, 0.10]$.
3. Compute the empirical efficiency ratio $f = \text{leak}_{\text{EC}} / [m \cdot h_2(\text{QBER})]$ across 500 independent trials per configuration.
4. Formulate an adaptive block-sizing heuristic: $k_1^*(\text{QBER}) = \lfloor \alpha / \text{QBER} \rfloor$ and demonstrate that it increases final key yield by $\ge 15\%$.

### 4. Feasibility & Required Resources
- **Feasibility:** Very High. The Cascade module is already fully verified and passing all unit tests.
- **Compute:** Classical Python script running locally (~20 minutes).
- **Target Venues:** Quantum Information Processing (Springer), IEEE Access, Physical Review Applied.

---

## Direction 3: Comparative Benchmarking of QKD-Derived Symmetric Telemetry vs. NIST Post-Quantum KEM (ML-KEM-512) over Constrained MQTT Bandwidth

### 1. The Core Scientific Problem
A central debate in modern cybersecurity is whether hardware-intensive QKD offers tangible benefits over algorithmic Post-Quantum Cryptography (PQC), specifically NIST's standardized Module-Lattice Key Encapsulation Mechanism (FIPS 203 ML-KEM-512 / CRYSTALS-Kyber).
Advocates of PQC argue that ML-KEM eliminates the need for quantum channels and specialized hardware. However, in low-bandwidth wireless IoT environments (e.g., 802.15.4 / Zigbee, LoRaWAN, NB-IoT with 127-byte Maximum Transmission Unit [MTU]), ML-KEM introduces significant overhead:
- Public key size: 800 bytes
- Ciphertext size: 768 bytes
- Requires multi-packet fragmentation and reassembly, increasing packet loss and energy consumption.
Conversely, QKD-derived symmetric telemetry transmits only the encrypted payload (e.g., 32 bytes) + 12-byte nonce + 16-byte GMAC tag (60 bytes total), fitting comfortably within a single MTU frame.

### 2. Research Questions
- What are the quantitative latency, throughput, and packet fragmentation penalties of ML-KEM-512 vs. QKD-derived AES-256-GCM when transmitting MQTT telemetry over constrained bandwidth links ($10\text{ kbps}$ to $250\text{ kbps}$)?
- At what message transmission frequency does the one-time establishment cost of QKD break even with the continuous encapsulation overhead of ML-KEM?

### 3. Proposed Methodology & Experimental Design
1. Implement a baseline client using `liboqs-python` or `pycryptodome` executing NIST FIPS 203 ML-KEM-512 encapsulation/decapsulation.
2. Emulate bandwidth and MTU constraints using Linux `tc` (traffic control) or NetEm on the loopback / Mosquitto broker interface:
   - Bandwidth: $50\text{ kbps}$, $100\text{ kbps}$, $250\text{ kbps}$
   - Packet loss: $0\%, 1\%, 5\%$
   - MTU: 128 bytes (forcing fragmentation of ML-KEM keys).
3. Measure:
   - Handshake duration (ms)
   - Bandwidth consumption (total bytes over 1,000 messages)
   - Energy consumption model (using standard Cortex-M4 energy models: $0.18\text{ mJ/encap}$).

### 4. Feasibility & Required Resources
- **Feasibility:** High. Requires installing `liboqs` or pure-Python ML-KEM package (`kyber-py`) alongside existing MQTT client.
- **Compute:** Local workstation with standard Python environment.
- **Target Venues:** IEEE Internet of Things Journal, IEEE Transactions on Dependable and Secure Computing, IEEE ICC/GLOBECOM.

---

## Direction 4: Multi-Client Quantum Key Pool Scheduling and Starvation Prevention in Edge-Cloud Brokers

### 1. The Core Scientific Problem
In multi-tenant IoT networks, multiple sensor nodes connect to a single edge gateway or cloud broker. If the quantum key distribution link produces keys at a finite rate (e.g., 10 keys per minute in a simulated or physical link), concurrent high-frequency publishers can deplete the key buffer, leading to **key starvation**. When starvation occurs, clients must either block transmission (increasing latency) or fall back to insecure classical modes.

### 2. Research Questions
- What key scheduling discipline (e.g., Fair Queuing, Priority-Weighted Allocation, Least-Remaining-Time-to-Live) minimizes message drop probability while ensuring QoS for critical sensor telemetry?
- Can a dynamic key-derivation hierarchy (using a single QKD master key expanded into multiple ephemeral session keys via HKDF-SHA256) maintain forward secrecy while reducing quantum channel load by $10\times$?

### 3. Proposed Methodology & Experimental Design
1. Extend `cloud_receiver/receiver.py` with a multi-client Key Management Module supporting $K \in \{5, 10, 25, 50\}$ simulated sensor nodes.
2. Simulate heterogeneous traffic: critical alarm sensors ($100\text{ Hz}$, high priority) vs. periodic telemetry ($1\text{ Hz}$, low priority).
3. Evaluate three allocation strategies:
   - First-Come-First-Served (FCFS)
   - Deficit Round Robin (DRR)
   - Master-Key HKDF Expansion (RFC 5869).
4. Measure key buffer utilization, blocking delay, and forward-secrecy compromise windows under adversarial node compromise.

### 4. Feasibility & Required Resources
- **Feasibility:** High. Extends existing Python backend and SQLite schema.
- **Compute:** Standard multicore workstation.
- **Target Venues:** IEEE Access, Journal of Network and Computer Applications (Elsevier).

---

## Direction 5: Robustness Analysis of Stateful Replay Filters under Out-of-Order Delivery in Lossy Wireless Sensor Networks

### 1. The Core Scientific Problem
Wireless sensor networks suffer from multi-path routing, channel fading, and network jitter, causing packets to arrive out of order. While strict monotonic counters prevent replay attacks, they discard legitimate out-of-order packets. Conversely, sliding window filters (RFC 4303) accept delayed packets within window size $W$, but memory and bitwise operations must remain minimal on edge nodes.
No prior study has empirically evaluated the false-rejection rate vs. memory footprint of sliding window filters specifically paired with QKD session re-keying under extreme packet jitter.

### 2. Research Questions
- What is the optimal sliding window size $W \in \{32, 64, 128, 256\}$ that achieves zero false packet rejection under typical IEEE 802.15.4 packet reordering without creating a denial-of-service vulnerability?
- How does window state transition behave across automated session re-keying boundaries ($10^5$ packets)?

### 3. Proposed Methodology & Experimental Design
1. Generate synthetic packet streams with controlled packet permutation (Kendall's tau distance $\tau \in [0.01, 0.25]$) and random replay injection (1% to 10% malicious replays).
2. Measure:
   - False positive rejections (legitimate out-of-order packets dropped)
   - False negative acceptances (replays mistakenly accepted)
   - Bitmask operation latency ($\mu\text{s}$) on simulated Raspberry Pi / edge hardware.
3. Validate seamless state reset upon QKD key renegotiation.

### 4. Feasibility & Required Resources
- **Feasibility:** Very High. The sliding window filter is already fully operational in `cloud_receiver/receiver.py` and passes all pytest test cases.
- **Compute:** Local Python test scripts (~5 minutes).
- **Target Venues:** IEEE Communications Letters, Ad Hoc Networks (Elsevier), Sensors.

---

## Direction 6: Adaptive Basis Sifting and Error-Correction Block Sizing for Variable-Noise Channels

### 1. The Core Scientific Problem
Most QKD implementations assume stationary channel noise. In real environments (e.g., optical fiber subjected to temperature variations, or free-space optical links to UAVs affected by atmospheric turbulence), channel noise fluctuates dynamically over time. When noise spikes, fixed-parameter Cascade error correction fails or induces excessive leakage, causing key generation to collapse.

### 2. Research Questions
- Can a real-time feedback loop between Bob's observed $\text{QBER}$ and Alice's quantum circuit noise estimation dynamically tune the sifting sample fraction and reconciliation block structure?
- What is the maximum noise volatility rate $(d\lambda / dt)$ that an adaptive pipeline can track while sustaining an active AES-256-GCM session key refresh rate?

### 3. Proposed Methodology & Experimental Design
1. Implement a time-varying depolarizing noise channel $\lambda(t) = \lambda_0 + A \sin(\omega t) + \xi(t)$ in `qkd/channel.py`.
2. Implement an adaptive Kalman filter or EWMA (Exponentially Weighted Moving Average) estimator tracking $\text{QBER}_t$.
3. Dynamically modulate the sifting verification sample size and Cascade initial block size based on the estimated noise.
4. Benchmark key generation yield and key stability against a static baseline.

### 4. Feasibility & Required Resources
- **Feasibility:** Moderate. Requires adding dynamic parameter modulation logic to the QKD orchestrator.
- **Compute:** Local workstation (~1 hour of simulation runs).
- **Target Venues:** IEEE Transactions on Quantum Engineering, Quantum Science and Technology (IOP).

---

## Recommended Strategic Selection for the Major Project

| Direction | Scientific Novelty | Implementation Effort | Academic Defensibility | Recommended Rank |
|:---|:---:|:---:|:---:|:---:|
| **Direction 3 (QKD vs. ML-KEM-512 over MQTT)** | **Very High** | Moderate | **Highest** | **#1 (Primary Recommendation)** |
| **Direction 1 (Finite-Key Budgeting for IoT)** | High | Low | Very High | **#2 (Strong Alternative)** |
| **Direction 2 (Cascade Leakage Profiling)** | High | Low | High | **#3 (Specialized Physics/Math)** |
| **Direction 5 (Robust Replay Filtering in Lossy Nets)** | Moderate | Very Low | Moderate | **#4 (Systems/Networking)** |
| **Direction 4 (Multi-Client Key Pool Scheduling)** | Moderate | Moderate | Moderate | **#5 (Cloud Systems)** |
| **Direction 6 (Adaptive Reconciliation for Dynamic Noise)** | High | High | High | **#6 (Advanced Theoretical)** |

### Why Direction 3 is the Winning Strategic Pivot:
Reviewers in applied cybersecurity and IoT continuously pose the fundamental objection: *"Why should anyone care about simulated QKD when NIST has already standardized post-quantum cryptography (FIPS 203 ML-KEM) that works on existing classical hardware?"*  
By experimentally answering this question—demonstrating that ML-KEM suffers from severe packet fragmentation and transmission latency penalties in constrained IoT networks compared to QKD-assisted symmetric telemetry—the manuscript transitions from a simple integration prototype to a **compelling, highly citable comparative research study**.
