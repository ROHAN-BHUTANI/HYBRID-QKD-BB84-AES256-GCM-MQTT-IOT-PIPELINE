# -*- coding: utf-8 -*-
"""
Unit tests for cryptographic utilities (AES-256-GCM, nonces, tags).
"""
import pytest
import os
import base64
from iot_client.crypto_utils import CryptoUtils
import config


def test_encrypt_decrypt_roundtrip(sample_key):
    """Verify clean AES-256-GCM encryption and decryption."""
    payload = {
        "device_id": "TEST-NODE-01",
        "reading_id": 1,
        "temperature_c": 24.5,
        "humidity_percent": 60.0,
        "pressure_hpa": 1013.25
    }
    envelope, enc_ms = CryptoUtils.encrypt_payload(sample_key, payload)
    assert enc_ms > 0.0
    assert "nonce" in envelope
    assert "ciphertext" in envelope
    assert "tag" in envelope

    decrypted, dec_ms = CryptoUtils.decrypt_payload(sample_key, envelope)
    assert dec_ms > 0.0
    assert decrypted["device_id"] == payload["device_id"]
    assert decrypted["temperature_c"] == payload["temperature_c"]
    assert decrypted["reading_id"] == payload["reading_id"]


def test_nonce_size_and_uniqueness(sample_key):
    """Verify 96-bit nonce size (12 bytes) and uniqueness across calls."""
    payload = {"data": "test"}
    envelope1, _ = CryptoUtils.encrypt_payload(sample_key, payload)
    envelope2, _ = CryptoUtils.encrypt_payload(sample_key, payload)

    nonce1 = base64.b64decode(envelope1["nonce"])
    nonce2 = base64.b64decode(envelope2["nonce"])

    assert len(nonce1) == 12  # 96 bits
    assert len(nonce2) == 12
    assert nonce1 != nonce2  # Fresh nonce per message


def test_invalid_key_size():
    """Verify ValueError is raised if key size is not 32 bytes."""
    short_key = os.urandom(16)
    with pytest.raises(ValueError, match="Invalid AES key size"):
        CryptoUtils.encrypt_payload(short_key, {"test": 1})

    with pytest.raises(ValueError, match="Invalid AES key size"):
        CryptoUtils.decrypt_payload(short_key, {"nonce": "", "ciphertext": "", "tag": ""})
