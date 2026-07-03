from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Literal

import typer

import fashion_radar.external_tool_readiness as external_tool_readiness_module
from fashion_radar.community_candidates import (
    preview_community_candidate_directory,
    preview_community_candidates,
    render_community_candidate_directory_table,
    render_community_candidates_table,
)
from fashion_radar.community_handoff_check import (
    check_community_handoff_directory,
    render_community_handoff_directory_check_table,
)
from fashion_radar.community_handoff_manifest import (
    build_community_handoff_manifest,
    render_community_handoff_manifest_table,
)
from fashion_radar.community_handoff_workflow import (
    build_community_handoff_workflow,
    render_community_handoff_workflow_table,
)
from fashion_radar.community_signal_profile import (
    build_community_signal_profile,
    render_community_signal_profile_table,
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
)
from fashion_radar.db.schema import (
    metadata as db_metadata,
)
from fashion_radar.db.schema_inspection import (
    DatabaseSchemaStatus,
    inspect_database_schema_status,
    parse_signed_schema_version_value,
    verify_readonly_schema,
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
from fashion_radar.external_tool_adapters import (
    DEFAULT_ADAPTER_AS_OF,
    DEFAULT_EXPORT_DIRECTORY,
    build_external_tool_adapter_registry,
    filter_external_tool_adapter_registry,
    render_external_tool_adapter_registry_table,
)
from fashion_radar.external_tool_readiness import (
    DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID,
    build_external_tool_readiness,
    render_external_tool_readiness_table,
)
from fashion_radar.external_tool_templates import (
    build_external_tool_template_collection,
    render_external_tool_template_csv,
    render_external_tool_template_json,
    render_external_tool_template_table,
)
from fashion_radar.external_tool_workflow import (
    DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID,
    build_external_tool_workflow,
    render_external_tool_workflow_table,
)
from fashion_radar.heat_movers import (
    HeatMoversReport,
    build_heat_movers,
    render_heat_movers_table,
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
from fashion_radar.imported_entity_evidence import (
    query_imported_entity_evidence,
    render_imported_entity_evidence_table,
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
from fashion_radar.row_one.ops import render_row_one_local_ops_runbook
from fashion_radar.row_one.readiness import build_row_one_readiness
from fashion_radar.row_one.server import (
    format_row_one_site_access_message,
    serve_row_one_site,
    validate_row_one_site_dir,
)
from fashion_radar.scheduling import (
    render_cron_example,
    render_github_actions_workflow,
    render_row_one_cron_example,
    render_row_one_serve_systemd_service,
    render_row_one_systemd_service,
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
from fashion_radar.source_liveness import (
    build_source_liveness_report,
    render_source_liveness_table,
    source_liveness_should_exit_nonzero,
)
from fashion_radar.source_packs import (
    SourcePackFindingSeverity,
    lint_source_pack,
    render_source_pack_lint_table,
)
from fashion_radar.trend_explanations import (
    TrendExplanationReport,
    build_trend_explanations,
    render_trend_explanations_table,
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
    prune_stale_daily_report_files,
    write_daily_report_files,
    write_row_one_site_files,
)

app = typer.Typer(
    help="Fashion Radar command line interface.",
    context_settings={"max_content_width": 120},
)
row_one_app = typer.Typer(help="ROW ONE local daily site commands.")
external_tool_readiness_shutil = external_tool_readiness_module.shutil
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
ROW_ONE_PORT_OPTION = typer.Option(8787, min=1, max=65535, help="ROW ONE site port.")
ROW_ONE_OUTPUT_DIR_OPTION = typer.Option(
    Path("reports/row-one/site"),
    help="ROW ONE generated site output directory.",
)
ROW_ONE_SITE_DIR_OPTION = typer.Option(
    Path("reports/row-one/site"),
    help="ROW ONE generated site directory.",
)
ROW_ONE_HOST_OPTION = typer.Option("127.0.0.1", help="ROW ONE site host address.")
ROW_ONE_UNIT_DIR_OPTION = typer.Option(
    default_factory=lambda: Path.home() / ".config" / "systemd" / "user",
    help="User systemd unit directory.",
)
AS_OF_OPTION = typer.Option(..., help="UTC report timestamp, for example 2026-06-11T12:00:00Z.")
NOW_OPTION = typer.Option(None, help="UTC collection timestamp override.")
RETENTION_DAYS_OPTION = typer.Option(30, min=1, help="Retention window in days.")
CandidateOutputFormat = Literal["table", "json"]
ManualSignalInputFormat = Literal["csv", "json"]
CommunityCandidatesOutputFormat = Literal["table", "json"]
CommunityHandoffCheckOutputFormat = Literal["table", "json"]
CommunityHandoffManifestOutputFormat = Literal["table", "json"]
CommunityHandoffWorkflowOutputFormat = Literal["table", "json"]
CommunitySignalLintOutputFormat = Literal["table", "json"]
CommunitySignalProfileOutputFormat = Literal["table", "json"]
ImportSignalsDirOutputFormat = Literal["table", "json"]
ImportedCandidateEvidenceOutputFormat = Literal["table", "json"]
ImportedCandidatesOutputFormat = Literal["table", "json"]
ImportedEntityDeltasOutputFormat = Literal["table", "json"]
ImportedEntityEvidenceOutputFormat = Literal["table", "json"]
ImportedReviewWorkflowOutputFormat = Literal["table", "json"]
ImportedSignalsOutputFormat = Literal["table", "json"]
ImportedSignalsSummaryOutputFormat = Literal["table", "json"]
EntityPackLintOutputFormat = Literal["table", "json"]
ExternalToolAdaptersOutputFormat = Literal["table", "json"]
ExternalToolReadinessOutputFormat = Literal["table", "json"]
ExternalToolTemplateOutputFormat = Literal["table", "json", "csv"]
ExternalToolWorkflowOutputFormat = Literal["table", "json"]
SourcePackLintOutputFormat = Literal["table", "json"]
SourceLivenessOutputFormat = Literal["table", "json"]
TrendOutputFormat = Literal["table", "json"]
TrendExplanationOutputFormat = Literal["table", "json"]
HeatMoversOutputFormat = Literal["table", "json"]
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
COMMUNITY_SIGNAL_PROFILE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
EXTERNAL_TOOL_ADAPTERS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
EXTERNAL_TOOL_READINESS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
EXTERNAL_TOOL_TEMPLATE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
EXTERNAL_TOOL_WORKFLOW_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
EXTERNAL_TOOL_WORKFLOW_ADAPTER_OPTION = typer.Option(
    DEFAULT_EXTERNAL_TOOL_WORKFLOW_ADAPTER_ID,
    "--adapter",
    help="Adapter id to print a workflow for.",
)
EXTERNAL_TOOL_WORKFLOW_DIRECTORY_OPTION = typer.Option(
    DEFAULT_EXPORT_DIRECTORY,
    "--directory",
    help="Local export directory used in printed commands only.",
)
EXTERNAL_TOOL_WORKFLOW_AS_OF_OPTION = typer.Option(
    DEFAULT_ADAPTER_AS_OF,
    "--as-of",
    help="UTC timestamp used in printed commands only.",
)
EXTERNAL_TOOL_WORKFLOW_INPUT_FORMAT_OPTION = typer.Option(
    None,
    "--input-format",
    help="Override adapter input file format.",
)
EXTERNAL_TOOL_WORKFLOW_PATTERN_OPTION = typer.Option(
    None,
    "--pattern",
    help="Override adapter handoff file glob pattern.",
)
EXTERNAL_TOOL_WORKFLOW_SOURCE_NAME_OPTION = typer.Option(
    None,
    "--source-name",
    help="Override adapter source name.",
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
COMMUNITY_HANDOFF_CHECK_FORMAT_OPTION = typer.Option(
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
IMPORTED_ENTITY_EVIDENCE_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC imported entity evidence timestamp, for example 2026-06-13T12:00:00Z.",
)
IMPORTED_ENTITY_EVIDENCE_FORMAT_OPTION = typer.Option(
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
SOURCE_LIVENESS_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
TREND_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
TREND_EXPLANATION_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
HEAT_MOVERS_FORMAT_OPTION = typer.Option(
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


def _database_required_columns_by_table() -> tuple[tuple[str, set[str]], ...]:
    return tuple(
        (table_name, {column.name for column in table.columns})
        for table_name, table in sorted(db_metadata.tables.items())
    )


def _format_database_schema_status(status: DatabaseSchemaStatus) -> str:
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
        status = inspect_database_schema_status(
            db_path,
            required_columns_by_table=_database_required_columns_by_table(),
            version_parser=parse_signed_schema_version_value,
        )
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

    status = inspect_database_schema_status(
        default_database_path(data_dir),
        required_columns_by_table=_database_required_columns_by_table(),
        version_parser=parse_signed_schema_version_value,
    )
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


@app.command(name="source-liveness")
def source_liveness_command(
    path: Path,
    output_format: SourceLivenessOutputFormat = SOURCE_LIVENESS_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Check configured source liveness with bounded network probes and no writes."""
    report = build_source_liveness_report(path)
    if output_format == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        for line in render_source_liveness_table(report):
            typer.echo(line)

    if source_liveness_should_exit_nonzero(report, strict=strict):
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


@app.command(name="community-signal-profile")
def community_signal_profile_command(
    output_format: CommunitySignalProfileOutputFormat = (COMMUNITY_SIGNAL_PROFILE_FORMAT_OPTION),
) -> None:
    """Print the local community signal producer contract."""
    profile = build_community_signal_profile()
    if output_format == "json":
        typer.echo(profile.model_dump_json(indent=2))
        return
    for line in render_community_signal_profile_table(profile):
        typer.echo(line)


@app.command(name="external-tool-adapters")
def external_tool_adapters_command(
    adapter: str | None = typer.Option(None, "--adapter", help="Adapter id to print."),
    directory: str = typer.Option(
        DEFAULT_EXPORT_DIRECTORY,
        "--directory",
        help="Suggested local export directory used in printed commands only.",
    ),
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = typer.Option(
        DEFAULT_ADAPTER_AS_OF,
        "--as-of",
        help="UTC timestamp used in printed commands only.",
    ),
    output_format: ExternalToolAdaptersOutputFormat = EXTERNAL_TOOL_ADAPTERS_FORMAT_OPTION,
) -> None:
    """Print local external tool adapter handoff guidance without running tools."""
    try:
        registry = build_external_tool_adapter_registry(
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of,
        )
        registry = filter_external_tool_adapter_registry(registry, adapter_id=adapter)
    except ValueError as exc:
        typer.echo(f"Could not build external tool adapter registry: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(registry.model_dump_json(indent=2))
        return
    for line in render_external_tool_adapter_registry_table(registry):
        typer.echo(line)


@app.command(name="external-tool-template")
def external_tool_template_command(
    adapter: str | None = typer.Option(
        None, "--adapter", help="Adapter id to print a template for."
    ),
    directory: str = typer.Option(
        DEFAULT_EXPORT_DIRECTORY,
        "--directory",
        help="Suggested local export directory used in printed commands only.",
    ),
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = typer.Option(
        DEFAULT_ADAPTER_AS_OF,
        "--as-of",
        help="UTC timestamp used in template rows and printed commands only.",
    ),
    output_format: ExternalToolTemplateOutputFormat = EXTERNAL_TOOL_TEMPLATE_FORMAT_OPTION,
) -> None:
    """Print local adapter handoff template rows without writing files."""
    try:
        template = build_external_tool_template_collection(
            adapter_id=adapter,
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of,
        )
    except ValueError as exc:
        typer.echo(f"Could not build external tool template: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(render_external_tool_template_json(template), nl=False)
        return
    if output_format == "csv":
        typer.echo(render_external_tool_template_csv(template), nl=False)
        return
    for line in render_external_tool_template_table(template):
        typer.echo(line)


@app.command(name="external-tool-workflow")
def external_tool_workflow_command(
    adapter: str = EXTERNAL_TOOL_WORKFLOW_ADAPTER_OPTION,
    directory: str = EXTERNAL_TOOL_WORKFLOW_DIRECTORY_OPTION,
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = EXTERNAL_TOOL_WORKFLOW_AS_OF_OPTION,
    input_format: ManualSignalInputFormat | None = EXTERNAL_TOOL_WORKFLOW_INPUT_FORMAT_OPTION,
    pattern: str | None = EXTERNAL_TOOL_WORKFLOW_PATTERN_OPTION,
    source_name: str | None = EXTERNAL_TOOL_WORKFLOW_SOURCE_NAME_OPTION,
    output_format: ExternalToolWorkflowOutputFormat = EXTERNAL_TOOL_WORKFLOW_FORMAT_OPTION,
) -> None:
    """Print local external tool workflow commands without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build external tool workflow: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        workflow = build_external_tool_workflow(
            adapter_id=adapter,
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of_value,
            input_format=input_format,
            pattern=pattern,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build external tool workflow: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(workflow.model_dump_json(indent=2))
        return
    for line in render_external_tool_workflow_table(workflow):
        typer.echo(line)


@app.command(name="external-tool-readiness")
def external_tool_readiness_command(
    adapter: str = typer.Option(
        DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID,
        "--adapter",
        help="Adapter id to check.",
    ),
    directory: str = EXTERNAL_TOOL_WORKFLOW_DIRECTORY_OPTION,
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = EXTERNAL_TOOL_WORKFLOW_AS_OF_OPTION,
    input_format: ManualSignalInputFormat | None = EXTERNAL_TOOL_WORKFLOW_INPUT_FORMAT_OPTION,
    pattern: str | None = EXTERNAL_TOOL_WORKFLOW_PATTERN_OPTION,
    source_name: str | None = EXTERNAL_TOOL_WORKFLOW_SOURCE_NAME_OPTION,
    output_format: ExternalToolReadinessOutputFormat = EXTERNAL_TOOL_READINESS_FORMAT_OPTION,
) -> None:
    """Print local external tool readiness guidance without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build external tool readiness: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        readiness = build_external_tool_readiness(
            adapter_id=adapter,
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of_value,
            input_format=input_format,
            pattern=pattern,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build external tool readiness: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(readiness.model_dump_json(indent=2))
        return
    for line in render_external_tool_readiness_table(readiness):
        typer.echo(line)


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


@app.command(name="community-handoff-check-dir")
def community_handoff_check_dir_command(
    directory: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
    output_format: CommunityHandoffCheckOutputFormat = COMMUNITY_HANDOFF_CHECK_FORMAT_OPTION,
) -> None:
    """Check a local community handoff directory without importing rows."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not check community handoff directory: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
        result = check_community_handoff_directory(
            directory,
            config_dir=config_dir,
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            source_name=source_name,
            strict=strict,
            limit=limit,
        )
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid community handoff check config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"Could not check community handoff directory: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(result.model_dump_json(indent=2))
    else:
        for line in render_community_handoff_directory_check_table(result):
            typer.echo(line)
    if not result.ok:
        raise typer.Exit(1)


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


@app.command(name="community-handoff-manifest")
def community_handoff_manifest_command(
    directory: str,
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_HANDOFF_WORKFLOW_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    output_format: CommunityHandoffManifestOutputFormat = (
        COMMUNITY_HANDOFF_WORKFLOW_FORMAT_OPTION
    ),
) -> None:
    """Print a local community handoff producer manifest without executing commands."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not build community handoff manifest: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        manifest = build_community_handoff_manifest(
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            input_format=input_format,
            pattern=pattern,
            as_of=as_of_value,
            source_name=source_name,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"Could not build community handoff manifest: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(manifest.model_dump_json(indent=2))
        return
    for line in render_community_handoff_manifest_table(manifest):
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


@row_one_app.command(name="build")
def row_one_build(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    latest_only: bool = typer.Option(
        False,
        help="Remove known ROW ONE generated children before writing the site.",
    ),
) -> None:
    """Build the local ROW ONE static daily site."""
    try:
        result = _write_row_one_site_from_cli_options(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            as_of=as_of,
            latest_only=latest_only,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"ROW ONE build failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Wrote ROW ONE site: {result.index_path}")
    typer.echo(f"Wrote {result.story_count} stories")


@row_one_app.command(name="preview")
def row_one_preview(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    latest_only: bool = typer.Option(
        False,
        help="Remove known ROW ONE generated children before writing the site.",
    ),
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    dry_run_serve_url: bool = typer.Option(
        False,
        help="Print the local ROW ONE serve URL without starting a server.",
    ),
) -> None:
    """Build a ROW ONE preview and print readiness details."""
    try:
        result = _write_row_one_site_from_cli_options(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            as_of=as_of,
            latest_only=latest_only,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"ROW ONE preview failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    readiness = build_row_one_readiness(result.edition)
    typer.echo("ROW ONE preview")
    typer.echo(f"Site: {result.index_path}")
    typer.echo(f"JSON: {result.output_dir / 'data' / 'edition.json'}")
    typer.echo(f"Manifest: {result.output_dir / 'data' / 'manifest.json'}")
    typer.echo(f"Runtime: {result.output_dir / 'data' / 'runtime.json'}")
    typer.echo(f"Stories: {readiness.story_count}")
    typer.echo(f"Sections: {readiness.section_count}")
    typer.echo(f"Evidence links: {readiness.safe_evidence_count}")
    typer.echo(f"Empty sections: {readiness.empty_sections.en}")
    typer.echo(f"Generated at: {readiness.generated_at}")
    typer.echo(f"Readiness: {readiness.readiness.en}")
    if dry_run_serve_url:
        typer.echo(format_row_one_site_access_message(host, port))


@row_one_app.command(name="refresh")
def row_one_refresh(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
) -> None:
    """Refresh ROW ONE by collecting, matching, reporting, and rebuilding the site."""
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
        site_result = _write_row_one_site_from_cli_options(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            as_of=as_of,
            latest_only=True,
        )
        report_retention = prune_stale_daily_report_files(
            reports_dir=reports_dir,
            as_of=as_of,
        )
    except ConfigError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"ROW ONE refresh failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    readiness = build_row_one_readiness(site_result.edition)
    typer.echo("ROW ONE refresh")
    typer.echo(f"Stored matches: {summary.matches_stored}")
    typer.echo(f"Markdown report: {markdown_path}")
    typer.echo(f"JSON report: {json_path}")
    typer.echo(f"HTML report: {markdown_path.with_suffix('.html')}")
    typer.echo(
        "Latest-only reports: "
        f"removed {report_retention.removed_count} stale files for "
        f"{report_retention.current_date}; "
        f"kept {report_retention.kept_current_count} current files"
    )
    typer.echo(f"Site: {site_result.index_path}")
    typer.echo(f"JSON: {site_result.output_dir / 'data' / 'edition.json'}")
    typer.echo(f"Manifest: {site_result.output_dir / 'data' / 'manifest.json'}")
    typer.echo(f"Stories: {readiness.story_count}")
    typer.echo(f"Evidence links: {readiness.safe_evidence_count}")
    typer.echo(f"Readiness: {readiness.readiness.en}")
    typer.echo(format_row_one_site_access_message(host, port))


def _write_row_one_site_from_cli_options(
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    as_of: str,
    latest_only: bool,
):
    scoring_config = load_scoring_config(config_dir / "scoring.yaml")
    entity_config = None
    entity_config_path = config_dir / "entities.yaml"
    if entity_config_path.exists():
        entity_config = load_entity_config(entity_config_path)
    return write_row_one_site_files(
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        scoring=scoring_config.scoring,
        candidate_discovery=scoring_config.candidate_discovery,
        entity_config=entity_config,
        as_of=as_of,
        latest_only=latest_only,
    )


@row_one_app.command(name="serve")
def row_one_serve(
    site_dir: Path = ROW_ONE_SITE_DIR_OPTION,
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    dry_run: bool = typer.Option(False, help="Print the site URL without serving."),
) -> None:
    """Serve a generated ROW ONE site locally."""
    access_message = format_row_one_site_access_message(host, port)
    try:
        if dry_run:
            validate_row_one_site_dir(site_dir)
            typer.echo(access_message)
            return
        typer.echo("Serving ROW ONE site")
        typer.echo(access_message)
        serve_row_one_site(site_dir=site_dir, host=host, port=port)
    except Exception as exc:
        typer.echo(f"Could not serve ROW ONE site: {exc}", err=True)
        raise typer.Exit(1) from exc


def _read_row_one_json_file(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _require_row_one_object(
    payload: dict[str, object],
    key: str,
    *,
    label: str | None = None,
) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"row-one {label or key} must be a JSON object")
    return value


def _require_row_one_value(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise ValueError(f"row-one {label} expected {expected!r}, got {actual!r}")


def _validate_row_one_story_directory(edition: dict[str, object]) -> None:
    stories = edition.get("stories")
    if not isinstance(stories, list):
        raise ValueError("row-one edition.stories must be a JSON array")
    story_directory = _require_row_one_object(
        edition,
        "story_directory",
        label="edition.story_directory",
    )
    story_count = len(stories)
    _require_row_one_value(
        "edition.story_directory.story_count",
        story_directory.get("story_count"),
        story_count,
    )
    story_ids = story_directory.get("story_ids")
    expected_story_ids: list[object] = []
    story_by_id: dict[object, dict[str, object]] = {}
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            raise ValueError(f"row-one edition.stories[{index}] must be a JSON object")
        story_id = story.get("id")
        expected_story_ids.append(story_id)
        story_by_id[story_id] = story
    _require_row_one_value(
        "edition.story_directory.story_ids",
        story_ids,
        expected_story_ids,
    )

    routes = story_directory.get("routes")
    if not isinstance(routes, list):
        raise ValueError("row-one edition.story_directory.routes must be a JSON array")
    _require_row_one_value(
        "edition.story_directory.routes length",
        len(routes),
        story_count,
    )
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            raise ValueError(
                f"row-one edition.story_directory.routes[{index}] must be a JSON object"
            )
        story_id = route.get("story_id")
        story = story_by_id.get(story_id)
        if story is None:
            raise ValueError(
                f"row-one edition.story_directory.routes[{index}].story_id "
                f"does not match an edition story"
            )
        section = story.get("section")
        if not isinstance(section, dict):
            raise ValueError(f"row-one edition.stories[{index}].section must be a JSON object")
        for key, expected in (
            ("detail_href", story.get("detail_href")),
            ("section_key", story.get("section_key")),
            ("section_href", section.get("href")),
            ("published_date", story.get("published_date")),
        ):
            _require_row_one_value(
                f"edition.story_directory.routes[{index}].{key}",
                route.get(key),
                expected,
            )


def _validate_row_one_status_payloads(
    *,
    manifest: dict[str, object],
    edition: dict[str, object],
    runtime: dict[str, object],
) -> None:
    _require_row_one_value(
        "runtime contract_version",
        runtime.get("contract_version"),
        "row-one-runtime/v1",
    )
    _require_row_one_value("runtime brand", runtime.get("brand"), "ROW ONE")
    _require_row_one_value(
        "runtime schema path",
        runtime.get("runtime_schema_path"),
        "schemas/row-one-runtime.schema.json",
    )
    _require_row_one_value(
        "manifest contract_version",
        manifest.get("contract_version"),
        "row-one-manifest/v1",
    )
    _require_row_one_value(
        "edition contract_version",
        edition.get("contract_version"),
        "row-one-app/v4",
    )
    manifest_app_contract = _require_row_one_object(
        manifest,
        "app_contract",
        label="manifest.app_contract",
    )
    _require_row_one_value(
        "manifest.app_contract.version",
        manifest_app_contract.get("version"),
        "row-one-app/v4",
    )
    _require_row_one_value(
        "manifest.app_contract.path",
        manifest_app_contract.get("path"),
        "data/edition.json",
    )
    _require_row_one_value(
        "manifest.app_contract.schema_path",
        manifest_app_contract.get("schema_path"),
        "schemas/row-one-app.schema.json",
    )

    site = _require_row_one_object(runtime, "site", label="runtime.site")
    for key, expected in (
        ("index_path", "index.html"),
        ("edition_path", "data/edition.json"),
        ("manifest_path", "data/manifest.json"),
        ("runtime_path", "data/runtime.json"),
    ):
        _require_row_one_value(f"runtime.site.{key}", site.get(key), expected)

    refresh = _require_row_one_object(runtime, "refresh", label="runtime.refresh")
    _require_row_one_value(
        "runtime.refresh.recommended_time",
        refresh.get("recommended_time"),
        "04:00",
    )
    _require_row_one_value(
        "runtime.refresh.latest_only_cleanup",
        refresh.get("latest_only_cleanup"),
        True,
    )
    refresh_command = refresh.get("command")
    if (
        not isinstance(refresh_command, str)
        or "fashion-radar row-one refresh" not in refresh_command
    ):
        raise ValueError("row-one runtime.refresh.command must run fashion-radar row-one refresh")

    serve = _require_row_one_object(runtime, "serve", label="runtime.serve")
    _require_row_one_value(
        "runtime.serve.default_host",
        serve.get("default_host"),
        "127.0.0.1",
    )
    _require_row_one_value("runtime.serve.default_port", serve.get("default_port"), 8787)
    _require_row_one_value(
        "runtime.serve.local_url",
        serve.get("local_url"),
        "http://127.0.0.1:8787",
    )
    _require_row_one_value(
        "runtime.serve.lan_url_hint",
        serve.get("lan_url_hint"),
        "http://<LAN-IP>:8787",
    )

    for key in ("generated_at", "edition_date"):
        runtime_value = runtime.get(key)
        _require_row_one_value(f"runtime {key}", runtime_value, edition.get(key))
        _require_row_one_value(f"manifest {key}", manifest.get(key), edition.get(key))

    runtime_counts = _require_row_one_object(runtime, "counts", label="runtime.counts")
    manifest_counts = _require_row_one_object(manifest, "counts", label="manifest.counts")
    _require_row_one_value("runtime counts", runtime_counts, manifest_counts)
    sections = edition.get("sections")
    if not isinstance(sections, list):
        raise ValueError("row-one edition.sections must be a JSON array")
    for key, expected in (
        ("story_count", edition.get("story_count")),
        ("section_count", len(sections)),
        ("evidence_count", edition.get("evidence_count")),
    ):
        _require_row_one_value(f"runtime.counts.{key}", runtime_counts.get(key), expected)

    runtime_readiness = _require_row_one_object(runtime, "readiness", label="runtime.readiness")
    manifest_readiness = _require_row_one_object(
        manifest,
        "readiness",
        label="manifest.readiness",
    )
    expected_status = "ready" if runtime_counts.get("story_count") else "empty"
    _require_row_one_value(
        "runtime.readiness.status",
        runtime_readiness.get("status"),
        expected_status,
    )
    _require_row_one_value(
        "runtime.readiness.status",
        runtime_readiness.get("status"),
        manifest_readiness.get("status"),
    )
    _require_row_one_value(
        "runtime.readiness.en",
        runtime_readiness.get("en"),
        runtime_readiness.get("status"),
    )
    if not isinstance(runtime_readiness.get("zh"), str) or not runtime_readiness.get("zh"):
        raise ValueError("row-one runtime.readiness.zh must be a non-empty string")
    _validate_row_one_story_directory(edition)


def _build_row_one_status_payload(
    *,
    site_dir: Path,
    host: str,
    port: int,
    manifest: dict[str, object],
    edition: dict[str, object],
    runtime: dict[str, object],
) -> dict[str, object]:
    site = _require_row_one_object(runtime, "site", label="runtime.site")
    counts = _require_row_one_object(runtime, "counts", label="runtime.counts")
    readiness = _require_row_one_object(runtime, "readiness", label="runtime.readiness")
    refresh = _require_row_one_object(runtime, "refresh", label="runtime.refresh")
    serve = _require_row_one_object(runtime, "serve", label="runtime.serve")
    story_count = counts.get("story_count")
    return {
        "ok": True,
        "site_dir": str(site_dir),
        "access": format_row_one_site_access_message(host, port),
        "paths": {
            "manifest": "data/manifest.json",
            "edition": "data/edition.json",
            "runtime": "data/runtime.json",
        },
        "manifest": manifest,
        "runtime": runtime,
        "site": site,
        "serve": serve,
        "refresh": refresh,
        "contracts": {
            "app": edition.get("contract_version"),
            "manifest": manifest.get("contract_version"),
            "runtime": runtime.get("contract_version"),
        },
        "counts": counts,
        "readiness": readiness,
        "story_count": story_count,
        "section_count": counts.get("section_count"),
        "evidence_count": counts.get("evidence_count"),
        "readiness_status": readiness.get("status"),
        "refresh_time": refresh.get("recommended_time"),
        "generated_at": runtime.get("generated_at"),
        "edition_date": runtime.get("edition_date"),
        "index_path": site.get("index_path"),
        "edition_path": site.get("edition_path"),
        "manifest_path": site.get("manifest_path"),
        "runtime_path": site.get("runtime_path"),
        "local_url": serve.get("local_url"),
        "lan_url_hint": serve.get("lan_url_hint"),
    }


@row_one_app.command(name="status")
def row_one_status(
    site_dir: Path = ROW_ONE_SITE_DIR_OPTION,
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print machine-readable JSON status.",
    ),
) -> None:
    """Validate a generated ROW ONE site and print runtime readiness."""
    try:
        validate_row_one_site_dir(site_dir)
        manifest = _read_row_one_json_file(site_dir / "data" / "manifest.json")
        edition = _read_row_one_json_file(site_dir / "data" / "edition.json")
        runtime = _read_row_one_json_file(site_dir / "data" / "runtime.json")
        _validate_row_one_status_payloads(
            manifest=manifest,
            edition=edition,
            runtime=runtime,
        )
    except Exception as exc:
        typer.echo(f"ROW ONE status failed: {exc}", err=True)
        raise typer.Exit(1) from exc

    payload = _build_row_one_status_payload(
        site_dir=site_dir,
        host=host,
        port=port,
        manifest=manifest,
        edition=edition,
        runtime=runtime,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    readiness = runtime.get("readiness")
    readiness_label = readiness.get("en", "unknown") if isinstance(readiness, dict) else "unknown"
    typer.echo("ROW ONE status")
    typer.echo(f"Site: {site_dir}")
    typer.echo(f"Runtime: {site_dir / 'data' / 'runtime.json'}")
    typer.echo(f"JSON: {site_dir / 'data' / 'edition.json'}")
    typer.echo(f"Manifest: {site_dir / 'data' / 'manifest.json'}")
    typer.echo(f"Stories: {payload['story_count']}")
    counts = runtime.get("counts")
    if isinstance(counts, dict):
        typer.echo(f"Sections: {counts.get('section_count', 'unknown')}")
        typer.echo(f"Evidence links: {counts.get('evidence_count', 'unknown')}")
    refresh = runtime.get("refresh")
    if isinstance(refresh, dict):
        typer.echo(f"Refresh time: {refresh.get('recommended_time', 'unknown')}")
    typer.echo(f"Generated at: {runtime.get('generated_at', 'unknown')}")
    typer.echo(f"Readiness: {readiness_label}")
    typer.echo(payload["access"])


@row_one_app.command(name="local-ops")
def row_one_local_ops(
    project_dir: Path = PROJECT_DIR_OPTION,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    time: str = typer.Option(
        "04:00",
        help="Daily ROW ONE refresh time in 24-hour HH:MM format.",
    ),
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
) -> None:
    """Print ROW ONE local daily ops runbook without installing anything."""
    try:
        typer.echo(
            render_row_one_local_ops_runbook(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                output_dir=str(output_dir),
                time=time,
                host=host,
                port=port,
            )
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _row_one_systemd_unit_payloads(
    *,
    project_dir: Path,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    time: str,
    host: str,
    port: int,
) -> dict[str, str]:
    validate_hhmm(time)
    return {
        "row-one-refresh.service": render_row_one_systemd_service(
            project_dir=str(project_dir),
            config_dir=str(config_dir),
            data_dir=str(data_dir),
            reports_dir=str(reports_dir),
            output_dir=str(output_dir),
        ),
        "row-one-refresh.timer": render_systemd_timer(time=time),
        "row-one-serve.service": render_row_one_serve_systemd_service(
            project_dir=str(project_dir),
            site_dir=str(output_dir),
            host=host,
            port=port,
        ),
    }


def _render_row_one_install_summary(
    *,
    unit_payloads: dict[str, str],
    host: str,
    port: int,
    dry_run: bool,
    unit_dir: Path,
    output_dir: Path,
) -> str:
    heading = "ROW ONE local install dry run" if dry_run else "ROW ONE local install"
    lines = [heading, f"Target unit directory: {unit_dir}"]
    for name, payload in unit_payloads.items():
        lines.append("")
        lines.append(f"# {_format_row_one_unit_path(unit_dir / name)}")
        lines.append(payload.rstrip())
    if not dry_run:
        lines.append("")
        lines.append(f"Wrote units to: {unit_dir}")
    lines.extend(
        [
            "",
            "Before enabling on a fresh install, generate the site once:",
            'AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"',
            (f'uv run fashion-radar row-one refresh --as-of "$AS_OF" --output-dir "{output_dir}"'),
            "",
            "Enable:",
            "systemctl --user daemon-reload",
            "systemctl --user enable --now row-one-refresh.timer",
            "systemctl --user enable --now row-one-serve.service",
            "",
            "Access:",
            format_row_one_site_access_message(host, port),
        ]
    )
    return "\n".join(lines) + "\n"


def _format_row_one_unit_path(path: Path) -> str:
    default_unit_dir = Path.home() / ".config" / "systemd" / "user"
    try:
        relative = path.relative_to(default_unit_dir)
    except ValueError:
        return str(path)
    return str(Path("~/.config/systemd/user") / relative)


def _write_row_one_systemd_units(
    *,
    unit_payloads: dict[str, str],
    unit_dir: Path,
    force: bool,
) -> None:
    existing = [unit_dir / name for name in unit_payloads if (unit_dir / name).exists()]
    if existing and not force:
        formatted = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"ROW ONE systemd unit already exists: {formatted}. Use --force.")
    unit_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in unit_payloads.items():
        (unit_dir / name).write_text(payload, encoding="utf-8")


@row_one_app.command(name="install-local")
def row_one_install_local(
    project_dir: Path = PROJECT_DIR_OPTION,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    time: str = typer.Option(
        "04:00",
        help="Daily ROW ONE refresh time in 24-hour HH:MM format.",
    ),
    host: str = ROW_ONE_HOST_OPTION,
    port: int = ROW_ONE_PORT_OPTION,
    dry_run: bool = typer.Option(
        False,
        help="Print the user systemd units without writing files.",
    ),
    unit_dir: Path = ROW_ONE_UNIT_DIR_OPTION,
    force: bool = typer.Option(False, help="Overwrite existing ROW ONE systemd units."),
) -> None:
    """Render or install ROW ONE user systemd units for local daily service."""
    try:
        unit_payloads = _row_one_systemd_unit_payloads(
            project_dir=project_dir,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            time=time,
            host=host,
            port=port,
        )
        if not dry_run:
            _write_row_one_systemd_units(
                unit_payloads=unit_payloads,
                unit_dir=unit_dir,
                force=force,
            )
        typer.echo(
            _render_row_one_install_summary(
                unit_payloads=unit_payloads,
                host=host,
                port=port,
                dry_run=dry_run,
                unit_dir=unit_dir,
                output_dir=output_dir,
            )
        )
    except (FileExistsError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    except Exception as exc:
        typer.echo(f"ROW ONE local install failed: {exc}", err=True)
        raise typer.Exit(1) from exc


@row_one_app.command(name="schedule")
def row_one_schedule(
    mode: Literal["cron", "systemd"] = typer.Option(
        "cron",
        help="Snippet type to print.",
    ),
    project_dir: Path = PROJECT_DIR_OPTION,
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    reports_dir: Path = REPORTS_DIR_OPTION,
    output_dir: Path = ROW_ONE_OUTPUT_DIR_OPTION,
    time: str = typer.Option("04:00", help="Daily run time in 24-hour HH:MM format."),
) -> None:
    """Print ROW ONE daily scheduling examples without installing them."""
    try:
        validate_hhmm(time)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    if mode == "cron":
        typer.echo(
            render_row_one_cron_example(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                output_dir=str(output_dir),
                time=time,
            )
        )
    else:
        typer.echo("# ~/.config/systemd/user/row-one.service")
        typer.echo(
            render_row_one_systemd_service(
                project_dir=str(project_dir),
                config_dir=str(config_dir),
                data_dir=str(data_dir),
                reports_dir=str(reports_dir),
                output_dir=str(output_dir),
            )
        )
        typer.echo("# ~/.config/systemd/user/row-one.timer")
        typer.echo(render_systemd_timer(time=time))


app.add_typer(row_one_app, name="row-one")


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
    """Generate Markdown, JSON, and companion HTML reports from the local database."""
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
    typer.echo(f"Wrote HTML report: {markdown_path.with_suffix('.html')}")
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
            weighted_mention_component=metric.weighted_mention_component,
            growth_component=metric.growth_component,
            source_diversity_component=metric.source_diversity_component,
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


@app.command(name="trend-explanations")
def trend_explanations_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(20, min=0, help="Maximum explanations to print."),
    output_format: TrendExplanationOutputFormat = TREND_EXPLANATION_FORMAT_OPTION,
    include_dropped: bool = typer.Option(False, help="Include signals present only in baseline."),
) -> None:
    """Explain local observed trend deltas."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not explain trend deltas: invalid --as-of: {exc}",
                err=True,
            )
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
                f"Could not explain trend deltas: invalid --baseline-as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        if baseline_as_of_value >= as_of_value:
            typer.echo(
                "Could not explain trend deltas: baseline-as-of must be before as-of",
                err=True,
            )
            raise typer.Exit(1)

        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid trend explanation config: {exc}", err=True)
        raise typer.Exit(1) from exc

    db_path = default_database_path(data_dir)
    if not db_path.exists():
        report = build_trend_explanations(
            TrendComparison(as_of=as_of_value, baseline_as_of=baseline_as_of_value, deltas=[]),
            limit=limit,
        )
        _print_trend_explanation_output(report, output_format=output_format)
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
            limit=None,
        )
        report = build_trend_explanations(comparison, limit=limit)
    except Exception as exc:
        typer.echo(f"Could not explain trend deltas: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        engine.dispose()

    _print_trend_explanation_output(report, output_format=output_format)


@app.command(name="heat-movers")
def heat_movers_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(5, min=0, help="Maximum rows per heat mover group."),
    output_format: HeatMoversOutputFormat = HEAT_MOVERS_FORMAT_OPTION,
    include_cooling: bool = typer.Option(False, help="Include a cooling watchlist group."),
) -> None:
    """Review local observed new and rising heat movers."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(f"Could not review heat movers: invalid --as-of: {exc}", err=True)
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
                f"Could not review heat movers: invalid --baseline-as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        if baseline_as_of_value >= as_of_value:
            typer.echo(
                "Could not review heat movers: baseline-as-of must be before as-of",
                err=True,
            )
            raise typer.Exit(1)

        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid heat movers config: {exc}", err=True)
        raise typer.Exit(1) from exc

    db_path = default_database_path(data_dir)
    if not db_path.exists():
        report = build_heat_movers(
            TrendComparison(as_of=as_of_value, baseline_as_of=baseline_as_of_value, deltas=[]),
            limit_per_group=limit,
            include_cooling=include_cooling,
        )
        _print_heat_movers_output(report, output_format=output_format)
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
            include_dropped=False,
            limit=None,
        )
        report = build_heat_movers(
            comparison,
            limit_per_group=limit,
            include_cooling=include_cooling,
        )
    except Exception as exc:
        typer.echo(f"Could not review heat movers: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        engine.dispose()

    _print_heat_movers_output(report, output_format=output_format)


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


@app.command(name="imported-entity-evidence")
def imported_entity_evidence_command(
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = IMPORTED_ENTITY_EVIDENCE_AS_OF_OPTION,
    entity_name: str = typer.Option(..., "--entity-name", help="Matched entity name to inspect."),
    entity_type: str = typer.Option(..., "--entity-type", help="Matched entity type to inspect."),
    source_name: str | None = typer.Option(None, help="Exact stored source name filter."),
    current_days: int = typer.Option(7, min=1, help="Current window in days."),
    baseline_days: int = typer.Option(7, min=1, help="Baseline window in days."),
    limit: int | None = typer.Option(20, min=0, help="Maximum evidence rows to print."),
    output_format: ImportedEntityEvidenceOutputFormat = IMPORTED_ENTITY_EVIDENCE_FORMAT_OPTION,
) -> None:
    """Review retained imported rows behind one matched entity."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not review imported entity evidence: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        entity_name_value = entity_name.strip()
        if not entity_name_value:
            typer.echo(
                "Could not review imported entity evidence: invalid --entity-name: "
                "entity name must not be blank",
                err=True,
            )
            raise typer.Exit(1)
        entity_type_value = entity_type.strip()
        if not entity_type_value:
            typer.echo(
                "Could not review imported entity evidence: invalid --entity-type: "
                "entity type must not be blank",
                err=True,
            )
            raise typer.Exit(1)
    except typer.Exit:
        raise

    try:
        review = query_imported_entity_evidence(
            default_database_path(data_dir),
            as_of=as_of_value,
            entity_name=entity_name_value,
            entity_type=entity_type_value,
            current_days=current_days,
            baseline_days=baseline_days,
            source_name=source_name,
            limit=limit,
        )
    except Exception as exc:
        typer.echo(f"Could not review imported entity evidence: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(review.model_dump_json(indent=2))
        return
    for line in render_imported_entity_evidence_table(review):
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
    typer.echo(f"Wrote HTML report: {markdown_path.with_suffix('.html')}")
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
    verify_readonly_schema(
        engine,
        required_tables=("schema_metadata", "items", "item_entities"),
        required_columns_by_table=tuple(
            (
                table_name,
                {column.name for column in db_metadata.tables[table_name].columns},
            )
            for table_name in ("schema_metadata", "items", "item_entities")
        ),
        version_parser=parse_signed_schema_version_value,
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


def _print_trend_explanation_output(
    report: TrendExplanationReport,
    *,
    output_format: TrendExplanationOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(report.model_dump_json(indent=2))
        return

    for line in render_trend_explanations_table(report):
        typer.echo(line)


def _print_heat_movers_output(
    report: HeatMoversReport,
    *,
    output_format: HeatMoversOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(report.model_dump_json(indent=2))
        return

    for line in render_heat_movers_table(report):
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
