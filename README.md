# AeroTrust: Build Spec v1

**Data audit checklist, database schema, metric definitions, validation plan, and day-by-day schedule**

Prepared for Pratik Shukla | November 2026

---

## 1. Project in one paragraph

AeroTrust is a data-integrity observatory for aircraft. Airbus has openly named two outside threats to aircraft data: intense solar radiation (A320 recall, November 2025) and GNSS jamming/spoofing (EASA's top safety priority; Airbus's own Fly Your Ideas 2026 theme). AeroTrust scores both in one place, says "unknown" when evidence is weak, measures a new metric called Silent Acceptance Rate (SAR), and includes an Incident Clock that prices the cost of slow scoping using Airbus's public cases.

> **Radiation Causality Notice:** Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual. Axis B is exposure context, not a cause.

**Scope tiers**

| Tier | Components |
| --- | --- |
| Must | Jamming baseline, spoofing detector, radiation exposure index, trust score with abstention, SAR (aggregate only), validation |
| Next | Incident Clock (calculator + precursor scanner), 24h forecast vs baseline, LLM briefing with verifier |
| Stretch | Delivery-corridor brief |

If time runs short, ship Must only. It is strong on its own.

---

## 2. Data audit checklist (Days 1-2)

Goal: find out what data you really have before writing any model code. Every item has a pass condition and a fallback.

### 2.1 Access and terms

| # | Task | Pass condition | Fallback |
| --- | --- | --- | --- |
| A1 | Create an OpenSky account and request historical (Trino) access. **Do this today**, approval takes time. | Access granted | Use the live REST API and collect your own snapshots over 2-3 weeks |
| A2 | Read OpenSky terms | Research / non-commercial use allowed for an interview prototype | Do not publish a public product; keep the demo private |
| A3 | Check NOAA SWPC data terms | Public data, free use | None needed |

### 2.2 Field availability (verify, do not assume)

| # | Question | Why it matters | If missing |
| --- | --- | --- | --- |
| F1 | Do tracks include barometric altitude **and** geometric (GNSS) altitude? | Core spoofing check (Section 4.1 check a) | Without both, drop check (a) |
| F2 | Are ADS-B integrity/accuracy fields available (NIC, NACp, SIL)? | Jamming baseline and SAR | Fall back to data-gap and position-jump indicators for jamming; SAR becomes "not computable", say so |
| F3 | Are Mode S Comm-B (EHS) registers available (e.g. airspeed, heading)? | Physics check against wind (check e) | Skip check (e); use checks a-d |
| F4 | Update rate and coverage in target regions (Baltic, Eastern Mediterranean, Black Sea, Middle East) vs a clean region (North Atlantic or Western Europe) | Detector needs enough points per flight | Narrow the study region to where coverage is good |
| F5 | Can icao24 be mapped to aircraft type and family (A319/A320/A321, A330, A350)? | Family-level SAR and precursor scanner | Use callsign/registration lookups; if coverage is low, report SAR for "all aircraft" only |

### 2.3 Space weather and validation sources

| # | Task | Notes |
| --- | --- | --- |
| S1 | Locate NOAA SWPC JSON services for proton flux (>10 MeV), Kp index, X-ray flux | **Verify exact endpoint names on the SWPC data page.** Store raw payloads with timestamps |
| V1 | Snapshot EASA's affected flight information regions list (7-day and 30-day rankings) weekly | Validation proxy. Note: it is itself built from ADS-B plus reports, so agreement is a sanity check, not proof |
| V2 | Identify candidate flights in historical data | Test case n=1. Confirm callsign and time window before use |

### 2.4 Decision gate at end of Day 2

Write a one-page note answering: which of F1-F5 passed? Which checks are in scope? Which fallbacks were used? Everything after this depends on that note.

---

## 3. Database schema (PostgreSQL + PostGIS, H3 cells for geography)

**flight\_track\_points**: icao24, ts, lat, lon, baro\_alt\_m, geo\_alt\_m, gs\_mps, track\_deg, vrate\_mps, on\_ground, nic, nacp, sil, source\_note

**aircraft**: icao24 (PK), registration, type\_code, family, operator

**spoof\_checks**: icao24, ts\_window\_start, ts\_window\_end, check\_name, residual, flag, confidence, n\_points

**interference\_cells**: h3\_cell, time\_bucket, jam\_score, spoof\_score, n\_aircraft, n\_checks, status (ok / degraded / unknown)

**space\_weather**: ts, kp, proton\_flux\_10mev, xray\_flux, raw\_payload\_ref

**radiation\_index**: icao24, ts, alt\_m, geomag\_lat, relative\_index, components (JSON)

**trust\_scores**: flight\_id, segment\_start, segment\_end, score, uncertainty, status (ok / degraded / unknown), reasons (array)

**sar\_aggregate**: family, region, month, n\_flights\_flagged, n\_silent, sar, ci\_low, ci\_high, suppressed (bool). **No tail numbers or icao24 anywhere in this table.**

**incident\_cases**: case\_id, name, trigger\_date, public\_statement\_date, directive\_date, aircraft\_held\_in\_service, aircraft\_held\_undelivered, days\_to\_scope, source\_urls

**precursor\_candidates** (private, never exported): icao24, ts, event\_type, vrate\_dip, altitude\_loss, radiation\_index\_at\_time, review\_status

---

## 4. Definitions

### 4.1 Spoofing checks

Each check returns a residual, a flag, and a confidence. No single check decides alone.

- **(a) Geometric vs barometric altitude:** residual = geo\_alt minus baro\_alt, compared with that flight's own baseline and regional distribution. Primary active detector in v0.3 (**`altitude_consistency_v2`** behind the abstention gate).
- **(b) Kinematic feasibility:** speed implied by consecutive positions vs reported velocity, plus bounds on acceleration and turn rate (supporting evidence only).
- **(c) Position-velocity consistency:** integrate reported velocity over a window and compare with position change (supporting evidence only).
- **(d) Multi-aircraft consensus:** **implemented, inactive, needs re-validation**. In v0.3, Check (d) is disabled due to a self-referential peer anomaly bug identified during holdout testing. Check (d) does NOT contribute to detection in v0.3.
- **(e) EHS physics (only if F3 passes):** ground speed vs true airspeed plus wind, and track vs heading (future work).

**Thresholds are set on Day 1-3 after you see real distributions. Do not hardcode numbers from this document.**

### 4.2 Jamming baseline

Drops in NIC/NACp (if F2 passes) or abnormal data gaps and position-quality loss, aggregated per H3 cell and time bucket.

### 4.3 Abstention rules (status = unknown)

A score is replaced by **unknown** when any of these hold: too few points in the window, fewer than the minimum number of independent checks available, or checks strongly disagree. The reasons array always says why.

### 4.4 Silent Acceptance Rate (SAR)

- **Numerator:** flights where at least k independent checks flagged inconsistency **and** integrity flags (NIC/NACp) stayed high throughout the flagged window.
- **Denominator:** flights where at least k independent checks flagged inconsistency.
- **Report:** SAR with a Wilson confidence interval.
- **Privacy and safety guardrails:** aggregate by aircraft family and region-month only; suppress any cell with fewer than 30 flagged flights; never publish per-aircraft or per-avionics-configuration results.
- k and the NIC/NACp cutoffs are chosen after the data audit.

### 4.5 Radiation relative index

Relative exposure index = altitude factor x geomagnetic-latitude factor x space-weather multiplier (from proton flux and Kp bins).

- It is **relative**, not a probability of any failure. Never claim a bit-flip probability.
- **Radiation Causality Notice:** Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual. Axis B is exposure context, not a cause.
- For the shape of each factor, use a documented published model or tables (for example FAA CARI-7 or NAIRAS publications), and **cite the source in your README**. Do not invent constants.

### 4.6 Incident Clock & Scoping Calculator (Phase 7 & 7.1)

**Inputs (all user-editable):** days to scope, aircraft held in-service, aircraft held undelivered, baseline monthly handover rate (optional), share recovered later (optional), value per aircraft (optional).

**Outputs (with formulas and assumptions listed on screen):**
- **Output a (Aircraft-Days Held):** `aircraft_days_held = (aircraft_held_in_service + aircraft_held_undelivered) × days_to_scope`.
- **Output b (Model A - Line Stop):** `gross_handovers_lost = baseline_handover_rate_per_month × (days_to_scope / 30)`, net of `share_recovered_later` if provided.
- **Output c (Model B - Finished Aircraft Hold):** Delivery slippage in aircraft-days: `handover_delay_aircraft_days = aircraft_held_undelivered × days_to_scope`.
- **Output d (Valuation Impact):** If `value_per_aircraft` is blank, **no money figure is shown**. Shows `--` with prompts to enter valuation.
- **One-Day Cost of Delay:** Stated in `aircraft-days / day`, with financial rate shown only if valuation is provided.
- **Sensitivity Matrix:** Sensitivity over scoping duration (0.5x, 1x, 2x).
- **Public Disclosure Timeline:** A320 solar radiation timeline (30 Oct 2025 event -> 28 Nov 2025 statement -> 28 Nov 2025 AD issued -> 1 Dec 2025 remediation), detailing the computed 29-day public gap with public-only disclosure caveat.

**Seed Cases (Strictly public facts; all marked "needs verification" until source URL is confirmed and marked sourced):**

| Case ID | Title | Directive Status | Sourced Public Facts | Verification Status |
| --- | --- | --- | --- | --- |
| `A320-SOLAR-2025` | A320 Solar Radiation Single-Event Effect | `issued` | Airbus alert and EASA emergency directive issued 28 Nov 2025 (effective date to be confirmed from the AD document); about 6,000 aircraft affected; fewer than 100 remaining on 1 Dec 2025. Computed gap: 29 days. | `needs verification` |
| `A320-PANEL-2025` | A320 Fuselage Panels Production Discrepancy | `proposed` | Airbus public statement 2 Dec 2025 (628 in scope); 2025 delivery target cut 820 to 790 on 3 Dec 2025; EASA proposed directive published 17 Dec 2025 (177 in service, 451 in production); later final directive to be confirmed. Dual sourced breakdowns: EASA proposed (177 in-service / 451 production) vs Reuters investigation (168 airline / 245 plant / 215 supplier). | `needs verification` |
| `A330NEO-TOOL-2026` | A330neo Stray Assembly Tool Inspection | `proposed` | Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026; number of aircraft inspected not disclosed; policy to regulator due mid-November 2026; scope of in-service inspections has conflicting reports (some say 24, some say 4), shown as `conflicting reports, needs verification`. | `needs verification` |

*Mandatory Scenario Notice:* "This calculator turns public information into a scenario. It does not describe Airbus internal data or decisions. Scenario outputs depend on the inputs you enter."

*Mandatory Radiation Context:* "Airbus stated that intense solar radiation may corrupt data critical to flight controls. Independent experts have questioned whether the radiation level on that date was unusual. Axis B is exposure context, not a cause."

### 4.7 Precursor scanner (hypothesis generator only)

Find A320-family aircraft in cruise with a sudden pitch-down-like profile: vertical rate drops sharply and recovers, with a defined altitude loss, outside normal phase changes. Run across cruise flights and **count false alarms** (turbulence, TCAS, ATC-directed changes). Output is a private, manually reviewed candidate list. It proves nothing by itself.

---

## 5. Validation plan

| Test | Method | Honest caveat |
| --- | --- | --- |
| Spoofing detector | Inject synthetic offsets and drifts of varying size and onset into clean tracks; report precision/recall vs offset size | Synthetic injection is not real spoofing |
| Regional sanity | Rank correlation of your cell scores with EASA's 7/30-day affected-region rankings | EASA's list uses ADS-B too, so partly circular |
| False positives | Run on a clean region and report flag rate | Clean means "no known interference", not guaranteed |
| Forecast (Next tier) | Time-split backtest vs a "repeat yesterday's map" baseline | If you do not beat the baseline, say so |
| LLM briefing (Next tier) | The model may only use numbers from computed tables; a verifier checks every number | Target: 100% of numbers verified |
| Precursor scanner | Run on the JetBlue flight (n=1), then count candidates elsewhere | Sanity check, not proof |

---

## 6. Schedule (Must tier first)

| Day | Work | Deliverable |
| --- | --- | --- |
| 1 | Apply for OpenSky; field audit F1-F5 on whatever data you can already reach; SWPC exploration | Audit notes |
| 2 | Finish audit; one-page decision note (Section 2.4) | Decision note |
| 3-4 | Ingestion pipeline, schema, H3 cells; jamming baseline map | Working map |
| 5-7 | Spoofing checks a-d (e if available); abstention rules; injection tests | Detector + test report |
| 8-9 | Radiation index; space-weather ingestion; trust score | Trust score per flight |
| 10-11 | SAR (aggregate); validation vs EASA rankings | SAR table + validation page |
| 12-13 | Dashboard (map, trust score, unknown states, SAR), deploy | Live demo |
| 14 | Demo rehearsal and limitations slide | Rehearsed 5-minute demo |
| 15+ | Next tier: Incident Clock calculator, then precursor scanner, forecast, LLM briefing | As time allows |

---

## 7. Safety and ethics guardrails

- Detection only. Never write how to spoof or jam.
- SAR stays aggregate. Do not publish per-aircraft-type or per-configuration weaknesses.
- The precursor watchlist stays private. Do not publish tail numbers.
- This is decision support, not a safety-critical system. Say so on the first slide.
- Respect OpenSky terms (research / non-commercial).

---

## 8. Interview kit

**One-line pitch:** Airbus has openly named solar radiation and GPS spoofing as threats to aircraft data. AeroTrust scores both, says "unknown" when evidence is weak, measures a new Silent Acceptance Rate, and prices slow incident scoping.

**Questions to ask the interviewer**

1. How does Airbus track fleet-level exposure to data-integrity threats today?
2. After an incident, where does scoping the affected aircraft take the most time?
3. What is the policy for sharing aggregate metrics like SAR outside the company?

**Limitations slide (say these yourself before anyone asks)**

- Public data only; validation uses proxies.
- Radiation index is relative, not a probability.
- Spoofing ground truth is not public; synthetic injection tests stand in.
- Airbus likely has internal analysis; this is an outside-in prototype.
