"""Publication-safe cloud configuration must come from the caller."""
import os
import unittest
from unittest.mock import patch

from src.core.models import ExecuteCodeRequest, PreparedExecution
from src.core.providers.aws_agentcore import AWSAgentCoreBackend
from src.core.providers.gemini_tool import GeminiToolBackend


class TestProviderConfiguration(unittest.IsolatedAsyncioTestCase):
    async def test_aws_missing_tool_fails_before_sdk_initialization(self):
        with patch.dict(os.environ, {}, clear=True):
            backend = AWSAgentCoreBackend()
            self.assertIsNone(backend.tool_id)
            with self.assertRaisesRegex(ValueError, "AWS_BEDROCK_AGENTCORE_TOOL_ID"):
                await backend.initialize()
            self.assertIsNone(backend._client)

    def test_aws_explicit_tool_overrides_environment(self):
        with patch.dict(os.environ, {"AWS_BEDROCK_AGENTCORE_TOOL_ID": "environment-tool"}, clear=True):
            self.assertEqual(AWSAgentCoreBackend().tool_id, "environment-tool")
            self.assertEqual(AWSAgentCoreBackend(tool_id="caller-tool").tool_id, "caller-tool")

    async def test_gemini_missing_project_does_not_construct_cloud_client(self):
        prepared = PreparedExecution(run_id="test", nonce="test", root="unused",
                                     request=ExecuteCodeRequest(code="print(42)"), inputs=[])
        # The optional SDK need not be installed to check this configuration path.
        from types import ModuleType
        google = ModuleType("google")
        genai = ModuleType("google.genai")
        genai.types = ModuleType("google.genai.types")
        google.genai = genai
        with patch.dict(os.environ, {}, clear=True), patch.dict(
            "sys.modules", {"google": google, "google.genai": genai, "google.genai.types": genai.types}
        ), patch.object(genai, "Client", create=True) as client:
            result = await GeminiToolBackend().execute(prepared)
            self.assertEqual(result.status, "failed")
            self.assertIn("GOOGLE_CLOUD_PROJECT", result.stderr)
            client.assert_not_called()
