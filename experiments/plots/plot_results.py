# -*- coding: utf-8 -*-
"""
Publication Figure Generator for IEEE/ACM Manuscript.
Reads empirical CSV results from experiments/raw_results/
Generates high-resolution publication figures (300 DPI PNG and PDF) in experiments/plots/.
"""
import os
import csv
import math
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def set_pub_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 12,
        "lines.linewidth": 1.5,
        "lines.markersize": 6,
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
    })


def read_csv(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def plot_fig1_scaling(raw_dir: str, out_dir: str):
    path = os.path.join(raw_dir, "exp1_qkd_scaling.csv")
    if not os.path.exists(path):
        return
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[int(r["num_qubits"])].append(r)

    qubits = sorted(grouped.keys())
    times_m = []
    times_s = []
    sifted_m = []
    reconciled_m = []

    for q in qubits:
        items = grouped[q]
        t = [float(x["exec_time_ms"]) for x in items]
        s = [float(x["sifted_bits"]) for x in items]
        rec = [float(x["reconciled_bits"]) for x in items]

        tm = sum(t) / len(t)
        ts = math.sqrt(sum((x - tm) ** 2 for x in t) / (len(t) - 1)) if len(t) > 1 else 0
        times_m.append(tm)
        times_s.append(ts)
        sifted_m.append(sum(s) / len(s))
        reconciled_m.append(sum(rec) / len(rec))

    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax2 = ax1.twinx()

    p1 = ax1.plot(qubits, sifted_m, 'o-', color='#1f77b4', label='Sifted Key (bits)')
    p2 = ax1.plot(qubits, reconciled_m, 's--', color='#2ca02c', label='Reconciled Key (bits)')
    p3 = ax2.errorbar(qubits, times_m, yerr=times_s, fmt='^-', color='#d62728', capsize=4, label='Execution Time (ms)')

    ax1.set_xlabel("Qubit Block Size ($N$)")
    ax1.set_ylabel("Key Length (bits)", color='#1f77b4')
    ax2.set_ylabel("Execution Time (ms)", color='#d62728')
    ax1.grid(True)

    lines = p1 + p2 + [p3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")

    plt.title("QKD Quantum Simulation Scaling & Key Yield")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig1_qkd_scaling.png"), dpi=300)
    plt.savefig(os.path.join(out_dir, "fig1_qkd_scaling.pdf"))
    plt.close()
    print("  -> Saved fig1_qkd_scaling (.png & .pdf)")


def plot_fig2_eve(raw_dir: str, out_dir: str):
    path = os.path.join(raw_dir, "exp2_eve_density.csv")
    if not os.path.exists(path):
        return
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[float(r["p_eve"])].append(r)

    probs = sorted(grouped.keys())
    qber_m = []
    qber_s = []
    theo_qber = [p * 0.25 for p in probs]

    for p in probs:
        items = grouped[p]
        q = [float(x["qber"]) for x in items]
        qm = sum(q) / len(q)
        qs = math.sqrt(sum((x - qm) ** 2 for x in q) / (len(q) - 1)) if len(q) > 1 else 0
        qber_m.append(qm)
        qber_s.append(qs)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(probs, qber_m, yerr=qber_s, fmt='o-', color='#1f77b4', capsize=4, label='Empirical QBER ($\mu \pm \sigma$)')
    ax.plot(probs, theo_qber, 'r--', label='Theoretical QBER ($p_{\\text{eve}}/4$)')
    ax.axhline(0.11, color='orange', linestyle=':', linewidth=2, label='Security Threshold (11%)')

    ax.set_xlabel("Eve Interception Probability ($p_{\\text{eve}}$)")
    ax.set_ylabel("Quantum Bit Error Rate (QBER)")
    ax.set_ylim(-0.02, 0.32)
    ax.grid(True)
    ax.legend(loc="upper left")

    plt.title("QBER Response to Intercept-Resend Attack")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig2_eve_qber.png"), dpi=300)
    plt.savefig(os.path.join(out_dir, "fig2_eve_qber.pdf"))
    plt.close()
    print("  -> Saved fig2_eve_qber (.png & .pdf)")


def plot_fig3_noise(raw_dir: str, out_dir: str):
    path = os.path.join(raw_dir, "exp3_channel_noise.csv")
    if not os.path.exists(path):
        return
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[float(r["noise_param"])].append(r)

    params = sorted(grouped.keys())
    qber_m = []
    qber_s = []
    for p in params:
        items = grouped[p]
        q = [float(x["qber"]) for x in items]
        qm = sum(q) / len(q)
        qs = math.sqrt(sum((x - qm) ** 2 for x in q) / (len(q) - 1)) if len(q) > 1 else 0
        qber_m.append(qm)
        qber_s.append(qs)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(params, qber_m, yerr=qber_s, fmt='s-', color='#2ca02c', capsize=4, label='Empirical QBER')
    ax.axhline(0.11, color='crimson', linestyle='--', label='Cascade Abort Bound (11%)')
    ax.set_xlabel("Depolarizing Noise Parameter ($\lambda$)")
    ax.set_ylabel("Measured QBER")
    ax.grid(True)
    ax.legend(loc="upper left")
    plt.title("QBER Growth under Depolarizing Channel Noise")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig3_channel_noise.png"), dpi=300)
    plt.savefig(os.path.join(out_dir, "fig3_channel_noise.pdf"))
    plt.close()
    print("  -> Saved fig3_channel_noise (.png & .pdf)")


def plot_fig4_crypto(raw_dir: str, out_dir: str):
    path = os.path.join(raw_dir, "exp4_crypto_throughput.csv")
    if not os.path.exists(path):
        return
    rows = read_csv(path)
    grouped = defaultdict(list)
    for r in rows:
        grouped[int(r["payload_size_bytes"])].append(r)

    sizes = sorted(grouped.keys())
    enc_m = []
    dec_m = []
    for s in sizes:
        items = grouped[s]
        e = [float(x["encryption_time_ms"]) for x in items]
        d = [float(x["decryption_time_ms"]) for x in items]
        enc_m.append(sum(e) / len(e))
        dec_m.append(sum(d) / len(d))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(sizes, enc_m, 'o-', color='#1f77b4', label='Encryption Time (ms)')
    ax.plot(sizes, dec_m, 's--', color='#ff7f0e', label='Decryption Time (ms)')
    ax.set_xlabel("Payload Size (Bytes)")
    ax.set_ylabel("Processing Latency (ms)")
    ax.grid(True)
    ax.legend(loc="upper left")
    plt.title("AES-256-GCM Latency across IoT Payload Scales")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig4_crypto_throughput.png"), dpi=300)
    plt.savefig(os.path.join(out_dir, "fig4_crypto_throughput.pdf"))
    plt.close()
    print("  -> Saved fig4_crypto_throughput (.png & .pdf)")


def main():
    set_pub_style()
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base, "raw_results")
    out_dir = os.path.join(base, "plots")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating publication figures from empirical datasets...")
    plot_fig1_scaling(raw_dir, out_dir)
    plot_fig2_eve(raw_dir, out_dir)
    plot_fig3_noise(raw_dir, out_dir)
    plot_fig4_crypto(raw_dir, out_dir)
    print("[SUCCESS] All publication figures generated successfully in experiments/plots/")


if __name__ == "__main__":
    main()
