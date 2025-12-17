#!/bin/bash
# Quick check for test dependencies
echo "Checking dependencies..."
python3 -c "
import sys
missing = []
try:
    import rich
    print('✓ rich')
except ImportError:
    missing.append('rich')
    print('✗ rich - MISSING')

try:
    import yaml
    print('✓ pyyaml')
except ImportError:
    missing.append('pyyaml')
    print('✗ pyyaml - MISSING')

try:
    import click
    print('✓ click')
except ImportError:
    missing.append('click')
    print('✗ click - MISSING')

try:
    import dotenv
    print('✓ python-dotenv')
except ImportError:
    missing.append('python-dotenv')
    print('✗ python-dotenv - MISSING')

if missing:
    print(f'\nMissing: {missing}')
    print('Install with: pip install -e ".[dev]"')
    sys.exit(1)
else:
    print('\n✓ All dependencies installed!')
"
