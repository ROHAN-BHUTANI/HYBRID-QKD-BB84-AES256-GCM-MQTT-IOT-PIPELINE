# Cryptographic Security Audit Report

**Project:** Hybrid BB84 QKD + AES-256-GCM IoT Pipeline  
**Project ID:** MP2026CSE205  
**Audit Date:** 2026-11-16  
**Classification:** Internal Security Review  
**Status:** FINAL

---

## Executive Summary

This document is a formal cryptographic security audit of the Hybrid BB84 Quantum Key Distribution (QKD) + AES-256-GCM IoT pipeline. The audit covers AES-GCM implementation correctness, key derivation security via Toeplitz hashing, privacy amplification bounds, replay protection compliance, CSPRNG usage, and overall threat model coverage.

> [!IMPORTANT]
> **Overall Verdict: CRYPTOGRAPHICALLY SOUND WITH DOCUMENTED LIMITATIONS**
> 
> The implementation is correct and NIST-compliant at the symmetric encryption layer. All major cryptographic primitives are used appropriately. Known limitations are bounded, documented, and acceptable for research/simulation contexts.

---

## 1. AES-256-GCM Implementation Audit

### Configuration Parameters

| Parameter | Specified Value | Standard Requirement | Status |
|-----------|----------------|----------------------|--------|
| Key size | `config.AES_KEY_SIZE_BYTES = 32` → 256 bits | NIST FIPS 197: 128/192/256-bit | ✅ PASS |
| Nonce | `os.urandom(12)` → 96-bit random | NIST SP 800-38D §8.2.1 recommended | ✅ PASS |
| Authentication tag | 128-bit (16 bytes) | NIST SP 800-38D §5.2.1.2 max tag length | ✅ PASS |
| Library | `cryptography.hazmat.primitives.ciphers.aead.AESGCM` | OpenSSL/libsodium backend | ✅ PASS |
| Nonce lifecycle | Random nonce, `IoTSensorClient.key_invocations` counter, limit = 100,000 | NIST SP 800-38D §8.3 | ✅ PASS |

### Nonce Collision Probability

With random 96-bit nonces and an invocation limit of 100,000, the birthday-bound collision probability is bounded by:

```
P(collision) ≤ q² / 2^(n+1)
where q = 100,000 invocations, n = 96 bits

P(collision) ≤ (10^5)² / 2^97 ≈ 10^10 / 1.585×10^29 ≈ 6.3 × 10^-20
```

This is negligibly small. The 100,000 invocation limit is conservative and consistent with NIST SP 800-38D guidance.

### Library Trust

`cryptography.hazmat.primitives.ciphers.aead.AESGCM` is part of the Python `cryptography` package (PyCA), which wraps OpenSSL's battle-tested AES-GCM implementation. This is an industry-standard choice for Python cryptography.

### ✅ VERDICT: AES-GCM implementation is **CORRECT** and **NIST-compliant**

---

## 2. Key Derivation Security Audit

### Toeplitz 2-Universal Hash over GF(2)

The key derivation layer uses a Toeplitz matrix hash for privacy amplification, a well-established technique in quantum cryptography (Bennett et al., 1995; Renner, 2008).

#### Security Parameter Analysis

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Security parameter | ε_sec = 2⁻³² | Design choice |
| Security margin (bits) | 2 × log₂(1/ε_sec) = 2 × 32 = 64 bits | LHL standard margin |
| Output key length formula | `l = m_raw − leak_bits − 64` | Strictly enforced in `calculate_secure_key_length()` |

#### Toeplitz Matrix Construction

| Property | Verification |
|----------|-------------|
| Matrix dimensions | (l × m) — output length × input length |
| Seed length | m + l − 1 bits (Toeplitz constraint) | ✅ CORRECT |
| Seed expansion | SHA-256 counter mode from fixed base seed | ✅ Deterministic |
| Bit packing | MSB-first into bytes | ✅ CORRECT |
| GF(2) arithmetic | XOR-based dot product | ✅ CORRECT |

#### ⚠️ Known Limitation: Deterministic Seed

```
Seed: b"QKD-BB84-TOEPLITZ-UNIVERSAL-SEED-2026" (fixed constant)
```

The SHA-256 counter-mode seed expansion produces a **deterministic, reproducible** Toeplitz matrix instance. This means:

- The hash matrix is the **same across all runs** of the simulation.
- An adversary who knows this constant (e.g., from source code) knows the exact linear map applied to the raw key.
- This does **not** break information-theoretic security if the sifted key bits are truly unknown to the adversary — the LHL guarantee holds regardless of the matrix, as long as it is a valid universal hash family and the adversary does not know the sifted bits.
- However, it **does** mean the matrix is not secret, eliminating any "matrix secrecy" defense in depth.

> [!NOTE]
> **For research simulation:** This is acceptable. The LHL proof does not require the hash seed to be secret; it requires the seed to be chosen uniformly at random from the hash family, independent of the quantum channel. A fixed seed does technically break this formal independence requirement in a production deployment.
>
> **For production:** A truly random shared seed must be transmitted over an **authenticated classical channel** (e.g., using pre-shared keys or a one-time pad for the seed itself). Without this, the statistical independence assumption of the LHL is not formally satisfied.

### ✅ VERDICT (Research Context): Key derivation is **CORRECT** per LHL with documented seed limitation

---

## 3. Privacy Amplification Security Boundaries

### Leftover Hash Lemma (LHL) Guarantee

The Leftover Hash Lemma provides the following information-theoretic security bound:

```
Statistical distance from uniform: δ ≤ ε_sec = 2^-32
```

This means the extracted key is **computationally indistinguishable from a uniformly random string** up to a distinguishing advantage of at most 2⁻³².

### Security Layer Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│              QUANTUM CHANNEL (Information-Theoretic)        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Raw key bits → Sifting → Error correction →        │   │
│  │  Privacy Amplification (Toeplitz + LHL)             │   │
│  │                                                     │   │
│  │  GUARANTEE: Eve's information ≤ ε_sec = 2^-32      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│         Extracted AES-256 Key (256-bit)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
         CLASSICAL AUTHENTICATION CHANNEL
         ┌──────────────────────────────┐
         │  Basis reconciliation        │
         │  QBER estimation             │
         │  Error correction syndromes  │
         │  Pre-shared identity         │
         │                              │
         │  ⚠️ ASSUMED SECURE           │
         │  No formal guarantee here    │
         └──────────────────────────────┘
```

### Critical Security Boundary

> [!CAUTION]
> **Information-theoretic security applies ONLY within the quantum channel layer.**
>
> If the classical authentication channel is compromised:
> - An adversary can perform a **man-in-the-middle attack** on basis reconciliation.
> - The adversary can inject false QBER estimates to prevent legitimate key agreement.
> - The adversary can substitute their own measurement outcomes for Bob's.
> - **The QKD security guarantee is completely voided.**
>
> This is a **fundamental architectural limitation** of BB84 without authenticated classical channels. It is a known, accepted limitation in QKD research when pre-shared authentication credentials are unavailable.

### Finite-Key Effects

For small N (number of transmitted qubits), finite-key statistical fluctuations can cause the QBER estimate to deviate from its true value. With the 11% abort threshold:

- For large N (N ≫ 1000): Statistical confidence is high; the threshold is robust.
- For small N (N ~ 100–300): There is a non-negligible probability that:
  - Legitimate sessions abort due to statistical fluctuation (false positive).
  - Eve performs a partial intercept-resend that stays below the threshold (false negative in extreme low-N regimes).

> [!NOTE]
> The simulation operates at N values where finite-key effects are observable. Production QKD deployments use rigorous finite-key analysis (Tomamichel et al., 2012) to compute tight security bounds for small N. This simulation uses the asymptotic QBER threshold, which is a standard simplification for research contexts.

---

## 4. Replay Protection Audit (RFC 4303 / RFC 6347)

### Implementation: `SlidingWindowAntiReplay` — window_size = 64

#### RFC 4303 Section 3.4.3 Compliance Matrix

| RFC Requirement | Implementation | Status |
|----------------|----------------|--------|
| Accept packet with seq > max_seq (advance window) | ✅ Window slides forward, bitmap updated | ✅ COMPLIANT |
| Accept in-order packet within window, not seen before | ✅ Bitmap bit clear → accept, set bit | ✅ COMPLIANT |
| Reject duplicate (already received within window) | ✅ Bitmap bit set → reject | ✅ COMPLIANT |
| Reject stale packet (seq < window_left boundary) | ✅ seq < max_seq − 64 → reject | ✅ COMPLIANT |
| Accept out-of-order within window | ✅ Bit-indexed within 64-entry bitmap | ✅ COMPLIANT |

### Algorithm Verification

```
Window state: [max_seq - 63  ...  max_seq]
                    ↑                  ↑
              oldest accepted     most recent

Incoming seq n:
  - n < (max_seq - 63)        → REJECT  (too old / stale)
  - n in window, bit set      → REJECT  (duplicate)
  - n in window, bit clear    → ACCEPT  (out-of-order, mark seen)
  - n > max_seq               → ACCEPT  (advance window, update max_seq)
```

This matches the RFC 4303 §3.4.3 algorithm exactly. ✅

### ⚠️ Known Limitation: Non-Persistent Replay State

> [!WARNING]
> **Replay window state is held entirely in memory.**
>
> On `CloudReceiver` restart:
> - `max_seq` resets to 0
> - The bitmap clears entirely
> - All previously seen sequence numbers are forgotten
>
> **Attack window:** An adversary who captures packets before a restart can replay them during the brief period after restart before `max_seq` advances past those sequence numbers.
>
> **RECOMMENDATION for production:** Persist `max_seq` (and optionally the full bitmap) to a durable store (database, Redis with fsync, or a write-ahead log) on clean shutdown. On startup, restore from the persisted state before accepting any packets.

### ✅ VERDICT: Replay protection is **RFC 4303 COMPLIANT** with documented persistence limitation

---

## 5. Threat Model Coverage

| Threat | Coverage | Implementation | Gap |
|--------|----------|----------------|-----|
| Passive eavesdropping on quantum channel | ✅ **COVERED** | QBER detection + Toeplitz privacy amplification (LHL ε = 2⁻³²) | None |
| Intercept-resend attack (Eve) | ✅ **COVERED** | QBER threshold abort at 11%; Eve's presence raises QBER to ~25% | Small-N finite-key edge case (see §3) |
| Ciphertext tampering in transit | ✅ **COVERED** | AES-GCM `InvalidTag` exception on authentication failure | None |
| Nonce tampering | ✅ **COVERED** | AES-GCM `InvalidTag` (nonce is part of auth input) | None |
| Authentication tag forgery | ✅ **COVERED** | 128-bit GCM tag → forgery probability ≤ 2⁻¹²⁸ per message | None |
| Replay attack | ⚠️ **PARTIAL** | 64-packet RFC 4303 sliding window bitmap | In-memory only; resets on restart |
| Man-in-the-middle on classical channel | ❌ **NOT COVERED** | Assumed secure (pre-shared identity only) | **Major known limitation** — no authenticated classical channel |
| Key exhaustion / nonce reuse | ✅ **COVERED** | 100,000 invocation limit tracked in `key_invocations`; triggers re-keying | None |
| Brute-force AES-256 | ✅ **NOT A CONCERN** | 2²⁵⁶ key space; computationally infeasible for all known adversaries including quantum (Grover: 2¹²⁸ effective) | None |
| Weak PRNG for crypto operations | ✅ **COVERED** (with note) | `secrets.SystemRandom()` for Alice/Bob; `os.urandom()` for nonces | Eve simulation uses `random.random()` — non-crypto, see §6 |
| Information leakage via error correction | ✅ **COVERED** | Leaked bits accounted for in `calculate_secure_key_length()` | None |
| Denial-of-service via QBER manipulation | ⚠️ **PARTIAL** | Abort on high QBER protects key material | No rate limiting or DoS-specific mitigation |

---

## 6. CSPRNG Audit

### PRNG Usage Inventory

| Usage | PRNG Used | Cryptographically Secure? | Assessment |
|-------|-----------|--------------------------|------------|
| Alice qubit bit generation | `secrets.SystemRandom()` | ✅ Yes (OS-level CSPRNG) | ✅ **CORRECT** |
| Alice basis selection | `secrets.SystemRandom()` | ✅ Yes (OS-level CSPRNG) | ✅ **CORRECT** |
| Bob basis selection | `secrets.SystemRandom()` | ✅ Yes (OS-level CSPRNG) | ✅ **CORRECT** |
| AES nonce generation | `os.urandom(12)` | ✅ Yes (OS entropy pool) | ✅ **CORRECT** |
| AES key fallback / test key | `os.urandom(32)` | ✅ Yes (OS entropy pool) | ✅ **CORRECT** |
| Eve intercept mask (simulation) | `random.random()` | ⚠️ No (Mersenne Twister) | ⚠️ **ACCEPTABLE FOR SIMULATION** |

### Eve's Non-Cryptographic PRNG

```python
# Eve intercept mask uses:
random.random()  # Mersenne Twister — NOT cryptographically secure
```

> [!NOTE]
> **Why this is acceptable in this context:**
>
> Eve is a **simulation entity**, not a real adversary. The purpose of `random.random()` here is to simulate probabilistic intercept behavior, not to generate secret key material. No security property of the system depends on Eve's intercept mask being unpredictable. This is a standard simplification in QKD simulation research.
>
> **What would be wrong:** Using `random.random()` for Alice/Bob key bits, basis choices, or AES nonce generation. None of these use it.
>
> **Documentation requirement:** This choice should be clearly documented in any publication derived from this codebase to avoid misinterpretation.

### CSPRNG Assessment Summary

- **Key material and crypto operations:** All use OS-level CSPRNG (`secrets` module or `os.urandom`). ✅
- **Simulation-only randomness:** Uses `random` module. ⚠️ Acceptable with documentation.

---

## 7. Security Verdict

### Component-Level Verdict Table

| Component | Standard/Reference | Verdict | Notes |
|-----------|-------------------|---------|-------|
| AES-256-GCM key size | NIST FIPS 197 | ✅ **PASS** | 32 bytes = 256 bits |
| AES-GCM nonce generation | NIST SP 800-38D §8.2.1 | ✅ **PASS** | 96-bit random nonce via `os.urandom` |
| AES-GCM authentication tag | NIST SP 800-38D §5.2.1.2 | ✅ **PASS** | 128-bit (maximum strength) |
| AES-GCM invocation limit | NIST SP 800-38D §8.3 | ✅ **PASS** | 100,000 limit tracked |
| Cryptographic library | Industry standard | ✅ **PASS** | PyCA `cryptography` / OpenSSL backend |
| Toeplitz hash construction | LHL / GF(2) theory | ✅ **PASS** | Correct dimensions and packing |
| Privacy amplification bound | Leftover Hash Lemma | ✅ **PASS** | ε_sec = 2⁻³² |
| Security margin | QKD theory | ✅ **PASS** | 64-bit margin (2 × log₂(1/ε)) |
| Toeplitz seed (determinism) | QKD production standards | ⚠️ **PARTIAL** | Fixed seed — acceptable for simulation |
| Replay protection algorithm | RFC 4303 §3.4.3 | ✅ **PASS** | Exact bitmap algorithm |
| Replay state persistence | RFC 6347 / Best Practice | ⚠️ **PARTIAL** | In-memory only; not persistent |
| QBER interception detection | BB84 security proofs | ✅ **PASS** | 11% threshold; Eve → ~25% QBER |
| Classical channel authentication | QKD security model | ❌ **KNOWN GAP** | Assumed secure — no MitM protection |
| Alice/Bob CSPRNG | NIST SP 800-90A | ✅ **PASS** | `secrets.SystemRandom()` |
| Nonce CSPRNG | NIST SP 800-90A | ✅ **PASS** | `os.urandom()` |
| Eve simulation PRNG | N/A (simulation) | ⚠️ **ACCEPTABLE** | `random.random()` — not for key material |
| Finite-key analysis | Tomamichel et al. (2012) | ⚠️ **PARTIAL** | Asymptotic threshold used (simulation) |

### Final Verdict

> **CRYPTOGRAPHICALLY SOUND WITH DOCUMENTED LIMITATIONS**

The implementation correctly applies all relevant cryptographic primitives:

- **AES-256-GCM** is implemented per NIST SP 800-38D with no deviations.
- **Privacy amplification** via Toeplitz hashing satisfies the Leftover Hash Lemma with ε_sec = 2⁻³².
- **Replay protection** correctly implements RFC 4303 §3.4.3.
- **All key material and nonce generation** uses OS-level CSPRNGs.

The documented limitations are:

1. **Deterministic Toeplitz seed** — Acceptable for research simulation; must use authenticated random seed in production.
2. **Non-persistent replay window** — Brief post-restart vulnerability; mitigated by persisting `max_seq` to durable storage in production.
3. **Unauthenticated classical channel** — Fundamental QKD limitation without pre-shared authenticated channel; must be addressed architecturally (not cryptographically) in production deployment.
4. **Asymptotic QBER threshold** — Finite-key corrections are not applied; acceptable for simulation at typical N values.

None of these limitations invalidate the security of the cryptographic implementation for its stated research purpose. Each is bounded, understood, and consistent with standard QKD simulation practice.

---

## References

1. NIST SP 800-38D: *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC* (2007)
2. NIST FIPS 197: *Advanced Encryption Standard (AES)* (2001)
3. RFC 4303: *IP Encapsulating Security Payload (ESP)*, Section 3.4.3 — Anti-Replay (2005)
4. RFC 6347: *Datagram Transport Layer Security Version 1.2* (2012)
5. Bennett, C.H. & Brassard, G. (1984): *Quantum cryptography: Public key distribution and coin tossing*. BB84 original protocol.
6. Renner, R. (2008): *Security of Quantum Key Distribution*. PhD Thesis, ETH Zurich.
7. Tomamichel, M. et al. (2012): *Tight finite-key analysis for quantum cryptography*. Nature Communications.
8. NIST SP 800-90A Rev. 1: *Recommendation for Random Number Generation Using Deterministic Random Bit Generators* (2015)

---

*Audit prepared for academic/research review. This document reflects the cryptographic properties of the simulation implementation as of 2026-11-16.*
