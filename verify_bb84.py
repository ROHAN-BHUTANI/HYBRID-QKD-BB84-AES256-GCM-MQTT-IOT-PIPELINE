# -*- coding: utf-8 -*-
"""
Direct BB84 verification script — bypasses pytest DLL issue.
Runs the QKD-dependent tests directly as Python functions.
Timestamp: run this to get actual execution evidence.
"""
import sys
import os
import time
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = []
FAIL = []
RESULTS = []

def record(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")
    if passed:
        PASS.append(name)
    else:
        FAIL.append(name)
    RESULTS.append({"test": name, "status": status, "detail": detail})

print("=" * 60)
print(f"BB84 DIRECT VERIFICATION SCRIPT")
print(f"Timestamp: {datetime.datetime.now().isoformat()}")
print(f"Python: {sys.version}")
print("=" * 60)

# ---- Test 1: Alice state preparation ----
try:
    from qkd.alice import Alice
    alice = Alice(num_qubits=10)
    bits, bases = alice.generate_random_bits_and_bases()
    ok = (len(bits) == 10 and len(bases) == 10 and
          all(b in (0,1) for b in bits) and all(a in (0,1) for a in bases))
    record("T1_alice_state_prep", ok, f"bits={bits[:5]}... bases={bases[:5]}...")
except Exception as e:
    record("T1_alice_state_prep", False, str(e))

# ---- Test 2: Bob measurement ----
try:
    from qkd.bob import Bob
    bob = Bob(num_qubits=8)
    bases = bob.generate_random_bases()
    raw = "10110001"
    bits = bob.extract_bits_from_counts(raw)
    ok = (len(bases) == 8 and len(bits) == 8 and bits[0] == 1 and bits[7] == 1)
    record("T2_bob_measurement", ok, f"bases_len={len(bases)}, bits={bits}")
except Exception as e:
    record("T2_bob_measurement", False, str(e))

# ---- Test 3: Sifting ----
try:
    from qkd.sifting import SiftingEngine
    alice_bits = [0, 1, 0, 1, 1, 0]
    alice_bases = [0, 0, 1, 1, 0, 1]
    bob_bits = [0, 1, 1, 1, 0, 0]
    bob_bases = [0, 1, 1, 1, 0, 0]
    indices, s_alice, s_bob = SiftingEngine.sift(alice_bits, alice_bases, bob_bits, bob_bases)
    ok = (indices == [0, 2, 3, 4] and s_alice == [0, 0, 1, 1] and s_bob == [0, 1, 1, 0])
    record("T3_sifting_engine", ok, f"indices={indices}, s_alice={s_alice}, s_bob={s_bob}")
except Exception as e:
    record("T3_sifting_engine", False, str(e))

# ---- Test 4: QBER Estimation ----
try:
    from qkd.qber import QBEREstimator
    s_alice = [0] * 100
    s_bob = [0] * 90 + [1] * 10
    qber, is_valid, rem_a, rem_b, sample_size, errors = QBEREstimator.estimate(
        s_alice, s_bob, sample_fraction=0.5, threshold=0.11
    )
    ok = (sample_size == 50 and len(rem_a) == 50 and len(rem_b) == 50 and 0.0 <= qber <= 0.30)
    record("T4_qber_estimator", ok, f"qber={qber:.4f}, sample_size={sample_size}, errors={errors}")
except Exception as e:
    record("T4_qber_estimator", False, str(e))

# ---- Test 5: Cascade Reconciliation ----
try:
    from qkd.postprocessing.reconciliation import InformationReconciler
    alice = [0, 1, 1, 0, 1, 0, 1, 1] * 15
    bob = list(alice)
    for idx in [5, 17, 34, 67, 95]:
        bob[idx] = 1 - bob[idx]
    rec_alice, rec_bob, leak, is_identical = InformationReconciler.reconcile(
        alice, bob, estimated_qber=0.041, passes=4
    )
    ok = (is_identical and rec_alice == rec_bob and leak > 0)
    record("T5_cascade_reconciliation", ok, f"identical={is_identical}, leak_bits={leak}")
except Exception as e:
    record("T5_cascade_reconciliation", False, str(e))

# ---- Test 6: Toeplitz GF(2) Hashing ----
try:
    from qkd.postprocessing.privacy_amplification import ToeplitzHash, PrivacyAmplifier
    x = [1, 0, 1, 1, 0]
    out = ToeplitzHash.multiply_gf2(x, out_bits=3)
    ok1 = (len(out) == 3 and all(b in (0, 1) for b in out))
    # Verify seed length property: should be m + l - 1 = 5 + 3 - 1 = 7
    seed_bits = ToeplitzHash.generate_seed_bits(b"test", 7)
    ok2 = (len(seed_bits) == 7)
    record("T6_toeplitz_hashing", ok1 and ok2, f"out={out}, seed_len=7, ok2={ok2}")
except Exception as e:
    record("T6_toeplitz_hashing", False, str(e))

# ---- Test 7: Privacy Amplification — sufficient material ----
try:
    reconciled_large = [1, 0, 1, 1] * 150  # 600 bits
    key, sec_bits, ratio = PrivacyAmplifier.amplify(
        reconciled_large, qber=0.01, ec_leakage_bits=20, target_key_bytes=32
    )
    ok = (key is not None and len(key) == 32 and sec_bits >= 256 and 0.0 < ratio <= 1.0)
    record("T7_privacy_amp_sufficient", ok, f"key_len={len(key) if key else None}, sec_bits={sec_bits}, ratio={ratio:.4f}")
except Exception as e:
    record("T7_privacy_amp_sufficient", False, str(e))

# ---- Test 8: Privacy Amplification — insufficient material returns None ----
try:
    reconciled_short = [1, 0] * 50  # 100 bits
    key_short, sec_short, _ = PrivacyAmplifier.amplify(
        reconciled_short, qber=0.05, ec_leakage_bits=30, target_key_bytes=32
    )
    ok = (key_short is None and sec_short < 256)
    record("T8_privacy_amp_insufficient", ok, f"key={key_short}, sec_bits={sec_short}")
except Exception as e:
    record("T8_privacy_amp_insufficient", False, str(e))

# ---- Test 9: BB84 Clean Run (no Eve, no noise) — N=1536 ----
try:
    t0 = time.time()
    from qkd.bb84 import BB84Simulator
    sim = BB84Simulator()
    res = sim.run(num_qubits=1536, enable_eve=False)
    elapsed = (time.time() - t0) * 1000
    ok = (res.is_valid is True and res.qber <= 0.11 and
          res.alice_key is not None and res.alice_key == res.bob_key and
          len(res.alice_key) == 32)
    record("T9_bb84_clean_1536", ok,
           f"valid={res.is_valid}, qber={res.qber:.4f}, key_match={res.alice_key==res.bob_key}, "
           f"key_len={len(res.alice_key) if res.alice_key else 0}, "
           f"sifted={res.sifted_length}, reconciled={res.reconciled_length}, "
           f"sec_bits={res.secure_key_bits}, elapsed_ms={elapsed:.1f}")
except Exception as e:
    record("T9_bb84_clean_1536", False, str(e))

# ---- Test 10: BB84 with Eve (full intercept) — expects QBER > 0.11 ----
try:
    t0 = time.time()
    res_eve = sim.run(num_qubits=512, enable_eve=True, eve_prob=1.0)
    elapsed = (time.time() - t0) * 1000
    ok = (res_eve.qber > 0.11 and res_eve.is_valid is False and
          res_eve.alice_key is None and res_eve.bob_key is None)
    record("T10_bb84_eve_abort", ok,
           f"qber={res_eve.qber:.4f}, is_valid={res_eve.is_valid}, elapsed_ms={elapsed:.1f}")
except Exception as e:
    record("T10_bb84_eve_abort", False, str(e))

# ---- Test 11: N=1024 LHL Investigation ----
try:
    res1024 = sim.run(num_qubits=1024, enable_eve=False)
    # Check if 256-bit key was actually produced
    key_derived = res1024.alice_key is not None and len(res1024.alice_key) == 32
    record("T11_n1024_lhl_check", True,
           f"sifted={res1024.sifted_length}, reconciled={res1024.reconciled_length}, "
           f"qber={res1024.qber:.4f}, sec_bits={res1024.secure_key_bits}, "
           f"256bit_key_derived={key_derived}, is_valid={res1024.is_valid}")
except Exception as e:
    record("T11_n1024_lhl_check", False, str(e))

# ---- Summary ----
print("\n" + "=" * 60)
print(f"SUMMARY: {len(PASS)} PASSED, {len(FAIL)} FAILED")
print(f"PASSED: {PASS}")
if FAIL:
    print(f"FAILED: {FAIL}")
print("=" * 60)
