"""Read-only check of files Git would publish, including ZIP contents.

Reports locations and categories only, never matched credentials. Run from any
directory with Python 3.10+ and Git. Ignored files are excluded; tracked files
remain checked even if an ignore rule was added later.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "personal home path": re.compile(r"/(?:Users|home)/(?!(?:sandbox|oai|user|runner|bard)(?:/|\b))[^/\s\"']+"),
    "macOS temporary path": re.compile(r"/var/folders/[A-Za-z0-9_/.-]+"),
    "machine-specific file link": re.compile(r"file:[/]{3}"),
    "private reference link": re.compile(r"(?:\.\./|\]\()refs/"),
    "publication draft link": re.compile(r"(?:\.\./|\]\()tasks/"),
    "social publication material": re.compile(r"linked" r"in", re.I),
    "private workspace URL": re.compile(r"https://dbc-[a-z0-9-]+\.cloud\.databricks\.com"),
    "cloud account ARN": re.compile(r"arn:aws:[^\s\"']*:\d{12}:"),
    "provider credential": re.compile(
        r"\b(?:AIza[0-9A-Za-z_-]{35}|(?:AKIA|ASIA)[A-Z0-9]{16}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
        r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}|dapi[a-f0-9]{20,}|"
        r"LTAI[A-Za-z0-9]{12,}|e2b_[A-Za-z0-9_-]{20,}|ya29\.[A-Za-z0-9_-]{20,})\b"
    ),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "literal credential": re.compile(
        r'''(?i)(?:api_key|access_key_secret|client_secret|password|token)\s*[:=]\s*["']([A-Za-z0-9_+/=-]{24,})["']'''
    ),
    "JWT credential": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "personal cloud default": re.compile(r'''["'](?:project-[a-f0-9]{8}-[a-f0-9-]+|code_interpreter_tool_[A-Za-z0-9_-]+)["']'''),
}


def check_text(name: str, data: bytes) -> list[str]:
    if b"\0" in data:
        return []
    text = data.decode("utf-8", errors="replace")
    issues = []
    for category, pattern in PATTERNS.items():
        # Keep output bounded even when a generated HTML payload repeats a log.
        matches = list(pattern.finditer(text))
        if matches:
            lines = sorted({text.count("\n", 0, m.start()) + 1 for m in matches})
            issues.append(f"{name}:{','.join(map(str, lines[:8]))}: {category} ({len(matches)} matches)")
    return issues


def check_history() -> list[str]:
    """Check reachable historical blobs for credentials, without exposing values."""
    objects = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT).decode().splitlines()
    process = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    issues = []
    checked = 0
    try:
        for entry in objects:
            oid, _, name = entry.partition(" ")
            process.stdin.write((oid + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().decode().split()
            size = int(header[2])
            data = process.stdout.read(size)
            process.stdout.read(1)
            if header[1] != "blob":
                continue
            checked += 1
            text = data.decode("utf-8", errors="replace")
            for category in ["provider credential", "private key", "literal credential", "JWT credential"]:
                if PATTERNS[category].search(text):
                    issues.append(f"history {oid[:12]} {name}: {category}")
    finally:
        process.stdin.close()
        process.wait(timeout=10)
    print(f"Checked {checked} reachable historical blobs for credentials.")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true", help="Also check reachable Git history for credentials")
    args = parser.parse_args()
    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).decode().split("\0")
    issues = []
    checked = 0
    for name in sorted(set(files) - {""}):
        path = ROOT / name
        if not path.exists():  # A worktree deletion is not part of publication.
            continue
        if path.is_symlink():
            if not path.resolve().is_relative_to(ROOT):
                issues.append(f"{name}: symlink escapes repository")
            continue
        if path.is_dir():
            issues.append(f"{name}: nested checkout/gitlink requires removal or a configured submodule")
            continue
        if name.startswith(("refs/", "tasks/")) or path.name.startswith(".env") and path.name != ".env.example":
            issues.append(f"{name}: private/local file remains tracked")
        if path.stat().st_size >= 100 * 1024 * 1024:
            issues.append(f"{name}: exceeds GitHub's 100 MiB file limit")
        checked += 1
        issues.extend(check_text(name, path.read_bytes()))
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                for entry in archive.infolist():
                    if entry.is_dir():
                        continue
                    if entry.file_size > 100 * 1024 * 1024:
                        issues.append(f"{name}!{entry.filename}: oversized archive member")
                        continue
                    issues.extend(check_text(f"{name}!{entry.filename}", archive.read(entry)))
    print(f"Checked {checked} publication files (plus ZIP members).")
    if args.history:
        issues.extend(check_history())
    for issue in issues:
        print(issue)
    print("FAIL" if issues else "PASS: no detected credentials, personal paths or private/draft references.")
    raise SystemExit(bool(issues))


if __name__ == "__main__":
    main()
