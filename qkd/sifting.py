# -*- coding: utf-8 -*-
"""
Module A.5: Classical Basis Sifting (Reconciliation Filter).
Performs classical basis comparison over the authenticated classical channel:
- Retains only bit positions where Alice and Bob selected identical bases
- Computes sifting yield efficiency
"""
from typing import List, Tuple


class SiftingEngine:
    """
    Executes the classical basis reconciliation (sifting) phase of BB84.
    """
    @staticmethod
    def sift(
        alice_bits: List[int],
        alice_bases: List[int],
        bob_bits: List[int],
        bob_bases: List[int]
    ) -> Tuple[List[int], List[int], List[int]]:
        """
        Filters Alice and Bob's bits based on matching basis choices.

        Returns:
            Tuple of (sifted_indices, sifted_alice_bits, sifted_bob_bits)
        """
        if len(alice_bases) != len(bob_bases) or len(alice_bits) != len(bob_bits):
            raise ValueError("Input lists must have identical lengths.")

        sifted_indices = [
            i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]
        ]
        sifted_alice = [alice_bits[i] for i in sifted_indices]
        sifted_bob = [bob_bits[i] for i in sifted_indices]

        return sifted_indices, sifted_alice, sifted_bob
