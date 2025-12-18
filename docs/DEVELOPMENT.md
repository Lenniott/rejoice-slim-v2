# Development Guide

## Initial Setup

### 1. Clone and Navigate

```bash
cd rejoice-slim-v2
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Verify Setup

```bash
# Run tests
pytest

# Check CLI works
python -m rejoice --version

# Run linting
black --check src tests
flake8 src tests
mypy src
```

## Development Workflow

### Test-Driven Development (TDD)

1. **Write failing test first**
   ```bash
   # Write test in tests/unit/test_feature.py
   pytest tests/unit/test_feature.py -v
   # Should FAIL
   ```

2. **Implement minimal code to pass**
   ```bash
   # Write implementation in src/rejoice/
   pytest tests/unit/test_feature.py -v
   # Should PASS
   ```

3. **Refactor while keeping tests green**
   ```bash
   pytest tests/unit/test_feature.py -v
   # Should still PASS
   ```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests
pytest tests/e2e

# With coverage
pytest --cov=src/rejoice --cov-report=html

# Specific test
pytest tests/unit/test_cli.py::test_cli_version -v
```

### Code Quality

```bash
# Format code
black src tests

# Lint
flake8 src tests

# Type check
mypy src

# All checks (via pre-commit)
pre-commit run --all-files
```

## Project Structure

```
rejoice-v2/
├── src/rejoice/          # Source code
│   ├── cli/              # CLI commands
│   ├── core/              # Core functionality
│   ├── audio/             # Audio recording
│   ├── transcription/     # Transcription engine
│   ├── transcript/        # Transcript file management
│   ├── ai/                # AI enhancement
│   └── utils/             # Utilities
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── fixtures/          # Test data
├── docs/                  # Documentation
├── scripts/               # Installation scripts
└── pyproject.toml         # Package configuration
```

## Adding New Features

1. **Read the user story** from `docs/BACKLOG.md`
2. **Write tests first** (TDD approach)
3. **Implement feature**
4. **Update story status** in BACKLOG.md
5. **Ensure 90%+ test coverage**

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "feat: add your feature"

# Run tests before pushing
pytest

# Push and create PR
git push origin feature/your-feature-name
```

## Common Tasks

### Add a new CLI command

1. Add command to `src/rejoice/cli/commands.py`
2. Write tests in `tests/unit/test_cli.py`
3. Update help text

### Add a new module

1. Create module in appropriate directory
2. Add `__init__.py`
3. Write tests
4. Update imports

### Update dependencies

1. Edit `pyproject.toml`
2. Run `pip install -e ".[dev]"`
3. Update tests if needed

## Troubleshooting

### Import errors

```bash
# Make sure package is installed in editable mode
pip install -e .
```

### Pre-commit hooks failing

```bash
# Run manually to see errors
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

### Coverage below 90%

```bash
# Generate coverage report
pytest --cov=src/rejoice --cov-report=html

# Open htmlcov/index.html to see what's missing
```

## Next Steps

- Follow stories in `docs/BACKLOG.md` in order
- Start with Phase 0: Installation & Environment
- Write tests first (TDD)
- Keep it simple (Slim mandate)
