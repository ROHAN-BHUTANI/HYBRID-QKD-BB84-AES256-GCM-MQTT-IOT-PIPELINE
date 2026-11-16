# -*- coding: utf-8 -*-
"""
Module A: BB84 Quantum Key Distribution Simulation using IBM Qiskit Aer.
Orchestrates:
1. Alice state preparation (qkd.alice)
2. Channel transmission with optional Eve intercept-resend attack (qkd.eve) & noise (qkd.channel)
3. Bob basis measurement (qkd.bob)
4. Basis sifting / reconciliation filter (qkd.sifting)
5. Parameter estimation & QBER threshold verification (qkd.qber)
6. Information Reconciliation / Classical Error Correction (qkd.postprocessing.reconciliation)
7. Universal-Hash Privacy Amplification / Key Derivation (qkd.postprocessing.privacy_amplification)
"""
import time
import sys
import os
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

import config
from qkd.alice import Alice
from qkd.bob import Bob
from qkd.eve import Eve
from qkd.channel import QuantumChannel
from qkd.sifting import SiftingEngine
from qkd.qber import QBEREstimator
from qkd.postprocessing.reconciliation import InformationReconciler
from qkd.postprocessing.privacy_amplification import PrivacyAmplifier


@dataclass
class BB84Result:
    """Stores the complete output and diagnostics of a BB84 QKD run."""
    alice_key: Optional[bytes]      # 32-byte (256-bit) derived AES key
    bob_key: Optional[bytes]        # Bob's derived key (identical if QBER acceptable)
    qber: float                     # Quantum Bit Error Rate (0.0 to 1.0)
    is_valid: bool                  # True if QBER <= threshold, False if aborted
    num_qubits: int                 # Initial number of transmitted qubits
    sifted_length: int              # Length of key after basis reconciliation (~50% of N)
    sample_length: int              # Number of bits sacrificed for QBER verification
    remaining_length: int           # Number of bits fed into reconciliation
    eve_present: bool               # Whether Eve was active during transmission
    execution_time_ms: float        # Total circuit & processing latency in milliseconds
    reconciled_length: int = 0      # Length of reconciled error-free key
    ec_leakage_bits: int = 0        # Parity bits disclosed during error correction
    entropy_ratio: float = 1.0      # Min-entropy ratio [1 - h(QBER)]


class BB84Simulator:
    """
    Simulates the BB84 Quantum Key Distribution protocol using Qiskit AerSimulator.
    """
    def __init__(self, backend=None):
        self.backend = backend or AerSimulator()

    def run(
        self,
        num_qubits: int = config.NUM_QUBITS,
        enable_eve: bool = config.ENABLE_EVE,
        eve_prob: float = config.EVE_INTERCEPT_PROB,
        sample_fraction: float = config.SAMPLE_FRACTION,
        threshold: float = config.QBER_THRESHOLD,
        noise_param: float = 0.0
    ) -> BB84Result:
        """
        Executes an end-to-end BB84 key exchange session with reconciliation and privacy amplification.
        """
        t0 = time.perf_counter()

        # Step 1: Alice state preparation
        alice = Alice(num_qubits=num_qubits)
        alice_bits, alice_bases = alice.generate_random_bits_and_bases()

        # Step 2: Bob measurement preparation
        bob = Bob(num_qubits=num_qubits)
        bob_bases = bob.generate_random_bases()

        # Step 3: Eve intercept-resend configuration
        eve = Eve(num_qubits=num_qubits, intercept_prob=eve_prob)
        if enable_eve:
            eve.configure_attack()

        # Step 4: Construct Quantum Circuit in Qiskit
        qr = QuantumRegister(num_qubits, name="q")
        cr_bob = ClassicalRegister(num_qubits, name="c_bob")

        if enable_eve:
            cr_eve = ClassicalRegister(num_qubits, name="c_eve")
            qc = QuantumCircuit(qr, cr_eve, cr_bob)
        else:
            qc = QuantumCircuit(qr, cr_bob)

        # Alice encodes state
        alice.prepare_quantum_circuits(qr, qc)

        # Eve intercept-resend attack (if active)
        if enable_eve:
            eve.apply_intercept_resend(qr, cr_eve, qc)

        # Bob basis rotation & measurement
        bob.apply_measurement_circuits(qr, cr_bob, qc)

        # Step 5: Execute Simulation on Aer Backend (with optional noise)
        noise_model = QuantumChannel.create_depolarizing_noise_model(noise_param)
        job = self.backend.run(qc, shots=config.SIMULATOR_SHOTS, noise_model=noise_model)
        result = job.result()
        raw_counts = list(result.get_counts().keys())[0]

        # Extract Bob's measured bits
        bob_bits = bob.extract_bits_from_counts(raw_counts)

        # Step 6: Classical Basis Sifting
        sifted_indices, sifted_alice, sifted_bob = SiftingEngine.sift(
            alice_bits, alice_bases, bob_bits, bob_bases
        )
        sifted_len = len(sifted_alice)

        if sifted_len == 0:
            t1 = time.perf_counter()
            return BB84Result(
                alice_key=None,
                bob_key=None,
                qber=1.0,
                is_valid=False,
                num_qubits=num_qubits,
                sifted_length=0,
                sample_length=0,
                remaining_length=0,
                eve_present=enable_eve,
                execution_time_ms=(t1 - t0) * 1000.0
            )

        # Step 7: Parameter Estimation & QBER Verification
        qber, is_valid, rem_alice, rem_bob, sample_size, errors = QBEREstimator.estimate(
            sifted_alice, sifted_bob, sample_fraction=sample_fraction, threshold=threshold
        )
        remaining_len = len(rem_alice)

        alice_key = None
        bob_key = None
        reconciled_len = 0
        ec_leakage = 0
        entropy_ratio = 1.0

        # Step 8: Information Reconciliation & Privacy Amplification
        if is_valid and remaining_len > 0:
            # Correct any residual bit differences between Alice and Bob
            rec_alice, rec_bob, ec_leakage, is_identical = InformationReconciler.reconcile(
                rem_alice, rem_bob, estimated_qber=qber
            )
            reconciled_len = len(rec_alice)

            if is_identical:
                # Privacy Amplification via Universal Hashing (2-universal hash bound)
                alice_key, _, entropy_ratio = PrivacyAmplifier.amplify(
                    rec_alice, qber=qber, ec_leakage_bits=ec_leakage, target_key_bytes=config.AES_KEY_SIZE_BYTES
                )
                bob_key, _, _ = PrivacyAmplifier.amplify(
                    rec_bob, qber=qber, ec_leakage_bits=ec_leakage, target_key_bytes=config.AES_KEY_SIZE_BYTES
                )
            else:
                # Reconciliation failed to correct all errors; abort
                is_valid = False

        t1 = time.perf_counter()
        return BB84Result(
            alice_key=alice_key,
            bob_key=bob_key,
            qber=qber,
            is_valid=is_valid,
            num_qubits=num_qubits,
            sifted_length=sifted_len,
            sample_length=sample_size,
            remaining_length=remaining_len,
            eve_present=enable_eve,
            execution_time_ms=(t1 - t0) * 1000.0,
            reconciled_length=reconciled_len,
            ec_leakage_bits=ec_leakage,
            entropy_ratio=entropy_ratio
        )


if __name__ == "__main__":
    sim = BB84Simulator()
    print("=== Testing Upgraded Modular BB84 QKD without Eve ===")
    res_no_eve = sim.run(num_qubits=512, enable_eve=False)
    print(f"Valid: {res_no_eve.is_valid}, QBER: {res_no_eve.qber:.4f}, Sifted: {res_no_eve.sifted_length}, "
          f"Reconciled: {res_no_eve.reconciled_length}, EC Leakage: {res_no_eve.ec_leakage_bits} bits, "
          f"Time: {res_no_eve.execution_time_ms:.2f}ms")
    if res_no_eve.alice_key:
        print(f"Alice Key (hex): {res_no_eve.alice_key.hex()}")
        print(f"Keys Match: {res_no_eve.alice_key == res_no_eve.bob_key}")

    print("\n=== Testing Upgraded Modular BB84 QKD with Eve ===")
    res_eve = sim.run(num_qubits=512, enable_eve=True)
    print(f"Valid: {res_eve.is_valid}, QBER: {res_eve.qber:.4f}, Threshold: {config.QBER_THRESHOLD}")
    print(f"Eve Detected (Key Aborted): {not res_eve.is_valid}")
