# Stage 50 Community Signal Producer Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a print-only `community-signal-profile` command that exposes the strict community signal producer contract for external user-controlled tools.

**Architecture:** A new focused module builds a Pydantic profile from existing community signal constants and renders table output. The Typer CLI imports that module and exposes JSON/table output without path, config, data, reports, network, or database behavior. Tests bind the profile to the checked-in CSV example, JSON schema, docs, and package archive checks.

**Tech Stack:** Python 3.11+, Pydantic v2, Typer, pytest, ruff, uv. No dependency, lockfile, scraping, browser automation, account/session, cookie, platform API, source acquisition, scheduler, watcher, database, dashboard, report, or compliance-review changes.

---

## File Structure

- Create `src/fashion_radar/community_signal_profile.py`: profile models,
  deterministic builder, and table renderer.
- Modify `src/fashion_radar/cli.py`: import the profile helpers, define
  `CommunitySignalProfileOutputFormat`, define a `--format` option, and add
  `community-signal-profile`.
- Create `tests/test_community_signal_profile.py`: direct profile/schema/example
  contract tests.
- Modify `tests/test_community_signal_import_contract.py`: assert the profile
  stays aligned with the schema contract and community examples.
- Modify `tests/test_cli.py`: command help/output/no-artifact tests.
- Create `examples/community-signal-profile.example.json`: generated example
  profile payload.
- Modify `scripts/check_package_archives.py` and
  `tests/test_package_archives.py`: require the profile example in sdist.
- Modify docs: `README.md`, `docs/community-signal-import.md`,
  `docs/community-signal-quality.md`, `docs/cli-reference.md`,
  `docs/source-boundaries.md`, `docs/architecture.md`,
  `docs/github-upload-checklist.md`, `CHANGELOG.md`.
- Create review artifacts under `docs/reviews/`.

## Parallel Work Ownership

- Worker A owns `src/fashion_radar/community_signal_profile.py`,
  `tests/test_community_signal_profile.py`, and focused profile contract tests.
- Worker B owns `src/fashion_radar/cli.py` and new `tests/test_cli.py` profile
  command tests.
- Worker C owns documentation, package archive lists, and docs/package drift
  tests.

Workers must not revert each other's edits. If a worker sees concurrent changes
outside its ownership set, it must adapt to them and report the touched paths.

## Task 1: Profile Model And Renderer

**Files:**
- Create: `src/fashion_radar/community_signal_profile.py`
- Create: `tests/test_community_signal_profile.py`
- Modify: `tests/test_community_signal_import_contract.py`

- [ ] **Step 1: Write failing profile contract tests**

Add `tests/test_community_signal_profile.py`:

```python
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar.community_signal_profile import (
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


def _schema_signal() -> dict[str, object]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["$defs"]["communitySignal"]


def _csv_header() -> list[str]:
    with CSV_EXAMPLE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def test_profile_contract_matches_schema_and_csv_header() -> None:
    profile = build_community_signal_profile()
    signal = _schema_signal()
    schema_fields = list(signal["properties"])

    assert profile.contract_version == "community-signals/v1"
    assert profile.execution_mode == "print_only"
    assert profile.schema_path == "schemas/community-signals.schema.json"
    assert profile.example_paths == [
        "examples/community-signals.example.csv",
        "examples/community-signals.example.json",
    ]
    assert profile.supported_input_formats == ["csv", "json"]
    assert profile.csv_header == _csv_header()
    assert profile.allowed_fields == profile.csv_header
    assert set(profile.allowed_fields) == ALLOWED_COMMUNITY_SIGNAL_FIELDS
    assert profile.required_fields == signal["required"]
    assert profile.optional_fields == [
        field for field in schema_fields if field not in signal["required"]
    ]
    assert profile.prohibited_fields == sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS)
    assert set(profile.prohibited_fields).isdisjoint(profile.allowed_fields)
    assert profile.json_envelopes == ["top_level_array", "object_with_items_only"]
    assert profile.field_rules["source_weight"] == {
        "exclusive_minimum": 0,
        "maximum": 5,
        "default": 1.0,
    }
    assert signal["properties"]["source_weight"]["exclusiveMinimum"] == 0
    assert signal["properties"]["source_weight"]["maximum"] == 5
    assert ManualSignalRow.model_fields["source_weight"].default == 1.0
    base_row = {
        "url": "https://example.com/signal",
        "title": "Signal",
        "published_at": "2026-06-12T08:00:00Z",
        "source_name": "Community Tool Export",
    }
    assert ManualSignalRow.model_validate(base_row).source_weight == 1.0
    assert ManualSignalRow.model_validate({**base_row, "source_weight": ""}).source_weight == 1.0
    assert ManualSignalRow.model_validate({**base_row, "source_weight": 5}).source_weight == 5
    with pytest.raises(ValidationError):
        ManualSignalRow.model_validate({**base_row, "source_weight": 0})
    with pytest.raises(ValidationError):
        ManualSignalRow.model_validate({**base_row, "source_weight": 5.1})


def test_profile_has_stable_json_key_order() -> None:
    payload = build_community_signal_profile().model_dump(mode="json")

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "schema_path",
        "example_paths",
        "supported_input_formats",
        "csv_header",
        "required_fields",
        "optional_fields",
        "allowed_fields",
        "prohibited_fields",
        "json_envelopes",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "recommended_commands",
        "boundaries",
    ]


def test_profile_model_rejects_extra_fields_and_missing_required_fields() -> None:
    payload = build_community_signal_profile().model_dump(mode="json")
    with_extra = {**payload, "unexpected": "value"}
    without_contract_version = {
        key: value for key, value in payload.items() if key != "contract_version"
    }

    try:
        CommunitySignalProducerProfile.model_validate(with_extra)
    except ValidationError as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("extra fields should fail validation")

    try:
        CommunitySignalProducerProfile.model_validate(without_contract_version)
    except ValidationError as exc:
        assert "Field required" in str(exc)
    else:
        raise AssertionError("missing required fields should fail validation")

    schema = CommunitySignalProducerProfile.model_json_schema()
    assert schema["additionalProperties"] is False


def test_profile_example_matches_generated_profile() -> None:
    expected = build_community_signal_profile().model_dump(mode="json")
    actual = json.loads(PROFILE_EXAMPLE.read_text(encoding="utf-8"))

    assert actual == expected


def test_profile_example_format_is_byte_for_byte_deterministic() -> None:
    expected = build_community_signal_profile().model_dump_json(indent=2) + "\n"

    assert PROFILE_EXAMPLE.read_text(encoding="utf-8") == expected


def test_profile_example_lists_prohibited_fields_only_as_contract_values() -> None:
    payload_text = PROFILE_EXAMPLE.read_text(encoding="utf-8")

    for prohibited in PROHIBITED_COMMUNITY_SIGNAL_FIELDS:
        assert f'"{prohibited}":' not in payload_text


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
    assert "Supported input formats: csv, json" in text
    assert "CSV header: url, title, published_at, summary, source_name, platform, source_weight, collected_at" in text
    assert "Required fields: url, title, published_at" in text
    assert "Optional fields: summary, source_name, platform, source_weight, collected_at" in text
    assert "JSON envelopes: top_level_array, object_with_items_only" in text
    assert "Source weight: >0 and <=5, default 1" in text
    assert "Unsupported capabilities: scraping, browser_automation" in text
    assert "Prohibited fields:" in text
    assert "fashion-radar community-signal-lint-dir" in text
    assert "Does not create config, data, report, dashboard, or SQLite artifacts." in text
    assert "Does not provide a compliance-review workflow." in text
```

Modify `tests/test_community_signal_import_contract.py`:

```python
from fashion_radar.community_signal_profile import build_community_signal_profile
```

Add:

```python
def test_community_signal_profile_matches_schema_properties() -> None:
    profile = build_community_signal_profile()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    signal = schema["$defs"]["communitySignal"]

    assert profile.required_fields == signal["required"]
    assert set(profile.allowed_fields) == set(signal["properties"])
    assert profile.csv_header == CSV_EXAMPLE.read_text(encoding="utf-8").splitlines()[0].split(",")
```

- [ ] **Step 2: Run failing focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py::test_community_signal_profile_matches_schema_properties -q
```

Expected: fail because `fashion_radar.community_signal_profile` and
`examples/community-signal-profile.example.json` do not exist.

- [ ] **Step 3: Implement the profile module**

Create `src/fashion_radar/community_signal_profile.py`:

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_signals import (
    ALLOWED_COMMUNITY_SIGNAL_FIELDS,
    PROHIBITED_COMMUNITY_SIGNAL_FIELDS,
)

COMMUNITY_SIGNAL_CONTRACT_VERSION = "community-signals/v1"
COMMUNITY_SIGNAL_EXECUTION_MODE = "print_only"
COMMUNITY_SIGNAL_SCHEMA_PATH = "schemas/community-signals.schema.json"
COMMUNITY_SIGNAL_EXAMPLE_PATHS = [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
]
COMMUNITY_SIGNAL_CSV_HEADER = [
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
]
COMMUNITY_SIGNAL_REQUIRED_FIELDS = ["url", "title", "published_at"]
COMMUNITY_SIGNAL_JSON_ENVELOPES = ["top_level_array", "object_with_items_only"]
COMMUNITY_SIGNAL_UNSUPPORTED_CAPABILITIES = [
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


class CommunitySignalProducerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: str
    schema_path: str
    example_paths: list[str]
    supported_input_formats: list[str]
    csv_header: list[str]
    required_fields: list[str]
    optional_fields: list[str]
    allowed_fields: list[str]
    prohibited_fields: list[str]
    json_envelopes: list[str]
    field_notes: dict[str, str] = Field(default_factory=dict)
    field_rules: dict[str, dict[str, int | float]] = Field(default_factory=dict)
    unsupported_capabilities: list[str]
    recommended_commands: list[str]
    boundaries: list[str]


def build_community_signal_profile() -> CommunitySignalProducerProfile:
    allowed_fields = _ordered_allowed_fields()
    return CommunitySignalProducerProfile(
        contract_version=COMMUNITY_SIGNAL_CONTRACT_VERSION,
        execution_mode=COMMUNITY_SIGNAL_EXECUTION_MODE,
        schema_path=COMMUNITY_SIGNAL_SCHEMA_PATH,
        example_paths=[*COMMUNITY_SIGNAL_EXAMPLE_PATHS],
        supported_input_formats=["csv", "json"],
        csv_header=[*COMMUNITY_SIGNAL_CSV_HEADER],
        required_fields=[*COMMUNITY_SIGNAL_REQUIRED_FIELDS],
        optional_fields=[
            field for field in allowed_fields if field not in COMMUNITY_SIGNAL_REQUIRED_FIELDS
        ],
        allowed_fields=allowed_fields,
        prohibited_fields=sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS),
        json_envelopes=[*COMMUNITY_SIGNAL_JSON_ENVELOPES],
        field_notes={
            "url": "Source URL or stable reference URL for the observed item.",
            "title": "Short observed text, headline, or normalized signal phrase.",
            "published_at": "ISO 8601-compatible publication or observation timestamp.",
            "summary": "Short sanitized note for local review.",
            "source_name": (
                "Display name for the external tool or local export; import commands can "
                "supply a fallback when omitted."
            ),
            "platform": (
                "Short local provenance label; not platform coverage, source acquisition, "
                "demand proof, or source ranking."
            ),
            "source_weight": (
                "Local score weight accepted in the range (0, 5]; importer default is 1.0 "
                "when omitted or blank."
            ),
            "collected_at": (
                "Timestamp for when the external tool produced the row; importer may use "
                "the import timestamp when omitted."
            ),
        },
        field_rules={
            "source_weight": {
                "exclusive_minimum": 0,
                "maximum": 5,
                "default": 1.0,
            }
        },
        unsupported_capabilities=[*COMMUNITY_SIGNAL_UNSUPPORTED_CAPABILITIES],
        recommended_commands=[
            (
                'fashion-radar community-signal-lint-dir ./exports --input-format csv '
                '--pattern "*.csv" --source-name "Community Tool Export" --strict'
            ),
            (
                "fashion-radar community-candidates-dir ./exports --input-format csv "
                '--pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" '
                '--source-name "Community Tool Export"'
            ),
            (
                "fashion-radar import-signals-dir ./exports --format csv --pattern "
                '"*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" '
                "--dry-run"
            ),
            (
                "fashion-radar import-signals-dir ./exports --format csv --pattern "
                '"*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" '
                '--data-dir "$PWD/data"'
            ),
            (
                'fashion-radar imported-review-workflow --data-dir "$PWD/data" '
                '--config-dir "$PWD/configs" --as-of "$AS_OF" '
                '--source-name "Community Tool Export"'
            ),
        ],
        boundaries=[
            "Prints the local handoff contract only.",
            "Does not read handoff files or directories.",
            "Does not create config, data, report, dashboard, or SQLite artifacts.",
            (
                "Does not fetch URLs, search platforms, log in, store cookies, automate "
                "browsers, call platform APIs, monitor communities, rank sources, or verify "
                "platform coverage."
            ),
            "Does not provide a compliance-review workflow.",
        ],
    )


def render_community_signal_profile_table(
    profile: CommunitySignalProducerProfile,
) -> list[str]:
    lines = [
        "Community signal producer profile",
        f"Contract version: {profile.contract_version}",
        f"Execution mode: {profile.execution_mode}",
        f"Schema path: {profile.schema_path}",
        f"Example paths: {', '.join(profile.example_paths)}",
        f"Supported input formats: {', '.join(profile.supported_input_formats)}",
        f"CSV header: {', '.join(profile.csv_header)}",
        f"Required fields: {', '.join(profile.required_fields)}",
        f"Optional fields: {', '.join(profile.optional_fields)}",
        f"Allowed fields: {', '.join(profile.allowed_fields)}",
        f"Prohibited fields: {', '.join(profile.prohibited_fields)}",
        f"JSON envelopes: {', '.join(profile.json_envelopes)}",
        (
            "Source weight: >"
            f"{profile.field_rules['source_weight']['exclusive_minimum']:g} and <="
            f"{profile.field_rules['source_weight']['maximum']:g}, default "
            f"{profile.field_rules['source_weight']['default']:g}"
        ),
        f"Unsupported capabilities: {', '.join(profile.unsupported_capabilities)}",
        "Field notes:",
    ]
    for field, note in profile.field_notes.items():
        lines.append(f"- {field}: {note}")
    lines.append("Recommended commands:")
    for command in profile.recommended_commands:
        lines.append(f"- {command}")
    lines.append("Boundaries:")
    for boundary in profile.boundaries:
        lines.append(f"- {boundary}")
    return lines


def _ordered_allowed_fields() -> list[str]:
    missing = set(COMMUNITY_SIGNAL_CSV_HEADER) - ALLOWED_COMMUNITY_SIGNAL_FIELDS
    extra = ALLOWED_COMMUNITY_SIGNAL_FIELDS - set(COMMUNITY_SIGNAL_CSV_HEADER)
    if missing or extra:
        raise ValueError("Community signal profile fields differ from lint contract.")
    return [*COMMUNITY_SIGNAL_CSV_HEADER]
```

- [ ] **Step 4: Add the generated profile example**

Create `examples/community-signal-profile.example.json` with the JSON output of:

```bash
UV_NO_CONFIG=1 uv run python -c 'from fashion_radar.community_signal_profile import build_community_signal_profile; print(build_community_signal_profile().model_dump_json(indent=2))'
```

The file must match `build_community_signal_profile().model_dump_json(indent=2)
+ "\n"` byte for byte.

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py -q
```

Expected: pass.

## Task 2: CLI Command And CLI Tests

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add near the existing community signal lint tests in `tests/test_cli.py`:

```python
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_community_signal_profile_help_lists_format() -> None:
    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--help"],
        env={"COLUMNS": "120"},
    )

    assert result.exit_code == 0
    assert "--format" in result.output
    assert "producer contract" in result.output
    for forbidden in (
        "--config-dir",
        "--data-dir",
        "--reports-dir",
        "--pattern",
        "--input-format",
        "--source-name",
        "--imported-at",
        "--dry-run",
    ):
        assert forbidden not in result.output


def test_community_signal_profile_prints_table() -> None:
    result = CliRunner().invoke(app, ["community-signal-profile"])

    assert result.exit_code == 0
    assert "Community signal producer profile" in result.output
    assert "Contract version: community-signals/v1" in result.output
    assert "CSV header: url, title, published_at" in result.output
    assert "fashion-radar community-signal-lint-dir" in result.output
    assert "Does not create config, data, report, dashboard, or SQLite artifacts." in result.output


def test_community_signal_profile_prints_json() -> None:
    result = CliRunner().invoke(app, ["community-signal-profile", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "schema_path",
        "example_paths",
        "supported_input_formats",
        "csv_header",
        "required_fields",
        "optional_fields",
        "allowed_fields",
        "prohibited_fields",
        "json_envelopes",
        "field_notes",
        "field_rules",
        "unsupported_capabilities",
        "recommended_commands",
        "boundaries",
    ]
    assert payload["contract_version"] == "community-signals/v1"
    assert payload["execution_mode"] == "print_only"
    assert payload["schema_path"] == "schemas/community-signals.schema.json"
    assert payload["supported_input_formats"] == ["csv", "json"]
    assert payload["csv_header"] == payload["allowed_fields"]
    assert payload["required_fields"] == ["url", "title", "published_at"]
    assert payload["unsupported_capabilities"][0] == "scraping"


def test_community_signal_profile_json_is_deterministic_across_env_and_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    first_cwd = tmp_path / "first"
    second_cwd = tmp_path / "second"
    first_cwd.mkdir()
    second_cwd.mkdir()

    monkeypatch.chdir(first_cwd)
    first = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(first_cwd / "config"),
            "FASHION_RADAR_DATA_DIR": str(first_cwd / "data"),
            "FASHION_RADAR_REPORTS_DIR": str(first_cwd / "reports"),
        },
    )
    monkeypatch.chdir(second_cwd)
    second = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(second_cwd / "config"),
            "FASHION_RADAR_DATA_DIR": str(second_cwd / "data"),
            "FASHION_RADAR_REPORTS_DIR": str(second_cwd / "reports"),
        },
    )

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert json.loads(first.output) == json.loads(second.output)


def test_community_signal_profile_does_not_create_project_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "json"],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not Path("configs").exists()
    assert not Path("data").exists()
    assert not Path("reports").exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite-*")) == []
    assert list(tmp_path.rglob("*.sqlite3")) == []
    assert list(tmp_path.rglob("*.db")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
    assert list(tmp_path.rglob("collection-workflow*.json")) == []


def test_community_signal_profile_does_not_run_side_effect_helpers(
    monkeypatch,
) -> None:
    def fail_side_effect(*args, **kwargs):
        raise AssertionError("side effect should not run")

    for name in ("iterdir", "glob", "rglob"):
        monkeypatch.setattr(Path, name, fail_side_effect)
    monkeypatch.setattr(os, "scandir", fail_side_effect)
    monkeypatch.setattr(cli_module.subprocess, "run", fail_side_effect)
    monkeypatch.setattr(subprocess, "Popen", fail_side_effect)
    monkeypatch.setattr(sqlite3, "connect", fail_side_effect)
    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail_side_effect)
    monkeypatch.setattr(cli_module, "initialize_schema", fail_side_effect)
    monkeypatch.setattr(cli_module, "load_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "lint_community_signal_file", fail_side_effect)
    monkeypatch.setattr(cli_module, "store_manual_signal_rows", fail_side_effect)
    monkeypatch.setattr(cli_module, "collect_configured_sources", fail_side_effect)
    monkeypatch.setattr(cli_module, "write_daily_report_files", fail_side_effect)
    monkeypatch.setattr(cli_module, "package_daily_digest", fail_side_effect)

    result = CliRunner().invoke(app, ["community-signal-profile", "--format", "json"])

    assert result.exit_code == 0


def test_community_signal_profile_real_process_does_not_create_artifacts(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "env-config"
    data_dir = tmp_path / "env-data"
    reports_dir = tmp_path / "env-reports"
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "FASHION_RADAR_CONFIG_DIR": str(config_dir),
        "FASHION_RADAR_DATA_DIR": str(data_dir),
        "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
    }

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fashion_radar",
            "community-signal-profile",
            "--format",
            "json",
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["contract_version"] == "community-signals/v1"
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite*")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []


def test_community_signal_profile_invalid_format_exits_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "--format", "yaml"],
        env={"FASHION_RADAR_DATA_DIR": str(data_dir)},
    )

    assert result.exit_code != 0
    assert not data_dir.exists()


def test_community_signal_profile_rejects_unexpected_path_without_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(
        app,
        ["community-signal-profile", "./exports"],
        env={"FASHION_RADAR_DATA_DIR": str(data_dir)},
    )

    assert result.exit_code != 0
    assert not data_dir.exists()
```

- [ ] **Step 2: Run failing CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_json_is_deterministic_across_env_and_cwd tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli.py::test_community_signal_profile_does_not_run_side_effect_helpers tests/test_cli.py::test_community_signal_profile_real_process_does_not_create_artifacts tests/test_cli.py::test_community_signal_profile_invalid_format_exits_without_artifacts tests/test_cli.py::test_community_signal_profile_rejects_unexpected_path_without_artifacts -q
```

Expected: fail because the CLI command is not registered.

- [ ] **Step 3: Add CLI imports, type alias, option, and command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.community_signal_profile import (
    build_community_signal_profile,
    render_community_signal_profile_table,
)
```

Near other output format aliases, add:

```python
CommunitySignalProfileOutputFormat = Literal["table", "json"]
```

Near community options, add:

```python
COMMUNITY_SIGNAL_PROFILE_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

Before `community-signal-lint`, add:

```python
@app.command(name="community-signal-profile")
def community_signal_profile_command(
    output_format: CommunitySignalProfileOutputFormat = (
        COMMUNITY_SIGNAL_PROFILE_FORMAT_OPTION
    ),
) -> None:
    """Print the local community signal producer contract."""
    profile = build_community_signal_profile()
    if output_format == "json":
        typer.echo(profile.model_dump_json(indent=2))
        return
    for line in render_community_signal_profile_table(profile):
        typer.echo(line)
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_json_is_deterministic_across_env_and_cwd tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli.py::test_community_signal_profile_does_not_run_side_effect_helpers tests/test_cli.py::test_community_signal_profile_real_process_does_not_create_artifacts tests/test_cli.py::test_community_signal_profile_invalid_format_exits_without_artifacts tests/test_cli.py::test_community_signal_profile_rejects_unexpected_path_without_artifacts -q
```

Expected: pass.

## Task 3: Documentation And Public Command Drift

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Run docs drift tests before docs changes**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_cli_reference_lists_every_public_command tests/test_cli_docs.py::test_upload_checklist_help_loop_matches_public_commands -q
```

Expected: fail after Task 2 because `community-signal-profile` is a new public
command that is not documented yet.

- [ ] **Step 2: Update docs for the producer profile**

Required documentation changes:

- In `docs/cli-reference.md`, under "Local Import And Community Handoff", add:

```markdown
- `community-signal-profile`: print the local producer contract for external
  tools that write sanitized community signal CSV/JSON handoff files; supports
  `--format table|json`.
```

- In `docs/community-signal-import.md`, add a section before "Preflight Lint":

```markdown
## Producer Profile

External tools can print the local producer contract before writing handoff
files:

```bash
uv run fashion-radar community-signal-profile
uv run fashion-radar community-signal-profile --format json
```

The profile includes the contract version, supported input formats, canonical
CSV header, required fields, optional fields, allowed fields, excluded fields,
accepted JSON envelope shapes, field notes, source-weight bounds, unsupported
capabilities, and the recommended local lint/preview/dry-run/import/review
command sequence. A checked-in example is available at
`examples/community-signal-profile.example.json`. It prints the contract only
and does not read handoff files or directories, create config/data/report
directories, open SQLite, fetch URLs, search platforms, log in, store cookies,
automate browsers, call platform APIs, monitor communities, rank sources,
verify platform coverage, or provide a compliance-review workflow.
```

- In `docs/community-signal-quality.md`, add a short sentence near the top:

```markdown
Run `community-signal-profile --format json` when a local external tool needs a
machine-readable producer contract before it writes CSV/JSON handoff files.
```

- In `docs/source-boundaries.md`, add:

```markdown
`community-signal-profile` prints the community handoff producer contract only.
It does not read handoff files or directories, create config/data/report
artifacts, open SQLite, fetch URLs, search platforms, log in, store cookies,
automate browsers, call platform APIs, monitor communities, rank sources,
verify platform coverage, or provide a compliance-review workflow.
```

- In `docs/architecture.md`, add one sentence to the local import/community
  signal component describing the print-only profile.
- In `README.md`, mention the command in the community handoff section near the
  existing `community-signal-lint` examples:

```bash
uv run fashion-radar community-signal-profile --format json
```

- In `docs/github-upload-checklist.md`, add `community-signal-profile` to the
  installed-wheel command help loop.
- In `CHANGELOG.md`, add an Unreleased entry:

```markdown
- Print-only `community-signal-profile` command and example JSON producer
  contract for external tools that generate sanitized community signal handoff
  files.
```

- [ ] **Step 3: Add docs tests for profile docs**

In `tests/test_cli_docs.py`, add:

```python
def test_community_signal_profile_docs_are_linked() -> None:
    readme = _read(README)
    cli_reference = _read(CLI_REFERENCE)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")

    for text in (readme, cli_reference, import_doc, quality_doc, boundaries):
        assert "community-signal-profile" in text

    assert "examples/community-signal-profile.example.json" in import_doc
    assert "producer contract" in import_doc
    assert "does not read handoff files or directories" in import_doc
    assert "does not read handoff files or directories" in boundaries
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: pass.

## Task 4: Package Archive Requirements

**Files:**
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Write failing package test update**

In both `scripts/check_package_archives.py` `SDIST_REQUIRED_PATHS` and
`tests/test_package_archives.py` `SDIST_FILES`, add:

```python
"examples/community-signal-profile.example.json",
```

near the existing community signal examples.

If `tests/test_package_archives.py` has a missing-sdist-file regression that
removes a specific file, keep the existing target unchanged; the generic
required-file test should cover the new path.

- [ ] **Step 2: Run package archive tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Expected: pass.

## Task 5: Focused Integration Verification

**Files:**
- All Stage 50 files.

- [ ] **Step 1: Run focused Stage 50 tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_json_is_deterministic_across_env_and_cwd tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli.py::test_community_signal_profile_does_not_run_side_effect_helpers tests/test_cli.py::test_community_signal_profile_real_process_does_not_create_artifacts tests/test_cli.py::test_community_signal_profile_invalid_format_exits_without_artifacts tests/test_cli.py::test_community_signal_profile_rejects_unexpected_path_without_artifacts tests/test_cli_docs.py tests/test_package_archives.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run ruff on changed Python files**

Run:

```bash
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_signal_profile.py src/fashion_radar/cli.py tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py tests/test_cli_docs.py tests/test_package_archives.py scripts/check_package_archives.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_signal_profile.py src/fashion_radar/cli.py tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py tests/test_cli_docs.py tests/test_package_archives.py scripts/check_package_archives.py
```

Expected: both commands exit zero.

- [ ] **Step 3: Run public command help smoke for the new command**

Run:

```bash
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar community-signal-profile --help
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar community-signal-profile --format json
```

Expected: help exits zero, JSON output parses if piped to `python -m json.tool`.

## Task 6: Full Release Verification, Review, Commit, Push

**Files:**
- All Stage 50 files.

- [ ] **Step 1: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
python3 -m venv "$tmp_env/venv"
"$tmp_env/venv/bin/python" -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple "$tmp_build"/*.whl
tmp_profile_run="$(mktemp -d)"
PROFILE_JSON="$(
  cd "$tmp_profile_run" && \
  FASHION_RADAR_CONFIG_DIR="$tmp_profile_run/config" \
  FASHION_RADAR_DATA_DIR="$tmp_profile_run/data" \
  FASHION_RADAR_REPORTS_DIR="$tmp_profile_run/reports" \
  "$tmp_env/venv/bin/fashion-radar" community-signal-profile --format json
)"
printf '%s\n' "$PROFILE_JSON" | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
test ! -e "$tmp_profile_run/config"
test ! -e "$tmp_profile_run/data"
test ! -e "$tmp_profile_run/reports"
test -z "$(find "$tmp_profile_run" -name '*.sqlite*' -o -name 'fashion-radar-*.json' -o -name 'fashion-radar-*.md' -o -name '*digest*' -o -name 'latest.*' -o -name 'report-index.json')"
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all commands exit zero; `uv.lock` is unchanged.

- [ ] **Step 2: Create Claude Code release review prompt**

Create `docs/reviews/claude-code-stage-50-release-review-prompt.md` with:

```markdown
# Claude Code Stage 50 Release Review Prompt

Review the Stage 50 diff in `/home/ubuntu/fashion-radar`.

Objective: add a print-only `community-signal-profile` command and example JSON
producer contract for external user-controlled tools that generate sanitized
community signal CSV/JSON handoff files.

Please review for correctness, missing tests, docs drift, packaging drift,
unintended side effects, and scope creep.

Hard boundaries:

- No scraping, crawling, browser automation, account/session/cookie handling,
  platform APIs, monitoring, scheduler behavior, source acquisition, database
  writes, report writes, dashboard state, or compliance-review functionality.
- The command should print only; it should not require path/config/data/report
  arguments.
- Critical and Important findings must be fixed before commit/push.

Return:

- Critical findings
- Important findings
- Minor findings
- Test/verification gaps
- Approval status
```

- [ ] **Step 3: Run Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-50-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-50-release-review.md
```

Expected: review has no Critical or Important findings, or all such findings
are fixed and re-reviewed.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/community_signal_profile.py src/fashion_radar/cli.py tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py tests/test_cli_docs.py tests/test_package_archives.py scripts/check_package_archives.py examples/community-signal-profile.example.json README.md CHANGELOG.md docs/community-signal-import.md docs/community-signal-quality.md docs/cli-reference.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md docs/superpowers/specs/2026-06-16-stage-50-community-signal-producer-profile-design.md docs/superpowers/plans/2026-06-16-stage-50-community-signal-producer-profile-plan.md docs/reviews/claude-code-stage-50-plan-review-prompt.md docs/reviews/claude-code-stage-50-plan-review.md docs/reviews/claude-code-stage-50-release-review-prompt.md docs/reviews/claude-code-stage-50-release-review.md
git commit -m "Add community signal producer profile"
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
BASIC="$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 \
  -c http.postBuffer=524288000 \
  -c http.lowSpeedLimit=0 \
  -c http.lowSpeedTime=999999 \
  -c http.extraHeader="Authorization: Basic ${BASIC}" \
  push --no-thin origin main
```

Do not print the token and do not store it in the remote URL. Claude Code is a
read-only reviewer in this workflow and Codex performs the commit, so do not add
a Claude Code co-author trailer unless a current repo or user instruction
explicitly requires one.

- [ ] **Step 5: Confirm GitHub Actions**

Run:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
curl -fsS -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/Lordakee/fashion-radar/actions/runs?branch=main&per_page=1" \
  | python3 -c 'import json,sys; r=json.load(sys.stdin)["workflow_runs"][0]; print(r["id"], r["status"], r["conclusion"], r["head_sha"], r["html_url"])'
```

Expected: latest `origin/main` run for the pushed Stage 50 commit completes
successfully.

## Self-Review

- Spec coverage: Tasks cover profile model, CLI command, example JSON, docs,
  package archive checks, focused verification, release review, commit, push,
  and Actions confirmation.
- Placeholder scan: The plan contains no TODO/TBD placeholders.
- Type consistency: The profile builder, renderer, CLI output format alias, and
  tests all use `community-signal-profile`,
  `CommunitySignalProducerProfile`, and `build_community_signal_profile`
  consistently.
