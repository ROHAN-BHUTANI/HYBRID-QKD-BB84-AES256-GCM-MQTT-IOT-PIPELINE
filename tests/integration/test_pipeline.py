# -*- coding: utf-8 -*-
"""
Integration tests for the hybrid QKD-to-IoT pipeline.
"""
import pytest
import time
import os

from qkd.bb84 import BB84Simulator
from iot_client.sensor_client import IoTSensorClient
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager
import config


def test_qkd_to_aes_integration(tmp_path):
    """Verify BB84 negotiated key operates seamlessly with IoT client and cloud receiver."""
    # 1. Run BB84 key agreement
    sim = BB84Simulator()
    res = sim.run(num_qubits=256, enable_eve=False)
    assert res.is_valid is True
    assert res.alice_key is not None

    # 2. Setup temporary DB and Cloud Receiver
    db_path = str(tmp_path / "integration_test.db")
    db = DatabaseManager(db_path=db_path)

    received_events = []
    receiver = CloudReceiver(
        aes_key=res.bob_key,
        db_manager=db,
        on_message_callback=lambda ev: received_events.append(ev)
    )
    receiver.start()

    # 3. Setup IoT Sensor Client with Alice's key
    sensor = IoTSensorClient(
        device_id="INTEG-NODE-01",
        aes_key=res.alice_key,
        initial_seq=0
    )
    sensor.connect()

    # 4. Transmit 3 readings
    for _ in range(3):
        sensor.publish_reading()
        time.sleep(0.05)

    time.sleep(0.2)

    # 5. Verify reception & DB records
    assert len(received_events) == 3
    assert all(ev["status"] == "AUTHENTICATED" for ev in received_events)

    readings = db.get_recent_readings(limit=10)
    assert len(readings) == 3
    assert readings[0]["status"] == "AUTHENTICATED"

    # 6. Test Tampering
    sensor.publish_reading(tamper=True)
    time.sleep(0.2)

    assert len(received_events) == 4
    assert received_events[-1]["status"] == "TAMPERED"

    alerts = db.get_security_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["alert_type"] == "INTEGRITY_VIOLATION"

    # Cleanup
    sensor.disconnect()
    receiver.stop()
