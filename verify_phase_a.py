# -*- coding: utf-8 -*-
"""
Phase A: N=1024 LHL Investigation + Eve QBER Verification + Channel Noise Test
Timestamp evidence collection for EXPERIMENT_REPRODUCIBILITY_REPORT
"""
import sys
import os
import time
import datetime
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print(f"PHASE A SCIENTIFIC VERIFICATION SCRIPT")
print(f"Timestamp: {datetime.datetime.now().isoformat()}")
print(f"Python: {sys.version}")
print("=" * 70)

from qkd.bb84 import BB84Simulator
from qkd.postprocessing.privacy_amplification import PrivacyAmplifier
import math

sim = BB84Simulator()

# ===================================================================
# INVESTIGATION 1: N=1024 LHL Consistency Check
# Previous reports claimed ~385.2 reconciled bits but LHL requires
# ~435 bits for 256-bit key. Let's verify with 10 actual runs.
# ===================================================================
print("\n--- INVESTIGATION 1: N=1024 LHL Consistency (10 trials) ---")
n1024_results = []
for trial in range(1, 11):
    res = sim.run(num_qubits=1024, enable_eve=False)
    
    # Manually compute LHL-extractable bits
    h_qber = -res.qber * math.log2(res.qber) - (1-res.qber) * math.log2(1-res.qber) if 0 < res.qber < 1 else 0.0
    theoretical_capacity = res.reconciled_length * (1.0 - h_qber) if res.reconciled_length > 0 else 0.0
    lhl_extractable = max(0, theoretical_capacity - res.ec_leakage_bits - 64)  # 64 = 2*32 security margin
    key_256_possible = lhl_extractable >= 256
    key_derived_256 = res.alice_key is not None and len(res.alice_key) == 32
    
    row = {
        "trial": trial,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": res.qber,
        "ec_leak": res.ec_leakage_bits,
        "lhl_extractable": lhl_extractable,
        "key_256_possible": key_256_possible,
        "key_derived_256": key_derived_256,
        "is_valid": res.is_valid
    }
    n1024_results.append(row)
    print(f"  T{trial:2d}: sifted={res.sifted_length:4d}, reconciled={res.reconciled_length:4d}, "
          f"qber={res.qber:.4f}, ec_leak={res.ec_leakage_bits:4d}, "
          f"lhl_extractable={lhl_extractable:.1f}, 256bit_ok={key_256_possible}, "
          f"key_derived={key_derived_256}")

sifted_vals = [r["sifted"] for r in n1024_results]
recon_vals = [r["reconciled"] for r in n1024_results]
lhl_vals = [r["lhl_extractable"] for r in n1024_results]
print(f"\n  N=1024 Statistics:")
print(f"    Sifted:     mean={statistics.mean(sifted_vals):.1f}, std={statistics.stdev(sifted_vals):.1f}")
print(f"    Reconciled: mean={statistics.mean(recon_vals):.1f}, std={statistics.stdev(recon_vals):.1f}")
print(f"    LHL Extractable: mean={statistics.mean(lhl_vals):.1f}, std={statistics.stdev(lhl_vals):.1f}")
print(f"    256-bit key possible: {sum(r['key_256_possible'] for r in n1024_results)}/10")
print(f"    256-bit key derived:  {sum(r['key_derived_256'] for r in n1024_results)}/10")

# ===================================================================
# INVESTIGATION 2: N=1536 Verification (5 trials)
# Verify the production default correctly yields 256-bit keys
# ===================================================================
print("\n--- INVESTIGATION 2: N=1536 Production Default (5 trials) ---")
n1536_results = []
for trial in range(1, 6):
    t0 = time.time()
    res = sim.run(num_qubits=1536, enable_eve=False)
    elapsed = (time.time() - t0) * 1000
    
    h_qber = -res.qber * math.log2(res.qber) - (1-res.qber) * math.log2(1-res.qber) if 0 < res.qber < 1 else 0.0
    lhl_extractable = max(0, res.reconciled_length * (1.0 - h_qber) - res.ec_leakage_bits - 64)
    
    n1536_results.append({
        "trial": trial,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": res.qber,
        "lhl_extractable": lhl_extractable,
        "key_derived_256": res.alice_key is not None and len(res.alice_key) == 32,
        "keys_match": res.alice_key == res.bob_key,
        "elapsed_ms": elapsed
    })
    print(f"  T{trial}: sifted={res.sifted_length}, reconciled={res.reconciled_length}, "
          f"qber={res.qber:.4f}, lhl_extractable={lhl_extractable:.1f}, "
          f"256bit_key={res.alice_key is not None}, keys_match={res.alice_key==res.bob_key}, "
          f"elapsed_ms={elapsed:.1f}")

# ===================================================================
# INVESTIGATION 3: Eve intercept-resend QBER verification
# Theoretical: full intercept (p_eve=1.0) → QBER ≈ 0.25
# ===================================================================
print("\n--- INVESTIGATION 3: Eve QBER at p_eve=1.0 (20 trials, N=200) ---")
eve_qbers = []
for trial in range(1, 21):
    res_eve = sim.run(num_qubits=200, enable_eve=True, eve_prob=1.0, noise_param=0.0)
    eve_qbers.append(res_eve.qber)
    print(f"  T{trial:2d}: qber={res_eve.qber:.4f}, aborted={not res_eve.is_valid}")

valid_qbers = [q for q in eve_qbers if q > 0]
print(f"\n  Eve QBER Statistics (p_eve=1.0, N=200, 20 trials):")
print(f"    Mean QBER:   {statistics.mean(eve_qbers):.4f}")
print(f"    Std QBER:    {statistics.stdev(eve_qbers):.4f}")
print(f"    Theoretical: ~0.25")
print(f"    Abort rate (QBER > 0.11): {sum(1 for q in eve_qbers if q > 0.11)}/20")

# ===================================================================
# INVESTIGATION 4: Clean channel QBER = 0 verification
# No Eve, no noise → QBER should be 0.0
# ===================================================================
print("\n--- INVESTIGATION 4: Clean Channel (no Eve, no noise, 10 trials, N=200) ---")
clean_qbers = []
for trial in range(1, 11):
    res_clean = sim.run(num_qubits=200, enable_eve=False, noise_param=0.0)
    clean_qbers.append(res_clean.qber)
    print(f"  T{trial:2d}: qber={res_clean.qber:.4f}, is_valid={res_clean.is_valid}")

print(f"\n  Clean channel QBER: all_zero={all(q == 0.0 for q in clean_qbers)}")
print(f"  QBER values: {clean_qbers}")

# ===================================================================
# INVESTIGATION 5: Channel noise (depolarizing p=0.04)
# Expected: QBER ≈ 0.02-0.03 for depolarizing p=0.04
# ===================================================================
print("\n--- INVESTIGATION 5: Channel Noise (noise_param=0.04, 10 trials, N=400) ---")
noisy_qbers = []
for trial in range(1, 11):
    res_noise = sim.run(num_qubits=400, enable_eve=False, noise_param=0.04)
    noisy_qbers.append(res_noise.qber)
    print(f"  T{trial:2d}: qber={res_noise.qber:.4f}")

valid_noisy = [q for q in noisy_qbers if q > 0]
print(f"\n  Noisy channel QBER (p=0.04):")
print(f"    Mean: {statistics.mean(noisy_qbers):.4f}")
if len(noisy_qbers) > 1:
    print(f"    Std:  {statistics.stdev(noisy_qbers):.4f}")
print(f"    Theoretical for uniform depolarizing p=0.04: QBER ≈ p*(2/3) ≈ {0.04*2/3:.4f}")

print("\n" + "=" * 70)
print(f"PHASE A VERIFICATION COMPLETE: {datetime.datetime.now().isoformat()}")
print("=" * 70)
