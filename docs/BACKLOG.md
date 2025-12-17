# 🎙️ Rejoice v2 - Development Backlog

**Last Updated:** December 17, 2024
**Status:** Ready for Development
**Target:** v2.0.0 Release

---

## 📊 Progress Overview

- **Total Stories:** 91
- **Completed:** 8
- **In Progress:** 0
- **Not Started:** 83

---

## 🗺️ Development Phases

### Phase 0: Installation & Environment (Day 1) 🏗️
**Must complete FIRST** - Can't develop without a working environment!
- 3 stories: Dev environment, user installation script, uninstall script
- Estimated: 2-3 days

### Phase 1: Foundation & Project Setup (Week 1) 🧱
Project structure, config system, testing framework, CLI skeleton
- 6 stories | 4-5 days

### Phase 2: Core Recording System (Week 2) 🎙️
Audio capture, file management, recording controls
- 10 stories | 5-7 days

### Phase 3: Transcription System (Week 3) 📝
faster-whisper integration, streaming to file, file processing
- 8 stories | 5-7 days

### Phase 4: Advanced Transcription (Week 4) 🎯
Speaker diarization, timestamps, quality metrics
- 5 stories | 3-4 days

### Phase 5: AI Enhancement (Week 5) 🤖
Ollama integration, summaries, tags, titles, analysis
- 10 stories | 5-7 days

### Phase 6: User Commands (Week 6) 💻
List, view, search, export, continue commands
- 10 stories | 5-6 days

### Phase 7: Configuration & Settings (Week 7) ⚙️
Settings menu, microphone setup, model config, doctor command
- 10 stories | 5-6 days

### Phase 8: Polish & Release (Week 8-9) ✨
CI/CD, documentation, performance, UAT, security, launch
- 13 stories | 7-10 days

---

## 🎯 How to Use This Backlog

### Story Format
```
### [ID] Story Title
**Priority:** Critical | High | Medium | Low
**Estimate:** XS (< 2h) | S (2-4h) | M (4-8h) | L (1-2d) | XL (2-5d)
**Status:** ❌ Not Started | 🚧 In Progress | ✅ Done
**Dependencies:** [Other story IDs]

**User Story:**
As a [user type], I want [goal] so that [benefit].

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Technical Notes:**
- Implementation details
- Edge cases to consider

**Test Requirements:**
- Unit tests needed
- Integration tests needed
```

### Status Legend
- ❌ Not Started
- 🚧 In Progress
- ✅ Done
- ⏸️ Blocked
- 🔄 In Review

---

## Phase 0: Installation & Environment (Day 1)

### [I-001] Installation Script
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ✅ Done
**Dependencies:** None

**User Story:**
As a user, I want one-command installation so that setup is effortless.

**Acceptance Criteria:**
- [x] `curl | bash` installer works
- [x] Creates virtual environment
- [x] Installs dependencies
- [x] Sets up config directory
- [x] Creates `rec` command alias
- [x] Tests installation
- [x] Works on macOS and Linux

**Technical Notes:**
```bash
#!/bin/bash
# install.sh

# Detect OS
OS="$(uname -s)"

# Install system dependencies
if [ "$OS" = "Darwin" ]; then
    brew install portaudio ffmpeg
elif [ "$OS" = "Linux" ]; then
    sudo apt-get install portaudio19-dev ffmpeg
fi

# Create venv
python3 -m venv ~/.rejoice/venv

# Install package
~/.rejoice/venv/bin/pip install rejoice

# Create alias
echo 'alias rec="~/.rejoice/venv/bin/rec"' >> ~/.bashrc
```

**Test Requirements:**
- Test on fresh macOS
- Test on fresh Linux (Ubuntu, Debian)
- Test with different shells (bash, zsh)
- Test venv isolation

---

### [I-002] Development Environment Setup
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** None

**User Story:**
As a developer, I want a reproducible development environment so that all contributors have the same setup.

**Acceptance Criteria:**
- [x] README.md with dev setup instructions
- [x] Requirements files (pyproject.toml with dev dependencies)
- [x] Virtual environment instructions
- [x] Pre-commit hooks configured
- [ ] IDE settings (VSCode recommended settings) - Optional
- [x] Environment variables documented (.env.example)

**Technical Notes:**
```bash
# Development setup
git clone https://github.com/user/rejoice-v2.git
cd rejoice-v2
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

**Test Requirements:**
- Test on fresh clone
- Verify all dev tools work
- Test pre-commit hooks

---

### [I-003] Uninstallation Script
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [I-001]

**User Story:**
As a user, I want clean uninstallation so that Rejoice doesn't leave system pollution.

**Acceptance Criteria:**
- [x] `rec uninstall` removes everything (backed by `scripts/uninstall.sh`)
- [x] Remove virtual environment
- [x] Remove config directory (with confirmation)
- [x] Remove command aliases
- [x] Optionally keep transcripts
- [x] Confirmation prompts

**Technical Notes:**
```bash
#!/bin/bash
# Included in package

echo "This will remove Rejoice from your system."
echo "Your transcripts will NOT be deleted."
read -p "Continue? (y/n) " -n 1 -r

echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.rejoice
    # Remove alias from shell rc
fi
```

**Test Requirements:**
- Test complete removal
- Test transcript preservation
- Test on different systems

---

## Phase 1: Foundation & Project Setup (Week 1)

### [F-001] Project Structure Setup
**Priority:** Critical
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** None

**User Story:**
As a developer, I want a well-organized project structure so that the codebase is easy to navigate and maintain.

**Acceptance Criteria:**
- [x] Directory structure follows Python best practices
- [x] `src/` for source code
- [x] `tests/` with unit/integration/e2e subdirectories
- [x] `docs/` for documentation
- [x] `scripts/` for installation/setup scripts
- [x] `.github/workflows/` for CI/CD
- [x] Root level: README, LICENSE, pyproject.toml

**Technical Notes:**
```
rejoice-v2/
├── src/
│   └── rejoice/
│       ├── __init__.py
│       ├── cli/
│       ├── core/
│       ├── transcription/
│       ├── ai/
│       └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── docs/
├── scripts/
└── pyproject.toml
```

**Test Requirements:**
- N/A (setup task)

---

## Phase 2: Core Recording System (Week 2)

### [R-001] Audio Device Detection
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [F-005]

**User Story:**
As a user, I want Rejoice to detect my microphone automatically so that I don't have to configure anything manually.

**Acceptance Criteria:**
- [ ] Detect available audio input devices
- [ ] Handle no devices gracefully
- [ ] Show device list with `rec config list-mics`
- [ ] Default to system default device
- [ ] Support device selection by index or name
- [ ] Test concurrent access (Zoom + Rejoice)

**Technical Notes:**
```python
import sounddevice as sd


def get_audio_devices():
    devices = sd.query_devices()
    input_devices = [d for d in devices if d["max_input_channels"] > 0]
    return input_devices
```

**Test Requirements:**
- Unit test device detection
- Integration test with mock audio device
- Test device selection

---

... (rest of backlog unchanged) ...
