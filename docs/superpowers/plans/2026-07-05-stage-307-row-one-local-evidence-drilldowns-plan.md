# ROW ONE Local Evidence Drilldowns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let ROW ONE homepage Daily Local Intelligence cards link directly to the exact saved local article paragraph evidence that supports each organized item.

**Architecture:** Keep `row-one-app/v7`, sidecar JSON shapes, local article models, and detail-page article rendering unchanged. Fix the existing aggregate detail-path/source mismatch first, then change homepage Daily Local Intelligence cards from full-card anchors into non-anchor cards with explicit safe same-site links to the saved article section and capped paragraph anchors.

**Tech Stack:** Python 3.13, Typer, Pydantic, pytest, ruff, existing ROW ONE static HTML/CSS renderer.

---

## Scope

In scope:
- `src/fashion_radar/row_one/local_intelligence.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_local_intelligence.py`
- `tests/test_row_one_render.py`
- `docs/row-one.md`
- `README.md`
- `tests/test_row_one_docs.py`
- Stage 307 review artifacts under `docs/reviews/`

Out of scope:
- External collectors, scraping integrations, platform adapters, LLM/image calls, scheduler/server behavior, dependency changes, schema version bumps, app contract changes, sidecar JSON schema creation, ROW ONE visual redesign, and compliance-review product features.

## Current Evidence

- `build_row_one_local_article_intelligence()` already emits `detail_path`, `paragraph_indices`, and structured `segments` for homepage Daily Local Intelligence items.
- `_render_daily_local_intelligence_item()` currently wraps the entire card in `<a class="daily-local-intelligence-card" href="...#local-article">...</a>`.
- `_render_daily_local_intelligence_segment_meta()` currently renders paragraph metadata as plain text.
- `_safe_daily_local_intelligence_href()` only accepts detail paths with no fragment or `#local-article`.
- New homepage action and paragraph-link anchors must receive minimal CSS in `row_one_css()` so Stage 307 does not regress link presentation into default browser styling.
- `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments()` currently asserts homepage hrefs do not include `#local-article-paragraph-`, so Stage 307 must replace that assertion deliberately.
- `test_reference_segments_can_upgrade_from_fallback_to_later_match()` currently proves the later segment wins but does not assert `detail_path`, leaving a link/body mismatch risk.

---

### Task 1: Fix Aggregate Detail Path Source Alignment

**Files:**
- Modify: `tests/test_row_one_local_intelligence.py`
- Modify: `src/fashion_radar/row_one/local_intelligence.py`

- [ ] **Step 1: Write the failing test**

Extend `test_reference_segments_can_upgrade_from_fallback_to_later_match()` so the selected aggregate item must point to the later matched article:

```python
    assert item.detail_path == "details/story-b-1234567890.html#local-article"
```

- [ ] **Step 2: Run the red test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py::test_reference_segments_can_upgrade_from_fallback_to_later_match
```

Expected: failure showing current `item.detail_path` is `details/story-a-1234567890.html#local-article`.

- [ ] **Step 3: Implement the minimal source alignment fix**

In `_reference_watch_section()`, update the aggregate detail path when a better source text/segment wins:

```python
            if aggregate.body is None or segment_match_score > aggregate.segment_match_score:
                aggregate.body = source_text.en
                aggregate.body_zh = source_text.zh
                aggregate.paragraph_indices = paragraph_indices
                aggregate.segments = segments
                aggregate.segment_match_score = segment_match_score
                aggregate.detail_path = _local_article_detail_path(story.detail_path)
            elif aggregate.detail_path is None:
                aggregate.detail_path = _local_article_detail_path(story.detail_path)
```

This preserves the existing first-detail fallback while ensuring displayed body/paragraph metadata and the link target belong to the same story when the aggregate upgrades.

- [ ] **Step 4: Run the green test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py::test_reference_segments_can_upgrade_from_fallback_to_later_match
```

Expected: pass.

---

### Task 2: Render Explicit Saved Text And Paragraph Links On Homepage Cards

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Write failing render tests for card actions**

Update `test_render_row_one_site_includes_daily_local_intelligence()` to expect explicit action links instead of relying on the whole card anchor:

```python
    assert '<a class="daily-local-intelligence-action" href="details/the-row-signal-1234567890.html#local-article">' in html
    assert "<span data-lang=\"en\">Open saved text</span>" in html
    assert "<span data-lang=\"zh\">打开本地正文</span>" in html
    assert '<a class="daily-local-intelligence-card"' not in html
```

Update `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments()` by replacing the current negative paragraph-anchor assertions with positive paragraph drilldown checks:

```python
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
    assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-2"' in html
    assert "Paragraph 1" in html
    assert "段落 1" in html
```

Add a nested-anchor guard to the same test:

```python
    assert '<a class="daily-local-intelligence-card"' not in html
```

Add CSS coverage in the same render test by importing or using the existing `row_one_css()` helper:

```python
    css = row_one_css()
    assert ".daily-local-intelligence-actions" in css
    assert ".daily-local-intelligence-action" in css
    assert ".daily-local-intelligence-paragraph-link" in css
```

- [ ] **Step 2: Run red render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_render_row_one_site_includes_daily_local_intelligence tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments
```

Expected: fail because the current renderer wraps cards in anchors and paragraph metadata is not linked.

- [ ] **Step 3: Implement explicit action link rendering**

Replace `_render_daily_local_intelligence_item()` so it always returns a `<div>` card and adds action links through a new helper:

```python
def _render_daily_local_intelligence_item(item: RowOneDailyLocalIntelligenceItem) -> str:
    href = _safe_daily_local_intelligence_href(item.detail_path)
    meta = _daily_local_intelligence_meta(item)
    segments = _render_daily_local_intelligence_segments(item, detail_href=href)
    actions = _render_daily_local_intelligence_actions(item, detail_href=href)
    body = f"""<h3>
    <span data-lang="en">{_esc(item.title.en)}</span>
    <span data-lang="zh">{_esc(item.title.zh)}</span>
  </h3>
  <p>
    <span data-lang="en">{_esc(item.body.en)}</span>
    <span data-lang="zh">{_esc(item.body.zh)}</span>
  </p>
  {segments}
  <div class="daily-local-intelligence-meta">{meta}</div>
  {actions}"""
    return f'<div class="daily-local-intelligence-card">{body}</div>'
```

Add helper:

```python
def _render_daily_local_intelligence_actions(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    if detail_href is None:
        return ""
    links = [
        (
            detail_href,
            "Open saved text",
            "打开本地正文",
        )
    ]
    for index in _daily_local_intelligence_paragraph_indices(item)[:3]:
        href = _daily_local_intelligence_paragraph_href(detail_href, index)
        if href is None:
            continue
        label = index + 1
        links.append((href, f"Open paragraph {label}", f"打开段落 {label}"))
    rendered = "".join(
        f'<a class="daily-local-intelligence-action" href="{_esc(href)}">'
        f'<span data-lang="en">{_esc(en)}</span>'
        f'<span data-lang="zh">{_esc(zh)}</span>'
        "</a>"
        for href, en, zh in links
    )
    return f'<div class="daily-local-intelligence-actions">{rendered}</div>' if rendered else ""
```

Add paragraph collection helper:

```python
def _daily_local_intelligence_paragraph_indices(
    item: RowOneDailyLocalIntelligenceItem,
) -> list[int]:
    indices: list[int] = []
    seen: set[int] = set()
    for index in item.paragraph_indices:
        if index >= 0 and index not in seen:
            seen.add(index)
            indices.append(index)
    for segment in item.segments:
        for segment_item in segment.items:
            for index in segment_item.paragraph_indices:
                if index >= 0 and index not in seen:
                    seen.add(index)
                    indices.append(index)
    return indices
```

Add paragraph href helper:

```python
def _daily_local_intelligence_paragraph_href(
    detail_href: str,
    index: int,
) -> str | None:
    if index < 0:
        return None
    path = detail_href.split("#", 1)[0]
    return f"{path}#local-article-paragraph-{index + 1}"
```

`detail_href` must already be the sanitized output of `_safe_daily_local_intelligence_href(item.detail_path)`, so this helper only replaces the fragment and does not re-run validation.

- [ ] **Step 4: Pass detail href into segment rendering**

Update the segment helpers:

```python
def _render_daily_local_intelligence_segments(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    detail_href: str | None,
) -> str:
    segments = [
        _render_daily_local_intelligence_segment(segment, detail_href=detail_href)
        for segment in item.segments
    ]
```

```python
def _render_daily_local_intelligence_segment(
    segment: RowOneDailyLocalIntelligenceSegment,
    *,
    detail_href: str | None,
) -> str:
    items = [
        _render_daily_local_intelligence_segment_item(
            segment_item,
            detail_href=detail_href,
        )
        for segment_item in segment.items
    ]
```

```python
def _render_daily_local_intelligence_segment_item(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
```

Update `_render_daily_local_intelligence_segment_meta()` to accept `detail_href` and render paragraph links when safe:

```python
def _render_daily_local_intelligence_segment_meta(
    segment_item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    detail_href: str | None,
) -> str:
    parts: list[str] = []
    for ref in segment_item.references:
        ref_text = " / ".join(value for value in (ref.name, ref.type, ref.label) if value)
        parts.append(
            f'<span><span data-lang="en">{_esc(ref_text)}</span>'
            f'<span data-lang="zh">{_esc(ref_text)}</span></span>'
        )
    for index in segment_item.paragraph_indices:
        paragraph_label = index + 1
        href = (
            _daily_local_intelligence_paragraph_href(detail_href, index)
            if detail_href is not None
            else None
        )
        label = (
            f'<span data-lang="en">Paragraph {paragraph_label}</span>'
            f'<span data-lang="zh">段落 {paragraph_label}</span>'
        )
        if href is None:
            parts.append(f"<span>{label}</span>")
        else:
            parts.append(
                f'<a class="daily-local-intelligence-paragraph-link" href="{_esc(href)}">'
                f"{label}</a>"
            )
    if not parts:
        return ""
    return f'<div class="daily-local-intelligence-segment-meta">{"".join(parts)}</div>'
```

- [ ] **Step 5: Add minimal CSS for new local evidence links**

In `row_one_css()`, add scoped rules near the existing Daily Local Intelligence styles:

```css
.daily-local-intelligence-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.85rem;
}

.daily-local-intelligence-action,
.daily-local-intelligence-paragraph-link {
  color: inherit;
  text-decoration: none;
}

.daily-local-intelligence-action {
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.daily-local-intelligence-paragraph-link {
  border-bottom: 1px solid currentColor;
}
```

These styles are intentionally minimal: they make the new anchors look like ROW ONE UI elements without changing layout hierarchy or redesigning the section.

- [ ] **Step 6: Run green render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_render_row_one_site_includes_daily_local_intelligence tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments
```

Expected: pass.

- [ ] **Step 7: Run the existing escaping regression**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_local_intelligence
```

Expected: pass, proving the renderer refactor still escapes Daily Local Intelligence text and link labels.

---

### Task 3: Expand Safe Fragment Validation For Local Article Paragraph Anchors

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Write failing href validator tests**

Extend `test_safe_daily_local_intelligence_href_accepts_only_safe_detail_links` with:

```python
        (
            "details/the-row-signal-1234567890.html#local-article-paragraph-1",
            "details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
        (
            "details/the-row-signal-1234567890.html#local-article-paragraph-42",
            "details/the-row-signal-1234567890.html#local-article-paragraph-42",
        ),
        ("details/the-row-signal-1234567890.html#local-article-paragraph-0", None),
        ("details/the-row-signal-1234567890.html#local-article-paragraph-x", None),
        ("details/the-row-signal-1234567890.html#local-article-body", None),
        ("details/the-row-signal-1234567890.html#local-article-content-section-1", None),
```

- [ ] **Step 2: Run the red validator test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_safe_daily_local_intelligence_href_accepts_only_safe_detail_links
```

Expected: fail for valid paragraph fragments because the current helper only accepts `#local-article`.

- [ ] **Step 3: Implement strict local article fragment validation**

Add a regex near existing detail path constants:

```python
_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")
```

Update `_safe_daily_local_intelligence_href()`:

```python
def _safe_daily_local_intelligence_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return href if _validated_detail_relative_path(href) is not None else None
    path, fragment = href.split("#", 1)
    if fragment != "local-article" and not _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(
        fragment
    ):
        return None
    return href if _validated_detail_relative_path(path) is not None else None
```

- [ ] **Step 4: Run green validator test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_safe_daily_local_intelligence_href_accepts_only_safe_detail_links
```

Expected: pass.

---

### Task 4: Update Docs For Homepage Evidence Drilldowns

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Write docs drift tests**

Add assertions to the existing `test_row_one_docs_describe_daily_local_intelligence()` test requiring these phrases:

```python
assert "homepage Daily Local Intelligence cards include local saved-text and paragraph drilldown links" in readme
assert "data/local-intelligence.json" in row_one_docs
```

Use the existing helper style in `tests/test_row_one_docs.py`; do not introduce a new docs parser.

- [ ] **Step 2: Run docs tests red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_docs.py
```

Expected: fail because docs do not yet describe homepage paragraph drilldown links and `data/local-intelligence.json` is missing from the generated files block.

- [ ] **Step 3: Update docs**

Update README ROW ONE description to mention:

```text
Homepage Daily Local Intelligence cards include local saved-text and paragraph drilldown links when source-backed local article paragraphs are available.
```

Update `docs/row-one.md` generated files list to include:

```text
- `data/local-intelligence.json` — optional sidecar with homepage Daily Local Intelligence sections derived from current saved local article bodies.
```

Add a short usage note:

```text
The homepage keeps local article bodies out of `data/edition.json`; when `data/local-intelligence.json` is present, cards link back to generated detail pages and exact `#local-article-paragraph-N` anchors.
```

- [ ] **Step 4: Run docs tests green**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_docs.py
```

Expected: pass.

---

### Task 5: Focused Verification And Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-307-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-307-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: all pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

Expected: all pass and `uv.lock` remains free of mirror URL rewrites.

- [ ] **Step 3: Request Claude Code implementation review**

Create `docs/reviews/claude-code-stage-307-code-review-prompt.md` with:
- base SHA `f774eff`
- changed files
- the Stage 307 requirements above
- verification commands and results
- explicit review objective: no nested anchors, safe local-only fragments, aggregate detail path aligns with displayed source, no app contract/schema bump, no external acquisition changes.

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-307-code-review-prompt.md)" > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-307-code-review.md
rm -f "$tmp_review"
```

Expected: `APPROVE` or `APPROVE_WITH_NOTES` with no Critical or Important issues. Fix any Critical or Important issues before committing.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add README.md docs/row-one.md src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py docs/reviews/claude-code-stage-307-code-review-prompt.md docs/reviews/claude-code-stage-307-code-review.md docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md
git commit -m "Stage 307: add row one local evidence drilldowns"
git push origin main
```

Expected: push succeeds and worktree is clean.

---

## Self-Review

- Spec coverage: The plan implements homepage evidence drilldowns, fixes the identified aggregate link/body mismatch, expands safe href validation only for generated local article paragraph anchors, and updates docs/tests.
- Placeholder scan: No TBD/TODO/implement-later placeholders remain.
- Boundary check: The plan does not add collectors, schemas, app contract version bumps, dependencies, scheduling/server changes, image generation, or compliance-review product behavior.
