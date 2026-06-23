# Stage 176 Source-Pack Quality Sample Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep `docs/source-pack-quality.md` table and JSON samples synchronized with current `source-pack-lint` output for the checked-in public source pack.

**Architecture:** Docs/test-only. Add focused Markdown extraction tests in `tests/test_source_pack_quality_docs.py`, using `lint_source_pack(...)` and `render_source_pack_lint_table(...)` as the source of truth. Update only the source-pack quality docs JSON sample so exact count fields and the clean `findings: []` list match runtime output.

**Tech Stack:** Python standard library `json`, pytest, Markdown, existing `fashion_radar.source_packs` helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_source_pack_quality_docs.py`
  - Add JSON/table fenced-block extraction helpers.
  - Add table sample parity test.
  - Add JSON sample parity test.
- Modify: `docs/source-pack-quality.md`
  - Expand `tag_counts` to current linter output.
  - Replace the synthetic warning finding with `findings: []`.
- Add: `docs/superpowers/specs/2026-06-24-stage-176-source-pack-quality-sample-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-176-source-pack-quality-sample-parity-plan.md`
- Add: `docs/reviews/opencode-stage-176-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-176-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-176-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-176-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-176-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-176-release-review.md`

## Task 1: Add RED Source-Pack Quality Docs Parity Tests

**Files:**

- Modify: `tests/test_source_pack_quality_docs.py`

- [ ] **Step 1: Add imports and public pack constant**

Change the import block from:

```python
from pathlib import Path
```

to:

```python
import json
from pathlib import Path
from typing import Any

from fashion_radar.source_packs import lint_source_pack, render_source_pack_lint_table
```

Then add this constant immediately after `SOURCE_PACK_QUALITY_DOC`:

```python
PUBLIC_SOURCE_PACK = ROOT / "configs" / "source-packs" / "fashion-public.example.yaml"
```

- [ ] **Step 2: Add fenced-block extraction helpers**

Add these helpers after `_normalized(...)`:

```python
def _fenced_block_after(text: str, marker: str, language: str) -> str:
    assert marker in text
    after_marker = text.split(marker, 1)[1]
    fence = f"```{language}"
    assert fence in after_marker
    after_fence = after_marker.split(fence, 1)[1]
    block, closing_fence, _ = after_fence.partition("```")
    assert closing_fence == "```"
    return block.strip()


def _source_pack_quality_table_sample() -> list[str]:
    block = _fenced_block_after(
        _read_source_pack_quality_doc(),
        "Table output starts with a compact summary:",
        "text",
    )
    return block.splitlines()


def _source_pack_quality_json_sample() -> dict[str, Any]:
    block = _fenced_block_after(
        _read_source_pack_quality_doc(),
        "JSON output contains the same information in a stable shape",
        "json",
    )
    payload = json.loads(block)
    assert isinstance(payload, dict)
    return payload
```

- [ ] **Step 3: Add the table sample parity test**

Add after `test_source_pack_quality_docs_keep_availability_and_demand_boundaries`:

```python
def test_source_pack_quality_table_sample_matches_public_pack_lint_prefix() -> None:
    sample_lines = _source_pack_quality_table_sample()
    relative_pack_path = PUBLIC_SOURCE_PACK.relative_to(ROOT)
    rendered_lines = render_source_pack_lint_table(lint_source_pack(relative_pack_path))

    assert sample_lines == rendered_lines[: len(sample_lines)]
```

This should already pass because the current table summary is in sync. It
guards future drift and intentionally uses the relative pack path so the
rendered path matches the documented CLI command and table sample.

- [ ] **Step 4: Add the JSON sample parity test**

Add after the table parity test:

```python
def test_source_pack_quality_json_sample_matches_public_pack_lint_output() -> None:
    payload = _source_pack_quality_json_sample()
    result = lint_source_pack(PUBLIC_SOURCE_PACK)
    documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()

    assert payload["path"] == documented_path
    assert payload["source_count"] == result.source_count
    assert payload["enabled_count"] == result.enabled_count
    assert payload["disabled_count"] == result.disabled_count
    assert payload["type_counts"] == result.type_counts
    assert payload["tag_counts"] == result.tag_counts
    assert payload["findings"] == []
    assert result.findings == []
```

- [ ] **Step 5: Run RED focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
```

Expected before docs update: the table parity test should pass because the
current table summary is already in sync, while the JSON parity test fails
because the current docs sample has abbreviated `tag_counts` and a synthetic
warning finding even though the current public pack has `findings: []`.

## Task 2: Sync `docs/source-pack-quality.md` JSON Sample

**Files:**

- Modify: `docs/source-pack-quality.md`

- [ ] **Step 1: Replace the JSON sample with current output**

Replace the current JSON block under `## JSON Output` with:

```json
{
  "path": "configs/source-packs/fashion-public.example.yaml",
  "source_count": 16,
  "enabled_count": 16,
  "disabled_count": 0,
  "type_counts": {
    "gdelt": 10,
    "rss": 6
  },
  "tag_counts": {
    "accessories": 1,
    "beauty": 1,
    "brand_news": 2,
    "celebrity_style": 2,
    "creative_directors": 1,
    "culture": 1,
    "designer_brands": 1,
    "emerging_designers": 1,
    "executive_moves": 1,
    "fashion_media": 2,
    "fashion_week": 1,
    "footwear": 1,
    "gdelt": 10,
    "industry_news": 5,
    "luxury": 2,
    "products": 1,
    "resale": 1,
    "retail": 2,
    "runway": 1,
    "shoes": 2,
    "streetwear": 2,
    "trade_media": 1
  },
  "findings": []
}
```

- [ ] **Step 2: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-176-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-176-code-review.md`
- Add: `docs/reviews/opencode-stage-176-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-176-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-176-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 176 implementation. The prompt
must require the response to start with:

```text
# Stage 176 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-176-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-176-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs, or
multiple drafts.

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

Create `docs/reviews/opencode-stage-176-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 176 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-176-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  docs/source-pack-quality.md \
  tests/test_source_pack_quality_docs.py \
  docs/superpowers/specs/2026-06-24-stage-176-source-pack-quality-sample-parity-design.md \
  docs/superpowers/plans/2026-06-24-stage-176-source-pack-quality-sample-parity-plan.md \
  docs/reviews/opencode-stage-176-plan-review-prompt.md \
  docs/reviews/opencode-stage-176-plan-review.md \
  docs/reviews/opencode-stage-176-code-review-prompt.md \
  docs/reviews/opencode-stage-176-code-review.md \
  docs/reviews/opencode-stage-176-release-review-prompt.md \
  docs/reviews/opencode-stage-176-release-review.md
git commit -m "docs: sync source pack quality samples"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the RED docs/runtime parity tests, Task 2 updates
  the source-pack quality docs JSON sample, and Task 3 covers review, release
  gate, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Type consistency: helpers use existing `Path`, `json`, `lint_source_pack`,
  and `render_source_pack_lint_table`; no new runtime types are introduced.
- Boundary check: runtime lint behavior, source config, collection, source
  acquisition, scraping, browser automation, platform APIs, monitoring,
  scheduling, demand proof, ranking, coverage verification, compliance-review
  product features, install hints, mirror hints, dependencies, and lockfiles
  remain out of scope.
