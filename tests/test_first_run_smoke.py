from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_first_run_smoke.py"


def load_smoke_module():
    spec = importlib.util.spec_from_file_location("check_first_run_smoke", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


smoke = load_smoke_module()


def make_context(tmp_path: Path, *, python: str = "python-test"):
    runtime_dir = tmp_path / "runtime"
    return smoke.SmokeContext(
        repo_root=tmp_path,
        python=python,
        runtime_dir=runtime_dir,
        config_dir=runtime_dir / "config",
        data_dir=runtime_dir / "data",
        reports_dir=runtime_dir / "reports",
        exports_dir=runtime_dir / "exports",
    )


def test_constants_pin_first_run_sample_inputs() -> None:
    assert smoke.AS_OF == "2026-06-13T12:00:00Z"
    assert smoke.SOURCE_NAME == "Community Tool Export"
    assert smoke.EXAMPLE_CSV == Path("examples/community-signals.example.csv")


def test_cli_command_runs_fashion_radar_module(tmp_path: Path) -> None:
    context = make_context(tmp_path, python="/venv/bin/python")

    command = smoke.cli_command(context, "doctor", "--data-dir", "data")

    assert command == ["/venv/bin/python", "-m", "fashion_radar", "doctor", "--data-dir", "data"]


def test_command_environment_prepends_src_and_preserves_pythonpath(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/already/here")

    env = smoke.command_environment(context)

    assert env["PYTHONPATH"].split(os.pathsep)[:2] == [
        str(tmp_path / "src"),
        "/already/here",
    ]


def test_command_environment_sets_pythonpath_when_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.delenv("PYTHONPATH", raising=False)

    env = smoke.command_environment(context)

    assert env["PYTHONPATH"] == str(tmp_path / "src")


def test_validate_json_output_rejects_invalid_json() -> None:
    with pytest.raises(smoke.SmokeError, match="not valid JSON"):
        smoke.validate_json_output("community-candidates", "not json")


def test_validate_imported_summary_requires_at_least_one_imported_row() -> None:
    smoke.validate_imported_summary(
        "imported-signals-summary",
        {"row_count": 1, "sources": []},
    )
    smoke.validate_imported_summary(
        "imported-signals-summary",
        {"sources": [{"source_name": "Community Tool Export", "row_count": 2}]},
    )

    with pytest.raises(smoke.SmokeError, match="at least one imported row"):
        smoke.validate_imported_summary("imported-signals-summary", {"row_count": 0})

    with pytest.raises(smoke.SmokeError, match="at least one imported row"):
        smoke.validate_imported_summary("imported-signals-summary", {"sources": []})


def test_report_paths_derive_date_from_as_of(tmp_path: Path) -> None:
    context = make_context(tmp_path)

    markdown_path, json_path = smoke.report_paths(context)

    assert markdown_path == context.reports_dir / "fashion-radar-2026-06-13.md"
    assert json_path == context.reports_dir / "fashion-radar-2026-06-13.json"


def test_default_artifact_guard_detects_new_repo_data_and_report_files(
    tmp_path: Path,
) -> None:
    before = smoke.snapshot_default_artifacts(tmp_path)
    data_file = tmp_path / "data" / "fashion-radar.sqlite"
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    data_file.parent.mkdir()
    report_file.parent.mkdir()
    data_file.write_text("sqlite", encoding="utf-8")
    report_file.write_text("{}", encoding="utf-8")

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "created:" in message
    assert "data/fashion-radar.sqlite" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_default_artifact_guard_detects_changed_repo_data_and_report_files(
    tmp_path: Path,
) -> None:
    data_file = tmp_path / "data" / "fashion-radar.sqlite"
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    data_file.parent.mkdir()
    report_file.parent.mkdir()
    data_file.write_text("before", encoding="utf-8")
    report_file.write_text('{"before": true}', encoding="utf-8")
    before = smoke.snapshot_default_artifacts(tmp_path)

    data_file.write_text("after", encoding="utf-8")
    report_file.write_text('{"after": true}', encoding="utf-8")

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "changed:" in message
    assert "data/fashion-radar.sqlite" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_default_artifact_guard_detects_deleted_repo_data_or_report_files(
    tmp_path: Path,
) -> None:
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    report_file.parent.mkdir()
    report_file.write_text("{}", encoding="utf-8")
    before = smoke.snapshot_default_artifacts(tmp_path)

    report_file.unlink()

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "deleted:" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_workspace_artifact_assertion_requires_temp_dirs_and_sqlite(tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.config_dir.mkdir(parents=True)
    context.data_dir.mkdir(parents=True)
    context.reports_dir.mkdir(parents=True)

    with pytest.raises(smoke.SmokeError, match="Expected SQLite database"):
        smoke.assert_workspace_artifacts(context)

    (context.data_dir / "fashion-radar.sqlite").write_text("sqlite", encoding="utf-8")

    smoke.assert_workspace_artifacts(context)


def test_run_first_run_flow_uses_deterministic_local_command_sequence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    example_csv = tmp_path / "examples" / "community-signals.example.csv"
    example_csv.parent.mkdir()
    example_csv.write_text(
        "url,title,published_at\nhttps://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    context = make_context(tmp_path, python=sys.executable)
    captured: list[tuple[str, ...]] = []

    def fake_run_cli(fake_context, *args: str):
        assert fake_context is context
        captured.append(args)
        command_name = args[0]
        if command_name == "init":
            context.config_dir.mkdir(parents=True)
            context.data_dir.mkdir(parents=True)
            context.reports_dir.mkdir(parents=True)
        if command_name == "migrate-db":
            context.data_dir.mkdir(parents=True, exist_ok=True)
            (context.data_dir / "fashion-radar.sqlite").write_text(
                "sqlite",
                encoding="utf-8",
            )
        if command_name == "report":
            context.reports_dir.mkdir(parents=True, exist_ok=True)
            markdown_path, json_path = smoke.report_paths(context)
            markdown_path.write_text("# Report\n", encoding="utf-8")
            json_path.write_text("{}", encoding="utf-8")

        stdout_by_command = {
            "community-candidates": '{"candidates": []}',
            "imported-signals-summary": '{"row_count": 1, "sources": []}',
            "imported-signals": "[]",
            "candidates": '{"candidates": []}',
            "trends": '{"trends": []}',
            "community-candidates-dir": '{"candidates": []}',
        }
        return subprocess.CompletedProcess(
            ["python", "-m", "fashion_radar", *args],
            0,
            stdout=stdout_by_command.get(command_name, ""),
            stderr="",
        )

    monkeypatch.setattr(smoke, "run_cli", fake_run_cli)

    smoke.run_first_run_flow(context)

    assert [command[0] for command in captured] == [
        "init",
        "migrate-db",
        "doctor",
        "community-signal-lint",
        "community-candidates",
        "import-signals",
        "import-signals",
        "imported-signals-summary",
        "imported-signals",
        "match",
        "report",
        "candidates",
        "trends",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-candidates-dir",
        "import-signals-dir",
    ]
    assert captured[0] == (
        "init",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
    )
    assert captured[1] == ("migrate-db", "--data-dir", str(context.data_dir))
    for command in captured:
        assert command[0] not in {"collect", "run", "dashboard"}
        if command[0] in {"doctor", "match", "report", "candidates", "trends"}:
            assert "--config-dir" in command
            assert str(context.config_dir) in command
        if command[0] in {
            "init",
            "migrate-db",
            "doctor",
            "import-signals",
            "imported-signals-summary",
            "imported-signals",
            "match",
            "report",
            "candidates",
            "trends",
            "community-handoff-workflow",
            "import-signals-dir",
        }:
            assert "--data-dir" in command
            assert str(context.data_dir) in command
        if command[0] in {
            "community-signal-lint",
            "community-candidates",
            "import-signals",
            "imported-signals",
            "community-handoff-workflow",
            "community-signal-lint-dir",
            "community-candidates-dir",
            "import-signals-dir",
        }:
            assert smoke.SOURCE_NAME in command
        if command[0] in {
            "community-candidates",
            "imported-signals",
            "report",
            "candidates",
            "trends",
            "community-handoff-workflow",
            "community-candidates-dir",
        } or (command[0] == "import-signals" and "--dry-run" not in command):
            assert smoke.AS_OF in command

    assert captured[13][1] == str(context.exports_dir)
    assert captured[14][1] == str(context.exports_dir)
    assert captured[15][1] == str(context.exports_dir)
    assert captured[16][1] == str(context.exports_dir)
    assert (context.exports_dir / smoke.DIR_EXPORT_CSV).read_text(encoding="utf-8") == (
        example_csv.read_text(encoding="utf-8")
    )
