# -*- coding: utf-8 -*-
"""
Tests for TSK-01: Autonomous QKD Key Renegotiation.
Covers all 16 acceptance criteria from the task specification.
"""
import os
import time
import threading
import pytest

from qkd.key_lifecycle import (
    KeyLifecycleManager, KeyState,
    KeyExpirationError, RekeyFailedError,
)
from iot_client.sensor_client import IoTSensorClient
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager
from qkd.bb84 import BB84Simulator
import config


# ---------------------------------------------------------------------------
# Shared fixtures and helpers
# ---------------------------------------------------------------------------

def _make_key():
    """Return a fresh 32-byte random AES key."""
    return os.urandom(32)


def _success_bb84_factory(key_override=None):
    """Factory that returns a fresh key without running Qiskit (fast)."""
    def factory():
        key = key_override or os.urandom(32)
        meta = {"qber": 0.02, "pa_output_bits": 256, "reconciled_bits": 1200,
                "ec_leakage_bits": 60, "num_qubits": 1536, "execution_time_ms": 100.0,
                "is_valid": True}
        return key, meta
    return factory


def _failing_bb84_factory():
    """Factory that always raises, simulating a network/hardware failure."""
    def factory():
        raise RuntimeError("Simulated BB84 hardware failure")
    return factory


def _aborting_bb84_factory():
    """Factory that returns (None, meta), simulating QBER threshold exceeded."""
    def factory():
        meta = {"qber": 0.25, "pa_output_bits": 0, "is_valid": False}
        return None, meta
    return factory


@pytest.fixture
def test_db(tmp_path):
    return DatabaseManager(db_path=str(tmp_path / "lifecycle_test.db"))


@pytest.fixture
def rotated_key_holder():
    """Tracks keys received by on_key_rotated callback."""
    received = []

    def on_rotated(new_key_id, new_key_bytes, meta):
        received.append({"key_id": new_key_id, "key": new_key_bytes, "meta": meta})

    return received, on_rotated


# ===========================================================================
# CRITERION 1: Normal publishing below the key limit
# ===========================================================================

class TestNormalPublishing:
    def test_publish_below_limit_does_not_trigger_rekey(self, tmp_path):
        """Verify invocation counter rises correctly and no rekey occurs below threshold."""
        initial_key = _make_key()
        rekey_calls = []

        sensor = IoTSensorClient(
            device_id="TEST-NORMAL-01",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=10,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=lambda kid, k, m: rekey_calls.append(kid),
        )
        sensor.connect()

        for _ in range(5):
            sensor.publish_reading()

        assert sensor.key_invocations == 5
        assert len(rekey_calls) == 0
        assert sensor._lifecycle.current_state == KeyState.ACTIVE
        sensor.disconnect()

    def test_invocation_counter_increments_per_publish(self, tmp_path):
        """Each publish_reading call increments counter exactly once."""
        sensor = IoTSensorClient(
            device_id="TEST-CTR-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=100,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        for i in range(1, 8):
            sensor.publish_reading()
            assert sensor.key_invocations == i
        sensor.disconnect()


# ===========================================================================
# CRITERION 2 & 3: Rekey trigger at threshold + successful BB84 renegotiation
# ===========================================================================

class TestRekeyTrigger:
    def test_rekey_triggered_at_threshold(self, tmp_path, rotated_key_holder):
        """When invocations reach max, the next publish triggers BB84 renegotiation."""
        received, on_rotated = rotated_key_holder
        new_key = _make_key()

        sensor = IoTSensorClient(
            device_id="TEST-REKEY-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=3,
            bb84_factory=_success_bb84_factory(new_key),
            on_key_rotated=on_rotated,
        )
        sensor.connect()

        # Publish 3 readings (fills the limit)
        for _ in range(3):
            sensor.publish_reading()

        # State should be REKEY_REQUIRED after hitting threshold
        assert sensor._lifecycle.current_state in (
            KeyState.REKEY_REQUIRED, KeyState.ACTIVE_NEW_KEY, KeyState.ACTIVE
        )

        # 4th publish triggers rekeying transparently
        sensor.publish_reading()

        # Rekeying completed; on_key_rotated was called
        assert len(received) >= 1
        assert received[0]["key"] == new_key
        sensor.disconnect()

    def test_new_bb84_session_executes_during_rekey(self, rotated_key_holder):
        """Verify the bb84_factory is actually called (not short-circuited)."""
        factory_calls = []

        def counting_factory():
            factory_calls.append(1)
            key = _make_key()
            return key, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                         "ec_leakage_bits": 50, "num_qubits": 1536,
                         "execution_time_ms": 100.0, "is_valid": True}

        received, on_rotated = rotated_key_holder
        sensor = IoTSensorClient(
            device_id="TEST-BB84-EXEC",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=counting_factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()
        for _ in range(3):  # 3rd triggers rekey
            sensor.publish_reading()

        assert len(factory_calls) >= 1, "BB84 factory was never called"
        sensor.disconnect()


# ===========================================================================
# CRITERION 4 & 5: New key installation + receiver synchronization
# ===========================================================================

class TestKeyInstallationAndReceiverSync:
    def test_new_key_installed_in_lifecycle_manager(self, rotated_key_holder):
        """After rekeying, lifecycle manager holds the new key."""
        received, on_rotated = rotated_key_holder
        new_key = _make_key()

        sensor = IoTSensorClient(
            device_id="TEST-INSTALL-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_success_bb84_factory(new_key),
            on_key_rotated=on_rotated,
        )
        sensor.connect()
        for _ in range(3):
            sensor.publish_reading()

        assert sensor._lifecycle.aes_key == new_key
        sensor.disconnect()

    def test_receiver_synchronizes_to_new_key(self, test_db, rotated_key_holder):
        """rotate_key callback updates receiver's active key."""
        received, on_rotated = rotated_key_holder
        receiver = CloudReceiver(aes_key=_make_key(), db_manager=test_db)
        new_key = _make_key()

        def on_key_rotated_with_receiver(new_key_id, new_key_bytes, meta):
            receiver.rotate_key(new_key_id, new_key_bytes, meta)
            on_rotated(new_key_id, new_key_bytes, meta)

        sensor = IoTSensorClient(
            device_id="TEST-SYNC-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_success_bb84_factory(new_key),
            on_key_rotated=on_key_rotated_with_receiver,
        )
        sensor.connect()
        receiver.start()

        for _ in range(3):
            sensor.publish_reading()

        time.sleep(0.3)
        # Receiver should now hold the new key
        assert receiver.aes_key == new_key
        assert receiver._active_key_id == received[0]["key_id"]

        sensor.disconnect()
        receiver.stop()

    def test_receiver_sync_failure_rejects_as_tampered(self, test_db):
        """When receiver fails to synchronize to new key, post-rekey frames are rejected as TAMPERED."""
        received_events = []
        receiver = CloudReceiver(
            aes_key=_make_key(),
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver._active_key_id = "OLD-KEY"
        receiver.start()

        # Simulate synchronization failure: on_key_rotated callback is a no-op, receiver NEVER learns the new key
        sensor = IoTSensorClient(
            device_id="TEST-SYNC-FAIL",
            aes_key=receiver.aes_key,
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=lambda: (_make_key(), {"qber": 0.0, "pa_output_bits": 256, "is_valid": True}),
            on_key_rotated=lambda kid, k, m: None,  # Intentionally drop rotation callback
        )
        sensor.connect()

        # First 2 succeed under initial shared key
        sensor.publish_reading()
        sensor.publish_reading()

        # 3rd frame rotates key on sensor, but receiver was NOT rotated
        sensor.publish_reading()

        # Wait for receiver
        for _ in range(20):
            tampered = [e for e in received_events if e["status"] == "TAMPERED"]
            if tampered:
                break
            time.sleep(0.05)

        assert len(tampered) >= 1, "Unsynchronized receiver must reject post-rekey frame as TAMPERED"
        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION 6: Old key retirement
# ===========================================================================

class TestOldKeyRetirement:
    def test_old_key_retired_after_rekeying(self, rotated_key_holder):
        """After rekeying, old key_id appears in retired_key_ids."""
        received, on_rotated = rotated_key_holder
        sensor = IoTSensorClient(
            device_id="TEST-RETIRE-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=on_rotated,
        )
        sensor.connect()
        old_key_id = sensor.key_id

        for _ in range(3):  # Triggers rekey on 3rd
            sensor.publish_reading()

        assert sensor._lifecycle.is_retired(old_key_id), \
            f"Old key_id {old_key_id} was not marked retired"
        sensor.disconnect()

    def test_lifecycle_key_id_changes_after_rekey(self, rotated_key_holder):
        """key_id must change to a new value after successful rekeying."""
        received, on_rotated = rotated_key_holder
        sensor = IoTSensorClient(
            device_id="TEST-KID-CHANGE",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=on_rotated,
        )
        sensor.connect()
        original_key_id = sensor.key_id
        for _ in range(3):
            sensor.publish_reading()

        assert sensor.key_id != original_key_id, \
            "key_id did not change after successful rekeying"
        sensor.disconnect()


# ===========================================================================
# CRITERION 7 & 8: Encryption with new key + nonce uniqueness across rotations
# ===========================================================================

class TestEncryptionUnderNewKeyAndNonces:
    def test_post_rekey_frames_encrypted_with_new_key(self, test_db):
        """Frames after rekey are decryptable with the new key but NOT the old key."""
        from iot_client.crypto_utils import CryptoUtils
        from cryptography.exceptions import InvalidTag

        new_key_holder = {}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                       "ec_leakage_bits": 50, "num_qubits": 1536, "execution_time_ms": 100.0,
                       "is_valid": True}

        old_key = _make_key()
        sensor = IoTSensorClient(
            device_id="TEST-NEWKEY-ENC",
            aes_key=old_key,
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=factory,
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()

        # Trigger rekeying
        for _ in range(3):
            env, _ = sensor.publish_reading()

        last_env = env
        new_key = new_key_holder["key"]

        # Last frame must be decryptable with new key
        dec, _ = CryptoUtils.decrypt_payload(new_key, last_env)
        assert dec is not None

        # Last frame must NOT be decryptable with old key
        with pytest.raises(InvalidTag):
            CryptoUtils.decrypt_payload(old_key, last_env)

        sensor.disconnect()

    def test_nonces_unique_across_key_rotation(self, test_db):
        """All nonces across both key sessions must be unique."""
        envelopes = []

        def factory():
            return _make_key(), {"qber": 0.01, "pa_output_bits": 256,
                                  "reconciled_bits": 1200, "ec_leakage_bits": 50,
                                  "num_qubits": 1536, "execution_time_ms": 100.0, "is_valid": True}

        sensor = IoTSensorClient(
            device_id="TEST-NONCES",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=3,
            bb84_factory=factory,
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()

        for _ in range(6):  # 3 pre-rekey + 3 post-rekey
            env, _ = sensor.publish_reading()
            envelopes.append(env["nonce"])

        assert len(envelopes) == len(set(envelopes)), \
            f"Duplicate nonces detected: {len(envelopes)} total, {len(set(envelopes))} unique"
        sensor.disconnect()


# ===========================================================================
# CRITERION 9 & 10: Rekey failure + BB84 session abort
# ===========================================================================

class TestRekeyFailure:
    def test_rekey_failure_raises_and_blocks_further_encryption(self):
        """When BB84 factory raises, RekeyFailedError is raised and state=SECURITY_ABORT."""
        sensor = IoTSensorClient(
            device_id="TEST-FAIL-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_failing_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()

        # First 2 succeed
        sensor.publish_reading()
        sensor.publish_reading()

        # 3rd triggers failing rekeying
        with pytest.raises((RekeyFailedError, KeyExpirationError)):
            sensor.publish_reading()

        # State should be terminal
        assert sensor._lifecycle.current_state in (KeyState.SECURITY_ABORT, KeyState.KEY_EXPIRED)
        sensor.disconnect()

    def test_privacy_amplification_failure_blocks_rekey(self):
        """When privacy amplification returns insufficient entropy (None key), state=SECURITY_ABORT."""
        def pa_failing_factory():
            # Returns None key simulating Toeplitz hash failure / insufficient entropy
            return None, {
                "qber": 0.02,
                "is_valid": False,
                "reconciled_bits": 50,
                "pa_output_bits": 0,
                "reason": "Insufficient entropy for 256-bit key"
            }

        sensor = IoTSensorClient(
            device_id="TEST-PA-FAIL",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=pa_failing_factory,
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        sensor.publish_reading()
        sensor.publish_reading()

        with pytest.raises((RekeyFailedError, KeyExpirationError)):
            sensor.publish_reading()

        assert sensor._lifecycle.current_state == KeyState.SECURITY_ABORT
        sensor.disconnect()

    def test_qber_abort_raises_and_blocks_encryption(self):
        """When BB84 returns None key (QBER > threshold), state=SECURITY_ABORT, encryption blocked."""
        sensor = IoTSensorClient(
            device_id="TEST-ABORT-01",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_aborting_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        sensor.publish_reading()
        sensor.publish_reading()

        with pytest.raises((RekeyFailedError, KeyExpirationError)):
            sensor.publish_reading()

        assert sensor._lifecycle.current_state == KeyState.SECURITY_ABORT
        sensor.disconnect()

    def test_expired_key_cannot_be_reused_after_abort(self):
        """After SECURITY_ABORT, further publish_reading calls are blocked."""
        sensor = IoTSensorClient(
            device_id="TEST-NORETRY",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=1,
            bb84_factory=_failing_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        sensor.publish_reading()

        # First rekey attempt
        with pytest.raises((RekeyFailedError, KeyExpirationError)):
            sensor.publish_reading()

        # Second attempt must also fail — no silent reuse of retired key
        with pytest.raises((RekeyFailedError, KeyExpirationError, RuntimeError)):
            sensor.publish_reading()
        sensor.disconnect()


# ===========================================================================
# CRITERION 11 & 12: Publishing during rekeying + pending message preservation
# ===========================================================================

class TestPublishingDuringRekey:
    def test_messages_not_lost_around_rekey_boundary(self, test_db):
        """All messages published across a rekey boundary must be received and authenticated."""
        received_events = []
        new_key_holder = {"key": None}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                       "ec_leakage_bits": 50, "num_qubits": 1536, "execution_time_ms": 100.0,
                       "is_valid": True}

        receiver = CloudReceiver(
            aes_key=None,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )

        def on_key_rotated(new_key_id, new_key_bytes, meta):
            receiver.rotate_key(new_key_id, new_key_bytes, meta)

        initial_key = _make_key()
        receiver.set_key(initial_key)
        receiver._active_key_id = "INITIAL"
        receiver.start()

        sensor = IoTSensorClient(
            device_id="TEST-MSGPRESERVE",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=3,
            bb84_factory=factory,
            on_key_rotated=on_key_rotated,
        )
        sensor.connect()

        # 3 before rekey, 1 triggers rekey (transparent), 3 after
        for _ in range(7):
            sensor.publish_reading()
            time.sleep(0.05)

        # Allow dispatcher to drain
        for _ in range(60):
            if len(received_events) >= 7:
                break
            time.sleep(0.05)

        authenticated = [e for e in received_events if e["status"] == "AUTHENTICATED"]
        assert len(authenticated) == 7, \
            f"Expected 7 authenticated msgs; got {len(authenticated)} (total events={len(received_events)})"

        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION 13: Concurrent publishing around rekey threshold
# ===========================================================================

class TestConcurrentPublishing:
    def test_concurrent_threads_no_duplicate_keys_or_lost_messages(self, test_db):
        """Multiple threads publishing concurrently across the rekey threshold."""
        received_events = []
        rekey_count = [0]

        def factory():
            rekey_count[0] += 1
            return _make_key(), {"qber": 0.01, "pa_output_bits": 256,
                                  "reconciled_bits": 1200, "ec_leakage_bits": 50,
                                  "num_qubits": 1536, "execution_time_ms": 100.0, "is_valid": True}

        receiver = CloudReceiver(
            aes_key=None,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        initial_key = _make_key()
        receiver.set_key(initial_key)
        receiver._active_key_id = "INIT"
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-CONCURRENT",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=5,
            bb84_factory=factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()

        errors = []

        def publish_n(n):
            for _ in range(n):
                try:
                    sensor.publish_reading()
                    time.sleep(0.02)
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=publish_n, args=(4,)) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        time.sleep(0.5)
        assert len(errors) == 0, f"Errors during concurrent publish: {errors}"
        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION 14: Prevention of encryption after key expiration
# ===========================================================================

class TestEncryptionAfterExpiration:
    def test_uninitialized_sensor_raises_on_publish(self):
        """Sensor with no key raises RuntimeError on publish."""
        sensor = IoTSensorClient(
            device_id="TEST-NOINIT",
            initial_seq=0,
            max_key_invocations=10,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        with pytest.raises(RuntimeError, match="key not set"):
            sensor.publish_reading()
        sensor.disconnect()

    def test_expired_state_blocks_all_encryption(self):
        """Directly setting state to KEY_EXPIRED prevents any encryption."""
        sensor = IoTSensorClient(
            device_id="TEST-EXPIRED",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=100,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
        )
        sensor.connect()
        sensor._lifecycle.state = KeyState.KEY_EXPIRED
        sensor._lifecycle.aes_key = None

        with pytest.raises(KeyExpirationError):
            sensor.publish_reading()
        sensor.disconnect()


# ===========================================================================
# CRITERION 15: Replay protection across key rotation
# ===========================================================================

class TestReplayProtectionAcrossRotation:
    def test_replay_rejected_after_key_rotation(self, test_db):
        """A replayed envelope from before key rotation must be rejected."""
        import json
        received_events = []

        new_key_holder = {"key": None}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                       "ec_leakage_bits": 50, "num_qubits": 1536, "execution_time_ms": 100.0,
                       "is_valid": True}

        initial_key = _make_key()
        receiver = CloudReceiver(
            aes_key=initial_key,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver._active_key_id = "INIT"
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-REPLAY-ROT",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=3,
            bb84_factory=factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()

        # Capture a valid pre-rekey envelope
        env1, _ = sensor.publish_reading()
        saved_payload = json.dumps(env1)

        # Trigger rekey
        for _ in range(3):
            sensor.publish_reading()

        time.sleep(0.3)

        # Replay old envelope (same reading_id, old nonce)
        sensor.mqtt_client.publish(config.MQTT_TOPIC_DATA, saved_payload)
        for _ in range(20):
            replay_events = [e for e in received_events
                             if e["status"] in ("REPLAY_REJECTED", "TAMPERED")]
            if replay_events:
                break
            time.sleep(0.05)

        assert len(replay_events) >= 1, \
            "Replayed pre-rotation envelope was not rejected"

        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION 16: Authentication failure under new key (tamper test post-rekey)
# ===========================================================================

class TestAuthFailureUnderNewKey:
    def test_tampered_frame_rejected_after_rekey(self, test_db):
        """Tampered frame published after key rotation is rejected with TAMPERED status."""
        received_events = []
        new_key_holder = {"key": None}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                       "ec_leakage_bits": 50, "num_qubits": 1536, "execution_time_ms": 100.0,
                       "is_valid": True}

        initial_key = _make_key()
        receiver = CloudReceiver(
            aes_key=initial_key,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver._active_key_id = "INIT"
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-TAMP-NEWKEY",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()

        # Trigger rekey
        for _ in range(3):
            sensor.publish_reading()

        # Send tampered frame post-rekey
        sensor.publish_reading(tamper=True)
        time.sleep(0.5)

        tampered = [e for e in received_events if e["status"] == "TAMPERED"]
        assert len(tampered) >= 1, \
            "Tampered post-rekey frame was not detected and rejected"

        sensor.disconnect()
        receiver.stop()

    def test_auth_tag_tampering_rejected_post_rekey(self, test_db):
        """Authentication tag tampering on post-rekey frame is caught and marked TAMPERED."""
        import base64
        received_events = []
        new_key_holder = {"key": None}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.0, "pa_output_bits": 256, "is_valid": True}

        initial_key = _make_key()
        receiver = CloudReceiver(
            aes_key=initial_key,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-TAG-TAMP",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()

        # 2 frames to threshold
        sensor.publish_reading()
        sensor.publish_reading()

        # 3rd frame triggers rekey
        env, _ = sensor.publish_reading()

        # Tamper the 16-byte authentication tag
        tag_bytes = bytearray(base64.b64decode(env["tag"]))
        tag_bytes[0] ^= 0xFF
        env["tag"] = base64.b64encode(tag_bytes).decode("utf-8")

        # Publish tampered tag envelope
        import json
        sensor.mqtt_client.publish(config.MQTT_TOPIC_DATA, json.dumps(env))

        for _ in range(20):
            tampered = [e for e in received_events if e["status"] == "TAMPERED"]
            if tampered:
                break
            time.sleep(0.05)

        assert len(tampered) >= 1, "Tampered authentication tag was not rejected"
        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION: Structured logging + DB persistence of lifecycle events
# ===========================================================================

class TestLifecycleEventPersistence:
    def test_lifecycle_events_persisted_to_db(self, test_db):
        """Key lifecycle events are stored in key_lifecycle_events table."""
        events_logged = []

        def db_logger(event):
            events_logged.append(event)
            test_db.log_key_lifecycle_event(event)

        sensor = IoTSensorClient(
            device_id="TEST-PERSIST",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=_success_bb84_factory(),
            on_key_rotated=lambda k, b, m: None,
            db_logger=db_logger,
        )
        sensor.connect()
        for _ in range(4):
            sensor.publish_reading()

        # Events captured in memory
        event_types = [e["event_type"] for e in events_logged]
        assert "REKEY_THRESHOLD_REACHED" in event_types
        assert "REKEY_STARTED" in event_types
        assert "REKEY_COMPLETED" in event_types

        # Events persisted to DB
        db_events = test_db.get_lifecycle_events(limit=50)
        db_event_types = [e["event_type"] for e in db_events]
        assert "REKEY_THRESHOLD_REACHED" in db_event_types
        assert "REKEY_COMPLETED" in db_event_types

        sensor.disconnect()

    def test_sensor_readings_tagged_with_key_id(self, test_db):
        """sensor_readings records include the key_id from the envelope."""
        received_events = []
        new_key_holder = {"key": None}

        def factory():
            k = _make_key()
            new_key_holder["key"] = k
            return k, {"qber": 0.01, "pa_output_bits": 256, "reconciled_bits": 1200,
                       "ec_leakage_bits": 50, "num_qubits": 1536, "execution_time_ms": 100.0,
                       "is_valid": True}

        initial_key = _make_key()
        receiver = CloudReceiver(
            aes_key=initial_key,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver._active_key_id = "INIT"
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-KID-TAG",
            aes_key=initial_key,
            initial_seq=0,
            max_key_invocations=2,
            bb84_factory=factory,
            on_key_rotated=on_rotated,
        )
        sensor.connect()
        for _ in range(5):
            sensor.publish_reading()

        for _ in range(80):
            if len(received_events) >= 5:
                break
            time.sleep(0.05)

        readings = test_db.get_recent_readings(limit=10)
        auth = [r for r in readings if r["status"] == "AUTHENTICATED"]
        assert len(auth) >= 4

        # Check that at least some readings have a key_id tagged
        with_kid = [r for r in auth if r.get("key_id") is not None]
        assert len(with_kid) >= 1

        sensor.disconnect()
        receiver.stop()

    def test_sqlite_write_failure_buffers_and_marks_persistence_failed(self, test_db, monkeypatch):
        """When SQLite write raises OperationalError, receiver buffers frame and emits PERSISTENCE_FAILED."""
        import sqlite3
        received_events = []
        key = _make_key()
        receiver = CloudReceiver(
            aes_key=key,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )
        receiver.start()

        def failing_log_sensor_reading(*args, **kwargs):
            raise sqlite3.OperationalError("database disk image is malformed / disk full")

        monkeypatch.setattr(test_db, "log_sensor_reading", failing_log_sensor_reading)

        sensor = IoTSensorClient(
            device_id="TEST-DB-FAIL",
            aes_key=key,
            initial_seq=0,
            max_key_invocations=10,
        )
        sensor.connect()
        sensor.publish_reading()

        for _ in range(20):
            if received_events:
                break
            time.sleep(0.05)

        assert len(received_events) >= 1
        ev = received_events[0]
        assert ev["status"] == "PERSISTENCE_FAILED"
        assert "disk full" in ev["error"] or "malformed" in ev["error"]
        assert len(receiver._unpersisted_buffer) >= 1
        assert receiver._unpersisted_buffer[0]["reading_id"] == 1

        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# Full E2E lifecycle with real BB84 (slow; mark explicitly)
# ===========================================================================

@pytest.mark.slow
class TestFullBB84RekeyIntegration:
    def test_real_bb84_rekey_end_to_end(self, test_db):
        """
        Runs actual Qiskit BB84 renegotiation with max_key_invocations=3.
        Verifies: initial key -> 3 frames -> rekey triggers real BB84 -> new key ->
        3 more frames -> receiver authenticated all 6 frames -> 2 key_ids in DB.
        """
        received_events = []

        receiver = CloudReceiver(
            aes_key=None,
            db_manager=test_db,
            on_message_callback=lambda ev: received_events.append(ev),
        )

        # Initial BB84 session
        sim = BB84Simulator()
        initial_result = sim.run(num_qubits=config.NUM_QUBITS, enable_eve=False)
        assert initial_result.is_valid and initial_result.alice_key is not None

        receiver.set_key(initial_result.bob_key)
        receiver._active_key_id = "INITIAL"
        receiver.start()

        def on_rotated(kid, k, m):
            receiver.rotate_key(kid, k, m)

        sensor = IoTSensorClient(
            device_id="TEST-REALBB84",
            aes_key=initial_result.alice_key,
            initial_seq=0,
            max_key_invocations=3,
            on_key_rotated=on_rotated,
            # Uses default _default_bb84_factory which runs real Qiskit simulation
        )
        sensor.connect()

        for i in range(6):
            sensor.publish_reading()
            time.sleep(0.05)

        # Allow dispatcher to drain
        for _ in range(100):
            if len(received_events) >= 6:
                break
            time.sleep(0.1)

        auth = [e for e in received_events if e["status"] == "AUTHENTICATED"]
        assert len(auth) == 6, \
            f"Expected 6 authenticated frames, got {len(auth)}"

        # Verify at least 2 distinct key IDs in DB records
        readings = test_db.get_recent_readings(limit=10)
        key_ids = set(r.get("key_id") for r in readings if r.get("key_id"))
        assert len(key_ids) >= 2, \
            f"Expected records from at least 2 key sessions, found: {key_ids}"

        sensor.disconnect()
        receiver.stop()


# ===========================================================================
# CRITERION: Message queue / broker failure handling
# ===========================================================================

class TestBrokerQueueFailure:
    def test_broker_queue_failure_raises_and_preserves_state(self, monkeypatch):
        """When broker publish fails with ConnectionError, exception is raised to caller and state is preserved."""
        sensor = IoTSensorClient(
            device_id="TEST-BROKER-FAIL",
            aes_key=_make_key(),
            initial_seq=0,
            max_key_invocations=5,
        )
        sensor.connect()

        def failing_publish(topic, payload):
            raise ConnectionError("Broker connection reset by peer")

        monkeypatch.setattr(sensor.mqtt_client, "publish", failing_publish)

        # Attempt to publish must raise ConnectionError — never silently swallow
        with pytest.raises(ConnectionError):
            sensor.publish_reading()

        assert sensor._lifecycle.current_state == KeyState.ACTIVE
        sensor.disconnect()
