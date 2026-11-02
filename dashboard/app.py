# -*- coding: utf-8 -*-
"""
Module E: Flask Web Dashboard.
Provides a real-time web interface for monitoring:
- Live IoT sensor telemetry
- QKD key agreement status and QBER levels
- MitM tampering alerts and AES-256-GCM verification
- Interactive buttons to trigger BB84 simulation and IoT transmissions
"""
import sys
import os
import time

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from qkd.bb84 import BB84Simulator
from iot_client.sensor_client import IoTSensorClient
from cloud_receiver.database import DatabaseManager
from cloud_receiver.receiver import CloudReceiver

app = Flask(__name__)
db = DatabaseManager()
qkd_sim = BB84Simulator()

# Global pipeline state
active_key = None
active_receiver = None
active_client = None


def init_pipeline():
    """Initializes the active key and background receiver."""
    global active_key, active_receiver, active_client
    if active_key is None:
        # Run an initial clean BB84 session to establish the shared key
        res = qkd_sim.run(num_qubits=config.NUM_QUBITS, enable_eve=False)
        if res.is_valid and res.alice_key:
            active_key = res.alice_key
            db.log_qkd_session(
                timestamp=datetime.now(timezone.utc).isoformat(),
                num_qubits=res.num_qubits,
                sifted_len=res.sifted_length,
                qber=res.qber,
                threshold=config.QBER_THRESHOLD,
                is_valid=res.is_valid,
                eve_present=res.eve_present,
                exec_ms=res.execution_time_ms,
                key_preview=active_key.hex()[:16] + "..."
            )

    if active_receiver is None:
        active_receiver = CloudReceiver(aes_key=active_key, db_manager=db)
        active_receiver.start()

    if active_client is None:
        active_client = IoTSensorClient(aes_key=active_key)
        active_client.connect()


@app.route("/")
def index():
    init_pipeline()
    return render_template("index.html")


@app.route("/api/stats")
def get_stats():
    summary = db.get_system_summary()
    latest_qkd = db.get_latest_qkd_session()
    return jsonify({
        "summary": summary,
        "latest_qkd": latest_qkd,
        "active_key_preview": active_key.hex()[:16] + "..." if active_key else "NONE"
    })


@app.route("/api/readings")
def get_readings():
    readings = db.get_recent_readings(limit=25)
    return jsonify(readings)


@app.route("/api/alerts")
def get_alerts():
    alerts = db.get_security_alerts(limit=20)
    return jsonify(alerts)


@app.route("/api/run_qkd", methods=["POST"])
def run_qkd():
    global active_key
    data = request.get_json() or {}
    enable_eve = bool(data.get("enable_eve", False))
    num_qubits = int(data.get("num_qubits", config.NUM_QUBITS))

    res = qkd_sim.run(num_qubits=num_qubits, enable_eve=enable_eve)
    
    key_preview = ""
    if res.is_valid and res.alice_key:
        active_key = res.alice_key
        if active_receiver:
            active_receiver.set_key(active_key)
        if active_client:
            active_client.set_key(active_key)
        key_preview = active_key.hex()[:16] + "..."

    db.log_qkd_session(
        timestamp=datetime.now(timezone.utc).isoformat(),
        num_qubits=res.num_qubits,
        sifted_len=res.sifted_length,
        qber=res.qber,
        threshold=config.QBER_THRESHOLD,
        is_valid=res.is_valid,
        eve_present=res.eve_present,
        exec_ms=res.execution_time_ms,
        key_preview=key_preview
    )

    return jsonify({
        "success": True,
        "is_valid": res.is_valid,
        "qber": round(res.qber, 4),
        "threshold": config.QBER_THRESHOLD,
        "eve_present": res.eve_present,
        "num_qubits": res.num_qubits,
        "sifted_length": res.sifted_length,
        "remaining_length": res.remaining_length,
        "execution_time_ms": round(res.execution_time_ms, 2),
        "key_preview": key_preview
    })


@app.route("/api/send_reading", methods=["POST"])
def send_reading():
    init_pipeline()
    data = request.get_json() or {}
    tamper = bool(data.get("tamper", False))

    if not active_client or not active_key:
        return jsonify({"success": False, "error": "Pipeline key not established"}), 400

    envelope, enc_ms = active_client.publish_reading(tamper=tamper)
    # Allow simulated queue to dispatch
    time.sleep(0.05)

    return jsonify({
        "success": True,
        "tampered": tamper,
        "encryption_time_ms": round(enc_ms, 4),
        "envelope_preview": {
            "nonce": envelope["nonce"],
            "tag": envelope["tag"],
            "ciphertext_len": len(envelope["ciphertext"])
        }
    })


if __name__ == "__main__":
    init_pipeline()
    print(f"Starting Flask Dashboard on http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT, debug=False)
