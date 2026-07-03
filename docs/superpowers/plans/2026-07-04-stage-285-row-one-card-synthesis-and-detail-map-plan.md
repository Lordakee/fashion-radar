# Stage 285 ROW ONE Card Synthesis And Detail Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE's app cards and story detail pages expose more organized information from existing deterministic story fields, so the tool presents usable intelligence rather than mostly links.

**Architecture:** Keep the stage narrow and additive. First, enrich existing `contentCard` payloads with the already-generated `why_it_matters` and `signal_context` fields so every app card in `content_sections`, `daily_digest.blocks`, and `daily_digest.briefing_topics` contains the same core story synthesis as the full story payload. Second, add a detail-page `detail-information-map` rendered from existing `RowOneStory` fields to summarize context, signal shape, evidence, and read order before the linear article sections. Do not add new model fields, source collection, inference, LLM generation, ranking changes, or app contract version changes.

**Tech Stack:** Python 3.11+, JSON Schema draft 2020-12, static HTML/CSS/vanilla JS, pytest, ruff, uv.

---

## Files

- Modify: `src/fashion_radar/row_one/render.py`
  - Add `why_it_matters` and `signal_context` to `_content_card_payload`.
- Modify: `schemas/row-one-app.schema.json`
  - Add required `why_it_matters` and `signal_context` fields to `$defs.contentCard`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Add `_render_detail_information_map(story, section_title)`.
  - Insert it after article contents and before the existing summary section.
  - Add scoped CSS for `.detail-information-map`.
- Modify: `tests/test_row_one_app_contract.py`
  - Assert content cards, digest cards, and briefing topic cards carry `why_it_matters` and `signal_context`.
  - Add schema drift checks for missing required card synthesis fields.
- Modify: `tests/test_row_one_render.py`
  - Assert JSON card payloads include the two synthesis fields.
  - Assert detail HTML renders the detail information map in the correct position and escapes content.
- Modify: `tests/test_row_one_docs.py`
  - Add documentation guards for card synthesis and detail information map.
- Modify: `docs/row-one.md`
  - Document the additive app-card synthesis fields and detail-page information map.
- Modify: `README.md`
  - Update the ROW ONE app contract summary to mention card synthesis and detail information map.
- Add: `docs/reviews/claude-code-stage-285-plan-review-prompt.md`
- Add after review: `docs/reviews/claude-code-stage-285-plan-review.md`
- Add after review fallback if Claude Code auth is unavailable: `docs/reviews/opencode-stage-285-plan-review.md`
- Add after implementation: `docs/reviews/claude-code-stage-285-code-review-prompt.md`
- Add after implementation: `docs/reviews/claude-code-stage-285-code-review.md`

## Task 1: Add App Card Tests

**Files:**
- Modify: `tests/test_row_one_app_contract.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Extend daily digest card assertions**

In `tests/test_row_one_app_contract.py`, inside `test_row_one_app_payload_includes_daily_digest_for_clients`, after the existing `blocks["read_first"]["cards"]` assertion, add:

```python
    read_first_card = blocks["read_first"]["cards"][0]
    assert read_first_card["why_it_matters"] == stories[0]["why_it_matters"]
    assert read_first_card["signal_context"] == stories[0]["signal_context"]
```

- [ ] **Step 2: Extend content section card assertions**

In `test_row_one_app_payload_groups_content_sections_for_clients`, inside the loop and after the card id assertion, add:

```python
        for card, story in zip(content_section["cards"], section_stories, strict=True):
            assert card["why_it_matters"] == story["why_it_matters"]
            assert card["signal_context"] == story["signal_context"]
```

- [ ] **Step 3: Extend briefing topic card assertions**

In `test_row_one_app_daily_digest_includes_briefing_topics_for_clients`, inside the `for topic in topics` loop, after the existing cards/story_ids assertion, add:

```python
        topic_stories = [story for story in payload["stories"] if story["id"] in topic["story_ids"]]
        for card, story in zip(topic["cards"], topic_stories, strict=True):
            assert card["why_it_matters"] == story["why_it_matters"]
            assert card["signal_context"] == story["signal_context"]
```

- [ ] **Step 4: Extend render JSON payload assertions**

In `tests/test_row_one_render.py`, inside `test_render_row_one_site_writes_json_payload`, after the story_directory assertions, add:

```python
    content_card = payload["content_sections"][0]["cards"][0]
    digest_card = payload["daily_digest"]["blocks"][0]["cards"][0]
    assert content_card["why_it_matters"] == story["why_it_matters"]
    assert content_card["signal_context"] == story["signal_context"]
    assert digest_card["why_it_matters"] == story["why_it_matters"]
    assert digest_card["signal_context"] == story["signal_context"]
```

- [ ] **Step 5: Extend exact card mirror assertion**

In `test_row_one_app_content_cards_mirror_story_display_fields`, add the new card
fields to the exact expected dict after `summary`:

```python
        "why_it_matters": story["why_it_matters"],
        "signal_context": story["signal_context"],
```

- [ ] **Step 6: Run RED card tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_groups_content_sections_for_clients \
  tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_daily_digest_for_clients \
  tests/test_row_one_app_contract.py::test_row_one_app_daily_digest_includes_briefing_topics_for_clients \
  tests/test_row_one_app_contract.py::test_row_one_app_content_cards_mirror_story_display_fields \
  tests/test_row_one_render.py::test_render_row_one_site_writes_json_payload \
  -q
```

Expected: assertions fail because content cards do not yet include `why_it_matters` and `signal_context`.

## Task 2: Implement App Card Synthesis Fields

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `schemas/row-one-app.schema.json`

- [ ] **Step 1: Update `_content_card_payload`**

In `src/fashion_radar/row_one/render.py`, add two fields after `summary`:

```python
        "why_it_matters": story["why_it_matters"],
        "signal_context": story["signal_context"],
```

- [ ] **Step 2: Update schema `contentCard.required`**

In `schemas/row-one-app.schema.json`, add these required fields to `$defs.contentCard.required` after `"summary"`:

```json
"why_it_matters",
"signal_context",
```

- [ ] **Step 3: Update schema `contentCard.properties`**

In `$defs.contentCard.properties`, add:

```json
"why_it_matters": {
  "$ref": "#/$defs/localizedText"
},
"signal_context": {
  "$ref": "#/$defs/localizedText"
},
```

- [ ] **Step 4: Validate JSON schema syntax**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
```

Expected: exit 0.

- [ ] **Step 5: Run GREEN card tests**

Run the RED command from Task 1 again.

Expected: selected tests pass and schema validation inside app contract tests passes.

## Task 3: Add Detail Information Map Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add detail information map render test**

Add near the existing detail page tests:

```python
def test_render_row_one_detail_includes_information_map(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )

    assert 'class="detail-information-map"' in detail_html
    assert "Detail Information Map" in detail_html
    assert "详情信息地图" in detail_html
    assert "Story Context" in detail_html
    assert "Signal Shape" in detail_html
    assert "Evidence" in detail_html
    assert "Read Order" in detail_html
    assert "Top Stories" in detail_html
    assert "Vogue Business" in detail_html
    assert "2026-07-02" in detail_html
    assert "1 evidence link" in detail_html
    assert "brand" in detail_html
    assert 'href="#summary"' in detail_html
    assert 'href="#why-it-matters"' in detail_html
    assert 'href="#signal-context"' in detail_html
    assert 'href="#evidence-trail"' in detail_html
    assert detail_html.index('class="article-contents"') < detail_html.index(
        'class="detail-information-map"'
    )
    assert detail_html.index('class="detail-information-map"') < detail_html.index('id="summary"')
```

- [ ] **Step 2: Add detail information map escaping test**

Add:

```python
def test_render_row_one_detail_information_map_escapes_story_values(tmp_path) -> None:
    edition = _edition()
    edition.stories[0].source_name = "Vogue <signals> Business"
    render_row_one_site(edition, tmp_path)

    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text(
        encoding="utf-8"
    )
    map_match = re.search(
        r'<section class="detail-information-map"(?P<map>.*?)</section>',
        detail_html,
        re.S,
    )

    assert map_match is not None
    map_html = map_match.group("map")
    assert "Vogue &lt;signals&gt; Business" in map_html
    assert "Vogue <signals> Business" not in map_html
```

- [ ] **Step 3: Run RED detail tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_information_map \
  tests/test_row_one_render.py::test_render_row_one_detail_information_map_escapes_story_values \
  -q
```

Expected: missing information map assertions fail.

## Task 4: Implement Detail Information Map

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add tag/type formatting helpers**

Add helper functions near other template helpers:

```python
def _story_type_label(story: RowOneStory) -> str:
    return story.story_type.replace("_", " ").title()


def _joined_tags(story: RowOneStory) -> str:
    return ", ".join(story.tags) if story.tags else "No tags"
```

Reuse the existing `_published_label(story)` helper for published-date display.
If `_safe_evidence_count` is added to `templates.py`, keep it as an intentional
small duplicate of the private render helper so templates do not import private
symbols from `render.py`.

- [ ] **Step 2: Add `_render_detail_information_map`**

Add:

```python
def _render_detail_information_map(story: RowOneStory, section_title: LocalizedText) -> str:
    published = _published_label(story)
    safe_evidence_count = _safe_evidence_count(story.evidence)
    evidence_label_en = (
        f"{safe_evidence_count} evidence link"
        if safe_evidence_count == 1
        else f"{safe_evidence_count} evidence links"
    )
    evidence_label_zh = f"{safe_evidence_count} 条线索"
    heat_delta = f"{story.heat_delta:+d}" if isinstance(story.heat_delta, int) else "n/a"
    return f"""<section class="detail-information-map" aria-label="Detail information map">
  <div class="detail-information-map-header">
    <p><span data-lang="en">Structured story scan</span><span data-lang="zh">结构化故事速览</span></p>
    <h2><span data-lang="en">Detail Information Map</span><span data-lang="zh">详情信息地图</span></h2>
  </div>
  <div class="detail-information-map-grid">
    <article class="detail-information-map-card">
      <h3><span data-lang="en">Story Context</span><span data-lang="zh">故事背景</span></h3>
      <p><span data-lang="en">{_esc(section_title.en)}</span><span data-lang="zh">{_esc(section_title.zh)}</span></p>
      <p>{_esc(story.source_name)}</p>
      <p><span data-lang="en">{_esc(published.en)}</span><span data-lang="zh">{_esc(published.zh)}</span></p>
    </article>
    <article class="detail-information-map-card">
      <h3><span data-lang="en">Signal Shape</span><span data-lang="zh">信号形态</span></h3>
      <p>{_esc(_story_type_label(story))}</p>
      <p>{_esc(_joined_tags(story))}</p>
      <p><span data-lang="en">Heat delta</span><span data-lang="zh">热度变化</span>: {_esc(heat_delta)}</p>
    </article>
    <article class="detail-information-map-card">
      <h3><span data-lang="en">Evidence</span><span data-lang="zh">证据</span></h3>
      <p><span data-lang="en">{_esc(evidence_label_en)}</span><span data-lang="zh">{_esc(evidence_label_zh)}</span></p>
      <p>{_esc(story.source_name)}</p>
    </article>
    <article class="detail-information-map-card">
      <h3><span data-lang="en">Read Order</span><span data-lang="zh">阅读顺序</span></h3>
      <p><a href="#summary"><span data-lang="en">Summary</span><span data-lang="zh">摘要</span></a></p>
      <p><a href="#why-it-matters"><span data-lang="en">Why It Matters</span><span data-lang="zh">为什么重要</span></a></p>
      <p><a href="#signal-context"><span data-lang="en">Signal Context</span><span data-lang="zh">信号背景</span></a></p>
      <p><a href="#evidence-trail"><span data-lang="en">Evidence Trail</span><span data-lang="zh">来源线索</span></a></p>
    </article>
  </div>
</section>"""
```

Add this local helper in `templates.py`:

```python
def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if safe_external_url(link.url) is not None)
```

- [ ] **Step 3: Insert map into detail page**

In `render_detail_html`, compute:

```python
    detail_information_map = _render_detail_information_map(story, section_title)
```

Then render `{detail_information_map}` after `{article_contents}` and before `<section id="summary">`.

- [ ] **Step 4: Add CSS**

In `row_one_css()`, add:

```css
.detail-information-map {
  border: 1px solid var(--ink);
  background: var(--panel);
  margin: 28px 0;
  padding: 20px;
}
.detail-information-map-header {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}
.detail-information-map-header p,
.detail-information-map-header h2 {
  margin: 0;
}
.detail-information-map-header p {
  color: var(--muted);
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0;
}
.detail-information-map-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1px;
  background: var(--line);
}
.detail-information-map-card {
  background: var(--panel);
  padding: 14px;
  display: grid;
  gap: 8px;
}
.detail-information-map-card h3,
.detail-information-map-card p {
  margin: 0;
}
.detail-information-map-card h3 {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0;
}
.detail-information-map-card p {
  color: var(--muted);
  font-size: 0.9rem;
}
```

- [ ] **Step 5: Run GREEN detail tests**

Run the RED command from Task 3 again.

Expected: selected tests pass.

## Task 5: Add Schema Drift And Docs

**Files:**
- Modify: `tests/test_row_one_app_contract.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `docs/row-one.md`
- Modify: `README.md`

- [ ] **Step 1: Add schema drift cases**

In the existing contract drift parametrization, add:

```python
(
    lambda payload: payload["content_sections"][0]["cards"][0].pop("why_it_matters"),
    "'why_it_matters' is a required property",
),
(
    lambda payload: payload["content_sections"][0]["cards"][0].pop("signal_context"),
    "'signal_context' is a required property",
),
```

- [ ] **Step 2: Add docs test**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_card_synthesis_and_detail_information_map() -> None:
    normalized = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "why_it_matters",
        "signal_context",
        "detail information map",
        "derived from existing row one story data",
        "links only to existing detail-page anchors",
        "does not change collection, matching, scoring, ranking, or story ids",
    ):
        assert phrase in normalized

    for phrase in (
        "why_it_matters",
        "signal_context",
        "detail information map",
    ):
        assert phrase in readme
```

- [ ] **Step 3: Update ROW ONE docs**

In `docs/row-one.md`, in the App JSON Contract section, add:

```markdown
App cards in `content_sections`, `daily_digest.blocks`, and
`daily_digest.briefing_topics` include the existing `why_it_matters` and
`signal_context` story synthesis fields, so clients can render organized story
cards without opening the full story object first. The detail page also renders
a Detail Information Map derived from existing ROW ONE story data: section,
source, date, story type, tags, heat delta, evidence count, and links only to
existing detail-page anchors. This does not change collection, matching,
scoring, ranking, or story IDs.
```

- [ ] **Step 4: Update README**

In the ROW ONE bullet and non-goal paragraph, add concise wording:

```markdown
App cards now carry `why_it_matters` and `signal_context`, and detail pages show
a Detail Information Map from existing story fields.
```

- [ ] **Step 5: Run docs and app contract tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run pytest tests/test_row_one_docs.py tests/test_row_one_app_contract.py -q
```

Expected: selected tests pass.

## Task 6: Verify, Review, Commit, And Push

**Files:**
- Add: `docs/reviews/claude-code-stage-285-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-285-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run python -m json.tool schemas/row-one-app.schema.json >/dev/null
UV_NO_CONFIG=1 uv --no-config run pytest \
  tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py \
  -q
```

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run ruff check .
UV_NO_CONFIG=1 uv --no-config run ruff format --check .
UV_NO_CONFIG=1 uv --no-config run pytest -q
UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-285-code-review-prompt.md` with objective, constraints, changed files, diff stat, and verification evidence. Run:

```bash
claude -p --effort max --tools none --no-session-persistence "$(cat docs/reviews/claude-code-stage-285-code-review-prompt.md)" \
  > /tmp/claude-code-stage-285-code-review.md
cp /tmp/claude-code-stage-285-code-review.md docs/reviews/claude-code-stage-285-code-review.md
```

Fix Critical and Important findings before committing.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py \
  schemas/row-one-app.schema.json \
  tests/test_row_one_app_contract.py tests/test_row_one_render.py tests/test_row_one_docs.py \
  docs/row-one.md README.md \
  docs/superpowers/plans/2026-07-04-stage-285-row-one-card-synthesis-and-detail-map-plan.md \
  docs/reviews/claude-code-stage-285-plan-review-prompt.md \
  docs/reviews/claude-code-stage-285-plan-review.md \
  docs/reviews/opencode-stage-285-plan-review.md \
  docs/reviews/claude-code-stage-285-code-review-prompt.md \
  docs/reviews/claude-code-stage-285-code-review.md
git commit -m "Stage 285: add row one card synthesis and detail map"
git push origin main
```

- [ ] **Step 5: Handoff Summary**

Report:

- Repo status
- Verified commands
- Uncommitted files
- Next step

## Self-Review

- Spec coverage: App cards expose existing synthesis fields and detail pages gain a structured information map.
- Boundary check: No source collection, social connectors, browser automation, LLM calls, image generation, scoring, matching, ranking, or story ID changes.
- Contract safety: Additive fields are added to `contentCard` and schema because `additionalProperties: false` requires it.
- Test coverage: App cards, digest cards, briefing topic cards, schema drift, detail rendering, docs, focused/full verification.
