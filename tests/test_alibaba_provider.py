"""Unit and integration tests for Alibaba OpenSandbox / AgentRun provider."""
import asyncio
import os
import unittest
from unittest.mock import MagicMock

from src.core.providers.alibaba import AlibabaBackend
from src.core.models import (
    ExecuteCodeRequest,
    PreparedExecution,
    ResolvedInputFile,
)


class TestAlibabaProvider(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.backend = AlibabaBackend(auto_spawn=True)
        await self.backend.initialize()

    async def asyncTearDown(self):
        await self.backend.teardown()

    async def test_health_check(self):
        resp = await self.backend._client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("alibaba/opensandbox", data.get("runtime", ""))

    async def test_command_execution(self):
        req = ExecuteCodeRequest(
            code="print('HELLO_FROM_ALIBABA_OPENSANDBOX')\nx = 21 * 2\nprint(f'CALC:{x}')"
        )
        prepared = PreparedExecution(
            run_id="test-run-alibaba-1",
            nonce="nonce-ali-1",
            root="/tmp/test-alibaba",
            request=req,
            inputs=[],
        )

        res = await self.backend.execute(prepared)
        self.assertEqual(res.status, "success")
        self.assertEqual(res.exit_code, 0)
        self.assertIn("HELLO_FROM_ALIBABA_OPENSANDBOX", res.stdout)
        self.assertIn("CALC:42", res.stdout)

    async def test_timeout_handling(self):
        req_timeout = ExecuteCodeRequest(code="import time\ntime.sleep(10)", timeout_seconds=2)
        prepared_timeout = PreparedExecution(
            run_id="test-run-alibaba-timeout",
            nonce="nonce-ali-to",
            root="/tmp/test-alibaba",
            request=req_timeout,
            inputs=[],
        )

        res_timeout = await self.backend.execute(prepared_timeout)
        self.assertEqual(res_timeout.status, "timed_out")
        self.assertEqual(res_timeout.exit_code, 124)

    async def test_file_upload_and_artifact_collection(self):
        payload = b"ALIBABA_OPENSANDBOX_PAYLOAD_TEST_999"
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
            run_id="test-run-alibaba-file",
            nonce="nonce-ali-file",
            root="/tmp/test-alibaba",
            request=req_file,
            inputs=[resolved_input],
        )

        await self.backend.prepare(prepared_file)
        res_file = await self.backend.execute(prepared_file)
        self.assertEqual(res_file.status, "success")
        self.assertIn("FILE_PROCESSED_SUCCESS", res_file.stdout)

        artifacts = await self.backend.collect_artifacts(prepared_file, res_file)
        self.assertGreaterEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].data.decode(), "alibaba_opensandbox_payload_test_999")

    async def test_opensandbox_sdk_models_and_connection(self):
        """Verify official opensandbox Python SDK integration and connection config."""
        from opensandbox.config.connection import ConnectionConfig
        from opensandbox.models import WriteEntry

        # Test ConnectionConfig creation
        cfg = ConnectionConfig(
            domain="127.0.0.1:8889",
            protocol="http",
            api_key=self.backend.api_key,
        )
        self.assertEqual(cfg.domain, "127.0.0.1:8889")
        self.assertEqual(cfg.protocol, "http")

        # Test WriteEntry model serialization
        entry = WriteEntry(path="/tmp/test.txt", data=b"hello", mode=644)
        self.assertEqual(entry.path, "/tmp/test.txt")
        self.assertEqual(entry.data, b"hello")


if __name__ == "__main__":
    unittest.main()
