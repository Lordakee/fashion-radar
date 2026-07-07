# Stage 338 ROW ONE Saved Article Paragraph Evidence Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Saved Article Paragraph Evidence Board to `articles/index.html` using only already-saved local article sidecars and existing content-organization paragraph indices.

**Architecture:** Create a focused private builder that derives a capped view model from `RowOneEdition`, `RowOneSavedArticleLibrary`, `RowOneSavedArticleContentOrganization`, and `local_articles_by_story_id`. `RowOneEdition.stories` supplies the authoritative current-edition detail-path-to-story-id mapping; saved library entries supply the canonical generated local-page allowlist; content-organization cards supply the group spine and paragraph indices. Wire the board through `render_row_one_site()` into `render_saved_article_library_html()`, render it after reading paths and before content organization, and keep app/runtime/manifest/schema/JSON contracts unchanged.

**Tech Stack:** Python dataclasses, existing Pydantic ROW ONE models, deterministic template rendering in `src/fashion_radar/row_one/templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_evidence_board.py`
  - Defines `RowOneSavedArticleEvidenceBoard`, group/card dataclasses, constants, and `build_row_one_saved_article_evidence_board()`.
  - Owns route mapping, paragraph validation, item-level reference matching, excerpt caps, and deterministic output caps.
- Create `tests/test_row_one_saved_article_evidence_board.py`
  - Builder-only unit tests for grouping, route mapping, library-route consistency, caps, safety, dedupe, excerpting, and reference attachment.
- Modify `src/fashion_radar/row_one/render.py`
  - Import the builder/view model.
  - Build the evidence board after reading paths and before page write.
  - Pass it into `_write_saved_article_library_page()`.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept the evidence board in `render_saved_article_library_html()`.
  - Render the section after reading paths and before content organization.
  - Revalidate paragraph hrefs before prefixing `../`.
  - Add CSS selectors for the new section.
- Modify `tests/test_row_one_render.py`
  - Add imports, direct render tests, full-site tests, order tests, contract guards, omission tests, unsafe href render tests, and CSS selector tests.
- Modify `tests/test_workflows.py`
  - Extend generated-site-only workflow contract guards with Stage 338 vocabulary.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 338 boundary sentinel.
- Modify `README.md` and `docs/row-one.md`
  - Add the Stage 338 generated-site-only boundary paragraph above Stage 337.

## Task 1: Builder Tests And View Model

**Files:**
- Create: `tests/test_row_one_saved_article_evidence_board.py`
- Create: `src/fashion_radar/row_one/saved_article_evidence_board.py`

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_row_one_saved_article_evidence_board.py` with concrete fixtures:

```python
from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_evidence_board import (
    SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS,
    build_row_one_saved_article_evidence_board,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)

AS_OF = datetime(2026, 7, 8, 4, 0, tzinfo=UTC)


def _localized(value: str) -> LocalizedText:
    return LocalizedText(zh=value, en=value)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key="top_stories",
        story_type="tracked_entity",
        headline="The Row signal",
        summary=_localized("Summary"),
        why_it_matters=_localized("Why"),
        editorial_takeaway=_localized("Takeaway"),
        signal_context=_localized("Signal"),
        reader_path=_localized("Reader"),
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=["brand"],
        evidence=[],
    )


def _edition(story: RowOneStory | None = None) -> RowOneEdition:
    active_story = story or _story()
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        summary=_localized("Daily summary"),
        sections=[RowOneSection(key="top_stories", title=_localized("Top Stories"))],
        stories=[active_story],
    )


def _article(story_id: str = "the-row-signal-1234567890") -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title="The Row saved article",
        source_name="Vogue Business",
        url="https://example.com/the-row",
        published_at=AS_OF,
        paragraphs=[
            "The Row paragraph one anchors the saved local evidence board.",
            "Alaia flats paragraph two carries a product reference.",
            "Dover Street Market paragraph three is source context.",
            "Long paragraph " + ("detail " * 80),
        ],
        brief_sections=[],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=_localized("Read First"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=_localized("Desk note"),
                        body=_localized("The Row board lead"),
                        paragraph_indices=[0, True, 0, 99],
                        references=[
                            RowOneReference(name="The Row", type="brand", label="tracked")
                        ],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=_localized("Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=_localized("Product note"),
                        body=_localized("Alaia board lead"),
                        paragraph_indices=[1],
                        references=[
                            RowOneReference(name="Alaia flats", type="shoe", label="product")
                        ],
                    ),
                    RowOneLocalArticleContentItem(
                        label=_localized("Long note"),
                        body=_localized("Long board lead"),
                        paragraph_indices=[3],
                        references=[
                            RowOneReference(name="The Row bag", type="bag", label="product")
                        ],
                    ),
                ],
            ),
        ],
        body_source="extracted",
    )
```

Add tests with complete assertions:

```python
def test_saved_article_evidence_board_builds_groups_from_referenced_paragraphs() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization(story.detail_path),
        {story.id: _article(story.id)},
    )

    assert board is not None
    assert board.group_count == 2
    assert board.card_count == 3
    assert board.source_count == 1
    assert [group.key for group in board.groups] == ["takeaways", "product_signals"]
    assert board.groups[0].cards[0].paragraph_number == 1
    assert board.groups[0].cards[0].href == (
        "details/the-row-signal-1234567890.html#local-article-paragraph-1"
    )
    assert board.groups[0].cards[0].excerpt.en == (
        "The Row paragraph one anchors the saved local evidence board."
    )
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["The Row"]


def test_saved_article_evidence_board_omits_empty_inputs() -> None:
    story = _story()
    article = _article(story.id)
    assert build_row_one_saved_article_evidence_board(None, _library(story.detail_path), _organization(story.detail_path), {story.id: article}) is None
    assert build_row_one_saved_article_evidence_board(_edition(story), None, _organization(story.detail_path), {story.id: article}) is None
    assert build_row_one_saved_article_evidence_board(_edition(story), _library(story.detail_path), None, {story.id: article}) is None
    assert build_row_one_saved_article_evidence_board(_edition(story), _library(story.detail_path), _organization(story.detail_path), {}) is None


def test_saved_article_evidence_board_rejects_unsafe_and_unmatched_routes() -> None:
    story = _story()
    unsafe = _organization("javascript:alert(1)#local-article-content-section-1")
    traversal = _organization("details/../the-row-signal-1234567890.html#local-article-content-section-1")
    wrong_fragment = _organization(f"{story.detail_path}#local-article-content-section-01")
    unmatched = _organization("details/other-signal-1234567890.html#local-article-content-section-1")
    for organization in (unsafe, traversal, wrong_fragment, unmatched):
        assert (
            build_row_one_saved_article_evidence_board(
                _edition(story),
                _library(story.detail_path),
                organization,
                {story.id: _article(story.id)},
            )
            is None
        )


def test_saved_article_evidence_board_requires_consistent_library_routes() -> None:
    story = _story()
    corrupted = _library(
        story.detail_path,
        reader_path="details/other-signal-1234567890.html#local-article-reader",
    )
    assert (
        build_row_one_saved_article_evidence_board(
            _edition(story),
            corrupted,
            _organization(story.detail_path),
            {story.id: _article(story.id)},
        )
        is None
    )


def test_saved_article_evidence_board_dedupes_rejects_bool_indices_and_caps_cards() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_with_many_duplicate_cards(story.detail_path),
        {story.id: _article(story.id)},
    )
    assert board is not None
    assert len(board.groups[0].cards) == 3
    assert [card.paragraph_number for card in board.groups[0].cards] == [1, 2, 4]


def test_saved_article_evidence_board_caps_long_excerpts_without_full_republication() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [3]),
        {story.id: _article(story.id)},
    )
    assert board is not None
    excerpt = board.groups[0].cards[0].excerpt.en
    assert len(excerpt) <= SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS + 3
    assert excerpt.endswith("...")
    assert "detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail detail" not in excerpt


def test_saved_article_evidence_board_uses_item_references_for_matching_paragraph() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [1]),
        {story.id: _article(story.id)},
    )
    assert board is not None
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["Alaia flats"]


def test_saved_article_evidence_board_falls_back_to_card_references_when_no_item_reference_matches() -> None:
    story = _story()
    board = build_row_one_saved_article_evidence_board(
        _edition(story),
        _library(story.detail_path),
        _organization_for_section(story.detail_path, "product_signals", 2, [2]),
        {story.id: _article(story.id)},
    )
    assert board is not None
    assert [ref.name for ref in board.groups[0].cards[0].references] == ["Fallback"]
```

Helper fixtures required in the test file:

```python
def _library(
    detail_path: str,
    *,
    reader_path: str | None = None,
    digest_path: str | None = None,
    evidence_path: str | None = None,
) -> RowOneSavedArticleLibrary:
    entry = RowOneSavedArticleLibraryEntry(
        title=_localized("The Row saved article"),
        source_name="Vogue Business",
        section_title=_localized("Top Stories"),
        saved_paragraph_count=4,
        organized_section_count=2,
        body_source="extracted",
        digest_path=digest_path or f"{detail_path}#local-article-digest",
        reader_path=reader_path or f"{detail_path}#local-article-reader",
        evidence_path=evidence_path or f"{detail_path}#local-article-paragraph-evidence",
        paragraph_links=(),
        references=(),
    )
    return RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=4,
        organized_section_count=2,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=4,
                organized_section_count=2,
                entries=[entry],
            )
        ],
    )


def _organization(detail_path: str) -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=_localized("Read First"),
                dek=_localized("Start here"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized("Read First"),
                        lead=_localized("The Row board lead"),
                        detail_path=f"{detail_path}#local-article-content-section-1",
                        paragraph_indices=(0, True, 0, 99),
                        references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
                    )
                ],
            ),
            RowOneSavedArticleContentOrganizationGroup(
                key="product_signals",
                title=_localized("Products"),
                dek=_localized("Product evidence"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized("Products"),
                        lead=_localized("Alaia board lead"),
                        detail_path=f"{detail_path}#local-article-content-section-2",
                        paragraph_indices=(1, 3),
                        references=(RowOneReference(name="Fallback", type="source", label="fallback"),),
                    )
                ],
            ),
        ]
    )


def _organization_for_section(
    detail_path: str,
    group_key: str,
    section_number: int,
    paragraph_indices: list[int],
) -> RowOneSavedArticleContentOrganization:
    group_title = "Read First" if group_key == "takeaways" else "Products"
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key=group_key,
                title=_localized(group_title),
                dek=_localized("Evidence"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=_localized("The Row saved article"),
                        source_name="Vogue Business",
                        section_title=_localized("Top Stories"),
                        section_label=_localized(group_title),
                        lead=_localized("Evidence lead"),
                        detail_path=f"{detail_path}#local-article-content-section-{section_number}",
                        paragraph_indices=tuple(paragraph_indices),
                        references=(RowOneReference(name="Fallback", type="source", label="fallback"),),
                    )
                ],
            )
        ]
    )


def _organization_with_many_duplicate_cards(detail_path: str) -> RowOneSavedArticleContentOrganization:
    cards = []
    for indices in (
        (0, True, 0, 99),
        (1,),
        (1,),
        (3,),
        (2,),
    ):
        cards.append(
            RowOneSavedArticleContentOrganizationCard(
                title=_localized("The Row saved article"),
                source_name="Vogue Business",
                section_title=_localized("Top Stories"),
                section_label=_localized("Read First"),
                lead=_localized("Evidence lead"),
                detail_path=f"{detail_path}#local-article-content-section-1",
                paragraph_indices=indices,
                references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
            )
        )
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=_localized("Read First"),
                dek=_localized("Start here"),
                cards=cards,
            )
        ]
    )
```

- [ ] **Step 2: Run builder tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_evidence_board.py -q
```

Expected: import failure because `saved_article_evidence_board.py` does not exist yet.

- [ ] **Step 3: Implement builder dataclasses and constants**

Create `src/fashion_radar/row_one/saved_article_evidence_board.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

MAX_SAVED_ARTICLE_EVIDENCE_BOARD_GROUPS = 4
MAX_SAVED_ARTICLE_EVIDENCE_BOARD_CARDS_PER_GROUP = 3
MAX_SAVED_ARTICLE_EVIDENCE_BOARD_REFERENCES = 4
SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS = 220

_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(
    r"^local-article-content-section-([1-9][0-9]*)$"
)


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoardCard:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    paragraph_number: int
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoardGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    card_count: int
    source_count: int
    cards: tuple[RowOneSavedArticleEvidenceBoardCard, ...]


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoard:
    group_count: int
    card_count: int
    source_count: int
    groups: tuple[RowOneSavedArticleEvidenceBoardGroup, ...]
```

- [ ] **Step 4: Implement safe paragraph evidence construction**

Implement this exact public signature:

```python
def build_row_one_saved_article_evidence_board(
    edition: RowOneEdition | None,
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleEvidenceBoard | None:
```

Implementation requirements:

- return `None` when `edition`, `library`, `organization`, or `local_articles_by_story_id` is empty;
- `_library_detail_paths(library)` must include an entry only when `reader_path`, `digest_path`, and `evidence_path` all validate with their expected fragments and all resolve to the same base detail path;
- `_local_articles_by_detail_path(edition, local_articles_by_story_id, allowed_detail_paths)` must map safe `story.detail_path` to the article only when `article.story_id == story.id` and `story.detail_path in allowed_detail_paths`;
- `_safe_content_section_href(card.detail_path)` must accept only `details/<safe>.html#local-article-content-section-N` where `N >= 1` and has no leading zero;
- `_section_for_card(article, section_number)` must return `article.content_sections[section_number - 1]` only when that index exists;
- `_valid_paragraph_indices(card.paragraph_indices, article.paragraphs)` must reject booleans, non-ints, out-of-range values, blank paragraphs, and duplicates;
- `_references_for_paragraph(section, paragraph_index, fallback)` must first collect references from section items whose paragraph indices include `paragraph_index`, dedupe by normalized name/type/label, cap at `MAX_SAVED_ARTICLE_EVIDENCE_BOARD_REFERENCES`, and only then fall back to deduped `fallback`;
- `_excerpt(paragraph)` must normalize whitespace, cap at `SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS`, `rstrip()`, and append `...` only when truncated;
- each card href must be `f"{detail_path}#local-article-paragraph-{paragraph_index + 1}"`;
- dedupe cards by `(group.key, detail_path, paragraph_index)`;
- source counts must use normalized source names;
- group and card caps must be enforced.

- [ ] **Step 5: Run builder tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_evidence_board.py -q
```

Expected: all builder tests pass.

## Task 2: Render Wiring And Template

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

In `tests/test_row_one_render.py`, import:

```python
from fashion_radar.row_one.saved_article_evidence_board import (
    RowOneSavedArticleEvidenceBoard,
    RowOneSavedArticleEvidenceBoardCard,
    RowOneSavedArticleEvidenceBoardGroup,
)
```

Add helper:

```python
def _saved_article_evidence_board_section_html(html: str) -> str:
    marker = '<section class="saved-article-evidence-board"'
    start = html.index(marker)
    tail = html[start:]
    content_organization = tail.find('<section class="saved-article-content-organization"')
    library_grid = tail.find('<div class="saved-article-library-grid">')
    end_candidates = [index for index in (content_organization, library_grid) if index >= 0]
    end = min(end_candidates) if end_candidates else len(tail)
    return tail[:end]
```

Add tests:

```python
def test_render_row_one_site_includes_saved_article_evidence_board_in_article_library(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _evidence_board_local_article()},
    )
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_evidence_board_section_html(library_html)

    assert 'class="saved-article-evidence-board"' in section_html
    assert "Saved Article Paragraph Evidence Board" in section_html
    assert "保存文章段落证据板" in section_html
    assert "Read First" in section_html
    assert "Paragraph 1" in section_html
    assert "The Row paragraph one anchors the saved local evidence board." in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "The Row" in section_html
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-evidence-board"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-evidence-board"' not in homepage_html
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_evidence_board" not in contract_json
        assert "paragraph_evidence_board" not in contract_json
        assert "saved-article-evidence-board" not in contract_json
        assert "Saved Article Paragraph Evidence Board" not in contract_json
        assert "保存文章段落证据板" not in contract_json
        assert "The Row paragraph one anchors the saved local evidence board." not in contract_json
    assert not (tmp_path / "data" / "saved-article-evidence-board.json").exists()
```

Also add:

```python
def test_render_row_one_site_omits_saved_article_evidence_board_when_no_valid_paragraphs(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    article = _evidence_board_local_article().model_copy(
        deep=True,
        update={"content_sections": [], "paragraphs": [""]},
    )
    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: article},
    )
    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    assert 'class="saved-article-evidence-board"' not in library_html
    assert "Saved Article Paragraph Evidence Board" not in library_html
    assert 'class="saved-article-library-hero"' in library_html
    assert 'class="saved-article-library-grid"' in library_html


def test_render_saved_article_library_html_renders_saved_article_evidence_board_directly() -> None:
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_evidence_board=RowOneSavedArticleEvidenceBoard(
            group_count=1,
            card_count=1,
            source_count=1,
            groups=(
                RowOneSavedArticleEvidenceBoardGroup(
                    key="takeaways",
                    title=LocalizedText(zh="Read First", en="Read First"),
                    dek=LocalizedText(zh="Evidence", en="Evidence"),
                    card_count=1,
                    source_count=1,
                    cards=(
                        RowOneSavedArticleEvidenceBoardCard(
                            title=LocalizedText(zh="The Row saved article", en="The Row saved article"),
                            source_name="Vogue Business",
                            section_title=LocalizedText(zh="Top Stories", en="Top Stories"),
                            section_label=LocalizedText(zh="Read First", en="Read First"),
                            paragraph_number=1,
                            excerpt=LocalizedText(zh="The Row paragraph one", en="The Row paragraph one"),
                            href="details/the-row-signal-1234567890.html#local-article-paragraph-1",
                            references=(RowOneReference(name="The Row", type="brand", label="tracked"),),
                        ),
                    ),
                ),
            ),
        ),
    )
    section_html = _saved_article_evidence_board_section_html(html)
    assert "Saved Article Paragraph Evidence Board" in section_html
    assert "The Row paragraph one" in section_html
    assert 'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
    assert "The Row" in section_html


def test_render_saved_article_library_html_revalidates_saved_article_evidence_board_links() -> None:
    unsafe_cards = tuple(
        RowOneSavedArticleEvidenceBoardCard(
            title=LocalizedText(zh="Unsafe", en="Unsafe"),
            source_name="Bad Source",
            section_title=LocalizedText(zh="Top Stories", en="Top Stories"),
            section_label=LocalizedText(zh="Read First", en="Read First"),
            paragraph_number=1,
            excerpt=LocalizedText(zh="Unsafe paragraph", en="Unsafe paragraph"),
            href=href,
            references=(),
        )
        for href in (
            "javascript:alert(1)#local-article-paragraph-1",
            "details/../the-row-signal-1234567890.html#local-article-paragraph-1",
            "details/the-row-signal-1234567890.html#local-article-content-section-1",
            "details/the-row-signal-1234567890.html#local-article-paragraph-0",
            "details/the-row-signal-1234567890.html#local-article-paragraph-01",
        )
    )
    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_evidence_board=RowOneSavedArticleEvidenceBoard(
            group_count=1,
            card_count=len(unsafe_cards),
            source_count=1,
            groups=(
                RowOneSavedArticleEvidenceBoardGroup(
                    key="takeaways",
                    title=LocalizedText(zh="Read First", en="Read First"),
                    dek=LocalizedText(zh="Evidence", en="Evidence"),
                    card_count=len(unsafe_cards),
                    source_count=1,
                    cards=unsafe_cards,
                ),
            ),
        ),
    )
    assert "javascript:alert(1)" not in html
    assert "../the-row-signal" not in html
    assert "#local-article-content-section-1" not in html
    assert "#local-article-paragraph-0" not in html
    assert "#local-article-paragraph-01" not in html
    assert 'class="saved-article-evidence-board-card"' not in html


def test_row_one_css_includes_saved_article_evidence_board_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")
    for selector in (
        ".saved-article-evidence-board",
        ".saved-article-evidence-board-header",
        ".saved-article-evidence-board-metrics",
        ".saved-article-evidence-board-grid",
        ".saved-article-evidence-board-group",
        ".saved-article-evidence-board-group-header",
        ".saved-article-evidence-board-cards",
        ".saved-article-evidence-board-card",
        ".saved-article-evidence-board-card-meta",
        ".saved-article-evidence-board-paragraph",
        ".saved-article-evidence-board-excerpt",
        ".saved-article-evidence-board-actions",
        ".saved-article-evidence-board-link",
        ".saved-article-evidence-board-refs",
        ".saved-article-evidence-board-ref",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

The revalidation test must construct cards with unsafe hrefs containing `javascript:`, traversal, wrong `#local-article-content-section-N` fragments, paragraph `0`, and zero-padded paragraph fragments; it must assert no unsafe href is rendered.

- [ ] **Step 2: Run render tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "evidence_board or reference_atlas or theme_digest or reading_paths"
```

Expected: failures because render wiring and template support are not implemented.

- [ ] **Step 3: Wire builder through render.py**

Update `render_row_one_site()`:

```python
saved_article_evidence_board = build_row_one_saved_article_evidence_board(
    edition,
    saved_article_library,
    saved_article_content_organization,
    local_articles_by_story_id,
)
```

Pass it into `_write_saved_article_library_page()` and from there into `render_saved_article_library_html()`.

- [ ] **Step 4: Render the evidence board in templates.py**

Update `render_saved_article_library_html()` signature with:

```python
saved_article_evidence_board: RowOneSavedArticleEvidenceBoard | None = None,
```

Render:

```python
evidence_board = _render_saved_article_evidence_board(saved_article_evidence_board)
...
{reading_paths}
{evidence_board}
{content_organization}
```

Add helpers with explicit safety:

```python
_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(
    r"^local-article-paragraph-([1-9][0-9]*)$"
)


def _safe_saved_article_evidence_board_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if _LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"
```

Then implement:

```python
def _render_saved_article_evidence_board(board: RowOneSavedArticleEvidenceBoard | None) -> str:
    if board is None or not board.groups:
        return ""
    ...


def _render_saved_article_evidence_board_group(group: RowOneSavedArticleEvidenceBoardGroup) -> str:
    ...


def _render_saved_article_evidence_board_card(card: RowOneSavedArticleEvidenceBoardCard) -> str:
    href = _safe_saved_article_evidence_board_href(card.href)
    if href is None:
        return ""
    href = "../" + href
    ...
```

Use `_localized_span()`, `_esc()`, and the established saved-article section markup style. Render no card when link revalidation fails.

- [ ] **Step 5: Add CSS selectors**

Add styles in `row_one_css()` near the other saved article modules for:

```text
.saved-article-evidence-board
.saved-article-evidence-board-header
.saved-article-evidence-board-metrics
.saved-article-evidence-board-grid
.saved-article-evidence-board-group
.saved-article-evidence-board-group-header
.saved-article-evidence-board-cards
.saved-article-evidence-board-card
.saved-article-evidence-board-card-meta
.saved-article-evidence-board-paragraph
.saved-article-evidence-board-excerpt
.saved-article-evidence-board-actions
.saved-article-evidence-board-link
.saved-article-evidence-board-refs
.saved-article-evidence-board-ref
```

- [ ] **Step 6: Run render tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "evidence_board or reference_atlas or theme_digest or reading_paths"
```

Expected: focused render tests pass.

## Task 3: Documentation And Workflow Boundary

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write failing docs and workflow tests**

Add `test_row_one_docs_describe_stage_338_saved_article_evidence_board_boundary()` before the Stage 337 docs test. The expected paragraph must state:

```text
Stage 338 adds generated-site only Saved Article Paragraph Evidence Board inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved article content organization paragraph indices, and existing detail-page `#local-article-paragraph-N` anchors to group capped local paragraph evidence excerpts by the existing saved article content groups; it does not publish full articles on the library index, does not add outbound article URLs in the evidence board, does not write `data/saved-article-evidence-board.json`, does not add LLM-generated summaries, does not add trend scoring or heat ranking, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

Extend `tests/test_workflows.py` generated-site-only contract guard with:

```python
for forbidden in (
    "saved_article_evidence_board",
    "paragraph_evidence_board",
    "saved-article-evidence-board",
    "Saved Article Paragraph Evidence Board",
    "保存文章段落证据板",
    "saved-article-evidence-board.json",
):
    assert forbidden not in contract_json
```

- [ ] **Step 2: Run docs/workflow tests and verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_338 or saved_article_evidence_board or row_one"
```

Expected: missing docs paragraph and workflow guard failures until implementation/docs are added.

- [ ] **Step 3: Update docs**

Add the exact Stage 338 paragraph above Stage 337 in both `README.md` and `docs/row-one.md`.

- [ ] **Step 4: Run docs/workflow tests and verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_338 or saved_article_evidence_board or row_one"
```

Expected: docs/workflow tests pass.

## Task 4: Review, Full Verification, Commit, Push

**Files:**
- Add review artifacts under `docs/reviews/`.
- Commit all Stage 338 files.

- [ ] **Step 1: Request plan and code review**

Create review prompt files under `docs/reviews/` for Stage 338 plan and code review. Use read-only reviewers. Required questions:

- Does Stage 338 remain generated-site-only?
- Does it avoid full article republication?
- Are paragraph indices validated and local-only?
- Are route-to-local-article mappings current-edition and saved-library constrained?
- Are item-level references attached only when paragraph indices match?
- Are app/runtime/manifest/schema/JSON contracts unchanged?
- Are there any Critical or Important blockers?

- [ ] **Step 2: Fix Critical and Important review findings**

Address only material blockers or correctness issues. Do not add compliance-review product functionality.

- [ ] **Step 3: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_evidence_board.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "evidence_board or reference_atlas or theme_digest or reading_paths"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_338 or saved_article_evidence_board or row_one"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_evidence_board.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_evidence_board.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

- [ ] **Step 4: Run full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

- [ ] **Step 5: Secret scan, commit, and push**

Run changed-file and cached-file secret scans without printing secret values:

```bash
python3 - <<'PY'
import pathlib, re, subprocess, sys
patterns = {
    "github classic token": re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    "github fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]+"),
    "openai-style api key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
proc = subprocess.run(["git", "status", "--porcelain"], text=True, capture_output=True, check=True)
paths = []
for line in proc.stdout.splitlines():
    path_text = line[3:]
    if " -> " in path_text:
        path_text = path_text.split(" -> ", 1)[1]
    path = pathlib.Path(path_text)
    if path.is_file():
        paths.append(path)
findings = []
for path in paths:
    text = path.read_text(errors="ignore")
    for label, pattern in patterns.items():
        if pattern.search(text):
            findings.append((str(path), label))
if findings:
    for path, label in findings:
        print(f"{path}: {label}")
    sys.exit(1)
print(f"Changed-file secret scan passed for {len(paths)} files.")
PY
```

After `git add`, run the same scanner with `git diff --cached --name-only` as the path source.

Commit:

```bash
git commit -m "Stage 338: add saved article evidence board"
git push
```

- [ ] **Step 6: Handoff Summary**

Report:

- repo state;
- commit SHA;
- verified commands;
- uncommitted files;
- next step.
