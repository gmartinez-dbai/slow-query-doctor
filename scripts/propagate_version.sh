#!/usr/bin/env bash
set -euo pipefail

# Simple version propagation script.
# - Reads VERSION from repo root
# - Updates common files if present: src/__init__.py, Chart.yaml (root or helm/**/Chart.yaml), Dockerfile
# - Commits changes (if any) and exits with non-zero if commit fails

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "${repo_root}"

if [[ ! -f VERSION ]]; then
  echo "VERSION file not found"
  exit 1
fi

VERSION_VALUE=$(cat VERSION | tr -d '\n')
echo "Propagation: setting version -> ${VERSION_VALUE}"

changed=0

update_file() {
  local file="$1"
  local pattern="$2"
  local replace="$3"

  if [[ -f "$file" ]]; then
    if grep -qE "$pattern" "$file"; then
      echo "Updating $file"
      # Use perl for reliable in-place regex replace across platforms
      perl -0777 -pe "s/${pattern}/${replace}/mg" -i.bak "$file"
      rm -f "$file.bak"
      changed=1
    else
      echo "Pattern not found in $file; attempting to append or add label"
      # If Chart.yaml and doesn't have appVersion, try to add it
      if [[ "${file}" == *Chart.yaml* ]] && ! grep -q "appVersion" "$file"; then
        echo "appVersion: \"${VERSION_VALUE}\"" >> "$file"
        changed=1
      fi
    fi
  fi
}

# 1) src/__init__.py or similar: look for __version__ or version =
for f in src/__init__.py; do
  update_file "$f" "(__version__\s*=\s*\")([^"]+)(\")" "\$1${VERSION_VALUE}\$3"
  update_file "$f" "(version\s*=\s*\")([^"]+)(\")" "\$1${VERSION_VALUE}\$3"
done

# 2) Chart.yaml files: update appVersion and version fields
shopt -s globstar || true
for chart in **/Chart.yaml Chart.yaml; do
  if [[ -f "$chart" ]]; then
    update_file "$chart" "(appVersion:\s*\")([^"]+)(\")" "\$1${VERSION_VALUE}\$3"
    update_file "$chart" "(version:\s*\")([^"]+)(\")" "\$1${VERSION_VALUE}\$3"
  fi
done

# 3) Dockerfile: replace LABEL version="..." or add LABEL
for df in Dockerfile docker/Dockerfile; do
  if [[ -f "$df" ]]; then
    if grep -qE "LABEL\s+version=\"[^"]+\"" "$df"; then
      update_file "$df" "(LABEL\s+version=\")([^"]+)(\")" "\$1${VERSION_VALUE}\$3"
    else
      echo "Adding LABEL version=\"${VERSION_VALUE}\" to $df"
      echo -e "\nLABEL version=\"${VERSION_VALUE}\"" >> "$df"
      changed=1
    fi
  fi
done

if [[ "$changed" -eq 1 ]]; then
  echo "Changes detected; committing"
  git config user.name "github-actions[bot]" || true
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com" || true
  git add -A
  git commit -m "chore(release): propagate version ${VERSION_VALUE} [skip ci]"
  # create tag
  git tag -a "v${VERSION_VALUE}" -m "Release v${VERSION_VALUE}"
  git push origin --follow-tags
  echo "Committed and pushed changes with tag v${VERSION_VALUE}"
else
  echo "No changes to propagate"
fi

exit 0
