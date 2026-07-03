from __future__ import annotations

import hashlib

BRIEFING_TOPIC_TYPES = ("brand", "product", "designer", "person")
BRIEFING_PERSON_REF_TYPES = {
    "actor",
    "artist",
    "celebrity",
    "creator",
    "influencer",
    "model",
    "person",
    "stylist",
}
BRIEFING_TOPIC_LABELS = {
    "brand": {"zh": "品牌", "en": "Brand"},
    "product": {"zh": "单品", "en": "Product"},
    "designer": {"zh": "设计师", "en": "Designer"},
    "person": {"zh": "人物", "en": "Person"},
}


def briefing_topics_payload(stories: list[dict[str, object]]) -> list[dict[str, object]]:
    topics: dict[tuple[str, str], dict[str, object]] = {}
    for story_index, story in enumerate(stories):
        story_topic_keys: set[tuple[str, str]] = set()
        for topic_type, reference in _topic_references_for_story(story):
            name = str(reference["name"]).strip()
            normalized_name = _normalize_topic_name(name)
            if not normalized_name:
                continue
            topic_key = (topic_type, normalized_name)
            if topic_key in story_topic_keys:
                continue
            story_topic_keys.add(topic_key)
            topic = topics.setdefault(
                topic_key,
                _empty_briefing_topic(topic_type, name, story_index),
            )
            topic["story_count"] = int(topic["story_count"]) + 1
            topic["evidence_count"] = int(topic["evidence_count"]) + int(story["evidence_count"])
            topic["positive_heat_delta_sum"] = int(topic["positive_heat_delta_sum"]) + max(
                int(story["heat_delta"]) if isinstance(story["heat_delta"], int) else 0,
                0,
            )
            topic["max_heat_delta"] = max(
                int(topic["max_heat_delta"]),
                int(story["heat_delta"]) if isinstance(story["heat_delta"], int) else 0,
            )
            topic["story_ids"].append(str(story["id"]))
            topic["cards"].append(dict(story))
            topic["source_refs"].append(dict(reference))

    sorted_topics = sorted(topics.values(), key=_briefing_topic_sort_key)
    return [_public_briefing_topic_payload(topic) for topic in sorted_topics]


def _topic_references_for_story(
    story: dict[str, object],
) -> list[tuple[str, dict[str, object]]]:
    references: list[tuple[str, dict[str, object]]] = []
    for reference in story["entity_refs"]:
        if not isinstance(reference, dict):
            continue
        topic_type = _topic_type_for_entity_reference(reference)
        if topic_type is not None:
            references.append((topic_type, reference))
    for reference in story["product_refs"]:
        if isinstance(reference, dict):
            references.append(("product", reference))
    for reference in story["designer_refs"]:
        if isinstance(reference, dict):
            references.append(("designer", reference))
    return references


def _topic_type_for_entity_reference(reference: dict[str, object]) -> str | None:
    reference_type = str(reference.get("type", "")).strip().casefold()
    if reference_type in {"brand", "retailer"}:
        return "brand"
    if reference_type == "designer":
        return "designer"
    if reference_type == "product":
        return "product"
    if reference_type in BRIEFING_PERSON_REF_TYPES:
        return "person"
    return None


def _empty_briefing_topic(
    topic_type: str,
    name: str,
    first_story_index: int,
) -> dict[str, object]:
    return {
        "id": _briefing_topic_id(topic_type, name),
        "topic_type": topic_type,
        "title": {"zh": name, "en": name},
        "label": BRIEFING_TOPIC_LABELS[topic_type],
        "story_count": 0,
        "evidence_count": 0,
        "positive_heat_delta_sum": 0,
        "max_heat_delta": 0,
        "first_story_index": first_story_index,
        "lead_story_id": None,
        "story_ids": [],
        "cards": [],
        "source_refs": [],
    }


def _public_briefing_topic_payload(topic: dict[str, object]) -> dict[str, object]:
    story_ids = [str(story_id) for story_id in topic["story_ids"]]
    return {
        "id": topic["id"],
        "topic_type": topic["topic_type"],
        "title": topic["title"],
        "label": topic["label"],
        "story_count": topic["story_count"],
        "evidence_count": topic["evidence_count"],
        "positive_heat_delta_sum": topic["positive_heat_delta_sum"],
        "max_heat_delta": topic["max_heat_delta"],
        "lead_story_id": story_ids[0] if story_ids else None,
        "story_ids": story_ids,
        "cards": topic["cards"],
        "source_refs": _dedupe_story_references(topic["source_refs"]),
    }


def _briefing_topic_sort_key(topic: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(topic["story_count"]),
        -int(topic["positive_heat_delta_sum"]),
        -int(topic["max_heat_delta"]),
        int(topic["first_story_index"]),
        str(topic["title"]["en"]).casefold(),
        str(topic["title"]["en"]),
        BRIEFING_TOPIC_TYPES.index(str(topic["topic_type"])),
    )


def _briefing_topic_id(topic_type: str, name: str) -> str:
    normalized_name = _normalize_topic_name(name)
    digest = hashlib.sha1(f"{topic_type}:{normalized_name}".encode()).hexdigest()[:10]
    return f"{topic_type}-{digest}"


def _normalize_topic_name(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def _dedupe_story_references(references: object) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    if not isinstance(references, list):
        return deduped
    for reference in references:
        if not isinstance(reference, dict):
            continue
        key = (
            _normalize_topic_name(str(reference.get("name", ""))),
            " ".join(str(reference.get("type", "")).strip().casefold().split()),
            " ".join(str(reference.get("label", "")).strip().casefold().split()),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(reference))
    return deduped
