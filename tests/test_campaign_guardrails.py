import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from src.bench.campaign import run_campaign
from src.bench.cost import attempt_budget_estimate
from src.bench.evidence import evidence_bundle
from src.bench.suites.workflows import CrossCallStateBenchmark
from src.core.providers.local_subprocess import LocalSubprocessBackend


class ControlledBackend(LocalSubprocessBackend):
    launched = 0

    async def initialize(self):
        type(self).launched += 1


class Guardrails(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_admission_counts_warmups_without_refunds(self):
        ControlledBackend.launched = 0
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "data/attempts/2026-10/runs.json"
            await run_campaign(ControlledBackend, [CrossCallStateBenchmark], output,
                repeats=6, warmups=1, concurrency=4, budget_cap_usd="0.25", budget_attempt_estimate_usd="0.10")
            bundle = evidence_bundle(tmp)
            self.assertEqual(ControlledBackend.launched, 2)
            self.assertEqual(len(bundle["attempts"]), 2)
            campaign = bundle["campaigns"][0]
            self.assertEqual(campaign["status"], "budget_exhausted")
            self.assertEqual(campaign["warmup_attempts"], 1)
            self.assertEqual(campaign["attempts"], 1)
            self.assertEqual(campaign["budget_skipped_jobs"], 5)
            self.assertEqual(campaign["budget"]["charged_estimate_usd"], .2)
            self.assertEqual(campaign["budget"]["in_flight_estimate_usd"], 0)
            self.assertTrue((Path(tmp) / campaign["report_path"]).exists())

    async def test_unknown_price_refused_before_initialization(self):
        class Unpriced(ControlledBackend):
            name = "unpriced-provider"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Cannot conservatively price"):
                await run_campaign(Unpriced, [CrossCallStateBenchmark], Path(tmp) / "runs.json", budget_cap_usd=1)
            self.assertFalse((Path(tmp) / "runs.json").exists())

    async def test_zero_admission_keeps_a_resolvable_empty_report(self):
        ControlledBackend.launched = 0
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "data/attempts/2026-10/runs.json"
            await run_campaign(ControlledBackend, [CrossCallStateBenchmark], output, repeats=2,
                budget_cap_usd=".01", budget_attempt_estimate_usd=".10")
            self.assertEqual(json.loads(output.read_text()), [])
            self.assertEqual(ControlledBackend.launched, 0)
            campaign = evidence_bundle(tmp)["campaigns"][0]
            self.assertTrue((Path(tmp) / campaign["report_path"]).is_file())
            self.assertEqual(campaign["budget_skipped_jobs"], 2)

    async def test_interruption_retains_attempt_and_cleanup(self):
        ready = asyncio.Event()
        cleaned = []
        class Hanging(LocalSubprocessBackend):
            async def initialize(self):
                ready.set()
                await asyncio.Event().wait()
            async def cleanup(self, prepared):
                cleaned.append("cleanup")
                await super().cleanup(prepared)
            async def teardown(self):
                cleaned.append("teardown")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "runs.json"
            task = asyncio.create_task(run_campaign(Hanging, [CrossCallStateBenchmark], output, repeats=3))
            await ready.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            attempts = json.loads(output.read_text())
            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0]["evaluation"], "fail")
            self.assertIn("interrupted", attempts[0]["error"])
            self.assertEqual(cleaned, ["cleanup", "teardown"])
            campaign = json.loads(next((Path(tmp) / "campaigns").glob("*.json")).read_text())
            self.assertEqual(campaign["status"], "interrupted")

    async def test_nonfinite_and_nonpositive_caps_rejected(self):
        for cap in ("nan", "inf", "0", "-1"):
            with self.assertRaises(ValueError):
                await run_campaign(LocalSubprocessBackend, [CrossCallStateBenchmark], Path("unused.json"), budget_cap_usd=cap)

    def test_default_e2b_allowance_is_not_client_wall_time_cost(self):
        class E2B:
            name = "e2b"
            benchmark_configuration = {"session_ttl_seconds": 180, "template": None}
        amount, details = attempt_budget_estimate(E2B(), CrossCallStateBenchmark)
        self.assertGreater(float(amount), .01)
        self.assertFalse(details["billing_verified"])
