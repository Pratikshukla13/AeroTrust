# AeroTrust Axe-Core Full Accessibility Audit Report (Phase 8.1)

> **Audit Scope**: All standard routes in static demo mode across Desktop (1366x768) and Mobile (390x844).
> **Severity Breakdown**: Critical: **0**, Serious: **0**, Moderate: **12**, Minor: **6** (Total: **18**).

| Route | Rule ID | Impact | Affected Elements | Description | Selector |
|:---|:---|:---:|:---:|:---|:---|
| `overview` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside` |
| `overview` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `overview` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
| `map` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside` |
| `map` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `map` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
| `flight-detail` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside` |
| `flight-detail` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `flight-detail` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
| `sar` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside` |
| `sar` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `sar` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
| `limitations` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside` |
| `limitations` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `limitations` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
| `incident-clock` | `aria-allowed-role` | **minor** | 1 | Ensure role attribute has an appropriate value for the element | `aside[role="alert"]` |
| `incident-clock` | `page-has-heading-one` | **moderate** | 1 | Ensure that the page, or at least one of its frames contains a level-one heading | `html` |
| `incident-clock` | `region` | **moderate** | 5 | Ensure all page content is contained by landmarks | `div[data-testid="dataset-fingerprint-bar"] > div > div:nth-child(1) > span` |
