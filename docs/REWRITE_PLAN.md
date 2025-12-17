# 🎙️ Rejoice v2 - Project Specification

**Status:** New Project - Planning Phase  
**Date:** December 17, 2025  
**Approach:** Greenfield rewrite (clean slate, no legacy code)

> **Note:** This is a complete rewrite starting from scratch. We're not migrating or refactoring existing code - we're building a new system based on lessons learned. The old `rejoice-slim` project taught us what works and what doesn't, and this specification describes the ideal system we want to build.

---

## 📋 Project Overview

**Rejoice v2** is a local-first voice transcription tool that prioritizes reliability, simplicity, and privacy. Record audio, get accurate transcripts with AI-powered summaries, all without sending data to the cloud.

**Key Philosophy:**
- Data integrity over features
- Simplicity over cleverness  
- Transparency over magic
- Privacy by design
- Test-driven development

**Why a rewrite?**
- Current system has accumulated complexity (custom chunking, dual transcription)
- openai-whisper fails on long recordings with silence
- Late file creation risks data loss
- Over-engineered solutions for simple problems
- Starting fresh allows us to implement best practices from day one

---

## 🎯 Core Requirements

### 1. **Zero Data Loss** ✅ CRITICAL
- Once recording starts, capture everything until stop
- Survive crashes, interruptions, system failures
- Incremental saving prevents loss of partial transcripts

### 2. **Concurrent Audio Access** 🎤
- Microphone works while Zoom, browser video, Spotify running
- No conflicts with other audio applications
- Cross-platform audio stability

### 3. **Configurable MD Template** 📝
- User-defined frontmatter properties
- Customizable metadata fields
- Template inheritance and defaults

### 4. **Transparent AI Prompts** 🤖
- Access and modify Ollama prompts
- Version-controlled prompt templates
- Easy to customize AI behavior

### 5. **AI Enhancement** ✨
- Ollama integration for summaries
- Automatic tagging
- Title generation

### 6. **Maximum Accuracy** 🎯
- Best local transcription quality
- Language-aware processing
- Speaker diarization support

### 7. **Language Control** 🌍
- Force specific language (prevent muffled English → Chinese)
- Auto-detection when desired
- Per-recording language override

### 8. **Flexible Input** 🔄
- Live recording from microphone
- Process existing audio files
- Batch processing support

### 9. **Simple Installation** 📦
- One-command install/uninstall
- Virtual environment isolation
- No system pollution

### 10. **Fast Startup** ⚡
- `rec` command instant start
- No loading delays
- Model preloading strategies

### 11. **Full Customization** ⚙️
- Save location configuration
- Command aliases
- All behaviors configurable

### 12. **Clean Terminal Output** 🧹
- Minimal default output
- Progress indicators only
- Debug mode available

### 13. **Transparency** 🔍
- Clear dependency explanations
- Debug mode for troubleshooting
- Settings visible and documented
- Easy configuration management

### 14. **Easy Control** 🎮
- Simple start: `rec`
- Simple stop: `Enter`
- Simple cancel: `Ctrl+C`

### 15. **Auto-Copy** 📋
- Copy to clipboard on completion
- Configurable behavior
- Silent operation

### 16. **Speaker Diarization** 👥 NEW
- Distinguish multiple speakers
- Default on/off configurable
- Flag: `-speakers` / `-no-speakers`

### 17. **Timestamps** ⏱️ NEW
- Segment timestamps in transcript
- Default on/off configurable
- Flag: `-timestamp` / `-no-timestamp`

---

## 🏗️ Architecture Design

### Technology Stack Changes

#### ❌ Remove
- `openai-whisper` → Too slow, fails on long silence
- Custom chunking system → Redundant with faster-whisper
- Dual transcription (quick + full) → Single pass sufficient
- Complex audio buffering → Simplified with streaming

#### ✅ Add
- `faster-whisper` → 4x faster, VAD support, robust
- `whisperX` → Speaker diarization, better alignment
- Streaming MD file writer → Zero data loss
- Simplified audio pipeline → Less complexity

#### 🔄 Keep
- `sounddevice` + `portaudio` → Reliable concurrent audio
- `ollama` integration → AI enhancement
- `pyperclip` → Clipboard support
- ID-based transcript system → Works well

---

## 📐 System Design Principles

### 1. **Reliability Over Features**
- Data integrity is non-negotiable
- Fail gracefully, never lose data
- Atomic operations for file writes
- Always preserve partial progress

### 2. **Simplicity Over Cleverness**
- Straightforward code paths
- Minimal abstraction layers
- Easy to understand and debug
- Delete more than you add

### 3. **Transparency Over Magic**
- User knows what's happening
- Clear error messages
- Visible configuration
- No hidden behaviors

### 4. **Performance Within Reason**
- Fast enough for good UX (<5s startup)
- Don't sacrifice reliability for speed
- Optimize hot paths only
- Local processing always

### 5. **Privacy By Design**
- Everything local by default
- No telemetry, no analytics
- User data never leaves machine
- Open source dependencies only

---

## 🧪 Development Principles

### Test-Driven Development (TDD)

**Philosophy:** Write tests first, then implement features.

#### Testing Strategy

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_transcript_manager.py
│   ├── test_audio_handler.py
│   ├── test_md_template.py
│   ├── test_config_manager.py
│   └── test_ollama_client.py
├── integration/             # Multi-component tests
│   ├── test_recording_flow.py
│   ├── test_transcription_pipeline.py
│   ├── test_ai_enhancement.py
│   └── test_speaker_diarization.py
├── e2e/                     # Full system tests
│   ├── test_basic_recording.py
│   ├── test_long_recording_with_pauses.py
│   ├── test_crash_recovery.py
│   └── test_file_processing.py
├── fixtures/                # Test data
│   ├── audio/
│   │   ├── speech_10s.wav
│   │   ├── speech_with_silence_5min.wav
│   │   ├── multi_speaker_2min.wav
│   │   └── muffled_english.wav
│   └── transcripts/
└── conftest.py             # Pytest configuration
```

#### TDD Workflow

```bash
# 1. Write failing test
pytest tests/unit/test_transcript_manager.py::test_append_to_transcript -v

# 2. Implement minimal code to pass
# ... write implementation ...

# 3. Refactor while keeping tests green
pytest tests/unit/test_transcript_manager.py -v

# 4. Repeat for next feature
```

#### Test Coverage Requirements
- **Unit tests:** 90%+ coverage
- **Integration tests:** Cover all user flows
- **E2E tests:** Cover critical paths (recording, processing, AI)
- **Performance tests:** Startup time, transcription speed

#### Example Test Structure

```python
# tests/unit/test_transcript_manager.py

import pytest
from pathlib import Path
from rejoice.transcript_manager import TranscriptManager

class TestTranscriptManager:
    """Test transcript creation and management"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create transcript manager with temp directory"""
        return TranscriptManager(save_dir=tmp_path)
    
    def test_create_transcript_creates_file_with_frontmatter(self, manager):
        """GIVEN a transcript manager
        WHEN creating a new transcript
        THEN file exists with valid frontmatter"""
        
        # Arrange
        content = "Test transcription content"
        
        # Act
        file_path, transcript_id = manager.create_transcript(content)
        
        # Assert
        assert file_path.exists()
        assert transcript_id.isdigit()
        
        content = file_path.read_text()
        assert "---" in content
        assert f"id: '{transcript_id}'" in content
        assert "status: recording" in content
        assert "Test transcription content" in content
    
    def test_append_to_transcript_preserves_existing_content(self, manager):
        """GIVEN an existing transcript
        WHEN appending new text
        THEN original content is preserved"""
        
        # Arrange
        file_path, _ = manager.create_transcript("Initial content")
        
        # Act
        manager.append_to_transcript(file_path, "Appended content")
        
        # Assert
        content = file_path.read_text()
        assert "Initial content" in content
        assert "Appended content" in content
    
    def test_append_to_transcript_is_atomic(self, manager, monkeypatch):
        """GIVEN an append operation
        WHEN write fails mid-operation
        THEN original file is unchanged"""
        
        # Arrange
        file_path, _ = manager.create_transcript("Original")
        original_content = file_path.read_text()
        
        # Simulate write failure
        def mock_write_fail(*args, **kwargs):
            raise IOError("Disk full")
        
        # Act
        with pytest.raises(IOError):
            monkeypatch.setattr(Path, "write_text", mock_write_fail)
            manager.append_to_transcript(file_path, "Should fail")
        
        # Assert - original file unchanged
        assert file_path.read_text() == original_content
```

---

## 🔧 Component Architecture

### Core Components

```
src/
├── core/
│   ├── __init__.py
│   ├── recorder.py              # Audio recording (sounddevice wrapper)
│   ├── transcriber.py           # Whisper integration (faster-whisper + whisperX)
│   ├── transcript_manager.py   # MD file operations
│   └── config.py                # Configuration management
├── ai/
│   ├── __init__.py
│   ├── ollama_client.py         # Ollama API client
│   ├── prompts.py               # Prompt templates
│   └── enhancer.py              # AI enhancement orchestration
├── cli/
│   ├── __init__.py
│   ├── commands.py              # CLI command handlers
│   └── output.py                # Terminal output formatting
├── utils/
│   ├── __init__.py
│   ├── file_ops.py              # Atomic file operations
│   ├── audio_ops.py             # Audio format conversions
│   └── logger.py                # Debug logging
└── main.py                      # Entry point
```

---

## 🎬 New Recording Flow

### Simplified Architecture

```
START RECORDING
    ↓
1. Create MD file with frontmatter (status: recording)
    ↓
2. Start audio capture (sounddevice)
    ↓
3. Buffer audio in memory
    ↓
USER PRESSES ENTER
    ↓
4. Stop audio capture
    ↓
5. Save audio to temporary WAV file
    ↓
6. Stream transcription with faster-whisper + whisperX
    ├─→ VAD filters silence automatically
    ├─→ For each segment with speech:
    │    ├─→ Get transcription text
    │    ├─→ Get speaker ID (if -speakers enabled)
    │    ├─→ Get timestamp (if -timestamp enabled)
    │    └─→ Append to MD file atomically
    ↓
7. Update frontmatter (status: processed)
    ↓
8. Run Ollama AI enhancement (if enabled)
    ├─→ Generate title
    ├─→ Generate summary
    └─→ Generate tags
    ↓
9. Rename file with AI-generated title
    ↓
10. Copy to clipboard (if AUTO_COPY=true)
    ↓
11. Cleanup audio file (if AUTO_CLEANUP=true)
    ↓
DONE ✅
```

### Design Philosophy

**Core Principles:**

| Principle | Implementation |
|-----------|----------------|
| Zero data loss | Create file at start, append incrementally |
| Single pass | One streaming transcription (not quick + full) |
| Smart silence handling | VAD automatically filters silence |
| Minimal dependencies | faster-whisper base, WhisperX only when needed |
| Crash recovery | Atomic appends preserve partial transcripts |
| Simple debugging | Clean code paths, comprehensive logging |

---

## 🎨 User Experience Design

### Command Line Interface

#### Basic Recording
```bash
# Start recording with defaults
$ rec

🚀 Recording started (ID: 42)
🔴 Press Enter to stop, Ctrl+C to cancel
[Press Enter]

⏹️  Stopped, transcribing...
✨ Processing segments: ████████████ 100%
📝 Transcript saved: 42_17122025_meeting-notes.md
📋 Copied to clipboard
✅ Done in 3.2s
```

#### With Speaker Diarization
```bash
$ rec -speakers

🚀 Recording started (ID: 43)
👥 Speaker diarization enabled
🔴 Press Enter to stop
[Press Enter]

⏹️  Stopped, transcribing...
✨ Processing segments: ████████████ 100%
👥 Detected 3 speakers
📝 Transcript saved: 43_17122025_team-discussion.md
✅ Done in 4.1s
```

#### With Timestamps
```bash
$ rec -timestamp

🚀 Recording started (ID: 44)
⏱️  Timestamps enabled
🔴 Press Enter to stop
```

#### Process Existing Audio
```bash
$ rec process audio/meeting.wav -speakers

📂 Processing: meeting.wav
✨ Transcribing: ████████████ 100%
👥 Detected 2 speakers
📝 Transcript saved: 45_17122025_meeting.md
✅ Done in 2.8s
```

#### Debug Mode
```bash
$ rec --debug

🚀 Recording started (ID: 46)
🔍 DEBUG MODE ENABLED

[Debug output showing each step]
🔧 Config loaded: /Users/ben/.rejoice/config.yaml
🎤 Audio device: MacBook Pro Microphone
🎙️  Sample rate: 16000 Hz
🤖 Whisper model: small (loaded in 0.8s)
🔴 Recording active...
[Press Enter]

🎯 Audio captured: 45.2s (1.4 MB)
💾 Saved to: /tmp/rejoice/stream_1234.wav
🔍 Transcription segments:
   [0:00-0:05] Speaker 1: "Hello everyone..."
   [0:06-0:12] Speaker 2: "Thanks for joining..."
📝 Appended 234 chars to transcript
✅ Transcript finalized: 46_17122025_debug-test.md
```

### Output Levels

```yaml
# Default: Clean output (minimal)
- Progress indicators only
- Essential status messages
- Errors and warnings

# Verbose (-v): More detail
- Timing information
- Speaker detection results
- File paths

# Debug (--debug): Everything
- Configuration values
- Audio device details
- Each processing step
- Segment-by-segment progress
- File operations
- AI API calls
```

---

## ⚙️ Configuration System

### Configuration Hierarchy

```
1. Defaults (hardcoded)
    ↓
2. Global config (~/.rejoice/config.yaml)
    ↓
3. Project config (./rejoice.yaml)
    ↓
4. Environment variables (.env)
    ↓
5. Command line flags
```

### Configuration File Structure

```yaml
# ~/.rejoice/config.yaml

# Core Settings
save_path: ~/Documents/benjamayden/VoiceNotes
language: en  # Force language, or 'auto' for detection

# Transcription
whisper:
  model: small  # tiny, base, small, medium, large
  engine: faster  # 'faster' or 'whisperx'
  vad_enabled: true
  vad_threshold: 0.5
  
# Features
features:
  speaker_diarization: false  # Default for -speakers
  timestamps: false           # Default for -timestamp
  auto_copy: true
  auto_cleanup_audio: true
  
# AI Enhancement (Ollama)
ollama:
  enabled: true
  url: http://localhost:11434
  model: gemma3:270m
  timeout: 180
  max_content_length: 32000

# Transcript Template
template:
  frontmatter:
    - id
    - type
    - status
    - created
    - area        # Custom field
    - category    # Custom field
    - linked      # Custom field
    - tags
    - summary
    - last_processed
    - archive_by
  
  defaults:
    type: voice-note
    status: recording
    area: ""
    category: ""
    linked: []
    tags: []

# Prompts
prompts:
  title: |
    Based on this transcript, generate a brief 3-5 word title.
    Transcript: {transcript}
  
  summary: |
    Summarize the following transcript in 2-3 sentences.
    Transcript: {transcript}
  
  tags: |
    Generate 3-5 relevant tags for this transcript.
    Return as JSON array.
    Transcript: {transcript}

# CLI
cli:
  record_command: rec
  clean_output: true
  show_progress: true

# Audio
audio:
  sample_rate: 16000
  device: -1  # -1 for default, or device ID
  
# Debug
debug:
  enabled: false
  log_file: ~/.rejoice/debug.log
  save_audio_on_error: true
```

### Environment Variables (.env)

```bash
# Override any config.yaml setting
REJOICE_SAVE_PATH=/custom/path
REJOICE_LANGUAGE=es
REJOICE_WHISPER_MODEL=medium
REJOICE_OLLAMA_ENABLED=false
REJOICE_DEBUG=true
```

### Command Line Flags

```bash
rec [OPTIONS] [COMMAND]

Commands:
  record          Start recording (default if no command)
  process FILE    Process existing audio file
  config          Manage configuration
  list            List recent transcripts
  show ID         Show transcript by ID

Recording Options:
  -speakers           Enable speaker diarization
  -no-speakers        Disable speaker diarization
  -timestamp          Enable timestamps
  -no-timestamp       Disable timestamps
  -lang LANG          Force language (en, es, fr, etc.)
  -model MODEL        Whisper model size
  -device ID          Audio device ID

Output Options:
  -v, --verbose       Verbose output
  --debug             Debug mode with full logging
  -q, --quiet         Minimal output

AI Options:
  -no-ai              Skip AI enhancement
  -ollama-model M     Use specific Ollama model

Other:
  -h, --help          Show help
  --version           Show version
```

---

## 📋 Transcript Template System

### Dynamic Template Definition

```python
# src/core/transcript_manager.py

from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime, timedelta

@dataclass
class FrontmatterField:
    """Definition of a frontmatter field"""
    name: str
    type: type
    default: Any = None
    required: bool = False
    auto_generate: bool = False
    generator: callable = None

class TranscriptTemplate:
    """Configurable transcript template"""
    
    def __init__(self, config: Dict[str, Any]):
        self.fields = self._load_fields(config)
    
    def _load_fields(self, config: Dict[str, Any]) -> List[FrontmatterField]:
        """Load field definitions from config"""
        fields = []
        
        # Standard fields
        fields.append(FrontmatterField(
            name="id",
            type=str,
            required=True,
            auto_generate=True,
            generator=self._generate_id
        ))
        
        fields.append(FrontmatterField(
            name="created",
            type=datetime,
            required=True,
            auto_generate=True,
            generator=lambda: datetime.now().strftime('%Y-%m-%d %H:%M')
        ))
        
        fields.append(FrontmatterField(
            name="status",
            type=str,
            default="recording",
            required=True
        ))
        
        # User-defined fields from config
        for field_name in config.get('template', {}).get('frontmatter', []):
            if field_name not in ['id', 'created', 'status']:
                default = config.get('template', {}).get('defaults', {}).get(field_name, '')
                fields.append(FrontmatterField(
                    name=field_name,
                    type=type(default),
                    default=default
                ))
        
        return fields
    
    def create_frontmatter(self, overrides: Dict[str, Any] = None) -> str:
        """Generate frontmatter YAML"""
        overrides = overrides or {}
        
        data = {}
        for field in self.fields:
            if field.name in overrides:
                data[field.name] = overrides[field.name]
            elif field.auto_generate:
                data[field.name] = field.generator()
            else:
                data[field.name] = field.default
        
        return self._to_yaml(data)
    
    def _to_yaml(self, data: Dict[str, Any]) -> str:
        """Convert data to YAML frontmatter"""
        import yaml
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n"
```

### Example Transcript Output

#### Without Speakers/Timestamps (default)
```markdown
---
id: '47'
type: voice-note
status: processed
created: 2025-12-17 14:30
area: work
category: meetings
linked: []
tags:
- standup
- project-update
- deadlines
summary: Team standup discussing project progress, upcoming deadlines, and blockers.
  Alice reported backend completion, Bob needs help with frontend integration.
last_processed: '2025-12-17T14:32:15.123456'
archive_by: '2026-01-16'
---
## 🎙️ Transcription

Good morning everyone. Let's start with Alice. What did you work on yesterday?

I finished the backend API for the user authentication module. All tests are passing and it's ready for integration.

Great work. Bob, how's the frontend coming along?

I'm making progress on the login page but I'm stuck on integrating with the new API. Could use some help there.

Sure, let's sync after this meeting. Any other blockers?

No other blockers. I should have the integration done by end of week.

Perfect. That's all for today. Thanks everyone.
```

#### With Speakers Enabled (`-speakers`)
```markdown
---
id: '48'
type: voice-note
status: processed
created: 2025-12-17 14:45
speakers: 3
tags:
- team-discussion
- technical
summary: Technical discussion between 3 team members about API integration challenges.
---
## 🎙️ Transcription

**Speaker 1:** Good morning everyone. Let's start with Alice. What did you work on yesterday?

**Speaker 2:** I finished the backend API for the user authentication module. All tests are passing and it's ready for integration.

**Speaker 1:** Great work. Bob, how's the frontend coming along?

**Speaker 3:** I'm making progress on the login page but I'm stuck on integrating with the new API. Could use some help there.

**Speaker 1:** Sure, let's sync after this meeting. Any other blockers?

**Speaker 3:** No other blockers. I should have the integration done by end of week.

**Speaker 1:** Perfect. That's all for today. Thanks everyone.
```

#### With Timestamps Enabled (`-timestamp`)
```markdown
---
id: '49'
type: voice-note
status: processed
created: 2025-12-17 15:00
duration: 125.4
tags:
- interview
- technical-discussion
summary: Interview discussing candidate's experience with distributed systems and API design.
---
## 🎙️ Transcription

**[00:00]** Good morning everyone. Let's start with Alice. What did you work on yesterday?

**[00:05]** I finished the backend API for the user authentication module. All tests are passing and it's ready for integration.

**[00:18]** Great work. Bob, how's the frontend coming along?

**[00:23]** I'm making progress on the login page but I'm stuck on integrating with the new API. Could use some help there.

**[00:35]** Sure, let's sync after this meeting. Any other blockers?

**[00:42]** No other blockers. I should have the integration done by end of week.

**[00:48]** Perfect. That's all for today. Thanks everyone.
```

#### With Both (`-speakers -timestamp`)
```markdown
---
id: '50'
type: voice-note
status: processed
created: 2025-12-17 15:15
speakers: 3
duration: 125.4
tags:
- interview
- panel-discussion
summary: Panel interview with 3 interviewers discussing candidate qualifications.
---
## 🎙️ Transcription

**[00:00] Speaker 1:** Good morning everyone. Let's start with Alice. What did you work on yesterday?

**[00:05] Speaker 2:** I finished the backend API for the user authentication module. All tests are passing and it's ready for integration.

**[00:18] Speaker 1:** Great work. Bob, how's the frontend coming along?

**[00:23] Speaker 3:** I'm making progress on the login page but I'm stuck on integrating with the new API. Could use some help there.

**[00:35] Speaker 1:** Sure, let's sync after this meeting. Any other blockers?

**[00:42] Speaker 3:** No other blockers. I should have the integration done by end of week.

**[00:48] Speaker 1:** Perfect. That's all for today. Thanks everyone.
```

---

## 📁 File Naming Conventions

### Transcript Files

**Format:** `{id}_{date}_{slug}.md`

**Components:**
- **`{id}`**: Sequential numeric ID (1, 2, 3, ...)
- **`{date}`**: Date in `DDMMYYYY` format (17122025)
- **`{slug}`**: URL-safe slug from AI-generated title (lowercase, hyphens)

**Lifecycle:**

```
1. Initial creation (before AI enhancement):
   42_17122025_streaming_transcript.md
   
2. After AI generates title "Team Standup Meeting":
   42_17122025_team-standup-meeting.md
   
3. Manual rename allowed (preserves ID and date):
   42_17122025_custom-name-here.md
```

**Rules:**
- ID never changes (permanent identifier)
- Date never changes (creation date)
- Slug can change (AI rename or manual rename)
- Max slug length: 50 characters
- Slug characters: `a-z`, `0-9`, `-` (hyphens)
- Multiple consecutive hyphens collapsed to one
- Leading/trailing hyphens removed

**Examples:**

```
1_17122025_quick-test.md
2_17122025_meeting-notes-with-alice-and-bob.md
3_17122025_brainstorming-session-product-ideas.md
15_18122025_debug-audio-issue.md
142_19122025_interview-senior-backend-engineer.md
```

### Slug Generation

```python
def generate_slug(title: str, max_length: int = 50) -> str:
    """
    Generate URL-safe slug from title.
    
    Examples:
        "Team Standup Meeting" → "team-standup-meeting"
        "Q4 2025 Review & Planning!" → "q4-2025-review-planning"
        "Alice & Bob's Discussion" → "alice-bobs-discussion"
    """
    import re
    
    # Lowercase
    slug = title.lower()
    
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Truncate to max length at word boundary
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    
    return slug
```

### Default Slug Fallback

If AI title generation fails or returns empty:
```
{id}_{date}_streaming_transcript.md
```

### Audio Session Files (Temporary)

**Format:** `stream_{timestamp}.wav`

**Location:** `~/.rejoice/audio_sessions/` (or configured temp location)

**Lifecycle:**
```
1. Created during recording:
   stream_1734441600.wav
   
2. Used for transcription
   
3. Deleted after successful transcription (if AUTO_CLEANUP=true)
   OR kept for debugging (if AUTO_CLEANUP=false)
```

**Cleanup Policy:**
- Default: Delete after successful transcription
- On error: Keep for recovery/debugging
- Manual cleanup: `rejoice cleanup --audio-sessions`

### Audio Archive Files (Optional)

**Format:** `{id}_{date}_audio.wav`

**Location:** `~/Documents/benjamayden/VoiceNotes/audio/` (configurable)

**When created:**
- If `ARCHIVE_AUDIO=true` in config
- Audio is permanently stored alongside transcript
- Used for re-processing or backup

**Examples:**
```
42_17122025_audio.wav
43_17122025_audio.wav
```

### Directory Structure

```
~/Documents/benjamayden/VoiceNotes/         # Main voice notes directory
├── 1_17122025_test.md                      # Transcript files
├── 2_17122025_meeting-notes.md
├── 3_17122025_brainstorm.md
└── audio/                                   # Optional: Archived audio
    ├── 1_17122025_audio.wav
    └── 2_17122025_audio.wav

~/.rejoice/                                  # Application data
├── config.yaml                              # User configuration
├── .env                                     # Environment overrides
├── prompts/                                 # Custom AI prompts
│   ├── title.txt
│   ├── summary.txt
│   └── tags.txt
├── audio_sessions/                          # Temporary audio files
│   └── stream_1734441600.wav
└── debug.log                                # Debug logging
```

### File Collision Handling

**Scenario:** Transcript with same ID + date + slug already exists

**Resolution:**
```python
def get_unique_filename(base_path: Path) -> Path:
    """
    Ensure unique filename by appending counter if needed.
    
    Example:
        42_17122025_meeting-notes.md      # Original
        42_17122025_meeting-notes-2.md    # Collision
        42_17122025_meeting-notes-3.md    # Another collision
    """
    if not base_path.exists():
        return base_path
    
    counter = 2
    while True:
        stem = base_path.stem
        new_name = f"{stem}-{counter}{base_path.suffix}"
        new_path = base_path.parent / new_name
        
        if not new_path.exists():
            return new_path
        
        counter += 1
```

**When this happens:**
- Log warning: "File collision detected, using suffix"
- Use next available number: `-2`, `-3`, etc.
- Should be rare (IDs are sequential, dates unique per day)

### Filename Validation

```python
def validate_transcript_filename(filename: str) -> bool:
    """
    Validate transcript filename format.
    
    Valid: 42_17122025_meeting-notes.md
    Invalid: meeting-notes.md
    Invalid: 42_meeting.md
    Invalid: 42_17122025.md
    """
    import re
    
    pattern = r'^(\d+)_(\d{8})_([a-z0-9-]+)\.md$'
    return bool(re.match(pattern, filename))
```

### ID Generation

**Strategy:** Sequential numbering

```python
def get_next_id(voice_notes_dir: Path) -> str:
    """
    Get next available transcript ID.
    
    Scans existing files, finds highest ID, returns ID+1.
    """
    existing_files = voice_notes_dir.glob("*.md")
    
    max_id = 0
    for file in existing_files:
        match = re.match(r'^(\d+)_', file.name)
        if match:
            file_id = int(match.group(1))
            max_id = max(max_id, file_id)
    
    return str(max_id + 1)
```

**Why sequential IDs?**
- Simple and predictable
- Easy to reference ("transcript 42")
- No UUID complexity
- Human-readable
- Sortable by creation order

### Renaming Transcripts

**User can manually rename:**
```bash
# Original
42_17122025_streaming_transcript.md

# User renames slug only (ID and date must stay)
42_17122025_my-custom-name.md

# Invalid renames (ID/date changed) - rejected:
99_17122025_my-custom-name.md  ❌
42_19122025_my-custom-name.md  ❌
```

**Validation on rename:**
- ID must match original
- Date must match original
- Only slug can change
- Slug must follow naming rules

**CLI command:**
```bash
rejoice rename 42 "My Custom Name"
# Renames: 42_17122025_* → 42_17122025_my-custom-name.md
```

---

## 🔌 WhisperX Integration

### Why WhisperX Over faster-whisper Alone?

| Feature | faster-whisper | WhisperX | Winner |
|---------|---------------|----------|--------|
| Speed | 4x faster | 4x faster | Tie |
| VAD | ✅ Built-in | ✅ Built-in | Tie |
| Speaker diarization | ❌ No | ✅ Yes | **WhisperX** |
| Word-level timestamps | ❌ Segment only | ✅ Word-level | **WhisperX** |
| Alignment quality | Good | Better (forced alignment) | **WhisperX** |
| Memory usage | Lower | Higher | faster-whisper |
| Dependencies | Fewer | More (pyannote) | faster-whisper |

**Decision:** Use **WhisperX when speakers/timestamps enabled**, faster-whisper otherwise.

### Implementation Strategy

```python
# src/core/transcriber.py

from faster_whisper import WhisperModel
import whisperx
from typing import Iterator, Dict, Any

class Transcriber:
    """Unified transcription interface"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config['whisper']['model']
        self.device = "cpu"  # or "cuda" if available
        self.compute_type = "int8"
        
        # Load appropriate model based on features
        self.needs_whisperx = (
            config['features']['speaker_diarization'] or
            config['features']['timestamps']
        )
        
        if self.needs_whisperx:
            self._load_whisperx()
        else:
            self._load_faster_whisper()
    
    def _load_faster_whisper(self):
        """Load faster-whisper for basic transcription"""
        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type
        )
        self.engine = "faster-whisper"
    
    def _load_whisperx(self):
        """Load WhisperX for advanced features"""
        self.model = whisperx.load_model(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type
        )
        
        # Load alignment model for word-level timestamps
        self.align_model, self.align_metadata = whisperx.load_align_model(
            language_code=self.config['language'],
            device=self.device
        )
        
        # Load diarization model if needed
        if self.config['features']['speaker_diarization']:
            self.diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=None,  # For HuggingFace models
                device=self.device
            )
        
        self.engine = "whisperx"
    
    def transcribe(self, audio_path: str) -> Iterator[Dict[str, Any]]:
        """
        Transcribe audio and yield segments.
        
        Returns:
            Iterator of segments with:
            - text: str
            - start: float (seconds)
            - end: float (seconds)
            - speaker: str (if diarization enabled)
        """
        if self.engine == "faster-whisper":
            yield from self._transcribe_faster_whisper(audio_path)
        else:
            yield from self._transcribe_whisperx(audio_path)
    
    def _transcribe_faster_whisper(self, audio_path: str) -> Iterator[Dict]:
        """Basic transcription without speakers"""
        segments, info = self.model.transcribe(
            audio_path,
            language=self.config['language'],
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=2000,
            ),
            beam_size=5,
        )
        
        for segment in segments:
            yield {
                'text': segment.text.strip(),
                'start': segment.start,
                'end': segment.end,
                'speaker': None
            }
    
    def _transcribe_whisperx(self, audio_path: str) -> Iterator[Dict]:
        """Advanced transcription with speakers and word-level timing"""
        import whisperx
        
        # 1. Transcribe with Whisper
        audio = whisperx.load_audio(audio_path)
        result = self.model.transcribe(
            audio,
            language=self.config['language'],
            batch_size=16
        )
        
        # 2. Align whisper output for word-level timestamps
        result = whisperx.align(
            result["segments"],
            self.align_model,
            self.align_metadata,
            audio,
            self.device,
            return_char_alignments=False
        )
        
        # 3. Assign speaker labels (if enabled)
        if self.config['features']['speaker_diarization']:
            diarize_segments = self.diarize_model(audio)
            result = whisperx.assign_word_speakers(
                diarize_segments,
                result
            )
        
        # 4. Yield segments
        for segment in result["segments"]:
            yield {
                'text': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end'],
                'speaker': segment.get('speaker', None)
            }
```

### WhisperX Dependencies

```txt
# requirements.txt additions

# Core transcription
faster-whisper>=0.10.0

# Advanced features (speaker diarization, word-level timestamps)
whisperx>=3.1.0
pyannote.audio>=3.1.0
torch>=2.0.0
torchaudio>=2.0.0
```

### Speaker Diarization Model Setup

```bash
# User needs HuggingFace token for pyannote models
# Setup instructions:

# 1. Accept pyannote terms:
#    https://huggingface.co/pyannote/speaker-diarization
#    https://huggingface.co/pyannote/segmentation

# 2. Get access token:
#    https://huggingface.co/settings/tokens

# 3. Configure (optional, stored in config):
echo "HUGGINGFACE_TOKEN=your_token_here" >> ~/.rejoice/.env
```

---

## 📦 Installation & Setup

### One-Command Install

```bash
# Install script (setup.sh)
curl -sSL https://raw.githubusercontent.com/benjamayden/rejoice-slim/main/setup.sh | bash
```

### What It Does

```bash
#!/bin/bash
# setup.sh

set -e

echo "🎙️ Installing Rejoice..."

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.8+ required"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "❌ Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# 2. Check system dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew required: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "📦 Installing PortAudio..."
    brew install portaudio
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "📦 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-dev
fi

# 3. Create virtual environment
INSTALL_DIR="$HOME/.rejoice"
echo "📁 Creating environment: $INSTALL_DIR"

python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# 4. Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install rejoice-transcription  # From PyPI

# Or install from source:
# git clone https://github.com/benjamayden/rejoice-slim.git /tmp/rejoice
# pip install /tmp/rejoice

# 5. Create config directory
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$HOME/Documents/benjamayden/VoiceNotes"

# 6. Generate default config
rejoice config init

# 7. Add to PATH
SHELL_RC="$HOME/.zshrc"
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if ! grep -q "rejoice" "$SHELL_RC"; then
    echo "" >> "$SHELL_RC"
    echo "# Rejoice voice transcription" >> "$SHELL_RC"
    echo "alias rec='$INSTALL_DIR/venv/bin/rejoice record'" >> "$SHELL_RC"
    echo "alias rejoice='$INSTALL_DIR/venv/bin/rejoice'" >> "$SHELL_RC"
fi

# 8. Download Whisper model
echo "🤖 Downloading Whisper model (this may take a few minutes)..."
rejoice download-model small

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start using:"
echo "  1. Restart your terminal, or run: source $SHELL_RC"
echo "  2. Start recording: rec"
echo ""
echo "Configuration:"
echo "  Config file: $INSTALL_DIR/config/config.yaml"
echo "  Voice notes: $HOME/Documents/benjamayden/VoiceNotes"
echo ""
echo "Optional: Install Ollama for AI summaries:"
echo "  https://ollama.ai"
echo ""
```

### One-Command Uninstall

```bash
#!/bin/bash
# uninstall.sh

echo "🗑️ Uninstalling Rejoice..."

INSTALL_DIR="$HOME/.rejoice"

# 1. Remove aliases from shell config
SHELL_RC="$HOME/.zshrc"
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

sed -i.bak '/# Rejoice voice transcription/d' "$SHELL_RC"
sed -i.bak '/alias rec=/d' "$SHELL_RC"
sed -i.bak '/alias rejoice=/d' "$SHELL_RC"

# 2. Ask about data
read -p "Delete voice notes? (y/N): " DELETE_DATA
if [[ "$DELETE_DATA" =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/Documents/benjamayden/VoiceNotes"
    echo "📁 Voice notes deleted"
fi

# 3. Remove installation
rm -rf "$INSTALL_DIR"

echo "✅ Uninstall complete!"
echo "Restart your terminal to complete removal."
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  ← Few, slow, critical paths
        │  Tests  │     (5-10 tests)
        └─────────┘
      ┌─────────────┐
      │ Integration │  ← Medium, component interactions
      │    Tests    │     (20-30 tests)
      └─────────────┘
    ┌─────────────────┐
    │   Unit Tests    │  ← Many, fast, isolated
    │   (TDD driven)  │     (100+ tests)
    └─────────────────┘
```

### Critical Test Cases

#### 1. **Zero Data Loss Tests**

```python
# tests/e2e/test_crash_recovery.py

def test_transcript_survives_mid_recording_crash(tmp_path):
    """GIVEN recording in progress
    WHEN process crashes mid-recording
    THEN partial transcript is preserved"""
    
    recorder = Recorder(save_dir=tmp_path)
    recorder.start_recording()
    
    # Simulate some recording
    time.sleep(2)
    
    # Simulate crash (kill process, don't cleanup)
    os.kill(os.getpid(), signal.SIGKILL)
    
    # Restart and check
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    
    content = files[0].read_text()
    assert "status: recording" in content  # Incomplete
    assert len(content) > 100  # Some content saved

def test_append_is_atomic_even_with_concurrent_writes():
    """GIVEN multiple threads appending to transcript
    WHEN concurrent writes occur
    THEN no data corruption occurs"""
    
    # Test atomic append under concurrent load
    # ...

def test_full_transcript_preserved_if_ai_enhancement_fails():
    """GIVEN transcript completed
    WHEN Ollama AI enhancement fails
    THEN full transcript still saved and accessible"""
    
    # ...
```

#### 2. **Long Recording with Silence Tests**

```python
# tests/integration/test_transcription_pipeline.py

def test_16_minute_recording_with_long_pauses():
    """GIVEN 16-minute recording with 2-minute silent pauses
    WHEN transcription completes
    THEN all speech segments are captured"""
    
    # Use fixture audio file
    audio_path = "tests/fixtures/audio/speech_with_silence_16min.wav"
    
    transcriber = Transcriber(config)
    segments = list(transcriber.transcribe(audio_path))
    
    # Verify all speech segments captured
    total_speech_time = sum(s['end'] - s['start'] for s in segments)
    assert total_speech_time > 120  # At least 2 minutes of speech
    
    # Verify silence was skipped
    total_duration = 16 * 60  # 16 minutes
    assert total_speech_time < total_duration  # Silence not counted

def test_vad_ignores_silence_periods():
    """GIVEN audio with long silence
    WHEN VAD processes audio
    THEN silence segments are not transcribed"""
    # ...
```

#### 3. **Speaker Diarization Tests**

```python
# tests/integration/test_speaker_diarization.py

def test_distinguishes_two_speakers():
    """GIVEN audio with 2 distinct speakers
    WHEN diarization enabled
    THEN segments correctly labeled"""
    
    audio_path = "tests/fixtures/audio/multi_speaker_2min.wav"
    config = {'features': {'speaker_diarization': True}}
    
    transcriber = Transcriber(config)
    segments = list(transcriber.transcribe(audio_path))
    
    speakers = {s['speaker'] for s in segments}
    assert len(speakers) >= 2  # At least 2 speakers detected

def test_speaker_labels_consistent_across_segments():
    """GIVEN same speaker in multiple segments
    WHEN diarization processes audio
    THEN same speaker ID used consistently"""
    # ...
```

#### 4. **Performance Tests**

```python
# tests/performance/test_speed.py

def test_startup_time_under_5_seconds():
    """GIVEN cold start
    WHEN running 'rec' command
    THEN ready to record in < 5 seconds"""
    
    start = time.time()
    subprocess.run(['rec', '--help'])
    duration = time.time() - start
    
    assert duration < 5.0

def test_transcription_faster_than_realtime():
    """GIVEN 60-second audio file
    WHEN transcribing
    THEN completes in < 60 seconds (faster than realtime)"""
    
    audio_path = "tests/fixtures/audio/speech_60s.wav"
    
    start = time.time()
    transcriber.transcribe(audio_path)
    duration = time.time() - start
    
    assert duration < 60.0  # Faster than realtime
```

### CI/CD Pipeline

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
      
      - name: Install system dependencies
        run: |
          if [ "$RUNNER_OS" == "Linux" ]; then
            sudo apt-get update
            sudo apt-get install -y portaudio19-dev
          elif [ "$RUNNER_OS" == "macOS" ]; then
            brew install portaudio
          fi
      
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration -v
      
      - name: Run E2E tests
        run: pytest tests/e2e -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 📅 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Project structure setup
- [ ] TDD framework configuration
- [ ] Configuration system (config.yaml, .env)
- [ ] Basic CLI skeleton
- [ ] Unit tests for config management

### Phase 2: Core Recording (Week 2)
- [ ] Audio capture with sounddevice
- [ ] Simple transcript manager (create, append)
- [ ] Atomic file operations
- [ ] Tests for recording flow
- [ ] Tests for atomic writes

### Phase 3: Transcription (Week 3)
- [ ] faster-whisper integration
- [ ] VAD configuration
- [ ] Streaming transcription to file
- [ ] Tests for transcription accuracy
- [ ] Tests for long recordings with silence

### Phase 4: Advanced Features (Week 4)
- [ ] WhisperX integration
- [ ] Speaker diarization
- [ ] Timestamp formatting
- [ ] Command-line flags (-speakers, -timestamp)
- [ ] Tests for diarization accuracy

### Phase 5: AI Enhancement (Week 5)
- [ ] Ollama client
- [ ] Prompt templates
- [ ] Title/summary/tag generation
- [ ] File renaming logic
- [ ] Tests for AI integration

### Phase 6: Polish (Week 6)
- [ ] Installation scripts
- [ ] Documentation
- [ ] Debug mode implementation
- [ ] Error handling improvements
- [ ] Performance optimization

### Phase 7: Testing & Release (Week 7)
- [ ] E2E test suite
- [ ] Performance benchmarking
- [ ] User acceptance testing
- [ ] Beta testing with real users
- [ ] Release v2.0.0

---

## 📚 Documentation Structure

```
docs/
├── README.md                    # Overview, quick start
├── INSTALLATION.md              # Detailed install instructions
├── USAGE.md                     # Command reference, examples
├── CONFIGURATION.md             # Config file reference
├── TROUBLESHOOTING.md           # Common issues, debug mode
├── ARCHITECTURE.md              # System design (this document)
├── DEPENDENCIES.md              # Why each dependency
├── DEVELOPMENT.md               # Contributing, dev setup
├── TESTING.md                   # Testing guide, TDD workflow
└── REWRITE_PLAN.md              # This planning document
```

---

## ✅ Success Criteria

### Must Have (MVP)
- ✅ Zero data loss in all tested scenarios
- ✅ Concurrent audio recording works
- ✅ faster-whisper integration complete
- ✅ VAD handles long silence correctly
- ✅ Clean terminal output
- ✅ One-command install/uninstall
- ✅ `rec` command starts in < 5s
- ✅ 90%+ test coverage

### Should Have
- ✅ WhisperX speaker diarization
- ✅ Timestamp support
- ✅ Ollama AI enhancement
- ✅ Configurable MD templates
- ✅ Debug mode
- ✅ Process existing audio files

### Nice to Have
- ⭐ Real-time transcript viewing in terminal
- ⭐ Web UI for browsing transcripts
- ⭐ Export to other formats (PDF, DOCX)
- ⭐ Multi-language support UI
- ⭐ Cloud sync (optional, privacy-preserving)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- macOS or Linux (Windows support coming later)
- 4GB RAM minimum (8GB recommended for large models)
- ~2GB disk space for models and dependencies

### Quick Start

```bash
# Install
curl -sSL https://raw.githubusercontent.com/benjamayden/rejoice-v2/main/install.sh | bash

# Configure (optional - has sensible defaults)
rejoice config init

# Start recording
rec

# That's it! 🎉
```

### Development Setup

```bash
# Clone repo
git clone https://github.com/benjamayden/rejoice-v2.git
cd rejoice-v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start development
# ... follow DEVELOPMENT.md guide
```

---

## 🎯 Project Goals

### Primary Goals
1. ✅ **Zero data loss** - Never lose a transcript
2. ✅ **Rock-solid reliability** - Survives crashes, interruptions
3. ✅ **Fast & accurate** - Best local transcription available
4. ✅ **Privacy-first** - All processing local
5. ✅ **Dead simple** - One command to start, one to stop

### Secondary Goals
- Extensible for future features
- Well-tested (90%+ coverage)
- Thoroughly documented
- Easy to contribute to
- Cross-platform (macOS, Linux, Windows)

### Non-Goals
- Cloud services or APIs (except local Ollama)
- Mobile apps
- Real-time collaboration
- Enterprise features
- Blockchain integration (sorry, not sorry 😄)

---

## 🤝 Contributing

This is a greenfield project - perfect opportunity to build something clean and maintainable from scratch!

### How to Contribute
1. Read `DEVELOPMENT.md` for setup
2. Check open issues or propose new features
3. Write tests first (TDD approach)
4. Submit PRs with clear descriptions
5. Update docs as needed

### Code of Conduct
- Be kind and respectful
- Write clean, tested code
- Document your changes
- Help others learn

---

## 📝 License

MIT License - use it, modify it, share it!

---

**Ready to build the most reliable voice transcription tool? Let's go! 🎙️✨**
