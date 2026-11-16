# -*- coding: utf-8 -*-
"""
Module A.3: Eve (Eavesdropper) Quantum Intercept-Resend Attack Simulation.
Handles:
1. Probabilistic interception selection (p_eve)
2. Random measurement basis selection (Z or X)
3. State projection measurement collapse
4. Re-preparation of collapsed quantum state for transmission to Bob
"""
import random
import secrets
from typing import List, Tuple
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class Eve:
    """
    Simulates an active intercept-resend eavesdropper attacking the quantum channel.
    """
    def __init__(self, num_qubits: int = 512, intercept_prob: float = 1.0):
        self.num_qubits = num_qubits
        self.intercept_prob = intercept_prob
        self.bases: List[int] = []
        self.intercept_mask: List[bool] = []
        self.intercepted_bits: List[int] = []

    def configure_attack(self) -> Tuple[List[int], List[bool]]:
        """
        Generates random attack decisions and measurement bases per qubit.
        """
        rng = secrets.SystemRandom()
        self.bases = [rng.randint(0, 1) for _ in range(self.num_qubits)]
        self.intercept_mask = [
            (random.random() < self.intercept_prob) for _ in range(self.num_qubits)
        ]
        return self.bases, self.intercept_mask

    def apply_intercept_resend(
        self,
        qr: QuantumRegister,
        cr_eve: ClassicalRegister,
        qc: QuantumCircuit
    ) -> QuantumCircuit:
        """
        Applies Eve's intercept-resend attack to the quantum circuit.
        """
        if not self.bases or not self.intercept_mask:
            self.configure_attack()

        for i in range(self.num_qubits):
            if self.intercept_mask[i]:
                # Eve measures in her chosen basis
                if self.bases[i] == 1:  # Diagonal (X) basis
                    qc.h(qr[i])
                qc.measure(qr[i], cr_eve[i])
                
                # Re-prepare state: rotating back to diagonal if measured in X basis
                if self.bases[i] == 1:
                    qc.h(qr[i])

        return qc
