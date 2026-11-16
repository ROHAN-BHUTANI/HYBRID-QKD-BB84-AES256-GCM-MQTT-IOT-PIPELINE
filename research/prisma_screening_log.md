# PRISMA 2020 Screening Log & Flow Accounting

**Project:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Screening Window:** 31 October 2026 – 2 November 2026  
**Auditor / Reviewer:** Applied Cryptography & Systematic Review Specialist

---

## 1. Flow Diagram (PRISMA 2020 Format)

```
┌─────────────────────────────────────────────────────────────┐
│                       IDENTIFICATION                        │
├─────────────────────────────────────────────────────────────┤
│  Records identified from:                                   │
│  - IEEE Xplore: 72                                          │
│  - ScienceDirect / Elsevier: 64                             │
│  - SpringerLink / Nature: 78                                │
│  - MDPI: 61                                                 │
│  - IOPscience / APS: 38                                     │
│  - Other databases & indexes: 52                            │
│  TOTAL IDENTIFIED: 365                                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    DUPLICATE REMOVAL                        │
├─────────────────────────────────────────────────────────────┤
│  Duplicate records removed: 82                              │
│  UNIQUE RECORDS SCREENED: 283                               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        SCREENING                            │
├─────────────────────────────────────────────────────────────┤
│  Records screened based on Title & Abstract: 283            │
│  Records excluded: 245                                      │
│  - Pure physical optical fabrication: 114                   │
│  - General IoT unrelated to cryptography: 86                │
│  - Classical crypto without post-quantum/QKD context: 45    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       ELIGIBILITY                           │
├─────────────────────────────────────────────────────────────┤
│  Reports sought for retrieval: 38                           │
│  Reports assessed for eligibility: 38                       │
│  Excluded after detailed assessment: 6                      │
│  - Unresolvable DOI / Citation not found: 2 (EX1, EX2)      │
│  - University Theses (not peer-reviewed): 2 (EX3, EX5)      │
│  - Unreviewed Preprints: 2 (EX4, PR3)                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        INCLUSION                            │
├─────────────────────────────────────────────────────────────┤
│  Total Peer-Reviewed Studies Included: 32                   │
│  - Theme A (QKD Post-Processing & Security Bounds): 6       │
│  - Theme B (BB84 / QKD Software Simulation): 8              │
│  - Theme C (Eavesdropping / Noise / Thresholds): 5          │
│  - Theme D (QKD-IoT / Cloud Key Management): 7              │
│  - Theme E (IoT AES-GCM & MQTT Security): 5                 │
│  - Theme F (Classical & PQC Baselines): 4                   │
│  - Theme G (Systematic Reviews & Surveys): 5                │
│  (Note: Several studies span multiple themes)               │
│                                                             │
│  Separately Tracked Non-Peer-Reviewed Items:                │
│  - Technical Standards (NIST, OASIS, IETF): 5               │
│  - Non-Peer-Reviewed Preprints & Theses: 6                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Numerical Reconciliation Table

| Metric | Count | Verification Formula / Evidence Check |
| :--- | :---: | :--- |
| **Initial Records Identified** | 365 | Sum of all distinct search hits across 18 search sessions (Q01–Q18) |
| **Duplicate Records** | 82 | Automated DOI and normalized title collision detection |
| **Unique Records Screened** | 283 | $365 - 82 = 283$ |
| **Abstract-Stage Exclusions** | 245 | Explicitly failed Inclusion Criteria IC1–IC4 |
| **Full-Text Reports Assessed** | 38 | $283 - 245 = 38$ |
| **Full-Text Stage Exclusions** | 6 | Detailed in Section 3 below |
| **Final Peer-Reviewed Corpus** | **32** | $38 - 6 = 32$ ($\ge 30$ requirement satisfied) |
| **Standards (Separate)** | 5 | NIST FIPS 197, NIST SP 800-38D, NIST FIPS 203, OASIS MQTT 5.0, RFC 8446 |
| **Preprints & Theses (Separate)**| 6 | PR1, PR2, PR3, PR4, PR5, TH1 |

---

## 3. Excluded Studies at Detailed Assessment Stage

| Reference Key | Cited Author / Year | Target Source | Detailed Reason for Exclusion |
| :--- | :--- | :--- | :--- |
| **EX1** | Sharma & Kumar (2021) | *IJACSA* Vol. 12, Issue 5, pp. 412–419 | **Citation Not Found:** A direct review of the table of contents and archive of *International Journal of Advanced Computer Science and Applications* (IJACSA) Vol. 12, No. 5 (2021) confirmed that no paper by these authors on BB84, QKD, or quantum cryptography was published in that issue. Excluded per scientific anti-hallucination rules. |
| **EX2** | VDE Verlag (2020) | *VDE Conference Proceedings*, ID 565876031 | **Unresolvable Bibliographic Record:** Search engines, CrossRef, and VDE Verlag's catalog returned no paper matching this title or ID. Excluded due to unverifiable provenance. |
| **EX3** | Bc. Patrik Lažek (2026) | Brno University of Technology Repository | **Non-Peer-Reviewed Academic Thesis:** Master's thesis titled *"Protocol extension to support post-quantum cryptography"* (MQTT v5 + ML-KEM). Excluded from peer-reviewed total; tracked as supplementary thesis `TH1`. |
| **EX4** | Mina & Simion (2020) | Cryptology ePrint Archive, Report 2020/1074 | **Unreviewed Preprint:** Published to IACR ePrint; no subsequent journal or peer-reviewed conference version could be verified. Tracked separately as `PR5`. |
| **EX5** | Martinez Pavon (2024) | engrXiv Preprints, DOI: 10.31224/5965 | **Non-Peer-Reviewed Preprint:** Master's dissertation uploaded to engrXiv. Excluded from 32 peer-reviewed count. |
| **EX6 / PR3**| Muller et al. (2024) | arXiv:2408.15758 | **Unreviewed Preprint:** Study on Cascade and LDPC for QKD. Excluded from peer-reviewed count; tracked as `PR3`. |

---
*Log generated following PRISMA 2020 transparent reporting standards.*
