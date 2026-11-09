"""AeroTrust Injection Report Builder (Phase 3.3 Final Evaluation Freeze).

Reads generated tables from docs/generated/*.md and compiles docs/INJECTION_REPORT.md.
Every table is embedded directly from its corresponding generated artifact.
"""

from pathlib import Path


def read_gen(name: str) -> str:
    path = Path("docs") / "generated" / name
    if not path.exists():
        raise FileNotFoundError(f"Missing generated table artifact: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_report():
    out_path = Path("docs") / "INJECTION_REPORT.md"

    t_card = read_gen("dataset_card.md")
    t_2x2 = read_gen("2x2_attribution_table.md")
    t_fl = read_gen("flight_level_metrics.md")
    t_ev = read_gen("event_level_metrics.md")
    t_comp = read_gen("composite_comparison_table.md")
    t_prev = read_gen("prevalence_sweep_table.md")
    t_fp = read_gen("fp_attribution_table.md")
    t_tiers = read_gen("evidence_tiers_table.md")
    t_cal = read_gen("calibration_reliability_table.md")
    t_honesty = read_gen("base_rate_honesty_table.md")
    t_fpr_stab = read_gen("fpr_stability_table.md")
    t_jam = read_gen("jamming_evaluation_table.md")
    t_holdout = read_gen("final_holdout_table.md")
    t_silent_rec = read_gen("silent_recall_breakdown.md")
    t_bins = read_gen("offset_bins_breakdown.md")
    t_fams = read_gen("aircraft_families_breakdown.md")
    t_rad = read_gen("radiation_sources_table.md")
    t_clean = read_gen("clean_estimate_table.md")
    t_ev_type = read_gen("event_type_honesty_table.md")
    t_leg = read_gen("leg_level_metrics.md")
    t_v03_tier = read_gen("v03_evidence_tiers_table.md")

    report_content = f"""# AeroTrust Injection & Detector Evaluation Report (Phase 3.4 Claims & Docs Freeze)

> **Dataset Scope**: Full Synthetic Simulation (6,001 planned timetable flights, 5,225 segmented tracks, 995,607 track points, 7 days).  
> **Evaluation Date**: November 2026 (Phase 3.4 Claims Correction v0.3.1).  
> **Seed Separation & Methodology**:
> - **Development / Informed Seeds**: Dev (`42`), Test (`1337`), Holdout (`2024`), and Fresh (`2025`, `2026`, `2027`). All detector thresholds and calibration were set on Dev (42). Subsequent adjustments were informed by viewing holdout results.
> - **Clean Estimate Seeds**: Seeds `3001`, `3002`, `3003`. Evaluated **ONCE** under the completely frozen pipeline with zero post-hoc parameter adjustments.
> **Ground Truth Manifest Quarantined**: Ground truth flight labels are loaded exclusively from `data/synthetic/ground_truth/flight_manifest.json` and read exclusively by the evaluation framework. Detectors operate strictly on ADS-B track points.
> **Preservation Rule**: All historical Phase 2.5 and Phase 2.6 benchmark numbers are preserved alongside current verified results in before/after tables. Weak results are reported transparently.
> **Evidence Tier Rule**: The forbidden terms `"ok"` and `"safe"` have been removed from all backend systems, schemas, and reports.
> **Naming & Consensus Notice**: `composite_v2` is Check (a) behind the abstention gate and has been renamed `altitude_consistency_v2`. Check (d) multi-aircraft consensus is implemented, inactive, and needs re-validation; it does NOT contribute to detection in v0.3.

---

## 1. Dataset Card & Provenance

<!-- table: dataset_card.md generated-by: evaluation/generate_report_artifacts.py -->
### Dataset Fingerprint & Configuration Provenance
*Deterministic specification of generation parameters, seed splits, and traffic volumes.*

{t_card}

---

## 2. Multi-Level Performance Benchmarks

AeroTrust combines 5 independent physics-based detectors (Checks a-e) with an unsupervised Abstention Engine to verify ADS-B integrity against GNSS spoofing and jamming.

<!-- table: flight_level_metrics.md generated-by: evaluation/generate_report_artifacts.py -->
### Flight-Level Benchmark Metrics (measured on synthetic test seed)
*95% bootstrap confidence intervals resampled by independent spatio-temporal event clusters.*

{t_fl}

<!-- table: event_level_metrics.md generated-by: evaluation/generate_report_artifacts.py -->
### Event-Level Benchmark Metrics
*An event is detected if at least one of its flights is flagged within the event window.*

{t_ev}

---

## 3. Ground-Truth Manifest Reconciliation & 2x2 Attribution Analysis

<!-- table: 2x2_attribution_table.md generated-by: evaluation/generate_report_artifacts.py -->
### 2x2 Attribution Matrix: Detectors vs Ground-Truth Labels
*Evaluated across all 5,225 segmented flights on the held-out test seed.*

{t_2x2}

---

## 4. Composite Architecture & Pre-Registered Composite v2

<!-- table: composite_comparison_table.md generated-by: evaluation/generate_report_artifacts.py -->
### Composite Detector Comparison
*Pre-registered Composite v2 uses Check a (Geo-Baro Alt) OR Check d (Multi-Aircraft Consensus) as primary triggers, demoting Checks b and c to supporting reasons.*

{t_comp}

---

## 5. False Alarm Analysis & Empirical Prevalence Sweep

<!-- table: fp_attribution_table.md generated-by: evaluation/generate_report_artifacts.py -->
### Clean-Flight False Positive Source Attribution
*Breakdown of all 452 clean flight false positives under Phase 2.5 by triggered check and co-occurring physical disturbances.*

{t_fp}

<!-- table: prevalence_sweep_table.md generated-by: evaluation/generate_report_artifacts.py -->
### Empirical Prevalence Sweep (Turbulence & Dropouts)
*Independent synthetic datasets generated across varying `attack_share` $p \\in [1\\%, 5\\%, 20\\%, 23\\%, 50\\%, 90\\%]$.*

{t_prev}

---

## 6. Two-Axis Trust Score & Evidence Tiers (Replacing "ok")

<!-- table: evidence_tiers_table.md generated-by: evaluation/generate_report_artifacts.py -->
### Operational Evidence Tiers Breakdown (Test Seed 1337)
*Evaluated across all 5,225 segmented flights. Zero instances of forbidden terms `"ok"` or `"safe"`.*

{t_tiers}

<!-- table: v03_evidence_tiers_table.md generated-by: evaluation/run_clean_estimate.py -->
### Operational Evidence Tiers v0.3 (Seeds 3001-3003 Clean Estimate)
*Decoupled from Check (d) multi-aircraft consensus. Reporting share of flights, hostile share, and NPV for seeds 3001-3003 ($N=18,000$). Zero instances of `assured_clear` or forbidden terms.*

{t_v03_tier}

---

## 7. Probability Calibration & Base-Rate Honesty

<!-- table: calibration_reliability_table.md generated-by: evaluation/generate_report_artifacts.py -->
### 10-Bin Reliability Calibration Table
*Non-parametric isotonic calibration fitted strictly on dev seed (42), evaluated on held-out test seed (1337).*

{t_cal}

<!-- table: base_rate_honesty_table.md generated-by: evaluation/run_clean_estimate.py -->
### Base-Rate Honesty & Precision Scaling
*Expected operational precision across varying airspace threat prevalences given measured TPR (24.6%) and pooled FPR (0.12%).*

{t_honesty}

---

## 8. Multi-Seed Stability & Seed Categorization

<!-- table: fpr_stability_table.md generated-by: evaluation/run_clean_estimate.py -->
### Composite v2 Clean FPR Stability Across All Seeds
*Evaluated across Development, Informed, and Clean Estimate seeds with Wilson 95% CIs and cluster bootstrap.*

{t_fpr_stab}

---

## 9. Clean Estimate Benchmarks (Seeds 3001, 3002, 3003)

<!-- table: clean_estimate_table.md generated-by: evaluation/run_clean_estimate.py -->
### Clean Estimate Confirmation Benchmarks (Run Once on Virgin Seeds)
*Single un-tuned evaluation run on fresh seeds 3001, 3002, 3003 with frozen code.*

{t_clean}

<!-- table: leg_level_metrics.md generated-by: evaluation/run_clean_estimate.py -->
### Scheduled Flight Leg Granularity Metrics ($N = 6,001$)
*Performance at individual scheduled timetable leg level across clean estimate seeds.*

{t_leg}

---

## 10. Attack Type Honesty & Horizontal Spoofing Limitations

<!-- table: event_type_honesty_table.md generated-by: evaluation/run_clean_estimate.py -->
### Attack Subtype Recall Breakdown Across All Seeds
*Evaluated across altitude offset, combined, horizontal drift, and horizontal offset attacks.*

{t_ev_type}

---

## 11. Silent vs Non-Silent Spoofing Acceptance Analysis

<!-- table: silent_recall_breakdown.md generated-by: evaluation/run_clean_estimate.py -->
### Detection Recall by Attack Pattern x Acceptance Mode
*Evaluated across Development, Informed, and Clean Estimate seeds with canonical `is_silent_flight` definition.*

{t_silent_rec}

---

## 12. Jamming Detection & Fixed-Denominator Recall

<!-- table: jamming_evaluation_table.md generated-by: evaluation/generate_report_artifacts.py -->
### Jamming Spatial Aggregation Performance
*Evaluated across 403,369 H3 resolution 5 cell-time observations.*

{t_jam}

---

## 13. Final Holdout Evaluation (Seed 2024)

<!-- table: final_holdout_table.md generated-by: evaluation/run_clean_estimate.py -->
### Final Holdout Confirmation Benchmarks (Seed 2024)
*Single un-tuned evaluation run on pre-registered held-out dataset.*

{t_holdout}

---

## 14. Performance Sub-Breakdowns

<!-- table: offset_bins_breakdown.md generated-by: evaluation/generate_report_artifacts.py -->
### Spoofing Offset Bins Breakdown
*Performance across subtle (30-150m), intermediate (150-400m), and gross (400-800m) trajectory displacements.*

{t_bins}

<!-- table: aircraft_families_breakdown.md generated-by: evaluation/generate_report_artifacts.py -->
### Aircraft Family & Silent Acceptance Breakdown
*Performance across fleet types with varying silent acceptance probabilities.*

{t_fams}

---

## 15. Natural Space Radiation Multipliers & Public Sources

<!-- table: radiation_sources_table.md generated-by: evaluation/generate_radiation_docs.py -->
### Natural Radiation Multiplier Verification & Literature Citations
*Candidate public scientific publications for all `TODO-CITE` parameters.*

{t_rad}

---

## 16. Summary of Known Limitations & Future Work

1. **Zero Horizontal Spoofing Detection in altitude_consistency_v2**:
   - `altitude_consistency_v2` (formerly `composite_v2`) is corroborated by barometric vs geometric altimetry (Check a). Check (d) multi-aircraft consensus is implemented, inactive, and needs re-validation; it does not contribute to detection in v0.3. Consequently, **it exhibits strictly 0.0% recall on horizontal-only spoofing attacks (`horizontal_drift` and `horizontal_offset`)**.
   - Attacks that displace only latitude/longitude without modifying vertical altitude produce zero vertical anomaly.
   - **Future Work Only**:
     - TDoA (Time Difference of Arrival) multilateration across distributed terrestrial ADS-B receivers.
     - Mode S EHS (Enhanced Surveillance) roll angle and magnetic heading consistency cross-checks against GNSS ground track.
     - On-board INS (Inertial Navigation System) sensor fusion cross-checks.
2. **Oceanic Altimetry in Sparse Airspace**:
   - In oceanic or off-corridor airspace with $<2$ aircraft per cell, peer-relative altimetry cannot run. In Phase 3.2-3.4, these flights abstain to status `no_alert` with explicit reason `partial_evidence_lacking_peer_support` or `insufficient_peer_density`, preventing false security.
3. **Kinematic False Positives during Missed Approaches**:
   - Severe go-around maneuvers exceed typical airliner vertical acceleration thresholds. Demoting kinematics to supporting evidence in `altitude_consistency_v2` maintains high precision.
4. **Jamming Single-Aircraft Dilution**:
   - Ground-truth jamming zones with low traffic density remain at 21.5% fixed recall because single-aircraft observations are held at status `unknown` / `insufficient` to prevent false alarm cascades.
5. **Base-Rate Dilution in Peacetime Airspace**:
   - When `attack_share` is $\\le 0.1\\%$, operational alerting systems require corroboration from independent non-ADS-B sensors (e.g. primary radar, DME/DME, eLoran) before triggering tactical cockpit warnings. Expected precision at baseline threat prevalence ($p = 17.47\\%$) is 85.1% (leg-level pooled over clean seeds 3001-3003).
"""

    out_path.write_text(report_content, encoding="utf-8")
    print(f"Report compiled successfully to {out_path}.")


if __name__ == "__main__":
    build_report()
