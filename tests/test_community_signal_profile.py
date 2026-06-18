from __future__ import annotations

import csv
import json
import shlex
from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar.community_signal_profile import (
    COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS,
    CommunitySignalProducerProfile,
    build_community_signal_profile,
    render_community_signal_profile_table,
)
from fashion_radar.community_signals import (
    ALLOWED_COMMUNITY_SIGNAL_FIELDS,
    PROHIBITED_COMMUNITY_SIGNAL_FIELDS,
    lint_community_signal_file,
)
from fashion_radar.importers.manual_signals import ManualSignalRow

ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
PROFILE_EXAMPLE = ROOT / "examples" / "community-signal-profile.example.json"
SCHEMA_PATH = ROOT / "schemas" / "community-signals.schema.json"
DIRECTORY_EXAMPLE_PATHS = [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]


def _schema_signal() -> dict[str, object]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["$defs"]["communitySignal"]


def _csv_header() -> list[str]:
    with CSV_EXAMPLE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def test_profile_contract_matches_schema_csv_header_and_constants() -> None:
    profile = build_community_signal_profile()
    signal = _schema_signal()
    schema_fields = list(signal["properties"])

    assert profile.contract_version == "community-signals/v1"
    assert profile.execution_mode == "print_only"
    assert profile.schema_path == "schemas/community-signals.schema.json"
    assert profile.example_paths == [
        "examples/community-signals.example.csv",
        "examples/community-signals.example.json",
        "examples/community-tool-handoff.example.csv",
        "examples/community-tool-handoff.example.json",
    ]
    assert profile.directory_example_paths == DIRECTORY_EXAMPLE_PATHS
    assert profile.supported_input_formats == ["csv", "json"]
    assert profile.csv_header == _csv_header()
    assert profile.allowed_fields == profile.csv_header
    assert set(profile.allowed_fields) == ALLOWED_COMMUNITY_SIGNAL_FIELDS
    assert set(profile.allowed_fields) == set(signal["properties"])
    assert profile.required_fields == signal["required"]
    assert profile.optional_fields == [
        field for field in schema_fields if field not in signal["required"]
    ]
    assert profile.prohibited_fields == sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS)
    assert set(profile.prohibited_fields).isdisjoint(profile.allowed_fields)
    assert set(profile.prohibited_fields).isdisjoint(signal["properties"])
    assert profile.json_envelopes == ["top_level_array", "object_with_items_only"]
    assert profile.suggested_platform_labels == COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS
    assert "suggested_platform_labels" not in profile.allowed_fields
    assert profile.field_rules["source_weight"] == {
        "exclusive_minimum": 0,
        "maximum": 5,
        "default": 1.0,
    }
    assert signal["properties"]["source_weight"]["exclusiveMinimum"] == 0
    assert signal["properties"]["source_weight"]["maximum"] == 5


def test_profile_example_paths_exist_and_lint_cleanly() -> None:
    profile = build_community_signal_profile()

    for relative_path in profile.example_paths:
        path = ROOT / relative_path
        input_format = path.suffix.removeprefix(".")

        assert path.exists()
        assert input_format in profile.supported_input_formats
        result = lint_community_signal_file(path, input_format=input_format)
        assert result.ok is True
        assert result.findings == []


def test_profile_directory_example_paths_exist_without_replacing_single_file_examples() -> None:
    profile = build_community_signal_profile()

    assert profile.directory_example_paths == DIRECTORY_EXAMPLE_PATHS
    assert all(
        (ROOT / relative_path).is_file() for relative_path in profile.directory_example_paths
    )
    assert all(
        not relative_path.startswith("examples/community-tool-handoff-directory.example/")
        for relative_path in profile.example_paths
    )


def test_profile_has_stable_json_key_order() -> None:
    payload = build_community_signal_profile().model_dump(mode="json")

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "schema_path",
        "example_paths",
        "directory_example_paths",
        "supported_input_formats",
        "csv_header",
        "required_fields",
        "optional_fields",
        "allowed_fields",
        "prohibited_fields",
        "json_envelopes",
        "suggested_platform_labels",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "recommended_commands",
        "boundaries",
    ]


def test_profile_recommended_commands_keep_directory_handoff_sequence() -> None:
    commands = build_community_signal_profile().recommended_commands
    parsed = [shlex.split(command) for command in commands]

    def flag_value(parts: list[str], flag: str) -> str:
        return parts[parts.index(flag) + 1]

    assert [parts[:2] for parts in parsed] == [
        ["fashion-radar", "community-signal-lint-dir"],
        ["fashion-radar", "community-candidates-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "imported-review-workflow"],
    ]
    assert all("./exports" in parts for parts in parsed[:4])
    assert "--strict" in parsed[0]
    assert "--config-dir" not in parsed[0]
    assert "--data-dir" not in parsed[0]
    assert "--config-dir" in parsed[1]
    assert flag_value(parsed[1], "--config-dir") == "$PWD/configs"
    assert flag_value(parsed[1], "--as-of") == "$AS_OF"
    assert "--data-dir" not in parsed[1]
    assert "--dry-run" in parsed[2]
    assert "--imported-at" not in parsed[2]
    assert flag_value(parsed[2], "--data-dir") == "$PWD/data"
    assert "--dry-run" not in parsed[3]
    assert flag_value(parsed[3], "--imported-at") == "$AS_OF"
    assert flag_value(parsed[3], "--data-dir") == "$PWD/data"
    assert flag_value(parsed[4], "--as-of") == "$AS_OF"
    assert flag_value(parsed[4], "--config-dir") == "$PWD/configs"
    assert flag_value(parsed[4], "--data-dir") == "$PWD/data"
    source_name_values = [flag_value(parts, "--source-name") for parts in parsed]
    assert source_name_values == ["Community Tool Export"] * 5


def test_profile_model_rejects_extra_fields_and_missing_required_fields() -> None:
    payload = build_community_signal_profile().model_dump(mode="json")
    with_extra = {**payload, "unexpected": "value"}
    without_contract_version = {
        key: value for key, value in payload.items() if key != "contract_version"
    }

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CommunitySignalProducerProfile.model_validate(with_extra)
    with pytest.raises(ValidationError, match="Field required"):
        CommunitySignalProducerProfile.model_validate(without_contract_version)

    schema = CommunitySignalProducerProfile.model_json_schema()
    assert schema["additionalProperties"] is False


def test_manual_signal_row_source_weight_matches_profile_rules() -> None:
    base_row = {
        "url": "https://example.com/signal",
        "title": "Signal",
        "published_at": "2026-06-12T08:00:00Z",
        "source_name": "Community Tool Export",
    }

    assert ManualSignalRow.model_fields["source_weight"].default == 1.0
    assert ManualSignalRow.model_validate(base_row).source_weight == 1.0
    assert ManualSignalRow.model_validate({**base_row, "source_weight": ""}).source_weight == 1.0
    assert ManualSignalRow.model_validate({**base_row, "source_weight": 5}).source_weight == 5
    with pytest.raises(ValidationError):
        ManualSignalRow.model_validate({**base_row, "source_weight": 0})
    with pytest.raises(ValidationError):
        ManualSignalRow.model_validate({**base_row, "source_weight": 5.1})


def test_profile_json_is_not_a_community_signal_import_file(tmp_path: Path) -> None:
    path = tmp_path / "profile.json"
    path.write_text(
        build_community_signal_profile().model_dump_json(indent=2),
        encoding="utf-8",
    )

    result = lint_community_signal_file(path, input_format="json")

    assert result.ok is False
    assert result.row_count == 0
    assert [finding.code for finding in result.findings] == ["invalid_file"]


def test_profile_example_matches_generated_profile() -> None:
    expected = build_community_signal_profile().model_dump(mode="json")
    actual = json.loads(PROFILE_EXAMPLE.read_text(encoding="utf-8"))

    assert actual == expected


def test_profile_example_format_is_byte_for_byte_deterministic() -> None:
    expected = build_community_signal_profile().model_dump_json(indent=2) + "\n"

    assert PROFILE_EXAMPLE.read_text(encoding="utf-8") == expected


def test_profile_unsupported_capabilities_are_structured() -> None:
    profile = build_community_signal_profile()

    assert profile.unsupported_capabilities == [
        "scraping",
        "browser_automation",
        "account_login",
        "cookies_sessions",
        "platform_api",
        "compliance_review",
        "source_acquisition",
        "media_download",
        "watching_monitoring",
        "scheduling",
    ]


def test_profile_table_includes_contract_commands_and_boundaries() -> None:
    lines = render_community_signal_profile_table(build_community_signal_profile())
    text = "\n".join(lines)

    assert "Community signal producer profile" in lines[0]
    assert "Contract version: community-signals/v1" in text
    assert "Execution mode: print_only" in text
    assert (
        "Directory example paths: examples/community-tool-handoff-directory.example/README.md"
    ) in text
    assert "Supported input formats: csv, json" in text
    assert (
        "CSV header: url, title, published_at, summary, source_name, platform, "
        "source_weight, collected_at"
    ) in text
    assert "Required fields: url, title, published_at" in text
    assert "Optional fields: summary, source_name, platform, source_weight, collected_at" in text
    assert "JSON envelopes: top_level_array, object_with_items_only" in text
    assert (
        "Suggested platform labels: rednote, xiaohongshu, instagram, tiktok, media, x, community"
    ) in text
    assert "Source weight: >0 and <=5, default 1" in text
    assert "Unsupported capabilities: scraping, browser_automation" in text
    assert "Prohibited fields:" in text
    assert "fashion-radar community-signal-lint-dir" in text
    assert "Does not create config, data, report, dashboard, or SQLite artifacts." in text
    assert "Does not provide a compliance-review workflow." in text
