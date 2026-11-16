# Technical Implementation Roadmap

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Roadmap Milestones & Phases

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: Project Audit & Literature Review (COMPLETE)      │
│  - Systematic review of 32 verified peer-reviewed papers   │
│  - Gap analysis & formal research gap decision              │
│  - Audit report: PROJECT_CURRENT_STATE_AUDIT.md             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Systems Engineering Documentation (COMPLETE)      │
│  - PRD, SRS (IEEE 830), System Architecture Document        │
│  - Threat Model (STRIDE/Quantum), Database Schema, ADRs     │
│  - Test Plan, Experiment Protocol, Traceability Matrix      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: Codebase Hardening & Modular Upgrade              │
│  - Modular QKD: alice, bob, eve, channel, postprocessing    │
│  - Information Reconciliation (Parity/Cascade Error Corr.)  │
│  - Universal-Hash Privacy Amplification KDF                 │
│  - Stateful Anti-Replay Watermarking in Cloud Receiver      │
│  - Channel Noise Integration (qiskit_aer.noise)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: Automated Testing & Validation                    │
│  - Full test suite: unit, integration, security, system     │
│  - Verify 100% test pass rate via pytest                    │
│  - Produce TEST_RESULTS.md and SECURITY_TEST_REPORT.md      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: Empirical Benchmarking & Data Collection          │
│  - Parameter sweeps: QKD vs Qubits, QBER vs Eve, Noise      │
│  - Crypto latency vs payload, E2E latency: MQTT vs Queue    │
│  - Baseline comparison (Plaintext vs PSK vs QKD vs Kyber)   │
│  - Generate CSV datasets and publication plots              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: Publication Manuscript Preparation                │
│  - IEEE conference/journal formatted LaTeX manuscript       │
│  - BibTeX database with complete verified DOIs              │
│  - PAPER_SUBMISSION_READINESS_REPORT.md                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Deliverable Checkpoints

1. **Checkpoint 1 (Core Architecture):** Working Qiskit BB84 simulation, parity reconciliation, AES-256-GCM, MQTT dual-mode bridge, and SQLite persistence.
2. **Checkpoint 2 (Security Hardening):** 100% detection of bit-flip tampering, rejection of replayed `reading_id`, and QBER-based abort when Eve is active.
3. **Checkpoint 3 (Empirical Evidence):** 7 automated benchmarks executed across 30+ trials, producing raw CSVs in `experiments/raw_results/` and summary tables in `experiments/processed_results/`.
4. **Checkpoint 4 (Submission Readiness):** Final manuscript drafted in `paper/manuscript.tex` with complete citations, ready for supervisor review and conference/journal submission.
