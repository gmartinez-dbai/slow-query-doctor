# Contributing to Slow Query Doctor

Thank you for your interest in contributing! 🎉

We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code changes.

## 🌳 Branching Strategy

We follow a **Git Flow** branching model with the following branches:

### Branch Overview Table

| Branch         | What Goes Here                        | Contributor Type      | Stability         |
| -------------- | ------------------------------------- | -------------------- | ----------------- |
| `main`         | Stable, production-ready releases     | Maintainers          | Stable            |
| `develop`      | All new features, fixes (integration) | Everyone             | Unstable/WIP      |
| `feature/*`    | Isolated experimental features        | Individuals          | Unstable/WIP      |
| `release/*`    | Final bugfix, QA before release       | Maintainers          | Semi-Stable       |

### Main Branches
- **`main`** - Production-ready code, always stable and deployable
- **`develop`** - Integration branch for features, pre-release testing

### Supporting Branches
- **`feature/*`** - New features and enhancements
- **`bugfix/*`** - Non-critical bug fixes
- **`hotfix/*`** - Critical fixes that need immediate deployment
- **`docs/*`** - Documentation-only changes
- **`refactor/*`** - Code refactoring without functional changes
- **`chore/*`** - Maintenance tasks, dependency updates

### Branch Protection Rules
- **`main`** and **`develop`** are protected branches
- All changes must go through Pull Requests
- Require at least 1 approval for PRs to `main`
- Require status checks to pass (CI, tests, linting)
- No direct pushes allowed to protected branches

## 📋 How to Contribute

### 🚀 Quick Start for New Contributors

1. **Fork & Clone** the repo.
2. **Create a Feature Branch:**
   Example:
   ```
   git checkout -b feature/my-new-feature
   ```
3. **Do your work:** Commit small, focused changes. Push to your feature branch.
4. **PR to Develop:** Open a pull request (PR) from `feature/*` to `develop`.
5. **Review & Testing:** Wait for CI/tests and code review from maintainers.
6. **Merge to Develop:** Maintainers merge after approval.
7. **Release Candidate:** When ready for release, maintainers create `release/*` and do final QA.
8. **Merge to Main:** Final, stable release gets merged to `main` and tagged.

### Detailed Steps

#### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/slow-query-doctor.git
cd slow-query-doctor
git remote add upstream https://github.com/gmartinez-dbai/slow-query-doctor.git
```

#### 2. Create a Feature Branch
```bash
# Start from develop for new features
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b bugfix/describe-the-fix

# For hotfixes (from main)
git checkout main
git pull upstream main
git checkout -b hotfix/critical-fix-name
```

### 3. Make Your Changes
- Follow the code style and guidelines below
- Add or update tests as appropriate
- Test with multi-line, CSV, and JSON log files
- Keep commits focused and atomic

### 4. Commit Your Changes
- Use [Conventional Commits](https://www.conventionalcommits.org/) format
- Each commit should be a logical unit of work
- Write clear, descriptive commit messages

### 5. Push & Create PR
```bash
git push origin feature/your-feature-name
```
- Open a Pull Request to the appropriate target branch:
  - **Features/bugfixes** → `develop` 
  - **Hotfixes** → `main`
  - **Docs/chore** → `develop`
- Fill out the PR template completely
- Link any related issues


## Code Style & Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style
- Use type hints where possible
- Write clear docstrings for all public functions and classes
- Use descriptive variable and function names
- Keep functions small and focused
- Add or update tests for new features and bug fixes
- Run `black` and `flake8` before submitting your PR
- Keep PRs focused and minimal; avoid unrelated changes
- Ensure you have `pyyaml`, `tqdm`, and all dev dependencies installed (see README)
- Reference `.slowquerydoctor.yml` for config-driven tests if needed

## 📝 Commit Message Convention

We enforce [Conventional Commits](https://www.conventionalcommits.org/) for all commits:

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat** - New features
- **fix** - Bug fixes  
- **docs** - Documentation changes
- **style** - Code style changes (formatting, etc.)
- **refactor** - Code refactoring
- **perf** - Performance improvements
- **test** - Test changes
- **build** - Build system changes
- **ci** - CI/CD changes
- **chore** - Maintenance tasks
- **hotfix** - Critical fixes for production

### Examples
```bash
feat(parser): add support for MySQL slow query logs
fix(analyzer): handle edge case with empty query strings
docs(readme): update installation instructions
refactor(report): simplify HTML generation logic
test(parser): add tests for multiline query parsing
ci: add automated release workflow
```

### Scope Guidelines
- **parser** - Log parsing functionality
- **analyzer** - Query analysis and antipattern detection
- **report** - Report generation (HTML, JSON, etc.)
- **cli** - Command-line interface
- **config** - Configuration handling
- **llm** - LLM integration features
- **docker** - Docker/containerization
- **docs** - Documentation

### Commit Message Rules
- Use lowercase for type and scope
- Keep subject line ≤ 72 characters
- Use imperative mood ("add" not "added")
- No period at end of subject
- Separate subject and body with blank line
- Wrap body at 100 characters
- Use body to explain *what* and *why*, not *how*

## 🔄 Release Process

### Release Phases

- **Alpha:** Early testing, unstable (tag: `v0.x.x-alpha.1`)
- **Beta:** Feature complete, needs polish (tag: `v0.x.x-beta.1`)
- **Release Candidate:** Ready for last QA (tag: `v0.x.x-rc.1`)
- **GA:** General Availability/stable (tag: `v0.x.x`)

### Version Management
- Versions follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- Version is stored in `VERSION` file and propagated by `scripts/propagate_version.py`
- Tags trigger automated releases via GitHub Actions

### Release Types
- **Major** (x.0.0) - Breaking changes, new architecture
- **Minor** (1.x.0) - New features, backwards compatible  
- **Patch** (1.1.x) - Bug fixes, security patches

### Release Workflow
1. **Feature Development** → `develop` branch
2. **Release Preparation**:
   ```bash
   git checkout develop
   git pull upstream develop
   # Update VERSION file (versions sync automatically via git hooks)
   echo "1.2.0" > VERSION
   git commit -am "chore: bump version to 1.2.0"
   git push upstream develop
   ```
3. **Release PR**: `develop` → `main`
4. **Tag & Release**:
   ```bash
   git checkout main
   git pull upstream main
   git tag v1.2.0
   git push upstream v1.2.0
   ```
5. **Automated Release** - GitHub Actions builds and publishes to PyPI

### Example Workflow

```
# Start with develop
git checkout develop

# Add a feature
git checkout -b feature/cool-feature
# ...code and commit...

# Push and create PR to develop
git push origin feature/cool-feature

# After review/merge, prepare release
git checkout develop
git pull
git checkout -b release/0.2.0-alpha.1

# Final QA then merge to main
git checkout main
git merge release/0.2.0-alpha.1
git tag v0.2.0-alpha.1
git push --tags
```

### Version Management
- **Automated Sync**: Git hooks automatically update all version files when `VERSION` changes
- **Manual Sync**: `make sync-version` or `python scripts/propagate_version.py`  
- **Verification**: `make check-version` or `python scripts/propagate_version.py --verify`
- **Setup**: Run `bash scripts/setup-hooks.sh` once to install automation
- **Documentation**: See [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) for details

### Hotfix Process
1. Create `hotfix/fix-name` from `main`
2. Make critical fix
3. Update VERSION file (patch increment)
4. PR to `main` 
5. Tag immediately after merge
6. Cherry-pick to `develop` if needed

## 🏁 Quick Rules

- **Never push unfinished code directly to main.**
- **Always use PRs (Pull Requests) for changes.**
- **Ask for help—no question is too small!**
- **Tag releases clearly for every release phase.**

## 🔍 Pull Request Review Process

### Automated Checks
- ✅ **CI Tests** - All tests must pass across Python versions
- ✅ **Code Quality** - Black, Flake8, MyPy checks
- ✅ **Branch Naming** - Must follow convention
- ✅ **Commit Messages** - Must follow Conventional Commits
- ✅ **Security** - CodeQL analysis

### Manual Review
- Code quality and maintainability
- Test coverage for new features
- Documentation updates
- Breaking change assessment
- Performance impact review

### Review Criteria
- **Features** - Require 1+ approval, all checks pass
- **Bugfixes** - Require 1+ approval, all checks pass  
- **Hotfixes** - May be fast-tracked with admin override
- **Docs** - Can be merged with basic review

### Merge Strategy
- **Squash and merge** for features (clean history)
- **Merge commit** for releases (preserve branch history)
- **Rebase and merge** for small fixes (linear history)

## Reporting Bugs & Requesting Features

- Use [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues)
- Provide as much detail as possible (logs, steps to reproduce, screenshots)
- Label your issue as `bug`, `feature`, or `question`

## Community Standards

- Be respectful and constructive
- No harassment, discrimination, or inappropriate behavior
- See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details

## Questions?

Open an issue or email gio@gmartinez.net

---

**Thank you for helping make Slow Query Doctor better!**
