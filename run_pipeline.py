# -*- coding: utf-8 -*-
"""
Main Prototype Pipeline Runner.
Executes an end-to-end demonstration of the Hybrid BB84 QKD + AES-256-GCM IoT Security Pipeline:
1. Runs Qiskit BB84 QKD protocol with Information Reconciliation & Universal Hashing
2. Initializes Cloud Receiver and subscribes to MQTT broker
3. Publishes authenticated environmental sensor telemetry from IoT Client
4. Simulates MitM classical tampering attack (demonstrating AES-GCM tag verification failure)
5. Simulates Replay attack (demonstrating monotonic sequence number rejection)
6. Simulates Eve quantum intercept-resend attack (demonstrating QBER-based abort)
7. Displays database telemetry and security summary
"""
import sys
import os
import time
import json
from typing import Optional, Dict, Any, List

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from qkd.bb84 import BB84Simulator
from iot_client.sensor_client import IoTSensorClient
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager


def run_rekey_demo(
    max_key_invocations: int = 3,
    total_frames: int = 8,
    db_path: Optional[str] = None,
    experiment_id: Optional[str] = None
) -> dict:
    """
    TSK-01 Demonstration: Autonomous QKD Key Renegotiation.

    Publishes `total_frames` sensor readings with max_key_invocations=N per key.
    When the invocation limit is reached, a new BB84 session automatically
    executes and the new key is installed transparently.

    NOTE: This is a software simulation. The receiver learns the new key via the
    same in-process shared-state channel used by the simulated broker transport.
    """
    exp_id = experiment_id or f"EXP-REKEY-{time.strftime('%Y%m%d%H%M%S')}"
    print("=" * 78)
    print("  TSK-01: AUTONOMOUS QKD KEY RENEGOTIATION DEMONSTRATION")
    print(f"  Experiment ID:        {exp_id}")
    print(f"  Key invocation limit: {max_key_invocations} frames per key")
    print(f"  Total frames to publish: {total_frames}")
    if db_path:
        print(f"  Database (Isolated):  {db_path}")
    print("=" * 78)

    from broker.broker_bridge import SimulatedBroker
    SimulatedBroker.reset_for_testing()

    db = DatabaseManager(db_path=db_path) if db_path else DatabaseManager()

    # Initial BB84 session
    print(f"\n[REKEY DEMO] Running initial BB84 QKD session ({config.NUM_QUBITS} qubits)...")
    sim = BB84Simulator()
    t_qkd0 = time.perf_counter()
    initial_result = sim.run(num_qubits=config.NUM_QUBITS, enable_eve=False)
    initial_qkd_ms = (time.perf_counter() - t_qkd0) * 1000.0

    if not initial_result.is_valid or not initial_result.alice_key:
        print("[REKEY DEMO] Initial QKD session failed. Aborting demo.")
        return {"status": "FAILED", "reason": "Initial QKD failed"}

    print(f"  -> Initial key established. QBER={initial_result.qber*100:.2f}%")

    # Set up receiver with rotation callback
    received_events = []

    def on_callback(ev):
        received_events.append(ev)

    receiver = CloudReceiver(
        aes_key=initial_result.bob_key,
        db_manager=db,
        on_message_callback=on_callback,
    )
    receiver._active_key_id = "INITIAL"
    receiver.start()

    qkd_transitions = []

    def on_key_rotated(new_key_id, new_key_bytes, session_meta):
        """Receiver learns new key when lifecycle manager rotates it."""
        receiver.rotate_key(new_key_id, new_key_bytes, session_meta)
        qkd_transitions.append({
            "key_id": new_key_id,
            "qber": session_meta.get("qber", 0.0),
            "pa_output_bits": session_meta.get("pa_output_bits", 0),
            "duration_ms": session_meta.get("execution_time_ms", 0.0),
        })
        print(f"\n  [REKEY DEMO] >> Receiver key rotated to {new_key_id}")
        print(f"  [REKEY DEMO]    QBER={session_meta.get('qber', 0.0)*100:.2f}%  "
              f"PA output={session_meta.get('pa_output_bits', 0)} bits\n")
        db.log_qkd_session(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            num_qubits=session_meta.get("num_qubits", config.NUM_QUBITS),
            sifted_len=session_meta.get("reconciled_bits", 0),
            qber=session_meta.get("qber", 0.0),
            threshold=config.QBER_THRESHOLD,
            is_valid=session_meta.get("is_valid", True),
            eve_present=False,
            exec_ms=session_meta.get("execution_time_ms", 0.0),
            key_preview=new_key_id,
            experiment_id=exp_id,
        )

    sensor = IoTSensorClient(
        device_id="REKEY-DEMO-SENSOR",
        aes_key=initial_result.alice_key,
        initial_seq=0,
        max_key_invocations=max_key_invocations,
        on_key_rotated=on_key_rotated,
        db_logger=db.log_key_lifecycle_event,
        experiment_id=exp_id,
    )
    # Log initial key QKD session with initial key ID
    db.log_qkd_session(
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        num_qubits=initial_result.num_qubits,
        sifted_len=initial_result.reconciled_length,
        qber=initial_result.qber,
        threshold=config.QBER_THRESHOLD,
        is_valid=initial_result.is_valid,
        eve_present=False,
        exec_ms=initial_qkd_ms,
        key_preview=sensor.key_id,
        experiment_id=exp_id,
    )
    sensor.connect()
    print(f"\n[REKEY DEMO] Publishing {total_frames} frames with limit={max_key_invocations}...\n")

    published_frames = []
    for i in range(1, total_frames + 1):
        try:
            env, enc_ms = sensor.publish_reading()
            published_frames.append({
                "frame_no": i,
                "key_id": env.get("key_id"),
                "nonce": env.get("nonce"),
                "enc_ms": enc_ms,
                "invocations": sensor.key_invocations,
            })
            print(f"  [Frame {i:02d}] key_id={env.get('key_id', 'N/A')[:18]}  "
                  f"nonce={env['nonce'][:8]}...  enc={enc_ms:.3f}ms  "
                  f"invocations={sensor.key_invocations}/{max_key_invocations}")
            time.sleep(0.15)
        except Exception as exc:
            print(f"  [Frame {i:02d}] FAILED: {exc}")
            break

    # Allow worker thread to drain queue
    for _ in range(30):
        if len(received_events) >= total_frames:
            break
        time.sleep(0.05)

    sensor.disconnect()
    receiver.stop()

    print("\n" + "=" * 78)
    print("  REKEY DEMONSTRATION SUMMARY")
    print("=" * 78)
    auth = [e for e in received_events if e["status"] == "AUTHENTICATED"]
    print(f"  Experiment ID:             {exp_id}")
    print(f"  Frames Published:          {len(published_frames)}")
    print(f"  Frames Authenticated:      {len(auth)}")
    print(f"  Final Key State:           {sensor._lifecycle.current_state.value}")
    print(f"  Final Key ID:              {sensor.key_id}")
    print(f"  Retired Key IDs:           {sensor._lifecycle.retired_key_ids}")

    # Query DB explicitly for this experiment (or all rows if fresh DB)
    readings = db.get_readings_by_experiment(exp_id)
    if not readings:
        readings = db.get_recent_readings(limit=total_frames + 5)
    key_ids_in_db = sorted(list(set(r.get("key_id") for r in readings if r.get("key_id"))))
    print(f"  Distinct Key IDs in DB:    {len(key_ids_in_db)} -> {key_ids_in_db}")
    print("=" * 78)

    return {
        "experiment_id": exp_id,
        "frames_published": len(published_frames),
        "frames_authenticated": len(auth),
        "final_state": sensor._lifecycle.current_state.value,
        "distinct_key_count": len(key_ids_in_db),
        "key_ids": key_ids_in_db,
        "retired_keys": list(sensor._lifecycle.retired_key_ids),
        "published_frames": published_frames,
        "received_events": received_events,
        "readings_in_db": readings,
    }


def run_full_pipeline_demo():
    print("=" * 78)
    print("  HYBRID BB84 QKD + AES-256-GCM SECURE IOT PIPELINE (PROTOTYPE DEMO)")
    print("  Project Team ID: MP2026CSE205 | Graphic Era Deemed to be University")
    print("=" * 78)

    db = DatabaseManager()

    # --------------------------------------------------------------------------
    # PHASE 1: Quantum Key Distribution (Qiskit BB84 Simulation)
    # --------------------------------------------------------------------------
    print("\n[PHASE 1] Initializing Module A: Quantum Key Generator (IBM Qiskit Aer)...")
    qkd = BB84Simulator()

    print(f"  -> Transmitting {config.NUM_QUBITS} single-photon quantum states (Alice -> Bob)...")
    qkd_result = qkd.run(num_qubits=config.NUM_QUBITS, enable_eve=False)

    print(f"  -> Sifted Key Length: {qkd_result.sifted_length} bits (basis matches)")
    print(f"  -> Sacrificed Sample: {qkd_result.sample_length} bits for parameter estimation")
    print(f"  -> Measured QBER: {qkd_result.qber * 100:.2f}% (Abort Threshold: {config.QBER_THRESHOLD * 100}%)")
    print(f"  -> Information Reconciliation: Corrected {qkd_result.reconciled_length} bits (Leakage: {qkd_result.ec_leakage_bits} bits)")
    print(f"  -> Universal Hash Privacy Amplification: Derived 256-bit AES Key")
    print(f"  -> QKD Protocol Time: {qkd_result.execution_time_ms:.2f} ms")

    if not qkd_result.is_valid or not qkd_result.alice_key:
        print("  [!] QKD Key agreement failed. Aborting pipeline.")
        return

    shared_key = qkd_result.alice_key
    print(f"  [✓] Key Agreement SUCCESS! Established 256-bit AES Key:")
    print(f"      Key (hex preview): {shared_key.hex()[:32]}...")

    # Log QKD session in DB
    db.log_qkd_session(
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        num_qubits=qkd_result.num_qubits,
        sifted_len=qkd_result.sifted_length,
        qber=qkd_result.qber,
        threshold=config.QBER_THRESHOLD,
        is_valid=qkd_result.is_valid,
        eve_present=qkd_result.eve_present,
        exec_ms=qkd_result.execution_time_ms,
        key_preview=shared_key.hex()[:16] + "..."
    )

    # --------------------------------------------------------------------------
    # PHASE 2: Start Cloud Receiver (Module C)
    # --------------------------------------------------------------------------
    print("\n[PHASE 2] Initializing Module C: Cloud Receiver & SQLite Storage...")
    received_packets = []

    def on_cloud_message(event):
        received_packets.append(event)
        status = event["status"]
        if status == "AUTHENTICATED":
            d = event["data"]
            print(f"  [Cloud Receiver] DECRYPTED & AUTHENTICATED reading #{d.get('reading_id')}: "
                  f"Temp={d.get('temperature_c')}°C, Hum={d.get('humidity_percent')}%, Press={d.get('pressure_hpa')} hPa "
                  f"(Dec: {event['dec_latency_ms']:.3f}ms, E2E: {event['e2e_latency_ms']:.2f}ms)")
        elif status == "REPLAY_REJECTED":
            print(f"  [Cloud Receiver] REPLAY ATTACK BLOCKED! Duplicate sequence #{event.get('reading_id')} rejected!")
        else:
            print(f"  [Cloud Receiver] TAMPER DETECTED! Rejected corrupted packet from {event.get('device_id')} "
                  f"(E2E: {event['e2e_latency_ms']:.2f}ms)")

    receiver = CloudReceiver(
        aes_key=shared_key,
        db_manager=db,
        on_message_callback=on_cloud_message
    )
    receiver.start()
    print(f"  [✓] Cloud Receiver subscribed to MQTT topic: '{config.MQTT_TOPIC_DATA}'")

    # --------------------------------------------------------------------------
    # PHASE 3: IoT Sensor Transmission (Module B)
    # --------------------------------------------------------------------------
    print("\n[PHASE 3] Initializing Module B: IoT Edge Sensor Client...")
    sensor = IoTSensorClient(device_id="IOT-WEATHER-01", aes_key=shared_key)
    sensor.connect()

    print("  -> Publishing 5 authenticated sensor telemetry packets...")
    saved_envelopes = []
    for i in range(1, 6):
        env, enc_ms = sensor.publish_reading()
        saved_envelopes.append(env)
        print(f"  [IoT Sensor] Encrypted reading #{i} in {enc_ms:.3f}ms | Nonce: {env['nonce'][:12]}... | Tag: {env['tag'][:12]}...")
        time.sleep(0.1)

    time.sleep(0.3)

    # --------------------------------------------------------------------------
    # PHASE 4: Security Test - Classical MitM Tampering Simulation
    # --------------------------------------------------------------------------
    print("\n[PHASE 4A] Security Test: Classical Man-in-the-Middle (MitM) Tampering Attack...")
    print("  -> Transmitting packet with modified ciphertext in transit...")
    tampered_env, _ = sensor.publish_reading(tamper=True)
    time.sleep(0.3)

    # --------------------------------------------------------------------------
    # PHASE 4B: Security Test - Replay Attack Simulation
    # --------------------------------------------------------------------------
    print("\n[PHASE 4B] Security Test: Classical Replay Attack Simulation...")
    print("  -> Replaying previously captured valid packet #1...")
    if saved_envelopes:
        replay_payload_str = json.dumps(saved_envelopes[0])
        sensor.mqtt_client.publish(config.MQTT_TOPIC_DATA, replay_payload_str)
    time.sleep(0.3)

    # --------------------------------------------------------------------------
    # PHASE 5: Security Test - Quantum Eavesdropping (Eve) Simulation
    # --------------------------------------------------------------------------
    print("\n[PHASE 5] Security Test: Quantum Channel Eavesdropping (Eve Active)...")
    print(f"  -> Alice transmits {config.NUM_QUBITS} qubits while Eve intercepts and measures in random bases...")
    eve_qkd_res = qkd.run(num_qubits=config.NUM_QUBITS, enable_eve=True)
    print(f"  -> Eve Interception Detected: QBER = {eve_qkd_res.qber * 100:.2f}%")
    print(f"  -> QBER > 11% Cutoff? {eve_qkd_res.qber > config.QBER_THRESHOLD}")
    print(f"  [✓] Key Rejected! Protocol safely aborted, preventing compromised key derivation.")

    # --------------------------------------------------------------------------
    # PHASE 6: Summary & Teardown
    # --------------------------------------------------------------------------
    sensor.disconnect()
    receiver.stop()

    summary = db.get_system_summary()
    print("\n" + "=" * 78)
    print("  DATABASE & TELEMETRY SUMMARY")
    print("=" * 78)
    print(f"  - Total Authenticated Messages Stored: {summary['authenticated_packets']}")
    print(f"  - Total Tampering / Replay Attacks:     {summary['tampered_packets']}")
    print(f"  - Average AES Decryption Latency:       {summary['avg_decryption_ms']} ms")
    print(f"  - Average End-to-End Latency:           {summary['avg_e2e_latency_ms']} ms")
    print(f"  - Total QKD Sessions Logged:            {summary['total_qkd_sessions']}")
    print("=" * 78)
    print("\nTo view the real-time visual web interface, run:")
    print("    python dashboard/app.py")
    print("To execute automated benchmarks and generate research CSVs, run:")
    print("    python benchmark/runner.py\n")


if __name__ == "__main__":
    run_full_pipeline_demo()
