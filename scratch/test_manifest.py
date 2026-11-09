import os
import sys
import json
import math
from collections import Counter

sys.path.insert(0, ".")
from data.synthetic.generator import SyntheticWorldGenerator, haversine_m, bearing_deg
from data.synthetic.schemas import SyntheticTrackPoint

def test_manifest():
    gen = SyntheticWorldGenerator(seed_mode="test")
    reg = gen.generate_aircraft_registry(600)
    start_ts = 1793491200
    gt = gen.generate_ground_truth_events(start_ts, start_ts + 7*86400)
    
    # Run track generation logic with manifest collection
    scale = gen.config.get("scale", {})
    n_flights = 6000
    sampling_interval = 30
    region_keys = list(gen.regions.keys())
    reg_weights = [gen.regional_flight_distribution.get(r, 1.0) for r in region_keys]
    corridor_p = gen.traffic_shaping.get("corridor_flight_fraction", 0.70)
    departure_banks = gen.traffic_shaping.get("departure_banks_hours", [6.5, 11.5, 16.5, 20.5])
    departure_sigma = gen.traffic_shaping.get("departure_bank_sigma_minutes", 40.0) * 60.0
    jitter_km = gen.traffic_shaping.get("corridor_lateral_jitter_km", 2.5)

    manifest = []
    
    for flight_i in range(n_flights):
        aircraft = gen.rng.choice(reg)
        is_corridor = (gen.rng.random() < corridor_p) and bool(gen.corridors)
        chosen_region = gen.rng.choices(region_keys, weights=reg_weights, k=1)[0]
        cruise_gs = 230.0 + gen.rng.uniform(-10.0, 15.0)

        if is_corridor:
            day = gen.rng.randint(0, 6)
            bank_h = gen.rng.choice(departure_banks)
            bank_offset = gen.rng.gauss(0, departure_sigma)
            flight_start = int(start_ts + (day * 86400) + (bank_h * 3600) + bank_offset)
            flight_start = max(start_ts, min(start_ts + (7 * 86400) - 18000, flight_start))
            reg_corridors = [c for c in gen.corridors if c.get("region") == chosen_region]
            if not reg_corridors:
                reg_corridors = gen.corridors
            corridor = gen.rng.choice(reg_corridors)
            corridor_region = corridor.get("region", chosen_region)
            wps = list(corridor["waypoints"])
            if gen.rng.random() < 0.5:
                wps.reverse()
            mean_lat = sum(p[0] for p in wps) / len(wps)
            dlat_jitter = gen.rng.gauss(0, jitter_km / 111.0)
            dlon_jitter = gen.rng.gauss(0, jitter_km / (111.0 * max(0.2, math.cos(math.radians(mean_lat)))))
            seg_dists_m = []
            cum_dists_m = [0.0]
            for s_i in range(len(wps) - 1):
                d_m = haversine_m(wps[s_i][0], wps[s_i][1], wps[s_i + 1][0], wps[s_i + 1][1])
                seg_dists_m.append(d_m)
                cum_dists_m.append(cum_dists_m[-1] + d_m)
            total_dist_m = max(1000.0, cum_dists_m[-1])
        else:
            flight_start = start_ts + gen.rng.randint(0, (7 * 86400) - 18000)
            origin_reg = chosen_region
            dest_reg = gen.rng.choice(region_keys)
            origin_apt = gen.rng.choice(gen.regions[origin_reg]["airports"])
            dest_apt = gen.rng.choice(gen.regions[dest_reg]["airports"])
            lat1, lon1 = origin_apt["lat"], origin_apt["lon"]
            lat2, lon2 = dest_apt["lat"], dest_apt["lon"]
            total_dist_m = max(1000.0, haversine_m(lat1, lon1, lat2, lon2))
            direct_track = bearing_deg(lat1, lon1, lat2, lon2)
            dlat_jitter = 0.0
            dlon_jitter = 0.0

        flight_dur_seconds = total_dist_m / cruise_gs
        flight_dur_minutes = max(35.0, min(330.0, flight_dur_seconds / 60.0))
        duration_points = int((flight_dur_minutes * 60) // sampling_interval)
        duration_points = max(30, duration_points)

        cruise_alt = float(gen.rng.choice([9500, 10500, 11500]))
        is_go_around = (gen.rng.random() < 0.03)
        silent_prob = gen.silent_probs.get(aircraft.family, 0.30)
        is_silent_acceptor = (gen.rng.random() < silent_prob)

        spoof_event = None
        jam_event = None
        applied_spoof = False
        applied_jam = False
        inj_start = None
        inj_end = None

        for pt_idx in range(duration_points):
            if gen.rng.random() < 0.04 and 5 < pt_idx < (duration_points - 5):
                continue
            fraction = pt_idx / max(1, duration_points - 1)
            curr_ts = flight_start + (pt_idx * sampling_interval)
            event_reg = corridor_region if is_corridor else (origin_reg if fraction < 0.5 else dest_reg)
            active_jam, active_spf = gen._is_in_event(event_reg, curr_ts, gt)
            if active_jam:
                jam_event = active_jam
                applied_jam = True
            if active_spf:
                spoof_event = active_spf
                applied_spoof = True
                if inj_start is None:
                    inj_start = curr_ts
                inj_end = curr_ts

        # Determine flight classification
        if spoof_event:
            ev_id = spoof_event.event_id
            ev_type = "spoofing"
            applied = applied_spoof
        elif jam_event:
            ev_id = jam_event.event_id
            ev_type = "jamming"
            applied = applied_jam
        else:
            ev_id = None
            ev_type = None
            applied = False

        manifest.append({
            "flight_id": f"{aircraft.icao24}_{flight_start}",
            "icao24": aircraft.icao24,
            "start_ts": flight_start,
            "event_id": ev_id,
            "event_type": ev_type,
            "applied": applied,
            "inj_start": inj_start,
            "inj_end": inj_end,
        })

    types = Counter(m["event_type"] for m in manifest)
    print("Manifest event types:", types)
    applied_counts = Counter(m["applied"] for m in manifest if m["event_type"] == "spoofing")
    print("Spoofing applied counts:", applied_counts)

if __name__ == "__main__":
    test_manifest()
