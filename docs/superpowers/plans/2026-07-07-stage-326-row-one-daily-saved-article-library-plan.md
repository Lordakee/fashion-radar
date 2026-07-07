# Stage 326 ROW ONE Daily Saved Article Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site only ROW ONE daily saved article library page at `articles/index.html`, plus a compact homepage entry point, using only the current edition and the in-memory local article data passed to `render_row_one_site()`.

**Architecture:** Add a focused render-only builder module that converts `RowOneEdition` and `local_articles_by_story_id` into capped dataclasses grouped by source. The builder must iterate current `edition.stories` and must not scan `output_dir`, `data/articles/*.json`, or persisted sidecar files, because non-`latest_only` renders can leave old sidecars on disk. Wire that builder into `render_row_one_site()` so generated HTML can write `articles/index.html` and the homepage entry point without changing app/runtime/manifest JSON, schemas, source collection, or local article JSON sidecars.

**Tech Stack:** Python, existing ROW ONE Pydantic models, dataclasses, existing static string-rendered HTML/CSS in `templates.py`, existing safe route helpers, pytest, Ruff, `UV_NO_CONFIG=1 uv --no-config run --frozen`, Claude Code review gates.

---

## Files

- Create: `src/fashion_radar/row_one/saved_article_library.py`
  - Define render-only dataclasses for library paragraph links, article entries, source groups, and the library aggregate.
  - Define `build_row_one_saved_article_library()`.
  - Reuse `safe_local_article_story_id()` and `is_safe_row_one_detail_path()`.
  - Keep caps and path fragments private to this module.
  - Build only from current `edition.stories` plus the current `local_articles_by_story_id` mapping; never read sidecar JSON from disk.
- Create: `tests/test_row_one_saved_article_library.py`
  - Unit-test grouping, filtering, caps, counts, and safe deep-link construction.
- Modify: `src/fashion_radar/row_one/render.py`
  - Import and build the saved article library.
  - Pass it to `render_index_html()`.
  - Write `articles/index.html` when the library exists.
  - Add `articles` to `GENERATED_CHILDREN`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Import the new dataclasses.
  - Add `saved_article_library` to `render_index_html()`.
  - Add `render_saved_article_library_html()`.
  - Add homepage entry and library page render helpers.
  - Add CSS selectors for the entry and page.
- Modify: `tests/test_row_one_render.py`
  - Add render tests for generated page, homepage entry, omission, escaping, and cleanup.
- Modify: `tests/test_workflows.py`
  - Extend generated-site boundary assertions.
- Modify: `tests/test_row_one_docs.py`
  - Add docs boundary checks for Stage 326 wording.
- Modify: `README.md`
  - Add a generated-site-only ROW ONE saved article library note.
- Modify: `docs/row-one.md`
  - Add the same generated-site-only boundary note in more detail.
- Create: `docs/reviews/claude-code-stage-326-plan-review-prompt.md`
- Create after review: `docs/reviews/claude-code-stage-326-plan-review.md`
- Create if Claude Code does not return a usable review: `docs/reviews/opencode-stage-326-plan-review-prompt.md`
- Create if Claude Code does not return a usable review: `docs/reviews/opencode-stage-326-plan-review.md`
- Create if fallback review needs a focused rereview: `docs/reviews/opencode-stage-326-plan-rereview-prompt.md`
- Create if fallback review needs a focused rereview: `docs/reviews/opencode-stage-326-plan-rereview.md`
- Create after implementation: `docs/reviews/claude-code-stage-326-code-review-prompt.md`
- Create after implementation if Claude Code returns a usable review: `docs/reviews/claude-code-stage-326-code-review.md`
- Create if Claude Code does not return a usable implementation review:
  `docs/reviews/opencode-stage-326-code-review-prompt.md`
- Create if Claude Code does not return a usable implementation review:
  `docs/reviews/opencode-stage-326-code-review.md`

## Task 1: Add Saved Article Library Builder With Tests

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_row_one_saved_article_library.py` with tests covering grouping, filters, caps, and deep-link construction. Include local fixture helpers for `_story()`, `_edition()`, `_article()`, `_section()`, and `_item()` so the tests are self-contained and do not depend on helpers from other test modules.

Key assertions to include:

```python
def test_saved_article_library_groups_articles_by_source_and_builds_counts() -> None:
    story_a = _story("the-row-a-1234567890", "The Row market signal", "top_stories")
    story_b = _story("shoe-b-1234567890", "Alaia shoe signal", "hot_products")
    library = build_row_one_saved_article_library(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                title="The Row saved source",
                source_name="Vogue Business",
                paragraphs=["Lead paragraph.", "Second paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Takeaways",
                        items=[
                            _item(
                                "Lead",
                                body="The Row demand is rising.",
                                paragraph_indices=[0, 1],
                                references=[
                                    RowOneReference(name="The Row", type="brand", label="tracked")
                                ],
                            )
                        ],
                    )
                ],
            ),
            story_b.id: _article(
                story_b.id,
                title="Alaia saved source",
                source_name="Vogue Business",
                paragraphs=["Alaia mesh shoe paragraph."],
                content_sections=[
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _item(
                                "Shoe",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(name="Alaia", type="brand", label="shoe")
                                ],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert library is not None
    assert library.article_count == 2
    assert library.source_count == 1
    assert library.saved_paragraph_count == 3
    assert library.organized_section_count == 2
    assert library.groups[0].source_name == "Vogue Business"
    assert [entry.title.en for entry in library.groups[0].entries] == [
        "The Row saved source",
        "Alaia saved source",
    ]
    assert library.groups[0].entries[0].digest_path == (
        "details/the-row-a-1234567890.html#local-article-digest"
    )
    assert library.groups[0].entries[0].reader_path == (
        "details/the-row-a-1234567890.html#local-article-reader"
    )
    assert library.groups[0].entries[0].evidence_path == (
        "details/the-row-a-1234567890.html#local-article-paragraph-evidence"
    )
    assert library.groups[0].entries[0].paragraph_links[0].href == (
        "details/the-row-a-1234567890.html#local-article-paragraph-1"
    )
```

The helper functions should create valid ROW ONE models with only the fields needed by this test module. For example, `_story()` must accept only valid `RowOneSectionKey` values such as `top_stories`, `brand_moves`, `celebrity_style`, `hot_products`, and `rising_radar`.

```python
def test_saved_article_library_filters_unsafe_or_unusable_articles() -> None:
    valid_story = _story("valid-1234567890", "Valid story", "top_stories")
    unsafe_route_story = valid_story.model_copy(
        update={"id": "unsafe-route-1234567890", "detail_path": "../outside.html"}
    )

    library = build_row_one_saved_article_library(
        _edition(valid_story, unsafe_route_story),
        {
            valid_story.id: _article(valid_story.id, paragraphs=["   "]),
            unsafe_route_story.id: _article(unsafe_route_story.id, paragraphs=["Saved."]),
            "not safe id": _article("not safe id", paragraphs=["Saved."]),
        },
    )

    assert library is None
```

```python
def test_saved_article_library_caps_groups_entries_references_and_paragraph_links() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}", "top_stories") for index in range(12)]
    local_articles = {
        story.id: _article(
            story.id,
            source_name="Shared Source" if index < 9 else f"Source {index}",
            paragraphs=[f"Paragraph {paragraph}" for paragraph in range(10)],
            content_sections=[
                _section(
                    "entities",
                    "People & Brands",
                    items=[
                        _item(
                            "Refs",
                            paragraph_indices=list(range(10)),
                            references=[
                                RowOneReference(name=f"Ref {ref}", type="brand", label="tracked")
                                for ref in range(10)
                            ],
                        )
                    ],
                )
            ],
        )
        for index, story in enumerate(stories)
    }

    library = build_row_one_saved_article_library(_edition(*stories), local_articles)

    assert library is not None
    assert len(library.groups) == 4
    assert len(library.groups[0].entries) == 8
    assert len(library.groups[0].entries[0].references) == 6
    assert len(library.groups[0].entries[0].paragraph_links) == 4
```

```python
def test_saved_article_library_filters_invalid_paragraph_indices() -> None:
    story = _story("the-row-a-1234567890", "The Row market signal", "top_stories")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["First paragraph.", "   ", "Third paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Refs",
                                paragraph_indices=[
                                    True,
                                    False,
                                    -1,
                                    0,
                                    1,
                                    2,
                                    2,
                                    99,
                                    "3",
                                ],
                                references=[
                                    RowOneReference(name="The Row", type="brand", label="tracked")
                                ],
                            )
                        ],
                    )
                ],
            )
        },
    )

    assert library is not None
    assert [link.href for link in library.groups[0].entries[0].paragraph_links] == [
        "details/the-row-a-1234567890.html#local-article-paragraph-1",
        "details/the-row-a-1234567890.html#local-article-paragraph-3",
    ]
```

```python
def test_saved_article_library_caps_source_groups() -> None:
    stories = [
        _story(f"group-{index}-1234567890", f"Group Story {index}", "top_stories")
        for index in range(10)
    ]
    local_articles = {
        story.id: _article(
            story.id,
            source_name=f"Source {index}",
            paragraphs=["Saved paragraph."],
        )
        for index, story in enumerate(stories)
    }

    library = build_row_one_saved_article_library(_edition(*stories), local_articles)

    assert library is not None
    assert library.source_count == 10
    assert len(library.groups) == 8
    assert [group.source_name for group in library.groups] == [
        f"Source {index}" for index in range(8)
    ]
```

Expected RED: importing `fashion_radar.row_one.saved_article_library` fails.

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py -q
```

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement the builder**

Create `src/fashion_radar/row_one/saved_article_library.py` with:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLibraryParagraphLink:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedArticleLibraryEntry:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    digest_path: str
    reader_path: str
    evidence_path: str
    paragraph_links: tuple[RowOneSavedArticleLibraryParagraphLink, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleLibrarySourceGroup:
    source_name: str
    article_count: int
    saved_paragraph_count: int
    organized_section_count: int
    entries: list[RowOneSavedArticleLibraryEntry]


@dataclass(frozen=True)
class RowOneSavedArticleLibrary:
    article_count: int
    source_count: int
    saved_paragraph_count: int
    organized_section_count: int
    groups: list[RowOneSavedArticleLibrarySourceGroup]
```

Implement `build_row_one_saved_article_library()` with helper functions for source normalization, section title fallback, paragraph count, organized section count, deduped references, and strict paragraph-index filtering. Count organized sections as `len(article.content_sections)` to match `saved_article_coverage.py`. For paragraph links, accept only zero-based paragraph indices that are integers but not booleans, map them to nonblank saved paragraphs, dedupe them, and render one-based fragments such as `#local-article-paragraph-1`. Use fixed fragments only:

```python
LOCAL_ARTICLE_DIGEST_FRAGMENT = "local-article-digest"
LOCAL_ARTICLE_READER_FRAGMENT = "local-article-reader"
LOCAL_ARTICLE_EVIDENCE_FRAGMENT = "local-article-paragraph-evidence"
LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph"
```

- [ ] **Step 4: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py -q
```

Expected: PASS.

## Task 2: Render Library Page And Homepage Entry

- [ ] **Step 1: Write failing render tests**

Modify `tests/test_row_one_render.py` to add:

```python
def test_render_row_one_site_writes_saved_article_library_page(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title='The Row <source>',
        url="https://example.com/the-row",
        source_name="Vogue <Business>",
        extracted_at=AS_OF,
        paragraphs=['First local paragraph with <signals>.', "Second paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="品牌与人物", en="People & Brands"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(zh="The Row 正文。", en="The Row body."),
                        paragraph_indices=[0],
                        references=[
                            RowOneReference(name="<The Row>", type="brand", label="tracked")
                        ],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    library_path = tmp_path / "articles" / "index.html"
    assert library_path.exists()
    html = library_path.read_text(encoding="utf-8")
    home_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert '<link rel="stylesheet" href="../assets/row-one.css">' in html
    assert '<script src="../assets/row-one.js"></script>' in html
    assert "Daily Saved Article Library" in html
    assert "每日本地文章库" in html
    assert "Vogue &lt;Business&gt;" in html
    assert "The Row &lt;source&gt;" in html
    assert "&lt;The Row&gt;" in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-reader"' in html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert 'href="articles/index.html"' in home_html
    assert 'class="saved-article-library-entry"' in home_html
```

Also add:

```python
def test_render_row_one_site_omits_saved_article_library_without_saved_articles(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    assert not (tmp_path / "articles" / "index.html").exists()
    assert "saved-article-library-entry" not in (tmp_path / "index.html").read_text(encoding="utf-8")
```

And add:

```python
def test_render_row_one_site_latest_only_removes_stale_saved_article_library(tmp_path) -> None:
    stale_articles = tmp_path / "articles"
    stale_articles.mkdir(parents=True)
    (stale_articles / "index.html").write_text("stale", encoding="utf-8")
    (tmp_path / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    render_row_one_site(_edition(), tmp_path, latest_only=True)

    assert not stale_articles.exists()
```

Expected RED: render does not create the page, homepage entry, or cleanup behavior.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: FAIL on the new Stage 326 assertions.

- [ ] **Step 3: Implement render integration**

Modify `render.py`:

- import `build_row_one_saved_article_library`
- add `"articles"` to `GENERATED_CHILDREN`
- build `saved_article_library` after saved article content organization
- pass `saved_article_library` into `render_index_html()`
- write `articles/index.html` through a private `_write_saved_article_library_page()`

Modify `templates.py`:

- import `RowOneSavedArticleLibrary`
- add `saved_article_library: RowOneSavedArticleLibrary | None = None` to `render_index_html()`
- render a homepage entry with a fixed `href="articles/index.html"`
- add public `render_saved_article_library_html(edition, library)` for the generated page
- use `_esc()` for all display values
- prefix library-page detail links with `../`
- insert the homepage entry after saved article coverage and before saved article briefs
- add a short code comment near the `articles` writer or `GENERATED_CHILDREN` entry explaining that top-level `articles/` is generated HTML and distinct from `data/articles/` JSON sidecars

- [ ] **Step 4: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS.

- [ ] **Step 5: Add CSS selector test**

Add a focused `row_one_css()` test near the existing CSS selector tests:

```python
def test_row_one_css_includes_saved_article_library_styles() -> None:
    css = row_one_css()

    for selector in (
        ".saved-article-library-entry",
        ".saved-article-library-entry-header",
        ".saved-article-library-entry-metrics",
        ".saved-article-library-page",
        ".saved-article-library-hero",
        ".saved-article-library-metrics",
        ".saved-article-library-source",
        ".saved-article-library-grid",
        ".saved-article-library-card",
        ".saved-article-library-card-meta",
        ".saved-article-library-actions",
        ".saved-article-library-refs",
        ".saved-article-library-paragraphs",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css)
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_row_one_css_includes_saved_article_library_styles -q
```

Expected: PASS after CSS is implemented.

## Task 3: Add Workflow Boundary Tests And Documentation

- [ ] **Step 1: Write failing docs and workflow tests**

Modify `tests/test_workflows.py` to assert generated HTML can contain `saved-article-library`, but JSON contracts do not contain:

```python
"saved_article_library",
"daily_saved_article_library",
"article_library",
"saved-article-library",
"Daily Saved Article Library",
```

Modify `tests/test_row_one_docs.py` to assert README and `docs/row-one.md` mention:

```python
"Stage 326"
"articles/index.html"
"generated-site only"
"does not change row-one-app/v7"
"does not add source collection, fetching, scoring, LLM, connector, scheduling, deployment, or compliance-review behavior"
```

Also update `test_row_one_docs_describe_generated_files_and_cleanup_boundary()` so the Generated Files inventory includes `articles/index.html` or `articles/` as a generated HTML child removed by latest-only cleanup.

Expected RED: docs do not contain the new Stage 326 language.

- [ ] **Step 2: Run boundary tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: FAIL on the new Stage 326 docs/boundary assertions.

- [ ] **Step 3: Update README and ROW ONE docs**

Add short Stage 326 generated-site-only notes to `README.md` and `docs/row-one.md`. Use exact, conservative wording:

```markdown
Stage 326 adds a generated-site only ROW ONE daily saved article library at `articles/index.html`. It organizes the current edition's saved local articles by source and links back into existing detail-page local article anchors without changing `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, JSON artifacts, source collection, fetching, scoring, LLM, connector, scheduling, deployment, or compliance-review behavior.
```

Also update the Generated Files inventory in `docs/row-one.md` to list:

```markdown
- `articles/index.html` when the current edition has publishable saved local articles for the daily saved article library
```

- [ ] **Step 4: Run boundary tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: PASS.

## Task 4: Full Verification, Review, Commit, Push

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Create Claude Code review prompt and request code review**

Create `docs/reviews/claude-code-stage-326-code-review-prompt.md` with the Stage 326 goal, spec, plan, verification commands, and git diff range. Run Claude Code with max effort. Save the completed review to `docs/reviews/claude-code-stage-326-code-review.md` only if it returns usable findings. If Claude Code times out or returns only an API error, record that in the Claude Code review file, then run opencode with `glm-5.2` and save the completed fallback review to `docs/reviews/opencode-stage-326-code-review.md`.

- [ ] **Step 4: Fix Critical and Important findings**

If Claude Code reports Critical or Important findings, fix them with TDD where behavior changes are needed, rerun focused and relevant full checks, and rerequest review until Critical and Important are clear.

- [ ] **Step 5: Secret scan, commit, push**

Run:

```bash
git grep -n -E 'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9]+' -- . ':!docs/reviews/*'
git status --short --branch
git add src/fashion_radar/row_one/saved_article_library.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/specs/2026-07-07-stage-326-row-one-daily-saved-article-library-design.md docs/superpowers/plans/2026-07-07-stage-326-row-one-daily-saved-article-library-plan.md docs/reviews/claude-code-stage-326-plan-review-prompt.md docs/reviews/opencode-stage-326-plan-review-prompt.md docs/reviews/opencode-stage-326-plan-review.md docs/reviews/opencode-stage-326-plan-rereview-prompt.md docs/reviews/opencode-stage-326-plan-rereview.md docs/reviews/claude-code-stage-326-code-review-prompt.md docs/reviews/claude-code-stage-326-code-review.md docs/reviews/opencode-stage-326-code-review-prompt.md docs/reviews/opencode-stage-326-code-review.md
git commit -m "Stage 326: add row one saved article library"
git push origin main
git status --short --branch
git ls-remote origin refs/heads/main
```

Expected: no secret hits, commit succeeds, push succeeds, local branch is clean and matches `origin/main`.

## Self-Review

- Spec coverage: the plan covers builder, generated page, homepage entry, cleanup, tests, docs, review, and push.
- Placeholder scan: no task uses TBD, TODO, or unspecified implementation language.
- Type consistency: all new names use `RowOneSavedArticleLibrary*` and remain render-only dataclasses, not Pydantic contract models.
- Scope check: this is one generated-site feature and does not alter collection, extraction, contracts, scheduling, deployment, social connectors, or compliance behavior.
