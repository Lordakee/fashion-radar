# Stage 161 Source-Pack Lint Tag Counts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic source tag counts to the default human `source-pack-lint` table output.

**Architecture:** Keep source-pack lint data unchanged. Reuse the existing `tag_counts` field already computed by `lint_source_pack(...)` and render it in `render_source_pack_lint_table(...)` immediately after `Types:`. The CLI already delegates table rendering to that function, so no command-layer behavior change is needed.

**Tech Stack:** Python, existing Typer CLI, pytest, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `src/fashion_radar/source_packs.py`
  - Add `Tags: ...` to `render_source_pack_lint_table(...)`.
- Modify: `tests/test_source_packs.py`
  - Import `render_source_pack_lint_table`.
  - Add a focused renderer test for deterministic tag counts.
- Modify: `tests/test_cli.py`
  - Strengthen the public-pack CLI table smoke to assert `Tags:` is printed.
- Modify: `docs/source-pack-quality.md`
  - Add `Tags:` to the table output example.
  - Add a summary bullet explaining tag counts.
- Add: `docs/reviews/opencode-stage-161-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-161-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-161-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-161-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-161-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-161-release-review.md`

## Task 1: Add RED Tests For Tag Counts In Human Output

**Files:**

- Modify: `tests/test_source_packs.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Import the renderer in `tests/test_source_packs.py`**

Change the import block to include `render_source_pack_lint_table`:

```python
from fashion_radar.source_packs import (
    SourcePackFindingSeverity,
    lint_source_pack,
    normalize_source_target,
    render_source_pack_lint_table,
)
```

- [ ] **Step 2: Add the focused table renderer test**

Add this test after `test_lint_result_json_shape_is_stable(...)`:

```python
def test_render_source_pack_lint_table_includes_tag_counts(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Runway
            type: gdelt
            query: runway
            weight: 0.8
            tags: [gdelt, runway]
          - name: GDELT Shoes
            type: gdelt
            query: shoes
            weight: 0.8
            tags: [gdelt, shoes]
        """,
    )

    result = lint_source_pack(path)
    lines = render_source_pack_lint_table(result)

    assert lines[:5] == [
        f"Source pack: {path}",
        "Sources: 2 total, 2 enabled, 0 disabled",
        "Types: gdelt=2",
        "Tags: gdelt=2, runway=1, shoes=1",
        "Findings: 0 errors, 0 warnings, 0 info",
    ]
    assert "No source-pack quality findings." in lines
```

Expected before implementation: this test fails because the current renderer
prints `Findings:` immediately after `Types:` and has no `Tags:` line.

- [ ] **Step 3: Strengthen the CLI table smoke**

In `tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack`, add:

```python
assert "Tags:" in result.output
```

Expected before implementation: this assertion fails because the current CLI
table output has no `Tags:` line.

- [ ] **Step 4: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
```

Expected before implementation: both tests fail for the missing `Tags:` line.

## Task 2: Render Tag Counts And Update Docs

**Files:**

- Modify: `src/fashion_radar/source_packs.py`
- Modify: `docs/source-pack-quality.md`

- [ ] **Step 1: Add the `Tags:` line in the renderer**

In `render_source_pack_lint_table(...)`, insert this line immediately after the
existing `Types:` line:

```python
f"Tags: {_format_counts(result.tag_counts)}",
```

The resulting summary list should start:

```python
lines = [
    f"Source pack: {result.path}",
    (
        f"Sources: {result.source_count} total, {result.enabled_count} enabled, "
        f"{result.disabled_count} disabled"
    ),
    f"Types: {_format_counts(result.type_counts)}",
    f"Tags: {_format_counts(result.tag_counts)}",
    (
        f"Findings: {result.error_count} errors, {result.warning_count} warnings, "
        f"{result.info_count} info"
    ),
]
```

- [ ] **Step 2: Update the docs table sample**

In `docs/source-pack-quality.md`, update the sample under `## Table Output` to
include the current public-pack tag count line:

```text
Source pack: configs/source-packs/fashion-public.example.yaml
Sources: 16 total, 16 enabled, 0 disabled
Types: gdelt=10, rss=6
Tags: accessories=1, beauty=1, brand_news=2, celebrity_style=2, creative_directors=1, culture=1, designer_brands=1, emerging_designers=1, executive_moves=1, fashion_media=2, fashion_week=1, footwear=1, gdelt=10, industry_news=5, luxury=2, products=1, resale=1, retail=2, runway=1, shoes=2, streetwear=2, trade_media=1
Findings: 0 errors, 0 warnings, 0 info
No source-pack quality findings.
```

- [ ] **Step 3: Add a summary bullet for `Tags`**

In the summary bullet list in `docs/source-pack-quality.md`, add:

```markdown
- `Tags`: source counts by configured source tag.
```

Place it after the `Types` bullet and before the `Findings` bullet.

- [ ] **Step 4: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
```

Expected after implementation: both tests pass.

- [ ] **Step 5: Run Stage 161 focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_cli.py -k "source_pack_lint" -q
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py tests/test_source_packs.py tests/test_cli.py -k "source_pack" -q
uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
```

Expected: focused tests, docs boundary tests, lint, and format checks pass.

## Task 3: Local Code Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-161-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-161-code-review.md`
- Add: `docs/reviews/opencode-stage-161-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-161-release-review.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-161-code-review-prompt.md` with:

````markdown
# Stage 161 Code Review Prompt

Review the Stage 161 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 161 Code Review
```

Changed files:

- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- `tests/test_cli.py`
- `docs/source-pack-quality.md`
- `docs/superpowers/specs/2026-06-23-stage-161-source-pack-lint-tag-counts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-161-source-pack-lint-tag-counts-plan.md`
- `docs/reviews/opencode-stage-161-plan-review-prompt.md`
- `docs/reviews/opencode-stage-161-plan-review.md`

Objective:

Show deterministic source tag counts in the default human table output from
`fashion-radar source-pack-lint`.

Review questions:

1. Does the renderer reuse existing `tag_counts` and `_format_counts(...)`?
2. Does the CLI table output include `Tags:` without changing JSON shape?
3. Are tests sufficient and scoped to source-pack lint output?
4. Does the docs update preserve local/read-only and non-data boundaries?
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
  "$(cat docs/reviews/opencode-stage-161-code-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 161 Code Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-161-code-review.md
rm -f "$raw_review" "$clean_review"
```

Expected: no critical or important findings. If any appear, fix and request
rereview before continuing.

- [ ] **Step 3: Run the full release gate**

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

Expected: tests and checks pass. `rg` exits 1 with no output when no token is
found; `git config --get-all ...extraheader` exits 1 with no output when no
persistent header is configured.

- [ ] **Step 4: Run local opencode release review**

Create `docs/reviews/opencode-stage-161-release-review-prompt.md` summarizing
the Stage 161 changes and fresh release-gate results. Then run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-161-release-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 161 Release Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-161-release-review.md
rm -f "$raw_review" "$clean_review"
```

Expected: no critical or important findings.

- [ ] **Step 5: Re-run release hygiene after release review**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: the Stage 161 review artifacts pass release hygiene.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py \
  docs/source-pack-quality.md \
  docs/superpowers/specs/2026-06-23-stage-161-source-pack-lint-tag-counts-design.md \
  docs/superpowers/plans/2026-06-23-stage-161-source-pack-lint-tag-counts-plan.md \
  docs/reviews/opencode-stage-161-plan-review-prompt.md \
  docs/reviews/opencode-stage-161-plan-review.md \
  docs/reviews/opencode-stage-161-code-review-prompt.md \
  docs/reviews/opencode-stage-161-code-review.md \
  docs/reviews/opencode-stage-161-release-review-prompt.md \
  docs/reviews/opencode-stage-161-release-review.md
git commit -m "feat: show source pack tag counts"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

Expected: commit succeeds and push updates `origin/main`.

## Self-Review Notes

- Spec coverage: plan covers table renderer, CLI output, docs, focused tests,
  code review, release review, release hygiene, commit, and push.
- Placeholder scan: no `TBD`, `TODO`, or vague implementation steps remain.
- Type consistency: `tag_counts`, `_format_counts`, and
  `render_source_pack_lint_table` names match existing code.
