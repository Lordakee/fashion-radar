# Stage 334 ROW ONE Saved Article Library Local Excerpts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only organized local excerpts to ROW ONE saved article library cards so `articles/index.html` shows short read-first snippets from existing saved local article organization.

**Architecture:** Reuse the existing `RowOneSavedArticleContentOrganization` view model and mirror its safe localized leads into matching `RowOneSavedArticleLibrary` source cards during template rendering. Keep this HTML-only; do not change saved article library dataclasses, sidecar schemas, `data/edition.json`, manifest/runtime contracts, collection, extraction, ranking, LLM, connectors, scheduling, or compliance-review behavior.

**Tech Stack:** Python 3.13, existing ROW ONE dataclass view models, existing static HTML renderer, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Build a snippet lookup from `RowOneSavedArticleContentOrganization`.
  - Match snippets to saved article library entries by canonical generated
    detail path.
  - Render safe, capped organized excerpt snippets inside saved article library
    cards.
  - Add small CSS rules for the snippet block.
- Modify: `tests/test_row_one_render.py`
  - Add generated-site and direct-render coverage for snippet rendering,
    escaping, truncation, dedupe/cap, safe links, unsafe filtering, canonical
    paths, and JSON contract stability.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 334 docs boundary sentinel.
- Modify: `README.md`
  - Document Stage 334 generated-site-only boundary.
- Modify: `docs/row-one.md`
  - Document Stage 334 generated-site-only boundary.
- Create review artifacts under `docs/reviews/`.

## Task 1: Render Matching Organized Snippets In Saved Article Cards

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add failing generated-site render assertions**

In `test_render_row_one_site_writes_saved_article_library_page()`, the existing
local article fixture already contains an `entities` content-section item body
`The Row body.` / `The Row 正文。`. The mirrored snippet label for that fixture
comes from the existing content-organization builder and should be
`People & Brands` / `品牌与人物`. Add:

```python
    assert 'class="saved-article-library-snippets"' in html
    assert 'class="saved-article-library-snippet"' in html
    assert "People &amp; Brands" in html
    assert "品牌与人物" in html
    assert "The Row body." in html
    assert "The Row 正文。" in html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in html
    )
```

Extend the contract sentinel tuple in the same test with:

```python
            "saved_article_library_snippets",
            "saved_article_library_snippet",
            "saved-article-library-snippets",
            "saved-article-library-snippet",
            "People & Brands",
            "品牌与人物",
            "The Row body.",
            "The Row 正文。",
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page -q
```

Expected: FAIL until card snippets render.

- [ ] **Step 2: Add failing source-card scoped assertion**

In `test_render_row_one_site_includes_saved_article_content_organization_in_article_library()`,
after the standalone content organization assertions, add:

```python
    library_grid_html = library_html[
        library_html.index('class="saved-article-library-grid"') :
    ]
    assert 'class="saved-article-library-snippets"' in library_grid_html
    assert "The Row appears in paragraph one." in library_grid_html
    assert "Alaia flats appear in paragraph two." in library_grid_html
```

Extend the contract sentinel loop in that test with:

```python
        assert "saved-article-library-snippets" not in contract_json
        assert "saved-article-library-snippet" not in contract_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library -q
```

Expected: FAIL until source cards render snippets from the organization lookup.

- [ ] **Step 3: Implement snippet lookup plumbing**

In `src/fashion_radar/row_one/templates.py`, update the collections import:

```python
from collections.abc import Mapping, Sequence
```

Then add:

```python
SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD = 3
```

Change `render_saved_article_library_html()` from:

```python
    groups = "\n".join(_render_saved_article_library_source(group) for group in library.groups)
```

to:

```python
    snippets_by_detail_path = _saved_article_library_snippets_by_detail_path(
        saved_article_content_organization
    )
    groups = "\n".join(
        _render_saved_article_library_source(
            group,
            snippets_by_detail_path=snippets_by_detail_path,
        )
        for group in library.groups
    )
```

Update `_render_saved_article_library_source()` signature:

```python
def _render_saved_article_library_source(
    group: RowOneSavedArticleLibrarySourceGroup,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ] | None = None,
) -> str:
```

Update the cards line:

```python
    cards = "\n".join(
        _render_saved_article_library_card(
            entry,
            snippets_by_detail_path=snippets_by_detail_path,
        )
        for entry in group.entries
    )
```

Update `_render_saved_article_library_card()` signature:

```python
def _render_saved_article_library_card(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ] | None = None,
) -> str:
```

Add inside `_render_saved_article_library_card()`:

```python
    snippets = _render_saved_article_library_snippets(
        _saved_article_library_entry_snippets(entry, snippets_by_detail_path)
    )
```

Insert `{snippets}` after the counts list and before `{refs}`.

- [ ] **Step 4: Implement lookup and matching helpers**

Add near the saved article library helpers:

```python
def _saved_article_library_snippets_by_detail_path(
    organization: RowOneSavedArticleContentOrganization | None,
) -> dict[str, tuple[RowOneSavedArticleContentOrganizationCard, ...]]:
    if organization is None:
        return {}
    grouped: dict[str, list[RowOneSavedArticleContentOrganizationCard]] = {}
    seen: dict[str, set[tuple[str, str, str, str]]] = {}
    for group in organization.groups:
        for card in group.cards:
            href = _safe_saved_article_content_organization_href(card.detail_path)
            if href is None:
                continue
            detail_path = _saved_article_library_detail_path_key(href)
            if detail_path is None:
                continue
            dedupe_key = (
                href,
                " ".join(card.section_label.en.split()).casefold(),
                " ".join(card.lead.en.split()).casefold(),
                " ".join(card.lead.zh.split()).casefold(),
            )
            seen_for_detail = seen.setdefault(detail_path, set())
            if dedupe_key in seen_for_detail:
                continue
            seen_for_detail.add(dedupe_key)
            grouped.setdefault(detail_path, []).append(card)
    return {
        detail_path: tuple(cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD])
        for detail_path, cards in grouped.items()
    }


def _saved_article_library_detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)


def _saved_article_library_entry_detail_path(entry: RowOneSavedArticleLibraryEntry) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _saved_article_library_detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _saved_article_library_entry_snippets(
    entry: RowOneSavedArticleLibraryEntry,
    snippets_by_detail_path: Mapping[
        str,
        Sequence[RowOneSavedArticleContentOrganizationCard],
    ] | None,
) -> Sequence[RowOneSavedArticleContentOrganizationCard]:
    if not snippets_by_detail_path:
        return ()
    detail_path = _saved_article_library_entry_detail_path(entry)
    if detail_path is None:
        return ()
    return snippets_by_detail_path.get(detail_path, ())
```

- [ ] **Step 5: Implement snippet renderer**

Add:

```python
def _render_saved_article_library_snippets(
    cards: Sequence[RowOneSavedArticleContentOrganizationCard],
) -> str:
    snippets = [
        _render_saved_article_library_snippet(card)
        for card in cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]
    ]
    snippets = [snippet for snippet in snippets if snippet]
    if not snippets:
        return ""
    return (
        '<div class="saved-article-library-snippets" '
        'aria-label="Organized saved article excerpts">'
        + "".join(snippets)
        + "</div>"
    )


def _render_saved_article_library_snippet(
    card: RowOneSavedArticleContentOrganizationCard,
) -> str:
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_content_organization_evidence(
        card,
        href_prefix="../",
    )
    # The evidence helper returns its own saved-article-content-organization-evidence
    # wrapper; keep that intact and wrap it once for card-local spacing.
    evidence_block = (
        f'\n              <span class="saved-article-library-snippet-evidence">{evidence}</span>'
        if evidence
        else ""
    )
    return f"""<article class="saved-article-library-snippet">
              <p class="saved-article-library-snippet-label">
                <span data-lang="en">{_esc(card.section_label.en)}</span>
                <span data-lang="zh">{_esc(card.section_label.zh)}</span>
              </p>
              <p class="saved-article-library-snippet-body">
                <span data-lang="en">{_esc(_local_article_digest_excerpt(card.lead.en))}</span>
                <span data-lang="zh">{_esc(_local_article_digest_excerpt(card.lead.zh))}</span>
              </p>
              <a class="saved-article-library-snippet-link" href="{_esc(href)}">
                <span data-lang="en">Open organized section</span>
                <span data-lang="zh">打开整理栏目</span>
              </a>{evidence_block}
  </article>"""
```

- [ ] **Step 6: Confirm evidence CSS interaction**

Inspect `row_one_css()` for `.saved-article-content-organization-evidence`
rules. If existing content-organization evidence link styles are too specific
for the card context, add a card-local override under the new
`.saved-article-library-snippet-evidence` selector. Do not remove existing
content-organization styles.

- [ ] **Step 7: Verify generated-site tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_content_organization_in_article_library \
  -q
```

Expected: PASS.

## Task 2: Safety, Canonicalization, Dedupe, And CSS

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add direct render test for safe organized snippets**

Add near the existing saved article library content organization tests:

```python
def test_render_saved_article_library_shows_organized_snippets_on_source_cards() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert 'class="saved-article-library-snippets"' in grid_html
    assert "Safe lead" in grid_html
    assert "安全摘要" in grid_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in grid_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"'
        in grid_html
    )
    assert grid_html.index("Safe lead") < grid_html.index('class="saved-article-library-actions"')
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_shows_organized_snippets_on_source_cards -q
```

Expected: PASS after Task 1 implementation.

- [ ] **Step 2: Add direct render test for unsafe snippet filtering**

Add:

```python
def test_render_saved_article_library_filters_unsafe_organized_snippets() -> None:
    def card(title: str, detail_path: str, lead: str) -> RowOneSavedArticleContentOrganizationCard:
        return RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=title, zh=title),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(en=lead, zh=lead),
            detail_path=detail_path,
            paragraph_indices=(0,),
            references=(),
        )

    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    card(
                        "Valid card",
                        "details/the-row-signal-1234567890.html#local-article-content-section-1",
                        "Safe <script>lead</script>",
                    ),
                    card("JS card", "javascript:alert(1)#local-article-content-section-1", "JS lead"),
                    card("Traversal card", "../secrets.html#local-article-content-section-1", "Traversal lead"),
                    card(
                        "Wrong fragment card",
                        "details/the-row-signal-1234567890.html#local-article-paragraph-1",
                        "Wrong fragment lead",
                    ),
                ],
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert "Safe &lt;script&gt;lead&lt;/script&gt;" in grid_html
    assert "<script>" not in grid_html
    assert "javascript:alert" not in grid_html
    assert "../secrets" not in grid_html
    assert "JS lead" not in grid_html
    assert "Traversal lead" not in grid_html
    assert "Wrong fragment lead" not in grid_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_filters_unsafe_organized_snippets -q
```

Expected: PASS.

- [ ] **Step 3: Add direct render test for unsafe library entry paths**

Add:

```python
def test_render_saved_article_library_omits_snippets_for_unsafe_entry_paths() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    entry = replace(
        fixture.groups[0].entries[0],
        reader_path="../outside.html#local-article-reader",
        digest_path="javascript:alert(1)#local-article-digest",
        evidence_path="details/the-row-signal-1234567890.html#wrong-fragment",
    )
    fixture = replace(fixture, groups=[replace(fixture.groups[0], entries=[entry])])

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert 'class="saved-article-library-snippets"' not in grid_html
    assert "Safe lead" not in grid_html
    assert "javascript:alert" not in grid_html
    assert "../outside" not in grid_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_omits_snippets_for_unsafe_entry_paths -q
```

Expected: PASS.

- [ ] **Step 4: Add canonicalization/dedupe/cap/truncation test**

Add:

```python
def test_render_saved_article_library_canonicalizes_caps_and_truncates_organized_snippets() -> None:
    long_lead = (
        "Canonical lead starts with The Row and keeps going long enough that the saved "
        "article library card should show a capped excerpt instead of a full organized "
        "content body ending with a unique tail marker."
    )
    cards = [
        RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(en=long_lead if index == 0 else f"Lead {index}", zh="中文摘要"),
            detail_path=(
                "details/./the-row-signal-1234567890.html#local-article-content-section-1"
                if index == 0
                else f"details/the-row-signal-1234567890.html#local-article-content-section-{index + 1}"
            ),
            paragraph_indices=(0,),
            references=(),
        )
        for index in range(5)
    ]
    cards.insert(1, cards[0])
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=cards,
            )
        ]
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_content_organization=organization,
    )
    grid_html = html[html.index('class="saved-article-library-grid"') :]

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in grid_html
    )
    assert "details/./the-row-signal-1234567890.html" not in grid_html
    assert grid_html.count('class="saved-article-library-snippet"') == 3
    assert grid_html.count("Canonical lead starts with The Row") == 1
    assert "…" in grid_html
    assert "unique tail marker" not in grid_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_saved_article_library_canonicalizes_caps_and_truncates_organized_snippets -q
```

Expected: PASS.

- [ ] **Step 5: Add CSS**

In `row_one_css()`, near existing `.saved-article-library-*` styles, add:

```css
.saved-article-library-snippets {
  display: grid;
  gap: 10px;
}

.saved-article-library-snippet {
  border-left: 2px solid var(--accent);
  padding-left: 12px;
}

.saved-article-library-snippet-label {
  color: var(--muted);
  font-size: 0.76rem;
  margin: 0 0 6px;
  text-transform: uppercase;
}

.saved-article-library-snippet-body {
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0 0 8px;
}

.saved-article-library-snippet-evidence {
  display: contents;
}

.saved-article-library-snippet-link,
.saved-article-library-snippet-evidence a {
  color: var(--accent);
  display: inline-flex;
  font-size: 0.78rem;
  margin-right: 8px;
  text-decoration: none;
}
```

Extend the existing CSS selector test near
`test_row_one_css_includes_saved_article_library_styles()` with:

```python
        ".saved-article-library-snippets",
        ".saved-article-library-snippet",
        ".saved-article-library-snippet-label",
        ".saved-article-library-snippet-body",
        ".saved-article-library-snippet-link",
        ".saved-article-library-snippet-evidence",
```

- [ ] **Step 6: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "saved_article_library or content_organization or row_one_css"
```

Expected: PASS.

## Task 3: Docs Boundary

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing docs sentinel**

Add to `tests/test_row_one_docs.py` before the Stage 333 test:

```python
def test_row_one_docs_describe_stage_334_saved_article_library_local_excerpt_boundary() -> None:
    expected = _normalized(
        "Stage 334 adds generated-site only organized local excerpts to saved "
        "article library cards inside `articles/index.html`; it reuses existing "
        "saved article content organization leads and existing detail-page "
        "content-section and paragraph anchors to show capped per-card read-first "
        "snippets from already-saved local text; it does not publish full "
        "articles on the library index, does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, market grouping, "
        "domestic/international classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index("stage 334 adds generated-site only organized local excerpts") : normalized.index(
                "stage 333 adds a generated-site only saved article library text-source map"
            )
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-library-local-excerpts.json`",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_334_saved_article_library_local_excerpt_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Add docs paragraph**

Insert this paragraph before Stage 333 in both `README.md` and
`docs/row-one.md`:

```markdown
Stage 334 adds generated-site only organized local excerpts to saved article library cards inside `articles/index.html`; it reuses existing saved article content organization leads and existing detail-page content-section and paragraph anchors to show capped per-card read-first snippets from already-saved local text; it does not publish full articles on the library index, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 3: Verify docs sentinel**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_334_saved_article_library_local_excerpt_boundary -q
```

Expected: PASS.

## Task 4: Review, Full Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-334-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-334-code-review.md`
- Possibly create rereview artifacts if Critical/Important findings appear.

- [ ] **Step 1: Run focused formatting and lint**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: PASS. If formatting fails, run `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format <files>` on the affected files, then rerun format check.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-334-code-review-prompt.md` with the Stage
334 objective, changed files, focused verification results, and a request to
classify Critical/Important/Minor findings.

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-334-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-334-code-review.md
rm -f "$tmp_review"
```

Expected: review completes. Fix Critical/Important findings and request rereview
before proceeding.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_build" "$tmp_env"
}
trap cleanup EXIT
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv venv "$tmp_env/venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --cached --check
```

Expected: all commands PASS.

- [ ] **Step 4: Stage and scan**

Run:

```bash
git add README.md docs/row-one.md docs/reviews docs/superpowers \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py
secret_pattern='gh''p_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|s''k-[A-Za-z0-9_-]{16,}|api[_-]?ke''y\s*[:=]|to''ken\s*[:=]|Authori''zation:|Bear''er [A-Za-z0-9._-]{16,}'
if git diff --cached -- README.md docs/row-one.md docs/reviews docs/superpowers src tests | rg --case-sensitive -n "$secret_pattern"; then
  echo "Secret scan failed" >&2
  exit 1
fi
git diff --cached --check
```

Expected: no secret matches and no whitespace errors.

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 334: add row one saved article organized snippets"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 push origin main
git status --short --branch
git rev-parse HEAD origin/main
```

Expected: push succeeds, status is clean, and `HEAD == origin/main`.

## Self-Review Notes

- Spec coverage: tasks cover card snippet rendering, safety, canonicalization,
  dedupe/caps, CSS, docs, review, full verification, secret scan, commit, and
  push.
- Placeholder scan: no `TBD`, `TODO`, or incomplete implementation steps.
- Scope check: generated-site-only HTML feature; no app/runtime/schema/JSON,
  source collection, extraction, ranking, LLM, connector, scheduling, or
  compliance-review behavior.
