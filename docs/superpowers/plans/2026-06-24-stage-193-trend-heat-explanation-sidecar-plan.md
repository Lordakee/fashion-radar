# Stage 193 Trend Heat Explanation Sidecar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new read-only `trend-explanations` sidecar command that explains why local trend deltas moved without changing existing `trends` or `heat-movers` contracts.

**Architecture:** Build a pure explanation module over `TrendComparison`, expose it through a new CLI command that reuses the existing read-only trend loading flow, and keep the sidecar contract separate from `TrendDelta` and `HeatMoversReport`. The new output is additive and standalone: existing trend and heat JSON/table outputs remain unchanged.

**Tech Stack:** Python 3.11, Pydantic, Typer, existing read-only trend comparison pipeline, pytest, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Add: `src/fashion_radar/trend_explanations.py`
- Modify: `src/fashion_radar/cli.py`
- Add: `tests/test_trend_explanations.py`
- Modify: `tests/test_cli.py`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-193-trend-heat-explanation-sidecar-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-193-trend-heat-explanation-sidecar-plan.md`
- Add after plan review: `docs/reviews/opencode-stage-193-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-193-plan-review.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-193-plan-rereview-prompt.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-193-plan-rereview.md`
- Add after implementation: `docs/reviews/opencode-stage-193-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-193-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-193-code-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-193-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-193-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-193-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-193-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-193-release-rereview.md`

## Task 1: Pure Explanation Module

**Files:**

- Add: `src/fashion_radar/trend_explanations.py`
- Add: `tests/test_trend_explanations.py`

- [ ] **Step 1: Write RED tests for the explanation builder**

Create `tests/test_trend_explanations.py` with:

```python
from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.trend_explanations import (
    TrendExplanationReport,
    build_trend_explanations,
    render_trend_explanations_table,
)

AS_OF = datetime(2026, 6, 24, 12, 0, tzinfo=UTC)
BASELINE_AS_OF = datetime(2026, 6, 17, 12, 0, tzinfo=UTC)


def delta(
    name: str,
    *,
    signal_kind: TrendSignalKind = TrendSignalKind.ENTITY,
    status: TrendStatus = TrendStatus.RISING,
    signal_type: str = "brand",
    current_score: float = 5.0,
    baseline_score: float = 2.0,
    current_mentions: int = 5,
    baseline_mentions: int = 2,
    current_distinct_sources: int = 3,
    baseline_distinct_sources: int = 1,
    current_label: str | None = "rising",
    baseline_label: str | None = "stable",
) -> TrendDelta:
    return TrendDelta(
        signal_kind=signal_kind,
        comparison_key=f"{signal_kind.value}:{signal_type}:{name.casefold()}",
        name=name,
        signal_type=signal_type,
        status=status,
        current_label=current_label,
        baseline_label=baseline_label,
        current_score=current_score,
        baseline_score=baseline_score,
        score_delta=current_score - baseline_score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        mention_delta=current_mentions - baseline_mentions,
        current_internal_baseline_mentions=baseline_mentions,
        baseline_internal_baseline_mentions=baseline_mentions,
        current_growth_ratio=2.0,
        baseline_growth_ratio=1.0,
        current_distinct_sources=current_distinct_sources,
        baseline_distinct_sources=baseline_distinct_sources,
        distinct_source_delta=current_distinct_sources - baseline_distinct_sources,
        first_seen_at=BASELINE_AS_OF,
    )


def comparison(deltas: list[TrendDelta]) -> TrendComparison:
    return TrendComparison(as_of=AS_OF, baseline_as_of=BASELINE_AS_OF, deltas=deltas)


def test_build_trend_explanations_preserves_delta_order_and_derives_reasons() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta("The Row", status=TrendStatus.NEW, current_label="new", baseline_label=None),
                delta(
                    "Mesh flats",
                    signal_kind=TrendSignalKind.CANDIDATE,
                    signal_type="phrase",
                    status=TrendStatus.RISING,
                ),
            ]
        )
    )

    assert [item.name for item in report.items] == ["The Row", "Mesh flats"]
    assert report.items[0].headline == "Local observed new tracked entity signal needs review."
    assert report.items[0].reason_codes == [
        "status_new",
        "score_increase_observed",
        "mention_increase_observed",
        "source_diversity_increase_observed",
        "label_changed_observed",
    ]
    assert report.items[1].headline == "Local observed rising candidate phrase signal needs review."
    assert "candidate_signal_needs_review" in report.items[1].reason_codes
    assert "configured sources and imported local signals" in report.items[1].summary


def test_build_trend_explanations_handles_stable_and_dropped_statuses() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "Mixed Brand",
                    status=TrendStatus.STABLE,
                    current_score=4.0,
                    baseline_score=1.0,
                    current_mentions=1,
                    baseline_mentions=4,
                    current_distinct_sources=2,
                    baseline_distinct_sources=2,
                ),
                delta(
                    "Old Brand",
                    status=TrendStatus.DROPPED,
                    current_score=0.0,
                    baseline_score=3.0,
                    current_mentions=0,
                    baseline_mentions=3,
                    current_distinct_sources=0,
                    baseline_distinct_sources=2,
                    current_label=None,
                    baseline_label="watch",
                ),
            ]
        )
    )

    assert report.items[0].headline == "Local observed stable tracked entity signal needs review."
    assert "status_stable" in report.items[0].reason_codes
    assert report.items[1].headline == "Local observed dropped tracked entity signal needs review."
    assert "status_dropped" in report.items[1].reason_codes
    assert "Signal was present in the baseline snapshot but not in the current snapshot." in report.items[1].summary


def test_build_trend_explanations_status_clauses_allow_flat_dimensions() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "Flat mentions",
                    status=TrendStatus.RISING,
                    current_score=3.0,
                    baseline_score=1.0,
                    current_mentions=2,
                    baseline_mentions=2,
                ),
                delta(
                    "Flat score",
                    status=TrendStatus.COOLING,
                    current_score=2.0,
                    baseline_score=2.0,
                    current_mentions=1,
                    baseline_mentions=3,
                ),
            ]
        )
    )

    assert "Score and/or mention movement increased" in report.items[0].summary
    assert "mention_increase_observed" not in report.items[0].reason_codes
    assert "Score and/or mention movement decreased" in report.items[1].summary
    assert "score_decrease_observed" not in report.items[1].reason_codes


def test_trend_explanations_json_top_level_key_order_is_stable() -> None:
    report = build_trend_explanations(comparison([]))
    payload = json.loads(report.model_dump_json())

    assert isinstance(report, TrendExplanationReport)
    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "as_of",
        "baseline_as_of",
        "item_count",
        "items",
        "boundaries",
    ]


def test_trend_explanations_table_states_boundaries_and_empty_report() -> None:
    report = build_trend_explanations(comparison([]))

    rendered = "\n".join(render_trend_explanations_table(report))

    assert "Local observed trend explanations need review." in rendered
    assert "configured sources and imported local signals" in rendered.lower()
    assert "no demand proof" in rendered.lower()
    assert "No platform coverage verification is performed." in rendered
    assert "No local observed trend explanations in this comparison." in rendered


def test_trend_explanations_table_sanitizes_dynamic_cells() -> None:
    report = build_trend_explanations(
        comparison(
            [
                delta(
                    "The|Row\nDrop",
                    signal_type="brand|\nline",
                    current_label="now|\nlabel",
                    baseline_label="base|\nlabel",
                )
            ]
        )
    )

    row = render_trend_explanations_table(report)[-1]

    assert "The / Row Drop" in row
    assert "brand / line" in row
    assert "now / label" in row
    assert "\n" not in row


def test_trend_explanations_limit_truncates_existing_order() -> None:
    report = build_trend_explanations(
        comparison([delta("A"), delta("B"), delta("C")]),
        limit=2,
    )

    assert [item.name for item in report.items] == ["A", "B"]
    assert report.item_count == 2

    zero = build_trend_explanations(comparison([delta("A")]), limit=0)
    assert zero.items == []
    assert zero.item_count == 0


def test_trend_explanations_rejects_negative_limit() -> None:
    with pytest.raises(ValueError, match="limit must be at least 0"):
        build_trend_explanations(comparison([]), limit=-1)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_trend_explanations.py -q
```

Expected: fail because `fashion_radar.trend_explanations` does not exist yet.

- [ ] **Step 3: Implement the pure explanation module**

Create `src/fashion_radar/trend_explanations.py` with:

```python
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.utils.dates import parse_datetime_utc

TREND_EXPLANATION_BOUNDARIES = (
    "Configured sources and imported local signals only; no demand proof.",
    "No platform coverage verification is performed.",
)


class TrendExplanationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_kind: TrendSignalKind
    comparison_key: str
    name: str
    signal_type: str
    status: TrendStatus
    headline: str
    summary: str
    reason_codes: list[str] = Field(default_factory=list)
    current_score: float = 0.0
    baseline_score: float = 0.0
    score_delta: float = 0.0
    current_mentions: int = 0
    baseline_mentions: int = 0
    mention_delta: int = 0
    current_distinct_sources: int = 0
    baseline_distinct_sources: int = 0
    distinct_source_delta: int = 0
    current_label: str | None = None
    baseline_label: str | None = None
    first_seen_at: datetime | None = None

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class TrendExplanationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = "trend-explanations/v1"
    execution_mode: Literal["local_read_only"] = "local_read_only"
    as_of: datetime
    baseline_as_of: datetime
    item_count: int = 0
    items: list[TrendExplanationItem] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=lambda: list(TREND_EXPLANATION_BOUNDARIES))

    @field_validator("as_of", "baseline_as_of", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)


def build_trend_explanations(
    comparison: TrendComparison,
    *,
    limit: int | None = None,
) -> TrendExplanationReport:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")

    items = [_to_explanation_item(delta) for delta in comparison.deltas]
    if limit is not None:
        items = items[:limit]
    return TrendExplanationReport(
        as_of=comparison.as_of,
        baseline_as_of=comparison.baseline_as_of,
        item_count=len(items),
        items=items,
    )


def render_trend_explanations_table(report: TrendExplanationReport) -> list[str]:
    lines = [
        "# Trend Explanations",
        "Local observed trend explanations need review.",
        f"As of: {report.as_of.isoformat()}",
        f"Baseline as of: {report.baseline_as_of.isoformat()}",
        *report.boundaries,
    ]
    if not report.items:
        lines.append("No local observed trend explanations in this comparison.")
        return lines
    lines.append("Status | Kind | Type | Name | Headline | Summary")
    for item in report.items:
        lines.append(
            f"{_cell(item.status.value)} | {_cell(item.signal_kind.value)} | "
            f"{_cell(item.signal_type)} | {_cell(item.name)} | "
            f"{_cell(item.headline)} | {_cell(item.summary)}"
        )
    return lines


def _to_explanation_item(delta: TrendDelta) -> TrendExplanationItem:
    return TrendExplanationItem(
        signal_kind=delta.signal_kind,
        comparison_key=delta.comparison_key,
        name=delta.name,
        signal_type=delta.signal_type,
        status=delta.status,
        headline=_headline(delta),
        summary=_summary(delta),
        reason_codes=_reason_codes(delta),
        current_score=delta.current_score,
        baseline_score=delta.baseline_score,
        score_delta=delta.score_delta,
        current_mentions=delta.current_mentions,
        baseline_mentions=delta.baseline_mentions,
        mention_delta=delta.mention_delta,
        current_distinct_sources=delta.current_distinct_sources,
        baseline_distinct_sources=delta.baseline_distinct_sources,
        distinct_source_delta=delta.distinct_source_delta,
        current_label=delta.current_label,
        baseline_label=delta.baseline_label,
        first_seen_at=delta.first_seen_at,
    )


def _headline(delta: TrendDelta) -> str:
    status_text = delta.status.value
    kind_text = "tracked entity" if delta.signal_kind == TrendSignalKind.ENTITY else "candidate phrase"
    return f"Local observed {status_text} {kind_text} signal needs review."


def _summary(delta: TrendDelta) -> str:
    kind_text = "tracked entity" if delta.signal_kind == TrendSignalKind.ENTITY else "candidate phrase"
    label_text = _label_text(delta)
    return (
        f"Local observed {kind_text} signal from configured sources and imported local signals: "
        f"score {delta.score_delta:+.2f}, mentions {delta.mention_delta:+d}, "
        f"distinct sources {delta.distinct_source_delta:+d}, {label_text}. "
        f"{_status_clause(delta.status)}"
    )


def _reason_codes(delta: TrendDelta) -> list[str]:
    reasons = [f\"status_{delta.status.value}\"]
    if delta.score_delta > 0:
        reasons.append(\"score_increase_observed\")
    elif delta.score_delta < 0:
        reasons.append(\"score_decrease_observed\")
    if delta.mention_delta > 0:
        reasons.append(\"mention_increase_observed\")
    elif delta.mention_delta < 0:
        reasons.append(\"mention_decrease_observed\")
    if delta.distinct_source_delta > 0:
        reasons.append(\"source_diversity_increase_observed\")
    elif delta.distinct_source_delta < 0:
        reasons.append(\"source_diversity_decrease_observed\")
    if delta.current_label != delta.baseline_label:
        reasons.append(\"label_changed_observed\")
    if delta.signal_kind == TrendSignalKind.CANDIDATE:
        reasons.append(\"candidate_signal_needs_review\")
    return reasons


def _label_text(delta: TrendDelta) -> str:
    current = delta.current_label or \"no current label\"
    baseline = delta.baseline_label or \"no baseline label\"
    return f\"label {current} from {baseline}\"


def _status_clause(status: TrendStatus) -> str:
    mapping = {
        TrendStatus.NEW: \"Signal was not present in the baseline snapshot.\",
        TrendStatus.RISING: \"Score and/or mention movement increased in the comparison window.\",
        TrendStatus.COOLING: \"Score and/or mention movement decreased in the comparison window.\",
        TrendStatus.STABLE: \"Score and mention movement did not agree on a rise or cooling signal.\",
        TrendStatus.DROPPED: \"Signal was present in the baseline snapshot but not in the current snapshot.\",
    }
    return mapping[status]


def _cell(value: object) -> str:
    text = \"-\" if value is None else str(value)
    text = text.replace(\"|\", \" / \")
    text = \" \".join(text.splitlines())
    return \" \".join(text.split())
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_trend_explanations.py -q
```

Expected: pass.

## Task 2: CLI Surface And Read-Only Behavior

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write RED CLI tests**

Add imports in `tests/test_cli.py`:

```python
from fashion_radar.trend_explanations import TrendExplanationReport
```

Add tests near the existing trend/heat-movers CLI tests:

```python
def test_trend_explanations_command_missing_database_writes_nothing(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = TrendExplanationReport.model_validate_json(result.output)
    assert report.items == []
    assert report.baseline_as_of == datetime(2026, 6, 5, 12, 0, tzinfo=UTC)
    assert not data_dir.exists()
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_trend_explanations_command_invalid_as_of_writes_nothing(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "invalid --as-of" in result.output
    assert not data_dir.exists()


def test_trend_explanations_command_prints_json(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = TrendExplanationReport.model_validate_json(result.output)
    assert report.items
    assert "The Row" in {item.name for item in report.items}


def test_trend_explanations_command_prints_table(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Local observed trend explanations need review." in result.output
    assert "Configured sources and imported local signals only" in result.output
    assert "The Row" in result.output


def test_trend_explanations_command_include_dropped_surfaces_baseline_only_signals(
    tmp_path: Path,
) -> None:
    config_dir, data_dir = _prepare_trend_cli_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--include-dropped",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = TrendExplanationReport.model_validate_json(result.output)
    assert "Old Brand" in {item.name for item in report.items}


def test_trend_explanations_command_help_lists_public_flags() -> None:
    result = CliRunner().invoke(app, ["trend-explanations", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "local observed trend deltas" in result.output.lower()
    assert "--config-dir" in result.output
    assert "--data-dir" in result.output
    assert "--as-of" in result.output
    assert "--baseline-as-of" in result.output
    assert "--include-dropped" in result.output
    assert "--limit" in result.output
    assert "--format" in result.output


def test_trend_explanations_command_rejects_negative_limit(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output
```

- [ ] **Step 2: Run CLI tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli.py::test_trend_explanations_command_missing_database_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_invalid_as_of_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_prints_json \
  tests/test_cli.py::test_trend_explanations_command_prints_table \
  tests/test_cli.py::test_trend_explanations_command_include_dropped_surfaces_baseline_only_signals \
  tests/test_cli.py::test_trend_explanations_command_help_lists_public_flags \
  tests/test_cli.py::test_trend_explanations_command_rejects_negative_limit \
  -q
```

Expected: fail because the new command and report type are not wired into the
CLI yet.

- [ ] **Step 3: Implement the CLI command**

In `src/fashion_radar/cli.py`, add imports:

```python
from fashion_radar.trend_explanations import (
    TrendExplanationReport,
    build_trend_explanations,
    render_trend_explanations_table,
)
```

Add type alias near the existing output-format aliases:

```python
TrendExplanationOutputFormat = Literal["table", "json"]
```

Add a dedicated option constant near the trend output-format option constants:

```python
TREND_EXPLANATION_FORMAT_OPTION = typer.Option("table", "--format", help="Output format.")
```

Add the command after `trends_command(...)`:

```python
@app.command(name="trend-explanations")
def trend_explanations_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(20, min=0, help="Maximum explanations to print."),
    output_format: TrendExplanationOutputFormat = TREND_EXPLANATION_FORMAT_OPTION,
    include_dropped: bool = typer.Option(False, help="Include signals present only in baseline."),
) -> None:
    """Explain local observed trend deltas."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not explain trend deltas: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        try:
            baseline_as_of_value = (
                parse_datetime_utc(baseline_as_of)
                if baseline_as_of is not None
                else as_of_value - timedelta(days=scoring_config.scoring.current_window_days)
            )
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not explain trend deltas: invalid --baseline-as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        if baseline_as_of_value >= as_of_value:
            typer.echo(
                "Could not explain trend deltas: baseline-as-of must be before as-of",
                err=True,
            )
            raise typer.Exit(1)
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except ConfigError as exc:
        typer.echo(f"Invalid trend explanation config: {exc}", err=True)
        raise typer.Exit(1) from exc

    db_path = default_database_path(data_dir)
    if not db_path.exists():
        _print_trend_explanation_output(
            build_trend_explanations(
                TrendComparison(as_of=as_of_value, baseline_as_of=baseline_as_of_value, deltas=[]),
                limit=limit,
            ),
            output_format=output_format,
        )
        return

    engine = create_readonly_sqlite_engine(db_path)
    try:
        verify_readonly_trend_schema(engine)
        comparison = build_trend_comparison(
            engine,
            scoring=scoring_config.scoring,
            candidate_discovery=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            baseline_as_of=baseline_as_of_value,
            include_dropped=include_dropped,
            limit=None,
        )
        report = build_trend_explanations(comparison, limit=limit)
    except Exception as exc:
        typer.echo(f"Could not explain trend deltas: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        engine.dispose()

    _print_trend_explanation_output(report, output_format=output_format)
```

Add output helper near `_print_trend_output(...)`:

```python
def _print_trend_explanation_output(
    report: TrendExplanationReport,
    *,
    output_format: TrendExplanationOutputFormat,
) -> None:
    if output_format == "json":
        typer.echo(report.model_dump_json(indent=2))
        return

    for line in render_trend_explanations_table(report):
        typer.echo(line)
```

- [ ] **Step 4: Run CLI tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_trend_explanations.py \
  tests/test_cli.py::test_trend_explanations_command_missing_database_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_invalid_as_of_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_prints_json \
  tests/test_cli.py::test_trend_explanations_command_prints_table \
  tests/test_cli.py::test_trend_explanations_command_include_dropped_surfaces_baseline_only_signals \
  tests/test_cli.py::test_trend_explanations_command_help_lists_public_flags \
  tests/test_cli.py::test_trend_explanations_command_rejects_negative_limit \
  -q
```

Expected: pass.

## Task 3: Docs, Docs Tests, And Release Gate

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write RED docs test**

In `tests/test_cli_docs.py`, extend the command/discoverability assertions to
cover `trend-explanations`.

Add `"trend-explanations": ("--config-dir", "--data-dir", "--as-of")` to
`REQUIRED_FLAGS_BY_COMMAND`.

Add `"trend-explanations"` to the command loops that currently assert public
command discoverability in README, CLI reference, and upload-checklist help
loops.

Add a focused docs test:

```python
def test_trend_explanations_docs_are_bounded_and_discoverable() -> None:
    docs = (
        README,
        ROOT / "docs" / "cli-reference.md",
        ROOT / "docs" / "trend-deltas.md",
        ROOT / "docs" / "architecture.md",
        ROOT / "docs" / "dashboard.md",
        ROOT / "docs" / "github-upload-checklist.md",
    )
    required_terms = (
        "trend-explanations",
        "configured sources and imported local signals",
        "no demand proof",
        "no platform coverage verification",
    )
    narrative_docs = (
        README,
        ROOT / "docs" / "cli-reference.md",
        ROOT / "docs" / "trend-deltas.md",
    )
    forbidden_terms = (
        "market-wide ranking",
        "verified demand",
        "full platform coverage",
    )

    for path in docs:
        text = _read(path).casefold()
        for term in required_terms:
            assert term in text, f"{path.relative_to(ROOT)} missing {term!r}"
        for term in forbidden_terms:
            assert term not in text, f"{path.relative_to(ROOT)} unexpectedly includes {term!r}"

    for path in narrative_docs:
        text = _read(path).casefold()
        assert "needs review" in text, f"{path.relative_to(ROOT)} missing 'needs review'"
```

- [ ] **Step 2: Run docs test to verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_trend_explanations_docs_are_bounded_and_discoverable -q
```

Expected: fail because docs do not mention the new command yet.

- [ ] **Step 3: Update docs and changelog**

Update docs to describe `trend-explanations` as:

- read-only;
- derived from local trend deltas;
- bounded to configured sources and imported local signals;
- not demand proof;
- not platform coverage verification;
- separate from the `trends` and `heat-movers` contracts.

Add a changelog bullet under `## [Unreleased]` / `### Added`:

```markdown
- Stage 193 read-only `trend-explanations` sidecar command for deterministic
  local explanations over existing trend deltas, without changing `trends` or
  `heat-movers` contracts.
```

- [ ] **Step 4: Run docs test to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_trend_explanations_docs_are_bounded_and_discoverable -q
```

Expected: pass.

- [ ] **Step 5: Run verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_trend_explanations.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
```

Expected: all commands pass.

- [ ] **Step 6: Request code review and release review**

Create the standard Stage 193 opencode code/release review prompts and capture
their outputs under:

- `docs/reviews/opencode-stage-193-code-review-prompt.md`
- `docs/reviews/opencode-stage-193-code-review.md`
- `docs/reviews/opencode-stage-193-release-review-prompt.md`
- `docs/reviews/opencode-stage-193-release-review.md`

Expected: no Critical or Important findings. If any appear, fix them and record
the corresponding rereview artifacts.

- [ ] **Step 7: Commit and push**

Run:

```bash
git add \
  src/fashion_radar/trend_explanations.py \
  src/fashion_radar/cli.py \
  tests/test_trend_explanations.py \
  tests/test_cli.py \
  README.md \
  docs/architecture.md \
  docs/cli-reference.md \
  docs/trend-deltas.md \
  docs/dashboard.md \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-193-trend-heat-explanation-sidecar-design.md \
  docs/superpowers/plans/2026-06-24-stage-193-trend-heat-explanation-sidecar-plan.md \
  docs/reviews/opencode-stage-193-plan-review-prompt.md \
  docs/reviews/opencode-stage-193-plan-review.md \
  docs/reviews/opencode-stage-193-code-review-prompt.md \
  docs/reviews/opencode-stage-193-code-review.md \
  docs/reviews/opencode-stage-193-release-review-prompt.md \
  docs/reviews/opencode-stage-193-release-review.md
git commit -m "feat: add trend explanation sidecar"
git push origin main
```

Add rereview artifacts to the same commit if they exist.

## Self-Review

- Spec coverage: the plan covers pure builder logic, CLI wiring, docs/tests,
  review gates, verification, and release.
- Placeholder scan: no `TBD`, `TODO`, or vague implementation markers remain.
- Boundary check: the plan keeps `TrendDelta`, `TrendComparison`,
  `HeatMover`, `HeatMoversReport`, dashboard row contracts, and existing
  `trends` / `heat-movers` outputs unchanged.
