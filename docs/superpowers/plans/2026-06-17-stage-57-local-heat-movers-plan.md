# Stage 57 Local Heat Movers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only `heat-movers` view that groups local `new` and `rising` tracked entities and candidate phrases from existing trend deltas.

**Architecture:** Create a pure `heat_movers` grouping/rendering module over `TrendComparison`, expose it through a new CLI command that reuses the existing read-only trend loading flow, and add a dashboard tab that reuses the same grouping helper. No database schema, dependency, lockfile, collection, report-generation, platform, or compliance feature changes.

**Tech Stack:** Python 3.12, Typer, Pydantic v2, SQLAlchemy read-only SQLite helpers already used by `trends`, pytest, ruff, Streamlit dashboard code already in the repo.

---

## Review Gate

Before implementation, submit this design and plan to local `opencode`:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-57-plan-review-prompt.md)" \
  > docs/reviews/opencode-stage-57-plan-review.md \
  2> /tmp/opencode-stage57-plan-review.err
```

Fix Critical and Important findings before touching production code.

## Files

Create:

- `src/fashion_radar/heat_movers.py`
- `tests/test_heat_movers.py`
- `docs/reviews/opencode-stage-57-plan-review-prompt.md`
- `docs/reviews/opencode-stage-57-plan-review.md`
- `docs/reviews/opencode-stage-57-release-review-prompt.md`
- `docs/reviews/opencode-stage-57-release-review.md`

Modify:

- `src/fashion_radar/cli.py`
- `src/fashion_radar/dashboard/app.py`
- `tests/test_cli.py`
- `tests/test_dashboard.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/trend-deltas.md`
- `docs/dashboard.md`
- `docs/cli-reference.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

Do not modify:

- `pyproject.toml`
- `uv.lock`
- database schema or migration files
- source packs, entity packs, or default starter configs
- report models/templates
- collection, scheduling, source, crawler, API, account, cookie, or browser automation code

## Task 1: Core Heat Movers Module

**Files:**

- Create: `tests/test_heat_movers.py`
- Create: `src/fashion_radar/heat_movers.py`

- [ ] **Step 1: Write pure grouping tests**

Add tests that build `TrendComparison` objects directly. Cover:

- `entity/new` goes to `new_tracked_entities`.
- `entity/rising` goes to `rising_tracked_entities`.
- `candidate/new` goes to `new_candidate_phrases`.
- `candidate/rising` goes to `rising_candidate_phrases`.
- `cooling` appears only when `include_cooling=True`.
- `stable` and `dropped` are omitted.
- `limit_per_group=1` limits each group independently.
- `limit_per_group=0` keeps groups but emits no rows.
- JSON top-level key order is stable.
- Table renderer sanitizes pipes/newlines and uses local observed wording.

Use helpers like:

```python
from datetime import UTC, datetime

from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus

AS_OF = datetime(2026, 6, 12, 12, tzinfo=UTC)
BASELINE_AS_OF = datetime(2026, 6, 5, 12, tzinfo=UTC)


def trend_delta(
    name: str,
    *,
    signal_kind: TrendSignalKind = TrendSignalKind.ENTITY,
    signal_type: str = "brand",
    status: TrendStatus = TrendStatus.RISING,
    current_score: float = 3.0,
    baseline_score: float = 1.0,
    current_mentions: int = 3,
    baseline_mentions: int = 1,
) -> TrendDelta:
    return TrendDelta(
        signal_kind=signal_kind,
        comparison_key=f"{signal_kind.value}:{signal_type}:{name.casefold()}",
        name=name,
        signal_type=signal_type,
        status=status,
        current_score=current_score,
        baseline_score=baseline_score,
        score_delta=current_score - baseline_score,
        current_mentions=current_mentions,
        baseline_mentions=baseline_mentions,
        mention_delta=current_mentions - baseline_mentions,
        current_distinct_sources=2,
        baseline_distinct_sources=1,
        distinct_source_delta=1,
        current_label="hot" if signal_kind == TrendSignalKind.ENTITY else "new_candidate",
        baseline_label="stable" if status == TrendStatus.RISING else None,
        first_seen_at=AS_OF,
    )
```

Expected first red command:

```bash
uv run pytest tests/test_heat_movers.py -q
```

Expected: import failure for `fashion_radar.heat_movers`.

- [ ] **Step 2: Implement models and grouping**

Create `src/fashion_radar/heat_movers.py` with strict Pydantic models:

```python
HeatMoverGroupName = Literal[
    "new_tracked_entities",
    "rising_tracked_entities",
    "new_candidate_phrases",
    "rising_candidate_phrases",
    "cooling_watchlist",
]

class HeatMover(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: TrendStatus
    signal_kind: TrendSignalKind
    signal_type: str
    name: str
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

class HeatMoverGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: HeatMoverGroupName
    label: str
    rows: list[HeatMover] = Field(default_factory=list)

class HeatMoversReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    as_of: datetime
    baseline_as_of: datetime
    execution_mode: Literal["local_read_only"] = "local_read_only"
    limit_per_group: int | None = 5
    include_cooling: bool = False
    group_count: int = 0
    row_count: int = 0
    groups: list[HeatMoverGroup] = Field(default_factory=list)
```

Implement:

```python
def build_heat_movers(
    comparison: TrendComparison,
    *,
    limit_per_group: int | None = 5,
    include_cooling: bool = False,
) -> HeatMoversReport:
    ...
```

Validation:

- If `limit_per_group` is not `None` and is less than zero, raise `ValueError("limit_per_group must be at least 0")`.
- Always return four primary groups in stable order.
- Return the cooling group only when `include_cooling=True`.
- Convert every included `TrendDelta` into a `HeatMover`.
- Apply limit after grouping.

Add:

```python
def render_heat_movers_table(report: HeatMoversReport) -> list[str]:
    ...
```

Table lines must include:

- `Local observed heat movers need review.`
- `Configured source set only; no demand proof or platform coverage verification.`
- `No local observed heat movers in this comparison.` when `row_count == 0`.

- [ ] **Step 3: Run core tests and formatting**

```bash
uv run pytest tests/test_heat_movers.py -q
uv run ruff check src/fashion_radar/heat_movers.py tests/test_heat_movers.py
uv run ruff format --check src/fashion_radar/heat_movers.py tests/test_heat_movers.py
```

Expected: all pass after implementation and formatting.

## Task 2: CLI Command

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add CLI tests**

Add tests near existing `trends` command tests:

- `test_heat_movers_command_help_lists_public_flags`
- `test_heat_movers_command_missing_database_writes_nothing`
- `test_heat_movers_command_prints_json_grouped_by_movement`
- `test_heat_movers_command_prints_table`
- `test_heat_movers_command_include_cooling_surfaces_cooling_watchlist`
- `test_heat_movers_command_rejects_invalid_dates_before_data_dir_creation`
- `test_heat_movers_command_rejects_invalid_baseline_before_data_dir_creation`
- `test_heat_movers_command_rejects_baseline_at_or_after_as_of`
- `test_heat_movers_command_rejects_invalid_config_before_data_dir_creation`
- `test_heat_movers_command_rejects_negative_limit`
- `test_heat_movers_command_existing_database_remains_read_only`

Reuse `_prepare_trend_cli_fixture()` and `_prepare_candidate_trend_cli_fixture()`
where possible. For JSON assertions, validate with:

```python
from fashion_radar.heat_movers import HeatMoversReport

report = HeatMoversReport.model_validate_json(result.output)
group_by_name = {group.name: group for group in report.groups}
assert "The Row" in {row.name for row in group_by_name["rising_tracked_entities"].rows}
```

Expected red command:

```bash
uv run pytest tests/test_cli.py -q -k heat_movers
```

Expected: command not found / missing implementation failures.

- [ ] **Step 2: Implement CLI command**

In `src/fashion_radar/cli.py`:

- Import `build_heat_movers`, `render_heat_movers_table`, and `HeatMoversReport` only if needed for type checks.
- Add `HeatMoversOutputFormat = Literal["table", "json"]`.
- Add a `HEAT_MOVERS_FORMAT_OPTION` matching existing format option style.
- Add:

```python
@app.command(name="heat-movers")
def heat_movers_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    baseline_as_of: str | None = typer.Option(None, help="UTC baseline timestamp."),
    limit: int | None = typer.Option(5, min=0, help="Maximum rows per heat mover group."),
    output_format: HeatMoversOutputFormat = HEAT_MOVERS_FORMAT_OPTION,
    include_cooling: bool = typer.Option(False, help="Include a cooling watchlist group."),
) -> None:
    """Review local observed new and rising heat movers."""
```

Implementation should mirror `trends_command` but:

- Use `build_trend_comparison(..., include_dropped=False, limit=None)`.
- If DB is missing, create an empty `TrendComparison` and still build a
  `HeatMoversReport`.
- Print JSON with `report.model_dump_json(indent=2)`.
- Print table with `render_heat_movers_table(report)`.
- Use clean error prefixes:
  - `Could not review heat movers: invalid --as-of`
  - `Could not review heat movers: invalid --baseline-as-of`
  - `Could not review heat movers: baseline-as-of must be before as-of`
  - `Invalid heat movers config`
  - `Could not review heat movers`

- [ ] **Step 3: Run CLI checks**

```bash
uv run pytest tests/test_cli.py -q -k heat_movers
uv run pytest tests/test_heat_movers.py tests/test_cli.py -q -k "heat_movers or trends_command"
uv run ruff check src/fashion_radar/cli.py tests/test_cli.py src/fashion_radar/heat_movers.py tests/test_heat_movers.py
uv run ruff format --check src/fashion_radar/cli.py tests/test_cli.py src/fashion_radar/heat_movers.py tests/test_heat_movers.py
```

Expected: all pass.

## Task 3: Dashboard Heat Movers View

**Files:**

- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Add dashboard tests**

Add tests near existing trend dashboard tests:

- `test_dashboard_heat_mover_rows_are_serialized_and_review_oriented`
- `test_render_heat_movers_warns_for_missing_scoring_without_data_dir_creation`
- `test_render_heat_movers_warns_for_query_errors`
- `test_render_heat_movers_shows_empty_state`
- `test_render_heat_movers_shows_grouped_rows`
- `test_dashboard_tab_labels_include_heat_movers_before_trend_deltas`
- `test_dashboard_main_routes_heat_movers_and_trend_deltas_by_label`

The expected row shape should include:

```python
{
    "section": "Rising tracked entities",
    "observed_status": "rising",
    "signal_kind": "entity",
    "type": "brand",
    "name": "The Row",
    "current_score": 3.0,
    "score_delta": 2.0,
    "current_mentions": 3,
    "mention_delta": 2,
    "current_label": None,
    "first_seen_at": "2026-06-01T09:30:00+00:00",
}
```

Expected red command:

```bash
uv run pytest tests/test_dashboard.py -q -k heat_mover
```

Expected: missing functions/constants.

- [ ] **Step 2: Implement dashboard helpers**

In `src/fashion_radar/dashboard/app.py`:

- Import `HeatMoversReport`, `build_heat_movers`, and `render_heat_movers_table` only as needed.
- Add constants:

```python
HEAT_MOVER_CAPTION = (
    "Local observed heat movement from configured RSS/web sources and imported manual "
    "signals. These grouped signals need review and describe only this configured source set."
)
HEAT_MOVER_EMPTY_MESSAGE = "No local observed heat movers in this comparison."
```

- Add `heat_mover_rows(report: HeatMoversReport) -> list[dict[str, Any]]`.
- Add `render_heat_movers(st, *, config_dir: Path, data_dir: Path, now: datetime | None = None)`.
- Reuse the same config/window/query error handling style as `render_trend_deltas`.
- Call `load_trend_comparison(..., include_dropped=False, limit=None)`.
- Call `build_heat_movers(comparison, limit_per_group=5)`.
- Add `"Heat Movers"` to `DASHBOARD_TAB_LABELS` before `"Trend Deltas"`.
- Refactor `main()` to route tabs by label instead of positional slice indices:

```python
tabs = st.tabs(list(DASHBOARD_TAB_LABELS))
tab_by_label = dict(zip(DASHBOARD_TAB_LABELS, tabs, strict=True))

with tab_by_label["Daily Brief"]:
    ...
with tab_by_label["Candidate Signals"]:
    ...
with tab_by_label["Heat Movers"]:
    render_heat_movers(st, config_dir=args.config_dir, data_dir=args.data_dir)
with tab_by_label["Trend Deltas"]:
    render_trend_deltas(st, config_dir=args.config_dir, data_dir=args.data_dir)
for entity_type, label in ENTITY_MENTION_TABS:
    with tab_by_label[label]:
        ...
with tab_by_label["Source Health"]:
    ...
```

The main-routing test should install a fake `streamlit` module through
`monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)`, monkeypatch
`parse_args`, `dashboard_summary`, `latest_candidate_report`,
`render_heat_movers`, and `render_trend_deltas`, then call `main()` and assert:

- `fake_streamlit.labels` equals `list(DASHBOARD_TAB_LABELS)`.
- `render_heat_movers` was called while the current fake tab label was
  `"Heat Movers"`.
- `render_trend_deltas` was called while the current fake tab label was
  `"Trend Deltas"`.
- `len(DASHBOARD_TAB_LABELS) == len(ENTITY_MENTION_TABS) + 5`.

- [ ] **Step 3: Run dashboard checks**

```bash
uv run pytest tests/test_dashboard.py -q -k "heat_mover or trend"
uv run ruff check src/fashion_radar/dashboard/app.py tests/test_dashboard.py
uv run ruff format --check src/fashion_radar/dashboard/app.py tests/test_dashboard.py
```

Expected: all pass.

## Task 4: Docs And Public Command Guardrails

**Files:**

- Modify: `README.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add docs tests first**

Extend `tests/test_cli_docs.py` with a focused test:

```python
def _section_after_heading(text: str, heading_pattern: str) -> str:
    match = re.search(heading_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    assert match is not None
    rest = text[match.start() :]
    next_heading = re.search(r"\n#{2,3}\s+", rest[1:])
    return rest if next_heading is None else rest[: next_heading.start() + 1]


def test_heat_movers_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    trend_doc = _read(ROOT / "docs" / "trend-deltas.md")
    dashboard_doc = _read(ROOT / "docs" / "dashboard.md")
    cli_reference = _read(CLI_REFERENCE)
    architecture = _read(ROOT / "docs" / "architecture.md")
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    agents = _read(ROOT / "AGENTS.md")
    checklist = _read(UPLOAD_CHECKLIST)
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (
        readme,
        trend_doc,
        dashboard_doc,
        cli_reference,
        architecture,
        checklist,
        changelog,
    ):
        assert "heat-movers" in text

    required_terms = (
        "local observed heat movement",
        "configured source set",
        "configured sources and imported local signals",
        "needs review",
        "no demand proof",
        "no platform coverage verification",
    )
    for text in (readme, trend_doc, dashboard_doc, architecture, boundaries, agents):
        normalized = _normalized_text(text).casefold()
        for term in required_terms:
            assert term.casefold() in normalized

    heat_mover_sections = (
        _section_after_heading(readme, r"^## .*heat-movers.*$"),
        _section_after_heading(trend_doc, r"^## .*heat movers.*$"),
        _section_after_heading(dashboard_doc, r"^## .*heat movers.*$"),
        _section_after_heading(cli_reference, r"^- `heat-movers`.*$"),
        _section_after_heading(architecture, r"^`heat-movers`.*$"),
        _section_after_heading(changelog, r"^- .*heat-movers.*$"),
    )
    forbidden_claims = (
        "hottest",
        "viral",
        "market-wide trend",
        "platform-wide popularity",
        "verified demand",
        "top social trend",
    )
    for text in heat_mover_sections:
        normalized = _normalized_text(text).casefold()
        for claim in forbidden_claims:
            assert claim.casefold() not in normalized

    assert REQUIRED_FLAGS_BY_COMMAND["heat-movers"] == (
        "--config-dir",
        "--data-dir",
        "--as-of",
    )
```

This intentionally scopes forbidden-claim absence to the new heat-movers
sections. Existing repo docs may keep negated boundary wording such as "not
verified demand"; the Stage 57 test must not force those disclaimers to be
removed.

Also update:

- `REQUIRED_FLAGS_BY_COMMAND` with `"heat-movers": ("--config-dir", "--data-dir", "--as-of")`.
- Public CLI command/help docs tests so the upload checklist installed-wheel help loop includes `heat-movers`.
- CHANGELOG coverage so the focused docs test fails if `CHANGELOG.md` omits the new command.

Expected red command:

```bash
uv run pytest tests/test_cli_docs.py -q -k heat_movers
```

Expected: docs missing command and boundary wording.

- [ ] **Step 2: Update docs**

Docs must say:

- `heat-movers` is a local read-only grouping over trend deltas.
- It reads existing local SQLite state and local config.
- It reuses configured scoring windows and candidate discovery snapshots.
- It does not write reports, SQLite, dashboards, configs, or entity files.
- It does not collect, scrape, crawl, call platform APIs, use browser automation,
  monitor, schedule, prove demand, verify platform coverage, rank sources, or
  implement compliance/policy/authorization/safety-review features.

Add examples:

```bash
uv run fashion-radar heat-movers --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar heat-movers --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "2026-06-12T12:00:00Z" --baseline-as-of "2026-06-05T12:00:00Z" --include-cooling --format json
```

Update `docs/github-upload-checklist.md` installed-wheel help loop to include
`heat-movers`.

The negative-limit CLI test should assert Typer's parse-time validation, not
the helper's direct `ValueError`:

```python
assert result.exit_code != 0
assert "Invalid value" in result.output
```

This assertion belongs in `test_heat_movers_command_rejects_negative_limit`
from Task 2.

The exact boundary vocabulary from `required_terms` must be added to all files
covered by that loop, including `README.md`, `docs/trend-deltas.md`,
`docs/dashboard.md`, `docs/architecture.md`, `docs/source-boundaries.md`, and
`AGENTS.md`.

- [ ] **Step 3: Run docs checks**

```bash
uv run pytest tests/test_cli_docs.py -q
uv run ruff check tests/test_cli_docs.py
uv run ruff format --check tests/test_cli_docs.py
git diff --check
```

Expected: all pass.

## Task 5: Integration Verification And Release Review

**Files:**

- Create: `docs/reviews/opencode-stage-57-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-57-release-review.md`

- [ ] **Step 1: Run targeted integration checks**

```bash
uv run pytest tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py -q
uv run ruff check src/fashion_radar/heat_movers.py src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py
uv run ruff format --check src/fashion_radar/heat_movers.py src/fashion_radar/cli.py src/fashion_radar/dashboard/app.py tests/test_heat_movers.py tests/test_cli.py tests/test_dashboard.py tests/test_cli_docs.py
git diff --check
```

- [ ] **Step 2: Run full release checks**

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

- [ ] **Step 3: Run installed-wheel smoke**

Use a temporary build and venv. Include:

```bash
fashion-radar --help
fashion-radar heat-movers --help
fashion-radar heat-movers --config-dir "$tmp_configs" --data-dir "$tmp_data" --as-of 2026-06-13T12:00:00Z --format json
```

The `$tmp_configs` directory should contain `scoring.yaml` copied from
`configs/scoring.example.yaml` and `entities.yaml` copied from
`configs/entities.example.yaml`. `$tmp_data` may be missing; the command should
return an empty read-only report and must not create SQLite.

- [ ] **Step 4: Submit release review to opencode**

The release review prompt must ask `opencode` to verify:

- `heat-movers` is read-only and local-only.
- It reuses `TrendComparison`/existing trend helpers.
- It does not add collection, scraping, APIs, browser automation, monitoring,
  scheduling, schema changes, report writes, dependencies, or compliance
  features.
- Docs avoid unsupported platform-wide/demand claims.
- Full verification commands passed.

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-57-release-review-prompt.md)" \
  > docs/reviews/opencode-stage-57-release-review.md \
  2> /tmp/opencode-stage57-release-review.err
```

Fix Critical and Important findings before commit.

- [ ] **Step 5: Commit and upload**

After verification and release approval:

```bash
git status --short --branch
git add <stage-57-files>
git diff --cached --check
git commit -m "Add local heat movers view"
```

Try normal push with non-persistent extraheader. If git HTTPS fails with the
known GnuTLS issue, use the GitHub Git Data API fast-forward path, verify local
and remote refs/trees match, then confirm GitHub Actions succeeds.

Final handoff summary must include:

- Repo status
- Verified commands
- Uncommitted files
- GitHub Actions URL and conclusion
- Next step
