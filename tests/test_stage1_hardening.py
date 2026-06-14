from importlib import resources
from pathlib import Path

from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.settings import ConfigError, load_entity_config, load_source_config


def test_init_uses_packaged_templates(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"

    result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
        ],
    )

    assert result.exit_code == 0
    assert "Fashionista" in (config_dir / "sources.yaml").read_text(encoding="utf-8")


def test_root_example_configs_match_packaged_templates() -> None:
    root_config_dir = Path(__file__).resolve().parents[1] / "configs"
    template_files = resources.files("fashion_radar.templates.configs")

    for name in ("sources", "entities", "scoring"):
        root_text = (root_config_dir / f"{name}.example.yaml").read_text(encoding="utf-8")
        package_text = template_files.joinpath(f"{name}.example.yaml").read_text(encoding="utf-8")
        assert root_text == package_text


def test_doctor_fails_when_required_config_files_are_missing(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    data_dir.mkdir()
    reports_dir.mkdir()

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Missing required config" in result.output


def test_doctor_reports_invalid_config_without_traceback(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    init_result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    assert init_result.exit_code == 0
    (config_dir / "entities.yaml").write_text("version: 1\nentities: nope\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid entities config" in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_malformed_yaml_without_traceback(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    init_result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    assert init_result.exit_code == 0
    (config_dir / "sources.yaml").write_text("version: 1\nsources: [\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid sources config" in result.output
    assert "Invalid YAML" in result.output
    assert "Traceback" not in result.output


def test_doctor_reports_missing_database_without_initializing_sqlite(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    init_result = CliRunner().invoke(
        app,
        [
            "init",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )
    assert init_result.exit_code == 0

    def fail(*_args, **_kwargs):
        raise AssertionError("doctor should not initialize or migrate SQLite")

    monkeypatch.setattr(cli_module, "create_sqlite_engine", fail)
    monkeypatch.setattr(cli_module, "initialize_schema", fail)

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Database schema: not initialized" in result.output
    assert "Traceback" not in result.output
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_source_config_rejects_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: Vogue
    type: rss
    url: https://example.com/feed.xml
    unknowable: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    try:
        load_source_config(path)
    except ConfigError as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("unknown source fields should be rejected")


def test_source_config_rejects_unknown_nested_fields(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """
version: 1
sources:
  - name: Vogue
    type: rss
    url: https://example.com/feed.xml
    http:
      timeout_seconds: 10
      unknowable: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    try:
        load_source_config(path)
    except ConfigError as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("unknown nested source fields should be rejected")


def test_safe_single_word_alias_requires_reason(tmp_path: Path) -> None:
    path = tmp_path / "entities.yaml"
    path.write_text(
        """
version: 1
entities:
  - name: Zendaya
    type: celebrity
    aliases:
      - value: Zendaya
        safe_single_word: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    try:
        load_entity_config(path)
    except ConfigError as exc:
        assert "safe_single_word aliases require a reason" in str(exc)
    else:
        raise AssertionError("safe aliases without reasons should be rejected")


def test_config_version_must_be_one(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text("version: 2\nsources: []\n", encoding="utf-8")

    try:
        load_source_config(path)
    except ConfigError as exc:
        assert "Input should be 1" in str(exc)
    else:
        raise AssertionError("unsupported config versions should be rejected")
