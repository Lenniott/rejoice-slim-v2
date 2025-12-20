# Changelog

All notable changes to Rejoice Slim v2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- [I-007] First-Run Setup
  - Implemented guided setup wizard for new users in `src/rejoice/setup.py`
  - Detects first run by checking for config file existence
  - Interactive model selection with descriptions (tiny, base, small, medium, large)
  - Automatic Whisper model download if not already available locally
  - Microphone testing with audio level detection
  - Save location configuration with directory creation
  - Optional Ollama connection testing
  - Sample transcript creation to demonstrate format
  - Integrated into CLI - automatically prompts on first run (can be skipped with `--skip-setup`)
  - All setup steps are optional and can be cancelled
  - Configuration is saved to `~/.config/rejoice/config.yaml` after setup
  - Tests: 14 new unit tests, all passing (79% coverage for setup module)

- [R-012] Simplified Recording with Visual Feedback
  - Implemented Rich Live display showing recording status, elapsed time (MM:SS), and audio level meter (visual bars) during recording.
  - Removed real-time transcription complexity - recording now uses a simple record-then-transcribe flow.
  - After recording stops, a single transcription pass runs with progress bar using faster-whisper.
  - Final transcript is written atomically using `append_to_transcript`.
  - Temporary WAV file is cleaned up after transcription completes.
  - Updated existing tests to reflect the simplified flow (removed RealtimeTranscriptionWorker dependencies).
  - Visual feedback provides clear indication that the system is working without the complexity of real-time transcription.

### Added

- [R-005] ID Normalization System
  - Introduced a `normalize_id` helper in `transcript/manager.py` to convert flexible numeric input like `"1"`, `"01"` or `"000001"` into the canonical zero-padded 6-digit transcript ID.
  - Added unit tests covering valid formats, non-numeric inputs, and out-of-range values (zero, negative and too-large IDs), keeping transcript ID handling predictable and safe for future CLI commands.

- [C-003] View Transcript Command
  - Added a `rec view` CLI subcommand (and underlying `view_transcript` helper) to display individual transcripts or the latest recording directly in the terminal with Rich-powered Markdown rendering.
  - Supports flexible numeric IDs via the shared `normalize_id` helper, optional display of YAML frontmatter metadata, and clear error messages when IDs are invalid or transcripts are missing.
  - Introduced unit tests exercising viewing by ID, viewing the latest transcript, metadata visibility toggling, and error handling paths.

- [R-008] Recording Control - Cancel
  - Extended `start_recording_session` in `cli/commands.py` to treat `Ctrl+C` as an explicit cancel flow with confirmation.
  - Implemented optional transcript deletion or safe cancellation by marking frontmatter status as `cancelled`, always cleaning up the audio stream.
  - Added CLI unit coverage for the cancel path to ensure status updates behave as expected.

- [T-009] Connect Recording to Transcription
  - Integrated automatic transcription into the recording workflow in `start_recording_session`.
  - Audio captured during recording is saved to a temporary WAV file and automatically transcribed after recording stops.
  - Transcription runs automatically and appends text to the transcript file using the `Transcriber.stream_file_to_transcript` method.
  - Temporary audio files are cleaned up after transcription completes, even on errors.
  - Transcription errors are handled gracefully without crashing the CLI.
  - Cancelled recordings skip transcription entirely.
  - Language override from `--language` CLI flag is passed through to the Transcriber.
  - Added 6 comprehensive unit tests covering all acceptance criteria: audio saving, transcription execution, text appending, cleanup, error handling, cancellation skipping, and language flag passing.

- [T-010] Real-Time Incremental Transcription During Recording
  - Implemented `RealtimeTranscriptionWorker` class in `transcription/realtime.py` for incremental transcription during recording.
  - Audio chunks are processed incrementally (every 1 second by default) while recording is in progress.
  - Transcript file is updated in real-time as speech segments are transcribed and confirmed.
  - Uses faster-whisper with chunked processing (alternative to whisper-streaming to maintain "slim" philosophy and avoid new dependencies).
  - Thread-safe file writing ensures no corruption from concurrent transcription updates.
  - Final transcription pass after recording stops catches any remaining audio not processed during real-time transcription.
  - Transcription errors are handled gracefully without stopping recording.
  - VAD support is provided via faster-whisper's built-in VAD filter.
  - Integrated into `start_recording_session` to enable real-time transcription by default.
  - Added 6 unit tests covering incremental updates, thread safety, error handling, final pass, chunk size, and VAD integration.

### Changed

- [T-002] Language Detection & Control
  - Extended `Transcriber` so that `language='auto'` passes `None` through to faster-whisper, records the model-reported language, and exposes it via a `last_language` property.
  - Updated `stream_file_to_transcript` to persist the effective language into transcript YAML frontmatter via a new atomic `update_language` helper in the transcript manager.
  - Added a global `--language / -l` CLI flag to accept per-invocation language overrides (plumbed into Click context for future transcription commands) and expanded unit coverage around language handling.

- [C-001] List Recordings Command
  - Implemented `rec list` CLI subcommand to list transcript files from the configured output directory using the standard naming pattern.
  - Output displays ID, date and filename in a Rich table, sorted newest-first, with a simple limit parameter and a friendly message when no recordings exist.
  - Added two unit tests covering empty and populated transcript directories, with the full test suite passing at 93% coverage.

## [2.0.0] - 2025-12-17

### Added - Phase 0: Development Environment Setup

#### Project Structure
- Complete directory structure following Python best practices
  - `src/rejoice/` - Main source code
    - `cli/` - CLI commands module
    - `core/` - Core functionality (empty, ready for implementation)
    - `audio/` - Audio recording module (empty, ready for implementation)
    - `transcription/` - Transcription engine module (empty, ready for implementation)
    - `transcript/` - Transcript file management module (empty, ready for implementation)
    - `ai/` - AI enhancement module (empty, ready for implementation)
    - `utils/` - Utility functions module (empty, ready for implementation)
  - `tests/` - Test suite
    - `unit/` - Unit tests (12 tests passing)
    - `integration/` - Integration tests (now includes install/uninstall script tests)
    - `e2e/` - End-to-end tests (sample test in place)
    - `fixtures/` - Test data (empty, ready)
  - `docs/` - Documentation
  - `scripts/` - Installation and utility scripts
    - `install.sh` - One-command installation script for macOS and Linux ([I-001])
      - Detects OS (macOS/Linux) and installs system dependencies (portaudio, ffmpeg)
      - Creates isolated virtual environment at `~/.rejoice/venv`
      - Installs Rejoice package (from source or PyPI)
      - Sets up shell alias (`rec` command) for bash, zsh, and fish
      - Tests installation and provides next steps
      - Supports both development (from source) and production (from PyPI) installations
    - `uninstall.sh` - Clean uninstallation script for macOS and Linux ([I-003])
      - Confirms with user before uninstalling
      - Removes `~/.rejoice` virtual environment and config
      - Cleans `rec` alias from common shell rc files (bash, zsh, fish)
      - Preserves transcripts under `~/Documents/benjamayden/VoiceNotes`
  - `.github/workflows/` - CI/CD configuration

#### Dependencies Installed

**Core Dependencies:**
- `faster-whisper>=0.10.0` - Transcription engine (4x faster than openai-whisper)
- `sounddevice>=0.4.6` - Audio recording
- `ollama>=0.1.0` - Local AI enhancement
- `pyperclip>=1.8.2` - Clipboard support
- `pyyaml>=6.0` - Configuration file handling
- `rich>=13.0.0` - Terminal UI and formatting
- `atomicwrites>=1.4.0` - Atomic file operations
- `click>=8.0.0` - CLI framework

**Development Dependencies:**
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Linting
- `mypy>=1.0.0` - Type checking
- `pre-commit>=3.0.0` - Git hooks
- `types-PyYAML>=6.0.0` - Type stubs for PyYAML

#### Configuration Files
- `pyproject.toml` - Complete package configuration with:
  - Project metadata (name, version, description, authors, license)
  - Dependencies and dev dependencies
  - Pytest configuration (90% coverage requirement in CI)
  - Black, mypy, and coverage tool settings
  - Entry point: `rec = "rejoice.cli.commands:main"`
- `.pre-commit-config.yaml` - Pre-commit hooks for:
  - Trailing whitespace removal
  - End of file fixes
  - YAML/JSON/TOML validation
  - Large file checks
  - Merge conflict detection
  - Debug statement detection
  - Black formatting
  - Flake8 linting
  - MyPy type checking
- `.gitignore` - Comprehensive ignore patterns for Python, venv, test artifacts, and Rejoice-specific files
- `.env.example` - Environment variable template
- `LICENSE` - MIT License

#### Source Code Implemented
- `src/rejoice/__init__.py` - Package initialization with version (`__version__ = "2.0.0"`)
- `src/rejoice/__main__.py` - Module entry point for `python -m rejoice`
- `src/rejoice/cli/commands.py` - Basic CLI implementation:
  - `main()` function with `--version` and `--debug` flags
  - Uses Click framework
  - Uses Rich for terminal output
- `src/rejoice/exceptions.py` - Custom exception hierarchy:
  - `RejoiceError` - Base exception class
  - `AudioError` - Audio-related errors
  - `TranscriptionError` - Transcription-related errors
  - `ConfigError` - Configuration-related errors
  - `TranscriptError` - Transcript file-related errors
  - `AIError` - AI enhancement-related errors
- `src/rejoice/transcript/manager.py` - Transcript Manager implementation ([R-003], [R-004]):
  - `create_transcript` creates a new markdown transcript file with a unique, zero-padded 6-digit ID on record start
  - `get_next_id` scans the transcript directory to generate the next sequential ID across all dates
  - `generate_frontmatter` adds YAML frontmatter with id, created timestamp, status (`recording`), language, tags, and summary
  - `write_file_atomic` performs atomic file creation using a temp file and `os.replace` to guarantee whole-file writes
  - `append_to_transcript` atomically appends new content to existing transcript files while preserving frontmatter and existing body
- `tests/unit/test_transcript_manager.py` - Unit tests for transcript manager:
  - Tests ID generation, directory creation, filename pattern, frontmatter structure, duplicate ID handling, and atomic writes
  - Tests atomic append behavior, frontmatter preservation, and newline handling for appended transcript content

#### Testing Infrastructure
- `tests/conftest.py` - Pytest configuration with:
  - Python path setup for imports
  - Shared fixtures: `tmp_dir`, `sample_audio_dir`, `config_dir`
- `tests/unit/test_cli.py` - CLI tests (3 tests):
  - `test_cli_help()` - Tests `--help` flag
  - `test_cli_version()` - Tests `--version` flag
  - `test_cli_debug_flag()` - Tests `--debug` flag
- `tests/unit/test_exceptions.py` - Exception tests (7 tests):
  - Tests for all exception classes
  - Tests for error messages and suggestions
- `tests/unit/test_main.py` - Main module tests (2 tests):
- `tests/integration/test_install_script.py` - Installation script tests (4 tests):
  - `test_install_script_syntax()` - Validates bash syntax
  - `test_install_script_exists()` - Verifies script exists
  - `test_install_script_is_executable()` - Verifies executable permissions
  - `test_install_script_has_shebang()` - Verifies shebang line
- `tests/integration/test_uninstall_script.py` - Uninstall script tests (4 tests):
  - `test_uninstall_script_exists()` - Verifies script exists
  - `test_uninstall_script_has_shebang()` - Verifies shebang line
  - `test_uninstall_script_is_executable()` - Verifies executable permissions
  - `test_uninstall_script_syntax()` - Validates bash syntax
  - Tests module import
  - Tests main function existence

#### Developer Notes

1. **Running Tests:**
   - Unit tests: `pytest tests/unit/ -v`
   - Integration tests: `pytest tests/integration/ -v`
   - E2E tests: `pytest tests/e2e/ -v`
   - All tests with coverage: `pytest --cov=src/rejoice --cov-report=html`

2. **Coverage Expectations:**
   - Phase 0: ~50% coverage acceptable
   - Phase 1-3: Increase towards 90%+

3. **How to Use Scripts:**
   - Development install: `pip install -e ".[dev]"`
   - User install (planned): `curl -sSL https://install.rejoice.ai | bash`
   - Uninstall: `bash scripts/uninstall.sh` (and eventually `rec uninstall`)

4. **Environment Setup:**
   - Use Python 3.8–3.11 (3.9+ recommended)
   - Create venv: `python3 -m venv venv && source venv/bin/activate`
   - Install dev deps: `pip install -e ".[dev]"`

5. **Module Status:**
   - ✅ `cli/` - Basic CLI implemented
   - ✅ `exceptions.py` - Exception hierarchy complete
   - ⏳ `core/` - Empty, ready for config system
   - ⏳ `audio/` - Empty, ready for recording implementation
   - ⏳ `transcription/` - Empty, ready for faster-whisper integration
   - ⏳ `transcript/` - Empty, ready for file management
   - ⏳ `ai/` - Empty, ready for Ollama integration
   - ⏳ `utils/` - Empty, ready for utility functions

7. **Testing:**
   - Run tests: `pytest tests/unit/ -v`
   - Run with coverage: `pytest --cov=src/rejoice --cov-report=html`
   - All tests should pass before committing
   - Write tests first (TDD)

8. **Installation:**
   - Development: `pip install -e ".[dev]"`
   - User installation script: `scripts/install.sh` ([I-001] ✅ Complete)
   - Uninstall script: `scripts/uninstall.sh` ([I-003] ✅ Complete)

### Added - Phase 2: Core Recording System

- [R-001] Audio Device Detection
  - Implemented `get_audio_input_devices` helper in `rejoice.audio` to enumerate input-capable devices
  - Added `rec config list-mics` CLI command to list microphones with index and default marker
  - Tests: 3 new unit tests covering device filtering and CLI behavior (all passing)
- [R-002] Audio Capture Implementation
  - Implemented `record_audio` helper in `rejoice.audio` using `sounddevice.InputStream` (16kHz mono, device-selectable)
  - Added unit tests for correct stream parameters, missing dependency handling, and wrapped sounddevice errors
  - Forms the basis for streaming audio into the recording pipeline in later stories
- [T-001] faster-whisper Integration
  - Implemented `Transcriber` in `rejoice.transcription` wrapping the `faster-whisper` `WhisperModel`
  - Added configuration-driven model selection via `TranscriptionConfig` (tiny/base/small/medium/large)
  - Normalised transcription output to simple `{text, start, end}` dictionaries and enabled VAD by default
  - Introduced 5 unit tests covering model initialisation, VAD and language wiring (including `language='auto'`), missing dependency handling, and error wrapping for underlying model failures
- [T-003] Streaming Transcription to File
  - Extended `Transcriber` with `stream_file_to_transcript` to stream segments from an audio file directly into a markdown transcript
  - Each non-empty segment is appended atomically via `append_to_transcript`, ensuring partial results are always persisted
  - Added a unit test verifying that segments are yielded in order and only non-empty segments trigger append operations
- [R-006] Recording Control - Start
  - Implemented `start_recording_session` helper in `rejoice.cli.commands` to coordinate config loading, transcript creation, and audio capture
  - Wired default `rec` invocation (no subcommand) to start a recording session immediately, printing transcript path and a simple duration summary
  - Added CLI unit tests to verify that `rec` triggers a recording session and that transcript creation happens before audio capture, with clean stream shutdown
- [R-007] Recording Control - Stop
  - Extended `start_recording_session` to finalise recordings by updating transcript frontmatter status to `completed` and printing a clear success message with file location
  - Implemented `update_status` helper in `rejoice.transcript.manager` to atomically update YAML frontmatter while preserving body content
  - Added unit tests covering CLI stop behaviour, default keypress handling for Enter, and frontmatter status updates performed via atomic writes

### Known Issues / Limitations

- Coverage is at ~48% (expected for Phase 0, will increase as features are added)
- Most modules are empty (ready for implementation)

### Technical Decisions

1. **CLI Framework:** Click (simple, well-documented, works well with Rich)
2. **Terminal UI:** Rich (beautiful terminal output, progress bars, tables)
3. **Testing:** Pytest (industry standard, excellent fixtures and plugins)
4. **Code Formatting:** Black (uncompromising, consistent style)
5. **Type Checking:** MyPy (static type checking for better code quality)
6. **Coverage:** pytest-cov (integrated with pytest, HTML reports)

---

## Next Release Planning

### Phase 0 Remaining (High Priority)
- [I-001] Installation Script ✅ Complete
- [I-003] Uninstall Script ✅ Complete

### Phase 1: Foundation (Next)
- [F-004] Configuration System Design
- [F-005] CLI Framework Setup (enhance existing)
- [F-006] Logging System

### Phase 2: Core Recording (After Phase 1)
- Audio device detection
- Audio capture implementation
- Transcript file management
- Recording controls

---

**Last Updated:** 2025-12-17
**Version:** 2.0.0-dev (Development Phase 0)
**Status:** ✅ Development environment ready, install/uninstall tooling in place; ready for feature development
