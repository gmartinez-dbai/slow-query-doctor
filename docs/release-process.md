```markdown
# Release Process & Versioning

This document describes the automated, single-source-of-truth release steps used by the project. It is the published (docs/) companion to the internal branching strategy in `notes/GITHUB_Branching_Release_Strategy.md`.

Key artifacts created by the repository:


## Semantic Versioning and Pre-release Naming

The project follows [semantic versioning](https://semver.org/) for all releases. For PyPI compatibility, versions must follow [PEP 440](https://peps.python.org/pep-0440/) standards, which means **no 'v' prefix**.

### Version Format Examples:
- **Alpha releases:** `0.2.0a1`, `0.2.0a2`, ...
- **Beta releases:** `0.2.0b1`, `0.2.0b2`, ...
- **Release candidates:** `0.2.0rc1`, `0.2.0rc2`, ...
- **General availability:** `0.2.0`, `1.0.0`, etc.

### Important: PEP 440 Compliance
- **❌ Old format:** `v0.2.0-alpha.1` (not PyPI compatible)
- **✅ New format:** `0.2.0a1` (PEP 440 compliant)

The 'v' prefix is common in Git tags and GitHub releases, but PyPI requires PEP 440 format for `pyproject.toml` and package metadata. The version propagation script automatically handles this conversion.

Update the `VERSION` file with the appropriate version string before running the propagation workflow.
Release steps (order: 1 → 2 → 3)

1) Single-source-of-truth version

- Maintain the version in the `VERSION` file at the repository root. This file is authoritative.
- When you want to create a release, update `VERSION` to the intended version (for example `v0.2.0` or `v0.2.0-alpha`).
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


---

# DBA-Grade Branching Model for Release Lifecycle

Here’s a **DBA-grade, disciplined branching model** to move through the alpha → beta → RC → GA software release lifecycle. This keeps your repo clean and instantly signals project maturity to contributors and stakeholders.

| Phase  | Purpose                    | Branch Name        | Tag Example        | Actions                                               |
|--------|----------------------------|--------------------|--------------------|-------------------------------------------------------|
| α      | Initial unstable changes   | `feature/vX.Y.0`   | `vX.Y.0-alpha.N`   | All dev goes here. Frequent push/PR. Merge to develop.|
| β      | Feature complete, testable | `develop`          | `vX.Y.0-beta.N`    | Hardening, bugfixes, docs. No breaking features.      |
| RC     | Release Candidate          | `release/vX.Y.0`   | `vX.Y.0-rc.N`      | Finalize, critical/blocker fixes only.                |
| GA     | General Availability       | `main` (prod)      | `vX.Y.0`           | Merge release → main. Tag, deploy, announce.          |

---

## Step-by-step Branch Flow

1. **Alpha**
	- All **new code** starts in `feature/vX.Y.0` branches (per-feature, then aggregate).
	- Merge to a shared `develop` branch when features begin to combine.
	- Tag as `vX.Y.0-alpha.1`, `vX.Y.0-alpha.2`, etc.

2. **Beta**
	- Once features are “locked,” create `develop` as your main **integration branch**.
	- No *new* features—just stabilization.
	- CI runs here. Tag as `vX.Y.0-beta.1`, etc.

3. **Release Candidate (RC)**
	- When close to production: cut `release/vX.Y.0` from `develop`.
	- Only bugfixes, release notes, and doc changes permitted.
	- Tag as `vX.Y.0-rc.1`, `rc.2`, etc.
	- If blockers, fix in `release/vX.Y.0` and merge back to `develop`.

4. **General Availability (GA)**
	- Final, stable release: merge `release/vX.Y.0` → `main`.
	- Tag as `vX.Y.0` (no suffix).
	- Deploy, announce, maintain bugfixes as patch branches.

---

## Quick Git View

- **feature/v0.2.0** (early work, unstable)  
 ↳ **develop** (integration, beta)  
  ↳ **release/v0.2.0** (RC + hotfix)  
   ↳ **main** (GA, production)

---

**TL;DR:**
- Major WIP: `feature/`
- Beta: `develop`
- Release Candidate: `release/`
- Production: `main`

Let me know if you want git commands or a one-line workflow for creating branches or tags!

---

## Basic Git Workflow Actions

### Alpha (feature branch)
```bash
# Create a new feature branch for alpha development
git checkout -b feature/v0.2.0
# Push changes
git push -u origin feature/v0.2.0
# Tag alpha release (VERSION file uses 'v' prefix)
git tag v0.2.0-alpha.1
git push origin v0.2.0-alpha.1
```

### Beta (develop branch)
```bash
# Merge feature branch into develop
git checkout develop
git merge feature/v0.2.0
# Tag beta release
git tag v0.2.0-beta.1
git push origin v0.2.0-beta.1
```

### Release Candidate (release branch)
```bash
# Create release branch from develop
git checkout -b release/v0.2.0 develop
# Tag RC release
git tag v0.2.0-rc.1
git push origin v0.2.0-rc.1
```

### General Availability (main branch)
```bash
# Merge release branch into main
git checkout main
git merge release/v0.2.0
# Tag GA release
git tag v0.2.0
git push origin v0.2.0
```
``` 
