from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT = 5
DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT = 3
DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS = 170

_BUCKET_ORDER = ("brands", "products", "people")
_BUCKET_TITLES = {
    "brands": LocalizedText(en="Brands", zh="品牌"),
    "products": LocalizedText(en="Products", zh="单品"),
    "people": LocalizedText(en="People", zh="人物"),
}
_BUCKET_REFERENCE_TYPES = {
    "brands": "brand",
    "products": "product",
    "people": "person",
}


@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigestSupport:
    title: LocalizedText
    source_name: str
    label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigestItem:
    name: LocalizedText
    reference_type: str
    article_count: int
    source_count: int
    supports: tuple[RowOneDailyLocalBrandProductPeopleSignalDigestSupport, ...]


@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigestBucket:
    key: str
    title: LocalizedText
    items: tuple[RowOneDailyLocalBrandProductPeopleSignalDigestItem, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalBrandProductPeopleSignalDigest:
    title: LocalizedText
    dek: LocalizedText
    article_count: int
    source_count: int
    entity_count: int
    buckets: tuple[RowOneDailyLocalBrandProductPeopleSignalDigestBucket, ...]


@dataclass
class _DigestItemDraft:
    name: str
    reference_type: str
    story_ids: set[str] = field(default_factory=set)
    source_keys: set[str] = field(default_factory=set)
    supports: list[RowOneDailyLocalBrandProductPeopleSignalDigestSupport] = field(
        default_factory=list
    )
    support_keys: set[tuple[str, int]] = field(default_factory=set)


def build_row_one_daily_local_brand_product_people_signal_digest(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalBrandProductPeopleSignalDigest | None:
    drafts_by_bucket: dict[str, dict[str, _DigestItemDraft]] = {
        bucket_key: {} for bucket_key in _BUCKET_ORDER
    }
    contributing_story_ids: set[str] = set()
    contributing_source_keys: set[str] = set()

    for story in edition.stories:
        article = _valid_article(story.id, local_articles_by_story_id)
        if article is None:
            continue
        page_href = _safe_article_page_href(
            story.id,
            article_hrefs_by_story_id.get(story.id),
        )
        if page_href is None:
            continue

        source_name = _source_name(article.source_name, story.source_name)
        source_key = _source_key(article.source_name) or _source_key(story.source_name)
        if not _add_article_references(
            drafts_by_bucket,
            story_id=story.id,
            article=article,
            article_title=_article_title(story.headline, article.title, story.id),
            source_name=source_name,
            source_key=source_key,
            page_href=page_href,
        ):
            continue
        contributing_story_ids.add(story.id)
        if source_key is not None:
            contributing_source_keys.add(source_key)

    if len(contributing_story_ids) < 2:
        return None

    buckets: list[RowOneDailyLocalBrandProductPeopleSignalDigestBucket] = []
    entity_count = 0
    for bucket_key in _BUCKET_ORDER:
        drafts = tuple(draft for draft in drafts_by_bucket[bucket_key].values() if draft.supports)
        if not drafts:
            continue
        entity_count += len(drafts)
        items = tuple(
            RowOneDailyLocalBrandProductPeopleSignalDigestItem(
                name=LocalizedText(en=draft.name, zh=draft.name),
                reference_type=draft.reference_type,
                article_count=len(draft.story_ids),
                source_count=len(draft.source_keys),
                supports=tuple(draft.supports),
            )
            for draft in drafts[:DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_ITEM_LIMIT]
        )
        if not items:
            continue
        buckets.append(
            RowOneDailyLocalBrandProductPeopleSignalDigestBucket(
                key=bucket_key,
                title=_BUCKET_TITLES[bucket_key],
                items=items,
                total_count=len(drafts),
            )
        )

    if not buckets:
        return None

    return RowOneDailyLocalBrandProductPeopleSignalDigest(
        title=LocalizedText(
            en="Daily Local Brand, Product & People Signal Digest",
            zh="每日本地品牌、单品与人物信号摘要",
        ),
        dek=LocalizedText(
            en=(
                "A factual cross-article read of brands, products, and people "
                "in today's saved local coverage."
            ),
            zh="基于今日保存本地报道，对品牌、单品与人物进行事实性跨文章整理。",
        ),
        article_count=len(contributing_story_ids),
        source_count=len(contributing_source_keys),
        entity_count=entity_count,
        buckets=tuple(buckets),
    )


def _valid_article(
    story_id: str,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneLocalArticle | None:
    if not safe_local_article_story_id(story_id):
        return None
    article = local_articles_by_story_id.get(story_id)
    if article is None or article.story_id != story_id:
        return None
    return article


def _add_article_references(
    drafts_by_bucket: dict[str, dict[str, _DigestItemDraft]],
    *,
    story_id: str,
    article: RowOneLocalArticle,
    article_title: LocalizedText,
    source_name: str,
    source_key: str | None,
    page_href: str,
) -> bool:
    emitted = False
    for section_position, section in enumerate(article.content_sections, start=1):
        label = _support_label(section)
        if label is None:
            continue
        href = _content_section_href(page_href, section_position)
        for item in section.items:
            excerpt = _support_excerpt(item, section)
            if excerpt is None:
                continue
            seen_reference_keys: set[tuple[str, str]] = set()
            for reference in item.references:
                bucket_key = row_one_saved_article_reference_bucket(reference)
                if bucket_key not in _BUCKET_ORDER:
                    continue
                name = normalize_row_one_paragraph(reference.name)
                if not name:
                    continue
                reference_key = (bucket_key, name.casefold())
                if reference_key in seen_reference_keys:
                    continue
                seen_reference_keys.add(reference_key)
                bucket_drafts = drafts_by_bucket[bucket_key]
                draft = bucket_drafts.get(reference_key[1])
                if draft is None:
                    draft = _DigestItemDraft(
                        name=name,
                        reference_type=_BUCKET_REFERENCE_TYPES[bucket_key],
                    )
                    bucket_drafts[reference_key[1]] = draft

                draft.story_ids.add(story_id)
                if source_key is not None:
                    draft.source_keys.add(source_key)
                support_key = (story_id, section_position)
                if (
                    support_key not in draft.support_keys
                    and len(draft.supports)
                    < DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_SUPPORT_LIMIT
                ):
                    draft.support_keys.add(support_key)
                    draft.supports.append(
                        RowOneDailyLocalBrandProductPeopleSignalDigestSupport(
                            title=article_title,
                            source_name=source_name,
                            label=label,
                            excerpt=excerpt,
                            href=href,
                        )
                    )
                emitted = True
    return emitted


def _support_label(
    section: RowOneLocalArticleContentSection,
) -> LocalizedText | None:
    return _clean_optional_localized(
        section.title,
        DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS,
    )


def _support_excerpt(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
) -> LocalizedText | None:
    excerpt = _clean_optional_localized(
        item.body,
        DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS,
    )
    if excerpt is not None:
        return excerpt
    return _clean_optional_localized(
        section.body,
        DAILY_LOCAL_BRAND_PRODUCT_PEOPLE_SIGNAL_DIGEST_EXCERPT_CHARS,
    )


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if (
        "://" in href
        or "//" in href
        or "?" in href
        or "#" in href
        or href.startswith((".", "/", "//"))
    ):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..", "index.html")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name


def _content_section_href(page_href: str, section_position: int) -> str:
    return f"articles/{page_href}#local-article-content-section-{section_position}"


def _article_title(headline: str, article_title: str | None, story_id: str) -> LocalizedText:
    title = normalize_row_one_paragraph(headline) or normalize_row_one_paragraph(
        article_title or ""
    )
    title = title or story_id
    return LocalizedText(en=title, zh=title)


def _source_name(article_source_name: str, story_source_name: str) -> str:
    return (
        normalize_row_one_paragraph(article_source_name)
        or normalize_row_one_paragraph(story_source_name)
        or "Saved local source"
    )


def _source_key(source_name: str) -> str | None:
    normalized = normalize_row_one_paragraph(source_name)
    return normalized.casefold() if normalized else None


def _clean_optional_localized(text: LocalizedText | None, limit: int) -> LocalizedText | None:
    if text is None:
        return None
    en = _truncate(normalize_row_one_paragraph(text.en), limit)
    zh = _truncate(normalize_row_one_paragraph(text.zh), limit)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: max(limit - 3, 0)].rstrip()}..."
