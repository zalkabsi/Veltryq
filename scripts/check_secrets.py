"""Small deterministic scan for common committed credential formats."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"glpat-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


def main() -> int:
    roots = [Path(argument) for argument in sys.argv[1:]] or [Path(".")]
    findings: list[str] = []
    for root in roots:
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if not path.is_file() or any(
                part in {".git", ".venv", "__pycache__"} for part in path.parts
            ):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if any(pattern.search(content) for pattern in PATTERNS):
                findings.append(str(path))
    if findings:
        for path in findings:
            print(f"Possible credential pattern in {path}")
        return 1
    print("No configured credential patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
