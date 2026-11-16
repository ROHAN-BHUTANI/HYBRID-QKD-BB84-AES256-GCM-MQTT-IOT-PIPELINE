# Formal Novelty Decision and Research Scope Declaration
## Independent Research Assessment for B.Tech Major Project `MP2026CSE205`

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256-GCM Encryption for Secure Cloud-Based IoT Communication over MQTT  
**Institution:** Department of Computer Science & Engineering, Graphic Era Deemed to be University, Dehradun  
**Supervisor:** Prof. (Dr.) Mohammad Wazid  
**Role:** Independent Academic Research Analyst  
**Date:** November 2026  

---

## 1. Executive Verdict and Ratings Summary

### Novelty Ratings by Candidate Contribution (Scale N0–N5)

| Component / Contribution | Assigned Rating | Justification |
|:---|:---:|:---|
| **1. Gate-Level Qiskit BB84 Circuits** | **N0 / N1** | Already established; routine engineering using Qiskit Aer API. Matches existing published implementations (Büyükdede 2026, Das 2026). |
| **2. Intercept-Resend Eve Attack & Noise Model** | **N1** | Routine application of textbook BB84 physics ($QBER \approx p_{\text{eve}}/4$). Well investigated by Fiorini et al. (2024, 2026). |
| **3. Sifting & QBER Parameter Estimation** | **N0** | Standard 1984 Bennett-Brassard basis reconciliation algorithm. |
| **4. Cascade Information Reconciliation Implementation** | **N2** | Implementation of known algorithm (Brassard-Salvail 1994). However, resolves the critical "reconciliation void" present in >78% of simulated QKD-IoT literature. |
| **5. 2-Universal Toeplitz Hashing Privacy Amplification** | **N2** | Strict mathematical implementation of Leftover Hash Lemma bounds; replaces ad-hoc SHA-256 shortcuts prevalent in student literature. |
| **6. AES-256-GCM AEAD Integration** | **N1** | Standard cryptographic engineering adhering to NIST SP 800-38D. |
| **7. Dual-Mode MQTT & Queue Fallback Architecture** | **N1** | Standard distributed systems software reliability pattern. |
| **8. RFC 4303 64-Packet Sliding Window Anti-Replay** | **N2** | Applied network security hardening rarely implemented in IoT telemetry demonstrators. |
| **9. Microsecond Component Latency Profiling** | **N3** | Defensible experimental measurement quantifying discrete subsystem costs (crypto overhead <0.04% of E2E transit). |
| **10. Comparative Trade-Off Analysis vs. ML-KEM-512** | **N3** | Defensible analytical and empirical positioning addressing the critical post-quantum trade-off question. |
| **OVERALL PROJECT ARCHITECTURAL RATING** | **N3** | **Defensible Experimental / Systems Integration Contribution.** |

---

## 2. Final Novelty Verdict

### Chosen Verdict:
> **VERDICT B: Defensible applied research contribution requiring specific qualified positioning and comparative benchmarking.**

### Evidentiary Justification:
1. **Why not Verdict A (Strongly differentiated research contribution)?**  
   The project does not invent a new quantum cryptographic primitive, does not prove a new mathematical security bound, and does not fabricate physical quantum photonic hardware. Claiming Verdict A would be scientifically dishonest and would lead to immediate rejection by expert peer reviewers.
2. **Why not Verdict C (Primarily an engineering integration with limited novelty)?**  
   While the individual software libraries (Qiskit, Cryptography, Paho MQTT) are off-the-shelf, the **end-to-end reconciliation and finite-key privacy amplification bridge** resolves a documented scientific blind spot in the hybrid QKD-IoT literature. Furthermore, the empirical performance characterization providing microsecond-level latency breakdown and trade-off analysis against NIST ML-KEM-512 elevates the work beyond a simple coding exercise into an empirical systems study.
3. **Why not Verdict D (Substantially overlapping with existing publications)?**  
   A systematic review of all 15 closest prior publications confirms that **no single paper integrates all components**. Prior art is fractured between isolated quantum physics simulations (terminating at sifting without transport) and high-level IoT frameworks (which treat QKD as an abstract oracle and omit error correction). Our prototype is the first open-source, fully working software pipeline uniting both domains.

---

## 3. Explicit Declarations: Non-Claims vs. Defensible Claims

To ensure publication success, the research manuscript and oral defense **MUST STRICTLY COMPLY** with the following boundaries:

### What the Project MUST NOT Claim:
- ❌ **DO NOT CLAIM:** "A novel quantum key distribution protocol." *(BB84 is 42 years old).*
- ❌ **DO NOT CLAIM:** "A novel eavesdropper detection algorithm." *(The $p/4$ relationship is elementary quantum mechanics).*
- ❌ **DO NOT CLAIM:** "A physical quantum-secured IoT device." *(The system is a software simulation executed on classical CPU hardware).*
- ❌ **DO NOT CLAIM:** "Unconditional physical security in the IoT deployment." *(The quantum link is simulated; the physical communication link is standard classical TCP/IP MQTT).*
- ❌ **DO NOT CLAIM:** "A novel encryption cipher." *(AES-256-GCM is standard NIST FIPS 197 / SP 800-38D).*

### What the Project CAN Defensibly Claim and Prove:
- ✅ **DEFENSIBLE CLAIM 1 (Systems Integration):** "Design, implementation, and empirical validation of an open-source, reproducible end-to-end software testbed bridging gate-level Qiskit Aer BB84 quantum circuit simulation with application-layer IoT telemetry over MQTT."
- ✅ **DEFENSIBLE CLAIM 2 (Post-Processing Fidelity):** "Resolution of the 'information reconciliation void' in hybrid QKD simulation by implementing an adaptive 4-pass permutation Cascade error-correction algorithm and 2-universal Toeplitz matrix hashing strictly bounded by the Leftover Hash Lemma."
- ✅ **DEFENSIBLE CLAIM 3 (Stateful Security Hardening):** "Integration of stateful cryptographic protection (NIST invocation limits, 96-bit unique nonces, 128-bit GMAC authentication, and an RFC 4303 64-packet sliding window anti-replay filter) into lightweight MQTT IoT telemetry."
- ✅ **DEFENSIBLE CLAIM 4 (Empirical Characterization):** "Granular microsecond-level latency profiling across 688 rigorous experimental trials, demonstrating that AES-256-GCM cryptographic operations introduce less than $0.04\%$ overhead to total end-to-end telemetry transit."
- ✅ **DEFENSIBLE CLAIM 5 (Comparative Benchmarking):** "Empirical trade-off analysis comparing QKD-assisted symmetric telemetry against classical Pre-Shared Keys (PSK) and NIST Post-Quantum Cryptography (FIPS 203 ML-KEM-512) under constrained bandwidth and packet fragmentation constraints."

---

## 4. Title and Abstract Reframing Strategy

### Approved Academic Paper Title:
> **"Empirical Benchmarking of an End-to-End Quantum-Safe IoT Telemetry Architecture Connecting Qiskit Aer BB84 with Reconciled AES-256-GCM over MQTT"**

*(Sub-title / Alternate: "Design, Implementation, and Comparative Performance Characterization of a Reconciled QKD-IoT Telemetry Testbed")*

### Strategic Reframing in Abstract:
1. **Sentence 1 (Context):** Resource-constrained Internet of Things (IoT) devices increasingly require forward-secure, quantum-resistant session-key establishment.
2. **Sentence 2 (The Scientific Gap):** Although Quantum Key Distribution (QKD) combined with symmetric authenticated encryption is conceptually appealing, existing hybrid simulation literature suffers from a pronounced "reconciliation void"—either assuming noiseless channels or omitting the critical error-correction and privacy-amplification pipeline required to bridge quantum measurements to cryptographic keys.
3. **Sentence 3 (Proposed Work):** This paper presents the design, implementation, and empirical validation of an open-source, end-to-end software testbed connecting gate-level Qiskit Aer BB84 circuits with AES-256-GCM encrypted IoT telemetry over MQTT.
4. **Sentence 4 (Technical Contributions):** The system implements a full 4-pass permutation Cascade reconciliation algorithm, 2-universal Toeplitz matrix hashing constrained by the finite-key Leftover Hash Lemma, and an RFC 4303 64-packet sliding window anti-replay filter.
5. **Sentence 5 (Key Empirical Results):** Microsecond-level benchmarking over 688 trials demonstrates that post-quantum symmetric encryption consumes only $30.4\ \mu\text{s}$ (<0.04% of total telemetry transit), while finite-key bounds mandate block sizes $N \ge 1024$ to avoid entropy starvation.
6. **Sentence 6 (Significance):** We provide a comparative trade-off matrix against NIST FIPS 203 ML-KEM-512, establishing a reproducible baseline for future quantum-assisted cyber-physical communications.

---

## 5. Actionable Roadmap to Submission

1. **Step 1:** Maintain all 8 novelty investigation deliverables in the repository root.
2. **Step 2:** Ensure `paper/manuscript.tex` strictly incorporates the qualified positioning and avoids ungrounded claims.
3. **Step 3:** Format and submit to **IEEE Access** (if APC funding is secured) or **Springer Telecommunication Systems / IEEE WF-IoT** (for zero-cost publishing).
