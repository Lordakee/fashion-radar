import json
from pathlib import Path

from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.importers.manual_signals import load_manual_signal_rows

ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
JSON_EXAMPLE = ROOT / "examples" / "community-signals.example.json"
SCHEMA_PATH = ROOT / "schemas" / "community-signals.schema.json"


def test_community_signal_csv_example_loads_through_manual_importer() -> None:
    rows = load_manual_signal_rows(
        CSV_EXAMPLE,
        input_format="csv",
        default_source_name="Community Tool Export",
    )

    assert len(rows) == 2
    assert rows[0].url == "https://example.com/community/east-west-tote"
    assert rows[0].title == "East-west tote interest"
    assert rows[0].source_name == "Community Tool Export"
    assert rows[0].platform == "community"
    assert rows[0].source_weight == 1.3
    assert rows[1].title == "Soft ballet flats mention"
    assert rows[1].summary is not None


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
    csv_header = CSV_EXAMPLE.read_text(encoding="utf-8").splitlines()[0].split(",")
    payload = json.loads(JSON_EXAMPLE.read_text(encoding="utf-8"))
    json_keys = set().union(*(item.keys() for item in payload["items"]))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["communitySignal"]["properties"])

    assert set(csv_header) <= allowed
    assert json_keys <= allowed


def test_import_signals_dry_run_validates_community_examples_without_artifacts(
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
    csv_result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(CSV_EXAMPLE),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Community Tool Export",
            "--dry-run",
        ],
        env=env,
    )
    json_result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(JSON_EXAMPLE),
            "--format",
            "json",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Community Tool Export",
            "--dry-run",
        ],
        env=env,
    )

    assert csv_result.exit_code == 0
    assert "Validated 2 manual signal rows" in csv_result.output
    assert json_result.exit_code == 0
    assert "Validated 2 manual signal rows" in json_result.output
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not list(tmp_path.rglob("*.sqlite*"))
    assert not list(tmp_path.rglob("fashion-radar-*.json"))
    assert not list(tmp_path.rglob("fashion-radar-*.md"))
    assert not list(tmp_path.rglob("latest.*"))
    assert not list(tmp_path.rglob("report-index.json"))
