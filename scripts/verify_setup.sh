#!/bin/bash
# Verify development environment setup

set -e

echo "🔍 Verifying Rejoice v2 development environment..."

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Check if venv exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
else
    echo "⚠ Virtual environment not found. Create with: python3 -m venv venv"
    exit 1
fi

# Check if package is installed
echo "✓ Checking package installation..."
python -c "import rejoice; print(f'Rejoice v{rejoice.__version__}')" || {
    echo "⚠ Package not installed. Install with: pip install -e '.[dev]'"
    exit 1
}

# Check dev dependencies
echo "✓ Checking dev dependencies..."
python -c "import pytest, black, flake8, mypy" || {
    echo "⚠ Dev dependencies missing. Install with: pip install -e '.[dev]'"
    exit 1
}

# Check pre-commit
if command -v pre-commit &> /dev/null; then
    echo "✓ Pre-commit installed"
    pre-commit --version
else
    echo "⚠ Pre-commit not installed. Install with: pip install pre-commit && pre-commit install"
fi

# Run basic tests
echo "✓ Running basic tests..."
pytest tests/unit/test_cli.py -v || {
    echo "⚠ Tests failed"
    exit 1
}

echo ""
echo "✅ Development environment verified!"
echo ""
echo "Next steps:"
echo "  1. Review docs/BACKLOG.md for next stories"
echo "  2. Start with Phase 0 stories"
echo "  3. Follow TDD: write tests first!"

