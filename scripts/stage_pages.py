"""Stage the portal with repository-relative source/provider links preserved."""
import argparse
import shutil
from pathlib import Path


def stage(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Staging destination must not exist (no destructive replacement)")
    if output == root or output in root.parents or output.is_relative_to(root / "reports"):
        raise ValueError("Invalid staging destination")
    output.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc", "*.lock", "*.tmp")
    for name in ("reports", "providers", "src", "scripts", "tests", "examples", "deploy", ".github"):
        shutil.copytree(root / name, output / name, ignore=ignore, symlinks=False)
    for name in ("readme.md", "index.html", "BENCHMARK_LOCATIONS.md", "CONTRIBUTING.md", "pyproject.toml",
                 "Dockerfile.runner", "compose.yaml", ".pre-commit-config.yaml"):
        shutil.copy2(root / name, output / name)
    (output / ".nojekyll").touch()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(stage(Path(__file__).resolve().parents[1], args.output))
