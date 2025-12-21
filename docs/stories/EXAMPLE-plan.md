# Story Plan: [STORY-ID] - Story Title

**Created:** YYYY-MM-DD
**Status:** Planning / In Progress / Complete
**Priority:** MVP / MMP / MLP
**Phase:** Phase X
**Complexity:** Simple / Medium / Complex

---

## 1. Story Overview

### From BACKLOG.md

[Copy the full story description from BACKLOG.md, including user story format]

**Example:**
```
As a user
I want to select transcripts interactively with fuzzy search
So that I can quickly find and work with specific recordings
```

### Context

[Brief context about why this story matters, where it fits in the product vision]

### Dependencies

- [List any stories that must be completed first]
- [List any external dependencies (libraries, tools, etc.)]

---

## 2. Acceptance Criteria

From BACKLOG.md:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

Additional criteria discovered during analysis:
- [ ] Additional criterion 1
- [ ] Additional criterion 2

---

## 3. Affected Files and Modules

### Files to Modify

1. **src/rejoice/[module]/[file].py**
   - What changes: [Brief description]
   - Why: [Rationale]

2. **src/rejoice/cli/commands.py**
   - What changes: [e.g., Add new command or update existing]
   - Why: [Rationale]

### New Files to Create

1. **src/rejoice/[module]/[new_file].py**
   - Purpose: [What this module does]
   - Key classes/functions: [List main components]

2. **tests/unit/test_[feature].py**
   - Purpose: Unit tests for [feature]
   - Coverage target: 90%+

3. **tests/integration/test_[feature]_integration.py**
   - Purpose: Integration tests for [feature]
   - Coverage target: 80%+

### Configuration Changes

- **src/rejoice/core/config.py**
  - Add new config section: [section name]
  - New fields: [list fields with types]
  - Default values: [list defaults]

---

## 4. Test Strategy

### Test Pyramid

```
     /\
    /  \  E2E Tests (1-2 tests)
   /____\
  /      \  Integration Tests (3-5 tests)
 /________\
/__________\ Unit Tests (8-15 tests)
```

### Unit Tests (RED-GREEN-REFACTOR)

**Test file:** `tests/unit/test_[feature].py`

1. **test_[basic_functionality]**
   - Test the simplest happy path
   - What it verifies: [description]
   - Expected coverage: [e.g., main function]

2. **test_[feature]_with_valid_input**
   - Test with various valid inputs
   - What it verifies: [description]

3. **test_[feature]_with_invalid_input**
   - Test error handling
   - What it verifies: [description]

4. **test_[feature]_edge_cases**
   - Empty inputs, boundary conditions
   - What it verifies: [description]

5. **test_[feature]_configuration**
   - Test with different config values
   - What it verifies: [description]

[Continue for all planned unit tests]

### Integration Tests

**Test file:** `tests/integration/test_[feature]_integration.py`

1. **test_[feature]_cli_integration**
   - Test CLI command invocation
   - Verify command-line parsing and execution

2. **test_[feature]_with_config_system**
   - Test integration with config loading
   - Verify settings are applied correctly

3. **test_[feature]_file_operations**
   - Test actual file creation/modification
   - Verify atomic writes and file integrity

### E2E Tests (If Applicable)

**Test file:** `tests/e2e/test_[feature]_e2e.py`

1. **test_full_user_workflow**
   - Test complete user journey from start to finish
   - Verify all components work together

### Coverage Targets

- **Overall:** 90%+
- **New code:** 95%+
- **Critical paths:** 100%

---

## 5. Implementation Sequence

### Phase 1: Core Logic (RED-GREEN-REFACTOR)

**Step 1.1:** Basic data models
- RED: Write test for data model creation
- GREEN: Implement minimal data model
- REFACTOR: Add validation and refinements
- Files: `src/rejoice/[module]/models.py`

**Step 1.2:** Core functionality
- RED: Write test for main function
- GREEN: Implement minimal function
- REFACTOR: Improve error handling and edge cases
- Files: `src/rejoice/[module]/[core].py`

**Step 1.3:** Error handling
- RED: Write tests for error conditions
- GREEN: Add error handling code
- REFACTOR: Improve error messages
- Files: Same as above

### Phase 2: CLI Integration (RED-GREEN-REFACTOR)

**Step 2.1:** CLI command structure
- RED: Write test for CLI invocation
- GREEN: Add command to CLI
- REFACTOR: Improve help text and options
- Files: `src/rejoice/cli/commands.py`

**Step 2.2:** User interaction
- RED: Write test for user prompts
- GREEN: Implement interaction flow
- REFACTOR: Improve UX and messaging
- Files: `src/rejoice/cli/commands.py`

### Phase 3: Configuration Integration (RED-GREEN-REFACTOR)

**Step 3.1:** Config schema
- RED: Write test for config loading
- GREEN: Add config fields
- REFACTOR: Add validation
- Files: `src/rejoice/core/config.py`

**Step 3.2:** Default values
- RED: Write test for defaults
- GREEN: Implement default config
- REFACTOR: Document config options
- Files: `src/rejoice/core/config.py`

### Phase 4: Polish and Edge Cases

**Step 4.1:** Handle edge cases
- Add tests for boundary conditions
- Implement robust error handling
- Verify data integrity

**Step 4.2:** User experience
- Improve error messages
- Add helpful suggestions
- Verify help text clarity

---

## 6. Configuration Changes

### Config Schema Updates

```python
# src/rejoice/core/config.py

@dataclass
class NewFeatureConfig:
    """Configuration for [feature]."""

    option1: str = "default_value"
    option2: bool = True
    option3: int = 10

    def validate(self) -> None:
        """Validate configuration values."""
        if self.option3 < 1:
            raise ConfigError("option3 must be positive")
```

### Environment Variables

- `REJOICE_FEATURE_OPTION1` → Maps to `new_feature.option1`
- `REJOICE_FEATURE_OPTION2` → Maps to `new_feature.option2`
- `REJOICE_FEATURE_OPTION3` → Maps to `new_feature.option3`

### Default config.yaml

```yaml
new_feature:
  option1: "default_value"
  option2: true
  option3: 10
```

---

## 7. Documentation Updates

### CHANGELOG.md

```markdown
### Added

- [STORY-ID] Story Title
  - Brief description of what was implemented
  - Key features or changes (bullet points)
  - New dependencies added (if any)
  - Configuration changes (if any)
  - Tests: X unit tests, Y integration tests (all passing)
  - Coverage: XX% for new module
```

### BACKLOG.md

- Change `❌ [STORY-ID]` to `✅ [STORY-ID]`
- Update progress counts:
  - Increment "Completed" count
  - Decrement "Not Started" count (or "In Progress" if applicable)
- Update "Last Updated" date

### CLI Help Text

```bash
rec [command] --help
```

Should display clear, helpful information about the new feature.

---

## 8. Risks and Edge Cases

### Known Risks

1. **Risk:** [Description of potential issue]
   - **Mitigation:** [How to address it]
   - **Testing:** [How to test for this]

2. **Risk:** Data loss during file operations
   - **Mitigation:** Use atomic writes (write to temp, then rename)
   - **Testing:** Test file operations with simulated failures

### Edge Cases to Test

1. **Empty input:** What happens with empty strings, empty lists, etc.?
2. **Invalid input:** What happens with malformed data?
3. **Missing files:** What happens if expected files don't exist?
4. **Permission errors:** What happens if can't write to disk?
5. **Concurrent access:** What happens if multiple processes access same file?
6. **Large data:** What happens with very large inputs?
7. **Special characters:** What happens with Unicode, spaces in paths, etc.?

### Dependencies and Blockers

- **Blocker:** [Any story that must be completed first]
- **External dependency:** [Any library or tool needed]
- **Configuration dependency:** [Any config that must be set]

---

## 9. Complexity Estimate

**Complexity:** Simple / Medium / Complex

### Rationale

[Explain why this story is rated at this complexity level]

**Simple:** Single file, straightforward logic, minimal tests
**Medium:** Multiple files, some complexity, moderate testing
**Complex:** Multiple modules, intricate logic, extensive testing

### Estimated Breakdown

- **Analysis and planning:** [Already done - this document]
- **Core implementation:** [X TDD cycles]
- **CLI integration:** [Y TDD cycles]
- **Testing:** [Z additional tests beyond TDD]
- **Documentation:** [Updates to CHANGELOG, BACKLOG, etc.]

---

## 10. Implementation Notes

### Existing Patterns to Follow

[List patterns from the codebase to follow]

**Example:**
- File operations: Use atomic writes (see `src/rejoice/transcript/manager.py`)
- CLI commands: Use Click decorators (see `src/rejoice/cli/commands.py`)
- Error handling: Raise RejoiceError with suggestions (see `src/rejoice/exceptions.py`)
- Config: Use dataclasses with validation (see `src/rejoice/core/config.py`)

### Code Examples

[Include relevant code snippets from existing codebase to guide implementation]

### Testing Examples

[Include examples of good tests from the existing test suite]

---

## 11. Open Questions

- [ ] Question 1: [Describe question]
  - **Answer:** [To be determined during implementation]

- [ ] Question 2: [Describe question]
  - **Answer:** [To be determined during implementation]

---

## Implementation Complete

[This section is added by Prompt 3 after implementation]

### Actual Implementation

- **Files created:** [List actual files]
- **Files modified:** [List actual modifications]
- **Deviations from plan:** [Any changes from original plan]

### Test Results

- **Unit tests:** X tests, all passing
- **Integration tests:** Y tests, all passing
- **E2E tests:** Z tests, all passing
- **Coverage:** XX% overall, YY% for new code

### Commit Hash

- **Commit:** `abc123def456`
- **Branch:** `feature/[STORY-ID]` or `main`

### Follow-up Work

- [ ] Any additional work needed
- [ ] Known issues or limitations
- [ ] Future enhancements to consider

### Notes

[Any additional notes about the implementation, challenges encountered, lessons learned, etc.]
