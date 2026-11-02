# -*- coding: utf-8 -*-
"""
Module F: Benchmarking & Performance Profiling Suite.
Generates comprehensive benchmark data across:
1. QKD execution time and QBER vs Qubit counts (qkd_benchmark.csv)
2. AES-256-GCM encryption time vs Payload size (encryption_benchmark.csv)
3. AES-256-GCM decryption time vs Payload size (decryption_benchmark.csv)
4. End-to-end communication latency (e2e_latency.csv)
5. CPU and RAM resource usage via psutil (resource_usage.csv)
"""
import sys
import os
import csv
import time
import json
import random
import psutil
from typing import List, Dict, Any

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from qkd.bb84 import BB84Simulator
from iot_client.crypto_utils import CryptoUtils
from iot_client.sensor_client import IoTSensorClient
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager


class BenchmarkRunner:
    def __init__(self, out_dir: str = config.BENCHMARK_DIR):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.qkd_sim = BB84Simulator()
        self.process = psutil.Process(os.getpid())

    def benchmark_qkd(self, qubit_counts: List[int] = [128, 256, 512, 1024], repetitions: int = 5):
        """Runs repeated BB84 trials across qubit counts with and without Eve."""
        print("\n--- Running QKD Simulation Benchmark ---")
        csv_path = config.QKD_BENCHMARK_FILE
        records = []

        for n in qubit_counts:
            for eve in [False, True]:
                for trial in range(1, repetitions + 1):
                    mem_before = self.process.memory_info().rss / (1024 * 1024)
                    res = self.qkd_sim.run(num_qubits=n, enable_eve=eve)
                    mem_after = self.process.memory_info().rss / (1024 * 1024)

                    records.append({
                        "qubits": n,
                        "eve_active": 1 if eve else 0,
                        "trial": trial,
                        "sifted_bits": res.sifted_length,
                        "remaining_bits": res.remaining_length,
                        "qber": round(res.qber, 4),
                        "key_valid": 1 if res.is_valid else 0,
                        "qkd_time_ms": round(res.execution_time_ms, 3),
                        "mem_used_mb": round(mem_after - mem_before, 2)
                    })
                    print(f"Qubits={n:4d} | Eve={str(eve):5s} | Trial={trial} | QBER={res.qber:.4f} | Time={res.execution_time_ms:6.2f} ms")

        # Save to CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        print(f"Saved QKD benchmark data to {csv_path}")

    def benchmark_crypto(self, payload_sizes: List[int] = [64, 128, 256, 512, 1024, 2048, 4096], repetitions: int = 50):
        """Benchmarks AES-256-GCM encryption and decryption across payload sizes."""
        print("\n--- Running AES-256-GCM Cryptographic Benchmark ---")
        test_key = os.urandom(config.AES_KEY_SIZE_BYTES)
        
        enc_records = []
        dec_records = []

        for size in payload_sizes:
            enc_times = []
            dec_times = []

            for _ in range(repetitions):
                raw_payload = {"device_id": config.DEVICE_ID, "data": "X" * size}
                
                # Encrypt
                envelope, enc_ms = CryptoUtils.encrypt_payload(test_key, raw_payload)
                enc_times.append(enc_ms)

                # Decrypt
                _, dec_ms = CryptoUtils.decrypt_payload(test_key, envelope)
                dec_times.append(dec_ms)

            avg_enc = sum(enc_times) / len(enc_times)
            avg_dec = sum(dec_times) / len(dec_times)

            enc_records.append({
                "payload_bytes": size,
                "repetitions": repetitions,
                "avg_encryption_ms": round(avg_enc, 4),
                "min_encryption_ms": round(min(enc_times), 4),
                "max_encryption_ms": round(max(enc_times), 4)
            })
            dec_records.append({
                "payload_bytes": size,
                "repetitions": repetitions,
                "avg_decryption_ms": round(avg_dec, 4),
                "min_decryption_ms": round(min(dec_times), 4),
                "max_decryption_ms": round(max(dec_times), 4)
            })

            print(f"Payload={size:4d} B | Avg Encrypt: {avg_enc:.4f} ms | Avg Decrypt: {avg_dec:.4f} ms")

        # Save to CSVs
        with open(config.ENCRYPTION_BENCHMARK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=enc_records[0].keys())
            writer.writeheader()
            writer.writerows(enc_records)
        print(f"Saved Encryption benchmark data to {config.ENCRYPTION_BENCHMARK_FILE}")

        with open(config.DECRYPTION_BENCHMARK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=dec_records[0].keys())
            writer.writeheader()
            writer.writerows(dec_records)
        print(f"Saved Decryption benchmark data to {config.DECRYPTION_BENCHMARK_FILE}")

    def benchmark_e2e(self, packet_count: int = 25):
        """Measures end-to-end communication latency through the entire pipeline."""
        print(f"\n--- Running End-to-End Pipeline Benchmark ({packet_count} packets) ---")
        # Step 1: Generate key via BB84
        res = self.qkd_sim.run(num_qubits=config.NUM_QUBITS, enable_eve=False)
        if not res.is_valid:
            print("QKD key agreement failed. Cannot run E2E benchmark.")
            return

        key = res.alice_key
        db = DatabaseManager()
        e2e_records = []

        receiver = CloudReceiver(
            aes_key=key,
            db_manager=db,
            on_message_callback=lambda msg: e2e_records.append(msg)
        )
        receiver.start()

        client = IoTSensorClient(aes_key=key)
        client.connect()

        for i in range(1, packet_count + 1):
            env, enc_ms = client.publish_reading()
            time.sleep(0.02)  # 20ms pacing

        time.sleep(0.5)  # Allow queue to drain
        client.disconnect()
        receiver.stop()

        # Save E2E CSV
        csv_records = []
        for idx, item in enumerate(e2e_records, 1):
            csv_records.append({
                "packet_id": idx,
                "status": item["status"],
                "decryption_ms": round(item.get("dec_latency_ms", 0.0), 4),
                "e2e_latency_ms": round(item["e2e_latency_ms"], 4)
            })

        if csv_records:
            with open(config.E2E_LATENCY_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=csv_records[0].keys())
                writer.writeheader()
                writer.writerows(csv_records)
            avg_e2e = sum(r["e2e_latency_ms"] for r in csv_records) / len(csv_records)
            print(f"Saved E2E latency data to {config.E2E_LATENCY_FILE} (Avg E2E: {avg_e2e:.3f} ms)")

    def profile_resource_usage(self, duration_sec: int = 5):
        """Profiles CPU and RAM resource usage during intensive pipeline execution."""
        print(f"\n--- Profiling CPU & Memory Resource Overhead ({duration_sec}s) ---")
        records = []
        start_time = time.time()
        
        test_key = os.urandom(config.AES_KEY_SIZE_BYTES)
        sim = BB84Simulator()

        step = 0
        while time.time() - start_time < duration_sec:
            step += 1
            cpu = psutil.cpu_percent(interval=0.1)
            mem = self.process.memory_info().rss / (1024 * 1024)

            # Alternate QKD and AES operations to generate realistic load
            if step % 2 == 0:
                sim.run(num_qubits=256, enable_eve=False)
                op = "QKD_BB84_256"
            else:
                for _ in range(50):
                    CryptoUtils.encrypt_payload(test_key, {"sensor": "test", "val": 22.5})
                op = "AES_GCM_BATCH_50"

            records.append({
                "timestamp_sec": round(time.time() - start_time, 2),
                "active_operation": op,
                "process_cpu_percent": cpu,
                "memory_rss_mb": round(mem, 2)
            })

        with open(config.RESOURCE_USAGE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        print(f"Saved resource usage profile to {config.RESOURCE_USAGE_FILE}")


if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.benchmark_qkd(qubit_counts=[128, 256, 512], repetitions=3)
    runner.benchmark_crypto(payload_sizes=[64, 256, 1024], repetitions=20)
    runner.benchmark_e2e(packet_count=15)
    runner.profile_resource_usage(duration_sec=3)
