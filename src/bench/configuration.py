"""Allowlisted requested configuration; never serialize backend credentials."""
from __future__ import annotations


ALLOWED_OPTIONS = {
    "modal": {"cpu", "memory", "image", "python_version", "gpu", "runtime", "region", "block_network", "session_ttl_seconds"},
    "e2b": {"template", "allow_internet_access", "session_ttl_seconds"},
    "blaxel": {"image", "memory", "region", "ttl"},
    "databricks_mcp": {"service"},
    "alibaba": {"image", "cpu", "memory", "auto_spawn"},
}


def requested_configuration(backend):
    if hasattr(backend, "benchmark_configuration"):
        return backend.benchmark_configuration
    return {
        "gcp_vertex": {"product": "Agent Engine default code sandbox", "image": "provider-default",
                       "cpu": None, "memory": None, "gpu": None, "region": "CLI-configured; see preflight",
                       "network_policy": "not requested by adapter", "session_mode": "one-shot run"},
        "aws": {"product": "AgentCore Code Interpreter", "region": getattr(backend, "region", None),
                "image": "provider-default", "cpu": None, "memory": None, "gpu": None,
                "network_policy": "tool configuration not attested by adapter", "session_mode": "fresh session"},
        "databricks": {"product": "SQL system.ai.python_exec", "image": "provider-default",
                       "cpu": None, "memory": None, "gpu": None},
        "databricks_sandbox": {"product": "Dedicated Sandbox", "image": "Sandbox() defaults",
                                "cpu": None, "memory": None, "gpu": None,
                                "server_ttl": "not exposed by installed SandboxSpec; explicit delete required"},
        "gemini_tool": {"product": "Gemini code_execution", "model": getattr(backend, "model_name", None),
                        "image": "provider-default", "cpu": None, "memory": None, "gpu": None},
        "openai_tool": {"product": "OpenAI Assistants Code Interpreter", "model": getattr(backend, "model_name", None)},
        "daytona": {"product": "Daytona", "image": "client.create defaults", "cpu": None, "memory": None, "gpu": None,
                    "ttl_minutes": 15, "auto_stop_interval": 5, "auto_delete_interval": 0},
        "k8s_agent_sandbox": {"product": "HTTP endpoint adapter", "auto_spawn": getattr(backend, "auto_spawn", None),
                              "deployment_attested": False},
        "local_baseline": {"product": "host subprocess control", "resource_limits": None},
    }.get(backend.name, {"product": backend.name, "configuration": "unrecorded"})
