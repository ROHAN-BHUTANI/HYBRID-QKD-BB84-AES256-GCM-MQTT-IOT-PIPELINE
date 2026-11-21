"""
INDEPENDENT FINITE-KEY SECURITY DERIVATION AND VERIFICATION
BB84 QKD Implementation in ROHAN-BHUTANI/HYBRID-QKD-BB84-AES256-GCM-MQTT-IOT-PIPELINE

Establish:
1. Parameter-estimation procedure.
2. Phase-error upper confidence bound.
3. Finite-size statistical correction.
4. Error-correction leakage.
5. Error-verification leakage.
6. Privacy-amplification security parameter.
7. Authentication assumptions.
8. Final extractable secret-key length.
9. Verification of reported 160-bit correction.
10. Minimum required block size N for certified security.
"""

import math
import csv
from typing import Dict, List

def h2(p: float) -> float:
    """Binary Shannon entropy function."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)

def serfling_bound(N_pop: int, n_sample: int, epsilon_pe: float) -> float:
    """
    Serfling inequality for sampling without replacement from a finite population.
    Computes delta such that:
      Pr(e_phase > q_sample + delta) <= epsilon_pe
    Formula:
      delta = sqrt( ((N_pop - n_sample + 1) / (2 * n_sample * N_pop)) * ln(1 / epsilon_pe) )
    """
    if N_pop <= n_sample or n_sample <= 0:
        return float('inf')
    factor = (N_pop - n_sample + 1) / (2.0 * n_sample * N_pop)
    return math.sqrt(factor * math.log(1.0 / epsilon_pe))

def hoeffding_bound(n_sample: int, epsilon_pe: float) -> float:
    """
    Hoeffding's inequality for bounded random variables (sampling with replacement or i.i.d.):
      delta = sqrt( ln(1 / epsilon_pe) / (2 * n_sample) )
    """
    if n_sample <= 0:
        return float('inf')
    return math.sqrt(math.log(1.0 / epsilon_pe) / (2.0 * n_sample))

def evaluate_finite_key_spectrum():
    print("=" * 80)
    print("INDEPENDENT FINITE-KEY SECURITY DERIVATION — DETAILED BREAKDOWN")
    print("=" * 80)
    
    # Standard security parameters for composable security
    eps_sec = 2**-32     # Leftover Hash Lemma smoothing failure parameter
    eps_pe = 2**-32      # Parameter estimation statistical failure parameter
    eps_hash = 2**-32    # Wegman-Carter error verification collision parameter
    eps_cor = eps_hash   # Correctness parameter
    
    # Subtractive margin breakdown:
    # Term 1: LHL smoothing margin = 2 * log2(1 / eps_sec) = 2 * 32 = 64 bits
    margin_lhl = 2.0 * math.log2(1.0 / eps_sec)
    
    # Term 2: Parameter estimation security margin = 2 * log2(1 / eps_pe) = 2 * 32 = 64 bits
    # (used in additive composability models e.g., Scarani & Renner 2008 / Tomamichel 2012)
    margin_pe = 2.0 * math.log2(1.0 / eps_pe)
    
    # Term 3: Error-verification hash leakage = log2(1 / eps_hash) = 32 bits
    margin_hash = math.log2(1.0 / eps_hash)
    
    # Total additive margin = 64 + 64 + 32 = 160 bits
    total_margin_160 = margin_lhl + margin_pe + margin_hash
    
    print(f"\n[1. Security Parameters (Composable Security Framework)]")
    print(f"  eps_sec   = 2^-32 = {eps_sec:.2e}  -> Margin 2*log2(1/eps_sec)   = {margin_lhl:.1f} bits")
    print(f"  eps_pe    = 2^-32 = {eps_pe:.2e}  -> Margin 2*log2(1/eps_pe)    = {margin_pe:.1f} bits")
    print(f"  eps_hash  = 2^-32 = {eps_hash:.2e}  -> Margin log2(1/eps_hash)    = {margin_hash:.1f} bits")
    print(f"  Total additive correction (reported heuristic): {total_margin_160:.1f} bits")
    print(f"  Codebase currently implemented margin:          {margin_lhl:.1f} bits (64 bits only)")
    print(f"  Discrepancy in additive terms:                  {total_margin_160 - margin_lhl:.1f} bits missing")

    # Now evaluate for various block sizes N under QBER = 0.0 and QBER = 0.04
    block_sizes = [256, 512, 1024, 1536, 2048, 3072, 4096, 6144, 8192, 12288, 16384, 32768]
    
    rows = []
    
    for N in block_sizes:
        # Step 1: Sifting (50% expected efficiency)
        n_sift = N // 2
        # Step 2: Parameter estimation sample (25% sample fraction)
        n_sample = int(n_sift * 0.25)
        # Step 3: Remaining raw key material
        m = n_sift - n_sample
        
        # Statistical confidence bounds on phase error
        delta_serf = serfling_bound(n_sift, n_sample, eps_pe)
        delta_hoeff = hoeffding_bound(n_sample, eps_pe)
        
        for q_obs in [0.0, 0.02, 0.04]:
            # Codebase implemented formula:
            # l_impl = floor( m * [1 - h2(q_obs)] - leak_EC - 64 )
            leak_ec_impl = 0.0 if q_obs == 0.0 else 1.16 * m * h2(q_obs)
            l_impl = max(0, math.floor(m * (1.0 - h2(q_obs)) - leak_ec_impl - margin_lhl))
            
            # Conservative finite-key formula with Serfling bound:
            # Worst-case phase error
            q_cons = min(0.5, q_obs + delta_serf)
            h_q_cons = h2(q_cons)
            # Reconciled min-entropy capacity
            leak_ec_cons = 0.0 if q_obs == 0.0 else 1.16 * m * h2(q_obs)
            raw_secure_finite = m * (1.0 - h_q_cons) - leak_ec_cons - total_margin_160
            l_finite = max(0, math.floor(raw_secure_finite))
            
            # Heuristic with observed QBER but 160-bit subtractive margin (WITHOUT delta_PE penalty)
            raw_160_nodelta = m * (1.0 - h2(q_obs)) - leak_ec_cons - total_margin_160
            l_160_nodelta = max(0, math.floor(raw_160_nodelta))
            
            rows.append({
                "N": N,
                "n_sift": n_sift,
                "n_sample": n_sample,
                "m_remaining": m,
                "q_observed": q_obs,
                "delta_serfling": round(delta_serf, 4),
                "q_conservative": round(q_cons, 4),
                "h2_q_conservative": round(h_q_cons, 4),
                "leak_ec_bits": round(leak_ec_cons, 1),
                "l_codebase_impl": l_impl,
                "l_heuristic_160_nodelta": l_160_nodelta,
                "l_hypothetical_composable": l_finite,
                "codebase_can_aes256": (l_impl >= 256),
                "hypothetical_can_aes256": (l_finite >= 256)
            })

    # Save to CSV
    csv_file = "finite_key_derivation_spectrum.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved finite-key spectrum to {csv_file}")
    
    # Print comparison table for key operational scales
    print("\n" + "=" * 105)
    print(f"{'N':>6} {'QBER':>6} {'m':>5} {'n_PE':>5} {'delta_PE':>9} {'Q_cons':>7} {'l_impl':>8} {'l_160(no-d)':>12} {'l_hypothetical':>16} {'AES256 Model?':>15}")
    print("=" * 105)
    for r in rows:
        if r["N"] in [512, 1024, 1536, 2048, 3072, 4096, 8192, 16384]:
            cert_str = "YES (>=256)" if r["hypothetical_can_aes256"] else "NO (<256)"
            print(f"{r['N']:6d} {r['q_observed']:6.2f} {r['m_remaining']:5d} {r['n_sample']:5d} "
                  f"{r['delta_serfling']:9.4f} {r['q_conservative']:7.4f} {r['l_codebase_impl']:8d} "
                  f"{r['l_heuristic_160_nodelta']:12d} {r['l_hypothetical_composable']:16d} {cert_str:>15}")
    print("=" * 105)

if __name__ == "__main__":
    evaluate_finite_key_spectrum()
