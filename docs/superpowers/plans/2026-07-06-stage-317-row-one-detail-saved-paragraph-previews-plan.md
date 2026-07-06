# Stage 317 ROW ONE Detail Saved Paragraph Previews Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site detail-page saved paragraph previews inside organized local article content items, so ROW ONE shows source evidence at the content-section landing point created by Stage 316.

**Architecture:** Keep this as HTML presentation only in `templates.py`. Use existing local article sidecar fields, existing paragraph anchors, existing detail routes, and existing escaping/excerpt helpers. Do not change app/runtime/manifest payloads, schemas, extraction, scoring, connectors, LLM calls, or compliance-review behavior.

**Tech Stack:** Python, deterministic string-rendered HTML/CSS, existing ROW ONE Pydantic models, pytest, Ruff, Claude Code plan/code review workflow.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Create: `docs/reviews/claude-code-stage-317-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-317-plan-review.md`
- Later implementation review artifacts:
  - `docs/reviews/claude-code-stage-317-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-317-code-review.md`

---

### Task 1: Detail-Page Paragraph Preview Rendering

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add failing render tests**

Add focused tests in `tests/test_row_one_render.py` near the existing local article
detail tests:

```python
def test_render_row_one_detail_content_items_show_saved_paragraph_previews(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "First saved source paragraph about The Row.",
            "Second saved source paragraph about Margaux.",
            "Third saved source paragraph that should be capped.",
        ],
        paragraphs_zh=[
            "第一段保存正文，关于 The Row。",
            "第二段保存正文，关于 Margaux。",
            "第三段保存正文会被上限省略。",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        body=LocalizedText(en="Structured item body.", zh="结构化条目正文。"),
                        paragraph_indices=[0, 1, 2],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = detail_html[
        detail_html.index('id="local-article-content-section-1"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert 'class="local-article-content-previews"' in section_html
    assert '<span data-lang="en">Saved paragraph 1</span>' in section_html
    assert '<span data-lang="zh">保存段落 1</span>' in section_html
    assert '<span data-lang="en">Saved paragraph 2</span>' in section_html
    assert '<span data-lang="zh">保存段落 2</span>' in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-paragraph-2"' in section_html
    assert "First saved source paragraph about The Row." in section_html
    assert "第一段保存正文，关于 The Row。" in section_html
    assert "Second saved source paragraph about Margaux." in section_html
    assert "第二段保存正文，关于 Margaux。" in section_html
    assert "Third saved source paragraph that should be capped." not in section_html
```

Add a second test:

```python
def test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Valid <script>source</script> paragraph.",
            "   ",
            "Second valid paragraph.",
        ],
        paragraphs_zh=["中文长度不匹配。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        paragraph_indices=[0, 0, 1, -1, 99, 2],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        _edition(),
        tmp_path,
        local_articles_by_story_id={local_article.story_id: local_article},
    )

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    section_html = detail_html[
        detail_html.index('id="local-article-content-section-1"') : detail_html.index(
            'id="local-article-body"'
        )
    ]

    assert section_html.count('class="local-article-content-preview"') == 2
    assert "Valid &lt;script&gt;source&lt;/script&gt; paragraph." in section_html
    assert "Second valid paragraph." in section_html
    assert "中文长度不匹配。" not in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="#local-article-paragraph-2"' not in section_html
    assert 'href="#local-article-paragraph-3"' in section_html
```

- [ ] **Step 2: Verify render tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_content_items_show_saved_paragraph_previews \
  tests/test_row_one_render.py::test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape -q
```

Expected: fail because the preview class/labels are not rendered yet.

- [ ] **Step 3: Implement preview rendering**

In `src/fashion_radar/row_one/templates.py`:

- add constants near existing local article constants:

```python
LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS = 140
LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS = 2
```

- update `_render_local_article_content_sections()` so `_render_local_article_content_item()`
  receives `article=article`:

```python
rendered_items = "\n".join(
    _render_local_article_content_item(
        item,
        article=article,
        rendered_indices=rendered_indices,
    )
    for item in section.items
)
```

- update `_render_local_article_content_item()` signature:

```python
def _render_local_article_content_item(
    item: RowOneLocalArticleContentItem,
    *,
    article: RowOneLocalArticle,
    rendered_indices: set[int],
) -> str:
```

- render previews after the optional body and before existing meta/reference output:

```python
previews = _render_local_article_content_paragraph_previews(
    article,
    item,
    rendered_indices=rendered_indices,
)
...
if previews:
    parts.append(previews)
```

- add helper:

```python
def _render_local_article_content_paragraph_previews(
    article: RowOneLocalArticle,
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
    valid_indices = _valid_local_article_paragraph_indices(
        item.paragraph_indices,
        rendered_indices,
    )[:LOCAL_ARTICLE_CONTENT_PREVIEW_MAX_ITEMS]
    if not valid_indices:
        return ""
    aligned_zh = (
        article.paragraphs_zh if len(article.paragraphs_zh) == len(article.paragraphs) else []
    )
    previews = []
    for index in valid_indices:
        en = _local_article_content_preview_excerpt(article.paragraphs[index])
        href = f"#{_local_article_paragraph_anchor(index)}"
        label_en = f"Saved paragraph {index + 1}"
        label_zh = f"保存段落 {index + 1}"
        if aligned_zh and aligned_zh[index].strip():
            zh = _local_article_content_preview_excerpt(aligned_zh[index])
            body = (
                f'<span data-lang="en">{_esc(en)}</span>'
                f'<span data-lang="zh">{_esc(zh)}</span>'
            )
        else:
            body = _esc(en)
        previews.append(
            "            "
            f'<li class="local-article-content-preview">'
            f'<a href="{_esc(href)}">'
            f'<span data-lang="en">{_esc(label_en)}</span>'
            f'<span data-lang="zh">{_esc(label_zh)}</span>'
            f"<span>{body}</span>"
            "</a></li>"
        )
    return (
        '          <ul class="local-article-content-previews" '
        'aria-label="Saved paragraph previews">\n'
        + "\n".join(previews)
        + "\n          </ul>"
    )
```

- add excerpt helper:

```python
def _local_article_content_preview_excerpt(text: str) -> str:
    return _meta_description(
        normalize_row_one_paragraph(text),
        limit=LOCAL_ARTICLE_CONTENT_PREVIEW_EXCERPT_CHARS,
    )
```

- add CSS beside `.local-article-content-meta`:

```css
.local-article-content-previews {
  display: grid;
  gap: 8px;
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
}
.local-article-content-preview a {
  border: 1px solid var(--line);
  color: inherit;
  display: grid;
  gap: 4px;
  padding: 10px;
  text-decoration: none;
}
.local-article-content-preview a > span:first-child,
.local-article-content-preview a > span:nth-child(2) {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.local-article-content-preview a > span:last-child {
  line-height: 1.45;
}
```

- [ ] **Step 4: Verify render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_content_items_show_saved_paragraph_previews \
  tests/test_row_one_render.py::test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape -q
```

Expected: pass.

---

### Task 2: Workflow and Docs Boundary Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing workflow assertions**

Extend `tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`:

```python
assert "local-article-content-previews" in detail_html
assert "Saved paragraph" in detail_html
assert "保存段落" in detail_html
assert '"saved_paragraph_previews"' not in generated_contract_payload
```

Keep the existing SQLite immutability assertions, contract-version assertions, and
top-level `data/*.json` allowlist unchanged.

- [ ] **Step 2: Add failing docs guard**

In `tests/test_row_one_docs.py`, update Stage 316 slice boundaries:

```python
readme_stage_316 = readme[
    readme.index("Stage 316 adds local article content organization") : readme.index(
        "Stage 317 adds"
    )
]
docs_stage_316 = docs[
    docs.index("Stage 316 adds local article content organization") : docs.index(
        "Stage 317 adds"
    )
]
```

Add `test_row_one_docs_describe_detail_saved_paragraph_previews_boundary()` with:

```python
readme_stage_317 = readme[
    readme.index("Stage 317 adds detail saved paragraph previews") : readme.index(
        "Stage 310 adds"
    )
]
docs_stage_317 = docs[
    docs.index("Stage 317 adds detail saved paragraph previews") : docs.index(
        "Stage 310 adds"
    )
]
```

Expected phrases:

- `detail saved paragraph previews`
- `generated-site only`
- `existing \`data/articles/<story-id>.json\` sidecars`
- `existing saved local paragraphs`
- `existing \`content_sections\``
- `existing paragraph anchors`
- `does not change \`row-one-app/v7\``
- `does not change \`data/edition.json\``
- `does not change \`row-one-manifest/v1\``
- `does not change \`row-one-runtime/v1\``
- `does not change detail routes`
- `does not change paragraph anchors`
- `does not change schemas`
- `does not write a new json artifact`
- `does not add source collection`
- `does not fetch article pages`
- `does not add scoring`
- `does not add llm calls`
- `does not add connectors`
- `not a compliance review feature`

Forbidden phrases:

- `row-one-app/v8`
- `row-one-manifest/v2`
- `row-one-runtime/v2`
- `changes schemas`
- `adds source collection`
- `adds scoring`
- `adds llm calls`
- `adds social connectors`
- `adds community connectors`
- `adds compliance review`

- [ ] **Step 3: Verify workflow/docs tests fail**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary -q
```

Expected: fail because docs are not updated yet and workflow markers are not rendered before Task 1.

- [ ] **Step 4: Update docs**

Insert this paragraph after Stage 316 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 317 adds detail saved paragraph previews to generated ROW ONE detail
pages. It is generated-site only and turns existing
`data/articles/<story-id>.json` sidecars, existing saved local paragraphs, and
existing `content_sections` into compact paragraph previews that link to
existing paragraph anchors. It does not change `row-one-app/v7`, does not change
`data/edition.json`, does not change `row-one-manifest/v1`, does not change
`row-one-runtime/v1`, does not change detail routes, does not change paragraph
anchors, does not change schemas, does not write a new json artifact, does not
add source collection, does not fetch article pages, does not add scoring, does
not add llm calls, does not add connectors, and is not a compliance review
feature.
```

- [ ] **Step 5: Verify workflow/docs tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary -q
```

Expected: pass.

---

### Task 3: Review, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-317-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-317-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

Expected: pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/claude-code-stage-317-code-review-prompt.md` summarizing:

- Stage 317 goal
- files changed
- generated-site-only boundaries
- one-based existing paragraph anchors
- no app/runtime/manifest/schema changes
- focused verification already run

- [ ] **Step 3: Run Claude Code review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  -p "$(cat docs/reviews/claude-code-stage-317-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-317-code-review.md
```

Expected: no Critical or Important issues. Fix any Critical/Important before continuing.

- [ ] **Step 4: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git status --short --branch
```

Expected:

- full pytest passes
- lock check passes
- release hygiene passes
- only intended Stage 317 files are modified/untracked

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-317-code-review-prompt.md \
  docs/reviews/claude-code-stage-317-code-review.md \
  docs/reviews/claude-code-stage-317-plan-review-prompt.md \
  docs/reviews/claude-code-stage-317-plan-review.md \
  docs/superpowers/plans/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-plan.md \
  docs/superpowers/specs/2026-07-06-stage-317-row-one-detail-saved-paragraph-previews-design.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_docs.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py
git commit -m "Stage 317: add row one saved paragraph previews"
git push origin main
git status --short --branch
```

Expected: pushed to `origin/main`, clean worktree.

