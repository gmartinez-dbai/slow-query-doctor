#!/usr/bin/env python3
"""Propagate repo VERSION into common files safely using ruamel.yaml.

Behavior:
- Read VERSION in repo root (single-line, e.g. 0.2.0)
- Update Chart.yaml files (appVersion and version) using ruamel.yaml
- Update src/__init__.py __version__ or version variables if present
- Update Dockerfile LABEL version="..." or append if missing
- Optionally verify all versions are consistent

Usage:
    python scripts/propagate_version.py           # Update all version references
    python scripts/propagate_version.py --verify # Verify versions are consistent
    python scripts/propagate_version.py --check  # Same as --verify
"""
import argparse
import os
import re
import subprocess
import sys
from glob import glob

try:
    from ruamel.yaml import YAML
except Exception:
    print("Missing ruamel.yaml. Please install it: pip install ruamel.yaml")
    raise


ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(ROOT)


def read_version():
    p = os.path.join(ROOT, "VERSION")
    if not os.path.isfile(p):
        print("VERSION file not found")
        sys.exit(1)
    return open(p, "r").read().strip()


def update_init_py(version):
    # Check multiple possible paths for __init__.py
    possible_paths = [
        os.path.join("src", "__init__.py"),
        os.path.join("slowquerydoctor", "__init__.py"),
        "__init__.py",
    ]

    updated = False
    for path in possible_paths:
        if not os.path.isfile(path):
            continue

        text = open(path, "r", encoding="utf8").read()
        new_text = re.sub(
            r"(__version__\s*=\s*\")(.*?)(\")", r"\g<1>{}\g<3>".format(version), text
        )
        new_text = re.sub(
            r"(version\s*=\s*\")(.*?)(\")", r"\g<1>{}\g<3>".format(version), new_text
        )
        if new_text != text:
            open(path, "w", encoding="utf8").write(new_text)
            print(f"Updated {path}")
            updated = True

    return updated


def update_chart_yaml(version):
    yaml = YAML()
    updated = False
    charts = glob("**/Chart.yaml", recursive=True) + glob("Chart.yaml")
    for c in charts:
        if not os.path.isfile(c):
            continue
        with open(c, "r", encoding="utf8") as fh:
            data = yaml.load(fh) or {}
        changed = False
        if data.get("appVersion") != str(version):
            data["appVersion"] = str(version)
            changed = True
        if data.get("version") != str(version):
            data["version"] = str(version)
            changed = True
        if changed:
            with open(c, "w", encoding="utf8") as fh:
                yaml.dump(data, fh)
            print(f"Updated {c}")
            updated = True
    return updated


def update_pyproject_toml(version):
    """Update version in pyproject.toml"""
    path = "pyproject.toml"
    if not os.path.isfile(path):
        return False

    text = open(path, "r", encoding="utf8").read()
    new_text = re.sub(
        r'(version\s*=\s*")([^"]+)(")', r"\g<1>{}\g<3>".format(version), text
    )

    if new_text != text:
        open(path, "w", encoding="utf8").write(new_text)
        print(f"Updated {path}")
        return True
    return False


def update_dockerfile(version):
    updated = False
    for path in ("Dockerfile", "docker/Dockerfile"):
        if not os.path.isfile(path):
            continue
        text = open(path, "r", encoding="utf8").read()

        # Update all version references in Dockerfile
        new_text = text

        # Update environment variable
    new_text = re.sub(
        r"(SLOW_QUERY_DOCTOR_VERSION=)([^\s]+)", r"\g<1>{}".format(version), new_text
    )

    # Update LABEL version (all instances)
    new_text = re.sub(
        r'(version="?)([^"\s]+)("?)', r"\g<1>{}\g<3>".format(version), new_text
    )
    new_text = re.sub(
        r'(org\.opencontainers\.image\.version="?)([^"\s]+)("?)',
        r"\g<1>{}\g<3>".format(version),
        new_text,
    )

    if new_text != text:
        open(path, "w", encoding="utf8").write(new_text)
        print(f"Updated {path}")
        updated = True
    return updated


def git_commit_and_tag(version):
    try:
        subprocess.check_call(["git", "config", "user.name", "github-actions[bot]"])
        subprocess.check_call(
            [
                "git",
                "config",
                "user.email",
                "41898282+github-actions[bot]@users.noreply.github.com",
            ]
        )
    except subprocess.CalledProcessError:
        pass

    subprocess.check_call(["git", "add", "-A"])
    # Check if anything to commit
    status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
    if not status:
        print("No changes to commit")
        return False
        subprocess.check_call(
            [
                "git",
                "commit",
                "-m",
                (f"chore(release): propagate version {version} " "[skip ci]"),
            ]
        )
    tag = f"v{version}"
    subprocess.check_call(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
    subprocess.check_call(["git", "push", "origin", "HEAD"])
    subprocess.check_call(["git", "push", "origin", tag])
    print("Committed and pushed tag", tag)
    return True


def verify_versions():
    """Verify all version references match the VERSION file"""
    expected_version = read_version()
    print(f"Verifying all versions match: {expected_version}")

    issues = []

    # Check __init__.py files
    possible_paths = [
        os.path.join("src", "__init__.py"),
        os.path.join("slowquerydoctor", "__init__.py"),
        "__init__.py",
    ]

    for path in possible_paths:
        if not os.path.isfile(path):
            continue
        text = open(path, "r", encoding="utf8").read()

        # Check __version__
        match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
        if match and match.group(1) != expected_version:
            issues.append(
                f'{path}: __version__ = "{match.group(1)}" '
                f'(expected "{expected_version}")'
            )

        # Check version variable
        match = re.search(r'version\s*=\s*"([^"]+)"', text)
        if match and match.group(1) != expected_version:
            issues.append(
                f'{path}: version = "{match.group(1)}" '
                f'(expected "{expected_version}")'
            )

    # Check pyproject.toml
    if os.path.isfile("pyproject.toml"):
        text = open("pyproject.toml", "r", encoding="utf8").read()
        match = re.search(r'version\s*=\s*"([^"]+)"', text)
        if match and match.group(1) != expected_version:
            issues.append(
                f'pyproject.toml: version = "{match.group(1)}" '
                f'(expected "{expected_version}")'
            )

    # Check Dockerfile
    for path in ("Dockerfile", "docker/Dockerfile"):
        if not os.path.isfile(path):
            continue
        text = open(path, "r", encoding="utf8").read()

        # Check environment variable
        match = re.search(r"SLOW_QUERY_DOCTOR_VERSION=([^\s]+)", text)
        if match and match.group(1) != expected_version:
            issues.append(
                f"{path}: SLOW_QUERY_DOCTOR_VERSION={match.group(1)} "
                f"(expected {expected_version})"
            )

        # Check version labels
        matches = re.findall(r'version="?([^"\s]+)"?', text)
        for version_found in matches:
            if version_found != expected_version:
                issues.append(
                    f'{path}: version="{version_found}" '
                    f'(expected "{expected_version}")'
                )

    if issues:
        print("❌ Version inconsistencies found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ All versions are consistent!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Propagate or verify version consistency"
    )
    parser.add_argument(
        "--verify",
        "--check",
        action="store_true",
        help="Verify all versions match instead of updating",
    )

    args = parser.parse_args()

    if args.verify:
        success = verify_versions()
        sys.exit(0 if success else 1)
    else:
        # Update mode
        version = read_version()
        print("Propagating version", version)
        changed_any = False
        if update_init_py(version):
            changed_any = True
        if update_pyproject_toml(version):
            changed_any = True
        if update_chart_yaml(version):
            changed_any = True
        if update_dockerfile(version):
            changed_any = True
        if changed_any:
            print("Files updated successfully")
            # Note: Removed auto-commit for manual control
        else:
            print("No files changed; nothing to do")


if __name__ == "__main__":
    main()
