# Stage 303 ROW ONE Local Article Paragraph Anchors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add stable paragraph anchors and in-page links for ROW ONE saved local article detail pages so readers can jump from organized takeaways, entities, and products to the exact saved source paragraph.

**Architecture:** Keep the existing saved local article sidecar model unchanged and add deterministic anchor rendering in the static detail-page HTML template. Detail pages will assign stable `id="local-article-paragraph-N"` anchors to rendered local article paragraphs, convert valid `paragraph_indices` metadata to safe in-page links, and omit invalid indices to avoid broken links. This stage deliberately does not add homepage Daily Local Intelligence paragraph links because those cards can be rendered as outer anchors, and nested `<a>` tags would be invalid HTML.

**Tech Stack:** Python 3.12, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stage 302 made Daily Local Intelligence cards show compact source-backed content segments. Stage 303 completes the detail-page reader path from organized content sections to local evidence: every valid detail-page paragraph-index badge becomes a navigable pointer to the exact saved local article paragraph. This improves information organization without adding scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.

## Scope Boundaries

- In scope: detail-page local article body paragraph IDs and detail-page content-section paragraph links.
- In scope: a homepage regression assertion that Daily Local Intelligence paragraph metadata remains plain text in this stage.
- Out of scope: homepage paragraph links, `_safe_daily_local_intelligence_href()` fragment expansion, Daily Local Intelligence card markup redesign, new JSON fields, source acquisition, app UI, social connectors, and paragraph availability data in `data/local-intelligence.json`.
- Anchor IDs are generated only from original zero-based `RowOneLocalArticle.paragraphs` indices. If `article.paragraphs[0]` is blank and `article.paragraphs[1]` renders, the rendered paragraph keeps `id="local-article-paragraph-2"` and metadata index `1` links to that ID.

## File Structure

- Modify `src/fashion_radar/row_one/templates.py`
  - Add stable helper functions for local article paragraph anchor IDs and valid rendered indices.
  - Add paragraph IDs to both bilingual and plain local article paragraph render paths.
  - Validate `paragraph_indices` against original indices whose source paragraphs actually rendered.
  - Render detail-page content-section paragraph metadata as bilingual in-page anchor links.
  - Rename the local paragraph metadata renderer from `_render_local_article_paragraph_indices` to `_render_local_article_paragraph_links` because it will emit link markup.
  - Keep homepage Daily Local Intelligence segment paragraph metadata unchanged to avoid invalid nested anchors inside linked cards.
  - Keep all existing user/source-controlled labels, bodies, and refs escaped.
- Modify `tests/test_row_one_render.py`
  - Add RED assertions to existing local article detail tests for paragraph IDs and paragraph-index links.
  - Add tests for plain local article paragraphs without `paragraphs_zh`.
  - Add tests for zh-mismatch plain rendering.
  - Add tests for invalid/out-of-range/blank-paragraph/duplicate paragraph indices.
  - Add a regression assertion that homepage Daily Local Intelligence segment metadata remains non-linked plain metadata in this stage.
- Modify `README.md` and `tests/test_row_one_docs.py`
  - Document that generated detail pages link content-section paragraph badges to anchored saved local paragraphs.

## Task 1: Review Gate

- [ ] **Step 1: Create Claude Code plan review prompt**

Create `docs/reviews/claude-code-stage-303-plan-review-prompt.md`:

```markdown
# Claude Code Stage 303 Plan Review Prompt

You are reviewing the Stage 303 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether stable local paragraph anchors and detail-page paragraph-index links are a sound next step after Stage 302 content segments.
- Check that the plan intentionally defers homepage paragraph links to avoid nested anchors and wrong-article aggregate links.
- Check that the plan preserves the free-first/local-first boundary and avoids scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.
- Check that generated links are safe, deterministic, and do not affect `data/edition.json`, `data/local-intelligence.json`, or `row-one-app/v7`.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
```

- [ ] **Step 2: Run Claude Code plan review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-303-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-303-plan-review.md
rm -f "$tmp_review"
```

Expected: a coherent review body with a clear verdict. If Claude Code exits without a usable review body or times out, write `docs/reviews/claude-code-stage-303-plan-review.md` with `Verdict: UNAVAILABLE` and the exact non-secret failure reason.

- [ ] **Step 3: Create opencode plan review/revision prompt**

Create `docs/reviews/opencode-stage-303-plan-review-prompt.md`:

```markdown
# opencode Stage 303 Plan Review Prompt

You are reviewing the Stage 303 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`
Claude Code review: `docs/reviews/claude-code-stage-303-plan-review.md`

After Claude Code's review, revise the plan based on that review and your own judgment. If Claude Code is unavailable, act as fallback reviewer. Use GLM 5.2 max judgment.

Review objective:
- Confirm the detail-page paragraph-anchor/linking approach is technically reasonable.
- Check that homepage paragraph links are deliberately deferred to avoid nested anchors, wrong-article aggregate links, and broken fragment links.
- Check that implementation remains local-first and deterministic, with no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product feature.
- Check that links are safe and that `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` remain unchanged.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required plan changes, if any
```

- [ ] **Step 4: Run opencode plan review/revision**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-303-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-303-plan-review.md
rm -f "$tmp_review"
```

Expected: a coherent review body with a clear verdict and no live-capture stubs.

- [ ] **Step 5: Apply plan-review findings**

If either review returns Critical or Important findings, update this plan before implementation and record rereview artifacts as `docs/reviews/*stage-303-plan-rereview*`.

## Task 2: RED Detail-Page Anchor Tests

- [ ] **Step 1: Extend `test_render_row_one_detail_includes_local_article_content`**

Add these assertions after the current paragraph text assertions in `tests/test_row_one_render.py`:

```python
assert 'id="local-article-paragraph-1"' in detail_html
assert 'id="local-article-paragraph-2"' in detail_html
assert 'href="#local-article-paragraph-1"' in detail_html
assert re.search(r'<a href="#local-article-paragraph-1">\s*Paragraph 1\s*</a>', detail_html)
assert re.search(r'<a href="#local-article-paragraph-1">\s*段落 1\s*</a>', detail_html)
assert detail_html.index('href="#local-article-paragraph-1"') < detail_html.index(
    'id="local-article-paragraph-1"'
)
```

- [ ] **Step 2: Extend plain and zh-mismatch branch tests**

Update `test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`:

```python
assert '<p id="local-article-paragraph-1">One source paragraph.</p>' in detail_html
assert '<p id="local-article-paragraph-2">Second source paragraph.</p>' in detail_html
```

Replace the existing exact assertions `"<p>One source paragraph.</p>"` and `"<p>Second source paragraph.</p>"`; do not keep them, because the `<p>` opening tag will include the new `id` attribute.

Update `test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch`:

```python
assert '<p id="local-article-paragraph-1">One source paragraph.</p>' in detail_html
assert '<p id="local-article-paragraph-2">Second source paragraph.</p>' in detail_html
assert 'href="#local-article-paragraph-1"' in detail_html
```

Replace the existing exact assertions `"<p>One source paragraph.</p>"` and `"<p>Second source paragraph.</p>"`; do not keep them, because the `<p>` opening tag will include the new `id` attribute.

- [ ] **Step 3: Add RED test for invalid, blank, and duplicate paragraph indices**

Add this test near the local article rendering tests:

```python
def test_render_row_one_detail_skips_invalid_local_article_paragraph_links(tmp_path) -> None:
    local_article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="Source article title",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["First rendered paragraph.", "   ", "Third rendered paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(en="Takeaways", zh="要点"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(en="Source lead", zh="来源导语"),
                        paragraph_indices=[-1, 0, 1, 2, 2, 99],
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

    assert 'id="local-article-paragraph-1"' in detail_html
    assert 'id="local-article-paragraph-2"' not in detail_html
    assert 'id="local-article-paragraph-3"' in detail_html
    assert 'href="#local-article-paragraph-1"' in detail_html
    assert 'href="#local-article-paragraph-3"' in detail_html
    assert detail_html.count('href="#local-article-paragraph-3"') == 2
    assert 'href="#local-article-paragraph-0"' not in detail_html
    assert 'href="#local-article-paragraph-2"' not in detail_html
    assert 'href="#local-article-paragraph-100"' not in detail_html
    assert "Paragraph 0" not in detail_html
    assert "Paragraph 2" not in detail_html
    assert "Paragraph 100" not in detail_html
    assert "段落 0" not in detail_html
    assert "段落 2" not in detail_html
    assert "段落 100" not in detail_html
```

The count is `2` because English and Chinese language spans each contain one anchor to paragraph 3. Duplicate paragraph index `2` should not produce extra links.

- [ ] **Step 4: Extend escaping coverage lightly**

Update `test_render_row_one_detail_escapes_local_article_content`:

```python
assert 'href="#local-article-paragraph-1"' in detail_html
assert 'id="local-article-paragraph-1"' in detail_html
```

- [ ] **Step 5: Add homepage deferral regression assertion**

Extend `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments`:

```python
assert '#local-article-paragraph-' not in "".join(re.findall(r'href="([^"]+)"', html))
assert "Paragraph 1" in html
assert "段落 1" in html
```

This inspects all homepage href values rather than one specific story path, so it catches nested paragraph links, wrong-article paragraph links, and broken paragraph fragments anywhere on the homepage.

- [ ] **Step 6: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch \
  tests/test_row_one_render.py::test_render_row_one_detail_skips_invalid_local_article_paragraph_links \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments
```

Expected: FAIL because local article paragraphs currently have no IDs and detail-page paragraph metadata is plain text.

## Task 3: Implement Detail-Page Paragraph Anchors

- [ ] **Step 1: Add anchor helpers**

In `src/fashion_radar/row_one/templates.py`, add near local article helpers:

```python
def _local_article_paragraph_anchor(index: int) -> str:
    # paragraph_indices are zero-based; fragment IDs are one-based for readers.
    return f"local-article-paragraph-{index + 1}"


def _valid_local_article_paragraph_indices(
    indices: list[int],
    rendered_indices: set[int],
) -> list[int]:
    # paragraph_indices and rendered_indices both use original zero-based
    # RowOneLocalArticle.paragraphs positions; blank source paragraphs are absent.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index not in rendered_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid
```

- [ ] **Step 2: Pass rendered source indices to content sections**

Update `_render_local_article(article)`:

```python
paragraphs = _render_local_article_paragraphs(article)
...
content_sections = _render_local_article_content_sections(
    article,
    rendered_indices=_local_article_rendered_paragraph_indices(article),
)
```

Add:

```python
def _local_article_rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}
```

Update signatures:

```python
def _render_local_article_content_sections(
    article: RowOneLocalArticle,
    *,
    rendered_indices: set[int],
) -> str:
...
def _render_local_article_content_item(
    item: RowOneLocalArticleContentItem,
    *,
    rendered_indices: set[int],
) -> str:
...
def _render_local_article_paragraph_links(
    indices: list[int],
    *,
    rendered_indices: set[int],
) -> str:
```

- [ ] **Step 3: Render detail paragraph metadata as safe anchor links**

Rename `_render_local_article_paragraph_indices` to `_render_local_article_paragraph_links` and replace its body with link generation:

```python
valid_indices = _valid_local_article_paragraph_indices(indices, rendered_indices)
if not valid_indices:
    return ""

en_links = []
zh_links = []
for index in valid_indices:
    anchor = _local_article_paragraph_anchor(index)
    href = f"#{anchor}"
    en_links.append(f'<a href="{_esc(href)}">Paragraph {index + 1}</a>')
    zh_links.append(f'<a href="{_esc(href)}">段落 {index + 1}</a>')

return f"""              <p class="local-article-content-meta local-article-content-paragraph-links">
                <span data-lang="en">{", ".join(en_links)}</span>
                <span data-lang="zh">{"、".join(zh_links)}</span>
              </p>"""
```

- [ ] **Step 4: Add IDs to rendered paragraphs**

Update `_render_local_article_paragraphs(article)`:

- For plain English fallback, refactor the current list comprehension into an explicit loop and include `id="{anchor}"`.
- For bilingual paragraphs, include `id="{anchor}"`.
- Keep escaped text.
- Anchor numbering is based on original source paragraph index, not compacted rendered order.
- Preserve the existing `len(article.paragraphs_zh) != len(article.paragraphs)` guard and the per-paragraph zh-to-en fallback; only insert `id="{anchor}"` into each rendered non-blank paragraph's `<p>` opening tag.

Plain fallback shape:

```python
rendered = []
for index, paragraph in enumerate(article.paragraphs):
    if not paragraph.strip():
        continue
    anchor = _local_article_paragraph_anchor(index)
    rendered.append(f'      <p id="{_esc(anchor)}">{_esc(paragraph)}</p>')
return rendered
```

Bilingual shape:

```python
for index, (paragraph_en, paragraph_zh) in enumerate(
    zip(article.paragraphs, article.paragraphs_zh, strict=True)
):
    if not paragraph_en.strip():
        continue
    anchor = _local_article_paragraph_anchor(index)
```

- [ ] **Step 5: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch \
  tests/test_row_one_render.py::test_render_row_one_detail_skips_invalid_local_article_paragraph_links \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments
```

Expected: PASS.

## Task 4: Docs, Verification, Code Review, Commit, Push

- [ ] **Step 1: Update docs**

Add a README sentence near Daily Local Intelligence:

```markdown
Generated detail pages link content-section paragraph badges to anchored saved local paragraphs when the referenced paragraph is available.
```

Update `tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence`:

```python
assert "anchored saved local paragraphs" in readme
```

- [ ] **Step 2: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py tests/test_row_one_docs.py
```

Expected: PASS.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

Expected: all pass.

- [ ] **Step 4: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-303-code-review-prompt.md`, run Claude Code with max effort, and store the review in `docs/reviews/claude-code-stage-303-code-review.md`. The prompt must ask Claude Code to review changes since `212a70a` against this plan.

- [ ] **Step 5: Use opencode fallback only if Claude Code is unavailable**

If Claude Code is unavailable, run opencode with GLM 5.2 max and store `docs/reviews/opencode-stage-303-code-review.md`.

- [ ] **Step 6: Fix Critical and Important findings**

Apply fixes, rerun relevant tests and full verification, and request rereview if needed.

- [ ] **Step 7: Commit and push**

Run:

```bash
git status --short
git add README.md \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md \
  docs/reviews/claude-code-stage-303-plan-review-prompt.md \
  docs/reviews/claude-code-stage-303-plan-review.md \
  docs/reviews/claude-code-stage-303-plan-rereview-prompt.md \
  docs/reviews/claude-code-stage-303-plan-rereview.md \
  docs/reviews/opencode-stage-303-plan-review-prompt.md \
  docs/reviews/opencode-stage-303-plan-review.md \
  docs/reviews/opencode-stage-303-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-303-plan-rereview.md \
  docs/reviews/claude-code-stage-303-code-review-prompt.md \
  docs/reviews/claude-code-stage-303-code-review.md
git commit -m "Stage 303: add row one local article paragraph anchors"
git push origin main
```

Expected: push succeeds.

- [ ] **Step 8: Handoff Summary**

Write a short Handoff Summary with:

- Repo status
- Latest commit
- Verified commands
- Uncommitted files
- Next recommended stage
- Note that `local-article-content-paragraph-links` is functional detail-page markup and can receive dedicated visual polish in a later styling stage if needed.
