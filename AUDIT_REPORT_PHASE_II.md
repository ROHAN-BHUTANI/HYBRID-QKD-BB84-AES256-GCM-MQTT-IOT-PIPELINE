# INDEPENDENT RESEARCH & DOCUMENTATION AUDIT REPORT

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Target Program:** B.Tech Major Project (2026–2027), Department of Computer Science & Engineering, MSIT (Affiliated to GGSIPU, New Delhi)  
**Audit Date:** 29 October 2026  
**Auditor:** Antigravity Autonomous Research & Verification Agent  
**Documents Audited:**
1. `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Working Research Dossier, 29 Oct 2026)
2. `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx` (Literature Screening & Evidence Matrix, Round 1, 29 Oct 2026)
3. `Synopsis_BB84_QKD_AES_IoT.docx` (Original Approved Phase I Project Synopsis, Sept 2026)
4. Project Workspace: `c:\Users\bhuta\Desktop\Major_Project(2027)`

---

## EXECUTIVE AUDIT SUMMARY & RESEARCH GATE DECISION

### Gate Determination: **C. RESEARCH GATE FAILED — Additional Investigation or Redesign is Necessary**

> **GATE STATUS: FAILED (EXECUTION BLOCKED)**  
> Prototype implementation MUST NOT commence. The current documentation exhibits foundational flaws, unverified literature claims, critical cryptographic inconsistencies, and completely absent systems engineering artifacts (PRD, SRS, DFDs, and Traceability Matrix). Approving this baseline in its present state would result in building a software prototype whose core cryptographic pipeline breaks under realistic channel noise, whose research gap is unproven against recent 2026 literature, and whose academic novelty claims collapse upon full-text inspection.

### Key Gate Breaches Summary
1. **Missing Core Engineering Artifacts:** The workspace contains **zero** formal PRD, **zero** formal SRS, **zero** Data Flow Diagrams (DFDs) (the synopsis contains literally `[Fig. 4.1: System Architecture Diagram — To be included]`), and **zero** Requirements Traceability Matrix (RTM).
2. **Unverified Literature & Abstract Reliance:** Of the 30 candidate sources, **none** of the contemporary simulation or integration papers have been examined in full text. The entire literature defense relies on publisher abstracts and highlights for 2021–2026 works. Standards are conflated with research papers.
3. **High Overlap / Unvalidated Novelty:** Closest 2026 literature (Das et al., Fiorini et al., IEEE NQComp 2026, Sharma & Kumar 2021) directly investigates Qiskit BB84 simulation under noise, intercept-resend, and threshold detection. No side-by-side comparison matrix exists to substantiate that the proposed work is not already demonstrated.
4. **Fatal Cryptographic Pipeline Flaw:** The proposed pipeline sifts bits in Qiskit, performs QBER sampling, and directly hashes the remaining sifted bits using SHA-256 to produce an AES-256 key without Information Reconciliation (Error Correction). In the presence of any channel noise ($QBER > 0$), Alice's and Bob's remaining sifted bits will differ by even a single bit, causing SHA-256 to produce completely disparate 256-bit keys. Bob will fail AES-GCM tag verification on **100% of received payloads**.
5. **Architectural Contradictions with Synopsis:** The original synopsis claims physical quantum security, claims Shor's algorithm breaks AES-256, specifies a fixed 11% QBER threshold assuming zero noise, and claims "first-ever" hybrid integration. The Phase II dossier contradicts all of these, retreating to an educational simulation, but without formal supervisor approval or an updated baseline specification.

---

## SECTION I: DIRECT RESPONSES TO THE 17 AUDIT QUESTIONS

### 1. Have at least 30 eligible research papers been verified?
**Finding:** **NO.**
- **Evidence:** While `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` Section 4 compiles a bibliography of 30 items, it explicitly admits: *"This is a working research dossier—not yet a fully screened systematic review. The 30-item corpus should be verified against full texts before being described in a paper as 30 studies reviewed in depth"* (Dossier, lines 10, 26).
- Furthermore, several items in the 30-item list are technical standards and specifications rather than eligible peer-reviewed research papers:
  - Reference [12]: OASIS MQTT Version 5.0 Standard (2019)
  - Reference [13]: NIST SP 800-38D (GCM/GMAC Standard, 2007)
  - Reference [20]: NIST FIPS 203 (ML-KEM Standard, 2024)
- In `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx`, only 13 priority sources (A1–A13) were even compiled for screening, and the document notes in Section 9: *"Retrieve full text and complete extraction for the 13 priority sources above... Build the final 30-paper matrix with source verification status."*

### 2. How many have been examined in full text?
**Finding:** **At most 3 of the 30 sources (and 0 of the recent simulation/integration papers).**
- **Evidence:** In `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx` Section 3, all priority modern research papers have their evidence explicitly qualified as derived from abstracts or publisher highlights:
  - Source A4 (Das et al., 2026): *"Evidence from publisher abstract"*
  - Source A5 (IEEE 2026 NQComp): *"Evidence from IEEE abstract"*
  - Source A6 (Fiorini et al., 2026): *"Evidence from publisher abstract"*
  - Source A7 (Khan et al., 2026): *"Evidence from abstract"*
  - Source A8 (Chawla & Mehra, 2023): *"Evidence from abstract"*
  - Source A9 (Babu et al., 2024): *"Evidence from publisher highlights"*
  - Source A10 (Adere et al., 2026): *"Evidence from publisher page"*
  - Source A13 (MDPI Computers 2026): *"Need: read full text and compare its included-study categories to our scope"* (Matrix, line 112).
- Only foundational public documents (Bennett & Brassard 1984 [A1], NIST SP 800-38D [A11], NIST FIPS 203 [A12]) were accessible in full text during this pass. Zero full texts of the peer-reviewed Qiskit or IoT QKD papers have been extracted.

### 3. Which important conclusions rely only on abstracts?
**Finding:** **Virtually all core scoping and research-gap conclusions in the project rely exclusively on abstracts:**
1. **The Feasibility and Non-Novelty of QBER Thresholding:** The decision in Dossier Section 3 (Cluster 5) and Matrix Section 3 (A6) that the project cannot claim a novel QBER threshold algorithm relies solely on the ScienceDirect abstract of Fiorini et al. (2026). The authors do not know the mathematical model, assumptions, or code used by Fiorini et al.
2. **The Redundancy of Noisy Qiskit Simulation:** The conclusion that *"a simple noisy-BB84 QBER plot alone is unlikely to differentiate our work"* (Matrix, line 58) relies entirely on the short publisher abstracts of Das et al. (2026) and IEEE NQComp (2026).
3. **The Exclusion of PNS Attacks:** The decision to exclude Photon Number Splitting (PNS) attacks from the threat model (Matrix, line 76) is justified solely by referencing the abstract of Khan et al. (2026).
4. **The Definition of Candidate Gap G1 (End-to-End Integration):** The primary surviving claim—that no one has benchmarked the end-to-end integration of Qiskit BB84, AES-GCM, and MQTT—is an inference drawn because abstracts of related papers did not explicitly mention MQTT. Without reading full-text experimental setups, the team cannot know if similar testbeds were implemented.

### 4. Have the closest existing QKD–IoT systems been compared directly?
**Finding:** **NO.**
- **Evidence:** Neither document contains a direct, feature-by-feature or quantitative comparison matrix benchmarking the proposed architecture against prior QKD-IoT implementations:
  - Sharma & Kumar (2021) (*"BB84 QKD protocol simulation for IoT security using Python"*), cited as primary prior work in Synopsis Section 2.4 [9], was completely dropped from the Dossier and Evidence Matrix! It was neither retrieved nor compared.
  - Mehic et al. (2017) (*"Implementation of quantum key distribution network simulation module in NS-3"*), cited in Synopsis [8] and Dossier [15], is included only with a raw Google Scholar search URL and has no architectural comparison.
  - Matrix Section 8 (line 148) admits: *"Whether the paper can claim a specific research gap. This requires a side-by-side comparison of the closest prior systems... Only then finalize the research gap and write the Phase II implementation specification"* (Matrix, line 160).

### 5. Is the selected research gap supported by the literature?
**Finding:** **NO. It is currently an unvalidated candidate hypothesis.**
- **Evidence:** Both documents explicitly warn that the gap is not yet supported:
  - Dossier Table 2: *"Not supported as a gap yet: 'No one has combined QKD, AES and IoT' or 'first-ever hybrid system.' Cannot be asserted from a quick search; recent closely related studies exist. Require systematic search and explicit comparison table before making novelty claims."*
  - Matrix Table 2: *"Not supported yet: 'No previous system has combined BB84, AES-GCM, MQTT and a cloud receiver.' This needs targeted full-text searching and a comparison matrix."*
- Merely connecting standard Python libraries (`qiskit`, `cryptography`, `paho-mqtt`, `flask`) is a software engineering integration task, not an automatic academic research gap. Unless the integration investigates an unaddressed scientific trade-off, performance bottleneck, or failure mode under rigor, it lacks peer-reviewed contribution.

### 6. Could the proposed contribution already have been demonstrated by a closely related paper?
**Finding:** **YES. There is an extremely high risk of prior demonstration.**
- **Evidence:**
  - *Qiskit BB84 Simulation with Noise & Intercept-Resend:* Already published by Das et al. (Physica Scripta, 2026) and IEEE NQComp (2026).
  - *Threshold-Based Eavesdropper Detection under Noise:* Already published by Fiorini, Garroppo & Pagano (Computer Networks, 2026).
  - *Python BB84 Prototyping:* Published in Informatica (2026).
  - *Software-Simulated BB84 for IoT:* Already published by Sharma & Kumar (2021).
  Because none of these full texts were read, the team cannot verify whether an end-to-end MQTT pipeline or similar benchmark was already evaluated in their experimental sections or appendices.

### 7. Are all major security assumptions explicit?
**Finding:** **NO. Several foundational assumptions are missing, implicit, or invalid:**
1. **Classical Channel Authentication (Man-in-the-Middle):** BB84 strictly requires that the classical sifting channel be authenticated (e.g., via Wegman-Carter authentication using an initial pre-shared key). Without this, Eve can execute an undetectable active Man-in-the-Middle attack. The design neither specifies nor implements classical channel authentication.
2. **Entity Allocation & QKD Node Topology:** In Synopsis Section 4.1, "Module A (Quantum Key Generator)" is described as a standalone component generating a key for Module B (IoT Client) and Module C (Cloud Server). If an external entity generates and distributes keys over classical networks, it is a classical Key Distribution Center (KDC), completely invalidating QKD principles. If Alice is the IoT node and Bob is the Cloud, the architecture fails to state how a memory/CPU-constrained IoT node can run IBM Qiskit.
3. **Key Storage & Memory Security:** Neither the synopsis nor the dossier states assumptions regarding key persistence, memory zeroization, or protection against side-channel/cold-boot attacks on the edge device or cloud server.

### 8. Is the BB84 key-processing method technically justified?
**Finding:** **NO. It is technically flawed and cryptographically invalid under realistic conditions.**
- **Evidence:** The proposed pipeline sifts bits, samples QBER, and directly hashes the remaining sifted bits using SHA-256 to create an AES-256 key (Synopsis Section 4.2, lines 114–118).
- **The Fatal Flaw:** The design completely omits **Information Reconciliation (Error Correction)**, such as the Cascade or Winnow algorithms:
  - In any physical or noisy simulated channel, Alice's and Bob's sifted bitstrings will differ by the channel error rate (e.g., 2%–5% QBER).
  - If Alice and Bob hash bitstrings containing even a single differing bit into SHA-256, the avalanche effect ensures their resulting 256-bit AES keys will be **completely different and uncorrelated**.
  - Bob will be unable to decrypt Alice's AES-GCM payloads; tag validation will fail on 100% of packets whenever noise is present.
  - The prototype can therefore only function when $QBER \equiv 0\%$ (an unphysical, noiseless simulation).
- Furthermore, hashing with SHA-256 is **not privacy amplification**. Privacy amplification requires 2-universal hashing where output length is compressed based on Renyi entropy bounds ($l \le n[1 - h(QBER)] - leak_{EC}$).

### 9. Are the SHA-256 and AES-256-GCM assumptions correct?
**Finding:** **PARTIALLY INCORRECT.**
1. **SHA-256 Entropy Fallacy:** The assumption that hashing arbitrary remaining sifted bits with SHA-256 produces a "256-bit cryptographically secure key" is mathematically false. If the sifted string contains 180 bits of min-entropy, hashing it produces a 256-bit digest with at most 180 bits of security. SHA-256 cannot create entropy.
2. **Shor's Algorithm Fallacy in Synopsis:** Synopsis Section 1 (line 36) asserts: *"Classical encryption algorithms such as AES-256, while currently robust, face a long-term existential threat from the advancement of quantum computing. Shor's algorithm... can break RSA and ECC...".* Shor's algorithm only breaks asymmetric primitives based on integer factorization and discrete logarithms. AES-256 is symmetric; it is affected only by Grover's algorithm, which reduces its effective brute-force security to 128 bits—still impregnable.
3. **AES-GCM Nonce Discipline Unspecified:** GCM catastrophically fails if a 96-bit nonce is ever repeated under the same key. The documentation specifies no nonce generation protocol (counter vs. CSPRNG), state persistence across reboots, or key-rekeying schedule.

### 10. Is the classical baseline clearly defined?
**Finding:** **NO.**
- **Evidence:**
  - The original synopsis defines **no** classical baseline whatsoever (Synopsis Table 2).
  - Dossier Section 3 (Cluster 6) and Table 3 propose a baseline consisting of *"Pre-shared test key + AES-GCM + MQTT"*.
  - A pre-shared static key baseline has **zero** key-establishment runtime. Comparing a heavy Python simulation (Qiskit quantum circuit compilation) against a static hardcoded key does not benchmark key exchange; it compares running code against doing nothing.
  - To be scientifically meaningful, the baseline must be an established classical or post-quantum key-establishment protocol: ECDH (X25519) / TLS 1.3 or NIST FIPS 203 (ML-KEM-512). The dossier treats ML-KEM as merely "optional" and defers its decision.

### 11. Are all research questions measurable?
**Finding:** **PARTIALLY. Only RQ1 and RQ2 are measurable research questions; RQ3 is a unit test, and RQ4 is unrelated to QKD.**
- **RQ1 (Latency/Resource Overhead):** Measurable, but compromised because the classical baseline is currently undefined and measuring Qiskit simulation execution time measures classical CPU matrix math, not QKD protocol physics.
- **RQ2 (Noise, Eve, and Detection/False-Alarm Rates):** Fully measurable via Monte Carlo simulation, parameter sweeps, and ROC curve generation.
- **RQ3 (Tamper, Wrong Key, and Replay Rejection):** **Not a research question.** AES-GCM tag verification is a deterministic cryptographic guarantee already proven by NIST SP 800-38D. Verifying that `InvalidTag` is raised is standard software QA / unit testing, not empirical research.
- **RQ4 (Payload Size & Throughput):** Measurable, but evaluates standard AES-GCM and MQTT performance; it has no relationship to BB84 or quantum cryptography.

### 12. Are all PRD and SRS requirements testable?
**Finding:** **NO. Formal PRD and SRS documents DO NOT EXIST in the workspace.**
- Looking at the de-facto requirements scattered across the Synopsis and Dossier:
  - *"Generates a cryptographically secure 256-bit shared key"* (Synopsis Section 3): **Untestable** without formal entropy estimation, error reconciliation, and privacy amplification specs.
  - *"Demonstrate eavesdropping detection with QBER near 0% without Eve and ~25% with Eve"* (Synopsis Section 6): **Ambiguous / Untestable** under channel noise.
  - *"Real-time web dashboard for monitoring"* (Synopsis Section 4.4): **Untestable** (no latency target, frame rate, or protocol specified).
  - *"Comprehensive benchmarking suite"* (Synopsis Section 6): **Untestable** (no statistical confidence intervals, sample sizes, or hardware acceptance criteria specified).

### 13. Are the DFDs consistent with the architecture?
**Finding:** **NO. Data Flow Diagrams DO NOT EXIST in any document.**
- **Evidence:** In Synopsis Section 4.1, the architecture figure is literally a placeholder: `[Fig. 4.1: System Architecture Diagram — To be included]`.
- Neither document provides Level-0 (Context), Level-1, or Level-2 DFDs.
- Textual flows are inconsistent:
  - Synopsis states Module A produces the key for Module B and Module C (a centralized KDC flow).
  - Dossier Section 8 describes Alice and Bob as distinct functions within a simulation module.
  - No data flow is defined for how Bob (Cloud) receives Alice's (IoT) measurement bases or sends sifting acknowledgments over the network.

### 14. Do the experiments actually measure the stated contributions?
**Finding:** **NO. There is a fundamental disconnect between what is measured and what is claimed.**
- **Evidence:**
  1. **Qiskit Runtime vs. QKD Physical Overhead:** Measuring `time.perf_counter()` around Qiskit Aer measures the CPU overhead of classical matrix algebra simulating Hilbert space operations. It does **not** measure quantum optical key distribution, photon transmission latency, detector jitter, or real QKD protocol exchange.
  2. **Laptop Execution vs. IoT Edge Constraints:** The experiments run on an x86 laptop. They do not measure microcontroller memory footprint, bus latency, or energy consumption on constrained edge devices (e.g., ESP32, ARM Cortex-M).
  3. **Synchronous vs. Asynchronous Keying:** If Qiskit simulation is run synchronously inside the MQTT sensor publish loop, it introduces artificial delays of 1–5 seconds per sensor reading, creating an unviable architecture that does not reflect real-world QKD key-buffer architectures.

### 15. Can all claimed results be reproduced from the proposed experiment protocol?
**Finding:** **NO. Critical experimental parameters, random seeds, and software specifications are missing.**
- **Evidence:**
  - Raw qubit count $N$ per key generation cycle is never specified (e.g., 500, 1000, 4096?).
  - Sifting sample size sacrificed for QBER estimation is unspecified.
  - Exact quantum noise model (depolarizing probability $\lambda$, phase damping, thermal noise) is not parameterized.
  - Number of independent trials/repetitions per experimental condition is omitted.
  - Software environment is unpinned: Synopsis specifies `qiskit >= 1.0`, but Qiskit 1.0 introduced breaking API changes (removal of `qiskit.Aer` namespace, changes to `transpile()` and `backend.run()`). No exact Python version (3.10 vs 3.12) or OS dependency lockfile exists.

### 16. Are there contradictions between the original synopsis and the new design?
**Finding:** **YES. There are fundamental contradictions across multiple dimensions:**
| Dimension | Original Synopsis (Sept 2026) | Phase II Dossier & Matrix (Oct 2026) | Contradiction Status |
| :--- | :--- | :--- | :--- |
| **Academic Novelty** | Claims state-of-the-art advancement; asserts no prior work combined simulated BB84 with end-to-end MQTT/cloud. | Disclaims novelty; confirms BB84+Qiskit+IoT is heavily explored; prohibits claiming "first-ever" system. | **DIRECT CONTRADICTION** |
| **Security Claims** | Claims physically impossible security; asserts Shor's algorithm threatens AES-256. | Admits software simulation cannot prove quantum security; clarifies Shor breaks asymmetric keys, not AES-256. | **DIRECT CONTRADICTION** |
| **QBER Threshold** | Assumes static 11% threshold; assumes 0% QBER without Eve and 25% with Eve. | Acknowledges channel noise causes false alarms at 11%; notes partial Eve yields variable QBER below 25%. | **DIRECT CONTRADICTION** |
| **Comparative Baseline** | No baseline proposed; evaluates hybrid system in isolation. | Mandates classical comparative baseline; proposes optional ML-KEM baseline. | **UNAPPROVED EXPANSION** |
| **Post-Processing Rigor** | Claims SHA-256 hash of sifted bits generates a cryptographically secure key. | Admits SHA-256 is incomplete post-processing; recommends labeling system as educational simulation. | **METHODOLOGICAL SHIFT** |

### 17. Which decisions still require the supervisor's approval?
**Finding:** **At least six major architectural, methodological, and scoping decisions remain unapproved:**
1. **Approval of Scope Pivot:** Formally approving the retreat from a "novel quantum-secure IoT architecture" to an "educational performance and noise-aware benchmarking simulation."
2. **Key Post-Processing Fidelity:** Approving whether the team may omit Information Reconciliation (Cascade/Winnow) and Privacy Amplification, with explicit documentation that the key is educational/non-composable.
3. **Classical Comparator Selection:** Formally deciding whether the baseline is static PSK AES-GCM, ECDH/TLS 1.3, or NIST FIPS 203 (ML-KEM).
4. **Threat Model Boundaries:** Formally approving that the adversary model is restricted to software intercept-resend, with physical, optical, and side-channel attacks excluded.
5. **Hardware Benchmark Environment:** Approving whether evaluation on an x86 PC is acceptable for a thesis titled "Cloud-Based IoT Communication," or if embedded edge hardware is required.
6. **Publication Target Tier:** Aligning on realistic conference/journal venues given the educational simulation scope.

---

## SECTION II: DETAILED PROBLEM REGISTER & AUDIT FINDINGS

The following audit log documents all identified defects, classified by severity according to standard engineering audit protocols.

```
FINDING SUMMARY MATRIX:
+-----------+----------+--------+---------+-------+
|  CRITICAL |   HIGH   | MEDIUM |   LOW   | TOTAL |
+-----------+----------+--------+---------+-------+
|     4     |    5     |   4    |    2    |  15   |
+-----------+----------+--------+---------+-------+
```

---

### [CRITICAL-01] Missing Information Reconciliation Causes 100% Decryption Failure Under Noise
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 4.2), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 3, Cluster 2; Section 8, Layer 3).
* **The Issue:** The proposed pipeline sifts bits in Qiskit, samples QBER, and directly hashes the remaining sifted bits using SHA-256 to produce an AES-256 key without executing an Information Reconciliation (Error Correction) protocol (e.g., Cascade or Winnow).
* **Significance:** **FATAL CRYPTOGRAPHIC DEFECT.** In any noisy simulation (or physical channel), Alice's and Bob's sifted bitstrings will contain bit errors (e.g., 2%–5% QBER). Because of the cryptographic avalanche effect in SHA-256, even a single bit discrepancy causes the resulting 256-bit keys of Alice and Bob to be completely uncorrelated. Bob will fail AES-256-GCM authentication tag verification on **100% of received IoT payloads**. The system will only function when noise is artificially set to zero.
* **Supporting Evidence:** Dossier lines 18 and 36 acknowledge that hashing is not complete post-processing, but Section 8 Layer 3 continues to recommend proceeding without reconciliation.
* **Recommended Correction:** Either:
  1. Implement a lightweight classical error correction protocol (e.g., simplified Cascade) over the classical channel before hashing; OR
  2. If error correction is declared out of scope, Bob's sifted key must be simulated by copying Alice's reconciled string directly in software with an explicit disclaimer that channel reconciliation is abstracted out.
* **Downstream Documents Affected:** SRS, System Architecture, BB84 Simulator Module, AES Encryption Module, Test Plan.

---

### [CRITICAL-02] Total Absence of Formal Requirements and Design Artifacts (PRD, SRS, DFD, RTM)
* **Affected File & Section:** Entire Workspace (`c:\Users\bhuta\Desktop\Major_Project(2027)`).
* **The Issue:** The project workspace contains **no** Product Requirements Document (PRD), **no** Software Requirements Specification (SRS), **no** Data Flow Diagrams (DFDs), and **no** Requirements Traceability Matrix (RTM). The synopsis contains only a placeholder: `[Fig. 4.1: System Architecture Diagram — To be included]`.
* **Significance:** **ENGINEERING INTEGRITY VIOLATION.** Without an SRS and DFDs, developers have no verified interface contracts, data schemas, buffer specifications, or testable acceptance criteria. Implementation in this state would be completely ad-hoc and unverified.
* **Supporting Evidence:** Workspace directory listings confirm only two Word dossiers exist. No system models, schemas, or requirements baselines are present.
* **Recommended Correction:** Formalize a baseline specification package:
  - Generate an SRS conforming to IEEE 830 / ISO/IEC/IEEE 29148.
  - Construct Level-0 Context, Level-1 System, and Level-2 Module Data Flow Diagrams.
  - Create a bidirectional Requirements Traceability Matrix (RTM) linking research questions $\to$ SRS requirements $\to$ test cases.
* **Downstream Documents Affected:** All design, implementation, and test documentation.

---

### [CRITICAL-03] Literature Defense Relies Wholly on Abstracts with Zero Full-Text Screening of 2021–2026 Works
* **Affected File & Section:** `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx` (Section 3, Section 9), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 4).
* **The Issue:** Zero full texts of contemporary peer-reviewed QKD simulation and IoT integration papers (Das et al. 2026, Fiorini et al. 2026, IEEE NQComp 2026, Khan et al. 2026, Sharma & Kumar 2021) have been examined. All analysis is derived from publisher abstracts, IEEE Xplore snippets, and ScienceDirect highlights. Technical standards (NIST SP 800-38D, NIST FIPS 203, OASIS MQTT) are improperly counted toward the 30 research papers.
* **Significance:** **HIGH RISK OF ACADEMIC INVALIDITY.** The team cannot verify whether the exact proposed architecture, QBER threshold algorithm, or benchmark experiments have already been published by other groups.
* **Supporting Evidence:** Evidence Matrix Section 3 explicitly prefixes findings with *"Evidence from publisher abstract"* and Section 9 tasks the team with retrieving full texts.
* **Recommended Correction:** Retrieve full-text PDFs for all 13 priority sources plus Sharma & Kumar (2021). Execute systematic data extraction using the template in Dossier Section 12. Remove standards from the research paper count and expand the peer-reviewed corpus to 30 true research studies.
* **Downstream Documents Affected:** Literature Review Chapter, Related Work Section, Research Gap Analysis.

---

### [CRITICAL-04] Direct Contradictions Between Phase I Approved Synopsis and Phase II Redesign
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` vs. `Phase_II_BB84_IoT_Literature_Review_Dossier.docx`.
* **The Issue:** The Phase II dossier introduces fundamental shifts that directly contradict the institutional commitments made in the approved Phase I synopsis:
  1. Synopsis claims novel state-of-the-art hybrid QKD-IoT system; Dossier disclaims novelty and states QKD+IoT is well-trodden.
  2. Synopsis claims physical quantum security guarantees; Dossier admits software simulation cannot prove security.
  3. Synopsis establishes a rigid 11% QBER threshold assuming zero noise; Dossier demonstrates that noise invalidates an 11% static threshold.
  4. Synopsis has no baseline; Dossier mandates classical and post-quantum baselines.
* **Significance:** **ACADEMIC & INSTITUTIONAL RISK.** Submitting a final dissertation or paper based on the Phase II redesign without formal written supervisor approval of the synopsis deviation risks examination rejection or project invalidation.
* **Supporting Evidence:** Side-by-side comparison of Synopsis Section 1–4 and Dossier Section 1, 3, 6, and 10.
* **Recommended Correction:** Compile a formal *Synopsis Modification & Baseline Deviation Memo* detailing each necessary technical correction, and secure written sign-off from the project guide/supervisor before freezing the design.
* **Downstream Documents Affected:** Project Synopsis, Phase II Scope Baseline, Thesis Final Report.

---

### [HIGH-01] Undefined and Cryptographically Flawed Classical Baseline
* **Affected File & Section:** `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 3, Cluster 6; Table 3), `Synopsis_BB84_QKD_AES_IoT.docx` (Table 2).
* **The Issue:** The synopsis specifies no baseline. The dossier specifies a baseline of *"Pre-shared test key + AES-GCM + MQTT"*.
* **Significance:** **METHODOLOGICAL INVALIDITY.** A pre-shared static key has zero key-establishment overhead. Comparing a complex quantum circuit simulation against a static variable in memory does not evaluate key-establishment trade-offs. It produces an uninterpretable, strawman comparison.
* **Supporting Evidence:** Dossier Table 3 lists Baseline as *"Pre-shared test key + AES-GCM + MQTT"*.
* **Recommended Correction:** Define two rigorous, realistic baselines:
  1. *Classical Baseline:* Ephemeral Elliptic Curve Diffie-Hellman (ECDH over Curve25519 / X25519) simulating standard TLS/DTLS key agreement.
  2. *Post-Quantum Baseline (Recommended):* NIST FIPS 203 ML-KEM-512 key encapsulation to evaluate quantum resistance without QKD hardware.
* **Downstream Documents Affected:** Benchmark Harness, Experiment Protocol, Results & Evaluation Section.

---

### [HIGH-02] Omission of Classical Channel Authentication and Vulnerability to Active MitM
* **Affected File & Section:** `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 3, Cluster 2; Section 8), `Synopsis_BB84_QKD_AES_IoT.docx` (Section 4.2).
* **The Issue:** The architecture does not specify or implement authentication for the classical public channel used during basis sifting and QBER estimation.
* **Significance:** **SECURITY VULNERABILITY.** In BB84 theory, if the classical channel is unauthenticated, an active eavesdropper (Eve) can execute an undetectable Man-in-the-Middle (MitM) attack by impersonating Bob to Alice and Alice to Bob. The security proof of BB84 relies strictly on an authenticated classical channel.
* **Supporting Evidence:** Dossier lines 36 and 180 acknowledge that classical channel authentication is outside the prototype's claims.
* **Recommended Correction:** Explicitly document this architectural boundary: state that the classical channel is assumed to be authenticated out-of-band, or implement HMAC-SHA256 authentication over the sifting messages with an initial pre-shared key.
* **Downstream Documents Affected:** Threat Model, System Architecture, Protocol Specification.

---

### [HIGH-03] Measurement of Qiskit CPU Runtime Misrepresented as Quantum Protocol Latency
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Table 2), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 8, Layer 7; Section 9).
* **The Issue:** The experimental design measures `time.perf_counter()` around the execution of Qiskit's `AerSimulator` and reports it as "QKD Time" or "Quantum Key Generation Latency."
* **Significance:** **SCIENTIFIC MISREPRESENTATION.** Qiskit execution time on an x86 CPU reflects the software overhead of simulating quantum statevectors and linear algebra on classical hardware. It bears no physical or mathematical relationship to real QKD key generation rates (which depend on laser pulse repetition rate, fiber attenuation, single-photon detector dead times, and optical synchronization).
* **Supporting Evidence:** Synopsis Table 2 defines QKD Time as `time.perf_counter() around BB84 simulation`.
* **Recommended Correction:** Rename the metric to *"Qiskit Circuit Simulation Execution Time (Classical CPU Overhead)"*. Explicitly state in the paper that this measures software simulation latency, and compare it against theoretical QKD secret key rates (SKR) from physical literature.
* **Downstream Documents Affected:** Experiment Protocol, Benchmark Harness, Results Chapter.

---

### [HIGH-04] Architectural Inconsistency Regarding QKD Entity Allocation (Centralized Generator vs. Peer-to-Peer)
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 4.1, 4.2), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 8).
* **The Issue:** The architecture vacillates between a 3-tier architecture with an external "Quantum Key Generator" (Module A) supplying keys to Client (Module B) and Server (Module C), versus a peer-to-peer QKD link between Alice and Bob.
* **Significance:** **ARCHITECTURAL COHERENCE BREACH.** If Module A is an external generator, it acts as a classical Key Distribution Center (KDC), which fundamentally contradicts QKD's point-to-point physical topology. If Module A is executed on the edge device, running Qiskit Aer on constrained IoT hardware is impossible due to memory and CPU constraints.
* **Supporting Evidence:** Synopsis Section 4.1 describes Module A as executing the simulation to produce a shared key, which Module B and C then use.
* **Recommended Correction:** Redefine the architecture as a simulated Point-to-Point QKD Link between IoT Edge Gateway (Alice) and Cloud Server (Bob). Formally document that Alice is an Edge Gateway (e.g., Raspberry Pi 4/x86 gateway), not a bare microcontroller.
* **Downstream Documents Affected:** Architecture Document, DFDs, Module Design.

---

### [HIGH-05] Missing AES-GCM Nonce Discipline and Replay Protection Specification
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 4.3, 4.4), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 8, Layer 4 & 5).
* **The Issue:** The documentation does not define the 96-bit nonce generation policy, counter management, state persistence across device reboots, or MQTT message replay window.
* **Significance:** **CRYPTOGRAPHIC FAILURE RISK.** Reusing an IV/nonce under the same key in AES-GCM allows an attacker to recover the authentication hash subkey $H$, catastrophically destroying message authenticity and integrity. Furthermore, MQTT brokers can deliver duplicate or out-of-order messages (under QoS 1 or 2); without a monotonic sequence counter, replay attacks are trivial.
* **Supporting Evidence:** Synopsis Section 4.3 merely states *"The encryption produces a nonce, authentication tag, and ciphertext... published to MQTT"*.
* **Recommended Correction:** Specify a deterministic 96-bit nonce construction: 32-bit fixed device ID + 64-bit strictly monotonic sequence counter. Implement replay rejection on the cloud receiver using a sliding-window sequence check.
* **Downstream Documents Affected:** SRS, AES Encryption Module, Cloud Receiver Module.

---

### [MEDIUM-01] Conflation of Shor's and Grover's Quantum Algorithms
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 1, line 36).
* **The Issue:** Synopsis asserts that Shor's algorithm poses an existential threat to AES-256.
* **Significance:** **CONCEPTUAL ERROR.** Shor's algorithm solves discrete logarithms and prime factorization in polynomial time, threatening RSA and ECC. Symmetric ciphers like AES are subject only to Grover's algorithm (quadratic search speedup), leaving AES-256 with 128 bits of post-quantum security—which is universally considered secure.
* **Supporting Evidence:** Synopsis Section 1 explicitly cites Shor's algorithm to justify replacing classical encryption.
* **Recommended Correction:** Rewrite the threat motivation: clarify that Shor's algorithm threatens the *classical public-key key exchange* (RSA, ECDH) used to distribute AES keys, while AES-256 itself remains quantum-safe for bulk payload encryption.
* **Downstream Documents Affected:** Synopsis Introduction, Research Paper Introduction.

---

### [MEDIUM-02] Omission of the Closest Literature Precedent (Sharma & Kumar 2021) from Evidence Matrix
* **Affected File & Section:** `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 4), `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx` (Section 3).
* **The Issue:** Sharma & Kumar (2021), titled *"BB84 QKD protocol simulation for IoT security using Python"*, was explicitly cited in the original synopsis as the primary prior work to be improved upon (Synopsis Ref [9]). In the Phase II dossier and evidence matrix, this paper was completely dropped from the 30-paper list and priority screening.
* **Significance:** **SELECTIVE CITATION / LITERATURE INTEGRITY ISSUE.** Dropping the exact paper previously identified as the baseline comparator prevents verifying whether the proposed Phase II work genuinely advances beyond it.
* **Supporting Evidence:** Synopsis Reference [9] vs. Dossier Section 4 references.
* **Recommended Correction:** Reinstate Sharma & Kumar (2021) into the priority screening matrix. Retrieve the full text and perform a side-by-side technical comparison against the proposed prototype.
* **Downstream Documents Affected:** Literature Review, Related Work, Research Gap Analysis.

---

### [MEDIUM-03] Ambiguity Between On-Demand and Buffered Key Generation in IoT Pipeline
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 4.1–4.4), `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 8, Layer 3).
* **The Issue:** The documents do not specify whether BB84 simulation executes synchronously on-demand for every published sensor reading, or runs asynchronously in the background into a pre-shared key pool/buffer.
* **Significance:** **PERFORMANCE DISCONNECT.** Synchronous key generation causes multi-second blocking delays per sensor packet. Buffered key generation decouples key distribution from payload encryption, meaning transmission latency is identical to standard AES. The experiments fail to clearly isolate these two operational modes.
* **Supporting Evidence:** Dossier Table 3 (Payload sweep vs. Key/batch sweep) hints at key reuse assumptions but leaves the architecture undefined.
* **Recommended Correction:** Explicitly model and benchmark both operational modes:
  1. *Mode 1 (Synchronous Rekeying):* Evaluates worst-case per-message setup penalty.
  2. *Mode 2 (Key Buffer / Batched Rekeying):* Evaluates realistic key-pool exhaustion and steady-state transmission throughput.
* **Downstream Documents Affected:** System Architecture, Benchmark Harness, Experiment Protocol.

---

### [MEDIUM-04] Non-Measurable Research Questions (RQ3 as QA, RQ4 as Classical IoT)
* **Affected File & Section:** `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 7), `Phase_II_Literature_Screening_Evidence_Matrix_Round1.docx` (Section 6).
* **The Issue:** RQ3 (rejection of tampered ciphertexts and invalid tags) is formulated as a research question when it is an assertion-based unit test. RQ4 (payload scaling) measures only standard AES and MQTT behavior, with no quantum or QKD component.
* **Significance:** **WEAK RESEARCH FORMULATION.** Academic reviewers will reject RQ3 as trivial QA and criticize RQ4 as irrelevant to quantum cryptography.
* **Supporting Evidence:** Dossier Section 7 lists RQ3 and RQ4 alongside RQ1 and RQ2.
* **Recommended Correction:** Reframe the research questions:
  - Demote RQ3 to a System Verification & Integrity Test Objective.
  - Reformulate RQ4 to investigate: *"How does key refresh frequency (rekeying interval) trade off against payload transmission latency and key exhaustion under varying sensor message arrival rates?"*
* **Downstream Documents Affected:** Research Questions, Hypotheses, Paper Structure.

---

### [LOW-01] Inconsistent Qiskit Version Requirements and Deprecated API References
* **Affected File & Section:** `Synopsis_BB84_QKD_AES_IoT.docx` (Section 5, Table 1).
* **The Issue:** Synopsis specifies `IBM Qiskit (>=1.0) + Qiskit-Aer`. In Qiskit 1.0+, `qiskit.Aer` was decoupled into the standalone `qiskit_aer` provider, and core execution workflows were overhauled.
* **Significance:** **CODE REPRODUCIBILITY ISSUE.** Novice developers following legacy tutorials will encounter runtime import errors and deprecation warnings under Qiskit 1.0+.
* **Supporting Evidence:** Synopsis Table 1 lists `IBM Qiskit (>=1.0) + Qiskit-Aer`.
* **Recommended Correction:** Pin dependencies explicitly in a `requirements.txt`: `qiskit==1.2.0`, `qiskit-aer==0.15.1`, `cryptography==43.0.1`, `paho-mqtt==2.1.0`. Provide verified Qiskit 1.0 syntax snippets.
* **Downstream Documents Affected:** Implementation Guide, Technology Stack, Environment Setup.

---

### [LOW-02] Incomplete Bibliographic Metadata in Dossier Corpus
* **Affected File & Section:** `Phase_II_BB84_IoT_Literature_Review_Dossier.docx` (Section 4).
* **The Issue:** Several entries in the 30-source corpus lack complete metadata: Reference [23] and [24] omit author names (listing only article titles and venues), and Reference [15] provides a Google Scholar query rather than a direct publisher DOI.
* **Significance:** **SCHOLARLY RIGOR DEFECT.** Incomplete citations degrade the academic professionalism of the literature dossier.
* **Supporting Evidence:** Dossier Section 4, entries [15], [23], [24].
* **Recommended Correction:** Populate full author lists, exact volume/issue numbers, and official DOIs for all 30 references.
* **Downstream Documents Affected:** References Section, Literature Dossier.

---

## SECTION III: MANDATORY ACTION PLAN & REMEDIATION ROADMAP

To transition the project from **RESEARCH GATE FAILED** to **RESEARCH GATE PASSED**, the engineering team must execute the following structured remediation sprints:

### Sprint 1: Literature Full-Text Extraction & Comparative Matrix (Target: 7 Days)
1. Retrieve full-text PDFs for the 13 priority sources plus Sharma & Kumar (2021).
2. Populate the detailed extraction template (Dossier Section 12) for all 14 retrieved papers.
3. Replace technical standards (NIST, OASIS) in the 30-item corpus with eligible peer-reviewed research papers to ensure a 30-paper scientific corpus.
4. Construct a comprehensive **Side-by-Side System Comparison Matrix** comparing prior systems.

### Sprint 2: Cryptographic & Baseline Technical Redesign (Target: 5 Days)
1. **Resolve Information Reconciliation Flaw:** Incorporate a lightweight Cascade error correction simulation or formally document a simulated error-free reconciled key handoff.
2. **Define Classical Baselines:** Specify Ephemeral ECDH (X25519) and optional ML-KEM-512 benchmarks.
3. **Formalize Nonce & Replay Protection:** Implement a 96-bit deterministic counter with sliding-window replay rejection.

### Sprint 3: Systems Engineering & Traceability Artifacts (Target: 5 Days)
1. **Draft SRS (Software Requirements Specification):** Author a formal SRS with uniquely identified requirements.
2. **Draft DFD Package:** Create Level-0 Context Diagram, Level-1 System DFD, and Level-2 Module DFDs.
3. **Build Traceability Matrix (RTM):** Link Research Questions to SRS Requirements to Test Cases.

### Sprint 4: Supervisor Review & Institutional Alignment (Target: 3 Days)
1. Prepare a formal **Synopsis Deviation & Baseline Approval Briefing** for Prof. [Guide Name] at MSIT.
2. Secure formal written sign-off on the scope pivot and baseline definitions.
3. Freeze the Phase II documentation baseline into the project repository.

---

## SECTION IV: CONCLUSION & GATE DECISION

The documentation package submitted for audit reveals an ambitious concept that was initially overclaimed in the Phase I synopsis and is currently undergoing an incomplete pivot in Phase II. While the author of the Phase II dossier correctly spotted many theoretical pitfalls in the executive notes, the project repository currently lacks the necessary empirical literature verification, systems engineering artifacts, and cryptographic post-processing rigor required to proceed to code implementation.

**FINAL GATE VERDICT:**  
**RESEARCH GATE FAILED**  
Implementation is paused. Execution of prototype code prior to completing Sprints 1–4 is strictly prohibited.
