#!/bin/bash
# Rejoice v2 Uninstallation Script
# Safely remove Rejoice installation from this machine.

set -euo pipefail

INSTALL_DIR="$HOME/.rejoice"
VOICE_NOTES_DIR="$HOME/Documents/benjamayden/VoiceNotes"

cat <<EOF
This will remove Rejoice from your system.

What will be removed:
  - Rejoice virtual environment and config at: $INSTALL_DIR
  - Shell aliases for the 'rec' command (bash, zsh, fish)

What will NOT be removed:
  - Your transcripts (stored under: $VOICE_NOTES_DIR)

EOF

read -r -p "Continue? (y/N) " REPLY

case "$REPLY" in
    [Yy]*) ;;
    *)
        echo "Aborted. Rejoice is still installed."
        exit 0
        ;;
esac

echo "Removing Rejoice installation..."

# 1. Remove virtual environment and config directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✓ Removed $INSTALL_DIR"
else
    echo "- No install directory found at $INSTALL_DIR"
fi

# 2. Remove shell aliases from common shell rc files
remove_alias_from_file() {
    local rc_file="$1"

    if [ -f "$rc_file" ]; then
        # Create backup
        cp "$rc_file" "${rc_file}.rejoice.bak" || true

        # Remove lines containing our alias/comment
        # Use temporary file to avoid in-place sed differences across platforms
        tmp_file="${rc_file}.tmp.rejoice"
        grep -v "Rejoice" "$rc_file" | grep -v "alias rec=\"\$HOME/.rejoice/venv/bin/rec\"" > "$tmp_file" || true
        mv "$tmp_file" "$rc_file"

        echo "✓ Cleaned Rejoice alias from $rc_file (backup: ${rc_file}.rejoice.bak)"
    fi
}

SHELL_NAME="$(basename "${SHELL:-}")"
OS_NAME="$(uname -s)"

# Bash rc files
if [ "$SHELL_NAME" = "bash" ] || [ -f "$HOME/.bashrc" ]; then
    remove_alias_from_file "$HOME/.bashrc"
fi
if [ "$OS_NAME" = "Darwin" ] && [ -f "$HOME/.bash_profile" ]; then
    remove_alias_from_file "$HOME/.bash_profile"
fi

# Zsh
if [ -f "$HOME/.zshrc" ]; then
    remove_alias_from_file "$HOME/.zshrc"
fi

# Fish
if [ -f "$HOME/.config/fish/config.fish" ]; then
    remove_alias_from_file "$HOME/.config/fish/config.fish"
fi

cat <<EOF

Uninstallation complete.

Your transcripts were NOT deleted.
If you also want to remove transcripts, you can manually delete:
  $VOICE_NOTES_DIR

EOF
