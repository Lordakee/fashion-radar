import json
from pathlib import Path
from textwrap import dedent

import pytest

from fashion_radar.community_signals import (
    PROHIBITED_COMMUNITY_SIGNAL_FIELDS,
    CommunitySignalFindingSeverity,
    lint_community_signal_directory,
    lint_community_signal_file,
    render_community_signal_directory_lint_table,
    render_community_signal_lint_table,
)
from fashion_radar.importers.manual_signals import load_manual_signal_rows

ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
JSON_EXAMPLE = ROOT / "examples" / "community-signals.example.json"
TOOL_HANDOFF_CSV_EXAMPLE = ROOT / "examples" / "community-tool-handoff.example.csv"
TOOL_HANDOFF_JSON_EXAMPLE = ROOT / "examples" / "community-tool-handoff.example.json"
WATCHLIST_CSV_EXAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_EXPECTED_ROWS = 8
COMMUNITY_SIGNAL_EXAMPLES = (
    (CSV_EXAMPLE, "csv", "Community Tool Export"),
    (JSON_EXAMPLE, "json", "Community Tool Export"),
    (TOOL_HANDOFF_CSV_EXAMPLE, "csv", "External Community Tool"),
    (TOOL_HANDOFF_JSON_EXAMPLE, "json", "External Community Tool"),
)


def _example_ids() -> list[str]:
    return [path.name for path, _, _ in COMMUNITY_SIGNAL_EXAMPLES]


def write_text(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def finding_codes(result) -> list[str]:
    return [finding.code for finding in result.findings]


def findings_by_code(result, code: str):
    return [finding for finding in result.findings if finding.code == code]


@pytest.mark.parametrize(
    ("path", "input_format", "source_name"),
    COMMUNITY_SIGNAL_EXAMPLES,
    ids=_example_ids(),
)
def test_repository_examples_lint_cleanly(
    path: Path,
    input_format: str,
    source_name: str,
) -> None:
    result = lint_community_signal_file(path, input_format=input_format)

    assert result.ok is True
    assert result.findings == []
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert result.source_name_counts == {source_name: 2}
    assert result.platform_counts == {"community": 2}


def test_watchlist_community_signal_example_lints_cleanly() -> None:
    result = lint_community_signal_file(WATCHLIST_CSV_EXAMPLE, input_format="csv")

    assert WATCHLIST_CSV_EXAMPLE.is_file()
    assert result.ok is True
    assert result.findings == []
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.row_count == WATCHLIST_EXPECTED_ROWS
    assert result.valid_row_count == WATCHLIST_EXPECTED_ROWS
    assert result.source_name_counts == {"Community Watchlist Sample": WATCHLIST_EXPECTED_ROWS}
    assert result.platform_counts == {"community": WATCHLIST_EXPECTED_ROWS}


def test_unknown_and_prohibited_csv_fields_are_errors(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,author_handle,unexpected
        https://example.com/a,Signal,2026-06-12T08:00:00Z,@private,value
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    prohibited = findings_by_code(result, "prohibited_field")[0]
    unknown = findings_by_code(result, "unknown_field")[0]
    assert prohibited.severity == CommunitySignalFindingSeverity.ERROR
    assert prohibited.row == 2
    assert prohibited.field == "author_handle"
    assert unknown.severity == CommunitySignalFindingSeverity.ERROR
    assert unknown.field == "unexpected"
    assert [finding.field for finding in findings_by_code(result, "unknown_field")] == [
        "unexpected"
    ]


def _valid_community_signal_row() -> dict[str, str]:
    return {
        "url": "https://example.com/a",
        "title": "Signal",
        "published_at": "2026-06-12T08:00:00Z",
        "summary": "Sanitized note",
        "source_name": "Community Tool Export",
        "platform": "community",
        "source_weight": "1.0",
        "collected_at": "2026-06-12T08:30:00Z",
    }


@pytest.mark.parametrize("field", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
@pytest.mark.parametrize(
    ("case_name", "input_format", "expected_row"),
    [
        ("csv", "csv", 2),
        ("json_array", "json", 1),
        ("json_items", "json", 1),
    ],
)
def test_all_prohibited_fields_are_lint_errors_for_supported_raw_rows(
    tmp_path: Path,
    field: str,
    case_name: str,
    input_format: str,
    expected_row: int,
) -> None:
    base = _valid_community_signal_row()
    if case_name == "csv":
        path = tmp_path / f"{field}.csv"
        path.write_text(
            ",".join([*base, field]) + "\n" + ",".join([*base.values(), "redacted"]) + "\n",
            encoding="utf-8",
        )
    else:
        path = tmp_path / f"{field}.json"
        row = {**base, field: "redacted"}
        payload = [row] if case_name == "json_array" else {"items": [row]}
        path.write_text(json.dumps(payload), encoding="utf-8")

    result = lint_community_signal_file(path, input_format=input_format)

    prohibited = findings_by_code(result, "prohibited_field")
    assert result.error_count == 1
    assert result.warning_count == 0
    assert result.valid_row_count == 1
    assert [(finding.row, finding.field, finding.severity) for finding in prohibited] == [
        (expected_row, field, CommunitySignalFindingSeverity.ERROR)
    ]


def test_invalid_row_is_error_using_import_validation(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        {
          "items": [
            {
              "url": "",
              "title": "Broken",
              "published_at": "2026-06-12T08:00:00Z"
            }
          ]
        }
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "invalid_row")[0]
    assert finding.severity == CommunitySignalFindingSeverity.ERROR
    assert finding.row == 1
    assert finding.field == "row"
    assert result.valid_row_count == 0


def test_invalid_json_shape_is_invalid_file_error(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        {"items": {}}
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "invalid_file")[0]
    assert result.error_count == 1
    assert finding.severity == CommunitySignalFindingSeverity.ERROR


def test_json_object_with_extra_top_level_key_is_invalid_file_error(
    tmp_path: Path,
) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        {
          "items": [
            {
              "url": "https://example.com/a",
              "title": "Signal",
              "published_at": "2026-06-12T08:00:00Z"
            }
          ],
          "extra": "not allowed"
        }
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "invalid_file")[0]
    assert result.error_count == 1
    assert finding.severity == CommunitySignalFindingSeverity.ERROR


@pytest.mark.parametrize("field", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
def test_json_top_level_prohibited_keys_are_invalid_file_not_raw_field_findings(
    tmp_path: Path,
    field: str,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "url": "https://example.com/a",
                        "title": "Signal",
                        "published_at": "2026-06-12T08:00:00Z",
                    }
                ],
                field: "redacted",
            }
        ),
        encoding="utf-8",
    )

    result = lint_community_signal_file(path, input_format="json")

    assert [finding.code for finding in result.findings] == ["invalid_file"]
    assert findings_by_code(result, "prohibited_field") == []


def test_csv_extra_cells_are_specific_errors(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,unexpected-cell
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    finding = findings_by_code(result, "csv_extra_cells")[0]
    assert finding.severity == CommunitySignalFindingSeverity.ERROR
    assert finding.row == 2
    assert finding.field == "row"
    assert "more cells than headers" in finding.message


@pytest.mark.parametrize("extra_cell", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
def test_csv_extra_cell_values_are_not_treated_as_raw_field_names(
    tmp_path: Path,
    extra_cell: str,
) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        f"""
        url,title,published_at,summary,source_name,platform,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Note,Tool,community,1.0,2026-06-12T08:30:00Z,{extra_cell}
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    assert [finding.code for finding in result.findings] == ["csv_extra_cells"]
    assert findings_by_code(result, "prohibited_field") == []


def test_source_name_fallback_matches_manual_importer(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,source_name
        https://example.com/a,Signal,2026-06-12T08:00:00Z,
        """,
    )

    result = lint_community_signal_file(
        path,
        input_format="csv",
        default_source_name="  ",
    )
    manual_rows = load_manual_signal_rows(
        path,
        input_format="csv",
        default_source_name="  ",
    )

    assert result.source_name_counts == {manual_rows[0].source_name: 1}
    assert result.source_name_counts == {"Manual Import": 1}
    assert findings_by_code(result, "missing_source_name")[0].row == 2


def test_duplicate_url_and_missing_provenance_are_warnings(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,First,2026-06-12T08:00:00Z
        https://example.com/a,Second,2026-06-12T09:00:00Z
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    assert "duplicate_url" in finding_codes(result)
    assert "missing_source_name" in finding_codes(result)
    assert "missing_platform" in finding_codes(result)
    assert "missing_summary" in finding_codes(result)
    assert "implicit_source_weight" in finding_codes(result)
    assert "implicit_collected_at" in finding_codes(result)
    assert result.warning_count >= 4
    assert result.info_count >= 2


def test_collected_before_published_is_warning(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.json",
        """
        [
          {
            "url": "https://example.com/a",
            "title": "Signal",
            "published_at": "2026-06-12T10:00:00Z",
            "source_name": "External Tool",
            "platform": "community",
            "summary": "Sanitized note",
            "source_weight": 1.0,
            "collected_at": "2026-06-12T09:00:00Z"
          }
        ]
        """,
    )

    result = lint_community_signal_file(path, input_format="json")

    finding = findings_by_code(result, "collected_before_published")[0]
    assert finding.severity == CommunitySignalFindingSeverity.WARNING
    assert finding.row == 1
    assert finding.field == "collected_at"


def test_empty_signal_file_is_warning(tmp_path: Path) -> None:
    path = write_text(tmp_path / "signals.csv", "url,title,published_at")

    result = lint_community_signal_file(path, input_format="csv")

    finding = findings_by_code(result, "empty_signal_file")[0]
    assert result.error_count == 0
    assert finding.severity == CommunitySignalFindingSeverity.WARNING


def test_lint_result_json_shape_is_stable(tmp_path: Path) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,summary,source_name,platform,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Note,Tool,community,1.2,2026-06-12T08:30:00Z
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")
    payload = json.loads(result.model_dump_json(indent=2))

    assert list(payload) == [
        "path",
        "input_format",
        "row_count",
        "valid_row_count",
        "field_counts",
        "source_name_counts",
        "platform_counts",
        "findings",
    ]
    assert payload["path"] == str(path)
    assert payload["input_format"] == "csv"
    assert payload["row_count"] == 1
    assert payload["valid_row_count"] == 1
    assert payload["findings"] == []


def test_render_community_signal_lint_table_includes_summary_and_findings(
    tmp_path: Path,
) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z
        """,
    )

    lines = render_community_signal_lint_table(lint_community_signal_file(path, input_format="csv"))

    assert lines[0] == f"Community signal file: {path}"
    assert "Input format: csv" in lines
    assert "Rows: 1 total, 1 import-ready" in lines
    assert "Severity | Code | Row | Field | Message" in lines
    assert any("missing_source_name" in line for line in lines)


def test_directory_lint_aggregates_matched_files_in_sorted_order(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "b.csv",
        """
        url,title,published_at,source_name,platform,summary,source_weight
        https://example.com/b,Second,2026-06-12T09:00:00Z,Zulu,forum,Note,1.1
        """,
    )
    write_text(
        tmp_path / "a.csv",
        """
        url,title,published_at,source_name,platform,summary
        https://example.com/a,First,2026-06-12T08:00:00Z,Alpha,community,Note
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is True
    assert result.file_count == 2
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert [Path(file.path).name for file in result.files] == ["a.csv", "b.csv"]
    assert result.source_name_counts == {"Alpha": 1, "Zulu": 1}
    assert list(result.source_name_counts) == ["Alpha", "Zulu"]
    assert result.platform_counts == {"community": 1, "forum": 1}
    assert list(result.platform_counts) == ["community", "forum"]
    assert list(result.field_counts) == sorted(result.field_counts)
    assert result.field_counts["source_weight"] == 1


def test_directory_lint_keeps_clean_and_invalid_file_results(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "clean.csv",
        """
        url,title,published_at,source_name,platform,summary
        https://example.com/clean,Clean,2026-06-12T08:00:00Z,Tool,community,Note
        """,
    )
    write_text(tmp_path / "broken.csv", "url,title,published_at\n,Missing,not-a-date")

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 2
    assert result.row_count == 2
    assert result.valid_row_count == 1
    assert result.error_count == 1
    assert {Path(file.path).name for file in result.files} == {
        "clean.csv",
        "broken.csv",
    }


def test_directory_lint_reports_no_matching_files(tmp_path: Path) -> None:
    write_text(tmp_path / "ignored.txt", "not a signal file")

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_directory_lint_reports_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    result = lint_community_signal_directory(
        missing,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"


def test_directory_lint_reports_file_path_as_invalid_directory(
    tmp_path: Path,
) -> None:
    path = write_text(tmp_path / "signals.csv", "url,title,published_at")

    result = lint_community_signal_directory(
        path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"


def test_directory_lint_reports_unreadable_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    original_iterdir = Path.iterdir

    def fail_iterdir(path: Path):
        if path == tmp_path:
            raise PermissionError("no access")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.ok is False
    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "invalid_directory"
    assert result.findings[0].message == "Could not read community signal directory."


def test_directory_lint_is_non_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    write_text(
        nested / "nested.csv",
        """
        url,title,published_at
        https://example.com/nested,Nested,2026-06-12T08:00:00Z
        """,
    )
    write_text(
        tmp_path / "top.csv",
        """
        url,title,published_at
        https://example.com/top,Top,2026-06-12T08:00:00Z
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="*.csv",
    )

    assert result.file_count == 1
    assert Path(result.files[0].path).name == "top.csv"


def test_directory_lint_double_star_pattern_does_not_recurse(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    write_text(
        nested / "nested.csv",
        """
        url,title,published_at
        https://example.com/nested,Nested,2026-06-12T08:00:00Z
        """,
    )

    result = lint_community_signal_directory(
        tmp_path,
        input_format="csv",
        pattern="**/*.csv",
    )

    assert result.file_count == 0
    assert result.error_count == 1
    assert result.findings[0].code == "no_matching_files"


def test_render_community_signal_directory_lint_table_includes_aggregate_and_file_lines(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z
        """,
    )

    lines = render_community_signal_directory_lint_table(
        lint_community_signal_directory(
            tmp_path,
            input_format="csv",
            pattern="*.csv",
        )
    )

    assert lines[0] == f"Community signal directory: {tmp_path}"
    assert "Input format: csv" in lines
    assert "Pattern: *.csv" in lines
    assert "Files: 1" in lines
    assert any(line.startswith(f"- {tmp_path / 'signals.csv'}:") for line in lines)
    assert "Severity | File | Code | Row | Field | Message" in lines


def test_render_community_signal_directory_lint_table_clean_directory(
    tmp_path: Path,
) -> None:
    write_text(
        tmp_path / "signals.csv",
        """
        url,title,published_at,source_name,platform,summary,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Tool,community,Note,1.0,2026-06-12T08:30:00Z
        """,
    )

    lines = render_community_signal_directory_lint_table(
        lint_community_signal_directory(
            tmp_path,
            input_format="csv",
            pattern="*.csv",
        )
    )

    assert "Findings: 0 errors, 0 warnings, 0 info" in lines
    assert "No community-signal directory findings." in lines
