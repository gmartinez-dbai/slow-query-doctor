#!/bin/bash

# Setup script to install git hooks
# Run this once: ./scripts/setup-hooks.sh

echo "🔧 Setting up git hooks for slow-query-doctor..."

# Check for .venv directory in repo root
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment '.venv' not found in repository root!"
    echo "💡 Please create it first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Source the virtual environment and check dependencies
echo "🐍 Activating virtual environment..."
source .venv/bin/activate

echo "🔍 Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

if ! python -c "import ruamel.yaml" 2>/dev/null; then
    echo "❌ ruamel.yaml not found!"
    echo "💡 Installing missing dependency..."
    pip install ruamel.yaml>=0.17.21
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy our custom hooks
echo "📋 Installing pre-commit hook..."
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "📋 Installing pre-push hook..."
cp .githooks/pre-push .git/hooks/pre-push  
chmod +x .git/hooks/pre-push

echo "✅ Git hooks installed successfully!"
echo ""
echo "ℹ️  The hooks will now:"
echo "   🔄 Pre-commit: Sync versions when VERSION file changes + basic linting"
echo "   🚀 Pre-push: Verify all versions are consistent before pushing"
echo ""
echo "💡 To run manually:"
echo "   python scripts/propagate_version.py           # Update versions"
echo "   python scripts/propagate_version.py --verify  # Check consistency"
echo ""
echo "🚀 You're all set! Try editing the VERSION file and committing to test it."