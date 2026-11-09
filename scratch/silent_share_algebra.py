import sys
import os
import json
import psycopg2
import numpy as np

def run_silent_algebra():
    conn = psycopg2.connect(
        dbname="aerotrust",
        user="aerotrust",
        password="aerotrust_secret",
        host="localhost",
        port=5432,
    )
    cur = conn.cursor()
    
    with open("data/synthetic/ground_truth/ground_truth_events.json", "r", encoding="utf-8") as f:
        gt_events = json.load(f)
    spoof_events = [e for e in gt_events if e["event_type"] == "spoofing"]

    # Let's count silent vs non-silent spoofed flights on the test seed
    # In injection_eval.py:
    # silent_acceptors: aircraft that accepted spoofing silently (without NIC/NACp drop)
    # Let's check the database spoof_checks or run the exact classification from injection_eval
    cur.execute("""
        SELECT count(DISTINCT icao24) FROM flight_track_points;
    """)
    print("DB active.")

if __name__ == "__main__":
    run_silent_algebra()

