# Stage 381 Saved Local Article Related-Read Connection Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only connection brief above existing related saved local reads so each saved article page explains why its next local reads belong together, instead of only showing related-read cards and links.

**Architecture:** Reuse the Stage 377/378/380 related-read cards that are already built from current-edition saved local article sidecars, safe local article routes, shared reference chips, lane reasons, and evidence bridge rows. Add a small deterministic connection-brief view model derived from the renderable related-read cards, then render the brief inside the existing `articles/<story-id>.html` related reads section before lanes/cards. The feature stays presentation-only and does not add collection, extraction, matching, scoring, ranking, source acquisition, connector, scheduling, route family, generated JSON artifact, schema, manifest/runtime, or app contract behavior.

**Tech Stack:** Python dataclasses, existing ROW ONE model/view-model helpers, existing `templates.py` server-rendered HTML helpers, pytest, ruff, uv with frozen `--no-config` verification commands.

---

## Product Gap

Stages 377 through 380 made related saved local reads more useful by adding same-site next-read cards, lane grouping, and paragraph evidence bridge rows. The page still makes the reader assemble the relationship themselves by scanning individual card reasons and chips. Stage 381 closes that report-layer organization gap in the collect -> match -> report pipeline by adding a compact editorial connection brief that summarizes the existing related-read set: how many next reads are present, which signal/source evidence appears across the set, which relationship types are represented, and how much paragraph-bridge evidence exists.

This is a content organization feature, not a new recommendation engine. It summarizes relationships that already exist in the related-read cards.

## Scope Decision From Pre-Plan Exploration

- Put the brief inside the existing `saved-article-local-related-reads` section on `articles/<story-id>.html`.
- Derive the brief from already-renderable related-read cards, so manually constructed unsafe cards in tests do not affect the summary.
- Keep the existing related-read card ordering, scoring, lane grouping, primary hrefs, evidence bridge rows, and excluded-story behavior unchanged.
- Use deterministic copy from card `reason`, `references`, `source_name`, and `evidence_bridges`; do not call an LLM.
- Keep all links same-site. The brief does not add new outbound links.
- Do not add default social scraping/connectors, scheduled collection, standalone pages, generated JSON, app contract fields, analytics, personalization, demand proof, coverage verification, or compliance-review product features.

## File Map

- Modify `src/fashion_radar/row_one/saved_article_local_related_reads.py`
  - Add `RowOneSavedArticleLocalRelatedReadConnectionBrief`.
  - Add `build_row_one_saved_article_local_related_read_connection_brief(cards)`.
  - Summarize only passed cards; the template passes renderable cards after href validation.
  - Deduplicate source names and signal references with existing normalization.
  - Count evidence bridge rows from existing `card.evidence_bridges`.
  - Classify represented reasons with existing `_related_read_lane_key(card)`.
  - Cap displayed signal references and source names to the existing related-read reference cap.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the new dataclass and builder.
  - In `_render_saved_article_local_related_reads(...)`, compute `renderable_cards` once, derive the brief from those cards, and render it before lanes/cards.
  - Add `_render_saved_article_local_related_read_connection_brief(...)`.
  - Escape all text and omit empty chips/rows.
  - Add CSS selectors for `.saved-article-local-related-read-connection-brief` and child elements.
- Modify `tests/test_row_one_saved_article_local_related_reads.py`
  - Add builder tests for deterministic counts, deduplication, lane labels, evidence bridge counts, empty input, and caps.
- Modify `tests/test_row_one_render.py`
  - Add render tests proving the brief appears before lanes/cards, uses only renderable safe cards, escapes card-derived text, and omits itself when no cards render.
  - Add CSS selector coverage.
- Modify `tests/test_workflows.py`
  - Extend generated contract denylist with Stage 381 connection-brief names and artifact stems.
  - Add a workflow sentinel that monkeypatches `_render_saved_article_local_related_read_connection_brief(...)` to prove the feature stays generated-site-only.
- Modify `tests/test_row_one_docs.py`
  - Add a Stage 381 docs boundary assertion above Stage 380.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 381 paragraph documenting generated-site-only behavior and explicit non-goals.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-381-plan-review.md`
  - `opencode-stage-381-plan-review.md`
  - `claude-code-stage-381-code-review.md`
  - `opencode-stage-381-code-review.md`
  - Rereview files only when Critical or Important findings require fixes.

## Data Contract

Add:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadConnectionBrief:
    title: LocalizedText
    lead: LocalizedText
    card_count: int
    source_count: int
    signal_count: int
    evidence_bridge_count: int
    lane_labels: tuple[LocalizedText, ...]
    signal_references: tuple[RowOneSavedArticleLocalRelatedReadReference, ...]
    source_names: tuple[str, ...]
```

The builder is:

```python
def build_row_one_saved_article_local_related_read_connection_brief(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> RowOneSavedArticleLocalRelatedReadConnectionBrief | None:
    ...
```

The builder returns `None` for an empty card sequence. It does not validate hrefs because the template passes `renderable_cards` after `_safe_saved_article_local_related_read_href(...)` has already filtered unsafe cards.

## Builder Rules

- `title`:
  - English: `Connection Brief`
  - Chinese: `关联阅读简报`
- `card_count` is `len(cards)`.
- `source_count` is the count of unique nonblank normalized source names displayed in `source_names`, capped at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.
- `signal_count` is the count of unique displayed references in `signal_references`, capped at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.
- `evidence_bridge_count` is the total number of existing bridge rows across cards.
- `lane_labels` is derived from `_related_read_lane_key(card)` in this stable order:
  - `Shared signals` / `共同信号`
  - `Same ROW ONE section` / `同一 ROW ONE 栏目`
  - `Same source desk` / `同一来源台`
- `signal_references` keeps first-seen unique references and caps at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.
- `source_names` keeps first-seen unique source names and caps at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.
- `lead` is deterministic:
  - If at least one signal reference exists:
    - English: `This path connects {card_count} local reads through shared signals, source context, and paragraph evidence already saved in ROW ONE.`
    - Chinese: `这条路径用 ROW ONE 已保存的共同信号、来源语境与段落证据串联 {card_count} 篇本地阅读。`
  - If no signal references exist:
    - English: `This path connects {card_count} local reads through section or source context already saved in ROW ONE.`
    - Chinese: `这条路径用 ROW ONE 已保存的栏目或来源语境串联 {card_count} 篇本地阅读。`

## Render Rules

- `_render_saved_article_local_related_reads(...)` already filters cards through `_render_saved_article_local_related_read_card(...)` and `_renderable_saved_article_local_related_read_cards(...)`.
- Stage 381 must compute the brief from `renderable_cards`, not from `related_reads.cards`.
- Render order inside the section:
  1. Header
  2. Connection brief
  3. Lanes or fallback grid
- Render the brief as:

```html
<div class="saved-article-local-related-read-connection-brief">
  <div class="saved-article-local-related-read-connection-brief-copy">
    <h3>...</h3>
    <p>...</p>
  </div>
  <div class="saved-article-local-related-read-connection-brief-metrics">...</div>
  <div class="saved-article-local-related-read-connection-brief-tags">...</div>
</div>
```

- Metrics show card count, source count, signal count, and evidence bridge count.
- Tags show lane labels, signal references, and source names.
- Omit tag groups that have no entries.
- Escape every card-derived value with `_esc(...)`.
- Do not add new anchor links in the brief. Existing card links and bridge links remain the only navigation inside the related-read section.

## Acceptance Criteria

- A related-read section with safe renderable cards includes a connection brief before lanes/cards.
- The brief summarizes card count, source count, signal count, evidence bridge count, relationship lane labels, signal reference chips, and source chips.
- Unsafe or mismatched related-read cards do not contribute to the brief.
- The brief is omitted when the related-read section has no renderable cards.
- Existing related-read cards, lane grouping, primary hrefs, evidence bridge rows, score ordering, and docs/workflow generated-site-only boundaries remain unchanged.
- No generated JSON artifact, standalone HTML page, route family, schema field, app/runtime/manifest key, source collection behavior, fetching behavior, extraction behavior, matching behavior, scoring behavior, ranking behavior, LLM behavior, connector behavior, scheduling behavior, analytics behavior, personalization behavior, recommendation behavior, demand proof, coverage verification, or compliance-review product feature is added.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-381-plan-review.md`
- Create: `docs/reviews/opencode-stage-381-plan-review.md`
- Modify after review feedback: `docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 381 Saved Local Article Related-Read Connection Brief plan in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around _render_saved_article_local_related_reads, _render_saved_article_local_related_read_card, _safe_saved_article_local_related_read_href, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py around related-read tests, tests/test_workflows.py, and tests/test_row_one_docs.py. Goal: add a generated-site-only connection brief above existing related saved local read cards on articles/<story-id>.html. Technical stack: Python dataclasses, templates.py HTML helpers, pytest, ruff, uv. Implementation method: derive a deterministic brief from already renderable related-read cards using card reasons, references, sources, and evidence bridges; render it inside the existing related-read section; add focused tests/docs/workflow boundaries. Check feasibility, data-model fit, unsafe-card filtering, generated-site-only boundaries, test coverage, docs, and duplication with existing ROW ONE surfaces. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-381-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists, contains a complete review body, and ends with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 381 Saved Local Article Related-Read Connection Brief plan. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-381-plan-review.md if present, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around related-read rendering and href validation, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py, tests/test_workflows.py, and tests/test_row_one_docs.py. Check feasibility, connection-brief derivation, generated-site-only boundaries, unsafe-card filtering, test coverage, docs boundaries, and whether this duplicates existing ROW ONE surfaces. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-381-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update this plan and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 381 Saved Local Article Related-Read Connection Brief plan after fixes. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, docs/reviews/claude-code-stage-381-plan-review.md, and docs/reviews/opencode-stage-381-plan-review.md. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-381-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 381 Saved Local Article Related-Read Connection Brief plan after fixes. Read the plan and review records. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-381-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Modify: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Add failing builder tests**

Update the existing import block to add:

```python
RowOneSavedArticleLocalRelatedReadEvidenceBridge,
build_row_one_saved_article_local_related_read_connection_brief,
```

Add these tests after `test_saved_article_local_related_read_lanes_dedupe_and_omit_unknown_reasons`:

```python
def test_saved_article_local_related_read_connection_brief_summarizes_cards() -> None:
    card = RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id="shared-row-1111111111",
        title=_text("Shared read"),
        source_name="WWD",
        reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
        excerpt=_text("Saved excerpt"),
        href="shared-row-1111111111.html#local-article-paragraph-1",
        references=(RowOneSavedArticleLocalRelatedReadReference(name="The Row", label="Brand"),),
        evidence_bridges=(
            RowOneSavedArticleLocalRelatedReadEvidenceBridge(
                reference=RowOneSavedArticleLocalRelatedReadReference(
                    name="The Row",
                    label="Brand",
                ),
                current_label=LocalizedText(en="Here ¶1", zh="本文 ¶1"),
                current_href="#local-article-paragraph-1",
                candidate_label=LocalizedText(en="Next read ¶1", zh="下一篇 ¶1"),
                candidate_href="shared-row-1111111111.html#local-article-paragraph-1",
            ),
        ),
    )
    same_source = replace(
        card,
        candidate_story_id="source-row-2222222222",
        source_name="Vogue Business",
        reason=LocalizedText(en="Same source desk", zh="同一来源"),
        href="source-row-2222222222.html#local-article-paragraph-1",
        evidence_bridges=(),
    )

    brief = build_row_one_saved_article_local_related_read_connection_brief(
        (card, same_source)
    )

    assert brief is not None
    assert brief.title.en == "Connection Brief"
    assert brief.title.zh == "关联阅读简报"
    assert brief.card_count == 2
    assert brief.source_count == 2
    assert brief.signal_count == 1
    assert brief.evidence_bridge_count == 1
    assert brief.lane_labels[0].en == "Shared signals"
    assert brief.lane_labels[1].en == "Same source desk"
    assert [reference.name for reference in brief.signal_references] == ["The Row"]
    assert brief.source_names == ("WWD", "Vogue Business")
    assert "2 local reads" in brief.lead.en
    assert "2 篇本地阅读" in brief.lead.zh


def test_saved_article_local_related_read_connection_brief_returns_none_without_cards() -> None:
    assert build_row_one_saved_article_local_related_read_connection_brief(()) is None


def test_saved_article_local_related_read_connection_brief_dedupes_and_caps_values() -> None:
    references = tuple(
        RowOneSavedArticleLocalRelatedReadReference(name=name, label="Brand")
        for name in ("The Row", "Alaia", "Margaux", "Tabi")
    )
    cards = tuple(
        RowOneSavedArticleLocalRelatedReadCard(
            candidate_story_id=f"shared-row-{index:010d}",
            title=_text(f"Shared read {index}"),
            source_name="WWD" if index < 3 else f"Source {index}",
            reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
            excerpt=_text("Saved excerpt"),
            href=f"shared-row-{index:010d}.html#local-article-paragraph-1",
            references=references,
        )
        for index in range(1, 5)
    )

    brief = build_row_one_saved_article_local_related_read_connection_brief(cards)

    assert brief is not None
    assert brief.signal_count == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert len(brief.signal_references) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert len(brief.source_names) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
    assert brief.source_count == 3
```

- [ ] **Step 2: Run builder tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: FAIL because `build_row_one_saved_article_local_related_read_connection_brief` does not exist.

## Task 3: Builder GREEN Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/saved_article_local_related_reads.py`
- Modify: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Add connection-brief dataclass and builder**

Add after `RowOneSavedArticleLocalRelatedReadLane`:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadConnectionBrief:
    title: LocalizedText
    lead: LocalizedText
    card_count: int
    source_count: int
    signal_count: int
    evidence_bridge_count: int
    lane_labels: tuple[LocalizedText, ...]
    signal_references: tuple[RowOneSavedArticleLocalRelatedReadReference, ...]
    source_names: tuple[str, ...]
```

Add builder helpers after `build_row_one_saved_article_local_related_read_lanes(...)`:

```python
def build_row_one_saved_article_local_related_read_connection_brief(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> RowOneSavedArticleLocalRelatedReadConnectionBrief | None:
    clean_cards = tuple(cards)
    if not clean_cards:
        return None
    signal_references = _related_read_connection_signal_references(clean_cards)
    source_names = _related_read_connection_sources(clean_cards)
    lane_labels = _related_read_connection_lane_labels(clean_cards)
    evidence_bridge_count = sum(len(card.evidence_bridges) for card in clean_cards)
    card_count = len(clean_cards)
    if signal_references:
        lead = LocalizedText(
            en=(
                f"This path connects {card_count} local reads through shared signals, "
                "source context, and paragraph evidence already saved in ROW ONE."
            ),
            zh=(
                "这条路径用 ROW ONE 已保存的共同信号、来源语境与段落证据串联 "
                f"{card_count} 篇本地阅读。"
            ),
        )
    else:
        lead = LocalizedText(
            en=(
                f"This path connects {card_count} local reads through section or source "
                "context already saved in ROW ONE."
            ),
            zh=(
                "这条路径用 ROW ONE 已保存的栏目或来源语境串联 "
                f"{card_count} 篇本地阅读。"
            ),
        )
    return RowOneSavedArticleLocalRelatedReadConnectionBrief(
        title=LocalizedText(en="Connection Brief", zh="关联阅读简报"),
        lead=lead,
        card_count=card_count,
        source_count=len(source_names),
        signal_count=len(signal_references),
        evidence_bridge_count=evidence_bridge_count,
        lane_labels=lane_labels,
        signal_references=signal_references,
        source_names=source_names,
    )
```

Add helper functions:

```python
def _related_read_connection_signal_references(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[RowOneSavedArticleLocalRelatedReadReference, ...]:
    references: list[RowOneSavedArticleLocalRelatedReadReference] = []
    seen: set[tuple[str, str]] = set()
    for card in cards:
        for reference in card.references:
            if len(references) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS:
                return tuple(references)
            name = normalize_row_one_paragraph(reference.name)
            label = normalize_row_one_paragraph(reference.label)
            if not name:
                continue
            key = (name.casefold(), label.casefold())
            if key in seen:
                continue
            seen.add(key)
            references.append(
                RowOneSavedArticleLocalRelatedReadReference(name=name, label=label)
            )
    return tuple(references)


def _related_read_connection_sources(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[str, ...]:
    sources: list[str] = []
    seen: set[str] = set()
    for card in cards:
        if len(sources) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS:
            break
        source_name = normalize_row_one_paragraph(card.source_name)
        if not source_name:
            continue
        key = source_name.casefold()
        if key in seen:
            continue
        seen.add(key)
        sources.append(source_name)
    return tuple(sources)


def _related_read_connection_lane_labels(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[LocalizedText, ...]:
    labels_by_key: dict[str, LocalizedText] = {}
    for card in cards:
        lane_key = _related_read_lane_key(card)
        if lane_key is None or lane_key in labels_by_key:
            continue
        copy = _LANE_COPY.get(lane_key)
        if copy is not None:
            labels_by_key[lane_key] = copy[0]
    return tuple(
        labels_by_key[key]
        for key in ("shared_signal", "same_section", "same_source")
        if key in labels_by_key
    )
```

- [ ] **Step 2: Run builder tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: PASS for the file.

- [ ] **Step 3: Run builder lint**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_local_related_reads.py tests/test_row_one_saved_article_local_related_reads.py
```

Expected: PASS.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Keep render tests on the existing helper API**

Use the existing `_related_reads_model(...)` and `_related_read_card(...)` helpers, so no direct connection-brief import is added to `tests/test_row_one_render.py`.

- [ ] **Step 2: Add failing render tests**

Add after `test_render_local_article_page_groups_related_reads_into_lanes`:

```python
def test_render_local_article_page_includes_related_read_connection_brief_before_lanes() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                candidate_story_id="related-row-2222222222",
                title="Shared signal read",
                source_name="WWD",
                reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
                href="related-row-2222222222.html#local-article-paragraph-1",
                references=(
                    RowOneSavedArticleLocalRelatedReadReference(
                        name="The Row",
                        label="Brand",
                    ),
                ),
                evidence_bridges=(_related_read_bridge(),),
            ),
            _related_read_card(
                candidate_story_id="source-row-3333333333",
                title="Same source read",
                source_name="Vogue Business",
                reason=LocalizedText(en="Same source desk", zh="同一来源"),
                href="source-row-3333333333.html#local-article-paragraph-1",
            ),
        ),
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert 'class="saved-article-local-related-read-connection-brief"' in section_html
    assert "Connection Brief" in section_html
    assert "关联阅读简报" in section_html
    assert "2 local reads" in section_html
    assert "2 篇本地阅读" in section_html
    assert "Shared signals" in section_html
    assert "Same source desk" in section_html
    assert "The Row" in section_html
    assert "WWD" in section_html
    assert section_html.index("saved-article-local-related-read-connection-brief") < (
        section_html.index("saved-article-local-related-read-lanes")
    )


def test_render_local_article_page_related_read_connection_brief_uses_only_safe_cards() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                candidate_story_id="related-row-2222222222",
                title="Safe read",
                source_name="WWD",
                href="related-row-2222222222.html#local-article-paragraph-1",
            ),
            _related_read_card(
                candidate_story_id="unsafe-row-3333333333",
                title="Unsafe read",
                source_name="Unsafe Source",
                href="articles/unsafe-row-3333333333.html#local-article-paragraph-1",
            ),
        ),
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert "Safe read" in section_html
    assert "Unsafe read" not in section_html
    assert "Unsafe Source" not in section_html
    assert "1 local read" in section_html


def test_render_local_article_page_escapes_related_read_connection_brief_values() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                candidate_story_id="related-row-2222222222",
                source_name='WWD <script>alert("x")</script>',
                reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
                href="related-row-2222222222.html#local-article-paragraph-1",
                references=(
                    RowOneSavedArticleLocalRelatedReadReference(
                        name='The Row <script>alert("x")</script>',
                        label="Brand",
                    ),
                ),
            ),
        ),
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert "<script>" not in section_html
    assert "&lt;script&gt;" in section_html
```

- [ ] **Step 3: Run render tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: FAIL because the connection-brief renderer and CSS selectors do not exist.

## Task 5: Render GREEN Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Import the builder and dataclass**

Update the existing import from `saved_article_local_related_reads`:

```python
from fashion_radar.row_one.saved_article_local_related_reads import (
    RowOneSavedArticleLocalRelatedReadCard,
    RowOneSavedArticleLocalRelatedReadConnectionBrief,
    RowOneSavedArticleLocalRelatedReadEvidenceBridge,
    RowOneSavedArticleLocalRelatedReadLane,
    RowOneSavedArticleLocalRelatedReads,
    build_row_one_saved_article_local_related_read_connection_brief,
    build_row_one_saved_article_local_related_read_lanes,
)
```

- [ ] **Step 2: Render the brief before lanes/cards**

In `_render_saved_article_local_related_reads(...)`, compute:

```python
renderable_cards = _renderable_saved_article_local_related_read_cards(
    related_reads.cards
)
connection_brief = _render_saved_article_local_related_read_connection_brief(
    build_row_one_saved_article_local_related_read_connection_brief(renderable_cards)
)
```

Reuse that same `renderable_cards` variable for lane construction, so unsafe cards are filtered once before both the brief and lanes. Return markup with:

```python
{connection_brief}
{body_html}
```

between the header and the body.

- [ ] **Step 3: Add the renderer helper**

Add before `_renderable_saved_article_local_related_read_cards(...)`:

```python
def _render_saved_article_local_related_read_connection_brief(
    brief: RowOneSavedArticleLocalRelatedReadConnectionBrief | None,
) -> str:
    if brief is None:
        return ""
    metrics = "\n".join(
        (
            _render_saved_article_local_related_read_connection_metric(
                _count_label(brief.card_count, "local read", "local reads"),
                LocalizedText(en="Next reads", zh="后续阅读"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                _count_label(brief.source_count, "source", "sources"),
                LocalizedText(en="Sources", zh="来源"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                _count_label(brief.signal_count, "signal", "signals"),
                LocalizedText(en="Signals", zh="信号"),
            ),
            _render_saved_article_local_related_read_connection_metric(
                _count_label(brief.evidence_bridge_count, "bridge", "bridges"),
                LocalizedText(en="Evidence", zh="证据"),
            ),
        )
    )
    tags = _render_saved_article_local_related_read_connection_tags(brief)
    return f"""      <div class="saved-article-local-related-read-connection-brief">
        <div class="saved-article-local-related-read-connection-brief-copy">
          <h3>
            <span data-lang="en">{_esc(brief.title.en)}</span>
            <span data-lang="zh">{_esc(brief.title.zh)}</span>
          </h3>
          <p>
            <span data-lang="en">{_esc(brief.lead.en)}</span>
            <span data-lang="zh">{_esc(brief.lead.zh)}</span>
          </p>
        </div>
        <div class="saved-article-local-related-read-connection-brief-metrics">
{metrics}
        </div>
{tags}
      </div>"""
```

Add helper functions:

```python
def _render_saved_article_local_related_read_connection_metric(
    value: str,
    label: LocalizedText,
) -> str:
    return f"""          <span>
            <strong>{_esc(value)}</strong>
            <span data-lang="en">{_esc(label.en)}</span>
            <span data-lang="zh">{_esc(label.zh)}</span>
          </span>"""
```

```python
def _render_saved_article_local_related_read_connection_tags(
    brief: RowOneSavedArticleLocalRelatedReadConnectionBrief,
) -> str:
    chips: list[str] = []
    for label in brief.lane_labels:
        chips.append(
            f"""          <span class="saved-article-local-related-read-connection-chip">
            <span data-lang="en">{_esc(label.en)}</span>
            <span data-lang="zh">{_esc(label.zh)}</span>
          </span>"""
        )
    for reference in brief.signal_references:
        if reference.name.strip():
            chips.append(
                f"""          <span class="saved-article-local-related-read-connection-chip">
            <span>{_esc(reference.name)}</span>
            <span>{_esc(reference.label)}</span>
          </span>"""
            )
    for source_name in brief.source_names:
        if source_name.strip():
            chips.append(
                f"""          <span class="saved-article-local-related-read-connection-chip">
            <span>{_esc(source_name)}</span>
          </span>"""
            )
    if not chips:
        return ""
    return (
        '        <div class="saved-article-local-related-read-connection-brief-tags">\n'
        + "\n".join(chips)
        + "\n        </div>"
    )
```

- [ ] **Step 4: Add CSS**

Add immediately after the `.saved-article-local-related-read-lane-header p` rule and before `.saved-article-local-related-read-card`:

```css
.saved-article-local-related-read-connection-brief {
  border: 1px solid var(--line);
  display: grid;
  gap: 12px;
  padding: 14px;
}
.saved-article-local-related-read-connection-brief-copy {
  display: grid;
  gap: 6px;
}
.saved-article-local-related-read-connection-brief-copy h3,
.saved-article-local-related-read-connection-brief-copy p {
  margin: 0;
}
.saved-article-local-related-read-connection-brief-copy h3 {
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.saved-article-local-related-read-connection-brief-metrics,
.saved-article-local-related-read-connection-brief-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.saved-article-local-related-read-connection-brief-metrics > span,
.saved-article-local-related-read-connection-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.75rem;
  padding: 7px 9px;
}
.saved-article-local-related-read-connection-brief-metrics strong,
.saved-article-local-related-read-connection-chip span {
  display: block;
}
```

- [ ] **Step 5: Run render tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS for the file.

## Task 6: Workflow And Docs RED Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add generated-site-only workflow sentinel**

Add denylist strings near the Stage 377/380 denylist entries:

```python
assert "saved_article_local_related_read_connection_brief" not in generated_contract_payload
assert "local_article_related_read_connection_brief" not in generated_contract_payload
assert "related_read_connection_brief" not in generated_contract_payload
assert "RowOneSavedArticleLocalRelatedReadConnectionBrief" not in generated_contract_payload
assert "Saved Local Article Related-Read Connection Brief" not in generated_contract_payload
assert "Related-Read Connection Brief" not in generated_contract_payload
assert "Connection Brief" not in generated_contract_payload
assert "saved-article-local-related-read-connection-brief" not in generated_contract_payload
assert "local-article-related-read-connection-brief" not in generated_contract_payload
assert "related-read-connection-brief" not in generated_contract_payload
assert "关联阅读简报" not in generated_contract_payload
```

Add the artifact stems to the generated artifact denylist tuple:

```python
"saved-local-article-related-read-connection-brief",
"local-article-related-read-connection-brief",
"related-read-connection-brief",
"saved_article_local_related_read_connection_brief",
"local_article_related_read_connection_brief",
"related_read_connection_brief",
"RowOneSavedArticleLocalRelatedReadConnectionBrief",
"Saved Local Article Related-Read Connection Brief",
```

Add a workflow test after the Stage 380 workflow sentinel:

```python
def test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_saved_article_local_related_read_connection_brief",
        lambda *_args, **_kwargs: "",
        raising=True,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

- [ ] **Step 2: Add docs boundary test**

Add after `test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary`:

```python
def test_row_one_docs_describe_stage_381_related_read_connection_brief_boundary() -> None:
    paragraph = (
        "Stage 381 adds generated-site only Saved Local Article Related-Read "
        "Connection Brief copy inside the existing related saved local reads section on "
        "`articles/<story-id>.html`; it reuses Stage 377/378/380 related-read cards, "
        "lanes, reasons, source names, shared reference chips, evidence bridge row "
        "counts, generated local article page routes, and existing safe renderable-card "
        "filters to explain why the next local reads connect without changing app-facing "
        "contracts; it does not create `data/saved-local-article-related-read-connection-brief.json`, "
        "does not create `data/local-article-related-read-connection-brief.json`, does "
        "not create `data/related-read-connection-brief.json`, does not create "
        "`saved-local-article-related-read-connection-brief.html`, does not create "
        "`local-article-related-read-connection-brief.html`, does not create "
        "`related-read-connection-brief.html`, does not create new article-source sidecars, "
        "does not create new route families, does not alter `index.html`, "
        "`articles/index.html`, or detail pages, does not publish full related articles "
        "outside existing local article pages, does not add outbound article URLs as "
        "primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, generated JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, "
        "deployment, market grouping, domestic/international classification, analytics, "
        "personalization, recommendation, demand proof, coverage verification, or "
        "compliance-review behavior."
    )
    readme = _read(README)
    docs = _read(ROW_ONE_DOC)

    for text in (readme, docs):
        assert paragraph in text
        assert text.index(paragraph) < text.index("Stage 380 adds")

        stage_381_slice = text[text.index(paragraph) : text.index("Stage 380 adds")]
        normalized = _normalized(stage_381_slice)
        for stale_phrase in (
            "creates data/saved-local-article-related-read-connection-brief.json",
            "writes data/saved-local-article-related-read-connection-brief.json",
            "creates data/local-article-related-read-connection-brief.json",
            "writes data/local-article-related-read-connection-brief.json",
            "creates data/related-read-connection-brief.json",
            "writes data/related-read-connection-brief.json",
            "creates saved-local-article-related-read-connection-brief.html",
            "writes saved-local-article-related-read-connection-brief.html",
            "creates local-article-related-read-connection-brief.html",
            "writes local-article-related-read-connection-brief.html",
            "creates related-read-connection-brief.html",
            "writes related-read-connection-brief.html",
            "creates new article-source sidecars",
            "creates new route families",
            "adds new routes",
            "publishes full related articles outside existing local article pages",
            "adds outbound article urls as primary navigation",
            "changes row-one-app/v7",
            "changes row-one-manifest/v1",
            "changes row-one-runtime/v1",
            "adds generated json artifacts",
            "adds source collection",
            "adds fetching",
            "adds matching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm",
            "adds connector",
            "adds scheduling",
            "adds deployment",
            "adds analytics",
            "adds personalization",
            "adds recommendation",
            "adds compliance-review",
        ):
            assert stale_phrase not in normalized
```

- [ ] **Step 3: Run workflow/docs tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_workflows.py::test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only tests/test_row_one_docs.py::test_row_one_docs_describe_stage_381_related_read_connection_brief_boundary -q
```

Expected: FAIL because the Stage 381 docs paragraphs are not yet present.

## Task 7: Docs GREEN Implementation

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add Stage 381 docs paragraph above Stage 380**

Add this exact paragraph before the Stage 380 paragraph in both `README.md` and `docs/row-one.md`:

```markdown
Stage 381 adds generated-site only Saved Local Article Related-Read Connection Brief copy inside the existing related saved local reads section on `articles/<story-id>.html`; it reuses Stage 377/378/380 related-read cards, lanes, reasons, source names, shared reference chips, evidence bridge row counts, generated local article page routes, and existing safe renderable-card filters to explain why the next local reads connect without changing app-facing contracts; it does not create `data/saved-local-article-related-read-connection-brief.json`, does not create `data/local-article-related-read-connection-brief.json`, does not create `data/related-read-connection-brief.json`, does not create `saved-local-article-related-read-connection-brief.html`, does not create `local-article-related-read-connection-brief.html`, does not create `related-read-connection-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

- [ ] **Step 2: Run workflow/docs tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_workflows.py::test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only tests/test_row_one_docs.py::test_row_one_docs_describe_stage_381_related_read_connection_brief_boundary -q
```

Expected: PASS.

## Task 8: Code Reviews, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-381-code-review.md`
- Create: `docs/reviews/opencode-stage-381-code-review.md`

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_workflows.py::test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only tests/test_row_one_docs.py::test_row_one_docs_describe_stage_381_related_read_connection_brief_boundary -q
```

Expected: PASS.

- [ ] **Step 2: Ask Claude Code to review the code**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 381 implementation in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, git diff HEAD, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around the related-read connection brief, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py related-read tests, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Check correctness, href safety, generated-site-only boundaries, escaping, test coverage, docs, and whether Critical or Important issues remain. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-381-code-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains complete output.

- [ ] **Step 3: Ask opencode to cross-check the code**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 381 implementation. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, docs/reviews/claude-code-stage-381-code-review.md if present, git diff HEAD, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Check correctness, generated-site-only boundaries, escaping, test coverage, docs, and remaining Critical or Important issues. Return one coherent final review body only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-381-code-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains complete output.

- [ ] **Step 4: Fix all Critical and Important findings**

For each Critical or Important finding, add or adjust a failing test first, run the focused failing test to verify RED, implement the smallest fix, and rerun the focused test to verify GREEN.

When fixes are needed, run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 381 implementation after review fixes. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, docs/reviews/claude-code-stage-381-code-review.md, docs/reviews/opencode-stage-381-code-review.md, and git diff HEAD. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-381-code-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 381 implementation after fixes. Read the plan, review records, and git diff HEAD. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-381-code-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important code findings.

- [ ] **Step 5: Run full verification gates**

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

Expected: every command exits 0.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short --branch
git add src/fashion_radar/row_one/saved_article_local_related_reads.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md docs/reviews/*stage-381*
git commit -m "Stage 381: add related-read connection brief"
git push origin main
```

Expected: push succeeds and `origin/main` points at the new commit.

- [ ] **Step 7: Handoff Summary**

Report:

```text
Handoff Summary
- Repo status:
- Verified commands:
- Uncommitted files:
- Next step:
```
