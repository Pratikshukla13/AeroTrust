import os
import json
import psycopg2
import pandas as pd
import numpy as np

conn = psycopg2.connect(
    dbname="aerotrust",
    user="aerotrust",
    password="aerotrust_secret",
    host="localhost",
    port=5432,
)
cur = conn.cursor()

# Run the exact query from injection_eval
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
flight_rows = cur.fetchall()

with open("data/synthetic/ground_truth/ground_truth_events.json", "r", encoding="utf-8") as f:
    gt_events = json.load(f)
spoof_events = [e for e in gt_events if e["event_type"] == "spoofing"]

# Correlate each flight with ground truth
spoofed_flights = []
for r in flight_rows:
    icao, start_ts, end_ts, avg_lat, avg_lon, min_nic, min_nacp = r
    # Overlap with any spoof event
    matched = None
    for ev in spoof_events:
        t_start = ev["start_time"]
        t_end = ev["end_time"]
        if (start_ts <= t_end) and (end_ts >= t_start):
            c_lat, c_lon = ev.get("center", (0, 0))
            dist_deg = ((avg_lat - c_lat)**2 + (avg_lon - c_lon)**2)**0.5
            if dist_deg <= 5.0: # ~500 km
                matched = ev
                break
    if matched:
        is_silent = bool(min_nic is not None and min_nic >= 9 and min_nacp is not None and min_nacp >= 9)
        spoofed_flights.append({
            "icao24": icao,
            "is_silent": is_silent,
            "min_nic": min_nic,
            "min_nacp": min_nacp,
        })

df_sp = pd.DataFrame(spoofed_flights)
print(f"Total matched spoofed flights: {len(df_sp)}")
if len(df_sp) > 0:
    n_silent = df_sp["is_silent"].sum()
    share = n_silent / len(df_sp)
    print(f"Silent count: {n_silent}, Non-silent count: {len(df_sp) - n_silent}, Silent share: {share*100:.2f}%")

