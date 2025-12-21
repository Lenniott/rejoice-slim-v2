# Development Workflow - Quick Reference

Fast reference for the three-prompt development workflow.

---

## 🎯 The Three Prompts

### 1️⃣ **Planning** → Creates `docs/stories/[STORY-ID]-plan.md`
### 2️⃣ **Implementation** → Builds feature using TDD
### 3️⃣ **Completion** → Tests, documents, commits

---

## 📋 Checklist for Each Story

### Before Starting
- [ ] Story is in BACKLOG.md
- [ ] No blockers or dependencies
- [ ] Virtual environment activated: `source venv/bin/activate`

### Prompt 1: Planning
- [ ] Copy Prompt 1 from `docs/Dev Workflow Prompts.md`
- [ ] Replace `[STORY-ID]` with actual ID (e.g., `C-004`)
- [ ] Paste into Claude Code
- [ ] Review generated plan in `docs/stories/[STORY-ID]-plan.md`
- [ ] Verify plan makes sense and is complete

### Prompt 2: Implementation
- [ ] Copy Prompt 2 from `docs/Dev Workflow Prompts.md`
- [ ] Replace `[STORY-ID]` with actual ID
- [ ] Paste into Claude Code
- [ ] Follow TDD workflow (RED-GREEN-REFACTOR)
- [ ] Verify all tests pass: `pytest tests/ -v`
- [ ] Check coverage: `pytest --cov=src/rejoice --cov-report=term`
- [ ] Coverage is 90%+ for new code

### Prompt 3: Completion
- [ ] Copy Prompt 3 from `docs/Dev Workflow Prompts.md`
- [ ] Replace `[STORY-ID]` with actual ID
- [ ] Paste into Claude Code
- [ ] All tests pass (unit, integration, e2e)
- [ ] Pre-commit checks pass: `pre-commit run --all-files`
- [ ] Manual E2E testing confirms behavior
- [ ] CHANGELOG.md updated
- [ ] BACKLOG.md updated (✅ status)
- [ ] Story plan updated with completion notes
- [ ] Git commit created
- [ ] Story is DONE!

---

## 🔄 TDD Cycle (During Prompt 2)

For each feature component:

```
1. 🔴 RED: Write failing test
   ├─ Create test file
   ├─ Write test that describes behavior
   ├─ Run test (should fail)
   └─ Commit: "test: add failing test for [feature]"

2. 🟢 GREEN: Make it pass
   ├─ Write minimal code to pass test
   ├─ Run test (should pass)
   └─ Commit: "feat: implement [feature] to pass test"

3. 🔵 REFACTOR: Improve code
   ├─ Clean up, remove duplication
   ├─ Run all tests (should still pass)
   └─ Commit: "refactor: improve [feature]"

Repeat for each component ↻
```

---

## 📊 Coverage Requirements

| Type | Target | Command |
|------|--------|---------|
| Overall | 90%+ | `pytest --cov=src/rejoice --cov-report=term` |
| New code | 95%+ | Check coverage report |
| Critical paths | 100% | Manual review |

---

## 🧪 Testing Commands

```bash
# Run specific test types
pytest tests/unit -v                    # Unit tests
pytest tests/integration -v              # Integration tests
pytest tests/e2e -v                      # E2E tests

# Run all with coverage
pytest --cov=src/rejoice --cov-report=html --cov-report=term

# Run single test
pytest tests/unit/test_file.py::test_function -v

# View coverage report
open htmlcov/index.html                  # macOS
```

---

## 🎨 Code Quality Commands

```bash
# Format code
black src tests

# Lint
flake8 src tests

# Type check
mypy src

# Run all pre-commit checks
pre-commit run --all-files
```

---

## 📝 Manual E2E Testing (Prompt 3)

```bash
# Test help text
rec --help
rec [command] --help

# Test the new feature
rec [command] [args]

# Test error cases
rec [command] --invalid-option
rec [command] missing-argument

# Test edge cases
rec [command] ""
rec [command] /nonexistent/path
```

---

## 📄 Documentation Updates (Prompt 3)

### CHANGELOG.md Format

```markdown
### Added

- [STORY-ID] Story Title
  - What was implemented
  - Key features or changes
  - New dependencies (if any)
  - Tests: X unit, Y integration, Z e2e (all passing)
  - Coverage: XX% for new module
```

### BACKLOG.md Updates

1. Change `❌ [STORY-ID]` → `✅ [STORY-ID]`
2. Update counts: Completed ↑, Not Started ↓
3. Update "Last Updated" date

---

## 🚫 Common Mistakes to Avoid

| ❌ Don't | ✅ Do |
|---------|------|
| Write code before tests | Write tests first (TDD) |
| Add features not in story | Only implement acceptance criteria |
| Skip edge case testing | Test boundaries, empty, invalid inputs |
| Commit without pre-commit | Run `pre-commit run --all-files` |
| Forget to update docs | Always update CHANGELOG + BACKLOG |
| Over-engineer solutions | Keep it simple (KISS) |
| Skip manual testing | Test CLI commands manually |
| Batch mark todos complete | Mark complete immediately after done |

---

## 🎯 Quality Gates

All must pass before story is complete:

- ✅ All tests pass (unit, integration, e2e)
- ✅ Coverage ≥ 90% overall, ≥ 95% for new code
- ✅ Pre-commit checks pass
- ✅ Manual E2E testing confirms behavior
- ✅ CHANGELOG updated
- ✅ BACKLOG updated
- ✅ Story plan completed
- ✅ Git commit created
- ✅ No TODOs or placeholders in code

---

## 📦 Git Commit Format

```bash
git commit -m "feat: implement [STORY-ID] - Story Title

- Key change 1
- Key change 2
- Key change 3

Tests: X unit, Y integration, Z e2e (all passing)
Coverage: XX% overall, YY% for new code

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## ⏱️ Typical Timeline

| Phase | Prompt | Duration | Output |
|-------|--------|----------|--------|
| Planning | 1 | 5-15 min | Story plan |
| Implementation | 2 | 30-120 min | Feature + tests |
| Completion | 3 | 10-20 min | Docs + commit |

**Simple story:** 45-90 min total
**Medium story:** 90-180 min total
**Complex story:** 3-6 hours total

---

## 🔗 Quick Links

- **Full prompts:** `docs/Dev Workflow Prompts.md`
- **Story plans:** `docs/stories/`
- **Example plan:** `docs/stories/EXAMPLE-plan.md`
- **Backlog:** `docs/BACKLOG.md`
- **Changelog:** `CHANGELOG.md`
- **Project guide:** `CLAUDE.md`

---

## 🆘 Troubleshooting

**Tests failing?**
→ Run `pytest tests/ -v` to see details
→ Check imports and file paths
→ Verify virtual environment is activated

**Coverage too low?**
→ Add tests for untested branches
→ Check `htmlcov/index.html` for gaps
→ Test edge cases and error paths

**Pre-commit failing?**
→ Run `black src tests` to format
→ Run `flake8 src tests` to see lint errors
→ Run `mypy src` to see type errors

**Can't find story?**
→ Check `docs/BACKLOG.md`
→ Search for story ID (e.g., `[C-004]`)
→ Verify story hasn't already been completed

---

**Remember:** Quality over speed. These prompts enforce the standards that make Rejoice reliable, simple, and trustworthy.
