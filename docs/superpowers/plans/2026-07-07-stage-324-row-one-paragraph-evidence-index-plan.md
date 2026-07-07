# Stage 324 ROW ONE Paragraph Evidence Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site only ROW ONE detail-page paragraph evidence index that maps saved local article paragraphs back to existing organized content sections, item labels, and references.

**Architecture:** Keep the feature entirely in generated detail HTML. Add private render-only helpers in `templates.py` that build capped evidence entries from existing `RowOneLocalArticle.content_sections[*].items[*].paragraph_indices`, using existing rendered paragraph validation and existing fragment anchor helpers. Extend focused render/workflow/docs tests and documentation while preserving `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, Pydantic models, source acquisition, and JSON artifacts.

**Tech Stack:** Python, existing ROW ONE Pydantic models, existing string-rendered HTML/CSS in `templates.py`, existing `render_row_one_site()` pipeline, pytest, Ruff, Claude Code review gates.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Add constants for paragraph evidence row/item/ref caps.
  - Add private dataclasses for evidence items and entries.
  - Add helpers that build and render paragraph evidence entries from existing local article content sections.
  - Add an optional evidence map link when the evidence index exists.
  - Render the new section inside `#local-article`, after the map and before digest/reader/brief/content sections.
  - Add CSS selectors for the new section.
- Modify: `tests/test_row_one_render.py`
  - Add Stage 324 render, omission, safety, escaping, cap, and CSS tests.
  - Import `_strict_valid_local_article_paragraph_indices` from `fashion_radar.row_one.templates`.
- Modify: `tests/test_workflows.py`
  - Extend generated-site boundary assertions for Stage 324 private markers not entering JSON contracts.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 324 docs boundary test.
- Modify: `README.md`
  - Add Stage 324 generated-site only paragraph.
- Modify: `docs/row-one.md`
  - Add Stage 324 generated-site only paragraph.
- Create: `docs/reviews/claude-code-stage-324-plan-review-prompt.md`
- Create if Claude Code returns a completed review: `docs/reviews/claude-code-stage-324-plan-review.md`
- Create if Claude Code is unavailable: `docs/reviews/opencode-stage-324-plan-review-prompt.md`
- Create if Claude Code is unavailable: `docs/reviews/opencode-stage-324-plan-review.md`
- Create if fallback plan review needs rereview: `docs/reviews/opencode-stage-324-plan-rereview-prompt.md`
- Create if fallback plan review needs rereview: `docs/reviews/opencode-stage-324-plan-rereview.md`
- Create after implementation: `docs/reviews/claude-code-stage-324-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-324-code-review.md`

## Task 1: Add Failing Render Tests

- [ ] **Step 1: Add a detail evidence-index render test**

Add near the existing local article render tests in `tests/test_row_one_render.py`:

```python
def test_render_row_one_detail_includes_local_article_paragraph_evidence_index() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    detail_html = render_detail_html(edition, story, local_article=local_article)

    assert 'id="local-article-paragraph-evidence"' in detail_html
    assert 'class="local-article-paragraph-evidence"' in detail_html
    assert "Saved Paragraph Evidence" in detail_html
    assert "本地段落线索" in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-content-section-1"' in detail_html
    assert "People &amp; Brands" in detail_html
    assert "The Row" in detail_html
    assert detail_html.index('class="local-article-map"') < detail_html.index(
        'id="local-article-paragraph-evidence"'
    )
    assert detail_html.index('id="local-article-paragraph-evidence"') < detail_html.index(
        'id="local-article-digest"'
    )
```

Expected RED: fails because the evidence index section and map link do not exist.

- [ ] **Step 2: Add an omission test**

```python
def test_render_row_one_detail_omits_local_article_paragraph_evidence_without_matches() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(en="No paragraph mapping", zh="没有段落映射"),
                            references=[],
                            paragraph_indices=[],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)

    assert 'id="local-article-paragraph-evidence"' not in detail_html
    assert 'href="#local-article-paragraph-evidence"' not in detail_html
```

Expected RED after Step 1 implementation if the evidence index renders unconditionally.

- [ ] **Step 3: Add invalid-index filtering test**

```python
def test_render_row_one_detail_paragraph_evidence_filters_invalid_indices() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": ["First saved paragraph.", "", "Third saved paragraph."],
            "paragraphs_zh": ["第一段。", "", "第三段。"],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="The Row", zh="The Row"),
                            body=LocalizedText(en="Uses filtered mappings", zh="使用过滤映射"),
                            references=[],
                            paragraph_indices=[-1, 0, 1, 2, 2, 99],
                        )
                    ],
                )
            ],
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'href="#local-article-paragraph-1"' in evidence_html
    assert 'href="#local-article-paragraph-3"' in evidence_html
    assert 'href="#local-article-paragraph-0"' not in evidence_html
    assert 'href="#local-article-paragraph-2"' not in evidence_html
    assert 'href="#local-article-paragraph-100"' not in evidence_html
    assert evidence_html.count('class="local-article-paragraph-evidence-row"') == 2
    assert evidence_html.count('href="#local-article-paragraph-3"') == 1
```

Expected RED: filtering helper does not exist for the new index.

- [ ] **Step 4: Add strict helper bool filtering test**

Extend the import from `fashion_radar.row_one.templates` with `_strict_valid_local_article_paragraph_indices`, then add:

```python
def test_strict_valid_local_article_paragraph_evidence_indices_rejects_bool_values() -> None:
    assert _strict_valid_local_article_paragraph_indices(
        [True, False, 0, 0, 1, "2", 2],
        {0, 2},
    ) == [0, 2]
```

Expected RED: `_strict_valid_local_article_paragraph_indices` is not defined.

- [ ] **Step 5: Add escaping test**

```python
def test_render_row_one_detail_paragraph_evidence_escapes_values() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": ['<script>alert("p")</script> paragraph'],
            "paragraphs_zh": ['<script>alert("zh")</script> 段落'],
            "content_sections": [
                RowOneLocalArticleContentSection(
                    key="entities",
                    title=LocalizedText(en="<script>Section</script>", zh="<script>栏目</script>"),
                    body=None,
                    items=[
                        RowOneLocalArticleContentItem(
                            label=LocalizedText(en="<script>Label</script>", zh="<script>标签</script>"),
                            body=LocalizedText(
                                en='<img src=x onerror="alert(1)"> body',
                                zh='<img src=x onerror="alert(2)"> 正文',
                            ),
                            references=[
                                RowOneReference(
                                    name="<script>Ref</script>",
                                    type="brand<script>",
                                    label="hot<script>",
                                )
                            ],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ],
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'class="local-article-reader"'
        )
    ]

    assert "<script>" not in evidence_html
    assert '<img src=x onerror="alert' not in evidence_html
    assert "&lt;script&gt;Section&lt;/script&gt;" in evidence_html
    assert "&lt;script&gt;Label&lt;/script&gt;" in evidence_html
    assert "&lt;script&gt;Ref&lt;/script&gt;" in evidence_html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; body" in evidence_html
```

Expected RED: evidence output does not exist.

- [ ] **Step 6: Add cap test**

```python
def test_render_row_one_detail_paragraph_evidence_caps_rows_items_and_refs() -> None:
    edition = _edition()
    story = edition.stories[0]
    paragraphs = [f"Saved paragraph {index}" for index in range(12)]
    sections = [
        RowOneLocalArticleContentSection(
            key="entities",
            title=LocalizedText(en="People & Brands", zh="品牌与人物"),
            body=None,
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(en=f"Item {item_index}", zh=f"条目 {item_index}"),
                    body=LocalizedText(en=f"Body {item_index}", zh=f"正文 {item_index}"),
                    references=[
                        RowOneReference(name=f"Ref {ref_index}", type="brand", label="hot")
                        for ref_index in range(6)
                    ],
                    paragraph_indices=list(range(12)),
                )
                for item_index in range(6)
            ],
        )
    ]
    local_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "paragraphs": paragraphs,
            "paragraphs_zh": [f"保存段落 {index}" for index in range(12)],
            "content_sections": sections,
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'class="local-article-reader"'
        )
    ]

    assert evidence_html.count('class="local-article-paragraph-evidence-row"') == 8
    assert evidence_html.count('class="local-article-paragraph-evidence-support"') == 32
    assert evidence_html.count('class="local-article-paragraph-evidence-ref"') == 128
    assert 'href="#local-article-paragraph-9"' not in evidence_html
```

Expected RED: no capped index exists.

- [ ] **Step 7: Add CSS selector test**

Extend `test_row_one_css_includes_local_article_map_styles` in `tests/test_row_one_render.py` with:

```python
        ".local-article-paragraph-evidence",
        ".local-article-paragraph-evidence-header",
        ".local-article-paragraph-evidence-grid",
        ".local-article-paragraph-evidence-row",
        ".local-article-paragraph-evidence-link",
        ".local-article-paragraph-evidence-excerpt",
        ".local-article-paragraph-evidence-support",
        ".local-article-paragraph-evidence-supports",
        ".local-article-paragraph-evidence-ref",
```

Expected RED: selectors are not in the generated CSS.

- [ ] **Step 8: Run focused render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  -k "paragraph_evidence or local_article_map_styles" -q
```

Expected: the newly added tests fail because Stage 324 is not implemented yet.

## Task 2: Implement Paragraph Evidence Rendering

- [ ] **Step 1: Add constants and private dataclasses**

In `src/fashion_radar/row_one/templates.py`, near the existing local article constants and private dataclasses, add:

```python
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS = 8
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS = 4
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS = 140
LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS = 120
```

Add private dataclasses:

```python
@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceItem:
    section_position: int
    section_title: LocalizedText
    item_label: LocalizedText
    item_body: LocalizedText | None
    references: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class _LocalArticleParagraphEvidenceEntry:
    paragraph_index: int
    excerpt: LocalizedText
    items: tuple[_LocalArticleParagraphEvidenceItem, ...]
```

- [ ] **Step 2: Add a strict paragraph-index helper**

Add below `_valid_local_article_paragraph_indices()`:

```python
def _strict_valid_local_article_paragraph_indices(
    indices: Sequence[object],
    rendered_indices: set[int],
) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if not isinstance(index, int) or isinstance(index, bool):
            continue
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid
```

- [ ] **Step 3: Add builder helpers**

Add below the strict helper:

```python
def _local_article_paragraph_evidence_entries(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> tuple[_LocalArticleParagraphEvidenceEntry, ...]:
    mapped: dict[int, list[_LocalArticleParagraphEvidenceItem]] = {}
    seen_items: dict[int, set[tuple[object, ...]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        for item in section.items:
            valid_indices = _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            )
            if not valid_indices:
                continue
            evidence_item = _local_article_paragraph_evidence_item(
                section=section,
                section_position=section_position,
                item=item,
            )
            dedupe_key = _local_article_paragraph_evidence_item_key(evidence_item)
            for index in valid_indices:
                item_keys = seen_items.setdefault(index, set())
                if dedupe_key in item_keys:
                    continue
                item_keys.add(dedupe_key)
                mapped.setdefault(index, []).append(evidence_item)
    if not mapped:
        return ()
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    entries: list[_LocalArticleParagraphEvidenceEntry] = []
    for index in sorted(mapped):
        excerpt_en = _local_article_paragraph_evidence_excerpt(article.paragraphs[index])
        if aligned_zh and aligned_zh[index].strip():
            excerpt_zh = _local_article_paragraph_evidence_excerpt(aligned_zh[index])
        else:
            excerpt_zh = excerpt_en
        entries.append(
            _LocalArticleParagraphEvidenceEntry(
                paragraph_index=index,
                excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh),
                items=tuple(mapped[index][:LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ITEMS]),
            )
        )
        if len(entries) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_ROWS:
            break
    return tuple(entries)
```

Add the item/key/excerpt helpers:

```python
def _local_article_paragraph_evidence_item(
    *,
    section: RowOneLocalArticleContentSection,
    section_position: int,
    item: RowOneLocalArticleContentItem,
) -> _LocalArticleParagraphEvidenceItem:
    refs: list[RowOneReference] = []
    seen_refs: set[tuple[str, str, str]] = set()
    for ref in item.references:
        dedupe_key = (
            normalize_row_one_paragraph(ref.name).casefold(),
            normalize_row_one_paragraph(ref.type).casefold(),
            normalize_row_one_paragraph(ref.label).casefold(),
        )
        if dedupe_key in seen_refs:
            continue
        seen_refs.add(dedupe_key)
        refs.append(ref)
        if len(refs) >= LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_MAX_REFS:
            break
    return _LocalArticleParagraphEvidenceItem(
        section_position=section_position,
        section_title=section.title,
        item_label=item.label,
        item_body=item.body,
        references=tuple(refs),
    )


def _local_article_paragraph_evidence_item_key(
    item: _LocalArticleParagraphEvidenceItem,
) -> tuple[object, ...]:
    return (
        item.section_position,
        normalize_row_one_paragraph(item.section_title.en).casefold(),
        normalize_row_one_paragraph(item.section_title.zh).casefold(),
        normalize_row_one_paragraph(item.item_label.en).casefold(),
        normalize_row_one_paragraph(item.item_label.zh).casefold(),
        normalize_row_one_paragraph(item.item_body.en).casefold() if item.item_body else "",
        normalize_row_one_paragraph(item.item_body.zh).casefold() if item.item_body else "",
        tuple(
            (
                normalize_row_one_paragraph(ref.name).casefold(),
                normalize_row_one_paragraph(ref.type).casefold(),
                normalize_row_one_paragraph(ref.label).casefold(),
            )
            for ref in item.references
        ),
    )


def _local_article_paragraph_evidence_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_EXCERPT_CHARS,
    )
```

- [ ] **Step 4: Add renderer helpers**

Add below the builder helpers:

```python
def _render_local_article_paragraph_evidence(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
    entries = _local_article_paragraph_evidence_entries(
        article,
        rendered_indices=rendered_indices,
    )
    if not entries:
        return ""
    rendered_entries = "\n".join(_render_local_article_paragraph_evidence_entry(entry) for entry in entries)
    return f"""      <div id="local-article-paragraph-evidence" class="local-article-paragraph-evidence" aria-label="Saved paragraph evidence">
        <div class="local-article-paragraph-evidence-header">
          <h4>
            <span data-lang="en">Saved Paragraph Evidence</span>
            <span data-lang="zh">本地段落线索</span>
          </h4>
          <p>
            <span data-lang="en">Saved paragraphs used by the organized ROW ONE reading path.</span>
            <span data-lang="zh">被 ROW ONE 正文整理引用的本地保存段落。</span>
          </p>
        </div>
        <div class="local-article-paragraph-evidence-grid">
{rendered_entries}
        </div>
      </div>"""
```

Add entry/item/ref renderers:

```python
def _render_local_article_paragraph_evidence_entry(
    entry: _LocalArticleParagraphEvidenceEntry,
) -> str:
    paragraph_number = entry.paragraph_index + 1
    paragraph_href = f"#{_local_article_paragraph_anchor(entry.paragraph_index)}"
    supports = "\n".join(
        _render_local_article_paragraph_evidence_support(item) for item in entry.items
    )
    return f"""          <article class="local-article-paragraph-evidence-row">
            <a class="local-article-paragraph-evidence-link" href="{_esc(paragraph_href)}">
              <span data-lang="en">Paragraph {paragraph_number}</span>
              <span data-lang="zh">段落 {paragraph_number}</span>
            </a>
            <p class="local-article-paragraph-evidence-excerpt">
              <span data-lang="en">{_esc(entry.excerpt.en)}</span>
              <span data-lang="zh">{_esc(entry.excerpt.zh)}</span>
            </p>
            <div class="local-article-paragraph-evidence-supports">
{supports}
            </div>
          </article>"""


def _render_local_article_paragraph_evidence_support(
    item: _LocalArticleParagraphEvidenceItem,
) -> str:
    section_href = f"#{_local_article_content_section_anchor(item.section_position)}"
    body = ""
    if item.item_body is not None:
        body = (
            '                <p>'
            f'<span data-lang="en">{_esc(_local_article_paragraph_evidence_body(item.item_body.en))}</span>'
            f'<span data-lang="zh">{_esc(_local_article_paragraph_evidence_body(item.item_body.zh))}</span>'
            "</p>\n"
        )
    refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
    return f"""              <div class="local-article-paragraph-evidence-support">
                <a href="{_esc(section_href)}">
                  <span data-lang="en">{_esc(item.section_title.en)}</span>
                  <span data-lang="zh">{_esc(item.section_title.zh)}</span>
                </a>
                <strong>
                  <span data-lang="en">{_esc(item.item_label.en)}</span>
                  <span data-lang="zh">{_esc(item.item_label.zh)}</span>
                </strong>
{body}                <div>{refs}</div>
              </div>"""


def _local_article_paragraph_evidence_body(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_BODY_CHARS,
    )


def _render_local_article_paragraph_evidence_ref(ref: RowOneReference) -> str:
    label = f"{ref.name} ({ref.type} / {ref.label})"
    return f'<span class="local-article-paragraph-evidence-ref">{_esc(label)}</span>'
```

- [ ] **Step 5: Wire the renderer into `_render_local_article()` and `_render_local_article_map()`**

In `_render_local_article()`, compute `rendered_indices` once and render evidence before the map call:

```python
rendered_indices = _local_article_rendered_paragraph_indices(article)
paragraph_evidence = _render_local_article_paragraph_evidence(
    article,
    rendered_indices=rendered_indices,
)
article_map = _render_local_article_map(
    article,
    include_digest=bool(digest),
    include_reader=bool(reader),
    include_paragraph_evidence=bool(paragraph_evidence),
)
content_sections = _render_local_article_content_sections(
    article,
    rendered_indices=rendered_indices,
)
```

Place `{paragraph_evidence}` immediately after `{article_map}` and before `{digest}`.

Update `_render_local_article_map()` signature:

```python
def _render_local_article_map(
    article: RowOneLocalArticle,
    *,
    include_digest: bool = False,
    include_reader: bool = False,
    include_paragraph_evidence: bool = False,
) -> str:
```

Add the map link before the digest link:

```python
if include_paragraph_evidence:
    links.append(
        '<a href="#local-article-paragraph-evidence">'
        '<span data-lang="en">Evidence</span>'
        '<span data-lang="zh">线索</span>'
        "</a>"
    )
```

- [ ] **Step 6: Add CSS**

In `row_one_css()` output in `templates.py`, near the existing local article map/reader/digest/content styles, add compact styles for:

```css
.local-article-paragraph-evidence { ... }
.local-article-paragraph-evidence-header { ... }
.local-article-paragraph-evidence-grid { ... }
.local-article-paragraph-evidence-row { ... }
.local-article-paragraph-evidence-link { ... }
.local-article-paragraph-evidence-excerpt { ... }
.local-article-paragraph-evidence-supports { ... }
.local-article-paragraph-evidence-support { ... }
.local-article-paragraph-evidence-support a { ... }
.local-article-paragraph-evidence-ref { ... }
```

Use existing colors, borders, spacing, and responsive conventions. Do not introduce new dependencies.

- [ ] **Step 7: Run focused render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  -k "paragraph_evidence or local_article_map_styles" -q
```

Expected: all selected tests pass.

## Task 3: Add Workflow Boundary Test

- [ ] **Step 1: Extend generated-site workflow assertions**

In `tests/test_workflows.py`, in the ROW ONE generated-site workflow test:

Add HTML marker assertions near existing detail HTML assertions:

```python
assert "Saved Paragraph Evidence" in detail_html
assert "本地段落线索" in detail_html
assert 'id="local-article-paragraph-evidence"' in detail_html
```

Extend the generated JSON absence assertions:

```python
assert '"local_article_paragraph_evidence"' not in generated_contract_payload
assert '"paragraph_evidence_index"' not in generated_contract_payload
assert '"local_evidence_index"' not in generated_contract_payload
assert '"evidence_paragraph_index"' not in generated_contract_payload
```

- [ ] **Step 2: Run focused workflow test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k "row_one" -q
```

Expected: selected workflow tests pass.

## Task 4: Add Documentation And Docs Tests

- [ ] **Step 1: Add docs boundary test**

In `tests/test_row_one_docs.py`, add near the Stage 323 docs boundary test:

```python
def test_row_one_docs_describe_stage_324_paragraph_evidence_index_boundary() -> None:
    readme = _normalized(_read(README))
    docs = _normalized(_read(ROW_ONE_DOC))

    for content in (readme, docs):
        stage = content[
            content.index("stage 324 adds paragraph evidence index") : content.index(
                "stage 323 adds local-first reading"
            )
        ]
        for phrase in (
            "paragraph evidence index",
            "saved paragraph evidence",
            "`rowonelocalarticle.content_sections`",
            "`paragraph_indices`",
            "`references`",
            "`#local-article-paragraph-n`",
            "`#local-article-content-section-n`",
            "generated-site only",
            "does not change `row-one-app/v7`",
            "does not change `data/edition.json`",
            "does not change `row-one-manifest/v1`",
            "does not change `row-one-runtime/v1`",
            "does not add source collection",
            "does not add scoring",
            "does not add connectors",
            "does not add llm calls",
            "does not add compliance-review product features",
        ):
            assert phrase in stage
```

- [ ] **Step 2: Add README paragraph**

Insert above the Stage 323 paragraph in `README.md`:

```markdown
Stage 324 adds Paragraph Evidence Index to generated ROW ONE detail pages. It is
generated-site only and turns existing `RowOneLocalArticle.content_sections`
items with existing `paragraph_indices`, existing `references`, existing
`#local-article-paragraph-N` anchors, and existing
`#local-article-content-section-N` anchors into a compact saved paragraph
evidence index with safe internal links. It does not change `row-one-app/v7`,
does not change `data/edition.json`, does not change `row-one-manifest/v1`,
does not change `row-one-runtime/v1`, does not add
`local_article_paragraph_evidence`, does not add `paragraph_evidence_index`,
does not change schemas, does not write a new JSON artifact, does not add source
collection, does not fetch article pages, does not add extraction, does not add
scoring, does not add ranking, does not add LLM calls, does not add translation
calls, does not add image generation, does not add connectors, does not add
scheduling, does not add deployment behavior, and does not add
compliance-review product features.
```

- [ ] **Step 3: Add docs paragraph**

Insert the same Stage 324 paragraph above Stage 323 in `docs/row-one.md`, keeping the wording aligned with README.

- [ ] **Step 4: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: docs tests pass.

## Task 5: Verification, Review, Commit, Push

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  -k "paragraph_evidence or local_article_map_styles" -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k "row_one" -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: all focused checks pass.

- [ ] **Step 2: Run full project verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Request Claude Code code review**

Create:

- `docs/reviews/claude-code-stage-324-code-review-prompt.md`
- `docs/reviews/claude-code-stage-324-code-review.md`

Run:

```bash
claude --bare --effort max --permission-mode plan --no-session-persistence --print "$(cat docs/reviews/claude-code-stage-324-code-review-prompt.md)"
```

Expected: no unresolved Critical or Important findings. Fix any Critical or Important finding, rerun focused/full verification, and request rereview before committing.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add README.md docs/row-one.md docs/reviews/claude-code-stage-324-code-review-prompt.md docs/reviews/claude-code-stage-324-code-review.md docs/reviews/claude-code-stage-324-plan-review-prompt.md docs/reviews/claude-code-stage-324-plan-review.md docs/superpowers/specs/2026-07-07-stage-324-row-one-paragraph-evidence-index-design.md docs/superpowers/plans/2026-07-07-stage-324-row-one-paragraph-evidence-index-plan.md src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
git commit -m "Stage 324: add row one paragraph evidence index"
git push origin main
```

Expected: push succeeds and `git status --short --branch` reports `## main...origin/main`.
