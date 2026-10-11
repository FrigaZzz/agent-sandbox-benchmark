"""Unit tests for the Databricks AI Gateway MCP sandbox backend (mocked HTTP)."""
import io
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.providers.databricks_mcp import DatabricksMcpSandboxBackend, RUN_CODE_TOOL
from src.core.models import ExecuteCodeRequest, PreparedExecution


def _fake_urlopen(body, status=200):
    response = MagicMock()
    response.read.return_value = json.dumps(body).encode("utf-8")
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


def _prepared(code="print('hi')", language="python"):
    return PreparedExecution(
        run_id="test-run-dbx-mcp-1",
        nonce="nonce-dbx-1",
        root="/tmp/test-dbx-mcp",
        request=ExecuteCodeRequest(code=code, language=language),
        inputs=[],
    )


class TestDatabricksMcpBackend(unittest.IsolatedAsyncioTestCase):
    async def test_tools_call_success(self):
        backend = DatabricksMcpSandboxBackend()
        backend._endpoint = "https://host/ai-gateway/mcp-services/system.ai.sandbox"
        backend._auth_headers = {"Authorization": "Bearer test"}
        calls = []

        def fake_urlopen(request, timeout=None):
            payload = json.loads(request.data.decode("utf-8"))
            calls.append(payload["method"])
            if payload["method"] == "tools/list":
                return _fake_urlopen({"result": {"tools": [{"name": RUN_CODE_TOOL}]}})
            return _fake_urlopen({"result": {"content": [{"type": "text", "text": "hi\n"}],
                                                         "session_id": "sess-1"}})

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = await backend.execute(_prepared())
        self.assertEqual(calls, ["tools/list", "tools/call"])
        self.assertEqual(result.status, "success")
        self.assertEqual(result.stdout, "hi\n")
        self.assertEqual(result.manifest.get("mcp_session"), "sess-1")

    async def test_missing_tool_warns_but_calls(self):
        backend = DatabricksMcpSandboxBackend()
        backend._endpoint = "https://host/ai-gateway/mcp-services/system.ai.sandbox"
        backend._auth_headers = {"Authorization": "Bearer test"}

        def fake_urlopen(request, timeout=None):
            payload = json.loads(request.data.decode("utf-8"))
            if payload["method"] == "tools/list":
                return _fake_urlopen({"result": {"tools": [{"name": "other"}]}})
            return _fake_urlopen({"result": {"content": [{"type": "text", "text": "ok"}]}})

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = await backend.execute(_prepared())
        self.assertEqual(result.status, "success")
        self.assertTrue(any("missing_tool" in w for w in result.warnings))

    async def test_rpc_error_maps_to_failed(self):
        backend = DatabricksMcpSandboxBackend()
        backend._endpoint = "https://host/ai-gateway/mcp-services/system.ai.sandbox"
        backend._auth_headers = {"Authorization": "Bearer test"}
        with patch("urllib.request.urlopen",
                   return_value=_fake_urlopen({"error": {"message": "denied"}})):
            result = await backend.execute(_prepared())
        self.assertEqual(result.status, "failed")
        self.assertIn("denied", result.stderr)

    async def test_uninitialized_maps_to_failed(self):
        backend = DatabricksMcpSandboxBackend()
        with patch.object(backend, "initialize", new_callable=AsyncMock):
            result = await backend.execute(_prepared())
        self.assertEqual(result.status, "failed")
        self.assertIn("not initialized", result.stderr)


if __name__ == "__main__":
    unittest.main()
