"""
ADVERSARIAL REPRODUCIBILITY REPLICATION — TASK 3
Independent reproduction of circuit trials with fresh random seeds.
Saves all individual trial records to CSV for complete provenance.

Trials executed:
  - Phase A1: N=1024, clean channel, 10 trials
  - Phase A2: N=1536, clean channel, 5 trials
  - Phase A3: N=200, Eve p=1.0, 20 trials
  - Phase A4: N=200, clean channel, 10 trials
Total: 45 circuit trials.

Author: Adversarial Verification Cycle — MP2026CSE205
Date: 2026-11-17
"""

import sys
import os
import time
import datetime
import statistics
import csv
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qkd.bb84 import BB84Simulator

print("=" * 70)
print("TASK 3: INDEPENDENT 45-CIRCUIT REPRODUCIBILITY REPLICATION")
print(f"Timestamp: {datetime.datetime.now().isoformat()}")
print(f"Python: {sys.version}")
print("=" * 70)

sim = BB84Simulator()
records = []

# --- A1: N=1024, clean channel (10 trials) ---
print("\n[Phase A1] N=1024 Clean Channel (10 trials)...")
for t in range(1, 11):
    t0 = time.time()
    res = sim.run(num_qubits=1024, enable_eve=False, noise_param=0.0)
    dur = (time.time() - t0) * 1000

    h_qber = -res.qber * math.log2(res.qber) - (1-res.qber) * math.log2(1-res.qber) if 0 < res.qber < 1 else 0.0
    lhl = max(0, res.reconciled_length * (1.0 - h_qber) - res.ec_leakage_bits - 64)
    derived = (res.alice_key is not None and len(res.alice_key) == 32)

    rec = {
        "suite": "A1_N1024_clean",
        "trial": t,
        "num_qubits": 1024,
        "eve_prob": 0.0,
        "noise_param": 0.0,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": round(res.qber, 6),
        "ec_leakage": res.ec_leakage_bits,
        "lhl_extractable": round(lhl, 1),
        "is_valid": res.is_valid,
        "key_derived_256": derived,
        "keys_match": (res.alice_key == res.bob_key) if res.alice_key else False,
        "elapsed_ms": round(dur, 2)
    }
    records.append(rec)
    print(f"  T{t:2d}: sifted={res.sifted_length}, reconciled={res.reconciled_length}, "
          f"qber={res.qber:.4f}, lhl={lhl:.1f}, 256bit={derived}, dur={dur:.1f}ms")

# --- A2: N=1536, clean channel (5 trials) ---
print("\n[Phase A2] N=1536 Clean Channel (5 trials)...")
for t in range(1, 6):
    t0 = time.time()
    res = sim.run(num_qubits=1536, enable_eve=False, noise_param=0.0)
    dur = (time.time() - t0) * 1000

    h_qber = -res.qber * math.log2(res.qber) - (1-res.qber) * math.log2(1-res.qber) if 0 < res.qber < 1 else 0.0
    lhl = max(0, res.reconciled_length * (1.0 - h_qber) - res.ec_leakage_bits - 64)
    derived = (res.alice_key is not None and len(res.alice_key) == 32)

    rec = {
        "suite": "A2_N1536_clean",
        "trial": t,
        "num_qubits": 1536,
        "eve_prob": 0.0,
        "noise_param": 0.0,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": round(res.qber, 6),
        "ec_leakage": res.ec_leakage_bits,
        "lhl_extractable": round(lhl, 1),
        "is_valid": res.is_valid,
        "key_derived_256": derived,
        "keys_match": (res.alice_key == res.bob_key) if res.alice_key else False,
        "elapsed_ms": round(dur, 2)
    }
    records.append(rec)
    print(f"  T{t:2d}: sifted={res.sifted_length}, reconciled={res.reconciled_length}, "
          f"qber={res.qber:.4f}, lhl={lhl:.1f}, 256bit={derived}, dur={dur:.1f}ms")

# --- A3: N=200, Eve p=1.0 (20 trials) ---
print("\n[Phase A3] N=200 Eve p=1.0 (20 trials)...")
for t in range(1, 21):
    t0 = time.time()
    res = sim.run(num_qubits=200, enable_eve=True, eve_prob=1.0, noise_param=0.0)
    dur = (time.time() - t0) * 1000

    rec = {
        "suite": "A3_N200_eve1.0",
        "trial": t,
        "num_qubits": 200,
        "eve_prob": 1.0,
        "noise_param": 0.0,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": round(res.qber, 6),
        "ec_leakage": res.ec_leakage_bits,
        "lhl_extractable": 0.0,
        "is_valid": res.is_valid,
        "key_derived_256": (res.alice_key is not None and len(res.alice_key) == 32),
        "keys_match": (res.alice_key == res.bob_key) if res.alice_key else False,
        "elapsed_ms": round(dur, 2)
    }
    records.append(rec)
    print(f"  T{t:2d}: qber={res.qber:.4f}, aborted={not res.is_valid}, dur={dur:.1f}ms")

# --- A4: N=200, clean channel (10 trials) ---
print("\n[Phase A4] N=200 Clean Channel (10 trials)...")
for t in range(1, 11):
    t0 = time.time()
    res = sim.run(num_qubits=200, enable_eve=False, noise_param=0.0)
    dur = (time.time() - t0) * 1000

    rec = {
        "suite": "A4_N200_clean",
        "trial": t,
        "num_qubits": 200,
        "eve_prob": 0.0,
        "noise_param": 0.0,
        "sifted": res.sifted_length,
        "reconciled": res.reconciled_length,
        "qber": round(res.qber, 6),
        "ec_leakage": res.ec_leakage_bits,
        "lhl_extractable": 0.0,
        "is_valid": res.is_valid,
        "key_derived_256": (res.alice_key is not None and len(res.alice_key) == 32),
        "keys_match": (res.alice_key == res.bob_key) if res.alice_key else False,
        "elapsed_ms": round(dur, 2)
    }
    records.append(rec)
    print(f"  T{t:2d}: qber={res.qber:.4f}, is_valid={res.is_valid}, dur={dur:.1f}ms")

# Write CSV
csv_out = "adversarial_repro_results.csv"
fieldnames = list(records[0].keys())
with open(csv_out, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

print("\n" + "=" * 70)
print(f"TASK 3 COMPLETE: {len(records)} trials recorded to {csv_out}")
print("=" * 70)
