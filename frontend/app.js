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
  if (btn) {
    btn.querySelector('.theme-icon').textContent = theme === 'light' ? '☀️' : '🌙';
    btn.querySelector('.theme-label').textContent = theme === 'light' ? 'Light' : 'Dark';
  }
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
    await renderAll(data);
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

/* ===== KPI CARDS ===== */
function makeGauge(canvasId, value, total, accentColor, isEmpty = false) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  const borderColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--border').trim() || '#30363d';
  const data = isEmpty
    ? { datasets: [{ data: [1], backgroundColor: [borderColor], borderWidth: 0 }] }
    : { datasets: [{ data: [value, Math.max(0, total - value)], backgroundColor: [accentColor, 'rgba(255,255,255,0.05)'], borderWidth: 0, borderRadius: 3 }] };

  return new Chart(ctx, {
    type: 'doughnut',
    data,
    options: {
      cutout: '72%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 800, easing: 'easeInOutQuart' },
    },
  });
}

function renderKPI(stats) {
  const {
    total_exposed_services: exposed = 0,
    total_critical_vulns:   vulns   = 0,
    total_threat_activity:  threats = 0,
    malicious_domains:      malware = 0,
    suspicious_domains:     susp    = 0,
  } = stats;

  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  document.getElementById('num-exposed').textContent = fmt(exposed);
  makeGauge('gauge-exposed', 72, 100, css('--accent-green'));

  document.getElementById('num-vulns').textContent = fmt(vulns);
  makeGauge('gauge-vulns', 60, 100, css('--accent-red'));

  document.getElementById('num-threats').textContent = fmt(threats);
  makeGauge('gauge-threats', 50, 100, css('--accent-amber'));

  document.getElementById('num-malware').textContent = fmt(malware);
  if (malware === 0) {
    makeGauge('gauge-malware', 0, 100, '', true);
    document.getElementById('nodata-malware').classList.remove('hidden');
  } else {
    const malPct = (malware / (malware + susp)) * 100;
    makeGauge('gauge-malware', malPct, 100, css('--accent-purple'));
  }
}

function renderApiStatus(status) {}
function renderTable(countries) {}
function renderCharts(countries, orgs) {}
/* ===== WORLD MAP ===== */
function getRiskTier(threatActivity) {
  if (threatActivity == null) return null;
  if (threatActivity >= 2000) return 'critical';
  if (threatActivity >= 1000) return 'high';
  if (threatActivity >= 1)    return 'medium';
  return 'low';
}

async function renderMap(countries) {
  const map = L.map('world-map', { zoomControl: true, scrollWheelZoom: false })
    .setView([20, 0], 2);
  window._leafletMap = map;

  window._tileLayer = L.tileLayer(
    currentTheme === 'dark' ? TILE_DARK : TILE_LIGHT,
    { attribution: TILE_ATTR, maxZoom: 6 }
  ).addTo(map);

  // Map legend
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
      const fill = tier ? CHOROPLETH_COLORS[tier] : neutral;
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
          <span style="color:#8b949e;font-size:0.75rem">
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
