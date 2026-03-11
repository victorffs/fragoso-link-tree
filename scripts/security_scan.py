#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {
    ".md", ".txt", ".sh", ".py", ".yml", ".yaml", ".json", ".js", ".ts", ".html", ".css", ".env"
}

PATTERNS = [
    ("hostinger_webhook", re.compile(r"https://webhooks\.hostinger\.com/deploy/[A-Za-z0-9]{20,}")),
    ("deploy_hex_token", re.compile(r"deploy/[a-f0-9]{24,}")),
    ("bearer_token", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}")),
    ("generic_api_key", re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{16,}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

EXCLUDED_DIRS = {".git", "node_modules", "dist", "build", "__pycache__"}


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".env", ".env.local", ".env.production"}


def staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for raw in result.stdout.splitlines():
        p = (ROOT / raw).resolve()
        if p.exists() and p.is_file():
            files.append(p)
    return files


def repo_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def scan_paths(paths: list[Path]) -> list[tuple[str, Path, int, str]]:
    findings = []
    for path in paths:
        if not is_text_candidate(path):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for idx, line in enumerate(content.splitlines(), start=1):
            for name, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append((name, path, idx, line.strip()))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan repository files for sensitive tokens/webhooks.")
    parser.add_argument("paths", nargs="*", help="Optional file paths to scan")
    parser.add_argument("--staged", action="store_true", help="Scan only staged files")
    parser.add_argument("--all", action="store_true", help="Scan all repository files")
    args = parser.parse_args()

    if args.staged:
        paths = staged_files()
    elif args.paths:
        paths = [Path(p).resolve() for p in args.paths if Path(p).exists()]
    else:
        paths = repo_files() if args.all else staged_files()

    findings = scan_paths(paths)

    if not findings:
        print("No sensitive patterns found.")
        return 0

    print("Sensitive patterns detected:")
    for name, path, line_no, line in findings:
        rel = path.relative_to(ROOT)
        print(f"- {name}: {rel}:{line_no} -> {line}")

    print("\nRun: python scripts/redact_sensitive.py <file> [...] and re-add files.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
