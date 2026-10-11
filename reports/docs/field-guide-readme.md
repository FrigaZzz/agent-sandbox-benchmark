# Sandbox field guide — presentation and evidence companion

Reviewed.

## Start here

- **[Short decision guide](../simplified/README.md)** and **[nine-page PDF](../simplified/agent-sandbox-decisions.pdf)**: the concise sharing version, centred on workload scope and five selection questions. This package is separate from the detailed ZIP below.
- **[Consolidated technical report](detailed-report.md)** and **[decision explorer](../variant/index.html)**: deeper narrative and requirement filtering. [Report map](../README.md) explains the complete file structure.
- **[sandbox-field-guide.pdf](../downloads/sandbox-field-guide.pdf)**: 23-page, 4:3 presentation export. Essential qualifications are printed beside the comparisons. Official web-source links remain clickable.
- **[index.html](../index.html)**: evidence dashboard with exact attempt filters, raw-check previews and the full price/capability tables.
- **`eu-data-residency.md`**: product-specific regions, data boundaries, retention caveats, benchmark location provenance and original legal/provider sources.
- **`findings.md`** and **`evaluation-framework.md`**: measurements, trial boundaries and methods.

Keep the extracted directory structure: HTML uses relative links to the included report JSON and provider specifications. Published data availability and documented capabilities are separate from measured fixtures.

## PDF and companion links

The PDF is self-contained for the narrative and plotted observations. References to local evidence files are labelled as companion material rather than exported as temporary localhost links. The ZIP includes the interactive deck, evidence dashboard, original referenced report JSON, campaign records, provider specifications and visual contact sheets.

The PDF and [ZIP companion](../downloads/sandbox-field-guide-bundle.zip) can be downloaded from this repository. No deployment-specific public URL is assumed in these files.

## Rebuild and verify in the repository

```sh
python3 -m src.cli dashboard
python3 scripts/verify_dashboard.py
python3 scripts/validate_evidence.py
```

The browser verifier uses a disposable headless Chrome profile, `websockets`, Pillow and PyMuPDF. It checks all slide containers, renders every PDF page, checks page count/aspect ratio/searchable text/source links, exercises responsive layouts, and regenerates the PDF/ZIP in `reports/downloads/` and screenshots in `reports/checks/dashboard/`.
