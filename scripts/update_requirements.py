#!/usr/bin/env python3
"""Generate a pinned requirements.txt from pyproject.toml using pip's
dry-run JSON report when available. This is intentionally conservative:
- prefer pip --report JSON when supported by the local pip version
- fallback to parsing pip text output heuristics
- final fallback: leave requirements.txt unchanged and exit non-zero

This script is used by `make update-requirements` and by the pre-commit
hook to keep `requirements.txt` in sync with `pyproject.toml` extras.
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Dict, List


def parse_pip_report_json(output: str) -> Dict[str, str]:
    """Parse pip --report JSON stdout and return mapping name.lower() -> 'Name==Version'."""
    packages: Dict[str, str] = {}
    try:
        report = json.loads(output)
    except Exception:
        return packages

    for entry in report.get("install", []):
        meta = entry.get("metadata") or {}
        name = meta.get("name")
        version = meta.get("version")
        if name and version:
            packages[name.lower()] = f"{name}=={version}"
    return packages


def parse_pip_text(lines: List[str]) -> Dict[str, str]:
    """Heuristic parser for older pip textual dry-run output.
    Looks for lines like "Would install pkg==ver" or "Collecting pkg==ver".
    """
    import re

    packages: Dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # "Would install pkg==1.2.3 pkg2==4.5.6"
        if line.startswith("Would install"):
            parts = line.replace("Would install", "").strip().split()
            for part in parts:
                if "==" in part:
                    name, version = part.split("==", 1)
                    packages[name.lower()] = f"{name}=={version}"
        # "Collecting pkg==1.2.3"
        m = re.search(r"Collecting\s+([A-Za-z0-9_.-]+)==([A-Za-z0-9_.-]+)", line)
        if m:
            name, version = m.groups()
            packages[name.lower()] = f"{name}=={version}"
    return packages


def main() -> int:
    extras_spec = "[dev,test,docs]"

    # First, try pip's machine-readable report (preferred)
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--dry-run", "--report", "-", f".{extras_spec}"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    except Exception as exc:
        print("Failed to run pip:", exc, file=sys.stderr)
        return 2

    packages: Dict[str, str] = {}

    if proc.returncode == 0 and proc.stdout:
        packages = parse_pip_report_json(proc.stdout)

    # If JSON parsing didn't find anything, try heuristic text parsing
    if not packages:
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        packages = parse_pip_text(combined.splitlines())

    # Final fallback: try pip-compile if available
    if not packages:
        try:
            cmd2 = [sys.executable, "-m", "piptools.scripts.compile", "--extra", "dev", "--extra", "test", "--extra", "docs", "pyproject.toml"]
            proc2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=".")
            if proc2.returncode == 0 and proc2.stdout:
                for line in proc2.stdout.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "==" in line:
                        name, version = line.split("==", 1)
                        packages[name.lower()] = f"{name}=={version}"
        except FileNotFoundError:
            # pip-compile not installed; nothing more we can do
            pass

    if not packages:
        print("No packages detected; requirements.txt will not be updated.", file=sys.stderr)
        return 3

    # Write requirements.txt with stable ordering
    try:
        with open("requirements.txt", "w", encoding="utf8") as fh:
            for req in sorted(packages.values(), key=lambda s: s.lower()):
                fh.write(req + "\n")
    except Exception as exc:
        print("Failed to write requirements.txt:", exc, file=sys.stderr)
        return 4

    print("✅ requirements.txt updated! ({} packages)".format(len(packages)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())