# Benchmark reports

Three reading depths: **overview → interactive exploration → technical reference**.
The web tools share portal navigation and use the same retained evidence.

| What you need | Start here |
|---|---|
| A quick overview | [Short decision guide](simplified/README.md) · [Nine-page PDF](simplified/agent-sandbox-decisions.pdf) |
| A PM / engineering-lead briefing | [Ten-slide executive infographics](executive/index.html) · [Exported figures](executive/README.md) |
| Interactive visual plots & charts | [Evidence Studio Dashboard](ui/index.html) · [UI Readme](ui/README.md) |
| Measured results and exact attempts | [Evidence dashboard](index.html) · [Findings](docs/findings.md) |
| The full technical account | [Technical report](docs/detailed-report.md) |
| Requirement and cost scenarios | [Decision explorer](variant/index.html) |
| Methods and interpretation | [Methodology](docs/evaluation-framework.md) · [Data notes](docs/data-notes.md) |
| Data geography and retention | [Residency guide](docs/eu-data-residency.md) |
| A presentation export | [PDF](downloads/sandbox-field-guide.pdf) · [Offline companion](downloads/sandbox-field-guide-bundle.zip) |
| Product/API contracts | [Provider specifications](../providers/README.md) |

## Directory layout

```text
reports/
├── README.md               this map
├── ui/                     interactive visual dashboard and plotting studio
├── index.html              canonical evidence dashboard
├── docs/                   technical report, findings, leaderboard and methods
├── data/
│   ├── attempts/           versioned evaluation records, including failures
│   ├── legacy/             historical unvalidated observations
│   ├── campaigns/          original concurrency/throughput records
│   └── derived/            generated specification and summary datasets
├── downloads/              detailed PDF and offline ZIP companion
├── checks/
│   ├── schema-links.json   schema and link validation
│   ├── dashboard/          detailed-deck/dashboard screenshots and checks
│   └── decision-guide/     decision explorer screenshots and checks
├── simplified/             self-contained short guide, renderer and export checks
├── variant/                decision explorer, source, builder and derived data
└── executive/              ten-slide business-facing briefing, figures and PDF export
```

Raw attempts and campaign records are retained, rather than replaced by summaries.
The short guide remains a self-contained package with its own `checks/` directory.
`index.html` is the single evidence dashboard; the duplicate `dashboard.html` was removed.
The compatibility leaderboard entry point is now `../scripts/leaderboard.py`.
Ignored append locks live beside their attempt files, not at the report root.

## Regenerate from the repository root

```bash
python3 -m src.cli specs
python3 -m src.cli dashboard
python3 -m src.cli leaderboard --suite all --output reports/docs/leaderboard.md
python3 reports/variant/build_variant.py
python3 reports/ui/build_ui.py
python3 reports/executive/build_deck.py
python3 scripts/verify_dashboard.py
python3 scripts/validate_evidence.py
```

The PDF/browser exporter needs the presentation extras and installed Chrome/Chromium.
See the [root README](../readme.md#rebuild-and-validate) for dependencies and
the [short guide](simplified/README.md#rebuild) for its separate rebuild commands.
New default benchmark runs append to `data/attempts/`.
