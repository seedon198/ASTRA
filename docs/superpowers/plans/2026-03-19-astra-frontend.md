# ASTRA Frontend Dashboard Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, production-quality static HTML/CSS/JS threat intelligence dashboard for ASTRA that visualises `data/latest.json` via a world map, KPI gauges, bar charts, sortable table, and API status bar — with dark/light theme toggle.

**Architecture:** Three files in `frontend/` — `index.html` (structure + CDN imports), `styles.css` (CSS custom properties for theming, all component styles), `app.js` (all rendering logic in organised sections). Data fetched from GitHub raw URL on page load. No build step, served directly by GitHub Pages from the `frontend/` folder.

**Tech Stack:** Vanilla JS (ES2020), Chart.js 4.4.x (CDN), Leaflet 1.9.4 (CDN), CartoDB tile layers, datasets/geo-countries GeoJSON

---

## File Map

| File | Responsibility |
|------|---------------|
| `frontend/index.html` | HTML skeleton, semantic structure, CDN `<link>`/`<script>` tags, all component containers |
| `frontend/styles.css` | CSS custom properties (dark/light), reset, layout, all component styles |
| `frontend/app.js` | Constants, theme management, data fetch, KPI gauges, choropleth map, bar charts, countries table, API status bar, init |
| `.github/workflows/deploy-pages.yml` | GitHub Actions workflow that deploys `frontend/` to GitHub Pages on push to main |

`app.js` is built section by section across tasks. Each task appends a new section; never replaces earlier sections unless explicitly stated.

---

## Task 1: HTML Skeleton + CSS Foundation

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/styles.css`

- [ ] **Step 1.1 — Write `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ASTRA — Global Attack Surface Tracker</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>

  <!-- Loading overlay -->
  <div id="loading-overlay" class="loading-overlay">
    <div class="spinner"></div>
    <p>Loading threat intelligence data…</p>
  </div>

  <!-- Error banner -->
  <div id="error-banner" class="error-banner hidden">
    <div class="error-inner">
      <span class="error-icon">⚠</span>
      <h2>Failed to load data</h2>
      <code id="error-message"></code>
    </div>
  </div>

  <!-- Main app — hidden until data loads -->
  <div id="app" class="hidden">

    <!-- Header -->
    <header class="header">
      <div class="header-brand">
        <h1 class="wordmark">ASTRA</h1>
        <span class="subtitle">Global Attack Surface Tracker</span>
      </div>
      <div class="header-center">
        <span class="last-updated-pill">Updated: <span id="last-updated">—</span></span>
      </div>
      <div class="header-right">
        <button id="theme-toggle" class="theme-toggle" aria-label="Toggle theme">
          <span class="theme-icon">🌙</span>
          <span class="theme-label">Dark</span>
        </button>
      </div>
    </header>

    <!-- KPI Cards -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-chart-wrap">
          <canvas id="gauge-exposed"></canvas>
          <div class="kpi-number" id="num-exposed">—</div>
        </div>
        <div class="kpi-label">Exposed Services</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-chart-wrap">
          <canvas id="gauge-vulns"></canvas>
          <div class="kpi-number" id="num-vulns">—</div>
        </div>
        <div class="kpi-label">Critical Vulns</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-chart-wrap">
          <canvas id="gauge-threats"></canvas>
          <div class="kpi-number" id="num-threats">—</div>
        </div>
        <div class="kpi-label">Active Threats</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-chart-wrap">
          <canvas id="gauge-malware"></canvas>
          <div class="kpi-number" id="num-malware">—</div>
          <div class="kpi-no-data hidden" id="nodata-malware">No data</div>
        </div>
        <div class="kpi-label">Malicious Domains</div>
      </div>
    </section>

    <!-- World Map -->
    <section class="map-section">
      <h3 class="section-title">Global Threat Map</h3>
      <div id="world-map"></div>
    </section>

    <!-- Charts Row -->
    <section class="charts-row">
      <div class="chart-panel">
        <h3 class="chart-title">Top 10 Countries by Exposed Services</h3>
        <canvas id="chart-countries"></canvas>
      </div>
      <div class="chart-panel">
        <h3 class="chart-title">Organizations by Exposed Services</h3>
        <canvas id="chart-orgs"></canvas>
      </div>
    </section>

    <!-- Countries Table -->
    <section class="table-section">
      <h3 class="section-title">Global Coverage</h3>
      <div class="table-wrap">
        <table id="countries-table">
          <thead>
            <tr>
              <th>Flag</th>
              <th>Country</th>
              <th class="sortable" data-col="exposed_services">Exposed Services <span class="sort-icon">↕</span></th>
              <th class="sortable" data-col="critical_vulns">Critical Vulns <span class="sort-icon">↕</span></th>
              <th class="sortable" data-col="threat_activity">Threat Activity <span class="sort-icon">↕</span></th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody id="countries-tbody"></tbody>
        </table>
      </div>
    </section>

    <!-- API Status Footer -->
    <footer class="api-status-bar">
      <span class="api-status-label">Data Sources:</span>
      <span class="api-status-item" id="status-shodan">
        <span class="status-dot"></span>Shodan
      </span>
      <span class="api-status-item" id="status-greynoise">
        <span class="status-dot"></span>GreyNoise
      </span>
      <span class="api-status-item" id="status-virustotal">
        <span class="status-dot"></span>VirusTotal
      </span>
    </footer>

  </div><!-- /#app -->

  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 1.2 — Write `frontend/styles.css`**

```css
/* ===== CSS CUSTOM PROPERTIES ===== */
:root {
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
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body.light {
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
}

/* ===== RESET ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font);
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background 0.2s, color 0.2s;
  min-height: 100vh;
}
a { color: var(--accent-green); }

/* ===== UTILITIES ===== */
.hidden { display: none !important; }

/* ===== LOADING OVERLAY ===== */
.loading-overlay {
  position: fixed; inset: 0;
  background: var(--bg-primary);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 1.5rem; z-index: 9999;
  color: var(--text-secondary);
}
.spinner {
  width: 48px; height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--accent-green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== ERROR BANNER ===== */
.error-banner {
  position: fixed; inset: 0;
  background: var(--bg-primary);
  display: flex; align-items: center; justify-content: center;
  z-index: 9998;
}
.error-inner {
  text-align: center; max-width: 560px; padding: 2rem;
}
.error-icon { font-size: 3rem; }
.error-inner h2 { margin: 1rem 0 0.5rem; color: var(--accent-red); }
.error-inner code {
  display: block; margin-top: 1rem; padding: 1rem;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 6px; font-size: 0.85rem; word-break: break-all;
  color: var(--text-secondary);
}

/* ===== HEADER ===== */
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
}
.header-brand { display: flex; align-items: baseline; gap: 0.75rem; }
.wordmark {
  font-size: 1.5rem; font-weight: 700; letter-spacing: 0.05em;
  color: var(--accent-green);
}
.subtitle { font-size: 0.8rem; color: var(--text-secondary); }
.last-updated-pill {
  font-size: 0.75rem; color: var(--text-secondary);
  background: var(--bg-primary); border: 1px solid var(--border);
  padding: 0.25rem 0.75rem; border-radius: 999px;
}
.theme-toggle {
  display: flex; align-items: center; gap: 0.4rem;
  background: var(--bg-primary); border: 1px solid var(--border);
  color: var(--text-primary); cursor: pointer; font-size: 0.85rem;
  padding: 0.4rem 0.9rem; border-radius: 6px;
  transition: border-color 0.2s;
}
.theme-toggle:hover { border-color: var(--accent-green); }

/* ===== KPI GRID ===== */
.kpi-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1rem; padding: 1.5rem 2rem;
}
@media (max-width: 900px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
.kpi-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; padding: 1.25rem;
  display: flex; flex-direction: column; align-items: center; gap: 0.75rem;
}
.kpi-chart-wrap {
  position: relative; width: 140px; height: 140px;
  display: flex; align-items: center; justify-content: center;
}
.kpi-chart-wrap canvas {
  position: absolute; inset: 0; width: 100% !important; height: 100% !important;
}
.kpi-number {
  position: relative; z-index: 1;
  font-size: 1.1rem; font-weight: 700;
  text-align: center; color: var(--text-primary);
  pointer-events: none;
}
.kpi-no-data {
  position: absolute; bottom: 24px; left: 0; right: 0;
  text-align: center; font-size: 0.7rem;
  color: var(--text-secondary); z-index: 2;
}
.kpi-label {
  font-size: 0.8rem; color: var(--text-secondary);
  text-align: center; text-transform: uppercase; letter-spacing: 0.05em;
}

/* ===== MAP ===== */
.map-section { padding: 0 2rem 1.5rem; }
.section-title {
  font-size: 0.9rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--text-secondary);
  margin-bottom: 0.75rem;
}
#world-map {
  height: 460px; border-radius: 10px;
  border: 1px solid var(--border); overflow: hidden;
}

/* ===== CHARTS ROW ===== */
.charts-row {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1rem; padding: 0 2rem 1.5rem;
}
@media (max-width: 900px) { .charts-row { grid-template-columns: 1fr; } }
.chart-panel {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; padding: 1.25rem;
}
.chart-title {
  font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 1rem;
}

/* ===== TABLE ===== */
.table-section { padding: 0 2rem 1.5rem; }
.table-wrap {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; overflow-x: auto;
}
#countries-table {
  width: 100%; border-collapse: collapse; font-size: 0.85rem;
}
#countries-table th {
  padding: 0.75rem 1rem; text-align: left;
  background: var(--bg-primary); color: var(--text-secondary);
  font-weight: 600; font-size: 0.75rem; text-transform: uppercase;
  letter-spacing: 0.04em; border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
#countries-table th.sortable { cursor: pointer; user-select: none; }
#countries-table th.sortable:hover { color: var(--text-primary); }
#countries-table th.sort-asc .sort-icon::after { content: ' ↑'; }
#countries-table th.sort-desc .sort-icon::after { content: ' ↓'; }
#countries-table td {
  padding: 0.6rem 1rem; border-bottom: 1px solid var(--border);
  color: var(--text-primary);
}
#countries-table tr:last-child td { border-bottom: none; }
#countries-table tr:hover td { background: var(--bg-primary); }
.risk-badge {
  display: inline-block; padding: 0.2rem 0.6rem;
  border-radius: 4px; font-size: 0.7rem; font-weight: 700;
  letter-spacing: 0.05em;
}

/* ===== API STATUS BAR ===== */
.api-status-bar {
  display: flex; align-items: center; gap: 1.5rem;
  padding: 0.75rem 2rem; border-top: 1px solid var(--border);
  background: var(--bg-card); font-size: 0.8rem;
  color: var(--text-secondary);
}
.api-status-item {
  display: flex; align-items: center; gap: 0.4rem;
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--text-secondary);
  display: inline-block;
}

/* ===== LEAFLET OVERRIDES ===== */
.leaflet-container { background: var(--bg-primary) !important; }
.leaflet-popup-content-wrapper, .leaflet-popup-tip {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.leaflet-popup-content { margin: 0.75rem 1rem; }
.leaflet-control-attribution {
  background: var(--bg-card) !important;
  color: var(--text-secondary) !important;
  font-size: 0.65rem;
}
.leaflet-control-zoom a {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border-color: var(--border) !important;
}
```

- [ ] **Step 1.3 — Verify structure in browser**

Open `frontend/index.html` directly in a browser (drag-and-drop or `open frontend/index.html`). The page should show the loading spinner on a dark background. No content yet — that's correct. The spinner should be rotating.

- [ ] **Step 1.4 — Commit**

```bash
cd /Users/user/Documents/code/Github/ASTRA
git add frontend/
git commit -m "feat: HTML skeleton and CSS foundation for ASTRA dashboard"
git push
```

---

## Task 2: App.js — Constants, Theme, Data Fetch

**Files:**
- Create: `frontend/app.js`

- [ ] **Step 2.1 — Write `frontend/app.js` (initial sections)**

```js
/* ===== CONSTANTS ===== */
const DATA_URL = 'https://raw.githubusercontent.com/seedon198/ASTRA/main/data/latest.json';
const GEOJSON_URL = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson';
const TILE_DARK  = 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png';
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png';
const TILE_ATTR  = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

const RISK_TIERS = [
  { min: 2000, max: Infinity, label: 'CRITICAL', bg: '#2a0000', color: '#ff4444' },
  { min: 1000, max: 1999,     label: 'HIGH',     bg: '#3a1500', color: '#ff8800' },
  { min: 1,    max: 999,      label: 'MEDIUM',   bg: '#3a2800', color: '#ffaa00' },
  { min: 0,    max: 0,        label: 'LOW',      bg: '#0d4f4f', color: '#00ff88' },
];

const CHOROPLETH_COLORS = {
  critical: '#cc0000',
  high:     '#cc5500',
  medium:   '#b8860b',
  low:      '#0d4f4f',
};

const fmt = (n) => new Intl.NumberFormat().format(n);

/* ===== THEME MANAGEMENT ===== */
let currentTheme = localStorage.getItem('astra-theme') === 'light' ? 'light' : 'dark';

function applyTheme(theme) {
  currentTheme = theme;
  document.body.classList.toggle('light', theme === 'light');
  const btn = document.getElementById('theme-toggle');
  btn.querySelector('.theme-icon').textContent = theme === 'light' ? '☀️' : '🌙';
  btn.querySelector('.theme-label').textContent = theme === 'light' ? 'Light' : 'Dark';
  localStorage.setItem('astra-theme', theme);
  if (window._leafletMap) swapTileLayer(theme);
}

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(currentTheme);
  document.getElementById('theme-toggle').addEventListener('click', () => {
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });
  loadData();
});

/* ===== DATA FETCH ===== */
async function loadData() {
  try {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status} — ${res.statusText}`);
    const data = await res.json();
    renderAll(data);
    document.getElementById('loading-overlay').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
  } catch (err) {
    document.getElementById('loading-overlay').classList.add('hidden');
    document.getElementById('error-message').textContent = err.message;
    document.getElementById('error-banner').classList.remove('hidden');
  }
}

async function renderAll(data) {
  document.getElementById('last-updated').textContent = data.last_updated || '—';
  renderKPI(data.global_stats);
  renderApiStatus(data.api_status || {});
  renderTable(data.countries || {});
  renderCharts(data.countries || {}, data.organizations || {});
  await renderMap(data.countries || {});
}
```

- [ ] **Step 2.2 — Add stub functions so no errors throw on load**

Append to `app.js`:

```js
/* ===== STUBS (replaced in later tasks) ===== */
function renderKPI(stats) {}
function renderApiStatus(status) {}
function renderTable(countries) {}
function renderCharts(countries, orgs) {}
async function renderMap(countries) {}
function swapTileLayer(theme) {}
```

- [ ] **Step 2.3 — Verify in browser**

Open `frontend/index.html`. The spinner should appear briefly then the main app layout should appear (empty sections with correct dark background and header). The theme toggle button should switch between dark and light. Open browser console — no errors should appear. If fetch fails (CORS when opening as file), that's expected — the app should show the error banner instead.

> **Local testing note:** The raw GitHub URL requires a network request. To test locally without CORS issues, run a simple server: `python3 -m http.server 8080 --directory .` from the ASTRA repo root, then open `http://localhost:8080/frontend/`.

- [ ] **Step 2.4 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: app.js foundation — constants, theme toggle, data fetch"
git push
```

---

## Task 3: KPI Cards with Doughnut Gauges

**Files:**
- Modify: `frontend/app.js` — replace `renderKPI` stub

- [ ] **Step 3.1 — Replace `renderKPI` stub in `app.js`**

Find and replace the line `function renderKPI(stats) {}` with:

```js
/* ===== KPI CARDS ===== */
function makeGauge(canvasId, value, total, accentColor, isEmpty = false) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  const data = isEmpty
    ? { datasets: [{ data: [1], backgroundColor: [getComputedStyle(document.body).getPropertyValue('--border').trim() || '#30363d'], borderWidth: 0 }] }
    : { datasets: [{ data: [value, Math.max(0, total - value)], backgroundColor: [accentColor, 'rgba(255,255,255,0.05)'], borderWidth: 0, borderRadius: 3 }] };

  return new Chart(ctx, {
    type: 'doughnut',
    data,
    options: {
      cutout: '72%',
      rotation: -90,
      circumference: 360,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 800, easing: 'easeInOutQuart' },
    },
  });
}

// NOTE: All KPI gauges use decorative fills — the gauge is a visual accent,
// the number is the data. Ratio-based fills were rejected because
// critical_vulns/exposed_services ≈ 0.013%, producing invisible arcs.
function renderKPI(stats) {
  const {
    total_exposed_services: exposed = 0,
    total_critical_vulns:   vulns   = 0,
    total_threat_activity:  threats = 0,
    malicious_domains:      malware = 0,
    suspicious_domains:     susp    = 0,
  } = stats;

  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  // Exposed services — decorative 72%
  document.getElementById('num-exposed').textContent = fmt(exposed);
  makeGauge('gauge-exposed', 72, 100, css('--accent-green'));

  // Critical vulns — decorative 60%
  document.getElementById('num-vulns').textContent = fmt(vulns);
  makeGauge('gauge-vulns', 60, 100, css('--accent-red'));

  // Active threats — decorative 50%
  document.getElementById('num-threats').textContent = fmt(threats);
  makeGauge('gauge-threats', 50, 100, css('--accent-amber'));

  // Malicious domains — ratio if data exists, empty sentinel if zero
  document.getElementById('num-malware').textContent = fmt(malware);
  if (malware === 0) {
    makeGauge('gauge-malware', 0, 100, '', true);
    document.getElementById('nodata-malware').classList.remove('hidden');
  } else {
    const malPct = (malware / (malware + susp)) * 100;
    makeGauge('gauge-malware', malPct, 100, css('--accent-purple'));
  }
}
```

- [ ] **Step 3.2 — Verify KPI cards**

Reload `http://localhost:8080/frontend/`. Four cards should now show animated doughnut gauges with large numbers. The malicious domains card should show "No data" under the empty grey ring. Numbers should be formatted with commas.

- [ ] **Step 3.3 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: KPI cards with Chart.js doughnut gauges"
git push
```

---

## Task 4: World Map (Leaflet Choropleth)

**Files:**
- Modify: `frontend/app.js` — replace `renderMap` and `swapTileLayer` stubs

- [ ] **Step 4.1 — Add risk tier helper above renderMap**

Find and replace the line `async function renderMap(countries) {}` with:

```js
/* ===== WORLD MAP ===== */
function getRiskTier(threatActivity) {
  if (threatActivity == null) return null;
  if (threatActivity >= 2000) return 'critical';
  if (threatActivity >= 1000) return 'high';
  if (threatActivity >= 1)    return 'medium';
  return 'low';
}

function getChoroplethColor(tier) {
  return CHOROPLETH_COLORS[tier] || null;
}

async function renderMap(countries) {
  const map = L.map('world-map', { zoomControl: true, scrollWheelZoom: false })
    .setView([20, 0], 2);
  window._leafletMap = map;

  // Initial tile layer
  window._tileLayer = L.tileLayer(
    currentTheme === 'dark' ? TILE_DARK : TILE_LIGHT,
    { attribution: TILE_ATTR, maxZoom: 6 }
  ).addTo(map);

  // Fetch GeoJSON
  let geoData;
  try {
    const res = await fetch(GEOJSON_URL);
    geoData = await res.json();
  } catch (e) {
    console.warn('GeoJSON failed to load:', e);
    return;
  }

  const neutral = getComputedStyle(document.body)
    .getPropertyValue('--map-neutral').trim() || '#3a3f47';

  L.geoJSON(geoData, {
    style(feature) {
      const iso = feature.properties['ISO3166-1-Alpha-2'];
      if (iso === '-99' || !countries[iso]) {
        return { fillColor: neutral, weight: 0.5, color: '#555', fillOpacity: 0.6 };
      }
      const tier = getRiskTier(countries[iso].threat_activity);
      const fill = getChoroplethColor(tier) || neutral;
      return { fillColor: fill, weight: 0.5, color: '#222', fillOpacity: 0.8 };
    },
    onEachFeature(feature, layer) {
      const iso = feature.properties['ISO3166-1-Alpha-2'];
      const name = feature.properties.name || iso;
      const d = countries[iso];
      if (!d) return;
      layer.bindTooltip(
        `<div style="min-width:160px">
          <strong>${name}</strong><br/>
          <span style="color:var(--text-secondary);font-size:0.75rem">
            Exposed: ${fmt(d.exposed_services)}<br/>
            Critical Vulns: ${fmt(d.critical_vulns)}<br/>
            Threat Activity: ${fmt(d.threat_activity)}
          </span>
        </div>`,
        { sticky: true, opacity: 0.97 }
      );
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2, color: '#fff', fillOpacity: 1 }); },
        mouseout(e)  { e.target.setStyle({ weight: 0.5, color: '#222', fillOpacity: 0.8 }); },
      });
    },
  }).addTo(map);
}

function swapTileLayer(theme) {
  if (!window._leafletMap || !window._tileLayer) return;
  window._leafletMap.removeLayer(window._tileLayer);
  window._tileLayer = L.tileLayer(
    theme === 'dark' ? TILE_DARK : TILE_LIGHT,
    { attribution: TILE_ATTR, maxZoom: 6 }
  ).addTo(window._leafletMap);
}
```

- [ ] **Step 4.2 — Verify map**

Reload the page. The world map should appear with countries coloured by threat tier (most countries dark teal, high-threat-activity countries orange/red). Hovering a country should show a tooltip. Toggling the theme should swap the map background tile layer.

- [ ] **Step 4.3 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: Leaflet choropleth world map with threat-tier colouring"
git push
```

---

## Task 5: Bar Charts

**Files:**
- Modify: `frontend/app.js` — replace `renderCharts` stub

- [ ] **Step 5.1 — Replace `renderCharts` stub**

Find and replace `function renderCharts(countries, orgs) {}` with:

```js
/* ===== BAR CHARTS ===== */
function renderCharts(countries, orgs) {
  const isDark = currentTheme === 'dark';
  const gridColor = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)';
  const tickColor = isDark ? '#8b949e' : '#656d76';

  const sharedOptions = (labelCallback) => ({
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: { label: (ctx) => ` ${fmt(ctx.raw)}` },
      },
    },
    scales: {
      x: {
        grid: { color: gridColor },
        ticks: { color: tickColor, callback: (v) => fmt(v) },
      },
      y: {
        grid: { display: false },
        ticks: { color: isDark ? '#e6edf3' : '#1f2328', font: { size: 12 } },
      },
    },
  });

  // Countries chart — top 10 by exposed_services
  const topCountries = Object.entries(countries)
    .filter(([, d]) => d.exposed_services != null)
    .sort(([, a], [, b]) => b.exposed_services - a.exposed_services)
    .slice(0, 10);

  new Chart(document.getElementById('chart-countries').getContext('2d'), {
    type: 'bar',
    data: {
      labels: topCountries.map(([code]) => code),
      datasets: [{
        data: topCountries.map(([, d]) => d.exposed_services),
        backgroundColor: isDark ? '#00ff8880' : '#1a7f3780',
        borderColor:     isDark ? '#00ff88'   : '#1a7f37',
        borderWidth: 1, borderRadius: 3,
      }],
    },
    options: sharedOptions(),
  });

  // Orgs chart — all orgs by exposed_services
  const sortedOrgs = Object.entries(orgs)
    .filter(([, d]) => d.exposed_services != null)
    .sort(([, a], [, b]) => b.exposed_services - a.exposed_services);

  new Chart(document.getElementById('chart-orgs').getContext('2d'), {
    type: 'bar',
    data: {
      labels: sortedOrgs.map(([name]) => name),
      datasets: [{
        data: sortedOrgs.map(([, d]) => d.exposed_services),
        backgroundColor: isDark ? '#ffaa0080' : '#9a670080',
        borderColor:     isDark ? '#ffaa00'   : '#9a6700',
        borderWidth: 1, borderRadius: 3,
      }],
    },
    options: sharedOptions(),
  });
}
```

- [ ] **Step 5.2 — Verify charts**

Reload. Two side-by-side horizontal bar charts should appear — top 10 countries on the left, 5 organisations on the right. Bars should be green-tinted (countries) and amber-tinted (orgs). Numbers on the x-axis should be comma-formatted.

- [ ] **Step 5.3 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: top-10 countries and organisations bar charts"
git push
```

---

## Task 6: Countries Table with Sort

**Files:**
- Modify: `frontend/app.js` — replace `renderTable` stub

- [ ] **Step 6.1 — Replace `renderTable` stub**

Find and replace `function renderTable(countries) {}` with:

```js
/* ===== COUNTRIES TABLE ===== */
function getRiskBadge(threatActivity) {
  const tier = RISK_TIERS.find(t => threatActivity >= t.min && threatActivity <= t.max)
    || RISK_TIERS[RISK_TIERS.length - 1];
  return `<span class="risk-badge" style="background:${tier.bg};color:${tier.color}">${tier.label}</span>`;
}

function countryFlag(code) {
  try {
    return [...code.toUpperCase()].map(c =>
      String.fromCodePoint(0x1F1E6 + c.charCodeAt(0) - 65)
    ).join('');
  } catch { return '🏳'; }
}

let _tableData = [];
let _sortCol = 'exposed_services';
let _sortDir = 'desc';

function renderTable(countries) {
  _tableData = Object.entries(countries).map(([code, d]) => ({ code, ...d }));
  bindTableSort();
  drawTable();
}

function bindTableSort() {
  document.querySelectorAll('#countries-table th.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (_sortCol === col) {
        _sortDir = _sortDir === 'desc' ? 'asc' : 'desc';
      } else {
        _sortCol = col; _sortDir = 'desc';
      }
      document.querySelectorAll('#countries-table th.sortable').forEach(t => {
        t.classList.remove('sort-asc', 'sort-desc');
      });
      th.classList.add(_sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
      drawTable();
    });
  });
  // Set initial sort indicator
  const defaultTh = document.querySelector(`#countries-table th[data-col="${_sortCol}"]`);
  if (defaultTh) defaultTh.classList.add('sort-desc');
}

function drawTable() {
  const sorted = [..._tableData].sort((a, b) => {
    const av = a[_sortCol]; const bv = b[_sortCol];
    // null/undefined → sort to bottom regardless of direction
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    return _sortDir === 'asc' ? av - bv : bv - av;
  });

  const tbody = document.getElementById('countries-tbody');
  tbody.innerHTML = sorted.map(row => `
    <tr>
      <td>${countryFlag(row.code)}</td>
      <td><strong>${row.code}</strong></td>
      <td>${row.exposed_services != null ? fmt(row.exposed_services) : '—'}</td>
      <td>${row.critical_vulns   != null ? fmt(row.critical_vulns)   : '—'}</td>
      <td>${row.threat_activity  != null ? fmt(row.threat_activity)  : '—'}</td>
      <td>${getRiskBadge(row.threat_activity ?? 0)}</td>
    </tr>
  `).join('');
}
```

- [ ] **Step 6.2 — Verify table**

Reload. The table should show all ~50 countries, defaulting to descending `exposed_services` order. US should be first. Clicking column headers should sort ascending/descending. The `↕` icon should update to `↑` or `↓` on the active sort column. Risk badges should be colour-coded.

- [ ] **Step 6.3 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: sortable countries table with risk badges and flag emojis"
git push
```

---

## Task 7: API Status Bar

**Files:**
- Modify: `frontend/app.js` — replace `renderApiStatus` stub

- [ ] **Step 7.1 — Replace `renderApiStatus` stub**

Find and replace `function renderApiStatus(status) {}` with:

```js
/* ===== API STATUS BAR ===== */
const STATUS_COLORS = {
  active:   '#00ff88',
  inactive: '#8b949e',
  error:    '#ff4444',
};

function renderApiStatus(status) {
  [
    ['shodan',     'status-shodan'],
    ['greynoise',  'status-greynoise'],
    ['virustotal', 'status-virustotal'],
  ].forEach(([key, elId]) => {
    const el = document.getElementById(elId);
    if (!el) return;
    const val = (status[key] || 'unknown').toLowerCase();
    const color = STATUS_COLORS[val] || '#ffaa00';
    el.querySelector('.status-dot').style.background = color;
    const label = val.charAt(0).toUpperCase() + val.slice(1);
    el.childNodes[el.childNodes.length - 1].textContent = ` ${['shodan','greynoise','virustotal'].find((_, i) => ['status-shodan','status-greynoise','status-virustotal'][i] === elId) || key} — ${label}`;
  });
}
```

- [ ] **Step 7.2 — Simplify the label update (cleaner version)**

The above label code is messy. Replace the `renderApiStatus` function with this cleaner version:

```js
/* ===== API STATUS BAR ===== */
const STATUS_COLORS = {
  active:   '#00ff88',
  inactive: '#8b949e',
  error:    '#ff4444',
};

function renderApiStatus(status) {
  const sources = [
    { key: 'shodan',     elId: 'status-shodan',     label: 'Shodan'     },
    { key: 'greynoise',  elId: 'status-greynoise',  label: 'GreyNoise'  },
    { key: 'virustotal', elId: 'status-virustotal', label: 'VirusTotal' },
  ];
  sources.forEach(({ key, elId, label }) => {
    const el = document.getElementById(elId);
    if (!el) return;
    const val = (status[key] || 'unknown').toLowerCase();
    const color = STATUS_COLORS[val] || '#ffaa00';
    el.querySelector('.status-dot').style.background = color;
    el.lastChild.textContent = `\u00A0${label}`;
  });
}
```

- [ ] **Step 7.3 — Verify API status bar**

Reload. The footer should show three coloured dots — all green when all APIs are active. Manually change `"active"` to `"error"` in a test to verify the dot turns red (then revert).

- [ ] **Step 7.4 — Commit**

```bash
git add frontend/app.js
git commit -m "feat: API status bar with colour-coded source indicators"
git push
```

---

## Task 8: Polish + GitHub Pages Deploy Action

**Files:**
- Modify: `frontend/styles.css` — final polish tweaks
- Create: `.github/workflows/deploy-pages.yml` — deploy `frontend/` to GitHub Pages via Actions

> **Why an Action:** GitHub Pages branch-based deployment only supports `/` root or `/docs/` as the source folder — not `/frontend/`. A deploy Action publishes the `frontend/` directory to Pages without restructuring the repo.

- [ ] **Step 8.1 — Create `.github/workflows/deploy-pages.yml`**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - 'data/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: frontend/
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Then in GitHub repo settings (`Settings → Pages`), set Source to **"GitHub Actions"** (not a branch).

- [ ] **Step 8.2 — Add number size polish to KPI cards in `styles.css`**

Append to the end of `frontend/styles.css`:

```css
/* ===== POLISH ===== */
/* Responsive number size in KPI cards */
@media (max-width: 1200px) { .kpi-number { font-size: 0.95rem; } }
@media (max-width: 900px)  { .kpi-number { font-size: 0.85rem; } }

/* Table numbers right-aligned */
#countries-table td:nth-child(3),
#countries-table td:nth-child(4),
#countries-table td:nth-child(5) { text-align: right; font-variant-numeric: tabular-nums; }
#countries-table th:nth-child(3),
#countries-table th:nth-child(4),
#countries-table th:nth-child(5) { text-align: right; }

/* Smooth transitions on theme switch */
.kpi-card, .chart-panel, .table-wrap, .api-status-bar, .header {
  transition: background 0.2s, border-color 0.2s;
}

/* Map legend */
.map-legend {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px; padding: 0.5rem 0.75rem;
  font-size: 0.72rem; color: var(--text-secondary);
  line-height: 1.8;
}
.legend-row { display: flex; align-items: center; gap: 0.5rem; }
.legend-swatch {
  width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0;
}
```

- [ ] **Step 8.3 — Add map legend to `renderMap` in `app.js`**

Inside the `renderMap` function, after `window._tileLayer = L.tileLayer(...).addTo(map);`, add:

```js
  // Legend
  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = () => {
    const div = L.DomUtil.create('div', 'map-legend');
    div.innerHTML = `
      <div class="legend-row"><span class="legend-swatch" style="background:#cc0000"></span>Critical (≥2000)</div>
      <div class="legend-row"><span class="legend-swatch" style="background:#cc5500"></span>High (1000–1999)</div>
      <div class="legend-row"><span class="legend-swatch" style="background:#b8860b"></span>Medium (1–999)</div>
      <div class="legend-row"><span class="legend-swatch" style="background:#0d4f4f"></span>Low (0)</div>
    `;
    return div;
  };
  legend.addTo(map);
```

- [ ] **Step 8.4 — Enable GitHub Pages via Actions in repo settings**

Go to: `https://github.com/seedon198/ASTRA/settings/pages`
Set Source → **GitHub Actions** → Save. (The deploy workflow created in Step 8.1 handles the rest.)

- [ ] **Step 8.5 — Final visual check**

Open locally at `http://localhost:8080/frontend/`. Verify:
- [ ] Spinner shows → data loads → spinner disappears
- [ ] Dark mode default, theme toggle switches to light and back
- [ ] 4 KPI gauges animate in with formatted numbers
- [ ] World map shows choropleth colours + legend
- [ ] Hovering a country shows tooltip
- [ ] Swapping theme swaps the tile layer
- [ ] Both bar charts render correctly
- [ ] Table defaults to exposed_services desc, sorting works on all columns
- [ ] Risk badges are colour-coded
- [ ] API status dots are all green
- [ ] Mobile: at 900px the KPI grid becomes 2-col

- [ ] **Step 8.6 — Final commit**

```bash
cd /Users/user/Documents/code/Github/ASTRA
git add frontend/
git commit -m "feat: polish, map legend, GitHub Pages deploy action"
git push
```

---

## Verification Checklist

After all tasks complete, do a full end-to-end pass:

- [ ] Page loads from live GitHub Pages URL: `https://seedon198.github.io/ASTRA/`
- [ ] Data is real (numbers match `data/latest.json`)
- [ ] All 8 UI sections render without console errors
- [ ] Theme toggle persists across page reload (test in private window too)
- [ ] No `undefined` or `NaN` values visible anywhere
- [ ] Choropleth countries match their threat_activity tier
