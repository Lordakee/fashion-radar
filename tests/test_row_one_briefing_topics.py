from __future__ import annotations

from fashion_radar.row_one.briefing_topics import briefing_topics_payload


def _story(
    story_id: str,
    *,
    evidence_count: int = 1,
    heat_delta: int = 0,
    entity_refs: list[dict[str, object]] | None = None,
    product_refs: list[dict[str, object]] | None = None,
    designer_refs: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "id": story_id,
        "headline": story_id,
        "detail_href": f"details/{story_id}.html",
        "evidence_count": evidence_count,
        "heat_delta": heat_delta,
        "entity_refs": entity_refs or [],
        "product_refs": product_refs or [],
        "designer_refs": designer_refs or [],
    }


def test_briefing_topics_payload_groups_explicit_topic_refs_once_per_story() -> None:
    topics = briefing_topics_payload(
        [
            _story(
                "the-row-signal-1234567890",
                evidence_count=2,
                heat_delta=5,
                entity_refs=[
                    {"name": "The Row", "type": "brand", "label": "brand"},
                    {"name": " the row ", "type": "retailer", "label": "duplicate"},
                    {"name": "Mary-Kate Olsen", "type": "designer", "label": "designer"},
                    {"name": "Zendaya", "type": "celebrity", "label": "person"},
                ],
                product_refs=[{"name": "Margaux", "type": "bag", "label": "bag"}],
                designer_refs=[{"name": "Ashley Olsen", "type": "designer", "label": "designer"}],
            ),
            _story(
                "the-row-followup-2222222222",
                evidence_count=1,
                heat_delta=-3,
                entity_refs=[{"name": "The Row", "type": "brand", "label": "brand"}],
            ),
        ]
    )

    by_type_and_title = {(topic["topic_type"], topic["title"]["en"]): topic for topic in topics}

    assert by_type_and_title[("brand", "The Row")]["story_count"] == 2
    assert by_type_and_title[("brand", "The Row")]["evidence_count"] == 3
    assert by_type_and_title[("brand", "The Row")]["positive_heat_delta_sum"] == 5
    assert by_type_and_title[("product", "Margaux")]["story_ids"] == ["the-row-signal-1234567890"]
    assert by_type_and_title[("designer", "Mary-Kate Olsen")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
    assert by_type_and_title[("designer", "Ashley Olsen")]["story_ids"] == [
        "the-row-signal-1234567890"
    ]
    assert by_type_and_title[("person", "Zendaya")]["story_ids"] == ["the-row-signal-1234567890"]
