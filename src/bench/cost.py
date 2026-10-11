"""Cost estimation and attribution engine for sandbox execution."""
from __future__ import annotations

from typing import Any
from decimal import Decimal
import math
import re
from .budget import positive_usd
from ..core.models import CostEstimate, ExecutionTiming, ResourceUsage

PROVIDER_RATES: dict[str, dict[str, Any]] = {
    "gcp_vertex": {
        "vcpu_per_second": 0.000045,
        "ram_gb_per_second": 0.000006,
        "default_vcpu": 2,
        "default_ram_gb": 4,
        "unit": "per-second compute + CMEK KMS",
    },
    "modal": {
        "vcpu_per_second": 0.0000288,
        "ram_gb_per_second": 0.0000036,
        "default_vcpu": 2,
        "default_ram_gb": 4,
        "unit": "per-second (vCPU + RAM)",
    },
    "blaxel": {
        "vcpu_per_second": 0.000035,
        "ram_gb_per_second": 0.000005,
        "default_vcpu": 2,
        "default_ram_gb": 4,
        "unit": "per-second microVM container",
    },
    "databricks": {
        "per_second_rate": 0.000025,
        "dbu_rate_usd": 0.07,
        "unit": "DBU (Databricks Units) Serverless SQL MCP",
    },
    "databricks_sandbox": {
        "per_second_rate": 0.000036,
        "default_vcpu": 4,
        "default_ram_gb": 8,
        "unit": "Databricks Serverless Sandbox MicroVM (4 vCPU / 8 GB)",
    },
    "e2b": {
        "per_second_rate": 0.000040,
        "unit": "per-second Firecracker microVM",
    },
    "daytona": {
        "per_second_rate": 0.000020,
        "unit": "per-second workspace instance (or self-hosted $0)",
    },
    "aws": {
        "per_second_rate": 0.000030,
        "unit": "AWS Bedrock / Firecracker compute",
    },
    "alibaba": {
        "per_second_rate": 0.000025,
        "unit": "AgentRun serverless compute",
    },
    "gemini_tool": {
        "per_second_rate": 0.0,
        "input_token_price_per_m": 0.075,
        "output_token_price_per_m": 0.30,
        "unit": "token-only (compute runtime free)",
    },
    "openai_tool": {
        "session_fee": 0.03,
        "input_token_price_per_m": 2.50,
        "output_token_price_per_m": 10.00,
        "unit": "$0.03/session + model tokens",
    },
}


def attempt_budget_estimate(backend, benchmark, explicit_usd=None) -> tuple[Decimal, dict]:
    """Conservative admission allowance, separate from historical attribution.

    Allow at least the declared sandbox TTL, plus 120s staging/startup and 120s
    cleanup/teardown, or all step deadlines plus that overhead, whichever is
    larger. This is an assumed lifetime, not a remotely enforced billing bound.
    Scalar Modal requests have no known autoscaling ceiling, custom E2B templates
    have unknown sizing, and other integrations lack complete pricing inputs.
    They fail closed unless the caller supplies a full-attempt USD allowance.
    """
    details = {"evidence": "conservative_estimate_unverified", "billing_verified": False,
               "limitations": "Compute-only published-rate assumptions; excludes storage, egress, plan fees, "
               "image builds and provider-internal retry amplification. Lifetime and termination are not attested."}
    if explicit_usd is not None:
        return positive_usd(explicit_usd), dict(details, source="explicit_full_attempt_allowance",
            limitations="Caller-supplied conservative allowance must include all resources, model/session fees, "
            "warmup work, internal retries and uncertain remote lifetimes; not independently verified.")
    if backend.name == "local_baseline":
        return Decimal(0), dict(details, source="local_control_no_provider_charge")
    c = getattr(backend, "benchmark_configuration", {})
    requests = getattr(benchmark, "get_requests", lambda: [benchmark.get_request()])()
    seconds = sum(r.timeout_seconds for r in requests) + 240
    rate = None
    if backend.name == "e2b" and not c.get("template") and c.get("session_ttl_seconds"):
        # Published default template, not guest-visible/attested allocations.
        seconds = max(seconds, _positive_number(c["session_ttl_seconds"]) + 240)
        rate = Decimal("0.000046")  # 2 vCPU + 4 GiB; no promotional/free-tier credit.
        details.update(resources={"vcpu": 2, "ram_gib": 4}, source="published_default_e2b_template")
    elif backend.name == "modal" and not c.get("gpu"):
        # Require requested hard maxima, not only lower-bound scalar requests.
        cpu, memory = c.get("cpu"), c.get("memory")
        if isinstance(cpu, (list, tuple)) and len(cpu) == 2 and isinstance(memory, (list, tuple)) and len(memory) == 2:
            cores, gib = _positive_number(cpu[1]), _positive_number(memory[1]) / 1024
            _positive_number(cpu[0])
            _positive_number(memory[0])
            if cpu[0] > cpu[1] or memory[0] > memory[1]:
                raise ValueError("Modal resource minima exceed maxima")
            seconds = max(seconds, _positive_number(c.get("session_ttl_seconds", 180)) + 240)
            # Physical core pricing, max documented region multiplier, 3x non-preemptible headroom.
            rate = (Decimal(str(cores)) * Decimal("0.00003942") + Decimal(str(gib)) * Decimal("0.00000667")) * Decimal("5.25")
            details.update(resources={"physical_cores_max": cores, "ram_gib_max": gib, "multiplier": 5.25},
                           source="modal_requested_hard_maxima")
    elif backend.name == "blaxel" and not c.get("gpu"):
        match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)", str(c.get("ttl", "")))
        if match:
            ttl = _positive_number(match[1]) * {"s": 1, "m": 60, "h": 3600}[match[2]]
            # Current adapter may create a sandbox per step; retain allowance for every one.
            seconds = max(seconds, ttl + 240) * len(requests)
            gb = _positive_number(c.get("memory")) / 1000  # MB API field; decimal GB conservative vs GiB.
            rate = Decimal(str(gb)) * Decimal("0.0000115")
            details.update(resources={"ram_gb": gb, "sandbox_count_allowance": len(requests)}, source="blaxel_ram_and_ttl")
    if rate is None:
        raise ValueError(f"Cannot conservatively price {backend.name}; supply --budget-attempt-estimate-usd "
                         "covering the full attempt (including retries and cleanup)")
    amount = Decimal(str(seconds)) * rate
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Attempt estimate must be positive and finite")
    return amount, dict(details, lifetime_seconds_allowance=seconds, rate_per_second_usd=float(rate))


def _positive_number(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Budget resource/lifetime assumptions must be positive and finite") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError("Budget resource/lifetime assumptions must be positive and finite")
    return number


def calculate_cost(
    provider: str,
    timings: ExecutionTiming,
    resources: ResourceUsage | None = None,
    tokens: dict[str, int] | None = None,
) -> CostEstimate:
    """Calculate realistic cost attribution for a sandbox run."""
    rates = PROVIDER_RATES.get(provider.lower())
    if rates is None:
        return CostEstimate(billing_unit="unknown", details={"evidence": "unpriced", "billing_verified": False})
    if provider in {"gemini_tool", "openai_tool"} and tokens is None:
        return CostEstimate(billing_unit="unknown model usage", details={
            "evidence": "missing_token_usage", "billing_verified": False,
            "limitations": "Token usage and actual container/session billing were not captured; no invented token counts."})
    duration_s = max(0.001, timings.total_wall_clock_ms / 1000.0)

    compute_cost = 0.0
    token_cost = 0.0
    session_fee = 0.0
    details: dict[str, Any] = {"duration_seconds": round(duration_s, 4)}

    if provider == "gemini_tool":
        tok_in = (tokens or {}).get("prompt_tokens", 500)
        tok_out = (tokens or {}).get("completion_tokens", 250)
        token_cost = (
            (tok_in / 1_000_000) * rates["input_token_price_per_m"]
            + (tok_out / 1_000_000) * rates["output_token_price_per_m"]
        )
        details.update({"prompt_tokens": tok_in, "completion_tokens": tok_out})
    elif provider == "openai_tool":
        session_fee = rates.get("session_fee", 0.03)
        tok_in = (tokens or {}).get("prompt_tokens", 800)
        tok_out = (tokens or {}).get("completion_tokens", 350)
        token_cost = (
            (tok_in / 1_000_000) * rates["input_token_price_per_m"]
            + (tok_out / 1_000_000) * rates["output_token_price_per_m"]
        )
        details.update({"session_fee": session_fee, "prompt_tokens": tok_in, "completion_tokens": tok_out})
    elif "vcpu_per_second" in rates:
        vcpu = rates.get("default_vcpu", 2)
        ram = rates.get("default_ram_gb", 4)
        compute_cost = duration_s * (
            vcpu * rates["vcpu_per_second"] + ram * rates["ram_gb_per_second"]
        )
        details.update({"vcpu": vcpu, "ram_gb": ram, "rate_per_sec": vcpu * rates["vcpu_per_second"] + ram * rates["ram_gb_per_second"]})
    else:
        rate = rates.get("per_second_rate", 0.00003)
        compute_cost = duration_s * rate
        details.update({"rate_per_sec": rate})

    total_cost = compute_cost + token_cost + session_fee

    return CostEstimate(
        compute_cost_usd=round(compute_cost, 7),
        token_cost_usd=round(token_cost, 7),
        session_fee_usd=round(session_fee, 4),
        total_cost_usd=round(total_cost, 7),
        billing_unit=rates.get("unit", "per-second"),
        details=details,
    )
