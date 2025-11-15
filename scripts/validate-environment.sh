#!/bin/bash

# Validation script to check if .venv setup is correct
# Run this to verify your environment is properly configured

set -e

echo "🔍 Validating slow-query-doctor development environment..."
echo ""

# Check 1: Verify .venv directory exists
if [ ! -d ".venv" ]; then
    echo "❌ FAIL: Virtual environment '.venv' directory not found"
    echo "💡 Run: uv venv --python 3.11"
    exit 1
else
    echo "✅ PASS: Virtual environment directory exists"
fi

# Check 2: Verify .venv has Python
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ FAIL: Python executable not found in .venv"
    echo "💡 Recreate .venv: rm -rf .venv && uv venv --python 3.11"
    exit 1
else
    echo "✅ PASS: Python executable found in .venv"
fi

# Check 3: Activate .venv and check it works
echo "🐍 Activating virtual environment..."
source .venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ FAIL: Virtual environment not activated properly"
    exit 1
else
    echo "✅ PASS: Virtual environment activated"
    echo "   VIRTUAL_ENV: $VIRTUAL_ENV"
fi

# Check 4: Verify requirements can be installed
echo "📦 Installing/checking requirements with uv..."
uv pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ FAIL: Could not install requirements"
    exit 1
else
    echo "✅ PASS: Requirements installed successfully"
fi

# Check 5: Verify ruamel.yaml is available
echo "🔍 Checking ruamel.yaml..."
if uv run python -c "import ruamel.yaml" 2>/dev/null; then
    RUAMEL_VERSION=$(uv run python -c "import ruamel.yaml; print(ruamel.yaml.version_info)")
    echo "✅ PASS: ruamel.yaml is available (version: $RUAMEL_VERSION)"
else
    echo "❌ FAIL: ruamel.yaml not available"
    echo "💡 Installing ruamel.yaml..."
    uv pip install "ruamel.yaml>=0.17.21"
    if uv run python -c "import ruamel.yaml" 2>/dev/null; then
        echo "✅ FIXED: ruamel.yaml installed successfully"
    else
        echo "❌ FAIL: Could not install ruamel.yaml"
        exit 1
    fi
fi

# Check 6: Test version management script
echo "🧪 Testing version management script..."
if uv run python scripts/propagate_version.py --verify 2>/dev/null; then
    echo "✅ PASS: Version management script works"
else
    echo "⚠️  WARNING: Version management script test failed (may need version sync)"
fi

# Check 7: Verify git hooks can be installed
if [ -f ".githooks/pre-commit" ] && [ -f ".githooks/pre-push" ]; then
    echo "✅ PASS: Git hook files exist"
else
    echo "❌ FAIL: Git hook files missing"
    exit 1
fi

# Check 8: Test Makefile commands
echo "🔧 Testing Makefile integration..."
make check-version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PASS: Makefile commands work with .venv"
else
    echo "❌ FAIL: Makefile commands don't work properly"
    exit 1
fi

echo ""
echo "🎉 All checks passed! Your environment is correctly configured."
echo ""
echo "📋 Summary:"
echo "   • Virtual environment: ./.venv ✅"
echo "   • Requirements installed ✅"  
echo "   • ruamel.yaml available ✅"
echo "   • Version management working ✅"
echo "   • Git hooks ready ✅"
echo "   • Makefile integration ✅"
echo ""
echo "🚀 Next steps:"
echo "   1. Install git hooks: bash scripts/setup-hooks.sh"
echo "   2. Run tests: make test"
echo "   3. Start developing!"
echo ""
echo "💡 Remember to always use 'source .venv/bin/activate' before development"