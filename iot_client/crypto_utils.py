# -*- coding: utf-8 -*-
"""
Cryptographic utility module providing NIST SP 800-38D compliant AES-256-GCM
authenticated encryption, decryption, nonce generation, and tag verification.
"""
import os
import sys
import time
import json
import base64
from typing import Tuple, Dict, Any, Optional

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

import config


class CryptoUtils:
    """
    AES-256-GCM authenticated encryption and decryption handler.
    """

    @staticmethod
    def encrypt_payload(
        aes_key: bytes,
        payload_dict: Dict[str, Any],
        associated_data: Optional[bytes] = None
    ) -> Tuple[Dict[str, Any], float]:
        """
        Encrypts a dictionary payload using AES-256-GCM with a unique 96-bit nonce.

        Returns:
            Tuple of (envelope_dict, encryption_time_ms)
        """
        if len(aes_key) != config.AES_KEY_SIZE_BYTES:
            raise ValueError(
                f"Invalid AES key size: expected {config.AES_KEY_SIZE_BYTES} bytes, got {len(aes_key)}"
            )

        # Serialize payload to canonical JSON bytes
        plaintext_bytes = json.dumps(payload_dict, sort_keys=True).encode("utf-8")

        # Generate fresh, unique 12-byte (96-bit) cryptographically secure nonce
        nonce = os.urandom(config.AES_GCM_NONCE_SIZE_BYTES)

        # Precise timer around cryptographic operation
        t0 = time.perf_counter()
        aesgcm = AESGCM(aes_key)
        # AESGCM.encrypt appends 16-byte authentication tag to ciphertext
        ct_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, associated_data)
        t1 = time.perf_counter()
        encryption_time_ms = (t1 - t0) * 1000.0

        # Separate ciphertext and 16-byte authentication tag
        tag = ct_with_tag[-config.AES_GCM_TAG_SIZE_BYTES:]
        ciphertext = ct_with_tag[:-config.AES_GCM_TAG_SIZE_BYTES]

        # Pack into transport envelope
        envelope = {
            "device_id": payload_dict.get("device_id", config.DEVICE_ID),
            "timestamp_ns": time.time_ns(),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            "tag": base64.b64encode(tag).decode("ascii"),
            "payload_size_bytes": len(plaintext_bytes)
        }

        return envelope, encryption_time_ms

    @staticmethod
    def decrypt_payload(
        aes_key: bytes,
        envelope: Dict[str, Any],
        associated_data: Optional[bytes] = None
    ) -> Tuple[Dict[str, Any], float]:
        """
        Decrypts an envelope using AES-256-GCM and verifies authentication tag.

        Returns:
            Tuple of (decrypted_dict, decryption_time_ms)
        Raises:
            InvalidTag: If payload or tag was tampered with in transit.
        """
        if len(aes_key) != config.AES_KEY_SIZE_BYTES:
            raise ValueError(
                f"Invalid AES key size: expected {config.AES_KEY_SIZE_BYTES} bytes, got {len(aes_key)}"
            )

        nonce = base64.b64decode(envelope["nonce"])
        ciphertext = base64.b64decode(envelope["ciphertext"])
        tag = base64.b64decode(envelope["tag"])

        # Recombine ciphertext + authentication tag for AESGCM.decrypt
        ct_with_tag = ciphertext + tag

        t0 = time.perf_counter()
        aesgcm = AESGCM(aes_key)
        # This will raise InvalidTag if tag or ciphertext does not match
        decrypted_bytes = aesgcm.decrypt(nonce, ct_with_tag, associated_data)
        t1 = time.perf_counter()
        decryption_time_ms = (t1 - t0) * 1000.0

        decrypted_dict = json.loads(decrypted_bytes.decode("utf-8"))
        return decrypted_dict, decryption_time_ms


if __name__ == "__main__":
    # Self-test
    test_key = os.urandom(32)
    sample_data = {
        "device_id": "TEST-NODE",
        "temperature": 24.5,
        "humidity": 55.2,
        "pressure": 1013.25,
        "seq": 1
    }
    env, enc_time = CryptoUtils.encrypt_payload(test_key, sample_data)
    print(f"Encrypted in {enc_time:.4f} ms")
    print(f"Nonce: {env['nonce']}")
    print(f"Tag: {env['tag']}")
    print(f"Ciphertext: {env['ciphertext'][:30]}...")

    dec_data, dec_time = CryptoUtils.decrypt_payload(test_key, env)
    print(f"Decrypted in {dec_time:.4f} ms")
    print(f"Decrypted data matches: {dec_data == sample_data}")

    # Test tampering detection
    print("\nTesting tampering detection...")
    tampered_env = env.copy()
    # Flip one character in ciphertext
    raw_ct = list(tampered_env["ciphertext"])
    raw_ct[0] = 'A' if raw_ct[0] != 'A' else 'B'
    tampered_env["ciphertext"] = "".join(raw_ct)
    try:
        CryptoUtils.decrypt_payload(test_key, tampered_env)
        print("ERROR: Tampered payload was accepted!")
    except InvalidTag:
        print("SUCCESS: InvalidTag raised! Tampered payload detected and rejected.")

