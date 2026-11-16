# -*- coding: utf-8 -*-
"""
Module A.6: Parameter Estimation & Quantum Bit Error Rate (QBER) Evaluation.
Handles:
1. Random subsampling of sifted bits for error estimation
2. Public comparison over classical channel
3. QBER calculation: errors / sample_size
4. Verification against theoretical abort threshold (tau = 0.11)
5. Secure disposal of sampled verification bits
"""
import random
from typing import List, Tuple, Set


class QBEREstimator:
    """
    Performs parameter estimation and threshold-based intrusion detection.
    """
    @staticmethod
    def estimate(
        sifted_alice: List[int],
        sifted_bob: List[int],
        sample_fraction: float = 0.25,
        threshold: float = 0.11
    ) -> Tuple[float, bool, List[int], List[int], int, int]:
        """
        Samples a fraction of sifted bits to estimate QBER and discards the sample.

        Returns:
            Tuple of:
            (qber, is_valid, remaining_alice, remaining_bob, sample_size, errors_found)
        """
        sifted_len = len(sifted_alice)
        if sifted_len == 0:
            return 1.0, False, [], [], 0, 0

        # Determine sample size (minimum 1 bit, at most sifted_len)
        sample_size = max(1, int(sifted_len * sample_fraction))
        sample_indices: Set[int] = set(random.sample(range(sifted_len), sample_size))

        # Count mismatches on the sampled subset
        errors_found = sum(
            1 for idx in sample_indices if sifted_alice[idx] != sifted_bob[idx]
        )
        qber = errors_found / sample_size

        # Discard sampled verification bits from remaining key candidate material
        remaining_alice = [
            sifted_alice[i] for i in range(sifted_len) if i not in sample_indices
        ]
        remaining_bob = [
            sifted_bob[i] for i in range(sifted_len) if i not in sample_indices
        ]

        # Protocol is valid if QBER <= threshold and remaining key length > 0
        is_valid = (qber <= threshold) and (len(remaining_alice) > 0)

        return qber, is_valid, remaining_alice, remaining_bob, sample_size, errors_found
