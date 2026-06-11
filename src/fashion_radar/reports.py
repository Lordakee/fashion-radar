from __future__ import annotations

from datetime import datetime, timedelta
from importlib import resources
from typing import Any

from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.repositories import CollectorRunRepository
from fashion_radar.db.schema import item_entities, items, source_health
from fashion_radar.discovery.candidates import CandidateMetric, discover_candidates
from fashion_radar.models.report import (
    CandidateReport,
    CollectorRunReport,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    SourceHealthReport,
)
from fashion_radar.scoring import EntityHeatMetric, score_entities
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc


def build_daily_report(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    as_of: datetime,
    candidate_discovery: CandidateDiscoverySettings | None = None,
    entity_config: EntityConfig | None = None,
    generated_at: datetime | None = None,
    max_entities: int = 20,
    representative_items_per_entity: int = 3,
    recent_runs_limit: int = 10,
) -> DailyReport:
    as_of_utc = parse_datetime_utc(as_of)
    metrics = score_entities(engine, scoring=scoring, as_of=as_of_utc)[:max_entities]
    entities = [
        _entity_report(
            engine,
            metric,
            scoring=scoring,
            as_of=as_of_utc,
            representative_items_per_entity=representative_items_per_entity,
        )
        for metric in metrics
    ]
    candidate_settings = candidate_discovery or CandidateDiscoverySettings()
    candidates = [
        _candidate_report(metric)
        for metric in discover_candidates(
            engine,
            scoring=scoring,
            settings=candidate_settings,
            entity_config=entity_config,
            as_of=as_of_utc,
        )
    ]
    return DailyReport(
        metadata=ReportMetadata(
            generated_at=generated_at or as_of_utc,
            report_date=as_of_utc,
            item_count=sum(entity.current_mentions for entity in entities),
        ),
        entities=entities,
        candidates=candidates,
        source_health=_source_health_reports(engine),
        recent_runs=_recent_run_reports(engine, limit=recent_runs_limit),
    )


def render_json_report(report: DailyReport) -> str:
    return report.model_dump_json(indent=2)


def render_markdown_report(report: DailyReport) -> str:
    template = resources.files("fashion_radar.templates").joinpath("daily_report.md")
    return template.read_text(encoding="utf-8").format(
        generated_at=report.metadata.generated_at.isoformat(),
        report_date=report.metadata.report_date.isoformat(),
        item_count=report.metadata.item_count,
        entity_sections=_render_entity_sections(report.entities),
        candidate_sections=_render_candidate_sections(report.candidates),
        source_health_section=_render_source_health(report.source_health),
        recent_runs_section=_render_recent_runs(report.recent_runs),
    )


def _entity_report(
    engine: Engine,
    metric: EntityHeatMetric,
    *,
    scoring: ScoringSettings,
    as_of: datetime,
    representative_items_per_entity: int,
) -> EntityReport:
    return EntityReport(
        entity_name=metric.entity_name,
        entity_type=metric.entity_type,
        label=metric.label,
        heat_score=metric.heat_score,
        current_mentions=metric.current_mentions,
        baseline_mentions=metric.baseline_mentions,
        distinct_sources=metric.distinct_sources,
        growth_ratio=metric.growth_ratio,
        representative_items=_representative_items(
            engine,
            entity_name=metric.entity_name,
            min_match_confidence=scoring.min_match_confidence,
            current_start=as_of - timedelta(days=scoring.current_window_days),
            as_of=as_of,
            limit=representative_items_per_entity,
        ),
    )


def _candidate_report(metric: CandidateMetric) -> CandidateReport:
    return CandidateReport(
        phrase=metric.phrase,
        candidate_type=metric.candidate_type,
        label=metric.label,
        score=metric.score,
        current_mentions=metric.current_mentions,
        baseline_mentions=metric.baseline_mentions,
        distinct_sources=metric.distinct_sources,
        growth_ratio=metric.growth_ratio,
        first_seen_at=metric.first_seen_at,
        contexts=list(metric.contexts),
        representative_items=list(metric.representative_items),
    )


def _representative_items(
    engine: Engine,
    *,
    entity_name: str,
    min_match_confidence: float,
    current_start: datetime,
    as_of: datetime,
    limit: int,
) -> list[RepresentativeItem]:
    with engine.connect() as connection:
        rows = list(
            connection.execute(
                select(
                    items.c.id,
                    items.c.source_name,
                    items.c.url,
                    items.c.published_at,
                    items.c.title,
                    items.c.summary,
                    items.c.collected_at,
                )
                .select_from(item_entities.join(items, item_entities.c.item_id == items.c.id))
                .where(
                    item_entities.c.entity_name == entity_name,
                    item_entities.c.confidence >= min_match_confidence,
                )
            ).mappings()
        )

    by_item_id: dict[int, dict[str, Any]] = {}
    for row in rows:
        collected_at = parse_datetime_utc(row["collected_at"])
        if not (current_start < collected_at <= as_of):
            continue
        by_item_id[int(row["id"])] = dict(row)

    ordered_rows = sorted(
        by_item_id.values(),
        key=lambda row: (parse_datetime_utc(row["collected_at"]), int(row["id"])),
        reverse=True,
    )
    return [
        RepresentativeItem(
            source_name=row["source_name"],
            source_url=row["url"],
            published_at=row["published_at"],
            title=row["title"],
            summary=row["summary"],
        )
        for row in ordered_rows[:limit]
    ]


def _source_health_reports(engine: Engine) -> list[SourceHealthReport]:
    with engine.connect() as connection:
        rows = connection.execute(
            select(source_health).order_by(source_health.c.source_name, source_health.c.source_type)
        ).mappings()
        return [
            SourceHealthReport(
                source_name=row["source_name"],
                source_type=row["source_type"],
                consecutive_failures=row["consecutive_failures"],
                last_success_at=row["last_success_at"],
                last_failure_at=row["last_failure_at"],
                unhealthy_until=row["unhealthy_until"],
                last_error_message=row["last_error_message"],
            )
            for row in rows
        ]


def _recent_run_reports(engine: Engine, *, limit: int) -> list[CollectorRunReport]:
    return [
        CollectorRunReport(
            source_name=row["source_name"],
            source_type=row["source_type"],
            status=row["status"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            items_seen=row["items_seen"],
            items_stored=row["items_stored"],
            error_message=row["error_message"],
            error_type=row["error_type"],
        )
        for row in CollectorRunRepository(engine).list_recent_runs(limit=limit)
    ]


def _render_entity_sections(entities: list[EntityReport]) -> str:
    if not entities:
        return "No entity signals in this window."
    sections: list[str] = []
    for entity in entities:
        items_markdown = "\n".join(
            (
                f"- {item.title} | {item.source_name} | {item.published_at.isoformat()} | "
                f"{item.source_url}\n  {item.summary or ''}"
            )
            for item in entity.representative_items
        )
        if not items_markdown:
            items_markdown = "- No representative items available."
        sections.append(
            "\n".join(
                [
                    f"### {entity.entity_name} ({entity.label})",
                    f"- Type: {entity.entity_type}",
                    f"- Heat score: {entity.heat_score:.2f}",
                    f"- Mentions: {entity.current_mentions} current, "
                    f"{entity.baseline_mentions} baseline",
                    f"- Distinct sources: {entity.distinct_sources}",
                    "",
                    items_markdown,
                ]
            )
        )
    return "\n\n".join(sections)


def _render_candidate_sections(candidates: list[CandidateReport]) -> str:
    if not candidates:
        return "No untracked candidate signals in this window."
    sections: list[str] = []
    for candidate in candidates:
        items_markdown = "\n".join(
            (
                f"- {item.title} | {item.source_name} | {item.published_at.isoformat()} | "
                f"{item.source_url}\n  {item.summary or ''}"
            )
            for item in candidate.representative_items
        )
        if not items_markdown:
            items_markdown = "- No representative items available."
        growth = f"{candidate.growth_ratio:.2f}" if candidate.growth_ratio is not None else "n/a"
        sections.append(
            "\n".join(
                [
                    f"### {candidate.phrase} ({candidate.label})",
                    "This candidate signal is an observed phrase from configured sources and "
                    "needs review.",
                    f"- Type: {candidate.candidate_type}",
                    f"- Score: {candidate.score:.2f}",
                    f"- Mentions: {candidate.current_mentions} current, "
                    f"{candidate.baseline_mentions} baseline",
                    f"- Distinct sources: {candidate.distinct_sources}",
                    f"- Growth ratio: {growth}",
                    f"- Context labels: {', '.join(candidate.contexts) or 'n/a'}",
                    "",
                    items_markdown,
                ]
            )
        )
    return "\n\n".join(sections)


def _render_source_health(source_health_reports: list[SourceHealthReport]) -> str:
    if not source_health_reports:
        return "No source health issues recorded."
    return "\n".join(_render_source_health_line(source) for source in source_health_reports)


def _render_source_health_line(source: SourceHealthReport) -> str:
    unhealthy_until = source.unhealthy_until.isoformat() if source.unhealthy_until else "n/a"
    return (
        f"- {source.source_name} ({source.source_type}): "
        f"{source.consecutive_failures} consecutive failures; "
        f"unhealthy until {unhealthy_until}; "
        f"{source.last_error_message or 'no error'}"
    )


def _render_recent_runs(recent_runs: list[CollectorRunReport]) -> str:
    if not recent_runs:
        return "No recent collector runs recorded."
    return "\n".join(
        (
            f"- {run.started_at.isoformat()} {run.source_name} ({run.source_type}) "
            f"{run.status}: {run.items_stored}/{run.items_seen} stored"
            + (f"; {run.error_message}" if run.error_message else "")
        )
        for run in recent_runs
    )
