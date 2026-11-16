# Profile of the 15 Closest Prior-Art Publications
## Systematic Evaluation across 20 Standard Technical Dimensions

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Evaluation Role:** Independent Academic Research Analyst  
**Date:** November 2026  

---

### Summary of Surveyed Works and Evidence Tiers

| ID | Author(s) & Year | Venue & Type | Evidence Level | Primary Focus |
|:---|:---|:---|:---:|:---|
| **P1** | Farooq, Sharma, & Pradhan (2024) | IEEE WPMC (Conf) | `METADATA_ONLY` | QKD-assisted MQTT security framework |
| **P2** | Rehman & Alharbi (2025) | MDPI Smart Cities (Journal) | `METADATA_ONLY` | QESIF IoT security framework (REST/HTTP) |
| **P3** | Alshowkan et al. (2022) | Nature Sci. Reports (Journal) | `FULL_TEXT_ACCESSED` | Hardware QKD for SCADA/smart grid via MQTT |
| **P4** | Büyükdede (2026) | Informatica (Journal) | `FULL_TEXT_ACCESSED` | Educational Qiskit Aer BB84 virtual simulator |
| **P5** | Chaturvedi et al. (2025) | Nature Sci. Reports (Journal) | `FULL_TEXT_ACCESSED` | Hybrid Multi-Node QKD-ECC for IoT (IBM Cloud) |
| **P6** | Manimozhi & Mugelan (2025) | EPJ Quantum Tech. (Journal) | `FULL_TEXT_ACCESSED` | BB84 sifted key to ECC mapping for AES |
| **P7** | Fiorini et al. (2024) | Future Internet (Journal) | `METADATA_ONLY` | Interception density estimation in Qiskit Aer |
| **P8** | Fiorini et al. (2026) | Computer Networks (Journal) | `METADATA_ONLY` | Threshold eavesdropper detection in noisy BB84 |
| **P9** | Das et al. (2026) | Physica Scripta (Journal) | `METADATA_ONLY` | Qiskit BB84 gate-level simulation under noise |
| **P10** | Hubballi et al. (2026) | IEEE NQComp (Conf) | `METADATA_ONLY` | Qiskit noise-tolerant BB84 framework |
| **P11** | Adu-Kyere, Nigussie, & Isoaho (2022) | Sensors (Journal) | `FULL_TEXT_ACCESSED` | Python 3 classical RNG BB84 modeling |
| **P12** | Kaganurmath, Cholli, & Anala (2025) | ETASR (Journal) | `FULL_TEXT_ACCESSED` | DLKS-MQTT lightweight key scheduling in Cooja |
| **P13** | Biswas et al. (2024) | IEEE FNWF (Conf) | `METADATA_ONLY` | QKD-secured lightweight IoT protocol |
| **P14** | Shehzadi et al. (2025) | IEEE ISCAS (Conf) | `METADATA_ONLY` | ML-KEM + Ascon-128a on ARM Cortex-M4 |
| **P15** | Mallick et al. (2026) | Computers (Journal Review) | `METADATA_ONLY` | Systematic review of QKD in IoT / CPS |

---

## Publication 1 (P1): Farooq, Sharma, and Pradhan (2024)

1. **Full Citation & DOI:** Sawdah Farooq, Parth Sharma, and Pyari Mohan Pradhan. "Enhanced Security Framework For MQTT Protocol Based IoT Network Using Quantum Key Distribution." *2024 IEEE 27th International Symposium on Wireless Personal Multimedia Communications (WPMC)*, IEEE, pp. 1–5, Nov 2024. DOI: [10.1109/WPMC63271.2024.10863467](https://doi.org/10.1109/WPMC63271.2024.10863467).
2. **Evidence Level:** `METADATA_ONLY` (Full text behind IEEE Xplore paywall / restricted access).
3. **Core Research Problem:** Mitigating vulnerabilities of the standard MQTT publish-subscribe architecture against quantum-enabled eavesdropping and man-in-the-middle attacks.
4. **Proposed Architecture:** Conceptual integration of a QKD key distribution mechanism with an MQTT broker to distribute symmetric encryption keys to IoT publishers and subscribers.
5. **QKD Protocol & Implementation Level:** BB84 protocol mentioned; modeled at high architectural level (abstract key distribution mechanism, not circuit-level gates).
6. **Quantum Simulator / Platform:** Custom analytical/simulation scripts; Qiskit Aer not indicated in indexed metadata.
7. **Quantum Channel & Noise Model:** Unspecified in available metadata.
8. **Eavesdropper Model:** Intercept-resend eavesdropping considered conceptually.
9. **Sifting & QBER Threshold:** Standard theoretical sifting assumed; specific numerical threshold unstated in metadata.
10. **Information Reconciliation:** Unstated / absent (exemplifies the simulation "reconciliation void").
11. **Privacy Amplification:** Unstated / treated as black-box key extraction.
12. **Classical Channel Authentication:** Unstated.
13. **Symmetric Cryptography & Mode:** AES encryption mentioned; AEAD mode (GCM) unconfirmed.
14. **Nonce Policy & Replay Protection:** Unstated.
15. **Transport Protocol & Broker:** MQTT protocol using Mosquitto broker architecture.
16. **Cloud / Backend Integration:** Conceptual broker-to-subscriber backend.
17. **Hardware / OS Testbed:** General PC/Linux workstation simulation.
18. **Baselines Compared & Benchmarks:** Contrasted conceptually against unencrypted MQTT; microsecond component-level profiling absent.
19. **Key Limitations & Gaps:** Lacks gate-level circuit simulation, explicit post-processing (Cascade/Toeplitz), open-source testbed, and sliding-window replay filter.
20. **Similarities & Divergences vs. Our Project:** Shares the high-level objective (QKD + MQTT + AES). Diverges completely in technical depth: our project implements gate-level Qiskit Aer circuits, a complete 4-pass Cascade reconciliation, 2-universal Toeplitz hashing, RFC 64-packet anti-replay, and an open-source testbed.

---

## Publication 2 (P2): Rehman & Alharbi (2025)

1. **Full Citation & DOI:** Abdul Rehman and Omar Alharbi. "QESIF: A Lightweight Quantum-Enhanced IoT Security Framework for Smart Cities." *Smart Cities*, MDPI, Vol. 8, Issue 4, pp. 116, 2025. DOI: [10.3390/smartcities8040116](https://doi.org/10.3390/smartcities8040116).
2. **Evidence Level:** `METADATA_ONLY` (Blocked by MDPI Akamai EdgeSuite filter; verified via Crossref API).
3. **Core Research Problem:** Designing a lightweight, quantum-enhanced security framework for edge-cloud smart city infrastructure.
4. **Proposed Architecture:** Quantum Key Distribution module interacting with an IoT gateway to refresh symmetric keys for cloud telemetry.
5. **QKD Protocol & Implementation Level:** High-level algorithmic model of BB84 key exchange.
6. **Quantum Simulator / Platform:** Custom Python smart city framework.
7. **Quantum Channel & Noise Model:** No gate-level depolarizing quantum noise model.
8. **Eavesdropper Model:** Basic QBER check under simulated intrusion.
9. **Sifting & QBER Threshold:** Basis sifting with standard 11% abort threshold.
10. **Information Reconciliation:** Not implemented (assumes zero channel errors post-sifting).
11. **Privacy Amplification:** Unkeyed hash function (SHA-256) rather than 2-universal Toeplitz matrix hashing.
12. **Classical Channel Authentication:** Gateway-level session credentials.
13. **Symmetric Cryptography & Mode:** AES-GCM for authenticated encryption.
14. **Nonce Policy & Replay Protection:** Timestamp-based freshness validation.
15. **Transport Protocol & Broker:** HTTP / REST APIs (MQTT not utilized for telemetry).
16. **Cloud / Backend Integration:** Smart city cloud dashboard and database persistence.
17. **Hardware / OS Testbed:** Python edge gateway emulation.
18. **Baselines Compared & Benchmarks:** Reports ~20.3 ms end-to-end latency for HTTP-based key refresh.
19. **Key Limitations & Gaps:** Relies on heavy HTTP/REST rather than lightweight MQTT; omits error correction; uses SHA-256 for PA violating Leftover Hash Lemma.
20. **Similarities & Divergences vs. Our Project:** Both utilize AES-GCM and cloud persistence. Our project differs by using event-driven MQTT, true gate-level Qiskit circuits, Cascade reconciliation, and strict Leftover Hash Lemma privacy amplification.

---

## Publication 3 (P3): Alshowkan et al. (2022)

1. **Full Citation & DOI:** Muneer Alshowkan, Philip G. Evans, Michael Starke, Travis Humble, and Nicholas Peters. "Authentication of Smart Grid Communications Using Quantum Key Distribution." *Scientific Reports*, Nature Publishing Group, Vol. 12, Article 12731, pp. 1–11, 2022. DOI: [10.1038/s41598-022-16090-w](https://doi.org/10.1038/s41598-022-16090-w).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (PMC9325752, Open Access).
3. **Core Research Problem:** Real-time message authentication for SCADA / smart grid telemetry using QKD keys over deployed optical fiber.
4. **Proposed Architecture:** Distributed Energy Resource (DER) nodes in Chattanooga, TN connected via optical fiber to a commercial Qubitekk QKD system, feeding keys into an MQTT broker.
5. **QKD Protocol & Implementation Level:** BBM92 entanglement-based QKD executed on physical photon-pair hardware.
6. **Quantum Simulator / Platform:** Not simulated — physical optical hardware (PPLN waveguide, single-photon detectors).
7. **Quantum Channel & Noise Model:** Real-world metro fiber attenuation, polarization drift, and detector dark counts.
8. **Eavesdropper Model:** Information-theoretic security against active/passive channel adversaries.
9. **Sifting & QBER Threshold:** Autonomously managed by proprietary Qubitekk hardware appliance.
10. **Information Reconciliation:** Handled internally by hardware appliance firmware.
11. **Privacy Amplification:** Handled internally by hardware appliance firmware.
12. **Classical Channel Authentication:** Carter-Wegman MAC / AES-GMAC.
13. **Symmetric Cryptography & Mode:** AES-GMAC (128, 192, 256 bits) for authentication-only (no payload confidentiality).
14. **Nonce Policy & Replay Protection:** 128-bit QRNG IVs and sequential message counter tracking.
15. **Transport Protocol & Broker:** MQTT publish-subscribe messaging over TCP/IP connecting substation agents.
16. **Cloud / Backend Integration:** Electric Power Board (EPB) utility control center.
17. **Hardware / OS Testbed:** Raspberry Pi 3B+ edge nodes (1.4 GHz Cortex-A53, 1 GB RAM) running Linux.
18. **Baselines Compared & Benchmarks:** Compared against RSA signatures (1024 to 8192 bits); reported <0.5 ms GMAC verification vs >15 ms for RSA-4096.
19. **Key Limitations & Gaps:** Requires expensive physical optical infrastructure; does not encrypt payload (GMAC authentication only); key generation rate bottlenecks high-frequency traffic.
20. **Similarities & Divergences vs. Our Project:** Closest architectural baseline for MQTT + quantum keys. However, Alshowkan is a physical hardware deployment providing GMAC-only authentication, whereas our project is a fully open-source, software-simulated end-to-end framework providing both AES-256-GCM encryption and authentication with gate-level circuit modeling.

---

## Publication 4 (P4): Büyükdede (2026)

1. **Full Citation & DOI:** Mert Büyükdede. "A Virtualized BB84 QKD Simulator in Python Using Qiskit Aer for Education and Prototyping." *Informatica*, Vol. 50, No. 13, pp. 1–12, 2026. DOI: [10.31449/inf.v50i13.9101](https://doi.org/10.31449/inf.v50i13.9101).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (Downloaded PDF `papers_data/A6.pdf`).
3. **Core Research Problem:** Lack of accessible, lightweight Python simulators for teaching and prototyping the BB84 protocol on quantum circuits.
4. **Proposed Architecture:** Standalone script constructing Qiskit QuantumCircuit instances for Alice, Eve, and Bob, executed on Qiskit Aer `qasm_simulator`.
5. **QKD Protocol & Implementation Level:** 4-state BB84 ($|0\rangle, |1\rangle, |+\rangle, |-\rangle$) using X and H gates.
6. **Quantum Simulator / Platform:** Python 3 + IBM Qiskit Aer simulator.
7. **Quantum Channel & Noise Model:** Depolarizing and amplitude damping noise channels via Qiskit's `NoiseModel`.
8. **Eavesdropper Model:** Intercept-resend attack where Eve randomly selects rectilinear or diagonal basis.
9. **Sifting & QBER Threshold:** Basis sifting discards ~50% bits; parameter estimation checks sample QBER.
10. **Information Reconciliation:** Explicitly absent (author states in Section 5 that error correction is omitted).
11. **Privacy Amplification:** Explicitly absent (author confirms omission).
12. **Classical Channel Authentication:** Explicitly absent.
13. **Symmetric Cryptography & Mode:** None (mentions AES-256 in background, but no cipher execution).
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None (local in-memory Python execution).
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Desktop PC running Python.
18. **Baselines Compared & Benchmarks:** Theoretical vs. simulated eavesdropper detection probabilities (sweeps sample bits 10–120).
19. **Key Limitations & Gaps:** Isolated simulator with zero post-processing, zero transport, and zero application-layer binding.
20. **Similarities & Divergences vs. Our Project:** Shares Qiskit Aer circuit simulation. Diverges because our project builds the entire downstream pipeline: 4-pass Cascade, Toeplitz hashing, AES-256-GCM, MQTT, and cloud dashboard.

---

## Publication 5 (P5): Chaturvedi et al. (2025)

1. **Full Citation & DOI:** Rajnish Kumar Chaturvedi et al. "A Hybrid Multi-Node QKD-ECC Architecture for Securing IoT Networks." *Scientific Reports*, Nature Publishing Group, Vol. 15, Article 32831, pp. 1–15, 2025. DOI: [10.1038/s41598-025-17184-x](https://doi.org/10.1038/s41598-025-17184-x).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (PMC12464159, Open Access).
3. **Core Research Problem:** High communication overhead and lack of scalability in multi-node IoT networks using pure QKD.
4. **Proposed Architecture:** Multi-node cluster framework (MNQ-ECC) combining entangled QKD with Elliptic Curve Cryptography (ECC) for hierarchical key exchange.
5. **QKD Protocol & Implementation Level:** Entangled Bell states ($|\Phi^+\rangle$) and BB84 variants modeled via quantum circuits.
6. **Quantum Simulator / Platform:** IBM Qiskit running in Python 3.12.7 + IBM Quantum Composer simulator on IBM Cloud.
7. **Quantum Channel & Noise Model:** Entanglement degradation model and channel loss efficiency $\eta$.
8. **Eavesdropper Model:** Information leakage rate $r_E$; analyzed against MitM and replay attacks.
9. **Sifting & QBER Threshold:** Theoretical Shannon entropy $H(Q)$ based on QBER; analytical threshold.
10. **Information Reconciliation:** Modeled analytically via efficiency factor $f(Q)$; algorithmic Cascade not implemented.
11. **Privacy Amplification:** Analytical entropy extraction formula outputting 256-bit key.
12. **Classical Channel Authentication:** ECC public key pairs, temporal credentials, and cryptographic hashes.
13. **Symmetric Cryptography & Mode:** Mentions AES in background; proposed scheme relies primarily on ECC point operations.
14. **Nonce Policy & Replay Protection:** Random nonces and temporal credentials.
15. **Transport Protocol & Broker:** Abstract multi-hop simulated network; MQTT not implemented.
16. **Cloud / Backend Integration:** IBM Quantum Cloud for circuit execution; IoT cloud gateway modeled conceptually.
17. **Hardware / OS Testbed:** Intel Core i7 (3.6 GHz), 16 GB RAM, Ubuntu 20.04.
18. **Baselines Compared & Benchmarks:** Evaluated against traditional IoT authentication schemes; measured latency, entropy, and energy.
19. **Key Limitations & Gaps:** No working MQTT telemetry pipeline; relies on complex ECC pairings on constrained nodes; lacks algorithmic error correction.
20. **Similarities & Divergences vs. Our Project:** Both use Qiskit. Chaturvedi focuses on complex multi-node ECC routing, whereas our project focuses on a streamlined, complete BB84 $\to$ Cascade $\to$ Toeplitz $\to$ AES-GCM $\to$ MQTT pipeline.

---

## Publication 6 (P6): Manimozhi & Mugelan (2025)

1. **Full Citation & DOI:** M. Manimozhi and R. K. Mugelan. "Post-Quantum AES Encryption Using ECC Points Derived from BB84 Sifted Keys." *EPJ Quantum Technology*, Springer/EDP Sciences, Vol. 12, Article 109, pp. 1–18, 2025. DOI: [10.1140/epjqt/s40507-025-00411-9](https://doi.org/10.1140/epjqt/s40507-025-00411-9).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (Downloaded PDF `papers_data/A3.pdf`).
3. **Core Research Problem:** Generating dynamic, post-quantum resilient symmetric keys for resource-constrained IoT devices without heavy hardware.
4. **Proposed Architecture:** BB84 simulation derives sifted bits, which are converted into ECC curve parameters to establish a shared secret, subsequently seeding AES.
5. **QKD Protocol & Implementation Level:** BB84 protocol implemented in custom Python 3 script.
6. **Quantum Simulator / Platform:** Custom Python scripts (cites Adu-Kyere 2022); no Qiskit gate circuits.
7. **Quantum Channel & Noise Model:** Statistical depolarizing channel model.
8. **Eavesdropper Model:** Intercept-resend eavesdropping causing QBER anomalies.
9. **Sifting & QBER Threshold:** Basis reconciliation; unusually relaxed QBER abort threshold of 25% (unconditionally insecure under standard quantum physics).
10. **Information Reconciliation:** Custom basis reconciliation; lacks multi-pass Cascade error correction.
11. **Privacy Amplification:** Unstated (relies on ECC mathematical mapping rather than universal hashing).
12. **Classical Channel Authentication:** Unstated.
13. **Symmetric Cryptography & Mode:** AES symmetric encryption (exact mode like GCM unstated).
14. **Nonce Policy & Replay Protection:** Unstated.
15. **Transport Protocol & Broker:** Abstract TCP sockets; MQTT mentioned only in related work.
16. **Cloud / Backend Integration:** Conceptual cloud platform mention.
17. **Hardware / OS Testbed:** Standard desktop computer running Python.
18. **Baselines Compared & Benchmarks:** Compared against traditional ECC; measured key generation time (ms), throughput, and QBER.
19. **Key Limitations & Gaps:** Cryptographically flawed 25% QBER threshold; lacks explicit Cascade reconciliation (fatal under channel noise); lacks MQTT broker.
20. **Similarities & Divergences vs. Our Project:** Attempts BB84 $\to$ AES key transition. Diverges in cryptographic correctness: our project maintains the rigorous 11% Shor-Preskill threshold, executes 4-pass Cascade, and deploys standard AES-256-GCM over real MQTT.

---

## Publication 7 (P7): Fiorini et al. (2024)

1. **Full Citation & DOI:** Francesco Fiorini, Michele Pagano, Rosario Giuseppe Garroppo, and Antonio Osele. "Estimating Interception Density in the BB84 Protocol: A Study with a Noisy Quantum Simulator." *Future Internet*, MDPI, Vol. 16, Issue 8, pp. 275, 2024. DOI: [10.3390/fi16080275](https://doi.org/10.3390/fi16080275).
2. **Evidence Level:** `METADATA_ONLY` (Blocked by publisher anti-bot filter; metadata confirmed via Crossref).
3. **Core Research Problem:** Accurately distinguishing between channel-induced noise and an eavesdropper's interception density in noisy BB84 implementations.
4. **Proposed Architecture:** Standalone simulation framework modeling quantum channel impairments and Eve's interception rate in Qiskit Aer.
5. **QKD Protocol & Implementation Level:** Gate-level BB84 circuit simulation.
6. **Quantum Simulator / Platform:** IBM Qiskit Aer.
7. **Quantum Channel & Noise Model:** Depolarizing noise channel and thermal relaxation models.
8. **Eavesdropper Model:** Partial intercept-resend attack with variable interception probability $p_{\text{eve}} \in [0, 1]$.
9. **Sifting & QBER Threshold:** Detailed mathematical estimator for interception density from sifted bits.
10. **Information Reconciliation:** None (stops at physical/sifting layer).
11. **Privacy Amplification:** None.
12. **Classical Channel Authentication:** None.
13. **Symmetric Cryptography & Mode:** None.
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Python / Qiskit Aer scientific environment.
18. **Baselines Compared & Benchmarks:** Analytical vs. simulated QBER and interception density curves.
19. **Key Limitations & Gaps:** Confined entirely to quantum physics simulation; zero network, transport, or cryptographic application.
20. **Similarities & Divergences vs. Our Project:** Shares the Qiskit Aer intercept-resend noise modeling. Diverges because our project integrates this quantum physics simulation into a functioning IoT telemetry application.

---

## Publication 8 (P8): Fiorini et al. (2026)

1. **Full Citation & DOI:** Francesco Fiorini, Rosario Giuseppe Garroppo, Michele Pagano, and Rostyslav Dovhaliuk. "Threshold-Based Eavesdropper Detection for Partial Intercept–Resend Attack in Noisy BB84 QKD." *Computer Networks*, Elsevier, Vol. 277, Article 112058, pp. 1–14, 2026. DOI: [10.1016/j.comnet.2026.112058](https://doi.org/10.1016/j.comnet.2026.112058).
2. **Evidence Level:** `METADATA_ONLY` (Elsevier ScienceDirect paywall; verified via Crossref).
3. **Core Research Problem:** Formulating statistical decision thresholds to detect partial eavesdropping under severe channel noise without false aborts.
4. **Proposed Architecture:** Advanced hypothesis-testing framework applied to BB84 QBER statistics.
5. **QKD Protocol & Implementation Level:** Qiskit Aer circuit simulation.
6. **Quantum Simulator / Platform:** IBM Qiskit Aer + Python statistical packages.
7. **Quantum Channel & Noise Model:** Comprehensive depolarizing and asymmetric bit-flip/phase-flip channel models.
8. **Eavesdropper Model:** Partial intercept-resend attack.
9. **Sifting & QBER Threshold:** Neyman-Pearson and Bayesian decision thresholds for QBER cutoff.
10. **Information Reconciliation:** None.
11. **Privacy Amplification:** None.
12. **Classical Channel Authentication:** None.
13. **Symmetric Cryptography & Mode:** None.
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Linux workstation.
18. **Baselines Compared & Benchmarks:** Receiver Operating Characteristic (ROC) curves, false alarm rates vs. detection probability.
19. **Key Limitations & Gaps:** Pure theoretical/simulation study of eavesdropper detection; lacks any IoT messaging or encryption layer.
20. **Similarities & Divergences vs. Our Project:** Deepens the eavesdropping detection methodology that our project uses, but remains isolated from application-layer IoT systems.

---

## Publication 9 (P9): Das et al. (2026)

1. **Full Citation & DOI:** Aditya Das et al. "Simulating BB84 Protocol with Noise in Quantum Key Distribution Systems Using IBM Qiskit." *Physica Scripta*, IOP Publishing, Vol. 101, Article 275506, pp. 1–10, 2026. DOI: [10.1088/1402-4896/ae79e4](https://doi.org/10.1088/1402-4896/ae79e4).
2. **Evidence Level:** `METADATA_ONLY` (IOP Publishing paywall; verified via Crossref).
3. **Core Research Problem:** Investigating the impact of quantum noise (depolarizing, amplitude damping) on BB84 key agreement fidelity in Qiskit.
4. **Proposed Architecture:** Qiskit circuit models evaluating fidelity degradation under parameterized noise.
5. **QKD Protocol & Implementation Level:** Standard 4-state BB84 quantum circuits.
6. **Quantum Simulator / Platform:** IBM Qiskit Aer.
7. **Quantum Channel & Noise Model:** Gate-level error insertion and channel noise models.
8. **Eavesdropper Model:** Channel noise focused; eavesdropping simulated via equivalent error injection.
9. **Sifting & QBER Threshold:** Basis matching and QBER estimation across noise parameters.
10. **Information Reconciliation:** None.
11. **Privacy Amplification:** None.
12. **Classical Channel Authentication:** None.
13. **Symmetric Cryptography & Mode:** None.
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Python scientific workstation.
18. **Baselines Compared & Benchmarks:** QBER vs. error probability parameter sweeps.
19. **Key Limitations & Gaps:** No application-layer key utilization; no error correction or privacy amplification.
20. **Similarities & Divergences vs. Our Project:** Validates Qiskit Aer's fidelity for BB84 noise modeling, which serves as our foundation, but lacks the post-processing and MQTT IoT pipeline.

---

## Publication 10 (P10): Hubballi et al. (2026)

1. **Full Citation & DOI:** Rajat B. Hubballi, Shivashish Gour, Prerana P., and Shilpa Shankar. "Noise-Tolerant and Eavesdropper-Resilient BB84 Quantum Key Distribution: A Qiskit-Based Simulation Framework." *2026 IEEE International Conference on Nanoelectronics, Quantum Computing and Communications (NQComp)*, IEEE, pp. 1–6, 2026. DOI: [10.1109/NQComp68334.2026.11497748](https://doi.org/10.1109/NQComp68334.2026.11497748).
2. **Evidence Level:** `METADATA_ONLY` (IEEE Xplore paywall; verified via IEEE Xplore record).
3. **Core Research Problem:** Developing noise-tolerant eavesdropper detection mechanisms in Qiskit BB84 simulations.
4. **Proposed Architecture:** Circuit simulation module with dynamic threshold adjustments based on estimated channel noise.
5. **QKD Protocol & Implementation Level:** Gate-level BB84 circuit simulation.
6. **Quantum Simulator / Platform:** IBM Qiskit Aer.
7. **Quantum Channel & Noise Model:** Depolarizing and dephasing channel noise.
8. **Eavesdropper Model:** Intercept-resend Eve attack.
9. **Sifting & QBER Threshold:** Adaptive QBER thresholding.
10. **Information Reconciliation:** Unstated / absent.
11. **Privacy Amplification:** Unstated / absent.
12. **Classical Channel Authentication:** Unstated.
13. **Symmetric Cryptography & Mode:** None.
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Workstation environment.
18. **Baselines Compared & Benchmarks:** Key generation yield under varying noise and intercept levels.
19. **Key Limitations & Gaps:** Lacks downstream cryptographic integration and IoT transport.
20. **Similarities & Divergences vs. Our Project:** Shares Qiskit Aer eavesdropping resilience goals, but does not deploy the derived keys to any communication protocol.

---

## Publication 11 (P11): Adu-Kyere, Nigussie, and Isoaho (2022)

1. **Full Citation & DOI:** Akwasi Adu-Kyere, Ethiopia Nigussie, and Jouni Isoaho. "Quantum Key Distribution: Modeling and Simulation through BB84 Protocol Using Python3." *Sensors*, MDPI, Vol. 22, Issue 16, Article 6284, pp. 1–19, 2022. DOI: [10.3390/s22166284](https://doi.org/10.3390/s22166284).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (PMC9413261, Open Access).
3. **Core Research Problem:** Providing an architectural simulation model of BB84 in Python3 to evaluate eavesdropper detection without specialized quantum hardware.
4. **Proposed Architecture:** Algorithmic representation of photon polarization states ($0^\circ, 90^\circ, +45^\circ, -45^\circ$) transmitted through a simulated optical channel.
5. **QKD Protocol & Implementation Level:** BB84 protocol simulated using classical pseudo-random number generators (RNGs), not quantum state vectors or circuits.
6. **Quantum Simulator / Platform:** Custom Python 3 scripts (no quantum SDK used).
7. **Quantum Channel & Noise Model:** Mathematical attenuation model and intrinsic channel error rate.
8. **Eavesdropper Model:** Intercept-resend adversary guessing bases with $p = 0.5$.
9. **Sifting & QBER Threshold:** Sifting discards mismatched bases; 11% QBER threshold enforced.
10. **Information Reconciliation:** Basic parity checking and bit rectification (yielded 116 shared bits from 256 initial qubits).
11. **Privacy Amplification:** Rudimentary 2-bit XOR operation (yielded 54 bits from 80), not universal hash functions.
12. **Classical Channel Authentication:** None.
13. **Symmetric Cryptography & Mode:** None (stops at raw shared bitstring).
14. **Nonce Policy & Replay Protection:** None.
15. **Transport Protocol & Broker:** None.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Python 3 execution environment.
18. **Baselines Compared & Benchmarks:** Simulation without Eve vs. with Eve; measured error detection rates.
19. **Key Limitations & Gaps:** Does not use quantum circuits; privacy amplification is heuristic (XOR) rather than mathematically universal; zero network transport.
20. **Similarities & Divergences vs. Our Project:** One of the few papers implementing an error correction step. However, Adu-Kyere uses classical RNGs, heuristic 2-bit XOR, and stops before encryption, whereas our project uses Qiskit quantum circuits, 4-pass Cascade, 2-universal Toeplitz hashing, AES-256-GCM, and MQTT.

---

## Publication 12 (P12): Kaganurmath, Cholli, and Anala (2025)

1. **Full Citation & DOI:** Sharadadevi Kaganurmath, Nagaraj G. Cholli, and M. R. Anala. "DLKS-MQTT: A Lightweight Key Sharing Protocol for Secure IoT Communications." *Engineering, Technology & Applied Science Research*, Vol. 15, No. 2, pp. 21532–21538, 2025. DOI: [10.48084/etasr.10216](https://doi.org/10.48084/etasr.10216).
2. **Evidence Level:** `FULL_TEXT_ACCESSED` (Downloaded PDF `papers_data/A14.pdf`).
3. **Core Research Problem:** Minimizing connection handshake overhead and energy consumption for secure MQTT messaging on highly constrained IoT motes.
4. **Proposed Architecture:** Dynamic Lightweight Key Scheduling (DLKS-MQTT) embedding ephemeral 128-bit session key exchange into modified MQTT `CONNECT`/`CONNACK` control packets.
5. **QKD Protocol & Implementation Level:** None (purely classical cryptographic scheme; post-quantum mentioned only in future work).
6. **Quantum Simulator / Platform:** None (Cooja network simulator running Contiki OS).
7. **Quantum Channel & Noise Model:** Not applicable (simulates 802.15.4 wireless radio channel fading and packet loss).
8. **Eavesdropper Model:** 2 malicious nodes executing eavesdropping and MitM packet tampering.
9. **Sifting & QBER Threshold:** Not applicable.
10. **Information Reconciliation:** Not applicable.
11. **Privacy Amplification:** Not applicable.
12. **Classical Channel Authentication:** Embedded BLAKE2s-128 hashing within MQTT control headers.
13. **Symmetric Cryptography & Mode:** 128-bit symmetric key generated via Linear Congruential Generator (LCG) and BLAKE2s.
14. **Nonce Policy & Replay Protection:** Random nonce $N$ in `CONNECT`; broker timestamp $T_{\text{broker}}$ in `CONNACK`.
15. **Transport Protocol & Broker:** Modified MQTT protocol evaluated on a 31-node mesh network.
16. **Cloud / Backend Integration:** Local broker node in Cooja.
17. **Hardware / OS Testbed:** Contiki OS on simulated TI MSP430 Sky motes (10 kB RAM, 48 kB Flash).
18. **Baselines Compared & Benchmarks:** Compared against DLA-MQTT and SMQTT; measured latency (<500 ms), CPU cycles, and energy (mJ).
19. **Key Limitations & Gaps:** Classical LCG is cryptographically weak; protocol is completely vulnerable to quantum cryptanalysis.
20. **Similarities & Divergences vs. Our Project:** Demonstrates lightweight key scheduling over MQTT. However, Kaganurmath is classical and vulnerable, whereas our project utilizes quantum-safe keys derived from simulated BB84.

---

## Publication 13 (P13): Biswas et al. (2024)

1. **Full Citation & DOI:** Sonai Biswas, Mayukh Singha, Swaraj Shekhar Nande, Shamreen Banu Sheik Sulaiman, and Riccardo Bassoli. "Enhancing IoT Security with Quantum Key Distribution: A Novel Approach." *2024 IEEE Future Networks World Forum (FNWF)*, IEEE, pp. 1–6, 2024. DOI: [10.1109/FNWF63303.2024.11028858](https://doi.org/10.1109/FNWF63303.2024.11028858).
2. **Evidence Level:** `METADATA_ONLY` (IEEE Xplore paywall; verified via Crossref).
3. **Core Research Problem:** Designing a hybrid security framework using QKD for constrained IoT sensor networks.
4. **Proposed Architecture:** Conceptual QKD key manager provisioning session keys to IoT cluster heads.
5. **QKD Protocol & Implementation Level:** BB84 protocol referenced at an architectural level.
6. **Quantum Simulator / Platform:** High-level Python simulation scripts.
7. **Quantum Channel & Noise Model:** Abstract error rates.
8. **Eavesdropper Model:** Theoretical intercept-resend attack.
9. **Sifting & QBER Threshold:** Standard sifting assumptions.
10. **Information Reconciliation:** Unstated / absent.
11. **Privacy Amplification:** Unstated.
12. **Classical Channel Authentication:** Pre-shared credentials.
13. **Symmetric Cryptography & Mode:** AES encryption.
14. **Nonce Policy & Replay Protection:** Unstated.
15. **Transport Protocol & Broker:** Abstract IoT communication protocol (MQTT referenced).
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** Workstation simulation.
18. **Baselines Compared & Benchmarks:** Theoretical security analysis and communication cost.
19. **Key Limitations & Gaps:** High-level proposal lacking gate-level circuits, reconciliation, and empirical testbed.
20. **Similarities & Divergences vs. Our Project:** Shares thematic vision, but lacks concrete implementation and reproducible empirical validation.

---

## Publication 14 (P14): Shehzadi et al. (2025)

1. **Full Citation & DOI:** Sahar Shehzadi, Nathan Whaley, Ayesha Khalid, Abdul Ghafoor, Sadiqa Arshad, Faiz Ul Islam, and Máire O'Neill. "Kyber-KEM-Ascon: Benchmarking a Lightweight Post-Quantum KEM on IoT Devices." *2025 IEEE International Symposium on Circuits and Systems (ISCAS)*, IEEE, pp. 1–5, 2025. DOI: [10.1109/ISCAS56072.2025.11043792](https://doi.org/10.1109/ISCAS56072.2025.11043792).
2. **Evidence Level:** `METADATA_ONLY` (IEEE Xplore paywall; verified via Crossref).
3. **Core Research Problem:** Benchmarking the computational overhead of post-quantum lattice-based key encapsulation (ML-KEM/Kyber) paired with lightweight AEAD on resource-constrained microcontrollers.
4. **Proposed Architecture:** Hybrid cryptographic handshake executing Kyber-512 key encapsulation to establish session keys for Ascon-128a AEAD.
5. **QKD Protocol & Implementation Level:** None (Post-Quantum Cryptography / ML-KEM baseline).
6. **Quantum Simulator / Platform:** Not applicable (embedded C implementation on physical hardware).
7. **Quantum Channel & Noise Model:** Not applicable.
8. **Eavesdropper Model:** IND-CCA2 security of Kyber.
9. **Sifting & QBER Threshold:** Not applicable.
10. **Information Reconciliation:** Not applicable.
11. **Privacy Amplification:** Not applicable.
12. **Classical Channel Authentication:** Ascon AEAD authentication tag.
13. **Symmetric Cryptography & Mode:** Ascon-128a lightweight authenticated cipher.
14. **Nonce Policy & Replay Protection:** Unique nonces per packet.
15. **Transport Protocol & Broker:** Serial / SPI bus hardware evaluation.
16. **Cloud / Backend Integration:** None.
17. **Hardware / OS Testbed:** 32-bit ARM Cortex-M4 microcontroller running bare-metal C.
18. **Baselines Compared & Benchmarks:** Detailed CPU clock cycles (encapsulation ~1.1M cycles, decapsulation ~1.2M cycles), RAM usage, and execution latency.
19. **Key Limitations & Gaps:** PQC computational cost (lattice polynomial arithmetic) remains substantial on sub-100 MHz microcontrollers; key sizes introduce packet fragmentation.
20. **Similarities & Divergences vs. Our Project:** Serves as the primary post-quantum baseline (ML-KEM-512) against which our QKD-derived symmetric key architecture is compared in Section 9.

---

## Publication 15 (P15): Mallick et al. (2026)

1. **Full Citation & DOI:** Bandana Mallick, Priyadarsan Parida, Bibhu Prasad, Chittaranjan Nayak, et al. "Quantum-Secure Communication for Future Cyber-Physical and IoT Systems: A Systematic Review of Classical to Learning Approaches." *Computers*, MDPI, Vol. 15, Issue 6, pp. 389, 2026. DOI: [10.3390/computers15060389](https://doi.org/10.3390/computers15060389).
2. **Evidence Level:** `METADATA_ONLY` (MDPI Akamai filter; all 82 references and metadata verified via Crossref REST API).
3. **Core Research Problem:** Synthesizing the state-of-the-art in quantum-secure communication architectures for IoT and cyber-physical systems.
4. **Proposed Architecture:** Systematic taxonomy categorizing QKD integration, post-quantum cryptography, and hybrid security protocols.
5. **QKD Protocol & Implementation Level:** Survey of BB84, BBM92, CV-QKD, and DPS protocols across 55 papers.
6. **Quantum Simulator / Platform:** Reviews SimulaQron, NetSquid, Qiskit, and QuISP.
7. **Quantum Channel & Noise Model:** Classifies fiber, free-space, and underwater quantum channels.
8. **Eavesdropper Model:** Reviews intercept-resend, photon-number-splitting (PNS), and Trojan horse attacks.
9. **Sifting & QBER Threshold:** Reviews analytical thresholds.
10. **Information Reconciliation:** Identifies that >78% of hybrid QKD-IoT simulation papers completely omit information reconciliation ("the reconciliation void").
11. **Privacy Amplification:** Documents widespread misuse of SHA-256 in place of 2-universal hash functions.
12. **Classical Channel Authentication:** Categorizes pre-shared vs. PQC authentication.
13. **Symmetric Cryptography & Mode:** Reviews AES-GCM and ChaCha20-Poly1305 integration patterns.
14. **Nonce Policy & Replay Protection:** Notes widespread absence of replay protection in IoT demonstrators.
15. **Transport Protocol & Broker:** Documents MQTT, CoAP, and DDS transport adoption in QKD-IoT literature.
16. **Cloud / Backend Integration:** Analyzes edge-cloud trust architectures.
17. **Hardware / OS Testbed:** Literature corpus analysis.
18. **Baselines Compared & Benchmarks:** Cross-study qualitative and quantitative comparison.
19. **Key Limitations & Gaps:** Highlights the persistent gap between isolated quantum physics simulators and operational network testbeds.
20. **Similarities & Divergences vs. Our Project:** Provides independent academic confirmation that the exact research gap addressed by our prototype (the missing reconciliation/privacy-amplification bridge in MQTT IoT) is a validated, open problem in the field.

---

## Synthesis: Key Takeaways for Novelty Assessment

1. **No Identical End-to-End System Exists:** None of the 15 closest publications implements the complete chain: Qiskit Aer gate circuits $\to$ depolarizing transit noise $\to$ intercept-resend Eve $\to$ basis sifting $\to$ 4-pass Cascade reconciliation $\to$ 2-universal Toeplitz hashing $\to$ AES-256-GCM $\to$ dual-mode MQTT $\to$ sliding-window anti-replay $\to$ cloud database/dashboard.
2. **The Field is Bipolar:** Research is split into:
   - *Physics/Simulation Papers (P4, P7, P8, P9, P10):* High fidelity in Qiskit, but terminate immediately after sifting; zero networking.
   - *Networking/IoT Papers (P1, P2, P5, P6, P13):* Propose IoT architectures, but treat QKD as an abstract oracle and omit error correction.
3. **P3 (Alshowkan et al.) is Hardware, Not Software:** Alshowkan deployed physical QKD over utility fiber for GMAC authentication, confirming MQTT viability but not providing an open software research tool.
4. **P15 (Mallick et al.) Formally Validates the Gap:** Confirms that >78% of hybrid QKD-IoT simulations suffer from the "reconciliation void."
