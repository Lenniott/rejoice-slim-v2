# 🎙️ Rejoice Slim v2 - Agent Working Prompt

**Use this prompt to continue building Rejoice Slim v2. This works for both starting fresh and picking up where you left off.**

---

## Your Mission

You're building **Rejoice Slim v2** - a local-first voice transcription tool.

**Rejoice** = {record, jot, voice}
**Slim** = {super lightweight, no UI, no cloud, no crazy}

**Core Principle:** Data integrity above all. Never lose a transcript.

---

## 📚 Your Guide Documents

You have 4 documents that guide everything:

1. **VISION.md** - Product principles, scope boundaries, decision framework
   - Read this when making product/design decisions
   - Contains "Red Lines" (never cross) and "Green Lights" (encouraged)

2. **REWRITE_PLAN.md** - Technical architecture, patterns, examples
   - Read this for implementation details and code patterns
   - Contains TDD workflow and testing strategies

3. **BACKLOG.md** - 91 user stories across 8 phases
   - **THIS IS YOUR PRIMARY WORK QUEUE**
   - Each story has: acceptance criteria, dependencies, test requirements
   - Update story status as you work: ❌ → 🚧 → ✅

4. **library_links.md** - Key dependency references
   - faster-whisper: https://github.com/SYSTRAN/faster-whisper
   - whisperX: https://github.com/m-bain/whisperX

---

## 🎯 Your Workflow

### Step 1: Check Current Status
**First, always check BACKLOG.md to see what's done:**

```bash
# Read the backlog
cat docs/BACKLOG.md | grep -A 2 "Status:"
```

Look for:
- ✅ **Done** - Completed stories
- 🚧 **In Progress** - Currently working on
- ❌ **Not Started** - Available to work on
- ⏸️ **Blocked** - Waiting on dependencies

### Step 2: Pick Next Story
**Find the next story to work on:**

1. Look for stories with status ❌ (Not Started)
2. Check dependencies are ✅ (Done)
3. Start with earliest phase that has available stories
4. Pick highest priority within that phase

**Example:**
```
Phase 2: Core Recording System
  [R-001] ✅ Done
  [R-002] 🚧 In Progress  ← Continue this
  [R-003] ❌ Not Started   ← Or start this if R-002 is done
  [R-004] ❌ Not Started (Dependencies: R-002, R-003)
```

### Step 3: Read the Story Details
Open BACKLOG.md and find your story. Read:
- **User Story** - What you're building and why
- **Acceptance Criteria** - Checkboxes for "done"
- **Dependencies** - What must be complete first
- **Technical Notes** - Implementation hints
- **Test Requirements** - What tests to write

### Step 4: Follow TDD Process
**Write tests first, then implement. This is non-negotiable.**

```bash
# 1. Write failing test
touch tests/unit/test_[feature].py
# Write test...

# 2. Run test (should FAIL)
pytest tests/unit/test_[feature].py -v

# 3. Implement minimal code to pass
touch src/rejoice/[module]/[feature].py
# Write implementation...

# 4. Run test (should PASS)
pytest tests/unit/test_[feature].py -v

# 5. Refactor while keeping tests green
# 6. Run full test suite
pytest tests/ -v --cov=src --cov-fail-under=90
```

### Step 5: Verify Tests Pass
**Before marking as done, ensure all tests pass:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage (should be 90%+ in CI, flexible locally)
pytest tests/ -v --cov=src/rejoice --cov-report=term-missing

# If any tests fail, fix them before proceeding
```

**Only proceed if:**
- ✅ All tests pass
- ✅ No linting errors (pre-commit hooks should catch these)
- ✅ Code coverage maintained or improved

### Step 6: Update BACKLOG.md
Mark your story status:
```markdown
### [R-003] Transcript File Manager (TDD)
**Status:** ✅ Done  ← Update this!
```

### Step 7: Update CHANGELOG.md
**Add your completed story to the changelog:**
```markdown
## [Unreleased]

### Added
- [R-003] Transcript File Manager - Create and append to transcript files atomically
  - Implemented TranscriptManager class
  - Added atomic file operations
  - Tests: 5 new tests, all passing
```

**Include:**
- Story ID and title
- Brief description of what was implemented
- Test count/status
- Any notable technical decisions

### Step 8: Commit and Push
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Complete [R-003]: Transcript File Manager

- Implemented TranscriptManager with atomic file operations
- Added 5 unit tests (all passing)
- Updated CHANGELOG.md
- Updated BACKLOG.md status"

# Push to remote
git push origin main
```

**Commit message should include:**
- Story ID in subject line
- What was implemented
- Test status
- Documentation updates

### Step 9: Continue to Next Story
Move to next available story with satisfied dependencies.

---

## 🚨 Critical Rules (NEVER BREAK THESE)

### ❌ Red Lines - Never Cross:
1. **No cloud dependencies** - Everything local, always
2. **No GUI components** - Terminal-only forever
3. **No data leaving user's machine** - Privacy first
4. **No hidden behavior** - Transparency always
5. **No sacrificing data integrity** - If it risks data loss, don't build it

### ✅ Green Lights - Always Do:
1. **Write tests first** - TDD is mandatory
2. **Keep it simple** - Delete more than you add
3. **Make errors clear** - Users need to know what happened
4. **Update BACKLOG.md** - Keep status current
5. **Check VISION.md when unsure** - Decision framework is there

---

## 🧭 Decision Framework

When you're uncertain about something:

**1. Check VISION.md** - Does this align with "Slim"?
- If it adds UI, cloud, or complexity → ❌ NO

**2. Check REWRITE_PLAN.md** - Is there a pattern for this?
- Follow established patterns

**3. Check BACKLOG.md** - Is this in scope?
- If not in backlog → Ask before building
- If blocked by dependencies → Do those first

**4. Ask yourself:**
- Does this improve data integrity? → ✅ Do it
- Does this make it simpler? → ✅ Do it
- Is this already solved? → ❌ Don't reinvent
- Would this violate local-first? → ❌ Don't do it

---

## 📦 Tech Stack Quick Reference

### Core Dependencies (don't change these):
- `faster-whisper` >= 0.10.0 (NOT openai-whisper)
- `sounddevice` >= 0.4.6
- `portaudio` (system dependency)
- `ollama-python` >= 0.1.0
- `pyperclip` >= 1.8.2
- `pyyaml` >= 6.0
- `rich` >= 13.0.0
- `atomicwrites` >= 1.4.0

### Dev Dependencies:
- `pytest` >= 7.0.0
- `pytest-cov` >= 4.0.0
- `black` >= 23.0.0
- `flake8` >= 6.0.0
- `mypy` >= 1.0.0

### Python: >= 3.8 (target 3.8, 3.9, 3.10, 3.11)

---

## 📁 Project Structure Reference

```
rejoice-v2/
├── docs/               # Documentation
├── src/rejoice/        # Source code
│   ├── cli/           # Commands
│   ├── core/          # Config, session
│   ├── audio/         # Recording
│   ├── transcription/ # Whisper
│   ├── transcript/    # MD files
│   ├── ai/            # Ollama
│   └── utils/         # Helpers
├── tests/
│   ├── unit/          # Fast, isolated
│   ├── integration/   # Multi-component
│   ├── e2e/          # Full system
│   └── fixtures/      # Test data
└── scripts/           # Install/uninstall
```

---

## 🎯 Phase Overview (Where Are We?)

**Phase 0:** Installation & Environment (4 stories)
**Phase 1:** Foundation & Setup (6 stories)
**Phase 2:** Core Recording System (5 stories)
**Phase 3:** Transcription (6 stories)
**Phase 4:** Advanced Features (4 stories)
**Phase 5:** AI Enhancement (6 stories)
**Phase 6:** User Commands (5+ stories)
**Phase 7:** Settings & Config (stories)
**Phase 8:** Polish & Release (stories)

**Check BACKLOG.md for current phase progress.**

---

## 💬 Communication Style

When you work:

### ✅ DO:
- Start with: "Checking BACKLOG.md for current status..."
- Say which story you're working on: "[R-003] Transcript File Manager"
- Show your TDD process: "Writing test first..."
- Verify tests pass before marking done: "All tests passing, coverage 92%"
- Update status: "Marking [R-003] as ✅ Done in BACKLOG.md"
- Update changelog: "Adding [R-003] to CHANGELOG.md"
- Push changes: "Committing and pushing changes"
- Be concise and focused

### ❌ DON'T:
- Write long explanations of obvious things
- Ask for permission to follow the process
- Explain TDD every time (just do it)
- Suggest features not in BACKLOG.md
- Question the architecture (it's already decided)

---

## 🔄 If You're Picking Up Where Another Agent Left Off

### First, Orient Yourself:

```bash
# 1. Check what's completed
grep "Status: ✅" docs/BACKLOG.md | wc -l

# 2. Check what's in progress
grep "Status: 🚧" docs/BACKLOG.md

# 3. Check current phase
# Look at the numbers above

# 4. Run tests to see what works
pytest tests/ -v

# 5. Check git log
git log --oneline -20
```

### Then:
1. **Complete any 🚧 in-progress stories first**
2. **Then pick next ❌ story with satisfied dependencies**
3. **Follow TDD process**
4. **Update BACKLOG.md**
5. **Continue**

---

## 📝 Example Session

```
Agent: Checking BACKLOG.md for current status...

Found:
- Phase 1: ✅ All complete
- Phase 2: [R-001] ✅ Done, [R-002] ✅ Done, [R-003] ❌ Not Started
- [R-003] dependencies satisfied. Starting.

Working on [R-003]: Transcript File Manager

Writing tests first...
[creates test_transcript_manager.py]

Running tests (expecting failure)...
$ pytest tests/unit/test_transcript_manager.py -v
FAILED ✗

Implementing TranscriptManager...
[creates manager.py with minimal code]

Running tests...
$ pytest tests/unit/test_transcript_manager.py -v
PASSED ✓

Running full test suite...
$ pytest tests/ -v --cov=src
Coverage: 92% ✓
All tests passing ✓

Updating BACKLOG.md...
[R-003] Status: ❌ Not Started → ✅ Done

Updating CHANGELOG.md...
Added entry for [R-003] under [Unreleased] section

Committing and pushing...
$ git add .
$ git commit -m "Complete [R-003]: Transcript File Manager

- Implemented TranscriptManager with atomic file operations
- Added 5 unit tests (all passing)
- Updated CHANGELOG.md
- Updated BACKLOG.md status"
$ git push origin main

✅ [R-003] complete. Moving to [R-004].
```

---

## 🆘 When You Need Help

**If acceptance criteria is unclear:**
- Check REWRITE_PLAN.md for similar patterns
- Check VISION.md for product direction
- Ask the human for clarification

**If dependencies seem wrong:**
- Double-check BACKLOG.md
- Verify previous stories are truly complete
- Tests pass for those stories

**If you want to add something not in BACKLOG.md:**
- DON'T - stick to the plan
- If it's critical, ask the human first

**If tests are hard to write:**
- Check REWRITE_PLAN.md for test examples
- Start with simplest test case
- Build up from there

---

## ✅ Success Metrics

**You're doing well if:**
- Tests written before implementation ✓
- Coverage stays above 90% ✓
- All tests pass ✓
- BACKLOG.md status is current ✓
- CHANGELOG.md updated for each completed story ✓
- Changes committed and pushed ✓
- No cloud/GUI added ✓
- Data integrity maintained ✓

**You're off track if:**
- Implementing without tests ✗
- Coverage dropping ✗
- Tests failing when marking story as done ✗
- Forgetting to update CHANGELOG.md ✗
- Not pushing changes to git ✗
- Adding features not in BACKLOG.md ✗
- Questioning architecture decisions ✗

---

## 🎯 Your Immediate Next Action

```bash
# 1. Check BACKLOG.md
cat docs/BACKLOG.md | grep -E "Status:|Phase" | head -50

# 2. Find next ❌ story with satisfied dependencies

# 3. Read that story's full details

# 4. Write tests for it

# 5. Implement it

# 6. Run all tests and verify they pass
pytest tests/ -v --cov=src/rejoice

# 7. Update BACKLOG.md (mark story as ✅ Done)

# 8. Update CHANGELOG.md (add entry for completed story)

# 9. Commit and push
git add .
git commit -m "Complete [STORY-ID]: [Story Title]

- [What was implemented]
- [Test status]
- Updated CHANGELOG.md and BACKLOG.md"
git push origin main

# 10. Continue to next story
```

---

**Now check BACKLOG.md and start working! 🚀**

**Remember: BACKLOG.md is your source of truth. Tests first, always. Keep it simple. Never lose data.**
