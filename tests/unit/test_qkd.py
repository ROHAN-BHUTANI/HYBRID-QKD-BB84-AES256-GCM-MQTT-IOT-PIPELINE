# -*- coding: utf-8 -*-
"""
Unit tests for QKD modules: Alice, Bob, Eve, Sifting, QBER, Reconciliation, Privacy Amplification.
"""
import pytest
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

from qkd.alice import Alice
from qkd.bob import Bob
from qkd.eve import Eve
from qkd.sifting import SiftingEngine
from qkd.qber import QBEREstimator
from qkd.postprocessing.reconciliation import InformationReconciler
from qkd.postprocessing.privacy_amplification import PrivacyAmplifier
from qkd.bb84 import BB84Simulator


def test_alice_state_prep():
    """Verify Alice encodes states properly onto quantum circuits."""
    alice = Alice(num_qubits=10)
    bits, bases = alice.generate_random_bits_and_bases()
    assert len(bits) == 10
    assert len(bases) == 10
    assert all(b in (0, 1) for b in bits)
    assert all(a in (0, 1) for a in bases)

    qr = QuantumRegister(10, "q")
    qc = QuantumCircuit(qr)
    qc = alice.prepare_quantum_circuits(qr, qc)
    assert qc.num_qubits == 10


def test_bob_measurement():
    """Verify Bob sets up measurement circuits and extracts bits."""
    bob = Bob(num_qubits=8)
    bases = bob.generate_random_bases()
    assert len(bases) == 8

    # Test bitstring parsing with reverse ordering
    raw_str = "10110001"
    bits = bob.extract_bits_from_counts(raw_str)
    assert len(bits) == 8
    # In raw_str, bit 0 is the rightmost character '1', bit 7 is leftmost '1'
    assert bits[0] == 1
    assert bits[7] == 1


def test_sifting_engine():
    """Verify basis sifting retains only matching bases."""
    alice_bits = [0, 1, 0, 1, 1, 0]
    alice_bases = [0, 0, 1, 1, 0, 1]
    bob_bits = [0, 1, 1, 1, 0, 0]
    bob_bases = [0, 1, 1, 1, 0, 0]

    # Matches at indices: 0 (bases 0,0), 2 (bases 1,1), 3 (bases 1,1), 4 (bases 0,0)
    indices, s_alice, s_bob = SiftingEngine.sift(alice_bits, alice_bases, bob_bits, bob_bases)
    assert indices == [0, 2, 3, 4]
    assert s_alice == [0, 0, 1, 1]
    assert s_bob == [0, 1, 1, 0]


def test_qber_estimator():
    """Verify parameter estimation correctly computes error rate and discards sample."""
    s_alice = [0] * 100
    s_bob = [0] * 90 + [1] * 10  # 10% errors

    qber, is_valid, rem_a, rem_b, sample_size, errors = QBEREstimator.estimate(
        s_alice, s_bob, sample_fraction=0.5, threshold=0.11
    )
    assert sample_size == 50
    assert len(rem_a) == 50
    assert len(rem_b) == 50
    # Sample QBER should be close to 0.10
    assert 0.0 <= qber <= 0.30


def test_information_reconciler():
    """Verify Cascade reconciliation eliminates bit errors between Alice and Bob."""
    alice = [0, 1, 1, 0, 1, 0, 1, 1] * 15  # 120 bits
    bob = list(alice)
    # Inject 5 errors (~4.1% QBER)
    err_indices = [5, 17, 34, 67, 95]
    for idx in err_indices:
        bob[idx] = 1 - bob[idx]

    rec_alice, rec_bob, leak, is_identical = InformationReconciler.reconcile(
        alice, bob, estimated_qber=0.041, passes=4
    )
    assert is_identical is True
    assert rec_alice == rec_bob
    assert leak > 0


def test_privacy_amplifier():
    """Verify universal-hash privacy amplification produces 256-bit key."""
    reconciled = [1, 0, 1, 1] * 32  # 128 bits
    key, sec_bits, ratio = PrivacyAmplifier.amplify(reconciled, qber=0.02, target_key_bytes=32)
    assert key is not None
    assert len(key) == 32
    assert sec_bits > 0
    assert 0.0 < ratio <= 1.0


def test_bb84_simulator_clean():
    """Verify end-to-end BB84 without Eve produces matching valid keys."""
    sim = BB84Simulator()
    res = sim.run(num_qubits=256, enable_eve=False)
    assert res.is_valid is True
    assert res.qber <= 0.11
    assert res.alice_key is not None
    assert res.alice_key == res.bob_key
    assert len(res.alice_key) == 32


def test_bb84_simulator_with_eve():
    """Verify end-to-end BB84 with Eve triggers QBER threshold abort."""
    sim = BB84Simulator()
    res = sim.run(num_qubits=512, enable_eve=True, eve_prob=1.0)
    # Full intercept-resend induces expected ~25% error
    assert res.qber > 0.11
    assert res.is_valid is False
    assert res.alice_key is None
    assert res.bob_key is None
