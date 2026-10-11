# Amazon Bedrock AgentCore Code Interpreter Sandbox

## Overview & Architecture
Amazon Bedrock AgentCore provides a dedicated code interpreter service designed for autonomous AI agents. Unlike standard Bedrock Agent action groups, **AgentCore Code Interpreter** operates over dedicated ephemeral MicroVM containers managed via the `bedrock-agentcore` data plane and `bedrock-agentcore-control` plane.

---

## Configure your account
- **AWS Region**: set `AWS_REGION` (adapter default: `eu-north-1`).
- **Code Interpreter Tool ID**: set `AWS_BEDROCK_AGENTCORE_TOOL_ID` to the identifier returned for your interpreter; there is no account-specific default.
- **Execution Role ARN**: supply your own IAM role when creating the interpreter.
- **Trust Policy Principal**: `bedrock-agentcore.amazonaws.com`
- **Supported Languages**: Python, JavaScript, TypeScript

---

## Network Modes & Isolation

| Mode | Internet Access | Network Boundary | Recommended Use Case |
| :--- | :---: | :--- | :--- |
| **SANDBOX** | ❌ No general public egress | Restricted service network | Security evaluations, testing untrusted agent scripts |
| **PUBLIC** | 🌐 Yes | Outbound public HTTPS enabled | Agents needing live web/API access |
| **VPC (Private)** | 🔒 VPC Only | Attached directly to AWS Private VPC | Enterprise production, accessing internal RDS/APIs |

---

## Tool API Primitives (`bedrock-agentcore`)

### 1. Session Lifecycle
- **`start_code_interpreter_session`**: Allocates an ephemeral session (configurable from 15 minutes up to 8 hours).
- **`stop_code_interpreter_session`**: Destroys the microVM session and purges files.

### 2. File Operations
- **`writeFiles`**: Uploads up to 100 MB of files directly via API into the sandbox.
- **`listFiles`**: Lists files present in the current session.
- **`readFiles`**: Reads file content back from the sandbox.
- **`removeFiles`**: Deletes files inside the sandbox.
- **S3 Large Files**: Supports up to 5 GB via S3 staging (`aws s3 cp`).

### 3. Execution Operations
- **`executeCode`**: Runs Python, JavaScript, or TypeScript scripts in the sandbox.
- **`executeCommand`**: Runs shell commands directly within the sandbox.

---

## AWS CLI Control Plane
```bash
# Create a code interpreter tool
aws bedrock-agentcore-control create-code-interpreter \
  --region eu-north-1 \
  --name "my-code-interpreter" \
  --description "AI Sandbox Runtime" \
  --network-configuration '{"networkMode": "SANDBOX"}' \
  --execution-role-arn "$AGENTCORE_EXECUTION_ROLE_ARN"

# List code interpreters
aws bedrock-agentcore-control list-code-interpreters --region eu-north-1
```

---

## Python SDK Integration (`boto3`)
```python
import boto3, json, os

client = boto3.client("bedrock-agentcore", region_name="eu-north-1")
TOOL_ID = os.environ["AWS_BEDROCK_AGENTCORE_TOOL_ID"]

# 1. Start ephemeral sandbox session
session = client.start_code_interpreter_session(
    codeInterpreterIdentifier=TOOL_ID,
    name="bench-run",
    sessionTimeoutSeconds=900,
)
session_id = session["sessionId"]

# 2. Stage file
client.invoke_code_interpreter(
    codeInterpreterIdentifier=TOOL_ID,
    sessionId=session_id,
    name="writeFiles",
    arguments={"content": [{"path": "data.txt", "text": "benchmark payload"}]}
)

# 3. Execute script
response = client.invoke_code_interpreter(
    codeInterpreterIdentifier=TOOL_ID,
    sessionId=session_id,
    name="executeCode",
    arguments={"code": "with open('data.txt') as f: print(f.read().upper())", "language": "python"}
)

# 4. Stop session
client.stop_code_interpreter_session(
    codeInterpreterIdentifier=TOOL_ID,
    sessionId=session_id,
)
```

---

## ADK & Agnostic Core Integration
Implemented in [`src/core/providers/aws_agentcore.py`](../../src/core/providers/aws_agentcore.py) and registered as `"aws"`:
```python
from src.core.providers import get_backend
from src.core.adk_bridge import create_adk_tool

aws_backend = get_backend("aws")
adk_tool = create_adk_tool(aws_backend)
```
