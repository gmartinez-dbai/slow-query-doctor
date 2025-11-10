#!/usr/bin/env python3
"""Update requirements.txt from pyproject.toml dependencies."""
import subprocess
import sys
import re

def main():
    # Use pip to resolve dependencies and get what would be installed
    result = subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--dry-run', '--quiet',
        '.[dev,test,docs]'
    ], capture_output=True, text=True, cwd='.')

    if result.returncode != 0:
        print('Failed to resolve dependencies:', result.stderr, file=sys.stderr)
        sys.exit(1)

    # Parse the output to extract package versions
    # Look for lines like "Would install package==version"
    packages = {}
    lines = result.stdout.split('\n') + result.stderr.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('Would install'):
            # Extract package names and versions from "Would install pkg1==v1 pkg2==v2 ..."
            parts = line.replace('Would install', '').strip().split()
            for part in parts:
                if '==' in part:
                    name, version = part.split('==', 1)
                    packages[name.lower()] = f'{name}=={version}'

    # Also check for any additional packages that might be mentioned
    # Look for patterns like "Collecting package==version"
    for line in lines:
        match = re.search(r'Collecting\s+([a-zA-Z0-9\-_.]+)==([a-zA-Z0-9\-_.]+)', line)
        if match:
            name, version = match.groups()
            packages[name.lower()] = f'{name}=={version}'

    # Write to requirements.txt
    with open('requirements.txt', 'w') as f:
        for pkg in sorted(packages.values()):
            f.write(pkg + '\n')

    print('✅ requirements.txt updated!')

if __name__ == '__main__':
    main()