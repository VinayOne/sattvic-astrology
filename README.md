# Sattvic Gyaan Astrology Prototype

Local prototype for generating a basic Vedic astrology PDF report.

## Setup

```powershell
& "C:\Users\vinay\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pip install --target .deps fastapi==0.115.6 "uvicorn[standard]==0.32.1" reportlab==4.2.5 astronomy-engine==2.1.19 python-multipart==0.0.20
```

On Linux/Coolify, install `requirements.txt` so `pyswisseph` is used as the primary calculation engine.

## Generate Demo PDF

```powershell
$env:PYTHONPATH="$PWD\.deps"
& "C:\Users\vinay\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" generate_demo.py
```

The generated approval PDF is:

```text
SattvicGyaan-Vinay-Basic-Vedic-Report.pdf
```

## Run App

```powershell
$env:PYTHONPATH="$PWD\.deps"
& "C:\Users\vinay\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Calculation Basis

The prototype uses Swiss Ephemeris via `pyswisseph`, sidereal Lahiri/Chitrapaksha ayanamsa, and Nirayana Vedic positions. The PDF interpretations are original Sattvic Gyaan content for spiritual reflection.
