"""Command-line interface for the Sandbox Benchmarking Suite."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .bench.suites import ALL_BENCHMARKS
from .bench.suites import REALISTIC_BENCHMARKS
from .core.providers import BACKENDS, get_backend
from .bench.leaderboard import calculate_leaderboard, generate_markdown_report


async def run_cmd(args: argparse.Namespace) -> None:
    names = set(args.suite.split(","))
    if "all" in names:
        names.update(b.name for b in ALL_BENCHMARKS)
        names.remove("all")
    if "realistic" in names:
        names.update(b.name for b in REALISTIC_BENCHMARKS)
        names.remove("realistic")
    unknown = names - {b.name for b in ALL_BENCHMARKS}
    if unknown:
        raise ValueError(f"Unknown suites: {sorted(unknown)}")
    suites_to_run = [b for b in ALL_BENCHMARKS if b.name in names]

    from .bench.campaign import run_campaign
    options = json.loads(Path(args.backend_options).read_text()) if args.backend_options else {}
    from .bench.configuration import ALLOWED_OPTIONS
    if not isinstance(options, dict) or set(options) - ALLOWED_OPTIONS.get(args.backend, set()):
        raise ValueError("Backend options contain unsupported keys; only documented non-credential configuration is accepted")
    await run_campaign(lambda: get_backend(args.backend, **options), suites_to_run,
        Path(args.output or f"reports/data/attempts/{datetime.now(timezone.utc):%Y-%m}/{args.backend}_evaluation.json"),
        repeats=args.repeats, warmups=args.warmups, concurrency=args.concurrency,
        config={"label": args.config_label}, seed=args.seed,
        budget_cap_usd=args.budget_cap_usd, budget_attempt_estimate_usd=args.budget_attempt_estimate_usd)



def leaderboard_cmd(args: argparse.Namespace) -> None:
    weights = {}
    if args.weights:
        for pair in args.weights.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                weights[k.strip()] = float(v.strip())

    suites = sorted({b.name for b in ALL_BENCHMARKS}) if args.suite == "all" else [args.suite]
    ranked = [score for suite in suites for score in calculate_leaderboard(weights if weights else None, suite=suite)]
    report = generate_markdown_report(ranked)
    print("\n" + report)

    if args.output:
        Path(args.output).write_text(report)
        print(f"✓ Saved leaderboard to {args.output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bench-sandboxes",
        description="Comprehensive AI Sandbox Benchmarking & Testing Suite",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run benchmark suites against a provider")
    run_parser.add_argument(
        "--backend",
        "-b",
        default="local",
        choices=list(BACKENDS.keys()),
        help="Target provider backend",
    )
    run_parser.add_argument(
        "--suite",
        "-s",
        default="realistic",
        help="Suite names separated by commas, 'realistic' (bounded workflows), or 'all' (includes memory/network probes)",
    )
    run_parser.add_argument(
        "--output",
        "-o",
        help="Path to save JSON benchmark results",
    )
    run_parser.add_argument("--repeats", type=int, default=5, help="Measured attempts per suite; never replace previous samples")
    run_parser.add_argument("--warmups", type=int, default=0, help="Excluded warmup attempts (also use fresh adapters)")
    run_parser.add_argument("--concurrency", type=int, default=1, help="Independent simultaneous adapter instances")
    run_parser.add_argument("--config-label", default="adapter-defaults", help="Region/image/resource/policy label; not proof of server configuration")
    run_parser.add_argument("--seed", type=int, default=42, help="Reproducible shuffled suite order")
    run_parser.add_argument("--backend-options", help="JSON file with non-credential Modal/E2B/Blaxel options; see methodology")
    run_parser.add_argument("--budget-cap-usd", help="Campaign-local estimated admission cap; includes warmups, not an invoice cap")
    run_parser.add_argument("--budget-attempt-estimate-usd", help="Conservative full-attempt USD allowance required for unpriceable configurations")

    # Leaderboard subcommand
    lb_parser = subparsers.add_parser("leaderboard", help="Generate weighted provider leaderboard")
    lb_parser.add_argument(
        "--weights",
        "-w",
        help="Measured dimensions only (e.g. latency=0.5,reliability=0.5)",
    )
    lb_parser.add_argument(
        "--output",
        "-o",
        help="Path to save Markdown leaderboard report",
    )
    lb_parser.add_argument("--suite", default="cold_start", help="Compare this workload (or 'all')")

    # Dashboard subcommand
    dash_parser = subparsers.add_parser("dashboard", help="Generate rich HTML decision matrix dashboard")
    dash_parser.add_argument(
        "--output",
        "-o",
        default="reports/index.html",
        help="Path to save interactive HTML dashboard report (default: reports/index.html)",
    )
    subparsers.add_parser("specs", help="Export common provider/configuration/runtime observation datasets")

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(run_cmd(args))
    elif args.command == "leaderboard":
        leaderboard_cmd(args)
    elif args.command == "dashboard":
        from .bench.dashboard import generate_dashboard_files
        out_file = generate_dashboard_files(args.output)
        print(f"✓ Generated interactive HTML decision dashboard at {out_file}")
    elif args.command == "specs":
        from .bench.specifications import export_specifications
        print(f"✓ Exported provider specifications to {export_specifications()}")



if __name__ == "__main__":
    main()
