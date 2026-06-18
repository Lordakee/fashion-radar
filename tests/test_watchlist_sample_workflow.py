from __future__ import annotations

import json
from pathlib import Path
from shutil import copyfile

from typer.testing import CliRunner

from fashion_radar.cli import app

ROOT = Path(__file__).resolve().parents[1]
WATCHLIST_SAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_PACK = ROOT / "configs" / "entity-packs" / "fashion-watchlist.example.yaml"
SCORING_EXAMPLE = ROOT / "configs" / "scoring.example.yaml"
AS_OF = "2026-06-13T12:00:00Z"
BASELINE_AS_OF = "2026-06-06T12:00:00Z"

EXPECTED_REPORT_ENTITIES = {
    "Khaite",
    "Khaite Lotus Bag",
    "Loewe",
    "Loewe Puzzle Bag",
    "Jonathan Anderson",
    "Bella Hadid",
    "Alaia Le Teckel",
    "Miu Miu Arcadie",
    "Mary Jane Shoes",
    "Boho Revival",
}


def invoke_ok(args: list[str]) -> str:
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    return result.output


def prepare_watchlist_config(tmp_path: Path) -> tuple[Path, Path, Path]:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    copyfile(WATCHLIST_PACK, config_dir / "entities.yaml")
    copyfile(SCORING_EXAMPLE, config_dir / "scoring.yaml")
    return config_dir, data_dir, reports_dir


def entity_pack_error_count(payload: dict[str, object]) -> int:
    explicit_count = payload.get("error_count")
    if isinstance(explicit_count, int):
        return explicit_count

    findings = payload["findings"]
    assert isinstance(findings, list)
    return sum(
        1
        for finding in findings
        if isinstance(finding, dict) and finding.get("severity") == "error"
    )


def test_optional_watchlist_sample_runs_local_import_match_report_and_trends(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = prepare_watchlist_config(tmp_path)

    lint_payload = json.loads(
        invoke_ok(
            [
                "community-signal-lint",
                str(WATCHLIST_SAMPLE),
                "--input-format",
                "csv",
                "--source-name",
                "Community Watchlist Sample",
                "--format",
                "json",
            ]
        )
    )
    assert lint_payload["valid_row_count"] == 8
    assert lint_payload["findings"] == []

    pack_payload = json.loads(
        invoke_ok(
            [
                "entity-pack-lint",
                str(WATCHLIST_PACK),
                "--format",
                "json",
            ]
        )
    )
    assert entity_pack_error_count(pack_payload) == 0

    dry_run_output = invoke_ok(
        [
            "import-signals",
            str(WATCHLIST_SAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ]
    )
    assert "Validated 8 manual signal rows" in dry_run_output
    assert not (data_dir / "fashion-radar.sqlite").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite*")) == []

    import_output = invoke_ok(
        [
            "import-signals",
            str(WATCHLIST_SAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--imported-at",
            AS_OF,
            "--data-dir",
            str(data_dir),
        ]
    )
    assert "Imported 8 manual signal rows" in import_output

    match_output = invoke_ok(
        [
            "match",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
        ]
    )
    assert "Processed 8 items" in match_output

    invoke_ok(
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
        ]
    )
    report_payload = json.loads(
        (reports_dir / "fashion-radar-2026-06-13.json").read_text(encoding="utf-8")
    )
    report_entities = {entity["entity_name"] for entity in report_payload["entities"]}
    assert EXPECTED_REPORT_ENTITIES <= report_entities

    trend_payload = json.loads(
        invoke_ok(
            [
                "trends",
                "--config-dir",
                str(config_dir),
                "--data-dir",
                str(data_dir),
                "--as-of",
                AS_OF,
                "--baseline-as-of",
                BASELINE_AS_OF,
                "--format",
                "json",
            ]
        )
    )
    trend_names = {delta["name"] for delta in trend_payload["deltas"]}
    assert EXPECTED_REPORT_ENTITIES <= trend_names
