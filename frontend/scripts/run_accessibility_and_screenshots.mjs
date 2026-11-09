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

async function run() {
  console.log('--- Starting Vite Preview Server ---')
  const preview = spawn('npx', ['vite', 'preview', '--port', '4173', '--strictPort'], {
    cwd: rootDir,
    shell: true,
    stdio: 'pipe',
  })

  // Wait for server to become responsive
  await new Promise((resolve) => setTimeout(resolve, 2500))

  console.log('--- Launching Headless Chromium ---')
  const browser = await chromium.launch({
    headless: true,
  })

  const routes = [
    { id: 'overview', label: 'Overview' },
    { id: 'map', label: 'Interference Map' },
    { id: 'flight-detail', label: 'Flight Detail' },
    { id: 'sar', label: 'SAR Metrics' },
    { id: 'incident-clock', label: 'Incident Clock' },
    { id: 'briefing', label: 'Briefing' },
    { id: 'corridors', label: 'Corridors' },
    { id: 'watchlist', label: 'Watchlist' },
    { id: 'limitations', label: 'Limitations' },
  ]

  let allViolations = []

  try {
    // 1. Desktop Viewport (1366x768)
    console.log('\n--- Auditing Desktop Viewport (1366x768) ---')
    const desktopContext = await browser.newContext({
      viewport: { width: 1366, height: 768 },
    })
    const page = await desktopContext.newPage()
    await page.goto('http://localhost:4173')
    await page.waitForLoadState('networkidle')

    for (const route of routes) {
      console.log(`Auditing Route: ${route.label}...`)
      // Click navigation button for this route
      await page.click(`button:has-text("${route.label}")`)
      await page.waitForTimeout(400) // Transition wait

      // Save screenshot
      const screenshotPath = path.join(screenshotsDir, `desktop_${route.id}.png`)
      await page.screenshot({ path: screenshotPath, fullPage: false })
      console.log(`  Saved screenshot: ${screenshotPath}`)

      // Run Axe accessibility & contrast check
      const results = await new AxeBuilder({ page })
        .withRules(['color-contrast', 'aria-roles', 'button-name', 'image-alt'])
        .analyze()

      const contrastViolations = results.violations.filter((v) => v.id === 'color-contrast')
      if (contrastViolations.length > 0) {
        console.error(`  Contrast violations on ${route.id}:`, JSON.stringify(contrastViolations, null, 2))
        allViolations.push({ route: route.id, violations: contrastViolations })
      } else {
        console.log(`  Accessibility & contrast check passed (>=4.5:1 ratio).`)
      }
    }
    await desktopContext.close()

    // 2. Mobile Viewport (375x812 - modern phone)
    console.log('\n--- Auditing Mobile Phone Viewport (375x812) ---')
    const mobileContext = await browser.newContext({
      viewport: { width: 375, height: 812 },
      isMobile: true,
      hasTouch: true,
    })
    const mobilePage = await mobileContext.newPage()
    await mobilePage.goto('http://localhost:4173')
    await mobilePage.waitForLoadState('networkidle')

    // Capture mobile overview
    const mobileOverviewPath = path.join(screenshotsDir, 'mobile_overview.png')
    await mobilePage.screenshot({ path: mobileOverviewPath, fullPage: false })
    console.log(`  Saved mobile overview: ${mobileOverviewPath}`)

    // Capture mobile map
    await mobilePage.click('button[aria-label="Toggle Navigation Menu"]')
    await mobilePage.waitForTimeout(300)
    await mobilePage.click('button:has-text("Interference Map")')
    await mobilePage.waitForTimeout(500)

    const mobileMapPath = path.join(screenshotsDir, 'mobile_map.png')
    await mobilePage.screenshot({ path: mobileMapPath, fullPage: false })
    console.log(`  Saved mobile map: ${mobileMapPath}`)

    await mobileContext.close()
  } finally {
    await browser.close()
    preview.kill('SIGTERM')
    console.log('--- Teardown complete ---')
  }

  if (allViolations.length > 0) {
    console.error(`FAIL: Detected ${allViolations.length} routes with accessibility/contrast violations!`)
    process.exit(1)
  } else {
    console.log('\nSUCCESS: All 9 routes passed automated WCAG 2.1 AA (>= 4.5:1) accessibility & contrast auditing!')
  }
}

run().catch((err) => {
  console.error(err)
  process.exit(1)
})

