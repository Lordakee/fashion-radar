from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneReference,
    RowOneSection,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
from fashion_radar.row_one.render import render_row_one_site

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "row-one-app.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas" / "row-one-manifest.schema.json"
RUNTIME_SCHEMA = ROOT / "schemas" / "row-one-runtime.schema.json"
AS_OF = datetime(2026, 7, 2, 4, 0, tzinfo=UTC)


def _edition(
    *,
    source_url: str | None = "https://example.com/the-row",
    evidence_url: str | None = "https://example.com/evidence",
    published_at: datetime | None = AS_OF,
    display: RowOneStoryDisplay | None = None,
) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(
            zh="ROW ONE 今日整理了 1 条本地时尚信号。",
            en="ROW ONE organized 1 local fashion signal for today.",
        ),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
            ),
            RowOneSection(
                key="brand_moves",
                title=LocalizedText(zh="品牌动态", en="Brand Moves"),
                dek=LocalizedText(zh="品牌、零售与商业动作。", en="Brand and retail context."),
            ),
        ],
        stories=[
            RowOneStory(
                id="the-row-signal-1234567890",
                section_key="top_stories",
                story_type="tracked_entity",
                headline="The Row signal",
                summary=LocalizedText(zh="来源摘要。", en="Source summary."),
                why_it_matters=LocalizedText(zh="值得关注。", en="Worth watching."),
                editorial_takeaway=LocalizedText(zh="编辑整理。", en="Editorial takeaway."),
                signal_context=LocalizedText(zh="信号背景。", en="Signal context."),
                reader_path=LocalizedText(zh="阅读路径。", en="Reader path."),
                source_name="Vogue Business",
                source_url=source_url,
                published_at=published_at,
                detail_path="details/the-row-signal-1234567890.html",
                tags=["brand"],
                evidence=[
                    RowOneLink(
                        title="Evidence",
                        url=evidence_url,
                        source_name="Vogue Business",
                    )
                ],
                display=display,
            )
        ],
    )


def _schema_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _manifest_schema_validator() -> Draft202012Validator:
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _runtime_schema_validator() -> Draft202012Validator:
    schema = json.loads(RUNTIME_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _payload(tmp_path: Path, edition: RowOneEdition | None = None) -> dict[str, object]:
    render_row_one_site(edition or _edition(), tmp_path)
    return json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))


def _manifest_payload(tmp_path: Path, edition: RowOneEdition | None = None) -> dict[str, object]:
    render_row_one_site(edition or _edition(), tmp_path)
    return json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))


def _runtime_payload(tmp_path: Path, edition: RowOneEdition | None = None) -> dict[str, object]:
    render_row_one_site(edition or _edition(), tmp_path)
    return json.loads((tmp_path / "data" / "runtime.json").read_text(encoding="utf-8"))


def _contract_drift_topic(payload: dict[str, object], **overrides: object) -> dict[str, object]:
    topic = {
        "id": "brand-1234567890",
        "topic_type": "brand",
        "title": {"zh": "The Row", "en": "The Row"},
        "label": {"zh": "品牌", "en": "Brand"},
        "story_count": 1,
        "evidence_count": 1,
        "positive_heat_delta_sum": 0,
        "max_heat_delta": 0,
        "lead_story_id": "the-row-signal-1234567890",
        "story_ids": ["the-row-signal-1234567890"],
        "cards": [payload["content_sections"][0]["cards"][0]],
        "source_refs": [{"name": "The Row", "type": "brand", "label": "rising"}],
    }
    topic.update(overrides)
    return topic


def test_row_one_app_contract_schema_validates_generated_payload(tmp_path: Path) -> None:
    payload = _payload(tmp_path)

    _schema_validator().validate(payload)


def test_row_one_manifest_schema_validates_generated_payload(tmp_path: Path) -> None:
    manifest = _manifest_payload(tmp_path)

    _manifest_schema_validator().validate(manifest)


def test_row_one_runtime_schema_validates_generated_payload(tmp_path: Path) -> None:
    runtime = _runtime_payload(tmp_path)

    _runtime_schema_validator().validate(runtime)


def test_row_one_manifest_points_to_app_contract_and_site_paths(tmp_path: Path) -> None:
    manifest = _manifest_payload(tmp_path)

    assert manifest["contract_version"] == "row-one-manifest/v1"
    assert manifest["brand"] == "ROW ONE"
    assert manifest["manifest_schema_path"] == "schemas/row-one-manifest.schema.json"
    assert manifest["app_contract"] == {
        "version": "row-one-app/v4",
        "path": "data/edition.json",
        "schema_path": "schemas/row-one-app.schema.json",
    }
    assert manifest["site"] == {
        "index_path": "index.html",
        "data_path": "data/edition.json",
        "manifest_path": "data/manifest.json",
        "assets_path": "assets/",
        "details_path": "details/",
    }
    assert "runtime_path" not in manifest["site"]


def test_row_one_runtime_payload_describes_local_runtime_contract(tmp_path: Path) -> None:
    runtime = _runtime_payload(tmp_path)

    assert runtime["contract_version"] == "row-one-runtime/v1"
    assert runtime["brand"] == "ROW ONE"
    assert runtime["runtime_schema_path"] == "schemas/row-one-runtime.schema.json"
    assert runtime["site"] == {
        "index_path": "index.html",
        "manifest_path": "data/manifest.json",
        "edition_path": "data/edition.json",
        "runtime_path": "data/runtime.json",
    }
    assert runtime["refresh"] == {
        "recommended_time": "04:00",
        "command": (
            'fashion-radar row-one refresh --as-of "$AS_OF" --output-dir reports/row-one/site'
        ),
        "latest_only_cleanup": True,
    }
    assert runtime["serve"] == {
        "default_host": "127.0.0.1",
        "default_port": 8787,
        "local_url": "http://127.0.0.1:8787",
        "lan_url_hint": "http://<LAN-IP>:8787",
    }
    assert runtime["counts"] == {
        "story_count": 1,
        "section_count": 2,
        "evidence_count": 1,
    }
    assert runtime["readiness"] == {
        "status": "ready",
        "zh": "可阅读",
        "en": "ready",
    }
    _runtime_schema_validator().validate(runtime)


def test_row_one_manifest_counts_match_app_payload(tmp_path: Path) -> None:
    app_payload = _payload(tmp_path)
    manifest = json.loads((tmp_path / "data" / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["generated_at"] == app_payload["generated_at"]
    assert manifest["edition_date"] == app_payload["edition_date"]
    assert manifest["counts"]["story_count"] == app_payload["story_count"]
    assert manifest["counts"]["section_count"] == len(app_payload["sections"])
    assert manifest["counts"]["evidence_count"] == app_payload["evidence_count"]
    assert manifest["readiness"]["status"] == "ready"


def test_row_one_app_payload_has_stable_counts(tmp_path: Path) -> None:
    payload = _payload(tmp_path)

    stories = payload["stories"]
    sections = payload["sections"]
    content_sections = payload["content_sections"]
    assert isinstance(stories, list)
    assert isinstance(sections, list)
    assert isinstance(content_sections, list)
    assert payload["story_count"] == len(stories)
    assert payload["evidence_count"] == sum(story["evidence_count"] for story in stories)
    for section in sections:
        assert section["story_count"] == sum(
            1 for story in stories if story["section_key"] == section["key"]
        )
    for content_section in content_sections:
        assert content_section["story_count"] == len(content_section["story_ids"])
        assert content_section["story_count"] == len(content_section["cards"])


def test_row_one_app_payload_groups_content_sections_for_clients(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    sections = payload["sections"]
    stories = payload["stories"]
    content_sections = payload["content_sections"]

    assert len(content_sections) == len(sections)
    for section, content_section in zip(sections, content_sections, strict=True):
        section_stories = [story for story in stories if story["section_key"] == section["key"]]
        assert content_section["key"] == section["key"]
        assert content_section["title"] == section["title"]
        assert content_section["dek"] == section["dek"]
        assert content_section["href"] == section["href"]
        assert content_section["story_count"] == len(section_stories)
        assert content_section["story_ids"] == [story["id"] for story in section_stories]
        assert content_section["lead_story_id"] == (
            section_stories[0]["id"] if section_stories else None
        )
        assert [card["id"] for card in content_section["cards"]] == [
            story["id"] for story in section_stories
        ]
        for card, story in zip(content_section["cards"], section_stories, strict=True):
            assert card["why_it_matters"] == story["why_it_matters"]
            assert card["signal_context"] == story["signal_context"]


def test_row_one_app_payload_includes_story_directory_for_clients(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    stories = payload["stories"]
    directory = payload["story_directory"]

    assert directory["story_count"] == payload["story_count"]
    assert directory["story_ids"] == [story["id"] for story in stories]
    assert len(directory["routes"]) == len(stories)

    for route, story in zip(directory["routes"], stories, strict=True):
        assert set(route) == {
            "story_id",
            "detail_href",
            "section_key",
            "section_href",
            "published_date",
        }
        assert route == {
            "story_id": story["id"],
            "detail_href": story["detail_href"],
            "section_key": story["section_key"],
            "section_href": story["section"]["href"],
            "published_date": story["published_date"],
        }

    _schema_validator().validate(payload)


def test_row_one_app_payload_includes_daily_digest_for_clients(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    digest = payload["daily_digest"]
    stories = payload["stories"]
    blocks = {block["key"]: block for block in digest["blocks"]}

    assert digest["title"] == {"zh": "今日简报", "en": "Today's Briefing"}
    assert digest["story_count"] == payload["story_count"]
    assert digest["evidence_count"] == payload["evidence_count"]
    assert digest["lead_story_id"] == stories[0]["id"]
    assert list(blocks) == ["read_first", "key_takeaways", "signals_to_watch"]
    assert blocks["read_first"]["story_ids"] == [stories[0]["id"]]
    assert [card["id"] for card in blocks["read_first"]["cards"]] == [stories[0]["id"]]
    read_first_card = blocks["read_first"]["cards"][0]
    assert read_first_card["why_it_matters"] == stories[0]["why_it_matters"]
    assert read_first_card["signal_context"] == stories[0]["signal_context"]
    assert blocks["key_takeaways"]["story_ids"] == [stories[0]["id"]]
    assert blocks["signals_to_watch"]["story_ids"] == []
    _schema_validator().validate(payload)


def test_row_one_app_daily_digest_includes_briefing_topics_for_clients(
    tmp_path: Path,
) -> None:
    edition = _edition()
    brand_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "the-row-brand-1111111111",
            "headline": "The Row Brand",
            "detail_path": "details/the-row-brand-1111111111.html",
            "heat_delta": 2,
            "entity_refs": [
                RowOneReference(name="The Row", type="brand", label="rising"),
            ],
            "designer_refs": [
                RowOneReference(name="Mary-Kate Olsen", type="designer", label="designer"),
            ],
        },
    )
    product_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "margaux-product-2222222222",
            "headline": "Margaux Product",
            "detail_path": "details/margaux-product-2222222222.html",
            "heat_delta": 7,
            "product_refs": [
                RowOneReference(name="Margaux", type="product", label="rising"),
            ],
        },
    )
    person_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "zoe-style-3333333333",
            "headline": "Zoe Style",
            "detail_path": "details/zoe-style-3333333333.html",
            "heat_delta": 0,
            "entity_refs": [
                RowOneReference(name="Zoe Kravitz", type="celebrity", label="style"),
            ],
        },
    )
    repeat_brand_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "the-row-brand-4444444444",
            "headline": "The Row Follow-up",
            "detail_path": "details/the-row-brand-4444444444.html",
            "heat_delta": 4,
            "entity_refs": [
                RowOneReference(name="the row", type="brand", label="rising"),
            ],
        },
    )
    edition.stories = [brand_story, product_story, person_story, repeat_brand_story]

    payload = _payload(tmp_path, edition)
    topics = payload["daily_digest"]["briefing_topics"]

    assert [topic["topic_type"] for topic in topics] == [
        "brand",
        "product",
        "designer",
        "person",
    ]
    topic_ids = [topic["id"] for topic in topics]
    assert len(topic_ids) == len(set(topic_ids))
    for topic in topics:
        assert topic["story_count"] == len(topic["story_ids"])
        assert topic["story_count"] == len(topic["cards"])
        assert topic["evidence_count"] == sum(card["evidence_count"] for card in topic["cards"])
        assert topic["lead_story_id"] == topic["story_ids"][0]
        assert [card["id"] for card in topic["cards"]] == topic["story_ids"]
        topic_stories = [story for story in payload["stories"] if story["id"] in topic["story_ids"]]
        for card, story in zip(topic["cards"], topic_stories, strict=True):
            assert card["why_it_matters"] == story["why_it_matters"]
            assert card["signal_context"] == story["signal_context"]
        assert topic["source_refs"]
    assert topics[0]["title"] == {"zh": "The Row", "en": "The Row"}
    assert topics[0]["label"] == {"zh": "品牌", "en": "Brand"}
    assert topics[0]["story_count"] == 2
    assert topics[0]["evidence_count"] == 2
    assert topics[0]["positive_heat_delta_sum"] == 6
    assert topics[0]["max_heat_delta"] == 4
    assert topics[0]["lead_story_id"] == "the-row-brand-1111111111"
    assert topics[0]["story_ids"] == ["the-row-brand-1111111111", "the-row-brand-4444444444"]
    assert [card["id"] for card in topics[0]["cards"]] == topics[0]["story_ids"]
    assert topics[0]["source_refs"] == [
        {"name": "The Row", "type": "brand", "label": "rising"},
    ]
    assert topics[1]["title"] == {"zh": "Margaux", "en": "Margaux"}
    assert topics[1]["positive_heat_delta_sum"] == 7
    assert topics[2]["label"] == {"zh": "设计师", "en": "Designer"}
    assert topics[3]["label"] == {"zh": "人物", "en": "Person"}
    _schema_validator().validate(payload)


def test_row_one_app_daily_digest_topics_do_not_infer_people_from_section_or_tags(
    tmp_path: Path,
) -> None:
    edition = _edition()
    story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "celebrity-section-1111111111",
            "section_key": "celebrity_style",
            "headline": "Celebrity Person Style",
            "detail_path": "details/celebrity-section-1111111111.html",
            "source_name": "Celebrity Person Desk",
            "source_url": "https://example.com/celebrity-person",
            "tags": ["celebrity", "person"],
            "evidence": [
                RowOneLink(
                    title="Celebrity person evidence",
                    url="https://example.com/person-evidence",
                    source_name="People Source",
                )
            ],
        },
    )
    edition.stories = [story]

    payload = _payload(tmp_path, edition)

    assert payload["daily_digest"]["briefing_topics"] == []
    _schema_validator().validate(payload)


def test_row_one_app_daily_digest_signal_block_uses_positive_raw_deltas(
    tmp_path: Path,
) -> None:
    edition = _edition()
    first = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "first-signal-1111111111",
            "headline": "First Signal",
            "detail_path": "details/first-signal-1111111111.html",
            "heat_delta": 3,
        },
    )
    second = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "second-signal-2222222222",
            "headline": "Second Signal",
            "detail_path": "details/second-signal-2222222222.html",
            "heat_delta": 9,
        },
    )
    flat = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "flat-signal-3333333333",
            "headline": "Flat Signal",
            "detail_path": "details/flat-signal-3333333333.html",
            "heat_delta": 0,
        },
    )
    edition.stories = [first, flat, second]

    payload = _payload(tmp_path, edition)
    signals = next(
        block for block in payload["daily_digest"]["blocks"] if block["key"] == "signals_to_watch"
    )

    assert signals["story_ids"] == ["second-signal-2222222222", "first-signal-1111111111"]
    assert [card["heat_delta"] for card in signals["cards"]] == [9, 3]
    assert [card["heat_delta_metric"] for card in signals["cards"]] == [
        "raw_mention_delta",
        "raw_mention_delta",
    ]
    _schema_validator().validate(payload)


def test_row_one_app_daily_digest_lead_matches_read_first_fallback(
    tmp_path: Path,
) -> None:
    edition = _edition()
    brand_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "brand-move-1111111111",
            "section_key": "brand_moves",
            "headline": "Brand Move",
            "detail_path": "details/brand-move-1111111111.html",
        },
    )
    top_story = edition.stories[0].model_copy(
        deep=True,
        update={
            "id": "top-story-2222222222",
            "section_key": "top_stories",
            "headline": "Top Story",
            "detail_path": "details/top-story-2222222222.html",
        },
    )
    edition.stories = [brand_story, top_story]

    payload = _payload(tmp_path, edition)
    digest = payload["daily_digest"]
    read_first = digest["blocks"][0]

    assert digest["lead_story_id"] == "top-story-2222222222"
    assert read_first["key"] == "read_first"
    assert read_first["story_ids"] == ["top-story-2222222222"]
    _schema_validator().validate(payload)


def test_row_one_app_content_cards_mirror_story_display_fields(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    story = payload["stories"][0]
    card = payload["content_sections"][0]["cards"][0]

    assert card == {
        "id": story["id"],
        "story_type": story["story_type"],
        "headline": story["headline"],
        "summary": story["summary"],
        "why_it_matters": story["why_it_matters"],
        "signal_context": story["signal_context"],
        "editorial_takeaway": story["editorial_takeaway"],
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


def test_row_one_app_stories_include_structured_signal_fields(tmp_path: Path) -> None:
    payload = _payload(tmp_path)
    story = payload["stories"][0]

    assert story["story_type"] == "tracked_entity"
    assert story["market_region"] is None
    assert story["source_region"] is None
    assert story["heat_delta"] is None
    assert story["heat_delta_metric"] is None
    assert story["entity_refs"] == []
    assert story["product_refs"] == []
    assert story["designer_refs"] == []
    _schema_validator().validate(payload)


def test_row_one_app_stories_include_detail_sections_and_evidence_summary(
    tmp_path: Path,
) -> None:
    payload = _payload(tmp_path)
    story = payload["stories"][0]

    assert [section["key"] for section in story["detail_sections"]] == [
        "summary",
        "why_it_matters",
        "editorial_takeaway",
        "signal_context",
        "reader_path",
        "evidence",
    ]
    text_sections = {
        section["key"]: section
        for section in story["detail_sections"]
        if section["key"] != "evidence"
    }
    assert text_sections["summary"]["body"] == story["summary"]
    assert text_sections["why_it_matters"]["body"] == story["why_it_matters"]
    assert text_sections["editorial_takeaway"]["body"] == story["editorial_takeaway"]
    assert text_sections["signal_context"]["body"] == story["signal_context"]
    assert text_sections["reader_path"]["body"] == story["reader_path"]
    for text_section in text_sections.values():
        assert text_section["evidence"] == []
    evidence_section = story["detail_sections"][-1]
    assert evidence_section["body"] is None
    assert evidence_section["evidence"] == story["evidence"]
    assert story["evidence_summary"] == {
        "safe_link_count": story["evidence_count"],
        "total_count": len(story["evidence"]),
        "primary_source_name": story["source_name"],
        "sources": ["Vogue Business"],
    }


def test_row_one_app_payload_supports_undated_stories(tmp_path: Path) -> None:
    payload = _payload(tmp_path, _edition(published_at=None))

    story = payload["stories"][0]
    assert story["published_at"] is None
    assert story["published_date"] is None
    _schema_validator().validate(payload)


def test_row_one_app_payload_normalizes_assigned_timezone_to_utc(tmp_path: Path) -> None:
    edition = _edition()
    edition.generated_at = datetime(2026, 7, 2, 12, 0, tzinfo=timezone(timedelta(hours=8)))
    edition.edition_date = datetime(2026, 7, 2, 12, 0, tzinfo=timezone(timedelta(hours=8)))
    edition.stories[0].published_at = datetime(
        2026,
        7,
        2,
        12,
        0,
        tzinfo=timezone(timedelta(hours=8)),
    )

    payload = _payload(tmp_path, edition)

    assert payload["generated_at"] == "2026-07-02T04:00:00Z"
    assert payload["edition_date"] == "2026-07-02T04:00:00Z"
    assert payload["stories"][0]["published_at"] == "2026-07-02T04:00:00Z"
    assert payload["stories"][0]["published_date"] == "2026-07-02"
    _schema_validator().validate(payload)


def test_row_one_app_payload_published_date_uses_utc_date(tmp_path: Path) -> None:
    edition = _edition()
    edition.stories[0].published_at = datetime(
        2026,
        7,
        2,
        0,
        30,
        tzinfo=timezone(timedelta(hours=8)),
    )

    payload = _payload(tmp_path, edition)

    assert payload["stories"][0]["published_at"] == "2026-07-01T16:30:00Z"
    assert payload["stories"][0]["published_date"] == "2026-07-01"
    _schema_validator().validate(payload)


def test_row_one_app_payload_preserves_rendering_for_sparse_sections(tmp_path: Path) -> None:
    edition = _edition()
    edition.sections = [
        RowOneSection(
            key="brand_moves",
            title=LocalizedText(zh="品牌动态", en="Brand Moves"),
            dek=LocalizedText(zh="品牌、零售与商业动作。", en="Brand and retail context."),
        )
    ]

    payload = _payload(tmp_path, edition)

    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "data" / "edition.json").exists()
    story = payload["stories"][0]
    assert story["section_key"] == "top_stories"
    assert story["section"] == {
        "key": "top_stories",
        "title": {"zh": "top_stories", "en": "Top Stories"},
        "href": "#top_stories",
    }
    _schema_validator().validate(payload)


def test_row_one_app_payload_repeated_href_fields_stay_in_sync(tmp_path: Path) -> None:
    payload = _payload(tmp_path)

    story = payload["stories"][0]
    assert story["detail_path"] == story["href"] == story["detail_href"]
    for link in story["evidence"]:
        assert link["url"] == link["href"]


def test_row_one_app_payload_sanitizes_urls(tmp_path: Path) -> None:
    payload = _payload(
        tmp_path,
        _edition(source_url="javascript:alert(1)", evidence_url="https:///bad"),
    )

    story = payload["stories"][0]
    assert story["source_url"] is None
    assert story["evidence_count"] == 0
    assert story["evidence"][0]["url"] is None
    assert story["evidence"][0]["href"] is None
    _schema_validator().validate(payload)


def test_row_one_app_payload_includes_story_display_metadata(tmp_path: Path) -> None:
    payload = _payload(tmp_path)

    story = payload["stories"][0]
    assert story["display"] == {
        "variant": "editorial",
        "accent": "ink",
        "image": None,
    }
    _schema_validator().validate(payload)

    image_payload = _payload(
        tmp_path,
        _edition(
            display=RowOneStoryDisplay(
                variant="product",
                accent="cobalt",
                image=RowOneStoryImage(
                    src="assets/images/the-row.png",
                    alt=LocalizedText(zh="The Row 视觉素材", en="The Row visual"),
                    credit="ROW ONE",
                    source_url="https://example.com/image-source",
                ),
            )
        ),
    )

    assert image_payload["stories"][0]["display"] == {
        "variant": "product",
        "accent": "cobalt",
        "image": {
            "src": "assets/images/the-row.png",
            "alt": {"zh": "The Row 视觉素材", "en": "The Row visual"},
            "credit": "ROW ONE",
            "source_url": "https://example.com/image-source",
        },
    }
    _schema_validator().validate(image_payload)


def test_row_one_app_payload_sanitizes_display_image_sources(tmp_path: Path) -> None:
    payload = _payload(
        tmp_path,
        _edition(
            display=RowOneStoryDisplay(
                variant="portrait",
                accent="rose",
                image=RowOneStoryImage(
                    src="../secret.png",
                    alt=LocalizedText(zh="不安全图片", en="Unsafe image"),
                    credit="ROW ONE",
                    source_url="javascript:alert(1)",
                ),
            )
        ),
    )

    assert payload["stories"][0]["display"] == {
        "variant": "portrait",
        "accent": "rose",
        "image": None,
    }
    _schema_validator().validate(payload)


@pytest.mark.parametrize(
    "src",
    [
        " assets/images/the-row.png",
        "assets/images/the-row.png\n",
        "assets/foo bar.png",
        "assets/foo+bar.png",
        "assets/foo%20bar.png",
    ],
)
def test_row_one_app_payload_rejects_schema_invalid_display_asset_paths(
    tmp_path: Path,
    src: str,
) -> None:
    payload = _payload(
        tmp_path,
        _edition(
            display=RowOneStoryDisplay(
                variant="product",
                accent="cobalt",
                image=RowOneStoryImage(
                    src=src,
                    alt=LocalizedText(zh="不安全图片", en="Unsafe image"),
                    credit="ROW ONE",
                    source_url="https://example.com/image-source",
                ),
            )
        ),
    )

    assert payload["stories"][0]["display"] == {
        "variant": "product",
        "accent": "cobalt",
        "image": None,
    }
    _schema_validator().validate(payload)


@pytest.mark.parametrize(
    "src",
    [
        " https://example.com/foo.png",
        "https://example.com\\foo.png",
        "https://example.com/foo bar.png",
        "https://example.com/foo.png ",
        "\nhttps://example.com/foo.png",
        "https://example.com/\nfoo.png",
        "https:///bad.png",
        "http://:80/foo.png",
    ],
)
def test_row_one_app_payload_rejects_display_image_urls_sanitizer_rejects(
    tmp_path: Path,
    src: str,
) -> None:
    payload = _payload(
        tmp_path,
        _edition(
            display=RowOneStoryDisplay(
                variant="product",
                accent="cobalt",
                image=RowOneStoryImage(
                    src=src,
                    alt=LocalizedText(zh="不安全图片", en="Unsafe image"),
                    credit="ROW ONE",
                    source_url="https://example.com/image-source",
                ),
            )
        ),
    )

    assert payload["stories"][0]["display"] == {
        "variant": "product",
        "accent": "cobalt",
        "image": None,
    }
    _schema_validator().validate(payload)


@pytest.mark.parametrize(
    "src",
    [
        " https://example.com/foo.png",
        "https://example.com\\foo.png",
        "https://example.com/foo bar.png",
        "https://example.com/foo.png ",
        "\nhttps://example.com/foo.png",
        "https://example.com/\nfoo.png",
        "https:///bad.png",
        "http://:80/foo.png",
    ],
)
def test_row_one_app_schema_rejects_display_image_urls_sanitizer_rejects(
    tmp_path: Path,
    src: str,
) -> None:
    payload = _payload(
        tmp_path,
        _edition(
            display=RowOneStoryDisplay(
                variant="product",
                accent="cobalt",
                image=RowOneStoryImage(
                    src="assets/images/the-row.png",
                    alt=LocalizedText(zh="The Row 视觉素材", en="The Row visual"),
                    credit="ROW ONE",
                    source_url="https://example.com/image-source",
                ),
            )
        ),
    )
    payload["stories"][0]["display"]["image"]["src"] = src

    with pytest.raises(ValidationError, match="not valid under any"):
        _schema_validator().validate(payload)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda payload: payload.__setitem__("contract_version", "row-one-app/v2"), "was expected"),
        (lambda payload: payload.pop("daily_digest"), "'daily_digest' is a required property"),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [
                    {
                        "id": "brand-1234567890",
                        "topic_type": "unknown",
                        "title": {"zh": "The Row", "en": "The Row"},
                        "label": {"zh": "品牌", "en": "Brand"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 0,
                        "max_heat_delta": 0,
                        "lead_story_id": "the-row-signal-1234567890",
                        "story_ids": ["the-row-signal-1234567890"],
                        "cards": [payload["content_sections"][0]["cards"][0]],
                        "source_refs": [{"name": "The Row", "type": "brand", "label": "rising"}],
                    }
                ],
            ),
            "is not one of",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [
                    {
                        "id": "brand-1234567890",
                        "topic_type": "brand",
                        "title": {"zh": "The Row", "en": "The Row"},
                        "label": {"zh": "品牌", "en": "Brand"},
                        "story_count": 1,
                        "evidence_count": 1,
                        "positive_heat_delta_sum": 0,
                        "max_heat_delta": 0,
                        "lead_story_id": "the-row-signal-1234567890",
                        "story_ids": ["the-row-signal-1234567890"],
                        "cards": [payload["content_sections"][0]["cards"][0]],
                        "source_refs": [{"name": "The Row", "type": "brand", "label": "rising"}],
                        "extra": True,
                    }
                ],
            ),
            "Additional properties",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, id="person-1234567890")],
            ),
            "does not match",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, label={"zh": "人物", "en": "Person"})],
            ),
            "was expected",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, story_count=0)],
            ),
            "less than the minimum",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, lead_story_id=None)],
            ),
            "not of type",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, story_ids=[])],
            ),
            "should be non-empty|is too short",
        ),
        (
            lambda payload: payload["daily_digest"].__setitem__(
                "briefing_topics",
                [_contract_drift_topic(payload, source_refs=[])],
            ),
            "should be non-empty|is too short",
        ),
        (
            lambda payload: payload["daily_digest"]["blocks"].pop(),
            "is too short",
        ),
        (
            lambda payload: payload["daily_digest"]["blocks"][0].__setitem__(
                "key", "signals_to_watch"
            ),
            "was expected",
        ),
        (
            lambda payload: payload.pop("story_directory"),
            "'story_directory' is a required property",
        ),
        (
            lambda payload: payload["story_directory"].__setitem__("extra", True),
            "Additional properties",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "headline",
                "The Row signal",
            ),
            "Additional properties",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].pop("story_id"),
            "'story_id' is a required property",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].pop("published_date"),
            "'published_date' is a required property",
        ),
        (
            lambda payload: payload["content_sections"][0]["cards"][0].pop("why_it_matters"),
            "'why_it_matters' is a required property",
        ),
        (
            lambda payload: payload["content_sections"][0]["cards"][0].pop("signal_context"),
            "'signal_context' is a required property",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "story_id",
                "Bad ID!",
            ),
            "does not match",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "detail_href",
                "../escape.html",
            ),
            "does not match",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "section_key",
                "unknown",
            ),
            "not one",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "section_href",
                "top_stories",
            ),
            "does not match",
        ),
        (
            lambda payload: payload["story_directory"]["routes"][0].__setitem__(
                "published_date",
                "2026-7-2",
            ),
            "not valid under any",
        ),
        (lambda payload: payload.__setitem__("extra", True), "Additional properties"),
        (lambda payload: payload["stories"][0].__setitem__("section_key", "unknown"), "not one"),
        (
            lambda payload: payload["stories"][0].__setitem__("detail_href", "../escape.html"),
            "does not match",
        ),
        (lambda payload: payload.__setitem__("generated_at", "not-a-date"), "does not match"),
        (
            lambda payload: payload["stories"][0].__setitem__(
                "published_at",
                "2026-07-02 04:00:00",
            ),
            "not valid under any",
        ),
        (
            lambda payload: payload["stories"][0].__setitem__("published_date", "2026-7-2"),
            "not valid under any",
        ),
        (
            lambda payload: payload["stories"][0]["display"].__setitem__("variant", "banner"),
            "is not one of",
        ),
        (lambda payload: payload["summary"].pop("zh"), "'zh' is a required property"),
    ],
)
def test_row_one_app_schema_rejects_contract_drift(
    tmp_path: Path,
    mutation,
    match: str,
) -> None:
    payload = copy.deepcopy(_payload(tmp_path))
    mutation(payload)

    with pytest.raises(ValidationError, match=match):
        _schema_validator().validate(payload)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda payload: payload.__setitem__("content_sections", []), "content_sections"),
        (
            lambda payload: payload["content_sections"][0].__setitem__("extra", "x"),
            "Additional properties",
        ),
        (
            lambda payload: payload["stories"][0]["detail_sections"][0].__setitem__(
                "key",
                "unknown",
            ),
            "not one of",
        ),
        (
            lambda payload: payload["stories"][0].__setitem__("evidence_summary", {}),
            "'safe_link_count' is a required property",
        ),
    ],
)
def test_row_one_app_v2_schema_rejects_content_organization_drift(
    tmp_path: Path,
    mutation,
    match: str,
) -> None:
    payload = copy.deepcopy(_payload(tmp_path))
    mutation(payload)

    with pytest.raises(ValidationError, match=match):
        _schema_validator().validate(payload)


def test_empty_row_one_app_payload_validates(tmp_path: Path) -> None:
    edition = RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="暂无信号。", en="No signals yet."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
            )
        ],
        stories=[],
    )

    payload = _payload(tmp_path, edition)

    assert payload["contract_version"] == "row-one-app/v4"
    assert payload["story_count"] == 0
    assert payload["evidence_count"] == 0
    assert payload["stories"] == []
    assert payload["story_directory"] == {
        "story_count": 0,
        "story_ids": [],
        "routes": [],
    }
    assert payload["daily_digest"] == {
        "title": {"zh": "今日简报", "en": "Today's Briefing"},
        "dek": {
            "zh": "暂无可整理的 ROW ONE 故事。",
            "en": "No ROW ONE stories are available to organize yet.",
        },
        "story_count": 0,
        "evidence_count": 0,
        "lead_story_id": None,
        "briefing_topics": [],
        "blocks": [
            {
                "key": "read_first",
                "title": {"zh": "先读", "en": "Read First"},
                "dek": {
                    "zh": "今日最值得先打开的一条 ROW ONE 信号。",
                    "en": "The first ROW ONE signal to open today.",
                },
                "story_count": 0,
                "story_ids": [],
                "cards": [],
            },
            {
                "key": "key_takeaways",
                "title": {"zh": "重点整理", "en": "Key Takeaways"},
                "dek": {
                    "zh": "按栏目顺序整理每个非空板块的第一条信号。",
                    "en": "The first signal from each non-empty section, in section order.",
                },
                "story_count": 0,
                "story_ids": [],
                "cards": [],
            },
            {
                "key": "signals_to_watch",
                "title": {"zh": "升温信号", "en": "Signals To Watch"},
                "dek": {
                    "zh": "仅按本地原始提及增量筛出的正向变化信号。",
                    "en": "Positive local raw mention deltas worth watching.",
                },
                "story_count": 0,
                "story_ids": [],
                "cards": [],
            },
        ],
    }
    assert payload["content_sections"] == [
        {
            "key": "top_stories",
            "title": {"zh": "今日重点", "en": "Top Stories"},
            "dek": {"zh": "今日最值得先看的时尚信号。", "en": "Read first."},
            "href": "#top_stories",
            "story_count": 0,
            "lead_story_id": None,
            "story_ids": [],
            "cards": [],
        }
    ]
    _schema_validator().validate(payload)


def test_empty_row_one_manifest_payload_validates(tmp_path: Path) -> None:
    edition = RowOneEdition(
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="暂无信号。", en="No signals yet."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="Read first."),
            )
        ],
        stories=[],
    )

    manifest = _manifest_payload(tmp_path, edition)

    assert manifest["counts"]["story_count"] == 0
    assert manifest["readiness"]["status"] == "empty"
    _manifest_schema_validator().validate(manifest)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            lambda payload: payload.__setitem__("contract_version", "row-one-manifest/v2"),
            "was expected",
        ),
        (lambda payload: payload.__setitem__("extra", True), "Additional properties"),
        (lambda payload: payload.__setitem__("generated_at", "not-a-date"), "does not match"),
        (
            lambda payload: payload["app_contract"].__setitem__("path", "/abs/edition.json"),
            "was expected",
        ),
        (
            lambda payload: payload["readiness"].__setitem__("status", "partial"),
            "is not one of",
        ),
        (
            lambda payload: payload["capabilities"].__setitem__("absolute_urls", True),
            "Additional properties",
        ),
    ],
)
def test_row_one_manifest_schema_rejects_contract_drift(
    tmp_path: Path,
    mutation,
    match: str,
) -> None:
    manifest = copy.deepcopy(_manifest_payload(tmp_path))
    mutation(manifest)

    with pytest.raises(ValidationError, match=match):
        _manifest_schema_validator().validate(manifest)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            lambda payload: payload.__setitem__("unexpected", True),
            "Additional properties",
        ),
        (
            lambda payload: payload["site"].__setitem__("runtime_path", "runtime.json"),
            "was expected",
        ),
        (
            lambda payload: payload["serve"].__setitem__("default_port", 8000),
            "was expected",
        ),
        (
            lambda payload: payload["readiness"].__setitem__("status", "partial"),
            "is not one of",
        ),
        (
            lambda payload: payload["readiness"].__setitem__("zh", ""),
            "should be non-empty",
        ),
        (
            lambda payload: payload["refresh"].__setitem__(
                "command",
                "fashion-radar row-one refresh --output-dir reports/row-one/site",
            ),
            "was expected",
        ),
    ],
)
def test_row_one_runtime_schema_rejects_contract_drift(
    tmp_path: Path,
    mutation,
    match: str,
) -> None:
    runtime = copy.deepcopy(_runtime_payload(tmp_path))
    mutation(runtime)

    with pytest.raises(ValidationError, match=match):
        _runtime_schema_validator().validate(runtime)
