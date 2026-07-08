# Stage 350 Saved Article Daily Signal Leaderboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Daily Signal Leaderboard that aggregates saved local article Signal Facets into brand, product, and theme rollups.

**Architecture:** Build a small in-memory leaderboard from the existing Stage 349 `RowOneSavedArticleSignalFacets` object, not from raw article text or raw references. Pass the typed leaderboard through the existing ROW ONE render pipeline and render it only in the generated `articles/index.html` saved article library page, after Signal Facets and before Theme Digest. Keep all links internal and safe, with no schemas, JSON artifacts, route families, extraction, ranking, LLM, scheduling, deployment, or app-facing contract changes.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_daily_signal_leaderboard.py`
  - Add constants:
    - `SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT = 5`
    - `SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT = 3`
  - Add frozen dataclasses:
    - `RowOneSavedArticleDailySignalLeaderboard`
    - `RowOneSavedArticleDailySignalLeaderboardBucket`
    - `RowOneSavedArticleDailySignalLeaderboardItem`
    - `RowOneSavedArticleDailySignalLeaderboardSupport`
  - Add builder:
    - `build_row_one_saved_article_daily_signal_leaderboard(...)`
  - Aggregate only existing `RowOneSavedArticleSignalFacets` rows.
- Modify `src/fashion_radar/row_one/render.py`
  - Build `saved_article_daily_signal_leaderboard` after `saved_article_signal_facets`.
  - Pass it to `_write_saved_article_library_page(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept the typed leaderboard in `render_saved_article_library_html(...)`.
  - Add `_render_saved_article_daily_signal_leaderboard(...)`.
  - Add the leaderboard to the saved article daily summary jump links and
    generated-surface count when the section is present.
  - Add CSS selectors for the new section, buckets, items, labels, metrics, and support links.
  - Render after Signal Facets and before Theme Digest.
- Add `tests/test_row_one_saved_article_daily_signal_leaderboard.py`
  - Cover aggregation, casefold dedupe, source counts, support caps, deterministic ordering, item caps, and empty omission.
- Modify `tests/test_row_one_render.py`
  - Add rendering, placement, escaping, link safety, homepage absence, empty-shell, and CSS selector coverage.
- Modify `tests/test_workflows.py`
  - Add Stage 350 generated-site-only guards and forbidden artifact assertions.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 350 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 350 boundary paragraph before Stage 349.
- Add `docs/reviews/claude-code-stage-350-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-350-plan-review-prompt.md`.

## Task 1: Write Failing Unit Tests

**Files:**
- Create: `tests/test_row_one_saved_article_daily_signal_leaderboard.py`

- [ ] **Step 1: Add fixtures using Stage 349 dataclasses**

Create local helpers that build `RowOneSavedArticleSignalFacets` with multiple
rows. Include:

```python
from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT,
    SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT,
    build_row_one_saved_article_daily_signal_leaderboard,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacetChip,
    RowOneSavedArticleSignalFacetRow,
    RowOneSavedArticleSignalFacets,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _chip(en: str, zh: str | None = None) -> RowOneSavedArticleSignalFacetChip:
    return RowOneSavedArticleSignalFacetChip(label=_lt(en, zh))


def _row(
    index: int,
    *,
    source_name: str = "Vogue Business",
    brands: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
    products: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
    themes: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
) -> RowOneSavedArticleSignalFacetRow:
    return RowOneSavedArticleSignalFacetRow(
        title=_lt(f"Article {index}", f"文章 {index}"),
        source_name=source_name,
        href=f"details/article-{index:010d}.html#local-article-digest",
        detail_path=f"details/article-{index:010d}.html",
        safe_card_count=2,
        brands=brands,
        products=products,
        themes=themes,
    )
```

- [ ] **Step 2: Add the aggregation behavior test**

Add:

```python
def test_build_saved_article_daily_signal_leaderboard_aggregates_facet_chips() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=3,
        brand_count=3,
        product_count=3,
        theme_count=2,
        rows=(
            _row(1, brands=(_chip("The Row"),), products=(_chip("Margaux Bag"),), themes=(_chip("Products"),)),
            _row(2, source_name="WWD", brands=(_chip("the row"),), products=(_chip("Alaia flats"),), themes=(_chip("Products"),)),
            _row(3, brands=(_chip("Prada"),), products=(_chip("Margaux Bag"),)),
        ),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    assert leaderboard.bucket_count == 3
    assert leaderboard.item_count == 5
    brands = leaderboard.buckets[0]
    assert brands.key == "brands"
    assert brands.title.en == "Brands"
    assert [(item.label.en, item.article_count, item.source_count) for item in brands.items] == [
        ("The Row", 2, 2),
        ("Prada", 1, 1),
    ]
    assert [support.title.en for support in brands.items[0].supports] == ["Article 1", "Article 2"]
```

Expected before implementation: import or name failure because the module does not exist.

- [ ] **Step 3: Add deterministic cap and empty tests**

Add tests that assert:

```python
assert len(bucket.items) == SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT
assert len(bucket.items[0].supports) == SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT
assert build_row_one_saved_article_daily_signal_leaderboard(None) is None
assert build_row_one_saved_article_daily_signal_leaderboard(
    RowOneSavedArticleSignalFacets(row_count=0, brand_count=0, product_count=0, theme_count=0, rows=())
) is None
```

Also add a partial-empty bucket test:

```python
def test_build_saved_article_daily_signal_leaderboard_omits_empty_buckets() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=1,
        brand_count=0,
        product_count=0,
        theme_count=1,
        rows=(_row(1, themes=(_chip("Read First"),)),),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    assert leaderboard.bucket_count == 1
    assert [bucket.key for bucket in leaderboard.buckets] == ["themes"]
    assert [item.label.en for item in leaderboard.buckets[0].items] == ["Read First"]
```

Add a cap-selection test, not just a cap-count test. Use at least six brand
labels with mixed support counts and assert the surviving five are the top five
by `article_count`, then first-seen order:

```python
facets = RowOneSavedArticleSignalFacets(
    row_count=6,
    brand_count=11,
    product_count=0,
    theme_count=0,
    rows=(
        _row(1, brands=(_chip("The Row"), _chip("Prada"), _chip("Alaia"))),
        _row(2, brands=(_chip("The Row"), _chip("Prada"), _chip("Miu Miu"))),
        _row(3, brands=(_chip("The Row"), _chip("Toteme"))),
        _row(4, brands=(_chip("Khaite"),)),
        _row(5, brands=(_chip("Alaia"),)),
        _row(6, brands=(_chip("Lemaire"),)),
    ),
)
leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)
assert leaderboard is not None
brands = leaderboard.buckets[0]
assert [item.label.en for item in brands.items] == [
    "The Row",
    "Prada",
    "Alaia",
    "Miu Miu",
    "Toteme",
]
```

Add a support-selection test where one chip appears in five article rows and
assert only the first three row-order supports survive:

```python
facets = RowOneSavedArticleSignalFacets(
    row_count=5,
    brand_count=5,
    product_count=0,
    theme_count=0,
    rows=tuple(_row(index, brands=(_chip("The Row"),)) for index in range(1, 6)),
)
leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)
assert leaderboard is not None
item = leaderboard.buckets[0].items[0]
assert [support.title.en for support in item.supports] == [
    "Article 1",
    "Article 2",
    "Article 3",
]
assert len(item.supports) == SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT
```

Add source and per-article defensive dedupe tests:

```python
assert item.article_count == 2
assert item.source_count == 1
```

for two same-source articles sharing the same chip, and:

```python
assert item.article_count == 1
```

for one row that repeats the same chip label twice.

Add a canonical bucket-order assertion to the main aggregation test:

```python
assert [bucket.key for bucket in leaderboard.buckets] == ["brands", "products", "themes"]
```

The builder should skip blank `source_name` values when computing
`source_count`.

- [ ] **Step 4: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_daily_signal_leaderboard.py -q
```

Expected: FAIL because `fashion_radar.row_one.saved_article_daily_signal_leaderboard` is missing.

## Task 2: Implement Leaderboard Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_daily_signal_leaderboard.py`
- Test: `tests/test_row_one_saved_article_daily_signal_leaderboard.py`

- [ ] **Step 1: Add dataclasses and constants**

Create the module with frozen dataclasses and constants:

```python
SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT = 5
SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT = 3
```

Dataclasses should include localized labels, source counts, article counts, and
support rows containing title, source name, href, and detail path from the
existing Signal Facets row.

- [ ] **Step 2: Implement aggregation from Signal Facets only**

Build buckets for:

```python
("brands", LocalizedText(en="Brands", zh="品牌"), "brands")
("products", LocalizedText(en="Products", zh="产品"), "products")
("themes", LocalizedText(en="Themes", zh="主题"), "themes")
```

For each row and chip:

- normalize key as `(chip.label.zh.casefold(), chip.label.en.casefold())`;
- preserve the first nonblank localized label;
- count each article at most once per chip label;
- collect unique source names for `source_count`;
- collect supports in row order and cap at three.

Sort by `(-article_count, first_seen_index, label.en.casefold())` and cap each
bucket at five items. Omit empty buckets and return `None` if all buckets are
empty.

- [ ] **Step 3: Run unit tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_daily_signal_leaderboard.py -q
```

Expected: PASS.

## Task 3: Render Leaderboard In Articles Page

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

In `tests/test_row_one_render.py`, add a section helper:

```python
def _saved_article_daily_signal_leaderboard_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-daily-signal-leaderboard"'
    assert marker in index_html
    section_start = index_html.index(marker)
    tail = index_html[section_start + len(marker) :]
    next_section = re.search(r"\n\s*<section class=", tail)
    if next_section is None:
        return index_html[section_start:]
    section_end = section_start + len(marker) + next_section.start()
    assert section_end > section_start
    return index_html[section_start:section_end]
```

Add a render test asserting:

```python
assert 'class="saved-article-daily-signal-leaderboard"' in section_html
assert "Daily Signal Leaderboard" in section_html
assert "每日信号榜" in section_html
assert 'href="#saved-article-daily-signal-leaderboard"' in library_html
assert "The Row" in section_html
assert "Alaia flats" in section_html
assert "article" in section_html
assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
assert library_html.index('class="saved-article-signal-facets"') < library_html.index(
    'class="saved-article-daily-signal-leaderboard"'
)
assert library_html.index('class="saved-article-daily-signal-leaderboard"') < library_html.index(
    'class="saved-article-theme-digest"'
)
assert 'class="saved-article-daily-signal-leaderboard"' not in homepage_html
```

Add an escaping test with an explicitly constructed
`RowOneSavedArticleDailySignalLeaderboard` and assert unsafe angle brackets are
escaped for labels, titles, and source names, and safe local article hrefs are
revalidated.

- [ ] **Step 2: Wire render pipeline**

In `render.py`:

- import `build_row_one_saved_article_daily_signal_leaderboard`;
- build `saved_article_daily_signal_leaderboard` after
  `saved_article_signal_facets`;
- add the parameter to `_write_saved_article_library_page(...)`;
- pass it to `render_saved_article_library_html(...)`.

- [ ] **Step 3: Add template renderer and CSS**

In `templates.py`:

- import the new typed dataclasses;
- add a `saved_article_daily_signal_leaderboard` parameter to
  `render_saved_article_library_html(...)`;
- render `{daily_signal_leaderboard}` after `{signal_facets}` and before
  `{theme_digest}`;
- add helper functions:
  - `_render_saved_article_daily_signal_leaderboard(...)`
  - `_render_saved_article_daily_signal_leaderboard_bucket(...)`
  - `_render_saved_article_daily_signal_leaderboard_item(...)`
  - `_render_saved_article_daily_signal_leaderboard_support(...)`
- reuse local article page href override validation before linking supports,
  mirroring `_saved_article_signal_facet_row_href(...)`;
- add a daily-summary jump link to `#saved-article-daily-signal-leaderboard`
  and include the section in the generated-surface count only when the
  leaderboard object is present;
- add CSS under the saved article library style block.

- [ ] **Step 4: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_signal_leaderboard or saved_article_signal_facets or row_one_css_includes_saved_article_library_styles"
```

Expected: PASS.

## Task 4: Add Workflow And Documentation Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`
- Add: `docs/reviews/claude-code-stage-350-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-350-plan-review-prompt.md`

- [ ] **Step 1: Add Stage 350 docs guard tests**

Add assertions that README and `docs/row-one.md` mention:

- `Stage 350`
- `Saved Article Daily Signal Leaderboard`
- `generated-site only`
- no `data/saved-article-daily-signal-leaderboard.json`
- no `row-one-app/v7` contract changes

- [ ] **Step 2: Add workflow contract and artifact assertions**

Add a dedicated test named:

```python
def test_stage_350_saved_article_daily_signal_leaderboard_stays_generated_site_only(tmp_path: Path) -> None:
```

Use a Stage-350-specific local article fixture that produces at least one
Stage 349 signal facet row with brand/product/theme chips. Render the site and
assert the section appears in `articles/index.html`, but
none of these strings leak into `edition.json`, `manifest.json`, or
`runtime.json`:

```python
"saved_article_daily_signal_leaderboard"
"daily_signal_leaderboard"
"saved-article-daily-signal-leaderboard"
"Daily Signal Leaderboard"
"每日信号榜"
```

Assert these artifacts do not exist:

```python
tmp_path / "data" / "saved-article-daily-signal-leaderboard.json"
tmp_path / "data" / "saved-article-daily-signal-leaderboard.html"
tmp_path / "data" / "article-chip-leaderboard.json"
tmp_path / "data" / "article-chip-leaderboard.html"
tmp_path / "saved-article-daily-signal-leaderboard.json"
tmp_path / "saved-article-daily-signal-leaderboard.html"
tmp_path / "article-chip-leaderboard.json"
tmp_path / "article-chip-leaderboard.html"
tmp_path / "articles" / "saved-article-daily-signal-leaderboard.json"
tmp_path / "articles" / "saved-article-daily-signal-leaderboard.html"
tmp_path / "articles" / "article-chip-leaderboard.json"
tmp_path / "articles" / "article-chip-leaderboard.html"
```

This dedicated fixture avoids relying on unrelated workflow fixtures to happen
to produce Signal Facets.

- [ ] **Step 3: Update docs**

Add a concise Stage 350 paragraph before Stage 349 in README and
`docs/row-one.md`:

```markdown
Stage 350 adds generated-site only Saved Article Daily Signal Leaderboard inside `articles/index.html`; it reuses the existing Stage 349 saved article signal facet rows and safe local article digest anchors to aggregate brand, product, and theme chips into capped daily support-count rollups without changing app-facing contracts; it does not create `data/saved-article-daily-signal-leaderboard.json`, does not create `data/article-chip-leaderboard.json`, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 4: Add review prompts**

Create Claude Code and OpenCode review prompt files asking reviewers to inspect
the Stage 350 design, plan, code changes, tests, generated-site-only boundary,
and next-stage plan before implementation or commit.

- [ ] **Step 5: Run focused Stage 350 tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_daily_signal_leaderboard.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_signal_leaderboard or stage_350"
```

Expected: PASS.

## Task 5: Review, Verify, Commit, And Push

**Files:**
- All Stage 350 files.

- [ ] **Step 1: Request implementation review**

Use Claude Code with max effort or a read-only subagent to review the completed
Stage 350 code and tests. Required focus:

- aggregation only from Stage 349 Signal Facets;
- deterministic sorting and caps;
- safe links and escaped labels;
- no app contract, schema, JSON artifact, route family, scheduling, deployment,
  or compliance-review product behavior;
- adequate tests.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Stage and scan**

Run:

```bash
git add README.md docs/row-one.md docs/reviews/claude-code-stage-350-plan-review-prompt.md docs/reviews/opencode-stage-350-plan-review-prompt.md docs/superpowers/plans/2026-07-08-stage-350-saved-article-daily-signal-leaderboard-plan.md docs/superpowers/specs/2026-07-08-stage-350-saved-article-daily-signal-leaderboard-design.md src/fashion_radar/row_one/render.py src/fashion_radar/row_one/saved_article_daily_signal_leaderboard.py src/fashion_radar/row_one/templates.py tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_row_one_saved_article_daily_signal_leaderboard.py tests/test_workflows.py
git diff --cached --check
git diff --cached | rg -n "ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9][A-Za-z0-9_-]{20,}" && exit 1 || true
```

Expected: no whitespace errors and no secret-like tokens.

- [ ] **Step 4: Commit and push**

Run:

```bash
git commit -m "Stage 350: add saved article daily signal leaderboard"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)
git -c http.version=HTTP/1.1 \
  -c http.curloptResolve=github.com:443:140.82.113.4 \
  -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" \
  push origin main
```

Expected: commit pushed to `origin/main`.
