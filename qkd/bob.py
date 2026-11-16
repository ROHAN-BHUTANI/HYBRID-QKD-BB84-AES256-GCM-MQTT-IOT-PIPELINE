# -*- coding: utf-8 -*-
"""
Module A.2: Bob (Receiver) Quantum Measurement.
Handles:
1. Independent random basis selection (Z or X)
2. Basis rotation (Hadamard gate for X basis)
3. Projective measurement onto computational basis
4. Classical bitstring extraction from Qiskit Aer simulation counts
"""
import secrets
from typing import List, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class Bob:
    """
    Bob: The quantum receiver node in the BB84 protocol.
    """
    def __init__(self, num_qubits: int = 512):
        self.num_qubits = num_qubits
        self.bases: List[int] = []
        self.measured_bits: List[int] = []

    def generate_random_bases(self) -> List[int]:
        """
        Generates independent random measurement bases for Bob.
        0 = Rectilinear (Z), 1 = Diagonal (X)
        """
        rng = secrets.SystemRandom()
        self.bases = [rng.randint(0, 1) for _ in range(self.num_qubits)]
        return self.bases

    def apply_measurement_circuits(
        self,
        qr: QuantumRegister,
        cr_bob: ClassicalRegister,
        qc: QuantumCircuit
    ) -> QuantumCircuit:
        """
        Applies basis rotation gates and measures qubits into Bob's classical register.
        """
        if not self.bases:
            self.generate_random_bases()

        for i in range(self.num_qubits):
            # If Bob's basis is Diagonal (X), rotate with H gate before measurement
            if self.bases[i] == 1:
                qc.h(qr[i])
            qc.measure(qr[i], cr_bob[i])

        return qc

    def extract_bits_from_counts(self, raw_counts_str: str) -> List[int]:
        """
        Parses Qiskit measurement string and maps to Bob's bit list.
        Note: Qiskit formats classical bitstrings in reverse order (bit 0 is rightmost).
        """
        # If multiple classical registers were measured, extract Bob's part
        if ' ' in raw_counts_str:
            bob_part = raw_counts_str.split(' ')[0]
        else:
            bob_part = raw_counts_str

        # Reverse to restore natural indexing (0 to num_qubits-1)
        self.measured_bits = [int(b) for b in reversed(bob_part)]
        return self.measured_bits
