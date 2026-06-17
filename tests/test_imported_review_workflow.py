from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.imported_review_workflow import (
    ImportedReviewWorkflow,
    ImportedReviewWorkflowStep,
    build_imported_review_workflow,
    render_imported_review_workflow_table,
)


def test_build_imported_review_workflow_returns_deterministic_steps() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of=datetime(2026, 6, 13, 12, 0, tzinfo=UTC),
    )

    assert workflow.as_of == "2026-06-13T12:00:00+00:00"
    assert workflow.config_dir == "configs"
    assert workflow.data_dir == "data"
    assert workflow.source_name is None
    assert workflow.lookback_days == 7
    assert workflow.current_days == 7
    assert workflow.baseline_days == 7
    assert workflow.execution_mode == "print_only"
    assert workflow.step_count == 7
    assert [step.order for step in workflow.steps] == [1, 2, 3, 4, 5, 6, 7]
    assert [step.name for step in workflow.steps] == [
        "summarize_imported_sources",
        "refresh_stored_matches",
        "compare_imported_entities",
        "review_imported_entity_evidence",
        "review_imported_candidate_phrases",
        "review_unmatched_imported_rows",
        "review_local_heat_movers",
    ]
    assert [step.suggested_effect for step in workflow.steps] == [
        "read_only",
        "updates_local_matches",
        "read_only",
        "read_only",
        "read_only",
        "read_only",
        "read_only",
    ]
    assert workflow.steps[0].command == ("fashion-radar imported-signals-summary --data-dir data")
    assert workflow.steps[1].command == ("fashion-radar match --config-dir configs --data-dir data")
    assert workflow.steps[2].command == (
        "fashion-radar imported-entity-deltas --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --current-days 7 --baseline-days 7"
    )
    assert workflow.steps[3].command == (
        "fashion-radar imported-entity-evidence --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' --entity-type brand "
        "--current-days 7 --baseline-days 7"
    )
    assert workflow.steps[3].purpose == (
        "Review retained imported rows behind one selected matched entity."
    )
    assert workflow.steps[4].command == (
        "fashion-radar imported-candidates --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00"
    )
    assert workflow.steps[4].purpose == (
        "Review observed candidate phrases from retained imported rows after stored "
        "matches are refreshed."
    )
    assert workflow.steps[5].command == (
        "fashion-radar imported-signals --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 --unmatched-only"
    )
    assert workflow.steps[6].command == (
        "fashion-radar heat-movers --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00"
    )


def test_build_imported_review_workflow_quotes_paths_and_source_name() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Community | Tool Export",
        lookback_days=3,
        current_days=5,
        baseline_days=9,
    )

    assert workflow.source_name == "Community | Tool Export"
    assert workflow.steps[0].command == (
        "fashion-radar imported-signals-summary --data-dir 'data ? # & %'"
    )
    assert workflow.steps[1].command == (
        "fashion-radar match --config-dir 'config ? # & %' --data-dir 'data ? # & %'"
    )
    assert workflow.steps[2].command == (
        "fashion-radar imported-entity-deltas --data-dir 'data ? # & %' "
        "--as-of 2026-06-13T12:00:00+00:00 --current-days 5 --baseline-days 9 "
        "--source-name 'Community | Tool Export'"
    )
    assert workflow.steps[3].command == (
        "fashion-radar imported-entity-evidence --data-dir 'data ? # & %' "
        "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' --entity-type brand "
        "--current-days 5 --baseline-days 9 --source-name 'Community | Tool Export'"
    )
    assert workflow.steps[4].command == (
        "fashion-radar imported-candidates --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Community | Tool Export'"
    )
    assert workflow.steps[5].command == (
        "fashion-radar imported-signals --data-dir 'data ? # & %' "
        "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 3 --unmatched-only "
        "--source-name 'Community | Tool Export'"
    )
    assert workflow.steps[6].command == (
        "fashion-radar heat-movers --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00"
    )
    assert "--source-name" not in workflow.steps[6].command


def test_build_imported_review_workflow_blank_source_name_is_no_filter() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name=" ",
    )

    assert workflow.source_name is None
    assert "--source-name" not in workflow.steps[2].command
    assert "--source-name" not in workflow.steps[3].command
    assert "--source-name" not in workflow.steps[4].command
    assert "--source-name" not in workflow.steps[5].command
    assert "--source-name" not in workflow.steps[6].command


def test_render_imported_review_workflow_table() -> None:
    workflow = ImportedReviewWorkflow(
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        step_count=4,
        steps=[
            ImportedReviewWorkflowStep(
                order=1,
                name="first | step\nname",
                purpose="Read | local\nstate.",
                command=(
                    "fashion-radar imported-signals-summary --data-dir ./data --source-name 'A | B'"
                ),
                suggested_effect="read_only",
            ),
            ImportedReviewWorkflowStep(
                order=2,
                name="refresh_stored_matches",
                purpose="Refresh stored local matches.",
                command="fashion-radar match --config-dir ./configs --data-dir ./data",
                suggested_effect="updates_local_matches",
            ),
            ImportedReviewWorkflowStep(
                order=3,
                name="review_imported_candidate_phrases",
                purpose="Review imported candidate phrases.",
                command=(
                    "fashion-radar imported-candidates --config-dir ./configs --data-dir ./data "
                    "--as-of 2026-06-13T12:00:00+00:00"
                ),
                suggested_effect="read_only",
            ),
            ImportedReviewWorkflowStep(
                order=4,
                name="review_local_heat_movers",
                purpose="Review local observed heat movement.",
                command=(
                    "fashion-radar heat-movers --config-dir ./configs --data-dir ./data "
                    "--as-of 2026-06-13T12:00:00+00:00"
                ),
                suggested_effect="read_only",
            ),
        ],
    )

    assert render_imported_review_workflow_table(workflow) == [
        "Imported manual signal review workflow.",
        "Execution mode: print_only",
        "Commands were not executed.",
        "As of: 2026-06-13T12:00:00+00:00",
        "Data dir: ./data",
        "Config dir: ./configs",
        "Source name: none",
        "Lookback days: 7",
        "Current days: 7",
        "Baseline days: 7",
        "Steps: 4",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | first / step name | read_only | Read / local state. | fashion-radar "
        "imported-signals-summary --data-dir ./data --source-name 'A | B'",
        "2 | refresh_stored_matches | updates_local_matches | Refresh stored local matches. | "
        "fashion-radar match --config-dir ./configs --data-dir ./data",
        "3 | review_imported_candidate_phrases | read_only | "
        "Review imported candidate phrases. | fashion-radar imported-candidates --config-dir "
        "./configs --data-dir ./data --as-of 2026-06-13T12:00:00+00:00",
        "4 | review_local_heat_movers | read_only | Review local observed heat movement. | "
        "fashion-radar heat-movers --config-dir ./configs --data-dir ./data --as-of "
        "2026-06-13T12:00:00+00:00",
    ]


def test_render_imported_review_workflow_table_source_name() -> None:
    workflow = build_imported_review_workflow(
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )

    lines = render_imported_review_workflow_table(workflow)

    assert "Source name: Community Tool Export" in lines
