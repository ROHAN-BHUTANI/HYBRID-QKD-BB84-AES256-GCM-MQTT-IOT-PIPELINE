# -*- coding: utf-8 -*-
"""
Repeatable Multi-Run Demonstration Script for TSK-01 Acceptance Audit.
Executes 5 independent clean demonstrations of autonomous QKD key renegotiation.
"""
import os
import sys
import json
import time
import tempfile
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import run_pipeline
from broker.broker_bridge import SimulatedBroker

def run_five_demonstrations():
    print("=" * 80)
    print("  EXECUTING 5 INDEPENDENT CLEAN REKEY DEMONSTRATIONS (PHASE 5)")
    print("  Threshold: 3 invocations/key | Frames: 8 | Real Qiskit Aer Simulation")
    print("=" * 80)

    runs_summary = []
    frames_records = []

    for run_idx in range(1, 6):
        SimulatedBroker.reset_for_testing()
        exp_id = f"EXP-REPRO-RUN{run_idx:02d}-{int(time.time())}"
        tmp_db = os.path.join(tempfile.gettempdir(), f"rekey_demo_run_{run_idx}.db")
        if os.path.exists(tmp_db):
            os.remove(tmp_db)

        print(f"\n>>> Starting Run {run_idx}/5: {exp_id}")
        t0 = time.perf_counter()
        res = run_pipeline.run_rekey_demo(
            max_key_invocations=3,
            total_frames=8,
            db_path=tmp_db,
            experiment_id=exp_id
        )
        total_duration_sec = time.perf_counter() - t0

        # Query isolated database
        conn = sqlite3.connect(tmp_db)
        c = conn.cursor()

        readings = c.execute(
            "SELECT id, reading_id, key_id, status, decryption_latency_ms, e2e_latency_ms FROM sensor_readings ORDER BY id ASC"
        ).fetchall()

        qkd_sessions = c.execute(
            "SELECT id, num_qubits, sifted_length, qber, is_valid, execution_time_ms, key_preview FROM qkd_sessions ORDER BY id ASC"
        ).fetchall()

        lifecycle_events = c.execute(
            "SELECT id, event_type, state, key_id, old_key_id, new_key_id FROM key_lifecycle_events ORDER BY id ASC"
        ).fetchall()

        conn.close()

        # Check key generation distribution
        gen1_keys = [r[2] for r in readings[0:3]]
        gen2_keys = [r[2] for r in readings[3:6]]
        gen3_keys = [r[2] for r in readings[6:8]]

        distinct_keys = sorted(list(set(r[2] for r in readings)))
        gen1_consistent = (len(set(gen1_keys)) == 1)
        gen2_consistent = (len(set(gen2_keys)) == 1)
        gen3_consistent = (len(set(gen3_keys)) == 1)
        generations_distinct = (len(distinct_keys) == 3)

        all_auth = all(r[3] == "AUTHENTICATED" for r in readings)
        total_auth = sum(1 for r in readings if r[3] == "AUTHENTICATED")
        total_failed = len(readings) - total_auth

        avg_dec_ms = sum(r[4] for r in readings) / len(readings) if readings else 0.0

        run_data = {
            "run_index": run_idx,
            "experiment_id": exp_id,
            "db_path": tmp_db,
            "total_frames_published": res["frames_published"],
            "total_frames_authenticated": total_auth,
            "total_frames_failed": total_failed,
            "distinct_key_count": len(distinct_keys),
            "key_gen_1": gen1_keys[0] if gen1_keys else None,
            "key_gen_2": gen2_keys[0] if gen2_keys else None,
            "key_gen_3": gen3_keys[0] if gen3_keys else None,
            "gen1_consistent": gen1_consistent,
            "gen2_consistent": gen2_consistent,
            "gen3_consistent": gen3_consistent,
            "generations_mutually_distinct": generations_distinct,
            "all_authenticated": all_auth,
            "qkd_session_count": len(qkd_sessions),
            "qkd_sessions": [
                {"session_no": s[0], "qubits": s[1], "sifted": s[2], "qber": s[3], "valid": bool(s[4]), "exec_ms": round(s[5], 2), "key_id": s[6]}
                for s in qkd_sessions
            ],
            "lifecycle_event_count": len(lifecycle_events),
            "avg_decryption_ms": round(avg_dec_ms, 3),
            "total_run_duration_sec": round(total_duration_sec, 2),
            "status": "PASS" if (all_auth and generations_distinct and len(readings) == 8) else "FAIL"
        }
        runs_summary.append(run_data)

        for r in readings:
            frames_records.append({
                "run_index": run_idx,
                "experiment_id": exp_id,
                "row_id": r[0],
                "reading_id": r[1],
                "key_id": r[2],
                "status": r[3],
                "dec_latency_ms": r[4],
                "e2e_latency_ms": r[5]
            })

    # Save to JSON and CSV
    with open("repeatable_rekey_benchmarks.json", "w") as f:
        json.dump(runs_summary, f, indent=2)

    df_runs = pd.DataFrame(runs_summary)
    # Exclude nested lists from CSV
    df_runs_flat = df_runs.drop(columns=["qkd_sessions"])
    df_runs_flat.to_csv("repeatable_rekey_benchmarks.csv", index=False)

    df_frames = pd.DataFrame(frames_records)
    df_frames.to_csv("repeatable_rekey_frames.csv", index=False)

    print("\n" + "=" * 80)
    print("  PHASE 5 REPEATABLE DEMONSTRATION SUMMARY (5/5 RUNS)")
    print("=" * 80)
    for r in runs_summary:
        k1 = r['key_gen_1'][:12] if r['key_gen_1'] else 'N/A'
        k2 = r['key_gen_2'][:12] if r['key_gen_2'] else 'N/A'
        k3 = r['key_gen_3'][:12] if r['key_gen_3'] else 'N/A'
        print(f"Run {r['run_index']} ({r['experiment_id']}): Status={r['status']} | "
              f"Frames={r['total_frames_authenticated']}/8 Auth | "
              f"Keys={r['distinct_key_count']} distinct ({k1} -> {k2} -> {k3}) | "
              f"QKD Sessions={r['qkd_session_count']} | Run Time={r['total_run_duration_sec']}s")
    print("=" * 80)

if __name__ == "__main__":
    run_five_demonstrations()
