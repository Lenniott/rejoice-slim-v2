# Development Workflow Prompts

This document contains three prompts for implementing user stories using a structured, test-driven development workflow.

---

## Prompt 1: Story Analysis & Planning

```
I need you to analyze user story [STORY-ID] from docs/BACKLOG.md and create a comprehensive implementation plan.

**Your tasks:**

1. **Read and understand the story:**
   - Read the full story from docs/BACKLOG.md
   - Identify acceptance criteria, dependencies, and scope
   - Note any edge cases or special requirements

2. **Analyze the codebase:**
   - Explore relevant modules that will be affected
   - Identify existing patterns and conventions to follow
   - Map out where new code will live (which modules, files, classes)
   - Identify any existing tests that provide good examples
   - Check for any conflicts with existing functionality

3. **Assess implications:**
   - What existing code needs to be modified?
   - What new modules/classes/functions need to be created?
   - Are there any breaking changes to existing APIs?
   - What test coverage is needed (unit, integration, e2e)?
   - Are there configuration changes needed?
   - What documentation needs updating?

4. **Create implementation plan:**
   - Create a new directory: `docs/stories/` (if it doesn't exist)
   - Create a story plan file: `docs/stories/[STORY-ID]-plan.md`
   - Include in the plan:
     * Story overview (copy from BACKLOG.md)
     * Acceptance criteria checklist
     * Affected files and modules
     * New files to create
     * Test strategy (what tests to write, in what order)
     * Step-by-step implementation sequence
     * Configuration changes needed
     * Documentation updates needed
     * Risks and edge cases
     * Estimated complexity (simple/medium/complex)

5. **Verify alignment:**
   - Does this align with the "Slim" philosophy? (No GUI, no cloud, minimal complexity)
   - Does this maintain data integrity principles?
   - Does this follow TDD requirements?
   - Does this respect the local-first mandate?
   - Are there any violations of project principles?

**Output:** A detailed story plan in `docs/stories/[STORY-ID]-plan.md` that provides a clear roadmap for implementation.

**Critical reminders:**
- Follow the zero-data-loss architecture patterns
- Respect the configuration hierarchy
- Maintain test coverage above 90%
- Keep it simple - delete more than you add
- No features beyond the story scope
```

---

## Prompt 2: TDD Implementation

```
I need you to implement user story [STORY-ID] using strict test-driven development (TDD).

**Prerequisites:**
- Story plan must exist at `docs/stories/[STORY-ID]-plan.md`
- Read the plan carefully before starting
- Activate the virtual environment: `source venv/bin/activate`

**Your tasks:**

1. **Follow TDD workflow strictly:**
   For each feature component:

   a. **RED - Write failing test first:**
      - Create test file in appropriate location (tests/unit/, tests/integration/, or tests/e2e/)
      - Write the minimum test that describes the expected behavior
      - Run test to confirm it fails: `pytest tests/path/to/test_file.py -v`
      - Commit: "test: add failing test for [feature]"

   b. **GREEN - Make it pass:**
      - Write minimal code to make the test pass
      - No extra features, no premature optimization
      - Run test to confirm it passes: `pytest tests/path/to/test_file.py -v`
      - Commit: "feat: implement [feature] to pass test"

   c. **REFACTOR - Improve without breaking:**
      - Clean up code while keeping tests green
      - Remove duplication, improve names, simplify
      - Run all tests: `pytest tests/ -v`
      - Commit: "refactor: improve [feature] implementation"

2. **Implementation order (from story plan):**
   - Follow the step-by-step sequence from the plan
   - Start with core functionality (usually models/core logic)
   - Then add CLI integration
   - Finally add configuration/settings if needed

3. **Testing requirements:**
   - Unit tests: Test each function/method in isolation
   - Integration tests: Test components working together
   - E2E tests: Test full user workflows (if specified in plan)
   - Coverage target: 90%+ for new code
   - Run coverage: `pytest --cov=src/rejoice --cov-report=term`

4. **Code quality standards:**
   - Follow existing patterns in the codebase
   - Use type hints for all function signatures
   - Add docstrings for public APIs
   - Handle errors gracefully with helpful messages
   - No over-engineering - KISS (Keep It Simple, Stupid)
   - No features beyond the story scope

5. **Continuous validation:**
   - Run tests frequently: `pytest tests/ -v`
   - Check coverage: `pytest --cov=src/rejoice --cov-report=term`
   - Run type checking: `mypy src`
   - Format code: `black src tests`
   - Lint: `flake8 src tests`

6. **Integration points:**
   - If adding CLI commands: Update `src/rejoice/cli/commands.py`
   - If adding config options: Update `src/rejoice/core/config.py`
   - If creating new modules: Update `src/rejoice/__init__.py` exports
   - Add fixtures to `tests/conftest.py` if needed

**Critical rules:**
- NEVER write implementation code before the test
- NEVER skip tests because "it's simple"
- NEVER add features not in the acceptance criteria
- NEVER compromise data integrity for convenience
- ALWAYS use atomic file writes for disk operations
- ALWAYS validate configuration inputs

**When complete:**
- All tests should be passing
- Coverage should be 90%+ for new code
- Code should be formatted and linted
- Implementation should match the story plan
- No TODO comments or placeholder code

**Do NOT proceed to documentation/commits yet - that's Prompt 3.**
```

---

## Prompt 3: Testing, Documentation & Completion

```
I need you to validate, test, document, and commit the implementation of user story [STORY-ID].

**Prerequisites:**
- Implementation from Prompt 2 must be complete
- All tests should already be passing
- Virtual environment must be activated: `source venv/bin/activate`

**Your tasks:**

1. **Comprehensive testing:**

   a. Run all test suites:
   ```bash
   # Unit tests
   pytest tests/unit -v

   # Integration tests
   pytest tests/integration -v

   # E2E tests
   pytest tests/e2e -v

   # All tests with coverage
   pytest --cov=src/rejoice --cov-report=html --cov-report=term
   ```

   b. Verify coverage:
   - Overall coverage should be 90%+
   - New code coverage should be 90%+
   - Check coverage report in `htmlcov/index.html`
   - If coverage is low, add more tests (back to Prompt 2)

2. **End-to-end manual testing:**

   a. Test the actual CLI commands:
   ```bash
   # Test help text
   rec --help
   rec [command] --help

   # Test the new feature with real usage
   [Run the actual commands as a user would]

   # Test error cases
   [Try invalid inputs, missing files, etc.]

   # Test edge cases from the story plan
   [Test boundary conditions, empty inputs, etc.]
   ```

   b. Verify behavior matches acceptance criteria
   c. Check output formatting and error messages
   d. Ensure no regressions in existing functionality

3. **Code quality validation:**

   a. Run pre-commit checks:
   ```bash
   pre-commit run --all-files
   ```

   b. If pre-commit fails, fix issues and re-run

   c. Verify all checks pass:
   - black (formatting)
   - flake8 (linting)
   - mypy (type checking)
   - trailing whitespace
   - end-of-file fixer
   - yaml check

4. **Update documentation:**

   a. Update CHANGELOG.md:
   - Add entry under `## [Unreleased]` section
   - Use format: `- [STORY-ID] Story Title`
   - List key changes (what was added/changed)
   - Include any new dependencies
   - Note any breaking changes
   - Reference test coverage

   Example:
   ```markdown
   ### Added

   - [C-004] Interactive Transcript Selection
     - Implemented fuzzy search for transcript selection using `fzf`-like interface
     - Added `select_transcript()` helper in `src/rejoice/transcript/selector.py`
     - Supports keyboard navigation and filtering
     - Used in `rec view`, `rec continue`, and `rec export` commands
     - Added `prompt-toolkit>=3.0.0` dependency for interactive selection
     - Tests: 8 new unit tests, all passing (92% coverage for selector module)
   ```

   b. Update BACKLOG.md:
   - Change story status from ❌ to ✅
   - Update "Completed" count in Progress Overview
   - Update "In Progress" count to 0
   - Update "Last Updated" date at top
   - Verify phase completion percentage if applicable

   c. Update story plan (docs/stories/[STORY-ID]-plan.md):
   - Add "## Implementation Complete" section at bottom
   - Note actual implementation approach
   - Document any deviations from original plan
   - List all tests created
   - Include coverage metrics
   - Note any follow-up work needed

5. **Create git commit:**

   a. Stage all changes:
   ```bash
   git add .
   ```

   b. Review what's staged:
   ```bash
   git status
   git diff --staged
   ```

   c. Create commit with proper message format:
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

6. **Final verification:**

   a. Verify commit was created:
   ```bash
   git log -1 --stat
   ```

   b. Run one final test to ensure commit didn't break anything:
   ```bash
   pytest tests/ -v
   ```

   c. Confirm all acceptance criteria are met:
   - Review original story in BACKLOG.md
   - Check off each acceptance criterion
   - Verify all edge cases are handled
   - Ensure error messages are helpful

7. **Completion summary:**

   Provide a summary report:
   - Story ID and title
   - Files created/modified
   - Test coverage metrics
   - Pre-commit status (passed/failed)
   - Commit hash
   - Any notes or follow-up items
   - Confirmation that story is complete

**Critical validations:**
- ALL tests must pass (no exceptions)
- Pre-commit checks must pass (no exceptions)
- Coverage must be 90%+ (no exceptions)
- Manual testing must confirm behavior matches acceptance criteria
- CHANGELOG and BACKLOG must be updated
- Commit message must follow format

**Do NOT skip any steps - this is the quality gate.**
```

---

## Usage Instructions

### Sequential Workflow

Use these prompts in order for each user story:

1. **Prompt 1 (Planning):** Understand and plan the story
   - Creates a roadmap in `docs/stories/[STORY-ID]-plan.md`
   - Identifies all affected code and tests needed
   - Provides step-by-step implementation sequence

2. **Prompt 2 (Implementation):** Build the feature using TDD
   - Follows RED-GREEN-REFACTOR cycle
   - Implements exactly what's in the plan
   - Achieves 90%+ test coverage

3. **Prompt 3 (Completion):** Validate and document
   - Runs comprehensive tests (unit, integration, e2e, manual)
   - Updates all documentation (CHANGELOG, BACKLOG, story plan)
   - Creates proper git commit

### Example Session

```bash
# Session 1: Planning
# Copy Prompt 1, replace [STORY-ID] with actual ID (e.g., C-004)
# Paste into Claude Code
# Review the generated plan in docs/stories/C-004-plan.md

# Session 2: Implementation (can be same session or new session)
# Copy Prompt 2, replace [STORY-ID] with actual ID
# Paste into Claude Code
# Watch TDD cycle: test → code → test → refactor

# Session 3: Completion (can be same session or new session)
# Copy Prompt 3, replace [STORY-ID] with actual ID
# Paste into Claude Code
# Review test results, CHANGELOG, and commit
```

### Tips for Success

1. **One story at a time:** Don't try to combine multiple stories
2. **Read the plan carefully:** Prompt 2 relies on the plan from Prompt 1
3. **Don't skip tests:** TDD is non-negotiable in this project
4. **Trust the process:** These prompts enforce the project's high standards
5. **Review before committing:** Always check the diff before the commit in Prompt 3

### Customization

You can customize these prompts by:
- Adding project-specific validation steps
- Adjusting coverage thresholds
- Adding additional documentation requirements
- Including deployment steps (for future phases)

---

## Prompt Variables to Replace

When using these prompts, always replace:
- `[STORY-ID]` → Actual story ID (e.g., `C-004`, `R-010`, `AI-002`)
- `[feature]` → Brief feature description (e.g., "transcript selection")
- `[command]` → Actual CLI command (e.g., `config`, `record`, `view`)

---

## Quality Gates Enforced

These prompts enforce the project's quality standards:

✅ **Zero data loss** - Atomic writes, immediate file creation
✅ **Test coverage** - 90%+ coverage required
✅ **TDD workflow** - Test first, always
✅ **Code quality** - Pre-commit checks must pass
✅ **Documentation** - CHANGELOG and BACKLOG always updated
✅ **Simplicity** - No features beyond acceptance criteria
✅ **Local-first** - No cloud, no GUI, terminal only

---

**Remember:** These prompts are designed to maintain the high quality bar that makes Rejoice Slim v2 reliable, simple, and trustworthy. Don't skip steps, don't compromise on coverage, don't add unnecessary features.
