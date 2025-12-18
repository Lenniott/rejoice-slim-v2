# 🎙️ Rejoice v2 - Development Backlog

**Last Updated:** December 18, 2025
**Status:** Ready for Development
**Target:** v2.0.0 Release

---

## 📊 Progress Overview

- **Total Stories:** 91
- **Completed:** 18
- **In Progress:** 0
- **Not Started:** 73

---

## 🎯 Priority Tiers (MVP → MMP → MLP)

These priority tiers sit **above phases**. When choosing what to work on next:

1. Always prefer **MVP** stories first.
2. Then move on to **MMP** (Minimum Marketable Product).
3. Treat all remaining stories as **MLP** (Minimum Lovable Product).

**MVP (Minimum Viable Product) – Core end‑to‑end flow**

- Phase 0 / 1 foundations:
  - [I-001], [I-002], [I-003], [I-004]
  - [F-001], [F-002], [F-003], [F-004], [F-005], [F-006]
- Core recording & transcripts:
  - [R-001], [R-002], [R-003], [R-004], [R-006], [R-007], [R-008]
- Core transcription:
  - [T-001], [T-002], [T-003]
- Core user commands:
  - [C-001], [C-003]

**MMP (Minimum Marketable Product) – Makes it pleasant for everyday use**

- Recording polish:
  - [R-009], [R-010]
- Transcription usability:
  - [T-004], [T-005], [T-006]
- CLI quality of life:
  - [C-002], [C-004], [C-005]
- Settings & setup:
  - [S-001], [S-002], [S-004]
- Basic AI assist:
  - [AI-001], [AI-003], [AI-005]

**MLP (Minimum Lovable Product) – Everything else**

- All stories **not listed above** are implicitly treated as **MLP**.

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
- [ ] `rec uninstall` removes everything
- [ ] Remove virtual environment
- [ ] Remove config directory (with confirmation)
- [ ] Remove command aliases
- [ ] Optionally keep transcripts
- [ ] Confirmation prompts

**Technical Notes:**
```bash
#!/bin/bash
# Included in package

echo "This will remove Rejoice from your system."
echo "Your transcripts will NOT be deleted."
read -p "Continue? (y/n) " -n 1 -r

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
- [ ] Directory structure follows Python best practices
- [ ] `src/` for source code
- [ ] `tests/` with unit/integration/e2e subdirectories
- [ ] `docs/` for documentation
- [ ] `scripts/` for installation/setup scripts
- [ ] `.github/workflows/` for CI/CD
- [ ] Root level: README, LICENSE, pyproject.toml

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

### [F-002] Python Package Configuration
**Priority:** Critical
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [F-001]

**User Story:**
As a developer, I want proper package configuration so that installation and dependency management is straightforward.

**Acceptance Criteria:**
- [ ] `pyproject.toml` configured with Poetry or setuptools
- [ ] Project metadata defined (name, version, authors)
- [ ] Dependencies specified with version constraints
- [ ] Dev dependencies separated
- [ ] Entry points defined for `rec` command
- [ ] Python version requirement (>= 3.8)

**Technical Notes:**
```toml
[tool.poetry]
name = "rejoice"
version = "2.0.0"
description = "Local-first voice transcription"

[tool.poetry.scripts]
rec = "rejoice.cli:main"
```

**Test Requirements:**
- Test that `rec` command is available after install
- Test in fresh virtual environment

---

### [F-003] Testing Framework Setup
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** [F-001, F-002]

**User Story:**
As a developer, I want a comprehensive testing framework so that I can practice TDD and maintain high code quality.

**Acceptance Criteria:**
- [ ] pytest configured
- [ ] pytest-cov for coverage reports
- [ ] pytest-asyncio for async tests
- [ ] Test fixtures structure created
- [ ] Sample test files for each test type
- [ ] Coverage reporting configured (90% target)
- [ ] Pre-commit hooks for running tests

**Technical Notes:**
```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html --cov-report=term
```

**Test Requirements:**
- Create sample passing test to verify setup
- Test coverage report generation

---

### [F-004] Configuration System Design
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ✅ Done
**Dependencies:** [F-002]

**User Story:**
As a user, I want a flexible configuration system so that I can customize Rejoice to my preferences without editing code.

**Acceptance Criteria:**
- [ ] `config.yaml` format designed
- [ ] `.env` support for sensitive values
- [ ] Config validation with schema
- [ ] Default configuration included
- [ ] User config overrides defaults
- [ ] Config location: `~/.config/rejoice/config.yaml`
- [ ] `rec config` commands work

**Technical Notes:**
```yaml
# config.yaml structure
transcription:
  model: medium
  language: auto
  vad_filter: true

output:
  save_path: ~/Documents/transcripts
  template: default
  auto_analyze: true
  auto_copy: true

audio:
  device: default
  sample_rate: 16000

ai:
  ollama_url: http://localhost:11434
  model: llama2
  prompts_path: ~/.config/rejoice/prompts/
```

**Test Requirements:**
- Unit tests for config loading
- Test default config
- Test config validation
- Test config merging (defaults + user overrides)

---

### [F-005] CLI Framework Setup
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** [F-002, F-004]

**User Story:**
As a user, I want intuitive CLI commands so that I can interact with Rejoice naturally.

**Acceptance Criteria:**
- [ ] Click or Typer framework configured
- [ ] Main `rec` command works
- [ ] Subcommands structure established
- [ ] `--help` provides clear information
- [ ] `--version` shows version
- [ ] `--debug` flag available globally
- [ ] Color output with rich library

**Technical Notes:**
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def record():
    """Start recording"""
    pass

@app.command()
def list():
    """List all recordings"""
    pass
```

**Test Requirements:**
- Test command registration
- Test help output
- Test version output
- Test debug flag

---

### [F-006] Logging System
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [F-004]

**User Story:**
As a user/developer, I want clear logging so that I can troubleshoot issues and understand what's happening.

**Acceptance Criteria:**
- [ ] Structured logging with Python logging module
- [ ] Different log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Log to file: `~/.config/rejoice/logs/rejoice.log`
- [ ] Console output respects `--debug` flag
- [ ] Log rotation configured (max 10MB, 5 files)
- [ ] Pretty formatting for terminal output

**Technical Notes:**
```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("~/.config/rejoice/logs/rejoice.log")
    ]
)
```

**Test Requirements:**
- Test log file creation
- Test different log levels
- Test debug mode enables verbose output

---

## Phase 2: Core Recording System (Week 2)

### [R-001] Audio Device Detection
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
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
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    return input_devices
```

**Test Requirements:**
- Unit test device detection
- Integration test with mock audio device
- Test device selection

---

### [R-002] Audio Capture Implementation
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ✅ Done
**Dependencies:** [R-001]

**User Story:**
As a user, I want to record audio from my microphone so that I can capture spoken content.

**Acceptance Criteria:**
- [ ] Capture audio using sounddevice
- [ ] Sample rate: 16kHz (Whisper requirement)
- [ ] Mono channel
- [ ] Real-time streaming to buffer
- [ ] Handle audio device errors
- [ ] Work concurrently with other apps
- [ ] Clean start/stop without clicks

**Technical Notes:**
```python
import sounddevice as sd
import numpy as np

def record_audio(callback, device=None):
    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        callback=callback,
        device=device
    )
    stream.start()
    return stream
```

**Test Requirements:**
- Unit test with mock audio
- Integration test with real device
- Test concurrent access
- Test error handling (device busy, disconnected)

---

### [R-003] Transcript Manager - Create File
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** [F-004]

**User Story:**
As a user, I want transcripts saved immediately when I start recording so that I never lose data even if the system crashes.

**Acceptance Criteria:**
- [x] Create MD file with unique ID on record start
- [x] Generate next available ID (000001, 000002, etc.)
- [x] Add YAML frontmatter with metadata
- [x] File naming: `transcript_YYYYMMDD_ID.md`
- [x] Save to configured directory
- [x] Handle directory creation if needed
- [x] Atomic file creation (temp + rename)

**Technical Notes:**
```python
def create_transcript(save_dir: Path) -> tuple[Path, str]:
    """Create new transcript file immediately"""
    transcript_id = get_next_id(save_dir)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"transcript_{date_str}_{transcript_id}.md"

    frontmatter = generate_frontmatter(transcript_id)
    filepath = save_dir / filename

    # Atomic write
    write_file_atomic(filepath, frontmatter)

    return filepath, transcript_id
```

**Test Requirements:**
- Test ID generation
- Test file creation
- Test frontmatter format
- Test atomic write
- Test directory creation
- Test duplicate ID handling

---

### [R-004] Transcript Manager - Append Content
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-003]

**User Story:**
As a system, I want to append transcribed text to the file in real-time so that partial transcripts are never lost.

**Acceptance Criteria:**
- [ ] Append text to existing file
- [ ] Preserve frontmatter
- [ ] Atomic append operation (read + write temp + rename)
- [ ] Handle concurrent write safety
- [ ] No data corruption on crash
- [ ] Maintain proper line breaks

**Technical Notes:**
```python
def append_to_transcript(filepath: Path, text: str):
    """Atomically append text to transcript"""
    # Read existing
    existing = filepath.read_text()

    # Append new content
    updated = existing + "\n" + text

    # Atomic write
    write_file_atomic(filepath, updated)
```

**Test Requirements:**
- Test atomic append
- Test with simulated crash mid-write
- Test preserve frontmatter
- Test concurrent append safety
- Test large content append

---

### [R-005] ID Normalization System
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-003]

**User Story:**
As a user, I want to type just "1" instead of "000001" so that commands are faster and easier.

**Acceptance Criteria:**
- [ ] Accept "1", "01", "001", "000001" - all work
- [ ] Normalize to 6-digit format internally
- [ ] Display padded format in listings
- [ ] Case-insensitive ID lookup
- [ ] Handle invalid IDs gracefully

**Technical Notes:**
```python
def normalize_id(user_input: str) -> str:
    """Convert any format to 6-digit ID"""
    try:
        num = int(user_input)
        return str(num).zfill(6)
    except ValueError:
        raise InvalidIDError(f"'{user_input}' is not a valid ID")
```

**Test Requirements:**
- Test various input formats
- Test invalid inputs
- Test edge cases (negative, too large)

---

### [R-006] Recording Control - Start
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-002, R-003]

**User Story:**
As a user, I want to type "rec" and immediately start recording so that capturing ideas is effortless.

**Acceptance Criteria:**
- [ ] `rec` command starts recording
- [ ] Create transcript file first
- [ ] Start audio capture
- [ ] Show recording indicator
- [ ] Display duration counter
- [ ] Handle Ctrl+C gracefully

**Technical Notes:**
```python
@app.command()
def record():
    # 1. Create transcript file immediately
    filepath, tid = create_transcript()

    # 2. Start audio capture
    stream = start_audio_capture()

    # 3. Show UI
    show_recording_ui(filepath, tid)

    # 4. Wait for stop signal
    wait_for_stop()
```

**Test Requirements:**
- E2E test full recording flow
- Test file created before audio starts
- Test UI display
- Test graceful shutdown

---

### [R-007] Recording Control - Stop
**Priority:** Critical
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-006]

**User Story:**
As a user, I want to press Enter to stop recording so that I have an obvious, simple way to finish.

**Acceptance Criteria:**
- [ ] Enter key stops recording cleanly
- [ ] Finalize transcript file
- [ ] Stop audio capture
- [ ] Update frontmatter status to "completed"
- [ ] Show success message with file location
- [ ] Show next steps

**Technical Notes:**
```python
def stop_recording(stream, filepath):
    # Stop audio
    stream.stop()
    stream.close()

    # Update frontmatter
    update_status(filepath, "completed")

    # Show completion UI
    show_success(filepath)
```

**Test Requirements:**
- Test clean stop
- Test frontmatter update
- Test success message

---

### [R-008] Recording Control - Cancel
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-006]

**User Story:**
As a user, I want to press Ctrl+C to cancel a recording so that I can discard mistakes without keeping files.

**Acceptance Criteria:**
- [ ] Ctrl+C stops recording immediately
- [ ] Optionally delete transcript file
- [ ] Confirm before deletion
- [ ] Or mark as "cancelled" in frontmatter
- [ ] Clean shutdown

**Technical Notes:**
```python
import signal

def handle_interrupt(signum, frame):
    if confirm("Cancel recording? (file will be deleted)"):
        cleanup_and_exit()
    else:
        continue_recording()
```

**Test Requirements:**
- Test Ctrl+C handling
- Test file deletion
- Test confirmation prompt
- Test cancelled status

---

### [R-009] Recording UI - Progress Display
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-006]

**User Story:**
As a user, I want to see recording status so that I know the system is working.

**Acceptance Criteria:**
- [ ] Show "🔴 Recording..." indicator
- [ ] Display elapsed time (0:00, 0:01, etc.)
- [ ] Update every second
- [ ] Clear instructions (Press Enter to stop)
- [ ] Microphone name shown
- [ ] Save location shown

**Technical Notes:**
```python
from rich.live import Live
from rich.panel import Panel

def show_recording_ui(filepath, tid):
    with Live(auto_refresh=False) as live:
        while recording:
            duration = get_elapsed_time()
            panel = Panel(
                f"🔴 Recording... ({duration})",
                title="Rejoice"
            )
            live.update(panel)
            time.sleep(1)
```

**Test Requirements:**
- Test UI rendering
- Test timer updates
- Test clean display

---

### [R-010] Audio Buffer Management
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-002]

**User Story:**
As a system, I want to buffer audio data efficiently so that transcription has access to complete audio without memory overflow.

**Acceptance Criteria:**
- [ ] Circular buffer for audio chunks
- [ ] Configurable buffer size (default: 30 seconds)
- [ ] Thread-safe read/write
- [ ] Provide audio segments to transcriber
- [ ] Handle overflow gracefully

**Technical Notes:**
```python
from collections import deque
import threading

class AudioBuffer:
    def __init__(self, max_duration_seconds=30):
        self.buffer = deque(maxlen=max_duration_seconds * 16)
        self.lock = threading.RLock()

    def write(self, chunk):
        with self.lock:
            self.buffer.append(chunk)

    def read_segment(self, duration):
        with self.lock:
            return list(self.buffer)[-duration:]
```

**Test Requirements:**
- Test thread safety
- Test overflow handling
- Test read/write operations
- Test buffer size limits

---

## Phase 3: Transcription System (Week 3)

### [T-001] faster-whisper Integration
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [R-002]

**User Story:**
As a user, I want accurate transcription so that my spoken words are converted to text correctly.

**Acceptance Criteria:**
- [ ] faster-whisper library integrated
- [ ] Model downloading on first use
- [ ] Model caching for subsequent uses
- [ ] Support all model sizes (tiny, base, small, medium, large)
- [ ] Configurable via config.yaml
- [ ] Handle long audio without failure
- [ ] VAD filter enabled by default

**Technical Notes:**
```python
from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self, config):
        self.model = WhisperModel(
            config.model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(
            audio_path,
            vad_filter=True,
            language=config.language
        )
        return segments
```

**Test Requirements:**
- Test with sample audio files
- Test each model size
- Test long audio (>30 min)
- Test with silence periods
- Test VAD filter effectiveness

---

### [T-002] Language Detection & Control
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want to control transcription language so that muffled English isn't detected as Chinese.

**Acceptance Criteria:**
- [ ] Auto-detect language by default
- [ ] Override with `--language en` flag
- [ ] Support all Whisper languages
- [ ] Save detected language in frontmatter
- [ ] Config file default language setting

**Technical Notes:**
```python
# Supported languages
LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh', ...]

def transcribe_with_language(audio, language='auto'):
    if language == 'auto':
        segments, info = model.transcribe(audio)
        detected = info.language
    else:
        segments, info = model.transcribe(audio, language=language)
        detected = language
    return segments, detected
```

**Test Requirements:**
- Test auto-detection
- Test forced language
- Test with multiple languages
- Test language saved to frontmatter

---

### [T-003] Streaming Transcription to File
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [T-001, R-004]

**User Story:**
As a user, I want transcription to be saved continuously so that I never lose partial work if something crashes.

**Acceptance Criteria:**
- [ ] Transcribe audio in segments
- [ ] Append each segment to file immediately
- [ ] No buffering - write as soon as transcribed
- [ ] Handle streaming gracefully
- [ ] Coordinate with audio capture

**Technical Notes:**
```python
def streaming_transcription(audio_stream, transcript_file):
    for audio_chunk in audio_stream:
        # Transcribe chunk
        segment_text = transcribe_chunk(audio_chunk)

        # Immediately append to file
        append_to_transcript(transcript_file, segment_text)

        # Show in UI (optional)
        display_text(segment_text)
```

**Test Requirements:**
- Test continuous streaming
- Test crash recovery (file has partial content)
- Test with long recordings
- Integration test full pipeline

---

### [T-004] VAD Configuration
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want silence detection to work properly so that long pauses don't cause transcription to fail.

**Acceptance Criteria:**
- [ ] VAD (Voice Activity Detection) enabled by default
- [ ] Configurable VAD threshold
- [ ] Test with long silence periods
- [ ] No failures on 30+ minute recordings with pauses

**Technical Notes:**
```python
# faster-whisper VAD parameters
model.transcribe(
    audio,
    vad_filter=True,
    vad_parameters=dict(
        threshold=0.5,
        min_silence_duration_ms=500
    )
)
```

**Test Requirements:**
- Test with speech + 5 min silence + speech
- Test different VAD thresholds
- Test lecture-style recordings with pauses

---

### [T-005] Transcription Progress Indicator
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-003]

**User Story:**
As a user, I want to see transcription progress so that I know how long it will take.

**Acceptance Criteria:**
- [ ] Show "🔄 Transcribing..." during processing
- [ ] Progress percentage if determinable
- [ ] Estimated time remaining
- [ ] Segments completed / total
- [ ] Clean, non-intrusive display

**Technical Notes:**
```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Transcribing...", total=duration)
    for segment in transcribe(audio):
        progress.update(task, advance=segment.duration)
```

**Test Requirements:**
- Test progress display
- Test with various audio lengths
- Test UI updates

---

### [T-006] Handle Audio File Processing
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want to transcribe existing audio files so that I can process recordings made elsewhere.

**Acceptance Criteria:**
- [ ] `rec process <file>` command works
- [ ] Support: mp3, wav, m4a, ogg, flac, aac
- [ ] Create transcript file with same ID system
- [ ] All transcription options available
- [ ] Progress indicator

**Technical Notes:**
```python
@app.command()
def process(filepath: Path, language: str = 'auto'):
    # Validate file exists and is audio
    validate_audio_file(filepath)

    # Create transcript
    transcript_file, tid = create_transcript()

    # Transcribe
    transcribe_file(filepath, transcript_file, language)

    # Show results
    show_completion(transcript_file, tid)
```

**Test Requirements:**
- Test with each audio format
- Test with invalid files
- Test with large files (>100MB)

---

### [T-007] Handle Video File Processing
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-006]

**User Story:**
As a user, I want to transcribe video files so that I can extract audio from recordings like Zoom meetings.

**Acceptance Criteria:**
- [ ] Support: mp4, mov, avi, mkv, webm
- [ ] Extract audio automatically
- [ ] Temporary audio file cleaned up after
- [ ] Progress shown for extraction + transcription

**Technical Notes:**
```python
import ffmpeg

def extract_audio(video_path: Path) -> Path:
    """Extract audio from video file"""
    audio_path = video_path.with_suffix('.wav')

    ffmpeg.input(str(video_path)).output(
        str(audio_path),
        acodec='pcm_s16le',
        ar='16000',
        ac=1
    ).run(quiet=True)

    return audio_path
```

**Test Requirements:**
- Test with each video format
- Test audio extraction quality
- Test cleanup of temp files

---

### [T-008] Batch File Processing
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [T-006]

**User Story:**
As a user, I want to process multiple files at once so that I can batch-transcribe recorded meetings.

**Acceptance Criteria:**
- [ ] `rec process *.mp3` works
- [ ] `rec process /path/to/folder/` works
- [ ] Progress for each file
- [ ] Summary at end
- [ ] Continue on error (don't stop batch)

**Technical Notes:**
```python
@app.command()
def process(files: List[Path]):
    results = []
    for file in files:
        try:
            result = process_single_file(file)
            results.append(('✅', file, result))
        except Exception as e:
            results.append(('❌', file, str(e)))

    show_batch_summary(results)
```

**Test Requirements:**
- Test with multiple files
- Test with mix of valid/invalid files
- Test error handling

---

## Phase 4: Advanced Transcription Features (Week 4)

### [A-001] WhisperX Integration
**Priority:** Medium
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want speaker diarization so that I can identify who said what in conversations.

**Acceptance Criteria:**
- [ ] WhisperX library integrated
- [ ] Speaker diarization optional feature
- [ ] Label speakers as "Speaker 1", "Speaker 2", etc.
- [ ] Maintain speaker consistency across segments
- [ ] Enable with `--speakers` flag

**Technical Notes:**
```python
import whisperx

def transcribe_with_diarization(audio_path):
    # Load audio
    audio = whisperx.load_audio(audio_path)

    # Transcribe
    result = whisper_model.transcribe(audio)

    # Align whisper output
    result = whisperx.align(result, model, audio)

    # Diarize
    diarize_model = whisperx.DiarizationPipeline()
    diarize_segments = diarize_model(audio)

    # Assign speakers to segments
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return result
```

**Test Requirements:**
- Test with multi-speaker audio
- Test speaker consistency
- Test with 2-5 speakers
- Test accuracy with fixture files

---

### [A-002] Speaker Label Formatting
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [A-001]

**User Story:**
As a user, I want speaker labels clearly shown in transcripts so that I can easily see who spoke.

**Acceptance Criteria:**
- [ ] Format: "**Speaker 1:** [text]"
- [ ] Consistent labeling throughout
- [ ] Option to customize format in template
- [ ] Clear visual separation

**Technical Notes:**
```markdown
**Speaker 1:** So we discussed the Q4 roadmap today.

**Speaker 2:** Yes, and we decided to prioritize the mobile app launch.

**Speaker 1:** Right, Sarah mentioned the timeline concerns.
```

**Test Requirements:**
- Test formatting
- Test with multiple speakers
- Test format customization

---

### [A-003] Timestamp Integration
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want timestamps in my transcript so that I can reference specific moments in the recording.

**Acceptance Criteria:**
- [ ] Timestamps at segment boundaries
- [ ] Format: `[00:00]`, `[00:42]`, `[12:34]`
- [ ] Toggle with `--timestamps` flag
- [ ] Configurable in config.yaml
- [ ] Option to show only on speaker changes

**Technical Notes:**
```markdown
[00:00] So today we discussed the Q4 roadmap and decided to prioritize the mobile app launch.

[00:15] Sarah mentioned that the timeline is tight but achievable.

[00:32] We need to coordinate with the design team.
```

**Test Requirements:**
- Test timestamp accuracy
- Test formatting
- Test toggle on/off

---

### [A-004] Combined Speaker + Timestamp
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [A-002, A-003]

**User Story:**
As a user, I want both speakers and timestamps so that I have complete context for conversations.

**Acceptance Criteria:**
- [ ] Format: `[00:00] **Speaker 1:** [text]`
- [ ] Enable with `--speakers --timestamps`
- [ ] Clean, readable output

**Technical Notes:**
```markdown
[00:00] **Speaker 1:** So we discussed the Q4 roadmap today.

[00:12] **Speaker 2:** Yes, and we decided to prioritize the mobile app launch.

[00:28] **Speaker 1:** Right, Sarah mentioned the timeline concerns.
```

**Test Requirements:**
- Test combined formatting
- Test readability
- Test toggle combinations

---

### [A-005] Transcription Quality Metrics
**Priority:** Low
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [T-001]

**User Story:**
As a user, I want to know transcription quality so that I can decide if I need to re-transcribe with a better model.

**Acceptance Criteria:**
- [ ] Show confidence scores in frontmatter
- [ ] Average confidence per segment
- [ ] Flag low-confidence segments
- [ ] Optional: highlight uncertain words

**Technical Notes:**
```yaml
---
transcription:
  avg_confidence: 0.87
  low_confidence_segments: 3
  language_confidence: 0.95
---
```

**Test Requirements:**
- Test confidence calculation
- Test with clear vs unclear audio
- Test metrics accuracy

---

## Phase 5: AI Enhancement (Week 5)

### [AI-001] Ollama Client Integration
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [F-004]

**User Story:**
As a user, I want AI-powered analysis so that I can extract insights from transcripts.

**Acceptance Criteria:**
- [ ] Ollama REST API integration
- [ ] Connection test: `rec doctor ollama`
- [ ] Model selection configurable
- [ ] Handle Ollama not running gracefully
- [ ] Streaming response support

**Technical Notes:**
```python
import requests

class OllamaClient:
    def __init__(self, base_url='http://localhost:11434'):
        self.base_url = base_url

    def generate(self, prompt, model='llama2'):
        response = requests.post(
            f'{self.base_url}/api/generate',
            json={'model': model, 'prompt': prompt}
        )
        return response.json()
```

**Test Requirements:**
- Test connection
- Test with/without Ollama running
- Test different models
- Test streaming

---

### [AI-002] Prompt Template System
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [AI-001]

**User Story:**
As a user, I want to customize AI prompts so that I can tailor analysis to my needs.

**Acceptance Criteria:**
- [ ] Prompt templates stored in `~/.config/rejoice/prompts/`
- [ ] Templates are editable text files
- [ ] Variables: `{transcript}`, `{language}`, `{duration}`
- [ ] Default templates included
- [ ] Easy to create custom templates

**Technical Notes:**
```
~/.config/rejoice/prompts/
├── summary.txt
├── tags.txt
├── questions.txt
├── actions.txt
└── title.txt
```

```
# summary.txt
Analyze this transcript and provide a concise summary:

{transcript}

Focus on:
- Main themes
- Key decisions
- Important points

Summary:
```

**Test Requirements:**
- Test template loading
- Test variable substitution
- Test custom templates
- Test missing templates (use defaults)

---

### [AI-003] Summary Generation
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [AI-002]

**User Story:**
As a user, I want AI summaries so that I can quickly understand transcript content without reading everything.

**Acceptance Criteria:**
- [ ] `rec analyze <id>` generates summary
- [ ] Summary added to frontmatter
- [ ] 2-3 sentence concise summary
- [ ] Captures main themes
- [ ] Works with long transcripts (chunking if needed)

**Technical Notes:**
```python
def generate_summary(transcript_text):
    prompt = load_template('summary.txt').format(
        transcript=transcript_text
    )
    summary = ollama_client.generate(prompt)
    return summary.strip()
```

**Test Requirements:**
- Test with short transcripts
- Test with long transcripts
- Test summary quality
- Test frontmatter update

---

### [AI-004] Tag Generation
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [AI-002]

**User Story:**
As a user, I want automatic tags so that transcripts are organized and searchable.

**Acceptance Criteria:**
- [ ] Generate 3-7 relevant tags
- [ ] Tags based on content themes
- [ ] Added to frontmatter as YAML array
- [ ] Lowercase, hyphenated format

**Technical Notes:**
```yaml
tags: [meeting, project-alpha, timeline, q4-planning]
```

**Test Requirements:**
- Test tag relevance
- Test tag format
- Test number of tags (3-7)

---

### [AI-005] Title Generation
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [AI-002]

**User Story:**
As a user, I want descriptive file names so that I can identify transcripts without opening them.

**Acceptance Criteria:**
- [ ] Generate descriptive title (3-7 words)
- [ ] Replace generic "transcript_YYYYMMDD_ID.md" name
- [ ] Format: "descriptive_title_YYYYMMDD_ID.md"
- [ ] Rename file atomically
- [ ] Title also added to frontmatter

**Technical Notes:**
```python
def rename_with_title(filepath, title):
    # Sanitize title for filename
    safe_title = sanitize_filename(title)

    # Keep date and ID
    parts = filepath.stem.split('_')
    date_id = '_'.join(parts[-2:])  # YYYYMMDD_ID

    # New name
    new_name = f"{safe_title}_{date_id}.md"
    new_path = filepath.parent / new_name

    # Atomic rename
    filepath.rename(new_path)
```

**Test Requirements:**
- Test title generation quality
- Test filename sanitization
- Test atomic rename
- Test title in frontmatter

---

### [AI-006] Question Extraction
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [AI-002]

**User Story:**
As a user, I want key questions extracted so that I can identify discussion points and decisions needed.

**Acceptance Criteria:**
- [ ] Extract main questions asked
- [ ] Extract unanswered questions
- [ ] List in frontmatter
- [ ] Format as bullet list

**Technical Notes:**
```yaml
questions:
  - "What's the timeline for mobile app launch?"
  - "Who will coordinate with the design team?"
  - "Do we have budget approval?"
```

**Test Requirements:**
- Test question extraction accuracy
- Test with transcripts containing questions
- Test with no questions

---

### [AI-007] Action Item Extraction
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [AI-002]

**User Story:**
As a user, I want action items extracted so that I know what needs to be done next.

**Acceptance Criteria:**
- [ ] Extract actionable items
- [ ] Identify who is responsible (if mentioned)
- [ ] Extract deadlines (if mentioned)
- [ ] List in frontmatter

**Technical Notes:**
```yaml
action_items:
  - "Sarah to create timeline for mobile app"
  - "Schedule meeting with design team by Friday"
  - "Get budget approval before next sprint"
```

**Test Requirements:**
- Test action extraction accuracy
- Test responsibility detection
- Test deadline extraction

---

### [AI-008] Full Analysis Command
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [AI-003, AI-004, AI-005, AI-006, AI-007]

**User Story:**
As a user, I want one command to run all AI analysis so that I get comprehensive insights easily.

**Acceptance Criteria:**
- [ ] `rec analyze <id>` runs all analyses
- [ ] `rec analyze <id> --full` includes extended analysis
- [ ] Progress indicator for each step
- [ ] All results added to frontmatter
- [ ] File renamed with AI title

**Technical Notes:**
```python
@app.command()
def analyze(transcript_id: str, full: bool = False):
    # Load transcript
    filepath = get_transcript_path(transcript_id)
    text = read_transcript_body(filepath)

    # Run analyses
    with Progress() as progress:
        task = progress.add_task("Analyzing...", total=5)

        title = generate_title(text)
        progress.advance(task)

        summary = generate_summary(text)
        progress.advance(task)

        tags = generate_tags(text)
        progress.advance(task)

        questions = extract_questions(text)
        progress.advance(task)

        actions = extract_actions(text)
        progress.advance(task)

    # Update frontmatter
    update_frontmatter(filepath, {
        'title': title,
        'summary': summary,
        'tags': tags,
        'questions': questions,
        'action_items': actions
    })

    # Rename file
    rename_with_title(filepath, title)
```

**Test Requirements:**
- Test full analysis pipeline
- Test with various transcript types
- Test progress display
- Integration test all AI features

---

### [AI-009] Analyze External Files
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [AI-008]

**User Story:**
As a user, I want to analyze any text file so that I can enhance existing notes with AI.

**Acceptance Criteria:**
- [ ] `rec analyze /path/to/file.txt` works
- [ ] Convert .txt to .md if needed
- [ ] Add frontmatter if missing
- [ ] Update frontmatter if exists
- [ ] Save as new file or overwrite (user choice)

**Technical Notes:**
```python
@app.command()
def analyze(path: Path, in_place: bool = False):
    # Read file
    content = path.read_text()

    # Check if has frontmatter
    has_fm, fm, body = parse_markdown(content)

    # Run AI analysis
    analysis = run_full_analysis(body)

    # Merge with existing frontmatter
    new_fm = {**fm, **analysis}

    # Write output
    if in_place:
        output_path = path
    else:
        output_path = path.with_stem(f"{path.stem}_analyzed")

    write_markdown(output_path, new_fm, body)
```

**Test Requirements:**
- Test with .txt files
- Test with .md files (with/without frontmatter)
- Test in-place vs new file
- Test frontmatter merging

---

### [AI-010] Batch Analyze Files
**Priority:** Low
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [AI-009]

**User Story:**
As a user, I want to batch analyze multiple files so that I can enhance entire folders of notes.

**Acceptance Criteria:**
- [ ] `rec analyze *.txt` works
- [ ] `rec analyze /path/to/folder/` works
- [ ] Progress for each file
- [ ] Summary at end
- [ ] Skip errors, continue processing

**Technical Notes:**
```python
for file in files:
    try:
        analyze_single_file(file)
        results.append(('✅', file))
    except Exception as e:
        results.append(('❌', file, str(e)))
```

**Test Requirements:**
- Test batch processing
- Test with mix of file types
- Test error handling

---

## Phase 6: User Commands (Week 6)

### [C-001] List Recordings Command
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-003]

**User Story:**
As a user, I want to see all my recordings so that I can find what I'm looking for.

**Acceptance Criteria:**
- [ ] `rec list` shows all transcripts
- [ ] Display: ID | Date | Filename
- [ ] Sorted by date (newest first)
- [ ] Pagination for many files
- [ ] Total count shown

**Technical Notes:**
```python
@app.command()
def list_recordings(limit: int = 50):
    files = get_all_transcripts()
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    table = Table(title="Your Recordings")
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Filename")

    for f in files[:limit]:
        id = extract_id(f)
        date = format_date(f.stat().st_mtime)
        table.add_row(id, date, f.name)

    console.print(table)
```

**Test Requirements:**
- Test with no recordings
- Test with many recordings
- Test sorting
- Test pagination

---

### [C-002] List with Filters
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [C-001]

**User Story:**
As a user, I want to filter recordings so that I can find specific ones quickly.

**Acceptance Criteria:**
- [ ] `rec list --recent 10` (last N recordings)
- [ ] `rec list --after "2024-12-01"`
- [ ] `rec list --before "2024-12-31"`
- [ ] `rec list --tag meeting`
- [ ] `rec list --search "keyword"`

**Technical Notes:**
```python
@app.command()
def list_recordings(
    recent: int = None,
    after: str = None,
    before: str = None,
    tag: str = None,
    search: str = None
):
    files = get_all_transcripts()

    # Apply filters
    if recent:
        files = files[:recent]
    if after:
        files = [f for f in files if f.date >= parse_date(after)]
    # ... other filters

    display_recordings(files)
```

**Test Requirements:**
- Test each filter independently
- Test combined filters
- Test date parsing

---

### [C-003] View Transcript Command
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-005]

**User Story:**
As a user, I want to read a transcript in the terminal so that I can review content quickly.

**Acceptance Criteria:**
- [ ] `rec view <id>` displays transcript
- [ ] Syntax highlighting for markdown
- [ ] Frontmatter shown separately (or hidden by default)
- [ ] Pagination for long transcripts
- [ ] `rec view latest` shows most recent

**Technical Notes:**
```python
from rich.markdown import Markdown

@app.command()
def view(transcript_id: str = 'latest'):
    if transcript_id == 'latest':
        filepath = get_latest_transcript()
    else:
        filepath = get_transcript_by_id(transcript_id)

    content = filepath.read_text()
    fm, body = parse_markdown(content)

    # Show frontmatter (optional)
    show_frontmatter(fm)

    # Render markdown
    md = Markdown(body)
    console.print(md)
```

**Test Requirements:**
- Test view by ID
- Test view latest
- Test with long transcripts
- Test markdown rendering

---

### [C-004] Continue/Append Command
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-004, R-006]

**User Story:**
As a user, I want to add more content to an existing transcript so that I can continue my thoughts later.

**Acceptance Criteria:**
- [ ] `rec continue <id>` starts recording
- [ ] Appends to existing transcript
- [ ] Preserves frontmatter
- [ ] Shows clear separator between sessions
- [ ] Updates "last_modified" timestamp

**Technical Notes:**
```python
@app.command()
def continue_recording(transcript_id: str):
    filepath = get_transcript_by_id(transcript_id)

    # Add session marker
    append_to_transcript(filepath, "\n\n---\n\n")
    append_to_transcript(filepath, f"## Continued: {datetime.now()}\n\n")

    # Start recording, append mode
    record_audio_to_file(filepath, append_mode=True)
```

**Test Requirements:**
- Test append to existing file
- Test session markers
- Test frontmatter preservation
- Test timestamp update

---

### [C-005] Open in Editor Command
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-005]

**User Story:**
As a user, I want to open transcripts in my editor so that I can edit and enhance them.

**Acceptance Criteria:**
- [ ] `rec open <id>` opens in default markdown editor
- [ ] `rec open <id> --editor vim` uses specific editor
- [ ] Detect: VSCode, Obsidian, vim, nano, etc.
- [ ] Configure default in config.yaml

**Technical Notes:**
```python
import subprocess

@app.command()
def open_transcript(transcript_id: str, editor: str = None):
    filepath = get_transcript_by_id(transcript_id)

    if editor:
        cmd = [editor, str(filepath)]
    else:
        cmd = [config.default_editor, str(filepath)]

    subprocess.run(cmd)
```

**Test Requirements:**
- Test with different editors
- Test default editor
- Test editor not found

---

### [C-006] Delete Command
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [R-005]

**User Story:**
As a user, I want to delete unwanted transcripts so that I can keep my collection clean.

**Acceptance Criteria:**
- [ ] `rec delete <id>` removes transcript
- [ ] Confirmation prompt before deletion
- [ ] `rec delete <id> --force` skips confirmation
- [ ] Also delete associated audio files (if any)
- [ ] Show what will be deleted

**Technical Notes:**
```python
@app.command()
def delete_transcript(transcript_id: str, force: bool = False):
    filepath = get_transcript_by_id(transcript_id)
    audio_files = get_associated_audio(transcript_id)

    # Show what will be deleted
    console.print(f"Will delete:\n  {filepath.name}")
    if audio_files:
        console.print(f"  {len(audio_files)} audio file(s)")

    # Confirm
    if not force:
        if not Confirm.ask("Are you sure?"):
            return

    # Delete
    filepath.unlink()
    for audio_file in audio_files:
        audio_file.unlink()
```

**Test Requirements:**
- Test deletion with confirmation
- Test force deletion
- Test deletion of audio files
- Test cancelled deletion

---

### [C-007] Search Transcripts
**Priority:** Low
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [C-001]

**User Story:**
As a user, I want to search transcript content so that I can find specific information across all recordings.

**Acceptance Criteria:**
- [ ] `rec search "keyword"` finds matches
- [ ] Search in transcript body and frontmatter
- [ ] Show context around matches
- [ ] Highlight matched text
- [ ] Show which transcript contains matches

**Technical Notes:**
```python
@app.command()
def search(query: str):
    results = []
    for transcript in get_all_transcripts():
        content = transcript.read_text()
        if query.lower() in content.lower():
            # Find context
            context = extract_context(content, query)
            results.append((transcript, context))

    display_search_results(results, query)
```

**Test Requirements:**
- Test case-insensitive search
- Test context extraction
- Test with multiple matches
- Test with no matches

---

### [C-008] Fuzzy ID/Filename Matching
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-005]

**User Story:**
As a user, I want typo tolerance so that small mistakes don't prevent me from finding transcripts.

**Acceptance Criteria:**
- [ ] `rec view meetnig` suggests "meeting_notes.md"
- [ ] `rec analyze brain` matches "brainstorm.md"
- [ ] Partial matches work
- [ ] Show suggestions if no exact match

**Technical Notes:**
```python
from difflib import get_close_matches

def find_transcript_fuzzy(user_input: str):
    all_files = get_all_transcripts()
    filenames = [f.stem for f in all_files]

    # Try exact match first
    if user_input in filenames:
        return get_transcript_by_name(user_input)

    # Try fuzzy match
    matches = get_close_matches(user_input, filenames, n=3, cutoff=0.6)

    if matches:
        console.print(f"Did you mean: {matches[0]}?")
        if Confirm.ask("Use this?"):
            return get_transcript_by_name(matches[0])
```

**Test Requirements:**
- Test typo correction
- Test partial matches
- Test suggestion UI
- Test no matches

---

### [C-009] Copy to Clipboard
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [C-003]

**User Story:**
As a user, I want to copy transcripts to clipboard so that I can paste them elsewhere easily.

**Acceptance Criteria:**
- [ ] Auto-copy after recording (configurable)
- [ ] `rec copy <id>` manually copies
- [ ] Cross-platform support (macOS, Linux, Windows)
- [ ] Success confirmation

**Technical Notes:**
```python
import pyperclip

@app.command()
def copy_transcript(transcript_id: str):
    filepath = get_transcript_by_id(transcript_id)
    content = read_transcript_body(filepath)  # Without frontmatter

    pyperclip.copy(content)
    console.print("✅ Copied to clipboard!")
```

**Test Requirements:**
- Test clipboard copy
- Test auto-copy after recording
- Test on different platforms
- Test with large content

---

### [C-010] Export Transcript
**Priority:** Low
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [C-003]

**User Story:**
As a user, I want to export transcripts in different formats so that I can use them in other applications.

**Acceptance Criteria:**
- [ ] `rec export <id> --format pdf`
- [ ] `rec export <id> --format docx`
- [ ] `rec export <id> --format txt` (plain text)
- [ ] Preserve formatting where possible

**Technical Notes:**
```python
from docx import Document
import markdown2

@app.command()
def export(transcript_id: str, format: str = 'pdf'):
    content = get_transcript_content(transcript_id)

    if format == 'pdf':
        export_to_pdf(content)
    elif format == 'docx':
        export_to_docx(content)
    elif format == 'txt':
        export_to_txt(content)
```

**Test Requirements:**
- Test each export format
- Test formatting preservation
- Test with various content types

---

## Phase 7: Configuration & Settings (Week 7)

### [S-001] Interactive Settings Menu
**Priority:** High
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [F-004]

**User Story:**
As a user, I want a friendly settings interface so that I don't have to manually edit config files.

**Acceptance Criteria:**
- [ ] `rec settings` opens interactive menu
- [ ] Navigate with arrow keys
- [ ] Change settings in-place
- [ ] Show current values
- [ ] Validate inputs
- [ ] Save changes to config.yaml

**Technical Notes:**
```python
from rich.prompt import Prompt, Confirm

@app.command()
def settings():
    while True:
        choice = show_settings_menu()

        if choice == 'transcription':
            transcription_settings()
        elif choice == 'output':
            output_settings()
        # ... etc
```

**Test Requirements:**
- Test menu navigation
- Test setting updates
- Test input validation
- Test config file updates

---

### [S-002] Microphone Configuration
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [R-001, S-001]

**User Story:**
As a user, I want to select my microphone so that Rejoice uses the right input device.

**Acceptance Criteria:**
- [ ] List available microphones
- [ ] Show current selection
- [ ] Test microphone with live audio level meter
- [ ] Save selection to config

**Technical Notes:**
```python
def microphone_settings():
    devices = get_audio_devices()

    # Show list
    for i, device in enumerate(devices):
        console.print(f"{i}. {device['name']}")

    # Get selection
    choice = Prompt.ask("Select microphone", default="0")

    # Test microphone
    if Confirm.ask("Test this microphone?"):
        test_microphone(devices[int(choice)])

    # Save
    config.update({'audio': {'device': int(choice)}})
```

**Test Requirements:**
- Test device listing
- Test device selection
- Test microphone test
- Test config save

---

### [S-003] Model Configuration
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [S-001, T-001]

**User Story:**
As a user, I want to choose transcription model size so that I can balance speed vs accuracy.

**Acceptance Criteria:**
- [ ] List available models (tiny, base, small, medium, large)
- [ ] Show model size and expected performance
- [ ] Download model if not cached
- [ ] Test transcription with selected model

**Technical Notes:**
```python
MODELS = {
    'tiny': {'size': '75MB', 'speed': 'Very Fast', 'accuracy': 'Good'},
    'base': {'size': '142MB', 'speed': 'Fast', 'accuracy': 'Better'},
    'small': {'size': '466MB', 'speed': 'Medium', 'accuracy': 'Great'},
    'medium': {'size': '1.5GB', 'speed': 'Slow', 'accuracy': 'Excellent'},
    'large': {'size': '2.9GB', 'speed': 'Very Slow', 'accuracy': 'Best'},
}
```

**Test Requirements:**
- Test model selection
- Test model download
- Test with different models
- Test config save

---

### [S-004] Save Location Configuration
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [S-001]

**User Story:**
As a user, I want to choose where transcripts are saved so that they integrate with my note-taking system.

**Acceptance Criteria:**
- [ ] Set custom save path
- [ ] Validate path exists
- [ ] Create directory if doesn't exist
- [ ] Expand `~` for home directory
- [ ] Show current location

**Technical Notes:**
```python
def output_settings():
    current = config.output.save_path
    console.print(f"Current: {current}")

    new_path = Prompt.ask("New save location", default=str(current))
    path = Path(new_path).expanduser()

    if not path.exists():
        if Confirm.ask(f"Create {path}?"):
            path.mkdir(parents=True)

    config.update({'output': {'save_path': str(path)}})
```

**Test Requirements:**
- Test path validation
- Test directory creation
- Test home expansion
- Test config save

---

### [S-005] Template Customization
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [S-001]

**User Story:**
As a user, I want to customize the markdown template so that frontmatter matches my note system.

**Acceptance Criteria:**
- [ ] Edit template in default editor
- [ ] Template variables documented
- [ ] Validate template syntax
- [ ] Preview template output
- [ ] Reset to default option

**Technical Notes:**
```yaml
# Template variables:
# ${date} - Current date
# ${time} - Current time
# ${id} - Transcript ID
# ${ai_title} - AI-generated title
# ${ai_summary} - AI summary
# ${ai_tags} - AI tags
# ${language} - Detected language
# ${duration} - Recording duration
```

**Test Requirements:**
- Test template editing
- Test variable substitution
- Test template validation
- Test reset to default

---

### [S-006] Default Behaviors Configuration
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [S-001]

**User Story:**
As a user, I want to set defaults so that I don't have to specify flags every time.

**Acceptance Criteria:**
- [ ] Default: auto-analyze after recording
- [ ] Default: auto-copy to clipboard
- [ ] Default: speaker diarization on/off
- [ ] Default: timestamps on/off
- [ ] Default: language
- [ ] All overridable with flags

**Technical Notes:**
```yaml
features:
  auto_analyze: true
  auto_copy: true
  speaker_diarization: false
  timestamps: false

transcription:
  default_language: auto
```

**Test Requirements:**
- Test each default setting
- Test flag overrides
- Test config save

---

### [S-007] Ollama Configuration
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [S-001, AI-001]

**User Story:**
As a user, I want to configure Ollama settings so that AI features work with my setup.

**Acceptance Criteria:**
- [ ] Set Ollama URL (default: localhost:11434)
- [ ] Set default model (llama2, mistral, etc.)
- [ ] Test connection
- [ ] List available models

**Technical Notes:**
```python
def ollama_settings():
    current_url = config.ai.ollama_url
    current_model = config.ai.model

    # Test connection
    if test_ollama_connection(current_url):
        console.print("✅ Connected to Ollama")

        # Show available models
        models = list_ollama_models(current_url)
        console.print(f"Available models: {', '.join(models)}")
```

**Test Requirements:**
- Test URL configuration
- Test connection testing
- Test model listing
- Test config save

---

### [S-008] Doctor/Health Check Command
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [F-006]

**User Story:**
As a user, I want to diagnose issues so that I can fix problems myself.

**Acceptance Criteria:**
- [ ] `rec doctor` checks system health
- [ ] Check: Python version
- [ ] Check: Dependencies installed
- [ ] Check: Microphone access
- [ ] Check: Ollama running
- [ ] Check: Disk space
- [ ] Check: Config file valid
- [ ] Suggest fixes for problems

**Technical Notes:**
```python
@app.command()
def doctor():
    checks = []

    # Python version
    if sys.version_info >= (3, 8):
        checks.append(("✅", "Python version", f"{sys.version}"))
    else:
        checks.append(("❌", "Python version", "Requires >= 3.8"))

    # Dependencies
    try:
        import faster_whisper
        checks.append(("✅", "faster-whisper", "Installed"))
    except ImportError:
        checks.append(("❌", "faster-whisper", "Not installed"))

    # ... more checks

    display_health_report(checks)
```

**Test Requirements:**
- Test all checks
- Test with problems present
- Test fix suggestions
- Test on different systems

---

### [S-009] Version & Update Check
**Priority:** Low
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [F-005]

**User Story:**
As a user, I want to know if updates are available so that I can stay current.

**Acceptance Criteria:**
- [ ] `rec --version` shows current version
- [ ] `rec update check` checks for updates
- [ ] Compare with GitHub releases
- [ ] Show changelog if update available
- [ ] Optional: auto-check on startup (weekly)

**Technical Notes:**
```python
import requests

def check_updates():
    current = __version__
    response = requests.get(
        "https://api.github.com/repos/user/rejoice-v2/releases/latest"
    )
    latest = response.json()['tag_name']

    if latest > current:
        console.print(f"Update available: {current} -> {latest}")
```

**Test Requirements:**
- Test version display
- Test update check
- Test with no internet
- Test changelog display

---

### [S-010] Debug Mode
**Priority:** High
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** [F-006]

**User Story:**
As a user, I want verbose output when troubleshooting so that I can understand what's happening.

**Acceptance Criteria:**
- [ ] `rec --debug <command>` enables debug mode
- [ ] Show all logging output
- [ ] Show API calls/responses
- [ ] Show file operations
- [ ] Show timing information
- [ ] Don't clear terminal output

**Technical Notes:**
```python
import logging

if debug:
    logging.getLogger().setLevel(logging.DEBUG)
    console.print("[yellow]Debug mode enabled[/yellow]")
```

**Test Requirements:**
- Test debug output
- Test with each command
- Test logging levels
- Test timing information

---



### [I-001] Virtual Environment Setup
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** [F-002]

**User Story:**
As a user, I want Rejoice installed in an isolated virtual environment so that it doesn't conflict with my system Python packages.

**Acceptance Criteria:**
- [ ] Create venv at `~/.rejoice/venv`
- [ ] Use system Python 3.8+
- [ ] Install all dependencies in venv
- [ ] Venv is completely isolated
- [ ] No system Python pollution
- [ ] Easy to delete (just remove `~/.rejoice/`)

**Technical Notes:**
```bash
# Create isolated environment
python3 -m venv ~/.rejoice/venv

# Activate and install
source ~/.rejoice/venv/bin/activate
pip install --upgrade pip
pip install rejoice

# Venv structure:
~/.rejoice/
├── venv/
│   ├── bin/
│   │   ├── python
│   │   ├── pip
│   │   └── rec          # Entry point
│   ├── lib/
│   └── pyvenv.cfg
└── config/
    └── config.yaml
```

**Test Requirements:**
- Test venv creation
- Test package installation in venv
- Test isolation (no system packages accessible)
- Test with different Python versions (3.8, 3.9, 3.10, 3.11)
- Test on macOS and Linux

---

### [I-002] Shell Alias Creation
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ✅ Done
**Dependencies:** [I-001]

**User Story:**
As a user, I want to type `rec` from anywhere so that I don't need to remember the full path to the venv.

**Acceptance Criteria:**
- [ ] Detect user's shell (bash, zsh, fish)
- [ ] Add alias to appropriate rc file
- [ ] Alias: `alias rec="~/.rejoice/venv/bin/rec"`
- [ ] Alias works immediately (source rc file)
- [ ] Handle multiple shell configurations
- [ ] Don't duplicate aliases on reinstall

**Technical Notes:**
```bash
# Detect shell
SHELL_NAME=$(basename "$SHELL")

# Add alias based on shell
case "$SHELL_NAME" in
    bash)
        RC_FILE="$HOME/.bashrc"
        ;;
    zsh)
        RC_FILE="$HOME/.zshrc"
        ;;
    fish)
        RC_FILE="$HOME/.config/fish/config.fish"
        ALIAS_CMD="alias rec='~/.rejoice/venv/bin/rec'"
        ;;
esac

# Check if alias already exists
if ! grep -q "alias rec=" "$RC_FILE" 2>/dev/null; then
    echo "" >> "$RC_FILE"
    echo "# Rejoice voice transcription" >> "$RC_FILE"
    echo "alias rec='~/.rejoice/venv/bin/rec'" >> "$RC_FILE"
    echo "✅ Added 'rec' alias to $RC_FILE"
fi

# Source immediately for current session
source "$RC_FILE" 2>/dev/null || echo "Please run: source $RC_FILE"
```

**Shell-Specific Considerations:**
- **Bash:** Use `~/.bashrc` (or `~/.bash_profile` on macOS)
- **Zsh:** Use `~/.zshrc` (default on modern macOS)
- **Fish:** Use `~/.config/fish/config.fish`, different syntax
- **Tcsh/Csh:** Use `~/.cshrc`, different alias syntax

**Test Requirements:**
- Test on bash
- Test on zsh (macOS default)
- Test on fish
- Test alias immediately available after install
- Test `rec` works from any directory
- Test reinstall doesn't duplicate aliases
- Test manual activation: `source ~/.bashrc`

---

### [I-003] Alias Activation & Path Resolution
**Priority:** Critical
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [I-002]

**User Story:**
As a user, I want the `rec` command to automatically activate the virtual environment so that I don't have to think about it.

**Acceptance Criteria:**
- [ ] Alias directly calls venv Python
- [ ] No manual activation needed
- [ ] Works from any directory
- [ ] Expands `~` correctly in alias
- [ ] Handles spaces in paths

**Technical Notes:**
```bash
# Option 1: Direct venv call (recommended)
alias rec="~/.rejoice/venv/bin/rec"

# Option 2: Wrapper script (if needed)
# ~/.rejoice/rec-wrapper.sh
#!/bin/bash
source ~/.rejoice/venv/bin/activate
rec "$@"
deactivate

# Then alias:
alias rec="~/.rejoice/rec-wrapper.sh"
```

**Why Direct Call is Better:**
- No activation/deactivation overhead
- Faster (instant startup)
- Simpler (fewer moving parts)
- Cleaner (no shell state changes)

**Test Requirements:**
- Test `rec` from home directory
- Test `rec` from any other directory
- Test with paths containing spaces
- Test `rec` passes arguments correctly
- Test no activation messages appear

---

### [I-004] Installation Script (Full Integration)
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ✅ Done
**Dependencies:** [I-001, I-002, I-003]

**User Story:**
As a user, I want one-command installation so that setup is effortless.

**Acceptance Criteria:**
- [ ] `curl -sSL https://install.rejoice.ai | bash` works
- [ ] Installs system dependencies (portaudio, ffmpeg)
- [ ] Creates virtual environment
- [ ] Installs Python package in venv
- [ ] Sets up shell alias
- [ ] Creates config directory
- [ ] Downloads default Whisper model
- [ ] Runs first-time setup
- [ ] Tests installation
- [ ] Works on macOS and Linux

**Technical Notes:**
```bash
#!/bin/bash
# install.sh - Complete installation script

set -e  # Exit on error

echo "🎙️  Installing Rejoice..."

# 1. Detect OS
OS="$(uname -s)"
case "$OS" in
    Darwin)
        echo "📦 Installing system dependencies (macOS)..."
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew required. Install from https://brew.sh"
            exit 1
        fi
        brew install portaudio ffmpeg
        ;;
    Linux)
        echo "📦 Installing system dependencies (Linux)..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y portaudio19-dev ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y portaudio-devel ffmpeg
        else
            echo "❌ Unsupported package manager"
            exit 1
        fi
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

# 2. Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# 3. Create directory structure
echo "📁 Creating directory structure..."
mkdir -p ~/.rejoice
mkdir -p ~/.rejoice/config
mkdir -p ~/.rejoice/logs

# 4. Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv ~/.rejoice/venv

# 5. Install package
echo "📦 Installing Rejoice..."
~/.rejoice/venv/bin/pip install --upgrade pip
~/.rejoice/venv/bin/pip install rejoice

# 6. Set up shell alias
echo "⚙️  Setting up shell alias..."
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    bash)
        RC_FILE="$HOME/.bashrc"
        [[ "$OS" == "Darwin" ]] && RC_FILE="$HOME/.bash_profile"
        ;;
    zsh)
        RC_FILE="$HOME/.zshrc"
        ;;
    fish)
        RC_FILE="$HOME/.config/fish/config.fish"
        ;;
    *)
        RC_FILE="$HOME/.bashrc"
        ;;
esac

# Add alias if not exists
if ! grep -q "alias rec=" "$RC_FILE" 2>/dev/null; then
    echo "" >> "$RC_FILE"
    echo "# Rejoice - Voice Transcription" >> "$RC_FILE"
    echo "alias rec=\"\$HOME/.rejoice/venv/bin/rec\"" >> "$RC_FILE"
    echo "✅ Added 'rec' command to $RC_FILE"
else
    echo "✅ 'rec' command already configured"
fi

# 7. Test installation
echo "🧪 Testing installation..."
if ~/.rejoice/venv/bin/rec --version &> /dev/null; then
    echo "✅ Installation successful!"
else
    echo "❌ Installation test failed"
    exit 1
fi

# 8. Instructions
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Rejoice installed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 To activate in current shell:"
echo "   source $RC_FILE"
echo ""
echo "🎙️  To start recording:"
echo "   rec"
echo ""
echo "💡 First time? Run setup:"
echo "   rec settings"
echo ""
echo "📚 For help:"
echo "   rec --help"
echo ""
```

**Test Requirements:**
- Test on fresh macOS (Intel & Apple Silicon)
- Test on fresh Linux (Ubuntu 20.04, 22.04, Debian)
- Test with bash
- Test with zsh
- Test with existing Python installations
- Test system dependency installation
- Test venv creation
- Test alias creation
- Test with `rec` immediately after install
- Test with new shell session after install

---

### [I-005] Uninstallation Script
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [I-004]

---

### [I-006] Uninstallation Script
**Priority:** Medium
**Estimate:** S (2-4h)
**Status:** ✅ Done
**Dependencies:** [I-004]

**User Story:**
As a user, I want clean uninstallation so that Rejoice doesn't leave system pollution.

**Acceptance Criteria:**
- [ ] `rec uninstall` removes everything
- [ ] Remove virtual environment
- [ ] Remove config directory (with confirmation)
- [ ] Remove command aliases
- [ ] Optionally keep transcripts
- [ ] Confirmation prompts

**Technical Notes:**
```bash
#!/bin/bash
# Included in package

echo "This will remove Rejoice from your system."
echo "Your transcripts will NOT be deleted."
read -p "Continue? (y/n) " -n 1 -r

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

### [I-007] First-Run Setup
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [I-004, S-002]

**User Story:**
As a new user, I want guided setup so that Rejoice is configured correctly on first use.

**Acceptance Criteria:**
- [ ] Detect first run (no config file)
- [ ] Welcome message
- [ ] Test microphone
- [ ] Choose save location
- [ ] Download default Whisper model
- [ ] Test Ollama (optional)
- [ ] Create sample transcript

**Technical Notes:**
```python
def first_run_setup():
    console.print(Panel("👋 Welcome to Rejoice!"))

    # 1. Microphone
    console.print("\n1️⃣ Let's test your microphone...")
    test_microphone()

    # 2. Save location
    console.print("\n2️⃣ Where should transcripts be saved?")
    save_path = setup_save_location()

    # 3. Model
    console.print("\n3️⃣ Downloading transcription model...")
    download_model('base')

    # 4. Done
    console.print("\n✅ Setup complete! Type 'rec' to start.")
```

**Test Requirements:**
- Test full setup flow
- Test partial setup (user cancels)
- Test setup skip option
- Test on fresh install

---

### [I-008] Documentation Generation
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** None

**User Story:**
As a user/developer, I want comprehensive documentation so that I can learn and contribute effectively.

**Acceptance Criteria:**
- [ ] README.md complete with examples
- [ ] INSTALLATION.md detailed guide
- [ ] USAGE.md command reference
- [ ] CONFIGURATION.md settings guide
- [ ] ARCHITECTURE.md system design
- [ ] CONTRIBUTING.md dev guide
- [ ] Generated API docs (Sphinx)

**Test Requirements:**
- Review documentation completeness
- Test all examples work
- Verify code samples are correct

---

### [I-009] CI/CD Pipeline
**Priority:** High
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [F-003]

**User Story:**
As a developer, I want automated testing so that code quality is maintained.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow configured
- [ ] Run tests on push
- [ ] Run tests on PR
- [ ] Test multiple Python versions (3.8-3.11)
- [ ] Test on multiple OS (Ubuntu, macOS)
- [ ] Coverage reporting
- [ ] Automated releases

**Technical Notes:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov
```

**Test Requirements:**
- Test CI runs successfully
- Test on all matrix combinations
- Test coverage reporting

---

## Phase 8: Polish & Release

### [P-001] Performance Optimization
**Priority:** Medium
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** [T-001, AI-001]

**User Story:**
As a user, I want fast startup and transcription so that Rejoice feels responsive.

**Acceptance Criteria:**
- [ ] Cold start < 5 seconds
- [ ] Warm start < 1 second
- [ ] Model preloading (optional)
- [ ] Optimize imports
- [ ] Lazy loading where possible

**Technical Notes:**
```python
# Lazy imports
def record():
    # Import heavy dependencies only when needed
    from .transcription import Transcriber
    transcriber = Transcriber()
```

**Test Requirements:**
- Benchmark startup time
- Profile code for bottlenecks
- Test with/without model preload

---

### [P-002] Error Handling Improvements
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** All core features

**User Story:**
As a user, I want helpful error messages so that I can fix problems easily.

**Acceptance Criteria:**
- [ ] All errors caught gracefully
- [ ] Clear, friendly error messages
- [ ] Suggestions for fixes
- [ ] No stack traces in normal mode
- [ ] Stack traces in debug mode
- [ ] Exit codes defined

**Technical Notes:**
```python
class RejoiceError(Exception):
    """Base exception"""
    def __init__(self, message, suggestion=None):
        self.message = message
        self.suggestion = suggestion

try:
    # ... operation
except FileNotFoundError:
    raise RejoiceError(
        "Recording not found",
        suggestion="Try 'rec list' to see available recordings"
    )
```

**Test Requirements:**
- Test all error paths
- Test error message quality
- Test debug vs normal mode
- Test exit codes

---

### [P-003] Progress Indicators
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [T-001, AI-001]

**User Story:**
As a user, I want to see progress so that I know operations haven't frozen.

**Acceptance Criteria:**
- [ ] Spinners for short operations
- [ ] Progress bars for long operations
- [ ] ETA for transcription
- [ ] Live updates don't flicker
- [ ] Clean, minimal design

**Technical Notes:**
```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Transcribing...", total=100)
    for chunk in transcribe():
        progress.update(task, advance=1)
```

**Test Requirements:**
- Test all progress indicators
- Test with various durations
- Test cancellation during progress

---

### [P-004] Success Messaging
**Priority:** Low
**Estimate:** S (2-4h)
**Status:** ❌ Not Started
**Dependencies:** All commands

**User Story:**
As a user, I want confirmation of success so that I know operations completed.

**Acceptance Criteria:**
- [ ] Success messages for all commands
- [ ] Show file location after recording
- [ ] Show next steps
- [ ] Consistent messaging style
- [ ] Optional: celebrations for milestones

**Technical Notes:**
```python
def show_success(filepath, transcript_id):
    console.print("\n✅ Transcription saved!\n")
    console.print(f"📄 File: {filepath.name}")
    console.print(f"🆔 ID: {transcript_id}")
    console.print("\n💡 What's next?")
    console.print(f"   • View it:    rec view {transcript_id}")
    console.print(f"   • Analyze it: rec analyze {transcript_id}")
```

**Test Requirements:**
- Test all success messages
- Test message consistency
- Test milestone celebrations

---

### [P-005] Tab Completion
**Priority:** Low
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [F-005]

**User Story:**
As a user, I want tab completion so that commands are faster to type.

**Acceptance Criteria:**
- [ ] Bash completion script
- [ ] Zsh completion script
- [ ] Complete commands: `rec <TAB>`
- [ ] Complete IDs: `rec view <TAB>`
- [ ] Complete file paths

**Technical Notes:**
```bash
# bash completion
_rec_completions()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(compgen -W "record list view analyze delete" -- $cur) )
}
complete -F _rec_completions rec
```

**Test Requirements:**
- Test bash completion
- Test zsh completion
- Test command completion
- Test ID completion

---

### [P-006] User Acceptance Testing
**Priority:** Critical
**Estimate:** XL (1 week)
**Status:** ❌ Not Started
**Dependencies:** All features complete

**User Story:**
As the project team, we want real users to test Rejoice so that we catch issues before release.

**Acceptance Criteria:**
- [ ] 10+ beta testers recruited
- [ ] Testing guide provided
- [ ] Feedback collected
- [ ] Critical bugs fixed
- [ ] UX issues addressed
- [ ] Documentation updated based on feedback

**Test Requirements:**
- Create testing guide
- Set up feedback collection
- Track and prioritize issues
- Verify fixes

---

### [P-007] Performance Benchmarking
**Priority:** Medium
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** All core features

**User Story:**
As a developer, I want performance metrics so that we can track improvements over time.

**Acceptance Criteria:**
- [ ] Benchmark suite created
- [ ] Startup time measured
- [ ] Transcription speed measured
- [ ] Memory usage tracked
- [ ] Baseline established
- [ ] Regression detection

**Technical Notes:**
```python
# tests/performance/benchmarks.py

def test_startup_time():
    start = time.time()
    subprocess.run(['rec', '--version'])
    duration = time.time() - start
    assert duration < 5.0  # Must start in < 5s

def test_transcription_speed():
    # 60s audio should transcribe in < 60s (faster than realtime)
    start = time.time()
    transcribe('tests/fixtures/audio/speech_60s.wav')
    duration = time.time() - start
    assert duration < 60.0
```

**Test Requirements:**
- Run benchmarks on reference hardware
- Track results over time
- Set up performance CI

---

### [P-008] Security Review
**Priority:** High
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** All features complete

**User Story:**
As a user, I want to trust that Rejoice is secure so that my data is safe.

**Acceptance Criteria:**
- [ ] Code review for security issues
- [ ] No hard-coded credentials
- [ ] Secure file permissions
- [ ] Input validation everywhere
- [ ] Dependency security audit
- [ ] Privacy policy clear

**Technical Notes:**
- Use `bandit` for Python security linting
- Use `safety` for dependency vulnerabilities
- Review file operations for path traversal
- Validate all user inputs

**Test Requirements:**
- Run security scanners
- Fix all high/critical issues
- Document security practices

---

### [P-009] Release Preparation
**Priority:** Critical
**Estimate:** L (1-2d)
**Status:** ❌ Not Started
**Dependencies:** All features complete

**User Story:**
As the project team, we want a smooth release so that users can start using Rejoice.

**Acceptance Criteria:**
- [ ] Version number finalized (2.0.0)
- [ ] CHANGELOG.md complete
- [ ] All documentation reviewed
- [ ] README polished
- [ ] Release notes written
- [ ] GitHub release created
- [ ] PyPI package published

**Technical Notes:**
```bash
# Release checklist
- [ ] All tests passing
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Git tag created
- [ ] GitHub release published
- [ ] PyPI package uploaded
- [ ] Announcement written
```

**Test Requirements:**
- Test installation from PyPI
- Test on fresh systems
- Verify all docs links work

---

### [P-010] Launch & Announcement
**Priority:** Critical
**Estimate:** M (4-8h)
**Status:** ❌ Not Started
**Dependencies:** [P-009]

**User Story:**
As the project team, we want to announce Rejoice so that users can discover it.

**Acceptance Criteria:**
- [ ] GitHub README looks great
- [ ] Demo video/gif created
- [ ] Launch tweet written
- [ ] HN post prepared
- [ ] Reddit post prepared
- [ ] Product Hunt submission

**Test Requirements:**
- Review all launch materials
- Test demo scenarios
- Verify links work

---

## 📈 Story Statistics

### By Priority
- **Critical:** 28 stories
- **High:** 23 stories
- **Medium:** 28 stories
- **Low:** 10 stories

### By Estimate
- **XS (<2h):** 0 stories
- **S (2-4h):** 28 stories
- **M (4-8h):** 39 stories
- **L (1-2d):** 16 stories
- **XL (2-5d):** 6 stories

### By Phase
- **Phase 1 (Foundation):** 6 stories
- **Phase 2 (Recording):** 10 stories
- **Phase 3 (Transcription):** 8 stories
- **Phase 4 (Advanced):** 5 stories
- **Phase 5 (AI):** 10 stories
- **Phase 6 (Commands):** 10 stories
- **Phase 7 (Settings):** 10 stories
- **Phase 8 (Installation):** 9 stories
- **Phase 9 (Polish):** 10 stories

---

## 🎯 Next Steps

1. **Review this backlog** - Adjust priorities and estimates
2. **Set up project tracking** - GitHub Projects, Linear, or Jira
3. **Start with Phase 1** - Foundation stories
4. **Follow TDD approach** - Write tests first
5. **Regular reviews** - Update backlog weekly

---

**Ready to build! 🚀**
