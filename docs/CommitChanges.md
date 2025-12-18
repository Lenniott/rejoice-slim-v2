### Committing Changes in Rejoice Slim v2

This project uses **TDD + pre-commit hooks**, so a few checks must pass before `git commit` succeeds. Use this checklist whenever you’re ready to commit.

---

### 1. Activate the virtual environment

From the project root (`rejoice-slim-v2`):

```bash
# If venv already exists (usual case)
source venv/bin/activate
```

If you don’t have a `venv/` yet:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

---

### 2. Run the tests

Pick the **smallest scope that covers what you changed**:

- **Single test file you just worked on** (fastest):
  ```bash
  pytest tests/unit/test_transcript_manager.py -v
  ```

- **All unit tests:**
  ```bash
  pytest tests/unit -v
  ```

- **Full suite (when finishing a bigger story):**
  ```bash
  pytest tests -v
  ```

If anything fails:
- Read the traceback
- Fix the code/tests
- Re-run the same `pytest` command until it’s green

---

### 3. (Optional but helpful) Run pre-commit manually

This runs the same checks that `git commit` will run:

```bash
pre-commit run --all-files
```

If this command **modifies files** (e.g. trims whitespace, fixes end-of-file newlines):

```bash
git add .
pre-commit run --all-files  # re-run if needed
```

Keep doing this until all hooks pass.

---

### 4. Commit your changes

Once tests and pre-commit hooks are passing:

```bash
git status           # sanity-check what’s staged
git add .            # or add specific files

git commit -m "Complete [R-003]: Transcript Manager - Create File"
```

For story work, follow this pattern in the commit message:

- **Subject:** `Complete [STORY-ID]: Short Story Title`
- **Body bullets:** what you implemented, test status, and any doc updates.

Example:

```bash
git commit -m "Complete [R-003]: Transcript Manager - Create File

- Implement transcript manager with atomic creation and YAML frontmatter
- Add unit tests for ID generation, file creation, and atomic writes
- Update BACKLOG and CHANGELOG entries for [R-003]
"
```

---

### 5. Push when ready

```bash
git push origin main
```

Use this loop for every story:
1. **Edit code + tests**
2. **Run pytest** (targeted or full)
3. **Run pre-commit** (or let `git commit` run it)
4. **Fix anything that fails**
5. **Commit + push**
