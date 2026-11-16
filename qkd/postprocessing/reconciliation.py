# -*- coding: utf-8 -*-
"""
Module A.7: Information Reconciliation (Classical Error Correction).
Implements an interactive multi-pass Cascade error correction protocol:
1. Segments sifted key material into adaptive parity blocks based on QBER
2. Detects block parity discrepancies over the classical channel
3. Bisects mismatched blocks using binary search to isolate and correct erroneous bits
4. Shuffles bits across multiple passes to decouple and resolve even-error pairings
5. Tracks classical parity disclosure (leakage) for finite-key privacy amplification
"""
import math
import random
from typing import List, Tuple


class InformationReconciler:
    """
    Implements interactive parity-based Cascade error reconciliation for BB84 sifted keys.
    """
    @staticmethod
    def _compute_parity(bits: List[int], start: int, end: int) -> int:
        """Computes XOR parity sum modulo 2 over bits[start:end]."""
        p = 0
        for i in range(start, end):
            p ^= bits[i]
        return p

    @classmethod
    def reconcile(
        cls,
        alice_bits: List[int],
        bob_bits: List[int],
        estimated_qber: float = 0.0,
        passes: int = 4
    ) -> Tuple[List[int], List[int], int, bool]:
        """
        Executes multi-pass Cascade error correction.

        Args:
            alice_bits: Alice's remaining sifted bit list
            bob_bits: Bob's remaining sifted bit list (corrected in-place on copy)
            estimated_qber: Measured channel QBER
            passes: Number of permutation and correction passes (default: 4)

        Returns:
            Tuple of:
            (reconciled_alice, reconciled_bob, total_parity_leakage, is_identical)
        """
        n = len(alice_bits)
        if n == 0 or len(bob_bits) != n:
            return alice_bits, bob_bits, 0, (alice_bits == bob_bits)

        corrected_bob = list(bob_bits)
        total_leakage = 0

        # Quick check if already identical
        if alice_bits == corrected_bob:
            return alice_bits, corrected_bob, 0, True

        q = max(0.01, estimated_qber)

        # Multi-pass Cascade reconciliation
        for p in range(passes):
            # Pass 0 uses optimal block size ~ 0.73 / QBER; subsequent passes use smaller, varied sizes
            if p == 0:
                block_size = max(4, min(32, int(0.73 / q)))
            else:
                block_size = max(4, min(16, int(12 / (p + 1))))

            # Deterministic permutation for pass > 0
            perm = list(range(n))
            if p > 0:
                rng = random.Random(42 + p)
                rng.shuffle(perm)

            p_a = [alice_bits[i] for i in perm]
            p_b = [corrected_bob[i] for i in perm]

            # Segment into blocks and compare parities
            for b in range(0, n, block_size):
                start = b
                end = min(n, b + block_size)

                parity_a = cls._compute_parity(p_a, start, end)
                parity_b = cls._compute_parity(p_b, start, end)
                total_leakage += 1

                if parity_a != parity_b:
                    # Mismatch found: odd number of errors. Bisect to isolate error
                    left, right = start, end
                    while right - left > 1:
                        mid = (left + right) // 2
                        sub_a = cls._compute_parity(p_a, left, mid)
                        sub_b = cls._compute_parity(p_b, left, mid)
                        total_leakage += 1

                        if sub_a != sub_b:
                            right = mid
                        else:
                            left = mid

                    # Invert erroneous bit in Bob's permuted array
                    p_b[left] = 1 - p_b[left]

            # Un-permute Bob's corrections back into natural order
            for idx, orig_idx in enumerate(perm):
                corrected_bob[orig_idx] = p_b[idx]

            # Early termination if all errors resolved
            if alice_bits == corrected_bob:
                break

        is_identical = (alice_bits == corrected_bob)
        return alice_bits, corrected_bob, total_leakage, is_identical
