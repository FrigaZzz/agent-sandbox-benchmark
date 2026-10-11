# Gemini Built-In Code Execution Tool

## Overview & Architecture
Google Gemini models (via `google-genai` and Google Cloud Vertex AI) feature an integrated, model-managed **Code Execution** capability. Unlike standalone sandbox APIs where a user or application directly submits Python scripts to an HTTP endpoint, Gemini's code execution operates within the model's iterative generation loop.

### How It Works
1. When calling `client.models.generate_content(...)`, the developer enables the tool:
   ```python
   from google import genai
   from google.genai import types

   client = genai.Client()
   response = client.models.generate_content(
       model="gemini-2.5-flash",
       contents="Calculate the first 50 Fibonacci numbers and find their sum.",
       config=types.GenerateContentConfig(
           tools=[types.Tool(code_execution=types.ToolCodeExecution())]
       ),
   )
   ```
2. The Gemini model decides when code execution is beneficial, generates an `executable_code` part containing Python code, and signals execution.
3. Google Cloud runs the code in an isolated Jupyter kernel sandbox in the backend.
4. The output or error is captured and injected back into the model context as a `code_execution_result` part in the same API turn.
5. The model synthesizes the result and returns a final response to the user.

### Capabilities & Environmental Boundaries
- **Runtime**: Python 3 standard environment with pre-installed scientific libraries: `numpy`, `pandas`, `scipy`, `sympy`, `scikit-learn`, `matplotlib`.
- **Filesystem**: Ephemeral scratch directory per turn. Files written to disk do not persist across separate API requests.
- **Network Access**: **Strictly disabled** (no internet egress).
- **Shell Access**: **None**. Only standard Python code is executed.
- **Execution Limits**: 30-second execution timeout per block; memory limit (~1GB); stdout capped at ~50KB.
- **Standalone Execution Endpoint**: **Does NOT exist**. You cannot execute code without querying a Gemini model.

### Billing & Telemetry
- **Cost**: **Free / Included in token billing**. There is no separate per-second compute charge for the code sandbox. The developer only pays standard input and output token rates for the generated code and result text.
- **Observability**: Execution logs, stdout, stderr, and outcome (`OUTCOME_OK` / `OUTCOME_FAILED`) are returned in the response metadata.

### Benchmark Consideration
When benchmarking Gemini's tool execution against standalone sandboxes:
- Measure: Total round-trip latency (prompt -> code generation -> execution -> interpretation).
- Measure: Model accuracy in utilizing the tool vs. raw code execution runtime.
- Cost: Token count vs. compute-seconds in dedicated sandboxes.
