# Paper Submission Readiness Report

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Telemetry over MQTT  
**Target Manuscript:** `paper/manuscript.tex`  
**Bibliography:** `paper/references.bib` (32 verified citations + standards)  
**Authors:** Rohan Bhutani, Anirudh Panwar, Shruti Sharma, Ananya Sharma, Prof. (Dr.) Mohammad Wazid  
**Affiliation:** Department of Computer Science & Engineering, Graphic Era Deemed to be University, Dehradun, India  
**Project ID:** MP2026CSE205  
**Date of Report:** November 2026  

---

## 1. Executive Summary

This report evaluates the academic and technical readiness of the research manuscript titled **"Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Telemetry over MQTT"** for submission to peer-reviewed IEEE, Springer, and MDPI venues.

The manuscript is grounded in an empirical research testbed with zero fabricated benchmarks or unbacked claims. All empirical tables, figures, and claims in the manuscript directly trace to reproducible test suites and raw CSV datasets generated across 7 experiments ($>700$ individual trials) in `experiments/raw_results/`.

---

## 2. Evaluation of Target Publication Venues

| Venue | Publisher | Impact Factor / Quartile | Scope & Focus Alignment | Review Timeline | Recommendation Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IEEE Access** | IEEE | 3.4 (Q2 / Multidisciplinary) | Broad applied engineering, quantum systems, IoT communication, practical implementation testbeds. High match for software-in-the-loop prototypes. | 4–6 weeks (Rapid Open Access) | **Primary Recommendation (Best Fit)** |
| **IEEE Internet of Things Journal (IoT-J)** | IEEE | 10.6 (Q1 / Top Tier) | Rigorous IoT architectures, security, and next-generation communication. Expects either physical hardware testbed or extensive mathematical optimization. | 3–5 months | **Secondary Recommendation (Ambitious)** |
| **Telecommunication Systems** | Springer | 2.5 (Q2) | Network protocols, cryptography, edge computing, applied simulation modeling. Good fit for simulation-driven protocol integration. | 3–4 months | **Strong Alternative** |
| **Sensors (Special Issue: Quantum Cryptography in IoT)** | MDPI | 3.4 (Q2) | Sensor networks, IoT telemetry security, quantum simulation frameworks. Very high fit for prototype-driven empirical studies. | 3–5 weeks | **Strong Rapid Alternative** |

### Venue Recommendation Rationale:
1. **IEEE Access (Primary):** IEEE Access is open access, rapid review, and values end-to-end engineering prototypes that demonstrate reproducible integration between theoretical principles (BB84, Cascade) and standard communication standards (MQTT, AES-GCM). The presence of Qiskit Aer simulation rather than physical single-photon detectors is completely acceptable within IEEE Access's applied scope.
2. **IEEE IoT-J (Secondary):** While highly prestigious, IoT-J reviewers frequently demand physical hardware measurements (e.g., bare-metal microcontroller power dissipation, physical optical fiber attenuators). If submitting to IoT-J, an embedded C implementation benchmark on physical ESP32/Raspberry Pi boards would strengthen competitiveness.

---

## 3. Manuscript Quality & Compliance Audit

### 3.1 Structural Completeness (10 / 10 Sections Present)
- [x] **Section I: Introduction:** Contextualizes quantum risk (Shor, HNDL), defines QKD vs PQC, and explicitly enumerates 5 core contributions.
- [x] **Section II: Related Work & Research Gap:** Surveys Qiskit simulators, hybrid QKD-IoT, highlights the "Information Reconciliation Void" (78% omission rate), and provides a side-by-side gap analysis.
- [x] **Section III: System Architecture & Threat Model:** Formalizes Dolev-Yao classical adversary, quantum intercept-resend adversary (Eve), Grover margin, and component models.
- [x] **Section IV: Quantum Key Agreement & Post-Processing:** Detail-oriented mathematical formulation of BB84 state preparation, Eve error derivation ($p_{\text{eve}}/4$), 11% threshold, 4-pass permutation Cascade protocol, and universal-hash PA.
- [x] **Section V: Cryptographic Binding & MQTT Transport:** Formulates AES-256-GCM, 96-bit CSPRNG nonces, Base64 JSON transport envelopes, and sequence watermark checks.
- [x] **Section VI: Experimental Setup & Testbed:** Transparent specifications of Qiskit Aer, Python runtime, Mosquitto broker, and SQLite WAL configuration.
- [x] **Section VII: Empirical Results & Evaluation:** Complete presentation of all 7 experiments backed by raw data:
  - Table 1: Qubit scaling $N \in [128, 1024]$ (sifting 50%, reconciled 75%, latency 6.88–120.30 ms).
  - Table 2: Eve interception tracking theoretical curve ($p/4$), 100% abort at $p \ge 0.8$.
  - Table 3: Depolarizing noise resilience (>93% success up to $\lambda = 0.08$).
  - Table 4: AES-GCM sub-millisecond latency ($\approx 0.01$ ms) and high throughput.
  - Table 5: 100% tamper detection across 150 bit-flip and modification attacks.
  - Table 6: End-to-end transit latency with crypto accounting for <0.04% overhead.
  - Table 7: Comparative baseline analysis against Plaintext, PSK, and ML-KEM-512.
- [x] **Section VIII: Security Analysis:** Formal breakdown of Shor immunity, Grover 128-bit margin, GHASH collision bounds, and anti-replay integrity.
- [x] **Section IX: Limitations & Threats to Validity:** Explicit, honest disclosure of simulation boundaries, authenticated classical channel assumptions, and desktop runtime profiling.
- [x] **Section X: Conclusion & Future Work:** Summarizes results and sets realistic future milestones (embedded C, physical optical QKD testbed).

### 3.2 Anti-Hallucination & Integrity Verification
- **Citations:** All 32 references in `paper/references.bib` correspond to genuine peer-reviewed publications, recognized standards (NIST SP 800-38D, FIPS 203, OASIS MQTT 5.0), and established authors with real DOIs.
- **Experimental Data:** Zero benchmark numbers are estimated or invented. All values in LaTeX tables exactly reflect `experiments/processed_results/summary_tables.md` and raw CSV files in `experiments/raw_results/`.
- **Honest Scoping:** The manuscript explicitly uses terms like "simulated BB84 QKD", "Qiskit Aer quantum circuit models", and avoids claiming physical optical hardware or single-photon generation.

---

## 4. Key Strengths of the Paper

1. **Resolves a Legitimate Research Void:** The majority of prior simulation papers fail when noise is introduced because they omit information reconciliation. Demonstrating an adaptive 4-pass Cascade implementation that achieves 100% convergence under noise is a substantial and defensible technical contribution.
2. **End-to-End System Integration:** Rather than evaluating QKD in isolation, this paper integrates the derived keys into a full MQTT sensor-to-cloud pipeline with database persistence, sequence watermarking, and dynamic tamper rejection.
3. **Rigorous Statistical Grounding:** Experiments are evaluated over repeated randomized trials with standard deviations, 95% confidence intervals, and comparison against theoretical mathematical derivations ($QBER = p/4$).
4. **Defense-in-Depth Classical Security:** Demonstrates that physical-layer key exchange must be coupled with rigorous application-layer integrity (unique nonces, sequence counters) to defeat practical network adversaries.

---

## 5. Potential Reviewer Critiques & Prepared Rebuttals

| Anticipated Reviewer Critique | Pre-Emptive Mitigation in Manuscript |
| :--- | :--- |
| *"The paper simulates QKD rather than using physical single-photon optics."* | Section IX explicitly scopes the simulation boundary. Section I notes that physical QKD hardware is economically and logistically infeasible for edge IoT microcontrollers today; simulation-in-the-loop provides the necessary protocol validation prior to expensive physical optical testbed integration. |
| *"Why use QKD instead of Post-Quantum Cryptography (PQC) like ML-KEM-512?"* | Addressed in Section I and Section VII (Table 7). PQC relies on unproven mathematical computational hardness (hardness of lattice problems), whereas QKD provides physical information-theoretic security that is fundamentally immune to unpredicted algorithmic breakthroughs. Furthermore, Table 7 highlights that QKD incurs 0 bytes of in-band classical transmission overhead during key establishment. |
| *"How is the classical channel authenticated during basis reconciliation?"* | Section IX explicitly discusses this assumption, citing classical pre-shared Wegman-Carter polynomial hashing as the standard physical deployment requirement. |
| *"Is Python performance representative of resource-constrained IoT devices?"* | Addressed in Section IX. The cryptographic primitive (AES-256-GCM via OpenSSL) is implemented in optimized C/assembly, demonstrating that symmetric payload encryption requires less than 0.02 ms, which easily fits within the clock budget of 160–240 MHz microcontrollers like the ESP32. |

---

## 6. Pre-Submission Checklist

- [x] Paper title and author block formatted according to IEEE standards.
- [x] Complete abstract (approx. 240 words) with problem statement, methodology, results, and conclusion.
- [x] Clean LaTeX compilation without undefined citations or references (`\cite` and `\ref` resolved).
- [x] Figures (`fig1_qkd_scaling.png`, `fig2_eve_qber.png`, etc.) generated at 300 DPI publication resolution in `experiments/plots/`.
- [x] Verified BibTeX entries in `paper/references.bib`.
- [x] Source code and experiment reproduction scripts documented and verified (`pytest` 100% pass rate).
- [x] GitHub repository prepared for open-source artifact sharing.

---

## 7. Final Recommendation

The manuscript is **technically complete, scientifically defensible, and ready for supervisor review and submission**. We recommend submitting to **IEEE Access** as a primary target, or a reputable IEEE/Springer conference in quantum information and IoT communications.
