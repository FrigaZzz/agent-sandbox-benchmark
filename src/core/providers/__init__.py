"""Registry and factory for all sandbox execution backends."""
from .local_subprocess import LocalSubprocessBackend
from .gcp_vertex import GcpVertexBackend
from .modal import ModalBackend
from .blaxel import BlaxelBackend
from .databricks import DatabricksBackend
from .e2b import E2BBackend
from .gemini_tool import GeminiToolBackend
from .openai_tool import OpenAIToolBackend
from .daytona import DaytonaBackend
from .databricks_sandbox import DatabricksServerlessSandboxBackend
from .databricks_mcp import DatabricksMcpSandboxBackend
from .aws_agentcore import AWSAgentCoreBackend
from .k8s_agent_sandbox import KubernetesAgentSandboxBackend
from .alibaba import AlibabaBackend

BACKENDS = {
    "local": LocalSubprocessBackend,
    "gcp_vertex": GcpVertexBackend,
    "modal": ModalBackend,
    "blaxel": BlaxelBackend,
    "databricks": DatabricksBackend,
    "databricks_sandbox": DatabricksServerlessSandboxBackend,
    "databricks_mcp": DatabricksMcpSandboxBackend,
    "e2b": E2BBackend,
    "gemini_tool": GeminiToolBackend,
    "openai_tool": OpenAIToolBackend,
    "daytona": DaytonaBackend,
    "aws": AWSAgentCoreBackend,
    "bedrock_agentcore": AWSAgentCoreBackend,
    "k8s_agent_sandbox": KubernetesAgentSandboxBackend,
    "agent_sandbox": KubernetesAgentSandboxBackend,
    "kubernetes_sigs": KubernetesAgentSandboxBackend,
    "alibaba": AlibabaBackend,
    "opensandbox": AlibabaBackend,
    "agentrun": AlibabaBackend,
}


def get_backend(name: str, **kwargs):
    cls = BACKENDS.get(name.lower())
    if not cls:
        raise ValueError(f"Unknown backend '{name}'. Available: {list(BACKENDS.keys())}")
    return cls(**kwargs)
