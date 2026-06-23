# Stage 164 Cross-Lint Finding Count Grammar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make human-readable lint table finding-count labels consistent across source-pack, entity-pack, and community-signal lint surfaces.

**Architecture:** Add a small internal formatting helper in `src/fashion_radar/lint_formatting.py` and wire existing lint renderers to it. Keep JSON output, lint semantics, strict-mode behavior, and CLI command flow unchanged.

**Tech Stack:** Python standard library, existing lint renderers, pytest, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Create: `src/fashion_radar/lint_formatting.py`
  - Add `format_count_label(...)`.
  - Add `format_finding_counts(...)`.
- Modify: `src/fashion_radar/source_packs.py`
  - Import `format_finding_counts`.
  - Replace the local `_format_finding_count(...)` usage.
  - Remove the now-local-only `_format_finding_count(...)` helper.
- Modify: `src/fashion_radar/entity_packs.py`
  - Import `format_finding_counts`.
  - Use it in `render_entity_pack_lint_table(...)`.
- Modify: `src/fashion_radar/community_signals.py`
  - Import `format_finding_counts`.
  - Use it in `render_community_signal_lint_table(...)`.
  - Use it in `render_community_signal_directory_lint_table(...)` aggregate and per-file lines.
- Modify: `tests/test_entity_pack_lint.py`
  - Add direct renderer tests for singular and plural finding counts.
- Modify: `tests/test_community_signal_lint.py`
  - Add direct renderer tests for single-file singular and plural finding counts.
  - Add direct renderer tests for directory aggregate/per-file singular and plural finding counts.
- Modify: `docs/community-signal-quality.md`
  - Update user-facing example output from `1 errors` to `1 error` where finding counts are shown.
- Modify: `tests/test_cli_docs.py`
  - Add a focused docs assertion for singular one-finding examples in `docs/community-signal-quality.md`.
- Add: `docs/reviews/opencode-stage-164-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-164-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-164-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-164-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-164-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-164-release-review.md`

## Task 1: Add RED Tests For Entity-Pack Finding Count Grammar

**Files:**

- Modify: `tests/test_entity_pack_lint.py`

- [ ] **Step 1: Import direct result and finding models**

Change:

```python
from fashion_radar.entity_packs import (
    EntityPackFindingSeverity,
    lint_entity_pack,
    render_entity_pack_lint_table,
)
```

to:

```python
from fashion_radar.entity_packs import (
    EntityPackFinding,
    EntityPackFindingSeverity,
    EntityPackLintResult,
    lint_entity_pack,
    render_entity_pack_lint_table,
)
```

- [ ] **Step 2: Add singular entity-pack renderer test**

Add after `test_render_entity_pack_lint_table_includes_summary_and_findings(...)`:

```python
def test_render_entity_pack_lint_table_singularizes_one_finding_count() -> None:
    result = EntityPackLintResult(
        path="entities.yaml",
        entity_count=1,
        alias_count=1,
        type_counts={"brand": 1},
        findings=[
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )

    lines = render_entity_pack_lint_table(result)

    assert "Findings: 1 error, 1 warning, 1 info" in lines
```

Expected before implementation: this test fails because the renderer prints
`Findings: 1 errors, 1 warnings, 1 info`.

- [ ] **Step 3: Add plural entity-pack renderer test**

Add:

```python
def test_render_entity_pack_lint_table_keeps_plural_finding_counts() -> None:
    result = EntityPackLintResult(
        path="entities.yaml",
        entity_count=1,
        alias_count=1,
        type_counts={"brand": 1},
        findings=[
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_one",
                message="Error one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.ERROR,
                code="error_two",
                message="Error two.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_one",
                message="Warning one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.WARNING,
                code="warning_two",
                message="Warning two.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_one",
                message="Info one.",
            ),
            EntityPackFinding(
                severity=EntityPackFindingSeverity.INFO,
                code="info_two",
                message="Info two.",
            ),
        ],
    )

    lines = render_entity_pack_lint_table(result)

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines
```

Expected before implementation: this test passes today and protects the
non-one wording.

- [ ] **Step 4: Run entity-pack RED check**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_singularizes_one_finding_count \
  tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_keeps_plural_finding_counts \
  -q
```

Expected before implementation: singular test fails, plural test passes.

## Task 2: Add RED Tests For Community-Signal Finding Count Grammar

**Files:**

- Modify: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Import direct result models**

Change the import from `fashion_radar.community_signals` to include:

```python
    CommunitySignalDirectoryLintResult,
    CommunitySignalFinding,
    CommunitySignalLintResult,
```

The resulting import block should include these names alongside
`CommunitySignalFindingSeverity`, `lint_community_signal_directory`,
`lint_community_signal_file`, `render_community_signal_directory_lint_table`,
and `render_community_signal_lint_table`.

- [ ] **Step 2: Add singular community-signal file renderer test**

Add after `test_render_community_signal_lint_table_includes_summary_and_findings(...)`:

```python
def test_render_community_signal_lint_table_singularizes_one_finding_count() -> None:
    result = CommunitySignalLintResult(
        path="exports/signals.csv",
        input_format="csv",
        row_count=1,
        valid_row_count=0,
        findings=[
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )

    lines = render_community_signal_lint_table(result)

    assert "Findings: 1 error, 1 warning, 1 info" in lines
```

Expected before implementation: this test fails because the renderer prints
`Findings: 1 errors, 1 warnings, 1 info`.

- [ ] **Step 3: Add plural community-signal file renderer test**

Add:

```python
def test_render_community_signal_lint_table_keeps_plural_finding_counts() -> None:
    result = CommunitySignalLintResult(
        path="exports/signals.csv",
        input_format="csv",
        row_count=1,
        valid_row_count=0,
        findings=[
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="error_one",
                message="Error one.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="error_two",
                message="Error two.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="warning_one",
                message="Warning one.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="warning_two",
                message="Warning two.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="info_one",
                message="Info one.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="info_two",
                message="Info two.",
            ),
        ],
    )

    lines = render_community_signal_lint_table(result)

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines
```

Expected before implementation: this test passes today and protects the
non-one wording.

- [ ] **Step 4: Add singular directory aggregate/per-file renderer test**

Add after `test_render_community_signal_directory_lint_table_includes_aggregate_and_file_lines(...)`:

```python
def test_render_community_signal_directory_lint_table_singularizes_finding_counts() -> None:
    file_result = CommunitySignalLintResult(
        path="exports/signals.csv",
        input_format="csv",
        row_count=1,
        valid_row_count=0,
        findings=[
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.ERROR,
                code="error_code",
                message="Error message.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.WARNING,
                code="warning_code",
                message="Warning message.",
            ),
            CommunitySignalFinding(
                severity=CommunitySignalFindingSeverity.INFO,
                code="info_code",
                message="Info message.",
            ),
        ],
    )
    result = CommunitySignalDirectoryLintResult(
        directory="exports",
        input_format="csv",
        pattern="*.csv",
        file_count=1,
        row_count=1,
        valid_row_count=0,
        error_count=1,
        warning_count=1,
        info_count=1,
        files=[file_result],
    )

    lines = render_community_signal_directory_lint_table(result)

    file_line = next(line for line in lines if line.startswith("- exports/signals.csv:"))

    assert "Findings: 1 error, 1 warning, 1 info" in lines
    assert "1 error, 1 warning, 1 info" in file_line
```

Expected before implementation: this test fails on both assertions because the
renderer prints fixed plural labels.

- [ ] **Step 5: Add plural directory aggregate/per-file renderer test**

Add:

```python
def test_render_community_signal_directory_lint_table_keeps_plural_finding_counts() -> None:
    findings = [
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.ERROR,
            code="error_one",
            message="Error one.",
        ),
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.ERROR,
            code="error_two",
            message="Error two.",
        ),
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.WARNING,
            code="warning_one",
            message="Warning one.",
        ),
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.WARNING,
            code="warning_two",
            message="Warning two.",
        ),
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.INFO,
            code="info_one",
            message="Info one.",
        ),
        CommunitySignalFinding(
            severity=CommunitySignalFindingSeverity.INFO,
            code="info_two",
            message="Info two.",
        ),
    ]
    file_result = CommunitySignalLintResult(
        path="exports/signals.csv",
        input_format="csv",
        row_count=1,
        valid_row_count=0,
        findings=findings,
    )
    result = CommunitySignalDirectoryLintResult(
        directory="exports",
        input_format="csv",
        pattern="*.csv",
        file_count=1,
        row_count=1,
        valid_row_count=0,
        error_count=2,
        warning_count=2,
        info_count=2,
        files=[file_result],
    )

    lines = render_community_signal_directory_lint_table(result)

    file_line = next(line for line in lines if line.startswith("- exports/signals.csv:"))

    assert "Findings: 2 errors, 2 warnings, 2 info" in lines
    assert "2 errors, 2 warnings, 2 info" in file_line
```

Expected before implementation: this test passes today and protects the
non-one wording.

- [ ] **Step 6: Run community-signal RED check**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_signal_lint.py::test_render_community_signal_lint_table_singularizes_one_finding_count \
  tests/test_community_signal_lint.py::test_render_community_signal_lint_table_keeps_plural_finding_counts \
  tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts \
  tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_keeps_plural_finding_counts \
  -q
```

Expected before implementation: the singular file and directory tests fail;
the plural tests pass.

## Task 3: Implement Shared Finding Count Formatting

**Files:**

- Create: `src/fashion_radar/lint_formatting.py`
- Modify: `src/fashion_radar/source_packs.py`
- Modify: `src/fashion_radar/entity_packs.py`
- Modify: `src/fashion_radar/community_signals.py`

- [ ] **Step 1: Create the internal formatting helper**

Create `src/fashion_radar/lint_formatting.py`:

```python
from __future__ import annotations


def format_count_label(count: int, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"


def format_finding_counts(error_count: int, warning_count: int, info_count: int) -> str:
    return (
        f"{format_count_label(error_count, 'error', 'errors')}, "
        f"{format_count_label(warning_count, 'warning', 'warnings')}, "
        f"{format_count_label(info_count, 'info', 'info')}"
    )
```

- [ ] **Step 2: Wire source-pack renderer to the shared helper**

In `src/fashion_radar/source_packs.py`, add:

```python
from fashion_radar.lint_formatting import format_finding_counts
```

Replace the `Findings:` tuple with:

```python
f"Findings: {format_finding_counts(result.error_count, result.warning_count, result.info_count)}",
```

Remove the local `_format_finding_count(...)` helper at the bottom of the file.

- [ ] **Step 3: Wire entity-pack renderer to the shared helper**

In `src/fashion_radar/entity_packs.py`, add:

```python
from fashion_radar.lint_formatting import format_finding_counts
```

Replace the `Findings:` tuple with:

```python
f"Findings: {format_finding_counts(result.error_count, result.warning_count, result.info_count)}",
```

- [ ] **Step 4: Wire community-signal renderers to the shared helper**

In `src/fashion_radar/community_signals.py`, add:

```python
from fashion_radar.lint_formatting import format_finding_counts
```

Replace the single-file `Findings:` tuple with:

```python
f"Findings: {format_finding_counts(result.error_count, result.warning_count, result.info_count)}",
```

Replace the directory aggregate `Findings:` tuple with the same expression.

Replace the per-file finding-count suffix:

```python
f"{file.valid_row_count} import-ready, {file.error_count} errors, "
f"{file.warning_count} warnings, {file.info_count} info"
```

with:

```python
f"{file.valid_row_count} import-ready, "
f"{format_finding_counts(file.error_count, file.warning_count, file.info_count)}"
```

- [ ] **Step 5: Run focused GREEN tests**

Run the two focused RED commands from Task 1 Step 4 and Task 2 Step 6 again.

Expected after implementation: all six tests pass.

- [ ] **Step 6: Run broader renderer checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint or entity_pack_lint or community_signal_lint"
uv --no-config run --frozen ruff check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py
uv --no-config run --frozen ruff format --check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py
```

Expected after implementation: all listed tests and lint checks pass.

## Task 4: Update User-Facing Community Signal Docs

**Files:**

- Modify: `docs/community-signal-quality.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Update affected example lines**

Change:

```text
Findings: 1 errors, 3 warnings, 2 info
- exports/b.csv: 1 rows, 0 import-ready, 1 errors, 3 warnings, 2 info
```

to:

```text
Findings: 1 error, 3 warnings, 2 info
- exports/b.csv: 1 rows, 0 import-ready, 1 error, 3 warnings, 2 info
```

- [ ] **Step 2: Add docs grammar regression test**

Add to `tests/test_cli_docs.py`, near the other `COMMUNITY_SIGNAL_QUALITY_DOC`
assertions:

```python
def test_community_signal_quality_docs_use_singular_one_finding_count_examples() -> None:
    text = _read(COMMUNITY_SIGNAL_QUALITY_DOC)

    assert "Findings: 1 error, 3 warnings, 2 info" in text
    assert "Findings: 1 errors" not in text
    assert "0 import-ready, 1 error, 3 warnings, 2 info" in text
    assert "0 import-ready, 1 errors" not in text
```

Expected before docs update: this test fails because the docs still show
`1 errors`.

- [ ] **Step 3: Run docs checks**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples \
  -q
```

Expected after docs update: tests pass.

## Task 5: Code Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-164-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-164-code-review.md`
- Add: `docs/reviews/opencode-stage-164-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-164-release-review.md`

- [ ] **Step 1: Create and run code review**

Create `docs/reviews/opencode-stage-164-code-review-prompt.md` summarizing:

- Objective.
- Changed files.
- RED failure evidence.
- GREEN verification evidence.
- Scope boundaries.
- Review questions about shared helper use, source-pack regression risk,
  entity/community output, per-file directory rows, docs updates, and
  out-of-scope behavior.

Run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-164-code-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 164 Code Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-164-code-review.md
rm -f "$raw_review" "$clean_review"
```

Fix any critical or important findings before continuing.

- [ ] **Step 2: Run full release gate**

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

Expected: all checks pass; token scan and extraheader commands produce no
configured secret/header output.

- [ ] **Step 3: Create and run release review**

Create `docs/reviews/opencode-stage-164-release-review-prompt.md` summarizing:

- Objective.
- Changed files.
- RED/GREEN/code-review evidence.
- Full release gate evidence.
- Scope boundaries.

Run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-164-release-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 164 Release Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-164-release-review.md
rm -f "$raw_review" "$clean_review"
```

Fix any critical or important findings before continuing.

- [ ] **Step 4: Run final hygiene checks**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: release hygiene and diff checks pass; token scan and extraheader
commands produce no configured secret/header output.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add src/fashion_radar/lint_formatting.py \
  src/fashion_radar/source_packs.py \
  src/fashion_radar/entity_packs.py \
  src/fashion_radar/community_signals.py \
  tests/test_entity_pack_lint.py \
  tests/test_community_signal_lint.py \
  tests/test_cli_docs.py \
  docs/community-signal-quality.md \
  docs/superpowers/specs/2026-06-23-stage-164-cross-lint-finding-count-grammar-design.md \
  docs/superpowers/plans/2026-06-23-stage-164-cross-lint-finding-count-grammar-plan.md \
  docs/reviews/opencode-stage-164-plan-review-prompt.md \
  docs/reviews/opencode-stage-164-plan-review.md \
  docs/reviews/opencode-stage-164-code-review-prompt.md \
  docs/reviews/opencode-stage-164-code-review.md \
  docs/reviews/opencode-stage-164-release-review-prompt.md \
  docs/reviews/opencode-stage-164-release-review.md
git commit -m "fix: share lint finding count grammar"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

- [ ] **Step 6: Run post-push checks**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git config --get-all http.https://github.com/.extraheader
```

Expected:

- Local `main` and `origin/main` point at the same commit.
- Worktree is clean.
- No persistent GitHub extraheader is configured.
