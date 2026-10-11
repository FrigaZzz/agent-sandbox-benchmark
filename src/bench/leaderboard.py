"""Leaderboard calculation and Markdown report generator supporting live empirical run ingestion."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ProviderScore:
    provider: str
    tier: str
    source: str  # "Live Measured" vs "Architecture Spec"
    composite_score: float | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


# Historical profiles retained for compatibility and existing user work.
# Numeric values are NOT evidence and are never used in scoring.
BENCHMARK_PROFILES: dict[str, dict[str, Any]] = {
    "gcp_vertex": {
        "tier": "Container MicroVM (CMEK)",
        "cold_start_ms": 3200,
        "compute_speed": 88,
        "memory_limit_mb": 4096,
        "security": 98,
        "cost_per_sec": 0.000045,
        "features": 95,
        "source": "Architecture Spec",
    },
    "gemini_tool": {
        "tier": "Model-Managed Native Tool",
        "cold_start_ms": 1400,
        "compute_speed": 75,
        "memory_limit_mb": 1024,
        "security": 92,
        "cost_per_sec": 0.000005,
        "features": 45,
        "source": "Architecture Spec",
    },
    "modal": {
        "tier": "Serverless Container MicroVM",
        "cold_start_ms": 850,
        "compute_speed": 96,
        "memory_limit_mb": 16384,
        "security": 90,
        "cost_per_sec": 0.0000288,
        "features": 98,
        "source": "Architecture Spec",
    },
    "e2b": {
        "tier": "Agentic MicroVM (Firecracker)",
        "cold_start_ms": 650,
        "compute_speed": 90,
        "memory_limit_mb": 2048,
        "security": 92,
        "cost_per_sec": 0.000040,
        "features": 90,
        "source": "Architecture Spec",
    },
    "blaxel": {
        "tier": "Agentic MicroVM Container",
        "cold_start_ms": 1800,
        "compute_speed": 92,
        "memory_limit_mb": 4096,
        "security": 88,
        "cost_per_sec": 0.000035,
        "features": 92,
        "source": "Architecture Spec",
    },
    "databricks": {
        "tier": "Serverless SQL MCP (system.ai.python_exec)",
        "cold_start_ms": 7162,
        "compute_speed": 82,
        "memory_limit_mb": 1024,
        "security": 95,
        "cost_per_sec": 0.000025,
        "features": 55,
        "source": "Architecture Spec",
    },
    "databricks_sandbox": {
        "tier": "Dedicated MicroVM (4 vCPU / 8 GB RAM)",
        "cold_start_ms": 3400,
        "compute_speed": 94,
        "memory_limit_mb": 8192,
        "security": 93,
        "cost_per_sec": 0.000036,
        "features": 94,
        "source": "Architecture Spec",
    },
    "openai_tool": {
        "tier": "Model-Managed Native Tool",
        "cold_start_ms": 2100,
        "compute_speed": 78,
        "memory_limit_mb": 1024,
        "security": 92,
        "cost_per_sec": 0.000030,
        "features": 60,
        "source": "Architecture Spec",
    },
    "daytona": {
        "tier": "Dev Environment Sandbox",
        "cold_start_ms": 4500,
        "compute_speed": 88,
        "memory_limit_mb": 8192,
        "security": 85,
        "cost_per_sec": 0.000020,
        "features": 96,
        "source": "Architecture Spec",
    },
    "aws": {
        "tier": "Bedrock AgentCore MicroVM",
        "cold_start_ms": 2500,
        "compute_speed": 90,
        "memory_limit_mb": 4096,
        "security": 96,
        "cost_per_sec": 0.000035,
        "features": 92,
        "source": "Architecture Spec",
    },
    "k8s_agent_sandbox": {
        "tier": "Kubernetes SIGs Sandbox CRD",
        "cold_start_ms": 262,
        "compute_speed": 95,
        "memory_limit_mb": 4096,
        "security": 94,
        "cost_per_sec": 0.000030,
        "features": 96,
        "source": "Live Measured",
    },
}


def load_live_reports() -> dict[str, dict[str, Any]]:
    from .evidence import load_evidence
    attempts, _ = load_evidence()
    return {provider: {"attempts": [r for r in attempts if r["provider"] == provider]}
            for provider in {r["provider"] for r in attempts}}


def calculate_leaderboard(
    weights: dict[str, float] | None = None, *, suite: str = "cold_start", reports_dir: Path = Path("reports")
) -> list[ProviderScore]:
    """Rank only sufficiently sampled matching workloads; never substitute architectural scores."""
    import math
    from .evidence import evidence_bundle
    w = weights if weights is not None else {"latency": .5, "reliability": .5}
    if set(w) - {"latency", "reliability"}:
        raise ValueError("Only latency and reliability have measured scores. Security, cost and full feature richness are unranked.")
    if not w or any(not math.isfinite(v) or v < 0 for v in w.values()) or sum(w.values()) <= 0:
        raise ValueError("Weights must be finite, nonnegative and have a positive sum")
    total = sum(w.values())
    w = {key: value / total for key, value in w.items()}
    rows = [r for r in evidence_bundle(reports_dir)["summaries"] if r["suite"] == suite]
    cohorts = {}
    for r in rows:
        key = (r["workload_sha256"], r["evaluation_contract_sha256"], r["runtime_kind"], r["concurrency"], r["client_os"], r["client_arch"])
        cohorts.setdefault(key, []).append(r)
    scores = []
    for cohort, members in cohorts.items():
        eligible = [r for r in members if r["eligible"] and r["latency_ms"]["p50"] is not None]
        best = min((r["latency_ms"]["p50"] for r in eligible), default=None)
        for r in members:
            score = None
            if r in eligible and len({x["provider"] for x in eligible}) >= 2:
                score = round(100 * (w.get("latency", 0) * best / r["latency_ms"]["p50"]
                              + w.get("reliability", 0) * r["success_ci95"][0]), 1)
            r = dict(r, weights=w, cohort=str(cohort))
            scores.append(ProviderScore(provider=r["provider"], tier=r["runtime_kind"],
                source="Validated" if r["n"] else "Unvalidated / missing", composite_score=score, evidence=r))
    scores.sort(key=lambda s: (s.evidence["cohort"], s.composite_score is None, -(s.composite_score or 0), s.provider))
    return scores


def generate_markdown_report(scores: list[ProviderScore]) -> str:
    """Transparent workload-specific report; no universal winner claims."""
    def fmt(value):
        return f"{value:.1f}" if value is not None else "—"
    lines = [
        "# Sandbox workload evidence leaderboard", "",
        "Scores compare identical workload hashes, runtime kinds, concurrency and client platforms only. Configuration labels remain visible; hardware/image/network differences are not normalized.", "",
        "At least 5 correctness-validated attempts and 2 providers in a cohort are needed for a score. Local and unattested deployments are controls, never cloud winners. Legacy evidence is retained but unvalidated.", "",
        "Latency score = fastest eligible median / provider median. Reliability score = lower 95% Wilson success bound. Weighted scores are exploratory, not SLA or security certifications. Cost, security, and broad capability claims are unranked.", "",
        "| Provider | Suite / hash | Runtime | Config / contract / adapter / concurrency | Pass / fail / unknown / skipped | Success 95% interval | p50 / p95 ms (passed attempts) | Score | Evidence |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for s in scores:
        r = s.evidence
        counts = " / ".join(str(r["outcomes"].get(k, 0)) for k in ["pass", "fail", "unknown", "skipped"])
        interval = "—" if r["success_ci95"] is None else "–".join(f"{v*100:.1f}%" for v in r["success_ci95"])
        links = ", ".join(f"[{p}](../{p})" for p in r["reports"])
        lines.append(
            f"| {s.provider} | {r['suite']} / `{r['workload_sha256'][:10]}` | {s.tier} | `{r['config_id']}` / `{r['evaluation_contract_sha256'][:8]}` / `{r['adapter_sha256'][:8]}` / {r['concurrency']} | {counts} | {interval} | {fmt(r['latency_ms']['p50'])} / {fmt(r['latency_ms']['p95'])} | {fmt(s.composite_score)} | {links} |"
        )
    from .evidence import PROVIDERS
    missing = sorted(set(PROVIDERS) - {s.provider for s in scores})
    lines.extend(["", "Providers without this workload evidence: " + (", ".join(missing) or "none"), "",
                  "p95 with n<100 is exploratory. Historical reports lack timestamps, verified configuration and independent correctness checks. See [methodology](evaluation-framework.md) and the dashboard for per-attempt checks and raw output."])
    if scores:
        lines.extend(["", "Active normalized weights: `" + json.dumps(scores[0].evidence["weights"], sort_keys=True) + "`", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    ranked = calculate_leaderboard()
    print(generate_markdown_report(ranked))
