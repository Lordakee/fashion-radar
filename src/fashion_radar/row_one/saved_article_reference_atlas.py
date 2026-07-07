from __future__ import annotations

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

MAX_SAVED_ARTICLE_REFERENCE_ATLAS_BUCKETS = 4
MAX_SAVED_ARTICLE_REFERENCE_ATLAS_REFERENCES = 6
MAX_SAVED_ARTICLE_REFERENCE_ATLAS_SUPPORTS = 3


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasEntry:
    name: str
    reference_type: str
    label: str
    support_count: int
    source_count: int
    supports: tuple[RowOneSavedArticleReferenceAtlasSupport, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlasBucket:
    key: str
    title: LocalizedText
    dek: LocalizedText
    reference_count: int
    support_count: int
    source_count: int
    references: tuple[RowOneSavedArticleReferenceAtlasEntry, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReferenceAtlas:
    bucket_count: int
    reference_count: int
    support_count: int
    source_count: int
    buckets: tuple[RowOneSavedArticleReferenceAtlasBucket, ...]


@dataclass(frozen=True)
class _ReferenceAccumulator:
    name: str
    reference_type: str
    label: str
    first_seen: int
    supports: tuple[RowOneSavedArticleReferenceAtlasSupport, ...] = ()
    support_keys: frozenset[tuple[str, str, str]] = frozenset()
    source_keys: frozenset[str] = frozenset()


_BUCKET_ORDER = ("brands", "people", "products", "source_context")

_BUCKET_METADATA: dict[str, tuple[LocalizedText, LocalizedText]] = {
    "brands": (
        LocalizedText(en="Brands", zh="品牌"),
        LocalizedText(
            en="Brand references already present in saved local article organization.",
            zh="保存本地文章组织中已经出现的品牌引用。",
        ),
    ),
    "people": (
        LocalizedText(en="People", zh="人物"),
        LocalizedText(
            en="People, designers, and creative figures referenced by saved cards.",
            zh="保存卡片中提到的人物、设计师与创意角色。",
        ),
    ),
    "products": (
        LocalizedText(en="Products", zh="产品"),
        LocalizedText(
            en="Products, silhouettes, and item-level references in saved coverage.",
            zh="保存报道中的产品、廓形与单品级引用。",
        ),
    ),
    "source_context": (
        LocalizedText(en="Source Context", zh="来源语境"),
        LocalizedText(
            en="Source and context references that frame saved article evidence.",
            zh="用于组织保存文章证据的来源与语境引用。",
        ),
    ),
}

_BRAND_TERMS = frozenset(
    {
        "brand",
        "brands",
        "designer brand",
        "fashion house",
        "house",
        "label",
        "maison",
        "tracked",
    }
)
_PEOPLE_TERMS = frozenset(
    {
        "celebrity",
        "creative",
        "creative director",
        "designer",
        "editor",
        "founder",
        "model",
        "people",
        "person",
        "stylist",
    }
)
_PRODUCT_TERMS = frozenset(
    {
        "accessories",
        "accessory",
        "apparel",
        "bag",
        "bags",
        "dress",
        "flat",
        "flats",
        "footwear",
        "handbag",
        "jewelry",
        "product",
        "products",
        "shoe",
        "shoes",
        "silhouette",
        "skirt",
        "sneaker",
        "sneakers",
        "watch",
    }
)
_SOURCE_CONTEXT_TERMS = frozenset(
    {
        "channel",
        "context",
        "coverage",
        "event",
        "market",
        "publication",
        "retailer",
        "source",
        "source context",
        "store",
    }
)


def build_row_one_saved_article_reference_atlas(
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleReferenceAtlas | None:
    if library is None or organization is None:
        return None

    allowed_detail_paths = _library_detail_paths(library)
    if not allowed_detail_paths:
        return None

    accumulators: dict[str, dict[str, _ReferenceAccumulator]] = {}
    next_seen_index = 0

    for group in organization.groups:
        for card in group.cards:
            support = _atlas_support(card, allowed_detail_paths)
            if support is None or not card.references:
                continue
            support_key = (
                support.detail_path,
                _normalized_text(support.lead.en).casefold(),
                _normalized_text(support.lead.zh).casefold(),
            )
            source_key = _source_key(support.source_name)
            for reference in card.references:
                bucket_key = _bucket_key(reference)
                if bucket_key is None:
                    continue
                reference_name = _normalized_text(reference.name)
                if not reference_name:
                    continue
                reference_key = reference_name.casefold()
                bucket = accumulators.setdefault(bucket_key, {})
                accumulator = bucket.get(reference_key)
                if accumulator is None:
                    accumulator = _ReferenceAccumulator(
                        name=reference_name,
                        reference_type=_normalized_text(reference.type),
                        label=_normalized_text(reference.label),
                        first_seen=next_seen_index,
                    )
                    bucket[reference_key] = accumulator
                    next_seen_index += 1
                if support_key in accumulator.support_keys:
                    continue
                reference_type = accumulator.reference_type or _normalized_text(reference.type)
                label = accumulator.label or _normalized_text(reference.label)
                bucket[reference_key] = _ReferenceAccumulator(
                    name=accumulator.name,
                    reference_type=reference_type,
                    label=label,
                    first_seen=accumulator.first_seen,
                    supports=(*accumulator.supports, support),
                    support_keys=accumulator.support_keys | {support_key},
                    source_keys=accumulator.source_keys | {source_key},
                )

    buckets: list[RowOneSavedArticleReferenceAtlasBucket] = []
    global_source_keys: set[str] = set()
    total_reference_count = 0
    total_support_count = 0

    for bucket_key in _BUCKET_ORDER:
        bucket_accumulators = accumulators.get(bucket_key, {})
        references = [
            accumulator for accumulator in bucket_accumulators.values() if accumulator.supports
        ]
        if not references:
            continue
        references.sort(key=lambda item: (-len(item.supports), item.first_seen))
        rendered_accumulators = references[:MAX_SAVED_ARTICLE_REFERENCE_ATLAS_REFERENCES]
        rendered_references = tuple(
            _atlas_entry(accumulator) for accumulator in rendered_accumulators
        )
        bucket_source_keys: set[str] = set()
        for accumulator in rendered_accumulators:
            bucket_source_keys.update(accumulator.source_keys)
        bucket_support_count = sum(reference.support_count for reference in rendered_references)
        global_source_keys.update(bucket_source_keys)
        title, dek = _BUCKET_METADATA[bucket_key]
        buckets.append(
            RowOneSavedArticleReferenceAtlasBucket(
                key=bucket_key,
                title=title,
                dek=dek,
                reference_count=len(rendered_references),
                support_count=bucket_support_count,
                source_count=len(bucket_source_keys),
                references=rendered_references,
            )
        )
        total_reference_count += len(rendered_references)
        total_support_count += bucket_support_count
        if len(buckets) >= MAX_SAVED_ARTICLE_REFERENCE_ATLAS_BUCKETS:
            break

    if not buckets:
        return None
    return RowOneSavedArticleReferenceAtlas(
        bucket_count=len(buckets),
        reference_count=total_reference_count,
        support_count=total_support_count,
        source_count=len(global_source_keys),
        buckets=tuple(buckets),
    )


def _atlas_entry(
    accumulator: _ReferenceAccumulator,
) -> RowOneSavedArticleReferenceAtlasEntry:
    supports = accumulator.supports[:MAX_SAVED_ARTICLE_REFERENCE_ATLAS_SUPPORTS]
    return RowOneSavedArticleReferenceAtlasEntry(
        name=accumulator.name,
        reference_type=accumulator.reference_type,
        label=accumulator.label,
        support_count=len(accumulator.supports),
        source_count=len(accumulator.source_keys),
        supports=supports,
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


def _atlas_support(
    card: RowOneSavedArticleContentOrganizationCard,
    allowed_detail_paths: set[str],
) -> RowOneSavedArticleReferenceAtlasSupport | None:
    href = _safe_content_section_href(card.detail_path)
    if href is None:
        return None
    detail_path = _detail_path_key(href)
    if detail_path is None or detail_path not in allowed_detail_paths:
        return None
    return RowOneSavedArticleReferenceAtlasSupport(
        title=card.title,
        source_name=card.source_name,
        section_title=card.section_title,
        section_label=card.section_label,
        lead=card.lead,
        detail_path=href,
        paragraph_indices=card.paragraph_indices,
    )


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith("local-article-content-section-"):
        return None
    number = fragment.removeprefix("local-article-content-section-")
    if not number.isascii() or not number.isdecimal() or len(number) > 6:
        return None
    section_index = int(number)
    if number != str(section_index) or section_index < 1:
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


def _bucket_key(reference: RowOneReference) -> str | None:
    values = {
        _normalized_bucket_text(reference.type),
        _normalized_bucket_text(reference.label),
    }
    values.discard("")
    if values & _BRAND_TERMS:
        return "brands"
    if values & _PEOPLE_TERMS:
        return "people"
    if values & _PRODUCT_TERMS:
        return "products"
    if values & _SOURCE_CONTEXT_TERMS:
        return "source_context"
    if values:
        return "source_context"
    return None


def _source_key(name: str) -> str:
    return _normalized_text(name).casefold()


def _normalized_text(value: str) -> str:
    return " ".join(value.split())


def _normalized_bucket_text(value: str) -> str:
    return _normalized_text(value.replace("_", " ").replace("-", " ")).casefold()
