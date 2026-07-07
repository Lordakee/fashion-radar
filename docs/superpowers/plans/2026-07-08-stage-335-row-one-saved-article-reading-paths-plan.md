# Stage 335 ROW ONE Saved Article Reading Paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add generated-site-only Saved Article Reading Paths to `articles/index.html` so ROW ONE organizes already-saved local article content into scan-first reading routes.

**Architecture:** Create a small private builder module, `saved_article_reading_paths.py`, that derives path cards from existing `RowOneSavedArticleLibrary` and `RowOneSavedArticleContentOrganization`. The builder intersects content-organization cards with safe canonical saved-library entry detail paths, then the existing static HTML renderer displays the paths before the standalone content-organization section. Keep app/runtime/manifest schemas and generated JSON unchanged.

**Tech Stack:** Python 3.13 dataclasses, existing ROW ONE generated-site renderer, existing safe detail-route helpers, pytest, Ruff, Claude Code review gates, `UV_NO_CONFIG=1 uv --no-config run --frozen`.

---

## Files

- Create: `src/fashion_radar/row_one/saved_article_reading_paths.py`
  - Private generated-site view model for saved article reading paths.
  - Safe canonical saved-library detail path extraction.
  - Path/step caps, dedupe, unsafe card filtering.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build reading paths after saved article library/content organization.
  - Pass reading paths into `_write_saved_article_library_page()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Accept optional reading paths in `render_saved_article_library_html()`.
  - Render the `saved-article-reading-paths` section.
  - Add CSS selectors.
- Test: `tests/test_row_one_saved_article_reading_paths.py`
  - Builder unit tests.
- Test: `tests/test_row_one_render.py`
  - Generated-site/direct-render/CSS/contract tests.
- Test: `tests/test_row_one_docs.py`
  - Stage 335 boundary docs sentinel.
- Modify: `README.md`
  - Stage 335 boundary paragraph.
- Modify: `docs/row-one.md`
  - Stage 335 boundary paragraph.
- Create review artifacts under `docs/reviews/`.

## Task 1: Builder View Model

**Files:**
- Create: `tests/test_row_one_saved_article_reading_paths.py`
- Create: `src/fashion_radar/row_one/saved_article_reading_paths.py`

- [ ] **Step 1: Add builder tests**

Create `tests/test_row_one_saved_article_reading_paths.py` with helper fixtures copied in style from `tests/test_row_one_saved_article_content_organization.py` and `tests/test_row_one_saved_article_library.py`.

Add these tests:

```python
def test_saved_article_reading_paths_builds_paths_from_library_and_content_organization() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["The Row paragraph.", "Alaia paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[
                            _item(
                                "Lead",
                                body="Start with The Row retail signal.",
                                body_zh="先看 The Row 零售信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Brand",
                                body="The Row remains central.",
                                body_zh="The Row 仍是核心。",
                                paragraph_indices=[0, 1],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        },
    )
    organization = build_row_one_saved_article_content_organization(
        _edition(story),
        {
            story.id: _article(
                story.id,
                paragraphs=["The Row paragraph.", "Alaia paragraph."],
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[
                            _item(
                                "Lead",
                                body="Start with The Row retail signal.",
                                body_zh="先看 The Row 零售信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "Brand",
                                body="The Row remains central.",
                                body_zh="The Row 仍是核心。",
                                paragraph_indices=[0, 1],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        },
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert reading_paths.path_count == 2
    assert reading_paths.step_count == 2
    assert [path.key for path in reading_paths.paths] == ["takeaways", "entities"]
    assert reading_paths.paths[0].title.en == "Read First"
    assert reading_paths.paths[0].steps[0].lead.en == "Start with The Row retail signal."
    assert reading_paths.paths[0].steps[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert reading_paths.paths[0].steps[0].paragraph_indices == (0,)
    assert reading_paths.paths[1].steps[0].references[0].name == "The Row"
```

Add canonicalization and unsafe-fragment tests:

```python
def test_saved_article_reading_paths_canonicalizes_content_card_detail_paths() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    library = build_row_one_saved_article_library(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[
                    _section(
                        "takeaways",
                        "Read First",
                        items=[_item("Lead", body="Canonical lead.", paragraph_indices=[0])],
                    )
                ],
            )
        },
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="takeaways",
                title=LocalizedText(en="Read First", zh="优先阅读"),
                dek=LocalizedText(en="Start here", zh="从这里开始"),
                cards=[
                    RowOneSavedArticleContentOrganizationCard(
                        title=LocalizedText(en="Canonical card", zh="规范卡片"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        section_label=LocalizedText(en="Read First", zh="优先阅读"),
                        lead=LocalizedText(en="Canonical lead.", zh="规范摘要。"),
                        detail_path=(
                            "details/./the-row-a-1234567890.html"
                            "#local-article-content-section-1"
                        ),
                        paragraph_indices=(0,),
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert reading_paths.paths[0].steps[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )


def test_saved_article_reading_paths_rejects_noncanonical_content_section_fragments() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Zero section lead", zh="零栏目摘要"),
                        detail_path=(
                            "details/the-row-a-1234567890.html"
                            "#local-article-content-section-0"
                        ),
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Padded section lead", zh="补零栏目摘要"),
                        detail_path=(
                            "details/the-row-a-1234567890.html"
                            "#local-article-content-section-01"
                        ),
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Paragraph lead", zh="段落摘要"),
                        detail_path="details/the-row-a-1234567890.html#local-article-paragraph-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Missing hash lead", zh="缺少锚点摘要"),
                        detail_path="details/the-row-a-1234567890.html",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="JS lead", zh="脚本摘要"),
                        detail_path="javascript:alert(1)#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
                        detail_path="../secrets.html#local-article-content-section-1",
                    ),
                ],
            )
        ]
    )
    library = RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[
                    RowOneSavedArticleLibraryEntry(
                        title=LocalizedText(en="Entry", zh="条目"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        body_source="extracted",
                        digest_path="details/the-row-a-1234567890.html#local-article-digest",
                        reader_path="details/the-row-a-1234567890.html#local-article-reader",
                        evidence_path=(
                            "details/the-row-a-1234567890.html"
                            "#local-article-paragraph-evidence"
                        ),
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    text = " ".join(step.lead.en for path in reading_paths.paths for step in path.steps)
    assert "Safe lead" in text
    assert "Zero section lead" not in text
    assert "Padded section lead" not in text
    assert "Paragraph lead" not in text
    assert "Missing hash lead" not in text
    assert "JS lead" not in text
    assert "Traversal lead" not in text
```

Add library-route fallback coverage:

```python
def test_saved_article_reading_paths_accepts_step_when_any_one_library_route_is_safe() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )

    for reader_path, digest_path, evidence_path in (
        (
            "../outside.html#local-article-reader",
            "details/the-row-a-1234567890.html#local-article-digest",
            "../outside.html#local-article-paragraph-evidence",
        ),
        (
            "../outside.html#local-article-reader",
            "../outside.html#local-article-digest",
            "details/the-row-a-1234567890.html#local-article-paragraph-evidence",
        ),
    ):
        library = RowOneSavedArticleLibrary(
            article_count=1,
            source_count=1,
            saved_paragraph_count=1,
            organized_section_count=1,
            extracted_article_count=1,
            summary_fallback_article_count=0,
            skipped_article_count=0,
            groups=[
                RowOneSavedArticleLibrarySourceGroup(
                    source_name="Vogue Business",
                    article_count=1,
                    saved_paragraph_count=1,
                    organized_section_count=1,
                    entries=[
                        RowOneSavedArticleLibraryEntry(
                            title=LocalizedText(en="Entry", zh="条目"),
                            source_name="Vogue Business",
                            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                            saved_paragraph_count=1,
                            organized_section_count=1,
                            body_source="extracted",
                            digest_path=digest_path,
                            reader_path=reader_path,
                            evidence_path=evidence_path,
                        )
                    ],
                )
            ],
        )

        reading_paths = build_row_one_saved_article_reading_paths(library, organization)

        assert reading_paths is not None
        assert reading_paths.paths[0].steps[0].lead.en == "Safe lead"
```

Add a cap/dedupe test that covers both path and step caps:

```python
def test_saved_article_reading_paths_caps_paths_steps_and_dedupes_steps() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(1, 7)]
    articles = {
        story.id: _article(story.id, paragraphs=[f"Paragraph {index}."])
        for index, story in enumerate(stories, start=1)
    }
    library = build_row_one_saved_article_library(_edition(*stories), articles)
    assert library is not None

    groups: list[RowOneSavedArticleContentOrganizationGroup] = []
    for group_index in range(1, 6):
        cards: list[RowOneSavedArticleContentOrganizationCard] = []
        for step_index, story in enumerate(stories[:5], start=1):
            cards.append(
                RowOneSavedArticleContentOrganizationCard(
                    title=LocalizedText(en=f"Group {group_index} Card {step_index}", zh="卡片"),
                    source_name="Vogue Business",
                    section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                    section_label=LocalizedText(en=f"Group {group_index}", zh="分组"),
                    lead=LocalizedText(en=f"Lead {group_index}-{step_index}.", zh="摘要。"),
                    detail_path=(
                        f"details/{story.id}.html#local-article-content-section-{step_index}"
                    ),
                    paragraph_indices=(0,),
                    references=(),
                )
            )
        cards.insert(1, cards[0])
        groups.append(
            RowOneSavedArticleContentOrganizationGroup(
                key=f"group-{group_index}",
                title=LocalizedText(en=f"Group {group_index}", zh="分组"),
                dek=LocalizedText(en="Path dek", zh="路径说明"),
                cards=cards,
            )
        )
    organization = RowOneSavedArticleContentOrganization(groups=groups)

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    assert len(reading_paths.paths) == 4
    assert all(path.step_count <= 3 for path in reading_paths.paths)
    assert [step.lead.en for step in reading_paths.paths[0].steps] == [
        "Lead 1-1.",
        "Lead 1-2.",
        "Lead 1-3.",
    ]
```

Add unsafe/mismatch tests:

```python
def test_saved_article_reading_paths_requires_safe_library_entry_match() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-a-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[
                    safe_card,
                    replace(
                        safe_card,
                        title=LocalizedText(en="Wrong path", zh="错误路径"),
                        lead=LocalizedText(en="Wrong path lead", zh="错误路径摘要"),
                        detail_path="details/not-in-library-1234567890.html#local-article-content-section-1",
                    ),
                    replace(
                        safe_card,
                        title=LocalizedText(en="Unsafe card", zh="不安全卡片"),
                        lead=LocalizedText(en="Unsafe lead", zh="不安全摘要"),
                        detail_path="../secrets.html#local-article-content-section-1",
                    ),
                ],
            )
        ]
    )
    library = RowOneSavedArticleLibrary(
        article_count=1,
        source_count=1,
        saved_paragraph_count=1,
        organized_section_count=1,
        extracted_article_count=1,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=1,
                saved_paragraph_count=1,
                organized_section_count=1,
                entries=[
                    RowOneSavedArticleLibraryEntry(
                        title=LocalizedText(en="Entry", zh="条目"),
                        source_name="Vogue Business",
                        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
                        saved_paragraph_count=1,
                        organized_section_count=1,
                        body_source="extracted",
                        digest_path="details/the-row-a-1234567890.html#local-article-digest",
                        reader_path="details/the-row-a-1234567890.html#local-article-reader",
                        evidence_path="details/the-row-a-1234567890.html#local-article-paragraph-evidence",
                    )
                ],
            )
        ],
    )

    reading_paths = build_row_one_saved_article_reading_paths(library, organization)

    assert reading_paths is not None
    section_text = " ".join(step.lead.en for path in reading_paths.paths for step in path.steps)
    assert "Safe lead" in section_text
    assert "Wrong path lead" not in section_text
    assert "Unsafe lead" not in section_text
```

Add empty input test:

```python
def test_saved_article_reading_paths_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_reading_paths(None, None) is None
    empty_library = RowOneSavedArticleLibrary(
        article_count=0,
        source_count=0,
        saved_paragraph_count=0,
        organized_section_count=0,
        extracted_article_count=0,
        summary_fallback_article_count=0,
        skipped_article_count=0,
        groups=[],
    )
    assert build_row_one_saved_article_reading_paths(empty_library, None) is None
    empty_organization = RowOneSavedArticleContentOrganization(groups=[])
    assert (
        build_row_one_saved_article_reading_paths(empty_library, empty_organization)
        is None
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_paths.py -q
```

Expected: FAIL because the module does not exist yet.

- [ ] **Step 2: Implement builder module**

Create `src/fashion_radar/row_one/saved_article_reading_paths.py`:

```python
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

MAX_SAVED_ARTICLE_READING_PATHS = 4
MAX_SAVED_ARTICLE_READING_PATH_STEPS = 3


@dataclass(frozen=True)
class RowOneSavedArticleReadingPathStep:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReadingPath:
    key: str
    title: LocalizedText
    dek: LocalizedText
    step_count: int
    steps: tuple[RowOneSavedArticleReadingPathStep, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReadingPaths:
    path_count: int
    step_count: int
    paths: tuple[RowOneSavedArticleReadingPath, ...]


def build_row_one_saved_article_reading_paths(
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleReadingPaths | None:
    if library is None or organization is None:
        return None
    allowed_detail_paths = _library_detail_paths(library)
    if not allowed_detail_paths:
        return None

    paths: list[RowOneSavedArticleReadingPath] = []
    total_steps = 0
    for group in organization.groups:
        steps: list[RowOneSavedArticleReadingPathStep] = []
        seen_steps: set[tuple[str, str, str, str]] = set()
        for card in group.cards:
            step = _reading_path_step(card, allowed_detail_paths)
            if step is None:
                continue
            dedupe_key = (
                step.detail_path,
                " ".join(step.section_label.en.split()).casefold(),
                " ".join(step.lead.en.split()).casefold(),
                " ".join(step.lead.zh.split()).casefold(),
            )
            if dedupe_key in seen_steps:
                continue
            seen_steps.add(dedupe_key)
            steps.append(step)
            if len(steps) >= MAX_SAVED_ARTICLE_READING_PATH_STEPS:
                break
        if not steps:
            continue
        path = RowOneSavedArticleReadingPath(
            key=group.key,
            title=group.title,
            dek=group.dek,
            step_count=len(steps),
            steps=tuple(steps),
        )
        paths.append(path)
        total_steps += path.step_count
        if len(paths) >= MAX_SAVED_ARTICLE_READING_PATHS:
            break
    if not paths:
        return None
    return RowOneSavedArticleReadingPaths(
        path_count=len(paths),
        step_count=total_steps,
        paths=tuple(paths),
    )


def _library_detail_paths(library: RowOneSavedArticleLibrary) -> set[str]:
    detail_paths: set[str] = set()
    for group in library.groups:
        for entry in group.entries:
            detail_path = _entry_detail_path(entry)
            if detail_path is not None:
                detail_paths.add(detail_path)
    return detail_paths


def _entry_detail_path(entry: RowOneSavedArticleLibraryEntry) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _reading_path_step(
    card: RowOneSavedArticleContentOrganizationCard,
    allowed_detail_paths: set[str],
) -> RowOneSavedArticleReadingPathStep | None:
    href = _safe_content_section_href(card.detail_path)
    if href is None:
        return None
    detail_path = _detail_path_key(href)
    if detail_path is None or detail_path not in allowed_detail_paths:
        return None
    return RowOneSavedArticleReadingPathStep(
        title=card.title,
        source_name=card.source_name,
        section_title=card.section_title,
        section_label=card.section_label,
        lead=card.lead,
        detail_path=href,
        paragraph_indices=card.paragraph_indices,
        references=card.references,
    )


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith("local-article-content-section-"):
        return None
    number = fragment.removeprefix("local-article-content-section-")
    if not number.isdecimal() or number != str(int(number)) or int(number) < 1:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_paths.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_reading_paths.py tests/test_row_one_saved_article_reading_paths.py
```

Expected: PASS after small syntax/import adjustments.

## Task 2: Render Reading Paths In `articles/index.html`

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add generated-site render test**

In `tests/test_row_one_render.py`, add helper:

```python
def _saved_article_reading_paths_section_html(index_html: str) -> str:
    marker = '<section class="saved-article-reading-paths"'
    assert marker in index_html
    start = index_html.index(marker)
    end = index_html.index('<section class="saved-article-content-organization"', start)
    return index_html[start:end]
```

Add test near the Stage 332-334 library tests:

```python
def test_render_row_one_site_includes_saved_article_reading_paths_in_article_library(
    tmp_path,
) -> None:
    edition = _edition()
    story = edition.stories[0]

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: _signal_briefing_local_article()},
    )

    library_html = (tmp_path / "articles" / "index.html").read_text(encoding="utf-8")
    homepage_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    section_html = _saved_article_reading_paths_section_html(library_html)

    assert 'class="saved-article-reading-paths"' in section_html
    assert "Saved Article Reading Paths" in section_html
    assert "保存文章阅读路径" in section_html
    assert "People &amp; Brands" in section_html
    assert "Products" in section_html
    assert "The Row appears in paragraph one." in section_html
    assert "Alaia flats appear in paragraph two." in section_html
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"'
        in section_html
    )
    assert "https://example.com/the-row" not in section_html
    assert (
        library_html.index('class="saved-article-library-hero"')
        < library_html.index('class="saved-signal-index"')
        < library_html.index('class="saved-article-reading-paths"')
        < library_html.index('class="saved-article-content-organization"')
        < library_html.index('class="saved-article-library-grid"')
    )
    assert 'class="saved-article-reading-paths"' not in homepage_html

    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_reading_paths" not in contract_json
        assert "saved_article_reading_path" not in contract_json
        assert "article_reading_paths" not in contract_json
        assert "saved-article-reading-paths" not in contract_json
        assert "saved-article-reading-path" not in contract_json
        assert "Saved Article Reading Paths" not in contract_json
        assert "保存文章阅读路径" not in contract_json
        assert "The Row appears in paragraph one." not in contract_json
    assert not (tmp_path / "data" / "saved-article-reading-paths.json").exists()
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_reading_paths_in_article_library -q
```

Expected: FAIL until render integration exists.

- [ ] **Step 2: Integrate builder in render flow**

Modify imports in `src/fashion_radar/row_one/render.py`:

```python
from fashion_radar.row_one.saved_article_reading_paths import (
    RowOneSavedArticleReadingPaths,
    build_row_one_saved_article_reading_paths,
)
```

After `saved_article_library` and `saved_article_content_organization` are built:

```python
    saved_article_reading_paths = build_row_one_saved_article_reading_paths(
        saved_article_library,
        saved_article_content_organization,
    )
```

Pass it into `_write_saved_article_library_page(...)`.

Update `_write_saved_article_library_page()` signature:

```python
    saved_article_reading_paths: RowOneSavedArticleReadingPaths | None,
```

Pass it into `render_saved_article_library_html(...)`.

- [ ] **Step 3: Add template render support**

Modify imports in `src/fashion_radar/row_one/templates.py`:

```python
from fashion_radar.row_one.saved_article_reading_paths import (
    RowOneSavedArticleReadingPath,
    RowOneSavedArticleReadingPathStep,
    RowOneSavedArticleReadingPaths,
)
```

Update `render_saved_article_library_html()` signature:

```python
    saved_article_reading_paths: RowOneSavedArticleReadingPaths | None = None,
```

Render:

```python
    reading_paths = _render_saved_article_reading_paths(saved_article_reading_paths)
```

Insert `{reading_paths}` between `{signal_index}` and `{content_organization}`.

Add render helpers near saved article library/content organization helpers:

```python
def _render_saved_article_reading_paths(
    reading_paths: RowOneSavedArticleReadingPaths | None,
) -> str:
    if reading_paths is None or not reading_paths.paths:
        return ""
    cards = [
        _render_saved_article_reading_path(path)
        for path in reading_paths.paths
    ]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    return f"""<section class="saved-article-reading-paths"
  aria-label="Saved article reading paths">
  <div class="saved-article-reading-paths-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Reading Paths</span>
        <span data-lang="zh">保存文章阅读路径</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Reading Paths</span>
        <span data-lang="zh">保存文章阅读路径</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Follow edited routes through today's saved local fashion text.</span>
      <span data-lang="zh">沿着编辑整理的路径阅读今天保存的本地时尚正文。</span>
    </p>
  </div>
  <div class="saved-article-reading-paths-grid">{"".join(cards)}</div>
</section>"""
```

```python
def _render_saved_article_reading_path(path: RowOneSavedArticleReadingPath) -> str:
    steps = [_render_saved_article_reading_path_step(index, step) for index, step in enumerate(path.steps, start=1)]
    steps = [step for step in steps if step]
    if not steps:
        return ""
    start_href = _safe_saved_article_content_organization_href(path.steps[0].detail_path)
    rendered_step_count = len(steps)
    start_link = ""
    if start_href is not None:
        start_href = _prefixed_saved_article_content_organization_href(start_href, "../")
        start_link = f"""      <a class="saved-article-reading-path-link" href="{_esc(start_href)}">
        <span data-lang="en">Start path</span>
        <span data-lang="zh">开始阅读</span>
      </a>"""
    return f"""    <article class="saved-article-reading-path-card">
      <div class="saved-article-reading-path-card-header">
        <p class="saved-article-reading-path-count">
          <span data-lang="en">{_esc(_count_label(rendered_step_count, "step", "steps"))}</span>
          <span data-lang="zh">{_esc(f"{rendered_step_count} 个步骤")}</span>
        </p>
        <h3>
          <span data-lang="en">{_esc(path.title.en)}</span>
          <span data-lang="zh">{_esc(path.title.zh)}</span>
        </h3>
        <p>
          <span data-lang="en">{_esc(path.dek.en)}</span>
          <span data-lang="zh">{_esc(path.dek.zh)}</span>
        </p>
      </div>
      <ol class="saved-article-reading-path-steps">{"".join(steps)}</ol>
{start_link}
    </article>"""
```

```python
def _render_saved_article_reading_path_step(
    index: int,
    step: RowOneSavedArticleReadingPathStep,
) -> str:
    href = _safe_saved_article_content_organization_href(step.detail_path)
    if href is None:
        return ""
    href = _prefixed_saved_article_content_organization_href(href, "../")
    evidence = _render_saved_article_reading_path_evidence(step)
    evidence_block = (
        f'\n          <span class="saved-article-reading-path-evidence">{evidence}</span>'
        if evidence
        else ""
    )
    return f"""        <li class="saved-article-reading-path-step">
          <a class="saved-article-reading-path-step-link" href="{_esc(href)}">
            <span class="saved-article-reading-path-step-number">{_esc(str(index))}</span>
            <span class="saved-article-reading-path-step-copy">
              <span class="saved-article-reading-path-step-meta">
                <span>{_esc(step.source_name)}</span>
                <span data-lang="en">{_esc(step.section_label.en)}</span>
                <span data-lang="zh">{_esc(step.section_label.zh)}</span>
              </span>
              <strong>
                <span data-lang="en">{_esc(step.title.en)}</span>
                <span data-lang="zh">{_esc(step.title.zh)}</span>
              </strong>
              <span class="saved-article-reading-path-step-lead">
                <span data-lang="en">{_esc(_local_article_digest_excerpt(step.lead.en))}</span>
                <span data-lang="zh">{_esc(_local_article_digest_excerpt(step.lead.zh))}</span>
              </span>
            </span>
          </a>{evidence_block}
        </li>"""
```

```python
def _render_saved_article_reading_path_evidence(
    step: RowOneSavedArticleReadingPathStep,
) -> str:
    card = RowOneSavedArticleContentOrganizationCard(
        title=step.title,
        source_name=step.source_name,
        section_title=step.section_title,
        section_label=step.section_label,
        lead=step.lead,
        detail_path=step.detail_path,
        paragraph_indices=step.paragraph_indices,
        references=step.references,
    )
    return _render_saved_article_content_organization_evidence(card, href_prefix="../")
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_reading_paths_in_article_library -q
```

Expected: PASS.

## Task 3: Safety, Canonicalization, Caps, And CSS

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add direct safety/canonicalization tests**

Add a direct renderer safety test that does not rely on builder filtering:

```python
def test_render_saved_article_library_filters_unsafe_reading_path_view_model_steps() -> None:
    safe_step = RowOneSavedArticleReadingPathStep(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe <script>lead</script>", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
    )
    unsafe_steps = [
        replace(
            safe_step,
            lead=LocalizedText(en="JS lead", zh="脚本摘要"),
            detail_path="javascript:alert(1)#local-article-content-section-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Traversal lead", zh="越界摘要"),
            detail_path="../secrets.html#local-article-content-section-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Paragraph-fragment lead", zh="段落锚点摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-paragraph-1",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Zero-section lead", zh="零栏目摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-content-section-0",
        ),
        replace(
            safe_step,
            lead=LocalizedText(en="Padded-section lead", zh="补零栏目摘要"),
            detail_path="details/the-row-signal-1234567890.html#local-article-content-section-01",
        ),
    ]
    reading_paths = RowOneSavedArticleReadingPaths(
        path_count=1,
        step_count=1 + len(unsafe_steps),
        paths=(
            RowOneSavedArticleReadingPath(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                step_count=1 + len(unsafe_steps),
                steps=(safe_step, *unsafe_steps),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)

    assert "Safe &lt;script&gt;lead&lt;/script&gt;" in section_html
    assert "<script>" not in section_html
    assert "javascript:alert" not in section_html
    assert "../secrets" not in section_html
    assert "JS lead" not in section_html
    assert "Traversal lead" not in section_html
    assert "Paragraph-fragment lead" not in section_html
    assert "Zero-section lead" not in section_html
    assert "Padded-section lead" not in section_html
```

Add an allowlist test for rendered reading-path hrefs:

```python
def test_render_saved_article_library_reading_path_hrefs_match_local_anchor_allowlist() -> None:
    safe_step = RowOneSavedArticleReadingPathStep(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Source",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0, 1),
    )
    reading_paths = RowOneSavedArticleReadingPaths(
        path_count=1,
        step_count=1,
        paths=(
            RowOneSavedArticleReadingPath(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                step_count=1,
                steps=(safe_step,),
            ),
        ),
    )

    html = render_saved_article_library_html(
        _edition(),
        _saved_article_library_fixture(),
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)
    hrefs = re.findall(r'href="([^"]+)"', section_html)

    assert hrefs
    for href in hrefs:
        assert re.fullmatch(
            r"\.\./details/[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html"
            r"#local-article-(?:content-section|paragraph)-[1-9][0-9]*",
            href,
        )
```

Add:

```python
def test_render_saved_article_library_omits_reading_paths_for_unsafe_entry_paths() -> None:
    safe_card = RowOneSavedArticleContentOrganizationCard(
        title=LocalizedText(en="Safe card", zh="安全卡片"),
        source_name="Vogue Business",
        section_title=LocalizedText(en="Top Stories", zh="今日重点"),
        section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
        lead=LocalizedText(en="Safe lead", zh="安全摘要"),
        detail_path="details/the-row-signal-1234567890.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=[safe_card],
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    entry = replace(
        fixture.groups[0].entries[0],
        reader_path="../outside.html#local-article-reader",
        digest_path="javascript:alert(1)#local-article-digest",
        evidence_path="details/the-row-signal-1234567890.html#wrong-fragment",
    )
    fixture = replace(fixture, groups=[replace(fixture.groups[0], entries=[entry])])
    reading_paths = build_row_one_saved_article_reading_paths(fixture, organization)

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
        saved_article_reading_paths=reading_paths,
    )

    assert 'class="saved-article-reading-paths"' not in html
    assert "Safe lead" not in html
```

Add:

```python
def test_render_saved_article_library_canonicalizes_caps_and_dedupes_reading_paths() -> None:
    long_lead = (
        "Canonical reading path starts with The Row and keeps going long enough that "
        "the saved article reading path should show a capped excerpt instead of a "
        "full organized content body ending with a unique reading path tail marker."
    )
    cards = [
        RowOneSavedArticleContentOrganizationCard(
            title=LocalizedText(en=f"Card {index}", zh=f"卡片 {index}"),
            source_name="Source",
            section_title=LocalizedText(en="Top Stories", zh="今日重点"),
            section_label=LocalizedText(en="People & Brands", zh="品牌与人物"),
            lead=LocalizedText(en=long_lead if index == 0 else f"Lead {index}", zh="中文摘要"),
            detail_path=(
                "details/./the-row-signal-1234567890.html#local-article-content-section-1"
                if index == 0
                else (
                    "details/the-row-signal-1234567890.html"
                    f"#local-article-content-section-{index + 1}"
                )
            ),
            paragraph_indices=(0,),
            references=(),
        )
        for index in range(5)
    ]
    cards.insert(1, cards[0])
    organization = RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key="entities",
                title=LocalizedText(en="People & Brands", zh="品牌与人物"),
                dek=LocalizedText(en="Entity context", zh="实体背景"),
                cards=cards,
            )
        ]
    )
    fixture = _saved_article_library_fixture()
    reading_paths = build_row_one_saved_article_reading_paths(fixture, organization)

    html = render_saved_article_library_html(
        _edition(),
        fixture,
        saved_article_content_organization=organization,
        saved_article_reading_paths=reading_paths,
    )
    section_html = _saved_article_reading_paths_section_html(html)

    assert (
        'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"'
        in section_html
    )
    assert "details/./the-row-signal-1234567890.html" not in section_html
    assert section_html.count('class="saved-article-reading-path-step"') == 3
    assert section_html.count("Canonical reading path starts with The Row") == 1
    assert "…" in section_html
    assert "unique reading path tail marker" not in section_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reading_paths or saved_article_library or content_organization"
```

Expected: PASS after implementation.

- [ ] **Step 2: Add CSS and CSS selector test**

In `row_one_css()`, add near saved article library/content organization styles:

```css
.saved-article-reading-paths {
  border-bottom: 1px solid var(--ink);
  display: grid;
  gap: 18px;
  padding-bottom: 28px;
}
.saved-article-reading-paths-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.36fr) minmax(0, 1fr);
}
.saved-article-reading-paths-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2rem, 5vw, 5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}
.saved-article-reading-paths-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-article-reading-path-card {
  background: var(--panel);
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}
.saved-article-reading-path-link,
.saved-article-reading-path-step-link,
.saved-article-reading-path-evidence a {
  color: var(--accent);
  text-decoration: none;
}
.saved-article-reading-path-evidence {
  display: contents;
}
```

Extend CSS tests with selector assertions:

```python
def test_row_one_css_includes_saved_article_reading_path_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-reading-paths",
        ".saved-article-reading-paths-header",
        ".saved-article-reading-paths-grid",
        ".saved-article-reading-path-card",
        ".saved-article-reading-path-link",
        ".saved-article-reading-path-step-link",
        ".saved-article-reading-path-evidence",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_row_one_css_includes_saved_article_reading_path_styles -q
```

Expected: PASS.

## Task 4: Docs Boundary

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing docs sentinel**

Add before Stage 334 docs test:

```python
def test_row_one_docs_describe_stage_335_saved_article_reading_paths_boundary() -> None:
    expected = _normalized(
        "Stage 335 adds generated-site only Saved Article Reading Paths inside "
        "`articles/index.html`; it reuses existing saved local article sidecars, "
        "existing saved local paragraphs, existing saved article content "
        "organization, and existing detail-page `#local-article`, "
        "`#local-article-reader`, `#local-article-content-section-N`, and "
        "`#local-article-paragraph-N` anchors to organize read-first, "
        "people/brands, products, and source-context paths from already-saved "
        "local text; it does not publish full articles on the library index, "
        "does not change row-one-app/v7, row-one-manifest/v1, "
        "row-one-runtime/v1, schemas, JSON artifacts, source collection, "
        "fetching, matching, extraction, scoring, ranking, LLM, connector, "
        "scheduling, deployment, market grouping, domestic/international "
        "classification, or compliance-review behavior."
    )

    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
        stage = normalized[
            normalized.index("stage 335 adds generated-site only saved article reading paths")
            : normalized.index("stage 334 adds generated-site only organized local excerpts")
        ]
        for stale_phrase in (
            "row-one-app/v8",
            "row-one-manifest/v2",
            "row-one-runtime/v2",
            "changes schemas",
            "writes `data/saved-article-reading-paths.json`",
            "publishes full articles",
            "adds source collection",
            "adds fetching",
            "adds extraction",
            "adds scoring",
            "adds ranking",
            "adds llm calls",
            "adds connectors",
            "adds scheduling",
            "adds deployment behavior",
            "adds compliance review",
        ):
            assert stale_phrase not in stage
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_335_saved_article_reading_paths_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Add docs paragraph**

Insert above Stage 334 in both `README.md` and `docs/row-one.md`:

```markdown
Stage 335 adds generated-site only Saved Article Reading Paths inside `articles/index.html`; it reuses existing saved local article sidecars, existing saved local paragraphs, existing saved article content organization, and existing detail-page `#local-article`, `#local-article-reader`, `#local-article-content-section-N`, and `#local-article-paragraph-N` anchors to organize read-first, people/brands, products, and source-context paths from already-saved local text; it does not publish full articles on the library index, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, or compliance-review behavior.
```

Run docs sentinel again. Expected: PASS.

## Task 5: Plan/Code Review And Verification

**Files:**
- Create review artifacts under `docs/reviews/`.

- [ ] **Step 1: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_paths.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reading_paths or saved_article_library or content_organization or row_one_css"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_335_saved_article_reading_paths_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_reading_paths.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_reading_paths.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_article_reading_paths.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_reading_paths.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-335-code-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-335-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-335-code-review.md
rm -f "$tmp_review"
```

Fix all Critical/Important findings and request rereview if needed.

- [ ] **Step 3: Full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
UV_NO_CONFIG=1 uv --no-config build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
python3 -m venv "$tmp_env/venv"
UV_NO_CONFIG=1 uv --no-config pip install \
  --python "$tmp_env/venv/bin/python" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py \
  --repo-root . \
  --python "$tmp_env/venv/bin/python" \
  --installed
"$tmp_env/venv/bin/fashion-radar" row-one build --help >/dev/null
rm -rf "$tmp_build" "$tmp_env"
```

- [ ] **Step 4: Stage, secret scan, commit, push**

Stage only Stage 335 files. Run:

```bash
git diff --cached --check
git diff --cached --name-only | rg -x 'uv.lock|pyproject.toml|dist/.*|build/.*|reports/.*|data/.*|\\.codegraph/.*|\\.venv/.*|\\.env|.*cookie.*|.*session.*|.*token.*' && exit 1 || exit 0
if git diff --cached -U0 | rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]+'; then
  echo "staged secret scan found matches" >&2
  exit 1
fi
```

Commit:

```bash
git commit -m "Stage 335: add saved article reading paths"
git push origin main
```

End with Handoff Summary containing repo state, verified commands, uncommitted
files, and next step.
