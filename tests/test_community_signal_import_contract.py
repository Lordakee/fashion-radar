import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.community_signals import (
    ALLOWED_COMMUNITY_SIGNAL_FIELDS,
    lint_community_signal_file,
)
from fashion_radar.importers.manual_signals import load_manual_signal_rows

ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
JSON_EXAMPLE = ROOT / "examples" / "community-signals.example.json"
TOOL_HANDOFF_CSV_EXAMPLE = ROOT / "examples" / "community-tool-handoff.example.csv"
TOOL_HANDOFF_JSON_EXAMPLE = ROOT / "examples" / "community-tool-handoff.example.json"
WATCHLIST_CSV_EXAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_EXPECTED_ROWS = 11
COMMUNITY_SIGNAL_EXAMPLES = (
    (CSV_EXAMPLE, "csv", "Community Tool Export"),
    (JSON_EXAMPLE, "json", "Community Tool Export"),
    (TOOL_HANDOFF_CSV_EXAMPLE, "csv", "External Community Tool"),
    (TOOL_HANDOFF_JSON_EXAMPLE, "json", "External Community Tool"),
)
TOOL_HANDOFF_EXAMPLES = (
    (TOOL_HANDOFF_CSV_EXAMPLE, "csv", "External Community Tool"),
    (TOOL_HANDOFF_JSON_EXAMPLE, "json", "External Community Tool"),
)
SCHEMA_PATH = ROOT / "schemas" / "community-signals.schema.json"


def _example_ids(examples) -> list[str]:
    return [path.name for path, _, _ in examples]


def _example_fields(path: Path, input_format: str) -> set[str]:
    if input_format == "csv":
        return set(path.read_text(encoding="utf-8").splitlines()[0].split(","))

    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else payload["items"]
    return set().union(*(item.keys() for item in items))


def test_community_signal_csv_example_loads_through_manual_importer() -> None:
    rows = load_manual_signal_rows(
        CSV_EXAMPLE,
        input_format="csv",
        default_source_name="Community Tool Export",
    )

    assert len(rows) == 2
    assert rows[0].url == "https://example.com/community/the-row-margaux-tote"
    assert rows[0].title == "The Row Margaux tote interest"
    assert rows[0].summary == "Sanitized local note about The Row Margaux handbag and tote demand"
    assert rows[0].source_name == "Community Tool Export"
    assert rows[0].platform == "community"
    assert rows[0].source_weight == 1.3
    assert rows[0].collected_at is not None
    assert rows[0].collected_at.isoformat() == "2026-06-12T08:30:00+00:00"
    assert rows[1].url == "https://example.com/community/ballet-flats-footwear"
    assert rows[1].title == "Ballet flats footwear mention"
    assert rows[1].summary == "Short sanitized note about ballet flats shoes and footwear styling"
    assert rows[1].source_name == "Community Tool Export"
    assert rows[1].platform == "community"
    assert rows[1].source_weight == 1.1
    assert rows[1].collected_at is not None
    assert rows[1].collected_at.isoformat() == "2026-06-12T09:20:00+00:00"


def test_community_signal_json_example_loads_through_manual_importer() -> None:
    rows = load_manual_signal_rows(
        JSON_EXAMPLE,
        input_format="json",
        default_source_name="Community Tool Export",
    )

    assert len(rows) == 2
    assert rows[0].url == "https://example.com/community/the-row-tote"
    assert rows[0].title == "The Row tote discussion"
    assert rows[0].source_name == "Community Tool Export"
    assert rows[0].platform == "community"
    assert rows[0].source_weight == 1.4
    assert rows[1].title == "Silver sneaker signal"


@pytest.mark.parametrize(
    ("path", "input_format", "source_name"),
    COMMUNITY_SIGNAL_EXAMPLES,
    ids=_example_ids(COMMUNITY_SIGNAL_EXAMPLES),
)
def test_community_examples_load_through_manual_importer(
    path: Path,
    input_format: str,
    source_name: str,
) -> None:
    rows = load_manual_signal_rows(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )

    assert len(rows) == 2
    assert {row.source_name for row in rows} == {source_name}
    assert {row.platform for row in rows} == {"community"}


def test_watchlist_community_signal_csv_example_loads_expected_rows() -> None:
    rows = load_manual_signal_rows(
        WATCHLIST_CSV_EXAMPLE,
        input_format="csv",
        default_source_name="Community Watchlist Sample",
    )

    assert len(rows) == 11
    assert rows[0].url == "https://example.com/community-watchlist/khaite-lotus-bag"
    assert rows[0].title == "Khaite Lotus Bag local watchlist note"
    assert rows[0].source_name == "Community Watchlist Sample"
    assert rows[0].platform == "community"
    assert rows[-1].title == "Boho Revival styling watchlist note"


@pytest.mark.parametrize(
    ("path", "input_format", "source_name"),
    TOOL_HANDOFF_EXAMPLES,
    ids=_example_ids(TOOL_HANDOFF_EXAMPLES),
)
def test_community_tool_handoff_examples_use_safe_demo_urls(
    path: Path,
    input_format: str,
    source_name: str,
) -> None:
    rows = load_manual_signal_rows(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )

    assert all(row.url.startswith("https://example.com/") for row in rows)
    assert {row.platform for row in rows} == {"community"}


def test_community_signal_schema_documents_strict_public_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    one_of = schema["oneOf"]
    array_form = next(option for option in one_of if option.get("type") == "array")
    object_form = next(option for option in one_of if option.get("type") == "object")
    signal = schema["$defs"]["communitySignal"]
    properties = signal["properties"]

    assert len(one_of) == 2
    assert array_form["items"]["$ref"] == "#/$defs/communitySignal"
    assert object_form["required"] == ["items"]
    assert object_form["additionalProperties"] is False
    assert object_form["properties"]["items"]["items"]["$ref"] == "#/$defs/communitySignal"
    assert set(signal["required"]) == {"url", "title", "published_at"}
    assert signal["additionalProperties"] is False
    assert set(properties) == {
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    }
    assert properties["source_weight"]["exclusiveMinimum"] == 0
    assert properties["source_weight"]["maximum"] == 5
    assert {
        "author_handle",
        "raw_comment",
        "account_id",
        "follower_count",
        "image_url",
        "video_url",
        "profile_url",
        "full_post_body",
        "direct_message",
        "cookie",
        "session",
        "token",
    }.isdisjoint(properties)


def test_community_examples_use_same_allowed_contract_fields() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["communitySignal"]["properties"])

    for path, input_format, _source_name in COMMUNITY_SIGNAL_EXAMPLES:
        assert _example_fields(path, input_format) <= allowed


def test_watchlist_community_signal_csv_example_uses_allowed_fields() -> None:
    fields = _example_fields(WATCHLIST_CSV_EXAMPLE, "csv")

    assert fields <= ALLOWED_COMMUNITY_SIGNAL_FIELDS


def test_community_signal_linter_allowed_fields_match_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["communitySignal"]["properties"])

    assert ALLOWED_COMMUNITY_SIGNAL_FIELDS == allowed


def test_community_signal_profile_matches_schema_properties() -> None:
    profile = build_community_signal_profile()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    signal = schema["$defs"]["communitySignal"]

    assert profile.required_fields == signal["required"]
    assert set(profile.allowed_fields) == set(signal["properties"])
    assert profile.csv_header == CSV_EXAMPLE.read_text(encoding="utf-8").splitlines()[0].split(",")


def test_community_signal_linter_accepts_repository_examples() -> None:
    for path, input_format, _source_name in COMMUNITY_SIGNAL_EXAMPLES:
        result = lint_community_signal_file(path, input_format=input_format)

        assert result.ok is True
        assert result.findings == []
        assert result.valid_row_count == 2


@pytest.mark.parametrize(
    ("path", "input_format", "source_name"),
    COMMUNITY_SIGNAL_EXAMPLES,
    ids=_example_ids(COMMUNITY_SIGNAL_EXAMPLES),
)
def test_import_signals_dry_run_validates_community_examples_without_artifacts(
    path: Path,
    input_format: str,
    source_name: str,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    env = {
        "FASHION_RADAR_CONFIG_DIR": str(config_dir),
        "FASHION_RADAR_DATA_DIR": str(data_dir),
        "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
    }
    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(path),
            "--format",
            input_format,
            "--data-dir",
            str(data_dir),
            "--source-name",
            source_name,
            "--dry-run",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    assert "Validated 2 manual signal rows" in result.output
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not list(tmp_path.rglob("*.sqlite*"))
    assert not list(tmp_path.rglob("fashion-radar-*.json"))
    assert not list(tmp_path.rglob("fashion-radar-*.md"))
    assert not list(tmp_path.rglob("latest.*"))
    assert not list(tmp_path.rglob("report-index.json"))


def test_import_signals_dry_run_validates_watchlist_sample_without_artifacts(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(WATCHLIST_CSV_EXAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ],
        env={"FASHION_RADAR_REPORTS_DIR": str(reports_dir)},
    )

    assert result.exit_code == 0
    assert f"Validated {WATCHLIST_EXPECTED_ROWS} manual signal rows" in result.output
    assert "Dry run: no rows imported" in result.output
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite*")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
