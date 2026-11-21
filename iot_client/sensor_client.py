# -*- coding: utf-8 -*-
"""
Module B: IoT Sensor Client.
Simulates an edge IoT device:
1. Generates environmental telemetry (temperature, humidity, pressure)
2. Tracks monotonic sequence numbers across session restarts
3. Enforces key lifecycle via KeyLifecycleManager (invocation limit + automatic rekeying)
4. Encrypts payload using AES-256-GCM with quantum-derived key and unique nonce
5. Publishes encrypted envelope over MQTT

NOTE: Rekeying is initiated automatically when the invocation counter reaches max_key_invocations.
Publishing pauses during rekeying and resumes under the new key.
This is a software prototype; it does NOT implement a cryptographically secure
out-of-band key management channel.
"""
import sys
import os
import time
import json
import logging
import random
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple, Callable

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from iot_client.crypto_utils import CryptoUtils
from broker.broker_bridge import get_mqtt_client, BaseMQTTClient
from qkd.key_lifecycle import KeyLifecycleManager, KeyState, KeyExpirationError, RekeyFailedError

logger = logging.getLogger(__name__)


class IoTSensorClient:
    """
    Simulated IoT edge device that encrypts readings with AES-256-GCM and publishes via MQTT.

    Key lifecycle is managed by KeyLifecycleManager which enforces invocation limits
    and automatically triggers BB84 renegotiation before the active key is exhausted.
    """

    def __init__(
        self,
        device_id: str = config.DEVICE_ID,
        aes_key: Optional[bytes] = None,
        initial_seq: Optional[int] = None,
        max_key_invocations: int = 100_000,
        bb84_factory: Optional[Callable] = None,
        on_key_rotated: Optional[Callable] = None,
        db_logger: Optional[Callable] = None,
    ):
        self.device_id = device_id

        # Initialize sequence from DB watermark if not explicitly provided
        if initial_seq is None:
            try:
                from cloud_receiver.database import DatabaseManager
                db = DatabaseManager()
                self.seq_num = db.get_device_sequence(device_id)
            except Exception:
                self.seq_num = 0
        else:
            self.seq_num = initial_seq

        self.mqtt_client: BaseMQTTClient = get_mqtt_client(f"{device_id}_pub")
        self.connected = False

        # --- Key Lifecycle Manager ---
        # bb84_factory must return (key_bytes, session_meta_dict) or raise on failure.
        # on_key_rotated notifies the receiver of the new key.
        self._lifecycle = KeyLifecycleManager(
            bb84_factory=bb84_factory or self._default_bb84_factory,
            on_key_rotated=on_key_rotated or self._noop_key_rotated,
            max_invocations=max_key_invocations,
            db_logger=db_logger,
        )

        # Install the initial key if provided at construction time
        if aes_key is not None:
            self._lifecycle.install_initial_key(aes_key, {"pa_output_bits": len(aes_key) * 8})

        # Legacy compatibility: expose key_invocations and max_key_invocations as properties
        self.max_key_invocations = max_key_invocations

    # ------------------------------------------------------------------
    # Legacy compatibility shims (preserve existing public interface)
    # ------------------------------------------------------------------

    @property
    def aes_key(self) -> Optional[bytes]:
        return self._lifecycle.aes_key

    @property
    def key_invocations(self) -> int:
        return self._lifecycle.current_invocation_count

    @property
    def key_id(self) -> Optional[str]:
        return self._lifecycle.current_key_id

    def set_key(self, key: bytes, session_meta: Optional[Dict[str, Any]] = None):
        """
        Updates the shared AES-256 key and resets invocation counter.
        Used for initial setup or manual testing.
        """
        if len(key) != config.AES_KEY_SIZE_BYTES:
            raise ValueError(f"AES key must be {config.AES_KEY_SIZE_BYTES} bytes.")
        meta = session_meta or {"pa_output_bits": len(key) * 8}
        if self._lifecycle.state == KeyState.UNINITIALIZED:
            self._lifecycle.install_initial_key(key, meta)
        else:
            # Force install a new key (for testing purposes only)
            self._lifecycle._retire_key_locked(self._lifecycle.key_id)
            new_id = self._lifecycle._generate_key_id()
            self._lifecycle._install_key_locked(new_id, key, meta, "MANUAL_SET_KEY")
            self._lifecycle.state = KeyState.ACTIVE

    def is_rekey_needed(self) -> bool:
        """Checks if key invocation count has exceeded the configured threshold."""
        return self._lifecycle.current_state in (KeyState.REKEY_REQUIRED, KeyState.REKEYING)

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self):
        """Connects to the MQTT broker."""
        self.mqtt_client.connect()
        self.connected = True

    def disconnect(self):
        """Disconnects from the MQTT broker."""
        self.mqtt_client.disconnect()
        self.connected = False

    # ------------------------------------------------------------------
    # Telemetry generation
    # ------------------------------------------------------------------

    def generate_sensor_reading(self) -> Dict[str, Any]:
        """Generates realistic synthetic environmental sensor data."""
        self.seq_num += 1
        now_utc = datetime.now(timezone.utc).isoformat()

        temp = round(22.0 + random.uniform(-4.0, 6.0), 2)
        humidity = round(55.0 + random.uniform(-10.0, 15.0), 2)
        pressure = round(1013.25 + random.uniform(-5.0, 5.0), 2)

        return {
            "device_id": self.device_id,
            "reading_id": self.seq_num,
            "timestamp": now_utc,
            "sensor_type": "BME280_ENVIRONMENTAL",
            "temperature_c": temp,
            "humidity_percent": humidity,
            "pressure_hpa": pressure,
        }

    # ------------------------------------------------------------------
    # Core publish — integrates lifecycle enforcement
    # ------------------------------------------------------------------

    def publish_reading(
        self,
        reading_dict: Optional[Dict[str, Any]] = None,
        tamper: bool = False,
    ) -> Tuple[Dict[str, Any], float]:
        """
        Encrypts and publishes a sensor reading over MQTT.

        LIFECYCLE ENFORCEMENT:
          - Calls pre_encrypt_check() which atomically increments the invocation counter.
          - If the threshold has been reached, pre_encrypt_check() triggers synchronous
            BB84 renegotiation before returning the new key.
          - If rekeying fails, KeyExpirationError / RekeyFailedError is raised and no
            encryption occurs; the pending reading is preserved and re-raised to caller.

        Returns:
            Tuple of (envelope_dict, encryption_time_ms)
        Raises:
            RuntimeError: If called before any key is installed.
            KeyExpirationError: If the key is expired and rekeying failed.
            RekeyFailedError: If BB84 renegotiation was attempted and failed.
        """
        if self._lifecycle.state == KeyState.UNINITIALIZED:
            raise RuntimeError("Cannot publish: AES-256 key not set. Run BB84 first.")

        # This call enforces the invocation limit and triggers rekeying if needed.
        # It raises KeyExpirationError / RekeyFailedError on irrecoverable failure.
        active_key = self._lifecycle.pre_encrypt_check()

        # Transition KEY_ESTABLISHED -> ACTIVE on first successful publish
        self._lifecycle.mark_active()

        if reading_dict is None:
            reading_dict = self.generate_sensor_reading()

        # Encrypt with AES-256-GCM using the key returned by pre_encrypt_check()
        # (which may be a new key after transparent rekeying)
        envelope, enc_time = CryptoUtils.encrypt_payload(active_key, reading_dict)

        # Stamp the key ID on the envelope for receiver correlation
        envelope["key_id"] = self._lifecycle.current_key_id

        # Inject intentional MitM tampering if requested (testing only)
        if tamper:
            raw_ct = list(envelope["ciphertext"])
            raw_ct[0] = 'Z' if raw_ct[0] != 'Z' else 'Y'
            envelope["ciphertext"] = "".join(raw_ct)

        # Publish over MQTT
        payload_str = json.dumps(envelope)
        self.mqtt_client.publish(config.MQTT_TOPIC_DATA, payload_str)

        logger.debug(
            "[SensorClient] Published reading_id=%s key_id=%s invocations=%d",
            reading_dict.get("reading_id"),
            envelope["key_id"],
            self._lifecycle.current_invocation_count,
        )

        return envelope, enc_time

    # ------------------------------------------------------------------
    # Private defaults
    # ------------------------------------------------------------------

    @staticmethod
    def _default_bb84_factory():
        """
        Default BB84 factory used when no custom factory is injected.
        Runs the full Qiskit simulation and returns (key_bytes, metadata).
        Returns (None, metadata) if QBER threshold is exceeded.
        """
        from qkd.bb84 import BB84Simulator
        sim = BB84Simulator()
        result = sim.run(num_qubits=config.NUM_QUBITS, enable_eve=False)
        meta = {
            "qber": result.qber,
            "pa_output_bits": len(result.alice_key) * 8 if result.alice_key else 0,
            "reconciled_bits": result.reconciled_length,
            "ec_leakage_bits": result.ec_leakage_bits,
            "num_qubits": result.num_qubits,
            "execution_time_ms": result.execution_time_ms,
            "is_valid": result.is_valid,
        }
        if not result.is_valid or result.alice_key is None:
            return None, meta
        return result.alice_key, meta

    @staticmethod
    def _noop_key_rotated(new_key_id: str, new_key_bytes: bytes, session_meta: dict):
        """Default no-op callback — used when no receiver is registered."""
        logger.warning(
            "[SensorClient] Key rotated to %s but no on_key_rotated callback registered.",
            new_key_id,
        )
