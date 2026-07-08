# Stage 342 ROW ONE Saved Paragraph Context Cues Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only paragraph context cues to ROW ONE local article pages so saved paragraphs show which organized section/item references them.

**Architecture:** Keep the feature inside the existing ROW ONE HTML/CSS renderer. Reuse `RowOneLocalArticle.content_sections`, strict valid paragraph indices, existing paragraph anchors, and existing content-section anchors; do not change models, JSON artifacts, source acquisition, extraction, ranking, scheduling, deployment, or app contracts.

**Tech Stack:** Python 3.12, Pydantic models already in `fashion_radar.row_one.models`, HTML string rendering in `src/fashion_radar/row_one/templates.py`, pytest, ruff, uv.

---

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add a small private support dataclass near the existing local paragraph evidence support type.
  - Add a helper that maps rendered paragraph indices to capped, deduped context labels and safe page-local content-section hrefs.
  - Update `_render_local_article_paragraphs(article)` to insert context cues while preserving `id="local-article-paragraph-N"` and bilingual spans.
  - Add CSS selectors for `.local-article-paragraph-context`.
- Modify `tests/test_row_one_render.py`
  - Add TDD coverage for cues on first-class local article pages and detail pages.
  - Add invalid-index, dedupe, cap, and escaping coverage.
  - Add CSS selector coverage.
- Modify `README.md` and `docs/row-one.md`
  - Add the Stage 342 boundary paragraph before Stage 341.
- Modify `tests/test_row_one_docs.py`
  - Add a docs guard that requires the Stage 342 paragraph and verifies it precedes Stage 341.
- Modify `tests/test_workflows.py`
  - Extend the existing ROW ONE write-site workflow guard to assert generated article pages contain the HTML-only cue marker and no Stage 342 JSON/HTML artifacts or app-facing contract keys are created.

---

### Task 1: Add Failing Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add tests for context cues on first-class local article pages**

Add tests near the existing Stage 341 local article page tests:

```python
def test_render_local_article_page_labels_saved_paragraphs_with_content_context() -> None:
    story = _story()
    html = render_local_article_page_html(
        _edition(),
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'id="local-article-paragraph-1"' in html
    assert 'class="local-article-paragraph-context"' in html
    assert 'href="#local-article-content-section-1"' in html
    assert '<span data-lang="en">Used in</span>' in html
    assert '<span data-lang="zh">用于</span>' in html
    assert "Entities - The Row" in html
```

- [ ] **Step 2: Add tests for information-panel saved paragraph cue excerpts**

Add this test near the existing Stage 341 local article information panel tests.
Slice only the panel so the full saved article body cannot create false
positives:

```python
def test_render_local_article_information_panel_shows_saved_paragraph_context_cues() -> None:
    base_article = _signal_briefing_local_article()
    article = base_article.model_copy(
        update={
            "paragraphs": [
                "Unique runway buyer context cue.",
                "Unique handbag market context cue.",
                "Unreferenced paragraph should stay out of cue previews.",
            ],
            "paragraphs_zh": [
                "独特秀场买手上下文提示。",
                "独特手袋市场上下文提示。",
                "未引用段落不应出现在提示预览。",
            ],
        }
    )
    html = render_local_article_page_html(_edition(), _story(), local_article=article)
    panel = _html_between(html, '<section class="local-article-information"', 'id="local-article"')

    assert 'href="#local-article-paragraph-1"' in panel
    assert 'href="#local-article-paragraph-2"' in panel
    assert "Unique runway buyer context cue." in panel
    assert "Unique handbag market context cue." in panel
    assert "独特秀场买手上下文提示。" in panel
    assert "未引用段落不应出现在提示预览。" not in panel
```

- [ ] **Step 3: Add tests for detail pages**

```python
def test_render_row_one_detail_labels_saved_paragraphs_with_content_context() -> None:
    story = _story()
    html = render_detail_html(
        _edition(),
        story,
        local_article=_signal_briefing_local_article(),
    )

    assert 'id="local-article-paragraph-1"' in html
    assert 'class="local-article-paragraph-context"' in html
    assert 'href="#local-article-content-section-1"' in html
    assert "Entities - The Row" in html
```

- [ ] **Step 4: Add tests for invalid indices, bools, duplicates, and out-of-range values**

```python
def test_render_local_article_paragraph_context_filters_invalid_duplicate_indices() -> None:
    base_article = _signal_briefing_local_article()
    section = base_article.content_sections[0]
    invalid_item = section.items[0].model_copy(
        update={"paragraph_indices": [True, 0, 0, -1, 99, 1]}
    )
    article = base_article.model_copy(
        update={
            "content_sections": [
                section.model_copy(update={"items": [invalid_item]}),
            ]
        }
    )

    html = render_local_article_page_html(_edition(), _story(), local_article=article)

    assert 'href="#local-article-content-section-1"' in html
    assert "#local-article-paragraph-0" not in html
    assert "#local-article-paragraph-100" not in html
```

Avoid exact-count assertions here because existing local-article navigation and
information-panel blocks may legitimately link to the same content-section
anchor multiple times.

- [ ] **Step 5: Add tests for escaping and caps**

```python
def test_render_local_article_paragraph_context_escapes_and_caps_labels() -> None:
    base_article = _signal_briefing_local_article()
    sections = []
    for index in range(1, 6):
        section = base_article.content_sections[0].model_copy(
            update={
                "title": LocalizedText(zh=f"栏目 <{index}>", en=f"Section <{index}>"),
                "items": [
                    base_article.content_sections[0].items[0].model_copy(
                        update={
                            "label": LocalizedText(
                                zh=f"条目 <{index}>",
                                en=f"Item <{index}>",
                            ),
                            "paragraph_indices": [0],
                        }
                    )
                ],
            }
        )
        sections.append(section)
    article = base_article.model_copy(update={"content_sections": sections})

    html = render_local_article_page_html(_edition(), _story(), local_article=article)

    assert "Section &lt;1&gt; - Item &lt;1&gt;" in html
    assert "Section <1>" not in html
    assert "Section &lt;5&gt; - Item &lt;5&gt;" not in html
```

The cap should exclude the fifth label when the implementation cap is four.

- [ ] **Step 6: Add generated-site HTML-only test**

Add or extend the existing first-class article page E2E around the generated
`articles/<story-id>.html` page:

```python
def test_render_row_one_site_local_article_page_context_cues_are_html_only(tmp_path) -> None:
    story = _story()
    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    article_html = (tmp_path / "articles" / f"{story.id}.html").read_text(encoding="utf-8")
    assert 'class="local-article-paragraph-context"' in article_html
    assert 'id="local-article-paragraph-1"' in article_html

    generated_contract_payload = "\n".join(
        [
            (tmp_path / "data" / "edition.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"),
            (tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"),
        ]
    )
    assert "saved_paragraph_context_cues" not in generated_contract_payload
    assert "paragraph_context_cues" not in generated_contract_payload
    assert not (tmp_path / "data" / "saved-paragraph-context-cues.json").exists()
```

- [ ] **Step 7: Add CSS selector test**

Extend `test_row_one_css_includes_local_article_information_styles` or add a new
focused test:

```python
def test_row_one_css_includes_local_article_paragraph_context_styles() -> None:
    css = row_one_css()

    for selector in (
        ".local-article-paragraph-context",
        ".local-article-paragraph-context-label",
        ".local-article-paragraph-context-links",
        ".local-article-paragraph-context a",
    ):
        assert selector in css
```

- [ ] **Step 8: Run the new tests and verify they fail for the missing feature**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "paragraph_context"
```

Expected: tests fail because `.local-article-paragraph-context` and new CSS
selectors do not exist yet.

---

### Task 2: Implement Renderer Helpers And Markup

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add constants near related local article constants**

Add:

```python
_LOCAL_ARTICLE_PARAGRAPH_CONTEXT_LIMIT = 4
```

- [ ] **Step 2: Add a private support dataclass near `_LocalArticleParagraphEvidenceEntry`**

Add:

```python
@dataclass(frozen=True)
class _LocalArticleParagraphContextCue:
    anchor: str
    label: str
```

- [ ] **Step 3: Add a helper for context cues near the local article anchor helpers**

Add:

```python
def _local_article_paragraph_contexts(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int] | None = None,
) -> dict[int, list[_LocalArticleParagraphContextCue]]:
    if rendered_indices is None:
        rendered_indices = _local_article_rendered_paragraph_indices(article)
    contexts: dict[int, list[_LocalArticleParagraphContextCue]] = {}
    seen_by_index: dict[int, set[tuple[str, str]]] = {}
    for section_position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(section_position)
        section_title_en = section.title.en.strip()
        for item in section.items:
            item_label_en = item.label.en.strip()
            if section_title_en and item_label_en:
                label = f"{section_title_en} - {item_label_en}"
            else:
                label = item_label_en or section_title_en
            if not label:
                continue
            key = (section_anchor, label)
            for paragraph_index in _strict_valid_local_article_paragraph_indices(
                item.paragraph_indices,
                rendered_indices,
            ):
                seen = seen_by_index.setdefault(paragraph_index, set())
                if key in seen:
                    continue
                seen.add(key)
                entries = contexts.setdefault(paragraph_index, [])
                if len(entries) < _LOCAL_ARTICLE_PARAGRAPH_CONTEXT_LIMIT:
                    entries.append(
                        _LocalArticleParagraphContextCue(
                            anchor=section_anchor,
                            label=label,
                        )
                    )
    return contexts
```

- [ ] **Step 4: Add a renderer for the context cue**

Add:

```python
def _render_local_article_paragraph_context(
    entries: Sequence[_LocalArticleParagraphContextCue],
) -> str:
    if not entries:
        return ""
    links = "".join(
        f'<a href="#{_esc(entry.anchor)}">{_esc(entry.label)}</a>' for entry in entries
    )
    return (
        '<span class="local-article-paragraph-context">'
        '<span class="local-article-paragraph-context-label">'
        '<span data-lang="en">Used in</span>'
        '<span data-lang="zh">用于</span>'
        "</span>"
        f'<span class="local-article-paragraph-context-links">{links}</span>'
        "</span>"
    )
```

- [ ] **Step 5: Update `_render_local_article_paragraphs(article)`**

Compute contexts once after confirming the article has nonblank source paragraphs:

```python
rendered_indices = _local_article_rendered_paragraph_indices(article)
paragraph_contexts = _local_article_paragraph_contexts(
    article,
    rendered_indices=rendered_indices,
)
```

Then, in both existing render branches, insert the context HTML immediately after
the opening `<p id="...">` and before the paragraph text.

For the non-bilingual branch:

```python
context = _render_local_article_paragraph_context(paragraph_contexts.get(index, []))
rendered.append(
    f'      <p id="{_esc(anchor)}">{context}{_esc(paragraph)}</p>'
)
```

For the bilingual branch:

```python
context = _render_local_article_paragraph_context(paragraph_contexts.get(index, []))
rendered.append(
    f'      <p id="{_esc(anchor)}">'
    f"{context}"
    f'<span data-lang="en">{_esc(paragraph_en)}</span>'
    f'<span data-lang="zh">{_esc(zh)}</span>'
    "</p>"
)
```

- [ ] **Step 6: Add CSS**

Add the selectors:

```css
.local-article-paragraph-context {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.45rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.local-article-paragraph-context-label {
  color: var(--color-muted);
}

.local-article-paragraph-context-links {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.local-article-paragraph-context a {
  color: var(--color-ink);
  text-decoration: none;
  border-bottom: 1px solid rgba(17, 17, 17, 0.25);
}
```

- [ ] **Step 7: Run render tests and fix formatting if needed**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "paragraph_context or local_article_page or local_article_information"
```

Expected: all selected tests pass.

---

### Task 3: Add Documentation And Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add Stage 342 documentation paragraph before Stage 341 in both docs**

Add this exact paragraph to `README.md` and `docs/row-one.md` before the Stage 341
paragraph:

```markdown
Stage 342 adds generated-site only saved paragraph context cues for ROW ONE local article pages; it reuses current-edition saved local article sidecars, existing local article rendering sections, existing content-section paragraph indices, existing detail-page `#local-article-content-section-N` anchors, existing `#local-article-paragraph-N` anchors, and existing `articles/<story-id>.html` pages to show which organized section or item cites each saved paragraph without changing app-facing contracts; it does not create `data/saved-paragraph-context-cues.json`, does not create `data/local-article-paragraph-contexts.json`, does not create new article-source sidecars, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs guard before the Stage 341 docs guard**

Add:

```python
def test_row_one_docs_describe_stage_342_saved_paragraph_context_cues_boundary() -> None:
    expected = _normalized(
        "Stage 342 adds generated-site only saved paragraph context cues for "
        "ROW ONE local article pages; it reuses current-edition saved local "
        "article sidecars, existing local article rendering sections, existing "
        "content-section paragraph indices, existing detail-page "
        "`#local-article-content-section-N` anchors, existing "
        "`#local-article-paragraph-N` anchors, and existing "
        "`articles/<story-id>.html` pages to show which organized section or "
        "item cites each saved paragraph without changing app-facing contracts; "
        "it does not create `data/saved-paragraph-context-cues.json`, does not "
        "create `data/local-article-paragraph-contexts.json`, does not create "
        "new article-source sidecars, does not publish full articles on the "
        "library index, does not add outbound article URLs as primary "
        "navigation, does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, "
        "scheduling, deployment, market grouping, domestic/international "
        "classification, analytics, personalization, recommendation, or "
        "compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage_342_pos = normalized.index(
            "stage 342 adds generated-site only saved paragraph context cues"
        )
        stage_341_pos = normalized.index(
            "stage 341 adds generated-site only local article reading improvements"
        )
        assert stage_342_pos < stage_341_pos
        stage = normalized[stage_342_pos:stage_341_pos]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "creates `data/saved-paragraph-context-cues.json`",
            "writes `data/saved-paragraph-context-cues.json`",
            "creates `data/local-article-paragraph-contexts.json`",
            "writes `data/local-article-paragraph-contexts.json`",
            "writes a new json artifact",
            "creates new article-source sidecars",
            "publishes full articles on the library index",
            "adds outbound article urls",
            "adds source collection",
            "adds fetching",
            "adds matching",
            "adds extraction",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds analytics",
            "adds personalization",
            "adds recommendation",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

- [ ] **Step 3: Extend workflow artifact and contract guards**

In `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`,
add positive generated-site assertions after existing detail/article HTML reads:

```python
article_pages = [
    path
    for path in (output_dir / "articles").glob("*.html")
    if path.name != "index.html"
]
assert article_pages
article_html = article_pages[0].read_text(encoding="utf-8")
assert 'class="local-article-paragraph-context"' in article_html
assert 'id="local-article-paragraph-1"' in article_html
```

Then
add app-contract negative assertions:

```python
assert "saved_paragraph_context_cues" not in generated_contract_payload
assert "local_article_paragraph_contexts" not in generated_contract_payload
assert "local_article_context_cues" not in generated_contract_payload
assert "paragraph_context_cues" not in generated_contract_payload
assert "Saved Paragraph Context Cues" not in generated_contract_payload
assert "saved-paragraph-context-cues" not in generated_contract_payload
assert "local-article-paragraph-contexts" not in generated_contract_payload
assert "local-article-context-cues" not in generated_contract_payload
assert "paragraph-context-cues" not in generated_contract_payload
```

Extend the artifact absence list with:

```python
output_dir / "saved-paragraph-context-cues.json",
output_dir / "articles" / "saved-paragraph-context-cues.json",
output_dir / "data" / "saved-paragraph-context-cues.json",
output_dir / "local-article-paragraph-contexts.json",
output_dir / "articles" / "local-article-paragraph-contexts.json",
output_dir / "data" / "local-article-paragraph-contexts.json",
output_dir / "saved-paragraph-context-cues.html",
output_dir / "articles" / "saved-paragraph-context-cues.html",
output_dir / "data" / "saved-paragraph-context-cues.html",
output_dir / "local-article-context-cues.json",
output_dir / "articles" / "local-article-context-cues.json",
output_dir / "data" / "local-article-context-cues.json",
output_dir / "local-article-context-cues.html",
output_dir / "articles" / "local-article-context-cues.html",
output_dir / "data" / "local-article-context-cues.html",
```

- [ ] **Step 4: Run docs and workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: all selected tests pass.

---

### Task 4: Review, Full Verification, Commit, And Push

**Files:**
- Review all changed files.

- [ ] **Step 1: Run focused render/docs/workflow verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "paragraph_context or local_article_page or local_article_information"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q
```

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

- [ ] **Step 3: Request Claude Code review of the completed node**

Create `docs/reviews/claude-code-stage-342-code-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-342-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-342-code-review.md
rm -f "$tmp_review"
```

Fix all critical and important findings before continuing.

- [ ] **Step 4: Stage and scan for token-shaped secrets**

Run:

```bash
git add README.md docs/row-one.md docs/reviews/claude-code-stage-342-plan-review-prompt.md docs/reviews/claude-code-stage-342-plan-review.md docs/reviews/opencode-stage-342-plan-review-prompt.md docs/reviews/opencode-stage-342-plan-review.md docs/reviews/claude-code-stage-342-code-review-prompt.md docs/reviews/claude-code-stage-342-code-review.md docs/superpowers/specs/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-design.md docs/superpowers/plans/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-plan.md src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}'; then exit 1; else echo "No token-shaped secrets in staged diff"; fi
```

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 342: add saved paragraph context cues"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

- [ ] **Step 6: Write handoff summary**

Report:

- repo state
- pushed commit
- verified commands
- uncommitted files
- next step recommendation
