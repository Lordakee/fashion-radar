# Stage 178 Community Handoff Renderer Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add exact regression tests for community handoff directory check renderer plural count labels and unavailable candidate preview output.

**Architecture:** Test-only hardening. Reuse `check_community_handoff_directory` and `render_community_handoff_directory_check_table` from the existing `tests/test_community_handoff_check.py` fixture flow, then assert exact summary lines. Runtime implementation should remain untouched unless the new tests reveal a real defect.

**Tech Stack:** Python, pytest, pydantic `model_copy`, existing community handoff check models, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_community_handoff_check.py`
  - Rename the existing singular renderer test to
    `test_render_community_handoff_directory_check_table_uses_singular_count_labels`.
  - Add a plural renderer exact-line test.
  - Add an unavailable candidate-preview renderer exact-line test.
- Add: `docs/superpowers/specs/2026-06-24-stage-178-community-handoff-renderer-guard-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-178-community-handoff-renderer-guard-plan.md`
- Add: `docs/reviews/opencode-stage-178-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-178-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-178-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-178-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-178-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-178-release-review.md`

## Task 1: Add Renderer Count Label Guards

**Files:**

- Modify: `tests/test_community_handoff_check.py`

- [ ] **Step 1: Confirm the plural guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Rename the singular renderer test**

Change:

```python
def test_render_community_handoff_directory_check_table_uses_singular_error_label(
    tmp_path: Path,
) -> None:
```

to:

```python
def test_render_community_handoff_directory_check_table_uses_singular_count_labels(
    tmp_path: Path,
) -> None:
```

- [ ] **Step 3: Add the plural renderer exact-line test**

Immediately after the singular renderer test, add:

```python
def test_render_community_handoff_directory_check_table_uses_plural_count_labels(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )
    assert result.candidate_preview is not None
    result = result.model_copy(
        update={
            "community_signal_lint": result.community_signal_lint.model_copy(
                update={
                    "file_count": 2,
                    "row_count": 2,
                    "valid_row_count": 2,
                    "error_count": 2,
                }
            ),
            "candidate_preview": result.candidate_preview.model_copy(
                update={
                    "row_count": 2,
                    "candidate_count": 2,
                }
            ),
            "import_dry_run": result.import_dry_run.model_copy(
                update={
                    "file_count": 2,
                    "valid_file_count": 2,
                    "row_count": 2,
                    "error_count": 2,
                }
            ),
        }
    )

    lines = render_community_handoff_directory_check_table(result)
    lint_line = next(line for line in lines if line.startswith("Lint: "))
    candidate_line = next(line for line in lines if line.startswith("Candidate preview: "))
    import_line = next(line for line in lines if line.startswith("Import dry-run: "))

    assert lint_line == "Lint: 2 files, 2/2 import-ready rows, 2 errors"
    assert candidate_line == "Candidate preview: 2 candidates from 2 rows"
    assert import_line == "Import dry-run: 2/2 valid files, 2 rows, 2 errors"
```

- [ ] **Step 4: Run the renamed singular and new plural tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_count_labels \
  tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_plural_count_labels -q
```

Expected: both tests pass.

## Task 2: Add Unavailable Candidate Preview Renderer Guard

**Files:**

- Modify: `tests/test_community_handoff_check.py`

- [ ] **Step 1: Confirm the unavailable renderer guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the unavailable candidate-preview renderer test**

Immediately after the plural renderer test, add:

```python
def test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    (directory / "bad.csv").write_text(
        "url,title,published_at,author_handle\n"
        "https://example.com/check/bad,Bad row,not-a-date,@raw\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=50,
    )

    assert result.candidate_preview is None
    lines = render_community_handoff_directory_check_table(result)
    candidate_line = next(line for line in lines if line.startswith("Candidate preview: "))

    assert candidate_line == "Candidate preview: unavailable"
    assert (
        "error | candidate_preview | candidate_preview_unavailable | "
        "Candidate preview could not read or validate the handoff directory."
    ) in lines
```

- [ ] **Step 3: Run the new unavailable renderer test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_shows_unavailable_candidate_preview -q
```

Expected: the test passes. If it fails, inspect whether the renderer output or
finding row changed. Only update runtime code if the failure reveals a real
regression from the intended existing behavior.

## Task 3: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_community_handoff_check.py`
- Add: `docs/reviews/opencode-stage-178-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-178-code-review.md`

- [ ] **Step 1: Run focused community handoff checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q
uv --no-config run --frozen ruff check tests/test_community_handoff_check.py
uv --no-config run --frozen ruff format --check tests/test_community_handoff_check.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-178-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 178 implementation. The prompt
must require the response to start with:

```text
# Stage 178 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-178-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-178-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact so it contains only one final review body if opencode includes
process chatter, ANSI output, command logs, or multiple drafts.

## Task 4: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-178-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-178-release-review.md`

- [ ] **Step 1: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass; token and extraheader checks report no persisted
secrets. For the two absence checks, exit 1 with no output is the expected clean
result.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-178-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 178 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-178-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_community_handoff_check.py \
  docs/superpowers/specs/2026-06-24-stage-178-community-handoff-renderer-guard-design.md \
  docs/superpowers/plans/2026-06-24-stage-178-community-handoff-renderer-guard-plan.md \
  docs/reviews/opencode-stage-178-plan-review-prompt.md \
  docs/reviews/opencode-stage-178-plan-review.md \
  docs/reviews/opencode-stage-178-code-review-prompt.md \
  docs/reviews/opencode-stage-178-code-review.md \
  docs/reviews/opencode-stage-178-release-review-prompt.md \
  docs/reviews/opencode-stage-178-release-review.md
git commit -m "test: guard community handoff renderer summaries"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers singular rename and plural summary guards, Task 2
  covers unavailable candidate-preview rendering, Task 3 covers focused
  verification and code review, and Task 4 covers release gate, release review,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: source acquisition, connectors, scraping, browser automation,
  platform APIs, monitoring, scheduling, ranking, compliance-review product
  features, dependencies, and lockfiles remain out of scope.
