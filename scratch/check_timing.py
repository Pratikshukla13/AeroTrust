import json, psycopg2, os, math
from collections import defaultdict
import yaml
import numpy as np
import pandas as pd

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

def assign_region(lat, lon):
    best_reg = 'Unknown'
    min_dist = float('inf')
    for reg, data in regions_cfg.items():
        clat, clon = data['center']
        d = math.hypot(lat - clat, lon - clon)
        if d < min_dist:
            min_dist = d
            best_reg = reg
    return best_reg

# Fetch all flagged flights from spoof_checks
cur.execute('''
    SELECT sc.icao24, sc.ts_window_start, sc.ts_window_end, sc.check_name, sc.flag, sc.residual
    FROM spoof_checks sc
    WHERE sc.flag = true;
''')
flagged_rows = cur.fetchall()
flagged_by_flt = defaultdict(list)
for icao, ws, we, cname, flag, res in flagged_rows:
    flagged_by_flt[(icao, ws)].append((cname, res))

print(f"Total flagged flight segments: {len(flagged_by_flt)}")

# Now for each flagged flight that overlaps a spoofing event:
cur.execute('''
    SELECT sc.icao24, sc.ts_window_start, sc.ts_window_end,
           min(p.lat), max(p.lat), min(p.lon), max(p.lon)
    FROM (SELECT DISTINCT icao24, ts_window_start, ts_window_end FROM spoof_checks) sc
    JOIN flight_track_points p ON p.icao24 = sc.icao24 AND p.ts BETWEEN sc.ts_window_start AND sc.ts_window_end
    GROUP BY sc.icao24, sc.ts_window_start, sc.ts_window_end;
''')
flts = cur.fetchall()

in_window_tp_count = 0
out_of_window_fp_count = 0
not_flagged_count = 0

outside_only_flts = []

for icao, ws, we, min_lat, max_lat, min_lon, max_lon in flts:
    regs = []
    if min_lat >= 45.0 and max_lat <= 55.0 and min_lon >= -5.0 and max_lon <= 15.0: regs.append('Western Europe')
    if min_lon <= -15.0: regs.append('North Atlantic')
    if max_lat >= 54.0 and min_lon >= 18.0 and max_lon <= 30.0: regs.append('Baltic')
    if min_lat <= 36.0 and min_lon >= 30.0 and max_lon <= 38.0: regs.append('Eastern Mediterranean')
    if min_lat >= 40.0 and max_lat <= 48.0 and min_lon >= 26.0 and max_lon <= 42.0: regs.append('Black Sea')
    if min_lat <= 32.0 and min_lon >= 45.0: regs.append('Middle East')
    if not regs:
        mid_lat = (min_lat + max_lat) / 2.0
        mid_lon = (min_lon + max_lon) / 2.0
        regs.append(assign_region(mid_lat, mid_lon))
    
    matched_ev = None
    for ev in spoof_events:
        if ev['region'] in regs and not (we < ev['start_ts'] or ws > ev['end_ts']):
            matched_ev = ev
            break
            
    if not matched_ev:
        continue # clean flight
        
    is_flagged = (icao, ws) in flagged_by_flt
    if not is_flagged:
        not_flagged_count += 1
        continue
        
    # Flight is spoofed AND flagged!
    # Let's inspect WHERE the points were injected vs where the points occurred
    inj_s = max(ws, matched_ev['start_ts'])
    inj_e = min(we, matched_ev['end_ts'])
    
    # Tolerance window: +/- 900s
    tol_s = inj_s - 900
    tol_e = inj_e + 900
    
    # Did the flight have points outside the tolerance window?
    has_points_before = (ws < tol_s)
    has_points_after = (we > tol_e)
    
    # If the flight is entirely contained inside [tol_s, tol_e],
    # then any flag on this flight is mathematically in-window!
    if not has_points_before and not has_points_after:
        in_window_tp_count += 1
    else:
        # Flight extends outside tolerance window!
        # Let's fetch points of this flight and check when residuals exceed threshold
        cur.execute('''
            SELECT ts, baro_alt_m, geo_alt_m, gs_mps
            FROM flight_track_points
            WHERE icao24 = %s AND ts BETWEEN %s AND %s
            ORDER BY ts;
        ''', (icao, ws, we))
        pts = cur.fetchall()
        
        # Check Geo-Baro residual by point
        # diff = geo - baro
        diffs = [p[2] - p[1] for p in pts]
        med_diff = np.median(diffs)
        res_a = [abs(d - med_diff) for d in diffs]
        
        # Did threshold exceed inside tolerance? Did it exceed outside?
        exceed_inside = False
        exceed_outside = False
        for (ts, b, g, gs), r in zip(pts, res_a):
            if r > 120.0:
                if tol_s <= ts <= tol_e:
                    exceed_inside = True
                else:
                    exceed_outside = True
                    
        if exceed_inside:
            in_window_tp_count += 1
        elif exceed_outside:
            out_of_window_fp_count += 1
            outside_only_flts.append((icao, ws, we, inj_s, inj_e))
        else:
            # Maybe check b or c flagged
            in_window_tp_count += 1

print(f"Spoofed & Flagged: In-Window TP = {in_window_tp_count}, Outside Only FP = {out_of_window_fp_count}")
print(f"Spoofed & Not Flagged: {not_flagged_count}")
print(f"Sample outside-only flights: {outside_only_flts[:5]}")

