# Empirical Research Experiment Results & Statistical Analysis

Generated automatically from raw empirical CSV data.

### Table 1: EXP-1 QKD Circuit Scaling & 2-Universal Toeplitz Key Yield

| Qubit Block Size ($N$) | Sifted Bits ($\mu$) | Reconciled Bits ($\mu$) | QBER ($\mu \pm \sigma$) | Execution Time (ms) ($\mu \pm \sigma$) | 256-bit AES Extraction Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 256 | 127.6 | 96.1 | 0.0000 $\pm$ 0.0000 | 28.91 $\pm$ 22.45 | 0.0% |
| 512 | 253.8 | 190.7 | 0.0000 $\pm$ 0.0000 | 141.12 $\pm$ 11.90 | 0.0% |
| 1024 | 513.1 | 385.2 | 0.0000 $\pm$ 0.0000 | 398.21 $\pm$ 39.75 | 100.0% |
| 1536 | 769.9 | 577.8 | 0.0000 $\pm$ 0.0000 | 805.06 $\pm$ 113.05 | 100.0% |
| 2048 | 1024.3 | 768.7 | 0.0000 $\pm$ 0.0000 | 1665.14 $\pm$ 143.77 | 100.0% |


### Table 2: EXP-2 QBER & Abort Probability vs. Interception Density ($p_{\text{eve}}$)

| Interception Prob ($p_{\text{eve}}$) | Empirical QBER ($\mu \pm \sigma$) | Theoretical QBER ($p/4$) | Key Abort Rate (%) | Security Decision |
| :--- | :--- | :--- | :--- | :--- |
| 0.0 | 0.0000 $\pm$ 0.0000 | 0.0000 | 0.0% | ACCEPT (Clean / Tolerable) |
| 0.2 | 0.0469 $\pm$ 0.0167 | 0.0500 | 0.0% | ACCEPT (Clean / Tolerable) |
| 0.4 | 0.1002 $\pm$ 0.0144 | 0.1000 | 20.0% | ABORT (Eve Detected) |
| 0.6 | 0.1427 $\pm$ 0.0164 | 0.1500 | 100.0% | ABORT (Eve Detected) |
| 0.8 | 0.2121 $\pm$ 0.0289 | 0.2000 | 100.0% | ABORT (Eve Detected) |
| 1.0 | 0.2489 $\pm$ 0.0330 | 0.2500 | 100.0% | ABORT (Eve Detected) |


### Table 3: EXP-3 Channel Depolarizing Noise vs. Cascade Reconciliation Success

| Depolarizing Param ($\lambda$) | Sample QBER ($\mu \pm \sigma$) | EC Parity Leakage (Bits) | Success Rate ($QBER \le 11\%$) |
| :--- | :--- | :--- | :--- |
| 0.00 | 0.0000 $\pm$ 0.0000 | 0.0 | 100.0% |
| 0.02 | 0.0096 $\pm$ 0.0063 | 102.6 | 100.0% |
| 0.05 | 0.0244 $\pm$ 0.0106 | 223.2 | 100.0% |
| 0.08 | 0.0413 $\pm$ 0.0133 | 277.6 | 100.0% |
| 0.10 | 0.0507 $\pm$ 0.0140 | 305.8 | 100.0% |
| 0.12 | 0.0576 $\pm$ 0.0214 | 348.5 | 100.0% |


### Table 4: EXP-4 AES-256-GCM Latency and Cryptographic Throughput

| Payload (Bytes) | Encryption Time ($\mu \pm \sigma$ ms) | Decryption Time ($\mu \pm \sigma$ ms) | Enc Throughput (KB/s) | Dec Throughput (KB/s) |
| :--- | :--- | :--- | :--- | :--- |
| 32 | 0.0917 $\pm$ 0.5356 | 0.0150 $\pm$ 0.0049 | 340.8 | 2,083.3 |
| 64 | 0.0312 $\pm$ 0.0992 | 0.0151 $\pm$ 0.0043 | 2,003.2 | 4,139.1 |
| 128 | 0.0222 $\pm$ 0.0260 | 0.0163 $\pm$ 0.0015 | 5,630.6 | 7,668.7 |
| 256 | 0.0167 $\pm$ 0.0009 | 0.0154 $\pm$ 0.0044 | 14,970.1 | 16,233.8 |
| 512 | 0.0386 $\pm$ 0.0952 | 0.0206 $\pm$ 0.0148 | 12,953.4 | 24,271.8 |
| 1024 | 0.0172 $\pm$ 0.0018 | 0.0204 $\pm$ 0.0262 | 58,139.5 | 49,019.6 |
| 2048 | 0.0215 $\pm$ 0.0379 | 0.0154 $\pm$ 0.0053 | 93,023.3 | 129,870.1 |


### Table 5: EXP-5 Cryptographic Tamper Detection Rate

| Attack Vector | Trials Tested | Rejections by GMAC / GCM | Detection Rate (%) | Security Margin |
| :--- | :--- | :--- | :--- | :--- |
| Ciphertext Inversion (1-bit) | 50 | 50 | 100.0% | 128-bit MAC Integrity |
| Nonce Corruption (1-byte) | 50 | 50 | 100.0% | AEAD Authentication Trap |
| Authentication Tag Tamper | 50 | 50 | 100.0% | Tag Collision Bound $2^{-128}$ |


### Table 6: EXP-6 End-to-End Latency Profile (Local Queue Mode)

| Metric | Latency (ms) | Notes |
| :--- | :--- | :--- |
| Mean E2E Latency | 180.484 $\pm$ 103.280 | Encrypt + Queue Dispatch + Decrypt + DB Commit |
| 95% Confidence Interval | [150.637, 210.330] | $N = 46$ repetitions |
| Mean AES-GCM Encrypt Overhead | 0.0745 $\pm$ 0.0158 | Cryptographic primitive overhead |
| Cryptographic Overhead Share | 0.04% | Negligible fraction of E2E transit |


### Table 7: EXP-7 Comparative Baseline Evaluation

| Communication Architecture | Key Exchange Mechanism | Handshake Latency (ms) | Packet Overhead (B) | Quantum Security Guarantee | Tamper Detection |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Plaintext MQTT | None | 0.0 | 0 | NO (Trivial Eavesdropping) | NO |
| Pre-Shared Key AES-256-GCM | Static Provisioning (PSK) | 0.0 | 28 | YES (128-bit Grover margin) | YES |
| Post-Quantum ML-KEM-512 (Kyber) + AES-GCM | Lattice KEM Encapsulation (FIPS 203) | 2.15 | 28 | YES (Computational Lattice) | YES |
| Proposed Hybrid QKD (Qiskit BB84) + AES-256-GCM | Quantum State Agreement + Universal Hash KDF | 38.5 | 28 | YES (Information-Theoretic Physics) | YES |


