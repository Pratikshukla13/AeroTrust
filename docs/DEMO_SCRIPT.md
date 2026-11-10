# AeroTrust Demonstration Script

> **MANDATORY PRESENTER RULE**: **Never claim real-world accuracy.**
> All flight paths, detector evaluations, and metrics in AeroTrust are evaluated on **synthetic datasets** (`v0.3.2-verified`). The Space Weather index is **illustrative exposure context, not a cause**. Incident Clock cases await primary source verification and are currently marked "unchecked".

---

## 1. Two-Minute Executive Walkthrough

**Target Audience**: Executive leadership, regulatory observers, aviation engineering directors.  
**Objective**: Demonstrate how multi-sensor telemetry integrity can be scored without false confidence or black-box probabilities.

### Minute 0:00 – 0:30: Overview & Ground Truth Transparency
* **Action**: Open `http://localhost:5173` (or static demo URL). Show the top **SYNTHETIC** banner and Dataset Fingerprint (`v0.3.2-verified`, config hash `b6011043368eca73`).
* **Talking Point**:
  > "AeroTrust is an avionics integrity observatory. We evaluate ADS-B flight telemetry against spoofing and jamming without making black-box assertions. Every number you see comes from a frozen synthetic benchmark of 18,000 scheduled legs. We deliberately avoid words like 'safe' or 'clear'. Instead, we assign strict evidence tiers."

### Minute 0:30 – 1:00: Interference Map & Localized Jamming
* **Action**: Click **Interference Map** in the navigation bar. Rotate the 3D Earth globe to the Eastern Mediterranean / Baltic region. Click an orange H3 hexagon.
* **Talking Point**:
  > "Rather than relying on isolated aircraft alarms, our spatial engine aggregates integrity drops (NIC/NACp) across flights into H3 hexagons. Here we see multi-aircraft corroborated jamming degrading GPS reliability across contested airspace."

### Minute 1:00 – 1:30: Flight Detail & Altimetry Verification
* **Action**: Click **Flight Telemetry** in the nav bar. Select a flight with tier `flagged_altitude_inconsistency` (e.g. `x603da7_1794073786`).
* **Talking Point**:
  > "Here is our primary active detector: Check (a) geometric versus barometric altitude consistency. When the GNSS altitude deviates by more than 120 meters from barometric altimetry, the flight is flagged. We disclose uncalibrated internal scores only for diagnostics; cockpit operators see only the standardized tier and verifiable physical reasons."

### Minute 1:30 – 2:00: Incident Scenario Calculator & Limitations
* **Action**: Click **Incident Scenario Calculator**, then click the **Limitations** page.
* **Talking Point**:
  > "Integrity failures carry massive fleet holding costs. Our Incident Scenario Calculator models the sensitivity of scoping delays using transparent public presets—all flagged with red 'primary source missing' badges until regulatory airworthiness directives are verified. Finally, on our Limitations page, we openly publish what our tool cannot do: 0% horizontal spoofing recall, disabled consensus, and degraded peacetime precision. We build trust by publishing our boundaries."

---

## 2. Five-Minute Technical Deep Dive

**Target Audience**: Avionics engineers, system architects, certification teams.

### Step 1: Navigating the Overview & Evidence Tiers (0:00 – 1:00)
1. **Click**: Top-left AeroTrust logo or **Overview** tab.
2. **Observe**:
   - Four Evidence Tiers: `no_alert`, `flagged_altitude_inconsistency`, `jamming_degraded`, `insufficient`.
   - Dataset Card: 18,000 scheduled legs (5,225 continuous tracks), $N_{\text{clean}} = 13,410$, $N_{\text{spoof}} = 2,729$.
   - Headline Box: "What this can and cannot do".
3. **Presenter Script**:
   > "Notice the four standardized tiers. In v0.3, we strictly retired misleading labels like 'ok' or 'safe'. If an aircraft has consistent barometric and geometric data, it is marked `no_alert`, not 'safe'. If peer coverage is too sparse to evaluate, it is marked `insufficient`. This eliminates the dangerous illusion of guaranteed clearance."

### Step 2: Spatial Corridor Analysis on the 3D Interference Map (1:00 – 2:00)
1. **Click**: **Interference Map** in navigation.
2. **Action**:
   - Filter dropdown: Select **Eastern Mediterranean**.
   - Scrub the time-bucket slider.
   - Click any highlighted H3 hexagon cell to view the popup card.
3. **Presenter Script**:
   > "GPS spoofing rarely occurs in isolation. In the Eastern Mediterranean corridor, our pipeline tracks spatial degradation over 30-minute epoch windows. Notice the popup: it reports the exact count of corroborating aircraft and reason codes ('peer_corroborated_jamming'). When multiple aircraft simultaneously observe NIC degradation in the same cell, the entire sector transitions to `jamming_degraded`."

### Step 3: Deep Altimetry Inspection & Abstention (2:00 – 3:15)
1. **Click**: **Flight Telemetry** tab.
2. **Action**:
   - Select flight `x603da7_1794073786` (`flagged_altitude_inconsistency`).
   - Observe the Altitude Consistency Chart: Barometric Altitude (blue) vs. Geometric Altitude (red).
   - Point out the flagged discrepancy window where residual exceeds 120.0 m.
   - Switch dropdown filter to `jamming_degraded` and inspect a degraded flight (`x1007f8_1793534495`).
3. **Presenter Script**:
   > "Under the hood, Check (a) calculates the vertical residual $|h_{\text{geo}} - h_{\text{baro}}|$. Here, you can see the red geometric trace drifting while the barometric profile remains stable, crossing our frozen 120-meter threshold. Note the telemetry breakdown: Check (d) multi-aircraft consensus is transparently labeled as inactive because of self-referential graph loops we discovered in earlier validation. We show exactly which checks fired and which are disabled."

### Step 4: SAR Privacy Auditor (3:15 – 4:00)
1. **Click**: **SAR Privacy** tab.
2. **Observe**:
   - Silent Acceptance Rate ($\hat{\text{SAR}}$) table across aircraft families (A320, B737, E190).
   - Suppression markers: Cells with $N < 30$ are marked `suppressed` to prevent identity leakage.
3. **Presenter Script**:
   > "Silent Acceptance Rate measures the proportion of spoofed flights where avionics accepted false data without triggering basic receiver alerts (NIC/NACp). But reporting micro-cohorts could leak airline fleet vulnerabilities. Therefore, our engine enforces complementary cell suppression: any cohort with fewer than 30 scheduled legs is masked, preventing inference by subtraction."

### Step 5: Incident Scenario Calculator & Limitations Disclosure (4:00 – 5:00)
1. **Click**: **Incident Scenario Calculator** tab.
2. **Action**:
   - Select the **A320 Panel Recall (2025)** preset.
   - Show that only sourced fields (`aircraft_held_in_service: 177`, `aircraft_held_undelivered: 451`) are filled; unsourced fields remain empty.
   - Note the red badge: **primary source missing (status: unchecked)**.
   - Click the **Limitations** tab and highlight the Base Rate Sensitivity table.
3. **Presenter Script**:
   > "In the Incident Scenario Calculator, we separate verified facts from operational assumptions. Presets leave unsourced parameters empty, preventing fabricated valuations. Notice the red disclaimer: primary airworthiness directives require formal confirmation. Finally, on our Limitations page, we show that in normal peacetime conditions, false alarms from background sensor noise dominate, dropping precision to 0.2%. By disclosing these weaknesses openly, AeroTrust provides engineering credibility rather than marketing hype."

---

## 3. Screen-by-Screen Reference & FAQs

| Screen / Route | Core Message | What NEVER to Say |
| :--- | :--- | :--- |
| **Overview (`/`)** | Transparent tier distribution from frozen synthetic benchmark. | Never call flights "cleared", "safe", or "certifiably clean". |
| **Interference Map (`/map`)** | Spatial clustering of RF degradation into H3 cells. | Never claim this shows real Russian/Middle Eastern live military emitters. |
| **Flight Detail (`/flight-detail`)** | Altimetry residual inspection and Check (a) mechanics. | Never claim the uncalibrated score is an absolute probability of hostile attack. |
| **SAR Auditor (`/sar`)** | Fleet vulnerability auditing under $N \ge 30$ privacy protection. | Never claim SAR isolates individual airline operational culpability. |
| **Incident Scenario Calculator (`/incidents`)** | Sensitivity calculator for fleet holding costs under directives. | Never claim the financial numbers are audited airline losses. |
| **Limitations (`/limitations`)** | Full disclosure of failure modes, 0% horizontal recall, and base-rate penalties. | Never promise that multi-aircraft consensus is actively protecting flights today. |
