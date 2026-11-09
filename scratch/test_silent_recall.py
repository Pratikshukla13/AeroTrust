import json
from collections import defaultdict
import numpy as np
import psycopg2

conn = psycopg2.connect("postgresql://aerotrust:aerotrust_secret@localhost:5432/aerotrust")
cur = conn.cursor()
cur.execute("SELECT flight_id, segment_start, segment_end, reasons FROM trust_scores;")
trust_rows = cur.fetchall()

manifest = json.load(open("data/synthetic/ground_truth/flight_manifest.json"))
gt_events = json.load(open("data/synthetic/ground_truth/ground_truth_events.json"))
event_type_map = {e["event_id"]: e.get("spoof_type", "unknown") for e in gt_events}

mf_by_icao = defaultdict(list)
for m in manifest:
    mf_by_icao[m["icao24"]].append(m)

cur.execute("SELECT icao24, ts, nic FROM flight_track_points;")
pts = cur.fetchall()
nic_by_icao = defaultdict(list)
for icao, ts, nic in pts:
    nic_by_icao[icao].append((ts, nic))

test_stats = defaultdict(lambda: {"total": 0, "tp": 0})
for fid, st, et, r_raw in trust_rows:
    icao = fid.split("_")[0]
    r_data = json.loads(r_raw) if isinstance(r_raw, str) else r_raw
    prim = r_data.get("axis_a", {}).get("primary_triggered", False)

    cands = mf_by_icao.get(icao, [])
    overlaps = [m for m in cands if not (et < m["start_ts"] or st > m["end_ts"]) and m["applied"] and m["event_type"] == "spoofing"]
    if not overlaps:
        continue
    m = overlaps[0]
    ev_type = event_type_map.get(m["event_id"], "unknown")

    fl_nics = [n for ts, n in nic_by_icao[icao] if st <= ts <= et]
    is_silent = (np.mean([n >= 7 for n in fl_nics]) > 0.5) if fl_nics else False

    key = (ev_type, "silent" if is_silent else "non-silent")
    test_stats[key]["total"] += 1
    if prim:
        test_stats[key]["tp"] += 1

print("=== TEST SEED (1337) Recall by event_type x silent ===")
for k, v in sorted(test_stats.items()):
    r = (v["tp"] / v["total"]) * 100 if v["total"] > 0 else 0
    print(f"{k[0]:22s} | {k[1]:10s}: TP={v['tp']:3d} / {v['total']:3d} ({r:5.1f}%)")

conn.close()

