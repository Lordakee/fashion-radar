# Stage 349 Saved Article Signal Facets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only Signal Facets that show article-level brand, product, and theme chips for saved local articles.

**Architecture:** Build Signal Facet view data in a small internal builder module, `src/fashion_radar/row_one/saved_article_signal_facets.py`, from the existing saved article library and existing saved article content organization cards. Reuse the existing Reference Atlas bucket classifier for brand/product chips, pass typed facet rows through `render.py`, and keep `templates.py` limited to placement, HTML rendering, and CSS. Render a compact matrix inside `articles/index.html` after the daily summary and before Theme Digest, without changing schemas, JSON artifacts, route families, collection, extraction, ranking, LLM, scheduling, deployment, or app-facing contracts.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_signal_facets.py`
  - Add constants:
    - `SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT = 6`
    - `SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT = 4`
  - Add public frozen dataclasses:
    - `RowOneSavedArticleSignalFacets`
    - `RowOneSavedArticleSignalFacetRow`
    - `RowOneSavedArticleSignalFacetChip`
  - Add builder:
    - `build_row_one_saved_article_signal_facets(...)`
  - Carry organization group title context with each safe card while grouping by
    detail path.
  - Reuse the Reference Atlas bucket classifier for brand/product chips.
- Modify `src/fashion_radar/row_one/saved_article_reference_atlas.py`
  - Expose a small public `row_one_saved_article_reference_bucket(...)` helper
    that returns the existing bucket key for a `RowOneReference`.
  - Keep the existing Reference Atlas behavior unchanged by having `_bucket_key`
    delegate to the public helper.
- Modify `src/fashion_radar/row_one/render.py`
  - Build `saved_article_signal_facets` after content organization and library.
  - Pass it to `render_saved_article_library_html(...)`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept the typed facet object in `render_saved_article_library_html(...)`.
  - Add `_render_saved_article_signal_facets(...)` and row/chip render helpers.
  - Add CSS selectors for `.saved-article-signal-facets`, header, grid, row,
    article, source, columns, chips, and metrics.
  - Render Signal Facets after `daily_summary` and before `theme_digest`.
- Add `tests/test_row_one_saved_article_signal_facets.py`
  - Cover builder classification, safe href filtering, dedupe, caps, group-title
    themes, safe-card counts, and Reference Atlas parity.
- Modify `tests/test_row_one_render.py`
  - Add rendering, placement, safety, capping, dedupe, empty-shell, homepage
    absence, and CSS selector tests.
- Modify `tests/test_workflows.py`
  - Add generated-contract negative assertions and artifact absence checks for
    Stage 349.
  - Add positive `articles/index.html` presence assertions.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 349 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 349 boundary paragraph before Stage 348.
- Add `docs/reviews/claude-code-stage-349-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-349-plan-review-prompt.md`.

## Task 1: Write Failing Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add a generated-site rendering and placement test**

Add near the saved article daily-summary/source-route tests:

```python
def test_render_row_one_site_includes_saved_article_signal_facets_in_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    section_html = _saved_article_signal_facets_section_html(library_html)

    assert 'class="saved-article-signal-facets"' in section_html
    assert "Saved Article Signal Facets" in section_html
    assert "信号切面" in section_html
    assert "The Row source" in section_html
    assert "Vogue Business" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert "Themes" in section_html
    assert 'href="the-row-signal-1234567890.html#local-article-digest"' in section_html
    assert library_html.index('class="saved-article-daily-summary"') < library_html.index(
        'class="saved-article-signal-facets"'
    )
    assert library_html.index('class="saved-article-signal-facets"') < library_html.index(
        'class="saved-article-theme-digest"'
    )
    assert 'class="saved-article-signal-facets"' not in homepage_html
```

This placement test intentionally uses `_reference_atlas_local_article()` because it already contains both brand and product references (`The Row` and `Alaia flats`) with safe content sections that match the fixture story detail path.

- [ ] **Step 2: Add the section extraction helper**

Add near `_saved_article_daily_summary_section_html(...)`:

```python
def _saved_article_signal_facets_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-signal-facets"'
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

Also add a small column extraction helper for the capping/dedupe assertions:

```python
def _saved_article_signal_facets_column_html(section_html: str, label: str) -> str:
    label_marker = f'<span data-lang="en">{label}</span>'
    assert label_marker in section_html
    label_start = section_html.index(label_marker)
    column_start = section_html.rfind(
        '<div class="saved-article-signal-facets-column">',
        0,
        label_start,
    )
    assert column_start >= 0
    next_column = section_html.find(
        '<div class="saved-article-signal-facets-column">',
        label_start,
    )
    row_end = section_html.find("</article>", label_start)
    if next_column == -1 or (row_end != -1 and row_end < next_column):
        column_end = row_end
    else:
        column_end = next_column
    assert column_end > column_start
    return section_html[column_start:column_end]
```

- [ ] **Step 3: Add escaping, dedupe, capping, and unsafe-link tests**

Create a custom `RowOneSavedArticleContentOrganization` with cards for the
fixture article:

- references including duplicate `The Row` brand values with different case;
- product references such as `Margaux Bag`, `Alaia flats`, and overflow chips;
- theme labels such as `People <Brands>`, `Products`, and duplicate themes;
- unsafe card hrefs such as `javascript:alert(1)#local-article-content-section-1`
  and `../secret.html#local-article-content-section-1`.

Assert:

```python
assert 'class="saved-article-signal-facets-row"' in section_html
assert section_html.count('class="saved-article-signal-facets-chip"') <= 12
brand_column = _saved_article_signal_facets_column_html(section_html, "Brands")
assert brand_column.count('class="saved-article-signal-facets-chip"') == 1
assert "The Row" in brand_column
assert "People &lt;Brands&gt;" in section_html
assert "People <Brands>" not in section_html
assert "javascript:" not in section_html
assert "../secret.html" not in section_html
assert "Overflow Product 5" not in section_html
```

- [ ] **Step 4: Add empty-shell test**

Call `render_saved_article_library_html(...)` with a library and
`saved_article_signal_facets=None`.

Assert:

```python
assert 'class="saved-article-signal-facets"' not in html
assert "Saved Article Signal Facets" not in html
```

- [ ] **Step 4b: Add unsafe-only organization empty-shell test**

Build facets from a real `RowOneSavedArticleContentOrganization` whose only card
for the fixture article has
`detail_path="javascript:alert(1)#local-article-content-section-1"` and a
unique reference such as `Unsafe Only Facet`, then pass the built
`saved_article_signal_facets` value into `render_saved_article_library_html(...)`.
The builder should return `None`, and the renderer should omit the shell.

Assert:

```python
facets = build_row_one_saved_article_signal_facets(library, unsafe_only_organization)
assert facets is None
assert 'class="saved-article-signal-facets"' not in html
assert "Unsafe Only Facet" not in html
assert "javascript:" not in html
```

- [ ] **Step 5: Add generated contract and artifact absence assertions**

Add a dedicated workflow test named
`test_stage_349_saved_article_signal_facets_stays_generated_site_only(...)` so
the focused `-k "signal_facets or stage_349"` command executes it. In that test,
render the site with `_reference_atlas_local_article()`, read `edition.json`,
`manifest.json`, and `runtime.json`, and assert none of these strings appear:

```python
"saved_article_signal_facets"
"article_signal_facets"
"signal_facets"
"saved-article-signal-facets"
"article-signal-facets"
"signal-facets"
"Saved Article Signal Facets"
"信号切面"
```

Assert no generated artifacts exist:

```python
tmp_path / "data" / "saved-article-signal-facets.json"
tmp_path / "data" / "article-signal-facets.json"
tmp_path / "articles" / "saved-article-signal-facets.html"
```

Also read `articles/index.html` in that dedicated workflow test and assert:

```python
assert 'class="saved-article-signal-facets"' in articles_html
assert "Saved Article Signal Facets" in articles_html
```

- [ ] **Step 6: Add CSS selector coverage**

Extend `test_row_one_css_includes_saved_article_library_styles(...)` with:

```python
".saved-article-signal-facets"
".saved-article-signal-facets-header"
".saved-article-signal-facets-grid"
".saved-article-signal-facets-row"
".saved-article-signal-facets-article"
".saved-article-signal-facets-source"
".saved-article-signal-facets-column"
".saved-article-signal-facets-chip"
```

- [ ] **Step 7: Add docs/workflow failing tests**

Add Stage 349 docs guard in `tests/test_row_one_docs.py`, mirroring Stage 348,
with expected text:

```text
Stage 349 adds generated-site only Saved Article Signal Facets inside
`articles/index.html`; it reuses the existing saved article library entries,
existing saved article content organization cards, existing safe local article
page routes, existing safe card detail-path anchors, and existing reference
labels to show article-level brand, product, and theme chips without changing
app-facing contracts; it does not create
`data/saved-article-signal-facets.json`, does not create
`data/article-signal-facets.json`, does not create new article-source sidecars,
does not create new route families, does not publish full articles on the
library index, does not add outbound article URLs as primary navigation, does
not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas,
JSON artifacts, source collection, fetching, matching, extraction, scoring,
ranking, LLM, connector, scheduling, deployment, market grouping,
domestic/international classification, analytics, personalization,
recommendation, or compliance-review behavior.
```

- [ ] **Step 8: Run tests and confirm they fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "signal_facets or stage_349"
```

Expected: fail because Signal Facets and docs do not exist yet.

## Task 2: Implement Signal Facet View Data

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_signal_facets.py`
- Modify: `src/fashion_radar/row_one/saved_article_reference_atlas.py`
- Create: `tests/test_row_one_saved_article_signal_facets.py`

- [ ] **Step 1: Add builder tests**

Create `tests/test_row_one_saved_article_signal_facets.py` with focused unit
tests that build a minimal `RowOneSavedArticleLibrary` plus
`RowOneSavedArticleContentOrganization` and assert Reference Atlas parity, safe
link filtering, dedupe, row/chip caps, uncapped `safe_card_count`, and
unsafe-only omission.

Use these imports and helper shape:

```python
from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT,
    SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT,
    build_row_one_saved_article_signal_facets,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)
```

Add tests with assertions like:

```python
def test_saved_article_signal_facets_reuse_reference_atlas_buckets() -> None:
    assert row_one_saved_article_reference_bucket(
        RowOneReference(name="The Row", type="brand", label="brand")
    ) == "brands"
    assert row_one_saved_article_reference_bucket(
        RowOneReference(name="Alaia flats", type="product", label="product")
    ) == "products"


def test_build_saved_article_signal_facets_filters_unsafe_links_and_counts_safe_cards() -> None:
    facets = build_row_one_saved_article_signal_facets(_library(), _organization())

    assert facets is not None
    assert facets.row_count == 1
    row = facets.rows[0]
    assert row.detail_path == "details/the-row-signal-1234567890.html"
    assert row.href == "details/the-row-signal-1234567890.html#local-article-digest"
    assert row.safe_card_count == 2
    assert [chip.label.en for chip in row.brands] == ["The Row"]
    assert [chip.label.en for chip in row.products] == ["Alaia flats", "Margaux Bag"]
    assert [chip.label.en for chip in row.themes] == ["People & Brands", "Products"]


def test_build_saved_article_signal_facets_omits_empty_and_unsafe_only_rows() -> None:
    facets = build_row_one_saved_article_signal_facets(
        _library(),
        _unsafe_only_organization(),
    )

    assert facets is None


def test_build_saved_article_signal_facets_caps_rows_and_chips() -> None:
    facets = build_row_one_saved_article_signal_facets(
        _large_library(),
        _large_organization(),
    )

    assert facets is not None
    assert len(facets.rows) == SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT
    assert all(
        len(row.products) <= SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT
        for row in facets.rows
    )
```

- [ ] **Step 2: Add constants and public view dataclasses**

In `saved_article_signal_facets.py`, add:

```python
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)

SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT = 6
SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT = 4


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacetChip:
    label: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacetRow:
    title: LocalizedText
    source_name: str
    href: str
    detail_path: str
    safe_card_count: int
    brands: tuple[RowOneSavedArticleSignalFacetChip, ...]
    products: tuple[RowOneSavedArticleSignalFacetChip, ...]
    themes: tuple[RowOneSavedArticleSignalFacetChip, ...]


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacets:
    row_count: int
    brand_count: int
    product_count: int
    theme_count: int
    rows: tuple[RowOneSavedArticleSignalFacetRow, ...]
```

- [ ] **Step 3: Build rows from existing library entries and organization cards**

Add:

```python
def build_row_one_saved_article_signal_facets(
    library: RowOneSavedArticleLibrary,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleSignalFacets | None:
    if organization is None:
        return None
    cards_by_detail_path = _saved_article_signal_facet_cards_by_detail_path(
        library,
        organization,
    )
    rows: list[RowOneSavedArticleSignalFacetRow] = []
    for group in library.groups:
        for entry in group.entries:
            detail_path = _saved_article_library_entry_detail_path(entry)
            if detail_path is None:
                continue
            cards = cards_by_detail_path.get(detail_path, ())
            if not cards:
                continue
            href = _saved_article_signal_facet_entry_href(entry)
            if href is None:
                continue
            row = _saved_article_signal_facet_row(
                entry,
                href=href,
                detail_path=detail_path,
                contexts=cards,
            )
            if row is not None:
                rows.append(row)
            if len(rows) >= SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT:
                return _saved_article_signal_facets(rows)
    return _saved_article_signal_facets(rows)
```

- [ ] **Step 4: Add safe card grouping and entry href helpers**

Use only public `detail_routes` helpers and a local private content-section
validator; do not import private template helpers into the builder module:

```python
@dataclass(frozen=True)
class _SignalFacetCardContext:
    group_title: LocalizedText
    card: RowOneSavedArticleContentOrganizationCard


def _saved_article_signal_facet_cards_by_detail_path(
    library: RowOneSavedArticleLibrary,
    organization: RowOneSavedArticleContentOrganization,
) -> dict[str, tuple[_SignalFacetCardContext, ...]]:
    allowed_detail_paths = _library_detail_paths(library)
    grouped: dict[str, list[_SignalFacetCardContext]] = {}
    for group in organization.groups:
        for card in group.cards:
            href = _safe_saved_article_content_organization_href(card.detail_path)
            if href is None:
                continue
            detail_path = _detail_path_key(href)
            if detail_path is None or detail_path not in allowed_detail_paths:
                continue
            grouped.setdefault(detail_path, []).append(
                _SignalFacetCardContext(group_title=group.title, card=card)
            )
    return {key: tuple(value) for key, value in grouped.items()}


def _library_detail_paths(library: RowOneSavedArticleLibrary) -> set[str]:
    detail_paths: set[str] = set()
    for group in library.groups:
        for entry in group.entries:
            detail_path = _saved_article_library_entry_detail_path(entry)
            if detail_path is not None:
                detail_paths.add(detail_path)
    return detail_paths


def _saved_article_library_entry_detail_path(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _saved_article_signal_facet_entry_href(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
    return safe_row_one_detail_fragment_href(entry.digest_path, "local-article-digest")


def _safe_saved_article_content_organization_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith("local-article-content-section-"):
        return None
    number = fragment.removeprefix("local-article-content-section-")
    if not number.isascii() or not number.isdecimal() or int(number) < 1:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)
```

- [ ] **Step 5: Expose and reuse Reference Atlas classification**

In `saved_article_reference_atlas.py`, add the public helper and delegate
`_bucket_key(...)` to it:

```python
def row_one_saved_article_reference_bucket(reference: RowOneReference) -> str | None:
    values = {
        _normalized_bucket_text(reference.type),
        _normalized_bucket_text(reference.label),
    }
    values.discard("")
    if values & _BRAND_TERMS:
        return "brands"
    if values & _PEOPLE_TERMS:
        return "people"
    if values & _PRODUCT_TERMS:
        return "products"
    if values & _SOURCE_CONTEXT_TERMS:
        return "source_context"
    if values:
        return "source_context"
    return None


def _bucket_key(reference: RowOneReference) -> str | None:
    return row_one_saved_article_reference_bucket(reference)
```

- [ ] **Step 6: Classify brand/product/theme chips**

In `saved_article_signal_facets.py`, add:

```python
def _saved_article_signal_facet_row(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    href: str,
    detail_path: str,
    contexts: Sequence[_SignalFacetCardContext],
) -> RowOneSavedArticleSignalFacetRow | None:
    brands = _saved_article_signal_facet_reference_chips(contexts, "brands")
    products = _saved_article_signal_facet_reference_chips(contexts, "products")
    themes = _saved_article_signal_facet_theme_chips(contexts)
    if not brands and not products and not themes:
        return None
    return RowOneSavedArticleSignalFacetRow(
        title=entry.title,
        source_name=entry.source_name,
        href=href,
        detail_path=detail_path,
        safe_card_count=len(contexts),
        brands=brands,
        products=products,
        themes=themes,
    )


def _saved_article_signal_facet_reference_chips(
    contexts: Sequence[_SignalFacetCardContext],
    bucket: str,
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    labels: list[LocalizedText] = []
    for context in contexts:
        for reference in context.card.references:
            if row_one_saved_article_reference_bucket(reference) != bucket:
                continue
            label = " ".join(reference.name.split())
            if label:
                labels.append(LocalizedText(zh=label, en=label))
    return _saved_article_signal_facet_chip_values(labels)


def _saved_article_signal_facet_theme_chips(
    contexts: Sequence[_SignalFacetCardContext],
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    return _saved_article_signal_facet_chip_values(
        context.group_title for context in contexts
    )


def _saved_article_signal_facet_chip_values(
    values: Iterable[LocalizedText],
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    chips: list[RowOneSavedArticleSignalFacetChip] = []
    seen: set[tuple[str, str]] = set()
    for value in values:
        label = LocalizedText(
            zh=" ".join(value.zh.split()),
            en=" ".join(value.en.split()),
        )
        if not label.zh and not label.en:
            continue
        key = (label.zh.casefold(), label.en.casefold())
        if key in seen:
            continue
        seen.add(key)
        chips.append(RowOneSavedArticleSignalFacetChip(label=label))
        if len(chips) >= SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT:
            break
    return tuple(chips)


def _saved_article_signal_facets(
    rows: list[RowOneSavedArticleSignalFacetRow],
) -> RowOneSavedArticleSignalFacets | None:
    if not rows:
        return None
    return RowOneSavedArticleSignalFacets(
        row_count=len(rows),
        brand_count=sum(len(row.brands) for row in rows),
        product_count=sum(len(row.products) for row in rows),
        theme_count=sum(len(row.themes) for row in rows),
        rows=tuple(rows),
    )
```

- [ ] **Step 7: Run builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_signal_facets.py -q
```

Expected: pass.

## Task 3: Render Signal Facets

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `src/fashion_radar/row_one/render.py`

- [ ] **Step 1: Pass facet rows through `render_saved_article_library_html(...)`**

In `render.py`, import and build:

```python
saved_article_signal_facets = build_row_one_saved_article_signal_facets(
    saved_article_library,
    saved_article_content_organization,
)
```

Pass `saved_article_signal_facets=saved_article_signal_facets` to
`render_saved_article_library_html(...)`.

In `templates.py`, add the parameter:

```python
saved_article_signal_facets: RowOneSavedArticleSignalFacets | None = None
```

Then render:

```python
signal_facets = _render_saved_article_signal_facets(
    saved_article_signal_facets,
    local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
)
```

In the returned page, place:

```python
  {daily_summary}
  {signal_facets}
  {theme_digest}
```

- [ ] **Step 2: Render section and rows**

Add:

```python
def _render_saved_article_signal_facets(
    facets: RowOneSavedArticleSignalFacets | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if facets is None or not facets.rows:
        return ""
    rows = "\n".join(
        _render_saved_article_signal_facet_row(
            row,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        for row in facets.rows
    )
    return f"""<section class="saved-article-signal-facets" aria-label="Saved article signal facets">
  <div class="saved-article-signal-facets-header">
    <p class="eyebrow">Signal Facets</p>
    <h2>
      <span data-lang="en">Saved Article Signal Facets</span>
      <span data-lang="zh">保存文章信号切面</span>
    </h2>
    <p>
      <span data-lang="en">{_esc(str(facets.row_count))} saved articles organized by brand, product, and theme chips.</span>
      <span data-lang="zh">{_esc(str(facets.row_count))} 篇保存文章按品牌、产品与主题信号整理。</span>
    </p>
  </div>
  <div class="saved-article-signal-facets-grid">
{rows}
  </div>
</section>"""
```

Render each row with:

- article title link;
- source label;
- uncapped safe-card count;
- `Brands`, `Products`, and `Themes` columns;
- each chip escaped with `_esc(...)`;
- no raw article body text.

When rendering the article link, prefer the existing local article page allowlist
using the row's detail path when available. Fall back to the safe detail href
from the builder.

Add row and chip helpers:

```python
def _render_saved_article_signal_facet_row(
    row: RowOneSavedArticleSignalFacetRow,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    href = _saved_article_signal_facet_row_href(
        row,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    return f"""    <article class="saved-article-signal-facets-row">
      <div class="saved-article-signal-facets-article">
        <a href="{_esc(href)}">
          <span data-lang="en">{_esc(row.title.en)}</span>
          <span data-lang="zh">{_esc(row.title.zh)}</span>
        </a>
        <span class="saved-article-signal-facets-source">{_esc(row.source_name)}</span>
        <span class="saved-article-signal-facets-metric">
          <span data-lang="en">{_esc(_count_label(row.safe_card_count, "safe card", "safe cards"))}</span>
          <span data-lang="zh">{_esc(f"{row.safe_card_count} 个安全卡片")}</span>
        </span>
      </div>
      {_render_saved_article_signal_facet_column("Brands", "品牌", row.brands)}
      {_render_saved_article_signal_facet_column("Products", "产品", row.products)}
      {_render_saved_article_signal_facet_column("Themes", "主题", row.themes)}
    </article>"""


def _saved_article_signal_facet_row_href(
    row: RowOneSavedArticleSignalFacetRow,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str:
    if local_article_page_hrefs_by_detail_path:
        page_href = local_article_page_hrefs_by_detail_path.get(row.detail_path)
        if (
            page_href
            and not page_href.startswith(".")
            and "/" not in page_href
            and page_href.endswith(".html")
            and safe_local_article_story_id(page_href.removesuffix(".html"))
        ):
            return f"{page_href}#local-article-digest"
    return _saved_article_library_page_href(row.href)


def _render_saved_article_signal_facet_column(
    label_en: str,
    label_zh: str,
    chips: Sequence[RowOneSavedArticleSignalFacetChip],
) -> str:
    chip_html = "".join(_render_saved_article_signal_facet_chip(chip) for chip in chips)
    if not chip_html:
        chip_html = '<span class="saved-article-signal-facets-empty">-</span>'
    return f"""<div class="saved-article-signal-facets-column">
        <span class="saved-article-signal-facets-column-label">
          <span data-lang="en">{_esc(label_en)}</span>
          <span data-lang="zh">{_esc(label_zh)}</span>
        </span>
        <div class="saved-article-signal-facets-chips">{chip_html}</div>
      </div>"""


def _render_saved_article_signal_facet_chip(
    chip: RowOneSavedArticleSignalFacetChip,
) -> str:
    return (
        '<span class="saved-article-signal-facets-chip">'
        f'<span data-lang="en">{_esc(chip.label.en)}</span>'
        f'<span data-lang="zh">{_esc(chip.label.zh)}</span>'
        "</span>"
    )
```

- [ ] **Step 3: Add CSS**

Add styles near saved article daily summary/source route styles:

```css
.saved-article-signal-facets {
  margin: 32px 0;
  padding: 24px;
  border: 1px solid rgba(20, 20, 20, 0.12);
  background: rgba(250, 248, 244, 0.72);
}
.saved-article-signal-facets-header {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
}
.saved-article-signal-facets-grid {
  display: grid;
  gap: 12px;
}
.saved-article-signal-facets-row {
  display: grid;
  grid-template-columns: minmax(220px, 1.4fr) repeat(3, minmax(140px, 1fr));
  gap: 14px;
  padding: 16px 0;
  border-top: 1px solid rgba(20, 20, 20, 0.1);
}
.saved-article-signal-facets-article {
  display: grid;
  gap: 6px;
}
.saved-article-signal-facets-source {
  color: var(--muted);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.saved-article-signal-facets-column {
  display: grid;
  align-content: start;
  gap: 8px;
}
.saved-article-signal-facets-chip {
  display: inline-flex;
  width: fit-content;
  border: 1px solid rgba(20, 20, 20, 0.16);
  border-radius: 999px;
  padding: 5px 9px;
  font-size: 0.78rem;
}
```

Keep the style consistent with the existing ROW ONE saved article library.

## Task 4: Documentation And Workflow Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Update workflow guard**

Add a dedicated workflow test named with `stage_349` or `signal_facets`, or run
the focused command with a selector that includes the existing workflow test
name. Prefer a dedicated workflow test so the planned focused command covers the
guard.

Add contract negatives:

```python
assert "saved_article_signal_facets" not in generated_contract_payload
assert "article_signal_facets" not in generated_contract_payload
assert "signal_facets" not in generated_contract_payload
assert "Saved Article Signal Facets" not in generated_contract_payload
assert "saved-article-signal-facets" not in generated_contract_payload
assert "article-signal-facets" not in generated_contract_payload
assert "signal-facets" not in generated_contract_payload
assert "信号切面" not in generated_contract_payload
```

Add article HTML positive:

```python
assert 'class="saved-article-signal-facets"' in articles_html
assert "Saved Article Signal Facets" in articles_html
```

Add artifact absence paths for root, `articles`, and `data` with `.json` and
`.html` variants of:

- `saved-article-signal-facets`
- `article-signal-facets`

- [ ] **Step 2: Add docs text**

Add before Stage 348 in both docs:

```text
Stage 349 adds generated-site only Saved Article Signal Facets inside `articles/index.html`; it reuses the existing saved article library entries, existing saved article content organization cards, existing safe local article page routes, existing safe card detail-path anchors, and existing reference labels to show article-level brand, product, and theme chips without changing app-facing contracts; it does not create `data/saved-article-signal-facets.json`, does not create `data/article-signal-facets.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

## Task 5: Verification, Review, Commit, Push

**Files:**
- Review all modified files.

- [ ] **Step 1: Run focused tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "signal_facets or stage_349"
```

Expected: pass.

- [ ] **Step 2: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Request implementation review**

Use Claude Code with `--effort max` to review the uncommitted Stage 349 diff.
If Claude Code times out, record the timeout and use a read-only subagent
cross-check before commit.

- [ ] **Step 4: Stage and scan**

```bash
git add README.md docs/row-one.md src/fashion_radar/row_one/templates.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/saved_article_reference_atlas.py \
  src/fashion_radar/row_one/saved_article_signal_facets.py \
  tests/test_row_one_docs.py tests/test_row_one_render.py tests/test_workflows.py \
  tests/test_row_one_saved_article_signal_facets.py \
  docs/reviews/claude-code-stage-349-plan-review-prompt.md \
  docs/reviews/opencode-stage-349-plan-review-prompt.md \
  docs/superpowers/plans/2026-07-08-stage-349-saved-article-signal-facets-plan.md \
  docs/superpowers/specs/2026-07-08-stage-349-saved-article-signal-facets-design.md
git diff --cached --check
```

Run staged secret scan for GitHub/OpenAI-style tokens before committing.

- [ ] **Step 5: Commit and push**

```bash
git commit -m "Stage 349: add saved article signal facets"
```

Push to `origin/main` using the existing temporary extraheader pattern.

- [ ] **Step 6: Handoff summary**

Report repo status, verified commands, uncommitted files, and next step.
