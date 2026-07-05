# Stage 297 ROW ONE Short Local Article Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve ROW ONE detail-page local article content when extraction fails or returns only a very short article, so the generated webpage publishes useful local content instead of a one-line summary.

**Architecture:** Keep local articles as generated-site sidecars under `data/articles/*.json`; do not add fields to `edition.json` or change app contract. Build local article paragraphs from extracted text first, then append existing ROW ONE story context (`editorial_takeaway`, `why_it_matters`, `signal_context`, `reader_path`) only when the cleaned article text is below a 240-character local-content threshold. Append context after already accepted source paragraphs so an unusable truncated source tail cannot block context, and continue respecting the source `row_one_article.max_chars` budget.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

After Stage 296, today's generated site has 18 detail pages and 18 local article sidecars. Nine sidecars still have only one short paragraph under 240 characters, some under 60 characters. Stage 297 improves the "article is local on the webpage" experience without pretending to have fetched more source text: short extracted/fallback bodies are supplemented by already-generated ROW ONE editorial context.

## File Structure

- Modify `src/fashion_radar/row_one/articles.py`
  - Add `_local_article_context_text(story)`.
  - Add `_story_local_article_paragraphs(story, text, max_chars)`.
  - Use the helper for both extracted text and fallback text.
  - Fall back to the stored story summary when non-empty extracted text cleans to zero local article paragraphs.
- Modify `tests/test_row_one_articles.py`
  - Update existing fallback expectations.
  - Add RED tests for short extraction enrichment, clean-empty extraction fallback, unusable source-tail enrichment, and long extraction non-enrichment.

## Task 1: Plan Review Gate

- [ ] Create `docs/reviews/claude-code-stage-297-plan-review-prompt.md` and `docs/reviews/opencode-stage-297-plan-review-prompt.md`.
- [ ] Attempt Claude Code plan review with `--effort max`; if unavailable, record `Verdict: UNAVAILABLE`.
- [ ] Run opencode fallback plan review with `zhipuai-coding-plan/glm-5.2 --variant max`.
- [ ] Fix Critical/Important findings before implementation.

## Task 2: RED Tests

- [ ] **Step 1: Update fallback expectation**

In `tests/test_row_one_articles.py`, update `test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure` so fallback paragraphs include the existing story editorial context:

```python
assert articles["the-row-signal-1234567890"].paragraphs == [
    "Summary",
    "Editorial",
    "Important",
    "Context",
    "Path",
]
```

- [ ] **Step 2: Preserve cleaned-summary fallback behavior**

In `test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary`, assert the first paragraph is still the cleaned source summary and the additional context paragraphs appear after it:

```python
assert articles["the-row-signal-1234567890"].paragraphs == [
    "The Row showroom note.",
    "Editorial",
    "Important",
    "Context",
    "Path",
]
assert edition.stories[0].summary.en == original_summary
```

- [ ] **Step 3: Add short extraction enrichment test**

Add:

```python
def test_build_row_one_local_articles_enriches_short_extracted_text() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Short extraction",
            text="Tiny source note.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    assert articles["the-row-signal-1234567890"].paragraphs == [
        "Tiny source note.",
        "Editorial",
        "Important",
        "Context",
        "Path",
    ]
```

- [ ] **Step 4: Add long extraction non-enrichment test**

Add:

```python
def test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text() -> None:
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Substantial extraction",
            text=(
                "First extracted paragraph carries enough context for the local article body. "
                "It is intentionally longer than a tiny feed summary and exceeds the context "
                "threshold used for fallback enrichment.\n\n"
                "Second extracted paragraph adds source detail without requiring local editorial "
                "fallback, keeping this article substantial without ROW ONE context."
            ),
            skipped=False,
        )

    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=extractor,
    )

    paragraphs = articles["the-row-signal-1234567890"].paragraphs

    assert sum(len(paragraph) for paragraph in paragraphs) >= 240
    assert any(paragraph.startswith("First extracted paragraph") for paragraph in paragraphs)
    assert any("Second extracted paragraph" in paragraph for paragraph in paragraphs)
    assert "Editorial" not in paragraphs
```

- [ ] **Step 5: Run RED tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_to_stored_summary_on_failure \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_cleans_fallback_without_mutating_story_summary \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_short_extracted_text \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_falls_back_when_extracted_text_cleans_empty \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_enriches_after_unusable_source_tail \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text \
  -q
```

Expected before implementation: the updated fallback, short extraction, clean-empty extraction, and unusable-tail tests fail; the long extraction behavior may pass once added if current logic already avoids context paragraphs.

## Task 3: GREEN Implementation

- [ ] **Step 1: Add local article context helpers**

In `src/fashion_radar/row_one/articles.py`, add:

```python
LOCAL_ARTICLE_MIN_CONTEXT_CHARS = 240


def _story_local_article_paragraphs(
    story: RowOneStory,
    text: str,
    *,
    max_chars: int,
) -> list[str]:
    paragraphs = text_to_local_article_paragraphs(text, max_chars=max_chars)
    if not paragraphs:
        return []
    total_chars = sum(len(paragraph) for paragraph in paragraphs)
    if total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS):
        return paragraphs
    context_text = _local_article_context_text(story)
    if not context_text:
        return paragraphs
    context_paragraphs = text_to_local_article_paragraphs(
        context_text,
        max_chars=max_chars - total_chars,
    )
    return [*paragraphs, *context_paragraphs]


def _local_article_context_text(story: RowOneStory) -> str:
    return "\n\n".join(
        text
        for text in (
            story.editorial_takeaway.en,
            story.why_it_matters.en,
            story.signal_context.en,
            story.reader_path.en,
        )
        if text.strip()
    )
```

- [ ] **Step 2: Use helper in extraction and fallback**

Replace both direct calls to `text_to_local_article_paragraphs(...)` inside `_build_story_local_article(...)` and `_fallback_story_summary_article(...)` with `_story_local_article_paragraphs(story, ..., max_chars=...)`.

- [ ] **Step 3: Preserve fallback for clean-empty extracted text**

When extracted text is present but cleans to zero paragraphs, return `_fallback_story_summary_article(...)` instead of publishing a context-only article with the extracted title.

- [ ] **Step 4: Run GREEN tests**

Run the same four tests from Task 2 Step 5 and expect them all to pass.

## Task 4: Verification And Generated Site Proof

- [ ] Run focused tests:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
```

- [ ] Run release gate:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv lock --check
```

- [ ] Rebuild today's site and compare local article paragraph counts. Expected: very short one-paragraph sidecars should receive additional ROW ONE context paragraphs, while already substantial extracted articles remain unchanged.

## Task 5: Code Review, Commit, Push

- [ ] Create code-review prompts for Claude Code and opencode.
- [ ] Attempt Claude Code with `--effort max`; record `Verdict: UNAVAILABLE` if it does not produce a completed body.
- [ ] Run opencode code review and fix Critical/Important findings.
- [ ] Commit and push:

```bash
git commit -m "Stage 297: enrich short row one local articles"
git push origin main
```

## Handoff Summary Template

```markdown
**Handoff Summary**
- Repo: `/home/ubuntu/fashion-radar`
- Branch/commit: `main` at `<sha>`, pushed to `origin/main`
- Verified commands: focused tests, full suite, ruff, release hygiene, uv lock, today site rebuild paragraph-count proof
- Uncommitted files: `<git status --short>`
- Generated site: `reports/row-one/site` rebuilt but ignored
- Next step: continue daily refresh/service or content presentation polish.
```
