#!/bin/bash

# Quick fix to update git hooks with venv support
# Run this to fix the "ruamel.yaml not found" error

set -e

echo "🔧 Updating git hooks to use venv properly..."

# Copy updated pre-commit hook
echo "📋 Installing updated pre-commit hook..."
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Copy updated pre-push hook  
echo "📋 Installing updated pre-push hook..."
cp .githooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

echo "✅ Git hooks updated successfully!"
echo ""
echo "🧪 Testing the updated pre-commit hook..."

# Test if the hook would work
if [ ! -d "venv" ]; then
    echo "⚠️  You need to create the venv first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
else
    echo "✅ venv directory found"
    
    # Quick test
    source venv/bin/activate 2>/dev/null || echo "⚠️  Could not activate venv"
    
    if python -c "import ruamel.yaml" 2>/dev/null; then
        echo "✅ ruamel.yaml is available in venv"
    else
        echo "⚠️  ruamel.yaml not found in venv, installing..."
        pip install -r requirements.txt > /dev/null 2>&1
        if python -c "import ruamel.yaml" 2>/dev/null; then
            echo "✅ ruamel.yaml installed successfully"
        else
            echo "❌ Failed to install ruamel.yaml"
        fi
    fi
fi

echo ""
echo "🎉 Hooks updated! Your next commit should work properly."