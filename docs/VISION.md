# 🎯 Rejoice Slim - Vision Document

**Version:** 2.0
**Date:** December 17, 2025
**Status:** Active Guide for Development

---

## 📍 Core Purpose

**One sentence:** Record voice, get accurate transcripts with AI summaries - all local, no cloud, no bloat.

**The name explained:** Rejoice {record, jot, voice} Slim {super lightweight, no UI, no cloud, no crazy}

---

## 🎨 Design Philosophy

### The "Slim" Mandate

This is **Rejoice SLIM**, not Rejoice Feature-Packed:

- **No GUI** - Terminal only, keyboard-driven
- **No cloud** - Everything local, period
- **No crazy** - Simple, predictable, boring (in a good way)
- **Lightweight** - Fast startup, minimal resources
- **Focused** - Does one thing exceptionally well

### Core Principles (Non-Negotiable)

1. **Data Integrity Above All**
   - Once recording starts, never lose a single word
   - Survive crashes, power loss, interruptions
   - Atomic operations, incremental saves
   - *Why:* Trust is everything - users must know their recordings are safe

2. **Simplicity Over Features**
   - One command to start: `rec`
   - One key to stop: `Enter`
   - One key to cancel: `Ctrl+C`
   - *Why:* Cognitive load kills adoption - make it brainless

3. **Local-First, Local-Only**
   - No internet required (except Ollama install)
   - No telemetry, no analytics, no phone-home
   - User data never leaves the machine
   - *Why:* Privacy isn't a feature, it's a baseline

4. **Transparency Over Magic**
   - User sees what's happening (when they want to)
   - Clear error messages
   - Configurable everything
   - Open prompts, open configs
   - *Why:* Hidden behaviors breed distrust

5. **Boring Reliability Over Clever Features**
   - Straightforward code > clever optimizations
   - Proven libraries > custom implementations
   - Delete more than you add
   - *Why:* The best code is code that just works

---

## ✅ Must-Have Features (MVP)

These are **non-negotiable** for v2.0 launch:

1. **Zero-Loss Recording**
   - Incremental MD file creation (immediate persistence)
   - Atomic writes (no partial corruption)
   - Crash recovery

2. **Concurrent Audio**
   - Works while Zoom/Spotify/browser running
   - No microphone conflicts

3. **Fast Transcription**
   - faster-whisper (4x faster than openai-whisper)
   - VAD support (handles silence)
   - Sub-5-second startup

4. **AI Enhancement**
   - Ollama integration
   - Title generation
   - Summary creation
   - Auto-tagging

5. **Language Control**
   - Force specific language
   - Prevent misdetection (muffled English → Chinese)

6. **Simple Installation**
   - One-command install
   - Virtual environment isolation
   - Clean uninstall

7. **Configurable Output**
   - Custom MD templates
   - Frontmatter control
   - Save location config

8. **Process Existing Files**
   - Transcribe uploaded audio
   - Batch processing

---

## 🚫 Explicitly Out of Scope

These are **forbidden** in v2.0 to maintain "Slim" identity:

### Never Add These:
- ❌ GUI or web interface (terminal only)
- ❌ Cloud services or remote APIs
- ❌ Mobile apps
- ❌ Real-time collaboration
- ❌ Database (flat files only)
- ❌ User accounts or authentication
- ❌ Plugins or extensions system
- ❌ Export to fancy formats (MD only)

### Maybe Later (v3.0+):
- ⏸️ Real-time transcript viewing in terminal
- ⏸️ Windows support (macOS/Linux first)
- ⏸️ Advanced noise filtering
- ⏸️ Custom whisper model training

---

## 👤 User Experience Goals

### How Should It Feel?

**Like a trusted notepad:**
- Always there when you need it
- Never loses your work
- Gets out of your way
- No surprises

**Terminal experience:**
- Minimal output by default (progress only)
- Debug mode available for troubleshooting
- Clear, actionable error messages
- No emoji spam (keep it professional)

**Speed perception:**
- Instant `rec` command response
- Real-time progress indicators
- No mysterious pauses or hangs

**Configuration philosophy:**
- Works great out-of-the-box
- Everything tweakable if needed
- Sensible defaults
- Clear documentation

---

## 🎯 Success Metrics

### How Do We Know We're Done?

**Technical metrics:**
- [ ] Zero data loss in 100+ crash test scenarios
- [ ] <5 second cold startup time
- [ ] 90%+ test coverage
- [ ] Works on macOS and Linux
- [ ] One-command install works on clean system

**User experience metrics:**
- [ ] New user records first transcript in <5 minutes
- [ ] Recording "just works" alongside other audio apps
- [ ] AI summaries are useful, not distracting
- [ ] Users trust the tool (no "where did my recording go?" moments)

**Code quality metrics:**
- [ ] Every feature has tests written first (TDD)
- [ ] <10 dependencies (excluding OS libraries)
- [ ] All configs explained in docs
- [ ] Contributing guide makes sense to newcomers

---

## 🧭 Decision-Making Framework

### When Building Features, Ask:

1. **Does this align with "Slim"?**
   - If it adds UI, cloud, or complexity → **NO**
   - If it's a helper script or fancy export → **NO**
   - If it requires >1 new dependency → **THINK HARD**

2. **Does this improve data integrity?**
   - If yes → **HIGH PRIORITY**
   - If no effect → **LOW PRIORITY**

3. **Does this make the tool simpler?**
   - Fewer steps to accomplish task → **YES**
   - Removes configuration → **MAYBE** (depends on use case)
   - Adds configuration → **LOW PRIORITY**

4. **Is this already solved by existing tools?**
   - If yes → **SKIP** (don't reinvent wheels)
   - If yes but poorly → **CONSIDER** (make it better)

5. **Would this violate local-first principle?**
   - If requires internet → **NO**
   - If optional internet → **THINK HARD**

---

## 🛡️ Guardrails for Autonomous Agents

### Red Lines (Never Cross):

1. **Never add cloud dependencies**
   - No API calls to external services
   - Ollama must be local-only

2. **Never store data outside user's machine**
   - No temp files in cloud storage
   - No "helpful" uploads

3. **Never hide behavior from user**
   - No silent failures
   - No background processes without explicit config

4. **Never sacrifice data integrity for features**
   - If it risks data loss → DON'T BUILD IT
   - If it makes recovery harder → DON'T BUILD IT

5. **Never add a GUI component**
   - Terminal only, forever
   - ASCII art is fine, HTML is not

### Green Lights (Encouraged):

1. **More tests** - Always good
2. **Better error messages** - Always good
3. **Documentation improvements** - Always good
4. **Performance optimizations** - Good if safe
5. **Simpler code** - Always good

---

## 📦 Project Structure at Start

### Initial Directory Layout:

```
rejoice-v2/
├── .github/
│   └── workflows/
│       └── test.yml              # CI/CD pipeline
├── src/
│   └── rejoice/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── cli.py               # Command handling
│       ├── config.py            # Configuration management
│       ├── audio.py             # Recording logic
│       ├── transcription.py    # Whisper integration
│       ├── transcript.py        # MD file management
│       └── ai.py                # Ollama integration
├── tests/
│   ├── unit/                    # Fast, isolated tests
│   ├── integration/             # Multi-component tests
│   ├── e2e/                     # Full system tests
│   ├── fixtures/                # Test data
│   └── conftest.py              # Pytest config
├── docs/
│   ├── README.md                # Quick start
│   ├── INSTALLATION.md          # Setup guide
│   ├── USAGE.md                 # Command reference
│   ├── CONFIGURATION.md         # Config options
│   └── TROUBLESHOOTING.md       # Debug help
├── scripts/
│   ├── install.sh               # Installation script
│   └── uninstall.sh             # Clean removal
├── .gitignore
├── .env.example                 # Config template
├── pyproject.toml               # Package config
├── setup.py                     # Install script
├── README.md                    # Project overview
├── VISION.md                    # This document
├── REWRITE_PLAN.md              # Technical spec
└── LICENSE
```

### Initial Files to Create:

1. **pyproject.toml** - Package metadata, dependencies
2. **setup.py** - Installation configuration
3. **.gitignore** - Ignore patterns
4. **.env.example** - Configuration template
5. **README.md** - Basic project info
6. **tests/conftest.py** - Pytest setup
7. **src/rejoice/__init__.py** - Package initialization
8. **scripts/install.sh** - Installation script

---

## 🚀 Initialization Prompt

### To Start the Project Build:

```
I want to build Rejoice Slim v2 from scratch following the vision and rewrite plan.

Context:
- This is a greenfield rewrite (clean slate, no legacy code)
- Local-first voice transcription tool
- Terminal-only, no GUI, no cloud
- Focus: reliability, simplicity, privacy

Approach:
1. Set up project structure following TDD principles
2. Create foundational files (pyproject.toml, setup.py, etc.)
3. Implement core functionality incrementally with tests first
4. Follow the vision document principles strictly

Phase 1 Goals:
- Project structure setup
- Package configuration (pyproject.toml, setup.py)
- TDD framework (pytest, fixtures)
- Basic CLI skeleton (argparse or click)
- Configuration system (config.yaml support)
- Unit tests for config management

Please start by:
1. Creating the initial project structure
2. Setting up pyproject.toml with all dependencies from REWRITE_PLAN.md
3. Creating a basic CLI entry point
4. Setting up pytest infrastructure
5. Writing first tests for configuration system

Constraints:
- Follow vision document principles (local-first, no GUI, data integrity)
- TDD approach (write tests first)
- Keep it simple (boring is good)
- Explain key decisions

Ready to build? Let's start with Phase 1.
```

---

## 🎓 Key Learnings from v1

### What Worked:
- ✅ ID-based transcript system
- ✅ sounddevice + portaudio (concurrent audio)
- ✅ Ollama integration
- ✅ Markdown output format
- ✅ Terminal-first approach

### What Didn't Work:
- ❌ openai-whisper (too slow, fails on silence)
- ❌ Custom chunking system (over-engineered)
- ❌ Dual transcription (unnecessary complexity)
- ❌ Late file creation (data loss risk)
- ❌ Too many configuration options (decision fatigue)

### Lessons Applied in v2:
1. **Incremental saves** - File exists from first byte
2. **Simpler pipeline** - One transcription pass
3. **Better VAD** - faster-whisper handles silence
4. **Less configuration** - Sensible defaults, fewer knobs
5. **Tests from day one** - TDD prevents regression

---

**Remember: This is SLIM. When in doubt, delete. When tempted to add features, re-read this document. 🎙️**
