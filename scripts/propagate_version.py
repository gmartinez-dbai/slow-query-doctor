#!/usr/bin/env python3
"""Propagate repo VERSION into common files safely using ruamel.yaml.

Behavior:
- Read VERSION in repo root (single-line, e.g. 0.2.0)
- Update Chart.yaml files (appVersion and version) using ruamel.yaml
- Update src/__init__.py __version__ or version variables if present
- Update Dockerfile LABEL version="..." or append if missing
- Commit changes and create a tag v{VERSION}
"""
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


def validate_version_consistency(version):
    # Check all docs for version consistency
    docs_errors = []
    docs_dir = os.path.join(ROOT, 'docs')
    for root, _, files in os.walk(docs_dir):
        for fname in files:
            if fname.endswith('.md') or fname.endswith('.rst'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf8') as f:
                    content = f.read()
                    # Look for version strings like v0.x.x, 0.x.x, alpha, beta, rc
                    import re
                    pattern = r'(v?\d+\.\d+\.\d+(-alpha\.\d+|-beta\.\d+|-rc\.\d+)?)'
                    matches = re.findall(pattern, content)
                    for m in matches:
                        if version not in m:
                            docs_errors.append(f"{fpath}: found version string '{m}' not matching VERSION '{version}'")
    if docs_errors:
        print("[PRE-COMMIT] Documentation version consistency issues:")
        for err in docs_errors:
            print("  -", err)
        print("[PRE-COMMIT] Please update documentation version references to match VERSION file.")
        sys.exit(2)
    errors = []
    # Validate __init__.py
    init_path = os.path.join('slowquerydoctor', '__init__.py')
    if os.path.isfile(init_path):
        text = open(init_path, 'r', encoding='utf8').read()
        match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
        if match and match.group(1) != version:
            errors.append(f"slowquerydoctor/__init__.py version '{match.group(1)}' does not match VERSION '{version}'")
    # Validate Dockerfile LABEL version and ENV SLOW_QUERY_DOCTOR_VERSION
    docker_path = 'Dockerfile'
    if os.path.isfile(docker_path):
        text = open(docker_path, 'r', encoding='utf8').read()
        label_match = re.search(r'LABEL version="([^"]+)"', text)
        env_match = re.search(r'ENV SLOW_QUERY_DOCTOR_VERSION=([\w\.-]+)', text)
        image_label_match = re.search(r'org.opencontainers.image.version="([^"]+)"', text)
        if label_match and label_match.group(1) != version:
            errors.append(f"Dockerfile LABEL version '{label_match.group(1)}' does not match VERSION '{version}'")
        if env_match and env_match.group(1) != version:
            errors.append(f"Dockerfile ENV SLOW_QUERY_DOCTOR_VERSION '{env_match.group(1)}' does not match VERSION '{version}'")
        if image_label_match and image_label_match.group(1) != version:
            errors.append(f"Dockerfile org.opencontainers.image.version '{image_label_match.group(1)}' does not match VERSION '{version}'")
    # Validate pyproject.toml version
    pyproject_path = 'pyproject.toml'
    if os.path.isfile(pyproject_path):
        text = open(pyproject_path, 'r', encoding='utf8').read()
        match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if match and match.group(1) != version:
            errors.append(f"pyproject.toml version '{match.group(1)}' does not match VERSION '{version}'")
    if errors:
        print("[PRE-COMMIT] Version consistency validation failed:")
        for err in errors:
            print("  -", err)
        print("[PRE-COMMIT] Please update all version fields to match VERSION file.")
        sys.exit(2)
    print(f"[PRE-COMMIT] Version consistency validated: All files match VERSION '{version}'.")

def read_version():
    p = os.path.join(ROOT, 'VERSION')
    if not os.path.isfile(p):
        print('VERSION file not found')
        sys.exit(1)
    return open(p, 'r').read().strip()


def update_init_py(version):
    path = os.path.join('src', '__init__.py')
    if not os.path.isfile(path):
        return False
    text = open(path, 'r', encoding='utf8').read()
    new_text = re.sub(r"(__version__\s*=\s*\")(.*?)(\")",
                      rf"\1{version}\3",
                      text)
    new_text = re.sub(r"(version\s*=\s*\")(.*?)(\")",
                      rf"\1{version}\3",
                      new_text)
    if new_text != text:
        open(path, 'w', encoding='utf8').write(new_text)
        print(f'Updated {path}')
        return True
    return False


def update_chart_yaml(version):
    yaml = YAML()
    updated = False
    charts = glob('**/Chart.yaml', recursive=True) + glob('Chart.yaml')
    for c in charts:
        if not os.path.isfile(c):
            continue
        with open(c, 'r', encoding='utf8') as fh:
            data = yaml.load(fh) or {}
        changed = False
        if data.get('appVersion') != str(version):
            data['appVersion'] = str(version)
            changed = True
        if data.get('version') != str(version):
            data['version'] = str(version)
            changed = True
        if changed:
            with open(c, 'w', encoding='utf8') as fh:
                yaml.dump(data, fh)
            print(f'Updated {c}')
            updated = True
    return updated


def update_dockerfile(version):
    updated = False
    for path in ('Dockerfile', 'docker/Dockerfile'):
        if not os.path.isfile(path):
            continue
        text = open(path, 'r', encoding='utf8').read()
        if re.search(r'LABEL\s+version=\".*?\"', text):
            new_text = re.sub(r'(LABEL\s+version=\")(.+?)(\")', rf"\1{version}\3", text)
        else:
            new_text = text + f"\nLABEL version=\"{version}\"\n"
        if new_text != text:
            open(path, 'w', encoding='utf8').write(new_text)
            print(f'Updated {path}')
            updated = True
    return updated


def git_commit_and_tag(version):
    try:
        subprocess.check_call(['git', 'config', 'user.name', 'github-actions[bot]'])
        subprocess.check_call(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'])
    except subprocess.CalledProcessError:
        pass

    subprocess.check_call(['git', 'add', '-A'])
    # Check if anything to commit
    status = subprocess.check_output(['git', 'status', '--porcelain']).decode().strip()
    if not status:
        print('No changes to commit')
        return False
    subprocess.check_call(['git', 'commit', '-m', f'chore(release): propagate version {version} [skip ci]'])
    tag = f'v{version}'
    subprocess.check_call(['git', 'tag', '-a', tag, '-m', f'Release {tag}'])
    subprocess.check_call(['git', 'push', 'origin', 'HEAD'])
    subprocess.check_call(['git', 'push', 'origin', tag])
    print('Committed and pushed tag', tag)
    return True


def main():
    version = read_version()
    print('Propagating version', version)
    validate_version_consistency(version)
    changed_any = False
    if update_init_py(version):
        changed_any = True
    if update_chart_yaml(version):
        changed_any = True
    if update_dockerfile(version):
        changed_any = True
    if changed_any:
        git_commit_and_tag(version)
    else:
        print('No files changed; nothing to do')


if __name__ == '__main__':
    main()
