from __future__ import annotations

import importlib.util
import subprocess
import sys
from importlib import resources
from pathlib import Path

import typer

from fashion_radar.settings import (
    ConfigError,
    load_entity_config,
    load_scoring_config,
    load_source_config,
)
from fashion_radar.utils.paths import default_config_dir, default_data_dir, default_reports_dir
from fashion_radar.workflows import (
    MatchSummary,
    clean_old_data,
    collect_configured_sources,
    match_stored_items,
    write_daily_report_files,
)

app = typer.Typer(help="Fashion Radar command line interface.")
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
HOST_OPTION = typer.Option("127.0.0.1", help="Dashboard host address.")
PORT_OPTION = typer.Option(8501, min=1, max=65535, help="Dashboard port.")
AS_OF_OPTION = typer.Option(..., help="UTC report timestamp, for example 2026-06-11T12:00:00Z.")
NOW_OPTION = typer.Option(None, help="UTC collection timestamp override.")
RETENTION_DAYS_OPTION = typer.Option(30, min=1, help="Retention window in days.")


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


@app.command()
def dashboard(
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
) -> None:
    """Generate Markdown and JSON reports from the local database."""
    try:
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
    except ConfigError as exc:
        typer.echo(f"Invalid scoring config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        markdown_path, json_path = write_daily_report_files(
            data_dir=data_dir,
            reports_dir=reports_dir,
            scoring=scoring_config.scoring,
            as_of=as_of,
        )
    except Exception as exc:
        typer.echo(f"Could not generate report: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Wrote Markdown report: {markdown_path}")
    typer.echo(f"Wrote JSON report: {json_path}")


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
