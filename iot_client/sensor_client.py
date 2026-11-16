# -*- coding: utf-8 -*-
"""
Module B: IoT Sensor Client.
Simulates an edge IoT device:
1. Generates environmental telemetry (temperature, humidity, pressure)
2. Tracks monotonic sequence numbers across session restarts
3. Encrypts payload using AES-256-GCM with quantum-derived key and unique nonce
4. Publishes encrypted envelope over MQTT
"""
import sys
import os
import time
import json
import random
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from iot_client.crypto_utils import CryptoUtils
from broker.broker_bridge import get_mqtt_client, BaseMQTTClient


class IoTSensorClient:
    """
    Simulated IoT edge device that encrypts readings with AES-256-GCM and publishes via MQTT.
    """
    def __init__(
        self,
        device_id: str = config.DEVICE_ID,
        aes_key: Optional[bytes] = None,
        initial_seq: Optional[int] = None
    ):
        self.device_id = device_id
        self.aes_key = aes_key
        
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
        self.key_invocations = 0
        self.max_key_invocations = 100_000  # NIST SP 800-38D invocation bound

    def set_key(self, key: bytes):
        """Updates the shared AES-256 key established via BB84 QKD and resets invocation counter."""
        if len(key) != config.AES_KEY_SIZE_BYTES:
            raise ValueError(f"AES key must be {config.AES_KEY_SIZE_BYTES} bytes.")
        self.aes_key = key
        self.key_invocations = 0

    def is_rekey_needed(self) -> bool:
        """Checks if key invocation count has exceeded NIST SP 800-38D threshold."""
        return self.key_invocations >= self.max_key_invocations

    def connect(self):
        """Connects to the MQTT broker."""
        self.mqtt_client.connect()
        self.connected = True

    def disconnect(self):
        """Disconnects from the MQTT broker."""
        self.mqtt_client.disconnect()
        self.connected = False

    def generate_sensor_reading(self) -> Dict[str, Any]:
        """Generates realistic synthetic environmental sensor data."""
        self.seq_num += 1
        now_utc = datetime.now(timezone.utc).isoformat()

        # Realistic atmospheric variations
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
            "pressure_hpa": pressure
        }

    def publish_reading(
        self,
        reading_dict: Optional[Dict[str, Any]] = None,
        tamper: bool = False
    ) -> Tuple[Dict[str, Any], float]:
        """
        Encrypts and publishes a sensor reading over MQTT.

        Args:
            reading_dict: Optional custom dictionary (generates synthetic reading if None)
            tamper: If True, simulates MitM ciphertext modification in transit

        Returns:
            Tuple of (envelope_dict, encryption_time_ms)
        """
        if not self.aes_key:
            raise RuntimeError("Cannot publish: AES-256 key not set. Run BB84 first.")

        self.key_invocations += 1

        if reading_dict is None:
            reading_dict = self.generate_sensor_reading()

        # Encrypt with AES-256-GCM
        envelope, enc_time = CryptoUtils.encrypt_payload(self.aes_key, reading_dict)

        # Inject intentional MitM tampering if requested
        if tamper:
            raw_ct = list(envelope["ciphertext"])
            # Flip character in base64 string
            raw_ct[0] = 'Z' if raw_ct[0] != 'Z' else 'Y'
            envelope["ciphertext"] = "".join(raw_ct)

        # Publish over MQTT
        payload_str = json.dumps(envelope)
        self.mqtt_client.publish(config.MQTT_TOPIC_DATA, payload_str)

        return envelope, enc_time
