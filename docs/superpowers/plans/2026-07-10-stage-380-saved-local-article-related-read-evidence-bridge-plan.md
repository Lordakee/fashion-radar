# Stage 380 Saved Local Article Related-Read Evidence Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only evidence bridge to related saved local read cards so a reader can see which paragraph in the current article connects to which paragraph in the next local article.

**Architecture:** Extend the existing `RowOneSavedArticleLocalRelatedReadCard` view model with optional paragraph bridge links derived from already-computed shared reference entries in the current saved local article and candidate saved local article. Render the bridge inside the existing `articles/<story-id>.html` related reads section, after reference chips and before the existing local read action. The feature remains presentation-only and does not add collection, extraction, ranking, source acquisition, connector, scheduling, route family, generated JSON artifact, schema, manifest/runtime, or app contract behavior.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, existing `templates.py` server-rendered HTML helpers, pytest, ruff, uv with frozen `--no-config` verification commands.

---

## Product Gap

Stages 377 and 378 added same-site related saved local reads and grouped those reads into lanes by shared signal, ROW ONE section, or source. The page now recommends what to read next, but for the strongest related-read case, "Shared signal", it does not show the paragraph-level evidence explaining why the next article is connected to the current article. Stage 380 closes that report-layer explanation gap in the collect -> match -> report pipeline by showing a compact "Here ¶N -> Next read ¶M" bridge for cards with shared references. It reuses existing saved local article sidecars, reference keys, paragraph indices, generated local article page routes, and existing paragraph anchors.

## Scope Decision From Pre-Plan Exploration

- Use the existing related-read card surface instead of creating a new organizer panel. The site already has many local-article organization modules, and the missing piece is the proof behind related-read cards.
- Show bridge rows only when there is a shared reference with a valid paragraph in both the current article and candidate article. Same-section and same-source cards without shared references keep their current rendering.
- Keep card ordering and scoring unchanged. Stage 380 explains an existing relationship; it does not introduce new ranking, recommendation, demand proof, or coverage verification.
- Keep all links same-site and already-generated:
  - Current paragraph link: `#local-article-paragraph-N`
  - Candidate paragraph link: `<candidate-story-id>.html#local-article-paragraph-N`
- Do not add outbound article URLs, social-platform behavior, default connectors, scheduled collection, generated JSON, standalone pages, or app contract fields.

## File Map

- Modify `src/fashion_radar/row_one/saved_article_local_related_reads.py`
  - Add `RowOneSavedArticleLocalRelatedReadEvidenceBridge`.
  - Add optional `evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...] = ()` to `RowOneSavedArticleLocalRelatedReadCard`.
  - Extend `_Candidate` with `evidence_bridges`.
  - Build bridge rows from shared reference keys by pairing the first valid current article paragraph for a shared reference with the first valid candidate article paragraph for the same shared reference.
  - Keep bridge rows capped to the existing reference chip limit, because the bridge explains shared references already visible on the card.
  - Preserve existing candidate score, sort order, card count, href fallback, reference chips, lane grouping, and excluded story behavior.
- Modify `src/fashion_radar/row_one/templates.py`
  - Render bridge rows inside `_render_saved_article_local_related_read_card(...)`.
  - Validate current article bridge hrefs with a new same-page paragraph guard.
  - Validate candidate bridge hrefs with the existing `_safe_saved_article_local_related_read_href(...)` guard.
  - Escape all labels and reference names.
  - Add CSS for `.saved-article-local-related-read-evidence-bridge` and row/link elements, aligned with existing related-read card styling.
- Modify `tests/test_row_one_saved_article_local_related_reads.py`
  - Add focused builder tests for shared-reference paragraph bridges.
  - Add focused tests proving unsafe current/candidate paragraph indices do not create bridge rows while cards still render when existing fallback behavior applies.
  - Add backward-compatibility tests for same-section/same-source cards without bridges.
- Modify `tests/test_row_one_render.py`
  - Add render tests for bridge markup, link validation, escaping, and lane rendering compatibility.
  - Add a full generated-site test proving the bridge appears only on `articles/<story-id>.html` and does not add contract payload keys or generated artifacts.
  - Add CSS selector coverage.
- Modify `tests/test_workflows.py`
  - Extend generated-site-only sentinels with Stage 380 denylist strings and artifact stems.
  - Add a Stage 380 workflow test that monkeypatches related-read rendering/building to prove the feature does not leak into app-facing contract payloads or create standalone artifacts.
- Modify `tests/test_row_one_docs.py`
  - Add a Stage 380 docs boundary assertion above Stage 379.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 380 paragraph documenting generated-site-only behavior and explicit non-goals.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-380-plan-review.md`
  - `opencode-stage-380-plan-review.md`
  - `claude-code-stage-380-code-review.md`
  - `opencode-stage-380-code-review.md`
  - Rereview files only if Critical or Important findings require fixes.

## Data Contract

Add:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadEvidenceBridge:
    reference: RowOneSavedArticleLocalRelatedReadReference
    current_label: LocalizedText
    current_href: str
    candidate_label: LocalizedText
    candidate_href: str
```

Add to `RowOneSavedArticleLocalRelatedReadCard`:

```python
evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...] = ()
```

Bridge labels use one-based paragraph numbers:

```python
current_label = LocalizedText(en=f"Here ¶{current_index + 1}", zh=f"本文 ¶{current_index + 1}")
candidate_label = LocalizedText(
    en=f"Next read ¶{candidate_index + 1}",
    zh=f"下一篇 ¶{candidate_index + 1}",
)
```

## Builder Rules

- Build a current reference-entry map once in `build_row_one_saved_article_local_related_reads(...)`:
  - Key: normalized reference name from `_reference_key(...)`
  - Value: first `_ReferenceEntry` for that key with at least one paragraph index that is valid for the article being mapped.
- Candidate bridge generation happens inside `_candidate(...)` after `entries` and `shared_keys` are known.
- A bridge is valid only when:
  - The shared key exists in the current reference-entry map.
  - The current entry has a valid paragraph index in the current article.
  - The candidate entry has a valid paragraph index in the candidate article.
  - The candidate base href passed `_safe_sibling_article_href(...)`.
  - The rendered reference has a nonblank name.
- The candidate card primary `href` continues to use the existing shared-reference candidate paragraph fallback behavior.
- If no bridge rows are valid, the card is still eligible through existing shared-reference, same-section, or same-source behavior.

## Render And Href Rules

- Current bridge hrefs:
  - Accept only exact fragment-only hrefs matching `#local-article-paragraph-N` through `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`.
  - Reject every other form, including external URLs, page paths, empty strings, whitespace, dot-prefixed paths, slash-containing paths, protocol URLs, `javascript:`, `data:`, and non-paragraph fragments.
- Candidate bridge hrefs:
  - Reuse `_safe_saved_article_local_related_read_href(card.candidate_story_id, href)`.
  - This preserves the existing sibling `story-id.html#local-article-paragraph-N` contract.
- If a bridge row has either unsafe href, omit that row.
- If all rows are omitted, omit the bridge shell.
- The bridge renders inside both lane and non-lane related-read layouts, because both call `_render_saved_article_local_related_read_card(...)`.

## Acceptance Criteria

- A related-read card with a shared reference and valid paragraph indices in both articles renders a compact evidence bridge.
- The bridge shows the shared reference chip and two links:
  - Current article paragraph anchor.
  - Candidate local article paragraph anchor.
- Related-read lane grouping still works and still covers all renderable cards when all cards have known lane reasons.
- Cards without shared-reference paragraph evidence keep their current behavior.
- Existing related-read card primary links, reference chips, reason copy, excerpts, card count, score ordering, and excluded story behavior remain unchanged.
- No new generated JSON artifact, standalone HTML page, route family, schema field, app/runtime/manifest key, source collection behavior, fetching behavior, extraction behavior, matching behavior, scoring behavior, ranking behavior, LLM behavior, connector behavior, scheduling behavior, analytics behavior, personalization behavior, recommendation behavior, demand proof, coverage verification, or compliance-review product feature is added.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-380-plan-review.md`
- Create: `docs/reviews/opencode-stage-380-plan-review.md`
- Modify if needed: `docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 380 Saved Local Article Related-Read Evidence Bridge plan in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around _render_saved_article_local_related_reads, _render_saved_article_local_related_read_card, _safe_saved_article_local_related_read_href, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py around related-read tests, tests/test_workflows.py, and tests/test_row_one_docs.py. Goal: add a generated-site-only paragraph evidence bridge to existing related saved local read cards on articles/<story-id>.html. Technical stack: Python dataclasses, templates.py HTML helpers, pytest, ruff, uv. Implementation method: extend existing related-read card view model with optional bridge rows derived from current and candidate shared-reference paragraph indices; render rows in existing card markup; validate hrefs at render time; add focused tests/docs/workflow boundaries. Check feasibility, paragraph-index correctness, href safety, generated-site-only boundaries, test coverage, docs, and duplication with existing ROW ONE surfaces. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-380-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body ending with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 380 Saved Local Article Related-Read Evidence Bridge plan. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-380-plan-review.md if present, docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py around related-read rendering and href validation, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py, tests/test_workflows.py, and tests/test_row_one_docs.py. Check feasibility, paragraph evidence derivation, generated-site-only boundaries, href safety, test coverage, docs boundaries, and whether this duplicates existing ROW ONE surfaces. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-380-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update this plan and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 380 Saved Local Article Related-Read Evidence Bridge plan after fixes. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md, docs/reviews/claude-code-stage-380-plan-review.md, and docs/reviews/opencode-stage-380-plan-review.md. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-380-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 380 Saved Local Article Related-Read Evidence Bridge plan after fixes. Read the plan and review records. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-380-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Modify: `tests/test_row_one_saved_article_local_related_reads.py`

- [ ] **Step 1: Add failing test for shared-reference bridge rows**

Add this test after `test_saved_article_local_related_reads_scores_shared_refs_section_source`:

```python
def test_saved_article_local_related_reads_adds_shared_reference_evidence_bridge() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared The Row signal")
    edition = _edition(current, shared)
    articles = {
        current.id: _article(
            current.id,
            paragraphs=["Current opening.", "Current The Row paragraph."],
            content_sections=[
                _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
        shared.id: _article(
            shared.id,
            paragraphs=["Shared opening.", "Shared The Row paragraph."],
            content_sections=[
                _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[1])
            ],
        ),
    }

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=edition,
        local_articles_by_story_id=articles,
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert len(related.cards) == 1
    bridge = related.cards[0].evidence_bridges[0]
    assert bridge.reference.name == "The Row"
    assert bridge.current_label.en == "Here ¶2"
    assert bridge.current_label.zh == "本文 ¶2"
    assert bridge.current_href == "#local-article-paragraph-2"
    assert bridge.candidate_label.en == "Next read ¶2"
    assert bridge.candidate_label.zh == "下一篇 ¶2"
    assert bridge.candidate_href == "shared-row-2222222222.html#local-article-paragraph-2"
```

- [ ] **Step 2: Run the focused test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py::test_saved_article_local_related_reads_adds_shared_reference_evidence_bridge -q
```

Expected: FAIL because `RowOneSavedArticleLocalRelatedReadCard` does not have `evidence_bridges`.

- [ ] **Step 3: Add failing tests for invalid and non-shared bridge behavior**

Add these tests near the first new test:

```python
def test_saved_article_local_related_reads_omits_bridge_when_current_paragraph_invalid() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared The Row signal")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                paragraphs=["Current opening."],
                content_sections=[
                    _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[9])
                ],
            ),
            shared.id: _article(
                shared.id,
                content_sections=[
                    _content_section("Shared refs", refs=[_ref("The Row")], paragraph_indices=[0])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert related.cards[0].reason.en == "Shared signal: The Row"
    assert related.cards[0].evidence_bridges == ()


def test_saved_article_local_related_reads_same_section_card_has_no_evidence_bridge() -> None:
    current = _story("current-row-0000000000")
    same_section = _story("same-section-3333333333", headline="Same section read")

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, same_section),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                content_sections=[
                    _content_section("Current refs", refs=[_ref("The Row")], paragraph_indices=[0])
                ],
            ),
            same_section.id: _article(
                same_section.id,
                content_sections=[
                    _content_section("Other refs", refs=[_ref("Alaia")], paragraph_indices=[0])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, same_section),
    )

    assert related is not None
    assert related.cards[0].reason.en == "Same ROW ONE section"
    assert related.cards[0].evidence_bridges == ()


def test_saved_article_local_related_reads_caps_evidence_bridges() -> None:
    current = _story("current-row-0000000000")
    shared = _story("shared-row-2222222222", headline="Shared signal read")
    refs = [_ref("The Row"), _ref("Alaia"), _ref("Tabi"), _ref("Phoebe Philo")]

    related = build_row_one_saved_article_local_related_reads(
        current_story=current,
        edition=_edition(current, shared),
        local_articles_by_story_id={
            current.id: _article(
                current.id,
                paragraphs=["Current A.", "Current B.", "Current C.", "Current D."],
                content_sections=[
                    _content_section("Current refs", refs=refs, paragraph_indices=[0, 1, 2, 3])
                ],
            ),
            shared.id: _article(
                shared.id,
                paragraphs=["Shared A.", "Shared B.", "Shared C.", "Shared D."],
                content_sections=[
                    _content_section("Shared refs", refs=refs, paragraph_indices=[0, 1, 2, 3])
                ],
            ),
        },
        local_article_page_hrefs_by_story_id=_hrefs(current, shared),
    )

    assert related is not None
    assert len(related.cards[0].evidence_bridges) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS
```

- [ ] **Step 4: Run the focused test file to verify RED state**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: FAIL only on missing `evidence_bridges` or missing bridge model behavior.

## Task 3: Builder GREEN Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/saved_article_local_related_reads.py`

- [ ] **Step 1: Add the bridge dataclass and card field**

Add after `RowOneSavedArticleLocalRelatedReadReference`:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadEvidenceBridge:
    reference: RowOneSavedArticleLocalRelatedReadReference
    current_label: LocalizedText
    current_href: str
    candidate_label: LocalizedText
    candidate_href: str
```

Add to `RowOneSavedArticleLocalRelatedReadCard`:

```python
evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...] = ()
```

Add to `_Candidate`:

```python
evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...]
```

- [ ] **Step 2: Pass current reference entries into candidates**

In `build_row_one_saved_article_local_related_reads(...)`, keep `current_refs` and add:

```python
current_ref_entries_by_key = _reference_entries_by_key(current_refs, current_article)
```

Pass it into `_candidate(...)`.

In the candidate loop, pass both the map and the current article:

```python
candidate = _candidate(
    story_order=story_order,
    current_story=current_story,
    current_article=current_article,
    current_ref_keys=current_ref_keys,
    current_ref_entries_by_key=current_ref_entries_by_key,
    current_has_content_sections=bool(current_article.content_sections),
    candidate_story=candidate_story,
    local_articles_by_story_id=local_articles_by_story_id,
    local_article_page_hrefs_by_story_id=local_article_page_hrefs_by_story_id,
)
```

Update the `_candidate(...)` signature with the new map:

```python
def _candidate(
    *,
    story_order: int,
    current_story: RowOneStory,
    current_article: RowOneLocalArticle,
    current_ref_keys: set[str],
    current_ref_entries_by_key: Mapping[str, _ReferenceEntry],
    current_has_content_sections: bool,
    candidate_story: RowOneStory,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    local_article_page_hrefs_by_story_id: Mapping[str, str],
) -> _Candidate | None:
```

Add helper:

```python
def _reference_entries_by_key(
    entries: tuple[_ReferenceEntry, ...],
    article: RowOneLocalArticle,
) -> dict[str, _ReferenceEntry]:
    by_key: dict[str, _ReferenceEntry] = {}
    for entry in entries:
        if (
            entry.key
            and entry.key not in by_key
            and _first_valid_entry_paragraph(entry, article) is not None
        ):
            by_key[entry.key] = entry
    return by_key
```

- [ ] **Step 3: Build bridge rows**

Add helper functions:

```python
def _evidence_bridges(
    *,
    current_article: RowOneLocalArticle,
    candidate_article: RowOneLocalArticle,
    candidate_base_href: str,
    current_entries_by_key: Mapping[str, _ReferenceEntry],
    candidate_entries: tuple[_ReferenceEntry, ...],
    shared_keys: tuple[str, ...],
) -> tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...]:
    bridges: list[RowOneSavedArticleLocalRelatedReadEvidenceBridge] = []
    candidate_entries_by_key = _reference_entries_by_key(candidate_entries, candidate_article)
    for shared_key in shared_keys:
        if len(bridges) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS:
            break
        current_entry = current_entries_by_key.get(shared_key)
        candidate_entry = candidate_entries_by_key.get(shared_key)
        if current_entry is None or candidate_entry is None:
            continue
        current_index = _first_valid_entry_paragraph(current_entry, current_article)
        candidate_index = _first_valid_entry_paragraph(candidate_entry, candidate_article)
        if current_index is None or candidate_index is None:
            continue
        bridges.append(
            RowOneSavedArticleLocalRelatedReadEvidenceBridge(
                reference=candidate_entry.reference,
                current_label=LocalizedText(
                    en=f"Here ¶{current_index + 1}",
                    zh=f"本文 ¶{current_index + 1}",
                ),
                current_href=f"#{local_article_paragraph_anchor(current_index)}",
                candidate_label=LocalizedText(
                    en=f"Next read ¶{candidate_index + 1}",
                    zh=f"下一篇 ¶{candidate_index + 1}",
                ),
                candidate_href=(
                    f"{candidate_base_href}#{local_article_paragraph_anchor(candidate_index)}"
                ),
            )
        )
    return tuple(bridges)


def _first_valid_entry_paragraph(
    entry: _ReferenceEntry,
    article: RowOneLocalArticle,
) -> int | None:
    for index in entry.paragraph_indices:
        if _valid_paragraph_index(index, article) is not None:
            return index
    return None
```

In `_candidate(...)`, call `_evidence_bridges(...)` after `shared_keys` is computed and pass the result into `_Candidate(...)`.

In `_card(...)`, pass `evidence_bridges=candidate.evidence_bridges`.

- [ ] **Step 4: Run focused builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
```

Expected: all related-read builder tests pass.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Import the bridge dataclass**

Add to the existing related-read import block:

```python
RowOneSavedArticleLocalRelatedReadEvidenceBridge,
```

- [ ] **Step 2: Add a helper bridge**

Add near `_related_read_card(...)`:

```python
def _related_read_bridge(
    *,
    reference_name: str = "The Row",
    reference_label: str = "Brand",
    current_href: str = "#local-article-paragraph-1",
    candidate_href: str = "related-row-2222222222.html#local-article-paragraph-1",
) -> RowOneSavedArticleLocalRelatedReadEvidenceBridge:
    return RowOneSavedArticleLocalRelatedReadEvidenceBridge(
        reference=RowOneSavedArticleLocalRelatedReadReference(
            name=reference_name,
            label=reference_label,
        ),
        current_label=LocalizedText(en="Here ¶1", zh="本文 ¶1"),
        current_href=current_href,
        candidate_label=LocalizedText(en="Next read ¶1", zh="下一篇 ¶1"),
        candidate_href=candidate_href,
    )
```

Extend `_related_read_card(...)` with:

```python
evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...] = (),
```

and pass it to the card constructor.

- [ ] **Step 3: Add failing render test for bridge markup**

Add near existing related-read render tests:

```python
def test_render_local_article_page_includes_related_read_evidence_bridge() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(evidence_bridges=(_related_read_bridge(),))
        ),
    )

    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert 'class="saved-article-local-related-read-evidence-bridge"' in section_html
    assert "The Row" in section_html
    assert "Brand" in section_html
    assert 'href="#local-article-paragraph-1"' in section_html
    assert 'href="related-row-2222222222.html#local-article-paragraph-1"' in section_html
    assert "Here ¶1" in section_html
    assert "Next read ¶1" in section_html
    assert "本文 ¶1" in section_html
    assert "下一篇 ¶1" in section_html
```

- [ ] **Step 4: Add failing render tests for filtering and escaping**

Add:

```python
def test_render_local_article_page_filters_unsafe_related_read_evidence_bridge_links() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                evidence_bridges=(
                    _related_read_bridge(current_href="../bad"),
                    _related_read_bridge(candidate_href="https://example.com/article"),
                )
            )
        ),
    )

    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert "saved-article-local-related-read-evidence-bridge" not in section_html
    assert "../bad" not in section_html
    assert "https://example.com/article" not in section_html


def test_render_local_article_page_escapes_related_read_evidence_bridge() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                evidence_bridges=(
                    _related_read_bridge(
                        reference_name="The Row <brand>",
                        reference_label="Brand <signal>",
                    ),
                )
            )
        ),
    )

    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert "The Row &lt;brand&gt;" in section_html
    assert "Brand &lt;signal&gt;" in section_html
    assert "The Row <brand>" not in section_html


def test_render_local_article_page_includes_related_read_evidence_bridge_inside_lanes() -> None:
    html = render_local_article_page_html(
        _edition(),
        _edition().stories[0],
        local_article=_signal_briefing_local_article(),
        saved_article_local_related_reads=_related_reads_model(
            _related_read_card(
                reason=LocalizedText(en="Shared signal: The Row", zh="共同信号：The Row"),
                evidence_bridges=(_related_read_bridge(),),
            )
        ),
    )

    section_html = _html_between(
        html,
        '<section class="saved-article-local-related-reads"',
        "</section>",
    )

    assert 'class="saved-article-local-related-read-lanes"' in section_html
    assert 'class="saved-article-local-related-read-evidence-bridge"' in section_html
```

- [ ] **Step 5: Run the focused render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_local_article_page_includes_related_read_evidence_bridge \
  tests/test_row_one_render.py::test_render_local_article_page_filters_unsafe_related_read_evidence_bridge_links \
  tests/test_row_one_render.py::test_render_local_article_page_escapes_related_read_evidence_bridge -q
```

Expected: FAIL because bridge rendering is not implemented.

## Task 5: Render GREEN Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Render bridge rows in cards**

In `_render_saved_article_local_related_read_card(...)`, add:

```python
evidence_bridge = _render_saved_article_local_related_read_evidence_bridge(card)
```

Insert `{evidence_bridge}` after `{references}` and before the action link.

Add:

```python
def _render_saved_article_local_related_read_evidence_bridge(
    card: RowOneSavedArticleLocalRelatedReadCard,
) -> str:
    rows = [
        row
        for bridge in card.evidence_bridges
        if (row := _render_saved_article_local_related_read_evidence_bridge_row(card, bridge))
    ]
    if not rows:
        return ""
    return (
        '          <div class="saved-article-local-related-read-evidence-bridge">\n'
        '            <span class="saved-article-local-related-read-evidence-bridge-label">\n'
        '              <span data-lang="en">Evidence bridge</span>\n'
        '              <span data-lang="zh">证据连接</span>\n'
        "            </span>\n"
        + "\n".join(rows)
        + "\n          </div>"
    )
```

Add:

```python
def _render_saved_article_local_related_read_evidence_bridge_row(
    card: RowOneSavedArticleLocalRelatedReadCard,
    bridge: RowOneSavedArticleLocalRelatedReadEvidenceBridge,
) -> str:
    current_href = _safe_saved_article_local_related_read_current_href(bridge.current_href)
    candidate_href = _safe_saved_article_local_related_read_href(
        card.candidate_story_id,
        bridge.candidate_href,
    )
    if current_href is None or candidate_href is None:
        return ""
    return f"""            <div class="saved-article-local-related-read-evidence-bridge-row">
              <span class="saved-article-local-related-read-evidence-bridge-ref">
                <span>{_esc(bridge.reference.name)}</span>
                <span>{_esc(bridge.reference.label)}</span>
              </span>
              <span class="saved-article-local-related-read-evidence-bridge-links">
                <a href="{_esc(current_href)}">
                  <span data-lang="en">{_esc(bridge.current_label.en)}</span>
                  <span data-lang="zh">{_esc(bridge.current_label.zh)}</span>
                </a>
                <span aria-hidden="true">-></span>
                <a href="{_esc(candidate_href)}">
                  <span data-lang="en">{_esc(bridge.candidate_label.en)}</span>
                  <span data-lang="zh">{_esc(bridge.candidate_label.zh)}</span>
                </a>
              </span>
            </div>"""
```

Add:

```python
def _safe_saved_article_local_related_read_current_href(href: str) -> str | None:
    if not isinstance(href, str):
        return None
    if not href.startswith("#"):
        return None
    fragment = href.removeprefix("#")
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return href
```

- [ ] **Step 2: Add CSS**

Add CSS near existing related-read styles:

```css
.saved-article-local-related-read-evidence-bridge {
  display: grid;
  gap: 0.45rem;
  border-top: 1px solid rgba(26, 24, 20, 0.1);
  padding-top: 0.75rem;
}

.saved-article-local-related-read-evidence-bridge-label {
  color: var(--muted);
  font-size: 0.72rem;
  text-transform: uppercase;
}

.saved-article-local-related-read-evidence-bridge-row {
  display: grid;
  gap: 0.4rem;
}

.saved-article-local-related-read-evidence-bridge-ref,
.saved-article-local-related-read-evidence-bridge-links {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.saved-article-local-related-read-evidence-bridge-ref span,
.saved-article-local-related-read-evidence-bridge-links a {
  border: 1px solid rgba(26, 24, 20, 0.12);
  border-radius: 999px;
  color: var(--ink);
  padding: 0.22rem 0.55rem;
  text-decoration: none;
}
```

- [ ] **Step 3: Run focused render tests**

Before running the render tests, extend
`test_row_one_css_includes_saved_article_local_related_reads_styles` with the
new selectors:

```python
".saved-article-local-related-read-evidence-bridge",
".saved-article-local-related-read-evidence-bridge-label",
".saved-article-local-related-read-evidence-bridge-row",
".saved-article-local-related-read-evidence-bridge-ref",
".saved-article-local-related-read-evidence-bridge-links",
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_local_article_page_includes_related_read_evidence_bridge \
  tests/test_row_one_render.py::test_render_local_article_page_filters_unsafe_related_read_evidence_bridge_links \
  tests/test_row_one_render.py::test_render_local_article_page_escapes_related_read_evidence_bridge \
  tests/test_row_one_render.py::test_render_local_article_page_groups_related_reads_into_lanes -q
```

Expected: all selected render tests pass.

## Task 6: Workflow And Docs RED/GREEN

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add workflow denylist coverage**

Add Stage 380 strings to the generated-site-only denylist near Stage 377/378:

```python
"saved_article_local_related_read_evidence_bridge",
"local_article_related_read_evidence_bridge",
"related_read_evidence_bridge",
"RowOneSavedArticleLocalRelatedReadEvidenceBridge",
"Saved Local Article Related-Read Evidence Bridge",
"Evidence bridge",
"证据连接",
"Here ¶",
"Next read ¶",
"本文 ¶",
"下一篇 ¶",
"saved-article-local-related-read-evidence-bridge",
"local-article-related-read-evidence-bridge",
"related-read-evidence-bridge",
```

Add artifact stems:

```python
"saved-local-article-related-read-evidence-bridge",
"local-article-related-read-evidence-bridge",
"related-read-evidence-bridge",
"saved_local_article_related_read_evidence_bridge",
"local_article_related_read_evidence_bridge",
"related_read_evidence_bridge",
"RowOneSavedArticleLocalRelatedReadEvidenceBridge",
"Saved Local Article Related-Read Evidence Bridge",
```

Add a focused Stage 380 workflow test:

```python
def test_stage_380_saved_local_article_related_read_evidence_bridge_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fashion_radar.row_one import templates as row_one_templates

    monkeypatch.setattr(
        row_one_templates,
        "_render_saved_article_local_related_read_evidence_bridge",
        lambda *_args, **_kwargs: "",
        raising=True,
    )
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

- [ ] **Step 2: Add docs tests**

Add in `tests/test_row_one_docs.py`:

```python
def test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary() -> None:
    paragraph = (
        "Stage 380 adds generated-site only Saved Local Article Related-Read "
        "Evidence Bridge rows inside existing related saved local read cards on "
        "`articles/<story-id>.html`"
    )
    for path in (ROOT / "README.md", ROOT / "docs" / "row-one.md"):
        text = path.read_text()
        assert paragraph in text
        assert text.index(paragraph) < text.index("Stage 379 adds")
        stage_380_slice = text[text.index(paragraph) : text.index("Stage 379 adds")]
        normalized = _normalized(stage_380_slice)
        assert "`data/saved-local-article-related-read-evidence-bridge.json`" in stage_380_slice
        assert "`saved-local-article-related-read-evidence-bridge.html`" in stage_380_slice
        assert "does not create new article-source sidecars" in stage_380_slice
        assert "does not add outbound article URLs as primary navigation" in stage_380_slice
        assert "does not change row-one-app/v7" in stage_380_slice
        assert "source collection" in stage_380_slice
        assert "connector" in stage_380_slice
        assert "scheduling" in stage_380_slice
        assert "compliance-review behavior" in stage_380_slice
        for stale_phrase in (
            "creates data/saved-local-article-related-read-evidence-bridge.json",
            "writes data/saved-local-article-related-read-evidence-bridge.json",
            "creates saved-local-article-related-read-evidence-bridge.html",
        ):
            assert _normalized(stale_phrase) not in normalized
```

- [ ] **Step 3: Run docs/workflow tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_stage_380_saved_local_article_related_read_evidence_bridge_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary -q
```

Expected: docs test FAILS until README/docs paragraphs are added; workflow test may pass after the sentinel is added.

- [ ] **Step 4: Add README and docs boundary paragraphs**

Insert this paragraph immediately before Stage 379 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 380 adds generated-site only Saved Local Article Related-Read Evidence Bridge rows inside existing related saved local read cards on `articles/<story-id>.html`; it reuses Stage 377/378 related-read cards and lanes, current-edition saved local article sidecars, existing shared reference keys, existing item-level paragraph indices, generated local article page routes, and existing paragraph anchors to show a compact current-paragraph to next-read-paragraph evidence bridge without changing app-facing contracts; it does not create `data/saved-local-article-related-read-evidence-bridge.json`, does not create `data/local-article-related-read-evidence-bridge.json`, does not create `data/related-read-evidence-bridge.json`, does not create `saved-local-article-related-read-evidence-bridge.html`, does not create `local-article-related-read-evidence-bridge.html`, does not create `related-read-evidence-bridge.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full related articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, demand proof, coverage verification, or compliance-review behavior.
```

- [ ] **Step 5: Run docs/workflow tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_stage_380_saved_local_article_related_read_evidence_bridge_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary -q
```

Expected: both tests pass.

## Task 7: Focused And Full Verification

**Files:**
- All Stage 380 modified files.

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_row_one_site_contract_excludes_generated_site_only_surfaces \
  tests/test_workflows.py::test_row_one_site_does_not_create_generated_site_only_artifacts \
  tests/test_workflows.py::test_stage_380_saved_local_article_related_read_evidence_bridge_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full gates before code review**

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

Expected: all commands exit 0.

## Task 8: Code Review, Fixes, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-380-code-review.md`
- Create: `docs/reviews/opencode-stage-380-code-review.md`
- Modify if needed: Stage 380 implementation files.

- [ ] **Step 1: Ask Claude Code to review the code**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 380 Saved Local Article Related-Read Evidence Bridge implementation in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md, git diff HEAD, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Check correctness, paragraph bridge derivation, href safety, escaping, generated-site-only boundary, docs, and tests. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-380-code-review.md
rm -f "$tmp_review"
```

Expected: complete review body ending with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the code**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 380 Saved Local Article Related-Read Evidence Bridge implementation. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-380-code-review.md if present, docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md, git diff HEAD, src/fashion_radar/row_one/saved_article_local_related_reads.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_saved_article_local_related_reads.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Check correctness, href safety, generated-site-only boundaries, docs, tests, and regressions. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-380-code-review.md
rm -f "$tmp_review"
```

Expected: complete coherent review body.

- [ ] **Step 3: Fix Critical and Important code review findings**

If either reviewer raises Critical or Important findings, fix them with focused tests and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 380 Saved Local Article Related-Read Evidence Bridge after fixes. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-380-code-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 380 Saved Local Article Related-Read Evidence Bridge after fixes. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-380-code-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important findings.

- [ ] **Step 4: Run full final gates**

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

Expected: all commands exit 0.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/saved_article_local_related_reads.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_local_related_reads.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md \
  docs/superpowers/plans/2026-07-10-stage-380-saved-local-article-related-read-evidence-bridge-plan.md \
  docs/reviews/claude-code-stage-380-plan-review.md \
  docs/reviews/opencode-stage-380-plan-review.md \
  docs/reviews/claude-code-stage-380-code-review.md \
  docs/reviews/opencode-stage-380-code-review.md
git commit -m "Stage 380: add related-read evidence bridge"
git push origin main
```

Expected: commit and push succeed. If rereview files exist, include them in the commit.

## Handoff Summary Template

After push, report:

```markdown
Handoff Summary
- Repo: `/home/ubuntu/fashion-radar`
- Branch: `main`
- Latest commit: `<sha> Stage 380: add related-read evidence bridge`
- Repo status: `<git status --short --branch>`
- Verified commands:
  - `<focused command>` -> passed
  - `<full command>` -> passed
- Review records:
  - `docs/reviews/claude-code-stage-380-plan-review.md`
  - `docs/reviews/opencode-stage-380-plan-review.md`
  - `docs/reviews/claude-code-stage-380-code-review.md`
  - `docs/reviews/opencode-stage-380-code-review.md`
- Unsubmitted files: `none`
- Next step: choose Stage 381 or pause for user questions.
```
