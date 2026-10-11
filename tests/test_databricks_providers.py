"""Unit tests verifying separation between Databricks SQL MCP and Databricks Serverless Sandboxes."""
import asyncio
import unittest
from unittest.mock import MagicMock, patch

from src.core.providers import get_backend
from src.core.providers.databricks import DatabricksBackend
from src.core.providers.databricks_sandbox import DatabricksServerlessSandboxBackend
from src.core.models import ExecuteCodeRequest, PreparedExecution, ResolvedInputFile


class TestDatabricksProvidersSeparation(unittest.IsolatedAsyncioTestCase):
    """Ensure Databricks SQL MCP and Databricks Dedicated Sandboxes are completely distinct providers."""

    def test_registry_registration(self):
        backend_sql = get_backend("databricks")
        backend_sandbox = get_backend("databricks_sandbox")

        self.assertIsInstance(backend_sql, DatabricksBackend)
        self.assertIsInstance(backend_sandbox, DatabricksServerlessSandboxBackend)

        self.assertEqual(backend_sql.name, "databricks")
        self.assertEqual(backend_sandbox.name, "databricks_sandbox")

    def test_capabilities_differentiation(self):
        sql_caps = DatabricksBackend.capabilities
        sb_caps = DatabricksServerlessSandboxBackend.capabilities

        # Databricks SQL MCP is stateless, zero-egress, no shell
        self.assertFalse(sql_caps.persistent_filesystem)
        self.assertFalse(sql_caps.shell_execution)
        self.assertFalse(sql_caps.has_internet_access)
        self.assertFalse(sql_caps.has_custom_packages)

        # Databricks Dedicated Sandboxes has full persistent FS, /bin/bash, egress, and pip
        self.assertTrue(sb_caps.persistent_filesystem)
        self.assertTrue(sb_caps.shell_execution)
        self.assertTrue(sb_caps.has_internet_access)
        self.assertTrue(sb_caps.has_custom_packages)

    async def test_databricks_sql_mock_execution(self):
        from databricks.sdk.service.sql import StatementState

        backend = DatabricksBackend(warehouse_id="test-wh-123")
        mock_client = MagicMock()
        mock_res = MagicMock()
        mock_res.status.state = StatementState.SUCCEEDED
        mock_res.statement_id = "stmt-123"
        mock_res.result.data_array = [["COMPUTED_OUTPUT_42\n"]]
        mock_client.statement_execution.execute_statement.return_value = mock_res
        backend._client = mock_client

        req = ExecuteCodeRequest(code="print('COMPUTED_OUTPUT_42')")
        prepared = PreparedExecution(run_id="run-sql-1", nonce="n1", root="/tmp/db-sql", request=req, inputs=[])

        res = await backend.execute(prepared)
        self.assertEqual(res.status, "success")
        self.assertIn("COMPUTED_OUTPUT_42", res.stdout)
        self.assertEqual(res.exit_code, 0)

    async def test_databricks_sandbox_mock_execution(self):
        backend = DatabricksServerlessSandboxBackend()
        mock_client = MagicMock()
        mock_sb_obj = MagicMock()
        mock_sb_obj.name = "agent-bench-sandbox-123"
        mock_client.sandbox.create_sandbox.return_value = mock_sb_obj

        mock_cmd_resp = MagicMock()
        mock_cmd_resp.stdout = "SANDBOX_MICROVM_RUN_SUCCESS\nPRIMES_FOUND:148933\n"
        mock_cmd_resp.stderr = ""
        mock_cmd_resp.exit_code = 0
        mock_client.sandbox.execute_command_sync.return_value = mock_cmd_resp
        backend._client = mock_client

        req = ExecuteCodeRequest(code="print('SANDBOX_MICROVM_RUN_SUCCESS')")
        prepared = PreparedExecution(run_id="run-sb-1", nonce="n2", root="/tmp/db-sb", request=req, inputs=[])

        res = await backend.execute(prepared)
        self.assertEqual(res.status, "success")
        self.assertIn("SANDBOX_MICROVM_RUN_SUCCESS", res.stdout)
        self.assertIn("PRIMES_FOUND:148933", res.stdout)
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(backend._sandbox_name, "agent-bench-sandbox-123")

        await backend.cleanup(prepared)
        mock_client.sandbox.delete_sandbox.assert_called_once_with(name="agent-bench-sandbox-123")


if __name__ == "__main__":
    unittest.main()
