# Stage 155 Package Archive Fixture Metadata Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Derive package archive fixture filenames and expected wheel/sdist paths
in `tests/test_package_archives.py` from `scripts/check_package_archives.py`
metadata helpers instead of duplicating `fashion_radar-0.1.0`.

**Architecture:** This is a tests-only fixture-hardening node. Keep the package
archive checker and runtime metadata unchanged. Add module-level derived
constants, route positive fixture construction through those constants, and leave
intentionally wrong negative fixtures explicit.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing package archive checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-155-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-155-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-155-plan-review-prompt.md`:

```markdown
# Stage 155 Plan Review Prompt

You are reviewing the Stage 155 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Derive `tests/test_package_archives.py` package archive fixture names,
wheel `dist-info` paths, sdist root paths, and positive expected metadata strings
from `scripts/check_package_archives.py` helper functions instead of duplicating
`fashion_radar-0.1.0`.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-155-package-archive-fixture-metadata-parity-design.md`
- `docs/superpowers/plans/2026-06-22-stage-155-package-archive-fixture-metadata-parity-plan.md`
- `tests/test_package_archives.py`
- `scripts/check_package_archives.py`

Please review:
- Whether the node is correctly tests-only and does not alter package validation behavior.
- Whether the derived constants should come from existing checker helpers.
- Whether positive fixtures and expected messages should use derived constants.
- Whether intentionally wrong negative fixture names should remain explicit.
- Whether the proposed guard test proves fixture names are routed through derived constants.
- Whether the verification commands are sufficient.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-155-plan-review-prompt.md)" > /tmp/opencode-stage-155-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-155-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-155-plan-review.md`. Strip live narration before the
review heading if present. Save the body to
`docs/reviews/opencode-stage-155-plan-review.md`.

### Task 2: Derived Fixture Constants

**Files:**
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add derived constants**

After `spec.loader.exec_module(check_package_archives)`, add constants derived
from `check_package_archives.load_expected_project_metadata()` and the existing
archive-name helper functions.

- [ ] **Step 2: Add the guard test**

Add `test_package_archive_fixture_names_are_derived_from_expected_metadata()` near
the metadata-loader tests. It should assert the current public names and assert
that the positive fixture dict contains `f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA"`.

- [ ] **Step 3: Run focused guard test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "fixture_names_are_derived"
```

Expected: pass.

### Task 3: Replace Positive Fixture Duplication

**Files:**
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Update positive wheel fixture paths**

Update `WHEEL_FILES` so every expected `.dist-info` member path is built from
`EXPECTED_WHEEL_DIST_INFO_DIR`.

- [ ] **Step 2: Update positive wheel metadata content**

Build the positive `METADATA` fixture from `EXPECTED_METADATA.name` and
`EXPECTED_METADATA.version`.

- [ ] **Step 3: Update positive wheel override keys**

Update these override sites to use `EXPECTED_WHEEL_DIST_INFO_DIR`:

- `test_rejects_wheel_metadata_without_project_name`
- `test_rejects_wheel_metadata_without_project_version`
- `test_rejects_wheel_entry_points_without_console_script`

- [ ] **Step 4: Update dist-info rewrite helper**

Update `wheel_files_with_dist_info_dir()` so it detects positive wheel dist-info
members with `path.startswith(f"{EXPECTED_WHEEL_DIST_INFO_DIR}/")` instead of a
hard-coded current version.

- [ ] **Step 5: Update fixture writer defaults**

Update:

```python
write_wheel(... filename=EXPECTED_WHEEL_ARCHIVE_NAME)
write_sdist(... filename=EXPECTED_SDIST_ARCHIVE_NAME, root_dir=EXPECTED_SDIST_ROOT_DIR)
write_sdist_with_raw_member(...)
```

- [ ] **Step 6: Update expected-path assertions and expected-message strings**

Where tests assert expected package archive names, expected sdist roots, or the
expected wheel dist-info directory, use the derived constants. Keep intentionally
wrong fixture values explicit.

This step must cover:

- expected portions of `test_rejects_package_archives_with_mismatched_filenames`
- expected portion of `test_rejects_sdist_with_mismatched_root_directory`
- expected portion of `test_rejects_wheel_with_mismatched_dist_info_directory`
- `METADATA is missing Name: ...`
- `METADATA is missing Version: ...`
- `entry_points.txt is missing ...`

Leave unsafe path traversal inputs such as
`fashion_radar-0.1.0/../outside.txt` explicit, because they are test inputs for
path normalization and traversal detection rather than expected metadata.

- [ ] **Step 7: Run focused package archive tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected: all package archive tests pass.

### Task 4: Plan Rereview

**Files:**
- Create: `docs/reviews/opencode-stage-155-plan-rereview-prompt.md`
- Create: `docs/reviews/opencode-stage-155-plan-rereview.md`

- [ ] **Step 1: Write opencode plan rereview prompt**

Create `docs/reviews/opencode-stage-155-plan-rereview-prompt.md` asking
opencode to verify that the important findings from the first plan review are
addressed and that no new Critical or Important blockers remain.

- [ ] **Step 2: Run opencode plan rereview**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-155-plan-rereview-prompt.md)" > /tmp/opencode-stage-155-plan-rereview.md
```

- [ ] **Step 3: Save sanitized rereview artifact**

Inspect `/tmp/opencode-stage-155-plan-rereview.md`. Strip live narration before
the review heading if present. Save the body to
`docs/reviews/opencode-stage-155-plan-rereview.md`.

### Task 5: Review, Release Gate, and Commit

**Files:**
- Create: `docs/reviews/opencode-stage-155-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-155-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_package_archives.py
uv --no-config run --frozen ruff format --check tests/test_package_archives.py
git diff --check
```

- [ ] **Step 2: Run opencode code review**

Create `docs/reviews/opencode-stage-155-code-review-prompt.md` with the same
review structure as the plan review prompt, but ask for a code review of the new
test fixture changes. Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-155-code-review-prompt.md)" > /tmp/opencode-stage-155-code-review.md
```

- [ ] **Step 3: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-155-code-review.md`. Strip live narration before the
review heading if present. Save the body to
`docs/reviews/opencode-stage-155-code-review.md`.

- [ ] **Step 4: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_package_archives.py \
  docs/reviews/opencode-stage-155-plan-review-prompt.md \
  docs/reviews/opencode-stage-155-plan-review.md \
  docs/reviews/opencode-stage-155-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-155-plan-rereview.md \
  docs/reviews/opencode-stage-155-code-review-prompt.md \
  docs/reviews/opencode-stage-155-code-review.md \
  docs/superpowers/specs/2026-06-22-stage-155-package-archive-fixture-metadata-parity-design.md \
  docs/superpowers/plans/2026-06-22-stage-155-package-archive-fixture-metadata-parity-plan.md
git commit -m "test: derive package archive fixture metadata"
```
