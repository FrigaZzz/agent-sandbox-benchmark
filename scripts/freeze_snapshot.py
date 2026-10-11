"""Freeze a content-hashed publication bundle without creating Git tags/releases."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_publication import check_text

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def freeze(root, destination):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if destination.is_relative_to(root / "reports"):
        raise ValueError("Snapshot cannot be inside its own report inputs")
    paths = [root / name for name in ("readme.md", "pyproject.toml", "CONTRIBUTING.md", "index.html")]
    paths.extend(root / name for name in ("Dockerfile.runner", "compose.yaml", ".pre-commit-config.yaml") if (root / name).exists())
    for directory in ("src", "providers", "reports", "scripts", "tests", "examples", ".github", "deploy"):
        paths.extend(p for p in (root / directory).rglob("*") if p.is_file()
                     and p.suffix in {".py", ".html", ".css", ".js", ".mjs", ".json", ".md", ".svg", ".pdf", ".png", ".yaml", ".yml"}
                     and "__pycache__" not in p.parts)
    payloads = {}
    for path in sorted(set(paths)):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Snapshot symlink/outside-root input refused")
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        issues = check_text(name, data)
        if issues:
            raise ValueError("Publication scan failed: " + "; ".join(issues))
        payloads[name] = data
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
    manifest = {"schema_version": 1, "git_revision": revision, "working_tree_dirty": dirty,
                "files": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in payloads.items()},
                "scope": "Frozen publication and implementation bytes; hashes attest integrity, not benchmark correctness"}
    encoded = json.dumps(manifest, sort_keys=True, indent=2).encode()
    manifest["snapshot_sha256"] = digest(encoded)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: a published snapshot is never overwritten.
    with destination.open("xb") as stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        payloads["snapshot-manifest.json"] = json.dumps(manifest, sort_keys=True, indent=2).encode()
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    verify(destination)
    return manifest["snapshot_sha256"]


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names) or any(PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts for n in names):
            raise ValueError("Unsafe or duplicate snapshot paths")
        manifest = json.loads(archive.read("snapshot-manifest.json"))
        identity = manifest.pop("snapshot_sha256")
        if digest(json.dumps(manifest, sort_keys=True, indent=2).encode()) != identity:
            raise ValueError("Snapshot manifest identity mismatch")
        if set(names) != set(manifest["files"]) | {"snapshot-manifest.json"}:
            raise ValueError("Snapshot membership mismatch")
        for name, evidence in manifest["files"].items():
            data = archive.read(name)
            if len(data) != evidence["bytes"] or digest(data) != evidence["sha256"]:
                raise ValueError(f"Snapshot content mismatch: {name}")
    return identity


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    print(verify(args.verify) if args.verify else freeze(ROOT, args.output))
