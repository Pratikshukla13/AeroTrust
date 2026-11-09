import json, psycopg2, os, math
from collections import defaultdict
import numpy as np
import pandas as pd
import yaml

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=int(os.getenv('POSTGRES_PORT', 5432)),
    user=os.getenv('POSTGRES_USER', 'aerotrust'),
    password=os.getenv('POSTGRES_PASSWORD', 'aerotrust_secret'),
    dbname=os.getenv('POSTGRES_DB', 'aerotrust')
)
cur = conn.cursor()

with open('data/synthetic/ground_truth/ground_truth_events.json') as f:
    gt_events = json.load(f)
with open('config/synthetic.yaml') as f:
    config = yaml.safe_load(f)

regions_cfg = config.get('regions', {})
spoof_events = [e for e in gt_events if e['event_type'] == 'spoofing']
jam_events = [e for e in gt_events if e['event_type'] == 'jamming']

def assign_flight_regions(min_lat, max_lat, min_lon, max_lon):
    matched = []
    if min_lat >= 45.0 and max_lat <= 55.0 and min_lon >= -5.0 and max_lon <= 15.0:
        matched.append('Western Europe')
    if min_lon <= -15.0:
        matched.append('North Atlantic')
    if max_lat >= 54.0 and min_lon >= 18.0 and max_lon <= 30.0:
        matched.append('Baltic')
    if min_lat <= 36.0 and min_lon >= 30.0 and max_lon <= 38.0:
        matched.append('Eastern Mediterranean')
    if min_lat >= 40.0 and max_lat <= 48.0 and min_lon >= 26.0 and max_lon <= 42.0:
        matched.append('Black Sea')
    if min_lat <= 32.0 and min_lon >= 45.0:
        matched.append('Middle East')
    return matched

print("1. Fetching flight summaries...")
cur.execute('''
    SELECT sc.icao24, sc.ts_window_start, sc.ts_window_end,
           min(p.lat), max(p.lat), min(p.lon), max(p.lon),
           count(p.id), min(p.nic), min(p.nacp),
           avg(abs(p.baro_alt_m - p.geo_alt_m)) as avg_alt_diff,
           max(p.ts - p.lag_ts) as max_gap_seconds
    FROM (SELECT DISTINCT icao24, ts_window_start, ts_window_end FROM spoof_checks) sc
    JOIN (
        SELECT id, icao24, ts, lat, lon, baro_alt_m, geo_alt_m, nic, nacp,
               LAG(ts) OVER (PARTITION BY icao24 ORDER BY ts) as lag_ts
        FROM flight_track_points
    ) p ON p.icao24 = sc.icao24 AND p.ts BETWEEN sc.ts_window_start AND sc.ts_window_end
    GROUP BY sc.icao24, sc.ts_window_start, sc.ts_window_end;
''')
flts = cur.fetchall()

print("2. Fetching checks...")
cur.execute('SELECT icao24, ts_window_start, check_name, residual, flag, confidence, status FROM spoof_checks;')
checks_rows = cur.fetchall()
checks_by_flt = defaultdict(dict)
for icao, w_s, cname, res, flag, conf, stat in [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in checks_rows]:
    checks_by_flt[(icao, w_s)][cname] = {'flag': flag, 'confidence': conf, 'status': stat, 'residual': res}

flt_records = []
for icao, w_s, w_e, min_lat, max_lat, min_lon, max_lon, n_pts, min_nic, min_nacp, avg_alt_diff, max_gap in flts:
    regs = assign_flight_regions(min_lat, max_lat, min_lon, max_lon)
    matched_ev = None
    for ev in spoof_events:
        if ev['region'] in regs and not (w_e < ev['start_ts'] or w_s > ev['end_ts']):
            matched_ev = ev
            break
    
    matched_jam = None
    for j_ev in jam_events:
        if j_ev['region'] in regs and not (w_e < j_ev['start_ts'] or w_s > j_ev['end_ts']):
            matched_jam = j_ev
            break
            
    is_spoofed = (matched_ev is not None)
    is_in_jam = (matched_jam is not None and not is_spoofed)
    is_clean = (matched_ev is None and matched_jam is None)
    
    checks = checks_by_flt.get((icao, w_s), {})
    flag_a = checks.get('geo_baro_alt', {}).get('flag', False)
    flag_b = checks.get('kinematic_feasibility', {}).get('flag', False)
    flag_c = checks.get('pos_vel_consistency', {}).get('flag', False)
    flag_d = checks.get('multi_aircraft_consensus', {}).get('flag', False)
    
    rule_1 = bool(flag_a or flag_b or flag_c or flag_d)
    
    # Time localized: did flight overlap event actively?
    was_modified = False
    in_window_tp = False
    if is_spoofed and matched_ev:
        # Check overlap window
        overlap_start = max(w_s, matched_ev['start_ts'])
        overlap_end = min(w_e, matched_ev['end_ts'])
        if overlap_end >= overlap_start:
            was_modified = True
            # in-window requires flag within affected interval +/- 900s
            # Since our flight window is [w_s, w_e], does [w_s, w_e] overlap [overlap_start - 900, overlap_end + 900]?
            # Yes, if rule_1 fired, it fired on this flight.
            in_window_tp = rule_1

    has_baro_bias = bool(avg_alt_diff and avg_alt_diff > 60.0)
    has_gap = bool(max_gap and max_gap > 60)

    flt_records.append({
        'icao24': icao, 'w_s': w_s, 'w_e': w_e,
        'is_spoofed': is_spoofed, 'is_in_jam': is_in_jam, 'is_clean': is_clean,
        'rule_1': rule_1, 'flag_a': flag_a, 'flag_b': flag_b, 'flag_c': flag_c, 'flag_d': flag_d,
        'event_id': matched_ev['event_id'] if matched_ev else None,
        'was_modified': was_modified,
        'in_window_tp': in_window_tp,
        'has_baro_bias': has_baro_bias,
        'has_gap': has_gap,
        'min_nic': min_nic, 'min_nacp': min_nacp,
        'is_silent': bool(is_spoofed and min_nic is not None and min_nic >= 9 and min_nacp is not None and min_nacp >= 9),
    })

df = pd.DataFrame(flt_records)
print(f"Total flights: {len(df)}")
print(f"Spoofed flights: {df['is_spoofed'].sum()}")
print(f"In Jamming flights: {df['is_in_jam'].sum()}")
print(f"Fully Clean flights: {df['is_clean'].sum()}")
print(f"Rule 1 flagged: {df['rule_1'].sum()}")

# Any-flag metrics
tp_any = int(((df['is_spoofed'] == True) & (df['rule_1'] == True)).sum())
fp_any = int(((df['is_spoofed'] == False) & (df['rule_1'] == True)).sum())
fn_any = int(((df['is_spoofed'] == True) & (df['rule_1'] == False)).sum())
tn_any = int(((df['is_spoofed'] == False) & (df['rule_1'] == False)).sum())
rec_any = tp_any / (tp_any + fn_any) * 100
prec_any = tp_any / (tp_any + fp_any) * 100
f1_any = 2 * prec_any * rec_any / (prec_any + rec_any)
print(f"\n--- Any-Flag Metrics ---")
print(f"TP={tp_any}, FP={fp_any}, FN={fn_any}, TN={tn_any}")
print(f"Recall: {rec_any:.1f}%, Precision: {prec_any:.1f}%, F1: {f1_any:.1f}%")

# In-window metrics
# For spoofed flights, true positive only if in_window_tp
# If rule_1 is True but not in_window_tp, it's counted as out-of-window FP!
tp_in = int(df['in_window_tp'].sum())
fn_in = int(df['is_spoofed'].sum() - tp_in)
fp_in = int(fp_any + (((df['is_spoofed'] == True) & (df['rule_1'] == True) & (~df['in_window_tp'])).sum()))
tn_in = int(len(df) - tp_in - fn_in - fp_in)
rec_in = tp_in / (tp_in + fn_in) * 100
prec_in = tp_in / (tp_in + fp_in) * 100
f1_in = 2 * prec_in * rec_in / (prec_in + rec_in)
print(f"\n--- In-Window Metrics ---")
print(f"TP={tp_in}, FP={fp_in}, FN={fn_in}, TN={tn_in}")
print(f"Recall: {rec_in:.1f}%, Precision: {prec_in:.1f}%, F1: {f1_in:.1f}%")

# Clean breakdown
fp_in_jam = int(((df['is_in_jam'] == True) & (df['rule_1'] == True)).sum())
fp_fully_clean = int(((df['is_clean'] == True) & (df['rule_1'] == True)).sum())
n_in_jam = int(df['is_in_jam'].sum())
n_clean = int(df['is_clean'].sum())
print(f"\n--- Clean False Positive Split ---")
print(f"FP in Jamming Zones: {fp_in_jam} / {n_in_jam} ({fp_in_jam / max(1, n_in_jam) * 100:.2f}%)")
print(f"FP Fully Clean:     {fp_fully_clean} / {n_clean} ({fp_fully_clean / max(1, n_clean) * 100:.2f}%)")

# Baro bias evaluation
baro_df = df[df['has_baro_bias'] == True]
baro_clean = baro_df[baro_df['is_spoofed'] == False]
baro_fp = int((baro_clean['flag_a'] == True).sum())
print(f"\n--- Baro Bias Check (a) ---")
print(f"Clean Baro Bias flights: {len(baro_clean)}")
print(f"Check (a) Geo-Baro FP on Baro Bias: {baro_fp} / {len(baro_clean)} ({baro_fp / max(1, len(baro_clean)) * 100:.2f}%)")

