# -*- coding: utf-8 -*-
"""
Module A: BB84 Quantum Key Distribution Simulation using IBM Qiskit.
Implements:
1. State preparation (Alice)
2. Channel transmission with optional Eve intercept-resend attack
3. Basis measurement (Bob)
4. Sifting phase (basis reconciliation)
5. Parameter estimation & QBER calculation
6. Privacy amplification / Key derivation using SHA-256 (yielding 256-bit AES key)
"""
import time
import random
import hashlib
import sys
import os
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

import config


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
    remaining_length: int           # Number of bits fed into SHA-256 KDF
    eve_present: bool               # Whether Eve was active during transmission
    execution_time_ms: float        # Total circuit & processing latency in milliseconds


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
        threshold: float = config.QBER_THRESHOLD
    ) -> BB84Result:
        """
        Executes an end-to-end BB84 key exchange session.
        """
        t0 = time.perf_counter()

        # Step 1: Alice generates random bits and random bases
        # 0 = Rectilinear (+, {|0>, |1>}), 1 = Diagonal (x, {|+>, |->})
        alice_bits = [random.randint(0, 1) for _ in range(num_qubits)]
        alice_bases = [random.randint(0, 1) for _ in range(num_qubits)]

        # Step 2: Bob generates random measurement bases
        bob_bases = [random.randint(0, 1) for _ in range(num_qubits)]

        # Step 3: Eve generates random bases and decides interception per qubit
        eve_bases = [random.randint(0, 1) for _ in range(num_qubits)]
        eve_intercepts = [
            enable_eve and (random.random() < eve_prob) for _ in range(num_qubits)
        ]

        # Step 4: Construct Quantum Circuit in Qiskit
        qr = QuantumRegister(num_qubits, name="q")
        cr_bob = ClassicalRegister(num_qubits, name="c_bob")
        
        registers = [qr, cr_bob]
        if enable_eve:
            cr_eve = ClassicalRegister(num_qubits, name="c_eve")
            registers.append(cr_eve)
            qc = QuantumCircuit(qr, cr_eve, cr_bob)
        else:
            qc = QuantumCircuit(qr, cr_bob)

        for i in range(num_qubits):
            # --- Alice State Preparation ---
            # |0> by default
            if alice_bits[i] == 1:
                qc.x(qr[i])  # Flip to |1>
            if alice_bases[i] == config.BASIS_DIAGONAL:
                qc.h(qr[i])  # Rotate to |+> or |->

            # --- Quantum Channel Transmission & Eve Simulation ---
            if enable_eve and eve_intercepts[i]:
                # Eve measures in her chosen basis
                if eve_bases[i] == config.BASIS_DIAGONAL:
                    qc.h(qr[i])
                qc.measure(qr[i], cr_eve[i])
                # Eve re-prepares in her basis
                if eve_bases[i] == config.BASIS_DIAGONAL:
                    qc.h(qr[i])

            # --- Bob Receives and Measures ---
            if bob_bases[i] == config.BASIS_DIAGONAL:
                qc.h(qr[i])
            qc.measure(qr[i], cr_bob[i])

        # Step 5: Execute Simulation
        job = self.backend.run(qc, shots=config.SIMULATOR_SHOTS)
        result = job.result()
        raw_counts = list(result.get_counts().keys())[0]

        # In Qiskit, measurements are ordered with c_bob as the rightmost/leftmost register
        # Format with multiple classical registers is space-separated strings
        if enable_eve:
            # Format: 'c_bob c_eve'
            bob_str, _ = raw_counts.split(' ')
        else:
            bob_str = raw_counts

        # Qiskit orders classical bits in reverse (index 0 is at the end)
        bob_bits = [int(b) for b in reversed(bob_str)]

        # Step 6: Sifting Phase (Basis Reconciliation)
        # Alice and Bob announce bases publicly and keep only matching indices
        sifted_indices = [
            i for i in range(num_qubits) if alice_bases[i] == bob_bases[i]
        ]
        sifted_alice = [alice_bits[i] for i in sifted_indices]
        sifted_bob = [bob_bits[i] for i in sifted_indices]
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
        sample_size = max(1, int(sifted_len * sample_fraction))
        sample_indices = set(random.sample(range(sifted_len), sample_size))

        sample_errors = sum(
            1 for idx in sample_indices if sifted_alice[idx] != sifted_bob[idx]
        )
        qber = sample_errors / sample_size

        # Discard sampled verification bits from the key material
        remaining_alice = [
            sifted_alice[i] for i in range(sifted_len) if i not in sample_indices
        ]
        remaining_bob = [
            sifted_bob[i] for i in range(sifted_len) if i not in sample_indices
        ]
        remaining_len = len(remaining_alice)

        # Step 8: Security Decision & Key Derivation (Privacy Amplification)
        # If QBER exceeds threshold, abort key agreement
        is_valid = (qber <= threshold) and (remaining_len > 0)

        alice_key = None
        bob_key = None
        if is_valid:
            # Key Derivation via SHA-256 into 256-bit AES key
            alice_bitstring = "".join(str(b) for b in remaining_alice)
            bob_bitstring = "".join(str(b) for b in remaining_bob)

            alice_key = hashlib.sha256(alice_bitstring.encode("utf-8")).digest()
            bob_key = hashlib.sha256(bob_bitstring.encode("utf-8")).digest()

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
            execution_time_ms=(t1 - t0) * 1000.0
        )


if __name__ == "__main__":
    sim = BB84Simulator()
    print("=== Testing BB84 QKD without Eve ===")
    res_no_eve = sim.run(num_qubits=512, enable_eve=False)
    print(f"Valid: {res_no_eve.is_valid}, QBER: {res_no_eve.qber:.4f}, Sifted: {res_no_eve.sifted_length}, Remaining: {res_no_eve.remaining_length}, Time: {res_no_eve.execution_time_ms:.2f}ms")
    if res_no_eve.alice_key:
        print(f"Alice Key (hex): {res_no_eve.alice_key.hex()}")
        print(f"Keys Match: {res_no_eve.alice_key == res_no_eve.bob_key}")

    print("\n=== Testing BB84 QKD with Eve ===")
    res_eve = sim.run(num_qubits=512, enable_eve=True)
    print(f"Valid: {res_eve.is_valid}, QBER: {res_eve.qber:.4f}, Threshold: {config.QBER_THRESHOLD}")
    print(f"Eve Detected (Key Aborted): {not res_eve.is_valid}")
