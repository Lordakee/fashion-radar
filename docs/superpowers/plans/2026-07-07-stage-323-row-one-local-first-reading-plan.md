# Stage 323 ROW ONE Local-First Reading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE generated pages prioritize locally saved article reading when saved paragraphs exist, and let saved content-organization cards jump directly to supporting saved paragraphs.

**Architecture:** Keep Stage 323 as generated-site-only rendering. Add a private `local_articles_by_story_id` argument to `render_index_html()`, pass the existing map from `render_row_one_site()`, render local-first CTA/badge HTML from existing `RowOneLocalArticle` paragraphs, and convert saved content-organization cards from wrapping anchors to article containers so paragraph evidence links are valid HTML. Preserve all app/runtime/manifest JSON contracts.

**Tech Stack:** Python, existing ROW ONE Pydantic models, existing string-rendered HTML/CSS in `templates.py`, existing `render_row_one_site()` pipeline, pytest, Ruff, Claude Code review gates.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Add constants for saved content-organization paragraph link cap.
  - Add `local_articles_by_story_id` optional keyword to `render_index_html()`.
  - Pass local article map into `_render_lead_story()` and `_render_section()`.
  - Add helpers for usable saved local paragraphs, local-article hrefs, local-first action blocks, and safe saved content-organization paragraph hrefs.
  - Render lead/story/detail local-first actions when usable saved paragraphs exist.
  - Convert saved content-organization cards from wrapping `<a>` to `<article>` with a standalone content-section link.
  - Render up to three evidence paragraph chips.
  - Add CSS selectors for local-first actions and evidence links.
- Modify: `src/fashion_radar/row_one/render.py`
  - Pass `local_articles_by_story_id` into `render_index_html()`.
- Modify: `tests/test_row_one_render.py`
  - Add Stage 323 render, omission, detail ordering, evidence-link, safety, nested-anchor, and CSS tests.
- Modify: `tests/test_workflows.py`
  - Extend ROW ONE generated-site-only boundary assertions for Stage 323 private markers not entering JSON contracts.
- Modify: `tests/test_row_one_docs.py`
  - Add Stage 323 docs boundary test.
- Modify: `README.md`
  - Add Stage 323 generated-site-only paragraph.
- Modify: `docs/row-one.md`
  - Add Stage 323 generated-site-only paragraph.
- Create: `docs/reviews/claude-code-stage-323-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-323-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-323-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-323-code-review.md`

## Task 1: Add Failing Render Tests

- [ ] **Step 1: Add a homepage local-first render test**

Add near the existing local article/detail render tests in `tests/test_row_one_render.py`:

```python
def test_render_row_one_site_prefers_saved_article_reading_on_homepage(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="local-read-path"' in index_html
    assert 'class="local-read-action"' in index_html
    assert "Read saved article" in index_html
    assert "阅读本地正文" in index_html
    assert "Saved locally" in index_html
    assert "本地已保存" in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' in index_html
    assert '<span data-lang="en">Read the brief</span>' not in index_html
    assert '<span data-lang="en">Read brief</span>' not in index_html
```

Expected RED: fails because `local_articles_by_story_id` is not passed into `render_index_html()` and local-first classes/labels do not exist.

- [ ] **Step 2: Add a homepage omission test**

```python
def test_render_row_one_site_omits_homepage_local_first_action_without_saved_article(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path, local_articles_by_story_id={})

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert 'class="local-read-path"' not in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' not in index_html
    assert "Read saved article" not in index_html
    assert "阅读本地正文" not in index_html
```

Expected RED after Step 1 implementation but before omission handling if local-first renders unconditionally.

- [ ] **Step 3: Add a detail local-first ordering test**

```python
def test_render_detail_html_puts_saved_article_action_before_external_source() -> None:
    edition = _edition()
    story = edition.stories[0]
    detail_html = render_detail_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'class="local-read-path detail-local-read-path"' in detail_html
    assert 'href="#local-article"' in detail_html
    assert "Read saved article" in detail_html
    assert "阅读本地正文" in detail_html
    assert detail_html.index('class="local-read-path detail-local-read-path"') < detail_html.index(
        "Open Source Article"
    )
    assert "打开原文" in detail_html
```

Expected RED: detail page has external source action but no local-first action block.

- [ ] **Step 4: Add a saved content-organization paragraph link test**

Add near the existing saved article content-organization render tests:

```python
def test_render_row_one_site_saved_article_content_organization_links_evidence_paragraphs(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_html = (
        tmp_path / "details" / "the-row-signal-1234567890.html"
    ).read_text(encoding="utf-8")

    assert '<article class="saved-article-content-organization-card">' in index_html
    assert '<a class="saved-article-content-organization-card"' not in index_html
    assert 'class="saved-article-content-organization-card-link"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-content-section-' in index_html
    assert 'class="saved-article-content-organization-evidence"' in index_html
    assert 'class="saved-article-content-organization-evidence-link"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in index_html
    assert "Evidence paragraph 1" in index_html
    assert "证据段落 1" in index_html
    assert 'id="local-article-paragraph-1"' in detail_html
```

Expected RED: content-organization cards are wrapping anchors and only show paragraph counts, not evidence paragraph links.

- [ ] **Step 5: Add a direct safety test for saved content-organization evidence links**

Add a direct `render_index_html()` safety test using a manually created `RowOneSavedArticleContentOrganization` payload. Ensure `from dataclasses import replace` is available in the test module. Keep one safe card, invalid-path cards that should not render, and a valid-path bad-index card that may render the card but must not render invalid evidence links.

```python
def test_render_index_html_filters_saved_article_content_organization_evidence_links() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 2),
        references=(),
    )
    invalid_path_cards = (
        replace(safe_card, title=LocalizedText(en="JS card", zh="JS 卡片"), detail_path="javascript:alert(1)"),
        replace(safe_card, title=LocalizedText(en="Traversal card", zh="穿越卡片"), detail_path="../secrets.html#local-article-content-section-1"),
        replace(safe_card, title=LocalizedText(en="Wrong fragment card", zh="错误片段卡片"), detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1"),
    )
    bad_index_card = replace(
        safe_card,
        title=LocalizedText(en="Bad index card", zh="坏索引卡片"),
        paragraph_indices=(-1, True),
    )
    duplicate_card = replace(
        safe_card,
        title=LocalizedText(en="Duplicate card", zh="重复卡片"),
        paragraph_indices=(0, 0, 1),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card, *invalid_path_cards, bad_index_card, duplicate_card],
            ),
        ]
    )

    index_html = render_index_html(
        _edition(),
        saved_article_content_organization=organization,
    )

    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-3"' in index_html
    assert "javascript:alert" not in index_html
    assert "../secrets" not in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-0"' not in index_html
    assert "JS card" not in index_html
    assert "Traversal card" not in index_html
    assert "Wrong fragment card" not in index_html
    assert "Bad index card" in index_html
    assert index_html.count('class="saved-article-content-organization-card"') == 3
    assert index_html.count('href="details/the-row-signal-1234567890.html#local-article-paragraph-1"') == 2
```

Expected RED: evidence paragraph links and article card behavior do not exist.

- [ ] **Step 5a: Add evidence cap and dedupe test**

```python
def test_render_index_html_caps_and_dedupes_saved_article_content_organization_evidence_links() -> None:
    card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Evidence card", zh="证据卡片"),
        source_name="Source",
        section_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        section_label=LocalizedText(en="Entity", zh="实体"),
        lead=LocalizedText(en="Lead", zh="摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1, 1, 2, 3, 4),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[card],
            ),
        ]
    )

    index_html = render_index_html(
        _edition(),
        saved_article_content_organization=organization,
    )

    assert index_html.count('class="saved-article-content-organization-evidence-link"') == 3
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-3"' in index_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-4"' not in index_html
    assert index_html.count('href="details/the-row-signal-1234567890.html#local-article-paragraph-2"') == 1
```

Expected RED: evidence links are not yet rendered or deduped.

- [ ] **Step 6: Add a CSS selector test**

Extend the existing CSS selector test in `tests/test_row_one_render.py`:

```python
def test_row_one_css_includes_stage_323_local_first_and_evidence_selectors() -> None:
    css = row_one_css()

    for selector in (
        ".local-read-path",
        ".local-read-path-badge",
        ".local-read-action",
        ".saved-article-content-organization-card-link",
        ".saved-article-content-organization-evidence",
        ".saved-article-content-organization-evidence-link",
    ):
        assert selector in css
```

Expected RED: new selectors do not exist.

- [ ] **Step 7: Run focused RED tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "local_first or saved_article_content_organization or stage_323" -q
```

Expected: new Stage 323 tests fail for missing classes/links/selectors, while unrelated selected tests keep their previous behavior.

## Task 2: Implement Generated-Site Template Changes

- [ ] **Step 1: Add constants and `render_index_html()` private argument**

In `src/fashion_radar/row_one/templates.py`, add:

```python
SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT = 3
```

Update `render_index_html()`:

```python
def render_index_html(
    edition: RowOneEdition,
    *,
    app_payload: dict[str, object] | None = None,
    local_article_intelligence: Sequence[RowOneDailyLocalIntelligenceSection] | None = None,
    saved_article_coverage: RowOneSavedArticleCoverage | None = None,
    saved_article_briefs: RowOneSavedArticleBriefs | None = None,
    saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None,
    editorial_brief: _EditorialBrief | None = None,
    local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None,
) -> str:
```

Inside the function:

```python
local_articles_by_story_id = local_articles_by_story_id or {}
lead_story_block = (
    _render_lead_story(
        lead_story,
        _section_title(edition, lead_story.section_key),
        local_article=local_articles_by_story_id.get(lead_story.id),
    )
    if lead_story
    else ""
)
story_cards = "\n".join(
    _render_section(edition, section.key, local_articles_by_story_id=local_articles_by_story_id)
    for section in edition.sections
)
```

- [ ] **Step 2: Pass local articles from `render_row_one_site()`**

In `src/fashion_radar/row_one/render.py`, add the keyword to the existing `render_index_html()` call:

```python
local_articles_by_story_id=local_articles_by_story_id,
```

This is a private render argument only; do not add it to `build_row_one_app_payload()`.

- [ ] **Step 3: Add local-first helpers**

In `templates.py`, near `_internal_detail_href()` or other detail href helpers, add:

```python
def _usable_local_article_paragraph_count(article: RowOneLocalArticle | None) -> int:
    if article is None:
        return 0
    return sum(1 for paragraph in article.paragraphs if normalize_row_one_paragraph(paragraph))


def _local_article_href(story: RowOneStory, article: RowOneLocalArticle | None) -> str | None:
    if _usable_local_article_paragraph_count(article) <= 0:
        return None
    detail_path = _validated_detail_relative_path(story.detail_path)
    if detail_path is None:
        return None
    return f"{detail_path}#local-article"


def _local_read_count_label(count: int) -> LocalizedText:
    paragraph_label = "paragraph" if count == 1 else "paragraphs"
    return LocalizedText(en=f"{count} saved {paragraph_label}", zh=f"{count} 个保存段落")
```

Use `_esc()` at render sites, not inside these helpers.

- [ ] **Step 4: Render homepage local-first action**

Update `_render_lead_story()` to accept `local_article: RowOneLocalArticle | None = None`. Compute:

```python
local_article_href = _local_article_href(story, local_article)
local_read_path = _render_homepage_local_read_path(story, local_article)
lead_action_href = local_article_href or detail_href
lead_action_label = (
    LocalizedText(en="Read saved article", zh="阅读本地正文")
    if local_article_href
    else LocalizedText(en="Read the brief", zh="查看详情")
)
lead_action_class = "lead-story-link local-read-action" if local_article_href else "lead-story-link"
```

Render the existing lead action using `lead_action_href`, `lead_action_label`, and `lead_action_class`, and place `{local_read_path}` near the lead action.

Update `_render_section()` to accept `local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None` and pass `local_article=local_articles_by_story_id.get(story.id)` into `_render_story_card()`.

Update `_render_story_card()` to accept `local_article: RowOneLocalArticle | None = None`. Compute `local_article_href`, action label, action class, and a `local_read_path` block. Render the footer detail link using the local article href and local label when available, otherwise keep the existing detail href and `Read brief / 阅读简报`. The local-first footer link should use `class="story-detail-link local-read-action"` only when it points to the local article section.

Add:

```python
def _render_homepage_local_read_path(
    story: RowOneStory,
    article: RowOneLocalArticle | None,
) -> str:
    href = _local_article_href(story, article)
    count = _usable_local_article_paragraph_count(article)
    if href is None or count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path">
      <span class="local-read-path-badge">
        <span data-lang="en">Saved locally</span>
        <span data-lang="zh">本地已保存</span>
      </span>
      <span>
        <span data-lang="en">{_esc(count_label.en)}</span>
        <span data-lang="zh">{_esc(count_label.zh)}</span>
      </span>
    </p>"""
```

- [ ] **Step 5: Render detail local-first action**

Add:

```python
def _render_detail_local_read_path(local_article: RowOneLocalArticle | None) -> str:
    count = _usable_local_article_paragraph_count(local_article)
    if count <= 0:
        return ""
    count_label = _local_read_count_label(count)
    return f"""<p class="local-read-path detail-local-read-path">
  <span class="local-read-path-badge">
    <span data-lang="en">Saved locally</span>
    <span data-lang="zh">本地已保存</span>
  </span>
  <a class="local-read-action" href="#local-article">
    <span data-lang="en">Read saved article</span>
    <span data-lang="zh">阅读本地正文</span>
  </a>
  <span>
    <span data-lang="en">{_esc(count_label.en)}</span>
    <span data-lang="zh">{_esc(count_label.zh)}</span>
  </span>
</p>"""
```

In `render_detail_html()`, compute:

```python
local_read_path = _render_detail_local_read_path(local_article)
```

Place `{local_read_path}` after `<p class="story-source">{source_link}</p>` and before `{source_action}`.

- [ ] **Step 6: Convert saved content-organization card and render evidence links**

Update `_render_saved_article_content_organization_card()` so it returns an `<article class="saved-article-content-organization-card">`, not an anchor. Include the existing title/lead/meta and a standalone:

```html
<a class="saved-article-content-organization-card-link" href="...">
  <span data-lang="en">Open organized section</span>
  <span data-lang="zh">打开整理栏目</span>
</a>
```

Update `_render_saved_article_content_organization_chips()` to append a new evidence block when paragraph links exist:

```python
evidence = _render_saved_article_content_organization_evidence(card)
return "".join(chips) + evidence
```

Add:

```python
def _render_saved_article_content_organization_evidence(
    card: RowOneSavedArticleContentOrganizationCard,
) -> str:
    links: list[str] = []
    seen: set[int] = set()
    for paragraph_index in card.paragraph_indices:
        if paragraph_index in seen:
            continue
        href = _safe_saved_article_content_organization_evidence_href(
            card.detail_path,
            paragraph_index,
        )
        if href is None:
            continue
        seen.add(paragraph_index)
        label_number = paragraph_index + 1
        links.append(
            '<a class="saved-article-content-organization-evidence-link" '
            f'href="{_esc(href)}">'
            f'<span data-lang="en">Evidence paragraph {_esc(str(label_number))}</span>'
            f'<span data-lang="zh">证据段落 {_esc(str(label_number))}</span>'
            "</a>"
        )
        if len(links) >= SAVED_ARTICLE_CONTENT_ORGANIZATION_EVIDENCE_LINK_LIMIT:
            break
    if not links:
        return ""
    return (
        '<span class="saved-article-content-organization-evidence">'
        + "".join(links)
        + "</span>"
    )
```

Add:

```python
def _safe_saved_article_content_organization_evidence_href(
    detail_path: object,
    paragraph_index: object,
) -> str | None:
    safe_section_href = _safe_saved_article_content_organization_href(detail_path)
    if safe_section_href is None:
        return None
    if not isinstance(paragraph_index, int) or isinstance(paragraph_index, bool) or paragraph_index < 0:
        return None
    path, _, _fragment = safe_section_href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    paragraph_fragment = f"local-article-paragraph-{paragraph_index + 1}"
    if not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(paragraph_fragment):
        return None
    return f"{safe_path}#{paragraph_fragment}"
```

- [ ] **Step 7: Add CSS**

In `row_one_css()`, near story-card and saved article organization styles, add selectors:

```css
.local-read-path {
  align-items: center;
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.74rem;
  gap: 8px 10px;
  letter-spacing: 0.08em;
  margin: 12px 0 0;
  text-transform: uppercase;
}
.local-read-path-badge {
  border: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 700;
  padding: 4px 7px;
}
.local-read-action {
  border-bottom: 1px solid var(--accent);
  color: var(--accent);
  font-weight: 800;
  padding-bottom: 3px;
  text-decoration: none;
}
.detail-local-read-path {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 12px 0;
}
.saved-article-content-organization-card-link {
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-decoration: none;
  text-transform: uppercase;
}
.saved-article-content-organization-evidence {
  display: contents;
}
.saved-article-content-organization-evidence-link {
  border: 1px solid var(--accent);
  color: var(--accent);
  display: inline-flex;
  font-size: 0.68rem;
  font-weight: 800;
  gap: 5px;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-decoration: none;
  text-transform: uppercase;
}
```

- [ ] **Step 8: Run focused GREEN tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "local_first or saved_article_content_organization or stage_323" -q
```

Expected: selected render tests pass.

## Task 3: Add Workflow Boundary And Docs Tests

- [ ] **Step 1: Extend workflow contract boundary test**

In `tests/test_workflows.py`, extend the existing ROW ONE local article workflow assertions:

```python
assert "Read saved article" in index_html
assert "阅读本地正文" in index_html
assert "saved-article-content-organization-evidence-link" in index_html
assert "local-read-path" in detail_html
```

Extend `generated_contract_payload` negative assertions:

```python
assert '"local_first_read"' not in generated_contract_payload
assert '"local_read_path"' not in generated_contract_payload
assert '"saved_article_cta"' not in generated_contract_payload
assert '"evidence_paragraph_trail"' not in generated_contract_payload
assert '"paragraph_trail"' not in generated_contract_payload
```

- [ ] **Step 2: Add docs boundary test**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_local_first_reading_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_323 = readme[
        readme.index("Stage 323 adds Local-First Reading") : readme.index("Stage 322 adds")
    ]
    docs_stage_323 = docs[
        docs.index("Stage 323 adds Local-First Reading") : docs.index("Stage 322 adds")
    ]
    readme_stage_323_normalized = _normalized(readme_stage_323)
    docs_stage_323_normalized = _normalized(docs_stage_323)

    expected_phrases = [
        "local-first reading",
        "generated-site only",
        "existing `data/articles/<story-id>.json` sidecars",
        "existing saved local paragraphs",
        "existing `#local-article`",
        "existing `#local-article-paragraph-n`",
        "safe internal links",
        "read saved article",
        "saved article content-organization cards",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not add `local_first_read`",
        "does not add `local_read_path`",
        "does not add `saved_article_cta`",
        "does not add `evidence_paragraph_trail`",
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
        assert phrase in readme_stage_323_normalized
        assert phrase in docs_stage_323_normalized
```

Expected RED before docs updates.

- [ ] **Step 3: Run docs/workflow RED tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k row_one -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -k local_first_reading -q
```

Expected: workflow may pass after Task 2, docs test fails before docs updates.

## Task 4: Update Documentation

- [ ] **Step 1: Add README Stage 323 paragraph**

Insert before the Stage 322 paragraph in `README.md`:

```markdown
Stage 323 adds Local-First Reading to generated ROW ONE pages. It is
generated-site only and uses existing `data/articles/<story-id>.json` sidecars,
existing saved local paragraphs, existing `#local-article`, existing
`#local-article-paragraph-N`, and existing content-section anchors to make
`Read saved article / 阅读本地正文` the primary generated-site action when saved
paragraphs are available. Saved article content-organization cards also expose
safe internal links for paragraph evidence while preserving the existing
organized section link. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not add `local_first_read`, does not add
`local_read_path`, does not add `saved_article_cta`, does not add
`evidence_paragraph_trail`, does not change `row-one-manifest/v1`, does not
change `row-one-runtime/v1`, does not change schemas, does not write a new json
artifact, does not add source collection, does not fetch article pages, does
not add scoring, does not add llm calls, does not add connectors, and is not a
compliance review feature.
```

- [ ] **Step 2: Add docs Stage 323 paragraph**

Insert the same paragraph before the Stage 322 paragraph in `docs/row-one.md`.

- [ ] **Step 3: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -k local_first_reading -q
```

Expected: docs boundary test passes.

## Task 5: Verification And Review

- [ ] **Step 1: Run focused tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "local_first or saved_article_content_organization or local_article_content or editorial_brief" -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k row_one -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -k "local_first_reading or editorial_source_trail" -q
```

- [ ] **Step 2: Run full verification**

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
git diff --check
```

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-323-code-review-prompt.md` with:

```markdown
Review Stage 323 ROW ONE Local-First Reading implementation.

Scope:
- Generated ROW ONE HTML/CSS only.
- Local saved article reading becomes the primary generated-site action when saved paragraphs exist.
- Saved article content-organization cards expose safe direct evidence paragraph links.
- External source links remain secondary provenance.
- No JSON contract/schema/model/source fetching/scoring/LLM/connector/deployment/compliance behavior changes.

Please review for:
- correctness and technical reasonableness
- href safety
- no nested anchors
- no JSON contract mutation
- docs/test coverage
- any Critical or Important findings that must be fixed before push
```

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-323-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-323-code-review.md
```

Fix Critical/Important findings and re-review until clear.

- [ ] **Step 4: Secret scan for known sensitive tokens**

Run an exact substring scan for known user-provided token/API-key prefixes without printing the secret values:

```bash
python - <<'PY'
from pathlib import Path
needles = [
    "ghp_",
    "sk-",
]
root = Path(".")
hits = []
for path in root.rglob("*"):
    if ".git" in path.parts or path.is_dir():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for needle in needles:
        if needle in text:
            hits.append((str(path), needle))
if hits:
    for path, needle in hits:
        print(f"potential secret marker {needle!r} in {path}")
    raise SystemExit(1)
print("no known secret markers found")
PY
```

- [ ] **Step 5: Commit and push**

```bash
git status --short
git add README.md docs/row-one.md docs/reviews/claude-code-stage-323-* docs/superpowers/specs/2026-07-07-stage-323-row-one-local-first-reading-design.md docs/superpowers/plans/2026-07-07-stage-323-row-one-local-first-reading-plan.md src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py
git commit -m "Stage 323: add row one local-first reading"
git push origin main
```

## Definition Of Done

- Stage 323 plan review by Claude Code has no unresolved Critical or Important findings.
- Stage 323 local-first actions and evidence paragraph links are implemented in generated HTML only.
- No app/runtime/manifest JSON contracts change.
- Focused tests and full verification pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Commit is pushed to `origin/main`.
- Handoff Summary records repo state, verified commands, uncommitted files, and next step.
