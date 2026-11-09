import json, psycopg2, os, math
from collections import defaultdict
import yaml
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

# Fetch all flights
cur.execute('''
    SELECT sc.icao24, sc.ts_window_start, sc.ts_window_end,
           min(p.lat), max(p.lat), min(p.lon), max(p.lon)
    FROM (SELECT DISTINCT icao24, ts_window_start, ts_window_end FROM spoof_checks) sc
    JOIN flight_track_points p ON p.icao24 = sc.icao24 AND p.ts BETWEEN sc.ts_window_start AND sc.ts_window_end
    GROUP BY sc.icao24, sc.ts_window_start, sc.ts_window_end;
''')
flts = cur.fetchall()

# Checks from spoof_checks (Phase 2.6 detectors)
cur.execute('SELECT icao24, ts_window_start, check_name, flag, status, reasons FROM spoof_checks;')
checks_rows = cur.fetchall()
checks_p26 = defaultdict(dict)
for icao, ws, cname, flag, status, reasons in checks_rows:
    checks_p26[(icao, ws)][cname] = {'flag': flag, 'status': status, 'reasons': json.loads(reasons) if isinstance(reasons, str) else (reasons or [])}

flt_p26_flags = {}
flt_p25_flags = {}
for icao, ws, we, min_lat, max_lat, min_lon, max_lon in flts:
    ch = checks_p26.get((icao, ws), {})
    fa = ch.get('geo_baro_alt', {}).get('flag', False)
    fb = ch.get('kinematic_feasibility', {}).get('flag', False)
    fc = ch.get('pos_vel_consistency', {}).get('flag', False)
    fd = ch.get('multi_aircraft_consensus', {}).get('flag', False)
    fa_p25 = fa or any('single_aircraft_baro_bias_suppressed' in r for r in ch.get('geo_baro_alt', {}).get('reasons', []))
    flt_p26_flags[(icao, ws)] = (fa or fb or fc or fd)
    flt_p25_flags[(icao, ws)] = (fa_p25 or fb or fc or fd)

# New Labels (Phase 2.6)
# Old Labels (Phase 2.5)
labels_p26 = {}
labels_p25 = {}

for icao, ws, we, min_lat, max_lat, min_lon, max_lon in flts:
    regs_p26 = []
    if min_lat >= 45.0 and max_lat <= 55.0 and min_lon >= -5.0 and max_lon <= 15.0: regs_p26.append('Western Europe')
    if min_lon <= -15.0: regs_p26.append('North Atlantic')
    if max_lat >= 54.0 and min_lon >= 18.0 and max_lon <= 30.0: regs_p26.append('Baltic')
    if min_lat <= 36.0 and min_lon >= 30.0 and max_lon <= 38.0: regs_p26.append('Eastern Mediterranean')
    if min_lat >= 40.0 and max_lat <= 48.0 and min_lon >= 26.0 and max_lon <= 42.0: regs_p26.append('Black Sea')
    if min_lat <= 32.0 and min_lon >= 45.0: regs_p26.append('Middle East')
    if not regs_p26:
        mid_lat = (min_lat + max_lat) / 2.0
        mid_lon = (min_lon + max_lon) / 2.0
        regs_p26.append(assign_region(mid_lat, mid_lon))
    is_spf_p26 = any(ev['region'] in regs_p26 and not (we < ev['start_ts'] or ws > ev['end_ts']) for ev in spoof_events)
    labels_p26[(icao, ws)] = is_spf_p26

    # Old labels (Phase 2.5 style: broader matching)
    regs_p25 = list(regs_p26)
    mid_lat = (min_lat + max_lat) / 2.0
    mid_lon = (min_lon + max_lon) / 2.0
    nn = assign_region(mid_lat, mid_lon)
    if nn not in regs_p25: regs_p25.append(nn)
    is_spf_p25 = any(ev['region'] in regs_p25 and not (we < ev['start_ts'] or ws > ev['end_ts']) for ev in spoof_events)
    labels_p25[(icao, ws)] = is_spf_p25

def get_m(det_flags, labels):
    tp = sum(1 for k in det_flags if det_flags[k] and labels[k])
    fp = sum(1 for k in det_flags if det_flags[k] and not labels[k])
    fn = sum(1 for k in det_flags if not det_flags[k] and labels[k])
    tn = sum(1 for k in det_flags if not det_flags[k] and not labels[k])
    prec = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'prec': prec, 'rec': rec, 'f1': f1}

m11 = get_m(flt_p25_flags, labels_p25)
m12 = get_m(flt_p25_flags, labels_p26)
m21 = get_m(flt_p26_flags, labels_p25)
m22 = get_m(flt_p26_flags, labels_p26)

print("=== 2x2 Attribution Table ===")
print("P2.5 det x Old labels: TP={}, FP={}, Prec={:.1f}%, Rec={:.1f}%, F1={:.1f}%".format(m11['tp'], m11['fp'], m11['prec'], m11['rec'], m11['f1']))
print("P2.5 det x New labels: TP={}, FP={}, Prec={:.1f}%, Rec={:.1f}%, F1={:.1f}%".format(m12['tp'], m12['fp'], m12['prec'], m12['rec'], m12['f1']))
print("P2.6 det x Old labels: TP={}, FP={}, Prec={:.1f}%, Rec={:.1f}%, F1={:.1f}%".format(m21['tp'], m21['fp'], m21['prec'], m21['rec'], m21['f1']))
print("P2.6 det x New labels: TP={}, FP={}, Prec={:.1f}%, Rec={:.1f}%, F1={:.1f}%".format(m22['tp'], m22['fp'], m22['prec'], m22['rec'], m22['f1']))

