#!/usr/bin/env python3
"""Reject private deployment details and likely secrets from public sources."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".rst", ".txt", ".toml", ".yaml", ".yml"}
IGNORED_PARTS = {"_build", "_dist", ".venv"}

# Split known deployment literals so this validator does not flag itself.
KNOWN_PRIVATE = (
    "gthiru" + "v1",
    "droid" + "-viu",
    "gokul" + "@",
    "viu" + "14",
)

PATTERNS = {
    "absolute user-home path": re.compile(r"/(?:home|Users)/[^/\s]+/"),
    "private IPv4 address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key block": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}


def source_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        yield path


def check(root: Path) -> list[str]:
    failures: list[str] = []
    for path in source_files(root):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{relative}:{line}: {label}")
        lowered = text.lower()
        for literal in KNOWN_PRIVATE:
            start = 0
            while True:
                index = lowered.find(literal.lower(), start)
                if index < 0:
                    break
                line = text.count("\n", 0, index) + 1
                failures.append(
                    f"{relative}:{line}: lab-specific identity {literal!r}"
                )
                start = index + len(literal)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    root = parser.parse_args().source.resolve()
    failures = check(root)
    if failures:
        print("Public-safety check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    count = sum(1 for _ in source_files(root))
    print(f"Public-safety check passed ({count} text sources).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
