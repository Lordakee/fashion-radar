# Stage 10 Trend Delta Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local read-only trend delta command and dashboard view so users can see which locally observed fashion entities and candidate phrases are new in the current comparison snapshot, rising, cooling, stable, or dropped between two scoring snapshots.

**Architecture:** Reuse the existing scoring and candidate discovery engines instead of adding a new heat formula. Add a focused trend model plus comparator module, wire a read-only CLI command that opens SQLite in read-only mode, then expose the same comparison in the dashboard.

**Tech Stack:** Python 3.11+, Typer with plain table-style `typer.echo` output, Pydantic, SQLAlchemy read-only SQLite URI connections, Streamlit for the optional dashboard, pytest, ruff, uv.

---

## Scope Guard

Stage 10 must not add platform search, crawlers, scrapers, browser automation,
Playwright, Selenium, MCP scraping servers, account automation, login cookies,
account/session files, browser profiles, tokens, credentials, proxy pools,
fingerprint evasion, CAPTCHA bypass, rate-limit bypass, access-control bypass,
paywall bypass, private data collection, social platform APIs, media downloads,
LLM scoring, embeddings, vector databases, image recognition, or paid services.

Stage 10 must not add schema migrations, new persistent trend tables, writable
indexes, or database writes. Trend deltas are computed on demand from existing
local tables.

Trend output must describe local observed signals only. It must not claim
market-wide trend proof, real-time platform coverage, verified demand, or full
social listening.

The "no external services" boundary applies to Fashion Radar runtime behavior.
Development verification may still use existing project tooling such as `uv`
sync checks, package-index mirrors, and Claude Code review gates.

Codex subagents must use `reasoning_effort: "xhigh"`. Claude Code review must
use `--effort max`.

## Files

- Create: `src/fashion_radar/models/trend.py`
- Create: `src/fashion_radar/trends.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `src/fashion_radar/dashboard/queries.py`
- Create: `tests/test_trends.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_dashboard.py`
- Create: `docs/trend-deltas.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/scoring.md`
- Modify: `CHANGELOG.md`
- Create after implementation: `docs/reviews/claude-code-stage-10-code-review-prompt.md`
- Create after code review: `docs/reviews/claude-code-stage-10-code-review.md`

## Public Interfaces

New CLI:

```bash
fashion-radar trends --as-of 2026-06-12T00:00:00Z --config-dir ./configs
fashion-radar trends --as-of 2026-06-12T00:00:00Z --baseline-as-of 2026-06-05T00:00:00Z --config-dir ./configs
fashion-radar trends --as-of 2026-06-12T00:00:00Z --format json --limit 30 --include-dropped --config-dir ./configs
```

New output concepts:

- `TrendSignalKind`: `entity` or `candidate`.
- `TrendStatus`: `new`, `rising`, `cooling`, `stable`, `dropped`.
- `TrendDelta`: one comparable local signal, including its normalized
  `comparison_key` and explicit internal baseline count fields.
- `TrendComparison`: metadata plus ordered deltas.

Default baseline:

```text
baseline_as_of = as_of - scoring.current_window_days
```

Read-only guarantee:

- Missing database prints an empty result.
- Missing database does not create `data_dir`.
- Existing database is opened with `mode=ro&uri=true`.
- Existing incompatible databases are rejected without schema mutation.
- CLI and dashboard trend paths verify schema version before reading, including
  tables needed by entity scoring such as `entity_first_seen`.
- The trends command must not call `initialize_schema()`.
- Invalid config or invalid dates fail before database access and do not create
  `data_dir`.
- `baseline_as_of` must be earlier than `as_of`.

Candidate universe rule:

- Snapshot discovery uses the configured candidate discovery maximum, not the
  CLI/dashboard display limit.
- CLI/dashboard `--limit` is applied only after `compare_trends()` computes
  entity and candidate deltas.
- Stage 10 does not bypass `CandidateDiscoverySettings.max_candidates`; users
  can increase that local config value when they need a wider candidate
  comparison universe.

## Task 1: Claude Code Plan Gate

- [ ] Use the already-created `docs/reviews/claude-code-stage-10-plan-review-prompt.md` with the Stage 10 goal, architecture, tech stack, implementation method, tests, docs, explicit read-only review instruction, and explicit safety boundaries.
- [ ] Run Claude Code in plan/read-only mode:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-10-plan-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-10-plan-review.md`.
- [ ] Fix every Critical and Important finding before Task 2. If the first
  review is not approved, save follow-up review prompts/results as
  `docs/reviews/claude-code-stage-10-plan-rereview*.md`; these files satisfy
  the Stage 10 plan gate once Claude Code approves implementation.

## Task 2: Trend Models And Comparator

**Files:**

- Create: `src/fashion_radar/models/trend.py`
- Create: `src/fashion_radar/trends.py`
- Create: `tests/test_trends.py`

- [ ] Add failing tests for model validation and comparison ordering.

Test names:

```python
def test_compare_trends_marks_snapshot_new_and_rising_entities() -> None: ...
def test_compare_trends_can_include_dropped_signals() -> None: ...
def test_compare_trends_sorts_by_status_and_delta() -> None: ...
def test_compare_trends_handles_candidate_phrases() -> None: ...
def test_compare_trends_treats_score_up_mentions_down_as_stable() -> None: ...
def test_compare_trends_treats_score_down_mentions_up_as_stable() -> None: ...
def test_compare_trends_marks_identical_metrics_stable() -> None: ...
def test_compare_trends_status_boundaries_are_deterministic() -> None: ...
def test_compare_trends_exposes_internal_baseline_mentions_with_explicit_names() -> None: ...
def test_compare_trends_uses_alias_key_normalization() -> None: ...
def test_compare_trends_sorts_same_name_signals_deterministically() -> None: ...
def test_compare_trends_applies_limit_after_comparison() -> None: ...
def test_compare_trends_limit_zero_returns_metadata_without_deltas() -> None: ...
```

Core assertions:

- A current-only entity is `status == "new"` and means new in the current
  comparison snapshot, not necessarily first observed locally.
- A current entity with score up and mentions flat/up is `status == "rising"`.
- A current entity with score down and mentions flat/down is `status == "cooling"`.
- A current entity with score up and mentions down is `status == "stable"`.
- A current entity with score down and mentions up is `status == "stable"`.
- Mention deltas decide direction only when `score_delta == 0`.
- Boundary cases are explicit: `(score_delta > 0, mention_delta == 0)` is
  `rising`; `(score_delta < 0, mention_delta == 0)` is `cooling`;
  `(score_delta == 0, mention_delta > 0)` is `rising`; and
  `(score_delta == 0, mention_delta < 0)` is `cooling`.
- Identical current and baseline metrics are `status == "stable"`.
- A baseline-only entity appears only when `include_dropped=True`.
- Candidate phrases compare separately from tracked entities.
- Entity and candidate comparison keys use `normalize_alias_key()` rather than
  ad hoc lowercasing or punctuation stripping.
- `current_mentions` and `baseline_mentions` are comparison-snapshot
  current-window counts, while existing metric internal baseline-window counts
  are exposed only as `current_internal_baseline_mentions` and
  `baseline_internal_baseline_mentions`.
- Output sorting is deterministic, including same-name signals across entity,
  candidate, and signal-type boundaries.
- Output `limit` is applied after comparison and sorting.
- `limit=0` returns valid metadata with no deltas.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_trends.py -q
```

Expected: fails because `fashion_radar.trends` and trend models do not exist.

- [ ] Implement `src/fashion_radar/models/trend.py`:

```python
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.utils.dates import parse_datetime_utc


class TrendSignalKind(StrEnum):
    ENTITY = "entity"
    CANDIDATE = "candidate"


class TrendStatus(StrEnum):
    NEW = "new"
    RISING = "rising"
    COOLING = "cooling"
    STABLE = "stable"
    DROPPED = "dropped"


class TrendDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_kind: TrendSignalKind
    comparison_key: str
    name: str
    signal_type: str
    status: TrendStatus
    current_label: str | None = None
    baseline_label: str | None = None
    current_score: float = 0.0
    baseline_score: float = 0.0
    score_delta: float = 0.0
    current_mentions: int = 0
    baseline_mentions: int = 0
    mention_delta: int = 0
    current_internal_baseline_mentions: int = 0
    baseline_internal_baseline_mentions: int = 0
    current_growth_ratio: float | None = None
    baseline_growth_ratio: float | None = None
    current_distinct_sources: int = 0
    baseline_distinct_sources: int = 0
    distinct_source_delta: int = 0
    first_seen_at: datetime | None = None

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class TrendComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    baseline_as_of: datetime
    deltas: list[TrendDelta]

    @field_validator("as_of", "baseline_as_of", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)
```

- [ ] Implement `src/fashion_radar/trends.py` comparator helpers:

```python
def compare_trends(
    *,
    current_entities: Sequence[EntityHeatMetric],
    baseline_entities: Sequence[EntityHeatMetric],
    current_candidates: Sequence[CandidateMetric],
    baseline_candidates: Sequence[CandidateMetric],
    as_of: datetime,
    baseline_as_of: datetime,
    include_dropped: bool = False,
    limit: int | None = None,
) -> TrendComparison: ...
```

Required internal helpers:

```python
def _entity_key(metric: EntityHeatMetric) -> str: ...
def _candidate_key(metric: CandidateMetric) -> str: ...
def _status(current: _Comparable | None, baseline: _Comparable | None) -> TrendStatus: ...
def _sort_key(delta: TrendDelta) -> tuple[int, float, float, int, str, str, str, str]: ...
```

Key helper requirements:

- `_entity_key()` must use `normalize_alias_key(metric.entity_name)` and include
  `metric.entity_type`.
- `_candidate_key()` must use `normalize_alias_key(metric.phrase)` and include
  `metric.candidate_type`.
- Do not use ad hoc lowercasing, punctuation stripping, or whitespace-only
  normalization in trend keys.

Status helper requirements:

- `NEW`: current-only metrics; this means new in the current comparison
  snapshot, not necessarily first observed locally.
- `DROPPED`: baseline-only metrics when `include_dropped=True`.
- `RISING`: `score_delta > 0 and mention_delta >= 0`, or
  `score_delta == 0 and mention_delta > 0`.
- `COOLING`: `score_delta < 0 and mention_delta <= 0`, or
  `score_delta == 0 and mention_delta < 0`.
- `STABLE`: `score_delta == 0 and mention_delta == 0`, or mixed-direction
  movement where score and mention deltas disagree.
- When score and mention movement disagree, keep the status `stable` because
  the local evidence is not directionally clear enough for a stronger label.

Candidate deltas are based on candidates discoverable under existing
candidate-discovery thresholds. They are not a complete raw phrase inventory.

Sort deltas by status rank, descending absolute score delta, descending current
score, descending current mentions, display name, `signal_kind.value`,
`signal_type`, and `comparison_key`.

Sorting requirements:

- Sort status groups in this order: `new`, `rising`, `cooling`, `stable`,
  `dropped`.
- Within status, sort by descending absolute score delta, descending current
  score, descending current mentions, name, `signal_kind`, `signal_type`, and
  normalized comparison key.
- Include a regression test with same-name entity and candidate signals so
  ordering cannot depend on dict/input construction order.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_trends.py -q
.venv/bin/python -m ruff check src/fashion_radar/models/trend.py src/fashion_radar/trends.py tests/test_trends.py
```

Expected: passes.

## Task 3: Read-Only Trend Workflow And CLI

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/trends.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_trends.py`

- [ ] Add failing CLI tests:

```python
def test_trends_command_missing_database_writes_nothing(tmp_path: Path) -> None: ...
def test_trends_command_rejects_invalid_dates_before_data_dir_creation(tmp_path: Path) -> None: ...
def test_trends_command_rejects_baseline_at_or_after_as_of(tmp_path: Path) -> None: ...
def test_trends_command_rejects_invalid_scoring_config_before_data_dir_creation(tmp_path: Path) -> None: ...
def test_trends_command_rejects_incompatible_database_without_schema_mutation(tmp_path: Path) -> None: ...
def test_trends_command_prints_json(tmp_path: Path) -> None: ...
def test_trends_command_missing_database_json_preserves_metadata_and_default_baseline(tmp_path: Path) -> None: ...
def test_trends_command_prints_table(tmp_path: Path) -> None: ...
def test_trends_command_existing_database_remains_read_only(tmp_path: Path) -> None: ...
def test_open_read_only_sqlite_engine_uses_uri_mode_ro(tmp_path: Path) -> None: ...
def test_trends_command_defaults_baseline_from_scoring_window(tmp_path: Path) -> None: ...
def test_trends_command_include_dropped_surfaces_baseline_only_signals(tmp_path: Path) -> None: ...
def test_trends_command_limit_caps_ordered_deltas(tmp_path: Path) -> None: ...
def test_trends_command_applies_limit_after_current_and_baseline_candidate_comparison(tmp_path: Path) -> None: ...
def test_trends_command_public_flags_work_end_to_end(tmp_path: Path) -> None: ...
def test_trends_command_help_lists_public_options() -> None: ...
def test_trends_command_does_not_call_collection_or_import_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None: ...
def test_build_trend_comparison_uses_scoring_and_candidate_discovery(tmp_path: Path) -> None: ...
def test_build_trend_comparison_calls_snapshot_engines_twice_and_keeps_limit_out_of_discovery(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None: ...
def test_build_trend_comparison_respects_read_only_sqlite_uri(tmp_path: Path) -> None: ...
```

Assertions:

- Missing database exits 0 and does not create `data_dir`.
- Invalid `--as-of` or `--baseline-as-of` exits non-zero and does not create
  `data_dir`.
- `baseline_as_of >= as_of` exits non-zero and does not create `data_dir`.
- Invalid scoring, candidate, or entity config exits non-zero with a concise
  error and does not create `data_dir` or a SQLite database.
- An existing incompatible SQLite file is rejected with a concise schema error
  and remains without initialized schema tables afterward.
- JSON output validates as a full `TrendComparison`, including missing-DB JSON
  output; do not return a bare `[]`.
- Missing-DB JSON output exits `0`, does not create `data_dir`, preserves the
  requested `as_of`, computes omitted `baseline_as_of` from
  `scoring.current_window_days`, and has `deltas == []`.
- Table output contains `local observed trend deltas` and at least one signal
  after seeded matched data.
- Existing database table row counts are unchanged after `trends`.
- Read-only SQLite engine construction is centralized in one helper and uses
  `mode=ro&uri=true`.
- `baseline_as_of` defaults to `as_of - scoring.current_window_days`.
- `--include-dropped` surfaces baseline-only signals.
- `--limit` caps returned deltas after deterministic ordering.
- Public Typer flags work end-to-end with
  `fashion-radar trends --as-of ... --format json --include-dropped --limit 1`.
- Help output lists `--include-dropped`, `--no-include-dropped`, `--limit`,
  `--baseline-as-of`, and `--format table|json`.
- `--limit` is applied only after both current and baseline candidate discovery
  results are compared, so baseline-only/dropped signals are not hidden before
  comparison.
- Trend command tests monkeypatch collection/import entrypoints to raise if
  called, proving no collector/import/social path is invoked.
- Seeded local DB tests prove entity deltas come from `score_entities()` at both
  snapshots, candidate deltas come from `discover_candidates()` at both
  snapshots, candidate filtering respects configured/stored entities, and the
  workflow works against a read-only SQLite URI.
- Spy/monkeypatch tests assert `score_entities()` and `discover_candidates()`
  are each called exactly twice, once for current and once for baseline,
  returned metrics flow into `compare_trends()`, and CLI/output `limit` is not
  passed into `discover_candidates()`.

- [ ] Add read-only workflow helper in `trends.py`:

```python
def create_readonly_sqlite_engine(db_path: Path) -> Engine: ...
def verify_readonly_trend_schema(engine: Engine) -> None: ...

def build_trend_comparison(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    candidate_discovery: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: datetime,
    baseline_as_of: datetime,
    include_dropped: bool = False,
    limit: int | None = None,
) -> TrendComparison: ...
```

This helper calls existing `score_entities()` and `discover_candidates()` for
both snapshots, then delegates to `compare_trends()`. It must not pass the CLI
output `limit` into `discover_candidates()`. Apply output `limit` only inside
`compare_trends()` after all current/baseline metrics are compared and sorted.
Candidate deltas still reflect candidates discoverable under configured
candidate-discovery thresholds, not every raw local phrase.

- [ ] Add CLI command:

```python
@app.command(name="trends")
def trends_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(20, min=0, help="Maximum trend deltas to print."),
    output_format: TrendOutputFormat = TREND_FORMAT_OPTION,
    include_dropped: bool = typer.Option(False, help="Include signals present only in baseline."),
) -> None: ...
```

Implementation requirements:

- Resolve `db_path` with `default_database_path(data_dir)` without creating
  directories.
- Parse `as_of` and `baseline_as_of` before loading config or opening the
  database.
- Reject `baseline_as_of >= as_of` before loading config or opening the
  database.
- Load config after date validation and before opening the database.
- If the database file is missing, print an empty trend comparison and return.
- Add `create_readonly_sqlite_engine(db_path: Path) -> Engine` and use it from
  both CLI and dashboard query code.
- `create_readonly_sqlite_engine()` must open existing SQLite with
  `create_engine(f"sqlite:///file:{db_path.as_posix()}?mode=ro&uri=true", future=True)`
  and must not create parent directories.
- Add `verify_readonly_trend_schema()` as a read-only schema guard for both CLI
  and dashboard trend paths. The guard must verify
  schema version and all tables needed by scoring/candidate discovery, including
  `items`, `item_entities`, `entity_first_seen`, and any existing metadata table
  used for schema version checks.
- Do not call `initialize_schema()`, add migrations, add persistent trend
  tables, or write to the database.

- [ ] Add output helpers:

```python
def _print_trend_output(comparison: TrendComparison, *, output_format: TrendOutputFormat) -> None: ...
def _trend_table_lines(comparison: TrendComparison) -> list[str]: ...
```

JSON output must use `comparison.model_dump_json()` or equivalent Pydantic JSON
serialization so datetime fields serialize safely.

Table output should follow the existing `candidates` command style with
`typer.echo` lines. Do not introduce a Rich rendering dependency or a Rich
`Console` unless tests prove it works cleanly under `CliRunner`.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_trends.py tests/test_cli.py -q
.venv/bin/python -m ruff check src/fashion_radar/cli.py src/fashion_radar/trends.py tests/test_cli.py tests/test_trends.py
```

Expected: passes.

## Task 4: Dashboard Trend Tab

**Files:**

- Modify: `src/fashion_radar/dashboard/queries.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_dashboard.py`

- [ ] Add failing dashboard tests:

```python
def test_dashboard_loads_trend_deltas_from_local_database(tmp_path: Path) -> None: ...
def test_dashboard_trend_query_returns_empty_when_database_missing(tmp_path: Path) -> None: ...
def test_dashboard_trend_query_missing_database_writes_nothing(tmp_path: Path) -> None: ...
def test_dashboard_trend_query_rejects_incompatible_database_without_schema_mutation(tmp_path: Path) -> None: ...
def test_dashboard_summary_handles_incompatible_database_without_masking_trend_errors(tmp_path: Path) -> None: ...
def test_dashboard_trends_default_as_of_uses_latest_local_collected_at(tmp_path: Path) -> None: ...
def test_dashboard_trends_default_as_of_uses_current_utc_when_database_has_no_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None: ...
def test_dashboard_trends_invalid_config_surfaces_error_without_data_dir_creation(tmp_path: Path) -> None: ...
def test_dashboard_trends_missing_config_surfaces_error_without_data_dir_creation(tmp_path: Path) -> None: ...
def test_dashboard_parse_args_accepts_config_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None: ...
def test_dashboard_command_forwards_config_dir_to_streamlit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None: ...
def test_dashboard_trend_render_copy_is_local_observed() -> None: ...
```

- [ ] Add a query helper:

```python
def load_trend_comparison(
    *,
    data_dir: Path,
    config_dir: Path,
    now: datetime | None = None,
    limit: int = 20,
) -> TrendComparison: ...


def resolve_dashboard_trend_window(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    now: datetime | None = None,
) -> tuple[datetime, datetime]: ...
```

Requirements:

- Missing DB returns an empty `TrendComparison`.
- Missing DB leaves `data_dir` nonexistent.
- Existing DB opens with the same read-only SQLite URI behavior as the CLI.
- Do not reuse dashboard helpers or engine helpers that call
  `create_sqlite_engine()`, because that function creates parent directories.
- Existing DB verifies schema version with the same read-only schema guard as
  the CLI before reading.
- Incompatible DB returns/surfaces a concise schema error and does not initialize
  schema tables.
- Dashboard startup remains graceful with incompatible databases: existing
  summary/top-entity/source-health helpers must not raise before the trend tab
  can render its concise local schema error.
- Default dashboard `as_of` is the latest local `items.collected_at` when any
  local items exist.
- Default dashboard `as_of` falls back to current UTC only when the database
  exists but contains no items.
- Dashboard `baseline_as_of` is computed as `as_of - scoring.current_window_days`.
- Invalid or missing dashboard trend config surfaces a concise error and does not
  create `data_dir` or a SQLite database.
- No schema initialization, migration, or persistent trend storage.
- The dashboard uses scoring settings, candidate discovery settings, and optional
  entity config loaded from `config_dir`, not hard-coded defaults.
- Errors are surfaced as concise dashboard messages.

- [ ] Add `--config-dir` to the `fashion-radar dashboard` CLI command and pass
  it through to Streamlit after the existing `--data-dir`/`--reports-dir`
  arguments.
- [ ] Add `--config-dir` to `dashboard.app.parse_args()` with the same default
  config dir used by the CLI.
- [ ] Add a dashboard tab labeled `Trend Deltas`.
- [ ] Display local observed trend deltas as a compact table.
- [ ] Use visible heading/caption/empty/error copy that says the results are
  local observed signal deltas, computed from this local database only, and need
  review.
- [ ] Add or extract a small render helper so tests can assert the visible tab
  label/copy without requiring a live browser.
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_dashboard.py -q
.venv/bin/python -m ruff check src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_cli.py tests/test_dashboard.py
```

Expected: passes.

## Task 5: Documentation

**Files:**

- Create: `docs/trend-deltas.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/scoring.md`
- Modify: `CHANGELOG.md`

- [ ] Document command examples:

```bash
uv run fashion-radar trends --as-of 2026-06-12T00:00:00Z --config-dir ./configs
uv run fashion-radar trends --as-of 2026-06-12T00:00:00Z --baseline-as-of 2026-06-05T00:00:00Z --format json --config-dir ./configs
```

- [ ] Document workflow:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv
uv run fashion-radar match
uv run fashion-radar trends --as-of 2026-06-12T00:00:00Z --config-dir ./configs
```

- [ ] Document safety wording:

```text
Trend deltas compare local observed signals only. They do not prove platform-wide or market-wide demand.
```

- [ ] Run:

```bash
rg -n "(scrape|crawler|cookie|proxy|CAPTCHA|fingerprint|bypass|account pool|login automation|full platform|viral|globally trending|market-wide trend|confirmed brand|confirmed product)" README.md docs/trend-deltas.md docs/architecture.md docs/dashboard.md docs/scoring.md CHANGELOG.md
```

Expected: only negative safety-boundary wording, if any.

- [ ] Manually review CLI, dashboard, README, and docs copy for softer
  overclaims that regex checks may miss. Include all visible dashboard strings:
  tab label, headings, captions, empty states, errors, and docs snippets. Avoid
  phrases such as `top trends` without a local qualifier, `consumer demand`,
  `market signal`, `social buzz`, `industry-wide`, and `what shoppers want`.
  Prefer `local observed signal deltas`, `locally observed heat changes`, and
  `needs review`.

## Task 6: Verification And Claude Code Review

- [ ] Run fresh verification:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check
uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

- [ ] Run installed-wheel smoke:

```bash
rm -rf /tmp/fashion-radar-dist-stage10
tmpdir="$(mktemp -d)"
uv build --out-dir /tmp/fashion-radar-dist-stage10
uv venv "$tmpdir/venv"
wheel="$(find /tmp/fashion-radar-dist-stage10 -maxdepth 1 -name 'fashion_radar-*.whl' | sort | tail -n 1)"
test -n "$wheel"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
"$tmpdir/venv/bin/fashion-radar" trends --help
"$tmpdir/venv/bin/fashion-radar" init --config-dir "$tmpdir/config" --data-dir "$tmpdir/init-data" --reports-dir "$tmpdir/reports"
"$tmpdir/venv/bin/fashion-radar" trends --as-of 2026-06-12T00:00:00Z --config-dir "$tmpdir/config" --data-dir "$tmpdir/missing-data"
test ! -e "$tmpdir/missing-data"
```

- [ ] Run CodeGraph status:

```text
mcp__codegraph.codegraph_status(projectPath="/home/ubuntu/fashion-radar")
```

- [ ] Create `docs/reviews/claude-code-stage-10-code-review-prompt.md`.
- [ ] In the code review prompt, require Claude Code to verify that no migration
  files, schema files, persistent trend tables, writable indexes, or DB writes
  were added for Stage 10.
- [ ] Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-10-code-review-prompt.md
```

- [ ] Save output to `docs/reviews/claude-code-stage-10-code-review.md`.
- [ ] Fix all Critical and Important findings.
- [ ] Commit:

```bash
git add src/fashion_radar/models/trend.py src/fashion_radar/trends.py src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py src/fashion_radar/dashboard/queries.py tests/test_trends.py tests/test_cli.py tests/test_dashboard.py README.md docs/trend-deltas.md docs/architecture.md docs/dashboard.md docs/scoring.md CHANGELOG.md docs/reviews/claude-code-stage-10-code-review-prompt.md docs/reviews/claude-code-stage-10-code-review.md
git commit -m "feat: add local trend deltas"
```

## Final Acceptance Criteria

- `fashion-radar trends` is available and read-only.
- Missing DB and invalid date/config paths do not create `data_dir`.
- Existing incompatible databases are rejected without schema mutation in CLI
  and dashboard trend paths.
- No migrations, persistent trend tables, writable trend indexes, or DB writes
  are added.
- Trend comparisons include entities and candidates.
- Output labels are local observed signals, not external market claims.
- Dashboard includes a trend delta tab.
- Full tests, ruff, lock/sync checks, build smoke, CodeGraph status, and Claude
  Code review pass before GitHub sync.
