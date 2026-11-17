"""
ADVERSARIAL EVE DETECTION ANALYSIS — TASK 4
100-trial Eve detection study at N=200 and N=1536.

Previously: 1/20 trials at p_eve=1.0, N=200 did NOT abort (QBER=0.0833).
This script runs larger experiments to establish:
  - False-acceptance rate (trials where Eve present but not detected)
  - 95% confidence interval on detection rate
  - Minimum N for guaranteed detection at probability > 0.999

Author: Adversarial verification script — MP2026CSE205
Date: 2026-11-17
"""

import sys
import math
import csv
import statistics
import time

# Ensure the project root is on the path
sys.path.insert(0, ".")

try:
    from qkd.bb84 import BB84Simulator, BB84Result
    QKD_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] Cannot import BB84Simulator: {e}")
    QKD_AVAILABLE = False

def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple:
    """Wilson score 95% confidence interval for proportion."""
    if n == 0:
        return (0.0, 0.0)
    p_hat = successes / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    spread = z * math.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - spread), min(1.0, center + spread))

def theoretical_eve_detection(p_eve: float, N_sifted: int, qber_threshold: float = 0.11) -> float:
    """
    Theoretical probability that Eve is detected given:
    - p_eve: fraction of qubits Eve intercepts
    - N_sifted: number of sifted bits used for QBER estimation sample
    - qber_threshold: abort threshold (default 11% per standard BB84)
    
    Under intercept-resend with probability p_eve:
    - Per-bit error rate introduced: p_eve/4 (each intercept has 50% basis mismatch
      and 50% measurement error)
    - Expected QBER from Eve: q_eve = p_eve * 0.25
    
    P(detected) = P(sample QBER > threshold) which for p_eve=1.0 gives q=0.25,
    and with n_sample bits, this converges rapidly to 1.0.
    """
    q_eve = p_eve * 0.25  # expected QBER from Eve
    if q_eve < qber_threshold:
        return 0.0
    # For large n_sample, detection is near-certain; using binomial approximation
    # P(QBER_sample <= threshold | true_QBER = q_eve) ≈ Chernoff: exp(-2*n*(q-t)^2)
    # This gives detection rate ≈ 1 - exp(-2*n*(q_eve-threshold)^2)
    # This is a lower bound (the actual rate is higher due to two-sided nature)
    n_sample_approx = int(N_sifted * 0.25)  # 25% sample fraction
    delta = q_eve - qber_threshold
    if delta <= 0:
        return 0.0
    p_miss = math.exp(-2 * n_sample_approx * delta**2)
    return 1.0 - p_miss

def run_eve_trials(N: int, p_eve: float, n_trials: int, qber_threshold: float = 0.11) -> dict:
    """Run n_trials of BB84 with Eve and report detection statistics."""
    if not QKD_AVAILABLE:
        return {"error": "BB84Protocol not available"}

    aborted = 0
    not_aborted = 0
    qber_values = []
    sifted_counts = []
    start_time = time.time()

    sim = BB84Simulator()
    for trial_idx in range(n_trials):
        try:
            result = sim.run(
                num_qubits=N,
                enable_eve=True,
                eve_prob=p_eve,
                sample_fraction=0.25,
                threshold=qber_threshold,
                noise_param=0.0,
            )

            qber_val = result.qber if result.qber is not None else 0.0
            qber_values.append(qber_val)
            sifted_counts.append(result.sifted_length if hasattr(result, 'sifted_length') else int(N * 0.5))

            # Detection: is_valid=False means the protocol rejected the key (aborted)
            # Also check if QBER exceeds threshold directly
            if not result.is_valid or qber_val > qber_threshold:
                aborted += 1
            else:
                not_aborted += 1

        except Exception as ex:
            print(f"  [Trial {trial_idx+1}] Exception: {ex}")
            not_aborted += 1  # count as failure to detect (worst case)

    elapsed = time.time() - start_time

    detection_rate = aborted / n_trials if n_trials > 0 else 0.0
    ci_low, ci_high = wilson_ci(aborted, n_trials)
    theoretical = theoretical_eve_detection(p_eve, 
                    int(statistics.mean(sifted_counts)) if sifted_counts else int(N * 0.5))

    return {
        "N": N,
        "p_eve": p_eve,
        "n_trials": n_trials,
        "aborted": aborted,
        "not_aborted": not_aborted,
        "detection_rate": round(detection_rate, 4),
        "false_acceptance_rate": round(1 - detection_rate, 4),
        "ci_95_low": round(ci_low, 4),
        "ci_95_high": round(ci_high, 4),
        "mean_qber": round(statistics.mean(qber_values), 4) if qber_values else None,
        "std_qber": round(statistics.stdev(qber_values), 4) if len(qber_values) > 1 else None,
        "min_qber": round(min(qber_values), 4) if qber_values else None,
        "max_qber": round(max(qber_values), 4) if qber_values else None,
        "mean_sifted": round(statistics.mean(sifted_counts), 1) if sifted_counts else None,
        "theoretical_detection_rate": round(theoretical, 4),
        "elapsed_seconds": round(elapsed, 2),
    }

print("=" * 72)
print("ADVERSARIAL EVE DETECTION ANALYSIS")
print("Task 4 — Statistical Eve Detection Rate with Confidence Intervals")
print("Project MP2026CSE205 — Graphic Era (Deemed to be University)")
print("=" * 72)

all_results = []

if not QKD_AVAILABLE:
    print("[BLOCKER] BB84Simulator import failed — cannot run live trials.")
    print("Recording as TASK-4-BLOCKED.")
    sys.exit(1)

# Configuration
EXPERIMENTS = [
    {"N": 200,  "p_eve": 1.0, "n_trials": 100, "label": "N=200,  p_eve=1.0 (100 trials)"},
    {"N": 200,  "p_eve": 0.5, "n_trials": 50,  "label": "N=200,  p_eve=0.5 (50 trials)"},
    {"N": 1536, "p_eve": 1.0, "n_trials": 50,  "label": "N=1536, p_eve=1.0 (50 trials)"},
    {"N": 1024, "p_eve": 1.0, "n_trials": 50,  "label": "N=1024, p_eve=1.0 (50 trials)"},
    {"N": 200,  "p_eve": 1.0, "n_trials": 20,  "label": "N=200,  p_eve=1.0 (20 trials — replicate prior)"},
]

for exp in EXPERIMENTS:
    print(f"\n[Running] {exp['label']} ...")
    result = run_eve_trials(exp["N"], exp["p_eve"], exp["n_trials"])
    all_results.append(result)

    print(f"  Detection rate: {result['detection_rate']:.4f} ({result['aborted']}/{result['n_trials']})")
    print(f"  False-acceptance rate: {result['false_acceptance_rate']:.4f}")
    print(f"  95% CI: [{result['ci_95_low']:.4f}, {result['ci_95_high']:.4f}]")
    print(f"  Theoretical detection rate: {result['theoretical_detection_rate']:.4f}")
    print(f"  Mean QBER: {result['mean_qber']} ± {result['std_qber']}")
    print(f"  QBER range: [{result['min_qber']}, {result['max_qber']}]")
    print(f"  Elapsed: {result['elapsed_seconds']}s")

# Summary
print(f"\n{'='*72}")
print("SUMMARY TABLE")
print(f"{'='*72}")
print(f"{'Config':<35} {'Det%':>6} {'FAR%':>6} {'95% CI':>18} {'Theory':>8}")
for r in all_results:
    label = f"N={r['N']}, p_eve={r['p_eve']}, n={r['n_trials']}"
    ci = f"[{r['ci_95_low']:.3f},{r['ci_95_high']:.3f}]"
    print(f"  {label:<33} {r['detection_rate']*100:6.1f} {r['false_acceptance_rate']*100:6.1f} {ci:>18} {r['theoretical_detection_rate']*100:7.1f}%")

# Save CSV
csv_path = "adversarial_eve_analysis.csv"
with open(csv_path, "w", newline="") as f_csv:
    if all_results:
        fieldnames = list(all_results[0].keys())
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

print(f"\n[CSV written: {csv_path}]")
print("\nADVERSARIAL EVE ANALYSIS COMPLETE.")
