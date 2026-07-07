# Stage 331 ROW ONE Local Article Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ROW ONE local article body provenance so generated saved article content distinguishes extracted article text from summary fallback and skipped/unusable extraction.

**Architecture:** Add a backward-compatible `body_source` field to `RowOneLocalArticle`, set it in the local article builder, then surface it through generated sidecars, metrics, readiness output, and detail-page provenance chips. Keep the change scoped to `data/articles/<story-id>.json` sidecars and generated HTML; do not change `data/edition.json`, ROW ONE app/runtime/manifest contracts, routes, anchors, scoring, source collection, or compliance-review behavior.

**Tech Stack:** Python 3.13, Pydantic models, existing ROW ONE static HTML renderer, Typer CLI, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Modify: `src/fashion_radar/row_one/models.py`
  - Add `RowOneLocalArticleBodySource` literal alias.
  - Add `body_source` field to `RowOneLocalArticle` with default `"extracted"`.
- Modify: `src/fashion_radar/row_one/articles.py`
  - Mark extracted sidecars as `body_source="extracted"`.
  - Pass fallback reasons into `_fallback_story_summary_article()`.
  - Mark fallback sidecars as `body_source="summary_fallback"`.
- Modify: `src/fashion_radar/row_one/site_metrics.py`
  - Add provenance counters and payload keys.
- Verify: `src/fashion_radar/row_one/article_readiness.py`
  - No source change is expected because its payload delegates local article
    metrics to `row_one_local_article_site_metrics_payload()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add local article provenance chips for body source and fallback reason.
- Modify: `src/fashion_radar/cli.py`
  - Print provenance counters in `row-one article-readiness`.
- Modify tests:
  - `tests/test_row_one_articles.py`
  - `tests/test_row_one_site_metrics.py`
  - `tests/test_row_one_article_readiness.py`
  - `tests/test_row_one_render.py`
  - `tests/test_row_one_docs.py`
  - `tests/test_cli_docs.py` only if docs sentinels need it.
- Modify docs:
  - `README.md`
  - `docs/row-one.md`
  - `docs/first-run.md` if readiness wording is affected.
- Create review artifacts under `docs/reviews/`.

## Task 1: Model And Builder Provenance

**Files:**
- Modify: `src/fashion_radar/row_one/models.py`
- Modify: `src/fashion_radar/row_one/articles.py`
- Modify: `tests/test_row_one_articles.py`

- [ ] **Step 1: Add failing model backward-compatibility test**

In `tests/test_row_one_articles.py`, add:

```python
def test_row_one_local_article_defaults_body_source_for_existing_sidecars() -> None:
    article = RowOneLocalArticle.model_validate(
        {
            "story_id": "the-row-signal-1234567890",
            "url": "https://example.com/the-row",
            "source_name": "Vogue Business",
            "extracted_at": AS_OF.isoformat(),
            "paragraphs": ["Saved paragraph."],
        }
    )

    assert article.body_source == "extracted"
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py::test_row_one_local_article_defaults_body_source_for_existing_sidecars -q
```

Expected: FAIL with `AttributeError` or validation/model field absence.

- [ ] **Step 2: Add model field**

In `src/fashion_radar/row_one/models.py`, update imports:

```python
from typing import Literal
```

Add near local article model definitions:

```python
RowOneLocalArticleBodySource = Literal["extracted", "summary_fallback", "skipped"]
```

Add to `RowOneLocalArticle`:

```python
    body_source: RowOneLocalArticleBodySource = "extracted"
```

- [ ] **Step 3: Verify backward-compatible model test passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py::test_row_one_local_article_defaults_body_source_for_existing_sidecars -q
```

Expected: PASS.

- [ ] **Step 4: Add failing builder tests for extracted and fallback reasons**

In `tests/test_row_one_articles.py`, add helper extractors:

```python
def _skipped_extractor(reason: str):
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(url=url, skipped=True, reason=reason)

    return extractor


def _raising_extractor():
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        raise RuntimeError("boom")

    return extractor
```

Add tests:

```python
def test_build_row_one_local_articles_marks_extracted_body_source() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_extractor("The Row opened a new showroom.\n\nBuyers cited demand."),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "extracted"
    assert article.reason is None
    assert article.skipped is False


def test_build_row_one_local_articles_marks_skipped_extraction_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_skipped_extractor("robots_disallowed"),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "robots_disallowed"
    assert article.skipped is False
    assert article.paragraphs


def test_build_row_one_local_articles_marks_exception_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_raising_extractor(),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "extraction_failed"
    assert article.skipped is False


def test_build_row_one_local_articles_marks_empty_text_as_summary_fallback() -> None:
    articles = build_row_one_local_articles(
        _edition(),
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=_extractor("   "),
    )

    article = articles["the-row-signal-1234567890"]

    assert article.body_source == "summary_fallback"
    assert article.reason == "no_extractable_text"
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q -k "body_source or summary_fallback"
```

Expected: FAIL until builder code sets provenance.

- [ ] **Step 5: Implement builder provenance**

In `src/fashion_radar/row_one/articles.py`, delete and replace the existing
combined branch:

```python
    if result.skipped or not result.text:
        return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
```

Replace it with separate reason-preserving branches:

```python
    try:
        result = extractor(...)
    except Exception:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="extraction_failed",
        )
    if result.skipped:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason=result.reason or "extraction_skipped",
        )
    if not result.text or not result.text.strip():
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="no_extractable_text",
        )
```

For unusable extracted paragraphs:

```python
    if not paragraphs:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="no_publishable_paragraphs",
        )
```

On the extracted `RowOneLocalArticle`, add:

```python
        body_source="extracted",
```

Change `_fallback_story_summary_article` signature:

```python
def _fallback_story_summary_article(
    story: RowOneStory,
    url: str,
    source: SourceDefinition,
    *,
    extracted_at,
    reason: str,
) -> RowOneLocalArticle | None:
```

On fallback `RowOneLocalArticle`, add:

```python
        body_source="summary_fallback",
        skipped=False,
        reason=reason,
```

- [ ] **Step 6: Run focused builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py
```

Expected: PASS.

## Task 2: Metrics And Article Readiness

**Files:**
- Modify: `src/fashion_radar/row_one/site_metrics.py`
- Verify: `src/fashion_radar/row_one/article_readiness.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_row_one_site_metrics.py`
- Modify: `tests/test_row_one_article_readiness.py`
- Modify: `tests/test_row_one_cli.py` if CLI text is pinned.

- [ ] **Step 1: Add failing metrics tests**

In `tests/test_row_one_site_metrics.py`, update zero payload expectation to include:

```python
        "extracted_article_count": 0,
        "summary_fallback_article_count": 0,
        "skipped_article_count": 0,
```

Add a test:

```python
def test_local_article_metrics_count_body_sources() -> None:
    articles = [
        RowOneLocalArticle(
            story_id="extracted-1234567890",
            url="https://example.com/extracted",
            source_name="Vogue Business",
            extracted_at=AS_OF,
            body_source="extracted",
            paragraphs=["Extracted paragraph."],
        ),
        RowOneLocalArticle(
            story_id="fallback-1234567890",
            url="https://example.com/fallback",
            source_name="Vogue Business",
            extracted_at=AS_OF,
            body_source="summary_fallback",
            reason="robots_disallowed",
            paragraphs=["Fallback paragraph."],
        ),
        RowOneLocalArticle(
            story_id="skipped-1234567890",
            url="https://example.com/skipped",
            source_name="PurseBlog",
            extracted_at=AS_OF,
            body_source="skipped",
            skipped=True,
            reason="no_publishable_paragraphs",
        ),
    ]

    metrics = build_row_one_local_article_metrics(articles)

    assert metrics.article_count == 3
    assert metrics.extracted_article_count == 1
    assert metrics.summary_fallback_article_count == 1
    assert metrics.skipped_article_count == 1
    assert row_one_local_article_site_metrics_payload(metrics) == {
        "article_count": 3,
        "paragraph_count": 2,
        "organized_section_count": 0,
        "source_count": 2,
        "extracted_article_count": 1,
        "summary_fallback_article_count": 1,
        "skipped_article_count": 1,
    }
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py -q
```

Expected: FAIL until metrics fields exist.

- [ ] **Step 2: Implement metrics fields and payload**

In `src/fashion_radar/row_one/site_metrics.py`, extend dataclass:

```python
    extracted_article_count: int = 0
    summary_fallback_article_count: int = 0
    skipped_article_count: int = 0
```

Inside `build_row_one_local_article_metrics()`:

```python
    extracted_article_count = 0
    summary_fallback_article_count = 0
    skipped_article_count = 0
```

In loop:

```python
        if article.body_source == "summary_fallback":
            summary_fallback_article_count += 1
        elif article.body_source == "skipped" or article.skipped:
            skipped_article_count += 1
        else:
            extracted_article_count += 1
```

Return the new fields and add them to `row_one_local_article_site_metrics_payload()`.

- [ ] **Step 3: Update article readiness payload test**

In `tests/test_row_one_article_readiness.py`, update expected `local_articles`
payloads to include the three new keys. Add non-zero values in
`test_article_readiness_counts_article_enabled_sources_and_story_coverage()`:

```python
        local_article_metrics=RowOneLocalArticleSiteMetrics(
            article_count=2,
            paragraph_count=4,
            organized_section_count=2,
            source_count=1,
            extracted_article_count=1,
            summary_fallback_article_count=1,
        ),
```

Assert JSON payload includes the new counts.

- [ ] **Step 4: Update CLI text output**

In `src/fashion_radar/cli.py`, after saved paragraph output in
`row_one_article_readiness()`, add:

```python
    typer.echo(f"Extracted local articles: {local_articles['extracted_article_count']}")
    typer.echo(
        "Summary fallback local articles: "
        f"{local_articles['summary_fallback_article_count']}"
    )
    typer.echo(f"Skipped local articles: {local_articles['skipped_article_count']}")
```

If `tests/test_row_one_cli.py` pins this command output, add expectations there.

- [ ] **Step 5: Run focused readiness tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_cli.py -q -k "article_readiness or local_article"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/site_metrics.py src/fashion_radar/cli.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_cli.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/site_metrics.py src/fashion_radar/cli.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_cli.py
```

Expected: PASS.

## Task 3: Detail Page Provenance UI

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render test**

In `tests/test_row_one_render.py`, add or update a local article detail render
test with a fallback article:

```python
def test_row_one_detail_local_article_renders_body_source_and_reason() -> None:
    article = RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="The Row signal",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        body_source="summary_fallback",
        reason="robots_disallowed",
        paragraphs=["Summary fallback paragraph."],
    )
    edition = _edition()
    story = edition.stories[0]

    html = render_detail_html(edition, story, local_article=article)

    assert "Text source" in html
    assert "正文来源" in html
    assert "ROW ONE summary fallback" in html
    assert "Fallback reason" in html
    assert "robots_disallowed" in html
```

Use the existing local helpers and render function names in `tests/test_row_one_render.py`; do not invent a second render path if helpers already exist.

Run the specific test. Expected: FAIL until template renders provenance.

- [ ] **Step 2: Implement provenance labels**

In `src/fashion_radar/row_one/templates.py`, add helper near
`_render_local_article_provenance()`:

```python
def _local_article_body_source_label(article: RowOneLocalArticle) -> str:
    if article.body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if article.body_source == "skipped" or article.skipped:
        return "Skipped"
    return "Extracted article text"
```

Inside `_render_local_article_provenance()`, after the saved time item, append:

```python
        _local_article_provenance_item(
            "Text source",
            "正文来源",
            _local_article_body_source_label(article),
        ),
```

If `article.reason` is nonblank, append:

```python
        _local_article_provenance_item(
            "Fallback reason",
            "兜底原因",
            article.reason,
        )
```

- [ ] **Step 3: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py
```

Expected: PASS.

## Task 4: Docs And Sentinels

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `docs/first-run.md` if needed
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add failing docs sentinel**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_local_article_body_provenance() -> None:
    docs = "\n".join(_normalized(_read(path)) for path in (README, ROW_ONE_DOC))

    for phrase in (
        "local article body provenance",
        "`body_source`",
        "`extracted`",
        "`summary_fallback`",
        "`skipped`",
        "row one summary fallback",
        "does not change `data/edition.json`",
        "does not change `row-one-runtime/v1`",
        "does not add compliance-review behavior",
    ):
        assert phrase in docs

    stale_claims = (
        "every saved local article is extracted source text",
        "all saved local article paragraphs are extracted article text",
    )
    for stale_claim in stale_claims:
        assert stale_claim not in docs
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q -k local_article_body_provenance
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Update docs**

Add a short Stage 331 paragraph to `README.md` and `docs/row-one.md`:

```markdown
Stage 331 adds local article body provenance for ROW ONE: generated
`data/articles/<story-id>.json` sidecars include `body_source` so detail pages
and article-readiness output can distinguish `extracted` article text,
`summary_fallback` content generated from the ROW ONE story summary/editorial
context, and `skipped` article bodies. Detail pages show a bilingual text-source
chip and fallback reason when present. This does not change `row-one-app/v7`,
does not change `data/edition.json`, does not change `row-one-manifest/v1`,
does not change `row-one-runtime/v1`, does not change detail routes or paragraph
anchors, does not add source collection, does not add scoring, does not add LLM
calls, and does not add compliance-review behavior.
```

- [ ] **Step 3: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check tests/test_row_one_docs.py
```

Expected: PASS.

## Task 5: Review, Verification, Commit

**Files:**
- Add: `docs/reviews/claude-code-stage-331-code-review-prompt.md`
- Add review/rereview outputs as needed.

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/site_metrics.py src/fashion_radar/row_one/templates.py src/fashion_radar/cli.py tests/test_row_one_articles.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/site_metrics.py src/fashion_radar/row_one/templates.py src/fashion_radar/cli.py tests/test_row_one_articles.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

- [ ] **Step 2: Claude Code review**

Create `docs/reviews/claude-code-stage-331-code-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-331-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-331-code-review.md
rm -f "$tmp_review"
```

Fix Critical/Important findings and rereview if needed.

- [ ] **Step 3: Full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
if git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'; then exit 1; else exit 0; fi
```

- [ ] **Step 4: Commit and push**

Run:

```bash
git add README.md docs/row-one.md docs/superpowers/specs/2026-07-07-stage-331-row-one-local-article-provenance-design.md docs/superpowers/plans/2026-07-07-stage-331-row-one-local-article-provenance-plan.md docs/reviews src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/site_metrics.py src/fashion_radar/row_one/templates.py src/fashion_radar/cli.py tests/test_row_one_articles.py tests/test_row_one_site_metrics.py tests/test_row_one_article_readiness.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_row_one_cli.py
git diff --cached --name-only
git commit -m "Stage 331: add row one local article provenance"
git push origin main
```
