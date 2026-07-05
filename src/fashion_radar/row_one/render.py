from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.briefing_topics import briefing_topics_payload
from fashion_radar.row_one.display import display_for_story, safe_story_image_src
from fashion_radar.row_one.local_intelligence import build_row_one_local_article_intelligence
from fashion_radar.row_one.models import (
    RowOneDailyLocalIntelligenceSection,
    RowOneEdition,
    RowOneLink,
    RowOneLocalArticle,
    RowOneSection,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
from fashion_radar.row_one.readiness import build_row_one_readiness
from fashion_radar.row_one.templates import (
    _validated_detail_relative_path,
    render_detail_html,
    render_index_html,
    row_one_css,
    row_one_js,
)
from fashion_radar.row_one.utils import isoformat_z, safe_external_url, utc_datetime

GENERATED_CHILDREN = ("index.html", ".row-one-site", "details", "assets", "data")
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v7"
ROW_ONE_MANIFEST_CONTRACT_VERSION = "row-one-manifest/v1"
ROW_ONE_MANIFEST_SCHEMA_PATH = "schemas/row-one-manifest.schema.json"
ROW_ONE_RUNTIME_CONTRACT_VERSION = "row-one-runtime/v1"
ROW_ONE_RUNTIME_SCHEMA_PATH = "schemas/row-one-runtime.schema.json"


@dataclass(frozen=True)
class RowOneRenderResult:
    output_dir: Path
    index_path: Path
    story_count: int
    edition: RowOneEdition


def render_row_one_site(
    edition: RowOneEdition,
    output_dir: Path,
    *,
    latest_only: bool = False,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle] | None = None,
) -> RowOneRenderResult:
    _validate_unique_story_routes(edition)
    if latest_only:
        clean_row_one_site_children(output_dir)
    local_articles_by_story_id = local_articles_by_story_id or {}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    _write_assets(output_dir)
    app_payload = build_row_one_app_payload(edition)
    local_article_intelligence = build_row_one_local_article_intelligence(
        edition,
        local_articles_by_story_id,
    )
    index_path = output_dir / "index.html"
    index_path.write_text(
        render_index_html(
            edition,
            app_payload=app_payload,
            local_article_intelligence=local_article_intelligence,
        ),
        encoding="utf-8",
    )
    _write_detail_pages(
        edition,
        output_dir / "details",
        local_articles_by_story_id=local_articles_by_story_id,
    )
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "edition.json").write_text(
        json.dumps(app_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    runtime_payload = build_row_one_runtime_payload(edition, app_payload)
    (data_dir / "runtime.json").write_text(
        json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_payload = build_row_one_manifest_payload(edition, app_payload)
    (data_dir / "manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_local_article_files(edition, data_dir, local_articles_by_story_id)
    _write_local_article_intelligence_file(data_dir, local_article_intelligence)
    return RowOneRenderResult(
        output_dir=output_dir,
        index_path=index_path,
        story_count=len(edition.stories),
        edition=edition,
    )


def _validate_unique_story_routes(edition: RowOneEdition) -> None:
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for story in edition.stories:
        if story.id in seen_ids:
            raise ValueError(f"Duplicate ROW ONE story id: {story.id}")
        seen_ids.add(story.id)
        if story.detail_path in seen_paths:
            raise ValueError(f"Duplicate ROW ONE detail path: {story.detail_path}")
        seen_paths.add(story.detail_path)


def clean_row_one_site_children(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    marker = output_dir / ".row-one-site"
    generated_children = [output_dir / child_name for child_name in GENERATED_CHILDREN]
    has_generated_children = any(child.exists() for child in generated_children if child != marker)
    if has_generated_children and not marker.exists():
        raise ValueError(f"ROW ONE output directory is not marked as generated: {output_dir}")
    for child_name in GENERATED_CHILDREN:
        child = output_dir / child_name
        if child.is_dir():
            rmtree(child)
        elif child.exists():
            child.unlink()


def _write_assets(output_dir: Path) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "row-one.css").write_text(row_one_css(), encoding="utf-8")
    (assets_dir / "row-one.js").write_text(row_one_js(), encoding="utf-8")


def _write_detail_pages(
    edition: RowOneEdition,
    details_dir: Path,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> None:
    details_dir.mkdir(parents=True, exist_ok=True)
    for story in edition.stories:
        pure_path = _validated_detail_relative_path(story.detail_path)
        if pure_path is None:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path = details_dir.parent / Path(*pure_path.parts)
        if detail_path.parent != details_dir:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path.write_text(
            render_detail_html(
                edition,
                story,
                local_article=local_articles_by_story_id.get(story.id),
            ),
            encoding="utf-8",
        )


def _write_local_article_files(
    edition: RowOneEdition,
    data_dir: Path,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> None:
    current_story_ids = {story.id for story in edition.stories}
    writable_articles = {
        story_id: article
        for story_id, article in local_articles_by_story_id.items()
        if story_id in current_story_ids
        and safe_local_article_story_id(story_id)
        and article.paragraphs
    }
    if not writable_articles:
        return
    articles_dir = data_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    for story_id, article in sorted(writable_articles.items()):
        (articles_dir / f"{story_id}.json").write_text(
            json.dumps(article.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _write_local_article_intelligence_file(
    data_dir: Path,
    sections: Sequence[RowOneDailyLocalIntelligenceSection],
) -> None:
    writable_sections = [section for section in sections if section.items]
    if not writable_sections:
        return
    (data_dir / "local-intelligence.json").write_text(
        json.dumps(
            [section.model_dump(mode="json") for section in writable_sections],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_row_one_app_payload(edition: RowOneEdition) -> dict[str, object]:
    stories = [_story_payload(edition, story) for story in edition.stories]
    sections = [_section_payload(edition, section) for section in edition.sections]
    content_sections = [_content_section_payload(section, stories) for section in edition.sections]
    daily_digest = _daily_digest_payload(edition, stories)
    story_directory = _story_directory_payload(stories)
    evidence_count = sum(_safe_evidence_count(story.evidence) for story in edition.stories)
    return {
        "contract_version": ROW_ONE_APP_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "summary": edition.summary.model_dump(mode="json"),
        "edition_brief": _edition_brief_payload(
            stories,
            content_sections,
            daily_digest,
            story_directory,
            evidence_count,
        ),
        "signal_synthesis": _signal_synthesis_payload(stories),
        "sections": sections,
        "content_sections": content_sections,
        "daily_digest": daily_digest,
        "story_directory": story_directory,
        "stories": stories,
        "story_count": len(stories),
        "evidence_count": evidence_count,
    }


SIGNAL_SYNTHESIS_GROUPS = (
    ("brand", {"zh": "品牌", "en": "Brands"}),
    ("product", {"zh": "单品", "en": "Products"}),
    ("designer", {"zh": "设计师", "en": "Designers"}),
    ("person", {"zh": "人物", "en": "People"}),
)
SIGNAL_SYNTHESIS_BOUNDARIES = {
    "zh": "本地观察，需人工复核。",
    "en": "Local observed signals; review required.",
}


def _signal_synthesis_payload(stories: list[dict[str, object]]) -> dict[str, object]:
    groups = _signal_synthesis_groups(stories)
    signal_count = sum(int(group["signal_count"]) for group in groups)
    return {
        "title": {"zh": "今日信号整理", "en": "Signal Synthesis"},
        "dek": _signal_synthesis_dek(len(stories), signal_count),
        "group_count": len(groups),
        "signal_count": signal_count,
        "boundaries": dict(SIGNAL_SYNTHESIS_BOUNDARIES),
        "groups": groups,
    }


def _signal_synthesis_groups(stories: list[dict[str, object]]) -> list[dict[str, object]]:
    story_href_by_id = _signal_story_href_map(stories)
    grouped: dict[str, list[dict[str, object]]] = {
        key: [] for key, _label in SIGNAL_SYNTHESIS_GROUPS
    }
    for topic in briefing_topics_payload(stories):
        signal = _signal_payload_from_topic(topic, story_href_by_id)
        if signal is None:
            continue
        grouped[str(signal["type"])].append(signal)

    groups: list[dict[str, object]] = []
    for group_key, group_label in SIGNAL_SYNTHESIS_GROUPS:
        signals = sorted(grouped[group_key], key=_signal_synthesis_sort_key)
        if not signals:
            continue
        groups.append(
            {
                "key": group_key,
                "label": dict(group_label),
                "signal_count": len(signals),
                "signals": signals,
            }
        )
    return groups


def _signal_payload_from_topic(
    topic: dict[str, object],
    story_href_by_id: dict[str, str],
) -> dict[str, object] | None:
    topic_type = str(topic.get("topic_type", ""))
    if topic_type not in {group_key for group_key, _label in SIGNAL_SYNTHESIS_GROUPS}:
        return None
    story_ids = [str(story_id) for story_id in topic.get("story_ids", [])]
    if not story_ids:
        return None
    story_refs = _signal_story_refs_from_topic(topic)
    story_ref_ids = [str(ref["story_id"]) for ref in story_refs]
    if story_ref_ids != story_ids:
        raise ValueError("ROW ONE signal story_refs must align with topic story_ids")
    lead_story_id = str(topic.get("lead_story_id") or story_ids[0])
    lead_story_href = story_href_by_id.get(lead_story_id)
    if lead_story_href is None:
        return None
    title = topic.get("title")
    name = ""
    if isinstance(title, dict):
        name = str(title.get("en") or title.get("zh") or "").strip()
    if not name:
        return None
    label = _signal_reference_label(topic.get("source_refs"))
    story_count = int(topic.get("story_count", 0))
    evidence_count = int(topic.get("evidence_count", 0))
    positive_heat_delta_sum = int(topic.get("positive_heat_delta_sum", 0))
    max_heat_delta = int(topic.get("max_heat_delta", 0))
    return {
        "name": name,
        "type": topic_type,
        "label": label,
        "story_count": story_count,
        "evidence_count": evidence_count,
        "positive_heat_delta_sum": max(positive_heat_delta_sum, 0),
        "max_heat_delta": max(max_heat_delta, 0),
        "lead_story_id": lead_story_id,
        "lead_story_href": lead_story_href,
        "summary": _signal_summary(
            name,
            story_count=story_count,
            evidence_count=evidence_count,
            max_heat_delta=max(max_heat_delta, 0),
        ),
        "story_ids": story_ids,
        "story_refs": story_refs,
    }


def _signal_story_refs_from_topic(topic: dict[str, object]) -> list[dict[str, object]]:
    cards = topic.get("cards")
    if not isinstance(cards, list):
        return []
    refs: list[dict[str, object]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        section = card.get("section")
        if not isinstance(section, dict):
            continue
        refs.append(
            {
                "story_id": card["id"],
                "headline": card["headline"],
                "section_key": card["section_key"],
                "section_title": section["title"],
                "detail_href": card["detail_href"],
                "source_name": card["source_name"],
                "published_date": card["published_date"],
                "evidence_count": card["evidence_count"],
                "heat_delta": card["heat_delta"],
            }
        )
    return refs


def _signal_reference_label(source_refs: object) -> str:
    if not isinstance(source_refs, list):
        return ""
    for source_ref in source_refs:
        if not isinstance(source_ref, dict):
            continue
        label = str(source_ref.get("label", "")).strip()
        if label:
            return label
    return ""


def _signal_summary(
    name: str,
    *,
    story_count: int,
    evidence_count: int,
    max_heat_delta: int,
) -> dict[str, str]:
    story_word = _plural_word(story_count, "story", "stories")
    evidence_word = _plural_word(evidence_count, "evidence link", "evidence links")
    return {
        "zh": (
            f"{name} 出现在 {story_count} 条故事中，最高本地提及增量 +{max_heat_delta}，"
            f"带有 {evidence_count} 条证据链接。"
        ),
        "en": (
            f"{name} appears in {story_count} {story_word}, with max local mention delta "
            f"+{max_heat_delta} and {evidence_count} {evidence_word}."
        ),
    }


def _signal_synthesis_dek(story_count: int, signal_count: int) -> dict[str, str]:
    if signal_count == 0:
        return {
            "zh": "暂无可整理的 ROW ONE 信号。",
            "en": "No ROW ONE signals are ready to organize yet.",
        }
    signal_word = _plural_word(signal_count, "readable signal", "readable signals")
    story_word = _plural_word(story_count, "story", "stories")
    return {
        "zh": f"ROW ONE 从今日 {story_count} 条故事中整理出 {signal_count} 个可读信号。",
        "en": (
            f"ROW ONE organized {signal_count} {signal_word} from {story_count} {story_word} today."
        ),
    }


def _signal_story_href_map(stories: list[dict[str, object]]) -> dict[str, str]:
    hrefs: dict[str, str] = {}
    for story in stories:
        story_id = str(story.get("id", ""))
        detail_href = str(story.get("detail_href", ""))
        if story_id and detail_href:
            hrefs[story_id] = detail_href
    return hrefs


def _signal_synthesis_sort_key(signal: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(signal["positive_heat_delta_sum"]),
        -int(signal["evidence_count"]),
        -int(signal["story_count"]),
        str(signal["name"]).casefold(),
        str(signal["name"]),
    )


def build_row_one_manifest_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    story_count = int(app_payload["story_count"])
    return {
        "contract_version": ROW_ONE_MANIFEST_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": app_payload["generated_at"],
        "edition_date": app_payload["edition_date"],
        "manifest_schema_path": ROW_ONE_MANIFEST_SCHEMA_PATH,
        "app_contract": {
            "version": ROW_ONE_APP_CONTRACT_VERSION,
            "path": "data/edition.json",
            "schema_path": "schemas/row-one-app.schema.json",
        },
        "site": {
            "index_path": "index.html",
            "data_path": "data/edition.json",
            "manifest_path": "data/manifest.json",
            "assets_path": "assets/",
            "details_path": "details/",
        },
        "counts": {
            "story_count": story_count,
            "section_count": len(edition.sections),
            "evidence_count": app_payload["evidence_count"],
        },
        "readiness": {
            "status": "ready" if story_count > 0 else "empty",
        },
        "capabilities": {
            "bilingual": True,
            "static_site": True,
            "detail_pages": True,
            "sanitized_external_urls": True,
            "latest_only_cleanup": True,
            "seo_metadata": True,
            "structured_story_metadata": True,
        },
    }


def build_row_one_runtime_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    readiness = build_row_one_readiness(edition)
    return {
        "contract_version": ROW_ONE_RUNTIME_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "runtime_schema_path": ROW_ONE_RUNTIME_SCHEMA_PATH,
        "site": {
            "index_path": "index.html",
            "manifest_path": "data/manifest.json",
            "edition_path": "data/edition.json",
            "runtime_path": "data/runtime.json",
        },
        "refresh": {
            "recommended_time": "04:00",
            "command": (
                'fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site'
            ),
            "latest_only_cleanup": True,
        },
        "serve": {
            "default_host": "127.0.0.1",
            "default_port": 8787,
            "local_url": "http://127.0.0.1:8787",
            "lan_url_hint": "http://<LAN-IP>:8787",
        },
        "counts": {
            "story_count": int(app_payload["story_count"]),
            "section_count": len(edition.sections),
            "evidence_count": int(app_payload["evidence_count"]),
        },
        "readiness": {
            "status": readiness.readiness.en,
            "zh": readiness.readiness.zh,
            "en": readiness.readiness.en,
        },
    }


def _section_payload(edition: RowOneEdition, section: RowOneSection) -> dict[str, object]:
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(edition.section_stories(section.key)),
    }


def _content_section_payload(
    section: RowOneSection,
    stories: list[dict[str, object]],
) -> dict[str, object]:
    section_stories = [story for story in stories if story["section_key"] == section.key]
    story_ids = [str(story["id"]) for story in section_stories]
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(section_stories),
        "lead_story_id": story_ids[0] if story_ids else None,
        "story_ids": story_ids,
        "cards": [_content_card_payload(story) for story in section_stories],
    }


def _daily_digest_payload(
    edition: RowOneEdition,
    stories: list[dict[str, object]],
) -> dict[str, object]:
    read_first_stories = _read_first_digest_stories(stories)
    return {
        "title": {"zh": "今日简报", "en": "Today's Briefing"},
        "dek": _daily_digest_dek(stories),
        "story_count": len(stories),
        "evidence_count": sum(int(story["evidence_count"]) for story in stories),
        "lead_story_id": str(read_first_stories[0]["id"]) if read_first_stories else None,
        "briefing_topics": [
            _content_cards_for_briefing_topic(topic) for topic in briefing_topics_payload(stories)
        ],
        "blocks": [
            _digest_block_payload(
                "read_first",
                {"zh": "先读", "en": "Read First"},
                {
                    "zh": "今日最值得先打开的一条 ROW ONE 信号。",
                    "en": "The first ROW ONE signal to open today.",
                },
                read_first_stories,
            ),
            _digest_block_payload(
                "key_takeaways",
                {"zh": "重点整理", "en": "Key Takeaways"},
                {
                    "zh": "按栏目顺序整理每个非空板块的第一条信号。",
                    "en": "The first signal from each non-empty section, in section order.",
                },
                _key_takeaway_digest_stories(edition, stories),
            ),
            _digest_block_payload(
                "signals_to_watch",
                {"zh": "升温信号", "en": "Signals To Watch"},
                {
                    "zh": "仅按本地原始提及增量筛出的正向变化信号。",
                    "en": "Positive local raw mention deltas worth watching.",
                },
                _signals_to_watch_digest_stories(stories),
            ),
        ],
    }


def _story_directory_payload(stories: list[dict[str, object]]) -> dict[str, object]:
    return {
        "story_count": len(stories),
        "story_ids": [str(story["id"]) for story in stories],
        "routes": [_story_directory_route_payload(story) for story in stories],
    }


def _story_directory_route_payload(story: dict[str, object]) -> dict[str, object]:
    section = story["section"]
    if not isinstance(section, dict):
        raise TypeError("ROW ONE story section payload must be an object")
    return {
        "story_id": story["id"],
        "detail_href": story["detail_href"],
        "section_key": story["section_key"],
        "section_href": section["href"],
        "published_date": story["published_date"],
    }


def _edition_brief_payload(
    stories: list[dict[str, object]],
    content_sections: list[dict[str, object]],
    daily_digest: dict[str, object],
    story_directory: dict[str, object],
    evidence_count: int,
) -> dict[str, object]:
    active_sections = [section for section in content_sections if int(section["story_count"]) > 0]
    topics = daily_digest.get("briefing_topics", [])
    topic_count = len(topics) if isinstance(topics, list) else 0
    path_blocks = _edition_brief_path_blocks(daily_digest)
    lead_story = _story_by_id(stories, daily_digest.get("lead_story_id"))
    lead_href = lead_story["detail_href"] if lead_story is not None else None
    lead_headline = str(lead_story["headline"]) if lead_story is not None else None
    return {
        "title": {"zh": "今日总览", "en": "Edition Brief"},
        "dek": _edition_brief_dek(
            len(stories), len(active_sections), topic_count, len(path_blocks)
        ),
        "lead_story_id": daily_digest.get("lead_story_id"),
        "lead_story_href": lead_href,
        "lead_story_headline": lead_headline,
        "story_directory_story_count": story_directory["story_count"],
        "metrics": [
            _edition_brief_metric("stories", {"zh": "故事", "en": "Stories"}, len(stories)),
            _edition_brief_metric(
                "sections",
                {"zh": "活跃栏目", "en": "Active Sections"},
                len(active_sections),
            ),
            _edition_brief_metric("topics", {"zh": "主题", "en": "Topics"}, topic_count),
            _edition_brief_metric(
                "evidence",
                {"zh": "证据链接", "en": "Evidence Links"},
                evidence_count,
            ),
        ],
        "summary_points": _edition_brief_summary_points(
            lead_story,
            active_sections,
            topics if isinstance(topics, list) else [],
            path_blocks,
            stories,
        ),
        "links": _edition_brief_links(lead_href, topic_count, path_blocks),
    }


def _edition_brief_metric(key: str, label: dict[str, str], value: int) -> dict[str, object]:
    return {"key": key, "label": label, "value": value}


def _story_by_id(stories: list[dict[str, object]], story_id: object) -> dict[str, object] | None:
    return next((story for story in stories if story["id"] == story_id), None)


def _edition_brief_path_blocks(daily_digest: dict[str, object]) -> list[dict[str, object]]:
    blocks = daily_digest.get("blocks", [])
    if not isinstance(blocks, list):
        return []
    digest_blocks = [block for block in blocks if isinstance(block, dict)]
    excluded_story_ids = _read_first_digest_story_ids(digest_blocks)
    return [
        block
        for block in digest_blocks
        if block.get("key") in {"key_takeaways", "signals_to_watch"}
        and _digest_block_cards(block, excluded_story_ids)
    ]


def _read_first_digest_story_ids(blocks: list[dict[str, object]]) -> set[str]:
    read_first_block = next((block for block in blocks if block.get("key") == "read_first"), None)
    if read_first_block is None:
        return set()
    story_ids = read_first_block.get("story_ids")
    if not isinstance(story_ids, list):
        return set()
    return {str(story_id) for story_id in story_ids}


def _digest_block_cards(
    block: dict[str, object],
    excluded_story_ids: set[str],
) -> list[dict[str, object]]:
    cards = block.get("cards")
    if not isinstance(cards, list):
        return []
    return [
        card
        for card in cards
        if isinstance(card, dict) and str(card.get("id")) not in excluded_story_ids
    ]


def _edition_brief_dek(
    story_count: int,
    active_section_count: int,
    topic_count: int,
    path_block_count: int,
) -> dict[str, str]:
    if story_count == 0:
        return {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        }
    return {
        "zh": (
            f"ROW ONE 将今日 {story_count} 条本地时尚信号整理成 "
            f"{active_section_count} 个栏目、{topic_count} 个主题和 "
            f"{path_block_count} 条后续阅读路径。"
        ),
        "en": (
            f"ROW ONE organized {story_count} local fashion signals across "
            f"{active_section_count} sections, "
            f"{topic_count} {_plural_word(topic_count, 'briefing topic', 'briefing topics')}, "
            f"and {path_block_count} "
            f"{_plural_word(path_block_count, 'follow-up path block', 'follow-up path blocks')}."
        ),
    }


def _plural_word(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


EDITION_BRIEF_TOPIC_TYPE_LABELS = {
    "brand": {"zh": "品牌", "en_singular": "brand", "en_plural": "brands"},
    "product": {"zh": "单品", "en_singular": "product", "en_plural": "products"},
    "designer": {"zh": "设计师", "en_singular": "designer", "en_plural": "designers"},
    "person": {"zh": "人物", "en_singular": "person", "en_plural": "people"},
}


def _edition_brief_topic_mix_point(topics: list[object]) -> dict[str, str] | None:
    counts = {topic_type: 0 for topic_type in EDITION_BRIEF_TOPIC_TYPE_LABELS}
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        topic_type = str(topic.get("topic_type", ""))
        if topic_type in counts:
            counts[topic_type] += 1
    active_counts = [(topic_type, count) for topic_type, count in counts.items() if count > 0]
    if not active_counts:
        return None
    zh_parts = [
        f"{EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]['zh']} {count}"
        for topic_type, count in active_counts
    ]
    en_parts = []
    for topic_type, count in active_counts:
        labels = EDITION_BRIEF_TOPIC_TYPE_LABELS[topic_type]
        en_parts.append(
            f"{count} {_plural_word(count, labels['en_singular'], labels['en_plural'])}"
        )
    return {
        "zh": f"主题结构：{'、'.join(zh_parts)}",
        "en": f"Topic mix: {', '.join(en_parts)}",
    }


def _edition_brief_heat_watch_point(
    stories: list[dict[str, object]],
) -> dict[str, str] | None:
    positive_heat_deltas = []
    for story in stories:
        heat_delta = story.get("heat_delta")
        if isinstance(heat_delta, int) and not isinstance(heat_delta, bool) and heat_delta > 0:
            positive_heat_deltas.append(heat_delta)
    if not positive_heat_deltas:
        return None
    signal_count = len(positive_heat_deltas)
    max_heat_delta = max(positive_heat_deltas)
    return {
        "zh": f"升温观察：{signal_count} 条正向热度信号，最高 +{max_heat_delta}",
        "en": (
            f"Heat watch: {signal_count} "
            f"{_plural_word(signal_count, 'positive heat signal', 'positive heat signals')}, "
            f"highest +{max_heat_delta}"
        ),
    }


def _edition_brief_summary_points(
    lead_story: dict[str, object] | None,
    active_sections: list[dict[str, object]],
    topics: list[object],
    path_blocks: list[dict[str, object]],
    stories: list[dict[str, object]],
) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    if lead_story is not None:
        headline = str(lead_story["headline"])
        points.append({"zh": f"先读：{headline}", "en": f"Read first: {headline}"})
    if active_sections:
        zh_sections = "、".join(str(section["title"]["zh"]) for section in active_sections)
        en_sections = ", ".join(str(section["title"]["en"]) for section in active_sections)
        points.append({"zh": f"活跃栏目：{zh_sections}", "en": f"Active sections: {en_sections}"})
    topic_titles = [
        str(topic["title"]["en"])
        for topic in topics
        if isinstance(topic, dict) and isinstance(topic.get("title"), dict)
    ][:4]
    if topic_titles:
        topic_text = ", ".join(topic_titles)
        points.append({"zh": f"整理主题：{topic_text}", "en": f"Briefing topics: {topic_text}"})
    topic_mix_point = _edition_brief_topic_mix_point(topics)
    if topic_mix_point is not None:
        points.append(topic_mix_point)
    heat_watch_point = _edition_brief_heat_watch_point(stories)
    if heat_watch_point is not None:
        points.append(heat_watch_point)
    if path_blocks:
        zh_blocks = "、".join(str(block["title"]["zh"]) for block in path_blocks)
        en_blocks = ", ".join(str(block["title"]["en"]) for block in path_blocks)
        points.append({"zh": f"后续路径：{zh_blocks}", "en": f"Follow-up path: {en_blocks}"})
    if not points:
        points.append({"zh": "暂无可整理的故事。", "en": "No stories are ready to organize yet."})
    return points


def _edition_brief_links(
    lead_href: object,
    topic_count: int,
    path_blocks: list[dict[str, object]],
) -> list[dict[str, object]]:
    links: list[dict[str, object]] = []
    if isinstance(lead_href, str):
        links.append(
            {
                "key": "read_first",
                "label": {"zh": "先读", "en": "Read First"},
                "href": lead_href,
            }
        )
    if topic_count > 0:
        links.append(
            {
                "key": "topics",
                "label": {"zh": "今日主题", "en": "Briefing Topics"},
                "href": "#briefing-topics",
            }
        )
    if path_blocks:
        links.append(
            {
                "key": "path",
                "label": {"zh": "阅读路径", "en": "Briefing Path"},
                "href": "#briefing-path",
            }
        )
    return links


def _content_cards_for_briefing_topic(topic: dict[str, object]) -> dict[str, object]:
    payload = dict(topic)
    payload["cards"] = [
        _content_card_payload(card) for card in topic["cards"] if isinstance(card, dict)
    ]
    return payload


def _daily_digest_dek(stories: list[dict[str, object]]) -> dict[str, str]:
    if not stories:
        return {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        }
    return {
        "zh": f"ROW ONE 将今日 {len(stories)} 条本地时尚信号整理成可直接阅读的简报。",
        "en": f"ROW ONE organized {len(stories)} local fashion signals into an app-ready briefing.",
    }


def _digest_block_payload(
    key: str,
    title: dict[str, str],
    dek: dict[str, str],
    stories: list[dict[str, object]],
) -> dict[str, object]:
    story_ids = [str(story["id"]) for story in stories]
    return {
        "key": key,
        "title": title,
        "dek": dek,
        "story_count": len(stories),
        "story_ids": story_ids,
        "cards": [_content_card_payload(story) for story in stories],
    }


def _read_first_digest_stories(stories: list[dict[str, object]]) -> list[dict[str, object]]:
    top_story = next((story for story in stories if story["section_key"] == "top_stories"), None)
    if top_story is not None:
        return [top_story]
    return stories[:1]


def _key_takeaway_digest_stories(
    edition: RowOneEdition,
    stories: list[dict[str, object]],
) -> list[dict[str, object]]:
    takeaways: list[dict[str, object]] = []
    for section in edition.sections:
        story = next((item for item in stories if item["section_key"] == section.key), None)
        if story is not None:
            takeaways.append(story)
        if len(takeaways) >= 5:
            break
    return takeaways


def _signals_to_watch_digest_stories(
    stories: list[dict[str, object]],
) -> list[dict[str, object]]:
    signals = [
        story
        for story in stories
        if isinstance(story["heat_delta"], int) and int(story["heat_delta"]) > 0
    ]
    signals.sort(
        key=lambda story: (
            -int(story["heat_delta"]),
            str(story["headline"]).casefold(),
            str(story["headline"]),
        )
    )
    return signals[:5]


def _content_card_payload(story: dict[str, object]) -> dict[str, object]:
    return {
        "id": story["id"],
        "story_type": story["story_type"],
        "headline": story["headline"],
        "summary": story["summary"],
        "why_it_matters": story["why_it_matters"],
        "editorial_takeaway": story["editorial_takeaway"],
        "signal_context": story["signal_context"],
        "reader_path": story["reader_path"],
        "detail_href": story["detail_href"],
        "display": story["display"],
        "source_name": story["source_name"],
        "market_region": story["market_region"],
        "source_region": story["source_region"],
        "published_date": story["published_date"],
        "tags": story["tags"],
        "entity_refs": story["entity_refs"],
        "product_refs": story["product_refs"],
        "designer_refs": story["designer_refs"],
        "heat_delta": story["heat_delta"],
        "heat_delta_metric": story["heat_delta_metric"],
        "evidence_count": story["evidence_count"],
    }


def _story_payload(edition: RowOneEdition, story: RowOneStory) -> dict[str, object]:
    section = _section_for_story(edition, story.section_key)
    detail_href = _app_detail_href(story.detail_path)
    published_at_utc = utc_datetime(story.published_at) if story.published_at else None
    return {
        "id": story.id,
        "section_key": story.section_key,
        "story_type": story.story_type,
        "section": {
            "key": section.key,
            "title": section.title.model_dump(mode="json"),
            "href": f"#{section.key}",
        },
        "headline": story.headline,
        "summary": story.summary.model_dump(mode="json"),
        "why_it_matters": story.why_it_matters.model_dump(mode="json"),
        "editorial_takeaway": story.editorial_takeaway.model_dump(mode="json"),
        "signal_context": story.signal_context.model_dump(mode="json"),
        "reader_path": story.reader_path.model_dump(mode="json"),
        "source_name": story.source_name,
        "source_url": safe_external_url(story.source_url),
        "market_region": story.market_region,
        "source_region": story.source_region,
        "display": _display_payload(display_for_story(story)),
        "published_at": isoformat_z(published_at_utc) if published_at_utc else None,
        "published_date": published_at_utc.date().isoformat() if published_at_utc else None,
        "detail_path": detail_href,
        "href": detail_href,
        "detail_href": detail_href,
        "tags": list(story.tags),
        "entity_refs": [_reference_payload(ref) for ref in story.entity_refs],
        "product_refs": [_reference_payload(ref) for ref in story.product_refs],
        "designer_refs": [_reference_payload(ref) for ref in story.designer_refs],
        "heat_delta": story.heat_delta,
        "heat_delta_metric": "raw_mention_delta" if story.heat_delta is not None else None,
        "evidence_count": _safe_evidence_count(story.evidence),
        "evidence": [_evidence_payload(link) for link in story.evidence],
        "detail_sections": _detail_sections_payload(story),
        "evidence_summary": _evidence_summary_payload(story),
    }


def _reference_payload(reference) -> dict[str, object]:
    return reference.model_dump(mode="json")


def _display_payload(display: RowOneStoryDisplay) -> dict[str, object]:
    return {
        "variant": display.variant,
        "accent": display.accent,
        "image": _image_payload(display.image),
    }


def _image_payload(image: RowOneStoryImage | None) -> dict[str, object] | None:
    if image is None:
        return None
    src = safe_story_image_src(image.src)
    if src is None:
        return None
    return {
        "src": src,
        "alt": image.alt.model_dump(mode="json"),
        "credit": image.credit,
        "source_url": safe_external_url(image.source_url),
    }


def _section_for_story(edition: RowOneEdition, section_key: str) -> RowOneSection:
    for section in edition.sections:
        if section.key == section_key:
            return section
    return RowOneSection(
        key=section_key,
        title=type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title()),
        dek=type(edition.summary)(zh="", en=""),
    )


def _evidence_payload(link: RowOneLink) -> dict[str, object]:
    safe_url = safe_external_url(link.url)
    return {
        "title": link.title,
        "url": safe_url,
        "href": safe_url,
        "source_name": link.source_name,
    }


def _detail_sections_payload(story: RowOneStory) -> list[dict[str, object]]:
    return [
        {
            "key": "summary",
            "title": {"en": "Summary", "zh": "摘要"},
            "body": story.summary.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "why_it_matters",
            "title": {"en": "Why It Matters", "zh": "为什么重要"},
            "body": story.why_it_matters.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "editorial_takeaway",
            "title": {"en": "Editorial Takeaway", "zh": "编辑整理"},
            "body": story.editorial_takeaway.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "signal_context",
            "title": {"en": "Signal Context", "zh": "信号背景"},
            "body": story.signal_context.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "reader_path",
            "title": {"en": "Reader Path", "zh": "阅读路径"},
            "body": story.reader_path.model_dump(mode="json"),
            "evidence": [],
        },
        {
            "key": "evidence",
            "title": {"en": "Evidence Trail", "zh": "来源线索"},
            "body": None,
            "evidence": [_evidence_payload(link) for link in story.evidence],
        },
    ]


def _evidence_summary_payload(story: RowOneStory) -> dict[str, object]:
    sources: list[str] = []
    for link in story.evidence:
        if link.source_name not in sources:
            sources.append(link.source_name)
    return {
        "safe_link_count": _safe_evidence_count(story.evidence),
        "total_count": len(story.evidence),
        "primary_source_name": story.source_name,
        "sources": sources,
    }


def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if safe_external_url(link.url) is not None)


def _app_detail_href(detail_path: str) -> str:
    pure_path = _validated_detail_relative_path(detail_path)
    if pure_path is None:
        raise ValueError(f"Invalid ROW ONE detail path: {detail_path}")
    return str(pure_path)
