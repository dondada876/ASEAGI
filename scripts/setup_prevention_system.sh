#!/bin/bash
# Setup Schema Mismatch Prevention System
# Run this once to install all preventions

set -e

echo "=" 80
echo "ASEAGI Schema Mismatch Prevention System Setup"
echo "=" * 80
echo

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

if [[ $python_version < "3.9" ]]; then
    echo "   ❌ Python 3.9+ required"
    exit 1
fi
echo "   ✅ Python version OK"
echo

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$SUPABASE_URL" ]; then
    echo "   ⚠️  SUPABASE_URL not set"
    echo "   Set with: export SUPABASE_URL='https://...'"
else
    echo "   ✅ SUPABASE_URL set"
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "   ⚠️  SUPABASE_KEY not set"
    echo "   Set with: export SUPABASE_KEY='...'"
else
    echo "   ✅ SUPABASE_KEY set"
fi
echo

# Install pre-commit
echo "📦 Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    echo "   ✅ pre-commit already installed"
else
    echo "   Installing pre-commit..."
    pip install pre-commit
    echo "   ✅ pre-commit installed"
fi
echo

# Install hooks
echo "🎣 Setting up pre-commit hooks..."
pre-commit install
echo "   ✅ Hooks installed"
echo

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-cov
echo "   ✅ Test dependencies installed"
echo

# Generate schema documentation
echo "📝 Generating schema documentation..."
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_KEY" ]; then
    python database/validate_schema.py
    echo "   ✅ Schema docs generated: database/SCHEMA.md"
else
    echo "   ⚠️  Skipped (missing credentials)"
fi
echo

# Run tests
echo "🧪 Running schema validation tests..."
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_KEY" ]; then
    python -m pytest tests/test_database_schema.py -v
    echo "   ✅ All tests passed"
else
    echo "   ⚠️  Skipped (missing credentials)"
fi
echo

# Test pre-commit hooks
echo "🎯 Testing pre-commit hooks..."
pre-commit run --all-files || true
echo "   ✅ Hooks tested"
echo

echo "=" * 80
echo "✅ SETUP COMPLETE!"
echo "=" * 80
echo
echo "Prevention system installed:"
echo "  ✅ Type hints (database/schema_types.py)"
echo "  ✅ Pre-commit hooks (.pre-commit-config.yaml)"
echo "  ✅ Automated tests (tests/test_database_schema.py)"
echo "  ✅ CI/CD pipeline (.github/workflows/schema-validation.yml)"
echo "  ✅ Schema validator (database/validate_schema.py)"
echo
echo "Next steps:"
echo "  1. Set SUPABASE_URL and SUPABASE_KEY if not already set"
echo "  2. Run: python database/validate_schema.py"
echo "  3. Read: SCHEMA_MISMATCH_PREVENTION.md"
echo
echo "Test the system:"
echo "  git commit -m 'Test commit' (triggers pre-commit hooks)"
echo "  python -m pytest tests/test_database_schema.py"
echo
