# Stage 305 ROW ONE Local Article Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a compact internal navigation map to each structured ROW ONE local article detail section, so readers can jump between the brief, organized content cards, and full saved text without leaving the generated page.

**Architecture:** Keep this as a template/CSS-only detail-page enhancement. Reuse the existing `RowOneLocalArticle.brief_sections`, `content_sections`, `paragraphs`, and Stage 303 paragraph anchors; generate deterministic in-page anchors from render order rather than model-supplied titles. Do not change local article sidecar JSON, `data/edition.json`, `row-one-app/v7`, source collection, extraction, or homepage Daily Local Intelligence schema.

**Tech Stack:** Python 3.11 static HTML rendering in `src/fashion_radar/row_one/templates.py`, existing CSS emitted by `row_one_css()`, pytest render/docs tests, ruff, uv.

---

## Product Gap Closed

The user wants ROW ONE to feel like a professional fashion news site that organizes locally saved content rather than acting like a list of links. Stages 297-304 made local article bodies available, added structured sections, projected compact homepage intelligence, added paragraph anchors, and populated reference cards with source-backed excerpts. Stage 305 improves the reader workflow inside a detail page: once a local article exists, the page should expose a small map of its local article structure and make paragraph-link jumps visually findable.

## Design Read

Reading this as: editorial static news/detail pages for fashion intelligence review, with a restrained premium utility language, leaning toward existing ROW ONE CSS with small typographic navigation chips and no broad redesign.

## Scope Boundaries

In scope:

- Render a detail-page-only `local-article-map` inside `#local-article` when the local article has `brief_sections` or `content_sections`.
- Link the map to:
  - `#local-article-brief` when brief cards exist;
  - each content section via ordinal anchors such as `#local-article-content-section-1`;
  - `#local-article-body`.
- Add stable IDs to the local article brief wrapper, content cards, and body wrapper.
- Add restrained CSS for the local article map, paragraph-link anchors, and paragraph `:target` focus feedback.
- Preserve Stage 303 paragraph anchors exactly: `local-article-paragraph-{index + 1}`.
- Keep homepage Daily Local Intelligence cards free of local article internal anchors.
- Escape all model-supplied visible text.

Out of scope:

- No source acquisition, scraping, browser automation, social connectors, scheduler, monitoring, demand proof, platform coverage verification, image generation, app UI, dependency changes, schema changes, `row-one-app/v7` changes, `data/edition.json` changes, or compliance-review product features.
- No redesign of the homepage or detail page hierarchy.
- No new JSON fields or generated sample data.
- No title-derived IDs; section anchors must be renderer-generated ordinals.

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Add deterministic local article section/body anchor helpers.
  - Render a local article map between the local article title and brief/content blocks.
  - Add IDs to brief/content/body wrappers.
  - Add CSS for local article map, paragraph links, and paragraph targets.
- Modify `tests/test_row_one_render.py`
  - Extend existing detail-page tests to assert the map and IDs.
  - Assert plain paragraph-only local articles do not render a one-link map.
  - Assert homepage hrefs do not receive detail-only local article map fragments.
  - Assert CSS includes map and target rules.
  - Extend escaping coverage for map link titles.
- Modify `tests/test_row_one_docs.py`
  - Add docs drift wording for the local article map.
- Modify `README.md` and `docs/row-one.md`
  - Document the detail-page local article map and paragraph target feedback.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-305-plan-review-prompt.md`
  - `claude-code-stage-305-plan-review.md`
  - `opencode-stage-305-plan-review-prompt.md`
  - `opencode-stage-305-plan-review.md`
  - code review artifacts after implementation.

## Implementation Method

Use TDD:

1. Add render/CSS/docs assertions that fail because the local article map and wrapper IDs do not exist yet.
2. Implement the smallest template/CSS helpers to satisfy those tests.
3. Run focused ROW ONE tests, full verification, Claude Code code review, fix Critical/Important findings, commit, and push.

## Task 1: Detail Page Local Article Map

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Extend the main detail local article render test**

In `tests/test_row_one_render.py`, update `test_render_row_one_detail_includes_local_article_content` after the local article title/source assertions:

```python
    assert 'class="local-article-map"' in detail_html
    assert 'aria-label="ROW ONE local article map"' in detail_html
    assert 'href="#local-article-brief"' in detail_html
    assert 'href="#local-article-content-section-1"' in detail_html
    assert 'href="#local-article-content-section-2"' in detail_html
    assert 'href="#local-article-body"' in detail_html
    assert 'id="local-article-brief"' in detail_html
    assert 'id="local-article-content-section-1"' in detail_html
    assert 'id="local-article-content-section-2"' in detail_html
    assert 'id="local-article-body"' in detail_html
    assert '<span data-lang="en">Brief</span>' in detail_html
    assert '<span data-lang="zh">本地简报</span>' in detail_html
    assert detail_html.index('class="local-article-map"') < detail_html.index(
        'class="local-article-brief"'
    )
    assert detail_html.index('href="#local-article-content-section-1"') < detail_html.index(
        'id="local-article-content-section-1"'
    )
```

This proves the map exists, uses generated anchors, stays in the local article section, and appears before the structured content it links to.

- [ ] **Step 2: Assert section titles are map link text**

Add these assertions in the same test:

```python
    assert re.search(
        r'<a href="#local-article-content-section-1">\s*<span data-lang="en">Takeaways</span>\s*<span data-lang="zh">要点</span>\s*</a>',
        detail_html,
    )
    assert re.search(
        r'<a href="#local-article-content-section-2">\s*<span data-lang="en">Entities</span>\s*<span data-lang="zh">相关对象</span>\s*</a>',
        detail_html,
    )
```

- [ ] **Step 3: Add a plain local article negative assertion**

In `test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`, add:

```python
    assert 'class="local-article-map"' not in detail_html
    assert 'id="local-article-body"' in detail_html
```

Plain paragraph-only local articles should still get a body anchor, but no one-link map.

- [ ] **Step 4: Run focused render test and confirm failure**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs -q
```

Expected before implementation: fail on missing `local-article-map`, `local-article-brief`, `local-article-content-section-*`, and `local-article-body` IDs.

- [ ] **Step 5: Add anchor helpers**

In `src/fashion_radar/row_one/templates.py`, near `_local_article_paragraph_anchor`, add:

```python
def _local_article_content_section_anchor(position: int) -> str:
    return f"local-article-content-section-{position}"
```

Use ordinal anchors from render order. Do not slug section titles.

- [ ] **Step 6: Render the local article map**

Add this helper near `_render_local_article_brief`:

```python
def _render_local_article_map(article: RowOneLocalArticle) -> str:
    if not article.brief_sections and not article.content_sections:
        return ""
    links = []
    if article.brief_sections:
        links.append(
            '<a href="#local-article-brief">'
            '<span data-lang="en">Brief</span>'
            '<span data-lang="zh">本地简报</span>'
            "</a>"
        )
    for position, section in enumerate(article.content_sections, start=1):
        anchor = f"#{_local_article_content_section_anchor(position)}"
        links.append(
            f'<a href="{_esc(anchor)}">'
            f'<span data-lang="en">{_esc(section.title.en)}</span>'
            f'<span data-lang="zh">{_esc(section.title.zh)}</span>'
            "</a>"
        )
    links.append(
        '<a href="#local-article-body">'
        '<span data-lang="en">Full saved text</span>'
        '<span data-lang="zh">完整保存正文</span>'
        "</a>"
    )
    return (
        '      <nav class="local-article-map" aria-label="ROW ONE local article map">\n'
        + "\n".join(f"        {link}" for link in links)
        + "\n      </nav>"
    )
```

Then in `_render_local_article`, compute:

```python
    article_map = _render_local_article_map(article)
```

and insert `{article_map}` after `<h3>{_esc(title)}</h3>`.

- [ ] **Step 7: Add IDs to brief, content sections, and body**

Change `_render_local_article_brief` return wrapper from:

```python
return f"""      <div class="local-article-brief" aria-label="ROW ONE brief">
```

to:

```python
return f"""      <div id="local-article-brief" class="local-article-brief" aria-label="ROW ONE brief">
```

In `_render_local_article_content_sections`, update the loop to:

```python
    for position, section in enumerate(article.content_sections, start=1):
        section_anchor = _local_article_content_section_anchor(position)
        section_parts = [
            f'        <article id="{_esc(section_anchor)}" class="local-article-content-card">',
```

In `_render_local_article`, change:

```python
      <div class="local-article-body">
```

to:

```python
      <div id="local-article-body" class="local-article-body">
```

- [ ] **Step 8: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs -q
```

Expected: pass.

## Task 2: Styling And Homepage Guard

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add CSS assertions**

In `tests/test_row_one_render.py`, extend the existing CSS asset test or add a focused test near `test_row_one_css_includes_edition_brief_styles`:

```python
def test_row_one_css_includes_local_article_map_styles(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    css_text = (tmp_path / "assets" / "row-one.css").read_text(encoding="utf-8")

    assert ".local-article-map" in css_text
    assert ".local-article-map a" in css_text
    assert ".local-article-content-paragraph-links a" in css_text
    assert ".local-article-body p:target" in css_text
```

- [ ] **Step 2: Extend homepage href guard**

In `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments`, extend the existing href scan:

```python
    homepage_hrefs = "".join(re.findall(r'href="([^"]+)"', html))
    assert "#local-article-paragraph-" not in homepage_hrefs
    assert "#local-article-content-section-" not in homepage_hrefs
    assert "#local-article-body" not in homepage_hrefs
```

Replace the existing one-line paragraph href guard with this variable to avoid duplicate regex work.

- [ ] **Step 3: Run tests and confirm CSS failure before implementation**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_row_one_css_includes_local_article_map_styles \
  tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments -q
```

Expected before CSS implementation: fail on missing CSS selectors.

- [ ] **Step 4: Add CSS**

In `row_one_css()` near the existing local article rules, add:

```css
.local-article-map {
  border: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 22px;
  padding: 12px;
}
.local-article-map a,
.local-article-content-paragraph-links a {
  border: 1px solid var(--line);
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 7px 9px;
  text-decoration: none;
}
.local-article-content-paragraph-links a {
  display: inline-block;
  margin: 0 4px 4px 0;
}
.local-article-body p:target {
  background: var(--panel);
  outline: 1px solid var(--accent);
  outline-offset: 4px;
}
```

Keep this restrained; no broad redesign.

- [ ] **Step 5: Run focused render/CSS tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: pass.

## Task 3: Escaping And Docs Drift

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Extend escaping test for map links**

In `test_render_row_one_site_escapes_local_article_content`, add assertions after the existing escaped content-section title assertions:

```python
    assert 'href="#local-article-content-section-1"' in detail_html
    assert "&lt;script&gt;Section&lt;/script&gt;" in detail_html
    assert 'href="#local-article-body"' in detail_html
```

The existing raw `<script>` / `<img>` absence assertions cover the new duplicated section-title map text.

- [ ] **Step 2: Extend docs drift test**

In `test_row_one_docs_describe_daily_local_intelligence`, add:

```python
    assert "local article map" in readme
    assert "paragraph target highlight" in row_one_docs
```

- [ ] **Step 3: Run docs test and confirm failure before docs update**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected before docs update: fail on the new phrases.

- [ ] **Step 4: Update README**

Near the local article paragraph in `README.md`, add:

```markdown
Structured local articles also include a detail-page local article map so readers can jump between the brief, organized content cards, and full saved text.
```

- [ ] **Step 5: Update docs/row-one.md**

Near the local article section in `docs/row-one.md`, add:

```markdown
Detail pages render a local article map for structured saved articles, and paragraph target highlight styling makes in-page paragraph jumps visibly land on the referenced saved text.
```

- [ ] **Step 6: Run focused docs/render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_local_article_content \
  tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected: pass.

## Task 4: Review, Verification, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-305-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-305-code-review.md`
- Possibly add rereview artifacts if Critical or Important findings are fixed.

- [ ] **Step 1: Run focused stage checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

Expected: pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

Expected:

- `pytest -q`: all tests pass.
- `ruff check`: all checks passed.
- `ruff format --check`: all files already formatted.
- Release hygiene: passed.
- Lock check: resolved without modifying `uv.lock`.

- [ ] **Step 3: Create Claude Code code review prompt**

Create `docs/reviews/claude-code-stage-305-code-review-prompt.md` with:

```markdown
# Claude Code Stage 305 Code Review Prompt

You are reviewing Stage 305 code changes for `/home/ubuntu/fashion-radar`.

Base commit: `<base-sha>`
Plan: `docs/superpowers/plans/2026-07-05-stage-305-row-one-local-article-map-plan.md`
Plan reviews:
- `docs/reviews/claude-code-stage-305-plan-review.md`
- `docs/reviews/opencode-stage-305-plan-review.md`

Changed files to review:
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 305 plan/review artifacts

Review objective:
- Confirm structured local article detail pages render a local article map linking to brief, content sections, and full saved text.
- Confirm generated IDs are deterministic renderer-owned anchors and not title-derived.
- Confirm Stage 303 paragraph anchors remain unchanged.
- Confirm plain paragraph-only local articles do not get a one-link local article map.
- Confirm homepage Daily Local Intelligence does not gain detail-only map or paragraph href fragments.
- Confirm CSS is restrained, readable, and scoped to local article map/paragraph target feedback.
- Confirm all model-supplied text remains escaped.
- Confirm no data schema, app contract, source acquisition, scraping, dependency, scheduling, image, demand proof, platform coverage, or compliance-review feature was added.
- Confirm tests would fail for missing map anchors, homepage contamination, escaping regressions, and CSS omissions.

Verification already run after latest changes:
- `<commands and results>`

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
```

- [ ] **Step 4: Run Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-305-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-305-code-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings before continuing.

- [ ] **Step 5: Commit only Stage 305 files**

Run:

```bash
git status --short --branch
git add \
  README.md \
  docs/row-one.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  docs/superpowers/plans/2026-07-05-stage-305-row-one-local-article-map-plan.md \
  docs/reviews/claude-code-stage-305-plan-review-prompt.md \
  docs/reviews/claude-code-stage-305-plan-review.md \
  docs/reviews/opencode-stage-305-plan-review-prompt.md \
  docs/reviews/opencode-stage-305-plan-review.md \
  docs/reviews/claude-code-stage-305-code-review-prompt.md \
  docs/reviews/claude-code-stage-305-code-review.md
git diff --cached --check
git commit -m "Stage 305: add row one local article map"
git push origin main
```

Do not commit `uv.lock`; this stage should not change dependencies.

## Self-Review

- Spec coverage: The plan improves local saved-content readability through detail-page internal navigation and paragraph target feedback, directly supporting the user's request for organized content presentation.
- Placeholder scan: No TBD/TODO/implement-later placeholders remain.
- Type consistency: The plan uses existing `RowOneLocalArticle` fields, existing template helpers, and generated anchors with stable names.
- Risk control: The change is template/CSS-only, verified through render tests, docs tests, full pytest, ruff, release hygiene, lock check, and Claude Code review.
