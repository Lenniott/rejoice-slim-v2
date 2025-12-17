#!/bin/bash
# Rejoice v2 Installation Script
# One-command installation for macOS and Linux

set -e  # Exit on error

echo "🎙️  Installing Rejoice v2..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Detect OS
OS="$(uname -s)"
echo "📱 Detected OS: $OS"

case "$OS" in
    Darwin)
        echo "📦 Installing system dependencies (macOS)..."
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew required. Install from https://brew.sh${NC}"
            exit 1
        fi
        brew install portaudio ffmpeg || {
            echo -e "${YELLOW}⚠️  Some dependencies may already be installed${NC}"
        }
        ;;
    Linux)
        echo "📦 Installing system dependencies (Linux)..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y portaudio19-dev ffmpeg python3-dev || {
                echo -e "${YELLOW}⚠️  Some dependencies may already be installed${NC}"
            }
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y portaudio-devel ffmpeg python3-devel || {
                echo -e "${YELLOW}⚠️  Some dependencies may already be installed${NC}"
            }
        elif command -v yum &> /dev/null; then
            sudo yum install -y portaudio-devel ffmpeg python3-devel || {
                echo -e "${YELLOW}⚠️  Some dependencies may already be installed${NC}"
            }
        else
            echo -e "${RED}❌ Unsupported package manager. Please install portaudio and ffmpeg manually.${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        echo "Rejoice v2 currently supports macOS and Linux only."
        exit 1
        ;;
esac

# 2. Check Python version
echo ""
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python 3.8+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# 3. Create directory structure
echo ""
echo "📁 Creating directory structure..."
INSTALL_DIR="$HOME/.rejoice"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/logs"
echo -e "${GREEN}✓${NC} Created $INSTALL_DIR"

# 4. Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "$INSTALL_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists. Removing old one...${NC}"
    rm -rf "$INSTALL_DIR/venv"
fi

python3 -m venv "$INSTALL_DIR/venv"
echo -e "${GREEN}✓${NC} Virtual environment created"

# 5. Install package
echo ""
echo "📦 Installing Rejoice package..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install --upgrade setuptools wheel --quiet

# Check if we're installing from source or PyPI
if [ -f "pyproject.toml" ] && [ -f "setup.py" ]; then
    # Installing from source (development)
    echo "   Installing from source..."
    "$INSTALL_DIR/venv/bin/pip" install -e . --quiet
else
    # Installing from PyPI (production)
    echo "   Installing from PyPI..."
    "$INSTALL_DIR/venv/bin/pip" install rejoice-slim --quiet
fi

echo -e "${GREEN}✓${NC} Package installed"

# 6. Set up shell alias
echo ""
echo "⚙️  Setting up shell alias..."

# Detect shell
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    bash)
        if [[ "$OS" == "Darwin" ]]; then
            RC_FILE="$HOME/.bash_profile"
        else
            RC_FILE="$HOME/.bashrc"
        fi
        ;;
    zsh)
        RC_FILE="$HOME/.zshrc"
        ;;
    fish)
        RC_FILE="$HOME/.config/fish/config.fish"
        mkdir -p "$HOME/.config/fish"
        ;;
    *)
        # Default to bash
        RC_FILE="$HOME/.bashrc"
        echo -e "${YELLOW}⚠️  Unknown shell '$SHELL_NAME', defaulting to bash${NC}"
        ;;
esac

# Check if alias already exists
ALIAS_LINE="alias rec=\"\$HOME/.rejoice/venv/bin/rec\""
if grep -q "alias rec=" "$RC_FILE" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  'rec' alias already exists in $RC_FILE${NC}"
    echo "   Skipping alias setup. You can manually add: $ALIAS_LINE"
else
    # Add alias
    {
        echo ""
        echo "# Rejoice - Voice Transcription"
        echo "$ALIAS_LINE"
    } >> "$RC_FILE"
    echo -e "${GREEN}✓${NC} Added 'rec' alias to $RC_FILE"
fi

# 7. Test installation
echo ""
echo "🧪 Testing installation..."
if "$INSTALL_DIR/venv/bin/rec" --version &> /dev/null; then
    VERSION=$("$INSTALL_DIR/venv/bin/rec" --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓${NC} Installation test passed (version: $VERSION)"
else
    echo -e "${YELLOW}⚠️  Installation test inconclusive (command may not be fully configured yet)${NC}"
fi

# 8. Success message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Rejoice v2 installed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo ""
echo "   1. Activate the alias in your current shell:"
echo "      source $RC_FILE"
echo ""
echo "   2. Or restart your terminal"
echo ""
echo "   3. Start recording:"
echo "      rec"
echo ""
echo "   4. First time setup (optional):"
echo "      rec settings"
echo ""
echo "📚 For help:"
echo "   rec --help"
echo ""
echo "📁 Installation location:"
echo "   $INSTALL_DIR"
echo ""
echo "🗑️  To uninstall:"
echo "   rec uninstall"
echo ""
