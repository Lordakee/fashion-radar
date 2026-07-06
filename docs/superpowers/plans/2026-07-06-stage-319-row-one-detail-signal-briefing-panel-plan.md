# Stage 319 ROW ONE Detail Signal Briefing Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only `Signal Briefing / 信号简报` panel to ROW ONE detail pages so each article organizes existing story fields, references, and saved local article cues into a concise briefing surface.

**Architecture:** Keep the feature in deterministic HTML/CSS inside `templates.py`. Reuse `RowOneStory` fields and optional `RowOneLocalArticle` sidecar structure already passed into `render_detail_html()`. Do not write new data artifacts or change app/runtime/manifest/schema contracts.

**Tech Stack:** Python, string-rendered HTML/CSS, existing ROW ONE Pydantic models, pytest, Ruff, Claude Code plan/code review workflow.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-319-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-319-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-319-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-319-code-review.md`

---

### Task 1: Detail Signal Briefing Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add a local article fixture helper for signal briefing tests**

Add this helper near the existing `_edition_with_stories()` helper:

```python
def _signal_briefing_local_article() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Signal source article",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        published_at=AS_OF,
        paragraphs=[
            "The Row Margaux bag appears in saved source text.",
            "Alaia flats appear in saved source text.",
            "A third saved paragraph carries styling context.",
        ],
        paragraphs_zh=[
            "The Row Margaux 手袋出现在保存正文中。",
            "Alaia 平底鞋出现在保存正文中。",
            "第三个保存段落提供造型背景。",
        ],
        brief_sections=[
            RowOneLocalArticleBriefSection(
                key="what_happened",
                title=LocalizedText(en="What Happened", zh="发生了什么"),
                body=LocalizedText(en="The saved article frames a new signal.", zh="保存正文呈现了新信号。"),
            ),
            RowOneLocalArticleBriefSection(
                key="why_it_matters",
                title=LocalizedText(en="Why It Matters", zh="为什么重要"),
                body=LocalizedText(en="It changes the read on quiet luxury.", zh="这改变了静奢解读。"),
            ),
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                body=LocalizedText(en="Brand context from saved text.", zh="保存正文中的品牌背景。"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="The Row", zh="The Row"),
                        body=LocalizedText(en="The Row appears in paragraph one.", zh="The Row 出现在第一段。"),
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                            RowOneReference(name="The Row", type="brand", label="tracked"),
                        ],
                        paragraph_indices=[0, 1],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(en="Products", zh="单品"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Alaia flats", zh="Alaia 平底鞋"),
                        body=LocalizedText(en="Alaia flats appear in paragraph two.", zh="Alaia 平底鞋出现在第二段。"),
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product"),
                        ],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )
```

- [ ] **Step 2: Add the primary failing render test**

Add this test near the existing detail-page render tests:

```python
def test_render_row_one_detail_includes_signal_briefing_panel(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={
            "headline": "The Row <script>signal</script>",
            "summary": LocalizedText(
                en="Original source summary: <b>The Row signal</b> is moving.",
                zh="来源摘要：<b>The Row 信号</b>正在变化。",
            ),
            "signal_context": LocalizedText(
                en="Signal context <script>alert(1)</script>.",
                zh="信号背景 <script>alert(1)</script>。",
            ),
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="tracked"),
                RowOneReference(name="The Row", type="brand", label="tracked"),
            ],
            "designer_refs": [
                RowOneReference(name="Mary-Kate Olsen", type="designer", label="person"),
            ],
            "product_refs": [
                RowOneReference(name="Margaux", type="bag", label="product"),
                RowOneReference(
                    name="Signal <script>Brand</script>",
                    type="brand",
                    label="unsafe",
                ),
            ],
        },
    )
    html = render_detail_html(edition, story, local_article=_signal_briefing_local_article())

    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert panel_start < html.index('id="summary"')
    assert '<span data-lang="en">Signal Briefing</span>' in panel_html
    assert '<span data-lang="zh">信号简报</span>' in panel_html
    assert '<span data-lang="en">What To Know</span>' in panel_html
    assert '<span data-lang="zh">重点整理</span>' in panel_html
    assert '<span data-lang="en">Signal</span>' in panel_html
    assert '<span data-lang="zh">信号</span>' in panel_html
    assert "The Row signal is moving." in panel_html
    assert "&lt;b&gt;" not in panel_html
    assert "<script>" not in panel_html
    assert "Vogue Business" in panel_html
    assert "1 safe evidence link" in panel_html
    assert "1 条安全线索" in panel_html
    assert "Signal context &lt;script&gt;alert(1)&lt;/script&gt;." in panel_html
    assert "The Row" in panel_html
    assert "Mary-Kate Olsen" in panel_html
    assert "Margaux" in panel_html
    assert "Alaia flats" in panel_html
    assert "Signal &lt;script&gt;Brand&lt;/script&gt;" in panel_html
    assert "<script>Brand</script>" not in panel_html
    assert panel_html.count('class="detail-signal-briefing-ref"') == 5
    assert panel_html.count(">The Row<") == 1
    assert "Local Article Cues" in panel_html
    assert "本地正文线索" in panel_html
    assert "What Happened" in panel_html
    assert "Why It Matters" in panel_html
    assert "People &amp; Brands" in panel_html
    assert "Products" not in panel_html
    assert 'href="#local-article-paragraph-1"' in panel_html
    assert 'href="#local-article-paragraph-2"' not in panel_html
    lower_why_start = html.index('id="why-it-matters"')
    lower_why_html = html[lower_why_start : html.index("</section>", lower_why_start)]
    assert panel_start < lower_why_start
    assert "This signal belongs in Top Stories." in lower_why_html
```

- [ ] **Step 3: Add omission and cap tests**

Add:

```python
def test_render_row_one_detail_signal_briefing_omits_local_cues_without_structure() -> None:
    edition = _edition()
    html = render_detail_html(edition, edition.stories[0])

    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert "Signal Briefing" in panel_html
    assert "Local Article Cues" not in panel_html
    assert "本地正文线索" not in panel_html


def test_render_row_one_detail_signal_briefing_caps_references() -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={
            "entity_refs": [
                RowOneReference(name=f"Brand {index}", type="brand", label="tracked")
                for index in range(1, 12)
            ],
        },
    )

    html = render_detail_html(edition, story)
    panel_start = html.index('class="detail-signal-briefing"')
    panel_html = html[panel_start : html.index('id="summary"', panel_start)]

    assert panel_html.count('class="detail-signal-briefing-ref"') == 8
    assert "Brand 1" in panel_html
    assert "Brand 8" in panel_html
    assert "Brand 9" not in panel_html
```

- [ ] **Step 4: Add the CSS selector failing test**

Add near existing CSS tests:

```python
def test_row_one_css_includes_detail_signal_briefing_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".detail-signal-briefing",
        ".detail-signal-briefing-header",
        ".detail-signal-briefing-grid",
        ".detail-signal-briefing-card",
        ".detail-signal-briefing-meta",
        ".detail-signal-briefing-ref",
        ".detail-signal-briefing-cues",
        ".detail-signal-briefing-cue-grid",
        ".detail-signal-briefing-cue",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

- [ ] **Step 5: Verify render and CSS tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_signal_briefing_panel \
  tests/test_row_one_render.py::test_render_row_one_detail_signal_briefing_omits_local_cues_without_structure \
  tests/test_row_one_render.py::test_render_row_one_detail_signal_briefing_caps_references \
  tests/test_row_one_render.py::test_row_one_css_includes_detail_signal_briefing_styles -q
```

Expected: fail because `detail-signal-briefing` is not rendered or styled yet.

---

### Task 2: Detail Signal Briefing Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add constants**

Add near existing detail/local article constants:

```python
DETAIL_SIGNAL_BRIEFING_MAX_REFS = 8
DETAIL_SIGNAL_BRIEFING_MAX_CUES = 3
```

- [ ] **Step 2: Render the panel from `render_detail_html()`**

In `render_detail_html()`, after `detail_information_map`:

```python
    detail_signal_briefing = _render_detail_signal_briefing(story, local_article)
```

Place `{detail_signal_briefing}` after `{detail_information_map}` and before
`<section id="summary">`.

- [ ] **Step 3: Add the panel renderer**

Add before `_render_local_article()`:

```python
def _render_detail_signal_briefing(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    summary = _display_summary_text(story.summary.en)
    summary_zh = _display_summary_text(story.summary.zh)
    safe_evidence_count = sum(
        1 for link in story.evidence if _safe_external_url(link.url) is not None
    )
    evidence_en = _count_label(safe_evidence_count, "safe evidence link", "safe evidence links")
    evidence_zh = f"{safe_evidence_count} 条安全线索"
    references = _render_detail_signal_briefing_references(story, local_article)
    cues = _render_detail_signal_briefing_cues(local_article)
    references_card = (
        f"""        <article class="detail-signal-briefing-card detail-signal-briefing-card--refs">
          <h3>
            <span data-lang="en">Names To Track</span>
            <span data-lang="zh">需要关注</span>
          </h3>
          <div class="detail-signal-briefing-refs">{references}</div>
        </article>"""
        if references
        else ""
    )
    cues_row = (
        f"""      <div class="detail-signal-briefing-cues">
        <h3>
          <span data-lang="en">Local Article Cues</span>
          <span data-lang="zh">本地正文线索</span>
        </h3>
        <div class="detail-signal-briefing-cue-grid">{cues}</div>
      </div>"""
        if cues
        else ""
    )
    return f"""    <section class="detail-signal-briefing" aria-label="Signal briefing">
      <div class="detail-signal-briefing-header">
        <p class="story-section">
          <span data-lang="en">Signal Briefing</span>
          <span data-lang="zh">信号简报</span>
        </p>
        <h2>
          <span data-lang="en">What To Know</span>
          <span data-lang="zh">重点整理</span>
        </h2>
      </div>
      <div class="detail-signal-briefing-grid">
        <article class="detail-signal-briefing-card">
          <h3>
            <span data-lang="en">Signal</span>
            <span data-lang="zh">信号</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(summary)}</span>
            <span data-lang="zh">{_esc(summary_zh)}</span>
          </p>
        </article>
        <article class="detail-signal-briefing-card">
          <h3>
            <span data-lang="en">Why It Matters</span>
            <span data-lang="zh">为什么重要</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(story.why_it_matters.en)}</span>
            <span data-lang="zh">{_esc(story.why_it_matters.zh)}</span>
          </p>
        </article>
        <article class="detail-signal-briefing-card">
          <h3>
            <span data-lang="en">Source Context</span>
            <span data-lang="zh">来源背景</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(story.signal_context.en)}</span>
            <span data-lang="zh">{_esc(story.signal_context.zh)}</span>
          </p>
          <p class="detail-signal-briefing-meta">
            <span>{_esc(story.source_name)}</span>
            <span data-lang="en">{_esc(evidence_en)}</span>
            <span data-lang="zh">{_esc(evidence_zh)}</span>
          </p>
        </article>
{references_card}
      </div>
{cues_row}
    </section>"""
```

If Ruff rejects the long `safe_evidence_count` line, split it over multiple lines.

- [ ] **Step 4: Add reference helpers**

Add:

```python
def _render_detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> str:
    return "".join(
        _render_detail_signal_briefing_ref(ref)
        for ref in _detail_signal_briefing_references(story, local_article)
    )


def _detail_signal_briefing_references(
    story: RowOneStory,
    local_article: RowOneLocalArticle | None,
) -> list[RowOneReference]:
    refs: list[RowOneReference] = []
    refs.extend(story.entity_refs)
    refs.extend(story.designer_refs)
    refs.extend(story.product_refs)
    if local_article is not None:
        for section in local_article.content_sections:
            for item in section.items:
                refs.extend(item.references)
    selected: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for ref in refs:
        key = (ref.name.strip().casefold(), ref.type.strip().casefold(), ref.label.strip().casefold())
        if not key[0] or key in seen:
            continue
        seen.add(key)
        selected.append(ref)
        if len(selected) >= DETAIL_SIGNAL_BRIEFING_MAX_REFS:
            break
    return selected


def _render_detail_signal_briefing_ref(ref: RowOneReference) -> str:
    label = ref.label.strip() or ref.type.strip()
    return (
        '<span class="detail-signal-briefing-ref">'
        f"<span>{_esc(ref.name)}</span>"
        f"<span>{_esc(label)}</span>"
        "</span>"
    )
```

- [ ] **Step 5: Add local article cue helpers**

Add:

```python
def _render_detail_signal_briefing_cues(article: RowOneLocalArticle | None) -> str:
    if article is None:
        return ""
    return "".join(
        _render_detail_signal_briefing_cue(cue)
        for cue in _detail_signal_briefing_cues(article)
    )


def _detail_signal_briefing_cues(
    article: RowOneLocalArticle,
) -> list[tuple[LocalizedText, LocalizedText | None, int | None]]:
    rendered_indices = _local_article_rendered_paragraph_indices(article)
    cues: list[tuple[LocalizedText, LocalizedText | None, int | None]] = []
    for section in article.brief_sections:
        cues.append((section.title, section.body, None))
        if len(cues) >= DETAIL_SIGNAL_BRIEFING_MAX_CUES:
            return cues
    for section in article.content_sections:
        paragraph_index = _first_valid_local_article_paragraph_index(section, rendered_indices)
        cues.append((section.title, section.body, paragraph_index))
        if len(cues) >= DETAIL_SIGNAL_BRIEFING_MAX_CUES:
            return cues
    return cues


def _first_valid_local_article_paragraph_index(
    section: RowOneLocalArticleContentSection,
    rendered_indices: set[int],
) -> int | None:
    paragraph_indices: list[int] = []
    seen_indices: set[int] = set()
    for item in section.items:
        for paragraph_index in item.paragraph_indices:
            if paragraph_index in seen_indices:
                continue
            seen_indices.add(paragraph_index)
            paragraph_indices.append(paragraph_index)
    valid_indices = _valid_local_article_paragraph_indices(
        paragraph_indices,
        rendered_indices,
    )
    return valid_indices[0] if valid_indices else None


def _render_detail_signal_briefing_cue(
    cue: tuple[LocalizedText, LocalizedText | None, int | None],
) -> str:
    title, body, paragraph_index = cue
    body_html = ""
    if body is not None:
        body_html = (
            "<p>"
            f'<span data-lang="en">{_esc(body.en)}</span>'
            f'<span data-lang="zh">{_esc(body.zh)}</span>'
            "</p>"
        )
    link_html = ""
    if paragraph_index is not None:
        href = f"#{_local_article_paragraph_anchor(paragraph_index)}"
        label_en = f"Saved paragraph {paragraph_index + 1}"
        label_zh = f"保存段落 {paragraph_index + 1}"
        link_html = (
            f'<a href="{_esc(href)}">'
            f'<span data-lang="en">{_esc(label_en)}</span>'
            f'<span data-lang="zh">{_esc(label_zh)}</span>'
            "</a>"
        )
    return f"""        <article class="detail-signal-briefing-cue">
          <h4>
            <span data-lang="en">{_esc(title.en)}</span>
            <span data-lang="zh">{_esc(title.zh)}</span>
          </h4>
          {body_html}
          {link_html}
        </article>"""
```

- [ ] **Step 6: Add CSS**

In `row_one_css()` near existing detail/local article rules, add:

```css
.detail-signal-briefing {
  border-top: 1px solid var(--ink);
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  margin: 32px 0;
  padding: 24px 0;
}
.detail-signal-briefing-header {
  display: grid;
  gap: 8px;
}
.detail-signal-briefing-header h2,
.detail-signal-briefing-header p {
  margin: 0;
}
.detail-signal-briefing-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 4.2vw, 4.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.94;
}
.detail-signal-briefing-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.detail-signal-briefing-card,
.detail-signal-briefing-cue {
  background: var(--panel);
  display: grid;
  gap: 10px;
  min-width: 0;
  padding: 16px;
}
.detail-signal-briefing-card h3,
.detail-signal-briefing-card p,
.detail-signal-briefing-cue h4,
.detail-signal-briefing-cue p {
  margin: 0;
}
.detail-signal-briefing-card h3,
.detail-signal-briefing-cues h3 {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.detail-signal-briefing-card p,
.detail-signal-briefing-cue p {
  line-height: 1.45;
}
.detail-signal-briefing-meta,
.detail-signal-briefing-refs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.detail-signal-briefing-meta span,
.detail-signal-briefing-ref {
  border: 1px solid var(--line);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 6px;
  letter-spacing: 0.1em;
  padding: 7px 9px;
  text-transform: uppercase;
}
.detail-signal-briefing-cues {
  display: grid;
  gap: 12px;
}
.detail-signal-briefing-cues h3 {
  margin: 0;
}
.detail-signal-briefing-cue-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.detail-signal-briefing-cue h4 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: 1.35rem;
  font-weight: 500;
  line-height: 1;
}
.detail-signal-briefing-cue a {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
```

In the mobile media block, add:

```css
  .detail-signal-briefing-grid { grid-template-columns: 1fr; }
  .detail-signal-briefing-cue-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 7: Run focused render and CSS tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_signal_briefing_panel \
  tests/test_row_one_render.py::test_render_row_one_detail_signal_briefing_omits_local_cues_without_structure \
  tests/test_row_one_render.py::test_render_row_one_detail_signal_briefing_caps_references \
  tests/test_row_one_render.py::test_row_one_css_includes_detail_signal_briefing_styles -q
```

Expected: pass.

---

### Task 3: Workflow and Documentation Boundaries

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Extend workflow boundary test**

In `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`, after existing detail HTML assertions, add:

```python
    assert 'class="detail-signal-briefing"' in detail_html
    assert "Signal Briefing" in detail_html
    assert "信号简报" in detail_html
```

After generated contract payload negative assertions, add:

```python
    assert '"detail_signal_briefing"' not in generated_contract_payload
    assert '"signal_briefing"' not in generated_contract_payload
```

- [ ] **Step 2: Update docs boundary tests**

In `tests/test_row_one_docs.py`, update Stage 318 slice end sentinel from
`"Stage 310 adds"` to `"Stage 319 adds"`.

Add:

```python
def test_row_one_docs_describe_detail_signal_briefing_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_319 = readme[
        readme.index("Stage 319 adds detail signal briefing") : readme.index("Stage 310 adds")
    ]
    docs_stage_319 = docs[
        docs.index("Stage 319 adds detail signal briefing") : docs.index("Stage 310 adds")
    ]
    readme_stage_319_normalized = _normalized(readme_stage_319)
    docs_stage_319_normalized = _normalized(docs_stage_319)

    expected_phrases = [
        "detail signal briefing",
        "generated-site only",
        "existing story fields",
        "existing references",
        "existing saved local article sections",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not change schemas",
        "does not write a new json artifact",
        "does not add source collection",
        "does not fetch article pages",
        "does not add scoring",
        "does not add llm calls",
        "does not add connectors",
        "not a compliance review feature",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_319_normalized
        assert phrase in docs_stage_319_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "adds source collection",
        "fetches article pages",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
        "adds compliance review",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_319_normalized
        assert phrase not in docs_stage_319_normalized
```

- [ ] **Step 3: Update README and docs**

Add this paragraph after Stage 318 and before Stage 310 in both `README.md` and
`docs/row-one.md`:

```markdown
Stage 319 adds detail signal briefing to generated ROW ONE detail pages. It is
generated-site only and organizes existing story fields, existing references,
and existing saved local article sections into a concise signal briefing panel.
It does not change `row-one-app/v7`, does not change `data/edition.json`, does
not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not
change schemas, does not write a new json artifact, does not add source
collection, does not fetch article pages, does not add scoring, does not add llm
calls, does not add connectors, and is not a compliance review feature.
```

- [ ] **Step 4: Run focused workflow/docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_continue_reading_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_signal_briefing_boundary -q
```

Expected: pass.

---

### Task 4: Review, Full Verification, Commit, and Push

**Files:**
- Create: `docs/reviews/claude-code-stage-319-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-319-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Create Claude Code implementation review prompt**

Create `docs/reviews/claude-code-stage-319-code-review-prompt.md` with:

```markdown
# Stage 319 Code Review Prompt

Please review the Stage 319 implementation in `/home/ubuntu/fashion-radar`.

## Goal

Stage 319 adds a generated-site-only `Signal Briefing / 信号简报` panel to ROW
ONE detail pages, organizing existing story fields, existing references, and
existing saved local article sections without changing generated JSON
contracts.

## Files to Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-design.md`
- `docs/superpowers/plans/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-plan.md`

## Required Behavior

- Render a detail-page signal briefing panel after the detail information map
  and before summary.
- Use existing story summary, why-it-matters, signal-context, source, evidence,
  references, and optional local article sections.
- De-duplicate and cap references.
- Prefer brief-section local article cues, fill from content sections, and cap
  cues.
- Link only to existing rendered paragraph anchors.
- Escape all visible values.
- Keep app/runtime/manifest/schema/source/fetching/scoring/connector/LLM and
  compliance-review boundaries unchanged.
- Write no new JSON artifact.

Return findings ordered by severity:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.

If there are no Critical or Important issues, state that clearly.
```

- [ ] **Step 3: Run Claude Code implementation review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-319-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-319-code-review.md
```

Fix any Critical or Important findings before continuing.

- [ ] **Step 4: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

Expected: full test suite passes, lock is current, release hygiene passes, and
only Stage 319 files are modified/untracked.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-319-code-review-prompt.md \
  docs/reviews/claude-code-stage-319-code-review.md \
  docs/reviews/claude-code-stage-319-plan-review-prompt.md \
  docs/reviews/claude-code-stage-319-plan-review.md \
  docs/superpowers/plans/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-plan.md \
  docs/superpowers/specs/2026-07-06-stage-319-row-one-detail-signal-briefing-panel-design.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 319: add row one detail signal briefing"
git push origin main
```

---

## Definition of Done

- Detail pages render the signal briefing panel before summary.
- The panel organizes existing story fields and optional saved local article
  cues without fetching or generating new data.
- References are de-duplicated and capped.
- Local article cue links only target existing rendered paragraph anchors.
- `row-one-app/v7`, `row-one-manifest/v1`, and `row-one-runtime/v1` remain
  unchanged.
- No new generated JSON artifact is written.
- Render, workflow, docs, lint, format, diff, full pytest, lock, and release
  hygiene verification pass.
- Claude Code plan and implementation reviews have no unresolved Critical or
  Important findings.
