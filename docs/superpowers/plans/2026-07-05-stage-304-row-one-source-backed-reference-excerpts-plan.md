# Stage 304 ROW ONE Source-Backed Reference Excerpts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE local article entity, designer, and product cards show the matched saved-source paragraph excerpt instead of only a `type / label` metadata string, so detail pages publish organized local content rather than acting like link directories.

**Architecture:** Preserve the current `RowOneLocalArticle` schema and reuse `RowOneLocalArticleContentItem.body`; no app contract change and no new generated artifact is needed. The article builder already finds `paragraph_indices` for each reference, so this stage adds a deterministic helper that uses the first saved paragraph matched by the reference name as the item body and keeps the existing `type / label` fallback when no name-matched paragraph exists. Paragraph badges may still use the broader existing name+label match, but excerpt bodies must be name-matched to avoid misleading generic labels such as `bag`, `new`, or `tracked`. Existing templates and Daily Local Intelligence segment projection already render item bodies, so the visible website changes come from richer local article data.

**Tech Stack:** Python 3.11, Pydantic models already in `src/fashion_radar/row_one/models.py`, deterministic ROW ONE article builder in `src/fashion_radar/row_one/articles.py`, static HTML renderer in `src/fashion_radar/row_one/templates.py`, pytest, ruff, uv.

---

## Product Gap Closed

The user asked for ROW ONE to organize and publish article content locally, with links and visual polish as lower priority. Stages 297-303 already save local article paragraphs, render detail pages, add content sections, project compact homepage intelligence, and link detail-page content badges to local paragraphs. Stage 304 closes the next report-layer gap: entity/designer/product cards still read like metadata (`brand / tracked`, `product / bag`) even when ROW ONE has the matching saved paragraph locally. This stage makes those cards show the actual saved-source excerpt that mentions the brand, person, designer, product, shoe, or bag.

## Scope Boundaries

In scope:

- Use existing saved `RowOneLocalArticle.paragraphs` and `paragraphs_zh`.
- Use existing `paragraph_indices` matching from `_local_article_paragraph_indices` for paragraph badges.
- Populate `RowOneLocalArticleContentItem.body` for reference items with the first reference-name-matched saved paragraph excerpt.
- Keep `type / label` as the fallback body when no paragraph match exists.
- Keep paragraph badges and anchors from Stage 303 unchanged.
- Keep homepage Daily Local Intelligence behavior as a downstream projection of local article content sections.
- Update README/docs to say reference cards can include source-backed excerpts.

Out of scope:

- No new scraping, browser automation, social connectors, source acquisition, scheduler, monitoring, demand proof, platform coverage verification, image generation, app UI, schema migration, dependency change, or compliance-review product feature.
- No `row-one-app/v7` or `data/edition.json` contract change.
- No new model classes unless the code review proves the existing `body` field cannot represent this safely.
- No generated sample data changes under `data/`, `reports/`, or generated site output.

## File Map

- Modify `src/fashion_radar/row_one/articles.py`
- Add a small helper that maps a matched paragraph index to localized excerpt body text.
  - Excerpt body matching must use `ref.name` only; paragraph badge matching can remain `ref.name` plus `ref.label`.
  - Change `_local_article_reference_section` to receive `paragraphs_zh`.
  - Keep matching and de-duplication behavior unchanged.
- Modify `tests/test_row_one_articles.py`
  - Extend existing content-section tests so entity/designer/product bodies become saved-source excerpts when matched.
  - Prove unmatched refs still fall back to `type / label`.
  - Prove JSON dumps include excerpt body in content sections.
- Modify `tests/test_row_one_render.py`
  - Ensure a detail page renders a source-backed reference excerpt from local article content item body and writes it to `data/articles/<story-id>.json`.
  - Keep Stage 303 paragraph link expectations intact.
- Modify `tests/test_row_one_docs.py`
  - Add a README/doc drift assertion for source-backed reference excerpts.
- Modify `README.md` and `docs/row-one.md`
  - Document that local article reference cards can show saved-source paragraph excerpts with paragraph badges.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-304-plan-review-prompt.md`
  - `claude-code-stage-304-plan-review.md`
  - `opencode-stage-304-plan-review-prompt.md`
  - `opencode-stage-304-plan-review.md`
  - Later code review artifacts after implementation.

## Implementation Method

Use TDD:

1. Add generator assertions that fail because reference item bodies are currently `type / label`.
2. Implement the minimal generator helper.
3. Add render/docs assertions.
4. Run focused tests, full verification, Claude Code code review, fix Critical/Important findings, commit, push.

## Task 1: Generator Reference Excerpts

**Files:**
- Modify: `tests/test_row_one_articles.py`
- Modify: `src/fashion_radar/row_one/articles.py`

- [ ] **Step 1: Extend the generator test with failing excerpt assertions**

In `tests/test_row_one_articles.py`, update `test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs` after the existing `paragraph_indices` assertions:

```python
    assert the_row.body is not None
    assert the_row.body.en == "First source paragraph frames The Row demand."
    assert the_row.body.zh == "First source paragraph frames The Row demand."
    assert zendaya.body is not None
    assert zendaya.body.en == (
        "Second source paragraph shows Zendaya styling context around Margaux."
    )
    assert olsen.body is not None
    assert olsen.body.en == (
        "Third source paragraph mentions Mary-Kate Olsen and a product signal."
    )

    assert margaux.body is not None
    assert margaux.body.en == (
        "Second source paragraph shows Zendaya styling context around Margaux."
    )
```

The zh value falls back to English in this fixture because extracted text has no separate zh paragraph source.

- [ ] **Step 2: Add fallback assertions**

In `test_build_row_one_local_articles_content_sections_work_on_fallback`, keep the current reference assertion and add:

```python
    unmatched = _content_item(_content_section(article, "entities"), "The Row")
    assert unmatched.body is not None
    assert unmatched.body.en == "brand / tracked"
    assert unmatched.body.zh == "brand / tracked"
```

This proves unmatched references still show deterministic metadata instead of blank bodies.

- [ ] **Step 3: Add generic-label guard test**

Add this test near the other local article content-section tests:

```python
def test_build_row_one_local_articles_reference_excerpt_requires_name_match() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.product_refs = [RowOneReference(name="Margaux", type="product", label="bag")]

    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Generic product source",
            text="The bag signal is accelerating, but this paragraph names no specific product.",
            skipped=False,
        )

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=240)],
        now=AS_OF,
        extractor=extractor,
    )

    product_section = _content_section(
        articles["the-row-signal-1234567890"],
        "product_signals",
    )
    margaux = _content_item(product_section, "Margaux")
    assert margaux.paragraph_indices == [0]
    assert margaux.body is not None
    assert margaux.body.en == "product / bag"
    assert margaux.body.zh == "product / bag"
```

This keeps Stage 303 paragraph badge behavior but blocks a misleading excerpt when only the generic label matched.

- [ ] **Step 4: Add JSON body assertion**

In `test_build_row_one_local_articles_content_sections_model_dump_json`, after the `references` assertion add:

```python
    assert product_section["items"][0]["body"] == {
        "en": "The Margaux bag is the product signal to watch.",
        "zh": "The Margaux bag is the product signal to watch.",
    }
```

- [ ] **Step 5: Run the focused failing tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_work_on_fallback \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_reference_excerpt_requires_name_match \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_model_dump_json -q
```

Expected before implementation: at least the matched-body assertions fail because current reference item body values are `brand / tracked`, `celebrity / new`, `designer / founder`, or `product / bag`.

- [ ] **Step 6: Implement localized excerpt body helpers**

In `src/fashion_radar/row_one/articles.py`, add this constant and helpers near `_local_article_paragraph_indices`:

```python
LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS = 280


def _local_article_reference_excerpt(
    paragraphs: list[str],
    paragraph_indices: list[int],
    *,
    max_chars: int = LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS,
) -> tuple[int, str] | None:
    for index in paragraph_indices:
        if index < 0 or index >= len(paragraphs):
            continue
        excerpt = normalize_row_one_paragraph(paragraphs[index])
        if not excerpt:
            continue
        if len(excerpt) > max_chars:
            excerpt = _truncate_at_word_boundary(excerpt, max_chars)
        return index, excerpt
    return None


def _local_article_reference_body(
    ref: RowOneReference,
    paragraphs: list[str],
    paragraphs_zh: list[str],
    excerpt_indices: list[int],
) -> tuple[str, str]:
    fallback = f"{ref.type} / {ref.label}"
    excerpt = _local_article_reference_excerpt(paragraphs, excerpt_indices)
    if excerpt is None:
        return fallback, fallback
    index, body_en = excerpt
    aligned_zh = _align_local_article_language_paragraphs(paragraphs, paragraphs_zh)
    body_zh = normalize_row_one_paragraph(aligned_zh[index]) if index < len(aligned_zh) else ""
    if len(body_zh) > LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS:
        body_zh = _truncate_at_word_boundary(
            body_zh,
            LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS,
        )
    return body_en, body_zh or body_en
```

This uses only saved local article paragraphs and keeps the existing metadata fallback.

- [ ] **Step 7: Use the helper in reference content sections**

Change `_local_article_reference_section` signature from:

```python
def _local_article_reference_section(
    *,
    key: RowOneLocalArticleContentKey,
    title: LocalizedText,
    refs: list[RowOneReference],
    paragraphs: list[str],
) -> RowOneLocalArticleContentSection | None:
```

to:

```python
def _local_article_reference_section(
    *,
    key: RowOneLocalArticleContentKey,
    title: LocalizedText,
    refs: list[RowOneReference],
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> RowOneLocalArticleContentSection | None:
```

Inside the `for ref in refs` loop, replace:

```python
        body = f"{ref.type} / {ref.label}"
        items.append(
            _localized_content_item(
                label_en=ref.name,
                body_en=body,
                body_zh=body,
                references=[ref],
                paragraph_indices=_local_article_paragraph_indices(
                    paragraphs,
                    [ref.name, ref.label],
                ),
            )
        )
```

with:

```python
        paragraph_indices = _local_article_paragraph_indices(
            paragraphs,
            [ref.name, ref.label],
        )
        excerpt_indices = _local_article_paragraph_indices(
            paragraphs,
            [ref.name],
            limit=1,
        )
        body_en, body_zh = _local_article_reference_body(
            ref,
            paragraphs,
            paragraphs_zh,
            excerpt_indices,
        )
        items.append(
            _localized_content_item(
                label_en=ref.name,
                body_en=body_en,
                body_zh=body_zh,
                references=[ref],
                paragraph_indices=paragraph_indices,
            )
        )
```

Update the two `_local_article_reference_section` calls in `_local_article_content_sections` to pass `paragraphs_zh=paragraphs_zh`.

- [ ] **Step 8: Run focused generator tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q
```

Expected after implementation: all `tests/test_row_one_articles.py` tests pass.

## Task 2: Detail Page Rendering Evidence

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Update local article fixture body to source excerpt**

In `test_render_row_one_detail_includes_local_article_content`, change the `entities` content item body from:

```python
body=LocalizedText(en="brand / tracked", zh="brand / tracked"),
```

to:

```python
body=LocalizedText(
    en="First local paragraph about The Row demand.",
    zh="第一段本地正文，关于 The Row 需求。",
),
```

- [ ] **Step 2: Add rendered excerpt and JSON assertions**

In the same test, after the `Refs: The Row` assertions add:

```python
    assert '<span data-lang="en">First local paragraph about The Row demand.</span>' in detail_html
    assert '<span data-lang="zh">第一段本地正文，关于 The Row 需求。</span>' in detail_html
```

After the `article_json["paragraphs_zh"]` assertion block, add:

```python
    entity_section = next(
        section for section in article_json["content_sections"] if section["key"] == "entities"
    )
    assert entity_section["items"][0]["body"] == {
        "en": "First local paragraph about The Row demand.",
        "zh": "第一段本地正文，关于 The Row 需求。",
    }
```

- [ ] **Step 3: Run focused render test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content -q
```

Expected: pass after Task 1 and this test update.

## Task 3: Documentation Drift Guard

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs test assertion**

In `tests/test_row_one_docs.py`, update the ROW ONE docs test that already checks Daily Local Intelligence/local article wording by adding assertions for these phrases:

```python
    assert "reference cards can include saved-source paragraph excerpts" in readme
    assert "source-backed reference excerpts" in row_one_docs
```

Use the existing docs-test helpers. If the test only reads `readme`, add:

```python
    row_one_docs = _normalized(_read(ROW_ONE_DOC))
```

- [ ] **Step 2: Run docs test to verify it fails**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected before docs update: fail on the new phrase assertion.

- [ ] **Step 3: Update README wording**

In `README.md`, near the existing Daily Local Intelligence paragraph, add one sentence:

```markdown
Detail-page reference cards can include saved-source paragraph excerpts for matched brands, designers, people, bags, shoes, and products while keeping paragraph badges linked to the local article body.
```

- [ ] **Step 4: Update docs/row-one.md wording**

In `docs/row-one.md`, near the local article section, add one sentence:

```markdown
Content sections use source-backed reference excerpts when a matched entity, designer, person, bag, shoe, or product appears in a saved local paragraph; otherwise they retain the deterministic reference metadata fallback.
```

- [ ] **Step 5: Run docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected: pass.

## Task 4: Review, Verification, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-304-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-304-code-review.md`
- Possibly add rereview artifacts if Critical or Important findings are fixed.

- [ ] **Step 1: Run focused stage checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py -q
```

Expected: all selected tests pass.

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

Create `docs/reviews/claude-code-stage-304-code-review-prompt.md` with:

```markdown
# Claude Code Stage 304 Code Review Prompt

You are reviewing Stage 304 code changes for `/home/ubuntu/fashion-radar`.

Base commit: `<base-sha>`
Plan: `docs/superpowers/plans/2026-07-05-stage-304-row-one-source-backed-reference-excerpts-plan.md`
Plan reviews:
- `docs/reviews/claude-code-stage-304-plan-review.md`
- `docs/reviews/opencode-stage-304-plan-review.md`

Changed files to review:
- `src/fashion_radar/row_one/articles.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 304 plan/review artifacts

Review objective:
- Confirm matched entity/designer/product reference cards use saved local article paragraph excerpts as `RowOneLocalArticleContentItem.body`.
- Confirm unmatched references retain deterministic `type / label` fallback body text.
- Confirm paragraph index matching, Stage 303 detail-page paragraph anchors, and homepage Daily Local Intelligence behavior remain safe.
- Confirm no app contract, dependency, source acquisition, scraping, social connector, scheduler, image, or compliance-review product behavior was added.
- Confirm tests would fail for metadata-only body regressions and unsafe escaping regressions.
- Confirm review artifacts are clean.

Verification already run after latest changes:
- `<commands and results>`

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
```

- [ ] **Step 4: Run Claude Code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-304-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-304-code-review.md
rm -f "$tmp_review"
```

Fix Critical and Important findings before continuing. If fixes are needed, rerun relevant tests, full verification, and save a rereview artifact.

- [ ] **Step 5: Commit only Stage 304 files**

Run:

```bash
git status --short --branch
git add \
  README.md \
  docs/row-one.md \
  src/fashion_radar/row_one/articles.py \
  tests/test_row_one_articles.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  docs/superpowers/plans/2026-07-05-stage-304-row-one-source-backed-reference-excerpts-plan.md \
  docs/reviews/claude-code-stage-304-plan-review-prompt.md \
  docs/reviews/claude-code-stage-304-plan-review.md \
  docs/reviews/opencode-stage-304-plan-review-prompt.md \
  docs/reviews/opencode-stage-304-plan-review.md \
  docs/reviews/claude-code-stage-304-code-review-prompt.md \
  docs/reviews/claude-code-stage-304-code-review.md
git diff --cached --check
git commit -m "Stage 304: add row one source-backed reference excerpts"
git push origin main
```

Do not commit `uv.lock` unless a real public lockfile change is intentionally introduced; this stage should not need one.

## Self-Review

- Spec coverage: The plan directly targets the user's local content organization request by replacing metadata-only reference bodies with saved paragraph excerpts while preserving anchors and local JSON output.
- Placeholder scan: No TBD/TODO/implement-later placeholders remain.
- Type consistency: The plan uses existing `RowOneLocalArticleContentItem.body: LocalizedText | None` and existing `paragraph_indices: list[int]`, avoiding new schema unless a reviewer blocks the approach.
- Risk control: The change is generator-local and verified through builder tests, render tests, docs tests, full pytest, ruff, release hygiene, lock check, and Claude Code review. The plan also separates broad badge matching from name-only excerpt matching so generic labels cannot create misleading excerpt bodies.
