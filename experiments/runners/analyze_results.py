# -*- coding: utf-8 -*-
"""
Statistical Analyzer for Scientific Experiments.
Computes summary statistics (mean, std, 95% confidence intervals) across all 7 experiments
and outputs LaTeX and Markdown formatted tables in experiments/processed_results/summary_tables.md.
"""
import os
import csv
import math
from collections import defaultdict
from typing import List, Dict, Any


def mean_std(values: List[float]):
    if not values:
        return 0.0, 0.0, 0.0
    n = len(values)
    m = sum(values) / n
    if n > 1:
        variance = sum((x - m) ** 2 for x in values) / (n - 1)
        std = math.sqrt(variance)
        ci95 = 1.96 * (std / math.sqrt(n))
    else:
        std = 0.0
        ci95 = 0.0
    return round(m, 4), round(std, 4), round(ci95, 4)


def read_csv(filepath: str) -> List[Dict[str, str]]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def analyze_exp1(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp1_qkd_scaling.csv")
    if not os.path.exists(path):
        return "EXP-1 results not found."
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[int(r["num_qubits"])].append(r)

    md = "### Table 1: EXP-1 QKD Circuit Scaling & Post-Processing Yield\n\n"
    md += "| Qubit Block Size ($N$) | Sifted Bits ($\mu$) | Reconciled Bits ($\mu$) | QBER ($\mu \pm \sigma$) | Execution Time (ms) ($\mu \pm \sigma$) | Convergence Rate (%) |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for n in sorted(grouped.keys()):
        items = grouped[n]
        sifted = [float(x["sifted_bits"]) for x in items]
        reconciled = [float(x["reconciled_bits"]) for x in items]
        qber = [float(x["qber"]) for x in items]
        exec_t = [float(x["exec_time_ms"]) for x in items]
        valid = [int(x["is_valid"]) for x in items]

        s_m, _, _ = mean_std(sifted)
        r_m, _, _ = mean_std(reconciled)
        q_m, q_s, _ = mean_std(qber)
        t_m, t_s, _ = mean_std(exec_t)
        v_rate = (sum(valid) / len(valid)) * 100.0

        md += f"| {n} | {s_m:.1f} | {r_m:.1f} | {q_m:.4f} $\\pm$ {q_s:.4f} | {t_m:.2f} $\\pm$ {t_s:.2f} | {v_rate:.1f}% |\n"

    return md


def analyze_exp2(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp2_eve_density.csv")
    if not os.path.exists(path):
        return "EXP-2 results not found."
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[float(r["p_eve"])].append(r)

    md = "### Table 2: EXP-2 QBER & Abort Probability vs. Interception Density ($p_{\\text{eve}}$)\n\n"
    md += "| Interception Prob ($p_{\\text{eve}}$) | Empirical QBER ($\mu \pm \sigma$) | Theoretical QBER ($p/4$) | Key Abort Rate (%) | Security Decision |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"

    for p in sorted(grouped.keys()):
        items = grouped[p]
        qber = [float(x["qber"]) for x in items]
        aborts = [int(x["key_aborted"]) for x in items]
        q_m, q_s, _ = mean_std(qber)
        p_theo = p * 0.25
        abort_rate = (sum(aborts) / len(aborts)) * 100.0
        decision = "ACCEPT (Clean / Tolerable)" if abort_rate == 0 else "ABORT (Eve Detected)"

        md += f"| {p:.1f} | {q_m:.4f} $\\pm$ {q_s:.4f} | {p_theo:.4f} | {abort_rate:.1f}% | {decision} |\n"

    return md


def analyze_exp3(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp3_channel_noise.csv")
    if not os.path.exists(path):
        return "EXP-3 results not found."
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[float(r["noise_param"])].append(r)

    md = "### Table 3: EXP-3 Channel Depolarizing Noise vs. Cascade Reconciliation Success\n\n"
    md += "| Depolarizing Param ($\lambda$) | Sample QBER ($\mu \pm \sigma$) | EC Parity Leakage (Bits) | Success Rate ($QBER \\le 11\\%$) |\n"
    md += "| :--- | :--- | :--- | :--- |\n"

    for lmb in sorted(grouped.keys()):
        items = grouped[lmb]
        qber = [float(x["qber"]) for x in items]
        leakage = [float(x["ec_leakage_bits"]) for x in items]
        valid = [int(x["is_valid"]) for x in items]

        q_m, q_s, _ = mean_std(qber)
        l_m, _, _ = mean_std(leakage)
        v_rate = (sum(valid) / len(valid)) * 100.0

        md += f"| {lmb:.2f} | {q_m:.4f} $\\pm$ {q_s:.4f} | {l_m:.1f} | {v_rate:.1f}% |\n"

    return md


def analyze_exp4(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp4_crypto_throughput.csv")
    if not os.path.exists(path):
        return "EXP-4 results not found."
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[int(r["payload_size_bytes"])].append(r)

    md = "### Table 4: EXP-4 AES-256-GCM Latency and Cryptographic Throughput\n\n"
    md += "| Payload (Bytes) | Encryption Time ($\mu \pm \sigma$ ms) | Decryption Time ($\mu \pm \sigma$ ms) | Enc Throughput (KB/s) | Dec Throughput (KB/s) |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"

    for sz in sorted(grouped.keys()):
        items = grouped[sz]
        enc = [float(x["encryption_time_ms"]) for x in items]
        dec = [float(x["decryption_time_ms"]) for x in items]

        e_m, e_s, _ = mean_std(enc)
        d_m, d_s, _ = mean_std(dec)

        enc_tp = (sz / (e_m / 1000.0)) / 1024.0 if e_m > 0 else 0
        dec_tp = (sz / (d_m / 1000.0)) / 1024.0 if d_m > 0 else 0

        md += f"| {sz} | {e_m:.4f} $\\pm$ {e_s:.4f} | {d_m:.4f} $\\pm$ {d_s:.4f} | {enc_tp:,.1f} | {dec_tp:,.1f} |\n"

    return md


def analyze_exp5(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp5_tamper_detection.csv")
    if not os.path.exists(path):
        return "EXP-5 results not found."
    rows = read_csv(path)
    ct = [int(x["ciphertext_tamper_detected"]) for x in rows]
    nonce = [int(x["nonce_tamper_detected"]) for x in rows]
    tag = [int(x["tag_tamper_detected"]) for x in rows]
    n = len(rows)

    md = "### Table 5: EXP-5 Cryptographic Tamper Detection Rate\n\n"
    md += "| Attack Vector | Trials Tested | Rejections by GMAC / GCM | Detection Rate (%) | Security Margin |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"
    md += f"| Ciphertext Inversion (1-bit) | {n} | {sum(ct)} | {(sum(ct)/n)*100.0:.1f}% | 128-bit MAC Integrity |\n"
    md += f"| Nonce Corruption (1-byte) | {n} | {sum(nonce)} | {(sum(nonce)/n)*100.0:.1f}% | AEAD Authentication Trap |\n"
    md += f"| Authentication Tag Tamper | {n} | {sum(tag)} | {(sum(tag)/n)*100.0:.1f}% | Tag Collision Bound $2^{{-128}}$ |\n"

    return md


def analyze_exp6(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp6_e2e_latency.csv")
    if not os.path.exists(path):
        return "EXP-6 results not found."
    rows = read_csv(path)
    lat = [float(x["e2e_latency_ms"]) for x in rows if float(x["e2e_latency_ms"]) > 0]
    enc = [float(x["encryption_ms"]) for x in rows]

    l_m, l_s, l_ci = mean_std(lat)
    e_m, e_s, _ = mean_std(enc)

    md = "### Table 6: EXP-6 End-to-End Latency Profile (Local Queue Mode)\n\n"
    md += "| Metric | Latency (ms) | Notes |\n"
    md += "| :--- | :--- | :--- |\n"
    md += f"| Mean E2E Latency | {l_m:.3f} $\\pm$ {l_s:.3f} | Encrypt + Queue Dispatch + Decrypt + DB Commit |\n"
    md += f"| 95% Confidence Interval | [{l_m - l_ci:.3f}, {l_m + l_ci:.3f}] | $N = {len(lat)}$ repetitions |\n"
    md += f"| Mean AES-GCM Encrypt Overhead | {e_m:.4f} $\\pm$ {e_s:.4f} | Cryptographic primitive overhead |\n"
    md += f"| Cryptographic Overhead Share | {((e_m / l_m) * 100.0 if l_m > 0 else 0):.2f}% | Negligible fraction of E2E transit |\n"

    return md


def analyze_exp7(raw_dir: str) -> str:
    path = os.path.join(raw_dir, "exp7_baseline_comparison.csv")
    if not os.path.exists(path):
        return "EXP-7 results not found."
    rows = read_csv(path)

    md = "### Table 7: EXP-7 Comparative Baseline Evaluation\n\n"
    md += "| Communication Architecture | Key Exchange Mechanism | Handshake Latency (ms) | Packet Overhead (B) | Quantum Security Guarantee | Tamper Detection |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for r in rows:
        md += f"| {r['scheme']} | {r['key_exchange_mechanism']} | {r['handshake_time_ms']} | {r['per_packet_overhead_bytes']} | {r['quantum_safe']} | {r['tamper_proof']} |\n"

    return md


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base, "raw_results")
    proc_dir = os.path.join(base, "processed_results")
    os.makedirs(proc_dir, exist_ok=True)

    full_md = "# Empirical Research Experiment Results & Statistical Analysis\n\n"
    full_md += "Generated automatically from raw empirical CSV data.\n\n"

    full_md += analyze_exp1(raw_dir) + "\n\n"
    full_md += analyze_exp2(raw_dir) + "\n\n"
    full_md += analyze_exp3(raw_dir) + "\n\n"
    full_md += analyze_exp4(raw_dir) + "\n\n"
    full_md += analyze_exp5(raw_dir) + "\n\n"
    full_md += analyze_exp6(raw_dir) + "\n\n"
    full_md += analyze_exp7(raw_dir) + "\n\n"

    out_file = os.path.join(proc_dir, "summary_tables.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"[SUCCESS] Processed summary tables written to: {out_file}")


if __name__ == "__main__":
    main()
