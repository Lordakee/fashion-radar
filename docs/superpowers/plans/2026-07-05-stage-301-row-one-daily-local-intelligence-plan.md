# Stage 301 ROW ONE Daily Local Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a homepage-level ROW ONE daily intelligence section derived from saved local article content so readers see organized fashion signals, brands, products, and heat movers without leaving the generated website.

**Architecture:** Build a deterministic, source-grounded local intelligence layer from `RowOneEdition`, `RowOneStory`, and the already-saved `RowOneLocalArticle` sidecars. Keep the app contract stable by rendering this layer into the static website and writing a separate optional `data/local-intelligence.json` artifact, without adding a new `row-one-app/v7` top-level field. The section uses saved local article takeaways/paragraphs as card bodies, existing bilingual text patterns, safe detail links, escaped HTML, and current generated-site cleanup.

**Tech Stack:** Python 3.12, Pydantic models, static HTML rendering, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Product Gap Closed

Stage 300 made each saved source article more readable on its own detail page. Stage 301 makes the daily homepage act like a fashion editor's organized board instead of a list of links:

- `strongest_reads`: the best saved local article paragraphs to read first.
- `brand_watch`: brands, designers, celebrities, and other entity refs appearing across saved articles, with source-backed paragraph context.
- `product_watch`: products such as bags, shoes, and named items appearing across saved articles, with source-backed paragraph context.
- `heat_movers`: stories with positive local heat deltas and saved local article bodies, with the saved local article takeaway as the body.

This stage is deterministic and free-first. It does not add a crawler, social connector, LLM summarizer, image generation, app UI change, paywall bypass, compliance-review feature, source acquisition, or platform monitoring.

## File Structure

- Create `src/fashion_radar/row_one/local_intelligence.py`
  - Build `RowOneDailyLocalIntelligenceSection` objects from the current edition plus saved local articles.
  - Aggregate entity/product refs by normalized name.
  - Pick readable source takeaways from `article.content_sections` when available and fall back to saved paragraphs.
  - Use the best matched saved paragraph/takeaway as each reference card body, keeping `type / label` metadata in `references` rather than replacing local source context.
  - Keep sorting deterministic: item count, heat, evidence, then display name.
- Modify `src/fashion_radar/row_one/models.py`
  - Add `RowOneDailyLocalIntelligenceKey`.
  - Add `RowOneDailyLocalIntelligenceItem`.
  - Add `RowOneDailyLocalIntelligenceSection`.
- Modify `src/fashion_radar/row_one/render.py`
  - Build local intelligence after normalizing `local_articles_by_story_id`.
  - Pass it to `render_index_html`.
  - Write `data/local-intelligence.json` only when at least one section has items.
  - Do not add the data to `data/edition.json`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Add optional `local_article_intelligence` parameter to `render_index_html`.
  - Render the section after `signal_synthesis` and before the lead story.
  - Use existing language toggle, HTML escaping, and safe detail href validation.
  - Add restrained CSS selectors for the section.
- Create `tests/test_row_one_local_intelligence.py`
  - Cover deterministic aggregation and fallbacks without depending on the full renderer.
- Modify `tests/test_row_one_render.py`
  - Cover homepage rendering, artifact writing, escaping, cleanup, and app-contract isolation.

## Task 1: Plan Review Gate

- [ ] **Step 1: Create Claude Code plan review prompt**

Create `docs/reviews/claude-code-stage-301-plan-review-prompt.md`:

```markdown
# Claude Code Stage 301 Plan Review Prompt

You are reviewing the Stage 301 plan for /home/ubuntu/fashion-radar.

Plan: docs/superpowers/plans/2026-07-05-stage-301-row-one-daily-local-intelligence-plan.md

Review objective:
- Confirm the goal, architecture, tech stack, implementation method, and staged plan are reasonable.
- Check whether the plan preserves the free-first/local-first boundary and avoids adding social scraping, platform APIs, app UI work, or compliance-review product features.
- Check whether keeping row-one-app/v7 stable while adding a separate local-intelligence artifact is technically sound.
- Identify Critical or Important issues that must be fixed before implementation.

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
```

- [ ] **Step 2: Attempt Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-301-plan-review-prompt.md)"
```

Expected: completed review text. If Claude Code exits without a usable body or times out, write `docs/reviews/claude-code-stage-301-plan-review.md` with `Verdict: UNAVAILABLE` and the exact non-secret failure reason.

- [ ] **Step 3: Create opencode fallback plan review prompt**

Create `docs/reviews/opencode-stage-301-plan-review-prompt.md` with the same review objective, plus this instruction:

```markdown
Claude Code review may be unavailable. If it is unavailable, act as fallback reviewer. Use GLM 5.2 max judgment and identify Critical/Important issues before implementation.
```

- [ ] **Step 4: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-301-plan-review-prompt.md)" \
  > docs/reviews/opencode-stage-301-plan-review.md
```

Expected: review file with a clear verdict and no ANSI/tool chatter.

- [ ] **Step 5: Apply plan-review findings**

If review returns Critical/Important findings, update this plan before implementing. Record any rereview as `docs/reviews/*stage-301-plan-rereview*`.

## Task 2: RED Local Intelligence Builder Tests

- [ ] **Step 1: Create `tests/test_row_one_local_intelligence.py` with imports and fixtures**

```python
from __future__ import annotations

from datetime import datetime, timezone

from fashion_radar.row_one.local_intelligence import build_row_one_local_article_intelligence
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)

AS_OF = datetime(2026, 7, 5, 4, 0, tzinfo=timezone.utc)


def _story(
    story_id: str,
    headline: str,
    *,
    detail_path: str,
    source_name: str = "Vogue Business",
    story_type: str = "tracked_entity",
    heat_delta: int | None = None,
    entity_refs: list[RowOneReference] | None = None,
    product_refs: list[RowOneReference] | None = None,
    designer_refs: list[RowOneReference] | None = None,
    tags: list[str] | None = None,
) -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type=story_type,
        headline=headline,
        summary=LocalizedText(zh=f"{headline} 摘要", en=f"{headline} summary"),
        why_it_matters=LocalizedText(zh="为什么重要", en="Why it matters"),
        editorial_takeaway=LocalizedText(zh="编辑判断", en="Editorial takeaway"),
        signal_context=LocalizedText(zh="本地信号背景", en="Local signal context"),
        reader_path=LocalizedText(zh="先读本地正文", en="Read the local article first"),
        source_name=source_name,
        source_url="https://example.com/source",
        published_at=AS_OF,
        detail_path=detail_path,
        tags=tags or [],
        evidence=[RowOneLink(title="Evidence", url="https://example.com/evidence", source_name=source_name)],
        entity_refs=entity_refs or [],
        product_refs=product_refs or [],
        designer_refs=designer_refs or [],
        heat_delta=heat_delta,
    )


def _edition(stories: list[RowOneStory]) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日本地时尚情报", en="Today local fashion intelligence"),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的内容", en="Read first"),
            )
        ],
        stories=stories,
    )


def _article(story_id: str, *, source_name: str, paragraphs: list[str]) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        url="https://example.com/article",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs,
        paragraphs_zh=[f"中文 {index + 1}" for index, _paragraph in enumerate(paragraphs)],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                        body=LocalizedText(zh="中文重点 1", en=paragraphs[0]),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )
```

- [ ] **Step 2: Add RED test for section keys and local article filtering**

```python
def test_build_row_one_local_article_intelligence_uses_only_current_saved_articles() -> None:
    the_row = RowOneReference(name="The Row", type="brand", label="tracked")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    stories = [
        _story(
            "the-row-1234567890",
            "The Row demand moves",
            detail_path="details/the-row-1234567890.html",
            heat_delta=9,
            entity_refs=[the_row],
            product_refs=[margaux],
            tags=["brand", "bag"],
        )
    ]
    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "the-row-1234567890": _article(
                "the-row-1234567890",
                source_name="Vogue Business",
                paragraphs=["The Row and Margaux are the saved local source signal."],
            ),
            "stale-story": _article(
                "stale-story",
                source_name="Old Source",
                paragraphs=["This stale article must not appear."],
            ),
        },
    )

    assert [section.key for section in sections] == [
        "strongest_reads",
        "brand_watch",
        "product_watch",
        "heat_movers",
    ]
    assert sections[0].items[0].title.en == "The Row demand moves"
    assert sections[0].items[0].detail_path == "details/the-row-1234567890.html#local-article"
    assert sections[0].items[0].source_name == "Vogue Business"
    assert sections[0].items[0].source_names == ["Vogue Business"]
    assert sections[1].items[0].title.en == "The Row"
    assert sections[2].items[0].title.en == "Margaux"
    assert sections[3].items[0].heat_delta == 9
    assert "stale" not in sections[0].items[0].body.en
```

- [ ] **Step 3: Add RED test for aggregation and deterministic sorting**

```python
def test_build_row_one_local_article_intelligence_aggregates_references_by_name() -> None:
    the_row_brand = RowOneReference(name="The Row", type="brand", label="tracked")
    the_row_label = RowOneReference(name="the row", type="brand", label="candidate")
    margaux = RowOneReference(name="Margaux", type="bag", label="product")
    sandal = RowOneReference(name="Bare Sandal", type="shoe", label="product")
    stories = [
        _story(
            "story-a-1234567890",
            "The Row opens the day",
            detail_path="details/story-a-1234567890.html",
            heat_delta=4,
            entity_refs=[the_row_brand],
            product_refs=[margaux],
        ),
        _story(
            "story-b-1234567890",
            "The Row product context",
            detail_path="details/story-b-1234567890.html",
            heat_delta=8,
            entity_refs=[the_row_label],
            product_refs=[sandal],
        ),
    ]

    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "story-a-1234567890": _article(
                "story-a-1234567890",
                source_name="Vogue Business",
                paragraphs=["The Row appears with Margaux in a saved article."],
            ),
            "story-b-1234567890": _article(
                "story-b-1234567890",
                source_name="WWD",
                paragraphs=["The Row appears again with Bare Sandal context."],
            ),
        },
    )

    brand_watch = next(section for section in sections if section.key == "brand_watch")
    assert brand_watch.items[0].title.en == "The Row"
    assert brand_watch.items[0].story_count == 2
    assert brand_watch.items[0].article_count == 2
    assert brand_watch.items[0].heat_delta == 8
    assert brand_watch.items[0].source_names == ["Vogue Business", "WWD"]
    assert brand_watch.items[0].references[0].name == "The Row"
    assert brand_watch.items[0].body.en == (
        "The Row appears with Margaux in a saved article. Sources: Vogue Business, WWD."
    )

    product_watch = next(section for section in sections if section.key == "product_watch")
    assert [item.title.en for item in product_watch.items] == ["Bare Sandal", "Margaux"]
```

- [ ] **Step 4: Add RED test for fallbacks and empty result**

```python
def test_build_row_one_local_article_intelligence_falls_back_to_paragraphs_and_omits_empty() -> None:
    story = _story(
        "story-a-1234567890",
        "Saved article without structured sections",
        detail_path="details/story-a-1234567890.html",
    )

    sections = build_row_one_local_article_intelligence(
        _edition([story]),
        {
            "story-a-1234567890": RowOneLocalArticle(
                story_id="story-a-1234567890",
                url="https://example.com/article",
                source_name="Source",
                extracted_at=AS_OF,
                paragraphs=["Fallback paragraph is still publishable locally."],
            )
        },
    )

    assert [section.key for section in sections] == ["strongest_reads"]
    assert sections[0].items[0].body.en == "Fallback paragraph is still publishable locally."

    assert build_row_one_local_article_intelligence(_edition([story]), {}) == []
```

- [ ] **Step 5: Run RED tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py -q
```

Expected: fails because `fashion_radar.row_one.local_intelligence` and the new model types do not exist yet.

## Task 3: GREEN Local Intelligence Models And Builder

- [ ] **Step 1: Add model types in `src/fashion_radar/row_one/models.py`**

Add after `RowOneLocalArticleContentKey`:

```python
RowOneDailyLocalIntelligenceKey = Literal[
    "strongest_reads",
    "brand_watch",
    "product_watch",
    "heat_movers",
]
```

Add after `RowOneLocalArticleContentSection`:

```python
class RowOneDailyLocalIntelligenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: LocalizedText
    body: LocalizedText
    detail_path: str | None = None
    source_name: str | None = None
    source_names: list[str] = Field(default_factory=list)
    story_count: int = 0
    article_count: int = 0
    evidence_count: int = 0
    heat_delta: int | None = None
    references: list[RowOneReference] = Field(default_factory=list)
    paragraph_indices: list[int] = Field(default_factory=list)


class RowOneDailyLocalIntelligenceSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: RowOneDailyLocalIntelligenceKey
    title: LocalizedText
    dek: LocalizedText
    items: list[RowOneDailyLocalIntelligenceItem] = Field(default_factory=list)
```

- [ ] **Step 2: Create `src/fashion_radar/row_one/local_intelligence.py`**

Implement:

```python
from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)

MAX_STRONGEST_READS = 4
MAX_REFERENCE_ITEMS = 6
MAX_HEAT_MOVERS = 5
```

Required public API:

```python
def build_row_one_local_article_intelligence(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> list[RowOneDailyLocalIntelligenceSection]:
    ...
```

Required behavior:
- Include only stories present in `edition.stories`.
- Include only local articles with non-empty `paragraphs`.
- Use `article.content_sections[*].key == "takeaways"` first for strongest reads.
- Fallback to the first non-empty paragraph when no takeaway item body exists.
- For entity/product aggregate bodies, prefer a saved takeaway or paragraph whose `paragraph_indices` match the reference item; otherwise use the article takeaway/first paragraph.
- Compose aggregate entity/product `body.en` as `"{chosen_source_text} Sources: {source_names}."` and `body.zh` as `"{chosen_source_text_zh} 来源：{source_names}。"`, with `source_names` deduplicated in first-seen order.
- Add `#local-article` to safe detail paths.
- Aggregate refs case-insensitively while preserving the first display name.
- Deduplicate sources and references.
- Sort aggregated refs by `story_count desc`, `article_count desc`, `heat_delta desc`, `name asc`.
- Sort heat movers by `heat_delta desc`, `evidence_count desc`, `headline asc`.
- `heat_movers` includes only stories that have `heat_delta > 0` and a saved local article with non-empty `paragraphs`.
- Omit sections with no items.

- [ ] **Step 3: Run GREEN builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py -q
```

Expected: all tests in the new file pass.

## Task 4: RED Render And Artifact Tests

- [ ] **Step 1: Add render tests to `tests/test_row_one_render.py`**

Add a focused helper near the existing local article tests if needed:

```python
def _local_article_for_daily_intelligence() -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        title="The Row local source",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["The Row and Margaux are moving in saved local coverage."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Saved Article Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="段落 1", en="Paragraph 1"),
                        body=LocalizedText(
                            zh="The Row 与 Margaux 的本地来源信号。",
                            en="The Row and Margaux are moving in saved local coverage.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            )
        ],
    )
```

Add:

```python
def test_render_row_one_site_includes_daily_local_intelligence(tmp_path: Path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    story.heat_delta = 6

    result = render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _local_article_for_daily_intelligence()},
    )

    html = result.index_path.read_text(encoding="utf-8")
    assert "daily-local-intelligence" in html
    assert '<span data-lang="en">Daily Local Intelligence</span>' in html
    assert '<span data-lang="zh">每日本地情报</span>' in html
    assert "The Row and Margaux are moving in saved local coverage." in html
    assert 'href="details/the-row-signal-1234567890.html#local-article"' in html

    artifact = json.loads((tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8"))
    assert [section["key"] for section in artifact] == [
        "strongest_reads",
        "brand_watch",
        "product_watch",
        "heat_movers",
    ]
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    assert "local_article_intelligence" not in payload
```

Add:

```python
def test_render_row_one_site_omits_daily_local_intelligence_without_saved_articles(tmp_path: Path) -> None:
    result = render_row_one_site(_edition(), tmp_path)

    html = result.index_path.read_text(encoding="utf-8")
    assert "daily-local-intelligence" not in html
    assert not (tmp_path / "data" / "local-intelligence.json").exists()
```

Add:

```python
def test_render_row_one_site_escapes_daily_local_intelligence(tmp_path: Path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.headline = '<script>alert("headline")</script>'
    story.entity_refs = [RowOneReference(name="<The Row>", type="brand", label="tracked")]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={
            story.id: RowOneLocalArticle(
                story_id=story.id,
                url="https://example.com/the-row",
                source_name="<Vogue>",
                extracted_at=AS_OF,
                paragraphs=['<script>alert("body")</script>'],
            )
        },
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert '<script>alert("body")</script>' not in html
    assert "&lt;script&gt;alert(&quot;body&quot;)&lt;/script&gt;" in html
    assert "&lt;The Row&gt;" in html
```

- [ ] **Step 2: Run RED render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: new render tests fail because the renderer does not yet pass or write local intelligence and the template does not render the section.

## Task 5: GREEN Render, Template, CSS, And Artifact

- [ ] **Step 1: Modify `src/fashion_radar/row_one/render.py`**

Required changes:
- Import `build_row_one_local_article_intelligence`.
- Build `local_article_intelligence` after `local_articles_by_story_id = local_articles_by_story_id or {}`.
- Pass `local_article_intelligence=local_article_intelligence` into `render_index_html`.
- Add `_write_local_article_intelligence_file(data_dir, local_article_intelligence)`.
- Call it after `_write_local_article_files(...)`.

Expected helper shape:

```python
def _write_local_article_intelligence_file(
    data_dir: Path,
    sections: Sequence[RowOneDailyLocalIntelligenceSection],
) -> None:
    writable_sections = [section for section in sections if section.items]
    if not writable_sections:
        return
    (data_dir / "local-intelligence.json").write_text(
        json.dumps(
            [section.model_dump(mode="json") for section in writable_sections],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
```

- [ ] **Step 2: Modify `src/fashion_radar/row_one/templates.py`**

Required changes:
- Add `local_article_intelligence: Sequence[RowOneDailyLocalIntelligenceSection] | None = None` to `render_index_html`.
- Render `{daily_local_intelligence}` after `{signal_synthesis}`.
- Add helpers:
  - `_render_daily_local_intelligence(sections)`
  - `_render_daily_local_intelligence_section(section)`
  - `_render_daily_local_intelligence_item(item)`
  - `_daily_local_intelligence_meta(item)`
- Add `_safe_daily_local_intelligence_href(href)` that accepts normal detail paths through `_validated_detail_relative_path(...)` and also accepts the exact `#local-article` fragment after a valid `.html` detail path. It must reject every other fragment and every unsafe path.
- Escape all item title/body/meta values with `_esc`.
- Render meta fields deterministically: article count, story count, evidence count, positive heat delta when present, and comma-joined `source_names`.

- [ ] **Step 3: Add CSS in `row_one_css()`**

Add selectors:

```css
.daily-local-intelligence
.daily-local-intelligence-header
.daily-local-intelligence-grid
.daily-local-intelligence-group
.daily-local-intelligence-group-title
.daily-local-intelligence-card
.daily-local-intelligence-card h3
.daily-local-intelligence-card p
.daily-local-intelligence-meta
```

Keep the style restrained and consistent with existing `.signal-synthesis` and `.edition-brief` blocks.

- [ ] **Step 4: Run GREEN render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py tests/test_row_one_render.py -q
```

Expected: new builder and render tests pass.

## Task 6: Documentation And Contract Guards

- [ ] **Step 1: Add a docs test in `tests/test_row_one_docs.py`**

Add a test that reads `README.md` and expects:

```python
def test_row_one_docs_describe_daily_local_intelligence() -> None:
    readme = _normalized(_read(README))

    assert "daily local intelligence" in readme
    assert "data/local-intelligence.json" in readme
    assert "row-one-app/v7 remains stable" in readme
```

- [ ] **Step 2: Update `README.md`**

Add a short ROW ONE note explaining:
- Saved local articles can now power a homepage Daily Local Intelligence section.
- `data/local-intelligence.json` is a generated site artifact.
- `row-one-app/v7` remains stable; the app payload does not include this field.

- [ ] **Step 3: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: docs tests pass.

## Task 7: Review, Verification, Rebuild, Commit, Push

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_local_intelligence.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  -q
```

Expected: focused tests pass.

- [ ] **Step 2: Full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Rebuild generated ROW ONE site**

Run:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one refresh \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --output-dir reports/row-one/site \
  --as-of "$AS_OF"
```

Expected proof:
- `reports/row-one/site/index.html` exists.
- `reports/row-one/site/data/local-intelligence.json` exists when saved local articles are present.
- `reports/row-one/site/index.html` contains `daily-local-intelligence`.
- `reports/row-one/site/data/edition.json` does not contain `local_article_intelligence`.

- [ ] **Step 4: Code review**

Create:
- `docs/reviews/claude-code-stage-301-code-review-prompt.md`
- `docs/reviews/opencode-stage-301-code-review-prompt.md`

Attempt Claude Code review with `--effort max`. If unavailable, record `Verdict: UNAVAILABLE`. Run opencode fallback with GLM 5.2 max. Fix Critical/Important findings, then rerun affected tests and full verification as needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/models.py \
  src/fashion_radar/row_one/local_intelligence.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_local_intelligence.py \
  tests/test_row_one_render.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/superpowers/plans/2026-07-05-stage-301-row-one-daily-local-intelligence-plan.md \
  docs/reviews/claude-code-stage-301-plan-review-prompt.md \
  docs/reviews/claude-code-stage-301-plan-review.md \
  docs/reviews/opencode-stage-301-plan-review-prompt.md \
  docs/reviews/opencode-stage-301-plan-review.md \
  docs/reviews/claude-code-stage-301-code-review-prompt.md \
  docs/reviews/claude-code-stage-301-code-review.md \
  docs/reviews/opencode-stage-301-code-review-prompt.md \
  docs/reviews/opencode-stage-301-code-review.md
git commit -m "Stage 301: add row one daily local intelligence"
git push origin main
```

Expected: clean push to `origin/main`.

## Self-Review

- Spec coverage: The plan addresses the user's current priority: locally published/organized content, not just links. It adds a daily homepage intelligence layer, local generated JSON artifact, tests, docs, review gates, and verification.
- Placeholder scan: No `TBD`, `TODO`, or unspecified implementation-only steps remain. The generated site rebuild command is pinned to the current documented `row-one refresh` path and run through the project's `UV_NO_CONFIG=1 uv --no-config run --frozen` verification convention.
- Type consistency: `RowOneDailyLocalIntelligence*` names are used consistently across models, builder, renderer, template, tests, and artifact writing.
