# Stage 190 Source Liveness Diagnostics Design

## Objective

Add a read-only `source-liveness` diagnostic that probes configured public
fashion sources so users can tell whether their RSS/RSSHub feeds and GDELT query
lanes are reachable today before relying on daily reports.

## Background

Stage 188 redirected the roadmap toward source coverage, source health, matching
quality, and optional report summaries. Stage 189 repaired review-gate hygiene
so future stages can safely return to product work.

The public source pack currently lints cleanly, but `source-pack-lint` is
intentionally static YAML quality validation. It does not fetch feeds, check
whether GDELT returns records, or tell a user whether a configured source is
currently productive. That gap matters before expanding the source pack further:
the project should have a local way to validate source liveness without turning
the check into collection, storage, source-health mutation, or coverage proof.

## Scope

In scope:

- Add a new `src/fashion_radar/source_liveness.py` module.
- Add a flat Typer command:

  ```bash
  fashion-radar source-liveness PATH --format table|json [--strict]
  ```

- Load the supplied source YAML or source-pack YAML with the existing
  `load_source_config(...)` path.
- Probe enabled `rss`, `rsshub`, and `gdelt` sources only.
- Include schema-valid disabled sources as `skipped` rows without network
  calls.
- For RSS/RSSHub:
  - fetch only the configured feed URL;
  - parse with `feedparser`;
  - classify live, degraded, empty, and failed outcomes.
- For GDELT:
  - call the GDELT Doc API with the configured query, `mode=artlist`,
    `format=json`, `timespan=<lookback_hours>h`, and `maxrecords=1`;
  - pass `gdelt_http_settings(source)` into the HTTP client factory so probes
    use the same GDELT-aware HTTP settings as the collector.
  - classify live, empty, and failed outcomes.
- Provide deterministic Pydantic result models and stable JSON key order.
- Provide table rendering with summary counts, rows, and explicit boundaries.
- Add unit tests with injected clients and no live network.
- Add CLI tests for table/json/strict behavior and artifact non-creation.
- Add concise docs in README, architecture, source-pack docs, source-pack
  quality docs, and CLI reference.

Out of scope:

- No source pack expansion in this stage.
- No live network tests in pytest or release gate.
- No SQLite reads or writes.
- No `collector_runs` or `source_health` mutation.
- No stored items, matching, scoring, reports, dashboard, digest, or workflow
  artifacts.
- No article page fetching or article extraction.
- No external/social/community handoff work.
- No platform coverage, demand proof, authorization, compliance, or policy
  review feature.

## Architecture

`source-liveness` is a separate diagnostics surface, not an extension of
`source-pack-lint` and not a wrapper around `collect_sources`.

This preserves existing boundaries:

- `source-pack-lint` remains local-only and non-fetching.
- `collect_sources` remains the ingestion path that owns persistence, collector
  runs, source-health state, and optional article enrichment.
- `source-liveness` performs bounded network probes and prints results only.

The module exposes:

```python
def build_source_liveness_report(
    path: Path,
    *,
    client_factory: SourceHttpClientFactory | None = None,
    clock: Callable[[], datetime] | None = None,
    monotonic: Callable[[], float] | None = None,
) -> SourceLivenessReport: ...

def render_source_liveness_table(report: SourceLivenessReport) -> list[str]: ...

def source_liveness_should_exit_nonzero(
    report: SourceLivenessReport,
    *,
    strict: bool,
) -> bool: ...
```

Tests use injected fake clients through `client_factory` so unit tests never
touch the network and never depend on host proxy settings.

## Data Model

Use Pydantic models with `ConfigDict(extra="forbid")`.

Enums:

```python
class SourceLivenessStatus(StrEnum):
    LIVE = "live"
    DEGRADED = "degraded"
    EMPTY = "empty"
    FAILED = "failed"
    SKIPPED = "skipped"


class SourceLivenessSeverity(StrEnum):
    OK = "ok"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
```

Per-source rows:

```python
class SourceLivenessResult(BaseModel):
    source_name: str
    source_type: SourceType
    enabled: bool
    target_type: Literal["url", "gdelt_query"]
    target: str
    status: SourceLivenessStatus
    severity: SourceLivenessSeverity
    code: str | None = None
    message: str
    checked_at: datetime
    elapsed_ms: int
    records_seen: int | None = None
    error_type: str | None = None
```

Report:

```python
class SourceLivenessFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SourceLivenessFinding(BaseModel):
    severity: SourceLivenessFindingSeverity
    code: str
    message: str


class SourceLivenessReport(BaseModel):
    contract_version: str = "source-liveness/v1"
    execution_mode: Literal["network_read_only"] = "network_read_only"
    path: str
    checked_at: datetime
    source_count: int
    enabled_count: int
    disabled_count: int
    probed_count: int
    live_count: int
    degraded_count: int
    empty_count: int
    failed_count: int
    skipped_count: int
    type_counts: dict[str, int]
    tag_counts: dict[str, int]
    error_count: int
    warning_count: int
    info_count: int
    results: list[SourceLivenessResult]
    findings: list[SourceLivenessFinding] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
```

`findings` is reserved for report-level issues such as invalid config. Normal
per-source outcomes live in `results`.

## Probe Semantics

Disabled sources:

- Status: `skipped`.
- Severity: `info`.
- Code: `source_disabled`.
- `elapsed_ms`: `0`.
- `target_type` and `target` are still derived from the schema-valid source:
  RSS/RSSHub use `url`, and GDELT uses `gdelt_query`.
- No network call.
- This applies after `load_source_config(...)` succeeds. A disabled source that
  is schema-invalid, such as a disabled RSS source without `url`, returns an
  `invalid_config` finding instead of a partial skipped row.

RSS/RSSHub:

- `live`: feed fetch succeeds, parse succeeds enough to expose entries, and
  `len(parsed.entries) > 0`.
- `degraded`: entries are present but `feedparser` marks the feed as bozo or
  malformed.
- `empty`: fetch succeeds and parses, but no entries are present.
- `failed`: fetch exception, unparseable response with no entries, or
  unexpected probe exception.

GDELT:

- Use `GDELT_DOC_API`.
- Use `gdelt_http_settings(source)`.
- `source-liveness` creates and closes clients per probed source, matching the
  existing collector style. In v1, the command reuses GDELT-aware settings but
  does not maintain command-global domain timing across separate GDELT sources.
  Each GDELT probe issues one request through one client, so the per-domain
  delay setting is present for collector parity rather than command-level
  pacing.
- Request params:

  ```python
  {
      "query": source.query or "",
      "mode": "artlist",
      "format": "json",
      "timespan": f"{source.gdelt.lookback_hours}h",
      "maxrecords": 1,
  }
  ```

- `live`: JSON object contains `articles` list with at least one article.
- `empty`: JSON object contains `articles: []`.
- `failed`: HTTP failure, JSON parse failure, non-object payload, missing
  `articles`, or non-list `articles`.

Severity mapping:

- `live`: `ok`.
- `skipped`: `info`.
- `empty` and `degraded`: `warning`.
- `failed` and invalid config findings: `error`.

## CLI Semantics

The command mirrors `source-pack-lint`:

```bash
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml --format json
uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml --strict
```

Output is printed before exit-code evaluation.

Exit rules:

- Exit 0 when there are no errors and either no warnings or `--strict` is not
  used.
- Exit 1 for invalid/unreadable config, failed probes, or warnings with
  `--strict`.
- Disabled-source `info` rows do not cause strict failure.
- Typer validation errors keep Typer's default behavior and must not call the
  builder.

## Rendering

Table output starts with:

```text
Source liveness: configs/source-packs/fashion-public.example.yaml
Contract version: source-liveness/v1
Execution mode: network_read_only
Checked at: 2026-06-24T02:00:00+00:00
Sources: 16 total, 16 enabled, 0 disabled, 16 probed
Results: 14 live, 0 degraded, 1 empty, 1 failed, 0 skipped
Types: gdelt=10, rss=6
Tags: gdelt=10, fashion_media=2, ...
Findings: 1 error, 1 warning, 0 info
Source | Type | Status | Severity | Records | Target | Message
```

Rows must sanitize pipes and newlines.

Boundary lines must make clear that this command:

- performs bounded network probes for configured RSS/RSSHub feed URLs and GDELT
  Doc API queries only;
- does not collect, store, score, match, report, open SQLite, update source
  health, fetch article pages, or prove demand/coverage.

## Testing Strategy

Unit tests in `tests/test_source_liveness.py`:

- stable JSON key shape;
- aggregate counts by status, severity, type, and tag;
- disabled sources skip without network call;
- invalid disabled sources return an invalid-config report, because source
  validation happens before per-source skipped rows are built;
- probe order matches source config order, keeps disabled rows in their original
  positions, and continues after failures;
- invalid config returns an error report without network calls;
- tests guard against accidental default network/client use;
- RSS and RSSHub live behavior plus RSS empty, degraded, and failed outcomes;
- GDELT params use `maxrecords=1` and `timespan=<lookback_hours>h`;
- GDELT probes receive settings from `gdelt_http_settings(source)`;
- GDELT live, empty, invalid-payload, and fetch-failure outcomes;
- deterministic `checked_at` and `elapsed_ms` through clock seams;
- table rendering includes summary, rows, boundaries, and sanitized cells;
- strict exit helper behavior.

CLI tests in `tests/test_cli.py`:

- help text lists `--format`, `--strict`, and network-read-only boundary;
- table output from builder;
- JSON output with stable keys;
- warning-only report exits 0 without strict and 1 with strict;
- error report exits 1 while still printing output;
- invalid format does not call builder;
- command does not create config/data/report directories or SQLite files.

Docs tests:

- source-pack docs mention `source-liveness`;
- source-pack quality docs still state lint is offline and link live checks to
  `source-liveness`;
- CLI reference lists the new command.

## Acceptance Criteria

- `source-liveness` works for configured RSS/RSSHub and GDELT sources with
  deterministic table and JSON output.
- The command is read-only aside from printing stdout/stderr.
- Tests use fake clients and no live network.
- `source-pack-lint` docs and behavior remain local-only and non-fetching.
- The next release gate remains green.
