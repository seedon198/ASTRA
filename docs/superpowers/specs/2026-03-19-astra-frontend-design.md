# ASTRA Frontend Dashboard — Design Spec

**Date:** 2026-03-19
**Status:** Approved
**Repo:** seedon198/ASTRA

---

## Overview

Build a polished, production-quality web dashboard for ASTRA (Attack Surface Trend & Risk Analytics) that visualises `data/latest.json` — the live threat intelligence dataset updated every 6 hours by GitHub Actions. The current `frontend/` directory contains three empty files; this spec defines what goes in them.

The dashboard is served as a static GitHub Pages site directly from the `frontend/` folder. No build step. No backend.

---

## Architecture

### Files

```
frontend/
├── index.html   — HTML structure, CDN script/link tags, semantic layout
├── app.js       — all data fetching and rendering logic
└── styles.css   — all styles, CSS custom properties for theming
```

### Data Flow

1. On `DOMContentLoaded`, show loading spinner overlay
2. `fetch(DATA_URL)` where `const DATA_URL = 'https://raw.githubusercontent.com/seedon198/ASTRA/main/data/latest.json'` — defined at the top of `app.js`
3. On success: hide spinner, parse JSON, populate all widgets
4. On failure: hide spinner, show full-page error banner with the error message

> **Why raw GitHub URL:** When GitHub Pages serves from the `frontend/` subfolder, relative paths like `../data/` resolve outside the served scope and 404. Using the raw content URL bypasses this entirely and also means the dashboard works when opened locally as a file.

### Libraries (CDN only, no install)

| Library | Version | CDN URL pattern |
|---------|---------|----------------|
| Chart.js | 4.x | `cdn.jsdelivr.net/npm/chart.js` |
| Leaflet | 1.9.x | `cdn.jsdelivr.net/npm/leaflet` |
| World GeoJSON | — | `https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson` |

#### Leaflet Tile Layers

Two tile sets are required — one per theme. Both are from CartoDB (no API key needed):

| Theme | URL | Style |
|-------|-----|-------|
| Dark | `https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png` | Dark Matter (no labels) |
| Light | `https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png` | Positron (no labels) |

Attribution for both: `© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>`

"No labels" variants are used so country labels from the tile layer don't clash with the tooltip overlays. On theme toggle, remove the current tile layer and add the new one.

**GeoJSON property key:** `ISO_A2` — the two-letter ISO country code used to join against `data.countries` object keys (e.g. `"US"`, `"DE"`). Countries where `ISO_A2` is `"-99"` (disputed territories) are rendered in neutral grey with no tooltip.

> **Note on TW / HK:** Taiwan (`TW`) and Hong Kong (`HK`) appear in `data.countries` but the GeoJSON source may encode them with `ISO_A2 === "-99"` due to political convention. If this occurs they will render neutral grey (the absent-country fallback) — this is acceptable behaviour and requires no special-casing.

---

## Layout & Components

### 1. Header Bar (full width)
- Left: `ASTRA` wordmark + "Global Attack Surface Tracker" subtitle
- Centre: last-updated pill — display `data.last_updated` (the human-readable string field, e.g. `"2026-03-18 17:48:31 UTC"`)
- Right: dark/light mode toggle button (moon/sun icon + label)

### 2. KPI Cards (4-column grid, reads from `data.global_stats`)

All four KPI values come exclusively from `global_stats` — never re-aggregated from the countries array.

| Card | Field | Gauge fill strategy | Colour |
|------|-------|-------------------|--------|
| Exposed Services | `total_exposed_services` | Decorative — always renders at 72% fill; the number is the focal point | Green `#00ff88` |
| Critical Vulns | `total_critical_vulns` | % of exposed services: `critical_vulns / exposed_services × 100`, capped at 100 | Red `#ff4444` |
| Active Threats | `total_threat_activity` | % of exposed services: `threat_activity / exposed_services × 100`, capped at 100 | Amber `#ffaa00` |
| Malicious Domains | `malicious_domains` | If value > 0: `value / (value + suspicious_domains) × 100`. If value === 0: use Chart.js dataset `[1]` with colour `--border` and `borderWidth: 0` as a sentinel to render a visible grey ring; overlay "No data" via an absolutely-positioned HTML element centred on the canvas | Purple `#a78bfa` |

Each card shows: large formatted number (via `Intl.NumberFormat`), metric label, and the doughnut gauge.

### 3. World Map (full width)
- Leaflet choropleth using the GeoJSON specified above
- Countries coloured by `threat_activity` using 4 fixed tiers:

| Tier | Threshold | Colour |
|------|-----------|--------|
| Low | `threat_activity === 0` | Dark teal `#0d4f4f` |
| Medium | `1 – 999` | Amber `#b8860b` |
| High | `1000 – 1999` | Orange `#cc5500` |
| Critical | `≥ 2000` | Bright red `#cc0000` |

- Countries in GeoJSON but absent from `data.countries`: neutral grey `#3a3f47` (dark) / `#cccccc` (light), no tooltip
- Hover tooltip: country name (from GeoJSON `name` property), exposed services, critical vulns, threat activity — all formatted with `Intl.NumberFormat`
- Map background matches the current theme's `--bg-primary`

### 4. Charts Row (two panels, side by side, 50/50)

**Left — Top 10 Countries by Exposed Services**
- Horizontal bar chart (Chart.js)
- Sort `data.countries` entries by `exposed_services` descending, take top 10
- X-axis: exposed_services; Y-axis: country code labels
- Bar colour: `--accent-green`

**Right — Organisations by Exposed Services**
- Horizontal bar chart (Chart.js)
- Sort `data.organizations` entries by `exposed_services` descending (all 5 shown)
- X-axis: exposed_services; Y-axis: org name labels
- Bar colour: `--accent-amber`
- Note: `threat_activity` is intentionally absent from org data — do not show it

### 5. Countries Table (full width)

- Renders all entries in `data.countries`
- **Default sort:** `exposed_services` descending
- **Columns:** Flag emoji · Country code · Exposed Services · Critical Vulns · Threat Activity · Risk badge
- **Sortable:** click any numeric column header to sort ascending/descending (toggle); "missing" means the key is absent or `null` in the JSON — those entries sort to the bottom. `0` is a valid value and sorts normally alongside other numbers.
- **Risk badge** — derived from `threat_activity` using the same thresholds as the choropleth:

| Badge label | Threshold | Background | Text |
|-------------|-----------|------------|------|
| LOW | `=== 0` | `#0d4f4f` | `#00ff88` |
| MEDIUM | `1 – 999` | `#3a2800` | `#ffaa00` |
| HIGH | `1000 – 1999` | `#3a1500` | `#ff8800` |
| CRITICAL | `≥ 2000` | `#2a0000` | `#ff4444` |

- Flag emoji sourced by converting country code to regional indicator Unicode: `String.fromCodePoint(...[...code].map(c => 0x1F1E6 + c.charCodeAt(0) - 65))`

### 6. API Status Bar (footer)

Reads from `data.api_status`. Possible values and visual treatment:

| Value | Dot colour | Label |
|-------|-----------|-------|
| `"active"` | Green `#00ff88` | Active |
| `"inactive"` | Grey `#8b949e` | Inactive |
| `"error"` | Red `#ff4444` | Error |
| Any other / missing | Amber `#ffaa00` | Unknown |

Three entries always shown: Shodan · GreyNoise · VirusTotal.

---

## Theming

CSS custom properties on `:root` define dark mode (default). Adding `.light` class to `<body>` overrides to light mode.

**First-visit behaviour:** Check `localStorage.getItem('astra-theme')`. If `'light'`, apply `.light`. Otherwise (empty, `'dark'`, or any other value) render dark mode. No `prefers-color-scheme` media query — dark is always the default.

### Dark mode (default, `:root`)

```css
--bg-primary:     #0d1117;
--bg-card:        #161b22;
--border:         #30363d;
--text-primary:   #e6edf3;
--text-secondary: #8b949e;
--accent-green:   #00ff88;
--accent-red:     #ff4444;
--accent-amber:   #ffaa00;
--accent-purple:  #a78bfa;
--map-neutral:    #3a3f47;
```

### Light mode (`body.light`)

```css
--bg-primary:     #f6f8fa;
--bg-card:        #ffffff;
--border:         #d0d7de;
--text-primary:   #1f2328;
--text-secondary: #656d76;
--accent-green:   #1a7f37;
--accent-red:     #cf222e;
--accent-amber:   #9a6700;
--accent-purple:  #6639ba;
--map-neutral:    #cccccc;
```

On toggle: flip `.light` class on `<body>`, save value to `localStorage`, re-render Leaflet tile layer background colour.

### Typography
System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`) — no web font request.

---

## Loading & Error States

**Loading:** Full-page overlay with a spinner and "Loading threat intelligence data…" label. Shown immediately on `DOMContentLoaded`, hidden once data renders or error occurs.

**Error:** Full-page error banner (replaces spinner overlay) with icon, "Failed to load data" heading, and the raw error message in a `<code>` block.

---

## Deployment

- GitHub Pages source: `frontend/` folder on `main` branch
- No workflow changes needed — the existing data-fetch Action commits `data/latest.json` every 6 hours; the dashboard reads whatever is committed on load

---

## Out of Scope

- Auto-refresh / polling (page loads once, manual browser refresh to update)
- Historical trend charts (data not yet stored historically)
- Search/filter on the countries table
- Backend or server-side rendering
