from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentSection,
    RowOneStory,
)
from fashion_radar.row_one.text import clean_row_one_text, normalize_row_one_paragraph

LOCAL_ARTICLE_SYNTHESIS_BRIEF_LEAD_CHARS = 180
LOCAL_ARTICLE_SYNTHESIS_BRIEF_CARD_CHARS = 160
LOCAL_ARTICLE_SYNTHESIS_BRIEF_ANCHOR_SUPPORT_CHARS = 110
LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS = 3
_BASIS_NOTE = LocalizedText(
    en="Built from saved ROW ONE story fields and local article text already stored for this page.",
    zh="基于本页已保存的 ROW ONE 故事字段与本地文章正文整理生成。",
)


@dataclass(frozen=True)
class RowOneLocalArticleSynthesisAnchor:
    label: LocalizedText
    href: str
    support: LocalizedText | None = None


@dataclass(frozen=True)
class RowOneLocalArticleSynthesisBrief:
    title: LocalizedText
    source_name: str
    lead: LocalizedText
    thesis: LocalizedText
    article_adds: LocalizedText
    reader_move: LocalizedText
    basis_note: LocalizedText
    anchors: tuple[RowOneLocalArticleSynthesisAnchor, ...]


@dataclass(frozen=True)
class _SynthesisCandidate:
    source_id: str
    text: LocalizedText


def build_row_one_local_article_synthesis_brief(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneLocalArticleSynthesisBrief | None:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None

    consumed_sources: set[str] = set()
    consumed_texts: set[str] = set()
    lead = _choose_candidate(
        _lead_candidates(story, local_article),
        consumed_sources=consumed_sources,
        consumed_texts=consumed_texts,
        limit=LOCAL_ARTICLE_SYNTHESIS_BRIEF_LEAD_CHARS,
    )
    thesis = _choose_candidate(
        _thesis_candidates(story, local_article),
        consumed_sources=consumed_sources,
        consumed_texts=consumed_texts,
        limit=LOCAL_ARTICLE_SYNTHESIS_BRIEF_CARD_CHARS,
    )
    article_adds = _choose_candidate(
        _article_adds_candidates(local_article),
        consumed_sources=consumed_sources,
        consumed_texts=consumed_texts,
        limit=LOCAL_ARTICLE_SYNTHESIS_BRIEF_CARD_CHARS,
    )
    if lead is None or thesis is None or article_adds is None:
        return None

    anchors = _anchors(local_article)
    source_name = normalize_row_one_paragraph(
        local_article.source_name
    ) or normalize_row_one_paragraph(story.source_name)
    return RowOneLocalArticleSynthesisBrief(
        title=LocalizedText(
            en="Local Article Synthesis Brief",
            zh="本地文章综合简报",
        ),
        source_name=source_name,
        lead=lead,
        thesis=thesis,
        article_adds=article_adds,
        reader_move=_reader_move(anchors=anchors, local_article=local_article),
        basis_note=_BASIS_NOTE,
        anchors=anchors,
    )


def _lead_candidates(
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> Iterable[_SynthesisCandidate]:
    yield _candidate("story.editorial_takeaway", story.editorial_takeaway)
    yield _candidate("story.summary", story.summary)
    yield from _brief_section_candidates(local_article.brief_sections, ("signal_context",))
    yield from _brief_section_candidates(local_article.brief_sections, ("what_happened",))
    yield from _brief_section_candidates(local_article.brief_sections, ("watch_next",))
    yield from _content_body_candidates(local_article.content_sections)
    yield from _item_body_candidates(local_article.content_sections)
    yield from _paragraph_candidates(local_article)
    yield _candidate("story.why_it_matters", story.why_it_matters)
    yield from _brief_section_candidates(local_article.brief_sections, ("why_it_matters",))


def _thesis_candidates(
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> Iterable[_SynthesisCandidate]:
    yield _candidate("story.editorial_takeaway", story.editorial_takeaway)
    yield from _brief_section_candidates(local_article.brief_sections, ("signal_context",))
    yield _candidate("story.signal_context", story.signal_context)
    yield from _content_title_body_candidates(local_article.content_sections)
    yield _candidate("story.summary", story.summary)


def _article_adds_candidates(
    local_article: RowOneLocalArticle,
) -> Iterable[_SynthesisCandidate]:
    yield from _content_body_candidates(local_article.content_sections)
    yield from _item_body_candidates(local_article.content_sections)
    yield from _paragraph_candidates(local_article)
    yield from _brief_section_candidates(local_article.brief_sections, ("what_happened",))
    yield from _brief_section_candidates(local_article.brief_sections, ("watch_next",))


def _candidate(source_id: str, value: LocalizedText | None) -> _SynthesisCandidate:
    return _SynthesisCandidate(source_id=source_id, text=value or LocalizedText(en="", zh=""))


def _choose_candidate(
    candidates: Iterable[_SynthesisCandidate],
    *,
    consumed_sources: set[str],
    consumed_texts: set[str],
    limit: int,
) -> LocalizedText | None:
    for candidate in candidates:
        text = _nonblank_localized_text(candidate.text)
        if text is None:
            continue
        key = _normalized_candidate_key(text)
        if candidate.source_id in consumed_sources or key in consumed_texts:
            continue
        consumed_sources.add(candidate.source_id)
        consumed_texts.add(key)
        return _truncate_localized_text(text, limit)
    return None


def _brief_section_candidates(
    brief_sections: Sequence[RowOneLocalArticleBriefSection],
    keys: Sequence[str],
) -> Iterable[_SynthesisCandidate]:
    for key in keys:
        for section in brief_sections:
            if section.key != key:
                continue
            yield _candidate(f"brief.{key}", section.body)


def _content_body_candidates(
    sections: Sequence[RowOneLocalArticleContentSection],
) -> Iterable[_SynthesisCandidate]:
    for index, section in enumerate(sections):
        yield _candidate(f"content_section.{index}.body", section.body)


def _content_title_body_candidates(
    sections: Sequence[RowOneLocalArticleContentSection],
) -> Iterable[_SynthesisCandidate]:
    for index, section in enumerate(sections):
        title = _nonblank_localized_text(section.title)
        body = _nonblank_localized_text(section.body)
        if title is not None and body is not None:
            yield _candidate(
                f"content_section.{index}.body",
                LocalizedText(
                    en=f"{title.en}: {body.en}",
                    zh=f"{title.zh}: {body.zh}",
                ),
            )
        elif body is not None:
            yield _candidate(f"content_section.{index}.body", body)
        elif title is not None:
            yield _candidate(f"content_section.{index}.title", title)


def _item_body_candidates(
    sections: Sequence[RowOneLocalArticleContentSection],
) -> Iterable[_SynthesisCandidate]:
    for section_index, section in enumerate(sections):
        for item_index, item in enumerate(section.items):
            yield _candidate(f"content_section.{section_index}.item.{item_index}.body", item.body)


def _paragraph_candidates(article: RowOneLocalArticle) -> Iterable[_SynthesisCandidate]:
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    for index, paragraph in enumerate(article.paragraphs):
        en = normalize_row_one_paragraph(paragraph)
        zh = (
            normalize_row_one_paragraph(article.paragraphs_zh[index])
            if aligned_zh and index < len(article.paragraphs_zh)
            else ""
        )
        yield _candidate(f"paragraph.{index}", LocalizedText(en=en, zh=zh or en))


def _anchors(
    local_article: RowOneLocalArticle,
) -> tuple[RowOneLocalArticleSynthesisAnchor, ...]:
    anchors: list[RowOneLocalArticleSynthesisAnchor] = []
    for section_position, section in enumerate(local_article.content_sections, start=1):
        if len(anchors) >= LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS - 1:
            break
        anchor = _section_anchor(section, section_position=section_position)
        if anchor is not None:
            anchors.append(anchor)
    if len(anchors) < LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS:
        paragraph = _paragraph_anchor(local_article)
        if paragraph is not None:
            anchors.append(paragraph)
    return tuple(anchors[:LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS])


def _section_anchor(
    section: RowOneLocalArticleContentSection,
    *,
    section_position: int,
) -> RowOneLocalArticleSynthesisAnchor | None:
    label = _nonblank_localized_text(section.title)
    support = _nonblank_localized_text(section.body)
    if label is None and support is None:
        return None
    return RowOneLocalArticleSynthesisAnchor(
        label=label
        or LocalizedText(
            en=f"Section {section_position}",
            zh=f"第 {section_position} 节",
        ),
        href=f"#local-article-content-section-{section_position}",
        support=_truncate_localized_text(
            support,
            LOCAL_ARTICLE_SYNTHESIS_BRIEF_ANCHOR_SUPPORT_CHARS,
        )
        if support is not None
        else None,
    )


def _paragraph_anchor(article: RowOneLocalArticle) -> RowOneLocalArticleSynthesisAnchor | None:
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    for index, paragraph in enumerate(article.paragraphs):
        en = normalize_row_one_paragraph(paragraph)
        if not en:
            continue
        zh = (
            normalize_row_one_paragraph(article.paragraphs_zh[index])
            if aligned_zh and index < len(article.paragraphs_zh)
            else ""
        )
        number = index + 1
        support = _truncate_localized_text(
            LocalizedText(en=en, zh=zh or en),
            LOCAL_ARTICLE_SYNTHESIS_BRIEF_ANCHOR_SUPPORT_CHARS,
        )
        return RowOneLocalArticleSynthesisAnchor(
            label=LocalizedText(en=f"Paragraph {number}", zh=f"第 {number} 段"),
            href=f"#local-article-paragraph-{number}",
            support=support,
        )
    return None


def _reader_move(
    *,
    anchors: Sequence[RowOneLocalArticleSynthesisAnchor],
    local_article: RowOneLocalArticle,
) -> LocalizedText:
    if anchors:
        return LocalizedText(
            en=_truncate(
                "Read next through the saved body anchors that connect the "
                "synthesis to the local article text.",
                LOCAL_ARTICLE_SYNTHESIS_BRIEF_CARD_CHARS,
            ),
            zh=_truncate(
                "下一步沿着已保存正文锚点阅读，把综合判断接回本地文章文本。",
                LOCAL_ARTICLE_SYNTHESIS_BRIEF_CARD_CHARS,
            ),
        )
    if local_article.content_sections:
        return LocalizedText(
            en="Read next through the organized body sections already stored on this page.",
            zh="下一步阅读本页已经整理好的正文栏目。",
        )
    return LocalizedText(
        en="Read next through the saved local article body below.",
        zh="下一步阅读下方已保存的本地文章正文。",
    )


def _nonblank_localized_text(value: LocalizedText | None) -> LocalizedText | None:
    if value is None:
        return None
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _truncate_localized_text(value: LocalizedText | None, limit: int) -> LocalizedText | None:
    text = _nonblank_localized_text(value)
    if text is None:
        return None
    return LocalizedText(en=_truncate(text.en, limit), zh=_truncate(text.zh, limit))


def _truncate(value: str, limit: int) -> str:
    cleaned = " ".join(clean_row_one_text(value).split())
    if not cleaned and value.strip():
        cleaned = normalize_row_one_paragraph(value)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: max(0, limit - 3)].rstrip() + "..."


def _normalized_candidate_key(value: LocalizedText) -> str:
    text = _nonblank_localized_text(value)
    if text is None:
        return ""
    return f"{text.en.casefold()}|{text.zh.casefold()}"
