"""AeroTrust Synthetic Telemetry Preview Generator.

Generates `docs/SYNTHETIC_PREVIEW.png` contrasting:
1. Nominal Clean Flight Track
2. GNSS Spoofed Track (Geometric vs Barometric altitude divergence)
3. GNSS Jammed Track (Severe NIC/NACp drop and temporal gaps)

Clearly labeled with SYNTHETIC banner to prevent confusion with real data.
"""

import os
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from data.synthetic.generator import SyntheticWorldGenerator
from data.synthetic.schemas import GroundTruthEvent


def generate_preview():
    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "SYNTHETIC_PREVIEW.png")

    generator = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    fleet = generator.generate_aircraft_registry(10)
    start_ts = 1793491200

    # 1. Clean track (No ground truth events)
    clean_tracks = generator.generate_flight_tracks(
        aircraft_list=[fleet[0]],
        ground_truth_events=[],
        n_flights=1,
        start_ts=start_ts,
        sampling_interval=30,
    )

    # 2. Spoofed track (Active spoofing event: subtle altitude offset + horizontal lateral drift)
    spf_event = GroundTruthEvent(
        event_id="GTE-PREVIEW-SPF",
        event_type="spoofing",
        region="Baltic",
        start_ts=start_ts - 3600,
        end_ts=start_ts + 18000,
        intensity=0.75,
        spoof_type="combined",
        metadata={
            "target_alt_offset_m": 120.0,    # Subtle altitude residual (within 30-800m distribution)
            "target_drift_mps": 3.2,         # Horizontal drift rate
        },
    )
    generator.regions["Baltic"]["airports"] = [
        {"code": "XBAL", "lat": 56.92, "lon": 23.97},
        {"code": "XBBE", "lat": 59.41, "lon": 24.83},
    ]
    spoofed_tracks = generator.generate_flight_tracks(
        aircraft_list=[fleet[1]],
        ground_truth_events=[spf_event],
        n_flights=1,
        start_ts=start_ts,
        sampling_interval=30,
    )

    # 3. Jammed track (Active jamming event: NIC/NACp drops)
    jam_event = GroundTruthEvent(
        event_id="GTE-PREVIEW-JAM",
        event_type="jamming",
        region="Eastern Mediterranean",
        start_ts=start_ts - 3600,
        end_ts=start_ts + 7200,
        intensity=0.9,
    )
    jammed_tracks = generator.generate_flight_tracks(
        aircraft_list=[fleet[2]],
        ground_truth_events=[jam_event],
        n_flights=1,
        start_ts=start_ts,
        sampling_interval=30,
    )

    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)
    fig.patch.set_facecolor("#0f172a")

    # Banner across top
    fig.suptitle(
        "AEROTRUST SYNTHETIC TELEMETRY PREVIEW (NOT REAL DATA)\n"
        "Comparative Validation: Clean vs GNSS Spoofed vs GNSS Jammed",
        fontsize=13,
        fontweight="bold",
        color="#38bdf8",
        y=0.98,
    )

    styles = {
        "bg": "#1e293b",
        "grid": "#334155",
        "text": "#f8fafc",
        "baro": "#38bdf8",
        "geo": "#f43f5e",
        "nic": "#34d399",
        "nacp": "#fbbf24",
    }

    # Helper to style axes
    def style_ax(ax, title, ylabel):
        ax.set_facecolor(styles["bg"])
        ax.set_title(title, color=styles["text"], fontsize=11, fontweight="bold", pad=8)
        ax.set_ylabel(ylabel, color=styles["text"], fontsize=10)
        ax.tick_params(colors=styles["text"], labelsize=9)
        ax.grid(True, color=styles["grid"], linestyle="--", alpha=0.6)
        for spine in ax.spines.values():
            spine.set_color("#475569")

    # Subplot 1: Clean flight (Baro vs Geo Altitude agreement)
    t_clean = [(p.ts - clean_tracks[0].ts) / 60.0 for p in clean_tracks]
    baro_clean = [p.baro_alt_m for p in clean_tracks]
    geo_clean = [p.geo_alt_m for p in clean_tracks]

    ax1 = axes[0]
    style_ax(ax1, "Case 1: Nominal Clean Flight (Realistic Sensor Noise & Normal Profile)", "Altitude (m)")
    ax1.plot(t_clean, baro_clean, label="Barometric Alt (m)", color=styles["baro"], lw=2.0)
    ax1.plot(t_clean, geo_clean, label="Geometric (GNSS) Alt (m)", color=styles["geo"], lw=1.5, ls="--", alpha=0.8)
    ax1.legend(loc="lower center", facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc")

    # Subplot 2: Spoofed flight (Geometric Alt divergence)
    t_spf = [(p.ts - spoofed_tracks[0].ts) / 60.0 for p in spoofed_tracks]
    baro_spf = [p.baro_alt_m for p in spoofed_tracks]
    geo_spf = [p.geo_alt_m for p in spoofed_tracks]

    ax2 = axes[1]
    style_ax(ax2, "Case 2: GNSS Spoofed Flight (Subtle +120m Geo/Baro Residual & Lateral Drift)", "Altitude (m)")
    ax2.plot(t_spf, baro_spf, label="Barometric Alt (Truth reference)", color=styles["baro"], lw=2.0)
    ax2.plot(t_spf, geo_spf, label="Spoofed Geometric Alt (+120m subtle offset)", color=styles["geo"], lw=2.0)
    ax2.fill_between(t_spf, baro_spf, geo_spf, color="#f43f5e", alpha=0.25, label="Subtle Residual Anomaly")
    ax2.legend(loc="lower center", facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc")

    # Subplot 3: Jammed flight (Integrity Metric Drop)
    t_jam = [(p.ts - jammed_tracks[0].ts) / 60.0 for p in jammed_tracks]
    nic_jam = [p.nic for p in jammed_tracks]
    nacp_jam = [p.nacp for p in jammed_tracks]

    ax3 = axes[2]
    style_ax(ax3, "Case 3: GNSS Jammed Flight (ADS-B Integrity Drop: NIC / NACp Degradation)", "Integrity Category (0-11)")
    ax3.plot(t_jam, nic_jam, label="NIC (Navigation Integrity Category)", color=styles["nic"], lw=2.2)
    ax3.plot(t_jam, nacp_jam, label="NACp (Navigation Accuracy Category)", color=styles["nacp"], lw=2.0, ls="-.")
    ax3.axhline(7.0, color="#ef4444", ls=":", label="NIC Jamming Threshold (<=7)")
    ax3.set_xlabel("Elapsed Time (Minutes)", color=styles["text"], fontsize=10)
    ax3.legend(loc="upper right", facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc")

    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Successfully generated preview figure at: {out_path}")


if __name__ == "__main__":
    generate_preview()

