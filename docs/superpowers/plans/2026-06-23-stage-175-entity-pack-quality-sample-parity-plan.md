# Stage 175 Entity-Pack Quality Sample Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep `docs/entity-pack-quality.md` table and JSON samples synchronized with current `entity-pack-lint` output for the checked-in starter watchlist pack.

**Architecture:** Docs/test-only. Add focused Markdown extraction tests in `tests/test_entity_pack_quality_docs.py`, using `lint_entity_pack(...)` and `render_entity_pack_lint_table(...)` as the source of truth. Update only the entity-pack quality docs sample so exact count fields match runtime output while the long findings list is clearly documented as an abbreviated representative excerpt.

**Tech Stack:** Python standard library `json`, pytest, Markdown, existing `fashion_radar.entity_packs` helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_entity_pack_quality_docs.py`
  - Add JSON/table fenced-block extraction helpers.
  - Add table sample parity test.
  - Add JSON count/finding sample parity test.
- Modify: `docs/entity-pack-quality.md`
  - Clarify that the JSON sample is an abbreviated representative excerpt from
    the checked-in starter watchlist pack.
  - Expand `tag_counts` and `category_tag_counts` to current linter output.
  - Replace the sample finding with the current first lint finding.
- Add: `docs/superpowers/specs/2026-06-23-stage-175-entity-pack-quality-sample-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-175-entity-pack-quality-sample-parity-plan.md`
- Add: `docs/reviews/opencode-stage-175-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-175-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-175-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-175-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-175-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-175-release-review.md`

## Task 1: Add RED Entity-Pack Quality Docs Parity Tests

**Files:**

- Modify: `tests/test_entity_pack_quality_docs.py`

- [ ] **Step 1: Add imports and starter pack constant**

Change the import block from:

```python
from pathlib import Path
```

to:

```python
import json
from pathlib import Path
from typing import Any

from fashion_radar.entity_packs import lint_entity_pack, render_entity_pack_lint_table
```

Then add this constant immediately after `ENTITY_PACK_QUALITY_DOC`:

```python
WATCHLIST_ENTITY_PACK = (
    ROOT / "configs" / "entity-packs" / "fashion-watchlist.example.yaml"
)
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


def _entity_pack_quality_table_sample() -> list[str]:
    block = _fenced_block_after(
        _read_entity_pack_quality_doc(),
        "Table output starts with a compact summary:",
        "text",
    )
    return block.splitlines()


def _entity_pack_quality_json_sample() -> dict[str, Any]:
    block = _fenced_block_after(
        _read_entity_pack_quality_doc(),
        "JSON output contains the same information in a stable shape",
        "json",
    )
    payload = json.loads(block)
    assert isinstance(payload, dict)
    return payload


def _json_ready_first_finding(result: object) -> dict[str, Any]:
    assert hasattr(result, "findings")
    assert result.findings
    payload = json.loads(result.findings[0].model_dump_json())
    assert isinstance(payload, dict)
    return payload
```

- [ ] **Step 3: Add the table sample parity test**

Add after `test_entity_pack_quality_docs_keep_non_claim_boundary`:

```python
def test_entity_pack_quality_table_sample_matches_watchlist_lint_prefix() -> None:
    sample_lines = _entity_pack_quality_table_sample()
    relative_pack_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT)
    rendered_lines = render_entity_pack_lint_table(lint_entity_pack(relative_pack_path))

    assert sample_lines == rendered_lines[: len(sample_lines)]
```

This may already pass because the current table summary is in sync, but it
guards future drift. The test intentionally passes the relative pack path into
`lint_entity_pack(...)` because the documented CLI command and table sample
print `configs/entity-packs/fashion-watchlist.example.yaml`, not an absolute
workspace path.

- [ ] **Step 4: Add the JSON sample parity test**

Add after the table parity test:

```python
def test_entity_pack_quality_json_sample_matches_watchlist_lint_counts() -> None:
    payload = _entity_pack_quality_json_sample()
    result = lint_entity_pack(WATCHLIST_ENTITY_PACK)
    documented_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT).as_posix()

    assert payload["path"] == documented_path
    assert payload["entity_count"] == result.entity_count
    assert payload["alias_count"] == result.alias_count
    assert payload["type_counts"] == result.type_counts
    assert payload["tag_counts"] == result.tag_counts
    assert payload["category_tag_counts"] == result.category_tag_counts
    assert (
        payload["accepted_without_context_aliases"]
        == result.accepted_without_context_aliases
    )
    assert payload["context_gated_aliases"] == result.context_gated_aliases
    assert payload["safe_aliases"] == result.safe_aliases
    assert (
        payload["product_parent_gated_aliases"]
        == result.product_parent_gated_aliases
    )
    assert [finding["severity"] for finding in payload["findings"]] == ["warning"]
    assert payload["findings"][0] == _json_ready_first_finding(result)

    normalized = _normalized(_read_entity_pack_quality_doc())
    assert "abbreviated representative excerpt" in normalized
    assert "not the full findings list" in normalized
```

- [ ] **Step 5: Run RED focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py::test_entity_pack_quality_json_sample_matches_watchlist_lint_counts -q
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
```

Expected before docs update: the table parity test should pass because the
current table summary is already in sync, while the JSON parity test fails
because the current docs sample has abbreviated `tag_counts` /
`category_tag_counts`, a non-current first finding, and no explicit
`abbreviated representative excerpt` / `not the full findings list` wording.

## Task 2: Sync `docs/entity-pack-quality.md` Samples

**Files:**

- Modify: `docs/entity-pack-quality.md`

- [ ] **Step 1: Clarify JSON sample scope**

Replace:

```markdown
JSON output contains the same information in a stable shape:
```

with:

```markdown
JSON output contains the same information in a stable shape. The example below
is an abbreviated representative excerpt from the checked-in starter watchlist
pack: scalar counts and count maps match current lint output, while `findings`
shows one representative finding rather than the full findings list:
```

- [ ] **Step 2: Replace the JSON sample with current counts and representative first finding**

Replace the current JSON block under `## JSON Output` with:

```json
{
  "path": "configs/entity-packs/fashion-watchlist.example.yaml",
  "entity_count": 28,
  "alias_count": 45,
  "type_counts": {
    "brand": 10,
    "category": 5,
    "celebrity": 2,
    "designer": 2,
    "product": 6,
    "trend": 3
  },
  "tag_counts": {
    "accessories": 2,
    "aesthetic": 3,
    "american_fashion": 1,
    "celebrity_style": 2,
    "consumer_trend": 1,
    "contemporary_luxury": 2,
    "creative_director": 2,
    "designer_brand": 9,
    "luxury": 4,
    "lvmh": 1,
    "minimalism": 2,
    "new_york": 1,
    "prada_group": 1,
    "red_carpet": 1,
    "street_style": 1,
    "styling": 2
  },
  "category_tag_counts": {
    "bag": 6,
    "flats": 2,
    "handbag": 4,
    "mule": 1,
    "shoe": 1,
    "shoes": 4,
    "shoulder_bag": 1,
    "sneakers": 1,
    "tote": 2
  },
  "accepted_without_context_aliases": 22,
  "context_gated_aliases": 4,
  "safe_aliases": 7,
  "product_parent_gated_aliases": 12,
  "findings": [
    {
      "severity": "warning",
      "code": "context_terms_no_effect",
      "message": "Entity has context_terms, but none of its aliases consult context under current matcher rules.",
      "entity_name": "Boat Shoes",
      "alias": null,
      "field": "context_terms"
    }
  ]
}
```

- [ ] **Step 3: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py::test_entity_pack_quality_json_sample_matches_watchlist_lint_counts -q
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-175-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-175-code-review.md`
- Add: `docs/reviews/opencode-stage-175-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-175-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-175-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 175 implementation. The prompt
must require the response to start with:

```text
# Stage 175 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-175-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-175-code-review.md
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

Create `docs/reviews/opencode-stage-175-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 175 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-175-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  docs/entity-pack-quality.md \
  tests/test_entity_pack_quality_docs.py \
  docs/superpowers/specs/2026-06-23-stage-175-entity-pack-quality-sample-parity-design.md \
  docs/superpowers/plans/2026-06-23-stage-175-entity-pack-quality-sample-parity-plan.md \
  docs/reviews/opencode-stage-175-plan-review-prompt.md \
  docs/reviews/opencode-stage-175-plan-review.md \
  docs/reviews/opencode-stage-175-code-review-prompt.md \
  docs/reviews/opencode-stage-175-code-review.md \
  docs/reviews/opencode-stage-175-release-review-prompt.md \
  docs/reviews/opencode-stage-175-release-review.md
git commit -m "docs: sync entity pack quality samples"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the RED docs/runtime parity tests, Task 2 updates
  the entity-pack quality docs sample, and Task 3 covers review, release gate,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Type consistency: helpers use existing `Path`, `json`, `lint_entity_pack`,
  and `render_entity_pack_lint_table`; no new runtime types are introduced.
- Boundary check: runtime lint behavior, entity config, matching, scoring,
  source acquisition, social/community connectors, scraping, browser automation,
  platform APIs, monitoring, scheduling, demand proof, ranking, coverage
  verification, compliance-review product features, install hints, mirror
  hints, dependencies, and lockfiles remain out of scope.
