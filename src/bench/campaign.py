"""Repeated, resumable evidence collection; one owned adapter per attempt."""
from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import json
import platform
import random
import subprocess
import time
import uuid
import inspect
import fcntl
import tempfile
import shutil
from dataclasses import asdict
from pathlib import Path

from .runner import BenchmarkRunner
from .configuration import requested_configuration
from .budget import CampaignBudget, positive_usd
from .cost import attempt_budget_estimate


def client_provenance() -> dict:
    versions = {}
    for name in ["pydantic", "modal", "e2b-code-interpreter", "blaxel", "boto3", "databricks-sdk", "google-genai", "daytona-sdk", "openai", "agent-sandbox"]:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    has_git = shutil.which("git") is not None
    revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() if has_git else ""
    return {"client_python": platform.python_version(), "client_os": platform.system(),
            "client_arch": platform.machine(), "sdk_versions": versions, "git_revision": revision,
            "working_tree_dirty": bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout) if revision else None}


def append_attempt(output, attempt):
    """Cross-process read/append/replace transaction; no lost campaign samples."""
    with output.with_suffix(output.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existing = json.loads(output.read_text()) if output.exists() else []
        if not isinstance(existing, list):
            raise ValueError("Existing output must be a JSON attempt list")
        existing.append(attempt)
        with tempfile.NamedTemporaryFile("w", dir=output.parent, prefix=output.name, suffix=".tmp", delete=False) as temporary:
            json.dump(existing, temporary, indent=2)
            temp_path = Path(temporary.name)
        temp_path.replace(output)


def runtime_kind(backend):
    if backend.name == "local_baseline":
        return "local_control"
    if backend.name in ("k8s_agent_sandbox", "alibaba"):
        return "local_control" if getattr(backend, "_server_proc", None) else "unattested_endpoint"
    return "model_mediated" if backend.capabilities.model_managed else "remote_runtime"


async def run_campaign(factory, suites, output: Path, *, repeats=5, warmups=0,
                       concurrency=1, config=None, seed=42, budget_cap_usd=None,
                       budget_attempt_estimate_usd=None) -> list[dict]:
    if repeats < 1 or warmups < 0 or concurrency < 1:
        raise ValueError("repeats/concurrency must be positive; warmups must be nonnegative")
    if not suites:
        raise ValueError("At least one suite is required")
    budget = CampaignBudget(budget_cap_usd) if budget_cap_usd is not None else None
    if budget_attempt_estimate_usd is not None:
        positive_usd(budget_attempt_estimate_usd)
        if budget is None:
            raise ValueError("--budget-attempt-estimate-usd requires --budget-cap-usd")
    # Preflight every suite before any remote initialization; unknown rates fail closed.
    allowances = {suite: attempt_budget_estimate(factory(), suite, budget_attempt_estimate_usd)
                  for suite in suites} if budget else {}
    campaign_id = f"campaign-{uuid.uuid4().hex[:12]}"
    config = config or {"label": "adapter-defaults"}
    common = client_provenance()
    attempts = []
    output.parent.mkdir(parents=True, exist_ok=True)
    # Even a zero-admission campaign has a resolvable empty raw report. Share the
    # append lock so concurrent campaigns cannot overwrite a newly appended row.
    with output.with_suffix(output.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not output.exists():
            output.write_text("[]")
    if output.exists():
        attempts = json.loads(output.read_text())
        if not isinstance(attempts, list):
            raise ValueError("Existing output must be a JSON attempt list")
    warmup_jobs = [(suite, index, True) for index in range(warmups) for suite in suites]
    jobs = [(suite, index, False) for index in range(repeats) for suite in suites]
    rng = random.Random(seed)
    rng.shuffle(warmup_jobs)
    rng.shuffle(jobs)
    sem = asyncio.Semaphore(concurrency)
    started = time.perf_counter()
    skipped_admissions = 0
    interrupted = False

    async def attempt(suite, index, warmup):
        nonlocal skipped_admissions
        async with sem:
            allowance, allowance_details = allowances.get(suite, (None, None))
            if budget and not budget.reserve(allowance):
                skipped_admissions += 1
                return
            backend = factory()
            adapter_path = Path(inspect.getfile(type(backend)))
            adapter_sha = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
            actual_config = dict(config, requested=requested_configuration(backend))
            config_id = hashlib.sha256(json.dumps(actual_config, sort_keys=True).encode()).hexdigest()[:12]
            result = None
            teardown = "success"
            kind = runtime_kind(backend)
            try:
                result = await BenchmarkRunner(backend).run_benchmark(suite)
            finally:
                kind = runtime_kind(backend)  # Capture before teardown clears deployment handles.
                try:
                    await asyncio.wait_for(backend.teardown(), 30)
                except Exception as exc:
                    teardown = f"failed:{type(exc).__name__}"
            result.teardown = teardown
            if teardown != "success":
                result.checks["teardown"] = False
                if result.evaluation == "pass":
                    result.evaluation = "fail"
            relevant_sdk = {"modal": "modal", "e2b": "e2b-code-interpreter", "aws": "boto3", "blaxel": "blaxel",
                "gemini_tool": "google-genai", "databricks": "databricks-sdk", "databricks_sandbox": "databricks-sdk",
                "daytona": "daytona-sdk", "openai_tool": "openai", "gcp_vertex": "agent-sandbox"}.get(backend.name)
            stack = {"python": common["client_python"], "sdk": relevant_sdk,
                     "version": common["sdk_versions"].get(relevant_sdk, "unrecorded CLI/SDK")}
            result.provenance = dict(common, **result.provenance, campaign_id=campaign_id, attempt=index,
                warmup=warmup, concurrency=concurrency, seed=seed, configuration=actual_config,
                config_id=config_id, runtime_kind=kind,
                adapter_sha256=adapter_sha,
                execution_stack=stack,
                stack_sha256=hashlib.sha256(json.dumps(stack, sort_keys=True).encode()).hexdigest(),
                capabilities_declared=asdict(backend.capabilities),
                timing_scope="initialize + prepare + execute + collect + cleanup; teardown separate",
                lifecycle="fresh_adapter_per_attempt; image cache state uncontrolled")
            if budget:
                result.provenance["budget_admission"] = dict(allowance_details, reserved_usd=float(allowance))
                budget.complete(allowance)
            append_attempt(output, result.model_dump())
            print(f"{backend.name}/{suite.name} #{index}: {result.evaluation} ({result.status}), {result.timings.total_wall_clock_ms:.1f}ms", flush=True)

    pending = []
    try:
        for wave in (warmup_jobs, jobs):
            pending = [asyncio.create_task(attempt(*job)) for job in wave]
            await asyncio.gather(*pending)
    except BaseException:
        interrupted = True
        for task in pending:
            if not task.done():
                task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        raise
    finally:
        duration = time.perf_counter() - started
        attempts = json.loads(output.read_text()) if output.exists() else []
        own = [r for r in attempts if r.get("provenance", {}).get("campaign_id") == campaign_id]
        measured = [r for r in own if not r["provenance"]["warmup"]]
        # Date shards still share reports/data/campaigns; custom outputs remain local.
        attempt_root = next((p for p in output.parents if p.name == "attempts"), None)
        data_root = attempt_root.parent if attempt_root else output.parent
        campaign_path = data_root / "campaigns" / f"{campaign_id}.json"
        campaign_path.parent.mkdir(parents=True, exist_ok=True)
        campaign_path.write_text(json.dumps({"campaign_id": campaign_id, "report_path": output.relative_to(data_root).as_posix(),
            "status": "interrupted" if interrupted else "budget_exhausted" if skipped_admissions else "completed",
            "wall_seconds_including_warmups": duration, "attempts": len(measured),
            "warmup_attempts": sum(r["provenance"]["warmup"] for r in own),
            "planned_attempts_including_warmups": len(warmup_jobs) + len(jobs),
            "budget_skipped_jobs": skipped_admissions, "budget": budget.snapshot() if budget else None,
            "passes": sum(r["evaluation"] == "pass" for r in measured), "concurrency": concurrency,
            "verified_completions_per_second_including_warmup_time": sum(r["evaluation"] == "pass" for r in measured) / duration}, indent=2))
    print(f"Campaign {campaign_id}: {len(measured)} measured attempts / {duration:.2f}s.")
    return attempts
