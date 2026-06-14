from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Literal

import typer
from sqlalchemy import inspect, select
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

from fashion_radar.community_candidates import (
    preview_community_candidate_directory,
    preview_community_candidates,
    render_community_candidate_directory_table,
    render_community_candidates_table,
)
from fashion_radar.community_handoff_workflow import (
    build_community_handoff_workflow,
    render_community_handoff_workflow_table,
)
from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    lint_community_signal_directory,
    lint_community_signal_file,
    render_community_signal_directory_lint_table,
    render_community_signal_lint_table,
)
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.schema import (
    SCHEMA_VERSION,
    SchemaVersionError,
    initialize_schema,
    schema_metadata,
)
from fashion_radar.db.schema import (
    metadata as db_metadata,
)
from fashion_radar.db.schema_messages import (
    FUTURE_SCHEMA_HINT,
    MIGRATE_DB_HINT,
    invalid_schema_message,
    missing_schema_message,
    unsupported_schema_message,
)
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
from fashion_radar.imported_candidate_evidence import (
    query_imported_candidate_evidence,
    render_imported_candidate_evidence_table,
)
from fashion_radar.imported_candidates import (
    query_imported_candidates,
    render_imported_candidates_table,
)
from fashion_radar.imported_entity_deltas import (
    query_imported_entity_deltas,
    render_imported_entity_deltas_table,
)
from fashion_radar.imported_review_workflow import (
    build_imported_review_workflow,
    render_imported_review_workflow_table,
)
from fashion_radar.imported_signals import (
    query_imported_signals,
    query_imported_signals_summary,
    render_imported_signals_summary_table,
    render_imported_signals_table,
)
from fashion_radar.importers.manual_signals import (
    ManualSignalDirectoryDryRunFinding,
    ManualSignalDirectoryDryRunResult,
    ManualSignalDirectoryImportResult,
    ManualSignalDryRunFindingSeverity,
    ManualSignalImportError,
    load_manual_signal_directory_rows,
    load_manual_signal_rows,
    render_manual_signal_directory_dry_run_table,
    render_manual_signal_directory_import_table,
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
CommunityCandidatesOutputFormat = Literal["table", "json"]
CommunityHandoffWorkflowOutputFormat = Literal["table", "json"]
CommunitySignalLintOutputFormat = Literal["table", "json"]
ImportSignalsDirOutputFormat = Literal["table", "json"]
ImportedCandidateEvidenceOutputFormat = Literal["table", "json"]
ImportedCandidatesOutputFormat = Literal["table", "json"]
ImportedEntityDeltasOutputFormat = Literal["table", "json"]
ImportedReviewWorkflowOutputFormat = Literal["table", "json"]
ImportedSignalsOutputFormat = Literal["table", "json"]
ImportedSignalsSummaryOutputFormat = Literal["table", "json"]
EntityPackLintOutputFormat = Literal["table", "json"]
SourcePackLintOutputFormat = Literal["table", "json"]
TrendOutputFormat = Literal["table", "json"]
CANDIDATE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
COMMUNITY_SIGNAL_LINT_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
COMMUNITY_CANDIDATES_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC community candidate preview timestamp, for example 2026-06-13T12:00:00Z.",
)
COMMUNITY_CANDIDATES_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC handoff workflow timestamp, for example 2026-06-13T12:00:00Z.",
)
COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION = typer.Option(
    "Community Tool Export",
    "--source-name",
    help="Fallback source name for rows that omit source_name.",
)
COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION = typer.Option(
    "csv",
    "--input-format",
    help="Input file format.",
)
COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION = typer.Option(
    "*.csv",
    "--pattern",
    help="Filename glob for direct child handoff files.",
)
COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION = typer.Option(
    ...,
    "--input-format",
    help="Input file format.",
)
COMMUNITY_SIGNAL_PATTERN_OPTION = typer.Option(
    ...,
    "--pattern",
    help="Non-recursive file glob pattern, for example *.csv or *.json.",
)
COMMUNITY_SIGNAL_SOURCE_NAME_OPTION = typer.Option(
    "Community Signal Import",
    "--source-name",
    help="Fallback source name for rows that omit source_name.",
)
IMPORT_SIGNALS_DIR_OUTPUT_FORMAT_OPTION = typer.Option(
    "table",
    "--output-format",
    help="Diagnostics output format.",
)
IMPORTED_CANDIDATE_EVIDENCE_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC imported candidate evidence timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_CANDIDATE_EVIDENCE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
IMPORTED_CANDIDATES_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC imported candidate review timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_CANDIDATES_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
IMPORTED_ENTITY_DELTAS_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC comparison timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_ENTITY_DELTAS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
IMPORTED_REVIEW_WORKFLOW_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC workflow timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_REVIEW_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
IMPORTED_SIGNALS_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC review timestamp, for example 2026-06-12T12:00:00Z.",
)
IMPORTED_SIGNALS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
IMPORTED_SIGNALS_SUMMARY_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
MANUAL_SIGNAL_DIR_FORMAT_OPTION = typer.Option(
    ...,
    "--format",
    help="Input file format.",
)
MANUAL_SIGNAL_PATTERN_OPTION = typer.Option(
    ...,
    "--pattern",
    help="Non-recursive file glob pattern, for example *.csv or *.json.",
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


@dataclass(frozen=True)
class _DatabaseSchemaStatus:
    state: Literal["missing", "current", "old", "future", "invalid"]
    version: int | None = None
    detail: str | None = None
    missing_schema: bool = False


def _inspect_database_schema_status(db_path: Path) -> _DatabaseSchemaStatus:
    if not db_path.exists():
        return _DatabaseSchemaStatus(state="missing")

    engine = create_readonly_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "schema_metadata" not in table_names:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="missing schema_metadata table",
                missing_schema=True,
            )

        metadata_columns = {column["name"] for column in inspector.get_columns("schema_metadata")}
        if "version" not in metadata_columns:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is missing",
            )

        try:
            with engine.connect() as connection:
                raw_version = connection.execute(
                    select(schema_metadata.c.version)
                ).scalar_one_or_none()
        except MultipleResultsFound:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version has multiple rows",
            )
        if raw_version is None:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is empty",
                missing_schema=True,
            )
        version = _parse_schema_version_value(raw_version)
        if version is None:
            return _DatabaseSchemaStatus(
                state="invalid",
                detail="schema_metadata.version is not an integer",
            )

        if version < SCHEMA_VERSION:
            return _DatabaseSchemaStatus(state="old", version=version)
        if version > SCHEMA_VERSION:
            return _DatabaseSchemaStatus(state="future", version=version)

        missing_tables = sorted(set(db_metadata.tables) - table_names)
        if missing_tables:
            return _DatabaseSchemaStatus(
                state="invalid",
                version=version,
                detail=f"missing tables: {', '.join(missing_tables)}",
            )
        for table_name, table in sorted(db_metadata.tables.items()):
            actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
            expected_columns = {column.name for column in table.columns}
            missing_columns = sorted(expected_columns - actual_columns)
            if missing_columns:
                return _DatabaseSchemaStatus(
                    state="invalid",
                    version=version,
                    detail=(f"table {table_name} missing columns: {', '.join(missing_columns)}"),
                )
        return _DatabaseSchemaStatus(state="current", version=version)
    except SQLAlchemyError as exc:
        return _DatabaseSchemaStatus(state="invalid", detail=str(exc))
    finally:
        engine.dispose()


def _parse_schema_version_value(value: object) -> int | None:
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value.strip()):
        return int(value)
    return None


def _format_database_schema_status(status: _DatabaseSchemaStatus) -> str:
    if status.state == "missing":
        return "Database schema: not initialized"
    if status.state == "current":
        return f"Database schema: v{status.version} (current)"
    if status.state == "old":
        return f"Database schema: v{status.version} (upgrade available; {MIGRATE_DB_HINT})"
    if status.state == "future":
        return (
            f"Database schema: v{status.version} "
            f"(unsupported; expected v{SCHEMA_VERSION}). {FUTURE_SCHEMA_HINT}"
        )
    detail = status.detail or "unknown schema problem"
    if status.missing_schema:
        return f"Database schema: invalid: {missing_schema_message(detail)}"
    return f"Database schema: {invalid_schema_message(detail)}"


def _parse_schema_version_from_error(message: str) -> int | None:
    match = re.search(r"Unsupported schema version ([0-9]+)", message)
    if match is None:
        return None
    return int(match.group(1))


@app.command(name="migrate-db")
def migrate_db(data_dir: Path = DATA_DIR_OPTION) -> None:
    """Initialize or upgrade the local SQLite database schema."""
    db_path = default_database_path(data_dir)
    engine = None
    try:
        engine = create_sqlite_engine(db_path)
        initialize_schema(engine)
        status = _inspect_database_schema_status(db_path)
    except SchemaVersionError as exc:
        message = str(exc)
        version = _parse_schema_version_from_error(message)
        if version is not None:
            message = unsupported_schema_message(version)
        typer.echo(f"Could not migrate database schema: {message}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Could not migrate database schema: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        if engine is not None:
            engine.dispose()

    typer.echo(f"Database path: {db_path}")
    typer.echo(_format_database_schema_status(status))
    if status.state != "current":
        raise typer.Exit(1)


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

    status = _inspect_database_schema_status(default_database_path(data_dir))
    typer.echo(_format_database_schema_status(status))
    if status.state in {"old", "future", "invalid"}:
        raise typer.Exit(1)


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


@app.command(name="community-signal-lint")
def community_signal_lint_command(
    path: Path,
    input_format: ManualSignalInputFormat = COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION,
    output_format: CommunitySignalLintOutputFormat = COMMUNITY_SIGNAL_LINT_FORMAT_OPTION,
    source_name: str = COMMUNITY_SIGNAL_SOURCE_NAME_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local community signal file without importing rows."""
    result = lint_community_signal_file(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_signal_lint_table(result):
            typer.echo(line)

    has_errors = any(
        finding.severity == CommunitySignalFindingSeverity.ERROR for finding in result.findings
    )
    has_warnings = any(
        finding.severity == CommunitySignalFindingSeverity.WARNING for finding in result.findings
    )
    if has_errors or (strict and has_warnings):
        raise typer.Exit(1)


@app.command(name="community-signal-lint-dir")
def community_signal_lint_dir_command(
    directory: Path,
    input_format: ManualSignalInputFormat = COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_SIGNAL_PATTERN_OPTION,
    output_format: CommunitySignalLintOutputFormat = COMMUNITY_SIGNAL_LINT_FORMAT_OPTION,
    source_name: str = COMMUNITY_SIGNAL_SOURCE_NAME_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint local community signal files in one directory without importing rows."""
    result = lint_community_signal_directory(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_name,
    )
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_signal_directory_lint_table(result):
            typer.echo(line)

    if result.error_count or (strict and result.warning_count):
        raise typer.Exit(1)


@app.command(name="community-candidates")
def community_candidates_command(
    path: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    as_of: str = COMMUNITY_CANDIDATES_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    output_format: CommunityCandidatesOutputFormat = COMMUNITY_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Preview candidate phrases from one local community signal file."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not preview community candidates: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid community candidate config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        preview = preview_community_candidates(
            path,
            input_format=input_format,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            default_source_name=source_name,
            limit=limit,
        )
    except ManualSignalImportError as exc:
        typer.echo(
            "Could not preview community candidates: input file could not be read or validated",
            err=True,
        )
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(
            "Could not preview community candidates: input file could not be read or validated",
            err=True,
        )
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(preview.model_dump_json(indent=2))
        return
    for line in render_community_candidates_table(preview):
        typer.echo(line)


@app.command(name="community-candidates-dir")
def community_candidates_dir_command(
    directory: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_CANDIDATES_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    output_format: CommunityCandidatesOutputFormat = COMMUNITY_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Preview candidate phrases from local community signal files in one directory."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not preview community candidates directory: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid community candidate directory config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        preview = preview_community_candidate_directory(
            directory,
            input_format=input_format,
            pattern=pattern,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            default_source_name=source_name,
            limit=limit,
        )
    except ManualSignalImportError as exc:
        typer.echo(
            "Could not preview community candidates directory: "
            "input directory could not be read or validated",
            err=True,
        )
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(
            "Could not preview community candidates directory: "
            "input directory could not be read or validated",
            err=True,
        )
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(preview.model_dump_json(indent=2))
        return
    for line in render_community_candidate_directory_table(preview):
        typer.echo(line)


@app.command(name="community-handoff-workflow")
def community_handoff_workflow_command(
    directory: str,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    output_format: CommunityHandoffWorkflowOutputFormat = (
        COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION
    ),
) -> None:
    """Print a local community handoff command checklist without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build community handoff workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_community_handoff_workflow(
            directory=Path(directory),
            config_dir=config_dir,
            data_dir=data_dir,
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build community handoff workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_community_handoff_workflow_table(workflow):
        typer.echo(line)


@app.command(name="import-signals-dir")
def import_signals_dir_command(
    directory: Path,
    data_dir: Path = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = MANUAL_SIGNAL_DIR_FORMAT_OPTION,
    pattern: str = MANUAL_SIGNAL_PATTERN_OPTION,
    imported_at: str | None = typer.Option(None, help="UTC import timestamp override."),
    dry_run: bool = typer.Option(False, help="Validate without writing rows."),
    output_format: ImportSignalsDirOutputFormat = IMPORT_SIGNALS_DIR_OUTPUT_FORMAT_OPTION,
    source_name: str = typer.Option("Manual Import", help="Fallback source name."),
) -> None:
    """Validate or import local manual signal files from one directory."""
    source_name_value = source_name.strip() or "Manual Import"
    try:
        if imported_at is not None:
            imported_at_value = parse_datetime_utc(imported_at)
        else:
            imported_at_value = datetime.now(UTC)
    except (TypeError, ValueError) as exc:
        message = f"Could not import signals directory: invalid --imported-at: {exc}"
        if output_format == "json":
            typer.echo(
                _invalid_imported_at_directory_result(
                    directory,
                    input_format=input_format,
                    pattern=pattern,
                    message=message,
                ).model_dump_json(indent=2)
            )
        else:
            typer.echo(message, err=True)
        raise typer.Exit(1) from exc

    loaded = load_manual_signal_directory_rows(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_name_value,
    )
    result = loaded.result

    if dry_run or result.error_count:
        _print_manual_signal_directory_diagnostics(result, output_format=output_format)
        if result.error_count:
            raise typer.Exit(1)
        return

    engine = create_sqlite_engine(default_database_path(data_dir))
    initialize_schema(engine)
    import_result = store_manual_signal_rows(
        engine,
        rows=loaded.rows,
        imported_at=imported_at_value,
    )
    directory_import_result = ManualSignalDirectoryImportResult(
        directory=result.directory,
        input_format=result.input_format,
        pattern=result.pattern,
        file_count=result.file_count,
        row_count=result.row_count,
        rows_imported=import_result.rows_imported,
        items_added=import_result.items_added,
        source_name_counts=result.source_name_counts,
        platform_counts=result.platform_counts,
    )
    if output_format == "json":
        typer.echo(directory_import_result.model_dump_json(indent=2))
    else:
        for line in render_manual_signal_directory_import_table(directory_import_result):
            typer.echo(line)


def _print_manual_signal_directory_diagnostics(
    result: ManualSignalDirectoryDryRunResult,
    *,
    output_format: ImportSignalsDirOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
        return
    for line in render_manual_signal_directory_dry_run_table(result):
        typer.echo(line)


def _invalid_imported_at_directory_result(
    directory: Path,
    *,
    input_format: ManualSignalInputFormat,
    pattern: str,
    message: str,
) -> ManualSignalDirectoryDryRunResult:
    return ManualSignalDirectoryDryRunResult(
        directory=str(directory),
        input_format=input_format,
        pattern=pattern,
        error_count=1,
        findings=[
            ManualSignalDirectoryDryRunFinding(
                severity=ManualSignalDryRunFindingSeverity.ERROR,
                code="invalid_imported_at",
                message=message,
            )
        ],
    )


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

    engine = create_readonly_sqlite_engine(db_path)
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


@app.command(name="imported-candidate-evidence")
def imported_candidate_evidence_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_CANDIDATE_EVIDENCE_AS_OF_OPTION,
    phrase: str = typer.Option(..., "--phrase", help="Candidate phrase to inspect."),
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    limit: int | None = typer.Option(20, min=0, help="Maximum evidence rows to print."),
    output_format: ImportedCandidateEvidenceOutputFormat = (
        IMPORTED_CANDIDATE_EVIDENCE_FORMAT_OPTION
    ),
) -> None:
    """Review retained imported rows behind one candidate phrase."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not review imported candidate evidence: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        phrase_value = phrase.strip()
        if not phrase_value:
            typer.echo(
                "Could not review imported candidate evidence: invalid --phrase: "
                "phrase must not be blank",
                err=True,
            )
            raise typer.Exit(1)
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid imported candidate evidence config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        review = query_imported_candidate_evidence(
            default_database_path(data_dir),
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            phrase=phrase_value,
            source_name=source_name,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not review imported candidate evidence: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_candidate_evidence_table(review):
        typer.echo(line)


@app.command(name="imported-candidates")
def imported_candidates_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_CANDIDATES_AS_OF_OPTION,
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    limit: int | None = typer.Option(50, min=0, help="Maximum imported candidates to print."),
    output_format: ImportedCandidatesOutputFormat = IMPORTED_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Review imported manual candidate signals from local SQLite."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not review imported candidates: invalid --as-of: {exc}", err=True)
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid imported candidates config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        review = query_imported_candidates(
            default_database_path(data_dir),
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            source_name=source_name,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not review imported candidates: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_candidates_table(review):
        typer.echo(line)


@app.command(name="imported-review-workflow")
def imported_review_workflow_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_REVIEW_WORKFLOW_AS_OF_OPTION,
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    lookback_days: int = typer.Option(7, min=1, help="Imported row review window in days."),
    current_days: int = typer.Option(7, min=1, help="Entity delta current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Entity delta baseline window in days."),
    output_format: ImportedReviewWorkflowOutputFormat = IMPORTED_REVIEW_WORKFLOW_FORMAT_OPTION,
) -> None:
    """Print a post-import review command checklist without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build imported review workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_imported_review_workflow(
            config_dir=config_dir,
            data_dir=data_dir,
            as_of=as_of_value,
            source_name=source_name,
            lookback_days=lookback_days,
            current_days=current_days,
            baseline_days=baseline_days,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build imported review workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_imported_review_workflow_table(workflow):
        typer.echo(line)


@app.command(name="imported-entity-deltas")
def imported_entity_deltas_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_ENTITY_DELTAS_AS_OF_OPTION,
    current_days: int = typer.Option(7, min=1, help="Current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Baseline window in days."),
    entity_type: str | None = typer.Option(None, help="Exact stored entity type filter."),
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    limit: int = typer.Option(50, min=0, help="Maximum entity delta rows to print."),
    output_format: ImportedEntityDeltasOutputFormat = IMPORTED_ENTITY_DELTAS_FORMAT_OPTION,
) -> None:
    """Compare imported manual entity counts across local collected-at windows."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not compare imported entity deltas: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        result = query_imported_entity_deltas(
            default_database_path(data_dir),
            as_of=as_of_value,
            current_days=current_days,
            baseline_days=baseline_days,
            entity_type=entity_type,
            source_name=source_name,
            limit=limit,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not compare imported entity deltas: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
        return
    for line in render_imported_entity_deltas_table(result):
        typer.echo(line)


@app.command(name="imported-signals-summary")
def imported_signals_summary_command(
    data_dir: Path = DATA_DIR_OPTION,
    output_format: ImportedSignalsSummaryOutputFormat = IMPORTED_SIGNALS_SUMMARY_FORMAT_OPTION,
) -> None:
    """Summarize imported manual signal source labels already stored in local SQLite."""
    try:
        summary = query_imported_signals_summary(default_database_path(data_dir))
    except Exception as exc:
        typer.echo(f"Could not summarize imported signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(summary.model_dump_json(indent=2))
        return
    for line in render_imported_signals_summary_table(summary):
        typer.echo(line)


@app.command(name="imported-signals")
def imported_signals_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_SIGNALS_AS_OF_OPTION,
    lookback_days: int = typer.Option(7, min=1, help="Review window in days."),
    limit: int | None = typer.Option(50, min=0, help="Maximum imported rows to print."),
    source_name: str | None = typer.Option(None, help="Exact imported source name filter."),
    unmatched_only: bool = typer.Option(False, help="Only show rows without stored matches."),
    output_format: ImportedSignalsOutputFormat = IMPORTED_SIGNALS_FORMAT_OPTION,
) -> None:
    """Review manual imported signals already stored in local SQLite."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not review imported signals: invalid --as-of: {exc}", err=True)
            raise typer.Exit(1) from exc

        review = query_imported_signals(
            default_database_path(data_dir),
            as_of=as_of_value,
            lookback_days=lookback_days,
            limit=limit,
            source_name=source_name,
            unmatched_only=unmatched_only,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not review imported signals: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_signals_table(review):
        typer.echo(line)


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
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    version = _read_candidate_schema_version_if_available(engine, inspector, table_names)
    if version is not None and version != SCHEMA_VERSION:
        raise RuntimeError(unsupported_schema_message(version))

    required = {"schema_metadata", "items", "item_entities"}
    missing = sorted(required - table_names)
    if missing:
        raise RuntimeError(
            missing_schema_message(
                f"Database schema is missing required tables: {', '.join(missing)}"
            )
        )
    for table_name in ("schema_metadata", "items", "item_entities"):
        table = db_metadata.tables[table_name]
        _verify_candidate_columns(
            inspector,
            table_name,
            {column.name for column in table.columns},
        )
    if version is None:
        raise RuntimeError(missing_schema_message("schema_metadata.version is empty"))


def _read_candidate_schema_version_if_available(
    engine,
    inspector,
    table_names: set[str],
) -> int | None:
    if "schema_metadata" not in table_names:
        return None
    metadata_columns = {column["name"] for column in inspector.get_columns("schema_metadata")}
    if "version" not in metadata_columns:
        raise RuntimeError(
            "Database schema table schema_metadata is missing required columns: version"
        )
    try:
        with engine.connect() as connection:
            raw_version = connection.execute(select(schema_metadata.c.version)).scalar_one_or_none()
    except MultipleResultsFound as exc:
        raise RuntimeError("schema_metadata.version has multiple rows") from exc
    if raw_version is None:
        return None
    version = _parse_schema_version_value(raw_version)
    if version is None:
        raise RuntimeError("schema_metadata.version is not an integer")
    return version


def _verify_candidate_columns(
    inspector,
    table_name: str,
    required_columns: set[str],
) -> None:
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing = sorted(required_columns - columns)
    if missing:
        raise RuntimeError(
            f"Database schema table {table_name} is missing required columns: {', '.join(missing)}"
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
