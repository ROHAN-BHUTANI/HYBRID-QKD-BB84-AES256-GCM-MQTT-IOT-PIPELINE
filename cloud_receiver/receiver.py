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
from typing import Optional, Callable, Dict, Any

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.exceptions import InvalidTag

import config
from iot_client.crypto_utils import CryptoUtils
from cloud_receiver.database import DatabaseManager
from broker.broker_bridge import get_mqtt_client, BaseMQTTClient


class CloudReceiver:
    """
    Cloud gateway server listening for MQTT sensor telemetry, enforcing AES-256-GCM verification,
    anti-replay sequence tracking, and SQLite persistence.
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

            # --- Anti-Replay Verification ---
            last_seq = self.db.get_device_sequence(device_id)
            if reading_id is not None and reading_id <= last_seq:
                # Replay attack detected! Sequence number has already been seen or is stale
                print(f"[SECURITY ALERT] Replay attack detected from {device_id}! "
                      f"Reading ID #{reading_id} <= last seen watermark #{last_seq}.")
                self.db.log_security_alert(
                    alert_type="REPLAY_ATTACK",
                    details=f"Duplicate or stale sequence number #{reading_id} received (watermark: #{last_seq}).",
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

            # Update sequence watermark
            if reading_id is not None:
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
