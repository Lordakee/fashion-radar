from datetime import UTC, datetime
from pathlib import Path

import pytest

from fashion_radar.community_handoff_workflow import (
    CommunityHandoffWorkflow,
    CommunityHandoffWorkflowStep,
    build_community_handoff_workflow,
    render_community_handoff_workflow_table,
)


def test_build_community_handoff_workflow_returns_deterministic_steps() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
        source_name="Community Tool Export",
    )

    assert workflow.directory == "exports"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.input_format == "csv"
    assert workflow.pattern == "*.csv"
    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.source_name == "Community Tool Export"
    assert workflow.execution_mode == "print_only"
    assert workflow.step_count == 5
    assert [step.name for step in workflow.steps] == [
        "lint_handoff_directory",
        "preview_candidate_phrases",
        "dry_run_directory_import",
        "import_directory_signals",
        "print_post_import_review",
    ]
    assert [step.suggested_effect for step in workflow.steps] == [
        "read_only",
        "read_only",
        "read_only",
        "updates_local_imports",
        "print_only",
    ]
    assert workflow.steps[0].command == (
        "fashion-radar community-signal-lint-dir exports --input-format csv "
        "--pattern '*.csv' --source-name 'Community Tool Export' --strict"
    )
    assert workflow.steps[1].command == (
        "fashion-radar community-candidates-dir exports --input-format csv "
        "--pattern '*.csv' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Community Tool Export'"
    )
    assert workflow.steps[2].command == (
        "fashion-radar import-signals-dir exports --format csv --pattern '*.csv' "
        "--data-dir data --source-name 'Community Tool Export' "
        "--imported-at 2026-06-13T12:00:00+00:00 --dry-run"
    )
    assert workflow.steps[3].command == (
        "fashion-radar import-signals-dir exports --format csv --pattern '*.csv' "
        "--data-dir data --source-name 'Community Tool Export' "
        "--imported-at 2026-06-13T12:00:00+00:00"
    )
    assert workflow.steps[4].command == (
        "fashion-radar imported-review-workflow --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"
    )


def test_build_community_handoff_workflow_quotes_paths_pattern_and_source_name() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        input_format="json",
        pattern="*.json",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community | Tool Export",
    )

    assert workflow.source_name == "Community | Tool Export"
    assert "'exports ? # & %'" in workflow.steps[0].command
    assert "--pattern '*.json'" in workflow.steps[0].command
    assert "--source-name 'Community | Tool Export'" in workflow.steps[0].command
    assert "--config-dir 'config ? # & %'" in workflow.steps[1].command
    assert "--data-dir 'data ? # & %'" in workflow.steps[2].command


def test_build_community_handoff_workflow_blank_source_name_uses_default() -> None:
    workflow = build_community_handoff_workflow(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name=" ",
    )

    assert workflow.source_name == "Community Tool Export"
    assert "--source-name 'Community Tool Export'" in workflow.steps[0].command


def test_build_community_handoff_workflow_invalid_as_of_raises() -> None:
    with pytest.raises(ValueError):
        build_community_handoff_workflow(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            input_format="csv",
            pattern="*.csv",
            as_of="not-a-date",
            source_name="Community Tool Export",
        )


def test_render_community_handoff_workflow_table_sanitizes_cells() -> None:
    workflow = CommunityHandoffWorkflow(
        directory="./exports",
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        source_name="Community | Tool",
        step_count=1,
        steps=[
            CommunityHandoffWorkflowStep(
                order=1,
                name="first | step\nname",
                purpose="Read | local\nstate.",
                command=(
                    "fashion-radar community-signal-lint-dir ./exports "
                    "--source-name 'A | B'\n--strict"
                ),
                suggested_effect="read_only",
            )
        ],
    )

    assert render_community_handoff_workflow_table(workflow) == [
        "Community signal handoff workflow.",
        "Execution mode: print_only",
        "Commands were not executed.",
        "Directory: ./exports",
        "Input format: csv",
        "Pattern: *.csv",
        "As of: 2026-06-13T12:00:00+00:00",
        "Config dir: ./configs",
        "Data dir: ./data",
        "Source name: Community / Tool",
        "Steps: 1",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | first / step name | read_only | Read / local state. | "
        "fashion-radar community-signal-lint-dir ./exports --source-name 'A / B' --strict",
    ]
