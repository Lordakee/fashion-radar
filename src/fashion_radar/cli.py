from __future__ import annotations

from pathlib import Path

import typer

from fashion_radar.settings import load_entity_config, load_scoring_config, load_source_config
from fashion_radar.utils.paths import default_config_dir, default_data_dir, default_reports_dir

app = typer.Typer(help="Fashion Radar command line interface.")
CONFIG_DIR_OPTION = typer.Option(default_factory=default_config_dir)
DATA_DIR_OPTION = typer.Option(default_factory=default_data_dir)
REPORTS_DIR_OPTION = typer.Option(default_factory=default_reports_dir)


def _copy_template(name: str, target: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "configs" / f"{name}.example.yaml"
    destination = target / f"{name}.yaml"
    if not destination.exists():
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


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
    """Check local paths and load config files when present."""
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
    for label, (path, loader) in config_files.items():
        if path.exists():
            loader(path)
            typer.echo(f"Loaded {label}: {path}")
        else:
            typer.echo(f"Optional config not found: {path}")
