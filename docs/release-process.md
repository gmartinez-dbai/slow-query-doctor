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

Here's the **Git Flow branching model** used by the project to manage releases through development phases. This follows the standard Git Flow pattern with main, develop, feature, and release branches.

| Branch Type | Purpose | Naming Pattern | Example | When to Use |
|-------------|---------|----------------|---------|-------------|
| `main` | Production-ready code | `main` | `main` | Stable releases, hotfixes |
| `develop` | Integration branch | `develop` | `develop` | Feature integration, ongoing development |
| `feature/` | Individual features | `feature/description` | `feature/add-mysql-support` | New features, enhancements |
| `release/` | Release preparation | `release/vX.Y.Z` | `release/v1.0.0` | Final QA, bug fixes before release |
| `hotfix/` | Critical fixes | `hotfix/description` | `hotfix/security-patch` | Emergency production fixes |

---

## Step-by-step Branch Flow

1. **Feature Development**
   - Create `feature/*` branches from `develop`
   - Work on features independently
   - Merge back to `develop` when complete

2. **Release Preparation**
   - Create `release/*` branch from `develop` when features are ready
   - Perform final testing and bug fixes
   - Merge to `main` for production release

3. **Hotfixes**
   - Create `hotfix/*` branches from `main` for critical fixes
   - Merge back to both `main` and `develop`

---

## Quick Git View

- **develop** (integration branch)
  - **feature/user-auth** (feature work)
  - **feature/api-improvements** (feature work)
  - ↳ **release/v1.0.0** (release prep)
    - ↳ **main** (production)

---

**Branch Hierarchy:**
- `main` ← `release/*` ← `develop` ← `feature/*`
- Hotfixes branch from `main` and merge to both `main` and `develop`

---

## Step-by-step Branch Flow

1. **Feature Development**
   - Create `feature/*` branches from `develop` for new features
   - Work independently on features, push regular commits
   - Merge completed features back to `develop` via pull requests

2. **Release Preparation**
   - When features are ready for release, create `release/*` branch from `develop`
   - Perform final testing, bug fixes, and stabilization on release branch
   - Only critical fixes and documentation updates allowed on release branches

3. **Production Release**
   - Merge stable `release/*` branch to `main` for production deployment
   - Tag the release on `main` branch
   - Deploy and announce the release

4. **Hotfixes**
   - For critical production issues, create `hotfix/*` branches from `main`
   - Fix the issue and merge back to both `main` and `develop`
   - Tag hotfix releases as patch versions

---

## Quick Git View

- **develop** (integration branch)
  - **feature/user-auth** (feature work)
  - **feature/api-improvements** (feature work)
  - ↳ **release/v1.0.0** (release prep)
    - ↳ **main** (production)

---

**Branch Hierarchy:**
- `main` ← `release/*` ← `develop` ← `feature/*`
- Hotfixes branch from `main` and merge to both `main` and `develop`

Let me know if you want git commands or a one-line workflow for creating branches or tags!

---

## Basic Git Workflow Actions

### Feature Development
```bash
# Create a new feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/add-new-feature

# Work on feature, commit changes
git add .
git commit -m "feat: add new feature implementation"

# Push feature branch
git push -u origin feature/add-new-feature
```

### Release Preparation
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# Final testing and bug fixes on release branch
git commit -m "fix: resolve issue in release prep"

# Merge release to main when ready
git checkout main
git merge release/v1.0.0
git push origin main

# Tag the release
git tag v1.0.0
git push origin v1.0.0
```

### Hotfix for Production
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Fix the issue
git commit -m "fix: critical production issue"

# Merge hotfix to both main and develop
git checkout main
git merge hotfix/critical-fix
git push origin main

git checkout develop
git merge hotfix/critical-fix
git push origin develop

# Tag the hotfix
git tag v1.0.1
git push origin v1.0.1
```
``` 
