# Stage 169 Manual Directory Dry-Run File Count Grammar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix singular `1 row` and `1 error` wording in human-readable `import-signals-dir --dry-run` per-file lines.

**Architecture:** Add one focused renderer test in `tests/test_manual_signal_import.py`, then use the existing `format_count_label(...)` helper in `src/fashion_radar/importers/manual_signals.py` for the per-file row and error-count phrases. Keep dry-run loading, structured models, JSON output, import behavior, CLI flow, and first-run smoke command shape unchanged.

**Tech Stack:** Python standard library, Pydantic model copies, pytest, existing `lint_formatting` helper, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_manual_signal_import.py`
  - Add one renderer test for singular `1 row, 1 error` wording in a per-file
    `import-signals-dir --dry-run` line.
- Modify: `src/fashion_radar/importers/manual_signals.py`
  - Import `format_count_label`.
  - Use it for the per-file `row_count` and `error_count` phrases in
    `render_manual_signal_directory_dry_run_table(...)`.
- Add: `docs/superpowers/specs/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-plan.md`
- Add: `docs/reviews/opencode-stage-169-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-169-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-169-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-169-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-169-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-169-release-review.md`

## Task 1: Add RED Renderer Test

**Files:**

- Modify: `tests/test_manual_signal_import.py`

- [ ] **Step 1: Add renderer test**

Add after `test_render_manual_signal_directory_dry_run_table_includes_summary_and_files(...)`:

```python
def test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels(
    tmp_path: Path,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Signal,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    result = dry_run_manual_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
        default_source_name="Fallback Source",
    )
    result = result.model_copy(
        update={
            "files": [
                result.files[0].model_copy(update={"row_count": 1, "error_count": 1})
            ]
        }
    )

    lines = render_manual_signal_directory_dry_run_table(result)
    file_line = next(line for line in lines if line.startswith(f"- {path}:"))

    assert file_line.endswith(": 1 row, 1 error")
```

- [ ] **Step 2: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import.py::test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels -q
```

Expected before implementation: fails because the file line ends with
`1 rows, 1 errors`.

## Task 2: Singularize Per-File Dry-Run Labels

**Files:**

- Modify: `src/fashion_radar/importers/manual_signals.py`

- [ ] **Step 1: Import helper**

Add in isort order with the existing `fashion_radar.*` imports:

```python
from fashion_radar.lint_formatting import format_count_label
```

- [ ] **Step 2: Update per-file dry-run renderer line**

Change:

```python
            lines.append(f"- {file.path}: {file.row_count} rows, {file.error_count} errors")
```

to:

```python
            lines.append(
                f"- {file.path}: "
                f"{format_count_label(file.row_count, 'row', 'rows')}, "
                f"{format_count_label(file.error_count, 'error', 'errors')}"
            )
```

- [ ] **Step 3: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_manual_signal_import.py::test_render_manual_signal_directory_dry_run_table_uses_singular_file_count_labels -q
uv --no-config run --frozen pytest tests/test_manual_signal_import.py -q
uv --no-config run --frozen ruff check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py
uv --no-config run --frozen ruff format --check src/fashion_radar/importers/manual_signals.py tests/test_manual_signal_import.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-169-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-169-code-review.md`
- Add: `docs/reviews/opencode-stage-169-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-169-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-169-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-plan.md`
- `src/fashion_radar/importers/manual_signals.py`
- `tests/test_manual_signal_import.py`

The prompt must require the response to start with:

```text
# Stage 169 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-169-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-169-code-review.md
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

Create `docs/reviews/opencode-stage-169-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 169 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-169-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/importers/manual_signals.py \
  tests/test_manual_signal_import.py \
  docs/superpowers/specs/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-design.md \
  docs/superpowers/plans/2026-06-23-stage-169-manual-directory-dry-run-file-count-grammar-plan.md \
  docs/reviews/opencode-stage-169-plan-review-prompt.md \
  docs/reviews/opencode-stage-169-plan-review.md \
  docs/reviews/opencode-stage-169-code-review-prompt.md \
  docs/reviews/opencode-stage-169-code-review.md \
  docs/reviews/opencode-stage-169-release-review-prompt.md \
  docs/reviews/opencode-stage-169-release-review.md
git commit -m "fix: singularize manual dry-run file counts"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers the RED renderer test, Task 2 covers the
  renderer implementation, Task 3 covers review/release/commit requirements.
- Placeholder scan: no placeholder implementation steps remain.
- Type consistency: helper and test names are defined before use and match the
  code snippets.
- Scope check: this is a focused human-readable renderer wording stage.
