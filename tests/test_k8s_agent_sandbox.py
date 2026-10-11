"""Unit and integration tests for kubernetes-sigs/agent-sandbox provider."""
import asyncio
import os
import unittest
from unittest.mock import MagicMock

from src.core.providers.k8s_agent_sandbox import KubernetesAgentSandboxBackend
from src.core.models import (
    ExecuteCodeRequest,
    PreparedExecution,
    ResolvedInputFile,
)


class TestKubernetesAgentSandbox(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.backend = KubernetesAgentSandboxBackend(auto_spawn=True)
        await self.backend.initialize()

    async def asyncTearDown(self):
        await self.backend.teardown()

    async def test_health_check(self):
        resp = await self.backend._client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("kubernetes-sigs", data.get("runtime", ""))

    async def test_command_execution(self):
        req = ExecuteCodeRequest(code="print('HELLO_FROM_AGENT_SANDBOX')\nx = 10 * 42\nprint(f'CALC:{x}')")
        prepared = PreparedExecution(
            run_id="test-run-1",
            nonce="nonce123",
            root="/tmp/test-k8s",
            request=req,
            inputs=[],
        )

        res = await self.backend.execute(prepared)
        self.assertEqual(res.status, "success")
        self.assertEqual(res.exit_code, 0)
        self.assertIn("HELLO_FROM_AGENT_SANDBOX", res.stdout)
        self.assertIn("CALC:420", res.stdout)

    async def test_timeout_handling(self):
        req_timeout = ExecuteCodeRequest(code="import time\ntime.sleep(10)", timeout_seconds=2)
        prepared_timeout = PreparedExecution(
            run_id="test-run-timeout",
            nonce="nonce-to",
            root="/tmp/test-k8s",
            request=req_timeout,
            inputs=[],
        )

        res_timeout = await self.backend.execute(prepared_timeout)
        self.assertEqual(res_timeout.status, "timed_out")
        self.assertEqual(res_timeout.exit_code, 124)

    async def test_file_upload_and_artifact_collection(self):
        payload = b"AGENT_SANDBOX_TEST_FILE_CONTENT_123"
        req_file = ExecuteCodeRequest(
            code=(
                "with open('input_test.txt', 'r') as f:\n"
                "    content = f.read()\n"
                "with open('transformed_output.txt', 'w') as f:\n"
                "    f.write(content.lower())\n"
                "print('FILE_PROCESSED_SUCCESS')\n"
            ),
            include_generated_artifacts=True,
        )

        resolved_input = ResolvedInputFile(
            artifact_name="input_test.txt",
            relative_path="input_test.txt",
            data=payload,
        )

        prepared_file = PreparedExecution(
            run_id="test-run-file",
            nonce="nonce-file",
            root="/tmp/test-k8s",
            request=req_file,
            inputs=[resolved_input],
        )

        await self.backend.prepare(prepared_file)
        res_file = await self.backend.execute(prepared_file)
        self.assertEqual(res_file.status, "success")
        self.assertIn("FILE_PROCESSED_SUCCESS", res_file.stdout)

        artifacts = await self.backend.collect_artifacts(prepared_file, res_file)
        self.assertGreaterEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].data.decode(), "agent_sandbox_test_file_content_123")

    async def test_sdk_integration(self):
        """Verify official k8s-agent-sandbox SDK integration with direct connection."""
        from k8s_agent_sandbox.sandbox import Sandbox
        from k8s_agent_sandbox.models import SandboxDirectConnectionConfig

        mock_k8s = MagicMock()
        sb = Sandbox(
            claim_name="bench-claim",
            sandbox_id="bench-sb-test",
            connection_config=SandboxDirectConnectionConfig(api_url=self.backend.api_url),
            k8s_helper=mock_k8s,
        )

        # 1. Test Files write & read via SDK
        sb.files.write("sdk_test.txt", b"Hello from k8s-agent-sandbox SDK")
        self.assertTrue(sb.files.exists("sdk_test.txt"))
        read_bytes = sb.files.read("sdk_test.txt")
        self.assertEqual(read_bytes, b"Hello from k8s-agent-sandbox SDK")

        # 2. Test Commands run via SDK
        cmd_result = sb.commands.run("cat sdk_test.txt")
        self.assertEqual(cmd_result.exit_code, 0)
        self.assertIn("Hello from k8s-agent-sandbox SDK", cmd_result.stdout)


if __name__ == "__main__":
    unittest.main()
