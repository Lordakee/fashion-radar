from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import select

from fashion_radar.collectors.gdelt import GdeltCollector
from fashion_radar.collectors.html import HtmlCollector
from fashion_radar.collectors.instagram import InstagramCollector
from fashion_radar.collectors.rss import RssCollector
from fashion_radar.collectors.runner import collect_sources
from fashion_radar.collectors.sitemap import SitemapCollector
from fashion_radar.collectors.twitter import TwitterCollector
from fashion_radar.collectors.xiaohongshu import XiaohongshuCollector
from fashion_radar.collectors.youtube import YouTubeCollector
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository, PruneResult
from fashion_radar.db.schema import initialize_schema
from fashion_radar.db.schema import items as items_table
from fashion_radar.digests import _parse_daily_report_path
from fashion_radar.extract.entities import match_entities
from fashion_radar.html_report import render_html_report
from fashion_radar.models.entity import EntityDefinition
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.reports import build_daily_report, render_json_report, render_markdown_report
from fashion_radar.row_one.edition import build_row_one_edition
from fashion_radar.row_one.render import RowOneRenderResult, render_row_one_site
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


_DAILY_REPORT_HTML_ARTIFACT_RE = re.compile(
    r"^fashion-radar-(?P<report_date>\d{4}-\d{2}-\d{2})\.html$"
)


@dataclass(frozen=True)
class ReportRetentionResult:
    current_date: str
    removed_paths: list[Path]
    kept_current_count: int

    @property
    def removed_count(self) -> int:
        return len(self.removed_paths)


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
    window_start = as_of_utc - timedelta(days=scoring.current_window_days)
    recent_items: list[dict[str, object]] = []
    with engine.connect() as conn:
        rows = conn.execute(
            select(
                items_table.c.source_name,
                items_table.c.url,
                items_table.c.title,
                items_table.c.summary,
                items_table.c.collected_at,
            )
            .where(
                items_table.c.collected_at > window_start.isoformat(),
                items_table.c.collected_at <= as_of_utc.isoformat(),
            )
            .order_by(items_table.c.collected_at.desc())
            .limit(50)
        ).mappings()
        recent_items = [dict(row) for row in rows]
    html_path = reports_dir / f"fashion-radar-{as_of_utc.date().isoformat()}.html"
    html_path.write_text(render_html_report(report, recent_items=recent_items), encoding="utf-8")
    return markdown_path, json_path


def _parse_daily_report_retention_path(path: Path) -> date | None:
    parsed_daily_path = _parse_daily_report_path(path)
    if parsed_daily_path is not None:
        report_date, _extension = parsed_daily_path
        return report_date

    match = _DAILY_REPORT_HTML_ARTIFACT_RE.fullmatch(path.name)
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group("report_date"))
    except ValueError:
        return None


def prune_stale_daily_report_files(
    *,
    reports_dir: Path,
    as_of: str | datetime,
) -> ReportRetentionResult:
    current_report_date = parse_datetime_utc(as_of).date()
    current_date = current_report_date.isoformat()
    if not reports_dir.exists():
        return ReportRetentionResult(
            current_date=current_date,
            removed_paths=[],
            kept_current_count=0,
        )

    removed_paths: list[Path] = []
    kept_current_count = 0
    for path in sorted(reports_dir.iterdir(), key=lambda candidate: candidate.name):
        if not path.is_file():
            continue
        report_date = _parse_daily_report_retention_path(path)
        if report_date is None:
            continue
        if report_date == current_report_date:
            kept_current_count += 1
            continue
        if report_date > current_report_date:
            continue
        path.unlink(missing_ok=True)
        removed_paths.append(path)

    return ReportRetentionResult(
        current_date=current_date,
        removed_paths=removed_paths,
        kept_current_count=kept_current_count,
    )


def write_row_one_site_files(
    *,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    scoring: ScoringSettings,
    as_of: str | datetime,
    candidate_discovery: CandidateDiscoverySettings | None = None,
    entity_config: EntityConfig | None = None,
    latest_only: bool = False,
) -> RowOneRenderResult:
    reports_dir.mkdir(parents=True, exist_ok=True)
    engine = create_sqlite_engine(default_database_path(data_dir))
    try:
        initialize_schema(engine)
        as_of_utc = parse_datetime_utc(as_of)
        report = build_daily_report(
            engine,
            scoring=scoring,
            candidate_discovery=candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_utc,
        )
        window_start = as_of_utc - timedelta(days=scoring.current_window_days)
        with engine.connect() as conn:
            rows = conn.execute(
                select(
                    items_table.c.source_name,
                    items_table.c.url,
                    items_table.c.title,
                    items_table.c.summary,
                    items_table.c.collected_at,
                )
                .where(
                    items_table.c.collected_at > window_start.isoformat(),
                    items_table.c.collected_at <= as_of_utc.isoformat(),
                )
                .order_by(items_table.c.collected_at.desc())
                .limit(50)
            ).mappings()
            recent_items = [dict(row) for row in rows]
        edition = build_row_one_edition(report=report, recent_items=recent_items, as_of=as_of_utc)
        return render_row_one_site(edition, output_dir, latest_only=latest_only)
    finally:
        engine.dispose()


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
        SourceType.HTML: HtmlCollector(),
        SourceType.SITEMAP: SitemapCollector(),
        SourceType.XIAOHONGSHU: XiaohongshuCollector(),
        SourceType.INSTAGRAM: InstagramCollector(),
        SourceType.TWITTER: TwitterCollector(),
        SourceType.YOUTUBE: YouTubeCollector(),
    }
