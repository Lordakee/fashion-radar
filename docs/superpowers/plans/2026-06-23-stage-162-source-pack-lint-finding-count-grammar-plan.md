# Stage 162 Source-Pack Lint Finding Count Grammar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `source-pack-lint` human table summary use singular labels for exactly one finding and plural labels otherwise.

**Architecture:** Keep the grammar helper local to `src/fashion_radar/source_packs.py` and use it only in `render_source_pack_lint_table(...)`. Keep source-pack lint data models, JSON output, validation behavior, strict-mode behavior, and CLI command flow unchanged.

**Tech Stack:** Python, existing source-pack lint renderer, pytest, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `src/fashion_radar/source_packs.py`
  - Add `_format_finding_count(...)`.
  - Use it in `render_source_pack_lint_table(...)`.
- Modify: `tests/test_source_packs.py`
  - Update the Stage 161 empty-tag test to expect `1 warning`.
  - Add direct renderer coverage for one finding per severity.
  - Add direct renderer coverage for plural non-one counts.
- Add: `docs/reviews/opencode-stage-162-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-162-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-162-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-162-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-162-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-162-release-review.md`

## Task 1: Add RED Tests For Source-Pack Finding Count Grammar

**Files:**

- Modify: `tests/test_source_packs.py`

- [ ] **Step 1: Import direct result/finding models**

Change the existing import block to include `SourcePackFinding` and
`SourcePackLintResult`:

```python
from fashion_radar.source_packs import (
    SourcePackFinding,
    SourcePackFindingSeverity,
    SourcePackLintResult,
    lint_source_pack,
    normalize_source_target,
    render_source_pack_lint_table,
)
```

- [ ] **Step 2: Update source-pack single-warning expectation**

In
`tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts`,
change:

```python
"Findings: 0 errors, 1 warnings, 0 info",
```

to:

```python
"Findings: 0 errors, 1 warning, 0 info",
```

Expected before implementation: this test fails because the renderer still
prints `1 warnings`.

- [ ] **Step 3: Add singular count coverage**

Add after `test_render_source_pack_lint_table_shows_none_for_empty_tag_counts`:

```python
def test_render_source_pack_lint_table_singularizes_one_finding_count() -> None:
    result = SourcePackLintResult(
        path="sources.yaml",
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"gdelt": 1},
        tag_counts={"gdelt": 1},
        findings=[
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )

    lines = render_source_pack_lint_table(result)

    assert "Findings: 1 error, 1 warning, 1 info" in lines
```

Expected before implementation: this test fails because the renderer prints
`Findings: 1 errors, 1 warnings, 1 info`.

- [ ] **Step 4: Add plural regression coverage**

Add:

```python
def test_render_source_pack_lint_table_keeps_plural_finding_counts() -> None:
    result = SourcePackLintResult(
        path="sources.yaml",
        source_count=1,
        enabled_count=1,
        disabled_count=0,
        type_counts={"gdelt": 1},
        tag_counts={"gdelt": 1},
        findings=[
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_one",
                message="Error one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.ERROR,
                code="error_two",
                message="Error two.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_one",
                message="Warning one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.WARNING,
                code="warning_two",
                message="Warning two.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_one",
                message="Info one.",
            ),
            SourcePackFinding(
                severity=SourcePackFindingSeverity.INFO,
                code="info_two",
                message="Info two.",
            ),
        ],
    )

    lines = render_source_pack_lint_table(result)

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines
```

Expected before implementation: this test passes today for plural counts and
protects the existing non-one wording after implementation.

- [ ] **Step 5: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts \
  tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count \
  tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts \
  -q
```

Expected before implementation: the single-warning and one-of-each tests fail;
the plural regression test passes.

## Task 2: Implement Source-Pack Finding Count Grammar

**Files:**

- Modify: `src/fashion_radar/source_packs.py`

- [ ] **Step 1: Add `_format_finding_count(...)`**

Add near `_format_counts(...)`:

```python
def _format_finding_count(count: int, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"
```

- [ ] **Step 2: Update the source-pack `Findings:` summary**

Replace the fixed `Findings:` tuple in `render_source_pack_lint_table(...)`:

```python
(
    f"Findings: {result.error_count} errors, {result.warning_count} warnings, "
    f"{result.info_count} info"
),
```

with:

```python
(
    "Findings: "
    f"{_format_finding_count(result.error_count, 'error', 'errors')}, "
    f"{_format_finding_count(result.warning_count, 'warning', 'warnings')}, "
    f"{_format_finding_count(result.info_count, 'info', 'info')}"
),
```

This keeps `0 info`, `1 info`, and `2 info`, matching current product wording.

- [ ] **Step 3: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts \
  tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts \
  tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count \
  tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts \
  tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack \
  -q
```

Expected after implementation: all focused tests pass.

- [ ] **Step 4: Run Stage 162 focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint"
uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py
```

Expected: source-pack tests, docs boundary tests, CLI source-pack lint tests,
lint, and format checks pass.

## Task 3: Local Code Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-162-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-162-code-review.md`
- Add: `docs/reviews/opencode-stage-162-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-162-release-review.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-162-code-review-prompt.md` with:

````markdown
# Stage 162 Code Review Prompt

Review the Stage 162 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 162 Code Review
```

Changed files:

- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- Stage 162 design, plan, and plan review artifacts.

Objective:

Make the `source-pack-lint` human table summary use singular labels for exactly
one finding and plural labels otherwise.

Review questions:

1. Does source-pack table output now render `1 error`, `1 warning`, and
   `1 info` while preserving `0 errors`, `0 warnings`, and `0 info`?
2. Are source-pack JSON output, lint semantics, strict-mode behavior, and CLI
   command flow unchanged?
3. Are tests sufficient and scoped to source-pack lint output?
4. Are entity-pack and community-signal lint outputs intentionally untouched?
5. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
````

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-162-code-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 162 Code Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-162-code-review.md
rm -f "$raw_review" "$clean_review"
```

Expected: no critical or important findings. If any appear, fix and request
rereview before continuing.

- [ ] **Step 3: Run full release gate**

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

Expected: checks pass. `rg` and extraheader commands exit 1 with no output when
clean.

- [ ] **Step 4: Run local opencode release review**

Create `docs/reviews/opencode-stage-162-release-review-prompt.md` summarizing
the Stage 162 changes and full release-gate results. Then run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-162-release-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 162 Release Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-162-release-review.md
rm -f "$raw_review" "$clean_review"
```

Expected: no critical or important findings.

- [ ] **Step 5: Re-run release hygiene after release review**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: Stage 162 review artifacts pass release hygiene.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add src/fashion_radar/source_packs.py tests/test_source_packs.py \
  docs/superpowers/specs/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-design.md \
  docs/superpowers/plans/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-plan.md \
  docs/reviews/opencode-stage-162-plan-review-prompt.md \
  docs/reviews/opencode-stage-162-plan-review.md \
  docs/reviews/opencode-stage-162-code-review-prompt.md \
  docs/reviews/opencode-stage-162-code-review.md \
  docs/reviews/opencode-stage-162-release-review-prompt.md \
  docs/reviews/opencode-stage-162-release-review.md
git commit -m "fix: singularize source-pack lint finding counts"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

Expected: commit succeeds and push updates `origin/main`.

## Self-Review Notes

- Spec coverage: plan covers source-pack table grammar only, including singular
  and plural cases.
- Placeholder scan: no `TBD`, `TODO`, or vague implementation steps remain.
- Type consistency: helper name and renderer references match the design.
