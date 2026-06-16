from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.community_signals import lint_community_signal_file
from fashion_radar.importers.manual_signals import load_manual_signal_rows

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = ROOT / "examples" / "community-tool-handoff-directory.example"
CSV_DIRECTORY = EXAMPLE_ROOT / "csv"
JSON_DIRECTORY = EXAMPLE_ROOT / "json"
CSV_FILES = ("community-tool-a.csv", "community-tool-b.csv")
JSON_FILES = ("community-tool-a.json", "community-tool-b.json")
EXPECTED_FIELDS = {
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
}
DIRECTORY_EXAMPLES = (
    (CSV_DIRECTORY, CSV_FILES, "csv", "*.csv"),
    (JSON_DIRECTORY, JSON_FILES, "json", "*.json"),
)


def _example_ids() -> list[str]:
    return [input_format for _directory, _files, input_format, _pattern in DIRECTORY_EXAMPLES]


def _signal_paths(directory: Path, names: tuple[str, ...]) -> list[Path]:
    return [directory / name for name in names]


def _field_names(path: Path, input_format: str) -> set[str]:
    if input_format == "csv":
        return set(path.read_text(encoding="utf-8").splitlines()[0].split(","))

    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload["items"] if isinstance(payload, dict) else payload
    return set().union(*(item.keys() for item in items))


def test_directory_example_root_layout_is_locked() -> None:
    assert sorted(path.name for path in EXAMPLE_ROOT.iterdir()) == [
        "README.md",
        "csv",
        "json",
    ]
    assert (EXAMPLE_ROOT / "README.md").is_file()
    assert CSV_DIRECTORY.is_dir()
    assert JSON_DIRECTORY.is_dir()


@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_example_shape_has_two_matched_handoff_files(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    matched = sorted(path.name for path in directory.glob(pattern))

    assert directory.exists()
    assert matched == sorted(expected_names)
    for signal_file in _signal_paths(directory, expected_names):
        assert signal_file.exists()
        assert signal_file.is_file()
        assert _field_names(signal_file, input_format) == EXPECTED_FIELDS
    assert not any(
        path.name.startswith("community-handoff-manifest") for path in directory.iterdir()
    )


@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_example_signal_files_lint_and_load_cleanly(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    rows = []

    for signal_file in _signal_paths(directory, expected_names):
        result = lint_community_signal_file(
            signal_file,
            input_format=input_format,
            default_source_name="External Community Tool",
        )
        loaded_rows = load_manual_signal_rows(
            signal_file,
            input_format=input_format,
            default_source_name="External Community Tool",
        )

        assert result.ok is True
        assert result.error_count == 0
        assert result.warning_count == 0
        assert result.row_count == 1
        assert result.valid_row_count == 1
        assert len(loaded_rows) == 1
        rows.extend(loaded_rows)

    assert len(rows) == 2
    assert all(row.url.startswith("https://example.com/") for row in rows)
    assert {row.source_name for row in rows} == {"External Community Tool"}
    assert {row.platform for row in rows} == {"community"}


@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_examples_pass_community_signal_lint_dir(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(directory),
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--format",
            "json",
            "--source-name",
            "External Community Tool",
            "--strict",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 2
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["platform_counts"] == {"community": 2}


@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_examples_pass_import_signals_dir_dry_run_without_artifacts(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(directory),
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--data-dir",
            str(data_dir),
            "--source-name",
            "External Community Tool",
            "--dry-run",
            "--output-format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["valid_file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["error_count"] == 0
    assert payload["platform_counts"] == {"community": 2}
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()


def test_directory_examples_pass_community_candidates_dir_limit_zero_without_artifacts(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring: {}\n"
        "candidate_discovery:\n"
        "  review_min_current_mentions: 1\n"
        "  review_min_distinct_sources: 1\n"
        "  min_single_token_mentions: 1\n"
        "  min_single_token_distinct_sources: 1\n",
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(CSV_DIRECTORY),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--source-name",
            "External Community Tool",
            "--limit",
            "0",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["limit"] == 0
    assert payload["candidates"] == []
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not (tmp_path / "fashion-radar.sqlite").exists()
