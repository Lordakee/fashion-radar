# Stage 168 Source Pack Public GDELT Doc Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep `docs/source-packs.md` synchronized with the checked-in public source pack's GDELT lanes and source-pack lint count example.

**Architecture:** Add focused documentation drift tests in `tests/test_source_packs_docs.py`, then update `docs/source-packs.md` to list the exact public-pack GDELT source names and current lint count JSON example. This is docs/test-only and does not change pack config, CLI, linter, collectors, or runtime behavior.

**Tech Stack:** Python standard library `json`, PyYAML via existing project dependency, `fashion_radar.source_packs.lint_source_pack`, pytest, Markdown, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_source_packs_docs.py`
  - Add helpers for reading the public pack and extracting the docs JSON
    example.
  - Add tests that require each GDELT source name to appear in the docs and
    require the example JSON count fields to match `lint_source_pack(...)`.
- Modify: `docs/source-packs.md`
  - Expand the example `tag_counts` object to current linter output.
  - Replace the abbreviated four-item GDELT theme list with all 10 exact
    current GDELT source names plus concise descriptions.
- Add: `docs/superpowers/specs/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-plan.md`
- Add: `docs/reviews/opencode-stage-168-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-168-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-168-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-168-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-168-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-168-release-review.md`

## Task 1: Add RED Documentation Drift Tests

**Files:**

- Modify: `tests/test_source_packs_docs.py`

- [ ] **Step 1: Add imports and public pack path**

Change the top of `tests/test_source_packs_docs.py` from:

```python
from pathlib import Path
```

to:

```python
import json
from pathlib import Path

import yaml

from fashion_radar.source_packs import lint_source_pack
```

Then add:

```python
PUBLIC_SOURCE_PACK = ROOT / "configs" / "source-packs" / "fashion-public.example.yaml"
```

immediately after `SOURCE_PACKS_DOC = ROOT / "docs" / "source-packs.md"`.

- [ ] **Step 2: Add local helper functions**

Add these helpers after `_section(...)`:

```python
def _json_block_after(text: str, marker: str) -> dict[str, object]:
    assert marker in text
    after_marker = text.split(marker, 1)[1]
    assert "```json" in after_marker
    block = after_marker.split("```json", 1)[1].split("```", 1)[0]
    return json.loads(block)


def _public_pack_gdelt_source_names() -> list[str]:
    payload = yaml.safe_load(PUBLIC_SOURCE_PACK.read_text(encoding="utf-8"))
    sources = payload["sources"]
    return [
        str(source["name"])
        for source in sources
        if source.get("type") == "gdelt"
    ]
```

- [ ] **Step 3: Add GDELT lane name drift test**

Add after `test_source_packs_docs_keep_public_pack_source_boundary(...)`:

```python
def test_source_packs_docs_list_current_public_pack_gdelt_lanes() -> None:
    section = _section(_read_source_packs_doc(), "GDELT Queries")

    for source_name in _public_pack_gdelt_source_names():
        assert f"`{source_name}`" in section

    assert "Scores only reflect the configured source set." in section
```

- [ ] **Step 4: Add source-pack lint example drift test**

Add after the GDELT lane test:

```python
def test_source_packs_docs_example_json_matches_public_pack_lint_counts() -> None:
    example = _json_block_after(_read_source_packs_doc(), "Example JSON shape:")
    result = lint_source_pack(PUBLIC_SOURCE_PACK)

    assert example["source_count"] == result.source_count
    assert example["enabled_count"] == result.enabled_count
    assert example["disabled_count"] == result.disabled_count
    assert example["type_counts"] == result.type_counts
    assert example["tag_counts"] == result.tag_counts
    assert example["findings"] == []
```

- [ ] **Step 5: Run RED focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
```

Expected before doc update: fails because the current "GDELT Queries" section
does not list all 10 exact GDELT source names and the example `tag_counts` is
abbreviated.

## Task 2: Sync `docs/source-packs.md`

**Files:**

- Modify: `docs/source-packs.md`

- [ ] **Step 1: Expand the example JSON `tag_counts`**

Replace the current abbreviated `tag_counts` object:

```json
  "tag_counts": {
    "industry_news": 5,
    "gdelt": 10
  },
```

with:

```json
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
```

- [ ] **Step 2: Replace the abbreviated GDELT query list**

Replace the current "GDELT Queries" text:

```markdown
The GDELT entries are broad starter queries for:

- luxury/designer fashion
- celebrity style/red carpet
- bags/shoes/products
- emerging designers

Tune the query strings, `max_records`, and source weights for your own research
needs. Scores only reflect the configured source set.
```

with:

```markdown
The GDELT entries are broad starter queries grouped into these current lanes:

- `GDELT Luxury Fashion`: luxury/designer fashion and fashion week signals.
- `GDELT Celebrity Style`: celebrity style and red carpet looks.
- `GDELT Bags Shoes Products`: designer bags, handbags, sneakers, ballet flats,
  and loafers.
- `GDELT Emerging Designers`: emerging and independent designers plus LVMH Prize
  and ANDAM fashion signals.
- `GDELT Runway Fashion Week`: runway shows, fashion week schedules, and
  collection coverage.
- `GDELT Designer Brand Momentum`: designer brands, quiet luxury, heritage
  fashion houses, and independent fashion labels.
- `GDELT Retail Resale Fashion`: fashion retail, luxury retail, resale
  marketplaces, and consignment signals.
- `GDELT Footwear Sneakers`: sneakers, footwear, loafers, ballet flats, and
  boots.
- `GDELT Creative Director Moves`: creative director, artistic director, and
  leadership moves at fashion houses and luxury brands.
- `GDELT Beauty Fashion Crossover`: beauty, fragrance, makeup, and skincare
  signals tied to fashion brands, designers, and luxury.

Tune the query strings, `max_records`, and source weights for your own research
needs. Scores only reflect the configured source set.
```

- [ ] **Step 3: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_packs_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-168-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-168-code-review.md`
- Add: `docs/reviews/opencode-stage-168-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-168-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-168-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-design.md`
- `docs/superpowers/plans/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-plan.md`
- `docs/source-packs.md`
- `tests/test_source_packs_docs.py`

The prompt must require the response to start with:

```text
# Stage 168 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-168-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-168-code-review.md
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

Create `docs/reviews/opencode-stage-168-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 168 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-168-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  docs/source-packs.md \
  tests/test_source_packs_docs.py \
  docs/superpowers/specs/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-design.md \
  docs/superpowers/plans/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-plan.md \
  docs/reviews/opencode-stage-168-plan-review-prompt.md \
  docs/reviews/opencode-stage-168-plan-review.md \
  docs/reviews/opencode-stage-168-code-review-prompt.md \
  docs/reviews/opencode-stage-168-code-review.md \
  docs/reviews/opencode-stage-168-release-review-prompt.md \
  docs/reviews/opencode-stage-168-release-review.md
git commit -m "docs: sync public source pack lanes"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 covers doc drift tests, Task 2 covers docs sync, Task 3
  covers review/release/commit requirements.
- Placeholder scan: no placeholder implementation steps remain.
- Type consistency: helper and test names are defined before use and match the
  code snippets.
- Scope check: this is docs/test-only and stays inside the source-pack docs
  synchronization objective.
