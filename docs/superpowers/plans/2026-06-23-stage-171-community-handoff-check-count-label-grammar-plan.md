# Stage 171 Community Handoff Check Count Label Grammar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix singular count-label wording in human-readable `community-handoff-check-dir` summary lines.

**Architecture:** Tighten the existing renderer test in `tests/test_community_handoff_check.py`, then update only `render_community_handoff_directory_check_table(...)` in `src/fashion_radar/community_handoff_check.py` to reuse the already-imported `format_count_label(...)` helper for display labels. Keep check logic, JSON output, models, CLI flow, strict mode, and historical prior-stage artifacts unchanged.

**Tech Stack:** Python standard library, existing Pydantic models, existing `lint_formatting` helper, pytest, Markdown, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_community_handoff_check.py`
  - Extend the existing renderer grammar test to force one-count state for the
    lint, candidate preview, and import dry-run summary lines.
- Modify: `src/fashion_radar/community_handoff_check.py`
  - Use `format_count_label(...)` for in-scope file, row, candidate, and valid
    file labels inside `render_community_handoff_directory_check_table(...)`.
- Add: `docs/superpowers/specs/2026-06-23-stage-171-community-handoff-check-count-label-grammar-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-171-community-handoff-check-count-label-grammar-plan.md`
- Add: `docs/reviews/opencode-stage-171-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-171-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-171-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-171-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-171-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-171-release-review.md`

## Task 1: Add RED Renderer Expectations

**Files:**

- Modify: `tests/test_community_handoff_check.py`

- [ ] **Step 1: Extend synthetic renderer state**

In `test_render_community_handoff_directory_check_table_uses_singular_error_label(...)`,
replace the existing `result.model_copy(...)` block with:

```python
    result = result.model_copy(
        update={
            "community_signal_lint": result.community_signal_lint.model_copy(
                update={
                    "file_count": 1,
                    "row_count": 1,
                    "valid_row_count": 1,
                    "error_count": 1,
                }
            ),
            "candidate_preview": result.candidate_preview.model_copy(
                update={
                    "row_count": 1,
                    "candidate_count": 1,
                }
            ),
            "import_dry_run": result.import_dry_run.model_copy(
                update={
                    "file_count": 1,
                    "valid_file_count": 1,
                    "row_count": 1,
                    "error_count": 1,
                }
            ),
        }
    )
```

The fixture builds a valid result before mutation, so `result.candidate_preview`
is expected to be non-`None`.

- [ ] **Step 2: Add exact line assertions**

After the existing `lint_line` lookup, add a candidate preview lookup:

```python
    candidate_line = next(line for line in lines if line.startswith("Candidate preview: "))
```

Replace the two existing `endswith(", 1 error")` assertions with:

```python
    assert lint_line == "Lint: 1 file, 1/1 import-ready row, 1 error"
    assert candidate_line == "Candidate preview: 1 candidate from 1 row"
    assert import_line == "Import dry-run: 1/1 valid file, 1 row, 1 error"
```

- [ ] **Step 3: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
```

Expected before implementation: fails because the renderer still emits plural
phrases such as `1 files`, `1/1 import-ready rows`, `1 candidates`, `1 rows`,
or `1/1 valid files`.

## Task 2: Singularize Handoff Check Summary Labels

**Files:**

- Modify: `src/fashion_radar/community_handoff_check.py`

- [ ] **Step 1: Update the Lint line**

Change:

```python
            f"{result.community_signal_lint.file_count} files, "
            f"{result.community_signal_lint.valid_row_count}/"
            f"{result.community_signal_lint.row_count} import-ready rows, "
```

to:

```python
            f"{format_count_label(result.community_signal_lint.file_count, 'file', 'files')}, "
            f"{result.community_signal_lint.valid_row_count}/"
            f"{format_count_label(result.community_signal_lint.row_count, 'import-ready row', 'import-ready rows')}, "
```

- [ ] **Step 2: Update the Candidate preview line**

Change:

```python
                    f"{result.candidate_preview.candidate_count} candidates from "
                    f"{result.candidate_preview.row_count} rows"
```

to:

```python
                    f"{format_count_label(result.candidate_preview.candidate_count, 'candidate', 'candidates')} from "
                    f"{format_count_label(result.candidate_preview.row_count, 'row', 'rows')}"
```

Leave the `Candidate preview: unavailable` branch unchanged.

- [ ] **Step 3: Update the Import dry-run line**

Change:

```python
            f"{result.import_dry_run.valid_file_count}/"
            f"{result.import_dry_run.file_count} valid files, "
            f"{result.import_dry_run.row_count} rows, "
```

to:

```python
            f"{result.import_dry_run.valid_file_count}/"
            f"{format_count_label(result.import_dry_run.file_count, 'valid file', 'valid files')}, "
            f"{format_count_label(result.import_dry_run.row_count, 'row', 'rows')}, "
```

- [ ] **Step 4: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q
uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_check_dir_table_output_is_summary_only -q
uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-171-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-171-code-review.md`
- Add: `docs/reviews/opencode-stage-171-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-171-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-171-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-171-community-handoff-check-count-label-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-171-community-handoff-check-count-label-grammar-plan.md`
- `src/fashion_radar/community_handoff_check.py`
- `tests/test_community_handoff_check.py`

The prompt must require the response to start with:

```text
# Stage 171 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-171-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-171-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter or command logs.

- [ ] **Step 3: Run release gate**

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

Expected: all commands pass; token and extraheader checks report no secrets.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-171-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 171 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-171-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/community_handoff_check.py \
  tests/test_community_handoff_check.py \
  docs/superpowers/specs/2026-06-23-stage-171-community-handoff-check-count-label-grammar-design.md \
  docs/superpowers/plans/2026-06-23-stage-171-community-handoff-check-count-label-grammar-plan.md \
  docs/reviews/opencode-stage-171-plan-review-prompt.md \
  docs/reviews/opencode-stage-171-plan-review.md \
  docs/reviews/opencode-stage-171-code-review-prompt.md \
  docs/reviews/opencode-stage-171-code-review.md \
  docs/reviews/opencode-stage-171-release-review-prompt.md \
  docs/reviews/opencode-stage-171-release-review.md
git commit -m "fix: singularize handoff check count labels"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the RED renderer test, Task 2 covers the source
  renderer changes, and Task 3 covers review/release/commit requirements.
- Placeholder scan: no placeholder implementation steps remain.
- Type consistency: all model field names (`file_count`, `valid_row_count`,
  `row_count`, `candidate_count`, `valid_file_count`, `error_count`) match the
  current Pydantic models.
- Scope check: this is a focused human-readable renderer wording stage.
