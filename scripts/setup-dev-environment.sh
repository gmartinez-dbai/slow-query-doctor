#!/bin/bash

# Enhanced setup script for slow-query-doctor development environment
# This script sets up everything needed for development

set -e

echo "🚀 Setting up slow-query-doctor development environment..."

# Ensure uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "❌ 'uv' is not installed. Please install uv first:"
    echo "   https://docs.astral.sh/uv/getting-started/"
    echo "   macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Homebrew: brew install uv"
    echo "   Windows: winget install Astral-UV.UV"
    exit 1
fi

# Check if .venv directory exists, create if not
if [ ! -d ".venv" ]; then
    echo "📦 Creating '.venv' virtual environment with uv in repository root..."
    uv venv --python 3.11
    echo "✅ Virtual environment created at ./.venv"
    echo ""
else
    echo "✅ Virtual environment '.venv' already exists"
fi

echo "🧰 Installing dependencies with uv..."
uv pip install -r requirements.txt
echo "📥 Installing slow-query-doctor with dev dependencies (uv)..."
uv pip install -e .[dev]

# Verify ruamel.yaml is installed
echo "🔍 Verifying ruamel.yaml installation..."
if uv run python -c "import ruamel.yaml; print('✅ ruamel.yaml installed successfully')" 2>/dev/null; then
    echo "✅ ruamel.yaml is available"
else
    echo "❌ ruamel.yaml not found, installing explicitly..."
    uv pip install "ruamel.yaml>=0.17.21"
fi

# Test the version script
echo "🧪 Testing version management script..."
if uv run python scripts/propagate_version.py --verify; then
    echo "✅ Version management script works correctly"
else
    echo "❌ Version script test failed"
    exit 1
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 What was installed:"
echo "   • Virtual environment at ./.venv"
echo "   • slow-query-doctor package (development mode)"
echo "   • All development dependencies (pytest, black, flake8, mypy, etc.)"
echo "   • ruamel.yaml for version management"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate virtual environment: source .venv/bin/activate"
echo "   2. Install git hooks: bash scripts/setup-hooks.sh"
echo "   3. Run tests: make test"
echo "   4. Check version consistency: make check-version"
echo ""
echo "💡 Available commands (all will use ./.venv automatically):"
echo "   make help           # See all available commands"
echo "   make setup          # Full setup including git hooks"
echo "   make check-version  # Verify version consistency"
echo "   make test           # Run test suite"
echo ""
echo "⚠️  Important: Always use '.venv' directory in repo root for this project!"