"""Offline dashboard generated from the same evidence summaries as Markdown."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from .evidence import evidence_bundle
from .specifications import specification_bundle
from .insights import measured_insights
from .portal import portal_html


def load_all_reports():
    bundle = evidence_bundle()
    return {provider: [r for r in bundle["attempts"] if r["provider"] == provider]
            for provider in {r["provider"] for r in bundle["attempts"]}}


def build_dashboard_html(reports_dir=Path("reports")) -> str:
    bundle = evidence_bundle(reports_dir)
    bundle.update(specification_bundle(reports_dir))
    bundle["insights"] = measured_insights(bundle)
    # Keep standalone HTML lightweight; original files retain all raw bytes.
    # The inspector clearly identifies previews and links the complete report.
    for run in bundle["attempts"]:
        previews = {}
        for field in ["stdout", "stderr"]:
            text = run.get(field, "")
            if len(text) > 16000:
                previews[field] = {"original_chars": len(text), "original_bytes": len(text.encode()),
                                   "sha256": hashlib.sha256(text.encode()).hexdigest(), "displayed_chars": 16000}
                run[field] = text[:16000]
        for step in run.get("steps", []):
            for field in ["stdout", "stderr"]:
                text = step.get(field, "")
                if len(text) > 2000:
                    step[field] = text[:2000]
                    step[f"{field}_preview"] = {"original_chars": len(text), "displayed_chars": 2000}
        if previews:
            run["display_previews"] = previews
    # Report stdout is untrusted; prevent closing the JSON script element.
    payload = json.dumps(bundle).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = Path(__file__).with_name("dashboard.html").read_text()
    template = template.replace('href="evaluation-framework.md"', 'href="docs/evaluation-framework.md"')
    return portal_html(template.replace("__EVIDENCE_JSON__", payload))


def generate_dashboard_files(output_path="reports/index.html", reports_dir=Path("reports")) -> Path:
    from .findings import generate_findings
    generate_findings(reports_dir)
    content = build_dashboard_html(reports_dir)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path
