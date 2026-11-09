"""AeroTrust Phase 3 Comprehensive Evaluation.

Evaluates the integrated Two-Axis Trust Score on the held-out test seed (1337):
1. Status Distribution: {ok, degraded, unknown}
2. Share of Unknown (Abstention Rate)
3. Agreement between Overall Status and Ground-Truth Manifest (TP, FP, FN, TN, P, R, F1)
4. Calibration of Axis A Hostile Interference Probability (Brier score & 10-bin reliability)
5. Distribution of Natural Exposure (Axis B: low, moderate, elevated)
6. Pipeline Runtime & Ingestion Benchmarks

Strict Architectural Boundary: This script in evaluation/ is the ONLY module permitted
to correlate trust_scores with data/synthetic/ground_truth/flight_manifest.json.
"""

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg2

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )


def run_phase3_evaluation():
    t0 = time.time()
    print("=== AeroTrust Phase 3 Two-Axis Trust Score Evaluation ===")
    conn = get_db()
    cur = conn.cursor()

    # Load ground truth manifest
    manifest_path = Path("data") / "synthetic" / "ground_truth" / "flight_manifest.json"
    assert manifest_path.exists(), f"Missing ground truth manifest: {manifest_path}"
    manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
    print(f"Loaded ground-truth manifest: {len(manifest):,} flights.")

    manifest_by_fl = {}
    for f in manifest:
        manifest_by_fl[(f["icao24"], f["start_ts"])] = f

    # Fetch trust scores from DB
    cur.execute("""
        SELECT flight_id, segment_start, segment_end, score, uncertainty, status, reasons
        FROM trust_scores;
    """)
    trust_rows = cur.fetchall()
    print(f"Loaded {len(trust_rows):,} flight trust scores from PostgreSQL.")

    # 1. Status Distribution
    status_counts = Counter(r[5] for r in trust_rows)
    total_flights = len(trust_rows)
    print("\n--- 1. OVERALL STATUS DISTRIBUTION ---")
    for st, count in status_counts.items():
        pct = (count / max(1, total_flights)) * 100.0
        print(f"  {st:12s}: {count:6d} ({pct:5.2f}%)")

    # 2. Share of Unknown (Abstention Rate)
    unknown_count = status_counts.get("unknown", 0)
    unknown_share = (unknown_count / max(1, total_flights)) * 100.0
    print(f"\n--- 2. ABSTENTION SUMMARY ---")
    print(f"  Total Unknown (Abstained) Flights: {unknown_count}")
    print(f"  Abstention Rate:                   {unknown_share:.2f}%")

    # 3. Agreement between Status and Ground Truth Manifest
    # Ground truth positive: applied == True (either spoofing or jamming)
    tp, fp, fn, tn = 0, 0, 0, 0
    pred_probs = []
    gt_binary = []
    axis_b_levels = Counter()

    for fl_id, st, et, score, uncert, status, reasons_raw in trust_rows:
        icao = fl_id.split("_")[0] if "_" in fl_id else fl_id
        mf = manifest_by_fl.get((icao, st))
        if mf is None:
            for f in manifest:
                if f["icao24"] == icao and abs(f["start_ts"] - st) <= 60:
                    mf = f
                    break

        is_gt_hostile = bool(mf and mf["applied"])

        if status == "degraded":
            if is_gt_hostile:
                tp += 1
            else:
                fp += 1
        elif status == "ok":
            if is_gt_hostile:
                fn += 1
            else:
                tn += 1
        elif status == "unknown":
            if is_gt_hostile:
                fn += 1
            else:
                tn += 1

        reasons_data = reasons_raw if isinstance(reasons_raw, dict) else (json.loads(reasons_raw) if reasons_raw else {})
        axis_a = reasons_data.get("axis_a", {})
        axis_b = reasons_data.get("axis_b", {})

        p_cal = axis_a.get("calibrated_prob")
        if p_cal is not None:
            pred_probs.append(p_cal)
            gt_binary.append(1 if is_gt_hostile else 0)

        level_b = axis_b.get("level", "low")
        axis_b_levels[level_b] += 1

    precision = (tp / max(1, tp + fp)) * 100.0
    recall = (tp / max(1, tp + fn)) * 100.0
    f1 = (2 * precision * recall) / max(1e-9, precision + recall)

    print("\n--- 3. AGREEMENT WITH GROUND TRUTH MANIFEST ---")
    print(f"  True Positives (TP):   {tp:5d}")
    print(f"  False Positives (FP):  {fp:5d}")
    print(f"  False Negatives (FN):  {fn:5d}")
    print(f"  True Negatives (TN):   {tn:5d}")
    print(f"  Precision:             {precision:5.2f}%")
    print(f"  Recall:                {recall:5.2f}%")
    print(f"  F1-Score:              {f1:5.2f}%")

    # 4. Calibration of Axis A Probability
    pred_probs = np.array(pred_probs)
    gt_binary = np.array(gt_binary)
    brier_score = float(np.mean((pred_probs - gt_binary) ** 2))
    mean_pred = float(np.mean(pred_probs))
    base_rate = float(np.mean(gt_binary))

    print("\n--- 4. AXIS A PROBABILITY CALIBRATION ---")
    print(f"  Mean Predicted Probability: {mean_pred:.3f}")
    print(f"  Empirical Base Rate:        {base_rate:.3f}")
    print(f"  Brier Score:                {brier_score:.4f}")

    print("\n  10-Bin Reliability Breakdown:")
    print(f"  {'Bin':12} | {'Count':8} | {'Mean Pred':10} | {'Observed Rate':14} | {'Delta':8}")
    print("  " + "-" * 60)
    bins = np.linspace(0.0, 1.0, 11)
    for i in range(10):
        low, high = bins[i], bins[i + 1]
        mask = (pred_probs >= low) & (pred_probs < high) if i < 9 else (pred_probs >= low) & (pred_probs <= high)
        n = int(np.sum(mask))
        if n > 0:
            mp = float(np.mean(pred_probs[mask]))
            op = float(np.mean(gt_binary[mask]))
            print(f"  [{low:.1f}, {high:.1f})   | {n:8d} | {mp:10.3f} | {op:14.3f} | {op - mp:+8.3f}")
        else:
            print(f"  [{low:.1f}, {high:.1f})   | {0:8d} |        --- |            --- |      ---")

    # 5. Natural Exposure Distribution (Axis B)
    print("\n--- 5. AXIS B NATURAL RADIATION EXPOSURE DISTRIBUTION ---")
    for lvl in ["low", "moderate", "elevated"]:
        cnt = axis_b_levels.get(lvl, 0)
        pct = (cnt / max(1, total_flights)) * 100.0
        print(f"  {lvl:12s}: {cnt:6d} ({pct:5.2f}%)")

    # Fetch max relative index in radiation_index
    cur.execute("SELECT max(relative_index), avg(relative_index) FROM radiation_index;")
    max_idx, avg_idx = cur.fetchone()
    print(f"  Mean Segment Relative Index: {avg_idx:.3f}")
    print(f"  Peak Segment Relative Index: {max_idx:.3f}")

    total_eval_time = time.time() - t0
    print(f"\n--- 6. EVALUATION RUNTIME ---")
    print(f"  Total Evaluation Runtime: {total_eval_time:.2f} seconds")

    conn.close()

    return {
        "status_distribution": dict(status_counts),
        "unknown_share_pct": unknown_share,
        "agreement": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        },
        "calibration": {
            "mean_pred": mean_pred,
            "base_rate": base_rate,
            "brier_score": brier_score,
        },
        "axis_b_distribution": dict(axis_b_levels),
        "runtime_seconds": total_eval_time,
    }


if __name__ == "__main__":
    run_phase3_evaluation()

