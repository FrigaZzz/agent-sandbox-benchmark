"""Read-only YAML/dispatch isolation check (requires PyYAML in the check environment)."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    paths = list((ROOT / ".github/workflows").glob("*.yml")) + [ROOT / "compose.yaml", ROOT / ".pre-commit-config.yaml"]
    documents = {path.name: yaml.load(path.read_text(), Loader=yaml.BaseLoader) for path in paths}
    ci = documents["ci.yml"]
    assert "pull_request" in ci["on"] and "pull_request_target" not in ci["on"]
    assert "secrets." not in (ROOT / ".github/workflows/ci.yml").read_text()
    live = documents["live-benchmark.yml"]
    assert set(live["on"]) == {"workflow_dispatch"}
    job = live["jobs"]["benchmark"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["environment"] == "benchmark"
    assert int(job["timeout-minutes"]) <= 30
    run = next(step for step in job["steps"] if step.get("name") == "Run reviewed fixtures")
    assert '--budget-cap-usd "$BUDGET"' in run["run"]
    assert "${{ inputs." not in run["run"]
    assert live["permissions"]["contents"] == "read"
    pages = documents["pages.yml"]
    assert pages["jobs"]["build"]["if"] == "github.ref == 'refs/heads/main'"
    assert pages["jobs"]["deploy"]["environment"]["name"] == "github-pages"
    print(f"PASS: {len(paths)} YAML files parse; PR secrets absent; live main/environment/budget isolation configured.")


if __name__ == "__main__":
    main()
