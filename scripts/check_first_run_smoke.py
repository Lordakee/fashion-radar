#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AS_OF = "2026-06-13T12:00:00Z"
SOURCE_NAME = "Community Tool Export"
EXAMPLE_CSV = Path("examples/community-signals.example.csv")
DIR_EXPORT_CSV = "community-signals.csv"
DIR_PATTERN = "*.csv"


class SmokeError(Exception):
    """Raised when the first-run smoke check fails."""


@dataclass(frozen=True)
class SmokeContext:
    repo_root: Path
    python: str
    runtime_dir: Path
    config_dir: Path
    data_dir: Path
    reports_dir: Path
    exports_dir: Path
    source_checkout: bool = True


def cli_command(context: SmokeContext, *args: str) -> list[str]:
    return [context.python, "-m", "fashion_radar", *args]


def command_environment(
    context: SmokeContext,
    base_env: Mapping[str, str] | None = None,
    *,
    source_checkout: bool = True,
) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    if not source_checkout:
        remove_pythonpath_entry(env, context.repo_root / "src", relative_to=context.repo_root)
        return env

    src_path = str(context.repo_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not existing_pythonpath else os.pathsep.join([src_path, existing_pythonpath])
    )
    return env


def remove_pythonpath_entry(env: dict[str, str], entry: Path, *, relative_to: Path) -> None:
    pythonpath = env.get("PYTHONPATH")
    if not pythonpath:
        return

    target = entry.resolve()
    kept = [
        value
        for value in pythonpath.split(os.pathsep)
        if value and resolve_pythonpath_entry(value, relative_to=relative_to) != target
    ]
    if kept:
        env["PYTHONPATH"] = os.pathsep.join(kept)
    else:
        env.pop("PYTHONPATH", None)


def resolve_pythonpath_entry(value: str, *, relative_to: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = relative_to / path
    return path.resolve()


def validate_json_output(command_name: str, output: str) -> Any:
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"{command_name} output is not valid JSON: {exc}") from exc


def validate_imported_summary(command_name: str, payload: Any) -> None:
    row_count = imported_summary_row_count(payload)
    if row_count <= 0:
        raise SmokeError(f"{command_name} must report at least one imported row")


def imported_summary_row_count(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 0

    top_level_row_count = payload.get("row_count")
    if isinstance(top_level_row_count, int) and not isinstance(top_level_row_count, bool):
        return top_level_row_count

    sources = payload.get("sources")
    if not isinstance(sources, list):
        return 0

    total = 0
    found_count = False
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_row_count = source.get("row_count")
        if isinstance(source_row_count, int) and not isinstance(source_row_count, bool):
            total += source_row_count
            found_count = True
    return total if found_count else 0


def report_paths(context: SmokeContext) -> tuple[Path, Path]:
    report_date = AS_OF.split("T", 1)[0]
    return (
        context.reports_dir / f"fashion-radar-{report_date}.md",
        context.reports_dir / f"fashion-radar-{report_date}.json",
    )


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_default_artifacts(repo_root: Path) -> dict[Path, str]:
    artifacts: dict[Path, str] = {}
    for directory_name in ("data", "reports"):
        directory = repo_root / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                artifacts[path.relative_to(repo_root)] = file_digest(path)
    return artifacts


def assert_default_artifacts_unchanged(repo_root: Path, before: dict[Path, str]) -> None:
    after = snapshot_default_artifacts(repo_root)
    before_paths = set(before)
    after_paths = set(after)
    created = sorted(after_paths - before_paths)
    deleted = sorted(before_paths - after_paths)
    changed = sorted(path for path in before_paths & after_paths if before[path] != after[path])
    if not (created or deleted or changed):
        return

    changes: list[str] = []
    if created:
        changes.append(f"created: {format_paths(created)}")
    if changed:
        changes.append(f"changed: {format_paths(changed)}")
    if deleted:
        changes.append(f"deleted: {format_paths(deleted)}")
    raise SmokeError(f"Smoke changed files under default data/reports ({'; '.join(changes)})")


def format_paths(paths: Sequence[Path]) -> str:
    return ", ".join(path.as_posix() for path in paths)


def run_cli(context: SmokeContext, *args: str) -> subprocess.CompletedProcess[str]:
    command = cli_command(context, *args)
    completed = subprocess.run(
        command,
        cwd=context.repo_root,
        env=command_environment(context, source_checkout=context.source_checkout),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeError(format_command_failure(command, completed))
    return completed


def format_command_failure(
    command: Sequence[str],
    completed: subprocess.CompletedProcess[str],
) -> str:
    command_text = " ".join(shlex.quote(part) for part in command)
    stdout = completed.stdout.strip() or "<empty>"
    stderr = completed.stderr.strip() or "<empty>"
    return (
        f"Command failed with exit code {completed.returncode}: {command_text}\n"
        f"stdout:\n{stdout}\n"
        f"stderr:\n{stderr}"
    )


def prepare_directory_export(context: SmokeContext) -> Path:
    source = context.repo_root / EXAMPLE_CSV
    if not source.is_file():
        raise SmokeError(f"Missing example CSV: {source}")
    context.exports_dir.mkdir(parents=True, exist_ok=True)
    destination = context.exports_dir / DIR_EXPORT_CSV
    shutil.copyfile(source, destination)
    return destination


def assert_non_empty_file(path: Path) -> None:
    if not path.is_file():
        raise SmokeError(f"Expected file was not created: {path}")
    if path.stat().st_size <= 0:
        raise SmokeError(f"Expected file is empty: {path}")


def run_smoke(context: SmokeContext) -> None:
    before_default_artifacts = snapshot_default_artifacts(context.repo_root)
    flow_error: SmokeError | None = None

    try:
        run_first_run_flow(context)
    except SmokeError as exc:
        flow_error = exc

    try:
        assert_default_artifacts_unchanged(context.repo_root, before_default_artifacts)
    except SmokeError as artifact_error:
        if flow_error is not None:
            raise SmokeError(f"{flow_error}\n{artifact_error}") from flow_error
        raise

    if flow_error is not None:
        raise flow_error


def run_first_run_flow(context: SmokeContext) -> None:
    example_csv = context.repo_root / EXAMPLE_CSV
    if not example_csv.is_file():
        raise SmokeError(f"Missing example CSV: {example_csv}")

    run_cli(
        context,
        "init",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
    )
    run_cli(context, "migrate-db", "--data-dir", str(context.data_dir))
    assert_workspace_artifacts(context)
    run_cli(
        context,
        "doctor",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
    )
    run_cli(
        context,
        "community-signal-lint",
        str(example_csv),
        "--input-format",
        "csv",
        "--source-name",
        SOURCE_NAME,
    )
    validate_json_output(
        "community-candidates",
        run_cli(
            context,
            "community-candidates",
            str(example_csv),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    run_cli(
        context,
        "import-signals",
        str(example_csv),
        "--data-dir",
        str(context.data_dir),
        "--format",
        "csv",
        "--source-name",
        SOURCE_NAME,
        "--dry-run",
    )
    run_cli(
        context,
        "import-signals",
        str(example_csv),
        "--data-dir",
        str(context.data_dir),
        "--format",
        "csv",
        "--source-name",
        SOURCE_NAME,
        "--imported-at",
        AS_OF,
    )
    imported_summary = validate_json_output(
        "imported-signals-summary",
        run_cli(
            context,
            "imported-signals-summary",
            "--data-dir",
            str(context.data_dir),
            "--format",
            "json",
        ).stdout,
    )
    validate_imported_summary("imported-signals-summary", imported_summary)
    validate_json_output(
        "imported-signals",
        run_cli(
            context,
            "imported-signals",
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    run_cli(
        context,
        "match",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
    )
    run_cli(
        context,
        "report",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
        "--as-of",
        AS_OF,
    )
    markdown_path, json_path = report_paths(context)
    assert_non_empty_file(markdown_path)
    assert_non_empty_file(json_path)
    validate_json_output("report JSON", json_path.read_text(encoding="utf-8"))
    validate_json_output(
        "candidates",
        run_cli(
            context,
            "candidates",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )
    validate_json_output(
        "trends",
        run_cli(
            context,
            "trends",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )

    prepare_directory_export(context)
    run_cli(
        context,
        "community-handoff-workflow",
        str(context.exports_dir),
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--input-format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--as-of",
        AS_OF,
        "--source-name",
        SOURCE_NAME,
    )
    run_cli(
        context,
        "community-signal-lint-dir",
        str(context.exports_dir),
        "--input-format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--source-name",
        SOURCE_NAME,
    )
    validate_json_output(
        "community-candidates-dir",
        run_cli(
            context,
            "community-candidates-dir",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--pattern",
            DIR_PATTERN,
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    run_cli(
        context,
        "import-signals-dir",
        str(context.exports_dir),
        "--data-dir",
        str(context.data_dir),
        "--format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--source-name",
        SOURCE_NAME,
        "--dry-run",
    )


def assert_workspace_artifacts(context: SmokeContext) -> None:
    for directory in (context.config_dir, context.data_dir, context.reports_dir):
        if not directory.is_dir():
            raise SmokeError(f"Expected directory was not created: {directory}")

    database_path = context.data_dir / "fashion-radar.sqlite"
    if not database_path.is_file():
        raise SmokeError(f"Expected SQLite database was not created: {database_path}")


def assert_installed_import_origin(context: SmokeContext, module_file: Path) -> None:
    source_root = (context.repo_root / "src").resolve()
    resolved_file = module_file.resolve()
    if resolved_file == source_root or source_root in resolved_file.parents:
        raise SmokeError(
            f"Installed smoke imported fashion_radar from source checkout: {resolved_file}"
        )


def installed_import_origin(context: SmokeContext) -> Path:
    command = [
        context.python,
        "-c",
        (
            "import fashion_radar, json, pathlib; "
            "print(json.dumps({'module_file': "
            "str(pathlib.Path(fashion_radar.__file__).resolve())}))"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=context.repo_root,
        env=command_environment(context, source_checkout=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeError(format_command_failure(command, completed))

    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(output_lines) != 1:
        raise SmokeError("Installed smoke import-origin preflight returned no module path")
    try:
        payload = json.loads(output_lines[0])
    except json.JSONDecodeError as exc:
        raise SmokeError(
            f"Installed smoke import-origin preflight returned invalid JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SmokeError("Installed smoke import-origin preflight returned invalid payload")
    module_file = payload.get("module_file")
    if not isinstance(module_file, str) or not module_file:
        raise SmokeError("Installed smoke import-origin preflight returned no module path")
    return Path(module_file)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local first-run sample smoke flow.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to run the smoke check against.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run `-m fashion_radar`.",
    )
    parser.add_argument(
        "--installed",
        action="store_true",
        help=(
            "Run against the supplied installed Python environment without "
            "prepending repo_root/src to PYTHONPATH."
        ),
    )
    return parser.parse_args(argv)


def build_context(
    repo_root: Path,
    python: str,
    runtime_dir: Path,
    *,
    source_checkout: bool = True,
) -> SmokeContext:
    return SmokeContext(
        repo_root=repo_root,
        python=python,
        runtime_dir=runtime_dir,
        config_dir=runtime_dir / "config",
        data_dir=runtime_dir / "data",
        reports_dir=runtime_dir / "reports",
        exports_dir=runtime_dir / "exports",
        source_checkout=source_checkout,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    try:
        with tempfile.TemporaryDirectory(prefix="fashion-radar-first-run-") as temp_dir:
            context = build_context(
                repo_root,
                args.python,
                Path(temp_dir),
                source_checkout=not args.installed,
            )
            if args.installed:
                assert_installed_import_origin(context, installed_import_origin(context))
            run_smoke(context)
    except SmokeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"First-run sample smoke failed: {exc}", file=sys.stderr)
        return 1

    print("First-run sample smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
