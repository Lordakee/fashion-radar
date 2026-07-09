# Stage 378 Saved Local Article Related Read Lanes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Organize the existing post-body Saved Local Article Related Reads on `articles/<story-id>.html` into deterministic lanes so readers see whether each same-site next read is tied by shared signal, same ROW ONE section, or same source.

**Architecture:** Add a pure lane view-model helper derived from the already-built Stage 377 related-read cards, without adding any field to `RowOneSavedArticleLocalRelatedReads`. The grouping consumes only the card `reason`, `candidate_story_id`, source labels, references, and hrefs that Stage 377 already produced; it does not add fetching, ranking, scoring, source matching, new artifacts, route families, schemas, or app/runtime/manifest contract fields. Rendering computes lanes inside the existing post-body `saved-article-local-related-reads` section from cards that pass the existing template href guard. If any renderable card cannot be classified into one of the three lane keys, the entire section falls back to the current flat card grid so reason-copy drift cannot silently remove cards from output.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, existing `templates.py` HTML helper style, pytest, ruff, uv with frozen `--no-config` commands.

---

## Product Gap

Stage 377 added same-site next reads after each saved local article body, but the cards are still a flat list. That helps a reader continue, yet it does not visibly organize why the next reads matter. Stage 378 closes that content-organization gap in the collect -> match -> report pipeline by turning the existing cards into a small article-backed lane structure: shared signals first, then same section, then same source. The feature remains generated-site-only and keeps all source attribution and saved local article content inside already generated local article pages.

## File Map

- Modify `src/fashion_radar/row_one/saved_article_local_related_reads.py`
  - Add `RowOneSavedArticleLocalRelatedReadLane`.
  - Keep `RowOneSavedArticleLocalRelatedReads` unchanged; do not add a `lanes` field.
  - Add `build_row_one_saved_article_local_related_read_lanes(...)` as a pure grouping helper that consumes already-built related-read cards at render time.
  - Classify cards by existing reason text prefixes:
    - `Shared signal:` / `共同信号：` -> `shared_signal`
    - `Same ROW ONE section` / `同一 ROW ONE 栏目` -> `same_section`
    - `Same source desk` / `同一来源` -> `same_source`
  - Preserve original card order within each lane, dedupe by `candidate_story_id + href`, and cap cards per lane.
  - Do not add another href validation layer in the builder helper; the Stage 377 builder already creates safe sibling hrefs and `_render_saved_article_local_related_read_card(...)` remains the final render-time guard for direct fixture or future caller mistakes.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import `RowOneSavedArticleLocalRelatedReadLane` and `build_row_one_saved_article_local_related_read_lanes`.
  - Compute and render lane markup inside the existing `saved-article-local-related-reads` section only when every renderable card is represented in a lane.
  - Keep `_render_saved_article_local_related_read_card(...)` as the single card renderer so lane cards retain the same href validation and escaping.
  - Preserve the flat `.saved-article-local-related-reads-grid` fallback when lane rendering is empty or incomplete.
  - Add CSS selectors for the lane layout.
- Modify `tests/test_row_one_saved_article_local_related_reads.py`
  - Add TDD tests for lane ordering, card order preservation, dedupe, unknown-reason omission, and empty input.
- Modify `tests/test_row_one_render.py`
  - Add render tests for lane markup placement inside the existing section, fallback behavior for empty lanes, no leakage to homepage/library/detail pages, and CSS selectors.
- Modify `tests/test_workflows.py`
  - Add Stage 378 contract/artifact denylist checks for lane names.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 378 documentation boundary test above Stage 377.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 378 paragraph documenting the generated-site-only boundary.
- Create review records under `docs/reviews/` during plan and code review.

## Acceptance Criteria

- Existing Stage 377 related-read cards remain available and safe when lane grouping is empty.
- Lanes render in deterministic order: shared signal, same ROW ONE section, same source.
- Cards preserve Stage 377 ordering within each lane and retain their existing excerpts, references, action copy, and safe sibling hrefs.
- Unsafe or mismatched related-read hrefs never render in lanes because lane rendering delegates each card to the existing safe card renderer.
- If any otherwise renderable related-read card has an unclassified reason, the existing flat grid renders instead of dropping that card.
- No new JSON artifact, standalone HTML page, route family, schema field, app/runtime/manifest key, source collection behavior, fetching behavior, matching behavior, extraction behavior, scoring behavior, ranking behavior, LLM behavior, connector behavior, scheduling behavior, analytics behavior, personalization behavior, recommendation behavior, or compliance-review product feature is added.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-378-plan-review.md`
- Create: `docs/reviews/opencode-stage-378-plan-review.md`
- Modify if needed: `docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 378 Saved Local Article Related Read Lanes plan in /home/ubuntu/fashion-radar. Read docs/REVIEW_PROTOCOL.md, AGENTS.md, docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around _render_saved_article_local_related_reads, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py around existing related-read tests, tests/test_workflows.py contract denylist, and tests/test_row_one_docs.py Stage 377 docs test. Goal: add generated-site-only lanes inside the existing post-body Saved Local Article Related Reads section, consuming only Stage 377 related-read cards and their existing reason/source/reference/href fields. Technical stack: Python dataclasses, existing ROW ONE models, templates.py, pytest, ruff, uv. Implementation method: pure lane grouping helper, no new RowOneSavedArticleLocalRelatedReads field, renderer computes lanes from existing cards and uses existing safe card renderer, docs/workflow boundary assertions. Check feasibility, duplication risk, href safety, generated-site-only boundaries, whether reason-prefix lane classification is acceptable, tests, and docs. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-378-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body ending with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 378 Saved Local Article Related Read Lanes plan. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-378-plan-review.md if present, docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around _render_saved_article_local_related_reads, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py around related-read tests, tests/test_workflows.py, and tests/test_row_one_docs.py. Check feasibility, compatibility, safe sibling href handling, generated-site-only boundaries, test coverage, docs boundaries, and whether this duplicates existing ROW ONE sections. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-378-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update this plan and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 378 Saved Local Article Related Read Lanes plan after fixes. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-378-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 378 Saved Local Article Related Read Lanes plan after fixes. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-378-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Modify: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Add failing lane ordering test**

Append a test that expects the new helper to group existing cards:

```python
def test_saved_article_local_related_reads_groups_cards_into_lanes() -> None:
    current = _story("current-row-0000000000", section_key="top_stories")
    shared = _story("shared-row-1111111111", headline="Shared The Row signal", source_name="WWD")
    same_section = _story(
        "same-section-2222222222",
        headline="Same section read",
        source_name="Harper's Bazaar",
    )
    same_source = _story(
        "same-source-3333333333",
        headline="Same source read",
        section_key="brand_moves",
    )
    articles = {
        current.id: _article(
            current.id,
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
            ],
        ),
        shared.id: _article(
            shared.id,
            source_name=shared.source_name,
            content_sections=[
                _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
        same_section.id: _article(same_section.id, source_name=same_section.source_name),
        same_source.id: _article(same_source.id, source_name=same_source.source_name),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared, same_section, same_source),
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, shared, same_section, same_source),
    )

    assert related is not None
    lanes = build_row_one_saved_article_local_related_read_lanes(related.cards)

    assert [lane.key for lane in lanes] == [
        "shared_signal",
        "same_section",
        "same_source",
    ]
    assert [lane.cards[0].candidate_story_id for lane in lanes] == [
        shared.id,
        same_section.id,
        same_source.id,
    ]
    assert lanes[0].title.en == "Shared signals"
    assert lanes[0].dek.en == "Next reads carrying the same named fashion signal."
    assert lanes[1].title.en == "Same ROW ONE section"
    assert lanes[1].dek.en == "Next reads filed near this story in today's edition."
    assert lanes[2].title.en == "Same source desk"
    assert lanes[2].dek.en == "Next reads from the same saved local source context."
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py::test_saved_article_local_related_reads_groups_cards_into_lanes -q
```

Expected: FAIL because `build_row_one_saved_article_local_related_read_lanes` does not exist yet.

- [ ] **Step 3: Add failing grouping helper edge test**

Append a test for dedupe and unknown-reason omission using direct card fixtures:

```python
def test_saved_article_local_related_read_lanes_dedupe_and_omit_unknown_reasons() -> None:
    safe_card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="safe-row-1111111111",
        title=_text("Safe read"),
        source_name="WWD",
        reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
        excerpt=_text("Saved excerpt"),
        href="safe-row-1111111111.html#local-article-paragraph-1",
        references=(RowOneSavedArticleLocalRelatedReadReference(name="The Row", label="Brand"),),
    )
    duplicate_card = replace(safe_card)
    unknown_card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="unknown-row-2222222222",
        title=_text("Unknown read"),
        source_name="WWD",
        reason=LocalizedText(en="Editorial adjacency", zh="编辑相邻"),
        excerpt=_text("Unknown excerpt"),
        href="unknown-row-2222222222.html#local-article-paragraph-1",
    )

    lanes = build_row_one_saved_article_local_related_read_lanes(
        (safe_card, duplicate_card, unknown_card)
    )

    assert len(lanes) == 1
    assert lanes[0].key == "shared_signal"
    assert [card.candidate_story_id for card in lanes[0].cards] == ["safe-row-1111111111"]
```

Update imports in the same file:

```python
from dataclasses import replace
```

and import the new helper after it exists:

```python
build_row_one_saved_article_local_related_read_lanes,
```

- [ ] **Step 4: Run edge test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py::test_saved_article_local_related_read_lanes_dedupe_and_omit_unknown_reasons -q
```

Expected: FAIL because the helper does not exist.

## Task 3: Builder Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/saved_article_local_related_reads.py`

- [ ] **Step 1: Add lane dataclass and constants**

Add:

```python
SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS_PER_LANE = 3


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneSavedArticleLocalRelatedReadCard, ...]
```

Keep `RowOneSavedArticleLocalRelatedReads` unchanged. Add `Sequence` to the existing `collections.abc` imports.

- [ ] **Step 2: Add pure lane builder**

Implement:

```python
def build_row_one_saved_article_local_related_read_lanes(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[RowOneSavedArticleLocalRelatedReadLane, ...]:
    deduped_by_lane: dict[str, list[RowOneSavedArticleLocalRelatedReadCard]] = {
        "shared_signal": [],
        "same_section": [],
        "same_source": [],
    }
    seen: set[tuple[str, str]] = set()
    for card in cards:
        dedupe_key = (card.candidate_story_id, card.href)
        if dedupe_key in seen:
            continue
        lane_key = _related_read_lane_key(card)
        if lane_key is None:
            continue
        seen.add(dedupe_key)
        if len(deduped_by_lane[lane_key]) < SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS_PER_LANE:
            deduped_by_lane[lane_key].append(card)

    lanes = [
        lane
        for key in ("shared_signal", "same_section", "same_source")
        if (lane := _related_read_lane(key, tuple(deduped_by_lane[key]))) is not None
    ]
    return tuple(lanes)
```

Add `_related_read_lane_key(...)` and `_related_read_lane(...)` with localized lane copy:

```python
def _related_read_lane_key(card: RowOneSavedArticleLocalRelatedReadCard) -> str | None:
    reason_en = normalize_row_one_paragraph(card.reason.en).casefold()
    reason_zh = normalize_row_one_paragraph(card.reason.zh)
    if reason_en.startswith("shared signal:") or reason_zh.startswith("共同信号："):
        return "shared_signal"
    if reason_en == "same row one section" or reason_zh == "同一 ROW ONE 栏目":
        return "same_section"
    if reason_en == "same source desk" or reason_zh == "同一来源":
        return "same_source"
    return None
```

Use this exact lane copy:

```python
_LANE_COPY = {
    "shared_signal": (
        LocalizedText(en="Shared signals", zh="共同信号"),
        LocalizedText(
            en="Next reads carrying the same named fashion signal.",
            zh="包含同一时尚信号的后续阅读。",
        ),
    ),
    "same_section": (
        LocalizedText(en="Same ROW ONE section", zh="同一 ROW ONE 栏目"),
        LocalizedText(
            en="Next reads filed near this story in today's edition.",
            zh="与本文同属今日相近栏目脉络的后续阅读。",
        ),
    ),
    "same_source": (
        LocalizedText(en="Same source desk", zh="同一来源台"),
        LocalizedText(
            en="Next reads from the same saved local source context.",
            zh="来自同一保存来源语境的后续阅读。",
        ),
    ),
}
```

`_related_read_lane(...)` returns `None` for empty card tuples or unknown lane keys.

- [ ] **Step 3: Run focused builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: all tests in the file pass.

## Task 4: Render RED Tests And Implementation

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add failing render test for lane markup**

Add a test near the existing related-read render tests that builds a related-read model whose cards cover shared-signal and same-section reasons, then asserts:

```python
assert 'class="saved-article-local-related-read-lanes"' in html
assert 'class="saved-article-local-related-read-lane"' in html
assert "Shared signals" in html
assert "Same ROW ONE section" in html
assert html.index('class="saved-article-local-related-read-lanes"') > html.index(
    'id="local-article"'
)
assert 'href="related-row-2222222222.html#local-article-paragraph-1"' in html
assert "articles/related-row-2222222222.html" not in html
```

Use `render_local_article_page_html(...)` so `id="local-article"` is present and the placement assertion checks the full article page.

Also add a render test with a lane-eligible card whose `href` is `articles/related-row-2222222222.html#local-article-paragraph-1`; assert the unsafe card title and link do not appear in the related-read lane body.

Add a render test with one classified card and one card using `reason=LocalizedText(en="Editorial adjacency", zh="编辑相邻")`; assert `.saved-article-local-related-read-lanes` is absent, `.saved-article-local-related-reads-grid` is present, and both safe card titles appear. This pins the no-card-loss fallback.

- [ ] **Step 2: Run render test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_local_article_page_groups_related_reads_into_lanes -q
```

Expected: FAIL because lane markup does not render yet.

- [ ] **Step 3: Implement lane rendering inside existing section**

In `_render_saved_article_local_related_reads(...)`, preserve the current initial card-rendering guard:

```python
cards = [
    card_html
    for card in related_reads.cards
    if (card_html := _render_saved_article_local_related_read_card(card))
]
if not cards:
    return ""
```

Then render lanes only from cards that pass the existing template href guard:

```python
renderable_cards = _renderable_saved_article_local_related_read_cards(related_reads.cards)
lanes = build_row_one_saved_article_local_related_read_lanes(renderable_cards)
lanes_html = _render_saved_article_local_related_read_lanes(lanes)
if _related_read_lane_card_count(lanes) != len(renderable_cards):
    lanes_html = ""
body_html = lanes_html or (
    '      <div class="saved-article-local-related-reads-grid">\n'
    + cards_html
    + "\n      </div>"
)
```

Use `body_html` in the existing section f-string where the grid currently appears; do not change the section wrapper or early return behavior.

Add:

```python
def _renderable_saved_article_local_related_read_cards(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[RowOneSavedArticleLocalRelatedReadCard, ...]:
    return tuple(
        card
        for card in cards
        if _safe_saved_article_local_related_read_href(card.candidate_story_id, card.href)
        is not None
    )


def _related_read_lane_card_count(
    lanes: Sequence[RowOneSavedArticleLocalRelatedReadLane],
) -> int:
    return sum(len(lane.cards) for lane in lanes)
```

Add helpers:

```python
def _render_saved_article_local_related_read_lanes(
    lanes: Sequence[RowOneSavedArticleLocalRelatedReadLane],
) -> str:
    rendered = [
        lane_html
        for lane in lanes
        if (lane_html := _render_saved_article_local_related_read_lane(lane))
    ]
    if not rendered:
        return ""
    return (
        '      <div class="saved-article-local-related-read-lanes">\n'
        + "\n".join(rendered)
        + "\n      </div>"
    )
```

Each lane should use `_render_saved_article_local_related_read_card(...)` for cards and omit empty lanes.

- [ ] **Step 4: Add CSS selector test and implementation**

Extend `test_row_one_css_includes_saved_article_local_related_reads_styles` with:

```python
".saved-article-local-related-read-lanes",
".saved-article-local-related-read-lane",
".saved-article-local-related-read-lane-header",
```

Add matching CSS near existing related-read styles.

- [ ] **Step 5: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: render tests pass.

## Task 5: Boundary, Docs, And Workflow Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow boundary assertions**

In the generated contract denylist test, assert these names are absent:

```python
assert "saved_article_local_related_read_lanes" not in generated_contract_payload
assert "local_article_related_read_lanes" not in generated_contract_payload
assert "related_read_lanes" not in generated_contract_payload
assert "RowOneSavedArticleLocalRelatedReadLane" not in generated_contract_payload
assert "Saved Local Article Related Read Lanes" not in generated_contract_payload
assert "saved-article-local-related-read-lanes" not in generated_contract_payload
assert "local-article-related-read-lanes" not in generated_contract_payload
assert "related-read-lanes" not in generated_contract_payload
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_row_one_site_contract_excludes_generated_site_only_surfaces -q
```

Expected: PASS after implementation keeps contracts unchanged.

Also extend the generated artifact-stem denylist loop with these kebab and snake stems:

```python
"saved-local-article-related-read-lanes",
"local-article-related-read-lanes",
"related-read-lanes",
"saved_local_article_related_read_lanes",
"local_article_related_read_lanes",
"related_read_lanes",
```

Run the existing artifact test:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_row_one_site_does_not_create_generated_site_only_artifacts -q
```

Expected: PASS and no lane JSON/HTML artifacts are created.

- [ ] **Step 2: Add docs test and paragraphs**

Add a Stage 378 docs test using this exact paragraph and assert it appears before the Stage 377 paragraph in both docs:

```text
Stage 378 adds generated-site only Saved Local Article Related Read Lanes inside the existing post-body Saved Local Article Related Reads section on `articles/<story-id>.html`; it reuses the Stage 377 same-site related-read cards, existing card reasons, existing source labels, existing reference chips, generated local article page routes, and existing paragraph anchors to organize next reads by shared signal, same ROW ONE section, and same source while preserving the current flat-card fallback; it does not create `data/saved-local-article-related-read-lanes.json`, does not create `data/local-article-related-read-lanes.json`, does not create `data/related-read-lanes.json`, does not create `saved-local-article-related-read-lanes.html`, does not create `local-article-related-read-lanes.html`, does not create `related-read-lanes.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

Insert the same paragraph in `README.md` and `docs/row-one.md` above Stage 377.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_378_saved_local_article_related_read_lanes_boundary -q
```

Expected: PASS after docs are updated.

- [ ] **Step 3: Run focused workflow/docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q
```

Expected: tests pass.

## Task 6: Code Review, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-378-code-review.md`
- Create: `docs/reviews/opencode-stage-378-code-review.md`
- Modify if needed after review: Stage 378 source/tests/docs files

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Ask Claude Code to review the code**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 378 Saved Local Article Related Read Lanes code in /home/ubuntu/fashion-radar. Review git diff from HEAD. Check implementation against docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md. Focus on correctness, safe href validation, generated-site-only boundaries, compatibility with existing direct dataclass fixtures, tests, docs, and whether it adds forbidden contracts/artifacts/source acquisition/scoring/ranking/recommendation/compliance features. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-378-code-review.md
rm -f "$tmp_review"
```

Expected: complete review file with no Critical or Important findings.

- [ ] **Step 3: Ask opencode to cross-check the code**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 378 Saved Local Article Related Read Lanes code. Review git diff from HEAD and docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md. Focus on correctness, safe href validation, generated-site-only boundaries, tests, docs, and forbidden contract/artifact/source acquisition/scoring/ranking/recommendation/compliance changes. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-378-code-review.md
rm -f "$tmp_review"
```

Expected: complete review file with no Critical or Important findings.

- [ ] **Step 4: Fix Critical and Important code findings**

If review finds Critical or Important issues, fix them with focused tests first and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 378 Saved Local Article Related Read Lanes code after fixes. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-378-code-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 378 Saved Local Article Related Read Lanes code after fixes. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-378-code-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important findings.

- [ ] **Step 5: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
git diff --cached --check
```

Expected: all pass.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/saved_article_local_related_reads.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/plans/2026-07-10-stage-378-saved-local-article-related-read-lanes-plan.md docs/reviews/claude-code-stage-378-plan-review.md docs/reviews/opencode-stage-378-plan-review.md docs/reviews/claude-code-stage-378-code-review.md docs/reviews/opencode-stage-378-code-review.md
git commit -m "Stage 378: add related read lanes"
git push origin main
```

Expected: commit pushed to GitHub. Then stop and report a Handoff Summary.
