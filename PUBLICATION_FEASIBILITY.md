# Publication Feasibility and Journal Target Evaluation
## Rigorous Venue Audit for Hybrid BB84 QKD, AES-256-GCM, and MQTT IoT Telemetry

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Role:** Senior Academic Publishing Advisor / Peer Reviewer  
**Date:** November 2026  
**Objective:** Provide an honest, fact-based assessment of publication feasibility across leading peer-reviewed journals and conferences, identifying actual scopes, acceptance standards for software-only simulations, review expectations, and fatal rejection triggers.

---

## Executive Summary: Publishing a Software QKD-IoT Simulation

A critical hurdle facing this project is that **purely software-simulated QKD papers occupy a precarious position in the academic literature**:
1. **Pure Physics / Quantum Hardware Journals (e.g., Physical Review Applied, Optica):** Will **immediately desk-reject** this work because it does not implement physical optical hardware (lasers, single-photon detectors, fiber spools, or quantum photonic integrated circuits).
2. **Pure Theoretical Quantum Information Journals (e.g., IEEE Transactions on Information Theory):** Will **reject** this work because the quantum protocols (BB84, Cascade, Leftover Hash Lemma) are established theory; no new mathematical security proof is developed.
3. **Applied Systems, IoT, and Computer Communications Journals (e.g., IEEE Access, MDPI Sensors, Springer Telecommunication Systems):** Are **receptive** to software simulation architectures, provided the paper is framed as an **end-to-end communication systems engineering, performance characterization, and comparative benchmarking study**, rather than a claim of a new quantum cipher.

---

## Venue-by-Venue Audit

---

### Venue 1: IEEE Access

* **Publisher:** IEEE  
* **Format:** Open Access, Rapid Review  
* **Scope & Subject Focus:** Broad multidisciplinary engineering, telecommunications, applied cybersecurity, IoT, software architectures, and simulation frameworks.  
* **Receptivity to Simulation-Only Work:** **High.** IEEE Access routinely publishes end-to-end software simulation architectures, testbed implementations, and empirical benchmark evaluations using tools like Qiskit, NS-3, and Cooja.  
* **Reviewer Expectations:**
  - Complete, end-to-end system architecture with reproducible software flow.
  - Rigorous empirical evaluation across multiple parameters (varying noise levels, block sizes, message rates).
  - Concrete comparison against classical and post-quantum baselines (e.g., PSK, ECDH, ML-KEM).
  - Fully accessible code repository and dataset.
* **Common Rejection Triggers:**
  - Inflated novelty claims (e.g., claiming to "invent a new QKD protocol").
  - Lack of comparative baselines or evaluation under ideal/zero-noise channels only.
  - Insufficient sample sizes (e.g., single trial runs without confidence intervals).
* **Estimated Review Timeline:** 4 to 8 weeks from submission to first decision.  
* **Article Processing Charge (APC):** ~$1,995 USD (mandatory open-access fee upon acceptance).  
* **Feasibility Rating:** **VERY HIGH (8.5 / 10)** — *Recommended Primary Target for Fast, High-Visibility Publication.*

---

### Venue 2: IEEE Internet of Things Journal (IEEE IoT-J)

* **Publisher:** IEEE  
* **Format:** Hybrid (Open Access / Traditional Subscription)  
* **Scope & Subject Focus:** Premier journal for IoT architectures, communication protocols, edge-cloud systems, sensor networks, and IoT security.  
* **Receptivity to Simulation-Only Work:** **Moderate to Low for pure simulation; Moderate to High if supported by extensive comparative analysis and realistic network emulation.**  
* **Reviewer Expectations:**
  - Deep system-level contribution with realistic network layer modeling (packet loss, latency distributions, bandwidth limits, channel jitter).
  - Explicit physical or edge hardware validation (e.g., executing the IoT client on real Raspberry Pi, ESP32, or STM32 hardware).
  - Direct comparative benchmarking against state-of-the-art IoT security standards (NIST ML-KEM, DTLS 1.3).
* **Common Rejection Triggers:**
  - "Simulation toy model" criticism: reviewers dismissing standalone Python scripts as detached from physical IoT realities.
  - Lack of hardware deployment (reviewers will ask: *"Why was this not tested on an actual microcontroller?"*).
  - Incremental pipeline combination without novel protocol design.
* **Estimated Review Timeline:** 3 to 6 months for first decision; 2 to 3 rounds of review.  
* **APC / Publishing Cost:** Optional Open Access (~$2,495 USD); $0 under traditional subscription publishing.  
* **Feasibility Rating:** **MODERATE (5.0 / 10)** — *Feasible only if the paper is extended with embedded hardware measurements (Raspberry Pi client) and Direction 3 (ML-KEM vs. QKD comparison).*

---

### Venue 3: IEEE Transactions on Quantum Engineering (IEEE TQE)

* **Publisher:** IEEE  
* **Format:** Open Access  
* **Scope & Subject Focus:** Applied quantum engineering, quantum software stacks, quantum communication protocols, and simulation platforms.  
* **Receptivity to Simulation-Only Work:** **Moderate.** TQE accepts software simulators and architectural studies, but requires rigorous quantum state fidelity modeling.  
* **Reviewer Expectations:**
  - Deep exploration of quantum channel impairments (detector dark counts, multi-photon emission, depolarizing channels, decoherence times).
  - Rigorous finite-key security proofs matching quantum information theory standards.
  - Clear demonstration of how the quantum engineering stack interfaces with classical hardware.
* **Common Rejection Triggers:**
  - Superficial treatment of quantum mechanics (e.g., treating Qiskit as an opaque black box).
  - Oversimplified noise models (e.g., ignoring phase-flip vs. bit-flip asymmetry in fiber channels).
  - Lack of formal quantum information theory rigor in privacy amplification.
* **Estimated Review Timeline:** 2 to 4 months for first decision.  
* **APC / Publishing Cost:** ~$1,995 USD (IEEE Open Access).  
* **Feasibility Rating:** **MODERATE-LOW (4.5 / 10)** — *Reviewers may feel the quantum part is standard BB84 and the networking part belongs in an IoT journal.*

---

### Venue 4: Quantum Information Processing (QIP)

* **Publisher:** Springer  
* **Format:** Hybrid (Subscription / Optional Open Access)  
* **Scope & Subject Focus:** Theoretical and applied quantum information, quantum cryptography, quantum algorithms, and quantum network protocols.  
* **Receptivity to Simulation-Only Work:** **Moderate.** Published Mehić et al. (NS-3 QKD module), but heavily favors theoretical and analytical contributions.  
* **Reviewer Expectations:**
  - Mathematical depth in security proofs, key generation rate derivations, and error-correction performance.
  - Detailed analysis of information leakage during reconciliation ($\text{leak}_{\text{EC}}$).
  - Analytical formulas validated by simulation.
* **Common Rejection Triggers:**
  - "Primarily a classical IoT software paper" — reviewers will argue that MQTT, SQLite, and Flask dashboards are classical computing topics outside QIP's core quantum physics scope.
* **Estimated Review Timeline:** 3 to 6 months.  
* **APC / Publishing Cost:** $0 under subscription option; ~$3,390 USD for open access.  
* **Feasibility Rating:** **LOW-MODERATE (4.0 / 10)** — *Unlikely to find enthusiastic reviewers unless refocused entirely on Direction 2 (Cascade reconciliation leakage profiling).*

---

### Venue 5: MDPI Sensors (Section: Internet of Things / Cyber-Physical Systems)

* **Publisher:** MDPI  
* **Format:** Gold Open Access  
* **Scope & Subject Focus:** Smart sensors, IoT communications, sensor security, applied cryptography for telemetry, and simulation testbeds.  
* **Receptivity to Simulation-Only Work:** **High.** Published Adu-Kyere et al. (2022) and dozens of hybrid QKD-IoT simulation prototypes.  
* **Reviewer Expectations:**
  - Clear architectural diagrams and transparent software workflows.
  - Reproducible experimental results with clear performance metrics (latency, throughput, QBER).
  - Analysis of sensor data integrity, replay resistance, and encryption overhead.
* **Common Rejection Triggers:**
  - Poor formatting, unclear diagrams, or broken reference chains.
  - Insufficient experimental sweeps or missing error bars.
* **Estimated Review Timeline:** 16 to 28 days from submission to first decision (very rapid).  
* **APC / Publishing Cost:** ~2,600 CHF (~$2,950 USD).  
* **Feasibility Rating:** **HIGH (8.0 / 10)** — *Very high probability of acceptance with rapid turnaround, but requires institutional APC funding.*

---

### Venue 6: Springer Telecommunication Systems

* **Publisher:** Springer Nature  
* **Format:** Hybrid (Subscription / Optional Open Access)  
* **Scope & Subject Focus:** Telecommunication protocols, network security, performance evaluation of communication systems, and IoT networking.  
* **Receptivity to Simulation-Only Work:** **High.** Welcomes detailed performance evaluation and comparative analysis of network protocols over simulators like Mosquitto, NS-3, and OMNeT++.  
* **Reviewer Expectations:**
  - Comprehensive network-layer performance characterization (latency, queuing, throughput, jitter).
  - Solid comparative analysis against classical communication protocols.
  - Mathematically sound threat and security analysis.
* **Common Rejection Triggers:**
  - Lack of sufficient network performance depth (e.g., measuring only single-client latency without multi-packet queuing).
* **Estimated Review Timeline:** 3 to 5 months.  
* **APC / Publishing Cost:** **$0 (Zero publishing cost under traditional subscription mode)**.  
* **Feasibility Rating:** **HIGH (7.5 / 10)** — *Best zero-cost hybrid journal target for this project.*

---

### Venue 7: Premier Peer-Reviewed IEEE Conferences

* **Examples:**
  - **IEEE World Forum on Internet of Things (WF-IoT)**
  - **IEEE International Conference on Communications (ICC)**
  - **IEEE Global Communications Conference (GLOBECOM)**
  - **IEEE Future Networks World Forum (FNWF)** (published Biswas et al. 2024)
  - **IEEE WPMC** (published Farooq et al. 2024)
* **Format:** Conference Proceedings (Indexed in IEEE Xplore, Scopus, Web of Science).  
* **Receptivity to Simulation-Only Work:** **Very High.** Prototype demonstrators, architecture proposals, and preliminary benchmarking are standard fare.  
* **Reviewer Expectations:** 5 to 6 page concise manuscript adhering strictly to IEEE two-column format, clear problem statement, clean plots, and focused experimental evaluation.  
* **Acceptance Rate:** Typically 35% to 45% for specialized tracks.  
* **Feasibility Rating:** **EXCELLENT (9.0 / 10)** — *Ideal venue for initial peer-reviewed dissemination and graduation defense.*

---

## Strategic Publication Roadmap & Recommendation

```
[ Current Implementation: EXP-BATCH-2 & 18 Tests Passing ]
                           │
                           ▼
          [ Decision Gate: Funding vs. Cost ]
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   [ APC Funding Available ]        [ Zero-Cost Required ]
   Target: IEEE Access              Target: Springer Telecomm. Systems
   (or MDPI Sensors)                (or IEEE Conference: WF-IoT / ICC)
          │                                 │
          ▼                                 ▼
   Acceptance Prob: ~85%            Acceptance Prob: ~75%
   Review Time: 4-6 Weeks           Review Time: 3-5 Months
   Cost: ~$1,995 USD                Cost: $0 USD
```

### Strategic Recommendations:
1. **Primary Recommendation (Funded): IEEE Access.**  
   Frame the paper as: *"An Open-Source End-to-End Quantum-Safe IoT Telemetry Testbed: Connecting Qiskit Aer BB84 with Reconciled AES-256-GCM over MQTT."* This directly fits the journal's systems and software engineering profile.
2. **Primary Recommendation (Zero-Cost / Self-Funded): Springer Telecommunication Systems OR an IEEE Conference (e.g., IEEE WF-IoT).**  
   Publishing under the subscription model incurs zero page charges or APCs while securing a prestigious, indexed citation.
3. **Manuscript Framing Must Avoid:**
   - Any claim of a "novel quantum cryptography algorithm" (immediate rejection).
   - Any implication of physical quantum hardware (desk rejection).
   - Any silence on ML-KEM/Kyber (reviewers will immediately ask why PQC was not considered).
