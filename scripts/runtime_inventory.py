"""Run the packaged guest inventory fixture directly; no secret/environment dump."""
from pathlib import Path

code = Path(__file__).resolve().parents[1].joinpath("src/bench/suites/runtime_probe.py").read_text()
exec(compile(code, "runtime_probe.py", "exec"))
