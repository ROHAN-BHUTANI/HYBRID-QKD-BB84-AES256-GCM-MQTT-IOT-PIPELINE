# -*- coding: utf-8 -*-
"""
Module C: Cloud Receiver.
Subscribes to incoming IoT sensor envelopes over MQTT, decrypts with AES-256-GCM,
verifies cryptographic authentication tags, enforces stateful anti-replay protection,
records end-to-end latency, and persists data in SQLite.
"""
import sys
import os
import time
import json
from typing import Optional, Callable, Dict, Any, Tuple

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.exceptions import InvalidTag

import config
from iot_client.crypto_utils import CryptoUtils
from cloud_receiver.database import DatabaseManager
from broker.broker_bridge import get_mqtt_client, BaseMQTTClient


class SlidingWindowAntiReplay:
    """
    RFC 4303 / RFC 6347 64-Packet Sliding Window Anti-Replay Filter.
    Maintains a 64-bit bitmap of received sequence IDs per device.
    Tolerates bounded network reordering while strictly rejecting duplicate/stale packets.
    """
    def __init__(self, window_size: int = 64):
        self.window_size = window_size
        self.windows: Dict[str, Tuple[int, int]] = {}  # device_id -> (max_seq, bitmap)

    def check_and_update(self, device_id: str, seq: int) -> Tuple[bool, str]:
        if device_id not in self.windows:
            self.windows[device_id] = (seq, 1)
            return True, "FIRST_PACKET"

        max_seq, bitmap = self.windows[device_id]

        if seq > max_seq:
            diff = seq - max_seq
            if diff < self.window_size:
                bitmap = (bitmap << diff) | 1
                bitmap &= (1 << self.window_size) - 1
            else:
                bitmap = 1
            self.windows[device_id] = (seq, bitmap)
            return True, "WINDOW_ADVANCED"
        elif seq > max_seq - self.window_size:
            offset = max_seq - seq
            if (bitmap >> offset) & 1:
                return False, f"DUPLICATE_IN_WINDOW (offset {offset} behind max #{max_seq})"
            else:
                bitmap |= (1 << offset)
                self.windows[device_id] = (max_seq, bitmap)
                return True, f"OUT_OF_ORDER_ACCEPTED (offset {offset} behind max #{max_seq})"
        else:
            return False, f"STALE_PACKET (seq #{seq} older than window max #{max_seq} - {self.window_size})"


class CloudReceiver:
    """
    Cloud gateway server listening for MQTT sensor telemetry, enforcing AES-256-GCM verification,
    RFC 64-packet sliding window anti-replay protection, and SQLite persistence.
    """
    def __init__(
        self,
        aes_key: Optional[bytes] = None,
        db_manager: Optional[DatabaseManager] = None,
        on_message_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.aes_key = aes_key
        self.db = db_manager or DatabaseManager()
        self.on_message_callback = on_message_callback
        self.mqtt_client: BaseMQTTClient = get_mqtt_client("cloud_receiver_sub")
        self.is_subscribed = False
        self.anti_replay = SlidingWindowAntiReplay(window_size=64)

    def set_key(self, key: bytes):
        """Sets the shared AES-256 key established via BB84 QKD."""
        if len(key) != config.AES_KEY_SIZE_BYTES:
            raise ValueError(f"AES key must be {config.AES_KEY_SIZE_BYTES} bytes.")
        self.aes_key = key

    def start(self):
        """Starts subscription to the MQTT sensor topic."""
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(config.MQTT_TOPIC_DATA, self._on_mqtt_message)
        self.is_subscribed = True

    def stop(self):
        """Stops subscription and disconnects."""
        self.mqtt_client.disconnect()
        self.is_subscribed = False

    def _on_mqtt_message(self, topic: str, payload_str: str):
        """Handler triggered when an encrypted packet arrives on MQTT."""
        recv_time_ns = time.time_ns()
        try:
            envelope = json.loads(payload_str)
        except Exception as e:
            print(f"[CloudReceiver Error] Malformed JSON: {e}")
            return

        sent_time_ns = envelope.get("timestamp_ns", recv_time_ns)
        e2e_latency_ms = max(0.0, (recv_time_ns - sent_time_ns) / 1_000_000.0)
        device_id = envelope.get("device_id", "UNKNOWN_DEVICE")

        if not self.aes_key:
            print(f"[CloudReceiver Warning] Key not set. Dropping message from {device_id}.")
            return

        try:
            # Decrypt with AES-256-GCM and verify 128-bit authentication tag
            decrypted_data, dec_latency_ms = CryptoUtils.decrypt_payload(
                self.aes_key, envelope
            )

            reading_id = decrypted_data.get("reading_id")
            sensor_ts = decrypted_data.get("timestamp", "")
            temp = decrypted_data.get("temperature_c")
            humidity = decrypted_data.get("humidity_percent")
            pressure = decrypted_data.get("pressure_hpa")

            # --- RFC 4303 / 6347 Sliding Window Anti-Replay Verification ---
            if reading_id is not None:
                is_fresh, replay_reason = self.anti_replay.check_and_update(device_id, reading_id)
                if not is_fresh:
                    # Replay attack detected! Sequence number has already been seen or is stale
                    print(f"[SECURITY ALERT] Replay attack detected from {device_id}! Reason: {replay_reason}.")
                    self.db.log_security_alert(
                        alert_type="REPLAY_ATTACK",
                        details=f"Sequence number #{reading_id} rejected: {replay_reason}.",
                        device_id=device_id,
                        severity="HIGH"
                    )
                    self.db.log_sensor_reading(
                        device_id=device_id,
                        reading_id=reading_id,
                        sensor_timestamp=sensor_ts,
                        temp=temp,
                        humidity=humidity,
                        pressure=pressure,
                        status="REPLAY_REJECTED",
                        dec_latency_ms=dec_latency_ms,
                        e2e_latency_ms=e2e_latency_ms
                    )
                    if self.on_message_callback:
                        self.on_message_callback({
                            "status": "REPLAY_REJECTED",
                            "device_id": device_id,
                            "reading_id": reading_id,
                            "e2e_latency_ms": e2e_latency_ms
                        })
                    return

                # Record watermark in database
                self.db.update_device_sequence(device_id, reading_id)

            # Successfully authenticated & fresh reading
            self.db.log_sensor_reading(
                device_id=device_id,
                reading_id=reading_id,
                sensor_timestamp=sensor_ts,
                temp=temp,
                humidity=humidity,
                pressure=pressure,
                status="AUTHENTICATED",
                dec_latency_ms=dec_latency_ms,
                e2e_latency_ms=e2e_latency_ms
            )

            if self.on_message_callback:
                self.on_message_callback({
                    "status": "AUTHENTICATED",
                    "data": decrypted_data,
                    "dec_latency_ms": dec_latency_ms,
                    "e2e_latency_ms": e2e_latency_ms
                })

        except InvalidTag:
            # Authentication tag mismatch: tampering detected!
            dec_latency_ms = 0.0
            print(f"[SECURITY ALERT] Tampering detected in message from {device_id}!")
            self.db.log_security_alert(
                alert_type="INTEGRITY_VIOLATION",
                details="AES-256-GCM authentication tag mismatch. Ciphertext or nonce modified in transit.",
                device_id=device_id,
                severity="CRITICAL"
            )
            self.db.log_sensor_reading(
                device_id=device_id,
                reading_id=None,
                sensor_timestamp="",
                temp=None,
                humidity=None,
                pressure=None,
                status="TAMPERED",
                dec_latency_ms=dec_latency_ms,
                e2e_latency_ms=e2e_latency_ms
            )

            if self.on_message_callback:
                self.on_message_callback({
                    "status": "TAMPERED",
                    "device_id": device_id,
                    "e2e_latency_ms": e2e_latency_ms
                })
        except Exception as ex:
            print(f"[CloudReceiver Error] Unexpected exception during processing: {ex}")


if __name__ == "__main__":
    import os
    test_key = os.urandom(32)
    receiver = CloudReceiver(aes_key=test_key)
    receiver.start()
    print("Cloud Receiver initialized and subscribed to", config.MQTT_TOPIC_DATA)
    time.sleep(1)
    receiver.stop()
