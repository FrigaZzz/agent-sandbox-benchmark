"""
Build script to aggregate benchmark reports into self-contained data.js and data.json
for the Sandbox Performance & Evidence Dashboard in reports/ui/.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.bench.portal import portal_html
from src.bench.evidence import load_evidence

UI_DIR = Path(__file__).resolve().parent
index = UI_DIR / "index.html"
index.write_text(portal_html(index.read_text(), "../", "ui/index.html"))
REPO_ROOT = UI_DIR.parents[1]
REPORTS_DIR = REPO_ROOT / "reports"
DATA_DIR = REPORTS_DIR / "data"

PROVIDER_METAS = {
    "modal": {
        "name": "Modal",
        "category": "Serverless Container Runtime",
        "badge": "Managed API",
        "color": "#10b981",
        "accent": "rgba(16, 185, 129, 0.15)",
        "icon": "⚡",
        "description": "High-speed serverless containers with custom images and GPU support."
    },
    "gcp_vertex": {
        "name": "GCP Agent Sandbox",
        "category": "Cloud Provider Interpreter",
        "badge": "Cloud Native",
        "color": "#3b82f6",
        "accent": "rgba(59, 130, 246, 0.15)",
        "icon": "☁️",
        "description": "Google Cloud managed sandbox for enterprise agent workflows."
    },
    "e2b": {
        "name": "E2B",
        "category": "Agent Sandbox Platform",
        "badge": "Dedicated Sandbox",
        "color": "#f59e0b",
        "accent": "rgba(245, 158, 11, 0.15)",
        "icon": "📦",
        "description": "Specialized sandboxes for AI agents with code execution environments."
    },
    "blaxel": {
        "name": "Blaxel",
        "category": "Agent Workspace Platform",
        "badge": "Managed API",
        "color": "#8b5cf6",
        "accent": "rgba(139, 92, 246, 0.15)",
        "icon": "🔮",
        "description": "Fast container workspaces with preconfigured agent developer tools."
    },
    "daytona": {
        "name": "Daytona",
        "category": "Development Workspace API",
        "badge": "Workspace API",
        "color": "#06b6d4",
        "accent": "rgba(6, 182, 212, 0.15)",
        "icon": "🚀",
        "description": "Standardized dev workspaces with persistent sessions and git tooling."
    },
    "aws": {
        "name": "AWS AgentCore",
        "category": "Cloud Provider Interpreter",
        "badge": "Cloud Native",
        "color": "#f97316",
        "accent": "rgba(249, 115, 22, 0.15)",
        "icon": "🟧",
        "description": "AWS managed code interpreter session infrastructure for Bedrock agents."
    },
    "alibaba": {
        "name": "Alibaba OpenSandbox",
        "category": "Hybrid / AgentRun Runtime",
        "badge": "Hybrid OSS/Cloud",
        "color": "#ff6a00",
        "accent": "rgba(255, 106, 0, 0.15)",
        "icon": "🐅",
        "description": "OpenSandbox container runtime with managed AgentRun serverless execution."
    },
    "databricks": {
        "name": "Databricks SQL MCP",
        "category": "Enterprise Data Platform",
        "badge": "Data Platform",
        "color": "#ef4444",
        "accent": "rgba(239, 68, 68, 0.15)",
        "icon": "🧱",
        "description": "Databricks serverless compute and SQL warehouse execution surface."
    },
    "databricks_sandbox": {
        "name": "Databricks Dedicated Sandbox",
        "category": "Dedicated Agent Sandbox",
        "badge": "Beta Preview",
        "color": "#e11d48",
        "accent": "rgba(225, 29, 72, 0.15)",
        "icon": "🧪",
        "description": "Dedicated agent sandbox preview environment inside Databricks workspaces."
    },
    "gemini_tool": {
        "name": "Gemini Tool (Google)",
        "category": "Model-Mediated Code Tool",
        "badge": "Model Tool",
        "color": "#4285f4",
        "accent": "rgba(66, 133, 244, 0.15)",
        "icon": "✨",
        "description": "Direct model-mediated code execution tool within Google Gemini API."
    },
    "openai_tool": {
        "name": "OpenAI Tool (Code Interpreter)",
        "category": "Model-Mediated Code Tool",
        "badge": "Model Tool",
        "color": "#10a37f",
        "accent": "rgba(16, 163, 127, 0.15)",
        "icon": "🤖",
        "description": "Hosted containerized Python execution environment for ChatGPT/Assistants."
    },
    "k8s_agent_sandbox": {
        "name": "Kubernetes Adapter",
        "category": "Self-Hosted Cluster",
        "badge": "Self-Hosted K8s",
        "color": "#326ce5",
        "accent": "rgba(50, 108, 229, 0.15)",
        "icon": "☸️",
        "description": "Kubernetes-native agent pod execution adapter without managed cloud wrapper."
    },
    "local_baseline": {
        "name": "Local Control (Host)",
        "category": "Local Baseline",
        "badge": "Local Host",
        "color": "#64748b",
        "accent": "rgba(100, 116, 139, 0.15)",
        "icon": "💻",
        "description": "Direct execution on the test machine (Apple M-series) as latency reference."
    }
}

SUITE_METAS = {
    "cold_start": {"name": "Cold Start Latency", "category": "Lifecycle", "icon": "⏱️", "desc": "Time to provision sandbox, execute minimal script, and cleanup."},
    "dependency_install": {"name": "Dependency Installation", "category": "Packaging", "icon": "📦", "desc": "Installing external wheel/pip dependencies inside the sandbox."},
    "sqlite_analytics": {"name": "SQLite Analytics", "category": "Computation", "icon": "🗄️", "desc": "In-memory database creation, 20k row aggregation, and rollback verification."},
    "data_pipeline": {"name": "Data Pipeline & Artifacts", "category": "I/O & Compute", "icon": "📊", "desc": "Input data staging, CSV transform, JSON aggregation, output artifact collection."},
    "repository_task": {"name": "Repository Task (TDD)", "category": "Developer Tasks", "icon": "🛠️", "desc": "Multi-file project setup, red test execution failure, code fix, green test pass."},
    "session_state": {"name": "Files Across Calls", "category": "Lifecycle", "icon": "💾", "desc": "Verifying files across separate live-session calls; memory resume and stopped-disk persistence are not measured."},
    "cpu_stress": {"name": "CPU Stress Test", "category": "Hardware", "icon": "🔥", "desc": "Prime number computation (Sieve of Eratosthenes) to measure CPU throttling."},
    "mem_stress": {"name": "Memory Stress Test", "category": "Hardware", "icon": "🧠", "desc": "Memory allocation up to limits to observe cgroup enforcement or OOM handling."},
    "disk_io": {"name": "Disk I/O Throughput", "category": "Hardware", "icon": "💽", "desc": "Sequential and random file write/read speed in sandbox temporary space."},
    "timeout_handling": {"name": "Deadline Response", "category": "Robustness", "icon": "⏳", "desc": "Checking the expected timeout response and response budget; remote termination is not independently attested."},
    "error_recovery": {"name": "Error Recovery", "category": "Robustness", "icon": "🔄", "desc": "Recovery and correct continued execution after an unhandled exception step."},
    "output_fidelity": {"name": "Output Fidelity & Logs", "category": "I/O & Compute", "icon": "📝", "desc": "Accurate byte-for-byte stdout/stderr capture without truncation banners."},
    "artifact_roundtrip": {"name": "Binary Artifact Integrity", "category": "I/O & Compute", "icon": "🔒", "desc": "Uploading and downloading binary files with cryptographic SHA-256 validation."},
    "parallel_throughput": {"name": "Parallel Throughput Burst", "category": "Scalability", "icon": "🚀", "desc": "Multi-worker concurrent execution testing completions per second."},
    "runtime_inventory": {"name": "Runtime Hardware Probe", "category": "Inspection", "icon": "🔍", "desc": "Detailed inspection of CPUs, RAM, kernel, cgroups, and GPU availability."},
    "net_isolation": {"name": "Network Isolation", "category": "Security", "icon": "🛡️", "desc": "Verifying sandbox outbound internet restrictions and firewall boundaries."},
    "env_security": {"name": "Environment Security", "category": "Security", "icon": "🔐", "desc": "Inspection of host environment variables, tokens, and isolation boundaries."},
    "package_ecosystem": {"name": "Scientific Package Availability", "category": "Packaging", "icon": "🧪", "desc": "Checking preinstalled availability of numpy, pandas, torch, requests, scipy."},
    "agent_multiturn": {"name": "Agent Multi-Turn Dialogue", "category": "Developer Tasks", "icon": "💬", "desc": "Simulating a multi-turn agent tool conversation with state preservation."}
}


def build_bundle():
    print("Building sandbox dashboard data bundle...")
    derived_dir = DATA_DIR / "derived" if (DATA_DIR / "derived").exists() else REPORTS_DIR
    campaigns_dir = DATA_DIR / "campaigns" if (DATA_DIR / "campaigns").exists() else REPORTS_DIR

    # 1. Load evaluation-summary.json
    eval_sum_path = derived_dir / "evaluation-summary.json"
    if eval_sum_path.exists():
        eval_sum = json.loads(eval_sum_path.read_text(encoding="utf-8"))
    else:
        eval_sum = {}

    # 2. Load specifications.json
    spec_path = derived_dir / "specifications.json"
    if spec_path.exists():
        specs_data = json.loads(spec_path.read_text(encoding="utf-8"))
    else:
        specs_data = {}

    # 3. Load all attempts from attempts directory
    attempts = []
    normalized, issues = load_evidence(REPORTS_DIR)
    for run in normalized:
        stdout, stderr = run.get("stdout", "") or "", run.get("stderr", "") or ""
        record = {key: run.get(key) for key in ("run_id", "provider", "suite", "status", "evaluation",
            "exit_code", "started_at", "timings", "checks", "cost", "metrics", "warnings", "error", "runtime_kind")}
        record.update(artifacts=len(run.get("artifacts", [])), report_file=run["report_path"],
            stdout_preview=stdout[:2000], stderr_preview=stderr[:2000],
            is_truncated=len(stdout) > 2000 or len(stderr) > 2000,
            stdout_chars=len(stdout), stderr_chars=len(stderr),
            configuration=run.get("provenance", {}).get("configuration", {}),
            campaign_id=run.get("provenance", {}).get("campaign_id"),
            evidence_label=run["evidence_label"])
        attempts.append(record)

    # 4. Load all campaigns
    campaigns = []
    if campaigns_dir.exists():
        for p in sorted(campaigns_dir.glob("campaign-*.json")):
            try:
                c = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(c, dict):
                    campaigns.append(c)
            except Exception:
                pass
    if not campaigns and "campaigns" in eval_sum:
        campaigns = eval_sum["campaigns"]

    # 5. Extract tested configurations & inventory observations
    tested_configs = specs_data.get("tested_configurations", [])
    specifications = specs_data.get("specifications", eval_sum.get("specifications", {}))

    # Calculate overall provider metrics
    provider_stats = {}
    for prov_id, prov_meta in PROVIDER_METAS.items():
        prov_attempts = [a for a in attempts if a["provider"] == prov_id]
        prov_summaries = [s for s in eval_sum.get("summaries", []) if s.get("provider") == prov_id]
        
        passes = sum(1 for a in prov_attempts if a["evaluation"] == "pass")
        fails = sum(1 for a in prov_attempts if a["evaluation"] == "fail")
        timed_out = sum(1 for a in prov_attempts if a["status"] == "timed_out")
        
        # Collect latencies
        wall_times = [a["timings"].get("total_wall_clock_ms") for a in prov_attempts if a["timings"].get("total_wall_clock_ms")]
        wall_times = [w for w in wall_times if w and w > 0]
        
        sorted_times = sorted(wall_times)
        p50 = sorted_times[len(sorted_times) // 2] if sorted_times else None
        p95_idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[min(p95_idx, len(sorted_times) - 1)] if sorted_times else None

        # Collect cold start latencies specifically
        cs_times = [a["timings"].get("total_wall_clock_ms") for a in prov_attempts if a["suite"] == "cold_start" and a["timings"].get("total_wall_clock_ms")]
        cs_p50 = sorted(cs_times)[len(cs_times) // 2] if cs_times else None

        provider_stats[prov_id] = {
            "meta": prov_meta,
            "total_attempts": len(prov_attempts),
            "passes": passes,
            "fails": fails,
            "timed_out": timed_out,
            "pass_rate": (passes / len(prov_attempts)) if prov_attempts else 0.0,
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "cold_start_p50_ms": cs_p50,
            "suites_tested": sorted(list({a["suite"] for a in prov_attempts})),
            "has_specs": prov_id in specifications,
        }

    # Build the unified output bundle
    bundle = {
        "metadata": {
            "generated_at": eval_sum.get("generated_at", "2026-10-13T20:00:00Z"),
            "schema_version": 2,
            "total_attempts": len(attempts),
            "total_summaries": len(eval_sum.get("summaries", [])),
            "total_campaigns": len(campaigns),
            "total_insights": len(eval_sum.get("insights", [])),
            "total_providers": len(PROVIDER_METAS),
            "total_suites": len(SUITE_METAS),
        },
        "providers": PROVIDER_METAS,
        "suites": SUITE_METAS,
        "provider_stats": provider_stats,
        "summaries": eval_sum.get("summaries", []),
        "campaigns": campaigns,
        "insights": eval_sum.get("insights", []),
        "specifications": specifications,
        "tested_configurations": tested_configs,
        "attempts": attempts,
        "issues": issues,
    }

    # Save to data.json
    json_path = UI_DIR / "data.json"
    json_content = json.dumps(bundle, indent=2)
    json_path.write_text(json_content, encoding="utf-8")
    print(f"Saved {json_path} ({len(json_content)} bytes)")

    # Save to data.js for seamless offline/file:// origin access
    js_path = UI_DIR / "data.js"
    # Safely escape for embedding in JS
    js_content = f"// Generated Sandbox Benchmark Data Bundle\nwindow.BENCHMARK_DATA = {json.dumps(bundle)};\n"
    js_path.write_text(js_content, encoding="utf-8")
    print(f"Saved {js_path} ({len(js_content)} bytes)")

    return bundle


if __name__ == "__main__":
    build_bundle()
