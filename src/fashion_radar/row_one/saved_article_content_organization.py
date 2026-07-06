from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentKey,
    RowOneLocalArticleContentSection,
    RowOneReference,
)

MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_GROUPS = 4
MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_CARDS = 4
MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_REFERENCES = 4


@dataclass(frozen=True)
class RowOneSavedArticleContentOrganizationCard:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleContentOrganizationGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: list[RowOneSavedArticleContentOrganizationCard]


@dataclass(frozen=True)
class RowOneSavedArticleContentOrganization:
    groups: list[RowOneSavedArticleContentOrganizationGroup]


_GROUPS: tuple[
    tuple[RowOneLocalArticleContentKey, LocalizedText, LocalizedText],
    ...,
] = (
    (
        "takeaways",
        LocalizedText(zh="优先阅读", en="Read First"),
        LocalizedText(zh="保存正文中的关键要点", en="Key takeaways from saved articles"),
    ),
    (
        "entities",
        LocalizedText(zh="人物与品牌", en="People & Brands"),
        LocalizedText(
            zh="正文提到的品牌、人物与设计师",
            en="Brands, people, and designers mentioned",
        ),
    ),
    (
        "product_signals",
        LocalizedText(zh="产品", en="Products"),
        LocalizedText(zh="包袋、鞋履与产品信号", en="Bags, shoes, and product signals"),
    ),
    (
        "brand_signals",
        LocalizedText(zh="来源结构", en="Source Structure"),
        LocalizedText(
            zh="来源结构与品牌信号背景",
            en="Source structure and brand-signal context",
        ),
    ),
)


def build_row_one_saved_article_content_organization(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleContentOrganization | None:
    groups: list[RowOneSavedArticleContentOrganizationGroup] = []
    for group_key, group_title, group_dek in _GROUPS[
        :MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_GROUPS
    ]:
        cards: list[RowOneSavedArticleContentOrganizationCard] = []
        for story in edition.stories:
            article = local_articles_by_story_id.get(story.id)
            if article is None:
                continue
            if article.story_id != story.id:
                continue
            if not safe_local_article_story_id(story.id):
                continue
            if not is_safe_row_one_detail_path(story.detail_path):
                continue
            if not _has_nonblank_paragraph(article):
                continue
            selected = _first_usable_section(article.content_sections, group_key)
            if selected is None:
                continue
            position, section = selected
            lead = _lead_text(section.items, article)
            if lead is None:
                continue
            cards.append(
                RowOneSavedArticleContentOrganizationCard(
                    title=LocalizedText(zh=story.headline, en=story.headline),
                    source_name=_source_display_name(article),
                    section_title=_section_title(edition, story.section_key),
                    section_label=section.title,
                    lead=lead,
                    detail_path=(f"{story.detail_path}#local-article-content-section-{position}"),
                    paragraph_indices=_paragraph_indices(section.items, article),
                    references=_references(section.items),
                )
            )
            if len(cards) >= MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_CARDS:
                break
        if cards:
            groups.append(
                RowOneSavedArticleContentOrganizationGroup(
                    key=group_key,
                    title=group_title,
                    dek=group_dek,
                    cards=cards,
                )
            )
    if not groups:
        return None
    return RowOneSavedArticleContentOrganization(groups=groups)


def _has_nonblank_paragraph(article: RowOneLocalArticle) -> bool:
    return any(paragraph.strip() for paragraph in article.paragraphs)


def _first_usable_section(
    sections: Iterable[RowOneLocalArticleContentSection],
    key: RowOneLocalArticleContentKey,
) -> tuple[int, RowOneLocalArticleContentSection] | None:
    for position, section in enumerate(sections, start=1):
        if section.key != key:
            continue
        if any(_item_has_usable_content(item) for item in section.items):
            return position, section
    return None


def _item_has_usable_content(item: RowOneLocalArticleContentItem) -> bool:
    return _item_body(item) is not None or bool(item.references) or bool(item.paragraph_indices)


def _lead_text(
    items: Iterable[RowOneLocalArticleContentItem],
    article: RowOneLocalArticle,
) -> LocalizedText | None:
    for item in items:
        body = _item_body(item)
        if body is not None:
            return body
    return _first_paragraph_text(article)


def _item_body(item: RowOneLocalArticleContentItem) -> LocalizedText | None:
    if item.body is None:
        return None
    en = item.body.en.strip()
    zh = item.body.zh.strip()
    if not en and not zh:
        return None
    return LocalizedText(zh=zh or en, en=en or zh)


def _first_paragraph_text(article: RowOneLocalArticle) -> LocalizedText | None:
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    for index, paragraph in enumerate(article.paragraphs):
        en = paragraph.strip()
        if not en:
            continue
        zh = article.paragraphs_zh[index].strip() if aligned_zh else ""
        return LocalizedText(zh=zh or en, en=en)
    return None


def _paragraph_indices(
    items: Iterable[RowOneLocalArticleContentItem],
    article: RowOneLocalArticle,
) -> tuple[int, ...]:
    valid_indices: list[int] = []
    seen: set[int] = set()
    for item in items:
        for index in item.paragraph_indices:
            if index < 0 or index >= len(article.paragraphs):
                continue
            if not article.paragraphs[index].strip():
                continue
            if index in seen:
                continue
            seen.add(index)
            valid_indices.append(index)
    return tuple(valid_indices)


def _references(items: Iterable[RowOneLocalArticleContentItem]) -> tuple[RowOneReference, ...]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        for ref in item.references:
            dedupe_key = (
                " ".join(ref.name.split()).casefold(),
                " ".join(ref.type.split()).casefold(),
                " ".join(ref.label.split()).casefold(),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            refs.append(
                RowOneReference(
                    name=ref.name.strip(),
                    type=ref.type.strip(),
                    label=ref.label.strip(),
                )
            )
            if len(refs) >= MAX_SAVED_ARTICLE_CONTENT_ORGANIZATION_REFERENCES:
                return tuple(refs)
    return tuple(refs)


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
