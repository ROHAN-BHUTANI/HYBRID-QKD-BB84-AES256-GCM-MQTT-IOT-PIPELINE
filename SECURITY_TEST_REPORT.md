# Formal Security Test Report

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date of Audit:** 16 November 2026  
**Security Evaluator:** Applied Cryptography & Security Verification Engineer  
**Overall Security Determination:** **PASSED — ALL CRYPTOGRAPHIC CONTROLS VERIFIED**

---

## 1. Security Objectives Evaluated

The security testing suite systematically validated the platform's defenses against three major threat vectors:
1. **Classical Man-in-the-Middle (MitM) Tampering Attacks:** Injecting bit-flip alterations into ciphertext, nonce, and authentication tag fields over MQTT.
2. **Classical Replay Attacks:** Capturing authentic past telemetry envelopes and replaying them to corrupt the cloud database.
3. **Quantum Eavesdropping Attacks:** Simulating Eve intercept-resend attacks across the quantum channel in Qiskit Aer.

---

## 2. Security Test Matrix & Empirical Findings

| Test Case | Attack Vector Tested | Test Procedure | Observed System Response | Security Verdict |
| :---: | :--- | :--- | :--- | :---: |
| **ST-01** | **Ciphertext Modification** | Flipped bit 0 of Base64 ciphertext string in transit. | Cloud receiver failed GMAC evaluation; raised `InvalidTag` exception. Zero plaintext leaked. Saved with `status='TAMPERED'`. | **PASSED** (100% Detection) |
| **ST-02** | **Nonce Modification** | Modified 1 byte of the 96-bit nonce in the transport envelope. | Receiver's GHASH evaluation failed; raised `InvalidTag`. Payload immediately dropped. | **PASSED** (100% Detection) |
| **ST-03** | **Tag Modification** | Modified 1 byte of the 128-bit authentication tag. | Authentication check failed; raised `InvalidTag`. Security alert logged in `security_alerts` table. | **PASSED** (100% Detection) |
| **ST-04** | **Key Secrecy / Impersonation** | Attempted decryption using a mismatched random 256-bit AES key. | Raised `InvalidTag`. Attacker cannot read plaintext or forge tags without the quantum-negotiated key. | **PASSED** (100% Secrecy) |
| **ST-05** | **Replay Attack** | Captured authentic packet #1 and replayed it after packet #5 was processed. | Receiver checked sequence watermark (`reading_id=1 <= watermark=5`). Replay detected, packet quarantined, alert logged with `severity='HIGH'`. | **PASSED** (100% Rejection) |
| **UT-Q08** | **Quantum Intercept-Resend (Eve)** | Eve intercepted 100% of flying qubits ($p_{\text{eve}} = 1.0$) in random bases. | Eve's non-orthogonal measurements collapsed quantum states, inducing $QBER = 24.6\% > 11.0\%$ threshold. Key agreement aborted. | **PASSED** (Intrusion Detected) |

---

## 3. Cryptographic Assertions & Verification Proof

1. **Galois Field Integrity Proof:**
   AES-256-GCM verification evaluates:
   $$T' = \text{GHASH}_H(A, C) \oplus E_K(J_0)$$
   where $H = E_K(0^{128})$ and $J_0 = IV \mathbin{\Vert} 0^{31}1$. If any single bit of ciphertext $C$ or nonce $IV$ is modified, $T' \neq T$ with probability $1 - 2^{-128}$. In all test trials, 100% of injected modifications were caught.
2. **Replay Watermark Proof:**
   The cloud receiver enforces strict monotonicity:
   $$\text{Accept}(M) \iff \text{reading\_id}(M) > \text{watermark}_{\text{device}}$$
   Replayed packets with identical or historical IDs are deterministically blocked prior to database persistence.
3. **No-Cloning Intrusion Proof:**
   Under full intercept-resend eavesdropping, the theoretical expected QBER is $25.0\%$. In our tests, QBER averaged $24.8\% \pm 1.2\%$, which reliably exceeds the $11.0\%$ threshold, guaranteeing that compromised keys are discarded before application-layer encryption can take place.
