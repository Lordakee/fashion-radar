from __future__ import annotations

import json
from pathlib import Path

from fashion_radar.community_handoff_check import (
    check_community_handoff_directory,
    render_community_handoff_directory_check_table,
)
from fashion_radar.settings import (
    CandidateDiscoverySettings,
    EntityConfig,
    ScoringSettings,
    load_entity_config,
    load_scoring_config,
)


def _load_candidate_config(
    config_dir: Path,
) -> tuple[ScoringSettings, CandidateDiscoverySettings, EntityConfig | None]:
    scoring_config = load_scoring_config(config_dir / "scoring.yaml")
    entity_path = config_dir / "entities.yaml"
    entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    return scoring_config.scoring, scoring_config.candidate_discovery, entity_config


def _write_config(config_dir: Path) -> None:
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
    (config_dir / "entities.yaml").write_text(
        "version: 1\nentities: []\n",
        encoding="utf-8",
    )


def _write_csv_directory(directory: Path) -> None:
    directory.mkdir()
    header = "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n"
    (directory / "first.csv").write_text(
        header
        + "https://example.com/check/the-row,The Row check,2026-06-12T12:00:00Z,"
        + "Synthetic check row,Community Tool Export,community,1.2,"
        + "2026-06-12T12:05:00Z\n",
        encoding="utf-8",
    )
    (directory / "second.csv").write_text(
        header
        + "https://example.com/check/mesh-flat,Mesh flat check,"
        + "2026-06-12T13:00:00Z,Synthetic mesh row,Community Tool Export,"
        + "community,1.1,2026-06-12T13:05:00Z\n",
        encoding="utf-8",
    )


def test_check_community_handoff_directory_returns_combined_readiness_report(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name=" Community Tool Export ",
        strict=False,
        limit=0,
    )

    assert result.model_dump_json(indent=2)
    assert result.directory == str(directory)
    assert result.input_format == "csv"
    assert result.pattern == "*.csv"
    assert result.as_of == "2026-06-16T00:00:00+00:00"
    assert result.config_dir == str(config_dir)
    assert result.source_name == "Community Tool Export"
    assert result.execution_mode == "local_read_only"
    assert result.strict is False
    assert result.limit == 0
    assert result.ok is True
    assert result.failed_check_count == 0
    assert result.warning_count == 0
    assert result.findings == []
    assert result.community_signal_lint.file_count == 2
    assert result.community_signal_lint.row_count == 2
    assert result.candidate_preview is not None
    assert result.candidate_preview.file_count == 2
    assert result.candidate_preview.row_count == 2
    assert result.candidate_preview.limit == 0
    assert result.candidate_preview.candidates == []
    assert result.import_dry_run.file_count == 2
    assert result.import_dry_run.valid_file_count == 2
    assert result.import_dry_run.row_count == 2


def test_check_community_handoff_directory_preserves_lint_and_dry_run_on_candidate_failure(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    (directory / "bad.csv").write_text(
        "url,title,published_at,author_handle\n"
        "https://example.com/check/bad,Bad row,not-a-date,@raw\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=50,
    )

    assert result.ok is False
    assert result.failed_check_count == 3
    assert result.community_signal_lint.error_count > 0
    assert result.candidate_preview is None
    assert result.import_dry_run.error_count > 0
    assert {finding.check for finding in result.findings} == {
        "community_signal_lint",
        "candidate_preview",
        "import_dry_run",
    }


def test_check_community_handoff_directory_strict_warnings_fail_overall_check(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    (directory / "empty.csv").write_text(
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    loose = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )
    strict = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=True,
        limit=0,
    )

    assert loose.warning_count == 1
    assert loose.ok is True
    assert strict.warning_count == 1
    assert strict.ok is False
    assert strict.failed_check_count == 1


def test_check_community_handoff_directory_normalizes_blank_source_name(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    directory.mkdir()
    header = "url,title,published_at,summary,platform,source_weight,collected_at\n"
    (directory / "first.csv").write_text(
        header
        + "https://example.com/check/source-default,Source default check,"
        + "2026-06-12T12:00:00Z,Synthetic row,community,1.2,"
        + "2026-06-12T12:05:00Z\n",
        encoding="utf-8",
    )
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="   ",
        strict=False,
        limit=0,
    )

    assert result.source_name == "Community Tool Export"
    assert result.community_signal_lint.source_name_counts == {"Community Tool Export": 1}
    assert result.import_dry_run.source_name_counts == {"Community Tool Export": 1}


def test_check_result_json_has_stable_top_level_keys(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )

    payload = json.loads(result.model_dump_json())

    assert list(payload) == [
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "source_name",
        "execution_mode",
        "strict",
        "limit",
        "ok",
        "failed_check_count",
        "warning_count",
        "findings",
        "community_signal_lint",
        "candidate_preview",
        "import_dry_run",
    ]


def test_render_community_handoff_directory_check_table_sanitizes_cells(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals | unsafe"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Source | Name\nWrapped",
        strict=False,
        limit=0,
    )
    lines = render_community_handoff_directory_check_table(result)

    assert lines[0] == "Community handoff directory check."
    assert "Execution mode: local_read_only" in lines
    assert "Directory: " in lines[2]
    assert "|" not in lines[2].split("Directory: ", 1)[1]
    assert "Source name: Source / Name Wrapped" in lines
    assert "Does not import rows or write SQLite." in lines


def test_render_community_handoff_directory_check_table_uses_singular_error_label(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    directory = tmp_path / "signals"
    _write_config(config_dir)
    _write_csv_directory(directory)
    scoring, settings, entity_config = _load_candidate_config(config_dir)

    result = check_community_handoff_directory(
        directory,
        config_dir=config_dir,
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-16T00:00:00Z",
        scoring=scoring,
        settings=settings,
        entity_config=entity_config,
        source_name="Community Tool Export",
        strict=False,
        limit=0,
    )
    assert result.candidate_preview is not None
    result = result.model_copy(
        update={
            "community_signal_lint": result.community_signal_lint.model_copy(
                update={
                    "file_count": 1,
                    "row_count": 1,
                    "valid_row_count": 1,
                    "error_count": 1,
                }
            ),
            "candidate_preview": result.candidate_preview.model_copy(
                update={
                    "row_count": 1,
                    "candidate_count": 1,
                }
            ),
            "import_dry_run": result.import_dry_run.model_copy(
                update={
                    "file_count": 1,
                    "valid_file_count": 1,
                    "row_count": 1,
                    "error_count": 1,
                }
            ),
        }
    )

    lines = render_community_handoff_directory_check_table(result)
    lint_line = next(line for line in lines if line.startswith("Lint: "))
    candidate_line = next(line for line in lines if line.startswith("Candidate preview: "))
    import_line = next(line for line in lines if line.startswith("Import dry-run: "))

    assert lint_line == "Lint: 1 file, 1/1 import-ready row, 1 error"
    assert candidate_line == "Candidate preview: 1 candidate from 1 row"
    assert import_line == "Import dry-run: 1/1 valid file, 1 row, 1 error"
