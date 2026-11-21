"""
EMPIRICAL EVE DETECTION STATISTICS VERIFICATION
Comprehensive verification of Eve detection statistics across block sizes and interception probabilities.
Calculates:
  - Empirical Detection Rate
  - False Acceptance Rate (FAR)
  - Wilson Score 95% Confidence Intervals
  - Clopper-Pearson Exact 95% Confidence Intervals
  - Empirical QBER mean, std, min, max
  - Theoretical Detection Probability from Binomial tail
  - Block size (N) and Interception probability (p_eve) dependence
"""

import sys
import math
import csv
import statistics
import time
from typing import Dict, List, Tuple

# Ensure project root is in python path
sys.path.insert(0, ".")

from qkd.bb84 import BB84Simulator

def wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Computes Wilson score interval for binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    # z for 95% is 1.95996
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0.0, center - margin), min(1.0, center + margin))

def clopper_pearson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Computes exact Clopper-Pearson confidence interval via Beta distribution / F-distribution."""
    if n == 0:
        return (0.0, 0.0)
    try:
        from scipy.stats import beta
        alpha = 1.0 - confidence
        lower = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
        upper = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
        return (float(lower), float(upper))
    except ImportError:
        # Fallback to Wilson if scipy not available
        return wilson_ci(k, n, confidence)

def theoretical_p_detect(p_eve: float, N: int, threshold: float = 0.11, sample_frac: float = 0.25) -> float:
    """
    Theoretical probability that sample QBER exceeds threshold under intercept-resend.
    Expected sifted length: n_sifted = N * 0.5.
    Sample size: n_sample = int(n_sifted * sample_frac) = int(N * 0.125).
    Each sampled bit has error probability p_err = p_eve * 0.25.
    Number of errors K ~ Binomial(n_sample, p_err).
    P(detect) = P(K / n_sample > threshold) = P(K > floor(n_sample * threshold)).
    """
    n_sample = max(1, int((N * 0.5) * sample_frac))
    p_err = p_eve * 0.25
    k_thresh = int(math.floor(n_sample * threshold))
    
    # Cumulative probability sum P(K <= k_thresh)
    p_accept = 0.0
    for k in range(0, k_thresh + 1):
        # binom coeff
        comb = math.comb(n_sample, k)
        term = comb * (p_err**k) * ((1.0 - p_err)**(n_sample - k))
        p_accept += term
    
    p_detect = max(0.0, min(1.0, 1.0 - p_accept))
    return p_detect

def run_evaluation_grid() -> List[Dict]:
    sim = BB84Simulator()
    
    # Grid of parameters
    grid = [
        # Small N (N=200): examine high FAR and sample size variance
        {"N": 200, "p_eve": 0.0, "trials": 30},
        {"N": 200, "p_eve": 0.2, "trials": 30},
        {"N": 200, "p_eve": 0.5, "trials": 50},
        {"N": 200, "p_eve": 0.8, "trials": 50},
        {"N": 200, "p_eve": 1.0, "trials": 100},
        
        # Intermediate N (N=512):
        {"N": 512, "p_eve": 0.5, "trials": 30},
        {"N": 512, "p_eve": 1.0, "trials": 40},
        
        # Production N (N=1024):
        {"N": 1024, "p_eve": 0.0, "trials": 20},
        {"N": 1024, "p_eve": 0.5, "trials": 30},
        {"N": 1024, "p_eve": 1.0, "trials": 40},
        
        # Recommended N (N=1536):
        {"N": 1536, "p_eve": 0.0, "trials": 15},
        {"N": 1536, "p_eve": 0.5, "trials": 25},
        {"N": 1536, "p_eve": 1.0, "trials": 30},
    ]
    
    results = []
    print(f"{'Config':<25} {'Trials':>6} {'Aborted':>7} {'Det Rate':>9} {'FAR':>8} {'95% Wilson CI':>20} {'Theory Det':>10}")
    print("-" * 92)
    
    for cfg in grid:
        N = cfg["N"]
        p_eve = cfg["p_eve"]
        n_trials = cfg["trials"]
        
        aborted = 0
        qber_list = []
        sifted_list = []
        sample_size_list = []
        
        t0 = time.time()
        for t in range(n_trials):
            res = sim.run(
                num_qubits=N,
                enable_eve=(p_eve > 0.0),
                eve_prob=p_eve,
                sample_fraction=0.25,
                threshold=0.11,
                noise_param=0.0
            )
            q = res.qber if res.qber is not None else 0.0
            qber_list.append(q)
            sifted_list.append(res.sifted_length)
            
            # Protocol aborts when is_valid is False or qber > 0.11
            if (not res.is_valid) or (q > 0.11):
                aborted += 1
                
        elapsed = time.time() - t0
        det_rate = aborted / n_trials
        far = 1.0 - det_rate
        w_low, w_high = wilson_ci(aborted, n_trials)
        cp_low, cp_high = clopper_pearson_ci(aborted, n_trials)
        th_det = theoretical_p_detect(p_eve, N, threshold=0.11, sample_frac=0.25)
        
        mean_q = statistics.mean(qber_list)
        std_q = statistics.stdev(qber_list) if len(qber_list) > 1 else 0.0
        
        label = f"N={N}, p_eve={p_eve:.1f}"
        ci_str = f"[{w_low*100:.1f}%, {w_high*100:.1f}%]"
        print(f"{label:<25} {n_trials:>6} {aborted:>7} {det_rate*100:>8.1f}% {far*100:>7.1f}% {ci_str:>20} {th_det*100:>9.1f}%")
        
        row = {
            "N": N,
            "p_eve": p_eve,
            "trials": n_trials,
            "aborted": aborted,
            "not_aborted": n_trials - aborted,
            "detection_rate": round(det_rate, 4),
            "false_acceptance_rate": round(far, 4),
            "wilson_ci_low": round(w_low, 4),
            "wilson_ci_high": round(w_high, 4),
            "clopper_pearson_low": round(cp_low, 4),
            "clopper_pearson_high": round(cp_high, 4),
            "theoretical_detection_prob": round(th_det, 4),
            "mean_qber": round(mean_q, 4),
            "std_qber": round(std_q, 4),
            "min_qber": round(min(qber_list), 4),
            "max_qber": round(max(qber_list), 4),
            "mean_sifted": round(statistics.mean(sifted_list), 1),
            "mean_sample_size": round(statistics.mean(sifted_list) * 0.25, 1),
            "elapsed_sec": round(elapsed, 2)
        }
        results.append(row)
        
    return results

if __name__ == "__main__":
    out_csv = "empirical_eve_detection_verified.csv"
    res = run_evaluation_grid()
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        writer.writeheader()
        writer.writerows(res)
    print(f"\nSaved empirical Eve detection verification to {out_csv}")
