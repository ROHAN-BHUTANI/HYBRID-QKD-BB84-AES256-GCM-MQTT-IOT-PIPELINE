"""
BENCHMARK SIMULATED BROKER (QUEUE FALLBACK)
Measures the 8 performance and reliability dimensions for the in-memory SimulatedBroker:
1. Connection establishment latency
2. Publish-to-receive latency
3. End-to-end latency (telemetry publish to receiver database commit)
4. Message loss rate
5. Reconnection latency and recovery
6. Burst traffic throughput and latency under load (500 packets)
7. Duplicate delivery rate
8. Receiver processing delay (decryption + anti-replay check + database commit)
"""

import sys
import os
import time
import json
import statistics
import csv
from typing import List, Dict

sys.path.insert(0, ".")

import config
from broker.broker_bridge import SimulatedBroker, LocalSimulatedClient
from iot_client.sensor_client import IoTSensorClient
from iot_client.crypto_utils import CryptoUtils
from cloud_receiver.receiver import CloudReceiver
from cloud_receiver.database import DatabaseManager

def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = int(len(sorted_d) * p)
    return sorted_d[min(idx, len(sorted_d) - 1)]

def run_queue_fallback_evaluation() -> Dict:
    print("=" * 70)
    print("IN-MEMORY QUEUE FALLBACK (SIMULATED BROKER) COMPREHENSIVE BENCHMARK")
    print("=" * 70)
    
    # Generate test key
    test_key = os.urandom(32)
    temp_db_path = os.path.join(config.DATABASE_DIR, "test_queue_bench.db")
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    db = DatabaseManager(db_path=temp_db_path)
    
    # 1. Connection establishment latency (50 trials)
    print("[1/8] Measuring connection establishment latency (50 trials)...")
    conn_times_ms = []
    for _ in range(50):
        t0 = time.perf_counter()
        client = LocalSimulatedClient("bench_client")
        client.connect()
        t1 = time.perf_counter()
        client.disconnect()
        conn_times_ms.append((t1 - t0) * 1000.0)
    
    # 2. Publish-to-receive latency & 3. Message loss & 7. Duplicate delivery (200 packets)
    print("[2/8] Measuring publish-to-receive latency, loss, and duplicate delivery (200 packets)...")
    received_events = []
    received_ids = []
    broker = SimulatedBroker()
    
    topic = "bench/pub_sub"
    
    def on_msg(t, payload):
        rec_time = time.perf_counter()
        data = json.loads(payload)
        received_events.append((data["seq"], data["send_time"], rec_time))
        received_ids.append(data["seq"])
        
    broker.subscribe(topic, on_msg)
    
    n_packets = 200
    for seq in range(1, n_packets + 1):
        send_time = time.perf_counter()
        payload = json.dumps({"seq": seq, "send_time": send_time, "val": 25.5})
        broker.publish(topic, payload)
        time.sleep(0.001)  # 1ms pace
        
    # Wait for queue to drain
    time.sleep(0.2)
    
    pub_sub_latencies_ms = [(rec - send) * 1000.0 for (_, send, rec) in received_events]
    loss_count = n_packets - len(received_events)
    loss_rate = loss_count / n_packets
    duplicate_count = len(received_ids) - len(set(received_ids))
    duplicate_rate = duplicate_count / max(1, len(received_ids))
    
    # 4. End-to-End Latency & 8. Receiver Processing Delay
    print("[4/8] Measuring end-to-end latency & receiver processing delay (100 full pipeline packets)...")
    e2e_records = []
    receiver = CloudReceiver(
        aes_key=test_key,
        db_manager=db,
        on_message_callback=lambda msg: e2e_records.append(msg)
    )
    receiver.start()
    
    sensor_client = IoTSensorClient(aes_key=test_key, initial_seq=1)
    sensor_client.connect()
    
    n_e2e = 100
    for _ in range(n_e2e):
        sensor_client.publish_reading()
        time.sleep(0.005)
        
    time.sleep(0.3)
    sensor_client.disconnect()
    receiver.stop()
    
    e2e_latencies_ms = [r["e2e_latency_ms"] for r in e2e_records if "e2e_latency_ms" in r]
    dec_latencies_ms = [r.get("dec_latency_ms", 0.0) for r in e2e_records if "dec_latency_ms" in r]
    
    # 5. Reconnection Latency & Reliability (20 cycles)
    print("[5/8] Measuring reconnection latency and recovery (20 cycles)...")
    reconn_times_ms = []
    reconn_success = 0
    test_client = LocalSimulatedClient("reconn_client")
    test_client.connect()
    for _ in range(20):
        t0 = time.perf_counter()
        test_client.disconnect()
        ok = test_client.connect()
        t1 = time.perf_counter()
        if ok and test_client.connected:
            reconn_success += 1
            reconn_times_ms.append((t1 - t0) * 1000.0)
    test_client.disconnect()
    
    # 6. Burst traffic evaluation (500 packets dispatched simultaneously)
    print("[6/8] Measuring burst traffic throughput (500 packets instant dispatch)...")
    burst_received = []
    burst_topic = "bench/burst"
    
    def on_burst(t, p):
        burst_received.append((time.perf_counter(), json.loads(p)["id"]))
        
    broker.subscribe(burst_topic, on_burst)
    
    n_burst = 500
    t_burst_start = time.perf_counter()
    for i in range(n_burst):
        broker.publish(burst_topic, json.dumps({"id": i, "data": "BURST_PAYLOAD_TEST"}))
    t_burst_dispatched = time.perf_counter()
    
    # Wait for all burst packets to be received
    timeout = 5.0
    t_wait_start = time.time()
    while len(burst_received) < n_burst and (time.time() - t_wait_start < timeout):
        time.sleep(0.01)
    t_burst_finished = time.perf_counter()
    
    burst_dispatch_ms = (t_burst_dispatched - t_burst_start) * 1000.0
    burst_total_drain_ms = (t_burst_finished - t_burst_start) * 1000.0
    burst_throughput = len(burst_received) / (burst_total_drain_ms / 1000.0) if burst_total_drain_ms > 0 else 0
    burst_loss = n_burst - len(burst_received)
    
    results = {
        "transport_type": "In-Memory Python Queue (SimulatedBroker)",
        "connection_ms_mean": round(statistics.mean(conn_times_ms), 4),
        "connection_ms_std": round(statistics.stdev(conn_times_ms), 4),
        "pub_to_rec_ms_mean": round(statistics.mean(pub_sub_latencies_ms), 4),
        "pub_to_rec_ms_median": round(statistics.median(pub_sub_latencies_ms), 4),
        "pub_to_rec_ms_p95": round(percentile(pub_sub_latencies_ms, 0.95), 4),
        "pub_to_rec_ms_p99": round(percentile(pub_sub_latencies_ms, 0.99), 4),
        "e2e_latency_ms_mean": round(statistics.mean(e2e_latencies_ms), 4),
        "e2e_latency_ms_std": round(statistics.stdev(e2e_latencies_ms), 4),
        "e2e_latency_ms_median": round(statistics.median(e2e_latencies_ms), 4),
        "e2e_latency_ms_p95": round(percentile(e2e_latencies_ms, 0.95), 4),
        "message_loss_count": loss_count,
        "message_loss_rate_pct": round(loss_rate * 100.0, 2),
        "duplicate_count": duplicate_count,
        "duplicate_rate_pct": round(duplicate_rate * 100.0, 2),
        "reconnect_ms_mean": round(statistics.mean(reconn_times_ms), 4),
        "reconnect_success_rate_pct": round((reconn_success / 20.0) * 100.0, 1),
        "burst_packets_sent": n_burst,
        "burst_packets_received": len(burst_received),
        "burst_loss_count": burst_loss,
        "burst_total_drain_ms": round(burst_total_drain_ms, 2),
        "burst_throughput_msg_per_sec": round(burst_throughput, 1),
        "receiver_processing_delay_ms_mean": round(statistics.mean(dec_latencies_ms), 4),
        "receiver_processing_delay_ms_median": round(statistics.median(dec_latencies_ms), 4),
    }
    
    print("\n" + "=" * 70)
    print("QUEUE FALLBACK BENCHMARK RESULTS")
    print("=" * 70)
    for k, v in results.items():
        print(f"  {k:<35}: {v}")
        
    return results

if __name__ == "__main__":
    out_csv = "queue_fallback_benchmark_results.csv"
    res = run_queue_fallback_evaluation()
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(res.keys()))
        writer.writeheader()
        writer.writerow(res)
    print(f"\nSaved Queue fallback benchmark to {out_csv}")
