# Stage 191 Code Review

Reviewed the Stage 191 files only: report model, builder/renderer, template,
report/CLI/first-run smoke tests and validator, plus the Daily Brief /
no-new-command docs tests. No commands were run during the review.

## Critical

None.

The implementation satisfies the Stage 191 goal and honors every stated
boundary:

- **Derivation source is correct.** `build_daily_brief` consumes only
  already-built report rows (`EntityReport`, `CandidateReport`,
  `SourceHealthReport`, `CollectorRunReport`) passed in from
  `build_daily_report`. It performs no database queries, no matcher/storage
  access, and no recomputation.
- **No new command or flag.** `DAILY_BRIEF_NON_COMMAND_NAMES` and
  `test_daily_brief_docs_do_not_add_public_commands` assert
  `daily-brief`/`heat-narrative`/`narrative` are absent from public CLI
  commands, the help loop, the CLI reference, and any documented
  `fashion-radar` invocation.
- **No LLM/external API, no source acquisition, no social search, no compliance
  feature.** The brief is pure deterministic Python string construction.
- **No contract mutation of trend/heat/dashboard.** The `brief` field on
  `DailyReport` is purely additive; existing
  `metadata/entities/candidates/source_health/recent_runs` shapes are
  untouched.
- **No new write behavior.** `render_json_report`/`render_markdown_report` and
  the report-file write path are unchanged in behavior; the brief is in-memory
  content folded into the same `DailyReport`.

## Important

None.

The Daily Brief contract is deterministic and report-safe:

- **JSON contract is pinned and stable.** `contract_version="daily-brief/v1"`,
  `execution_mode="local_report_derived"`, fixed `Literal` enums for `kind` and
  section `name`, and `extra="forbid"` on all brief models. Tests pin top-level
  key order, brief key order, section names, item kinds, reason codes, and the
  two `boundaries` strings; first-run smoke validates the same contract.
- **Deterministic ordering.** Tracked/candidate items are sliced from the
  already-ordered report lists; source caveats are sorted by
  `(-consecutive_failures, source_name, source_type)` then backfilled with
  failed runs in recent-run order. Reason-code lists are built in fixed order.
  Markdown rendering sanitizes `|`/newlines via `_table_cell` and renders the
  brief before Top Signals.
- **No leak of matcher/storage internals or article content.** Brief titles are
  entity names / candidate phrases / source names; entity and candidate
  summaries are synthetic count+label strings. The brief carries no
  representative items/snippets, so `report_safe_snippet` content never enters
  it. Internal fields (`content_hash`, `normalized_url`, alias/reason/context
  terms) remain excluded.

## Minor

1. **Unbounded error strings in caveat summaries.** `_brief_item_for_source_health`
   and `_brief_item_for_recent_run` interpolate `last_error_message` /
   `error_message` verbatim into `DailyBriefItem.summary`. This is consistent
   with the pre-existing Source Health / Recent Runs sections, which also do
   not truncate these fields, so it is not a new leak and they contain no
   article content. If report-safety hardening is ever desired, capping these
   would be the one spot to do it.

2. **Possible duplicate source-caveat titles.** A source that records both a
   `source_health` failure and a failed collector run may yield two
   `source_caveats` entries with the same `title`. This is deterministic and
   within scope, just slightly redundant.

3. **Cosmetic fallback reuse.** `_render_daily_brief` uses the same
   `"- No daily brief items available."` line both for the global all-empty
   case and per-empty-section. Harmless and only asserted for presence, but a
   distinct per-section phrasing would read slightly cleaner.

## Verdict

Approve for release. The Stage 191 goal is met with deterministic, report-safe
contracts and strong test/docs coverage: unit, CLI, first-run smoke with drift
detection, and docs guards for both Daily Brief wording and the no-new-command
boundary. No Critical or Important issues. The three Minor items are optional
polish, not blockers.
