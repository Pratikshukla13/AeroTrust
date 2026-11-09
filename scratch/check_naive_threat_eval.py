import sys
import os
import json
import psycopg2
import pandas as pd
import numpy as np

sys.path.insert(0, ".")
from evaluation.injection_eval import run_evaluation

# We can modify run_evaluation or inspect by adding a return of eval_df
conn = psycopg2.connect(
    dbname="aerotrust",
    user="aerotrust",
    password="aerotrust_secret",
    host="localhost",
    port=5432,
)
cur = conn.cursor()

# Query the exact columns needed for all flights
cur.execute("""
    SELECT 
        p.icao24,
        min(p.ts) as start_ts,
        max(p.ts) as end_ts,
        avg(p.lat) as avg_lat,
        avg(p.lon) as avg_lon,
        min(p.nic) as min_nic,
        min(p.nacp) as min_nacp
    FROM flight_track_points p
    GROUP BY p.icao24, (p.ts / 14400);
""")
rows = cur.fetchall()

with open("data/synthetic/ground_truth/ground_truth_events.json", "r", encoding="utf-8") as f:
    gt_events = json.load(f)
spoof_events = [e for e in gt_events if e["event_type"] == "spoofing"]
jam_events = [e for e in gt_events if e["event_type"] == "jamming"]

# Also load spoof_checks
cur.execute("SELECT icao24, ts_window_start, check_name, flag FROM spoof_checks;")
checks = cur.fetchall()
from collections import defaultdict
flags = defaultdict(dict)
for icao, ws, cname, flg in checks:
    flags[(icao, ws)][cname] = flg

evaluated = []
for r in rows:
    icao, sts, ets, alat, alon, min_nic, min_nacp = r
    # Matching logic from injection_eval
    # Spoof match
    sp_match = False
    for ev in spoof_events:
        if (sts <= ev["end_ts"]) and (ets >= ev["start_ts"]):
            # Check affected_icao24
            if icao in (ev.get("affected_icao24") or []):
                sp_match = True
                break
    
    # Jam match
    jam_match = False
    for ev in jam_events:
        if (sts <= ev["end_ts"]) and (ets >= ev["start_ts"]):
            if icao in (ev.get("affected_icao24") or []):
                jam_match = True
                break

    is_flagged_naive = bool((min_nic is not None and min_nic < 7) or (min_nacp is not None and min_nacp < 7))
    
    # Find matching check in flags
    # Find ws within 900s of sts
    flg_a, flg_b, flg_c, flg_d = False, False, False, False
    for (c_icao, ws), chk_dict in flags.items():
        if c_icao == icao and abs(ws - sts) <= 900:
            flg_a = chk_dict.get("geo_baro_alt", False)
            flg_b = chk_dict.get("kinematic_feasibility", False)
            flg_c = chk_dict.get("pos_vel_consistency", False)
            flg_d = chk_dict.get("multi_aircraft_consensus", False)
            break
    rule_1 = flg_a or flg_b or flg_c or flg_d

    evaluated.append({
        "icao24": icao,
        "is_spoofed": sp_match,
        "is_jammed": jam_match,
        "is_clean": not sp_match,
        "is_naive": is_flagged_naive,
        "is_rule1": rule_1,
    })

df = pd.DataFrame(evaluated)
print(f"Total evaluated: {len(df)}")
clean_df = df[df["is_clean"] == True]
jam_clean = clean_df[clean_df["is_jammed"] == True]
pure_clean = clean_df[clean_df["is_jammed"] == False]

print(f"Clean in Jamming Zones: {len(jam_clean)}")
print(f"Fully Clean Flights: {len(pure_clean)}")

print("\n--- Naive Baseline Clean FP Split ---")
naive_fp_jam = jam_clean["is_naive"].sum()
naive_fp_pure = pure_clean["is_naive"].sum()
print(f"Naive FPs in Jamming Zones: {naive_fp_jam} ({naive_fp_jam/len(jam_clean)*100:.2f}%)")
print(f"Naive FPs in Fully Clean: {naive_fp_pure} ({naive_fp_pure/len(pure_clean)*100:.2f}%)")
print(f"Naive Total Clean FPs: {naive_fp_jam + naive_fp_pure} ({(naive_fp_jam + naive_fp_pure)/len(clean_df)*100:.2f}%)")

print("\n--- AeroTrust Clean FP Split ---")
at_fp_jam = jam_clean["is_rule1"].sum()
at_fp_pure = pure_clean["is_rule1"].sum()
print(f"AeroTrust FPs in Jamming Zones: {at_fp_jam} ({at_fp_jam/len(jam_clean)*100:.2f}%)")
print(f"AeroTrust FPs in Fully Clean: {at_fp_pure} ({at_fp_pure/len(pure_clean)*100:.2f}%)")
print(f"AeroTrust Total Clean FPs: {at_fp_jam + at_fp_pure} ({(at_fp_jam + at_fp_pure)/len(clean_df)*100:.2f}%)")

print("\n--- Combined Threat Evaluation (Threat = Spoofing OR Jamming) ---")
df["is_threat"] = df["is_spoofed"] | df["is_jammed"]
threat_pos = df[df["is_threat"] == True]
threat_neg = df[df["is_threat"] == False]

# Naive on Combined Threat
naive_threat_tp = threat_pos["is_naive"].sum()
naive_threat_fp = threat_neg["is_naive"].sum()
naive_threat_fn = len(threat_pos) - naive_threat_tp
naive_threat_rec = naive_threat_tp / len(threat_pos) * 100
naive_threat_prec = naive_threat_tp / (naive_threat_tp + naive_threat_fp) * 100
naive_threat_f1 = 2 * (naive_threat_prec/100) * (naive_threat_rec/100) / ((naive_threat_prec + naive_threat_rec)/100) * 100

# AeroTrust on Combined Threat
at_threat_tp = threat_pos["is_rule1"].sum()
at_threat_fp = threat_neg["is_rule1"].sum()
at_threat_fn = len(threat_pos) - at_threat_tp
at_threat_rec = at_threat_tp / len(threat_pos) * 100
at_threat_prec = at_threat_tp / (at_threat_tp + at_threat_fp) * 100
at_threat_f1 = 2 * (at_threat_prec/100) * (at_threat_rec/100) / ((at_threat_prec + at_threat_rec)/100) * 100

print(f"Combined Positives: {len(threat_pos)}, Negatives: {len(threat_neg)}")
print(f"Naive:     TP={naive_threat_tp:4d}, FP={naive_threat_fp:4d}, Rec={naive_threat_rec:5.1f}%, Prec={naive_threat_prec:5.1f}%, F1={naive_threat_f1:5.1f}%")
print(f"AeroTrust: TP={at_threat_tp:4d}, FP={at_threat_fp:4d}, Rec={at_threat_rec:5.1f}%, Prec={at_threat_prec:5.1f}%, F1={at_threat_f1:5.1f}%")
