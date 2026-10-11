# AI Sandbox Benchmark & Evidence Dashboard

An interactive chart studio over the canonical evidence loader: 12 provider
specifications, a local control and documented workload categories. Historical and
date-sharded attempts are normalized consistently with the raw evidence explorer.

## Features

- **10 Interactive Dedicated Views**:
  1. **Overview & Executive Summary**: Coverage counts, evidence layers, readiness lifecycle cohorts, failure findings and a coverage table. No composite capability/security scores.
  2. **Latency Comparison Studio**: Latest eligible serial cohorts for one fixture at a time (default prime), preserving setup labels; no pooled cross-task speed winner.
  3. **Lifecycle Phase Breakdown**: Horizontal stacked bar charts decomposing time spent across `Initialize`, `Prepare`, `Execute`, `Collect`, and `Cleanup`.
  4. **Reliability & Pass Rate Studio**: Bar chart with Wilson 95% Confidence Bounds alongside an interactive 2D Provider-by-Suite pass/fail Heatmap Grid (click any cell to inspect those exact runs).
  5. **Pricing Evidence**: Metered campaign cost is unavailable; documented-unit scenarios replace an unsupported cheapest-provider frontier.
  6. **Recorded Burst Campaigns**: Provider-attributed direct-remote campaign rates; no invented worker count or quota ceiling.
  7. **Architectural Feature Matrix**: Detailed feature comparison (Custom Docker images, CPU/RAM sizing, GPU sandboxes, Network egress policy, Offline pip, Persistent disk, CMEK encryption, EU residency).
  8. **Hardware & Runtime Probes**: Direct guest OS measurements (visible CPUs, reported physical memory, cgroup limits, kernel, GPU driver probe).
  9. **Scenario Cost Calculator**: Published CPU/RAM-unit request-only E2B/Modal illustrations. Physical cores differ from vCPUs; omitted premiums/fees prevent invoice predictions.
  10. **Evidence Attempt Inspector**: Retained attempts including historical unknown outcomes. The drawer shows timings, checks and bounded stdout/stderr previews.

- **Design & Performance**:
  - Dark mode by default with light mode toggle (persisted via `localStorage`).
  - Fullscreen presentation view for slide decks and demos.
  - Zero external CDN dependencies: runs 100% offline and works out-of-the-box via `file://` protocol or any web server.
  - Custom Canvas and SVG chart engine with high-DPI Retina sharpness, smooth hover tooltips, and interactive filtering.
  - One-click CSV export of all evaluated attempts.

## How to View

### Option 1: Direct File Open (Offline)
Open `index.html` directly in your browser:
```bash
open reports/ui/index.html
```
No web server is required because the dataset is bundled directly into `data.js`.

### Option 2: Local Web Server
You can also serve it locally using any static server:
```bash
# Using Python
python3 -m http.server 8080 --directory reports/ui

# Or using npx serve
npx serve reports/ui
```
Then visit `http://localhost:8080` in your browser.

## How to Rebuild the Dataset

Whenever new benchmark evaluation runs are executed or updated:
```bash
python3 reports/ui/build_ui.py
```
This script reads the raw data from `reports/data/` (or `reports/`), compiles all metrics, extracts run previews, and generates fresh `data.js` and `data.json` bundles.
