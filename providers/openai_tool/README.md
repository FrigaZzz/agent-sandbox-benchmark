# OpenAI & Azure OpenAI Code Interpreter

## Overview & Architecture
OpenAI provides a managed **Code Interpreter** tool integrated into the Assistants API and the new Responses API. Like Gemini's code execution, the primary interaction pattern is model-driven: the LLM determines when code execution is needed, writes Python code, and inspects stdout/stderr to answer queries.

### How It Works
1. When defining an Assistant or creating a thread run, enable `{"type": "code_interpreter"}`:
   ```python
   assistant = client.beta.assistants.create(
       name="Data Analyst",
       instructions="Analyze user data files using Python.",
       tools=[{"type": "code_interpreter"}],
       model="gpt-4o",
   )
   ```
2. The model produces tool calls to the interpreter, which executes in a secure container.
3. Python plots and generated files (images, CSVs, PDFs) are saved as File objects and returned as `file_id` references.

### Capabilities & Environmental Boundaries
- **Runtime**: Python 3 sandbox with extensive data analysis libraries (`numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`, `openpyxl`, `docx`, `pdfminer`, etc.).
- **Filesystem**: Scoped to the session / thread container. Files uploaded to the thread or created during earlier turns remain available across subsequent turns in the same thread.
- **File Limits**: Max file size 512 MB per file; max 10 GB per assistant/organization.
- **Network Access**: **Strictly disabled** (sandboxes cannot connect to the internet).
- **Shell Access**: **None**. Execution is limited to Python script evaluations.
- **Direct Execution API**: OpenAI does not expose a raw HTTP endpoint to execute arbitrary code outside the assistant/model conversation lifecycle.

### Billing & Telemetry
- **Cost**:
  - **Session Fee**: $0.03 per active container session (per assistant thread per day).
  - **Token Costs**: Standard model token rates for prompt input and code output.
- **Telemetry**: Run steps report execution duration, code inputs, and text/image outputs.

### Benchmark Consideration
- Contrast with standalone microVMs (Modal/E2B/Blaxel): OpenAI handles file upload and conversion automatically, but lacks raw shell, package installation (`pip install`), custom image support, and external API connectivity.
