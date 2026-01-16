#!/bin/bash
# Setup pre-commit hooks for TERAG
# Installs pre-commit and gitleaks to prevent committing secrets

set -e

echo "🔒 Setting up pre-commit hooks for TERAG..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
fi

# Check if gitleaks is installed (optional, will be installed via pre-commit)
if ! command -v gitleaks &> /dev/null; then
    echo "⚠️  gitleaks will be installed automatically by pre-commit on first run"
fi

# Install pre-commit hooks
echo "📥 Installing pre-commit hooks..."
pre-commit install

# Test hooks
echo "🧪 Testing pre-commit hooks..."
pre-commit run --all-files || echo "⚠️  Some hooks failed (this is normal on first run)"

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "📝 Next steps:"
echo "  1. Hooks will run automatically on 'git commit'"
echo "  2. To test manually: pre-commit run --all-files"
echo "  3. To skip hooks (not recommended): git commit --no-verify"


















