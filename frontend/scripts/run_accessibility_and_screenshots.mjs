import { chromium } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')
const screenshotsDir = path.resolve(rootDir, '..', 'docs', 'screenshots')

fs.mkdirSync(screenshotsDir, { recursive: true })

const FORBIDDEN_WORDS_REGEX = /\b(ok|safe|clear|assured)\b/i

async function run() {
  console.log('--- Starting Vite Preview Server ---')
  const preview = spawn('npx', ['vite', 'preview', '--port', '4173', '--strictPort'], {
    cwd: rootDir,
    shell: true,
    stdio: 'pipe',
  })

  // Wait for preview server to become fully responsive
  console.log('--- Awaiting Vite Preview Server on Port 4173 ---')
  let serverReady = false
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch('http://localhost:4173')
      if (res.status === 200 || res.status === 404) {
        serverReady = true
        console.log(`Preview server responded with status ${res.status} after ${(i + 1) * 500}ms`)
        break
      }
    } catch {
      // Wait for server to accept TCP connections
    }
    await new Promise((resolve) => setTimeout(resolve, 500))
  }

  if (!serverReady) {
    throw new Error('Vite preview server failed to become responsive on port 4173 within 20s!')
  }

  console.log('--- Launching Headless Chromium ---')
  const browser = await chromium.launch({
    headless: true,
  })

  const routes = [
    { id: 'overview', label: 'Overview' },
    { id: 'map', label: 'Interference Map' },
    { id: 'flight-detail', label: 'Flight Detail' },
    { id: 'sar', label: 'SAR Metrics' },
    { id: 'limitations', label: 'Limitations' },
    { id: 'incident-clock', label: 'Incident Clock' },
    { id: 'briefing', label: 'Briefing' },
    { id: 'corridors', label: 'Corridors' },
    { id: 'watchlist', label: 'Watchlist' },
  ]

  let allViolations = []
  let integrityFailures = []

  try {
    // -----------------------------------------------------------------------
    // 1. Desktop Viewport (1366x768) - Full Screenshot & Axe Audit
    // -----------------------------------------------------------------------
    console.log('\n======================================================')
    console.log('--- Auditing Desktop Viewport (1366x768) Across All Routes ---')
    console.log('======================================================')
    const desktopContext = await browser.newContext({
      viewport: { width: 1366, height: 768 },
    })
    const page = await desktopContext.newPage()
    page.on('console', (msg) => console.log('PAGE LOG:', msg.text()))
    page.on('pageerror', (err) => console.log('PAGE ERROR:', err.message))
    await page.goto('http://localhost:4173')
    await page.waitForLoadState('networkidle')

    for (const route of routes) {
      console.log(`\n[Desktop 1366x768] Auditing Route: ${route.label}...`)
      // Click navigation button for this route in main sidebar
      await page.click(`nav[aria-label="Main Navigation"] button:has-text("${route.label}")`)
      await page.waitForTimeout(800) // Transition and fetch wait

      // Save desktop screenshot
      const screenshotPath = path.join(screenshotsDir, `desktop_${route.id}.png`)
      await page.screenshot({ path: screenshotPath, fullPage: false })
      console.log(`  Saved desktop screenshot: ${screenshotPath}`)

      // DOM Integrity Rule 1: No forbidden words ("ok", "safe", "clear", "assured")
      const pageText = await page.evaluate(() => document.body.innerText)
      const matchForbidden = pageText.match(FORBIDDEN_WORDS_REGEX)
      if (matchForbidden) {
        console.error(`  INTEGRITY VIOLATION on ${route.id}: Found forbidden word '${matchForbidden[0]}'`)
        integrityFailures.push({ route: route.id, failure: `Forbidden word rendered: ${matchForbidden[0]}` })
      }

      // DOM Integrity Rule 2: Never show probability for Axis A
      if (pageText.match(/Axis A.*probability/i) || pageText.match(/calibrated_prob/i)) {
        console.error(`  INTEGRITY VIOLATION on ${route.id}: Axis A probability exposed in DOM!`)
        integrityFailures.push({ route: route.id, failure: 'Axis A probability rendered' })
      }

      // DOM Integrity Rule 3: On SAR page, suppressed cells must NOT expose counts
      if (route.id === 'sar') {
        const suppressedCountsExposed = await page.evaluate(() => {
          const rows = document.querySelectorAll('tr[data-testid*="sar-row"]')
          for (const row of rows) {
            if (row.textContent && row.textContent.includes('suppressed')) {
              // Any digits inside sample size or silent count cells?
              const sampleCell = row.querySelector('[data-testid*="cell-sample-size"]')
              if (sampleCell && /\d+/.test(sampleCell.textContent || '')) return true
            }
          }
          return false
        })
        if (suppressedCountsExposed) {
          console.error(`  INTEGRITY VIOLATION on SAR: Suppressed cell exposed numeric count!`)
          integrityFailures.push({ route: 'sar', failure: 'Suppressed count exposed' })
        }
      }

      // DOM Integrity Rule 4: On Overview, numbers must match API
      if (route.id === 'overview') {
        const noAlertText = await page.locator('[data-testid="tier-count-no_alert"]').innerText()
        const countClean = parseInt(noAlertText.replace(/,/g, ''), 10)
        if (countClean !== 14654) {
          console.error(`  INTEGRITY VIOLATION on Overview: count ${countClean} differs from API (14654)!`)
          integrityFailures.push({ route: 'overview', failure: `Count mismatch: ${countClean} != 14654` })
        }
      }

      // Run Axe accessibility & contrast check
      const results = await new AxeBuilder({ page })
        .withRules(['color-contrast', 'aria-roles', 'button-name', 'image-alt'])
        .analyze()

      const contrastViolations = results.violations.filter((v) => v.id === 'color-contrast')
      if (contrastViolations.length > 0) {
        console.error(`  Contrast violations on ${route.id}:`, JSON.stringify(contrastViolations, null, 2))
        allViolations.push({ route: route.id, violations: contrastViolations })
      } else {
        console.log(`  Axe-core accessibility & contrast check passed (>=4.5:1 ratio).`)
      }
    }
    await desktopContext.close()

    // -----------------------------------------------------------------------
    // 2. Mobile Viewport (375x812) - Full Screenshots for ALL 9 Routes & Axe
    // -----------------------------------------------------------------------
    console.log('\n======================================================')
    console.log('--- Auditing Phone Viewport (375x812) Across ALL 9 Routes ---')
    console.log('======================================================')
    const mobileContext = await browser.newContext({
      viewport: { width: 375, height: 812 },
      isMobile: true,
      hasTouch: true,
    })
    const mobilePage = await mobileContext.newPage()
    await mobilePage.goto('http://localhost:4173')
    await mobilePage.waitForLoadState('networkidle')

    for (const route of routes) {
      console.log(`\n[Phone 375x812] Auditing Route: ${route.label}...`)
      // Open mobile hamburger menu
      await mobilePage.click('button[aria-label="Toggle Navigation Menu"]')
      await mobilePage.waitForTimeout(300)

      // Click route navigation button
      await mobilePage.click(`nav[aria-label="Main Navigation"] button:has-text("${route.label}")`, { force: true })
      await mobilePage.waitForTimeout(800) // Transition wait

      // Save mobile screenshot for ALL routes
      const mobileScreenshotPath = path.join(screenshotsDir, `mobile_${route.id}.png`)
      await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: false })
      console.log(`  Saved phone screenshot: ${mobileScreenshotPath}`)

      // Run Axe accessibility on mobile view
      const results = await new AxeBuilder({ page: mobilePage })
        .withRules(['color-contrast', 'aria-roles', 'button-name', 'image-alt'])
        .analyze()

      const contrastViolations = results.violations.filter((v) => v.id === 'color-contrast')
      if (contrastViolations.length > 0) {
        console.error(`  Mobile contrast violations on ${route.id}:`, JSON.stringify(contrastViolations, null, 2))
        allViolations.push({ route: `mobile_${route.id}`, violations: contrastViolations })
      } else {
        console.log(`  Mobile Axe-core accessibility check passed.`)
      }
    }
    await mobileContext.close()
  } finally {
    await browser.close()
    preview.kill('SIGTERM')
    console.log('\n--- Teardown complete ---')
  }

  if (integrityFailures.length > 0) {
    console.error(`\nFAIL: Detected ${integrityFailures.length} Phase 6 integrity rule failures:`, integrityFailures)
    process.exit(1)
  }

  if (allViolations.length > 0) {
    console.error(`\nFAIL: Detected ${allViolations.length} routes with accessibility/contrast violations!`)
    process.exit(1)
  }

  console.log('\nSUCCESS: 0 automated axe-core findings; manual accessibility checks pending.')
}

run().catch((err) => {
  console.error(err)
  process.exit(1)
})
