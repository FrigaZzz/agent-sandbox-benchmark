"""Regression checks for scientific correctness and campaign evidence retention."""
import asyncio
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.bench.campaign import run_campaign
from src.bench.evidence import evidence_bundle, load_evidence, summarize, wilson
from src.bench.leaderboard import calculate_leaderboard
from src.bench.dashboard import build_dashboard_html
from src.bench.findings import generate_findings
from src.bench.insights import measured_insights, provenance_gaps
from src.bench.runner import BenchmarkRunner, request_fingerprint
from src.bench.suites.artifact_roundtrip import ArtifactRoundtripBenchmark
from src.bench.suites.timeout_handling import TimeoutHandlingBenchmark
from src.bench.suites.workflows import (CrossCallStateBenchmark, DataPipelineBenchmark,
    DependencyInstallBenchmark, ErrorRecoveryBenchmark, OutputFidelityBenchmark, RepositoryTaskBenchmark)
from src.core.models import RawExecutionResult, ExecuteCodeRequest, InputFileRef
from src.core.providers.local_subprocess import LocalSubprocessBackend


class CorruptArtifactBackend(LocalSubprocessBackend):
    async def collect_artifacts(self, prepared, result):
        arts = await super().collect_artifacts(prepared, result)
        arts[0].data = b"silent corruption"
        return arts


class TestWorkloads(unittest.IsolatedAsyncioTestCase):
    async def test_initialization_timeout_cannot_pass_execution_deadline(self):
        class SetupTimeout(LocalSubprocessBackend):
            async def initialize(self):
                raise asyncio.TimeoutError()
        result = await BenchmarkRunner(SetupTimeout()).run_benchmark(TimeoutHandlingBenchmark)
        self.assertEqual(result.evaluation, "fail")
        self.assertEqual(result.steps, [])

    async def test_recovery_requires_filesystem_state_after_failure(self):
        class ResetAfterError(LocalSubprocessBackend):
            async def execute(self, prepared):
                raw = await super().execute(prepared)
                if raw.status == "failed":
                    Path(prepared.work_dir, "recovery_sentinel").unlink(missing_ok=True)
                return raw
        result = await BenchmarkRunner(ResetAfterError()).run_benchmark(ErrorRecoveryBenchmark)
        self.assertEqual(result.evaluation, "fail")
        self.assertIsNone(result.error)

    async def test_later_inputs_staged_and_fingerprinted(self):
        class LaterInput:
            name = "later_input"
            expected_metrics = {"value": "binary payload"}
            payload = b"binary payload"
            @classmethod
            def get_request(cls):
                return cls.get_requests()[0]
            @classmethod
            def get_requests(cls):
                return [ExecuteCodeRequest(code="print('step one')"), ExecuteCodeRequest(
                    code="import os, pathlib, json\nprint('BENCH_RESULT:'+json.dumps(dict(value=pathlib.Path(os.environ['INPUT_DIR'], 'later.bin').read_text())))",
                    input_files=[InputFileRef(artifact_name="later.bin", data=cls.payload)])]
        first = await BenchmarkRunner(LocalSubprocessBackend()).run_benchmark(LaterInput)
        self.assertEqual(first.evaluation, "pass")
        LaterInput.payload = b"different payload"
        second = await BenchmarkRunner(LocalSubprocessBackend()).run_benchmark(LaterInput)
        self.assertNotEqual(first.workload_sha256, second.workload_sha256)
        LaterInput.expected_metrics = {"value": "different payload"}
        third = await BenchmarkRunner(LocalSubprocessBackend()).run_benchmark(LaterInput)
        self.assertNotEqual(second.evaluation_contract_sha256, third.evaluation_contract_sha256)
        self.assertEqual(second.workload_sha256, third.workload_sha256)

    async def test_real_workflow_oracles(self):
        for suite in [DataPipelineBenchmark, DependencyInstallBenchmark, RepositoryTaskBenchmark,
                      OutputFidelityBenchmark, CrossCallStateBenchmark, ErrorRecoveryBenchmark]:
            with self.subTest(suite=suite.name):
                result = await BenchmarkRunner(LocalSubprocessBackend()).run_benchmark(suite)
                self.assertEqual(result.evaluation, "pass", result.model_dump())

    async def test_corrupt_artifact_cannot_pass_successful_execution(self):
        result = await BenchmarkRunner(CorruptArtifactBackend()).run_benchmark(ArtifactRoundtripBenchmark)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.evaluation, "fail")
        self.assertFalse(result.checks["artifact_bytes:transformed_output.txt"])

    async def test_campaign_retains_repetitions_and_owns_workers(self):
        instances = []
        def factory():
            backend = LocalSubprocessBackend()
            instances.append(backend)
            return backend
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data/attempts/runs.json"
            await run_campaign(factory, [CrossCallStateBenchmark], path, repeats=3, concurrency=2)
            await run_campaign(factory, [CrossCallStateBenchmark], path, repeats=1)
            data = json.loads(path.read_text())
            self.assertEqual(len(data), 4)
            self.assertEqual(len(set(r["run_id"] for r in data)), 4)
            self.assertTrue(all(r["evaluation"] == "pass" and r["teardown"] == "success" for r in data))
            self.assertEqual(len(set(map(id, instances))), 4)
            bundle = evidence_bundle(Path(tmp))
            self.assertEqual(len(bundle["attempts"]), 4)
            self.assertEqual(len(bundle["campaigns"]), 2)
            for campaign in bundle["campaigns"]:
                self.assertTrue((Path(tmp) / campaign["report_path"]).is_file())
                self.assertTrue((Path(tmp) / campaign["evidence_path"]).is_file())

    async def test_concurrent_campaigns_and_warmup_barrier(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runs.json"
            await asyncio.gather(
                run_campaign(LocalSubprocessBackend, [OutputFidelityBenchmark], path, repeats=2, warmups=2, concurrency=2),
                run_campaign(LocalSubprocessBackend, [OutputFidelityBenchmark], path, repeats=1))
            runs = json.loads(path.read_text())
            self.assertEqual(len(runs), 5)
            campaign = next(r["provenance"]["campaign_id"] for r in runs if r["provenance"]["warmup"])
            wave = [r["provenance"]["warmup"] for r in runs if r["provenance"]["campaign_id"] == campaign]
            self.assertEqual(wave, [True, True, False, False])


class TestEvidence(unittest.TestCase):
    def test_structured_report_inputs_exclude_derived_views(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory, run_id in [("data/attempts", "current"), ("data/legacy", "legacy"),
                                      ("data/derived", "generated"), ("variant", "ui-copy")]:
                path = root / directory / "runs.json"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps([dict(provider="modal", run_id=run_id, suite="cold_start")]))
            runs, issues = load_evidence(root)
            self.assertEqual(issues, [])
            self.assertEqual({r["run_id"] for r in runs}, {"current", "legacy"})
            self.assertTrue(all((root / r["report_path"]).is_file() for r in runs))

    def fixture_attempts(self, suite, stdout="", passed=True):
        fingerprint = hashlib.sha256(json.dumps(request_fingerprint(suite.get_request()), sort_keys=True).encode()).hexdigest()
        return [dict(provider="aws", run_id=f"run-{i}", report_path="runs.json", report_index=i,
            suite=suite.name, schema_version=2, started_at="2026-10-13T00:00:00Z",
            workload_sha256=fingerprint, evaluation_contract_sha256="contract", runtime_kind="remote_runtime",
            evaluation="pass" if passed else "fail", status="success", stdout=stdout,
            checks={"stdout_exact": passed}, cleanup="success", teardown="success",
            timings={"total_wall_clock_ms": 10}, provenance={"runtime_kind": "remote_runtime",
                "config_id": "setup", "adapter_sha256": "adapter", "stack_sha256": "stack"}) for i in range(5)]

    def test_insights_follow_output_and_do_not_assume_old_fixture_size(self):
        runs = self.fixture_attempts(OutputFidelityBenchmark, OutputFidelityBenchmark.payload[:-1], passed=False)
        insight = measured_insights({"attempts": runs, "summaries": summarize(runs)})[0]
        self.assertIn("131,071", insight["finding"])
        self.assertIn("final newline", insight["finding"])
        self.assertEqual(insight["returned_stdout_bytes"], [131071])
        self.assertEqual(insight["expected_stdout_bytes"], 131072)
        self.assertEqual(len(insight["evidence"]), 5)
        for r in runs:
            r["stdout"] = "other output"
            r["workload_sha256"] = "earlier-fixture"
        changed = measured_insights({"attempts": runs, "summaries": summarize(runs)})[0]
        self.assertNotIn("131,072", changed["finding"])
        self.assertNotIn("final newline", changed["finding"])
        self.assertEqual(changed["returned_stdout_bytes"], [len("other output".encode())])
        self.assertNotIn("expected_stdout_bytes", changed)

    def test_report_keeps_all_failed_readiness_and_has_no_absent_provider_claims(self):
        class Readiness:
            name = "cold_start"
            get_request = staticmethod(OutputFidelityBenchmark.get_request)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs.json").write_text(json.dumps(self.fixture_attempts(Readiness, passed=False)))
            generate_findings(root)
            body = (root / "docs/findings.md").read_text()
            self.assertIn("0 / 5 | — (0) | 10.0", body)
            self.assertNotIn("Blaxel stdout", body)
            self.assertNotIn("all five current", body)
            self.assertIn("run-0", body)

    def test_contract_hash_does_not_hide_provenance_gap(self):
        run = self.fixture_attempts(OutputFidelityBenchmark)[0]
        run["provenance"]["execution_stack"] = {"version": "unrecorded CLI/SDK"}
        self.assertIn("execution CLI/SDK version not recorded", provenance_gaps(run))

    def test_dashboard_encodes_untrusted_logs_and_bounds_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            injected = '</script><script>alert("bad")</script>'
            (path / 'logs.json').write_text(json.dumps([dict(provider='modal', run_id='x', suite='output_fidelity', stdout=injected+'x'*20000)]))
            html = build_dashboard_html(path)
            self.assertNotIn(injected, html)
            self.assertIn('display_previews', html)
            original = json.loads((path / 'logs.json').read_text())
            self.assertEqual(len(original[0]['stdout']), 20000+len(injected))

    def test_legacy_success_is_not_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "old.json").write_text(json.dumps([{"provider": "modal", "run_id": "a", "suite": "cold_start", "status": "success", "timings": {"total_wall_clock_ms": 1}}]))
            runs, _ = load_evidence(path)
            self.assertEqual(runs[0]["evaluation"], "unknown")
            self.assertEqual(summarize(runs)[0]["latency_ms"]["n"], 0)
            self.assertIsNone(calculate_leaderboard(reports_dir=path)[0].composite_score)

    def test_missing_reports_never_get_spec_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(calculate_leaderboard(reports_dir=Path(tmp)), [])

    def test_uncertainty_and_invalid_weights(self):
        self.assertLess(wilson(5, 5)[0], .6)
        for weights in [{"security": 1}, {"latency": -1}, {"latency": float('nan')}, {"latency": 0}]:
            with self.assertRaises(ValueError):
                calculate_leaderboard(weights)


if __name__ == '__main__':
    unittest.main()
