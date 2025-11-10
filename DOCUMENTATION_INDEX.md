# 📚 Documentation Index

Welcome to the Slow Query Doctor documentation! This guide helps you navigate all available documentation and resources.

## 🏠 **Main Documentation**

### **Getting Started**
- [**README.md**](README.md) - Main project overview, installation, and usage guide
- [**Getting Started Guide**](docs/getting-started.md) - Step-by-step tutorial for new users
- [**Configuration Guide**](docs/configuration.md) - Detailed configuration options and examples

### **Usage & Examples**
- [**Examples**](docs/examples.md) - Real-world usage examples and sample outputs
- [**FAQ**](docs/faq.md) - Frequently asked questions and troubleshooting
- [**Sample Data**](docs/sample-data.md) - Test data and example log files

## 🤝 **Contributing & Development**

### **For Contributors**
- [**CONTRIBUTING.md**](CONTRIBUTING.md) - Complete contributor guide with Git Flow, commit conventions, and review process
- [**CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md) - Community guidelines and standards
- [**VERSION_MANAGEMENT.md**](VERSION_MANAGEMENT.md) - Automated version synchronization system

### **For Repository Maintainers**
- [**BRANCH_PROTECTION.md**](BRANCH_PROTECTION.md) - Repository governance and branch protection setup
- [**ARCHITECTURE.md**](ARCHITECTURE.md) - System architecture and extension points
- [**TECHNICAL_DEBT.md**](TECHNICAL_DEBT.md) - Known limitations and areas for improvement

### **Project Planning**
- [**ROADMAP.md**](ROADMAP.md) - Feature roadmap, timeline, and community requests
- [**Release Process**](docs/release-process.md) - How releases are managed and published

## 🛠️ **Development Tools**

### **Quick Reference**
```bash
# First-time setup (creates venv in repo root)
bash scripts/setup-dev-environment.sh
source venv/bin/activate

# Development commands (all require ./venv)
make validate          # Check environment setup
make setup             # Install deps + git hooks  
make help              # See all available commands

# Version management  
make check-version     # Verify version consistency
make sync-version      # Update all version files

# Code quality
make format lint test  # Format, lint, and test code
make dev-check         # Full development workflow
```

### **Important: Virtual Environment Requirement**
⚠️ **All commands require a `venv` directory in the repository root!**
- First run: `bash scripts/setup-dev-environment.sh`
- Always activate: `source venv/bin/activate`
- Validate setup: `make validate`

### **Git Hooks & Automation**
- **Pre-commit Hook** - Automatically syncs versions and runs linting
- **Pre-push Hook** - Verifies version consistency before push
- **Setup**: `bash scripts/setup-hooks.sh` (one-time)

### **Workflow Files**
- [**CI Pipeline**](.github/workflows/ci.yml) - Tests, linting, coverage
- [**Release Workflow**](.github/workflows/release.yml) - Automated PyPI publishing
- [**Commit Linting**](.github/workflows/commitlint.yml) - Branch + commit validation
- [**Security Analysis**](.github/workflows/codeql-analysis.yml) - CodeQL scanning

## 🎯 **Documentation by Use Case**

### **I want to...**

#### **Use the Tool**
→ Start with [README.md](README.md) → [Getting Started](docs/getting-started.md) → [Examples](docs/examples.md)

#### **Contribute Code**
→ Read [CONTRIBUTING.md](CONTRIBUTING.md) → [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) → [ARCHITECTURE.md](ARCHITECTURE.md)

#### **Set up Repository Governance**
→ Follow [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) → Configure GitHub settings

#### **Understand the Codebase**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) → [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md) → Browse `/slowquerydoctor/`

#### **Report Issues or Request Features**
→ Check [FAQ](docs/faq.md) → [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues) → [ROADMAP.md](ROADMAP.md)

#### **Manage Versions**
→ See [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) → `make sync-version` → Test with sample data

## 🔗 **External Links**

- **Repository**: [github.com/gmartinez-dbai/slow-query-doctor](https://github.com/gmartinez-dbai/slow-query-doctor)
- **Issues**: [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues)
- **PyPI Package**: [pypi.org/project/slow-query-doctor](https://pypi.org/project/slow-query-doctor/)
- **Discussions**: [GitHub Discussions](https://github.com/gmartinez-dbai/slow-query-doctor/discussions)

## 📋 **Documentation Checklist**

For maintainers, ensure all documentation stays current:

- [ ] **README.md** - Updated with latest features and version
- [ ] **CONTRIBUTING.md** - Current branching strategy and commit conventions  
- [ ] **VERSION_MANAGEMENT.md** - Automation setup instructions accurate
- [ ] **BRANCH_PROTECTION.md** - GitHub settings match actual configuration
- [ ] **ROADMAP.md** - Reflects current priorities and timeline
- [ ] **Release docs** - Process matches actual workflow
- [ ] **Examples** - Work with current version and sample data
- [ ] **API docs** - Match current codebase functionality

## 🆘 **Getting Help**

- **Quick Questions**: Check [FAQ](docs/faq.md)
- **Bug Reports**: [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues) with `bug` label
- **Feature Requests**: [GitHub Issues](https://github.com/gmartinez-dbai/slow-query-doctor/issues) with `feature` label
- **Development Questions**: [GitHub Discussions](https://github.com/gmartinez-dbai/slow-query-doctor/discussions)
- **Direct Contact**: gio@gmartinez.net

---

**Keep this index updated as documentation evolves!** 📖✨