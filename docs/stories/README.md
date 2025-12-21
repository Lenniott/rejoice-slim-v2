# Story Plans

This directory contains detailed implementation plans for user stories from the BACKLOG.

## Purpose

Each story plan provides a comprehensive roadmap for implementing a user story using test-driven development (TDD). Plans are created during the analysis phase (Prompt 1) and guide the implementation (Prompt 2).

## File Naming Convention

```
[STORY-ID]-plan.md
```

Examples:
- `C-004-plan.md` - Interactive Transcript Selection
- `R-010-plan.md` - Audio Level Monitoring
- `AI-002-plan.md` - AI-Generated Summaries

## Story Plan Structure

Each plan should include:

1. **Story Overview**
   - Story ID and title
   - Description from BACKLOG.md
   - Priority tier (MVP/MMP/MLP)
   - Phase assignment

2. **Acceptance Criteria**
   - Checklist of criteria from BACKLOG.md
   - Any additional criteria discovered during analysis

3. **Affected Files and Modules**
   - Existing files to modify
   - New files to create
   - Test files needed

4. **Test Strategy**
   - Unit tests to write (in order)
   - Integration tests needed
   - E2E tests required
   - Expected coverage target

5. **Implementation Sequence**
   - Step-by-step implementation order
   - RED-GREEN-REFACTOR cycles
   - Integration points

6. **Configuration Changes**
   - Config file updates
   - Environment variables
   - Default values

7. **Documentation Updates**
   - CHANGELOG entry format
   - BACKLOG status update
   - README changes (if any)

8. **Risks and Edge Cases**
   - Known challenges
   - Edge cases to test
   - Dependencies or blockers

9. **Complexity Estimate**
   - Simple / Medium / Complex
   - Rationale for estimate

## Workflow Integration

Plans are used in the three-prompt development workflow:

1. **Prompt 1 (Planning):** Creates the story plan
   - Analyzes codebase
   - Identifies implications
   - Creates `[STORY-ID]-plan.md` in this directory

2. **Prompt 2 (Implementation):** Follows the plan
   - Implements using TDD
   - References plan for sequence and tests
   - Updates plan with deviations

3. **Prompt 3 (Completion):** Updates the plan
   - Adds "Implementation Complete" section
   - Documents actual approach
   - Notes any follow-up work

## Example Plan

See `EXAMPLE-plan.md` for a template/example structure.

## Best Practices

- **Read before coding:** Always read the plan thoroughly before starting implementation
- **Update as you go:** If you deviate from the plan, update it with rationale
- **Reference in commits:** Link to the plan in commit messages
- **Keep it focused:** One plan per story, no combining multiple stories
- **Include context:** Assume the implementer hasn't read the BACKLOG in detail

## Archives

Completed story plans remain in this directory as historical reference and examples for future stories.
