# Stage 325 ROW ONE Paragraph Evidence Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Stage 324 paragraph evidence index polish items by removing empty reference wrappers, adding a Chinese body fallback, and explicitly testing the map link to the evidence block.

**Architecture:** Keep the work entirely inside generated ROW ONE detail-page rendering. Add focused tests in `tests/test_row_one_render.py`, then update `_render_local_article_paragraph_evidence_support()` in `templates.py` to render optional references and fallback body text without changing data models or JSON contracts. Documentation changes are limited to Stage 325 spec/plan/review artifacts because this is a polish node for existing Stage 324 behavior.

**Tech Stack:** Python, existing ROW ONE Pydantic models, existing string-rendered HTML/CSS in `templates.py`, pytest, Ruff, Claude Code review gates.

---

## Files

- Modify: `src/fashion_radar/row_one/templates.py`
  - Update `_render_local_article_paragraph_evidence_support()` to omit an empty refs wrapper.
  - Add English fallback for blank or whitespace-only `item.item_body.zh`.
- Modify: `tests/test_row_one_render.py`
  - Add explicit map-link assertion to `test_render_row_one_detail_includes_local_article_paragraph_evidence_index`.
  - Add focused no-empty-ref-wrapper test.
  - Add focused zh-body-fallback test.
- Create: `docs/reviews/claude-code-stage-325-plan-review-prompt.md`
- Create after plan review: `docs/reviews/claude-code-stage-325-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-325-code-review-prompt.md`
- Create after implementation: `docs/reviews/claude-code-stage-325-code-review.md`

## Task 1: Add Failing Render Tests

- [ ] **Step 1: Strengthen the map-link render test**

In `tests/test_row_one_render.py`, update `test_render_row_one_detail_includes_local_article_paragraph_evidence_index()` after the existing map/evidence ordering assertion:

```python
    map_html = detail_html[
        detail_html.index('class="local-article-map"') : detail_html.index(
            'id="local-article-paragraph-evidence"'
        )
    ]
    assert 'href="#local-article-paragraph-evidence"' in map_html
```

Expected: this already passes, but it makes the Stage 324 map-link contract explicit.

- [ ] **Step 2: Add a no-empty-reference-wrapper test**

Add near the Stage 324 paragraph evidence render tests:

```python
def test_render_row_one_detail_paragraph_evidence_omits_empty_reference_wrapper() -> None:
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
                            body=LocalizedText(en="Support without refs", zh="无引用支持"),
                            references=[],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert 'class="local-article-paragraph-evidence-support"' in evidence_html
    assert "<div></div>" not in evidence_html
    assert 'class="local-article-paragraph-evidence-ref"' not in evidence_html
```

Expected RED: fails because current renderer emits `<div></div>` when references are empty.

- [ ] **Step 3: Add a Chinese body fallback test**

Add near the Stage 324 paragraph evidence render tests:

```python
def test_render_row_one_detail_paragraph_evidence_body_zh_falls_back_to_english() -> None:
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
                            body=LocalizedText(en="English <fallback> body.", zh="   "),
                            references=[],
                            paragraph_indices=[0],
                        )
                    ],
                )
            ]
        },
    )

    detail_html = render_detail_html(edition, story, local_article=local_article)
    evidence_html = detail_html[
        detail_html.index('id="local-article-paragraph-evidence"') : detail_html.index(
            'id="local-article-digest"'
        )
    ]

    assert '<span data-lang="en">English &lt;fallback&gt; body.</span>' in evidence_html
    assert '<span data-lang="zh">English &lt;fallback&gt; body.</span>' in evidence_html
    assert '<span data-lang="zh"></span>' not in evidence_html
    assert "English <fallback> body." not in evidence_html
```

Expected RED: fails because current renderer emits an empty Chinese body span for whitespace-only Chinese body text and does not use the English fallback.

- [ ] **Step 4: Run focused render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  -k "paragraph_evidence" -q
```

Expected: the no-empty-wrapper and zh-fallback tests fail for the current implementation.

## Task 2: Implement Minimal Renderer Polish

- [ ] **Step 1: Add a body fallback helper**

In `src/fashion_radar/row_one/templates.py`, add below `_local_article_paragraph_evidence_body()`:

```python
def _local_article_paragraph_evidence_body_text(body: LocalizedText) -> LocalizedText:
    en = _local_article_paragraph_evidence_body(body.en)
    zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
    return LocalizedText(en=en, zh=zh)
```

- [ ] **Step 2: Update `_render_local_article_paragraph_evidence_support()`**

Replace the body/reference rendering section with:

```python
    body = ""
    if item.item_body is not None:
        body_text = _local_article_paragraph_evidence_body_text(item.item_body)
        body = (
            "                <p>"
            f'<span data-lang="en">{_esc(body_text.en)}</span>'
            f'<span data-lang="zh">{_esc(body_text.zh)}</span>'
            "</p>\n"
        )
    refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
    refs_html = f"                <div>{refs}</div>\n" if refs else ""
```

Then render `{refs_html}` instead of `                <div>{refs}</div>`.

The return block should end as:

```python
    return f"""              <div class="local-article-paragraph-evidence-support">
                <a href="{_esc(section_href)}">
                  <span data-lang="en">{_esc(item.section_title.en)}</span>
                  <span data-lang="zh">{_esc(item.section_title.zh)}</span>
                </a>
                <strong>
                  <span data-lang="en">{_esc(item.item_label.en)}</span>
                  <span data-lang="zh">{_esc(item.item_label.zh)}</span>
                </strong>
{body}{refs_html}              </div>"""
```

- [ ] **Step 3: Run focused render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  -k "paragraph_evidence" -q
```

Expected: all selected paragraph evidence tests pass.

## Task 3: Verification, Code Review, Commit, Push

- [ ] **Step 1: Run focused and full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "paragraph_evidence" -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k "row_one" -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Request Claude Code code review**

Create:

- `docs/reviews/claude-code-stage-325-code-review-prompt.md`
- `docs/reviews/claude-code-stage-325-code-review.md`

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-325-code-review-prompt.md)" > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-325-code-review.md
rm -f "$tmp_review"
```

Expected: no unresolved Critical or Important findings. If Claude Code is unavailable, use opencode fallback per `AGENTS.md` and record completed fallback review artifacts only.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-07-07-stage-325-row-one-paragraph-evidence-polish-design.md docs/superpowers/plans/2026-07-07-stage-325-row-one-paragraph-evidence-polish-plan.md docs/reviews/claude-code-stage-325-plan-review-prompt.md docs/reviews/claude-code-stage-325-plan-review.md docs/reviews/claude-code-stage-325-code-review-prompt.md docs/reviews/claude-code-stage-325-code-review.md src/fashion_radar/row_one/templates.py tests/test_row_one_render.py
git commit -m "Stage 325: polish row one paragraph evidence"
git push origin main
```

Expected: push succeeds and `git status --short --branch` reports `## main...origin/main`.
