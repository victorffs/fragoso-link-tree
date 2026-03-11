#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    (
        re.compile(r"https://webhooks\\.hostinger\\.com/deploy/[A-Za-z0-9]{20,}"),
        "https://webhooks.hostinger.com/deploy/<REDACTED>",
    ),
    (
        re.compile(r"(deploy/)[a-f0-9]{24,}"),
        r"\\1<REDACTED>",
    ),
    (
        re.compile(r"(Bearer\\s+)[A-Za-z0-9._\\-]{20,}"),
        r"\\1<REDACTED>",
    ),
    (
        re.compile(r"(?i)((api[_-]?key|token|secret)\\s*[:=]\\s*[\\\"']?)[A-Za-z0-9._\\-]{16,}"),
        r"\\1<REDACTED>",
    ),
]


def redact_content(content: str) -> tuple[str, int]:
    count = 0
    redacted = content
    for pattern, replacement in REPLACEMENTS:
        redacted, changed = pattern.subn(replacement, redacted)
        count += changed
    return redacted, count


def main() -> int:
    parser = argparse.ArgumentParser(description="Redact sensitive webhook/token values from files.")
    parser.add_argument("paths", nargs="+", help="File paths to redact")
    args = parser.parse_args()

    total_changes = 0
    for raw in args.paths:
        path = Path(raw).resolve()
        if not path.exists() or not path.is_file():
            print(f"Skipping missing file: {raw}")
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            print(f"Skipping non-text file: {raw}")
            continue

        redacted, changed = redact_content(content)
        if changed > 0:
            path.write_text(redacted, encoding="utf-8")
            total_changes += changed
            rel = path.relative_to(ROOT) if str(path).startswith(str(ROOT)) else path
            print(f"Redacted {changed} item(s) in {rel}")

    if total_changes == 0:
        print("No sensitive values found to redact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())