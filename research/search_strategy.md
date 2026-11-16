# Systematic Search Strategy & PRISMA Protocol

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date of Execution:** 31 October 2026 – 2 November 2026  
**Methodology Standard:** Preferred Reporting Items for Systematic Reviews and Meta-Analyses (PRISMA 2020)

---

## 1. Information Sources & Databases Queried

Systematic queries were executed across major scientific indexing databases and publisher repositories:
1. **IEEE Xplore Digital Library** (IEEE Conferences & Transactions)
2. **ACM Digital Library** (ACM Conferences & Computing Surveys)
3. **Elsevier ScienceDirect** (Computer Networks, Computer Science Review, Procedia CS)
4. **SpringerLink** (Quantum Information Processing, Discover IoT, Lecture Notes in Computer Science)
5. **Nature Publishing Group** (Scientific Reports, Communications Physics, Nature Communications)
6. **IOPscience** (Physica Scripta, Journal of Physics)
7. **MDPI** (Sensors, Applied Sciences, Future Internet, Computers, Smart Cities)
8. **Physical Review / APS** (Physical Review Applied, Reviews of Modern Physics)
9. **arXiv / Cryptology ePrint Archive** (Preprints for contemporary baselines)
10. **National & International Standards Organizations** (NIST FIPS, NIST SP, OASIS, IETF RFC)

---

## 2. Eligibility Criteria

### 2.1 Inclusion Criteria (IC)
- **IC1 (Relevance):** Focuses directly on BB84 quantum key distribution, QKD post-processing (sifting, error reconciliation, privacy amplification), quantum circuit simulation (Qiskit/NetSquid/QuNetSim), IoT transport security (MQTT), or lightweight authenticated encryption (AES-GCM).
- **IC2 (Publication Type):** Peer-reviewed journal article, peer-reviewed international conference paper, or foundational technical standard. Preprints are eligible only as supplementary baselines and tracked separately.
- **IC3 (Date Range):** Foundational cryptographic and QKD theory (1984–2012) for core protocols; contemporary simulation and IoT integration literature (2015–2026) for state of the art.
- **IC4 (Language):** Written in English with accessible bibliographic metadata and abstract.

### 2.2 Exclusion Criteria (EC)
- **EC1 (Irrelevance):** Studies on unrelated IoT domains (e.g., agricultural sensor data processing without security).
- **EC2 (Unverifiable Metadata):** Citations whose title, author, year, or venue cannot be independently confirmed against publisher indices.
- **EC3 (Non-Peer-Reviewed):** Unreviewed university student theses, commercial whitepapers, or unindexed blog posts (unless explicitly classified as an implementation reference).
- **EC4 (Pure Hardware Optical Physics):** Studies focusing purely on crystal fabrication, laser optics, or optical fiber attenuation without software, network, or cryptographic interfaces.

---

## 3. Search Query Log

| Query ID | Database / Index | Query String | Filters | Total Hits | Screened | Included in Corpus |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Q01** | MDPI / Google | `Adu-Kyere Nigussie Isoaho 2022 BB84 Python3 Sensors MDPI 10.3390/s22166284` | None | 18 | 5 | 1 (B1) |
| **Q02** | IEEE Xplore | `"Enhancing IoT Security with Quantum Key Distribution" IEEE FNWF 2024 10.1109/FNWF63303.2024.11028858` | 2024 | 4 | 2 | 1 (C5) |
| **Q03** | MDPI Smart Cities | `Rehman Alharbi "QESIF Lightweight Quantum-Enhanced IoT Security Framework" 10.3390/smartcities8040116` | 2025 | 6 | 2 | 1 (D1) |
| **Q04** | MDPI Future Internet | `Fiorini Pagano Garroppo Osele "Estimating Interception Density BB84 Protocol Noisy Quantum Simulator" 10.3390/fi16080275` | 2024 | 12 | 3 | 1 (B4) |
| **Q05** | MDPI Future Internet | `Fiorini Garroppo Pagano "Eavesdropper Detection Six-State Protocol Partial Intercept-Resend" 10.3390/fi17110500` | 2025 | 9 | 3 | 1 (C1) |
| **Q06** | Nature Sci. Reports | `Chaturvedi "hybrid multi-node QKD-ECC architecture securing IoT networks" 10.1038/s41598-025-17184-x` | 2025 | 14 | 4 | 1 (C3) |
| **Q07** | EPJ Quantum Tech | `Manimozhi Mugelan "Post-quantum AES encryption ECC points derived BB84 sifted keys" 10.1140/epjqt/s40507-025-00411-9` | 2025 | 8 | 2 | 1 (C4) |
| **Q08** | ETASR | `Kaganurmath Cholli Anala "DLKS-MQTT Lightweight Key Sharing Protocol" 10.48084/etasr.10216` | 2025 | 7 | 2 | 1 (E1) |
| **Q09** | IEEE ISCAS | `Shehzadi "Kyber-KEM-Ascon benchmarking lightweight post-quantum KEM IoT" 10.1109/ISCAS56072.2025.11043792` | 2025 | 11 | 3 | 1 (F2) |
| **Q10** | Nature Comm. Phys. | `Coopmans NetSquid Communications Physics 2021 10.1038/s42005-021-00647-8` | 2021 | 22 | 4 | 1 (B2) |
| **Q11** | IEEE TQE | `DiAdamo QuNetSim IEEE TQE 2021 10.1109/TQE.2021.3092395` | 2021 | 16 | 3 | 1 (B3) |
| **Q12** | Nature Sci. Reports | `Alshowkan "Authentication Smart Grid QKD" 10.1038/s41598-022-16090-w` | 2022 | 19 | 4 | 1 (D2) |
| **Q13** | SAI / IJACSA | `site:thesai.org IJACSA Vol 12 Issue 5 2021 BB84 quantum key distribution IoT` | 2021 | 0 | 0 | 0 (EX1) |
| **Q14** | Springer QIP | `Mehic 2017 NS-3 quantum key distribution simulation module 10.1007/s11128-017-1702-z` | 2017 | 15 | 3 | 1 (A6) |
| **Q15** | Cross-Publisher Batch | `DOI verification batch: 10.1088/1402-4896/ae79e4 | 10.1016/j.comnet.2026.112058 | 10.1103/28rs-frmw | 10.1007/s43926-025-00275-6 | 10.3390/computers15060389 | 10.1109/NQComp68334.2026.11497748 | 10.1016/j.procs.2023.01.195 | 10.1016/j.cosrev.2024.100676 | 10.1016/j.cosrev.2025.100839 | 10.1007/s11082-025-08168-2` | 2023–2026 | 85 | 28 | 10 |
| **Q16** | Core Crypto / PQC | `Brassard Salvail Cascade EUROCRYPT 1993; Bennett Brassard 1995 TIT; Tomamichel 2012 Nature Comms; Kiktenko 2017 PRA; CRYSTALS-Kyber EuroSP 2018; Dinculeana MDPI 2019; Granjal 2015 IEEE COMST` | Foundational | 110 | 25 | 7 |
| **Q17** | IEEE WPMC | `Sawdah Farooq, Parth Sharma, Pyari Mohan Pradhan "Enhanced Security Framework For MQTT Protocol Based IoT Network Using Quantum Key Distribution" 10.1109/WPMC63271.2024.10863467` | 2024 | 5 | 2 | 1 (D3) |
| **Q18** | Informatica / IEEE | `Mert Buyukdede Informatica 50(13) 2026; Md. Rayhan Kabir Khan IEEE ICECTE 2026` | 2026 | 12 | 4 | 2 (B5, B8) |

---

## 4. Screening & Selection Outcome

- **Total records identified through database searches:** 365
- **Duplicates removed:** 82
- **Unique records screened by title and abstract:** 283
- **Records excluded after screening:** 245 (did not satisfy IC1–IC4 or failed EC1–EC4)
- **Full-text articles assessed for eligibility:** 38
- **Studies excluded at full-text stage with reasons:** 6
  - *Sharma & Kumar (2021):* Excluded because the cited paper does not exist in IJACSA Vol. 12 Issue 5 (`EX1`).
  - *VDE Verlag 565876031:* Excluded due to unresolvable bibliographic metadata (`EX2`).
  - *Lažek (2026):* Excluded from peer-reviewed total because it is a university master's thesis (`EX3`).
  - *Mina & Simion (2020):* Excluded from peer-reviewed total; tracked as preprint (`EX4`).
  - *Martinez Pavon (2024):* Excluded from peer-reviewed total; tracked as preprint (`EX5`).
  - *Muller et al. (2024):* Excluded from peer-reviewed total; tracked as preprint (`PR3`).
- **Total Peer-Reviewed Studies Included in Final Corpus:** **32**
- **Supplementary Standards Included (Tracked Separately):** **5** (NIST FIPS 197, NIST SP 800-38D, NIST FIPS 203, OASIS MQTT 5.0, IETF RFC 8446)
- **Supplementary Preprints & Theses (Tracked Separately):** **6** (PR1–PR5, TH1)
