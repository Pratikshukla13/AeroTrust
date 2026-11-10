# AeroTrust Manual Accessibility Verification Checklist

This document tracks manual accessibility verification protocols that supplement automated axe-core testing.
Automated audit status: **0 automated axe-core findings; manual accessibility checks pending**.

---

## 1. Keyboard-Only Navigation Walkthrough
*Verify that all interactive elements, navigation links, filters, and dialogs are fully navigable and operable without a mouse.*

- [ ] **Tab Order & Focus Visibility**: Focus ring is clearly visible across all interactive controls (buttons, links, form inputs) on every route.
- [ ] **Skip Links & Navigation**: User can tab through the primary navigation drawer, toggle between views, and jump to main content.
- [ ] **Modal & Drawer Focus Trapping**: When the mobile navigation drawer is opened, focus stays within the drawer until dismissed (ESC key or close button).
- [ ] **Data Table Scrolling & Interaction**: In the SAR table and Incident Scenario Calculator table, overflowing content is reachable and navigable via keyboard arrow keys.
- [ ] **Interactive Calculator Controls**: All input fields (steppers, text inputs, radio selections) in the Incident Scenario Calculator allow full keyboard data entry and adjustment.

**Result / Notes**:
```
[ ] PENDING EVALUATION
Tester:
Date:
Notes:
```

---

## 2. 200% Browser Zoom & Reflow (WCAG 1.4.10 / 1.4.4)
*Verify that content reflows without loss of information or functionality when zoomed up to 200% on a standard desktop viewport (1280px+).*

- [ ] **Text Container Reflow**: Text wraps cleanly without truncation, overlapping, or clipping across all evidence cards and tables.
- [ ] **Horizontal Scrolling Avoidance**: Content reflows vertically into single-column or responsive layouts, avoiding bi-directional scrolling except for data tables.
- [ ] **Header & Banner Layouts**: Top `SYNTHETIC` disclaimer banner, dataset fingerprint bar, and page headers remain legible and properly aligned.
- [ ] **Plot & Map Canvas Scaling**: The 3D globe / map canvas and altimetry profile chart scale down gracefully or fit within the expanded viewport.

**Result / Notes**:
```
[ ] PENDING EVALUATION
Tester:
Date:
Notes:
```

---

## 3. Reduced Motion (`prefers-reduced-motion: reduce`)
*Verify that animations and transitions respect user system preferences for reduced motion.*

- [ ] **3D Globe Rotation**: When `prefers-reduced-motion` is enabled, Three.js globe auto-rotation ceases and falls back to a static view or fixed perspective.
- [ ] **Telemetry Pulse & Glow Transitions**: CSS radar sweep, pulse animations, and glowing alerts remain static.
- [ ] **Drawer Transitions**: Navigation menu opens and closes instantly without slide animations.

**Result / Notes**:
```
[ ] PENDING EVALUATION
Tester:
Date:
Notes:
```

---

## 4. Screen-Reader Verification Pass (NVDA / VoiceOver / JAWS)
*Verify speech output, semantic landmark navigation, and announcement of dynamic content.*

- [ ] **Landmark Hierarchy**: Screen reader recognizes `<header>`, `<nav>`, `<main>`, and `<footer role="contentinfo">`.
- [ ] **Heading Navigation (H Key)**: Each route announces exactly one `<h1>` title, followed logically by `<h2>` section headers and `<h3>` component cards with no skipped levels.
- [ ] **Dynamic Live Region Announcements**: Role alert announcements (`<div role="alert">`) are read upon view mount (e.g., synthetic disclaimer, static demo substitution warning).
- [ ] **Table Semantics**: SAR regional breakdown and Incident Scenario sensitivity tables announce column and row headers correctly (`<th>` scope).
- [ ] **SVG & Icon Hiding**: Decorative icons have `aria-hidden="true"`, preventing redundant announcements.

**Result / Notes**:
```
[ ] PENDING EVALUATION
Tester:
Date:
Notes:
```

