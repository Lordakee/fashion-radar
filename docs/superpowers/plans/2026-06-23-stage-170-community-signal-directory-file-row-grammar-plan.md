# Stage 170 Community Signal Directory File Row Grammar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix singular `1 row` wording in human-readable `community-signal-lint-dir` per-file lines.

**Architecture:** Tighten an existing renderer test in `tests/test_community_signal_lint.py`, update `src/fashion_radar/community_signals.py` to use the existing `format_count_label(...)` helper for the per-file row-count label, and sync the example output in `docs/community-signal-quality.md`. Keep lint behavior, structured models, JSON output, finding-count grammar, CLI flow, and top-level summary lines unchanged.

**Tech Stack:** Python standard library, existing Pydantic models, existing `lint_formatting` helpers, pytest, Markdown, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_community_signal_lint.py`
  - Tighten the existing singular finding-count renderer test to also assert the
    per-file line starts with `- exports/signals.csv: 1 row, 0 import-ready,`.
- Modify: `src/fashion_radar/community_signals.py`
  - Import `format_count_label` alongside `format_finding_counts`.
  - Use it only for the per-file `file.row_count` phrase in
    `render_community_signal_directory_lint_table(...)`.
- Modify: `docs/community-signal-quality.md`
  - Update the example output from `1 rows` to `1 row`.
- Add: `docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md`
- Add: `docs/reviews/opencode-stage-170-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-170-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-170-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-170-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-170-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-170-release-review.md`

## Task 1: Add RED Renderer/Docs Expectations

**Files:**

- Modify: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Tighten renderer test**

In `test_render_community_signal_directory_lint_table_singularizes_finding_counts(...)`,
after the existing `file_line` lookup, add:

```python
    assert file_line.startswith("- exports/signals.csv: 1 row, 0 import-ready, ")
```

Keep the existing finding-count assertions:

```python
    assert "Findings: 1 error, 1 warning, 1 info" in lines
    assert "1 error, 1 warning, 1 info" in file_line
```

- [ ] **Step 2: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q
```

Expected before implementation: fails because the file line starts with
`- exports/signals.csv: 1 rows, 0 import-ready, ...`.

## Task 2: Singularize Per-File Row Count And Sync Docs

**Files:**

- Modify: `src/fashion_radar/community_signals.py`
- Modify: `docs/community-signal-quality.md`

- [ ] **Step 1: Import helper**

Change:

```python
from fashion_radar.lint_formatting import format_finding_counts
```

to:

```python
from fashion_radar.lint_formatting import format_count_label, format_finding_counts
```

- [ ] **Step 2: Update per-file directory lint row phrase**

Change:

```python
                f"- {file.path}: {file.row_count} rows, "
```

to:

```python
                f"- {file.path}: {format_count_label(file.row_count, 'row', 'rows')}, "
```

- [ ] **Step 3: Update docs example**

In `docs/community-signal-quality.md`, change:

```text
- exports/b.csv: 1 rows, 0 import-ready, 1 error, 3 warnings, 2 info
```

to:

```text
- exports/b.csv: 1 row, 0 import-ready, 1 error, 3 warnings, 2 info
```

- [ ] **Step 4: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q
uv --no-config run --frozen pytest tests/test_community_signal_lint.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q
uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-170-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-170-code-review.md`
- Add: `docs/reviews/opencode-stage-170-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-170-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-170-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md`
- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`

The prompt must require the response to start with:

```text
# Stage 170 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-170-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-170-code-review.md
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

Create `docs/reviews/opencode-stage-170-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 170 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-170-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/community_signals.py \
  tests/test_community_signal_lint.py \
  docs/community-signal-quality.md \
  docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md \
  docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md \
  docs/reviews/opencode-stage-170-plan-review-prompt.md \
  docs/reviews/opencode-stage-170-plan-review.md \
  docs/reviews/opencode-stage-170-code-review-prompt.md \
  docs/reviews/opencode-stage-170-code-review.md \
  docs/reviews/opencode-stage-170-release-review-prompt.md \
  docs/reviews/opencode-stage-170-release-review.md
git commit -m "fix: singularize community signal file rows"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the RED renderer test, Task 2 covers source and
  docs updates, Task 3 covers review/release/commit requirements.
- Placeholder scan: no placeholder implementation steps remain.
- Type consistency: helper and test names are defined before use and match the
  code snippets.
- Scope check: this is a focused human-readable renderer and docs wording
  stage.
