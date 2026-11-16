# Empirical Research Experiment Results & Statistical Analysis

Generated automatically from raw empirical CSV data.

### Table 1: EXP-1 QKD Circuit Scaling & Post-Processing Yield

| Qubit Block Size ($N$) | Sifted Bits ($\mu$) | Reconciled Bits ($\mu$) | QBER ($\mu \pm \sigma$) | Execution Time (ms) ($\mu \pm \sigma$) | Convergence Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 128 | 65.0 | 49.1 | 0.0000 $\pm$ 0.0000 | 6.88 $\pm$ 2.90 | 100.0% |
| 256 | 128.0 | 96.4 | 0.0000 $\pm$ 0.0000 | 12.87 $\pm$ 1.31 | 100.0% |
| 512 | 259.4 | 195.0 | 0.0000 $\pm$ 0.0000 | 40.76 $\pm$ 10.99 | 100.0% |
| 1024 | 513.2 | 385.3 | 0.0000 $\pm$ 0.0000 | 120.30 $\pm$ 33.07 | 100.0% |


### Table 2: EXP-2 QBER & Abort Probability vs. Interception Density ($p_{\text{eve}}$)

| Interception Prob ($p_{\text{eve}}$) | Empirical QBER ($\mu \pm \sigma$) | Theoretical QBER ($p/4$) | Key Abort Rate (%) | Security Decision |
| :--- | :--- | :--- | :--- | :--- |
| 0.0 | 0.0000 $\pm$ 0.0000 | 0.0000 | 0.0% | ACCEPT (Clean / Tolerable) |
| 0.2 | 0.0437 $\pm$ 0.0276 | 0.0500 | 0.0% | ACCEPT (Clean / Tolerable) |
| 0.4 | 0.0892 $\pm$ 0.0331 | 0.1000 | 25.0% | ABORT (Eve Detected) |
| 0.6 | 0.1442 $\pm$ 0.0356 | 0.1500 | 80.0% | ABORT (Eve Detected) |
| 0.8 | 0.1859 $\pm$ 0.0510 | 0.2000 | 100.0% | ABORT (Eve Detected) |
| 1.0 | 0.2351 $\pm$ 0.0475 | 0.2500 | 100.0% | ABORT (Eve Detected) |


### Table 3: EXP-3 Channel Depolarizing Noise vs. Cascade Reconciliation Success

| Depolarizing Param ($\lambda$) | Sample QBER ($\mu \pm \sigma$) | EC Parity Leakage (Bits) | Success Rate ($QBER \le 11\%$) |
| :--- | :--- | :--- | :--- |
| 0.00 | 0.0000 $\pm$ 0.0000 | 0.0 | 100.0% |
| 0.02 | 0.0111 $\pm$ 0.0131 | 30.7 | 100.0% |
| 0.05 | 0.0426 $\pm$ 0.0330 | 65.8 | 93.3% |
| 0.08 | 0.0670 $\pm$ 0.0327 | 82.7 | 93.3% |
| 0.10 | 0.0664 $\pm$ 0.0392 | 86.7 | 86.7% |
| 0.12 | 0.0961 $\pm$ 0.0398 | 70.1 | 66.7% |


### Table 4: EXP-4 AES-256-GCM Latency and Cryptographic Throughput

| Payload (Bytes) | Encryption Time ($\mu \pm \sigma$ ms) | Decryption Time ($\mu \pm \sigma$ ms) | Enc Throughput (KB/s) | Dec Throughput (KB/s) |
| :--- | :--- | :--- | :--- | :--- |
| 32 | 0.4863 $\pm$ 3.3678 | 0.0182 $\pm$ 0.0691 | 64.3 | 1,717.0 |
| 64 | 0.0073 $\pm$ 0.0015 | 0.0066 $\pm$ 0.0011 | 8,561.6 | 9,469.7 |
| 128 | 0.0112 $\pm$ 0.0139 | 0.0078 $\pm$ 0.0028 | 11,160.7 | 16,025.6 |
| 256 | 0.0113 $\pm$ 0.0073 | 0.0100 $\pm$ 0.0045 | 22,123.9 | 25,000.0 |
| 512 | 0.0114 $\pm$ 0.0013 | 0.0105 $\pm$ 0.0038 | 43,859.6 | 47,619.0 |
| 1024 | 0.0134 $\pm$ 0.0099 | 0.0105 $\pm$ 0.0019 | 74,626.9 | 95,238.1 |
| 2048 | 0.0182 $\pm$ 0.0118 | 0.0196 $\pm$ 0.0209 | 109,890.1 | 102,040.8 |


### Table 5: EXP-5 Cryptographic Tamper Detection Rate

| Attack Vector | Trials Tested | Rejections by GMAC / GCM | Detection Rate (%) | Security Margin |
| :--- | :--- | :--- | :--- | :--- |
| Ciphertext Inversion (1-bit) | 50 | 50 | 100.0% | 128-bit MAC Integrity |
| Nonce Corruption (1-byte) | 50 | 50 | 100.0% | AEAD Authentication Trap |
| Authentication Tag Tamper | 50 | 50 | 100.0% | Tag Collision Bound $2^{-128}$ |


### Table 6: EXP-6 End-to-End Latency Profile (Local Queue Mode)

| Metric | Latency (ms) | Notes |
| :--- | :--- | :--- |
| Mean E2E Latency | 362.334 $\pm$ 185.473 | Encrypt + Queue Dispatch + Decrypt + DB Commit |
| 95% Confidence Interval | [309.309, 415.360] | $N = 47$ repetitions |
| Mean AES-GCM Encrypt Overhead | 0.1259 $\pm$ 0.3050 | Cryptographic primitive overhead |
| Cryptographic Overhead Share | 0.03% | Negligible fraction of E2E transit |


### Table 7: EXP-7 Comparative Baseline Evaluation

| Communication Architecture | Key Exchange Mechanism | Handshake Latency (ms) | Packet Overhead (B) | Quantum Security Guarantee | Tamper Detection |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Plaintext MQTT | None | 0.0 | 0 | NO (Trivial Eavesdropping) | NO |
| Pre-Shared Key AES-256-GCM | Static Provisioning (PSK) | 0.0 | 28 | YES (128-bit Grover margin) | YES |
| Post-Quantum ML-KEM-512 (Kyber) + AES-GCM | Lattice KEM Encapsulation (FIPS 203) | 2.15 | 28 | YES (Computational Lattice) | YES |
| Proposed Hybrid QKD (Qiskit BB84) + AES-256-GCM | Quantum State Agreement + Universal Hash KDF | 38.5 | 28 | YES (Information-Theoretic Physics) | YES |


