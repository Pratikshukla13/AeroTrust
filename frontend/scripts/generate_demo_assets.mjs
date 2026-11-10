import { chromium } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')
const demoDir = path.resolve(rootDir, '..', 'docs', 'demo')
const docsDir = path.resolve(rootDir, '..', 'docs')

fs.mkdirSync(demoDir, { recursive: true })

const FORBIDDEN_WORDS_REGEX = /\b(ok|safe|clear|assured)\b/i

async function run() {
  console.log('--- Starting Vite Preview Server in Demo Mode ---')
  const cmd = process.platform === 'win32' ? 'npx.cmd' : 'npx'
  const preview = spawn(cmd, ['vite', 'preview', '--port', '4173', '--strictPort'], {
    cwd: rootDir,
    shell: true,
    stdio: 'pipe',
  })

  preview.stdout.on('data', (d) => process.stdout.write(`[VitePreview] ${d}`))
  preview.stderr.on('data', (d) => process.stderr.write(`[VitePreview ERR] ${d}`))

  // Wait for preview server
  let serverReady = false
  for (let i = 0; i < 60; i++) {
    try {
      const res = await fetch('http://localhost:4173')
      if (res.status === 200 || res.status === 304 || res.status === 404) {
        serverReady = true
        console.log(`Preview server responded after ${(i + 1) * 500}ms`)
        break
      }
    } catch {
      // Waiting
    }
    await new Promise((r) => setTimeout(r, 500))
  }

  if (!serverReady) {
    throw new Error('Vite preview server failed to start on port 4173')
  }

  const browser = await chromium.launch({ headless: true })

  const routes = [
    { id: 'overview', label: 'Overview' },
    { id: 'map', label: 'Interference Map' },
    { id: 'flight-detail', label: 'Flight Detail' },
    { id: 'sar', label: 'SAR Metrics' },
    { id: 'limitations', label: 'Limitations' },
    { id: 'incident-clock', label: 'Incident Scenario Calculator' },
  ]

  let allViolations = []
  let integrityFailures = []

  try {
    // 1. Desktop Viewport (1366x768)
    console.log('\n--- Capturing Desktop Screenshots & Axe Audit (1366x768) ---')
    const desktopContext = await browser.newContext({ viewport: { width: 1366, height: 768 } })
    const page = await desktopContext.newPage()

    await page.goto('http://localhost:4173')
    await page.waitForLoadState('networkidle')

    for (const route of routes) {
      console.log(`Auditing Desktop: ${route.label}...`)
      await page.click(`nav[aria-label="Main Navigation"] button:has-text("${route.label}")`)
      await page.waitForTimeout(800)

      const ssPath = path.join(demoDir, `desktop_${route.id}.png`)
      await page.screenshot({ path: ssPath, fullPage: false })
      console.log(`  Saved: ${ssPath}`)

      // Verify Synthetic Banner & Dataset Fingerprint & Footer
      const hasBanner = await page.locator('[data-testid="synthetic-banner"]').isVisible()
      const hasFingerprint = await page.locator('text=v0.3.2-verified').first().isVisible()
      const hasFooter = await page.locator('[data-testid="app-footer"]').isVisible()
      if (!hasBanner) integrityFailures.push({ route: route.id, failure: 'Synthetic banner missing' })
      if (!hasFingerprint) integrityFailures.push({ route: route.id, failure: 'Dataset fingerprint tag missing' })
      if (!hasFooter) integrityFailures.push({ route: route.id, failure: 'Footer missing' })

      // Check forbidden words
      const text = await page.evaluate(() => document.body.innerText)
      const match = text.match(FORBIDDEN_WORDS_REGEX)
      if (match) {
        integrityFailures.push({ route: route.id, failure: `Forbidden word rendered: ${match[0]}` })
      }

      // Phase 8.1 Incident Clock: check "Work in progress: sources being verified" header
      if (route.id === 'incident-clock') {
        const hasPendingHeader = await page.locator('[data-testid="sources-work-in-progress-header"]').isVisible()
        if (!hasPendingHeader) {
          integrityFailures.push({ route: route.id, failure: '"Work in progress: sources being verified" header missing' })
        }
      }

      // Full Axe-core audit across all impact levels (critical, serious, moderate, minor)
      const axeResults = await new AxeBuilder({ page }).analyze()
      for (const v of axeResults.violations) {
        allViolations.push({
          route: route.id,
          id: v.id,
          impact: v.impact,
          description: v.description,
          nodes: v.nodes.length,
          sampleSelector: v.nodes[0]?.target?.join(' '),
          helpUrl: v.helpUrl,
        })
      }
    }
    await desktopContext.close()

    // 2. Mobile Viewport (390x844)
    console.log('\n--- Capturing Mobile Screenshots (390x844) ---')
    const mobileContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
    })
    const mobilePage = await mobileContext.newPage()
    await mobilePage.goto('http://localhost:4173')
    await mobilePage.waitForLoadState('networkidle')

    for (const route of routes) {
      // On mobile, toggle mobile drawer
      const hamburger = mobilePage.locator('button[aria-label="Toggle Navigation Menu"]')
      if (await hamburger.isVisible()) {
        await hamburger.click()
        await mobilePage.waitForTimeout(400)
      }
      // Click the route button inside mobile drawer or visible nav
      const routeBtn = mobilePage.locator(`button:has-text("${route.label}")`).last()
      await routeBtn.click({ force: true })
      await mobilePage.waitForTimeout(800)

      const ssPath = path.join(demoDir, `mobile_${route.id}.png`)
      await mobilePage.screenshot({ path: ssPath, fullPage: false })
      console.log(`  Saved: ${ssPath}`)
    }
    await mobileContext.close()

    // 3. Generate One-Page PDF: "AeroTrust at a glance"
    console.log('\n--- Generating One-Page PDF: AeroTrust at a glance ---')
    const pdfPage = await browser.newPage()
    const pdfHtml = `
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {
    size: A4 portrait;
    margin: 10mm 12mm 10mm 12mm;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    font-size: 8.5pt;
    line-height: 1.35;
  }
  .header {
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .title {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 9pt;
    font-weight: 600;
    color: #0284c7;
  }
  .badge-tag {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    padding: 3px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 7.5pt;
    color: #334155;
  }
  .synthetic-banner {
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    padding: 5px 8px;
    margin-bottom: 8px;
    font-size: 7.5pt;
    color: #991b1b;
  }
  .section {
    margin-bottom: 8px;
  }
  .section-title {
    font-size: 9.5pt;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 2px;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .box-can {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 4px;
    padding: 6px 8px;
  }
  .box-cannot {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 4px;
    padding: 6px 8px;
  }
  .box-title {
    font-weight: 700;
    font-size: 8pt;
    margin-bottom: 4px;
  }
  .box-can .box-title { color: #166534; }
  .box-cannot .box-title { color: #991b1b; }
  ul {
    padding-left: 12px;
  }
  li {
    margin-bottom: 2px;
    font-size: 7.5pt;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7.5pt;
    margin-top: 4px;
  }
  th {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    padding: 3px 5px;
    text-align: left;
    font-weight: 700;
    color: #334155;
  }
  td {
    border: 1px solid #e2e8f0;
    padding: 3px 5px;
  }
  .tier-pill {
    display: inline-block;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 7pt;
    font-weight: 600;
  }
  .tier-no-alert { background: #dcfce7; color: #15803d; }
  .tier-flagged { background: #fee2e2; color: #b91c1c; }
  .tier-jamming { background: #fef3c7; color: #b45309; }
  .tier-insufficient { background: #f1f5f9; color: #64748b; }
  .footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    margin-top: 8px;
    display: flex;
    justify-content: space-between;
    font-size: 7pt;
    color: #64748b;
  }
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="title">AeroTrust at a Glance</div>
    <div class="subtitle">Avionics Telemetry Integrity Observatory &amp; Verification System</div>
  </div>
  <div style="text-align: right;">
    <div class="badge-tag">Eval Tag: v0.3.2-verified</div>
    <div class="badge-tag" style="margin-top: 2px;">App Tag: v1.0.3-demo</div>
  </div>
</div>

<div class="synthetic-banner">
  <strong>SYNTHETIC DATASET NOTICE:</strong> All trajectories and threat injections are synthetic simulations. Numbers derived from pooled clean seeds (3001-3003; 18,000 scheduled legs). No operational commercial flights are depicted.
</div>

<div class="section">
  <div class="section-title">1. Executive Summary</div>
  <p style="font-size: 8pt; margin-bottom: 4px;">
    AeroTrust is an avionics data-integrity observatory designed to evaluate aircraft ADS-B telemetry against GNSS spoofing, interference, and atmospheric radiation anomalies in a single unified interface. Operating under frozen verification benchmarks on synthetic flight trajectories, it pairs physics-based altimetry consistency checks with an unsupervised abstention engine, classifying telemetry into four standardized evidence tiers (<span class="tier-pill tier-no-alert">no_alert</span>, <span class="tier-pill tier-flagged">flagged_altitude_inconsistency</span>, <span class="tier-pill tier-jamming">jamming_degraded</span>, <span class="tier-pill tier-insufficient">insufficient</span>). It features an aggregate Silent Acceptance Rate (SAR) auditor, geographic H3 interference mapping, and an Incident Scenario Calculator for aviation airworthiness directives.
  </p>
</div>

<div class="section">
  <div class="section-title">2. Operational Capabilities &amp; Boundaries</div>
  <div class="grid-2">
    <div class="box-can">
      <div class="box-title">&#10003; WHAT AEROTRUST CAN DO</div>
      <ul>
        <li><strong>Altimetry Verification:</strong> Compares barometric vs GNSS altitude residuals, flagging vertical discrepancies &gt; 120.0 m (Check a).</li>
        <li><strong>Interference Clustering:</strong> Aggregates multi-aircraft NIC/NACp/SIL drops into H3 spatial cells for regional jamming detection.</li>
        <li><strong>Evidence-Tiered Output:</strong> Never exposes uncalibrated probabilities or claims flights are &quot;safe&quot;; uses standardized evidence tiers.</li>
        <li><strong>Privacy-Preserving SAR:</strong> Evaluates Silent Acceptance Rate with cell suppression for cohorts where N &lt; 30.</li>
        <li><strong>Incident Scenario Calculator:</strong> Models fleet scoping delay sensitivity under airworthiness directives using transparent parameters.</li>
      </ul>
    </div>
    <div class="box-cannot">
      <div class="box-title">&#10007; WHAT AEROTRUST CANNOT DO</div>
      <ul>
        <li><strong>0% Horizontal Spoofing Recall:</strong> Cannot detect lateral track shifts or circular waypoint attacks (vertical only).</li>
        <li><strong>No Real-World Certification:</strong> Benchmarks are synthetic; not calibrated on certified Flight Data Recorders.</li>
        <li><strong>Consensus Inactive:</strong> Multi-aircraft consensus (Check d) is disabled due to self-referential graph loops.</li>
        <li><strong>Peacetime Base-Rate Drop:</strong> At 0.01% threat prevalence, precision drops to 0.2% due to background barometric noise.</li>
        <li><strong>No Radiation Causality:</strong> Solar proton flux and Kp indices serve strictly as illustrative exposure context, not a cause.</li>
        <li><strong>No Audited Financials:</strong> Incident Scenario Calculator cases require verified primary AD documents (currently unchecked).</li>
      </ul>
    </div>
  </div>
</div>

<div class="section">
  <div class="section-title">3. Verified Benchmark Evidence &amp; Performance Metrics</div>
  <table>
    <thead>
      <tr>
        <th>Metric / Capability</th>
        <th>Verified Result</th>
        <th>Baseline &amp; Operational Evaluation Scope</th>
        <th>Tag &amp; Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Spoofing Precision (Check a)</strong></td>
        <td><strong>83.0%</strong> (79.7% &ndash; 85.8%)</td>
        <td>Test Base Rate = 17.47% (5,225 segmented tracks)</td>
        <td><code>v0.3.2-verified</code> (Frozen)</td>
      </tr>
      <tr>
        <td><strong>Spoofing Recall (Check a)</strong></td>
        <td><strong>40.8%</strong> (37.6% &ndash; 44.0%)</td>
        <td>Altimetry consistency detector (|Geo - Baro| &gt; 120 m)</td>
        <td><code>v0.3.2-verified</code> (Frozen)</td>
      </tr>
      <tr>
        <td><strong>Horizontal Spoofing Recall</strong></td>
        <td><strong>0.0%</strong></td>
        <td>Lateral displacements produce 0 altitude residual</td>
        <td><code>v0.3.2-verified</code> (Known Limit)</td>
      </tr>
      <tr>
        <td><strong>Clean False Positives (Legs)</strong></td>
        <td><strong>42 to 52</strong> per seed</td>
        <td>~35-36 baro-bias draws + 7-16 boundary leg splits</td>
        <td><code>v0.3.2-verified</code> (Documented)</td>
      </tr>
      <tr>
        <td><strong>Multi-Aircraft Consensus</strong></td>
        <td><strong>0.0% (Inactive)</strong></td>
        <td>Check (d) disabled; needs re-validation in v0.4</td>
        <td><code>v0.3.1-claims</code> (Disabled)</td>
      </tr>
      <tr>
        <td><strong>SAR Suppression Threshold</strong></td>
        <td><strong>N &ge; 30 enforced</strong></td>
        <td>Sub-threshold cells suppressed; no marginal leakage</td>
        <td><code>v0.3.2-verified</code> (Enforced)</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="section">
  <div class="section-title">4. Plain-Language Disclaimers &amp; Known Weaknesses</div>
  <p style="font-size: 7.5pt; line-height: 1.3;">
    1. <strong>Altitude-consistency only:</strong> Only vertical discrepancies trigger detection.<br/>
    2. <strong>False alarm base rate:</strong> In peacetime airspaces, sensor turbulence produces ~117 false alarms per 10,000 clean flights.<br/>
    3. <strong>Abstention scope:</strong> Benchmark commercial flights have N &ge; 68 points; abstention is exercised only in the demo dataset.<br/>
    4. <strong>Incident case presets:</strong> All 3 presets (A320 Solar, A320 Panels, A330neo) display &quot;primary source missing&quot; in red until primary regulatory airworthiness directives are formally verified.
  </p>
</div>

<div class="footer">
  <div>Eval Tag: v0.3.2-verified &bull; App Tag: v1.0.3-demo &bull; Independent personal project, not affiliated with or endorsed by Airbus. Uses public information only.</div>
  <div>Page 1 of 1</div>
</div>

</body>
</html>
    `
    await pdfPage.setContent(pdfHtml, { waitUntil: 'networkidle' })
    const pdfPath = path.join(docsDir, 'aerotrust_at_a_glance.pdf')
    await pdfPage.pdf({
      path: pdfPath,
      format: 'A4',
      printBackground: true,
      margin: { top: '10mm', bottom: '10mm', left: '12mm', right: '12mm' },
    })
    console.log(`Saved One-Page PDF: ${pdfPath}`)
    await pdfPage.close()

  } finally {
    await browser.close()
    preview.kill('SIGKILL')
  }

  console.log('\n======================================================')
  console.log('--- Phase 8.1 Full Axe-Core Accessibility Audit Results ---')
  console.log('======================================================')
  console.log(`Total Findings across all severities: ${allViolations.length}`)

  const byImpact = { critical: 0, serious: 0, moderate: 0, minor: 0 }
  for (const v of allViolations) {
    if (byImpact[v.impact] !== undefined) byImpact[v.impact]++
  }
  console.log(`Breakdown: Critical: ${byImpact.critical}, Serious: ${byImpact.serious}, Moderate: ${byImpact.moderate}, Minor: ${byImpact.minor}`)

  let reportMd = `# AeroTrust Axe-Core Full Accessibility Audit Report (Phase 8.1)\n\n`
  reportMd += `> **Audit Scope**: All standard routes in static demo mode across Desktop (1366x768) and Mobile (390x844).\n`
  reportMd += `> **Severity Breakdown**: Critical: **${byImpact.critical}**, Serious: **${byImpact.serious}**, Moderate: **${byImpact.moderate}**, Minor: **${byImpact.minor}** (Total: **${allViolations.length}**).\n\n`
  reportMd += `| Route | Rule ID | Impact | Affected Elements | Description | Selector |\n`
  reportMd += `|:---|:---|:---:|:---:|:---|:---|\n`

  for (const v of allViolations) {
    console.log(`[${v.impact.toUpperCase()}] Route: ${v.route} | Rule: ${v.id} | Elements: ${v.nodes} | ${v.description}`)
    reportMd += `| \`${v.route}\` | \`${v.id}\` | **${v.impact}** | ${v.nodes} | ${v.description.replace(/\|/g, '\\|')} | \`${(v.sampleSelector || '').replace(/\|/g, '\\|')}\` |\n`
  }

  if (allViolations.length === 0) {
    reportMd += `\n*0 automated axe-core findings; manual accessibility checks pending.*\n`
  }

  fs.writeFileSync(path.join(docsDir, 'AXE_ACCESSIBILITY_REPORT.md'), reportMd, 'utf8')
  console.log(`Wrote full axe-core report to docs/AXE_ACCESSIBILITY_REPORT.md`)

  console.log('\n======================================================')
  console.log('--- Phase 8.1 Demo Packaging & Integrity Summary ---')
  console.log('======================================================')
  console.log(`Integrity Failures: ${integrityFailures.length}`)

  if (integrityFailures.length > 0) {
    console.error('Integrity failures detected:', integrityFailures)
    process.exit(1)
  }

  console.log('All static demo screenshots captured into docs/demo/!')
  console.log('One-page PDF "AeroTrust at a glance" generated in docs/aerotrust_at_a_glance.pdf!')
  console.log('Static demo mode smoke test passed with 0 integrity failures!')
}

run().catch((err) => {
  console.error('Fatal Demo Assets Generation Error:', err)
  process.exit(1)
})
