from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Literal

import typer
from sqlalchemy import create_engine, inspect, select

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import SCHEMA_VERSION, initialize_schema, schema_metadata
from fashion_radar.digests import (
    DigestLatestMode,
    DigestOptions,
    DigestResult,
    package_daily_digest,
)
from fashion_radar.discovery.candidates import discover_candidates
from fashion_radar.entity_packs import (
    EntityPackFindingSeverity,
    lint_entity_pack,
    render_entity_pack_lint_table,
)
from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    load_manual_signal_rows,
    store_manual_signal_rows,
)
from fashion_radar.models.report import CandidateReport
from fashion_radar.models.trend import TrendComparison
from fashion_radar.scheduling import (
    render_cron_example,
    render_github_actions_workflow,
    render_systemd_service,
    render_systemd_timer,
    validate_hhmm,
)
from fashion_radar.settings import (
    ConfigError,
    load_entity_config,
    load_scoring_config,
    load_source_config,
)
from fashion_radar.source_packs import (
    SourcePackFindingSeverity,
    lint_source_pack,
    render_source_pack_lint_table,
)
from fashion_radar.trends import (
    build_trend_comparison,
    create_readonly_sqlite_engine,
    verify_readonly_trend_schema,
)
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.paths import default_config_dir, default_data_dir, default_reports_dir
from fashion_radar.workflows import (
    MatchSummary,
    clean_old_data,
    collect_configured_sources,
    default_database_path,
    match_stored_items,
    write_daily_report_files,
)

app = typer.Typer(
    help="Fashion Radar command line interface.",
    context_settings={"max_content_width": 120},
)
CONFIG_DIR_OPTION = typer.Option(
    default_factory=default_config_dir,
    envvar="FASHION_RADAR_CONFIG_DIR",
)
DATA_DIR_OPTION = typer.Option(
    default_factory=default_data_dir,
    envvar="FASHION_RADAR_DATA_DIR",
)
REPORTS_DIR_OPTION = typer.Option(
    default_factory=default_reports_dir,
    envvar="FASHION_RADAR_REPORTS_DIR",
)
PROJECT_DIR_OPTION = typer.Option(
    default_factory=lambda: Path.cwd(),
    help="Project working directory.",
)
HOST_OPTION = typer.Option("127.0.0.1", help="Dashboard host address.")
PORT_OPTION = typer.Option(8501, min=1, max=65535, help="Dashboard port.")
AS_OF_OPTION = typer.Option(..., help="UTC report timestamp, for example 2026-06-11T12:00:00Z.")
NOW_OPTION = typer.Option(None, help="UTC collection timestamp override.")
RETENTION_DAYS_OPTION = typer.Option(30, min=1, help="Retention window in days.")
CandidateOutputFormat = Literal["table", "json"]
ManualSignalInputFormat = Literal["csv", "json"]
EntityPackLintOutputFormat = Literal["table", "json"]
SourcePackLintOutputFormat = Literal["table", "json"]
TrendOutputFormat = Literal["table", "json"]
CANDIDATE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
ENTITY_PACK_LINT_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
SOURCE_PACK_LINT_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
TREND_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
DIGEST_LATEST_OPTION = typer.Option(
    DigestLatestMode.NONE,
    "--digest-latest",
    help="Write local latest report artifacts: none, copy, or symlink.",
)
DIGEST_INDEX_OPTION = typer.Option(
    False,
    "--digest-index/--no-digest-index",
    help="Write local reports/report-index.json.",
)
DIGEST_EML_OPTION = typer.Option(
    False,
    "--digest-eml/--no-digest-eml",
    help="Write a local .eml digest file without sending email.",
)
DIGEST_SUMMARY_OPTION = typer.Option(
    False,
    "--digest-summary/--no-digest-summary",
    help="Print a local observed digest summary.",
)
MANUAL_SIGNAL_FORMAT_OPTION = typer.Option(
    "csv",
    "--format",
    help="Input file format.",
)


def _copy_template(name: str, target: Path) -> None:
    destination = target / f"{name}.yaml"
    if not destination.exists():
        template = resources.files("fashion_radar.templates.configs").joinpath(
            f"{name}.example.yaml"
        )
        destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")


@app.command()
def init(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
) -> None:
    """Create local Fashion Radar directories and starter config files."""
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for name in ("sources", "entities", "scoring"):
        _copy_template(name, config_dir)

    typer.echo(f"Configuration directory: {config_dir}")
    typer.echo(f"Data directory: {data_dir}")
    typer.echo(f"Reports directory: {reports_dir}")


@app.command()
def doctor(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
) -> None:
    """Check local paths and required config files."""
    typer.echo(f"Configuration directory: {config_dir}")
    typer.echo(f"Data directory: {data_dir}")
    typer.echo(f"Reports directory: {reports_dir}")

    missing_dirs = [path for path in (config_dir, data_dir, reports_dir) if not path.exists()]
    if missing_dirs:
        for path in missing_dirs:
            typer.echo(f"Missing directory: {path}", err=True)
        raise typer.Exit(1)

    config_files = {
        "sources": (config_dir / "sources.yaml", load_source_config),
        "entities": (config_dir / "entities.yaml", load_entity_config),
        "scoring": (config_dir / "scoring.yaml", load_scoring_config),
    }
    missing_configs = [path for path, _loader in config_files.values() if not path.exists()]
    if missing_configs:
        for path in missing_configs:
            typer.echo(f"Missing required config: {path}", err=True)
        raise typer.Exit(1)

    for label, (path, loader) in config_files.items():
        try:
            loader(path)
            typer.echo(f"Loaded {label}: {path}")
        except ConfigError as exc:
            typer.echo(f"Invalid {label} config: {exc}", err=True)
            raise typer.Exit(1) from exc


@app.command(name="source-pack-lint")
def source_pack_lint_command(
    path: Path,
    output_format: SourcePackLintOutputFormat = SOURCE_PACK_LINT_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local source pack without collecting sources."""
    result = lint_source_pack(path)
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_source_pack_lint_table(result):
            typer.echo(line)

    has_errors = any(
        finding.severity == SourcePackFindingSeverity.ERROR for finding in result.findings
    )
    has_warnings = any(
        finding.severity == SourcePackFindingSeverity.WARNING for finding in result.findings
    )
    if has_errors or (strict and has_warnings):
        raise typer.Exit(1)


@app.command(name="entity-pack-lint")
def entity_pack_lint_command(
    path: Path,
    output_format: EntityPackLintOutputFormat = ENTITY_PACK_LINT_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local entity pack without matching, scoring, or collecting sources."""
    result = lint_entity_pack(path)
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_entity_pack_lint_table(result):
            typer.echo(line)

    has_errors = any(
        finding.severity == EntityPackFindingSeverity.ERROR for finding in result.findings
    )
    has_warnings = any(
        finding.severity == EntityPackFindingSeverity.WARNING for finding in result.findings
    )
    if has_errors or (strict and has_warnings):
        raise typer.Exit(1)


@app.command(name="schedule-example")
def schedule_example(
    mode: Literal["cron", "systemd", "github-actions"] = typer.Option(
        "cron",
        help="Snippet type to print.",
    ),
    project_dir: Path = PROJECT_DIR_OPTION,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    time: str = typer.Option("08:00", help="Daily run time in 24-hour HH:MM format."),
) -> None:
    """Print safe daily scheduling examples without installing them."""
    try:
        validate_hhmm(time)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    if mode == "cron":
        typer.echo(
            render_cron_example(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                time=time,
            )
        )
    elif mode == "systemd":
        typer.echo("# ~/.config/systemd/user/fashion-radar.service")
        typer.echo(
            render_systemd_service(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
            )
        )
        typer.echo("# ~/.config/systemd/user/fashion-radar.timer")
        typer.echo(render_systemd_timer(time=time))
    else:
        typer.echo(render_github_actions_workflow(time=time))


@app.command()
def dashboard(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    host: str = HOST_OPTION,
    port: int = PORT_OPTION,
) -> None:
    """Launch the local read-only Streamlit dashboard."""
    if importlib.util.find_spec("streamlit") is None:
        typer.echo(
            "Dashboard requires the dashboard extra. Install it with "
            '`uv sync --extra dashboard` or `pip install "fashion-radar[dashboard]"`.',
            err=True,
        )
        raise typer.Exit(1)

    app_path = Path(__file__).resolve().parent / "dashboard" / "app.py"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(port),
        "--",
        "--config-dir",
        str(config_dir),
        "--data-dir",
        str(data_dir),
        "--reports-dir",
        str(reports_dir),
    ]
    subprocess.run(command, check=True)


@app.command()
def report(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    digest_latest: DigestLatestMode = DIGEST_LATEST_OPTION,
    digest_index: bool = DIGEST_INDEX_OPTION,
    digest_eml: bool = DIGEST_EML_OPTION,
    digest_summary: bool = DIGEST_SUMMARY_OPTION,
) -> None:
    """Generate Markdown and JSON reports from the local database."""
    try:
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid report config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        markdown_path, json_path = write_daily_report_files(
            data_dir=data_dir,
            reports_dir=reports_dir,
            scoring=scoring_config.scoring,
            candidate_discovery=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of,
        )
    except Exception as exc:
        typer.echo(f"Could not generate report: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Wrote Markdown report: {markdown_path}")
    typer.echo(f"Wrote JSON report: {json_path}")
    _package_digest_or_exit(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=reports_dir,
        digest_latest=digest_latest,
        digest_index=digest_index,
        digest_eml=digest_eml,
        digest_summary=digest_summary,
    )


@app.command(name="candidates")
def candidates_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    limit: int | None = typer.Option(None, min=0, help="Maximum candidates to print."),
    output_format: CandidateOutputFormat = CANDIDATE_FORMAT_OPTION,
) -> None:
    """Print read-only untracked candidate signals from local collected items."""
    try:
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid candidate config: {exc}", err=True)
        raise typer.Exit(1) from exc

    db_path = default_database_path(data_dir)
    if not db_path.exists():
        _print_candidate_output([], output_format=output_format)
        return

    engine = create_engine(
        f"sqlite:///file:{db_path.as_posix()}?mode=ro&uri=true",
        future=True,
    )
    try:
        _verify_candidate_database_schema(engine)
        metrics = discover_candidates(
            engine,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not read candidate signals: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        engine.dispose()

    reports = [
        CandidateReport(
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
        for metric in metrics
    ]
    _print_candidate_output(reports, output_format=output_format)


@app.command(name="trends")
def trends_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(20, min=0, help="Maximum trend deltas to print."),
    output_format: TrendOutputFormat = TREND_FORMAT_OPTION,
    include_dropped: bool = typer.Option(False, help="Include signals present only in baseline."),
) -> None:
    """Compare local observed signal deltas between two scoring snapshots."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not compare trends: invalid --as-of: {exc}", err=True)
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        try:
            baseline_as_of_value = (
                parse_datetime_utc(baseline_as_of)
                if baseline_as_of is not None
                else as_of_value - timedelta(days=scoring_config.scoring.current_window_days)
            )
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not compare trends: invalid --baseline-as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        if baseline_as_of_value >= as_of_value:
            typer.echo(
                "Could not compare trends: baseline-as-of must be before as-of",
                err=True,
            )
            raise typer.Exit(1)

        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid trend config: {exc}", err=True)
        raise typer.Exit(1) from exc

    db_path = default_database_path(data_dir)
    if not db_path.exists():
        _print_trend_output(
            TrendComparison(as_of=as_of_value, baseline_as_of=baseline_as_of_value, deltas=[]),
            output_format=output_format,
        )
        return

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_readonly_trend_schema(engine)
        comparison = build_trend_comparison(
            engine,
            scoring=scoring_config.scoring,
            candidate_discovery=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            baseline_as_of=baseline_as_of_value,
            include_dropped=include_dropped,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not compare trends: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        engine.dispose()

    _print_trend_output(comparison, output_format=output_format)


@app.command(name="import-signals")
def import_signals_command(
    path: Path,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = MANUAL_SIGNAL_FORMAT_OPTION,
    source_name: str = typer.Option("Manual Import", help="Fallback source name."),
    imported_at: str | None = typer.Option(None, help="UTC import timestamp override."),
    dry_run: bool = typer.Option(False, help="Validate without writing rows."),
) -> None:
    """Import user-provided local signal rows from CSV or JSON."""
    source_name_value = source_name.strip() or "Manual Import"
    try:
        try:
            if imported_at is not None:
                imported_at_value = parse_datetime_utc(imported_at)
            else:
                imported_at_value = datetime.now(UTC)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not import signals: invalid --imported-at: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc

        rows = load_manual_signal_rows(
            path,
            input_format=input_format,
            default_source_name=source_name_value,
        )

        if dry_run:
            typer.echo(f"Validated {len(rows)} manual signal rows")
            typer.echo("Dry run: no rows imported")
            return

        engine = create_sqlite_engine(default_database_path(data_dir))
        initialize_schema(engine)
        result = store_manual_signal_rows(
            engine,
            rows=rows,
            imported_at=imported_at_value,
        )
    except ManualSignalImportError as exc:
        typer.echo(f"Could not import signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Validated {result.rows_seen} manual signal rows")
    typer.echo(f"Imported {result.rows_imported} manual signal rows")
    typer.echo(f"Items added: {result.items_added}")


@app.command()
def collect(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    now: str | None = NOW_OPTION,
) -> None:
    """Collect configured public sources into the local database."""
    try:
        source_config = load_source_config(config_dir / "sources.yaml")
        results = collect_configured_sources(
            data_dir=data_dir,
            sources=source_config.sources,
            now=now,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid source config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Collection failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    succeeded = sum(1 for result in results if result.status.status == "success")
    typer.echo(f"Collection finished: {succeeded}/{len(results)} sources succeeded")


@app.command(name="match")
def match_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
) -> None:
    """Match configured entities against stored item titles and summaries."""
    try:
        entity_config = load_entity_config(config_dir / "entities.yaml")
        summary = match_stored_items(data_dir=data_dir, entities=entity_config.entities)
    except ConfigError as exc:
        typer.echo(f"Invalid entity config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Matching failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Processed {summary.items_processed} items")
    typer.echo(f"Stored {summary.matches_stored} matches")


@app.command(name="clean-old-data")
def clean_old_data_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    retention_days: int = RETENTION_DAYS_OPTION,
    dry_run: bool = typer.Option(False, help="Report prune counts without deleting rows."),
) -> None:
    """Prune old collected items and their matcher rows."""
    try:
        result = clean_old_data(
            data_dir=data_dir,
            as_of=as_of,
            retention_days=retention_days,
            dry_run=dry_run,
        )
    except Exception as exc:
        typer.echo(f"Could not clean old data: {exc}", err=True)
        raise typer.Exit(1) from exc

    prefix = "Would prune" if result.dry_run else "Pruned"
    typer.echo(f"{prefix} {result.items_deleted} items")
    typer.echo(f"{prefix} {result.item_entities_deleted} item/entity matches")


@app.command()
def run(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    digest_latest: DigestLatestMode = DIGEST_LATEST_OPTION,
    digest_index: bool = DIGEST_INDEX_OPTION,
    digest_eml: bool = DIGEST_EML_OPTION,
    digest_summary: bool = DIGEST_SUMMARY_OPTION,
) -> None:
    """Run collect, match, and report serially."""
    try:
        source_config = load_source_config(config_dir / "sources.yaml")
        entity_config = load_entity_config(config_dir / "entities.yaml")
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        collect_configured_sources(
            data_dir=data_dir,
            sources=source_config.sources,
            now=as_of,
        )
        summary: MatchSummary = match_stored_items(
            data_dir=data_dir,
            entities=entity_config.entities,
        )
        markdown_path, json_path = write_daily_report_files(
            data_dir=data_dir,
            reports_dir=reports_dir,
            scoring=scoring_config.scoring,
            candidate_discovery=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Run failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Stored {summary.matches_stored} matches")
    typer.echo(f"Wrote Markdown report: {markdown_path}")
    typer.echo(f"Wrote JSON report: {json_path}")
    _package_digest_or_exit(
        markdown_path=markdown_path,
        json_path=json_path,
        reports_dir=reports_dir,
        digest_latest=digest_latest,
        digest_index=digest_index,
        digest_eml=digest_eml,
        digest_summary=digest_summary,
    )


def _package_digest_or_exit(
    *,
    markdown_path: Path,
    json_path: Path,
    reports_dir: Path,
    digest_latest: DigestLatestMode,
    digest_index: bool,
    digest_eml: bool,
    digest_summary: bool,
) -> None:
    options = DigestOptions(
        latest=DigestLatestMode(digest_latest),
        write_index=digest_index,
        write_eml=digest_eml,
        print_summary=digest_summary,
    )
    if options == DigestOptions():
        return
    try:
        result = package_daily_digest(
            markdown_path=markdown_path,
            json_path=json_path,
            reports_dir=reports_dir,
            options=options,
        )
    except Exception as exc:
        typer.echo(f"Could not package digest: {exc}", err=True)
        raise typer.Exit(1) from exc
    _print_digest_result(result)


def _print_digest_result(result: DigestResult) -> None:
    if result.latest_markdown_path is not None:
        typer.echo(f"Wrote latest Markdown: {result.latest_markdown_path}")
    if result.latest_json_path is not None:
        typer.echo(f"Wrote latest JSON: {result.latest_json_path}")
    if result.index_path is not None:
        typer.echo(f"Wrote report index: {result.index_path}")
    if result.eml_path is not None:
        typer.echo(f"Wrote local EML digest: {result.eml_path}")
    if result.summary_text:
        typer.echo(result.summary_text)


def _verify_candidate_database_schema(engine) -> None:
    table_names = set(inspect(engine).get_table_names())
    required = {"schema_metadata", "items", "item_entities"}
    missing = sorted(required - table_names)
    if missing:
        raise RuntimeError(f"Database schema is missing required tables: {', '.join(missing)}")
    with engine.connect() as connection:
        version = connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()
    if version != SCHEMA_VERSION:
        raise RuntimeError(
            f"Unsupported database schema version {version}; expected {SCHEMA_VERSION}"
        )


def _print_candidate_output(
    candidates: list[CandidateReport],
    *,
    output_format: CandidateOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(
            json.dumps(
                [candidate.model_dump(mode="json") for candidate in candidates],
                indent=2,
            )
        )
        return

    typer.echo(
        "Candidate signals are observed phrases from configured sources and "
        "imported local signals and need review."
    )
    if not candidates:
        typer.echo("No untracked candidate signals in this window.")
        return
    typer.echo("Phrase | Type | Label | Score | Current Mentions | Distinct Sources")
    for candidate in candidates:
        typer.echo(
            f"{candidate.phrase} | {candidate.candidate_type} | {candidate.label} | "
            f"{candidate.score:.2f} | {candidate.current_mentions} | "
            f"{candidate.distinct_sources}"
        )


def _print_trend_output(
    comparison: TrendComparison,
    *,
    output_format: TrendOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(comparison.model_dump_json(indent=2))
        return

    for line in _trend_table_lines(comparison):
        typer.echo(line)


def _trend_table_lines(comparison: TrendComparison) -> list[str]:
    lines = [
        "Local observed trend deltas need review.",
        f"As of: {comparison.as_of.isoformat()}",
        f"Baseline as of: {comparison.baseline_as_of.isoformat()}",
    ]
    if not comparison.deltas:
        lines.append("No local observed trend deltas in this comparison.")
        return lines
    lines.append(
        "Status | Kind | Type | Name | Current Score | Score Delta | "
        "Mention Delta | Current Label | Baseline Label"
    )
    for delta in comparison.deltas:
        lines.append(
            f"{delta.status.value} | {delta.signal_kind.value} | {delta.signal_type} | "
            f"{delta.name} | {delta.current_score:.2f} | {delta.score_delta:+.2f} | "
            f"{delta.mention_delta:+d} | {delta.current_label or 'n/a'} | "
            f"{delta.baseline_label or 'n/a'}"
        )
    return lines
