# -*- coding: utf-8 -*-
"""
Security and threat model tests: Tamper detection, Replay attacks, Key mismatch.
"""
import pytest
import os
import base64
import json
from cryptography.exceptions import InvalidTag

from iot_client.crypto_utils import CryptoUtils
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager


def test_ciphertext_tampering_raises_invalid_tag(sample_key):
    """Verify modifying any character in ciphertext raises InvalidTag."""
    payload = {"device_id": "NODE-1", "temp": 25.0}
    envelope, _ = CryptoUtils.encrypt_payload(sample_key, payload)

    # Tamper with ciphertext
    raw_ct = list(envelope["ciphertext"])
    raw_ct[0] = 'Z' if raw_ct[0] != 'Z' else 'A'
    envelope["ciphertext"] = "".join(raw_ct)

    with pytest.raises(InvalidTag):
        CryptoUtils.decrypt_payload(sample_key, envelope)


def test_nonce_tampering_raises_invalid_tag(sample_key):
    """Verify modifying nonce in transit raises InvalidTag."""
    payload = {"device_id": "NODE-1", "temp": 25.0}
    envelope, _ = CryptoUtils.encrypt_payload(sample_key, payload)

    raw_nonce = list(envelope["nonce"])
    raw_nonce[0] = 'Z' if raw_nonce[0] != 'Z' else 'A'
    envelope["nonce"] = "".join(raw_nonce)

    with pytest.raises(InvalidTag):
        CryptoUtils.decrypt_payload(sample_key, envelope)


def test_tag_tampering_raises_invalid_tag(sample_key):
    """Verify modifying authentication tag raises InvalidTag."""
    payload = {"device_id": "NODE-1", "temp": 25.0}
    envelope, _ = CryptoUtils.encrypt_payload(sample_key, payload)

    raw_tag = list(envelope["tag"])
    raw_tag[0] = 'Z' if raw_tag[0] != 'Z' else 'A'
    envelope["tag"] = "".join(raw_tag)

    with pytest.raises(InvalidTag):
        CryptoUtils.decrypt_payload(sample_key, envelope)


def test_wrong_key_decryption_fails(sample_key):
    """Verify decrypting with a mismatched key raises InvalidTag."""
    payload = {"secret": "confidential_telemetry"}
    envelope, _ = CryptoUtils.encrypt_payload(sample_key, payload)

    attacker_key = os.urandom(32)
    with pytest.raises(InvalidTag):
        CryptoUtils.decrypt_payload(attacker_key, envelope)


def test_cloud_receiver_anti_replay(tmp_path, sample_key):
    """Verify cloud receiver detects and rejects replayed sequence numbers."""
    db_path = str(tmp_path / "replay_test.db")
    db = DatabaseManager(db_path=db_path)

    events = []
    receiver = CloudReceiver(
        aes_key=sample_key,
        db_manager=db,
        on_message_callback=lambda ev: events.append(ev)
    )

    # Packet 1 (reading_id = 1)
    p1 = {"device_id": "EDGE-01", "reading_id": 1, "temperature_c": 20.0}
    env1, _ = CryptoUtils.encrypt_payload(sample_key, p1)
    receiver._on_mqtt_message("iot/secure/data", json.dumps(env1))

    assert len(events) == 1
    assert events[0]["status"] == "AUTHENTICATED"
    assert db.get_device_sequence("EDGE-01") == 1

    # Replay packet 1
    receiver._on_mqtt_message("iot/secure/data", json.dumps(env1))
    assert len(events) == 2
    assert events[1]["status"] == "REPLAY_REJECTED"

    # Check alert logged in DB
    alerts = db.get_security_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["alert_type"] == "REPLAY_ATTACK"
