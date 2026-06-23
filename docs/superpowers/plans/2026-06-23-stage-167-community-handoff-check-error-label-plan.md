# Stage 167 Community Handoff Check Error Label Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix singular `1 error` wording in the human-readable `community-handoff-check-dir` table.

**Architecture:** Add one focused renderer test in `tests/test_community_handoff_check.py`, then use the existing `format_count_label(...)` helper in `src/fashion_radar/community_handoff_check.py` for the two error-count phrases. Keep structured result behavior and JSON output unchanged.

**Tech Stack:** Python standard library, Pydantic model copies, pytest, existing `lint_formatting` helper, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_community_handoff_check.py`
  - Add one renderer test for singular `1 error` wording in lint and import
    dry-run summary lines.
- Modify: `src/fashion_radar/community_handoff_check.py`
  - Import `format_count_label`.
  - Use it for the lint and import dry-run error-count phrases.
- Add: `docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md`
- Add: `docs/reviews/opencode-stage-167-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-167-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-167-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-167-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-167-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-167-release-review.md`

## Task 1: Add RED Renderer Test

**Files:**

- Modify: `tests/test_community_handoff_check.py`

- [ ] **Step 1: Add renderer test**

Add after `test_render_community_handoff_directory_check_table_sanitizes_cells(...)`:

```python
def test_render_community_handoff_directory_check_table_uses_singular_error_label(
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
    result = result.model_copy(
        update={
            "community_signal_lint": result.community_signal_lint.model_copy(
                update={"error_count": 1}
            ),
            "import_dry_run": result.import_dry_run.model_copy(update={"error_count": 1}),
        }
    )

    lines = render_community_handoff_directory_check_table(result)
    lint_line = next(line for line in lines if line.startswith("Lint: "))
    import_line = next(line for line in lines if line.startswith("Import dry-run: "))

    assert lint_line.endswith(", 1 error")
    assert import_line.endswith(", 1 error")
```

- [ ] **Step 2: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
```

Expected before implementation: fails because both lines end with `1 errors`.

## Task 2: Singularize Community Handoff Error Labels

**Files:**

- Modify: `src/fashion_radar/community_handoff_check.py`

- [ ] **Step 1: Import helper**

Add:

```python
from fashion_radar.lint_formatting import format_count_label
```

- [ ] **Step 2: Update lint summary error phrase**

Change:

```python
            f"{result.community_signal_lint.error_count} errors"
```

to:

```python
            f"{format_count_label(result.community_signal_lint.error_count, 'error', 'errors')}"
```

- [ ] **Step 3: Update import dry-run summary error phrase**

Change:

```python
            f"{result.import_dry_run.error_count} errors"
```

to:

```python
            f"{format_count_label(result.import_dry_run.error_count, 'error', 'errors')}"
```

- [ ] **Step 4: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_handoff_check.py::test_render_community_handoff_directory_check_table_uses_singular_error_label -q
uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q
uv --no-config run --frozen ruff check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-167-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-167-code-review.md`
- Add: `docs/reviews/opencode-stage-167-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-167-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-167-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md`
- `docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md`
- `src/fashion_radar/community_handoff_check.py`
- `tests/test_community_handoff_check.py`

The prompt must require the response to start with:

```text
# Stage 167 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-167-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-167-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Fix
any critical or important findings before continuing.

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

Create `docs/reviews/opencode-stage-167-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 167 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-167-release-review.md`.

Expected: completed review output with no critical or important findings.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  src/fashion_radar/community_handoff_check.py \
  tests/test_community_handoff_check.py \
  docs/superpowers/specs/2026-06-23-stage-167-community-handoff-check-error-label-design.md \
  docs/superpowers/plans/2026-06-23-stage-167-community-handoff-check-error-label-plan.md \
  docs/reviews/opencode-stage-167-plan-review-prompt.md \
  docs/reviews/opencode-stage-167-plan-review.md \
  docs/reviews/opencode-stage-167-code-review-prompt.md \
  docs/reviews/opencode-stage-167-code-review.md \
  docs/reviews/opencode-stage-167-release-review-prompt.md \
  docs/reviews/opencode-stage-167-release-review.md
git commit -m "fix: singularize handoff check error labels"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.
