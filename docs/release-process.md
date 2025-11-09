```markdown
# Release Process & Versioning

This document describes the automated, single-source-of-truth release steps used by the project. It is the published (docs/) companion to the internal branching strategy in `notes/GITHUB_Branching_Release_Strategy.md`.

Key artifacts created by the repository:

- `VERSION` (repo root) — single source of truth for the project version.
- `scripts/propagate_version.py` — helper script (Python) that reads `VERSION`, computes or applies metadata updates (Chart.yaml, src/__init__.py, Dockerfile). The script supports `--dry-run` to print unified diffs.
- NOTE: The previous `propagate-version` GitHub Actions workflow has been removed; propagation is expected to be run locally or via an explicitly-reviewed PR workflow.

Release steps (order: 1 → 2 → 3)

1) Single-source-of-truth version

- Maintain the version in the `VERSION` file at the repository root. This file is authoritative.
- When you want to create a release, update `VERSION` to the intended version (for example `0.2.0` or `0.2.0-alpha`).
- Use the propagate workflow to update tracked files and create the git tag automatically.

2) Automated changelog / release notes

- Use conventional commits across PRs to enable automated release note generation.
- Recommended: enable [Release Drafter](https://github.com/release-drafter/release-drafter) or run a `conventional-changelog` job in CI to draft release notes from merged PRs. The project provides a release notes template in `notes/RELEASE_NOTES_v0.2.0.md` (internal draft).
- The CI should publish a draft release when tags are pushed, then maintainers can edit and publish the final release notes before the GA tag is pushed.

3) Security and dependency scanning (gated checks)

- Add dependency / SCA scanning to CI (Dependabot alerts, Snyk, or OSS Index) and make scan results required checks for release merges.
- Add container image scanning (Trivy or GitHub Container Scanning) before images are published.
- Add static analysis (CodeQL/Bandit) as part of CI and include those status checks in branch protection rules.

Where to run the propagation

Local-first (recommended): run the propagation script locally and create a PR for review.

Use the `--dry-run` flag to preview exactly what would change (the script prints unified diffs):

```bash
# dry-run preview (no files changed)
python3 scripts/propagate_version.py --dry-run
```

If the diffs look good, run the script to apply changes (it will commit and tag):

```bash
# apply changes and create commit + tag (will push if remote is configured)
python3 scripts/propagate_version.py
```

Alternatively, prefer creating a `bump-version/*` or `release/*` branch, run the script locally on that branch, commit and push, open a PR for review, then merge and tag from `main` once approved.

Notes and best practices

- Keep `VERSION` at the repo root for discoverability and automation.
The `propagate_version.py` script is intentionally conservative: it updates `src/__init__.py`, `Chart.yaml` files, and `Dockerfile` if they exist. It supports a `--dry-run` mode to preview changes as unified diffs. If your repository uses different metadata locations, extend the script accordingly.

If you require automated pushes/tags from CI in the future, prefer the PR-creation pattern (Action opens a branch and PR) so changes are reviewed before being merged and tagged. For GA releases, a maintainer should perform the final tag signing and publishing step.

Suggested additions (future):

- Attach SBOM and signed artifacts to GA releases.
- Add a `release-drafter.yml` configuration to automate draft release notes.
- Add a `release` workflow that builds and publishes images and Helm charts only when a GA tag is pushed.

Useful links

- `VERSION` file: `/VERSION`
- Propagate script: `/scripts/propagate_version.sh`
- Propagate helper script: `/scripts/propagate_version.py`
- Branching & release strategy (notes, internal): `/notes/GITHUB_Branching_Release_Strategy.md`

``` 
