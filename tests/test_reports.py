from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from importlib import resources

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.db.schema import initialize_schema
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.reports import (
    build_daily_report,
    render_json_report,
    render_markdown_report,
)
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings

AS_OF = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)


def _source(name: str = "Vogue Business") -> SourceDefinition:
    return SourceDefinition(
        name=name,
        type=SourceType.RSS,
        url=f"https://example.com/{name.lower().replace(' ', '-')}.xml",
    )


def _store_item(
    engine,
    *,
    url: str,
    entity_name: str,
    source_name: str = "Vogue Business",
    source_weight: float = 1.0,
    collected_at: datetime,
    published_at: datetime | None = None,
    summary: str = "Short attributed summary.",
) -> int:
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=SourceType.RSS,
            url=url,
            title=f"{entity_name} fashion signal",
            published_at=published_at or collected_at,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at,
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": entity_name,
                "entity_type": "brand",
                "alias": "raw alias must stay internal",
                "confidence": 1.0,
                "reason": "raw reason must stay internal",
                "context_terms": ["raw context must stay internal"],
            }
        ],
    )
    return item_id


def test_daily_report_template_is_packaged() -> None:
    template = resources.files("fashion_radar.templates").joinpath("daily_report.md")

    assert template.is_file()
    assert "{entity_sections}" in template.read_text(encoding="utf-8")


def test_markdown_report_includes_entities_attribution_and_source_status(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row-margaux",
        entity_name="The Row",
        source_name="Vogue Business",
        source_weight=1.7,
        collected_at=AS_OF - timedelta(hours=1),
        summary="Margaux demand is accelerating in market coverage.",
    )
    source = _source()
    SourceHealthRepository(engine).record_failure(
        source,
        error_message="timeout",
        occurred_at=AS_OF - timedelta(minutes=30),
        max_failures=1,
        retention_hours=24,
    )
    CollectorRunRepository(engine).record_run(
        source,
        status="failed",
        started_at=AS_OF - timedelta(minutes=31),
        finished_at=AS_OF - timedelta(minutes=30),
        items_seen=0,
        items_stored=0,
        error_message="timeout",
        error_type="ReadTimeout",
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)

    assert "Fashion Radar Daily Report" in markdown
    assert "The Row" in markdown
    assert "new" in markdown
    assert "Vogue Business" in markdown
    assert "https://example.com/the-row-margaux" in markdown
    assert "2026-06-11T11:00:00+00:00" in markdown
    assert "Margaux demand is accelerating" in markdown
    assert "Source Health" in markdown
    assert "timeout" in markdown
    assert "failed" in markdown


def test_json_report_excludes_internal_database_and_matcher_fields(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/miu-miu",
        entity_name="Miu Miu",
        source_name="Elle",
        collected_at=AS_OF - timedelta(hours=1),
        summary="Short public snippet only.",
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    payload = render_json_report(report)
    parsed = json.loads(payload)

    assert parsed["entities"][0]["entity_name"] == "Miu Miu"
    assert parsed["entities"][0]["representative_items"][0] == {
        "source_name": "Elle",
        "source_url": "https://example.com/miu-miu",
        "published_at": "2026-06-11T11:00:00Z",
        "title": "Miu Miu fashion signal",
        "summary": "Short public snippet only.",
    }
    for forbidden in (
        "content_hash",
        "normalized_url",
        "raw alias must stay internal",
        "raw reason must stay internal",
        "raw context must stay internal",
    ):
        assert forbidden not in payload


def test_empty_database_produces_useful_empty_report(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)
    parsed = json.loads(render_json_report(report))

    assert report.entities == []
    assert parsed["entities"] == []
    assert "No entity signals in this window." in markdown


def test_daily_report_includes_untracked_candidate_signals(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    sentinel_item_id = _store_item(
        engine,
        url="https://example.com/le-teckel-a",
        entity_name="Tracked Placeholder",
        source_name="Fashionista",
        collected_at=AS_OF - timedelta(hours=1),
        summary="Le Teckel bag demand is accelerating.",
    )
    _store_item(
        engine,
        url="https://example.com/le-teckel-b",
        entity_name="Tracked Placeholder",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
        summary="Le Teckel bag appears again.",
    )
    sentinel_match = ItemRepository(engine).list_item_matches(sentinel_item_id)[0]
    assert sentinel_match["alias"] == "raw alias must stay internal"
    assert sentinel_match["reason"] == "raw reason must stay internal"
    assert sentinel_match["context_terms"] == ["raw context must stay internal"]

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)
    parsed = json.loads(render_json_report(report))

    assert "Untracked Candidate Signals" in markdown
    assert "candidate signal" in markdown.lower()
    assert "needs review" in markdown.lower()
    assert "from configured sources" in markdown.lower()
    assert "viral" not in markdown.lower()
    assert "market-wide trend" not in markdown.lower()
    assert "confirmed brand" not in markdown.lower()
    assert "Le Teckel bag" in markdown
    assert "Fashionista" in markdown
    assert "https://example.com/le-teckel-a" in markdown
    assert "Le Teckel bag demand is accelerating." in markdown
    assert parsed["candidates"][0]["phrase"] == "Le Teckel bag"
    assert parsed["candidates"][0]["representative_items"][0]["source_name"] == "Fashionista"
    assert (
        parsed["candidates"][0]["representative_items"][0]["source_url"]
        == "https://example.com/le-teckel-a"
    )
    assert (
        "Le Teckel bag demand is accelerating."
        in parsed["candidates"][0]["representative_items"][0]["summary"]
    )
    serialized_candidates = json.dumps(parsed["candidates"])
    for forbidden in (
        "content_hash",
        "contexts",
        "normalized_key",
        "normalized_url",
        '"id"',
        "proper_name_span",
        "fashion_anchor",
        "single_token",
        "raw reason must stay internal",
        "raw alias must stay internal",
        "raw context must stay internal",
        "context_terms",
        "raw extraction context",
    ):
        assert forbidden not in serialized_candidates
        assert forbidden not in markdown


def test_empty_candidate_section_is_useful(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )

    assert report.candidates == []
    assert "No untracked candidate signals in this window." in render_markdown_report(report)


def test_report_candidate_filter_uses_entity_config_without_stored_matches(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/the-row-margaux-a",
            title="The Row Margaux bag gains momentum",
            published_at=AS_OF - timedelta(hours=1),
            summary="The Row Margaux bag gets coverage.",
        ),
        collected_at=AS_OF - timedelta(hours=1),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/the-row-margaux-b",
            title="Margaux bag appears again",
            published_at=AS_OF - timedelta(hours=2),
            summary="Another configured source mentions Margaux bag.",
        ),
        collected_at=AS_OF - timedelta(hours=2),
    )
    entity_config = EntityConfig(
        entities=[
            EntityDefinition(
                name="The Row",
                type=EntityType.BRAND,
                aliases=[{"value": "The Row"}],
                context_terms=["bag"],
            ),
            EntityDefinition(
                name="Margaux",
                type=EntityType.PRODUCT,
                aliases=[{"value": "Margaux"}],
                context_terms=["bag"],
            ),
        ]
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=entity_config,
        as_of=AS_OF,
        generated_at=AS_OF,
    )

    assert (
        "margaux"
        not in json.dumps([candidate.model_dump() for candidate in report.candidates]).lower()
    )
