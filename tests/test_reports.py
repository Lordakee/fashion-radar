from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.db.schema import initialize_schema
from fashion_radar.html_report import render_html_report
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import (
    REPORT_SNIPPET_MAX_CHARS,
    CandidateReport,
    CollectorRunReport,
    DailyBrief,
    DailyBriefItem,
    DailyBriefSection,
    DailyReport,
    EntityMatchEvidence,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    SourceHealthReport,
)
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.reports import (
    build_daily_brief,
    build_daily_report,
    render_json_report,
    render_markdown_report,
)
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings

AS_OF = datetime(2026, 6, 11, 12, 0, tzinfo=UTC)
LONG_SUMMARY = "Lead text. " + ("detail " * 120) + "TAIL_MARKER"
LONG_ERROR = "timeout: " + ("retry detail " * 80) + "TAIL_MARKER"
MULTILINE_ERROR = "connection reset\n  by peer\n\nretry exhausted TAIL_MARKER"
WHITESPACE_ONLY_ERROR = "   \n\t  "


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
    return _store_item_with_matches(
        engine,
        url=url,
        entity_name=entity_name,
        source_name=source_name,
        source_weight=source_weight,
        collected_at=collected_at,
        published_at=published_at,
        summary=summary,
        matches=[
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


def _store_item_with_matches(
    engine,
    *,
    url: str,
    entity_name: str,
    matches: list[dict[str, object]],
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
    repository.replace_item_matches(item_id, matches)
    return item_id


def test_daily_report_template_is_packaged() -> None:
    template = resources.files("fashion_radar.templates").joinpath("daily_report.md")

    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert "{brief_section}" in text
    assert "{entity_sections}" in text
    assert "## Daily Brief" in text


def test_representative_item_summary_is_report_safe_snippet() -> None:
    item = RepresentativeItem(
        source_name="Vogue Business",
        source_url="https://example.com/signal",
        published_at="2026-06-14T08:00:00Z",
        title="The Row signal",
        summary=LONG_SUMMARY,
    )

    assert item.summary is not None
    assert len(item.summary) <= REPORT_SNIPPET_MAX_CHARS
    assert item.summary.endswith("...")
    assert "TAIL_MARKER" not in item.summary


def test_entity_report_match_evidence_default_json_shape() -> None:
    report = EntityReport(
        entity_name="The Row",
        entity_type="brand",
        label="new",
        heat_score=1.0,
        current_mentions=1,
        baseline_mentions=0,
        distinct_sources=1,
    )
    payload = report.model_dump(mode="json")

    assert isinstance(report.match_evidence, EntityMatchEvidence)
    assert list(payload["match_evidence"]) == [
        "matched_items",
        "accepted_without_context_items",
        "context_supported_items",
        "parent_brand_supported_items",
        "safe_alias_supported_items",
        "other_supported_items",
        "min_confidence",
        "avg_confidence",
        "max_confidence",
    ]
    assert payload["match_evidence"] == {
        "matched_items": 0,
        "accepted_without_context_items": 0,
        "context_supported_items": 0,
        "parent_brand_supported_items": 0,
        "safe_alias_supported_items": 0,
        "other_supported_items": 0,
        "min_confidence": None,
        "avg_confidence": None,
        "max_confidence": None,
    }


def test_rendered_reports_cap_entity_and_candidate_summaries() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=2),
        entities=[
            EntityReport(
                entity_name="The Row",
                entity_type="brand",
                label="new",
                heat_score=4.2,
                current_mentions=1,
                baseline_mentions=0,
                distinct_sources=1,
                representative_items=[
                    RepresentativeItem(
                        source_name="Vogue Business",
                        source_url="https://example.com/the-row",
                        published_at=AS_OF,
                        title="The Row signal",
                        summary=LONG_SUMMARY,
                    )
                ],
            )
        ],
        candidates=[
            CandidateReport(
                phrase="Le Teckel bag",
                candidate_type="bag",
                label="new_candidate",
                score=2.1,
                current_mentions=1,
                baseline_mentions=0,
                distinct_sources=1,
                first_seen_at=AS_OF,
                representative_items=[
                    RepresentativeItem(
                        source_name="Fashionista",
                        source_url="https://example.com/le-teckel",
                        published_at=AS_OF,
                        title="Le Teckel signal",
                        summary=LONG_SUMMARY,
                    )
                ],
            )
        ],
    )

    markdown = render_markdown_report(report)
    payload = render_json_report(report)
    parsed = json.loads(payload)

    assert "TAIL_MARKER" not in markdown
    assert "TAIL_MARKER" not in payload
    entity_summary = parsed["entities"][0]["representative_items"][0]["summary"]
    candidate_summary = parsed["candidates"][0]["representative_items"][0]["summary"]
    assert len(entity_summary) <= REPORT_SNIPPET_MAX_CHARS
    assert len(candidate_summary) <= REPORT_SNIPPET_MAX_CHARS
    assert entity_summary.endswith("...")
    assert candidate_summary.endswith("...")


def test_daily_report_includes_stable_daily_brief_json_shape(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row",
        entity_name="The Row",
        source_name="Vogue Business",
        source_weight=1.7,
        collected_at=AS_OF - timedelta(hours=1),
        summary="The Row gains local observed coverage.",
    )
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel",
            title="Le Teckel bag signal",
            published_at=AS_OF - timedelta(hours=2),
            summary="Le Teckel bag appears in a local observed item.",
        ),
        collected_at=AS_OF - timedelta(hours=2),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel-again",
            title="Le Teckel bag appears again",
            published_at=AS_OF - timedelta(hours=3),
            summary="Le Teckel bag appears again in local observed coverage.",
        ),
        collected_at=AS_OF - timedelta(hours=3),
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    parsed = json.loads(render_json_report(report))

    assert isinstance(report.brief, DailyBrief)
    assert isinstance(report.brief.sections[0], DailyBriefSection)
    assert isinstance(report.brief.sections[0].items[0], DailyBriefItem)
    assert list(parsed) == [
        "metadata",
        "brief",
        "entities",
        "candidates",
        "source_health",
        "recent_runs",
    ]
    assert list(parsed["brief"]) == [
        "contract_version",
        "execution_mode",
        "summary",
        "sections",
        "boundaries",
    ]
    assert parsed["brief"]["contract_version"] == "daily-brief/v1"
    assert parsed["brief"]["execution_mode"] == "local_report_derived"
    assert "Local observed brief" in parsed["brief"]["summary"]
    assert (
        "It provides no demand proof and no platform coverage verification."
        in parsed["brief"]["summary"]
    )
    assert [section["name"] for section in parsed["brief"]["sections"]] == [
        "tracked_signals",
        "candidate_signals",
        "source_caveats",
    ]
    assert parsed["brief"]["sections"][0]["items"][0]["kind"] == "tracked_entity"
    assert parsed["brief"]["sections"][0]["items"][0]["title"] == "The Row"
    assert parsed["brief"]["sections"][0]["items"][0]["reason_codes"] == [
        "new_tracked_entity",
        "current_mentions_observed",
        "high_weight_source_observed",
    ]
    assert parsed["brief"]["sections"][1]["items"][0]["kind"] == "candidate_phrase"
    assert parsed["brief"]["sections"][1]["items"][0]["needs_review"] is True
    assert parsed["brief"]["sections"][1]["items"][0]["reason_codes"] == [
        "candidate_needs_review",
        "new_candidate_phrase",
        "current_mentions_observed",
        "multiple_sources_observed",
    ]
    candidate_item = parsed["brief"]["sections"][1]["items"][0]
    assert "Score components:" in candidate_item["summary"]
    assert "high-weight" not in candidate_item["summary"]
    assert parsed["brief"]["boundaries"] == [
        (
            "Daily Brief is derived from local report rows for configured sources "
            "and imported local signals."
        ),
        (
            "Daily Brief does not collect sources, search platforms, prove demand, "
            "or verify platform coverage."
        ),
    ]


def test_daily_brief_caps_source_caveat_errors_and_deduplicates_recent_runs() -> None:
    long_error = "Lead error. " + ("detail " * 120) + "TAIL_MARKER"

    brief = build_daily_brief(
        entities=[],
        candidates=[],
        source_health=[
            SourceHealthReport(
                source_name="Vogue Business",
                source_type="rss",
                consecutive_failures=2,
                last_error_message=long_error,
            )
        ],
        recent_runs=[
            CollectorRunReport(
                source_name="vogue business",
                source_type="RSS",
                status="failed",
                started_at=AS_OF,
                finished_at=AS_OF,
                items_seen=0,
                items_stored=0,
                error_message=long_error,
                error_type="ReadTimeout",
            ),
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="failed",
                started_at=AS_OF,
                finished_at=AS_OF,
                items_seen=0,
                items_stored=0,
                error_message=long_error,
                error_type="ReadTimeout",
            ),
        ],
        limit_per_section=3,
    )

    source_items = brief.sections[2].items

    assert [item.title for item in source_items] == ["Vogue Business", "Fashionista"]
    assert source_items[0].reason_codes == [
        "source_health_failure",
        "source_last_error_present",
    ]
    assert source_items[1].reason_codes == ["recent_collection_failed"]
    assert all("Lead error." in item.summary for item in source_items)
    assert all("Last error:" in item.summary for item in source_items)
    assert all("TAIL_MARKER" not in item.summary for item in source_items)
    assert all("..." in item.summary for item in source_items)


def test_markdown_report_renders_daily_brief_before_top_signals(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row",
        entity_name="The Row",
        source_name="Vogue Business",
        source_weight=1.7,
        collected_at=AS_OF - timedelta(hours=1),
        summary="The Row local observed signal.",
    )
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel",
            title="Le Teckel bag signal",
            published_at=AS_OF - timedelta(hours=2),
            summary="Le Teckel bag appears in local observed coverage.",
        ),
        collected_at=AS_OF - timedelta(hours=2),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel-again",
            title="Le Teckel bag appears again",
            published_at=AS_OF - timedelta(hours=3),
            summary="Le Teckel bag appears again in local observed coverage.",
        ),
        collected_at=AS_OF - timedelta(hours=3),
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)

    assert markdown.index("## Daily Brief") < markdown.index("## Top Signals")
    assert "### Tracked Signals To Review" in markdown
    assert "- The Row:" in markdown
    daily_brief = markdown.split("## Daily Brief", 1)[1].split("## Top Signals", 1)[0]
    candidate_brief = daily_brief.split("### Candidate Signals Needing Review", 1)[1].split(
        "### Source Caveats", 1
    )[0]
    assert "### Candidate Signals Needing Review" in daily_brief
    assert "- Le Teckel bag:" in candidate_brief
    assert "Score components: mentions 2.00; growth 0.00; sources 1.00" in candidate_brief
    assert "high-weight" not in candidate_brief
    assert "Reasons:" in markdown
    assert "It provides no demand proof and no platform coverage verification." in markdown
    for forbidden in (
        "viral",
        "market-wide trend",
        "platform-wide popularity",
        "verified demand",
        "top social trend",
    ):
        assert forbidden not in markdown.lower()


def test_daily_brief_candidate_summary_includes_existing_score_components() -> None:
    brief = build_daily_brief(
        entities=[],
        candidates=[
            CandidateReport(
                phrase="Le Teckel bag",
                candidate_type="bag",
                label="rising_candidate",
                score=4.25,
                weighted_mention_component=2.5,
                growth_component=0.75,
                source_diversity_component=1.0,
                current_mentions=2,
                baseline_mentions=1,
                distinct_sources=3,
                growth_ratio=2.0,
                first_seen_at=AS_OF,
            )
        ],
        source_health=[],
        recent_runs=[],
    )

    candidate_item = brief.sections[1].items[0]

    assert candidate_item.kind == "candidate_phrase"
    assert candidate_item.score == 4.25
    assert "Score components: mentions 2.50; growth 0.75; sources 1.00" in candidate_item.summary
    assert "mentions 2.50" in candidate_item.summary
    assert "growth 0.75" in candidate_item.summary
    assert "sources 1.00" in candidate_item.summary
    assert "high-weight" not in candidate_item.summary
    assert not hasattr(candidate_item, "weighted_mention_component")


def test_daily_brief_markdown_uses_section_empty_fallback_when_partially_empty() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        brief=DailyBrief(
            summary=(
                "Local observed brief from configured sources and imported local signals: "
                "1 tracked signal, 0 candidate signals needing review, 0 source caveats. "
                "It provides no demand proof and no platform coverage verification."
            ),
            sections=[
                DailyBriefSection(
                    name="tracked_signals",
                    title="Tracked Signals To Review",
                    items=[
                        DailyBriefItem(
                            kind="tracked_entity",
                            title="The Row",
                            summary="Local observed tracked brand signal.",
                            reason_codes=["current_mentions_observed"],
                            current_mentions=1,
                        )
                    ],
                ),
                DailyBriefSection(
                    name="candidate_signals",
                    title="Candidate Signals Needing Review",
                ),
                DailyBriefSection(name="source_caveats", title="Source Caveats"),
            ],
        ),
    )

    markdown = render_markdown_report(report)

    assert "- No items in this section." in markdown
    assert "- No daily brief items available." not in markdown


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
    parsed = json.loads(render_json_report(report))

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
    entity = parsed["entities"][0]
    assert entity["weighted_mention_component"] > 0
    assert entity["growth_component"] == 0
    assert entity["source_diversity_component"] == 0
    assert entity["high_weight_component"] > 0
    assert "- Score components:" in markdown


def test_daily_report_includes_aggregate_entity_match_evidence(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-context",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=1),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw alias must stay internal",
                "confidence": 0.8,
                "reason": "context",
                "context_terms": ["raw context must stay internal"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw alias duplicate must stay internal",
                "confidence": 0.95,
                "reason": "parent_brand",
                "context_terms": ["raw duplicate context must stay internal"],
            },
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-safe",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=2),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw safe alias must stay internal",
                "confidence": 0.9,
                "reason": "safe_alias",
                "context_terms": ["raw safe context must stay internal"],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-context-direct",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(minutes=90),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw direct context alias must stay internal",
                "confidence": 0.8333,
                "reason": "context",
                "context_terms": ["raw direct context must stay internal"],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-accepted",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(minutes=95),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw accepted alias must stay internal",
                "confidence": 0.7665,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-tie",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=3),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw tie safe alias must stay internal",
                "confidence": 0.7,
                "reason": "safe_alias",
                "context_terms": ["raw tie safe context must stay internal"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw tie parent alias must stay internal",
                "confidence": 0.7,
                "reason": "parent_brand",
                "context_terms": ["raw tie parent context must stay internal"],
            },
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-tie-reversed",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=3, minutes=30),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw reversed tie parent alias must stay internal",
                "confidence": 0.75,
                "reason": "parent_brand",
                "context_terms": ["raw reversed tie parent context must stay internal"],
            },
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "raw reversed tie safe alias must stay internal",
                "confidence": 0.75,
                "reason": "safe_alias",
                "context_terms": ["raw reversed tie safe context must stay internal"],
            },
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-low-confidence",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=4),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "low confidence alias must stay internal",
                "confidence": 0.3,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-wrong-type",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(hours=5),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "product",
                "alias": "wrong type alias must stay internal",
                "confidence": 0.99,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    _store_item_with_matches(
        engine,
        url="https://example.com/the-row-old",
        entity_name="The Row",
        collected_at=AS_OF - timedelta(days=8),
        matches=[
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "old alias must stay internal",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(current_window_days=7, min_match_confidence=0.5),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    evidence = report.entities[0].match_evidence
    markdown = render_markdown_report(report)

    assert evidence.matched_items == 6
    assert evidence.accepted_without_context_items == 1
    assert evidence.context_supported_items == 1
    assert evidence.parent_brand_supported_items == 3
    assert evidence.safe_alias_supported_items == 1
    assert evidence.other_supported_items == 0
    assert evidence.min_confidence == 0.7
    assert evidence.avg_confidence == 0.8166
    assert evidence.max_confidence == 0.95
    assert (
        "- Match evidence: 6 matched items; 1 accepted without context, "
        "1 context supported, 3 parent-brand supported, 1 safe-alias supported; "
        "confidence 0.70-0.95 avg 0.82"
    ) in markdown
    for forbidden in (
        "raw alias must stay internal",
        "raw alias duplicate must stay internal",
        "raw duplicate context must stay internal",
        "raw safe alias must stay internal",
        "raw safe context must stay internal",
        "raw direct context alias must stay internal",
        "raw direct context must stay internal",
        "raw accepted alias must stay internal",
        "raw tie safe alias must stay internal",
        "raw tie safe context must stay internal",
        "raw tie parent alias must stay internal",
        "raw tie parent context must stay internal",
        "raw reversed tie parent alias must stay internal",
        "raw reversed tie parent context must stay internal",
        "raw reversed tie safe alias must stay internal",
        "raw reversed tie safe context must stay internal",
        "low confidence alias must stay internal",
        "wrong type alias must stay internal",
        "old alias must stay internal",
    ):
        assert forbidden not in markdown


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
    entity = parsed["entities"][0]
    assert entity["match_evidence"]["matched_items"] == 1
    assert entity["match_evidence"]["other_supported_items"] == 1
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
        "raw duplicate context must stay internal",
        "raw safe alias must stay internal",
    ):
        assert forbidden not in payload


def test_rendered_entity_sections_show_empty_match_evidence_message() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        entities=[
            EntityReport(
                entity_name="No Evidence Brand",
                entity_type="brand",
                label="new",
                heat_score=1.0,
                current_mentions=1,
                baseline_mentions=0,
                distinct_sources=1,
            )
        ],
    )

    markdown = render_markdown_report(report)

    assert (
        "- Match evidence: no current-window accepted matches above the report "
        "confidence threshold."
    ) in markdown


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
    assert parsed["brief"]["summary"] == (
        "Local observed brief from configured sources and imported local signals: "
        "0 tracked signals, 0 candidate signals needing review, 0 source caveats. "
        "It provides no demand proof and no platform coverage verification."
    )
    assert all(section["items"] == [] for section in parsed["brief"]["sections"])
    assert "No entity signals in this window." in markdown
    assert "## Daily Brief" in markdown
    assert "- No daily brief items available." in markdown


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
    assert "from configured sources and imported local signals" in markdown.lower()
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
    candidate = parsed["candidates"][0]
    assert candidate["weighted_mention_component"] == pytest.approx(2.0)
    assert candidate["growth_component"] == 0
    assert candidate["source_diversity_component"] == pytest.approx(1.0)
    assert candidate["score"] == pytest.approx(3.0)
    assert candidate["score"] == pytest.approx(
        candidate["weighted_mention_component"]
        + candidate["growth_component"]
        + candidate["source_diversity_component"]
    )
    assert "- Score components: mentions 2.00; growth 0.00; sources 1.00" in markdown
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


def test_markdown_source_health_collapses_and_truncates_long_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=3,
                unhealthy_until=AS_OF + timedelta(hours=1),
                last_error_message=LONG_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert "WWD (rss)" in source_health_section
    assert "3 consecutive failures" in source_health_section
    assert "TAIL_MARKER" not in source_health_section
    assert "retry detail" in source_health_section
    assert source_health_section.rstrip().endswith("...")


def test_markdown_source_health_collapses_multiline_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="Fashionista",
                source_type="rss",
                consecutive_failures=2,
                last_error_message=MULTILINE_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert "connection reset by peer retry exhausted TAIL_MARKER" in source_health_section
    assert "connection reset\n  by peer" not in source_health_section
    assert "retry exhausted TAIL_MARKER" in source_health_section


def test_markdown_source_health_without_error_keeps_no_error_fallback() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=0,
                last_error_message=None,
            )
        ],
    )

    markdown = render_markdown_report(report)
    source_health_section = markdown.split("## Source Health", 1)[1].split(
        "## Recent Collector Runs", 1
    )[0]

    assert "no error" in source_health_section
    assert "None" not in source_health_section


def test_markdown_recent_runs_collapses_and_truncates_long_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=0,
                items_stored=0,
                error_message=LONG_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    assert "WWD (rss)" in recent_runs_section
    assert "failed" in recent_runs_section
    assert "0/0 stored" in recent_runs_section
    assert "TAIL_MARKER" not in recent_runs_section
    assert "retry detail" in recent_runs_section
    assert recent_runs_section.rstrip().endswith("...")


def test_markdown_recent_runs_collapses_multiline_error() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=4,
                items_stored=2,
                error_message=MULTILINE_ERROR,
            )
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    assert "connection reset by peer retry exhausted TAIL_MARKER" in recent_runs_section
    assert "connection reset\n  by peer" not in recent_runs_section


def test_markdown_recent_runs_omits_error_segment_when_snippet_is_none() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="ok",
                started_at=AS_OF - timedelta(minutes=5),
                finished_at=AS_OF - timedelta(minutes=4),
                items_seen=9,
                items_stored=9,
                error_message=WHITESPACE_ONLY_ERROR,
            ),
            CollectorRunReport(
                source_name="Fashionista",
                source_type="rss",
                status="ok",
                started_at=AS_OF - timedelta(minutes=3),
                finished_at=AS_OF - timedelta(minutes=2),
                items_seen=7,
                items_stored=7,
                error_message=None,
            ),
        ],
    )

    markdown = render_markdown_report(report)
    recent_runs_section = markdown.split("## Recent Collector Runs", 1)[1]

    wwd_line = next(line for line in recent_runs_section.splitlines() if "WWD (rss)" in line)
    fashionista_line = next(
        line for line in recent_runs_section.splitlines() if "Fashionista (rss)" in line
    )
    assert wwd_line.endswith("9/9 stored")
    assert ";" not in wwd_line
    assert fashionista_line.endswith("7/7 stored")
    assert ";" not in fashionista_line


def test_json_report_keeps_raw_source_health_and_run_error_fields() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF),
        source_health=[
            SourceHealthReport(
                source_name="WWD",
                source_type="rss",
                consecutive_failures=3,
                last_error_message=LONG_ERROR,
            )
        ],
        recent_runs=[
            CollectorRunReport(
                source_name="WWD",
                source_type="rss",
                status="failed",
                started_at=AS_OF - timedelta(minutes=5),
                items_seen=0,
                items_stored=0,
                error_message=MULTILINE_ERROR,
            )
        ],
    )

    parsed = json.loads(render_json_report(report))

    assert parsed["source_health"][0]["last_error_message"] == LONG_ERROR
    assert parsed["recent_runs"][0]["error_message"] == MULTILINE_ERROR


def test_render_html_report_produces_valid_html_with_empty_report() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=0),
    )

    html = render_html_report(report)

    assert "<!DOCTYPE html>" in html
    assert "</html>" in html
    assert "FASHION RADAR" in html
    assert "No entity signals" in html


def test_render_html_report_includes_entities_and_candidates() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=5),
        entities=[
            EntityReport(
                entity_name="The Row",
                entity_type="brand",
                label="rising",
                heat_score=8.5,
                current_mentions=12,
                baseline_mentions=5,
                distinct_sources=4,
                representative_items=[
                    RepresentativeItem(
                        source_name="WWD",
                        source_url="https://wwd.com/test",
                        published_at=AS_OF,
                        title="The Row Margaux",
                        summary="Popular bag.",
                    )
                ],
            ),
        ],
        candidates=[
            CandidateReport(
                phrase="quiet luxury",
                candidate_type="trend",
                label="rising_candidate",
                score=6.0,
                current_mentions=8,
                baseline_mentions=2,
                distinct_sources=3,
                first_seen_at=AS_OF,
            ),
        ],
    )

    html = render_html_report(report)

    assert "The Row" in html
    assert "quiet luxury" in html
    assert "score-fill" in html
    assert "wwd.com/test" in html


def test_render_html_report_includes_recent_items_safely() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=2),
    )
    long_summary = "Lead text. " + ("detail " * 40) + "TAIL_MARKER"

    html = render_html_report(
        report,
        recent_items=[
            {
                "source_name": "Vogue & Business",
                "url": "https://example.com/the-row?ref=a&b=1",
                "title": "The Row <Margaux> gains momentum",
                "summary": "Fresh local coverage.",
            },
            {
                "source_name": "<Unsafe Source>",
                "url": "javascript:alert(1)",
                "title": "<script>alert(1)</script>",
                "summary": long_summary,
            },
        ],
    )

    assert "<h2>Latest Collected News</h2>" in html
    assert "The Row &lt;Margaux&gt; gains momentum" in html
    assert "Vogue &amp; Business" in html
    assert "Fresh local coverage." in html
    assert "href='https://example.com/the-row?ref=a&amp;b=1'" in html
    assert "target='_blank' rel='noopener'" in html
    assert "javascript:" not in html
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;Unsafe Source&gt;" in html
    assert "TAIL_MARKER" not in html


def test_render_html_report_escapes_untrusted_content() -> None:
    report = DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        entities=[
            EntityReport(
                entity_name="<script>alert(1)</script>",
                entity_type="brand",
                label="rising",
                heat_score=5.0,
                current_mentions=1,
                baseline_mentions=0,
                distinct_sources=1,
                representative_items=[
                    RepresentativeItem(
                        source_name="Dolce & Gabbana",
                        source_url="javascript:alert(1)",
                        published_at=AS_OF,
                        title="Dolce & Gabbana <show>",
                        summary="Test 'quote' & ampersand",
                    )
                ],
            ),
        ],
    )

    html = render_html_report(report)

    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    assert "javascript:" not in html
    assert "Dolce &amp; Gabbana" in html
    assert "&lt;show&gt;" in html
