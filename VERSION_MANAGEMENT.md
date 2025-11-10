# 🔄 Version Management Automation

This document explains the automated version synchronization system for the slow-query-doctor project.

## 🎯 **The Problem**
When you update the `VERSION` file, you need to remember to update version references in:
- `slowquerydoctor/__init__.py` (`__version__`)
- `pyproject.toml` (`version`)  
- `Dockerfile` (multiple version labels)
- Any Chart.yaml files (if present)

## 🚀 **Automated Solutions**

### **Option 1: Git Hooks (Recommended)**
Automatically runs on every commit/push:

```bash
# One-time setup
bash scripts/setup-hooks.sh

# Now every time you commit, versions sync automatically!
echo "0.1.9" > VERSION
git add VERSION  
git commit -m "feat: bump version to 0.1.9"
# ✅ Hook automatically updates all version files and stages them
```

**What it does:**
- **Pre-commit**: When `VERSION` file changes, automatically updates all other files
- **Pre-push**: Verifies all versions are consistent before allowing push

### **Option 2: Makefile Commands**
Quick manual commands:

```bash
# Update all versions to match VERSION file
make sync-version

# Check if all versions are consistent  
make check-version

# Full development workflow
make dev-check  # format + lint + test + version check
```

### **Option 3: Manual Script**
Direct script usage:

```bash
# Update all version references
python scripts/propagate_version.py

# Verify consistency (exit code 0 = success, 1 = inconsistent)
python scripts/propagate_version.py --verify
```

### **Option 4: GitHub Actions (CI)**
Automatically checks version consistency in CI pipeline - no action needed, just ensures consistency.

## 🛠️ **Setup Instructions**

### 1. Set Up Development Environment (Recommended)
```bash
# Complete setup with virtual environment and dependencies
bash scripts/setup-dev-environment.sh

# Then activate the virtual environment
source venv/bin/activate

# Install git hooks
bash scripts/setup-hooks.sh
```

### 2. Quick Setup (If you already have a venv)
```bash
# Install dependencies and hooks
make setup
```

### 3. Manual Setup
```bash
# Create virtual environment in repo root
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Install git hooks
bash scripts/setup-hooks.sh
```

The git hooks will:
- ✅ Auto-sync versions when `VERSION` file changes in commits
- ✅ Verify consistency before pushes
- ✅ Run basic linting on Python files
- ✅ Automatically detect and use your virtual environment

## 📋 **Daily Workflow**

With hooks installed, your workflow becomes:

```bash
# 1. Update version (triggers auto-sync on commit)
echo "0.1.9" > VERSION

# 2. Make your changes
# ... edit code ...

# 3. Commit normally (versions sync automatically)
git add .
git commit -m "feat: add new feature"

# 4. Push (automatically verified)
git push origin feature/my-branch
```

## 🔍 **Manual Verification**

To check if versions are consistent:

```bash
# Quick check
make check-version

# Or direct script  
python scripts/propagate_version.py --verify

# Expected output:
# Verifying all versions match: 0.1.8
# ✅ All versions are consistent!
```

## 🚨 **Troubleshooting**

### Problem: "Version inconsistencies detected"
```bash
# Fix it automatically
make sync-version
# or
python scripts/propagate_version.py

# Then commit the changes
git add -u
git commit -m "chore: sync version references"
```

### Problem: Git hooks not working
```bash
# Reinstall hooks
bash scripts/setup-hooks.sh

# Verify hooks are installed
ls -la .git/hooks/pre-*
```

### Problem: Want to skip hook temporarily
```bash
# Skip pre-commit hook (not recommended)
git commit --no-verify -m "emergency fix"

# Skip pre-push hook (not recommended) 
git push --no-verify
```

## 🎛️ **Configuration**

The version propagation script updates these patterns:

### `slowquerydoctor/__init__.py`
```python
__version__ = "0.1.8"  # ← Updated
```

### `pyproject.toml`
```toml
[project]
version = "0.1.8"  # ← Updated
```

### `Dockerfile`
```dockerfile
ENV SLOW_QUERY_DOCTOR_VERSION=0.1.8  # ← Updated
LABEL version="0.1.8"                # ← Updated  
LABEL org.opencontainers.image.version="0.1.8"  # ← Updated
```

## 🏆 **Best Practices**

1. **Always update VERSION file first** - other files sync automatically
2. **Use semantic versioning** - MAJOR.MINOR.PATCH (e.g., 1.2.3)
3. **Install git hooks** - prevents inconsistency issues
4. **Run `make check-version`** - before important releases
5. **Let CI verify** - GitHub Actions also check consistency

## 🆘 **Need Help?**

- **Check version status**: `make check-version`
- **Fix inconsistencies**: `make sync-version`
- **Full dev check**: `make dev-check`
- **View all commands**: `make help`

---

**With this system, you'll never have mismatched versions again!** 🎉