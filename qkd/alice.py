# -*- coding: utf-8 -*-
"""
Module A.1: Alice (Transmitter) Quantum State Preparation.
Handles:
1. Cryptographically secure random bit generation (CSPRNG)
2. Random basis selection (Z rectilinear, X diagonal)
3. Quantum state encoding onto single-qubit circuits using Pauli-X and Hadamard gates
"""
import secrets
from typing import List, Tuple
from qiskit import QuantumCircuit, QuantumRegister


class Alice:
    """
    Alice: The quantum transmitter node in the BB84 protocol.
    """
    def __init__(self, num_qubits: int = 512):
        self.num_qubits = num_qubits
        self.bits: List[int] = []
        self.bases: List[int] = []  # 0: Rectilinear (Z, {|0>, |1>}), 1: Diagonal (X, {|+>, |->})

    def generate_random_bits_and_bases(self) -> Tuple[List[int], List[int]]:
        """
        Generates cryptographically secure random bits and basis choices.
        """
        # Use Python's secrets module for cryptographically secure random numbers
        rng = secrets.SystemRandom()
        self.bits = [rng.randint(0, 1) for _ in range(self.num_qubits)]
        self.bases = [rng.randint(0, 1) for _ in range(self.num_qubits)]
        return self.bits, self.bases

    def prepare_quantum_circuits(
        self,
        qr: QuantumRegister,
        qc: QuantumCircuit
    ) -> QuantumCircuit:
        """
        Encodes Alice's bits into quantum states on the provided QuantumCircuit.
        - |0> (bit 0, basis Z): default ground state
        - |1> (bit 1, basis Z): apply Pauli-X
        - |+> (bit 0, basis X): apply H
        - |-> (bit 1, basis X): apply X then H
        """
        if not self.bits or not self.bases:
            self.generate_random_bits_and_bases()

        for i in range(self.num_qubits):
            bit = self.bits[i]
            basis = self.bases[i]

            if bit == 1:
                qc.x(qr[i])
            if basis == 1:  # Diagonal basis (X)
                qc.h(qr[i])

        return qc
