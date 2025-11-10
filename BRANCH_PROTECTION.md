# 🛡️ Branch Protection & Repository Governance

This document outlines the branch protection rules, workflows, and governance policies for the Slow Query Doctor repository.

## 🌳 Branch Protection Configuration

### Protected Branches

#### `main` Branch
- **Restrict pushes** - No direct pushes allowed
- **Require pull request reviews** - At least 1 approval required
- **Dismiss stale reviews** - When new commits are pushed
- **Require review from code owners** - If CODEOWNERS file exists
- **Restrict review dismissals** - Only admins can dismiss reviews
- **Require status checks** - All CI checks must pass:
  - `test (3.8, 3.9, 3.10, 3.11, 3.12)` - CI test matrix
  - `integration-test` - Integration test suite
  - `commitlint` - Commit message linting
  - `branch-name-check` - Branch naming convention
  - `CodeQL` - Security analysis
- **Require up-to-date branches** - Must be current with main
- **Include administrators** - Admins follow same rules
- **Allow force pushes** - Disabled
- **Allow deletions** - Disabled

#### `develop` Branch  
- **Restrict pushes** - No direct pushes allowed
- **Require pull request reviews** - At least 1 approval required
- **Require status checks** - All CI checks must pass:
  - `test` - Full CI test suite
  - `commitlint` - Commit message validation
  - `branch-name-check` - Branch naming validation
  - `CodeQL` - Security analysis
- **Require up-to-date branches** - Must be current with develop
- **Include administrators** - Recommended but not enforced
- **Allow force pushes** - Disabled  
- **Allow deletions** - Disabled

### Setting Up Branch Protection

Repository administrators should configure these rules in:
**Settings → Branches → Add rule**

Example rule configuration:
```yaml
Branch name pattern: main
☑️ Restrict pushes that create files larger than 100MB
☑️ Require a pull request before merging
  ☑️ Require approvals: 1
  ☑️ Dismiss stale reviews when new commits are pushed
  ☑️ Require review from code owners
☑️ Require status checks to pass before merging  
  ☑️ Require branches to be up to date before merging
  Required status checks:
    - test (3.8)
    - test (3.9) 
    - test (3.10)
    - test (3.11)
    - test (3.12)
    - integration-test
    - commitlint
    - branch-name-check
    - CodeQL
☑️ Require conversation resolution before merging
☑️ Include administrators
☑️ Restrict pushes that create files larger than 100MB
```

## 🚦 Automated Workflows

### CI Pipeline (`.github/workflows/ci.yml`)
**Triggers:** Push/PR to `main`, `develop`
- **Test Matrix** - Python 3.8-3.12 across Ubuntu
- **Code Quality** - Black, Flake8, MyPy checks  
- **Coverage** - Pytest with coverage reporting
- **Integration Tests** - CLI testing with sample data
- **Artifacts** - Coverage reports to Codecov

### Security Analysis (`.github/workflows/codeql-analysis.yml`)
**Triggers:** Push/PR to `main`, `develop`
- **CodeQL** - Static security analysis
- **Language Detection** - Python codebase scanning
- **Vulnerability Detection** - Security issue identification

### Commit Linting (`.github/workflows/commitlint.yml`)  
**Triggers:** Pull requests to `main`, `develop`
- **Conventional Commits** - Enforce commit message format
- **Branch Naming** - Validate branch naming conventions
- **Multi-commit PRs** - Lint all commits in PR

### Release Automation (`.github/workflows/release.yml`)
**Triggers:** Tag push (`v*`)
- **Version Verification** - Ensure VERSION file matches tag
- **Package Building** - Create wheel and source distributions
- **GitHub Release** - Auto-generate release notes  
- **PyPI Publishing** - Automated package upload
- **Changelog Update** - Maintain release history

## 🔐 Repository Secrets

### Required Secrets
Configure these in **Settings → Secrets and variables → Actions**:

- `PYPI_API_TOKEN` - PyPI publishing token for automated releases
- `CODECOV_TOKEN` - (Optional) Codecov integration for coverage reports

### Setting Up Secrets

#### PyPI Token
1. Create PyPI account and verify email
2. Generate API token: Account settings → API tokens → Add API token
3. Scope: Entire account or specific to slow-query-doctor
4. Add to GitHub: Settings → Secrets → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-...` (your token)

#### Codecov Token (Optional)
1. Sign up at codecov.io with GitHub account
2. Add slow-query-doctor repository
3. Copy upload token from repository settings  
4. Add to GitHub secrets as `CODECOV_TOKEN`

## 📝 Repository Settings Checklist

### General Settings
- [ ] **Default branch** - Set to `main`
- [ ] **Allow merge commits** - ✅ Enabled 
- [ ] **Allow squash merging** - ✅ Enabled (default for features)
- [ ] **Allow rebase merging** - ✅ Enabled
- [ ] **Automatically delete head branches** - ✅ Enabled
- [ ] **Allow auto-merge** - ✅ Enabled (optional)

### Access & Permissions
- [ ] **Base permissions** - Read for public repo
- [ ] **Admin access** - Repository owner(s)
- [ ] **Maintain access** - Core maintainers (if any)  
- [ ] **Write access** - Trusted contributors (if any)

### Branch Protection (As configured above)
- [ ] **main** - Full protection with required reviews
- [ ] **develop** - Protection with required status checks

### Actions Settings
- [ ] **Actions permissions** - Allow GitHub Actions
- [ ] **Fork pull request workflows** - Require approval for first-time contributors
- [ ] **Workflow permissions** - Read and write permissions

### Security & Analysis
- [ ] **Dependency graph** - ✅ Enabled
- [ ] **Dependabot alerts** - ✅ Enabled  
- [ ] **Dependabot security updates** - ✅ Enabled
- [ ] **Code scanning alerts** - ✅ Enabled (CodeQL)
- [ ] **Secret scanning** - ✅ Enabled

## 🚨 Enforcement & Override

### When Rules Apply
- **All contributors** - Must follow branch protection and workflows
- **External contributors** - PRs require maintainer approval to run Actions
- **Repository admins** - Can override protections in emergencies

### Emergency Procedures
In case of critical issues requiring immediate fixes:

1. **Hotfix Process** - Preferred approach:
   ```bash
   git checkout main
   git checkout -b hotfix/critical-security-fix
   # Make fix, test, commit
   # Create PR with "hotfix" label for priority review
   ```

2. **Admin Override** - Last resort only:
   - Temporarily disable branch protection
   - Make critical fix directly
   - Re-enable protection immediately
   - Document override in issue/PR

### Violation Handling
- **Failed status checks** - PR cannot merge until fixed
- **Missing approvals** - Must get required reviews
- **Bad commit messages** - Rebase/squash to fix
- **Branch naming violations** - Rename branch and force-push

## 📞 Support & Questions

For questions about repository governance:
- **GitHub Issues** - Technical questions about workflows
- **Email** - gio@gmartinez.net for access/permission issues  
- **Discussions** - General questions about contribution process

---

**This governance model ensures code quality, security, and collaboration while maintaining development velocity.**