from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.runner import collect_sources
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository, PruneResult
from fashion_radar.db.schema import initialize_schema
from fashion_radar.extract.entities import match_entities
from fashion_radar.models.entity import EntityDefinition
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.reports import build_daily_report, render_json_report, render_markdown_report
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc


@dataclass(frozen=True)
class MatchSummary:
    items_processed: int
    matches_stored: int


def default_database_path(data_dir: Path) -> Path:
    return data_dir / "fashion-radar.sqlite"


def report_output_paths(reports_dir: Path, as_of: datetime) -> tuple[Path, Path]:
    report_date = parse_datetime_utc(as_of).date().isoformat()
    return (
        reports_dir / f"fashion-radar-{report_date}.md",
        reports_dir / f"fashion-radar-{report_date}.json",
    )


def write_daily_report_files(
    *,
    data_dir: Path,
    reports_dir: Path,
    scoring: ScoringSettings,
    as_of: str | datetime,
    candidate_discovery: CandidateDiscoverySettings | None = None,
    entity_config: EntityConfig | None = None,
) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    as_of_utc = parse_datetime_utc(as_of)
    report = build_daily_report(
        engine,
        scoring=scoring,
        candidate_discovery=candidate_discovery,
        entity_config=entity_config,
        as_of=as_of_utc,
    )
    markdown_path, json_path = report_output_paths(reports_dir, as_of_utc)
    markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
    json_path.write_text(render_json_report(report) + "\n", encoding="utf-8")
    return markdown_path, json_path


def collect_configured_sources(
    *,
    data_dir: Path,
    sources: Sequence[SourceDefinition],
    collectors: Mapping[str | SourceType, object] | None = None,
    now: datetime | None = None,
):
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    return collect_sources(
        sources,
        engine=engine,
        collectors=collectors or _default_collectors(),
        now=parse_datetime_utc(now) if now is not None else None,
    )


def match_stored_items(
    *,
    data_dir: Path,
    entities: Sequence[EntityDefinition],
) -> MatchSummary:
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    items = repository.list_items_for_matching()
    matches_stored = 0
    for item in items:
        text = " ".join(
            value for value in (item["title"], item["summary"]) if isinstance(value, str)
        )
        matches = match_entities(text, entities)
        repository.replace_item_matches(item["id"], matches)
        matches_stored += len(matches)
    return MatchSummary(items_processed=len(items), matches_stored=matches_stored)


def clean_old_data(
    *,
    data_dir: Path,
    as_of: str | datetime,
    retention_days: int,
    dry_run: bool = False,
) -> PruneResult:
    cutoff = parse_datetime_utc(as_of) - timedelta(days=retention_days)
    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    return ItemRepository(engine).prune_items_older_than(cutoff, dry_run=dry_run)


def _default_collectors() -> dict[SourceType, object]:
    return {
        SourceType.RSS: RssCollector(),
        SourceType.RSSHUB: RssCollector(),
        SourceType.GDELT: GdeltCollector(),
    }
