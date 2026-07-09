# Stage 379 Saved Local Article Cross-Surface Organization Trail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only "Filed In / 内容归档" trail to each saved local article page so readers can jump from `articles/<story-id>.html` back to the matching organization group and saved article library card on `articles/index.html`.

**Architecture:** Extend the existing saved article local reading companion view model with optional cross-surface organization trail links derived from already-built library, content organization, story, and generated local article route data. Add stable HTML anchors to the existing saved article content organization groups and saved article library cards, then render the trail inside the existing local reading companion panel. The feature does not add collection, matching, extraction, scoring, ranking, connector, scheduling, schema, route family, JSON artifact, or app/runtime/manifest contract behavior.

**Tech Stack:** Python dataclasses, existing ROW ONE models, existing `templates.py` server-rendered HTML helpers, pytest, ruff, uv with frozen `--no-config` verification commands.

---

## Product Gap

Stages 377 and 378 made each local article page better at recommending what to read next, but the page still does not explain where the current saved article lives inside ROW ONE's broader organized library surface. The reader can see companion links, related reads, and article body structure, yet they cannot jump directly back to the library organization group or the library card that contextualizes the same article. Stage 379 closes this report-layer organization gap in the collect -> match -> report pipeline by adding deterministic cross-surface anchors and a compact trail. It remains generated-site-only and reuses existing local article pages, current source attribution, and existing saved article library/organization view models.

## Scope Decision From Pre-Plan Exploration

Two read-only explorers checked the target surfaces before this plan was finalized:

- The trail should target `articles/index.html#...` from `articles/<story-id>.html`, because `index.html` is the sibling saved article library page. A root homepage target would need `../index.html#...` and is not the primary library context for this stage.
- The source shelf link is deferred. Existing source shelf anchors are derived from mutable source display text and duplicate-order suffixes. Stage 379 will not promote those to a durable cross-surface trail contract.
- Organization group and article card anchors must be derived from stable internal keys and validated detail/story IDs, not titles, localized labels, or source names.

## File Map

- Modify `src/fashion_radar/row_one/saved_article_local_reading_companion.py`
  - Add `RowOneSavedArticleLocalReadingCompanionTrailLink`.
  - Add optional `filing_links: tuple[RowOneSavedArticleLocalReadingCompanionTrailLink, ...] = ()` to `RowOneSavedArticleLocalReadingCompanion`.
  - Build trail links in `build_row_one_saved_article_local_reading_companion(...)` after the current group/card match is known.
  - Use `group.key` and the already-validated current detail path to create at most two same-site library links:
    - `index.html#saved-article-organization-group-<safe-group-key>`
    - `index.html#saved-article-library-card-<safe-story-id>`
  - Keep the builder pure and generated-site-only; do not add fields to app payloads, local article JSON, manifest, runtime, or edition contracts.
- Modify `src/fashion_radar/row_one/templates.py`
  - Add stable `id` attributes to `_render_saved_article_content_organization_group(...)` using a safe group-key anchor helper. The helper should preserve existing stable internal keys such as `entities` and permit underscores only if existing group keys require them.
  - Add stable `id` attributes to `_render_saved_article_library_card(...)` using a safe detail-path/story-id helper derived from `RowOneSavedArticleLibraryEntry.digest_path`.
  - Render `companion.filing_links` inside `_render_saved_article_local_reading_companion_current(...)` as a compact trail under the current article summary.
  - Extend `_saved_article_local_reading_companion_href(...)` to accept only the new `index.html#saved-article-organization-group-...` and `index.html#saved-article-library-card-...` patterns in addition to existing same-page anchors and sibling article links.
  - Add CSS for `.saved-article-local-reading-companion-filing-trail` and its links, reusing the companion chip visual language.
- Modify `tests/test_row_one_saved_article_local_reading_companion.py`
  - Add focused builder tests for deterministic filing links, unsafe group-key filtering, unsafe story-id filtering through existing no-match behavior, and backward compatibility when no library/organization match exists.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for companion filing trail markup and href filtering.
  - Add full-site tests that verify the saved article library organization group anchor, saved article library card anchor, and article-page trail hrefs resolve to matching generated `articles/index.html` targets.
  - Add generated-site-only no-leakage checks for Stage 379 denylist strings and artifact stems.
  - Add CSS selector guard.
- Modify `tests/test_workflows.py`
  - Extend the broad local article workflow sentinel with Stage 379 contract denylist strings and artifact stems.
  - Add a Stage 379 generated-site-only test that monkeypatches the companion builder to return a companion without filing links and reuses the local article workflow sentinel.
- Modify `tests/test_row_one_docs.py`
  - Add a Stage 379 docs boundary assertion above Stage 378.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 379 paragraph documenting generated-site-only behavior and explicit non-goals.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-379-plan-review.md`
  - `opencode-stage-379-plan-review.md`
  - `claude-code-stage-379-code-review.md`
  - `opencode-stage-379-code-review.md`
  - Rereview files only if Critical or Important findings require fixes.

## Anchor And Href Rules

- Organization group anchors:
  - Anchor id: `saved-article-organization-group-<group.key>`
  - `<group.key>` must be a stable safe internal key. Use a strict allow-list regex `r"[a-z][a-z0-9_]{0,63}"`; omit this trail link and id if validation fails.
  - Article-page href: `index.html#saved-article-organization-group-<group.key>`
  - The id renders only when the group itself renders at least one safe card, so the link never targets an empty group.
- Saved article library card anchors:
  - Anchor id: `saved-article-library-card-<story-id>`
  - Derive `<story-id>` from the canonical validated detail path, not from titles or raw `story.id`.
  - `<story-id>` must pass `safe_local_article_story_id(...)`; omit the id/link if validation fails.
  - Article-page href: `index.html#saved-article-library-card-<story-id>`
- Render-time guard:
  - Accept existing local same-page anchors.
  - Accept existing sibling article hrefs through `_saved_article_read_next_cluster_href(...)`.
  - Accept only these new generated-site patterns:
    - `index.html#saved-article-organization-group-<safe-group-key>`
    - `index.html#saved-article-library-card-<safe-story-id>`
  - Reject external URLs, protocol-relative URLs, absolute paths, dot-prefixed paths, whitespace, `javascript:`, `data:`, unknown fragments, and slash-containing page paths other than exact `index.html`.

## Acceptance Criteria

- Each generated `articles/<story-id>.html` with a valid companion and organization match shows a "Filed In / 内容归档" trail.
- The trail links to the exact saved article library organization group anchor and exact saved article library card anchor for the current article.
- Target anchors exist in generated `articles/index.html`; article page hrefs use `index.html#...` because the library page is a sibling of `articles/<story-id>.html`.
- Existing local companion same-page links and related item links keep their current behavior.
- Source shelf links are not included in Stage 379 because current source route anchors are display-text-derived and not stable enough for this contract.
- No new JSON artifact, standalone HTML page, route family, schema field, app/runtime/manifest key, source collection behavior, fetching behavior, extraction behavior, matching behavior, scoring behavior, ranking behavior, LLM behavior, connector behavior, scheduling behavior, analytics behavior, personalization behavior, recommendation behavior, or compliance-review product feature is added.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-379-plan-review.md`
- Create: `docs/reviews/opencode-stage-379-plan-review.md`
- Modify if needed: `docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 379 Saved Local Article Cross-Surface Organization Trail plan in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md, src/fashion_radar/row_one/saved_article_local_reading_companion.py, src/fashion_radar/row_one/templates.py around render_saved_article_library_html, _render_saved_article_library_source, _render_saved_article_library_card, _render_saved_article_content_organization_group, _render_saved_article_local_reading_companion_current, and _saved_article_local_reading_companion_href, tests/test_row_one_saved_article_local_reading_companion.py, tests/test_row_one_render.py, tests/test_workflows.py, and tests/test_row_one_docs.py. Goal: add generated-site-only Filed In / 内容归档 organization trail links from articles/<story-id>.html to existing articles/index.html organization group and library card anchors. Technical stack: Python dataclasses, templates.py HTML helpers, pytest, ruff, uv. Implementation method: extend existing local reading companion view model with optional trail links, add stable anchors to existing generated HTML library surfaces, render inside existing companion, validate hrefs at render time, add tests/docs/workflow boundaries. Check feasibility, anchor correctness, href context, generated-site-only boundaries, test coverage, docs, and duplication with existing ROW ONE surfaces. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-379-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains a complete review body ending with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 379 Saved Local Article Cross-Surface Organization Trail plan. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-379-plan-review.md if present, docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md, src/fashion_radar/row_one/saved_article_local_reading_companion.py, src/fashion_radar/row_one/templates.py around saved article library rendering, saved article content organization rendering, and saved article local reading companion rendering, tests/test_row_one_saved_article_local_reading_companion.py, tests/test_row_one_render.py, tests/test_workflows.py, and tests/test_row_one_docs.py. Check feasibility, stable anchor derivation, generated-site-only boundaries, href safety, test coverage, docs boundaries, and whether this duplicates existing ROW ONE surfaces. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-379-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update this plan and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 379 Saved Local Article Cross-Surface Organization Trail plan after fixes. Read the plan and review records. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-379-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 379 Saved Local Article Cross-Surface Organization Trail plan after fixes. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-379-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Modify: `tests/test_row_one_saved_article_local_reading_companion.py`

- [ ] **Step 1: Add failing test for filing links**

Add a test near the existing companion match test:

```python
def test_build_local_reading_companion_adds_cross_surface_organization_trail_links() -> None:
    current_id = "the-row-signal-1234567890"
    peer_id = "alaia-signal-1234567890"

    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id, title="The Row signal"), _entry(peer_id)),
        organization=_organization(_card(current_id, title="The Row card"), _card(peer_id)),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html",
            f"details/{peer_id}.html": f"{peer_id}.html",
        },
    )

    assert companion is not None
    assert [(link.label.en, link.href) for link in companion.filing_links] == [
        ("Library organization group", "index.html#saved-article-organization-group-entities"),
        ("Saved article library card", f"index.html#saved-article-library-card-{current_id}"),
    ]
    assert [link.label.zh for link in companion.filing_links] == [
        "文章库整理分组",
        "文章库卡片",
    ]
```

- [ ] **Step 2: Run the focused test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py::test_build_local_reading_companion_adds_cross_surface_organization_trail_links -q
```

Expected: FAIL because `filing_links` does not exist.

- [ ] **Step 3: Add failing unsafe group-key filtering test**

Add a test that invalid group keys do not create unsafe organization links:

```python
def test_build_local_reading_companion_omits_unsafe_organization_group_trail_link() -> None:
    current_id = "the-row-signal-1234567890"
    companion = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id)),
        organization=RowOneSavedArticleContentOrganization(
            groups=[
                RowOneSavedArticleContentOrganizationGroup(
                    key="../bad",
                    title=_lt("Bad", "坏"),
                    dek=_lt("Bad", "坏"),
                    cards=[_card(current_id)],
                )
            ]
        ),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html"
        },
    )

    assert companion is not None
    assert [link.href for link in companion.filing_links] == [
        f"index.html#saved-article-library-card-{current_id}"
    ]
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py::test_build_local_reading_companion_omits_unsafe_organization_group_trail_link -q
```

Expected: FAIL until unsafe group-key filtering exists.

- [ ] **Step 4: Add failing group-key boundary test**

Add a test that accepts existing underscore-style internal keys and rejects digit/hyphen starts:

```python
def test_build_local_reading_companion_filters_cross_surface_group_key_boundaries() -> None:
    current_id = "the-row-signal-1234567890"
    accepted = build_row_one_saved_article_local_reading_companion(
        story=_story(current_id),
        local_article=_local_article(current_id),
        library=_library(_entry(current_id)),
        organization=RowOneSavedArticleContentOrganization(
            groups=[
                RowOneSavedArticleContentOrganizationGroup(
                    key="top_stories",
                    title=_lt("Top Stories", "今日重点"),
                    dek=_lt("Top context", "重点上下文"),
                    cards=[_card(current_id)],
                )
            ]
        ),
        local_article_page_hrefs_by_detail_path={
            f"details/{current_id}.html": f"{current_id}.html"
        },
    )

    assert accepted is not None
    assert accepted.filing_links[0].href == (
        "index.html#saved-article-organization-group-top_stories"
    )

    for unsafe_key in ("1bad", "-bad"):
        rejected = build_row_one_saved_article_local_reading_companion(
            story=_story(current_id),
            local_article=_local_article(current_id),
            library=_library(_entry(current_id)),
            organization=RowOneSavedArticleContentOrganization(
                groups=[
                    RowOneSavedArticleContentOrganizationGroup(
                        key=unsafe_key,
                        title=_lt("Bad", "坏"),
                        dek=_lt("Bad", "坏"),
                        cards=[_card(current_id)],
                    )
                ]
            ),
            local_article_page_hrefs_by_detail_path={
                f"details/{current_id}.html": f"{current_id}.html"
            },
        )
        assert rejected is not None
        assert rejected.filing_links == (
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Saved article library card", zh="文章库卡片"),
                href=f"index.html#saved-article-library-card-{current_id}",
            ),
        )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py::test_build_local_reading_companion_filters_cross_surface_group_key_boundaries -q
```

Expected: FAIL until group-key boundary filtering exists.

## Task 3: Builder Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/saved_article_local_reading_companion.py`

- [ ] **Step 1: Add trail link dataclass and companion field**

Add this dataclass after `RowOneSavedArticleLocalReadingCompanionLink`:

```python
@dataclass(frozen=True)
class RowOneSavedArticleLocalReadingCompanionTrailLink:
    label: LocalizedText
    href: str
```

Add this field to `RowOneSavedArticleLocalReadingCompanion` after `related_items`:

```python
    filing_links: tuple[RowOneSavedArticleLocalReadingCompanionTrailLink, ...] = ()
```

- [ ] **Step 2: Add safe anchor constants and helpers**

Add constants near existing fragment constants:

```python
_ORGANIZATION_GROUP_PREFIX = "saved-article-organization-group-"
_LIBRARY_CARD_PREFIX = "saved-article-library-card-"
```

Add helpers:

```python
def _filing_links(
    *,
    current_detail_path: str,
    group: RowOneSavedArticleContentOrganizationGroup,
) -> tuple[RowOneSavedArticleLocalReadingCompanionTrailLink, ...]:
    links: list[RowOneSavedArticleLocalReadingCompanionTrailLink] = []
    group_href = _organization_group_href(group.key)
    if group_href is not None:
        links.append(
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Library organization group", zh="文章库整理分组"),
                href=group_href,
            )
        )
    card_href = _library_card_href_from_detail_path(current_detail_path)
    if card_href is not None:
        links.append(
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Saved article library card", zh="文章库卡片"),
                href=card_href,
            )
        )
    return tuple(links)
```

Use private helpers to validate group keys and detail-derived story ids. Keep them local to the companion module so the builder does not import template internals. Do not generate the card href from raw `story.id`; the builder has already computed `current_detail_path`, and that canonical path must be the source for the card href.

- [ ] **Step 3: Attach filing links in builder**

Pass the links into the companion:

```python
        filing_links=_filing_links(current_detail_path=current_detail_path, group=group),
```

- [ ] **Step 4: Run builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_reading_companion.py -q
```

Expected: PASS.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add direct render test for filing trail**

Add a test near `test_render_local_article_page_includes_saved_article_local_reading_companion`:

```python
def test_render_local_article_page_includes_cross_surface_organization_trail() -> None:
    edition = _edition()
    story = edition.stories[0]
    companion = RowOneSavedArticleLocalReadingCompanion(
        current_title=LocalizedText(en="The Row signal", zh="The Row signal"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        group_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        group_dek=LocalizedText(en="Brand context", zh="品牌上下文"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        body_source_label=LocalizedText(en="Extracted article text", zh="提取正文"),
        lead=LocalizedText(en="Lead", zh="导语"),
        saved_paragraph_count=2,
        organized_section_count=1,
        evidence_count=1,
        detail_path=story.detail_path,
        local_links=(),
        related_items=(),
        filing_links=(
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Library organization group", zh="文章库整理分组"),
                href="index.html#saved-article-organization-group-entities",
            ),
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Saved article library card", zh="文章库卡片"),
                href=f"index.html#saved-article-library-card-{story.id}",
            ),
        ),
    )

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_local_reading_companion=companion,
    )
    section_html = _html_between(
        html,
        '<section class="saved-article-local-reading-companion"',
        'id="local-article"',
    )

    assert "saved-article-local-reading-companion-filing-trail" in section_html
    assert 'href="index.html#saved-article-organization-group-entities"' in section_html
    assert f'href="index.html#saved-article-library-card-{story.id}"' in section_html
    assert "Filed In" in section_html
    assert "内容归档" in section_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_local_article_page_includes_cross_surface_organization_trail -q
```

Expected: FAIL until template imports/dataclass/rendering exist.

- [ ] **Step 2: Add full-site anchor resolution test**

Add a full-site test near existing local article page generation tests:

```python
def test_render_row_one_site_writes_saved_article_cross_surface_organization_trail_targets(
    tmp_path: Path,
) -> None:
    current = _edition().stories[0]
    peer = _detail_story("alaia-signal-1234567890", "Alaia signal")
    edition = _edition_with_stories(current, peer)
    peer_article = _signal_briefing_local_article().model_copy(
        deep=True,
        update={
            "story_id": peer.id,
            "title": "Alaia source article",
            "source_name": "Alaia Desk",
            "url": "https://example.com/alaia",
        },
    )
    articles = {
        current.id: _signal_briefing_local_article(),
        peer.id: peer_article,
    }

    render_row_one_site(edition, tmp_path, local_articles_by_story_id=articles)

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    article_html = (tmp_path / "articles" / f"{current.id}.html").read_text(encoding="utf-8")
    detail_html = (tmp_path / "details" / f"{current.id}.html").read_text(encoding="utf-8")

    assert 'id="saved-article-organization-group-entities"' in library_html
    assert f'id="saved-article-library-card-{current.id}"' in library_html
    assert 'href="index.html#saved-article-organization-group-entities"' in article_html
    assert f'href="index.html#saved-article-library-card-{current.id}"' in article_html
    assert "saved-article-local-reading-companion-filing-trail" not in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_cross_surface_organization_trail_targets -q
```

Expected: FAIL until target anchors render and builder creates filing links.

- [ ] **Step 3: Add href filtering test**

Add a direct render test with unsafe trail hrefs:

```python
def test_render_local_article_page_filters_unsafe_cross_surface_organization_trail_links() -> None:
    edition = _edition()
    story = edition.stories[0]
    companion = RowOneSavedArticleLocalReadingCompanion(
        current_title=LocalizedText(en="The Row signal", zh="The Row signal"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        group_title=LocalizedText(en="People & Brands", zh="品牌与人物"),
        group_dek=LocalizedText(en="Brand context", zh="品牌上下文"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        body_source_label=LocalizedText(en="Extracted article text", zh="提取正文"),
        lead=LocalizedText(en="Lead", zh="导语"),
        saved_paragraph_count=2,
        organized_section_count=1,
        evidence_count=1,
        detail_path=story.detail_path,
        local_links=(),
        related_items=(),
        filing_links=(
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Unsafe", zh="不安全"),
                href="https://evil.example/path",
            ),
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Unsafe", zh="不安全"),
                href="index.html#unknown-anchor",
            ),
            RowOneSavedArticleLocalReadingCompanionTrailLink(
                label=LocalizedText(en="Safe", zh="安全"),
                href=f"index.html#saved-article-library-card-{story.id}",
            ),
        ),
    )

    html = render_local_article_page_html(
        edition,
        story,
        local_article=_signal_briefing_local_article(),
        saved_article_local_reading_companion=companion,
    )

    assert "https://evil.example" not in html
    assert "unknown-anchor" not in html
    assert f'href="index.html#saved-article-library-card-{story.id}"' in html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_local_article_page_filters_unsafe_cross_surface_organization_trail_links -q
```

Expected: FAIL until render-time href guard accepts only Stage 379 patterns.

- [ ] **Step 4: Add direct library card anchor helper test**

Import `_saved_article_library_card_anchor_id` from `fashion_radar.row_one.templates` with the other template helpers and add:

```python
def test_saved_article_library_card_anchor_id_uses_validated_detail_story_id() -> None:
    story_id = "the-row-signal-1234567890"
    entry = _saved_article_library_fixture().groups[0].entries[0]
    assert _saved_article_library_card_anchor_id(entry) == f"saved-article-library-card-{story_id}"
    assert _saved_article_library_card_anchor_id(
        replace(
            entry,
            digest_path="../bad.html#local-article-digest",
        )
    ) is None
```

This uses the existing `_saved_article_library_fixture()` and `replace` import in `tests/test_row_one_render.py`; do not create a new `_story`, `_local_article`, `_edition`, or `_saved_article_library_entry` fixture family in that file.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_saved_article_library_card_anchor_id_uses_validated_detail_story_id -q
```

Expected: FAIL until `_saved_article_library_card_anchor_id(...)` exists.

- [ ] **Step 5: Add builder-to-anchor agreement test**

Add `build_row_one_saved_article_local_reading_companion` to the existing import from `fashion_radar.row_one.saved_article_local_reading_companion`, then add:

```python
def test_saved_article_cross_surface_card_href_matches_library_card_anchor() -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = _signal_briefing_local_article()
    library = _saved_article_library_fixture()
    organization = build_row_one_saved_article_content_organization(
        edition,
        {story.id: local_article},
    )

    companion = build_row_one_saved_article_local_reading_companion(
        story=story,
        local_article=local_article,
        library=library,
        organization=organization,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
    )

    entry = library.groups[0].entries[0]
    card_anchor = _saved_article_library_card_anchor_id(entry)

    assert companion is not None
    assert card_anchor == "saved-article-library-card-the-row-signal-1234567890"
    assert f"index.html#{card_anchor}" in {link.href for link in companion.filing_links}
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_saved_article_cross_surface_card_href_matches_library_card_anchor -q
```

Expected: FAIL until the builder derives the card href from the validated detail path and the template helper derives the card anchor from `entry.digest_path` with the same canonical logic.

## Task 5: Template Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Import the new trail link dataclass**

Add `RowOneSavedArticleLocalReadingCompanionTrailLink` to the existing import from `saved_article_local_reading_companion`.

- [ ] **Step 2: Add stable organization group anchors**

In `_render_saved_article_content_organization_group(...)`, compute:

```python
group_anchor = _saved_article_content_organization_group_anchor_id(group.key)
group_id_attr = f' id="{_esc(group_anchor)}"' if group_anchor else ""
```

and render:

```python
<article class="saved-article-content-organization-group"{group_id_attr}>
```

Add `_saved_article_content_organization_group_anchor_id(...)` near the content organization helpers and keep it strict.

- [ ] **Step 3: Add stable saved article library card anchors**

In `_render_saved_article_library_card(...)`, compute:

```python
card_anchor = _saved_article_library_card_anchor_id(entry)
card_id_attr = f' id="{_esc(card_anchor)}"' if card_anchor else ""
```

and render:

```python
<article class="saved-article-library-card"{card_id_attr}>
```

Add `_saved_article_library_card_anchor_id(...)` near `_saved_article_library_entry_detail_path(...)`, but do not call `_saved_article_library_entry_detail_path(...)` because that helper checks `reader_path` before `digest_path`. The card anchor must use `entry.digest_path` only, validate it with `safe_row_one_detail_fragment_href(entry.digest_path, "local-article-digest")`, derive the `details/<story-id>.html` path from that safe digest href, and validate the extracted story id with `safe_local_article_story_id(...)`.

- [ ] **Step 4: Render the filing trail**

Add `_render_saved_article_local_reading_companion_filing_trail(...)` and call it from `_render_saved_article_local_reading_companion_current(...)` after the local same-page links and before references:

```python
filing_trail = _render_saved_article_local_reading_companion_filing_trail(
    companion.filing_links
)
...
{links}{filing_trail}{refs}
```

The trail HTML should use:

```html
<div class="saved-article-local-reading-companion-filing-trail" aria-label="Saved article filing trail">
  <strong><span data-lang="en">Filed In</span><span data-lang="zh">内容归档</span></strong>
  ...
</div>
```

The updated current companion skeleton must keep the trail inside the current `<article>` and before references:

```python
return f"""      <article class="saved-article-local-reading-companion-current">
        ...
{links}{filing_trail}{refs}
      </article>"""
```

The filing-trail renderer must not reuse `_render_saved_article_local_reading_companion_links(...)` or its `href.startswith("#")` filter. It should keep any link whose href passes `_saved_article_local_reading_companion_href(...)` and starts with the new `index.html#` cross-surface pattern.

- [ ] **Step 5: Extend href validation**

Update `_saved_article_local_reading_companion_href(...)` to call a new `_saved_article_local_reading_companion_cross_surface_href(...)` before falling through to `_saved_article_read_next_cluster_href(...)`.

The new helper must accept only:

```text
index.html#saved-article-organization-group-<safe-group-key>
index.html#saved-article-library-card-<safe-story-id>
```

- [ ] **Step 6: Add CSS**

Extend the existing companion CSS block:

```css
.saved-article-local-reading-companion-filing-trail {
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 10px;
}
.saved-article-local-reading-companion-filing-trail strong,
.saved-article-local-reading-companion-filing-trail a {
  border: 1px solid var(--line);
  font-size: 0.75rem;
  padding: 7px 9px;
  text-decoration: none;
}
.saved-article-local-reading-companion-filing-trail strong {
  color: var(--ink);
}
.saved-article-local-reading-companion-filing-trail a {
  color: var(--accent);
  font-weight: 800;
}
```

- [ ] **Step 7: Run focused render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_local_article_page_includes_cross_surface_organization_trail \
  tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_cross_surface_organization_trail_targets \
  tests/test_row_one_render.py::test_render_local_article_page_filters_unsafe_cross_surface_organization_trail_links \
  tests/test_row_one_render.py::test_saved_article_library_card_anchor_id_uses_validated_detail_story_id \
  tests/test_row_one_render.py::test_saved_article_cross_surface_card_href_matches_library_card_anchor \
  -q
```

Expected: PASS.

## Task 6: Generated-Site-Only Guards And Docs

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add Stage 379 no-leakage render assertions**

Add denylist strings near existing generated-site-only render tests:

```python
for forbidden in (
    "saved_local_article_cross_surface_organization_trail",
    "local_article_cross_surface_organization_trail",
    "cross_surface_organization_trail",
    "saved-local-article-cross-surface-organization-trail",
    "Saved Local Article Cross-Surface Organization Trail",
):
    assert forbidden not in edition_json
    assert forbidden not in runtime_json
    assert forbidden not in manifest_json
```

Also assert no artifacts are created with stems:

```python
(
    "saved-local-article-cross-surface-organization-trail",
    "local-article-cross-surface-organization-trail",
    "cross-surface-organization-trail",
    "saved_local_article_cross_surface_organization_trail",
    "local_article_cross_surface_organization_trail",
    "cross_surface_organization_trail",
)
```

- [ ] **Step 2: Add workflow sentinel coverage**

Add `from dataclasses import replace` to `tests/test_workflows.py`. Extend `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` with the same contract denylist and artifact stems. The render orchestration module `src/fashion_radar/row_one/render.py` imports `build_row_one_saved_article_local_reading_companion` directly and `_write_local_article_pages(...)` calls that module attribute, so patch `row_one_render.build_row_one_saved_article_local_reading_companion` with `raising=True`. Add:

```python
def test_stage_379_saved_local_article_cross_surface_organization_trail_stays_generated_site_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fashion_radar.row_one import render as row_one_render

    original_builder = row_one_render.build_row_one_saved_article_local_reading_companion

    def _without_filing_links(**kwargs):
        companion = original_builder(**kwargs)
        if companion is None:
            return None
        return replace(companion, filing_links=())

    monkeypatch.setattr(
        row_one_render,
        "build_row_one_saved_article_local_reading_companion",
        _without_filing_links,
        raising=True,
    )

    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

Expected: the test proves removing only the new filing links does not change app-facing JSON, local SQLite behavior, or generated artifact families.

- [ ] **Step 3: Add docs boundary test**

Add `test_row_one_docs_describe_stage_379_cross_surface_organization_trail_boundary` above the Stage 378 docs test. Required paragraph:

```text
Stage 379 adds generated-site only Saved Local Article Cross-Surface Organization Trail links inside the existing Saved Article Local Reading Companion on `articles/<story-id>.html`; it reuses existing saved article library groups, existing saved article content organization groups, generated local article page routes, existing article library cards, and existing saved article library organization groups to link each local article back to its Filed In / 内容归档 context; it does not create `data/saved-local-article-cross-surface-organization-trail.json`, does not create `data/local-article-cross-surface-organization-trail.json`, does not create `data/cross-surface-organization-trail.json`, does not create `saved-local-article-cross-surface-organization-trail.html`, does not create `local-article-cross-surface-organization-trail.html`, does not create `cross-surface-organization-trail.html`, does not create source shelf links, does not create new article-source sidecars, does not create new route families, does not alter `details/<story-id>.html`, does not publish full articles outside existing local article pages, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, generated JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

Assert the paragraph appears before `"Stage 378 adds"` in both README and docs. Scope stale-phrase checks to the Stage 379 paragraph or Stage 379 slice, not the entire file.

- [ ] **Step 4: Add the same paragraph to docs**

Insert the Stage 379 paragraph above Stage 378 in:

```text
README.md
docs/row-one.md
```

- [ ] **Step 5: Run focused docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_379_cross_surface_organization_trail_boundary \
  tests/test_workflows.py::test_stage_379_saved_local_article_cross_surface_organization_trail_stays_generated_site_only \
  -q
```

Expected: PASS.

## Task 7: Review, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-379-code-review.md`
- Create: `docs/reviews/opencode-stage-379-code-review.md`
- Modify if needed based on review findings.

- [ ] **Step 1: Run focused Stage 379 tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_local_reading_companion.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_stage_379_saved_local_article_cross_surface_organization_trail_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_379_cross_surface_organization_trail_boundary \
  -q
```

Expected: PASS.

- [ ] **Step 2: Run Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 379 code changes in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md, git diff HEAD, src/fashion_radar/row_one/saved_article_local_reading_companion.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_saved_article_local_reading_companion.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Goal: generated-site-only Filed In / 内容归档 cross-surface organization trail from local article pages to existing articles/index.html organization groups and library cards. Check correctness, href safety, anchor existence, generated-site-only boundaries, docs, and tests. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-379-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings.

- [ ] **Step 3: Run opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 379 code changes. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-379-code-review.md if present, docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md, git diff HEAD, src/fashion_radar/row_one/saved_article_local_reading_companion.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_saved_article_local_reading_companion.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-379-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings.

- [ ] **Step 4: Fix Critical and Important code findings**

If either reviewer raises Critical or Important findings, fix them, run focused tests, and capture rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 379 code fixes. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-379-code-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 379 code fixes. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-379-code-rereview.md
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
git add \
  src/fashion_radar/row_one/saved_article_local_reading_companion.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_local_reading_companion.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md \
  docs/superpowers/plans/2026-07-10-stage-379-saved-local-article-cross-surface-trail-plan.md \
  docs/reviews/claude-code-stage-379-plan-review.md \
  docs/reviews/opencode-stage-379-plan-review.md \
  docs/reviews/claude-code-stage-379-code-review.md \
  docs/reviews/opencode-stage-379-code-review.md
git commit -m "Stage 379: add cross-surface organization trail"
git push origin main
```

Expected: commit is pushed to GitHub, and `git status --short --branch` is clean.

## Handoff Summary Template

At node end, write:

```text
Handoff Summary
- Repo status:
- Commit:
- Verified commands:
- Review records:
- Unsubmitted/uncommitted files:
- Next step:
```
