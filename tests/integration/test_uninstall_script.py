"""Integration tests for uninstallation script.

These tests verify basic properties (syntax, existence, shebang) of the
uninstall script. Full destructive behavior (actually removing ~/.rejoice
or shell aliases) is NOT executed in tests.
"""

import subprocess
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
UNINSTALL_SCRIPT = SCRIPTS_DIR / "uninstall.sh"


def test_uninstall_script_exists():
    """The uninstall script file should exist once implemented."""
    assert UNINSTALL_SCRIPT.exists(), "Uninstall script not found"
    assert UNINSTALL_SCRIPT.is_file(), "Uninstall script is not a file"


def test_uninstall_script_has_shebang():
    """The uninstall script should start with a bash shebang."""
    content = UNINSTALL_SCRIPT.read_text()
    assert content.startswith("#!/bin/bash"), "Uninstall script missing bash shebang"


def test_uninstall_script_is_executable():
    """The uninstall script should be executable."""
    assert UNINSTALL_SCRIPT.stat().st_mode & 0o111, "Uninstall script is not executable"


def test_uninstall_script_syntax():
    """The uninstall script should have valid bash syntax (bash -n)."""
    result = subprocess.run(
        ["bash", "-n", str(UNINSTALL_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"Syntax error in uninstall script: {result.stderr}"
