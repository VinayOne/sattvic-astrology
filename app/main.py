from __future__ import annotations

import os
from datetime import date, time

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response

from app.astro import BirthDetails, calculate_chart
from app.pdf_report import build_pdf


_DEFAULT_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://sattvicgyaan.com",
    "https://www.sattvicgyaan.com",
]

_extra = os.environ.get("EXTRA_CORS_ORIGINS", "")
ALLOWED_ORIGINS = _DEFAULT_ORIGINS + [o.strip() for o in _extra.split(",") if o.strip()]

app = FastAPI(title="Sattvic Gyaan Astrology API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_FORM_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Free Vedic Astrology Report – Sattvic Gyaan</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #8B0000;
      --primary-dark: #6B0000;
      --accent: #CC0000;
      --accent-light: #fff0f0;
      --ink: #1a1a1a;
      --muted: #666666;
      --border: #e0e0e0;
      --bg: #ffffff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Open Sans', Arial, sans-serif;
      color: var(--ink);
      background: transparent;
    }
    main {
      width: min(960px, calc(100% - 24px));
      margin: 28px auto;
      display: grid;
      grid-template-columns: 1fr 1.25fr;
      gap: 28px;
      align-items: start;
    }
    .intro { padding: 20px 0; }
    h1 {
      margin: 0 0 12px;
      color: var(--primary);
      font-size: clamp(1.6rem, 4vw, 2.8rem);
      font-weight: 700;
      line-height: 1.15;
    }
    .tagline {
      margin: 0 0 16px;
      font-size: 1rem;
      line-height: 1.7;
      color: var(--muted);
    }
    .bullets {
      margin: 0;
      padding: 0 0 0 1.2em;
      font-size: .92rem;
      line-height: 1.9;
      color: var(--ink);
    }
    .bullets li::marker { color: var(--accent); }
    form {
      background: var(--bg);
      border: 1px solid var(--border);
      border-top: 5px solid var(--accent);
      border-radius: 4px;
      padding: 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
      display: grid;
      grid-template-columns: repeat(2, minmax(0,1fr));
      gap: 14px;
    }
    label {
      display: grid;
      gap: 5px;
      font-size: .85rem;
      font-weight: 600;
      color: #333;
      text-transform: uppercase;
      letter-spacing: .03em;
    }
    .wide { grid-column: 1 / -1; }
    input, select {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 3px;
      padding: 9px 11px;
      font: 1rem 'Open Sans', Arial, sans-serif;
      color: var(--ink);
      background: #fafafa;
      transition: border-color .15s;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--accent);
      background: #fff;
    }
    .place-wrap { position: relative; grid-column: 1 / -1; }
    #suggestions {
      position: absolute;
      top: 100%;
      left: 0; right: 0;
      background: white;
      border: 1px solid var(--border);
      border-top: none;
      border-radius: 0 0 3px 3px;
      z-index: 10;
      max-height: 200px;
      overflow-y: auto;
      box-shadow: 0 4px 8px rgba(0,0,0,.1);
    }
    #suggestions li {
      padding: 9px 12px;
      cursor: pointer;
      font-size: .9rem;
      list-style: none;
      border-bottom: 1px solid #f0f0f0;
    }
    #suggestions li:hover { background: var(--accent-light); color: var(--primary); }
    .coords-row {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 14px;
    }
    .coords-row label { grid-column: auto; }
    .hint { font-size: .76rem; color: var(--muted); font-weight: 400; margin-top: 2px; text-transform: none; letter-spacing: 0; }
    button[type=submit] {
      grid-column: 1 / -1;
      border: 0;
      border-radius: 3px;
      padding: 12px 16px;
      font: 700 .95rem 'Open Sans', Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: white;
      background: var(--accent);
      cursor: pointer;
      transition: background .15s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    button[type=submit]:hover:not(:disabled) { background: var(--primary); }
    button[type=submit]:disabled { opacity: .65; cursor: not-allowed; }
    .spinner {
      display: none;
      width: 18px; height: 18px;
      border: 3px solid rgba(255,255,255,.4);
      border-top-color: white;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .error-msg {
      grid-column: 1 / -1;
      background: #fff3f3;
      border: 1px solid #f5b5b5;
      border-radius: 6px;
      padding: 10px 14px;
      color: #8b1c1c;
      font-size: .92rem;
      display: none;
    }
    .download-card {
      grid-column: 1 / -1;
      display: none;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      background: var(--accent-light);
      border: 1.5px solid #f5b5b5;
      border-radius: 4px;
      padding: 18px 20px;
      text-align: center;
    }
    .download-card .ready-icon {
      font-size: 2rem;
      line-height: 1;
    }
    .download-card .ready-title {
      font-size: 1rem;
      font-weight: 700;
      color: var(--primary);
      margin: 0;
    }
    .download-card .ready-sub {
      font-size: .82rem;
      color: var(--muted);
      margin: 0;
      word-break: break-all;
    }
    .download-card .dl-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--primary);
      color: white;
      border: 0;
      border-radius: 3px;
      padding: 11px 24px;
      font: 700 .9rem 'Open Sans', Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: .05em;
      cursor: pointer;
      text-decoration: none;
      transition: background .15s;
    }
    .download-card .dl-btn:hover { background: var(--primary-dark); }
    .download-card .reset-link {
      font-size: .82rem;
      color: var(--muted);
      cursor: pointer;
      text-decoration: underline;
      background: none;
      border: none;
      padding: 0;
      font-family: 'Open Sans', Arial, sans-serif;
    }
    @media (max-width: 760px) {
      main { grid-template-columns: 1fr; margin-top: 16px; }
      form { grid-template-columns: 1fr; }
      .wide, .place-wrap { grid-column: auto; }
      .coords-row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <section class="intro">
      <h1>Free Vedic Astrology Report</h1>
      <p class="tagline">Receive a personalised Sattvic Gyaan PDF based on precise Nirayana Vedic calculations with Lahiri/Chitrapaksha ayanamsa.</p>
      <ul class="bullets">
        <li>Lagna, Rashi &amp; Janma Nakshatra</li>
        <li>All 9 planetary positions with house &amp; pada</li>
        <li>Tithi, Paksha, Yoga &amp; Karana (Panchang)</li>
        <li>Basic predictions across 6 life areas</li>
        <li>Instant PDF download, no account needed</li>
      </ul>
    </section>

    <form id="astro-form" novalidate>
      <label>Full Name
        <input name="name" placeholder="Your full name" required autocomplete="name">
      </label>
      <label>Gender
        <select name="gender">
          <option value="Not specified">Prefer not to say</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </label>
      <label>Date of Birth
        <input type="date" name="birth_date" required>
      </label>
      <label>Time of Birth
        <input type="time" name="birth_time" required>
        <span class="hint">Use local birth time</span>
      </label>

      <div class="place-wrap">
        <label style="display:grid;gap:5px;">Birth Place
          <input id="place-input" name="place" placeholder="City, Country  (type to search)" required autocomplete="off">
          <span class="hint">Start typing — select from suggestions to auto-fill coordinates</span>
        </label>
        <ul id="suggestions" style="display:none;margin:0;padding:0;"></ul>
      </div>

      <div class="coords-row">
        <label>Latitude
          <input type="number" step="0.0001" name="latitude" id="lat" placeholder="e.g. 22.8000" required>
        </label>
        <label>Longitude
          <input type="number" step="0.0001" name="longitude" id="lng" placeholder="e.g. 86.1667" required>
        </label>
        <label>Timezone (UTC offset)
          <input type="number" step="0.25" name="timezone_offset" id="tz" placeholder="e.g. 5.5" required>
          <span class="hint">e.g. India = 5.5, UK = 0 or 1</span>
        </label>
      </div>

      <div class="error-msg" id="error-msg"></div>

      <button type="submit" id="submit-btn">
        <span class="spinner" id="spinner"></span>
        <span id="btn-text">Generate PDF Report</span>
      </button>

      <div class="download-card" id="download-card">
        <div class="ready-icon">✦</div>
        <p class="ready-title">Your report is ready!</p>
        <p class="ready-sub" id="ready-filename"></p>
        <a class="dl-btn" id="dl-btn" href="#" download>
          ↓ &nbsp;Download PDF
        </a>
        <button class="reset-link" id="reset-link">Generate another report</button>
      </div>
    </form>
  </main>

  <script>
  (function () {
    const placeInput = document.getElementById('place-input');
    const suggestions = document.getElementById('suggestions');
    const latInput = document.getElementById('lat');
    const lngInput = document.getElementById('lng');
    const tzInput = document.getElementById('tz');
    let debounceTimer;

    placeInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const q = this.value.trim();
      if (q.length < 3) { suggestions.style.display = 'none'; return; }
      debounceTimer = setTimeout(() => geocode(q), 400);
    });

    async function geocode(q) {
      try {
        const url = 'https://nominatim.openstreetmap.org/search?format=json&limit=5&q=' + encodeURIComponent(q);
        const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
        const data = await res.json();
        renderSuggestions(data);
      } catch (_) { suggestions.style.display = 'none'; }
    }

    function renderSuggestions(places) {
      suggestions.innerHTML = '';
      if (!places.length) { suggestions.style.display = 'none'; return; }
      places.forEach(p => {
        const li = document.createElement('li');
        li.textContent = p.display_name;
        li.addEventListener('click', () => {
          placeInput.value = p.display_name;
          latInput.value = parseFloat(p.lat).toFixed(4);
          lngInput.value = parseFloat(p.lon).toFixed(4);
          tzInput.value = guessTimezone(parseFloat(p.lon));
          suggestions.style.display = 'none';
        });
        suggestions.appendChild(li);
      });
      suggestions.style.display = 'block';
    }

    function guessTimezone(lon) {
      // Rough estimate: offset = longitude / 15, rounded to nearest 0.25
      const raw = lon / 15;
      return (Math.round(raw * 4) / 4).toFixed(2);
    }

    document.addEventListener('click', e => {
      if (!e.target.closest('.place-wrap')) suggestions.style.display = 'none';
    });

    const form = document.getElementById('astro-form');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    const errorMsg = document.getElementById('error-msg');
    const downloadCard = document.getElementById('download-card');
    const dlBtn = document.getElementById('dl-btn');
    const readyFilename = document.getElementById('ready-filename');
    const resetLink = document.getElementById('reset-link');
    let currentBlobUrl = null;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      errorMsg.style.display = 'none';
      downloadCard.style.display = 'none';

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      // Revoke any previous blob to free memory
      if (currentBlobUrl) { URL.revokeObjectURL(currentBlobUrl); currentBlobUrl = null; }

      submitBtn.disabled = true;
      spinner.style.display = 'block';
      btnText.textContent = 'Generating your report…';

      const data = new FormData(form);

      try {
        const res = await fetch('/api/report.pdf', { method: 'POST', body: data });
        if (!res.ok) {
          let detail = 'Something went wrong. Please check your details and try again.';
          try { const j = await res.json(); detail = j.detail || detail; } catch (_) {}
          throw new Error(detail);
        }
        const blob = await res.blob();
        const name = data.get('name').trim().replace(/[^a-zA-Z0-9_-]/g, '') || 'Report';
        const filename = 'SattvicGyaan-' + name + '-Vedic-Report.pdf';

        currentBlobUrl = URL.createObjectURL(blob);
        dlBtn.href = currentBlobUrl;
        dlBtn.download = filename;
        readyFilename.textContent = filename;

        // Scroll download card into view and show it
        downloadCard.style.display = 'flex';
        downloadCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Generate PDF Report';
      }
    });

    // "Generate another report" resets the card and scrolls back to form
    resetLink.addEventListener('click', function () {
      downloadCard.style.display = 'none';
      if (currentBlobUrl) { URL.revokeObjectURL(currentBlobUrl); currentBlobUrl = null; }
      form.reset();
      document.querySelector('input[name="name"]').focus();
    });
  })();
  </script>
</body>
</html>
"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def form() -> str:
    return _FORM_HTML


@app.post("/api/calculate")
def calculate(
    name: str = Form(...),
    gender: str = Form("Not specified"),
    birth_date: date = Form(...),
    birth_time: time = Form(...),
    place: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timezone_offset: float = Form(...),
) -> dict:
    details = BirthDetails(name, gender, birth_date, birth_time, place, latitude, longitude, timezone_offset)
    try:
        chart = calculate_chart(details)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _json_safe_chart(chart)


@app.post("/api/report.pdf")
def report_pdf(
    name: str = Form(...),
    gender: str = Form("Not specified"),
    birth_date: date = Form(...),
    birth_time: time = Form(...),
    place: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timezone_offset: float = Form(...),
) -> Response:
    details = BirthDetails(name, gender, birth_date, birth_time, place, latitude, longitude, timezone_offset)
    try:
        chart = calculate_chart(details)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    pdf = build_pdf(chart)
    filename = f"SattvicGyaan-{_safe_filename(name)}-Basic-Vedic-Report.pdf"
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_safe_chart(chart: dict) -> dict:
    result = dict(chart)
    birth = result.pop("birth")
    result["birth"] = {
        "name": birth.name,
        "gender": birth.gender,
        "birth_date": birth.birth_date.isoformat(),
        "birth_time": birth.birth_time.isoformat(timespec="minutes"),
        "place": birth.place,
        "latitude": birth.latitude,
        "longitude": birth.longitude,
        "timezone_offset": birth.timezone_offset,
    }
    result["local_datetime"] = chart["local_datetime"].isoformat(timespec="minutes")
    result["utc_datetime"] = chart["utc_datetime"].isoformat(timespec="minutes")
    return result


def _safe_filename(value: str) -> str:
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in ("-", "_")).strip()
    return cleaned or "Report"
