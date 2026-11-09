"""AeroTrust Deterministic Synthetic World Generator.

Generates:
1. Synthetic Aircraft Registry (fake hex icao24, fake operators)
2. Synthetic Flights & Track Points between synthetic hubs across 6 regions
3. Ground-Truth Event Table (Jamming zones & Spoofing events) - KEPT STRICTLY SEPARATE
4. Hard Negatives: turbulence spikes, barometric errors, coverage gaps, go-arounds
5. Configurable Silent Acceptance per family (NIC/NACp high vs low during spoofing)
6. Space Weather series (Kp, proton flux) with storm episodes
7. Weekly synthetic affected region rankings CSV
8. README Section 4.6 public incident cases with source_url="verify:..."
9. Synthetic flight with pitch-down profile for precursor scanner tests

All outputs are clearly tagged SYNTHETIC. No real-world passenger identifiers.
"""

import csv
import json
import math
import os
import random
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import yaml

from data.synthetic.schemas import (
    GroundTruthEvent,
    SyntheticAircraft,
    SyntheticIncidentCase,
    SyntheticSpaceWeatherPoint,
    SyntheticTrackPoint,
)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great circle distance in meters."""
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return r * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Forward great circle azimuth in degrees [0, 360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


class SyntheticWorldGenerator:
    """Deterministic generator for AeroTrust synthetic simulation data."""

    def __init__(self, config_path: str = "config/synthetic.yaml", seed_mode: str = "dev"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        if isinstance(seed_mode, int):
            seed = seed_mode
        else:
            seed = self.config["seeds"].get(seed_mode, 42)
        self.rng = random.Random(seed)
        self.seed_mode = str(seed_mode)

        self.difficulty = self.config.get("difficulty_knobs", {})
        self.silent_probs = self.config.get("silent_acceptance_probability", {
            "A320-family": 0.40,
            "A330": 0.25,
            "A350": 0.15,
            "other": 0.30,
        })
        self.regions = self.config.get("regions", {})
        self.traffic_shaping = self.config.get("traffic_shaping", {})
        self.corridors = self.config.get("corridors", [])
        self.regional_flight_distribution = self.config.get("regional_flight_distribution", {})
        self.last_flight_durations_minutes: List[float] = []
        self.flight_manifest: List[Dict[str, Any]] = []

    def generate_aircraft_registry(self, n_aircraft: int) -> List[SyntheticAircraft]:
        """Generates fake aircraft registry with realistic family proportions."""
        families = ["A320-family", "A330", "A350", "other"]
        weights = [
            self.config["fleet_distribution"].get(f, 0.25) for f in families
        ]

        family_type_codes = {
            "A320-family": ["A20N", "A21N", "A320"],
            "A330": ["A333", "A339"],
            "A350": ["A359", "A35K"],
            "other": ["B738", "B789", "E195"],
        }

        registry: List[SyntheticAircraft] = []
        for i in range(n_aircraft):
            family = self.rng.choices(families, weights=weights, k=1)[0]
            type_code = self.rng.choice(family_type_codes[family])
            # Fake 24-bit hex code starting with 'x' to clearly indicate fake non-ICAO
            fake_hex = f"x{self.rng.randint(0x100000, 0xFFFFFF):06x}"
            reg = f"SYN-{type_code}-{i+1:04d}"
            operator = f"Synthetic Airways {(i % 6) + 1:02d}"

            registry.append(
                SyntheticAircraft(
                    icao24=fake_hex,
                    registration=reg,
                    type_code=type_code,
                    family=family,
                    operator=operator,
                )
            )
        return registry

    def generate_space_weather(
        self, start_ts: int, n_days: int, step_seconds: int = 3600
    ) -> List[SyntheticSpaceWeatherPoint]:
        """Generates space weather series (Kp, proton flux) with storm episodes."""
        records: List[SyntheticSpaceWeatherPoint] = []
        total_steps = (n_days * 86400) // step_seconds

        # Inject 2 storm episodes
        storm_1_step = total_steps // 3
        storm_2_step = (total_steps * 2) // 3

        for step in range(total_steps):
            ts = start_ts + (step * step_seconds)
            # Baseline background levels
            base_kp = 1.5 + self.rng.uniform(-0.5, 0.5)
            base_proton = 0.5 + self.rng.uniform(0.0, 0.3)
            base_xray = 1e-7 + self.rng.uniform(0.0, 5e-8)

            # Storm 1: Moderate Kp=5.5, Proton flux=18 pfu
            if 0 <= (step - storm_1_step) <= 6:
                decay = math.exp(-(step - storm_1_step) / 2.0)
                base_kp += 4.0 * decay
                base_proton += 18.0 * decay
                base_xray += 1e-5 * decay

            # Storm 2: Strong Kp=7.5, Proton flux=85 pfu (Solar radiation event)
            if 0 <= (step - storm_2_step) <= 10:
                decay = math.exp(-(step - storm_2_step) / 3.0)
                base_kp += 6.0 * decay
                base_proton += 85.0 * decay
                base_xray += 5e-4 * decay

            records.append(
                SyntheticSpaceWeatherPoint(
                    ts=ts,
                    kp=round(min(9.0, max(0.0, base_kp)), 2),
                    proton_flux_10mev=round(max(0.1, base_proton), 2),
                    xray_flux=float(f"{base_xray:.2e}"),
                )
            )
        return records

    def generate_ground_truth_events(
        self, start_ts: int, end_ts: int
    ) -> List[GroundTruthEvent]:
        """Generates ground truth jamming zones and spoofing events.

        KEPT STRICTLY SEPARATE FROM DETECTOR MODULES.
        Generates >= 15 jamming zones and >= 40 spoofing events (total >= 60)
        spread across all 4 high-risk regions over the entire simulation duration.
        """
        events: List[GroundTruthEvent] = []
        high_risk_regions = ["Baltic", "Eastern Mediterranean", "Black Sea", "Middle East"]
        total_span = max(86400, end_ts - start_ts)

        # Plan: 4 jamming events + 12 spoofing events per high-risk region (16 * 4 = 64 events)
        # Event types: all 4 types represented (altitude_offset, horizontal_offset, horizontal_drift, combined)
        # Offset bins: subtle (30-150m), moderate (150-400m), large (400-800m)
        spoof_types = ["altitude_offset", "horizontal_offset", "horizontal_drift", "combined"]
        offset_bins = [
            ("30-150m", 30.0, 150.0),
            ("150-400m", 150.0, 400.0),
            ("400-800m", 400.0, 800.0),
        ]

        event_idx = 1
        for region in high_risk_regions:
            n_events_region = 16
            slot_duration = total_span / n_events_region

            # Jamming at indices 0, 4, 8, 12 (spread across the 7 days)
            jam_slots = {0, 4, 8, 12}

            spoof_counter = 0
            for slot_i in range(n_events_region):
                slot_start = start_ts + int(slot_i * slot_duration)
                max_off = max(600, int(slot_duration * 0.15))
                offset_in_slot = self.rng.randint(300, max_off)
                ev_start = slot_start + offset_in_slot

                if slot_i in jam_slots:
                    max_dur = max(3600, int(slot_duration * 0.6))
                    min_dur = min(3600, max_dur)
                    dur = self.rng.randint(min_dur, max_dur)
                    ev_end = min(end_ts, ev_start + dur)
                    events.append(
                        GroundTruthEvent(
                            event_id=f"GTE-JAM-{event_idx:03d}",
                            event_type="jamming",
                            region=region,
                            start_ts=ev_start,
                            end_ts=ev_end,
                            intensity=round(self.rng.uniform(0.6, 0.95), 2),
                            metadata={"target_quality_drop": "NIC/NACp severe drop"},
                        )
                    )
                    event_idx += 1
                else:
                    max_dur = max(1800, int(slot_duration * 0.5))
                    min_dur = min(1800, max_dur)
                    dur = self.rng.randint(min_dur, max_dur)
                    ev_end = min(end_ts, ev_start + dur)

                    stype = spoof_types[spoof_counter % len(spoof_types)]
                    bin_name, min_alt, max_alt = offset_bins[spoof_counter % len(offset_bins)]
                    spoof_counter += 1

                    alt_offset_m = round(self.rng.uniform(min_alt, max_alt), 1)
                    horiz_offset_m = round(self.rng.uniform(50.0, 1000.0), 1)
                    drift_mps = round(self.rng.uniform(0.5, 8.0), 2)

                    events.append(
                        GroundTruthEvent(
                            event_id=f"GTE-SPF-{event_idx:03d}",
                            event_type="spoofing",
                            region=region,
                            start_ts=ev_start,
                            end_ts=ev_end,
                            intensity=round(self.rng.uniform(0.3, 0.95), 2),
                            spoof_type=stype,
                            metadata={
                                "target_alt_offset_m": alt_offset_m,
                                "target_horiz_offset_m": horiz_offset_m,
                                "target_drift_mps": drift_mps,
                                "offset_bin": bin_name,
                                "subtle": bool(alt_offset_m < 150.0 or horiz_offset_m < 200.0),
                            },
                        )
                    )
                    event_idx += 1

        return events

    def _is_in_event(
        self, region: str, ts: int, events: List[GroundTruthEvent]
    ) -> Tuple[Optional[GroundTruthEvent], Optional[GroundTruthEvent]]:
        """Checks if region & timestamp overlap with active ground truth events."""
        active_jam = None
        active_spf = None
        for ev in events:
            if ev.region == region and ev.start_ts <= ts <= ev.end_ts:
                if ev.event_type == "jamming":
                    active_jam = ev
                elif ev.event_type == "spoofing":
                    active_spf = ev
        return active_jam, active_spf

    def generate_flight_tracks(
        self,
        aircraft_list: List[SyntheticAircraft],
        ground_truth_events: List[GroundTruthEvent],
        n_flights: int,
        start_ts: int,
        sampling_interval: int = 30,
    ) -> List[SyntheticTrackPoint]:
        """Generates realistic synthetic flight trajectories with airway corridors and departure banks."""
        all_points: List[SyntheticTrackPoint] = []
        self.last_flight_durations_minutes = []
        region_keys = list(self.regions.keys())
        reg_weights = [self.regional_flight_distribution.get(r, 1.0) for r in region_keys]

        noise_sigma = self.difficulty.get("noise_level_sigma_meters", 15.0)
        dropout_p = self.difficulty.get("coverage_dropout_probability", 0.04)
        turb_p = self.difficulty.get("turbulence_spike_probability", 0.03)
        baro_drift_p = self.difficulty.get("baro_drift_error_probability", 0.02)
        go_around_p = self.difficulty.get("go_around_probability", 0.03)

        corridor_p = self.traffic_shaping.get("corridor_flight_fraction", 0.70)
        departure_banks = self.traffic_shaping.get("departure_banks_hours", [6.5, 11.5, 16.5, 20.5])
        departure_sigma = self.traffic_shaping.get("departure_bank_sigma_minutes", 40.0) * 60.0
        jitter_km = self.traffic_shaping.get("corridor_lateral_jitter_km", 2.5)

        for flight_i in range(n_flights):
            aircraft = self.rng.choice(aircraft_list)
            is_corridor = (self.rng.random() < corridor_p) and bool(self.corridors)
            chosen_region = self.rng.choices(region_keys, weights=reg_weights, k=1)[0]

            flight_spoof_event = None
            flight_jam_event = None
            applied_spoof = False
            applied_jam = False
            inj_start_ts = None
            inj_end_ts = None

            # Aircraft nominal cruise speed ~450 kts
            cruise_gs = 230.0 + self.rng.uniform(-10.0, 15.0)

            # Departure time and route setup
            if is_corridor:
                # Departure banks: 4 daily peaks with Gaussian spread
                day = self.rng.randint(0, 6)
                bank_h = self.rng.choice(departure_banks)
                bank_offset = self.rng.gauss(0, departure_sigma)
                flight_start = int(start_ts + (day * 86400) + (bank_h * 3600) + bank_offset)
                flight_start = max(start_ts, min(start_ts + (7 * 86400) - 18000, flight_start))

                # Select corridor in region or fallback
                reg_corridors = [c for c in self.corridors if c.get("region") == chosen_region]
                if not reg_corridors:
                    reg_corridors = self.corridors
                corridor = self.rng.choice(reg_corridors)
                corridor_region = corridor.get("region", chosen_region)
                wps = list(corridor["waypoints"])
                if self.rng.random() < 0.5:
                    wps.reverse()

                # Lateral jitter for H3 corridor tube realism (persistent across the flight)
                mean_lat = sum(p[0] for p in wps) / len(wps)
                dlat_jitter = self.rng.gauss(0, jitter_km / 111.0)
                dlon_jitter = self.rng.gauss(0, jitter_km / (111.0 * max(0.2, math.cos(math.radians(mean_lat)))))

                # Precompute polyline segment lengths in meters
                seg_dists_m = []
                cum_dists_m = [0.0]
                for s_i in range(len(wps) - 1):
                    d_m = haversine_m(wps[s_i][0], wps[s_i][1], wps[s_i + 1][0], wps[s_i + 1][1])
                    seg_dists_m.append(d_m)
                    cum_dists_m.append(cum_dists_m[-1] + d_m)
                total_dist_m = max(1000.0, cum_dists_m[-1])
            else:
                # Direct / off-corridor flights (preserves sparse regions & off-peak traffic)
                flight_start = start_ts + self.rng.randint(0, (7 * 86400) - 18000)
                origin_reg = chosen_region
                dest_reg = self.rng.choice(region_keys)
                origin_apt = self.rng.choice(self.regions[origin_reg]["airports"])
                dest_apt = self.rng.choice(self.regions[dest_reg]["airports"])
                lat1, lon1 = origin_apt["lat"], origin_apt["lon"]
                lat2, lon2 = dest_apt["lat"], dest_apt["lon"]
                total_dist_m = max(1000.0, haversine_m(lat1, lon1, lat2, lon2))
                direct_track = bearing_deg(lat1, lon1, lat2, lon2)
                dlat_jitter = 0.0
                dlon_jitter = 0.0

            # Compute flight duration matched to physical distance and ground speed
            flight_dur_seconds = total_dist_m / cruise_gs
            flight_dur_minutes = max(35.0, min(330.0, flight_dur_seconds / 60.0))
            duration_points = int((flight_dur_minutes * 60) // sampling_interval)
            duration_points = max(30, duration_points)
            self.last_flight_durations_minutes.append(flight_dur_minutes)

            cruise_alt = float(self.rng.choice([9500, 10500, 11500]))  # Cruise ~FL310-FL380

            # Hard negative: is this flight executing a go-around (missed approach)?
            is_go_around = (self.rng.random() < go_around_p)

            # Does this aircraft accept spoofing silently if spoofed?
            silent_prob = self.silent_probs.get(aircraft.family, 0.30)
            is_silent_acceptor = (self.rng.random() < silent_prob)

            # Simulated drift accumulator for this flight
            cumulative_spoof_drift_lat = 0.0
            cumulative_spoof_drift_lon = 0.0
            prev_lat, prev_lon, prev_ts = None, None, None

            for pt_idx in range(duration_points):
                # Check for random coverage dropout (hard negative check)
                if self.rng.random() < dropout_p and 5 < pt_idx < (duration_points - 5):
                    continue  # Gap in coverage

                fraction = pt_idx / max(1, duration_points - 1)
                curr_ts = flight_start + (pt_idx * sampling_interval)

                if is_corridor:
                    target_s = fraction * total_dist_m
                    seg_idx = 0
                    for s_i in range(len(seg_dists_m)):
                        if target_s <= cum_dists_m[s_i + 1] or s_i == len(seg_dists_m) - 1:
                            seg_idx = s_i
                            break
                    seg_len = max(1.0, seg_dists_m[seg_idx])
                    seg_t = (target_s - cum_dists_m[seg_idx]) / seg_len
                    seg_t = max(0.0, min(1.0, seg_t))
                    p0 = wps[seg_idx]
                    p1 = wps[seg_idx + 1]
                    true_lat = p0[0] + seg_t * (p1[0] - p0[0]) + dlat_jitter
                    true_lon = p0[1] + seg_t * (p1[1] - p0[1]) + dlon_jitter
                    track = bearing_deg(p0[0], p0[1], p1[0], p1[1])
                    event_reg = corridor_region
                else:
                    true_lat = lat1 + (lat2 - lat1) * fraction
                    true_lon = lon1 + (lon2 - lon1) * fraction
                    track = direct_track
                    event_reg = origin_reg if fraction < 0.5 else dest_reg

                # Compute true nominal speed and heading along trajectory
                if prev_lat is None:
                    nominal_gs = cruise_gs
                    nominal_track = track
                else:
                    dt_actual = max(1.0, float(curr_ts - prev_ts))
                    d_step = haversine_m(prev_lat, prev_lon, true_lat, true_lon)
                    nominal_gs = d_step / dt_actual
                    nominal_track = bearing_deg(prev_lat, prev_lon, true_lat, true_lon)

                prev_lat, prev_lon, prev_ts = true_lat, true_lon, curr_ts
                # Physical vertical profile: standard commercial transport climb/descent
                climb_time_sec = (cruise_alt - 100.0) / 14.0
                descent_time_sec = (cruise_alt - 100.0) / 12.0
                flight_time_sec = duration_points * sampling_interval

                t_from_start = pt_idx * sampling_interval
                t_to_end = flight_time_sec - t_from_start

                if t_from_start < climb_time_sec:
                    nominal_alt = min(cruise_alt, 100.0 + (t_from_start * 14.0))
                    vrate = 14.0
                    on_ground = False
                elif t_to_end < descent_time_sec:
                    if is_go_around and 0.90 <= fraction <= 0.96:
                        # Missed approach: aborts descent, initiates sharp climb to 1000m, then descends again
                        go_frac = (fraction - 0.90) / 0.06
                        if go_frac < 0.5:
                            nominal_alt = 300.0 + (1000.0 - 300.0) * (go_frac / 0.5)
                            vrate = 14.0  # Sharp climb rate ~2700 ft/min
                        else:
                            nominal_alt = 1000.0 - (1000.0 - 100.0) * ((go_frac - 0.5) / 0.5)
                            vrate = -12.0
                        on_ground = False
                    else:
                        nominal_alt = max(100.0, 100.0 + (t_to_end * 12.0))
                        vrate = -12.0
                        on_ground = False
                else:
                    # Proper sustained level cruise segment
                    nominal_alt = cruise_alt
                    vrate = 0.0
                    on_ground = False

                # Hard negative: clear-air turbulence spike during cruise
                if fraction >= 0.15 and fraction <= 0.85 and self.rng.random() < turb_p:
                    vrate += self.rng.choice([-12.0, 14.0])

                # Hard negative: barometric sensor bias/drift
                baro_bias = 0.0
                if self.rng.random() < baro_drift_p:
                    baro_bias = self.rng.uniform(60.0, 180.0)

                baro_noise = self.rng.gauss(0, noise_sigma)
                geo_noise = self.rng.gauss(0, noise_sigma)

                baro_alt = max(0.0, nominal_alt + baro_noise + baro_bias)
                geo_alt = max(0.0, nominal_alt + geo_noise)

                # Baseline high ADS-B integrity
                nic = 10
                nacp = 10
                sil = 3

                # Active environmental interference?
                active_jam, active_spf = self._is_in_event(event_reg, curr_ts, ground_truth_events)

                if active_jam:
                    # Jamming degrades NIC / NACp / SIL
                    nic = self.rng.randint(2, 6)
                    nacp = self.rng.randint(3, 7)
                    sil = self.rng.randint(0, 1)
                    flight_jam_event = active_jam
                    applied_jam = True
                    if flight_spoof_event is None and inj_start_ts is None:
                        inj_start_ts = curr_ts
                    if flight_spoof_event is None:
                        inj_end_ts = curr_ts

                if active_spf:
                    # Spoofing event active: supports subtle to large altitude and horizontal perturbations
                    if flight_spoof_event is None:
                        flight_spoof_event = active_spf
                        inj_start_ts = curr_ts
                    applied_spoof = True
                    inj_end_ts = curr_ts
                    stype = active_spf.spoof_type or "altitude_offset"
                    if stype in ("altitude_offset", "combined"):
                        geo_alt += active_spf.metadata.get("target_alt_offset_m", 150.0)
                    if stype in ("horizontal_offset",):
                        true_lat += active_spf.metadata.get("target_horiz_offset_m", 250.0) / 111000.0
                    if stype in ("horizontal_drift", "combined"):
                        drift_v = active_spf.metadata.get("target_drift_mps", 2.0)
                        cumulative_spoof_drift_lat += (drift_v * sampling_interval) / 111000.0
                        true_lat += cumulative_spoof_drift_lat

                    # Silent Acceptance rule:
                    # If silent acceptor, NIC/NACp stay high!
                    # If not silent acceptor, aircraft avionics flag degraded integrity
                    if not is_silent_acceptor:
                        nic = self.rng.randint(4, 6)
                        nacp = self.rng.randint(5, 7)
                    else:
                        nic = 10
                        nacp = 10

                all_points.append(
                    SyntheticTrackPoint(
                        icao24=aircraft.icao24,
                        ts=curr_ts,
                        lat=round(true_lat, 6),
                        lon=round(true_lon, 6),
                        baro_alt_m=round(baro_alt, 2),
                        geo_alt_m=round(geo_alt, 2),
                        gs_mps=round(nominal_gs + self.rng.uniform(-2, 2), 2),
                        track_deg=round(nominal_track, 2),
                        vrate_mps=round(vrate, 2),
                        on_ground=on_ground,
                        nic=nic,
                        nacp=nacp,
                        sil=sil,
                        source_note="SYNTHETIC_GENERATOR",
                    )
                )

            # Record per-flight ground-truth manifest
            if flight_spoof_event is not None:
                ev_id = flight_spoof_event.event_id
                ev_type = "spoofing"
                applied = applied_spoof
                i_start = inj_start_ts
                i_end = inj_end_ts
            elif flight_jam_event is not None:
                ev_id = flight_jam_event.event_id
                ev_type = "jamming"
                applied = applied_jam
                i_start = inj_start_ts
                i_end = inj_end_ts
            else:
                ev_id = None
                ev_type = None
                applied = False
                i_start = None
                i_end = None

            self.flight_manifest.append({
                "flight_id": f"{aircraft.icao24}_{flight_start}",
                "icao24": aircraft.icao24,
                "start_ts": flight_start,
                "end_ts": flight_start + (duration_points * sampling_interval),
                "event_id": ev_id,
                "event_type": ev_type,
                "applied": applied,
                "inj_start": i_start,
                "inj_end": i_end,
            })

        return all_points

    def generate_pitch_down_test_flight(
        self, start_ts: int
    ) -> Tuple[SyntheticAircraft, List[SyntheticTrackPoint]]:
        """Generates synthetic flight with a pitch-down-like profile for scanner tests.

        Labeled SYNTHETIC. Does not name any real flight or airline.
        """
        aircraft = SyntheticAircraft(
            icao24="xpd320",
            registration="SYN-A20N-SCANNER-TEST",
            type_code="A20N",
            family="A320-family",
            operator="Synthetic Precursor Test Flight",
        )

        points: List[SyntheticTrackPoint] = []
        duration_minutes = 40
        sampling_sec = 10
        total_steps = (duration_minutes * 60) // sampling_sec
        event_step = total_steps // 2  # Event occurs at minute 20

        lat, lon = 48.0, 5.0
        cruise_alt = 10600.0  # Cruise FL350 (~10,600m)

        for step in range(total_steps):
            curr_ts = start_ts + (step * sampling_sec)
            lat += 0.002
            lon += 0.002

            vrate = 0.0
            alt = cruise_alt

            # Pitch-down profile: sharp vertical rate dip and 200m altitude loss, then recovery
            if 0 <= (step - event_step) <= 6:
                dip_idx = step - event_step
                # Sharp negative vertical rate peaking at -30 m/s (~-6000 ft/min)
                vrate_profile = [-5.0, -25.0, -32.0, -18.0, 10.0, 15.0, 5.0]
                alt_loss_profile = [0.0, -40.0, -120.0, -210.0, -180.0, -90.0, -20.0]

                vrate = vrate_profile[dip_idx]
                alt = cruise_alt + alt_loss_profile[dip_idx]

            points.append(
                SyntheticTrackPoint(
                    icao24=aircraft.icao24,
                    ts=curr_ts,
                    lat=round(lat, 6),
                    lon=round(lon, 6),
                    baro_alt_m=round(alt, 2),
                    geo_alt_m=round(alt + self.rng.gauss(0, 5), 2),
                    gs_mps=240.0,
                    track_deg=45.0,
                    vrate_mps=round(vrate, 2),
                    on_ground=False,
                    nic=10,
                    nacp=10,
                    sil=3,
                    source_note="SYNTHETIC_PRECURSOR_PITCH_DOWN_FLIGHT",
                )
            )

        return aircraft, points

    def generate_incident_cases(self) -> List[SyntheticIncidentCase]:
        """Seeds strictly the public incident numbers from README Section 4.6."""
        raw_cases = self.config.get("incident_seed_cases", [])
        return [SyntheticIncidentCase(**case) for case in raw_cases]

    def export_affected_region_ranking_csv(
        self, ground_truth_events: List[GroundTruthEvent], output_path: str
    ):
        """Generates synthetic weekly affected region ranking CSV.

        Derived from ground truth + noise, clearly labelled SYNTHETIC.
        Used strictly to test importer and rank-correlation code path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        region_scores: Dict[str, float] = {r: 0.0 for r in self.regions.keys()}

        for ev in ground_truth_events:
            region_scores[ev.region] += ev.intensity * 10.0

        # Add noise to simulate external report discrepancy
        noisy_scores = []
        for r, score in region_scores.items():
            noisy_score = max(0.0, score + self.rng.uniform(-1.5, 1.5))
            noisy_scores.append((r, noisy_score))

        noisy_scores.sort(key=lambda x: x[1], reverse=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["rank", "region_name", "synthetic_interference_index", "source_note"])
            for rank, (r, score) in enumerate(noisy_scores, 1):
                writer.writerow([rank, r, round(score, 2), "SYNTHETIC_REGIONAL_RANKING_FOR_VALIDATION_TESTING"])


def generate_full_synthetic_world(
    config_path: str = "config/synthetic.yaml",
    seed_mode: str = "dev",
    output_dir: str = "data/synthetic/output",
) -> Dict[str, Any]:
    """Orchestrates generation of the full synthetic world."""
    os.makedirs(output_dir, exist_ok=True)
    generator = SyntheticWorldGenerator(config_path=config_path, seed_mode=seed_mode)

    scale = generator.config.get("scale", {})
    n_aircraft = scale.get("n_aircraft", 60)
    n_flights = scale.get("n_flights", 180)
    n_days = scale.get("n_days", 7)
    sampling_sec = scale.get("sampling_interval_seconds", 30)

    start_ts = int(datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp())
    end_ts = start_ts + (n_days * 86400)

    # 1. Aircraft Registry
    aircraft = generator.generate_aircraft_registry(n_aircraft)

    # 2. Ground Truth Events (KEPT STRICTLY SEPARATE IN ISOLATED JSON DIRECTORY)
    gt_events = generator.generate_ground_truth_events(start_ts, end_ts)
    gt_dir = os.path.join(output_dir, "ground_truth") if output_dir != "data/synthetic/output" else os.path.join("data", "synthetic", "ground_truth")
    os.makedirs(gt_dir, exist_ok=True)
    gt_file = os.path.join(gt_dir, "ground_truth_events.json")
    with open(gt_file, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in gt_events], f, indent=2)

    # 3. Flight Tracks
    tracks = generator.generate_flight_tracks(
        aircraft, gt_events, n_flights, start_ts, sampling_sec
    )

    # 4. Space Weather
    space_weather = generator.generate_space_weather(start_ts, n_days)

    # 5. Incident Cases (README 4.6)
    incidents = generator.generate_incident_cases()

    # 6. Pitch Down Test Flight
    scanner_aircraft, pitch_down_points = generator.generate_pitch_down_test_flight(start_ts)
    generator.flight_manifest.append({
        "flight_id": f"{scanner_aircraft.icao24}_{start_ts}",
        "icao24": scanner_aircraft.icao24,
        "start_ts": start_ts,
        "end_ts": start_ts + len(pitch_down_points) * sampling_sec,
        "event_id": None,
        "event_type": None,
        "applied": False,
        "inj_start": None,
        "inj_end": None,
    })

    # Save Flight Manifest in ground_truth folder
    manifest_file = os.path.join(gt_dir, "flight_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(generator.flight_manifest, f, indent=2)

    # 7. Affected region ranking CSV
    csv_path = os.path.join(output_dir, "synthetic_affected_region_rankings.csv")
    generator.export_affected_region_ranking_csv(gt_events, csv_path)

    return {
        "aircraft": aircraft,
        "ground_truth_events": gt_events,
        "tracks": tracks,
        "space_weather": space_weather,
        "incidents": incidents,
        "scanner_flight": (scanner_aircraft, pitch_down_points),
        "region_rankings_csv": csv_path,
    }

