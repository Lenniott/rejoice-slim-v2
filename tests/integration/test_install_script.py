"""Integration tests for installation script.

Note: These tests verify the installation script syntax and basic functionality.
Full installation testing should be done manually on clean systems.
"""

import subprocess
from pathlib import Path


def test_install_script_syntax():
    """Test that the installation script has valid bash syntax."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "install.sh"

    # Use bash -n to check syntax without executing
    result = subprocess.run(
        ["bash", "-n", str(script_path)], capture_output=True, text=True
    )

    assert result.returncode == 0, f"Script syntax error: {result.stderr}"


def test_install_script_exists():
    """Test that the installation script exists."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "install.sh"
    assert script_path.exists(), "Installation script not found"
    assert script_path.is_file(), "Installation script is not a file"


def test_install_script_is_executable():
    """Test that the installation script is executable."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "install.sh"
    assert script_path.stat().st_mode & 0o111, "Installation script is not executable"


def test_install_script_has_shebang():
    """Test that the installation script has a shebang line."""
    script_path = Path(__file__).parent.parent.parent / "scripts" / "install.sh"
    content = script_path.read_text()
    assert content.startswith("#!/bin/bash"), "Script missing shebang line"
