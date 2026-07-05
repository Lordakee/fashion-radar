# Stage 299 ROW ONE Local Article Brief Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a compact structured ROW ONE brief to each local article sidecar and detail page, so a reader can scan what happened, why it matters, the signal context, and what to watch before reading the local body.

**Architecture:** Extend `RowOneLocalArticle` sidecars with optional `brief_sections` built entirely from existing `RowOneStory` localized fields. Render the brief inside the existing local article section, above the saved body paragraphs, using the existing language toggle. Keep `paragraphs` as the canonical saved article body and leave `row-one-app/v7`, `data/edition.json`, collection, scraping, translation, and social connectors unchanged.

The saved local article body should not duplicate the analysis-oriented scan-layer fields. Short extracted articles and fallback articles keep their source/summary body plus `editorial_takeaway`; `why_it_matters`, `signal_context`, and `reader_path` move out of the saved body and into `brief_sections`. `summary` is also exposed as `what_happened`, but it may match fallback/source body text when no fuller source article was available.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stages 297 and 298 made the local article body complete enough to read and aligned it with the English/Chinese toggle. The remaining content-layer gap is that the saved body is still mostly a sequence of paragraphs. Stage 299 adds a structured ROW ONE brief directly inside each local article sidecar and detail page:

- `what_happened`: story summary
- `why_it_matters`: story impact
- `signal_context`: ROW ONE signal background
- `watch_next`: reader path

This is content organization over existing ROW ONE fields. It is not a translation feature, new ranking layer, collection change, source enrichment, app-contract bump, compliance review feature, or page beautification pass.

## File Structure

- Modify `src/fashion_radar/row_one/models.py`
  - Add `RowOneLocalArticleBriefKey`.
  - Add `RowOneLocalArticleBriefSection`.
  - Add `brief_sections: list[RowOneLocalArticleBriefSection] = Field(default_factory=list)` to `RowOneLocalArticle`.
- Modify `src/fashion_radar/row_one/articles.py`
  - Add `_local_article_brief_sections(story)`.
  - Populate `brief_sections` in both extracted and fallback local article paths.
- Modify `src/fashion_radar/row_one/templates.py`
  - Add `_render_local_article_brief(article)`.
  - Render the brief between the local article title and body.
  - Add modest CSS for `.local-article-brief`.
- Modify `tests/test_row_one_articles.py`
  - Assert local article sidecars get four structured brief sections.
  - Assert summary-backed `what_happened` brief text strips raw feed HTML and
    does not mutate the source story summary.
- Modify `tests/test_row_one_render.py`
  - Assert brief sections render with bilingual spans.
  - Assert sidecar JSON includes `brief_sections`.
  - Assert brief section titles and bodies are escaped safely.
  - Assert local article rendering remains backward-compatible when `brief_sections` is empty.

## Task 1: Plan Review Gate

- [ ] Create `docs/reviews/claude-code-stage-299-plan-review-prompt.md` and `docs/reviews/opencode-stage-299-plan-review-prompt.md`.
- [ ] Attempt Claude Code plan review with `--effort max`; if unavailable, record `Verdict: UNAVAILABLE`.
- [ ] Run opencode fallback plan review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings before implementation.

## Task 2: RED Article Builder Tests

- [ ] **Step 1: Add expected brief-section assertion helper**

In `tests/test_row_one_articles.py`, add near the existing fixtures:

```python
def _assert_local_article_brief_sections(article, story) -> None:
    assert [section.key for section in article.brief_sections] == [
        "what_happened",
        "why_it_matters",
        "signal_context",
        "watch_next",
    ]
    assert [section.title.en for section in article.brief_sections] == [
        "What Happened",
        "Why It Matters",
        "Signal Context",
        "Watch Next",
    ]
    assert [section.title.zh for section in article.brief_sections] == [
        "发生了什么",
        "为什么重要",
        "信号背景",
        "接下来观察",
    ]
    assert [section.body.en for section in article.brief_sections] == [
        story.summary.en,
        story.why_it_matters.en,
        story.signal_context.en,
        story.reader_path.en,
    ]
    assert [section.body.zh for section in article.brief_sections] == [
        story.summary.zh,
        story.why_it_matters.zh,
        story.signal_context.zh,
        story.reader_path.zh,
    ]
```

- [ ] **Step 2: Assert fallback path populates brief sections**

In `test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure`,
assign the fixture to a variable before the build:

```python
edition = _edition()
```

pass `edition` to `build_row_one_local_articles(...)`, and after existing paragraph assertions add:

```python
_assert_local_article_brief_sections(article, edition.stories[0])
```

- [ ] **Step 3: Assert extracted path populates brief sections**

In `test_build_row_one_local_articles_enriches_short_extracted_text`, assign the fixture to a variable before the build:

```python
edition = _edition()
```

pass `edition` to `build_row_one_local_articles(...)`, and after existing paragraph assertions add:

```python
_assert_local_article_brief_sections(
    articles["the-row-signal-1234567890"],
    edition.stories[0],
)
```

- [ ] **Step 4: Run RED article tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_short_extracted_text \
  -q
```

Expected before implementation: tests fail because `RowOneLocalArticle` has no `brief_sections` field.

## Task 3: GREEN Article Builder Implementation

- [ ] **Step 1: Add brief models**

In `src/fashion_radar/row_one/models.py`, add the alias near the existing top-level `Literal` aliases:

```python
RowOneLocalArticleBriefKey = Literal[
    "what_happened",
    "why_it_matters",
    "signal_context",
    "watch_next",
]
```

Then add after `RowOneLink`:

```python
class RowOneLocalArticleBriefSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: RowOneLocalArticleBriefKey
    title: LocalizedText
    body: LocalizedText
```

Add to `RowOneLocalArticle`:

```python
brief_sections: list[RowOneLocalArticleBriefSection] = Field(default_factory=list)
```

- [ ] **Step 2: Import model type**

In `src/fashion_radar/row_one/articles.py`, import `RowOneLocalArticleBriefSection`.

- [ ] **Step 3: Add cleaned section builder**

In `src/fashion_radar/row_one/articles.py`, add:

```python
def _local_article_brief_text(text: str) -> str:
    protected = protect_literal_angle_tokens(text)
    cleaned = clean_row_one_text(protected)
    sentences = clean_row_one_sentences(cleaned, set())
    return restore_literal_angle_tokens(normalize_row_one_paragraph(" ".join(sentences)))


def _local_article_brief_sections(story: RowOneStory) -> list[RowOneLocalArticleBriefSection]:
    return [
        RowOneLocalArticleBriefSection(
            key="what_happened",
            title=LocalizedText(en="What Happened", zh="发生了什么"),
            body=LocalizedText(
                en=_local_article_brief_text(story.summary.en),
                zh=_local_article_brief_text(story.summary.zh),
            ),
        ),
        RowOneLocalArticleBriefSection(
            key="why_it_matters",
            title=LocalizedText(en="Why It Matters", zh="为什么重要"),
            body=story.why_it_matters,
        ),
        RowOneLocalArticleBriefSection(
            key="signal_context",
            title=LocalizedText(en="Signal Context", zh="信号背景"),
            body=story.signal_context,
        ),
        RowOneLocalArticleBriefSection(
            key="watch_next",
            title=LocalizedText(en="Watch Next", zh="接下来观察"),
            body=story.reader_path,
        ),
    ]
```

Also import `LocalizedText`, `protect_literal_angle_tokens`, and
`restore_literal_angle_tokens` if not already imported. The summary-backed
`what_happened` body is cleaned before saving because feed summaries can include
raw HTML image/link markup that would otherwise render as visible escaped tag
text in the brief.

- [ ] **Step 4: Populate extracted and fallback articles**

In both `RowOneLocalArticle(...)` constructors inside `src/fashion_radar/row_one/articles.py`, add:

```python
brief_sections=_local_article_brief_sections(story),
```

- [ ] **Step 5: Run GREEN article tests**

Run the command from Task 2 Step 4. Expected: both tests pass.

## Task 4: RED Render Tests

- [ ] **Step 1: Import brief-section model if needed**

In `tests/test_row_one_render.py`, make sure `RowOneLocalArticleBriefSection` is imported from `fashion_radar.row_one.models` if explicit construction needs it.

- [ ] **Step 2: Add brief sections to local article fixture**

In `test_render_row_one_detail_includes_local_article_content`, add to the `RowOneLocalArticle(...)` fixture:

```python
brief_sections=[
    RowOneLocalArticleBriefSection(
        key="what_happened",
        title=LocalizedText(en="What Happened", zh="发生了什么"),
        body=LocalizedText(en="The Row demand moved this week.", zh="The Row 需求本周升温。"),
    ),
    RowOneLocalArticleBriefSection(
        key="why_it_matters",
        title=LocalizedText(en="Why It Matters", zh="为什么重要"),
        body=LocalizedText(en="It changes how buyers read quiet luxury.", zh="这会改变买手理解静奢的方式。"),
    ),
]
```

- [ ] **Step 3: Assert brief renders and serializes**

In the same test, add:

```python
assert 'class="local-article-brief"' in detail_html
assert '<span data-lang="en">What Happened</span>' in detail_html
assert '<span data-lang="zh">发生了什么</span>' in detail_html
assert '<span data-lang="en">The Row demand moved this week.</span>' in detail_html
assert '<span data-lang="zh">The Row 需求本周升温。</span>' in detail_html
assert [section["key"] for section in article_json["brief_sections"]] == [
    "what_happened",
    "why_it_matters",
]
```

- [ ] **Step 4: Add brief escaping coverage**

In `test_render_row_one_detail_escapes_local_article_content`, add a malicious brief section to the `RowOneLocalArticle(...)` fixture:

```python
brief_sections=[
    RowOneLocalArticleBriefSection(
        key="what_happened",
        title=LocalizedText(en="<script>Brief</script>", zh="简报<script>"),
        body=LocalizedText(
            en='<img src=x onerror="alert(2)"> & brief',
            zh='<img src=x onerror="alert(3)"> 中文 & brief',
        ),
    )
],
```

and assert:

```python
assert "&lt;script&gt;Brief&lt;/script&gt;" in detail_html
assert "&lt;img src=x onerror=&quot;alert(2)&quot;&gt; &amp; brief" in detail_html
assert "&lt;img src=x onerror=&quot;alert(3)&quot;&gt; 中文 &amp; brief" in detail_html
assert "<script>Brief</script>" not in detail_html
assert 'onerror="alert' not in detail_html
```

- [ ] **Step 5: Assert empty brief remains backward-compatible**

In `test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs`, add:

```python
assert 'class="local-article-brief"' not in detail_html
```

- [ ] **Step 6: Run RED render tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  -q
```

Expected before implementation: the first test fails because `_render_local_article(...)` does not render `brief_sections`.

## Task 5: GREEN Render Implementation

- [ ] **Step 1: Render local article brief**

In `src/fashion_radar/row_one/templates.py`, inside `_render_local_article(...)`, add:

```python
brief = _render_local_article_brief(article)
```

and include `{brief}` between `<h3>{_esc(title)}</h3>` and `<div class="local-article-body">`.

- [ ] **Step 2: Add brief renderer**

Add below `_render_local_article(...)`:

```python
def _render_local_article_brief(article: RowOneLocalArticle) -> str:
    cards = []
    for section in article.brief_sections:
        cards.append(
            f"""        <article class="local-article-brief-card">
          <h4>
            <span data-lang="en">{_esc(section.title.en)}</span>
            <span data-lang="zh">{_esc(section.title.zh)}</span>
          </h4>
          <p>
            <span data-lang="en">{_esc(section.body.en)}</span>
            <span data-lang="zh">{_esc(section.body.zh)}</span>
          </p>
        </article>"""
        )
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return f"""      <div class="local-article-brief" aria-label="ROW ONE brief">
{rendered_cards}
      </div>"""
```

- [ ] **Step 3: Add brief CSS**

In `row_one_css()` near the `.local-article` styles, add:

```css
.local-article-brief {
  border: 1px solid var(--line);
  display: grid;
  gap: 0;
  margin: 0 0 22px;
}
.local-article-brief-card {
  border-bottom: 1px solid var(--line);
  padding: 16px 18px;
}
.local-article-brief-card:last-child { border-bottom: 0; }
.local-article-brief-card h4 {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.local-article-brief-card p {
  color: var(--ink);
  line-height: 1.55;
  margin: 0;
}
```

- [ ] **Step 4: Run GREEN render tests**

Run the command from Task 4 Step 6. Expected: selected tests pass.

## Task 6: Verification And Site Proof

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
```

- [ ] Run release gate:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] Rebuild today's site:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
```

- [ ] Run proof script verifying:
  - `story_count == 18`
  - `data/articles/*.json == 18`
  - every sidecar has four `brief_sections`
  - every sidecar has `what_happened`, `why_it_matters`, `signal_context`, `watch_next`
  - every detail page with `id="local-article"` includes `class="local-article-brief"`

## Task 7: Code Review, Commit, Push

- [ ] Create `docs/reviews/claude-code-stage-299-code-review-prompt.md` and `docs/reviews/opencode-stage-299-code-review-prompt.md`.
- [ ] Attempt Claude Code with `--effort max`; record `Verdict: UNAVAILABLE` if it does not produce a completed body.
- [ ] Run opencode code review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings.
- [ ] Commit and push:

```bash
git add src/fashion_radar/row_one/models.py \
  src/fashion_radar/row_one/articles.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_articles.py \
  tests/test_row_one_render.py \
  docs/superpowers/plans/2026-07-05-stage-299-row-one-local-article-brief-sections-plan.md \
  docs/reviews/claude-code-stage-299-*.md \
  docs/reviews/opencode-stage-299-*.md
git diff --cached --check
git commit -m "Stage 299: add row one local article brief sections"
git push origin main
```

## Handoff Summary Template

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: focused article/render tests, full suite, ruff, release hygiene, uv lock, today site rebuild brief-section proof
- Uncommitted files: `<git status --short>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: continue local content depth or move to presentation polish.
```
