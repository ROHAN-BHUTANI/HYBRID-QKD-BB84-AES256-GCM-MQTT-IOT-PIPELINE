# -*- coding: utf-8 -*-
"""
Module A.4: Quantum Channel Noise Models.
Constructs realistic Qiskit Aer noise models simulating:
1. Depolarizing quantum channel error
2. Bit-flip error
3. Phase-flip error
"""
from typing import Optional
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error


class QuantumChannel:
    """
    Builds parameterized quantum noise channels for Qiskit Aer simulation.
    """
    @staticmethod
    def create_depolarizing_noise_model(error_prob: float = 0.0) -> Optional[NoiseModel]:
        """
        Creates a single-qubit depolarizing error channel applied to single-qubit gates (x, h).
        If error_prob <= 0.0, returns None (ideal noiseless channel).
        """
        if error_prob <= 0.0:
            return None

        # Clamp error_prob between 0.0 and 0.75 (max depolarizing rate for 1 qubit)
        p = min(0.75, max(0.0, error_prob))
        noise_model = NoiseModel()
        error_gate = depolarizing_error(p, 1)
        noise_model.add_all_qubit_quantum_error(error_gate, ["x", "h", "id"])
        return noise_model

    @staticmethod
    def create_pauli_noise_model(
        bit_flip_prob: float = 0.0,
        phase_flip_prob: float = 0.0
    ) -> Optional[NoiseModel]:
        """
        Creates a single-qubit Pauli bit-flip (X) and phase-flip (Z) error channel.
        """
        if bit_flip_prob <= 0.0 and phase_flip_prob <= 0.0:
            return None

        px = min(0.5, max(0.0, bit_flip_prob))
        pz = min(0.5, max(0.0, phase_flip_prob))
        pi = max(0.0, 1.0 - px - pz)

        error_gate = pauli_error([('X', px), ('Z', pz), ('I', pi)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error_gate, ["x", "h", "id"])
        return noise_model
