# Risk Register & Technical Mitigation Plan

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Risk Evaluation Matrix

Risks are categorized across four domains: **Technical & Cryptographic (T)**, **Experimental & Scientific (E)**, **Operational & Environmental (O)**, and **Publication & Academic (P)**.  
*Risk Score = Probability (1–5) × Impact (1–5)*.

| Risk ID | Domain | Risk Description | Prob (1-5) | Imp (1-5) | Score | Mitigation Strategy | Contingency Plan | Residual Risk |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **R-01** | **T** | **Noise Key Divergence:** Residual channel errors cause Alice and Bob's sifted keys to differ, causing 100% AES decryption failures. | 4 | 5 | **20** | Implement interactive Information Reconciliation (parity/Cascade search) before key derivation to correct bit discrepancies. | If reconciliation fails due to high noise, abort session and renegotiate. | Low |
| **R-02** | **T** | **Nonce Collision in GCM:** Nonce reuse across identical keys catastrophically breaks GMAC integrity. | 1 | 5 | **5** | Enforce 96-bit CSPRNG nonces (`os.urandom(12)`) and periodic key rotation via BB84 before $2^{32}$ messages. | Abort encryption if nonce counter reaches $2^{32}$. | Negligible |
| **R-03** | **O** | **External Broker Unavailability:** Lab or presentation machine lacks Mosquitto or network access. | 4 | 4 | **16** | Implement dual-mode broker architecture with a zero-dependency in-memory Queue fallback (`USE_SIMULATED_BROKER`). | Automatic fallback to in-memory queue if TCP socket connect fails. | Low |
| **R-04** | **E** | **Unsound Security Claims:** Claiming "unconditional physical security" from a Qiskit software simulation. | 3 | 5 | **15** | Explicitly define scope as quantum circuit simulation. Document mathematical finite-key bounds honestly in research paper. | Peer review and supervisor sign-off on paper claims. | Low |
| **R-05** | **T** | **Replay Attacks on MQTT:** Attacker replays valid ciphertext envelopes to inject stale sensor telemetry into cloud DB. | 3 | 4 | **12** | Implement stateful monotonic sequence window checking (`reading_id > last_sequence_id`) in cloud receiver. | Reject and log security alert for any duplicate sequence ID. | Low |
| **R-06** | **P** | **Reviewer Rejection for Lack of Baselines:** Academic reviewers reject manuscript due to lack of comparison with post-quantum standards. | 3 | 4 | **12** | Implement empirical comparison against NIST FIPS 203 (ML-KEM-512 / Kyber) and pre-shared key baselines. | Include baseline comparison tables in experimental results section. | Low |
| **R-07** | **O** | **Windows Console Unicode Crash:** PowerShell crashing on UTF-8 symbols (`✓`, `°C`). | 3 | 3 | **9** | Add `sys.stdout.reconfigure(encoding="utf-8")` across all entry points and CLI scripts. | Wrap console outputs in safe ASCII fallbacks if UTF-8 fails. | Negligible |
| **R-08** | **E** | **Simulation Performance Bottleneck:** Simulating thousands of qubits in Qiskit Aer causes high CPU latency. | 2 | 3 | **6** | Optimize circuit depth; parameterize qubit blocks ($N \le 2048$) suitable for edge simulation; measure execution times. | Limit interactive dashboard QKD runs to $N=512$. | Low |
