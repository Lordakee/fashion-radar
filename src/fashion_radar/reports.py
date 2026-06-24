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
    DailyBrief,
    DailyBriefItem,
    DailyBriefSection,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    SourceHealthReport,
    report_safe_snippet,
)
from fashion_radar.scoring import EntityHeatMetric, score_entities
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc

DAILY_BRIEF_SECTION_LIMIT = 3


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
    source_health_reports = _source_health_reports(engine)
    recent_run_reports = _recent_run_reports(engine, limit=recent_runs_limit)
    return DailyReport(
        metadata=ReportMetadata(
            generated_at=generated_at or as_of_utc,
            report_date=as_of_utc,
            item_count=sum(entity.current_mentions for entity in entities),
        ),
        brief=build_daily_brief(
            entities=entities,
            candidates=candidates,
            source_health=source_health_reports,
            recent_runs=recent_run_reports,
        ),
        entities=entities,
        candidates=candidates,
        source_health=source_health_reports,
        recent_runs=recent_run_reports,
    )


def render_json_report(report: DailyReport) -> str:
    return report.model_dump_json(indent=2)


def render_markdown_report(report: DailyReport) -> str:
    template = resources.files("fashion_radar.templates").joinpath("daily_report.md")
    return template.read_text(encoding="utf-8").format(
        generated_at=report.metadata.generated_at.isoformat(),
        report_date=report.metadata.report_date.isoformat(),
        item_count=report.metadata.item_count,
        brief_section=_render_daily_brief(report.brief),
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
        weighted_mention_component=metric.weighted_mention_component,
        growth_component=metric.growth_component,
        source_diversity_component=metric.source_diversity_component,
        high_weight_component=metric.high_weight_component,
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
        representative_items=list(metric.representative_items),
    )


def _render_daily_brief(brief: DailyBrief) -> str:
    lines = [brief.summary]
    any_items = False
    for section in brief.sections:
        lines.extend(["", f"### {section.title}"])
        if not section.items:
            lines.append("- No items in this section.")
            continue
        any_items = True
        for item in section.items:
            reasons = ", ".join(item.reason_codes) if item.reason_codes else "none"
            lines.append(
                f"- {_table_cell(item.title)}: {_table_cell(item.summary)} "
                f"Reasons: {_table_cell(reasons)}."
            )
    if not any_items:
        return "\n".join([brief.summary, "", "- No daily brief items available."])
    return "\n".join(lines)


def build_daily_brief(
    *,
    entities: list[EntityReport],
    candidates: list[CandidateReport],
    source_health: list[SourceHealthReport],
    recent_runs: list[CollectorRunReport],
    limit_per_section: int = DAILY_BRIEF_SECTION_LIMIT,
) -> DailyBrief:
    if limit_per_section < 0:
        raise ValueError("limit_per_section must be at least 0")

    tracked_items = [_brief_item_for_entity(entity) for entity in entities[:limit_per_section]]
    candidate_items = [
        _brief_item_for_candidate(candidate) for candidate in candidates[:limit_per_section]
    ]
    source_items = _source_caveat_items(
        source_health=source_health,
        recent_runs=recent_runs,
        limit=limit_per_section,
    )

    return DailyBrief(
        summary=_daily_brief_summary(
            tracked_count=len(tracked_items),
            candidate_count=len(candidate_items),
            source_caveat_count=len(source_items),
        ),
        sections=[
            DailyBriefSection(
                name="tracked_signals",
                title="Tracked Signals To Review",
                items=tracked_items,
            ),
            DailyBriefSection(
                name="candidate_signals",
                title="Candidate Signals Needing Review",
                items=candidate_items,
            ),
            DailyBriefSection(name="source_caveats", title="Source Caveats", items=source_items),
        ],
    )


def _daily_brief_summary(
    *,
    tracked_count: int,
    candidate_count: int,
    source_caveat_count: int,
) -> str:
    tracked_label = _count_label(tracked_count, "tracked signal", "tracked signals")
    candidate_label = _count_label(
        candidate_count,
        "candidate signal needing review",
        "candidate signals needing review",
    )
    source_caveat_label = _count_label(
        source_caveat_count,
        "source caveat",
        "source caveats",
    )
    return (
        "Local observed brief from configured sources and imported local signals: "
        f"{tracked_count} {tracked_label}, "
        f"{candidate_count} {candidate_label}, "
        f"{source_caveat_count} {source_caveat_label}. "
        "It provides no demand proof and no platform coverage verification."
    )


def _brief_item_for_entity(entity: EntityReport) -> DailyBriefItem:
    return DailyBriefItem(
        kind="tracked_entity",
        title=entity.entity_name,
        summary=(
            f"Local observed tracked {entity.entity_type} signal from configured sources "
            f"and imported local signals: {entity.current_mentions} "
            f"{_count_label(entity.current_mentions, 'current mention', 'current mentions')}, "
            f"{entity.baseline_mentions} "
            f"{_count_label(entity.baseline_mentions, 'baseline mention', 'baseline mentions')}, "
            f"{entity.distinct_sources} "
            f"{_count_label(entity.distinct_sources, 'distinct source', 'distinct sources')}."
        ),
        reason_codes=_entity_reason_codes(entity),
        current_mentions=entity.current_mentions,
        baseline_mentions=entity.baseline_mentions,
        distinct_sources=entity.distinct_sources,
        score=entity.heat_score,
    )


def _brief_item_for_candidate(candidate: CandidateReport) -> DailyBriefItem:
    current_label = _count_label(candidate.current_mentions, "current mention", "current mentions")
    baseline_label = _count_label(
        candidate.baseline_mentions,
        "baseline mention",
        "baseline mentions",
    )
    source_label = _count_label(candidate.distinct_sources, "distinct source", "distinct sources")
    return DailyBriefItem(
        kind="candidate_phrase",
        title=candidate.phrase,
        summary=(
            "Local observed candidate phrase from configured sources and imported local "
            f"signals; needs review: {candidate.current_mentions} {current_label}, "
            f"{candidate.baseline_mentions} {baseline_label}, "
            f"{candidate.distinct_sources} {source_label}."
        ),
        reason_codes=_candidate_reason_codes(candidate),
        current_mentions=candidate.current_mentions,
        baseline_mentions=candidate.baseline_mentions,
        distinct_sources=candidate.distinct_sources,
        score=candidate.score,
        needs_review=True,
    )


def _source_caveat_items(
    *,
    source_health: list[SourceHealthReport],
    recent_runs: list[CollectorRunReport],
    limit: int,
) -> list[DailyBriefItem]:
    if limit == 0:
        return []

    health_sources = [
        source
        for source in sorted(
            source_health,
            key=lambda row: (-row.consecutive_failures, row.source_name, row.source_type),
        )
        if _source_health_needs_caveat(source)
    ]
    health_items = [_brief_item_for_source_health(source) for source in health_sources]
    represented_health_keys = {
        _source_caveat_key(source.source_name, source.source_type) for source in health_sources
    }
    remaining = limit - len(health_items)
    if remaining <= 0:
        return health_items[:limit]

    run_items = [
        _brief_item_for_recent_run(run)
        for run in recent_runs
        if run.status.casefold() == "failed"
        and _source_caveat_key(run.source_name, run.source_type) not in represented_health_keys
    ]
    return (health_items + run_items[:remaining])[:limit]


def _brief_item_for_source_health(source: SourceHealthReport) -> DailyBriefItem:
    reasons: list[str] = []
    if source.consecutive_failures > 0:
        reasons.append("source_health_failure")
    if source.unhealthy_until is not None:
        reasons.append("source_unhealthy_until_set")
    if source.last_error_message:
        reasons.append("source_last_error_present")

    failure_label = _count_label(
        source.consecutive_failures,
        "consecutive failure",
        "consecutive failures",
    )
    summary = (
        f"Local source caveat: {source.source_name} has {source.consecutive_failures} "
        f"{failure_label}."
    )
    error_message = report_safe_snippet(source.last_error_message)
    if error_message:
        summary = f"{summary} Last error: {error_message}."

    return DailyBriefItem(
        kind="source_caveat",
        title=source.source_name,
        summary=summary,
        reason_codes=reasons,
    )


def _brief_item_for_recent_run(run: CollectorRunReport) -> DailyBriefItem:
    error_message = report_safe_snippet(run.error_message)
    return DailyBriefItem(
        kind="collector_run_caveat",
        title=run.source_name,
        summary=(
            f"Local source caveat: {run.source_name} recent collection failed with "
            f"{run.items_stored}/{run.items_seen} stored."
            + (f" Last error: {error_message}." if error_message else "")
        ),
        reason_codes=["recent_collection_failed"],
    )


def _source_caveat_key(source_name: str, source_type: str) -> tuple[str, str]:
    return (source_name.casefold(), source_type.casefold())


def _source_health_needs_caveat(source: SourceHealthReport) -> bool:
    return (
        source.consecutive_failures > 0
        or source.unhealthy_until is not None
        or bool(source.last_error_message)
    )


def _entity_reason_codes(entity: EntityReport) -> list[str]:
    codes: list[str] = []
    if entity.label == "new":
        codes.append("new_tracked_entity")
    if entity.label == "rising":
        codes.append("rising_tracked_entity")
    if entity.current_mentions > 0:
        codes.append("current_mentions_observed")
    if entity.baseline_mentions > 0:
        codes.append("baseline_mentions_observed")
    if entity.distinct_sources > 1:
        codes.append("multiple_sources_observed")
    if entity.growth_component > 0:
        codes.append("growth_component_observed")
    if entity.high_weight_component > 0:
        codes.append("high_weight_source_observed")
    return codes


def _candidate_reason_codes(candidate: CandidateReport) -> list[str]:
    codes = ["candidate_needs_review"]
    if candidate.label == "new_candidate":
        codes.append("new_candidate_phrase")
    if candidate.label == "rising_candidate":
        codes.append("rising_candidate_phrase")
    if candidate.current_mentions > 0:
        codes.append("current_mentions_observed")
    if candidate.baseline_mentions > 0:
        codes.append("baseline_mentions_observed")
    if candidate.distinct_sources > 1:
        codes.append("multiple_sources_observed")
    if candidate.growth_ratio is not None:
        codes.append("growth_ratio_observed")
    return codes


def _count_label(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def _table_cell(value: str) -> str:
    return " ".join(value.replace("|", "/").replace("\r", " ").replace("\n", " ").split())


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
                    (
                        "- Score components: "
                        f"mentions {entity.weighted_mention_component:.2f}; "
                        f"growth {entity.growth_component:.2f}; "
                        f"sources {entity.source_diversity_component:.2f}; "
                        f"high-weight {entity.high_weight_component:.2f}"
                    ),
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
                    "imported local signals and needs review.",
                    f"- Type: {candidate.candidate_type}",
                    f"- Score: {candidate.score:.2f}",
                    f"- Mentions: {candidate.current_mentions} current, "
                    f"{candidate.baseline_mentions} baseline",
                    f"- Distinct sources: {candidate.distinct_sources}",
                    f"- Growth ratio: {growth}",
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
