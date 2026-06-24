# Stage 193 Trend Heat Explanation Sidecar Design

## Objective

Add a read-only local explanation layer over existing trend deltas so a user
can see why a brand, designer, celebrity, product, category, or candidate
phrase is marked `new`, `rising`, `cooling`, `stable`, or `dropped` without
changing the existing `TrendComparison`, `TrendDelta`, `HeatMover`, or
dashboard row contracts.

## Background

Stage 190 added source-liveness diagnostics so users can verify whether the
configured public source set is currently reachable. Stage 191 added a Daily
Brief Heat Narrative so the daily report highlights what deserves review. Stage
192 polished the Daily Brief caveat output and cleaned full-project review
status.

The next product-value gap is explanation. Today the project can tell a user
that a signal moved, but it does not yet answer the narrow operational question:

```text
Why did this local signal move in this comparison?
```

The existing deterministic ingredients already exist inside `TrendDelta`:

- status
- signal kind and type
- current and baseline score
- score delta
- current and baseline mentions
- mention delta
- current and baseline distinct sources
- distinct-source delta
- current and baseline labels
- current and baseline growth ratios
- first-seen timestamp

That is enough to build a pure explanation sidecar over one `TrendComparison`
without querying new data, mutating trend contracts, or introducing any LLM or
external summarization dependency.

## Recommended Approach

Recommended option: add a new read-only command and pure module:

```text
fashion-radar trend-explanations
```

Why this option:

- It keeps the existing `trends` JSON contract untouched. Existing tests and
  downstream consumers continue to parse `TrendComparison` exactly as before.
- It avoids mutating `HeatMoversReport` or dashboard row shapes, which the user
  and previous stages explicitly kept stable.
- It gives users a practical, directly usable tool instead of only embedding
  explanations in one surface.
- It stays compatible with a later dashboard/report reuse path because the core
  explanation builder will be a pure module over `TrendComparison`.

Rejected options:

1. Add fields directly to `TrendDelta`:
   rejected because it mutates the existing trend JSON contract and broadens the
   blast radius for CLI, dashboard, docs, first-run smoke, and any downstream
   parsing.
2. Add fields directly to `HeatMover`:
   rejected because it mutates the grouped report contract and still would not
   explain stable or dropped trend deltas outside heat-mover groups.
3. Only add explanation text to the table output of `trends`:
   rejected because it leaves JSON consumers without a structured explanation
   surface and still entangles the new behavior with an existing contract.

## Scope

In scope:

- Add a new pure module for deterministic explanation building over one
  `TrendComparison`.
- Add a new read-only CLI command:

  ```bash
  fashion-radar trend-explanations
  ```

- Support `--format table|json`.
- Reuse the same read-only data-loading flow as `trends`:
  - `--config-dir`
  - `--data-dir`
  - `--as-of`
  - optional `--baseline-as-of`
  - optional `--limit`
  - optional `--include-dropped`
- Produce explanations for entity and candidate deltas.
- Keep explanation language conservative:
  - `local observed`
  - `configured sources and imported local signals`
  - `needs review`
  - no demand proof
  - no platform coverage verification
- Add deterministic JSON models with stable key order for the new command only.
- Add focused tests for:
  - explanation reason-code derivation;
  - stable JSON shape for the new sidecar contract;
  - empty comparison behavior;
  - missing-database read-only behavior;
  - CLI table and JSON output;
  - docs wording and command discoverability.
- Update README, CLI reference, architecture, trend-deltas docs, dashboard docs,
  upload checklist, and changelog.
- Record Stage 193 plan/code/release reviews under `docs/reviews/`.

Out of scope:

- No changes to `TrendDelta`, `TrendComparison`, `HeatMover`,
  `HeatMoversReport`, dashboard trend rows, dashboard heat rows, scoring
  formulas, candidate scoring formulas, or matching behavior.
- No changes to existing `trends` JSON output.
- No changes to existing `heat-movers` JSON output.
- No new network requests, source acquisition, scraping, browser automation,
  platform APIs, monitoring, scheduling, ranking, demand proof, or coverage
  verification.
- No compliance-review product feature.
- No LLM summarization.
- No new report-file writes.
- No dashboard tab in this stage.

## Architecture

Stage 193 adds a sidecar command and a pure explanation module:

```text
SQLite
  -> existing build_trend_comparison(...)
  -> TrendComparison
  -> build_trend_explanations(...)
  -> TrendExplanationReport
  -> CLI table/json output
```

The core builder must be pure:

```python
def build_trend_explanations(
    comparison: TrendComparison,
    *,
    limit: int | None = None,
) -> TrendExplanationReport: ...
```

The CLI command should reuse the same config/date/schema/missing-database logic
as `trends`, then call the explanation builder over the returned
`TrendComparison`.

This keeps the new feature:

- deterministic;
- read-only;
- local-only;
- contract-safe for existing trend/heat consumers.

## Data Model

Use Pydantic models with `ConfigDict(extra="forbid")`.

```python
class TrendExplanationItem(BaseModel):
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


class TrendExplanationReport(BaseModel):
    contract_version: str = "trend-explanations/v1"
    execution_mode: Literal["local_read_only"] = "local_read_only"
    as_of: datetime
    baseline_as_of: datetime
    item_count: int = 0
    items: list[TrendExplanationItem] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
```

Boundary strings:

1. `Configured sources and imported local signals only; no demand proof.`
2. `No platform coverage verification is performed.`

## Explanation Rules

Explanation order must follow the existing `TrendComparison.deltas` order. The
sidecar must never re-rank or regroup deltas.

Each explanation item derives from one `TrendDelta`.

### Headline format

- `new`: `Local observed new {signal_kind} signal needs review.`
- `rising`: `Local observed rising {signal_kind} signal needs review.`
- `cooling`: `Local observed cooling {signal_kind} signal needs review.`
- `stable`: `Local observed stable {signal_kind} signal needs review.`
- `dropped`: `Local observed dropped {signal_kind} signal needs review.`

`signal_kind` renders as:

- `tracked entity` for `TrendSignalKind.ENTITY`
- `candidate phrase` for `TrendSignalKind.CANDIDATE`

### Summary format

The summary must be deterministic and metric-based, for example:

```text
Local observed tracked entity signal from configured sources and imported local
signals: score +3.00, mentions +4, distinct sources +2, label new from no
baseline label.
```

The summary should include:

- score delta;
- mention delta;
- distinct-source delta;
- current and baseline labels when present;
- one short status-specific explanation clause.

### Reason codes

Common reason codes:

- `status_new`
- `status_rising`
- `status_cooling`
- `status_stable`
- `status_dropped`
- `score_increase_observed` when `score_delta > 0`
- `score_decrease_observed` when `score_delta < 0`
- `mention_increase_observed` when `mention_delta > 0`
- `mention_decrease_observed` when `mention_delta < 0`
- `source_diversity_increase_observed` when `distinct_source_delta > 0`
- `source_diversity_decrease_observed` when `distinct_source_delta < 0`
- `label_changed_observed` when `current_label != baseline_label`
- `candidate_signal_needs_review` for candidate phrases

Status-specific explanation clause:

- `new`: `Signal was not present in the baseline snapshot.`
- `rising`: `Score and/or mention movement increased in the comparison window.`
- `cooling`: `Score and/or mention movement decreased in the comparison window.`
- `stable`: `Score and mention movement did not agree on a rise or cooling signal.`
- `dropped`: `Signal was present in the baseline snapshot but not in the current snapshot.`

## CLI Contract

Add:

```bash
fashion-radar trend-explanations --config-dir ./configs --data-dir ./data --as-of 2026-06-12T00:00:00Z
```

Arguments:

- `--config-dir`
- `--data-dir`
- `--as-of`
- `--baseline-as-of`
- `--limit`
- `--format`
- `--include-dropped`

Output modes:

- `json`: `TrendExplanationReport`
- `table`: deterministic text with:
  - top-level local/boundary lines;
  - `As of` and `Baseline as of`;
  - one row per explanation item containing status, kind, type, name, headline,
    and summary.

Missing database behavior must mirror `trends`:

- exit code `0`;
- emit an empty `TrendExplanationReport`;
- do not create the data directory or SQLite database.

## Testing Strategy

Unit tests:

- explanation builder derives deterministic headlines, summaries, and reason
  codes from hand-built `TrendDelta` values;
- JSON top-level key order is stable;
- empty comparison report is useful;
- limit truncates the already-ordered list rather than re-sorting.

CLI tests:

- missing database JSON output is empty and read-only;
- invalid dates fail before data-dir creation;
- invalid config fails before data-dir creation;
- incompatible database remains read-only;
- JSON output parses as `TrendExplanationReport`;
- table output includes local-review boundary lines;
- `--include-dropped` surfaces dropped explanations.

Docs tests:

- command appears in README / CLI reference / upload checklist help loop;
- docs keep the local-only / no demand proof / no platform coverage
  verification wording;
- docs distinguish the explanation sidecar from the existing `trends` and
  `heat-movers` contracts.

## Acceptance Criteria

- Users can run `fashion-radar trend-explanations` against the same local
  database and config used by `trends`.
- Existing `trends` and `heat-movers` JSON contracts remain unchanged.
- The explanation report is deterministic, local-only, and metric-based.
- The explanation output explicitly stays inside configured sources and imported
  local signals and does not claim demand proof or platform coverage
  verification.
- Full tests, lint, release hygiene, first-run smoke, lockfile check, and
  mirror check pass before commit.
