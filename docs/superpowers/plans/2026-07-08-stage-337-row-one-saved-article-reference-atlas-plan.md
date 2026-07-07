# Stage 337 ROW ONE Saved Article Reference Atlas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Reference Atlas to `articles/index.html` so ROW ONE can organize existing saved local article references into compact brand, people, product, and source-context indexes.

**Architecture:** Create a private builder, `saved_article_reference_atlas.py`, that aggregates existing `RowOneReference` chips from safe saved article content-organization cards. Wire it through the existing ROW ONE render pipeline and render only HTML in the saved article library page, with no app/runtime/manifest/schema or generated JSON contract changes.

**Tech Stack:** Python 3.13 dataclasses, existing ROW ONE generated-site renderer, existing safe detail-route helpers, pytest, Ruff, Claude Code/opencode review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Create: `src/fashion_radar/row_one/saved_article_reference_atlas.py`
  - Private generated-site view model for reference atlas buckets and support links.
  - Deterministic reference bucketing, dedupe, source counts, support counts, caps, and safe route filtering.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build reference atlas after saved article content organization and theme digest.
  - Pass reference atlas into `_write_saved_article_library_page()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Accept optional reference atlas in `render_saved_article_library_html()`.
  - Render `saved-article-reference-atlas` after theme digest and before saved signal index.
  - Add CSS selectors matching existing ROW ONE saved-article sections.
- Test: `tests/test_row_one_saved_article_reference_atlas.py`
  - Builder unit tests.
- Test: `tests/test_row_one_render.py`
  - Generated-site/direct-render/CSS/contract tests.
- Test: `tests/test_row_one_docs.py`
  - Stage 337 boundary docs sentinel.
- Modify: `README.md`
  - Stage 337 boundary paragraph.
- Modify: `docs/row-one.md`
  - Stage 337 boundary paragraph.
- Create review artifacts under `docs/reviews/`.

## Task 1: Builder View Model

**Files:**
- Create: `tests/test_row_one_saved_article_reference_atlas.py`
- Create: `src/fashion_radar/row_one/saved_article_reference_atlas.py`

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_row_one_saved_article_reference_atlas.py` with local fixtures similar to `tests/test_row_one_saved_article_theme_digest.py`. Define `_library_with_safe_stories(*story_ids: str)` in this test file by generalizing the Stage 336 singular `_library_with_safe_story()` helper; it should emit one `RowOneSavedArticleLibraryEntry` per story id with safe `digest_path`, `reader_path`, and `evidence_path` fragments.

Include this positive behavior test:

```python
def test_saved_article_reference_atlas_builds_buckets_from_existing_references() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    article = _article(
        story.id,
        paragraphs=["The Row paragraph.", "Alaia paragraph."],
        content_sections=[
            _section(
                "entities",
                "People & Brands",
                items=[
                    _item(
                        "Brand",
                        body="The Row appears as the main brand signal.",
                        paragraph_indices=[0],
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="Mary-Kate Olsen", type="designer", label="person"),
                        ],
                    )
                ],
            ),
            _section(
                "product_signals",
                "Products",
                items=[
                    _item(
                        "Product",
                        body="Alaia flats appear as the product signal.",
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                        ],
                    )
                ],
            ),
        ],
    )
    edition = _edition(story)
    library = build_row_one_saved_article_library(edition, {story.id: article})
    organization = build_row_one_saved_article_content_organization(edition, {story.id: article})

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 3
    assert atlas.reference_count == 3
    assert atlas.support_count == 3
    assert [bucket.key for bucket in atlas.buckets] == ["brands", "people", "products"]
    assert atlas.buckets[0].references[0].name == "The Row"
    assert atlas.buckets[0].references[0].support_count == 1
    assert atlas.buckets[0].references[0].source_count == 1
    assert atlas.buckets[0].references[0].supports[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert atlas.buckets[1].references[0].name == "Mary-Kate Olsen"
    assert atlas.buckets[2].references[0].name == "Alaia flats"
```

Add safety, dedupe, cap, and empty-input tests:

```python
def test_saved_article_reference_atlas_dedupes_names_and_counts_sources() -> None:
    library = _library_with_safe_stories(
        "the-row-a-1234567890",
        "the-row-b-1234567890",
    )
    card_a = _organization_card(
        title="The Row A",
        source_name="Vogue Business",
        lead="Lead A",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
    )
    card_b = _organization_card(
        title="The Row B",
        source_name="WWD",
        lead="Lead B",
        detail_path="details/the-row-b-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="the row", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=[card_a, card_b],
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 1
    reference = atlas.buckets[0].references[0]
    assert reference.name == "The Row"
    assert reference.support_count == 2
    assert reference.source_count == 2
    assert [support.lead.en for support in reference.supports] == ["Lead A", "Lead B"]
```

```python
def test_saved_article_reference_atlas_rejects_unsafe_or_unmatched_support_paths() -> None:
    library = _library_with_safe_stories("the-row-a-1234567890")
    safe_card = _organization_card(
        lead="Safe lead",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=[
                    safe_card,
                    replace(safe_card, detail_path="../secret.html#local-article-content-section-1"),
                    replace(safe_card, detail_path="javascript:alert(1)#local-article-content-section-1"),
                    replace(safe_card, detail_path="details/other-story.html#local-article-content-section-1"),
                    replace(safe_card, detail_path="details/the-row-a-1234567890.html#external"),
                ],
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.support_count == 1
    assert atlas.buckets[0].references[0].supports[0].lead.en == "Safe lead"
```

```python
def test_saved_article_reference_atlas_caps_buckets_references_and_supports() -> None:
    story_ids = [f"story-{index}-1234567890" for index in range(1, 9)]
    library = _library_with_safe_stories(*story_ids)
    cards = [
        _organization_card(
            title=f"Story {index}",
            source_name="Vogue Business" if index % 2 else "WWD",
            lead=f"Lead {index}",
            detail_path=f"details/{story_id}.html#local-article-content-section-1",
            references=(RowOneReference(name=f"Brand {index}", type="brand", label="tracked"),),
        )
        for index, story_id in enumerate(story_ids, start=1)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="人物与品牌"),
                dek=LocalizedText(en="Entities", zh="实体"),
                cards=cards,
            )
        ]
    )

    atlas = build_row_one_saved_article_reference_atlas(library, organization)

    assert atlas is not None
    assert atlas.bucket_count == 1
    assert len(atlas.buckets[0].references) == 6
    assert all(len(reference.supports) <= 3 for reference in atlas.buckets[0].references)
```

```python
def test_saved_article_reference_atlas_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_reference_atlas(None, None) is None
    empty_library = RowOneSavedArticleLibrary(
        article_count=0,
        source_count=0,
        saved_paragraph_count=0,
        organized_section_count=0,
        extracted_article_count=0,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[],
    )
    assert build_row_one_saved_article_reference_atlas(empty_library, None) is None
    empty_organization = RowOneSavedArticleContentOrganization(groups=[])
    assert build_row_one_saved_article_reference_atlas(empty_library, empty_organization) is None
```

- [ ] **Step 2: Run builder tests to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reference_atlas.py -q
```

Expected: FAIL because `saved_article_reference_atlas.py` does not exist.

- [ ] **Step 3: Implement minimal builder**

Create `src/fashion_radar/row_one/saved_article_reference_atlas.py` with frozen dataclasses:

```python
@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasEntry:
    name: str
    reference_type: str
    label: str
    support_count: int
    source_count: int
    supports: tuple[RowOneSavedArticleReferenceAtlasSupport, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasBucket:
    key: str
    title: LocalizedText
    dek: LocalizedText
    reference_count: int
    support_count: int
    source_count: int
    references: tuple[RowOneSavedArticleReferenceAtlasEntry, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlas:
    bucket_count: int
    reference_count: int
    support_count: int
    source_count: int
    buckets: tuple[RowOneSavedArticleReferenceAtlasBucket, ...]
```

Constants:

```python
MAX_SAVED_ARTICLE_REFERENCE_ATLAS_BUCKETS = 4
MAX_SAVED_ARTICLE_REFERENCE_ATLAS_REFERENCES = 6
MAX_SAVED_ARTICLE_REFERENCE_ATLAS_SUPPORTS = 3
```

Implement `build_row_one_saved_article_reference_atlas(library, organization)`:

- return `None` when library or organization is missing;
- derive safe allowed detail paths from library using `safe_row_one_detail_fragment_href()` and `validated_row_one_detail_relative_path()`;
- accept only content-section hrefs with `#local-article-content-section-N`, ASCII digits, no leading zeros, and `N >= 1`;
- require the canonical detail path to exist in the saved article library;
- iterate organization groups and cards in existing order;
- skip cards with no safe detail path or no references;
- skip references whose `name.strip()` is empty;
- bucket references using normalized reference type/label as described in the Stage 337 spec;
- dedupe entries by `(bucket_key, normalized_reference_name)`;
- preserve first display `name`, first non-empty `type`, and first non-empty `label`;
- count supports as safe cards mentioning that reference, deduped by `(detail_path, normalized lead en, normalized lead zh)`;
- count sources by normalized source name across supports;
- sort references by `support_count` descending and first-seen order as tie-breaker;
- render buckets in canonical order: `brands`, `people`, `products`, `source_context`;
- cap to four buckets, six references per bucket, and three support links per reference;
- global `source_count` is the union of normalized sources across rendered supports;
- return `None` if no buckets have references.

Use deterministic bucket metadata:

```python
brands = LocalizedText(en="Brands", zh="品牌")
people = LocalizedText(en="People", zh="人物")
products = LocalizedText(en="Products", zh="产品")
source_context = LocalizedText(en="Source Context", zh="来源语境")
```

- [ ] **Step 4: Run builder tests to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reference_atlas.py -q
```

Expected: PASS.

## Task 2: Render Pipeline And HTML

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

In `tests/test_row_one_render.py`, add imports for atlas dataclasses and add tests near the Stage 336 theme digest tests. Add a dedicated `_reference_atlas_local_article()` helper rather than relying on `_theme_digest_local_article()`. The helper should start from `_theme_digest_local_article()` and return a deep `model_copy()` whose content sections explicitly include the existing read-first section plus `entities` with `The Row` and `product_signals` with `Alaia flats`. This keeps Stage 337 render expectations independent from Stage 336 fixture drift.

Add full-site test:

```python
def test_render_row_one_site_includes_saved_article_reference_atlas_in_article_library(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _reference_atlas_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_reference_atlas_section_html(library_html)

    assert 'class="saved-article-reference-atlas"' in section_html
    assert "Saved Article Reference Atlas" in section_html
    assert "保存文章引用图谱" in section_html
    assert "The Row" in section_html
    assert "Alaia flats" in section_html
    assert "Brands" in section_html
    assert "Products" in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-article-theme-digest"')
        < library_html.index('class="saved-article-reference-atlas"')
        < library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-reference-atlas"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_reference_atlas" not in contract_json
        assert "reference_atlas" not in contract_json
        assert "saved-article-reference-atlas" not in contract_json
        assert "Saved Article Reference Atlas" not in contract_json
        assert "保存文章引用图谱" not in contract_json
        assert "Alaia flats" not in contract_json
    assert not (tmp_path / "data" / "saved-article-reference-atlas.json").exists()
```

Add direct-render safety/escaping/empty tests:

```python
def test_render_saved_article_library_html_filters_unsafe_reference_atlas_supports() -> None:
    safe_support = RowOneSavedArticleReferenceAtlasSupport(
        title=LocalizedText(en="Safe support", zh="安全支持"),
        source_name="Safe Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="Read First", zh="优先阅读"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(),
    )
    atlas = RowOneSavedArticleReferenceAtlas(
        bucket_count=1,
        reference_count=1,
        support_count=4,
        source_count=1,
        buckets=(
            RowOneSavedArticleReferenceAtlasBucket(
                key="brands",
                title=LocalizedText(en="Brands", zh="品牌"),
                dek=LocalizedText(en="Brand references", zh="品牌引用"),
                reference_count=1,
                support_count=4,
                source_count=1,
                references=(
                    RowOneSavedArticleReferenceAtlasEntry(
                        name="The Row <brand>",
                        reference_type="brand",
                        label="tracked",
                        support_count=4,
                        source_count=1,
                        supports=(
                            safe_support,
                            replace(safe_support, detail_path="javascript:alert(1)#local-article-content-section-1"),
                            replace(safe_support, detail_path="../secret.html#local-article-content-section-1"),
                            replace(safe_support, detail_path="details/the-row-signal-1234567890.html#external"),
                        ),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=atlas,
    )
    section_html = _saved_article_reference_atlas_section_html(html)

    assert "The Row &lt;brand&gt;" in section_html
    assert "javascript:" not in section_html
    assert "../secret.html" not in section_html
    assert "#external" not in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
    assert section_html.count('class="saved-article-reference-atlas-support"') == 1
```

```python
def test_render_saved_article_library_html_omits_empty_reference_atlas_shell() -> None:
    html_without_atlas = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=None,
    )
    empty_atlas = RowOneSavedArticleReferenceAtlas(
        bucket_count=0,
        reference_count=0,
        support_count=0,
        source_count=0,
        buckets=(),
    )
    html_with_empty_atlas = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reference_atlas=empty_atlas,
    )

    for html in (html_without_atlas, html_with_empty_atlas):
        assert 'class="saved-article-reference-atlas"' not in html
        assert "Saved Article Reference Atlas" not in html
        assert "保存文章引用图谱" not in html
        assert 'class="saved-article-library-hero"' in html
        assert 'class="saved-article-library-grid"' in html
```

Add `_saved_article_reference_atlas_section_html()` helper like `_saved_article_theme_digest_section_html()`.

Add CSS selector sentinel test:

```python
def test_row_one_css_includes_saved_article_reference_atlas_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-reference-atlas",
        ".saved-article-reference-atlas-header",
        ".saved-article-reference-atlas-metrics",
        ".saved-article-reference-atlas-grid",
        ".saved-article-reference-atlas-bucket",
        ".saved-article-reference-atlas-bucket-header",
        ".saved-article-reference-atlas-bucket-meta",
        ".saved-article-reference-atlas-entries",
        ".saved-article-reference-atlas-entry",
        ".saved-article-reference-atlas-entry-header",
        ".saved-article-reference-atlas-entry-meta",
        ".saved-article-reference-atlas-chip",
        ".saved-article-reference-atlas-supports",
        ".saved-article-reference-atlas-support",
        ".saved-article-reference-atlas-support-meta",
        ".saved-article-reference-atlas-lead",
        ".saved-article-reference-atlas-actions",
        ".saved-article-reference-atlas-evidence",
        ".saved-article-reference-atlas-link",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

- [ ] **Step 2: Run render tests to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reference_atlas or theme_digest or saved_article_library or row_one_css"
```

Expected: FAIL because render pipeline/template imports and helper do not exist.

- [ ] **Step 3: Wire render pipeline**

In `src/fashion_radar/row_one/render.py`:

- import `RowOneSavedArticleReferenceAtlas` and `build_row_one_saved_article_reference_atlas`;
- build `saved_article_reference_atlas` after `saved_article_theme_digest`;
- pass it into `_write_saved_article_library_page()`;
- add `_write_saved_article_library_page(..., saved_article_reference_atlas: RowOneSavedArticleReferenceAtlas | None)`;
- pass it into `render_saved_article_library_html()`.

- [ ] **Step 4: Render atlas HTML and CSS**

In `src/fashion_radar/row_one/templates.py`:

- import atlas dataclasses;
- add optional `saved_article_reference_atlas` parameter to `render_saved_article_library_html()`;
- compute `reference_atlas = _render_saved_article_reference_atlas(saved_article_reference_atlas)`;
- insert `{reference_atlas}` immediately after `{theme_digest}` and before `{signal_index}`;
- add helpers:
  - `_render_saved_article_reference_atlas()`;
  - `_render_saved_article_reference_atlas_bucket()`;
  - `_render_saved_article_reference_atlas_entry()`;
  - `_render_saved_article_reference_atlas_support()`;
  - `_render_saved_article_reference_atlas_evidence()`.

Use existing `_safe_saved_article_content_organization_href()`, `_prefixed_saved_article_content_organization_href()`, `_render_saved_article_content_organization_evidence()`, `_local_article_digest_excerpt()`, `_count_label()`, and `_esc()`.

CSS selectors to add:

```python
(
    ".saved-article-reference-atlas",
    ".saved-article-reference-atlas-header",
    ".saved-article-reference-atlas-metrics",
    ".saved-article-reference-atlas-grid",
    ".saved-article-reference-atlas-bucket",
    ".saved-article-reference-atlas-bucket-header",
    ".saved-article-reference-atlas-bucket-meta",
    ".saved-article-reference-atlas-entries",
    ".saved-article-reference-atlas-entry",
    ".saved-article-reference-atlas-entry-header",
    ".saved-article-reference-atlas-entry-meta",
    ".saved-article-reference-atlas-chip",
    ".saved-article-reference-atlas-supports",
    ".saved-article-reference-atlas-support",
    ".saved-article-reference-atlas-support-meta",
    ".saved-article-reference-atlas-lead",
    ".saved-article-reference-atlas-actions",
    ".saved-article-reference-atlas-evidence",
    ".saved-article-reference-atlas-link",
)
```

- [ ] **Step 5: Run render tests to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reference_atlas or theme_digest or saved_article_library or row_one_css"
```

Expected: PASS.

## Task 3: Docs And Boundary Sentinels

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Write failing docs test**

Add `test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary()` adjacent to the Stage 336 docs test:

```python
def test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary() -> None:
    expected = _normalized(
        "Stage 337 adds generated-site only Saved Article Reference Atlas inside "
        "`articles/index.html`; it reuses existing saved local article sidecars, "
        "existing saved article content organization references, and existing "
        "detail-page `#local-article-content-section-N` and "
        "`#local-article-paragraph-N` anchors to group saved local references "
        "by brands, people, products, and source context; it does not publish "
        "full articles on the library index, does not add LLM-generated "
        "summaries, does not add trend scoring or heat ranking, does not change "
        "row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, "
        "JSON artifacts, source collection, fetching, matching, extraction, "
        "scoring, ranking, LLM, connector, scheduling, deployment, market "
        "grouping, domestic/international classification, or compliance-review "
        "behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 337 adds generated-site only saved article reference atlas"
            ) : normalized.index(
                "stage 336 adds generated-site only saved article theme digest"
            )
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-reference-atlas.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds trend scoring",
            "adds heat ranking",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

- [ ] **Step 2: Run docs test to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary -q
```

Expected: FAIL because docs do not include Stage 337.

- [ ] **Step 3: Add Stage 337 docs paragraph**

Insert this paragraph immediately above Stage 336 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 337 adds generated-site only Saved Article Reference Atlas inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved article content organization references, and existing detail-page `#local-article-content-section-N` and `#local-article-paragraph-N` anchors to group saved local references by brands, people, products, and source context; it does not publish full articles on the library index, does not add LLM-generated summaries, does not add trend scoring or heat ranking, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 4: Run docs test to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary -q
```

Expected: PASS.

## Task 4: Reviews, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-337-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-337-plan-review.md`
- Create: `docs/reviews/opencode-stage-337-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-337-plan-review.md`
- Create: `docs/reviews/claude-code-stage-337-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-337-code-review.md`
- Create: `docs/reviews/opencode-stage-337-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-337-code-review.md`

- [ ] **Step 1: Plan review before implementation**

Create Claude Code and opencode plan-review prompts describing Stage 337 goal, files, boundaries, and review checklist. Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence   --tools Read,Grep,Glob,LS,Bash   -p "$(cat docs/reviews/claude-code-stage-337-plan-review-prompt.md)"   > docs/reviews/claude-code-stage-337-plan-review.md
opencode run -m zhipuai-coding-plan/glm-5.2   "$(cat docs/reviews/opencode-stage-337-plan-review-prompt.md)"   > docs/reviews/opencode-stage-337-plan-review.md
```

Resolve Critical/Important findings before implementing.

- [ ] **Step 2: Focused verification after implementation**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reference_atlas.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reference_atlas or theme_digest or saved_article_library or row_one_css"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q -k "stage_337 or saved_article_reference_atlas"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_reference_atlas.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_reference_atlas.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_reference_atlas.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_reference_atlas.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

- [ ] **Step 3: Code review after implementation**

Create Claude Code and opencode code-review prompts. Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence   --tools Read,Grep,Glob,LS,Bash   -p "$(cat docs/reviews/claude-code-stage-337-code-review-prompt.md)"   > docs/reviews/claude-code-stage-337-code-review.md
opencode run -m zhipuai-coding-plan/glm-5.2   "$(cat docs/reviews/opencode-stage-337-code-review-prompt.md)"   > docs/reviews/opencode-stage-337-code-review.md
```

Fix Critical/Important findings before full verification.

- [ ] **Step 4: Full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
python3 -m venv "$tmp_env/venv"
UV_NO_CONFIG=1 uv --no-config pip install   --python "$tmp_env/venv/bin/python"   --index-url https://pypi.tuna.tsinghua.edu.cn/simple   "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py   --repo-root .   --python "$tmp_env/venv/bin/python"   --installed
"$tmp_env/venv/bin/fashion-radar" row-one build --help >/dev/null
rm -rf "$tmp_build" "$tmp_env"
```

- [ ] **Step 5: Stage, scan, commit, push**

Run:

```bash
git diff --check
git add   README.md   docs/row-one.md   src/fashion_radar/row_one/render.py   src/fashion_radar/row_one/templates.py   src/fashion_radar/row_one/saved_article_reference_atlas.py   tests/test_row_one_docs.py   tests/test_row_one_render.py   tests/test_row_one_saved_article_reference_atlas.py   docs/superpowers/specs/2026-07-08-stage-337-row-one-saved-article-reference-atlas-design.md   docs/superpowers/plans/2026-07-08-stage-337-row-one-saved-article-reference-atlas-plan.md   docs/reviews/claude-code-stage-337-plan-review-prompt.md   docs/reviews/claude-code-stage-337-plan-review.md   docs/reviews/opencode-stage-337-plan-review-prompt.md   docs/reviews/opencode-stage-337-plan-review.md   docs/reviews/claude-code-stage-337-code-review-prompt.md   docs/reviews/claude-code-stage-337-code-review.md   docs/reviews/opencode-stage-337-code-review-prompt.md   docs/reviews/opencode-stage-337-code-review.md
git diff --cached --check
if git diff --cached --name-only | rg -x 'uv.lock|pyproject.toml|dist/.*|build/.*|reports/.*|data/.*|\.codegraph/.*|\.venv/.*|\.env|.*cookie.*|.*session.*|.*token.*'; then
  echo "blocked forbidden staged path" >&2
  exit 1
fi
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]+'; then
  echo "staged secret scan found matches" >&2
  exit 1
fi
git commit -m "Stage 337: add saved article reference atlas"
git push
```

Expected: commit and push succeed.

## Self-Review Checklist

- Stage 337 remains generated-site-only.
- No generated JSON artifact is added.
- No app/runtime/manifest/schema contract version changes are planned.
- No source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, social/community, market grouping, domestic/international classification, or compliance-review behavior is added.
- Every atlas link is internal and validated before rendering.
- Tests cover builder behavior, HTML ordering, unsafe paths, contract non-leakage, CSS selectors, and docs boundaries.
