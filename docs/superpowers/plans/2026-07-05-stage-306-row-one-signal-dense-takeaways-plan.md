# Stage 306 ROW ONE Signal-Dense Local Article Takeaways Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE local article `takeaways` prefer saved paragraphs with explicit brand, designer, person, bag, shoe, or product signals instead of always defaulting to the first three paragraphs.

**Architecture:** Keep this as a deterministic content-organization change inside the local article builder. Score saved article paragraphs against the story's existing explicit references and select the strongest matching paragraphs for the existing `takeaways` content section, preserving original paragraph indices and falling back to the current first-three behavior when no signal paragraph is detected. Do not change models, JSON schema, app payloads, source acquisition, render structure, scheduling, dependencies, or social connectors.

**Tech Stack:** Python 3.11, `src/fashion_radar/row_one/articles.py`, existing `RowOneLocalArticleContentSection` models, pytest, ruff, uv.

---

## Product Gap Closed

The user wants ROW ONE to organize locally saved fashion information, not simply expose links. Stages 297-305 made local article bodies visible, structured, linked, and easier to navigate. The remaining content-quality gap is that `takeaways` still mostly mirror the first three saved paragraphs. In many fashion articles, the opening paragraphs are generic context while the meaningful brand/product/designer signal appears later. Since Daily Local Intelligence uses the first takeaway as the strongest-read body, improving takeaway selection improves both detail pages and homepage local intelligence without adding fields or changing render contracts.

## Scope Boundaries

In scope:

- Score each non-empty saved local article paragraph against story explicit references:
  - `story.entity_refs`
  - `story.designer_refs`
  - `story.product_refs`
- Prefer paragraphs with explicit reference-name matches.
- Preserve original zero-based paragraph positions in `paragraph_indices`.
- Keep at most three takeaway items.
- Preserve the current first-three non-empty paragraph fallback when no paragraph has a reference-name match.
- Preserve existing bilingual alignment and fallback behavior.
- Add tests proving signal-rich later paragraphs become takeaways and Daily Local Intelligence uses the improved first takeaway.
- Document that ROW ONE takeaways prefer source-backed signal paragraphs.

Out of scope:

- No schema changes.
- No `RowOneLocalArticle` model changes.
- No `data/edition.json` or `row-one-app/v7` changes.
- No template, CSS, visual redesign, source acquisition, scraping, scheduler, social connector, image generation, dependency, or compliance-review product changes.
- No AI summarization or external enrichment.
- No paragraph-level homepage deep links in this stage.

## Design

`_local_article_takeaway_section` will accept `story` in addition to `paragraphs` and `paragraphs_zh`. It will build a deterministic list of explicit reference names from story entity, designer, and product refs, ignoring one- and two-character noisy names. For each non-empty paragraph, it will calculate a score with case-insensitive boundary-aware reference-name matching, so short refs are not promoted from unrelated words. Paragraphs with matches are selected first by descending score, then by original paragraph order. If no paragraphs match any explicit reference name, the function uses the current first-three non-empty paragraph behavior exactly.

The selected paragraph indices remain original source positions. Labels stay simple and deterministic: first selected item is `Source lead` / `来源导语`; later selected items are `Source point N` / `来源要点 N`. The section key remains `takeaways`, so existing detail rendering, local sidecar JSON, and Daily Local Intelligence consume the improved content without contract changes.

## File Map

- Modify `src/fashion_radar/row_one/articles.py`
  - Add helper to collect explicit local article signal terms from story refs.
  - Add helper to select takeaway paragraph indices, compiling signal regex patterns once per story.
  - Update `_local_article_takeaway_section` to accept `story`.
  - Update `_local_article_content_sections` to pass `story`.
- Modify `tests/test_row_one_articles.py`
  - Add a small `_extractor(text: str)` test helper compatible with the existing extractor signature.
  - Add signal-rich later paragraph selection coverage using `edition = _edition(); story = edition.stories[0]`.
  - Add fallback preservation coverage.
  - Add equal-score original-order coverage and short-term near-miss coverage.
  - Update the existing content-section test to assert the new scored takeaway order.
  - Assert original paragraph indices are retained.
- Modify `tests/test_row_one_local_intelligence.py`
  - Add strongest-read body coverage proving Daily Local Intelligence uses the curated first takeaway.
- Modify `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`
  - Add docs drift coverage and short documentation for source-backed signal paragraph prioritization.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-306-plan-review-prompt.md`
  - `claude-code-stage-306-plan-review.md`
  - `opencode-stage-306-plan-review-prompt.md`
  - `opencode-stage-306-plan-review.md`
  - code review artifacts after implementation.

## Task 1: Failing Article Builder Tests

**Files:**
- Modify: `tests/test_row_one_articles.py`

- [ ] **Step 1: Add a test for reference-rich later paragraph priority**

Add this helper near `_source` so new tests can reuse the existing extractor signature without changing production code:

```python
def _extractor(text: str):
    def extractor(url: str, *, source, html_fetcher, robots_checker):
        return ArticleExtractionResult(
            url=url,
            title="Signal source",
            text=text,
            skipped=False,
        )

    return extractor
```

Then add this test near the existing local article content-section tests:

```python
def test_build_row_one_local_articles_takeaways_prefer_signal_dense_paragraphs() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    story.designer_refs = [
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer")
    ]
    story.tags = ["quiet luxury"]
    paragraphs = [
        "Opening market context without a named signal.",
        "The Row and Margaux bag demand accelerated in saved source reporting.",
        "General retail context continues across wholesale accounts.",
        "Mary-Kate Olsen framed the design language around restraint.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    article = articles[story.id]
    takeaways = _content_section(article, "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "The Row and Margaux bag demand accelerated in saved source reporting.",
        "Mary-Kate Olsen framed the design language around restraint.",
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [3]]
```

Expected before implementation: fail because current `takeaways` uses the first three paragraphs.

- [ ] **Step 2: Add a test proving fallback stays first-three when no signal matches**

Add this test near the same section:

```python
def test_build_row_one_local_articles_takeaways_keep_first_three_when_no_signal_matches() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    paragraphs = [
        "Opening source paragraph.",
        "Second source paragraph.",
        "Third source paragraph.",
        "Fourth source paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[:3]
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1], [2]]
```

Expected before implementation: pass today; keep it to prevent regressions during refactor.


- [ ] **Step 3: Add equal-score and near-miss coverage**

Add these tests near the same section:

```python
def test_build_row_one_local_articles_takeaways_keep_original_order_for_equal_scores() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
    ]
    paragraphs = [
        "Opening source paragraph.",
        "The Row appears in this saved paragraph.",
        "Zendaya appears in this later saved paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[1:]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [2]]


def test_build_row_one_local_articles_takeaways_ignore_short_ref_near_misses() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="Ro", type="brand", label="typo"),
        RowOneReference(name="Row", type="brand", label="short"),
        RowOneReference(name="The Row", type="brand", label="tracked"),
    ]
    paragraphs = [
        "Opening brown leather market context without a named signal.",
        "The Row appears as an explicit saved source signal.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == [
        "The Row appears as an explicit saved source signal."
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1]]
```

The near-miss test requires scoring to avoid promoting short standalone refs inside unrelated words.

- [ ] **Step 4: Add cap coverage when more than three paragraphs match**

Add this test near the same section:

```python
def test_build_row_one_local_articles_takeaways_cap_signal_matches_at_three() -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [
        RowOneReference(name="The Row", type="brand", label="tracked"),
        RowOneReference(name="Zendaya", type="celebrity", label="new"),
        RowOneReference(name="Mary-Kate Olsen", type="designer", label="founder"),
    ]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    paragraphs = [
        "The Row appears in the opening saved source paragraph.",
        "Zendaya appears in the second saved source paragraph.",
        "Margaux appears in the third saved source paragraph.",
        "Mary-Kate Olsen appears in the fourth saved source paragraph.",
    ]

    articles = build_row_one_local_articles(
        edition,
        [_source(max_chars=500)],
        now=AS_OF,
        extractor=_extractor("\n\n".join(paragraphs)),
    )

    takeaways = _content_section(articles[story.id], "takeaways")
    assert [item.body.en for item in takeaways.items] == paragraphs[:3]
    assert [item.paragraph_indices for item in takeaways.items] == [[0], [1], [2]]
```

- [ ] **Step 5: Run focused article tests and confirm red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_prefer_signal_dense_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_keep_first_three_when_no_signal_matches \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_keep_original_order_for_equal_scores \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_ignore_short_ref_near_misses \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_cap_signal_matches_at_three -q
```

Expected before implementation: the signal-dense, equal-score, near-miss, and cap tests fail because current `takeaways` still use the first saved paragraphs; the first-three fallback test passes.

## Task 2: Deterministic Takeaway Paragraph Selection

**Files:**
- Modify: `src/fashion_radar/row_one/articles.py`
- Test: `tests/test_row_one_articles.py`

- [ ] **Step 1: Add explicit signal term helper**

Near `_local_article_paragraph_indices`, add:

```python
def _local_article_signal_terms(story: RowOneStory) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for ref in [*story.entity_refs, *story.designer_refs, *story.product_refs]:
        term = normalize_row_one_paragraph(ref.name)
        if len(term) < 3:
            continue
        key = term.casefold()
        if key in seen:
            continue
        seen.add(key)
        terms.append(term)
    return terms
```

Do not include labels such as `tracked`, `new`, `bag`, or generic tags in this helper. The intent is explicit named signal matching.

- [ ] **Step 2: Add a selected-index helper with fallback**

Near `_local_article_signal_terms`, add. `articles.py` already imports `re`, so use boundary-aware regex patterns rather than raw substring containment, and compile those patterns once per story:

```python
def _local_article_takeaway_indices(
    story: RowOneStory,
    paragraphs: list[str],
    *,
    limit: int = 3,
) -> list[int]:
    non_empty = [index for index, paragraph in enumerate(paragraphs) if paragraph.strip()]
    terms = _local_article_signal_terms(story)
    patterns = [
        re.compile(rf"(?<![a-z0-9]){re.escape(term.casefold())}(?![a-z0-9])")
        for term in terms
    ]
    scored = [
        (
            index,
            sum(
                1
                for pattern in patterns
                if pattern.search(paragraphs[index].casefold())
            ),
        )
        for index in non_empty
    ]
    matched = [(index, score) for index, score in scored if score > 0]
    if matched:
        matched.sort(key=lambda item: (-item[1], item[0]))
        return [index for index, _score in matched[:limit]]
    return non_empty[:limit]
```

This keeps deterministic output, preserves original paragraph positions, ignores 1-2 character noisy refs, and avoids matching short terms inside unrelated words.

- [ ] **Step 3: Update `_local_article_takeaway_section` signature and loop**

Change the signature from:

```python
def _local_article_takeaway_section(
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> RowOneLocalArticleContentSection | None:
```

to:

```python
def _local_article_takeaway_section(
    story: RowOneStory,
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> RowOneLocalArticleContentSection | None:
```

Inside the function, replace the current `enumerate(zip(paragraphs[:3], aligned_zh[:3], strict=True))` loop with:

```python
    for position, index in enumerate(_local_article_takeaway_indices(story, paragraphs)):
        paragraph_en = paragraphs[index]
        paragraph_zh = aligned_zh[index] if index < len(aligned_zh) else ""
        if not paragraph_en.strip():
            continue
        label_en = "Source lead" if position == 0 else f"Source point {position + 1}"
        label_zh = "来源导语" if position == 0 else f"来源要点 {position + 1}"
```

Keep the existing `_localized_content_item(...)` call but pass `paragraph_indices=[index]`.

- [ ] **Step 4: Update caller**

In `_local_article_content_sections`, change:

```python
takeaway_section = _local_article_takeaway_section(paragraphs, paragraphs_zh)
```

to:

```python
takeaway_section = _local_article_takeaway_section(story, paragraphs, paragraphs_zh)
```

- [ ] **Step 5: Update existing content-section takeaway assertions**

In `test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs`, update the takeaway assertions to reflect the scored order. Replace the existing first-three order assertions with:

```python
    assert [item.body.en for item in takeaways.items] == [
        "Second source paragraph shows Zendaya styling context around Margaux.",
        "First source paragraph frames The Row demand.",
        "Third source paragraph mentions Mary-Kate Olsen and a product signal.",
    ]
    assert [item.paragraph_indices for item in takeaways.items] == [[1], [0], [2]]
```

- [ ] **Step 6: Run focused article tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_prefer_signal_dense_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_keep_first_three_when_no_signal_matches \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_keep_original_order_for_equal_scores \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_ignore_short_ref_near_misses \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_takeaways_cap_signal_matches_at_three \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_work_on_fallback -q
```

Expected: all pass.

## Task 3: Daily Local Intelligence Uses Curated Takeaway

**Files:**
- Modify: `tests/test_row_one_local_intelligence.py`

- [ ] **Step 1: Add a local intelligence test for curated first takeaway**

Add this test near the strongest reads tests:

```python
def test_build_row_one_local_article_intelligence_uses_curated_first_takeaway() -> None:
    story = _story(
        "the-row-1234567890",
        "The Row saved article",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[RowOneReference(name="The Row", type="brand", label="tracked")],
        product_refs=[RowOneReference(name="Margaux", type="bag", label="product")],
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Opening source context without a named product signal.",
            "The Row and Margaux moved together in the saved local source.",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 和 Margaux 在本地来源中一起变化。",
                            en="The Row and Margaux moved together in the saved local source.",
                        ),
                        paragraph_indices=[1],
                    ),
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源要点 2", en="Source point 2"),
                        body=LocalizedText(
                            zh="没有明确产品信号的开头上下文。",
                            en="Opening source context without a named product signal.",
                        ),
                        paragraph_indices=[0],
                    ),
                ],
            )
        ],
    )

    sections = build_row_one_local_article_intelligence(_edition([story]), {story.id: article})

    strongest = next(section for section in sections if section.key == "strongest_reads")
    item = strongest.items[0]
    assert item.body.en == "The Row and Margaux moved together in the saved local source."
    assert item.paragraph_indices == [1]
```

Expected before Task 2 implementation if generated articles are not used here: this test may pass because it constructs the curated article directly. Its purpose is to lock the local intelligence contract after the builder improves generated `takeaways`.

- [ ] **Step 2: Run local intelligence focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_local_intelligence.py::test_build_row_one_local_article_intelligence_uses_curated_first_takeaway \
  tests/test_row_one_local_intelligence.py::test_build_row_one_local_article_intelligence_preserves_article_content_segments -q
```

Expected: pass.

## Task 4: Docs Drift

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs drift assertions**

In `test_row_one_docs_describe_daily_local_intelligence`, add:

```python
    assert "source-backed signal paragraphs" in readme
    assert "explicit brand, designer, person, bag, shoe, or product matches" in row_one_docs
```

- [ ] **Step 2: Run docs test and confirm red**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected before docs update: fail on the new phrases.

- [ ] **Step 3: Update README**

Near the existing local article paragraph, add:

```markdown
Local article takeaways prioritize source-backed signal paragraphs with explicit
brand, designer, person, bag, shoe, or product matches before falling back to
the first saved paragraphs.
```

- [ ] **Step 4: Update docs/row-one.md**

Near the local article section, add:

```markdown
The `takeaways` content section prefers saved paragraphs with explicit brand,
designer, person, bag, shoe, or product matches, while retaining the first saved
paragraphs as the deterministic fallback when no signal paragraph is present.
```

- [ ] **Step 5: Run docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_daily_local_intelligence -q
```

Expected: pass.

## Task 5: Review, Verification, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-306-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-306-code-review.md`

- [ ] **Step 1: Run focused ROW ONE checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py \
  tests/test_row_one_local_intelligence.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite -q
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

Expected: all pass.

- [ ] **Step 3: Create Claude Code code review prompt**

Create `docs/reviews/claude-code-stage-306-code-review-prompt.md` with:

```markdown
# Claude Code Stage 306 Code Review Prompt

You are reviewing Stage 306 for `/home/ubuntu/fashion-radar`.

Review objective:
- Confirm ROW ONE local article takeaways now prefer deterministic source-backed signal paragraphs.
- Confirm fallback remains first-three non-empty saved paragraphs when no explicit reference term matches.
- Confirm original paragraph_indices are preserved.
- Confirm Daily Local Intelligence uses the curated first takeaway without changing models or app contracts.
- Confirm docs reflect the new behavior.
- Confirm scope excludes templates/CSS redesign, source acquisition, scraping, social connectors, scheduler, dependencies, schema, `data/edition.json`, `row-one-app/v7`, image generation, and compliance-review product features.
- Identify Critical or Important issues that must be fixed before commit/push.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required fixes before commit
End with the exact line: REVIEW_COMPLETE
```

Fill in the actual base SHA, changed files, and verification commands before running the review.

- [ ] **Step 4: Run Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-306-code-review-prompt.md)" > "$tmp_review"
cat "$tmp_review"
tail -n 1 "$tmp_review" | grep -qx 'REVIEW_COMPLETE'
cp "$tmp_review" docs/reviews/claude-code-stage-306-code-review.md
rm -f "$tmp_review"
```

Fix any Critical or Important findings before proceeding.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add README.md docs/row-one.md src/fashion_radar/row_one/articles.py \
  tests/test_row_one_articles.py tests/test_row_one_local_intelligence.py \
  tests/test_row_one_docs.py \
  docs/superpowers/plans/2026-07-05-stage-306-row-one-signal-dense-takeaways-plan.md \
  docs/reviews/claude-code-stage-306-plan-review-prompt.md \
  docs/reviews/claude-code-stage-306-plan-review.md \
  docs/reviews/opencode-stage-306-plan-review-prompt.md \
  docs/reviews/opencode-stage-306-plan-review.md \
  docs/reviews/claude-code-stage-306-code-review-prompt.md \
  docs/reviews/claude-code-stage-306-code-review.md
git commit -m "Stage 306: prioritize row one signal-dense takeaways"
git push origin main
```

Expected final state: pushed commit on `main`, clean working tree.
