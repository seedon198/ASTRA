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

1. On `DOMContentLoaded`, `fetch('../data/latest.json')` (relative path works locally and on GitHub Pages)
2. Parse JSON response
3. Populate all widgets: KPI cards, choropleth map, bar charts, countries table, API status bar
4. Display `last_updated` timestamp from JSON in the header

### Libraries (CDN only, no install)

| Library | Version | Purpose |
|---------|---------|---------|
| Chart.js | 4.x | Doughnut gauge charts on KPI cards; horizontal bar charts |
| Leaflet | 1.9.x | Interactive choropleth world map |
| World GeoJSON | — | Country boundary polygons for Leaflet (CDN-hosted) |

---

## Layout & Components

### 1. Header Bar (full width)
- Left: `ASTRA` wordmark + "Global Attack Surface Tracker" subtitle
- Centre: last-updated pill showing `data.last_updated`
- Right: dark/light mode toggle button (icon + label)

### 2. KPI Cards (4-column grid)

| Card | Data field | Gauge colour |
|------|-----------|-------------|
| Exposed Services | `global_stats.total_exposed_services` | Green `#00ff88` |
| Critical Vulns | `global_stats.total_critical_vulns` | Red `#ff4444` |
| Active Threats | `global_stats.total_threat_activity` | Amber `#ffaa00` |
| Malicious Domains | `global_stats.malicious_domains` | Purple `#a78bfa` |

Each card: large formatted number, label, Chart.js doughnut used as a gauge (value expressed as % of a sensible max).

### 3. World Map (full width)
- Leaflet choropleth; countries coloured in 4 tiers by composite risk score (threat_activity weighted + exposed_services normalised)
- 4-colour scale: dark teal (low) → amber → orange → bright red (high)
- Hover tooltip: country name, exposed services, critical vulns, threat activity
- Countries not in the dataset rendered in neutral grey

### 4. Charts Row (two panels, side by side)
- **Left:** Horizontal bar chart — top 10 countries by `exposed_services`
- **Right:** Horizontal bar chart — all 5 organisations by `exposed_services`
- Both use Chart.js, accent colour matching the green/red theme

### 5. Countries Table (full width)
- All ~50 countries from `data.countries`
- Columns: Flag emoji · Country code · Exposed Services · Critical Vulns · Threat Activity · Risk badge
- Sortable by any numeric column (click header)
- Risk badge: colour-coded pill (Low / Medium / High / Critical) derived from threat_activity threshold

### 6. API Status Bar (footer)
- Three inline status indicators: Shodan · GreyNoise · VirusTotal
- Dot colour: green if `api_status[source] === 'active'`, red otherwise
- Thin, unobtrusive — sits at the bottom of the page

---

## Theming

CSS custom properties on `:root` and `body.light` — toggling `.light` on `<body>` switches the entire UI.

### Dark mode (default)

```css
--bg-primary:    #0d1117;
--bg-card:       #161b22;
--border:        #30363d;
--text-primary:  #e6edf3;
--text-secondary:#8b949e;
--accent-green:  #00ff88;
--accent-red:    #ff4444;
--accent-amber:  #ffaa00;
--accent-purple: #a78bfa;
```

### Light mode

```css
--bg-primary:    #f6f8fa;
--bg-card:       #ffffff;
--border:        #d0d7de;
--text-primary:  #1f2328;
--text-secondary:#656d76;
/* accent colours same, slightly desaturated */
```

Theme preference persisted to `localStorage` and restored on load.

### Typography
System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`) — no web font request, faster load.

---

## Error Handling

- If `fetch` fails (e.g. offline, missing file): show a full-page error banner with the error message
- If a country in the GeoJSON has no data in `latest.json`: render it in neutral grey, no tooltip data
- All number formatting via `Intl.NumberFormat` for locale-aware comma separators

---

## Deployment

- GitHub Pages source: `frontend/` folder on `main` branch
- No workflow changes needed — the existing data-fetch Action already commits `data/latest.json` every 6 hours
- The frontend always reads the latest committed JSON on page load

---

## Out of Scope

- Auto-refresh / polling (page loads once)
- Historical trend charts (data not yet stored historically)
- Search/filter on the countries table (can be added later)
- Backend or server-side rendering
