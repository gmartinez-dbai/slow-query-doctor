#!/usr/bin/env python3
"""Generate a pinned requirements.txt from pyproject.toml dependencies.

This script parses pyproject.toml to extract dependency names, then uses
pip show to get their currently installed versions. This ensures requirements.txt
stays in sync with both pyproject.toml and the actual installed environment.
"""
from __future__ import annotations

import subprocess
import sys
from typing import Dict


def main() -> int:
    # Parse pyproject.toml to get dependencies
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print(
                "tomllib/tomli not available; install with: pip install tomli",
                file=sys.stderr,
            )
            return 1

    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
    except Exception as exc:
        print(f"Failed to parse pyproject.toml: {exc}", file=sys.stderr)
        return 1

    # Collect all dependency names
    dep_names: set[str] = set()

    # Main dependencies
    for dep in pyproject.get("project", {}).get("dependencies", []):
        # Extract package name from spec like "package>=1.0.0"
        name = (
            dep.split()[0]
            .split(">=")[0]
            .split("==")[0]
            .split("<=")[0]
            .split("!=")[0]
            .split(";")[0]
            .strip()
        )
        dep_names.add(name.lower())

    # Optional dependencies
    for deps in pyproject.get("project", {}).get("optional-dependencies", {}).values():
        for dep in deps:
            name = (
                dep.split()[0]
                .split(">=")[0]
                .split("==")[0]
                .split("<=")[0]
                .split("!=")[0]
                .split(";")[0]
                .strip()
            )
            dep_names.add(name.lower())

    # Get installed versions using pip show
    packages: Dict[str, str] = {}
    for name in sorted(dep_names):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", name],
                capture_output=True,
                text=True,
                cwd=".",
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        packages[name] = f"{name}=={version}"
                        break
        except Exception:
            continue

    if not packages:
        print(
            "No packages detected; requirements.txt will not be updated.",
            file=sys.stderr,
        )
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
