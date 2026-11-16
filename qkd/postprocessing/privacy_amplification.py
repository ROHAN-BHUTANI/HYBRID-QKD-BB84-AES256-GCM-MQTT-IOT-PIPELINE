# -*- coding: utf-8 -*-
"""
Module A.8: 2-Universal Toeplitz Hash Privacy Amplification (Key Derivation).
Implements information-theoretic privacy amplification under the Leftover Hash Lemma:
1. Finite-key entropy calculation using binary Shannon entropy h(QBER)
2. Classical information reconciliation leakage accounting (leak_EC)
3. Strict finite-key security margin Delta = 2*log2(1/epsilon_sec)
4. True 2-universal Toeplitz matrix hashing over GF(2)
5. Strict entropy enforcement: aborts if secure extractable bits < required key length
"""
import math
import hashlib
from typing import List, Tuple, Optional


class InsufficientKeyMaterialError(Exception):
    """Raised when available quantum entropy cannot support the requested key size."""
    pass


class ToeplitzHash:
    """
    Implements a 2-universal hash family via Toeplitz matrix multiplication over GF(2).
    A Toeplitz matrix T of dimension (out_bits x in_bits) is defined by T[i, j] = seed[i - j + in_bits - 1].
    Multiplying T * x over GF(2) extracts a uniformly distributed key bounded by the Leftover Hash Lemma.
    """
    @staticmethod
    def generate_seed_bits(seed_material: bytes, required_bits: int) -> List[int]:
        """
        Expands public seed material into a deterministic pseudorandom bit sequence for the Toeplitz matrix.
        Uses SHA-256 in counter mode to produce required_bits.
        """
        bits = []
        counter = 0
        while len(bits) < required_bits:
            block = hashlib.sha256(seed_material + counter.to_bytes(4, byteorder="big")).digest()
            for byte in block:
                for shift in range(7, -1, -1):
                    bits.append((byte >> shift) & 1)
                    if len(bits) >= required_bits:
                        break
                if len(bits) >= required_bits:
                    break
            counter += 1
        return bits[:required_bits]

    @classmethod
    def multiply_gf2(
        cls,
        input_bits: List[int],
        out_bits: int,
        seed_bytes: bytes = b"QKD-BB84-TOEPLITZ-UNIVERSAL-SEED-2026"
    ) -> List[int]:
        """
        Computes y = T * x over GF(2).
        
        Args:
            input_bits: List of input bits of length m
            out_bits: Desired output length l (l <= m)
            seed_bytes: Public seed material defining the matrix
            
        Returns:
            List of l output bits
        """
        m = len(input_bits)
        l = out_bits
        if l <= 0 or m <= 0 or l > m:
            raise ValueError(f"Invalid dimensions: in_bits={m}, out_bits={l}")

        # Seed length needed for (l x m) Toeplitz matrix is m + l - 1 bits
        seed_bits = cls.generate_seed_bits(seed_bytes, m + l - 1)

        output_bits = []
        for i in range(l):
            accum = 0
            # Row i of Toeplitz matrix: T[i, j] = seed_bits[i - j + m - 1]
            offset = i + m - 1
            for j in range(m):
                if input_bits[j]:
                    accum ^= seed_bits[offset - j]
            output_bits.append(accum)

        return output_bits


class PrivacyAmplifier:
    """
    Derives cryptographically secure symmetric keys from reconciled key material
    using 2-universal Toeplitz hashing bounded by the Leftover Hash Lemma.
    """
    @staticmethod
    def binary_entropy(p: float) -> float:
        """
        Computes the Shannon binary entropy h(p) = -p*log2(p) - (1-p)*log2(1-p).
        """
        if p <= 0.0 or p >= 1.0:
            return 0.0
        return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)

    @classmethod
    def calculate_secure_key_length(
        cls,
        reconciled_length: int,
        qber: float,
        ec_leakage_bits: int = 0,
        security_parameter_bits: int = 32
    ) -> int:
        """
        Computes the extractable secret key length according to the finite-key Leftover Hash Lemma:
        l <= m * [1 - h(QBER)] - leak_EC - 2*log2(1/epsilon_sec)
        
        Here security_parameter_bits represents 2*log2(1/epsilon_sec), e.g. 64 bits for epsilon=2^-32.
        """
        if reconciled_length <= 0:
            return 0

        h_qber = cls.binary_entropy(qber)
        theoretical_capacity = reconciled_length * (1.0 - h_qber)
        # Margin for epsilon_sec = 2^-32: 2 * 32 = 64 bits
        finite_key_margin = 2 * security_parameter_bits
        net_secret_bits = theoretical_capacity - ec_leakage_bits - finite_key_margin

        return max(0, int(math.floor(net_secret_bits)))

    @classmethod
    def amplify(
        cls,
        reconciled_bits: List[int],
        qber: float = 0.0,
        ec_leakage_bits: int = 0,
        target_key_bytes: int = 32,
        seed: bytes = b"QKD-BB84-TOEPLITZ-SALT-2026",
        allow_128_bit_fallback: bool = False
    ) -> Tuple[Optional[bytes], int, float]:
        """
        Compresses reconciled key material into an exact cryptographic AES key
        via 2-universal Toeplitz matrix hashing over GF(2).

        Args:
            reconciled_bits: Error-corrected identical bit list
            qber: Evaluated channel QBER
            ec_leakage_bits: Number of parity bits disclosed during reconciliation
            target_key_bytes: Desired key size (default 32 bytes = 256 bits, or 16 bytes = 128 bits)
            seed: Public random salt defining the 2-universal hash family
            allow_128_bit_fallback: If True, falls back to AES-128 if 256 bits cannot be securely extracted

        Returns:
            Tuple of:
            (derived_key_bytes, extractable_secure_bits, min_entropy_ratio)
        """
        m = len(reconciled_bits)
        if m == 0:
            return None, 0, 0.0

        secure_bits = cls.calculate_secure_key_length(m, qber, ec_leakage_bits)
        entropy_ratio = max(0.0, 1.0 - cls.binary_entropy(qber))
        target_bits = target_key_bytes * 8

        # Enforce Leftover Hash Lemma: Never manufacture key bits beyond available secure entropy
        if secure_bits < target_bits:
            if allow_128_bit_fallback and secure_bits >= 128:
                target_bits = 128
                target_key_bytes = 16
            else:
                # Insufficient secure entropy under finite-key bounds
                return None, secure_bits, entropy_ratio

        # Apply 2-Universal Toeplitz Matrix Multiplication over GF(2)
        extracted_bits = ToeplitzHash.multiply_gf2(
            input_bits=reconciled_bits,
            out_bits=target_bits,
            seed_bytes=seed
        )

        # Pack extracted bits into cryptographic key bytes
        byte_chunks = [extracted_bits[i:i+8] for i in range(0, len(extracted_bits), 8)]
        derived_key = bytes([sum(bit << (7 - idx) for idx, bit in enumerate(chunk)) for chunk in byte_chunks])

        return derived_key, secure_bits, entropy_ratio
