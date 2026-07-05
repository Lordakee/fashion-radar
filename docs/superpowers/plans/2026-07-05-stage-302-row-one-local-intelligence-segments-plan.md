# Stage 302 ROW ONE Local Intelligence Segments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE's Daily Local Intelligence cards show compact, source-backed content segments from saved local article bodies, so the homepage and `data/local-intelligence.json` organize information instead of exposing only one summary line and a link.

**Architecture:** Reuse the existing local article sidecar structure (`RowOneLocalArticle.content_sections`) and project it into a capped nested segment model on `RowOneDailyLocalIntelligenceItem`. Keep `row-one-app/v7` stable by writing the new structure only to the already-separate generated `data/local-intelligence.json` and rendering it in the static homepage. The implementation stays deterministic, local-first, escaped in HTML, source-attributed, capped, and bounded to saved local article excerpts.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

The user asked for ROW ONE to organize fashion information locally instead of acting like a list of external links. Stages 300 and 301 already created saved local article content sections and a homepage Daily Local Intelligence area. Stage 302 closes the next gap: daily cards currently flatten that organized content into one `body` sentence. This stage carries compact content segments such as takeaways, matched entity/product context, and brand signals into each daily intelligence item.

This stage does not add scraping, social connectors, source acquisition, ranking changes, demand proof, platform coverage verification, app UI work, image generation, paywall bypass, or compliance-review product features.

## File Structure

- Modify `src/fashion_radar/row_one/models.py`
  - Add `RowOneDailyLocalIntelligenceSegment`.
  - Add `segments: list[RowOneDailyLocalIntelligenceSegment]` to `RowOneDailyLocalIntelligenceItem`.
  - Keep `extra="forbid"` so generated JSON remains contract-like.
- Modify `src/fashion_radar/row_one/local_intelligence.py`
  - Replace the reference aggregate `dict[str, object]` with a small internal `_ReferenceAggregate` dataclass so segment state does not add more broad casts.
  - Build capped segments from existing `RowOneLocalArticle.content_sections`.
  - For `strongest_reads` and `heat_movers`, include the first useful segments from `takeaways`, `entities`, `product_signals`, and `brand_signals`.
  - For `brand_watch` and `product_watch`, prefer matching reference items from `entities` or `product_signals`, then fall back to the existing source paragraph/takeaway.
  - Preserve `source_names`, `references`, `paragraph_indices`, and safe detail paths.
  - Never include the full `paragraphs` list in daily intelligence items.
- Modify `src/fashion_radar/row_one/templates.py`
  - Render each item segment under the card body using existing bilingual spans and HTML escaping.
  - Keep the whole card link safe with `_safe_daily_local_intelligence_href`.
  - Do not render empty segments.
- Modify `tests/test_row_one_local_intelligence.py`
  - Add builder tests for segment projection and matched reference segment preference.
- Modify `tests/test_row_one_render.py`
  - Add render/artifact tests for nested segment JSON, homepage HTML, and escaping.
- Modify `README.md` and `tests/test_row_one_docs.py` only if behavior wording needs to mention compact content segments explicitly.

## Task 1: Review Gate

- [ ] **Step 1: Create Claude Code plan review prompt**

Create `docs/reviews/claude-code-stage-302-plan-review-prompt.md`:

```markdown
# Claude Code Stage 302 Plan Review Prompt

You are reviewing the Stage 302 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether adding nested compact segments to Daily Local Intelligence is a sound way to satisfy the user's content-organization requirement.
- Check whether the plan preserves the free-first/local-first boundary and avoids adding scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review product features.
- Check whether keeping `row-one-app/v7` stable while enriching only the separate `data/local-intelligence.json` artifact is technically sound.
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
  -p "$(cat docs/reviews/claude-code-stage-302-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-302-plan-review.md
rm -f "$tmp_review"
```

Expected: a coherent review body with a clear verdict. If Claude Code exits without a usable review body or times out, write `docs/reviews/claude-code-stage-302-plan-review.md` with `Verdict: UNAVAILABLE` and the exact non-secret failure reason.

- [ ] **Step 3: Create opencode plan review/revision prompt**

Create `docs/reviews/opencode-stage-302-plan-review-prompt.md`:

```markdown
# opencode Stage 302 Plan Review Prompt

You are reviewing the Stage 302 plan for `/home/ubuntu/fashion-radar`.

Plan: `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`
Claude Code review: `docs/reviews/claude-code-stage-302-plan-review.md`

After Claude Code's review, revise the plan based on that review and your own judgment. If Claude Code is unavailable, act as fallback reviewer. Use GLM 5.2 max judgment.

Review objective:
- Confirm that compact nested Daily Local Intelligence segments are technically reasonable.
- Check that implementation remains local-first and deterministic, with no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review product features.
- Check that the new segment JSON remains outside `data/edition.json` and does not break `row-one-app/v7`.
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
  "$(cat docs/reviews/opencode-stage-302-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-302-plan-review.md
rm -f "$tmp_review"
```

Expected: a coherent review body with a clear verdict and no live-capture stubs.

- [ ] **Step 5: Apply plan-review findings**

If either review returns Critical or Important findings, update this plan before implementation and record rereview artifacts as `docs/reviews/*stage-302-plan-rereview*`.

## Task 2: RED Builder Tests For Segments

- [ ] **Step 1: Add RED test for strongest-read segments**

Add this test to `tests/test_row_one_local_intelligence.py`:

```python
def test_build_row_one_local_article_intelligence_preserves_article_content_segments() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    story = _story(
        "the-row-1234567890",
        "The Row demand moves",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[the_row],
        product_refs=[margaux],
        heat_delta=7,
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row opened with broader market context.",
            "Margaux demand was called out as a bag signal.",
        ],
        paragraphs_zh=["The Row 中文上下文。", "Margaux 中文产品信号。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 中文上下文。",
                            en="The Row opened with broader market context.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Margaux", en="Margaux"),
                        body=LocalizedText(
                            zh="bag / product",
                            en="bag / product",
                        ),
                        references=[margaux],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    strongest = next(section for section in sections if section.key == "strongest_reads")
    item = strongest.items[0]
    assert [segment.key for segment in item.segments] == ["takeaways", "product_signals"]
    assert item.segments[0].title.en == "Takeaways"
    assert item.segments[0].items[0].label.en == "Source lead"
    assert item.segments[0].items[0].body.en == "The Row opened with broader market context."
    assert item.segments[0].items[0].paragraph_indices == [0]
    assert item.segments[1].items[0].references == [margaux]
    dumped = item.model_dump(mode="json")
    assert "paragraphs" not in dumped
```

- [ ] **Step 2: Add RED test for matched reference segments**

Add:

```python
def test_build_row_one_local_article_intelligence_uses_matching_reference_segments() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    story = _story(
        "the-row-1234567890",
        "The Row context",
        detail_path="details/the-row-1234567890.html",
        entity_refs=[the_row],
    )
    article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "Generic opening paragraph.",
            "The Row paragraph has the useful brand context.",
        ],
        paragraphs_zh=["通用开头。", "The Row 中文品牌上下文。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(zh="通用开头。", en="Generic opening paragraph."),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="相关对象", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="The Row", en="The Row"),
                        body=LocalizedText(
                            zh="brand / tracked",
                            en="brand / tracked",
                        ),
                        references=[the_row],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {story.id: article},
    )

    brand_watch = next(section for section in sections if section.key == "brand_watch")
    item = brand_watch.items[0]
    assert item.body.en == "The Row paragraph has the useful brand context. Sources: Vogue Business."
    assert item.paragraph_indices == [1]
    assert [segment.key for segment in item.segments] == ["entities"]
    assert item.segments[0].items[0].label.en == "The Row"
    assert item.segments[0].items[0].paragraph_indices == [1]
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py
```

Expected: FAIL because `RowOneDailyLocalIntelligenceItem` has no `segments` attribute yet.

## Task 3: Implement Segment Models And Builder Projection

- [ ] **Step 1: Add segment models**

In `src/fashion_radar/row_one/models.py`, add:

```python
class RowOneDailyLocalIntelligenceSegmentItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: LocalizedText
    body: LocalizedText | None = None
    references: list[RowOneReference] = Field(default_factory=list)
    paragraph_indices: list[int] = Field(default_factory=list)


class RowOneDailyLocalIntelligenceSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: RowOneLocalArticleContentKey
    title: LocalizedText
    body: LocalizedText | None = None
    items: list[RowOneDailyLocalIntelligenceSegmentItem] = Field(default_factory=list)
```

`body` intentionally mirrors `RowOneLocalArticleContentSection.body`; the projection should copy it when present so section-level context such as "saved source text points to these reads" can render in the homepage segment. It is not dead schema weight.

Then add to `RowOneDailyLocalIntelligenceItem`:

```python
segments: list[RowOneDailyLocalIntelligenceSegment] = Field(default_factory=list)
```

- [ ] **Step 2: Project local article content sections**

In `src/fashion_radar/row_one/local_intelligence.py`, add helper functions that:

- Convert `RowOneLocalArticleContentSection` into `RowOneDailyLocalIntelligenceSegment`.
- Copy non-empty section-level `body` into the segment.
- Drop sections with no useful item bodies, references, or paragraph indices.
- Cap sections to 4 and items per section to 3.
- Preserve `label`, optional `body`, `references`, and `paragraph_indices`.
- For reference cards, select only sections/items matching the requested normalized reference name when possible.

Replace the aggregate dict in `_reference_watch_section()` with:

```python
@dataclass
class _ReferenceAggregate:
    display_name: str
    stories: set[str] = field(default_factory=set)
    articles: set[str] = field(default_factory=set)
    source_names: list[str] = field(default_factory=list)
    evidence_count: int = 0
    heat_delta: int | None = None
    references: list[RowOneReference] = field(default_factory=list)
    body: str | None = None
    body_zh: str | None = None
    detail_path: str | None = None
    paragraph_indices: list[int] = field(default_factory=list)
    segments: list[RowOneDailyLocalIntelligenceSegment] = field(default_factory=list)
```

Use deterministic constants:

```python
MAX_SEGMENTS_PER_ITEM = 4
MAX_SEGMENT_ITEMS = 3
```

- [ ] **Step 3: Attach segments to items**

Update:

- `_story_article_item(...)` to pass `segments=_article_segments(article)`.
- `_reference_watch_section(...)` aggregate dict to store `segments`.
- The first matching reference for an aggregate should set `segments=_reference_segments(article, ref)`.
- `_aggregate_item(...)` to pass the stored segment list.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py
```

Expected: PASS.

## Task 4: RED Render And Artifact Tests

- [ ] **Step 1: Add render/artifact test**

Add to `tests/test_row_one_render.py` near the existing Daily Local Intelligence tests:

```python
def test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row source paragraph.",
            "Margaux product paragraph.",
        ],
        paragraphs_zh=["The Row 中文段落。", "Margaux 中文段落。"],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(zh="The Row 中文段落。", en="The Row source paragraph."),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Margaux", en="Margaux"),
                        body=LocalizedText(zh="bag / product", en="bag / product"),
                        references=[RowOneReference(name="Margaux", type="bag", label="product")],
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "daily-local-intelligence-segments" in html
    assert "Takeaways" in html
    assert "Source lead" in html
    assert "The Row source paragraph." in html
    assert "Product Signals" in html
    assert "Margaux" in html

    artifact = json.loads(
        (tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8")
    )
    strongest = next(section for section in artifact if section["key"] == "strongest_reads")
    assert strongest["items"][0]["segments"][0]["key"] == "takeaways"
    assert strongest["items"][0]["segments"][0]["items"][0]["paragraph_indices"] == [0]
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    assert "local_article_intelligence" not in payload
```

- [ ] **Step 2: Add escaping test for nested segments**

Replace the local article fixture inside `test_render_row_one_site_escapes_daily_local_intelligence` with:

```python
RowOneLocalArticle(
    story_id=story.id,
    url="https://example.com/the-row",
    source_name="<Vogue>",
    extracted_at=AS_OF,
    paragraphs=['<script>alert("body")</script>'],
    content_sections=[
        RowOneLocalArticleContentSection(
            key="takeaways",
            title=LocalizedText(
                zh="<script>栏目</script>",
                en="<script>Segment</script>",
            ),
            body=LocalizedText(
                zh="<img src=x onerror=\"alert(1)\"> 中文段说明",
                en="<img src=x onerror=\"alert(1)\"> segment body",
            ),
            items=[
                RowOneLocalArticleContentItem(
                    label=LocalizedText(
                        zh="<script>标签</script>",
                        en="<script>Label</script>",
                    ),
                    body=LocalizedText(
                        zh="<img src=x onerror=\"alert(2)\"> 中文嵌套正文",
                        en="<img src=x onerror=\"alert(2)\"> nested body",
                    ),
                    references=[
                        RowOneReference(
                            name="<script>Nested Ref</script>",
                            type="brand",
                            label="tracked",
                        )
                    ],
                    paragraph_indices=[0],
                )
            ],
        )
    ],
)
```

Then assert:

```python
assert '<script>Segment</script>' not in html
assert '<script>Label</script>' not in html
assert '<script>Nested Ref</script>' not in html
assert '<img src=x onerror="alert' not in html
assert "&lt;script&gt;Segment&lt;/script&gt;" in html
assert "&lt;script&gt;Label&lt;/script&gt;" in html
assert "&lt;img src=x onerror=&quot;alert(2)&quot;&gt; nested body" in html
assert "&lt;script&gt;Nested Ref&lt;/script&gt;" in html
```

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_local_intelligence
```

Expected: FAIL because the homepage template does not render segment markup yet.

## Task 5: Render Segments In Homepage Cards

- [ ] **Step 1: Add segment rendering helpers**

In `src/fashion_radar/row_one/templates.py`, add helpers near Daily Local Intelligence rendering:

- `_render_daily_local_intelligence_segments(item)`
- `_render_daily_local_intelligence_segment(segment)`
- `_render_daily_local_intelligence_segment_item(segment_item)`

The helpers must:

- Return `""` for empty segment lists.
- Escape all labels, bodies, and reference names.
- Render bilingual labels and bodies with `data-lang`.
- Keep compact markup below the card body.

- [ ] **Step 2: Call segment renderer from cards**

Update `_render_daily_local_intelligence_item` so `body` includes:

```python
segments = _render_daily_local_intelligence_segments(item)
...
{segments}
```

- [ ] **Step 3: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_render.py::test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_local_intelligence
```

Expected: PASS.

## Task 6: Docs, Full Verification, Review, Commit, Push

- [ ] **Step 1: Update docs if needed**

If the README wording does not mention nested compact content segments, add one sentence near the Daily Local Intelligence paragraph.

- [ ] **Step 2: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py
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

Create and run `docs/reviews/claude-code-stage-302-code-review-prompt.md`, then store the review in `docs/reviews/claude-code-stage-302-code-review.md`. The prompt must ask Claude Code to review only changes since `0f591ab` and check the Stage 302 plan.

- [ ] **Step 5: Use opencode fallback only if Claude Code is unavailable**

If Claude Code is unavailable, run opencode with:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-302-code-review-prompt.md)"
```

- [ ] **Step 6: Fix Critical and Important findings**

Apply fixes, rerun relevant tests and full verification, and request rereview if needed.

- [ ] **Step 7: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/models.py \
  src/fashion_radar/row_one/local_intelligence.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_local_intelligence.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md \
  docs/reviews/claude-code-stage-302-plan-review-prompt.md \
  docs/reviews/claude-code-stage-302-plan-review.md \
  docs/reviews/opencode-stage-302-plan-review-prompt.md \
  docs/reviews/opencode-stage-302-plan-review.md \
  docs/reviews/claude-code-stage-302-code-review-prompt.md \
  docs/reviews/claude-code-stage-302-code-review.md
git commit -m "Stage 302: add row one local intelligence segments"
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
