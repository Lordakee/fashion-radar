# Stage 336 ROW ONE Saved Article Theme Digest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only Saved Article Theme Digest to `articles/index.html` so ROW ONE summarizes recurring themes from already-saved local article content.

**Architecture:** Create a small private generated-site builder, `saved_article_theme_digest.py`, for deterministic theme selection, capping, dedupe, and safe route filtering. Derive the digest from existing saved article library/content organization inputs, render it only in the generated saved article library HTML, and keep app/runtime/manifest schemas and generated JSON unchanged.

**Tech Stack:** Python 3.13 dataclasses, existing ROW ONE generated-site renderer, existing safe detail-route helpers, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Create: `src/fashion_radar/row_one/saved_article_theme_digest.py`
  - Private generated-site view model for theme digest cards.
  - Deterministic theme mapping from existing content-organization groups.
  - Safe saved-library detail-path intersection, item capping, source counts, and dedupe.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build theme digest after saved article library/content organization.
  - Pass theme digest into `_write_saved_article_library_page()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Accept optional theme digest in `render_saved_article_library_html()`.
  - Render the `saved-article-theme-digest` section after the hero.
  - Add CSS selectors matching the existing ROW ONE generated-site style.
- Test: `tests/test_row_one_saved_article_theme_digest.py`
  - Builder unit tests.
- Test: `tests/test_row_one_render.py`
  - Generated-site/direct-render/CSS/contract tests.
- Test: `tests/test_row_one_docs.py`
  - Stage 336 boundary docs sentinel.
- Modify: `README.md`
  - Stage 336 boundary paragraph.
- Modify: `docs/row-one.md`
  - Stage 336 boundary paragraph.
- Create review artifacts under `docs/reviews/`.

## Task 1: Builder View Model

**Files:**
- Create: `tests/test_row_one_saved_article_theme_digest.py`
- Create: `src/fashion_radar/row_one/saved_article_theme_digest.py`

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_row_one_saved_article_theme_digest.py` using local fixtures patterned after `tests/test_row_one_saved_article_reading_paths.py`.

Include these behavioral tests:

```python
def test_saved_article_theme_digest_builds_theme_cards_from_existing_saved_inputs() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    article = _article(
        story.id,
        paragraphs=["The Row paragraph.", "Alaia paragraph."],
        content_sections=[
            _section(
                "takeaways",
                "Read First",
                items=[
                    _item(
                        "Lead",
                        body="Start with The Row retail signal.",
                        body_zh="先看 The Row 零售信号。",
                        paragraph_indices=[0],
                    )
                ],
            ),
            _section(
                "product_signals",
                "Products",
                items=[
                    _item(
                        "Product",
                        body="The new bag shape is driving saved coverage.",
                        body_zh="新包型正在带动保存报道。",
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="bag", type="product", label="product"),
                        ],
                    )
                ],
            ),
        ],
    )
    edition = _edition(story)
    library = build_row_one_saved_article_library(edition, {story.id: article})
    organization = build_row_one_saved_article_content_organization(edition, {story.id: article})
    digest = build_row_one_saved_article_theme_digest(
        library,
        organization,
    )

    assert digest is not None
    assert digest.theme_count == 2
    assert digest.item_count == 2
    assert digest.themes[0].key == "read_first"
    assert digest.themes[0].items[0].lead.en == "Start with The Row retail signal."
    assert digest.themes[0].items[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert digest.themes[1].key == "products"
    assert digest.themes[1].items[0].references[1].name == "bag"
```

Add safety/capping tests:

```python
def test_saved_article_theme_digest_rejects_unsafe_or_unmatched_detail_paths() -> None:
    library = _library_with_safe_story("the-row-a-1234567890")
    safe_card = _organization_card(
        lead="Safe lead",
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
                        detail_path="../secret.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Unmatched lead", zh="未匹配摘要"),
                        detail_path="details/other-story.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Wrong fragment", zh="错误锚点"),
                        detail_path="details/the-row-a-1234567890.html#external",
                    ),
                ],
            )
        ],
    )

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert digest.item_count == 1
    rendered_leads = [item.lead.en for theme in digest.themes for item in theme.items]
    assert rendered_leads == ["Safe lead"]
```

```python
def test_saved_article_theme_digest_caps_and_dedupes_theme_items() -> None:
    library = _library_with_safe_story("the-row-a-1234567890")
    duplicate_cards = [
        _organization_card(
            title=f"The Row card {index}",
            lead="Repeated signal",
            detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        )
        for index in range(8)
    ]
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=duplicate_cards,
            )
        ],
    )

    digest = build_row_one_saved_article_theme_digest(library, organization)

    assert digest is not None
    assert digest.theme_count == 1
    assert digest.item_count == 1
```

- [ ] **Step 2: Run builder tests to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_theme_digest.py -q
```

Expected: FAIL because `saved_article_theme_digest.py` does not exist.

- [ ] **Step 3: Implement minimal builder**

Create `src/fashion_radar/row_one/saved_article_theme_digest.py` with frozen dataclasses:

```python
@dataclass(frozen=True)
class RowOneSavedArticleThemeDigestItem:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleThemeDigestTheme:
    key: str
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    items: tuple[RowOneSavedArticleThemeDigestItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleThemeDigest:
    theme_count: int
    item_count: int
    source_count: int
    themes: tuple[RowOneSavedArticleThemeDigestTheme, ...]
```

Implement `build_row_one_saved_article_theme_digest(library, organization)`:

- return `None` when `library` or `organization` is missing;
- derive safe allowed detail paths from the library using the same route helpers as Stage 335;
- map organization group keys to theme keys:
  - `takeaways` -> `read_first`
  - `entities` -> `people_brands`
  - `product_signals` -> `products`
  - `brand_signals` -> `source_structure`
- use these bilingual theme titles and deks:
  - `read_first`: `Read First` / `优先阅读`; `The strongest opening reads from today's saved local text.` / `今天本地保存文本中最适合作为入口的内容。`
  - `people_brands`: `People & Brands` / `人物与品牌`; `Designers, celebrities, brands, and creative figures shaping the saved set.` / `影响今天保存内容的设计师、明星、品牌与创意人物。`
  - `products`: `Products` / `产品`; `Bags, shoes, silhouettes, and product cues appearing across saved articles.` / `在保存文章中反复出现的包袋、鞋履、廓形与产品线索。`
  - `source_structure`: `Source Structure` / `来源结构`; `How sources structure the context around the saved local text.` / `不同来源如何组织今天保存文本里的语境。`
- emit themes in the order their source organization groups appear in
  `RowOneSavedArticleContentOrganization.groups`; skip groups whose key has no
  mapping;
- accept only content-section hrefs with `#local-article-content-section-N`;
- canonicalize path fragments through `validated_row_one_detail_relative_path`;
- require the canonical detail path to exist in the saved article library;
- dedupe by `(theme_key, canonical_detail_path, lead.en, lead.zh)`;
- cap at four themes and three items per theme;
- count unique normalized source names per theme and globally; the global
  `source_count` is the union of sources across rendered theme items, not the
  sum of per-theme source counts.
- keep `RowOneSavedArticleReadingPaths` out of the builder contract; Stage 335
  reading paths remain a downstream navigation surface rendered after this
  digest.

- [ ] **Step 4: Run builder tests to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_theme_digest.py -q
```

Expected: PASS.

## Task 2: Render Theme Digest In `articles/index.html`

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

In `tests/test_row_one_render.py`, add tests near saved article library/reading-path tests:

Create `_row_one_edition_with_local_article_sections()` and
`_local_articles_with_theme_digest_signals()` as new private helpers in
`tests/test_row_one_render.py`. Do not reuse `_signal_briefing_local_article()`
as-is for this test, because the existing helper does not include a `takeaways`
content section and the theme digest test needs a deterministic `Read First`
card. The new helpers should build one deterministic ROW ONE edition with saved
local article `content_sections` covering at least `takeaways` and
`product_signals`, plus local article paragraphs and references that exercise
brand, product, source, and safe detail-anchor rendering.

```python
def test_render_row_one_site_includes_saved_article_theme_digest_in_article_library(
    tmp_path: Path,
) -> None:
    edition = _row_one_edition_with_local_article_sections()
    local_articles = _local_articles_with_theme_digest_signals(edition)

    render_row_one_site(edition, tmp_path, local_articles_by_story_id=local_articles)

    html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    assert "saved-article-theme-digest" in html
    assert "Saved Article Theme Digest" in html
    assert "保存文章主题简报" in html
    assert "Read First" in html
    assert "Products" in html
    digest_section = html[
        html.index("saved-article-theme-digest") : html.index("saved-signal-index")
    ]
    assert 'href="../details/' in digest_section
    assert "#local-article-content-section-" in html
    assert html.index("saved-article-library-hero") < html.index(
        "saved-article-theme-digest"
    ) < html.index("saved-signal-index")
```

Add a contract test:

```python
def test_render_row_one_site_keeps_theme_digest_out_of_json_contracts(tmp_path: Path) -> None:
    edition = _row_one_edition_with_local_article_sections()
    local_articles = _local_articles_with_theme_digest_signals(edition)

    render_row_one_site(edition, tmp_path, local_articles_by_story_id=local_articles)

    for relative_path in ("data/edition.json", "data/manifest.json", "data/runtime.json"):
        text = (tmp_path / relative_path).read_text(encoding="utf-8").casefold()
        assert "saved article theme digest" not in text
        assert "saved-article-theme-digest" not in text
    assert not (tmp_path / "data" / "saved-article-theme-digest.json").exists()
```

- [ ] **Step 2: Run render tests to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "theme_digest or saved_article_library or content_organization or reading_path or row_one_css"
```

Expected: FAIL because the digest is not wired into rendering.

- [ ] **Step 3: Wire builder through render pipeline**

Modify `src/fashion_radar/row_one/render.py`:

- import `RowOneSavedArticleThemeDigest` and `build_row_one_saved_article_theme_digest`;
- call the builder after `saved_article_library` and
  `saved_article_content_organization` are available;
- pass `saved_article_theme_digest` into `_write_saved_article_library_page()`;
- extend `_write_saved_article_library_page()` to pass it into
  `render_saved_article_library_html()`.

- [ ] **Step 4: Render digest HTML**

Modify `src/fashion_radar/row_one/templates.py`:

- import `RowOneSavedArticleThemeDigest` and related item/theme classes;
- add optional parameter `saved_article_theme_digest` to
  `render_saved_article_library_html()`;
- compute `theme_digest = _render_saved_article_theme_digest(...)`;
- insert `{theme_digest}` immediately after the hero section and before
  `{signal_index}`;
- add `_render_saved_article_theme_digest()`,
  `_render_saved_article_theme_digest_theme()`, and
  `_render_saved_article_theme_digest_item()` helpers;
- prefix safe detail links with `../` only after validating they are generated
  detail links with allowed content-section fragments;
- derive optional paragraph evidence links only from validated
  `paragraph_indices`, rendering them as `#local-article-paragraph-N` anchors;
  `paragraph_indices` are zero-based, so rendered paragraph anchors use
  `index + 1` to match the existing `local-article-paragraph-N` convention;
- reuse existing template helpers for safe content-organization hrefs where
  possible, especially `_safe_saved_article_content_organization_href()` and
  `_prefixed_saved_article_content_organization_href()`;
- truncate leads using existing local truncation style if available, otherwise
  a small private helper capped around 180 characters.

- [ ] **Step 5: Run render tests to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "theme_digest or saved_article_library or content_organization or reading_path or row_one_css"
```

Expected: PASS.

## Task 3: Styling, Escaping, And Safety Coverage

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add focused renderer safety assertions**

Add tests that call `render_saved_article_library_html()` directly with a
minimal `RowOneSavedArticleThemeDigest`:

```python
def test_render_saved_article_library_html_escapes_and_truncates_theme_digest() -> None:
    digest = RowOneSavedArticleThemeDigest(
        theme_count=1,
        item_count=1,
        source_count=1,
        themes=(
            RowOneSavedArticleThemeDigestTheme(
                key="read_first",
                title=LocalizedText(en="Brand <Momentum>", zh="品牌<动能>"),
                dek=LocalizedText(en="Theme dek", zh="主题说明"),
                item_count=1,
                source_count=1,
                items=(
                    RowOneSavedArticleThemeDigestItem(
                        title=LocalizedText(en="The Row <script>", zh="The Row"),
                        source_name="Source <Name>",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        section_label=LocalizedText(en="Read First", zh="优先阅读"),
                        lead=LocalizedText(en="Long lead " * 80, zh="长摘要" * 80),
                        detail_path=(
                            "details/the-row-a-1234567890.html"
                            "#local-article-content-section-1"
                        ),
                    ),
                ),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_theme_digest=digest,
    )

    assert "Brand &lt;Momentum&gt;" in html
    assert "Source &lt;Name&gt;" in html
    assert "<script>" not in html
    assert "../details/the-row-a-1234567890.html#local-article-content-section-1" in html
    assert html.count("Long lead") < 80
```

- [ ] **Step 2: Add CSS assertions**

Extend existing `row_one_css()` tests to assert:

```python
css = row_one_css()
assert ".saved-article-theme-digest" in css
assert ".saved-article-theme-digest-header" in css
assert ".saved-article-theme-digest-metrics" in css
assert ".saved-article-theme-digest-grid" in css
assert ".saved-article-theme-digest-card" in css
assert ".saved-article-theme-digest-card-meta" in css
assert ".saved-article-theme-digest-items" in css
assert ".saved-article-theme-digest-link" in css
assert ".saved-article-theme-digest-ref" in css
```

- [ ] **Step 3: Add CSS**

In `row_one_css()`, add selectors matching the surrounding modules:

- `.saved-article-theme-digest`
- `.saved-article-theme-digest-header`
- `.saved-article-theme-digest-metrics`
- `.saved-article-theme-digest-grid`
- `.saved-article-theme-digest-card`
- `.saved-article-theme-digest-card-meta`
- `.saved-article-theme-digest-items`
- `.saved-article-theme-digest-item`
- `.saved-article-theme-digest-link`
- `.saved-article-theme-digest-ref`

Use existing variables, grid structure, serif headings, compact uppercase meta,
and responsive media-query conventions from saved signal index and reading path
styles.

- [ ] **Step 4: Run focused tests and formatting check**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_theme_digest.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "theme_digest or saved_article_library or content_organization or reading_path or row_one_css"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_theme_digest.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_theme_digest.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_theme_digest.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_theme_digest.py tests/test_row_one_render.py
```

Expected: all commands PASS.

## Task 4: Docs Boundary

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs test**

Add `test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary()` adjacent to the Stage 335 docs test:

```python
def test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary() -> None:
    expected = _normalized(
        "Stage 336 adds generated-site only Saved Article Theme Digest inside "
        "`articles/index.html`; it reuses existing saved local article sidecars, "
        "existing saved local paragraphs, existing saved article content "
        "organization, and existing detail-page "
        "`#local-article-content-section-N`, and `#local-article-paragraph-N` "
        "anchors to summarize recurring themes from already-saved local text; "
        "it does not publish full articles on the library index, does not add "
        "LLM-generated summaries, does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, market grouping, "
        "domestic/international classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index(
                "stage 336 adds generated-site only saved article theme digest"
            ) : normalized.index(
                "stage 335 adds generated-site only saved article reading paths"
            )
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-theme-digest.json`",
            "writes a new json artifact",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds connectors",
            "adds scheduling",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

- [ ] **Step 2: Run docs test to verify failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary -q
```

Expected: FAIL because the docs paragraph is missing.

- [ ] **Step 3: Add Stage 336 docs paragraph**

Insert this exact paragraph above Stage 335 in both `README.md` and
`docs/row-one.md`:

```markdown
Stage 336 adds generated-site only Saved Article Theme Digest inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved local paragraphs, existing saved article content organization, and existing detail-page `#local-article-content-section-N` and `#local-article-paragraph-N` anchors to summarize recurring themes from already-saved local text; it does not publish full articles on the library index, does not add LLM-generated summaries, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

- [ ] **Step 4: Run docs test to verify pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary -q
```

Expected: PASS.

## Task 5: Review, Verification, Commit, And Push

**Files:**
- Create: `docs/reviews/claude-code-stage-336-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-336-code-review.md`
- Create: `docs/reviews/opencode-stage-336-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-336-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_theme_digest.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "theme_digest or saved_article_library or content_organization or reading_path or row_one_css"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_theme_digest.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_theme_digest.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_theme_digest.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_theme_digest.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: all commands PASS.

- [ ] **Step 2: Request code review**

Create Claude Code review prompt using Stage 336 changed files and run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-336-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-336-code-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings before proceeding.

- [ ] **Step 3: Request opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run -m zhipuai-coding-plan/glm-5.2 \
  "$(cat docs/reviews/opencode-stage-336-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-336-code-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings before proceeding.

- [ ] **Step 4: Run full node verification**

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
UV_NO_CONFIG=1 uv --no-config pip install \
  --python "$tmp_env/venv/bin/python" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py \
  --repo-root . \
  --python "$tmp_env/venv/bin/python" \
  --installed
"$tmp_env/venv/bin/fashion-radar" row-one build --help >/dev/null
rm -rf "$tmp_build" "$tmp_env"
```

Expected: all commands PASS. If `uv.lock` changes because of a mirror/index
configuration, restore it before staging.

- [ ] **Step 5: Run staging guards, commit, and push**

Run:

```bash
git diff --check
git status --short
git add \
  src/fashion_radar/row_one/saved_article_theme_digest.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_theme_digest.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md \
  docs/superpowers/specs/2026-07-08-stage-336-row-one-saved-article-theme-digest-design.md \
  docs/superpowers/plans/2026-07-08-stage-336-row-one-saved-article-theme-digest-plan.md \
  docs/reviews/claude-code-stage-336-plan-review-prompt.md \
  docs/reviews/claude-code-stage-336-plan-review.md \
  docs/reviews/opencode-stage-336-plan-review-prompt.md \
  docs/reviews/opencode-stage-336-plan-review.md \
  docs/reviews/claude-code-stage-336-code-review-prompt.md \
  docs/reviews/claude-code-stage-336-code-review.md \
  docs/reviews/opencode-stage-336-code-review-prompt.md \
  docs/reviews/opencode-stage-336-code-review.md
git diff --cached --check
git diff --cached --name-only | rg -x 'uv.lock|pyproject.toml|dist/.*|build/.*|reports/.*|data/.*|\.codegraph/.*|\.venv/.*|\.env|.*cookie.*|.*session.*|.*token.*' && exit 1 || exit 0
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]+'; then
  echo "staged secret scan found matches" >&2
  exit 1
fi
git commit -m "Stage 336: add saved article theme digest"
git push
```

- [ ] **Step 6: Write Handoff Summary**

Include:

- repo status;
- commit SHA;
- pushed branch;
- verified commands;
- uncommitted files;
- next recommended node.
