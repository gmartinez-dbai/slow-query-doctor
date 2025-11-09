```markdown
# Release Process & Versioning

This document describes the automated, single-source-of-truth release steps used by the project. It is the published (docs/) companion to the internal branching strategy in `notes/GITHUB_Branching_Release_Strategy.md`.

Key artifacts created by the repository:

- `VERSION` (repo root) — single source of truth for the project version.
- `scripts/propagate_version.sh` — helper script that reads `VERSION`, updates common files (if present), commits, and tags the repo.
- `.github/workflows/propagate-version.yml` — manual/branch-triggered workflow to run the propagate script and push the tag.

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

- Manually via the Actions UI: go to `Actions → Propagate Version → Run workflow`.
- Or push to a `bump-version/*` branch to trigger the workflow automatically (the workflow pushes commits and tags back to the repo).

Notes and best practices

- Keep `VERSION` at the repo root for discoverability and automation.
- The `propagate_version.sh` script is intentionally conservative: it updates `src/__init__.py`, `Chart.yaml` files, and `Dockerfile` if they exist. If your repository uses different metadata locations, extend the script accordingly.
- The workflow uses the built-in `GITHUB_TOKEN` and `persist-credentials: true` to push commits/tags. If you prefer signed tags or a bot account, switch to a dedicated deploy key or bot token in `secrets`.

Suggested additions (future):

- Attach SBOM and signed artifacts to GA releases.
- Add a `release-drafter.yml` configuration to automate draft release notes.
- Add a `release` workflow that builds and publishes images and Helm charts only when a GA tag is pushed.

Useful links

- `VERSION` file: `/VERSION`
- Propagate script: `/scripts/propagate_version.sh`
- Propagate workflow: `/.github/workflows/propagate-version.yml`
- Branching & release strategy (notes, internal): `/notes/GITHUB_Branching_Release_Strategy.md`

``` 
