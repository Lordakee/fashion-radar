#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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
EXPECTED_SAMPLE_ROWS = (
    {
        "url": "https://example.com/community/the-row-margaux-tote",
        "title": "The Row Margaux tote interest",
        "published_at": "2026-06-12T08:00:00Z",
        "summary": "Sanitized local note about The Row Margaux handbag and tote demand",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.3",
        "collected_at": "2026-06-12T08:30:00Z",
    },
    {
        "url": "https://example.com/community/ballet-flats-footwear",
        "title": "Ballet flats footwear mention",
        "published_at": "2026-06-12T09:00:00Z",
        "summary": "Short sanitized note about ballet flats shoes and footwear styling",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.1",
        "collected_at": "2026-06-12T09:20:00Z",
    },
)
EXPECTED_SAMPLE_TITLES = tuple(row["title"] for row in EXPECTED_SAMPLE_ROWS)
EXPECTED_SAMPLE_ENTITIES = ("The Row", "The Row Margaux", "Ballet Flats")
EXPECTED_PLATFORM_COUNTS = {"community": 2}
EXPECTED_SOURCE_COUNTS = {SOURCE_NAME: 2}
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS = (
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_imported_candidate_phrases",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
)
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS = (
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)


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


def assert_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise SmokeError(f"{label} expected {expected!r}, got {actual!r}")


def validate_sample_csv(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert_equal("sample CSV row count", len(rows), len(EXPECTED_SAMPLE_ROWS))
    for index, expected in enumerate(EXPECTED_SAMPLE_ROWS):
        row = rows[index]
        for key, expected_value in expected.items():
            assert_equal(
                f"sample CSV row {index + 1} {key}",
                row.get(key),
                expected_value,
            )


def validate_community_candidates(
    command_name: str,
    payload: Any,
    *,
    directory: bool = False,
) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "csv")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} candidate_count", payload.get("candidate_count"), 0)
    assert_equal(f"{command_name} candidates", payload.get("candidates"), [])
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    if directory:
        assert_equal(f"{command_name} file_count", payload.get("file_count"), 1)


def assert_output_contains(command_name: str, output: str, expected_lines: Sequence[str]) -> None:
    output_lines = {line.strip() for line in output.splitlines() if line.strip()}
    for expected in expected_lines:
        if expected not in output_lines:
            raise SmokeError(f"{command_name} output missing expected text: {expected}")


def validate_import_signals_dry_run(output: str) -> None:
    assert_output_contains(
        "import-signals --dry-run",
        output,
        ("Validated 2 manual signal rows", "Dry run: no rows imported"),
    )


def validate_import_signals_import(output: str) -> None:
    assert_output_contains(
        "import-signals",
        output,
        ("Validated 2 manual signal rows", "Imported 2 manual signal rows", "Items added: 2"),
    )


def validate_import_signals_dir_dry_run(output: str) -> None:
    output_lines = {line.strip() for line in output.splitlines() if line.strip()}
    assert_output_contains(
        "import-signals-dir --dry-run",
        output,
        (
            "Files: 1 total, 1 valid",
            "Rows: 2 import-ready",
            "Sources: Community Tool Export=2",
            "Platforms: community=2",
            "Errors: 0",
            "No manual signal directory dry-run errors.",
        ),
    )
    expected_file_suffix = f"{DIR_EXPORT_CSV}: 2 rows, 0 errors"
    if not any(line.endswith(expected_file_suffix) for line in output_lines):
        raise SmokeError(
            f"import-signals-dir --dry-run output missing expected text: {expected_file_suffix}"
        )


def validate_imported_summary(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")

    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} source_count", payload.get("source_count"), 1)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(
        f"{command_name} platform_counts",
        payload.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 1:
        raise SmokeError(f"{command_name} must report exactly one source")
    source = sources[0]
    if not isinstance(source, dict):
        raise SmokeError(f"{command_name} source summary must be a JSON object")
    assert_equal(f"{command_name} source name", source.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} source row_count", source.get("row_count"), 2)
    assert_equal(f"{command_name} source matched_count", source.get("matched_count"), 2)


def validate_imported_signals(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} total_count", payload.get("total_count"), 2)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(
        f"{command_name} source_name_counts",
        payload.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} platform_counts",
        payload.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise SmokeError(f"{command_name} must contain exactly two sample items")

    titles = [item.get("title") for item in items if isinstance(item, dict)]
    assert_equal(
        f"{command_name} item titles",
        titles,
        ["Ballet flats footwear mention", "The Row Margaux tote interest"],
    )

    matches_by_title: dict[str, set[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("match_status") != "matched":
            raise SmokeError(f"{command_name} item must be marked matched: {item.get('title')}")
        matches = item.get("matches")
        if not isinstance(matches, list):
            matches = []
        matches_by_title[str(item.get("title"))] = {
            str(match.get("entity_name"))
            for match in matches
            if isinstance(match, dict) and match.get("entity_name") is not None
        }

    for title in EXPECTED_SAMPLE_TITLES:
        if title not in matches_by_title:
            raise SmokeError(f"{command_name} missing sample title: {title}")
    if "Ballet Flats" not in matches_by_title["Ballet flats footwear mention"]:
        raise SmokeError(f"{command_name} missing Ballet Flats match")
    row_matches = matches_by_title["The Row Margaux tote interest"]
    for expected_entity in ("The Row", "The Row Margaux"):
        if expected_entity not in row_matches:
            raise SmokeError(f"{command_name} missing {expected_entity} match")


def validate_imported_review_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 6)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS),
    )

    candidate_step = steps[3]
    if not isinstance(candidate_step, dict):
        raise SmokeError(f"{command_name} candidate step must be a JSON object")
    candidate_command = str(candidate_step.get("command", ""))
    for expected in (
        "fashion-radar imported-candidates",
        "--config-dir",
        "--data-dir",
        "--as-of",
        "--source-name",
        SOURCE_NAME,
    ):
        if expected not in candidate_command:
            raise SmokeError(f"{command_name} candidate command missing {expected!r}")

    heat_step = steps[-1]
    if not isinstance(heat_step, dict):
        raise SmokeError(f"{command_name} heat step must be a JSON object")
    assert_equal(f"{command_name} final step", heat_step.get("name"), "review_local_heat_movers")
    heat_command = str(heat_step.get("command", ""))
    if "fashion-radar heat-movers" not in heat_command:
        raise SmokeError(f"{command_name} final heat command missing heat-movers")
    if "--source-name" in heat_command:
        raise SmokeError(f"{command_name} final heat command must not include --source-name")


def validate_community_handoff_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 6)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS),
    )

    readiness_step = steps[2]
    if not isinstance(readiness_step, dict):
        raise SmokeError(f"{command_name} readiness step must be a JSON object")
    readiness_command = str(readiness_step.get("command", ""))
    for expected in (
        "fashion-radar community-handoff-check-dir",
        "--input-format",
        "--pattern",
        "--config-dir",
        "--as-of",
        "--source-name",
        SOURCE_NAME,
        "--strict",
    ):
        if expected not in readiness_command:
            raise SmokeError(f"{command_name} readiness command missing {expected!r}")

    import_step = steps[4]
    if not isinstance(import_step, dict):
        raise SmokeError(f"{command_name} import step must be a JSON object")
    assert_equal(
        f"{command_name} import step effect",
        import_step.get("suggested_effect"),
        "updates_local_imports",
    )

    post_review_step = steps[5]
    if not isinstance(post_review_step, dict):
        raise SmokeError(f"{command_name} post-review step must be a JSON object")
    assert_equal(
        f"{command_name} post-review step effect",
        post_review_step.get("suggested_effect"),
        "print_only",
    )


def validate_external_tool_adapters(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(
        f"{command_name} contract_version",
        payload.get("contract_version"),
        "external-tool-adapters/v1",
    )
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    adapters = payload.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        raise SmokeError(f"{command_name} adapters must be a non-empty list")
    first_adapter = adapters[0]
    if not isinstance(first_adapter, dict):
        raise SmokeError(f"{command_name} first adapter must be a JSON object")
    assert_equal(f"{command_name} first adapter id", first_adapter.get("id"), "rednote_mcp")


def validate_report_outputs(json_payload: Any, markdown_text: str) -> None:
    if not isinstance(json_payload, dict):
        raise SmokeError("report JSON output must be a JSON object")
    metadata = json_payload.get("metadata")
    if not isinstance(metadata, dict):
        raise SmokeError("report JSON missing metadata")
    assert_equal("report metadata item_count", metadata.get("item_count"), 3)
    entities = json_payload.get("entities")
    if not isinstance(entities, list):
        raise SmokeError("report JSON entities must be a list")
    entity_names = [entity.get("entity_name") for entity in entities if isinstance(entity, dict)]
    assert_equal("report entity names", entity_names, list(EXPECTED_SAMPLE_ENTITIES))
    for expected in EXPECTED_SAMPLE_ENTITIES:
        if f"### {expected} (new)" not in markdown_text:
            raise SmokeError(f"report Markdown missing sample entity section: {expected}")
    if "No entity signals in this window." in markdown_text:
        raise SmokeError("report Markdown should not contain the empty entity signal message")


def validate_candidates(command_name: str, payload: Any, report_payload: Any) -> None:
    assert_equal(f"{command_name} candidates", payload, [])
    if isinstance(report_payload, dict):
        assert_equal("report candidates", report_payload.get("candidates"), payload)


def validate_trends(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00Z")
    deltas = payload.get("deltas")
    if not isinstance(deltas, list):
        raise SmokeError(f"{command_name} deltas must be a list")
    expected_types = {
        "The Row": "brand",
        "The Row Margaux": "product",
        "Ballet Flats": "category",
    }
    deltas_by_name = {str(delta.get("name")): delta for delta in deltas if isinstance(delta, dict)}
    assert_equal(
        f"{command_name} entity delta names",
        list(deltas_by_name),
        list(EXPECTED_SAMPLE_ENTITIES),
    )
    for name, signal_type in expected_types.items():
        delta = deltas_by_name[name]
        assert_equal(f"{command_name} {name} signal_kind", delta.get("signal_kind"), "entity")
        assert_equal(f"{command_name} {name} signal_type", delta.get("signal_type"), signal_type)
        assert_equal(f"{command_name} {name} status", delta.get("status"), "new")


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
    validate_sample_csv(example_csv)

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
    external_tool_adapters = validate_json_output(
        "external-tool-adapters",
        run_cli(context, "external-tool-adapters", "--format", "json").stdout,
    )
    validate_external_tool_adapters("external-tool-adapters", external_tool_adapters)
    run_cli(
        context,
        "community-signal-lint",
        str(example_csv),
        "--input-format",
        "csv",
        "--source-name",
        SOURCE_NAME,
    )
    community_candidates = validate_json_output(
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
    validate_community_candidates("community-candidates", community_candidates)
    validate_import_signals_dry_run(
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
        ).stdout
    )
    validate_import_signals_import(
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
        ).stdout
    )
    run_cli(
        context,
        "match",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
    )
    imported_review_workflow = validate_json_output(
        "imported-review-workflow",
        run_cli(
            context,
            "imported-review-workflow",
            "--config-dir",
            str(context.config_dir),
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
    validate_imported_review_workflow("imported-review-workflow", imported_review_workflow)
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
    imported_signals = validate_json_output(
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
    validate_imported_signals("imported-signals", imported_signals)
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
    report_payload = validate_json_output("report JSON", json_path.read_text(encoding="utf-8"))
    validate_report_outputs(report_payload, markdown_path.read_text(encoding="utf-8"))
    candidates_payload = validate_json_output(
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
    validate_candidates("candidates", candidates_payload, report_payload)
    trends_payload = validate_json_output(
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
    validate_trends("trends", trends_payload)

    prepare_directory_export(context)
    community_handoff_workflow = validate_json_output(
        "community-handoff-workflow",
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
            "--format",
            "json",
        ).stdout,
    )
    validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow,
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
    community_candidates_dir = validate_json_output(
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
    validate_community_candidates(
        "community-candidates-dir",
        community_candidates_dir,
        directory=True,
    )
    validate_import_signals_dir_dry_run(
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
        ).stdout
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
