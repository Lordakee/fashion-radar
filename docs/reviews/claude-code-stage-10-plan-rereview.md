Not approved

- Critical: `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`, Task 2 proposed `TrendDelta` model still omits required fields from the design:
  - `current_internal_baseline_mentions`
  - `baseline_internal_baseline_mentions`
  - Change needed: add both fields to the planned model snippet, comparator mapping, JSON/model tests, and any explicit table/display decision.

- Important: Task 2 sorting requirements do not fully guarantee deterministic ordering. Same-name signals across entity/candidate kinds or signal types can still rely on input/dict construction order. Change needed: extend sort tie-breakers after `name` to include `signal_kind`, `signal_type`, and normalized comparison key, with a same-name regression test.

- Important: Task 3 does not require a focused test proving `build_trend_comparison()` actually calls existing `score_entities()` and `discover_candidates()`. Change needed: add spy/monkeypatch tests asserting each is called exactly twice for current/baseline snapshots, returned metrics flow into `compare_trends()`, and CLI/output `limit` is not passed into `discover_candidates()`.

- Important: Missing-DB JSON behavior needs explicit metadata/default-baseline assertions. Change needed: test `--format json` against a missing DB and assert exit code `0`, no `data_dir` creation, JSON parses as `TrendComparison`, requested `as_of` is preserved, omitted `--baseline-as-of` resolves from `scoring.current_window_days`, and `deltas == []`.

- Important: CLI option plumbing should explicitly test public Typer flags end-to-end. Add a test invoking `fashion-radar trends --as-of ... --format json --include-dropped --limit 1`, plus help-output assertions for `--include-dropped`, `--no-include-dropped`, `--limit`, `--baseline-as-of`, and `--format table|json`.

- Important: Task 4 still does not specify dashboard default `as_of` behavior from the design. Add implementation/tests deriving dashboard `as_of` from latest local `collected_at` when local items exist, falling back to current UTC only when the database exists but contains no items, then deriving `baseline_as_of` from loaded scoring config.

- Important: Task 2 does not explicitly require `_entity_key()` and `_candidate_key()` to use `normalize_alias_key()`. Add that requirement and tests proving repository normalization behavior is used.

- Important: Dashboard incompatible-DB handling may still be preempted by existing dashboard startup queries. Add a task/test ensuring dashboard startup remains graceful with an incompatible existing DB, or that trend-tab schema errors are not masked by global summary failures.

- Important: Dashboard invalid/missing config no-creation behavior should be explicitly tested. Add a dashboard test asserting invalid/missing config surfaces a concise error and does not create `data_dir` or a DB.

- Minor: Make dashboard visible copy more explicitly local, e.g. heading/caption/empty state: “Local observed signal deltas” and “computed from this local database only; needs review.”

- Minor: Expand docs/copy review checklist to include all visible dashboard strings: tab label, headings, captions, empty states, errors, and docs snippets.

- Minor: Consider centralizing read-only SQLite URI construction for CLI/dashboard trend paths to reduce path/escaping drift while preserving `mode=ro&uri=true`.

Positive coverage: the revised plan/design now substantially cover invalid config/date checks before DB opening, read-only rejection of incompatible existing DBs, dashboard schema verification without initialization/migrations, the ban on migrations/persistent trend tables/writable indexes/DB writes, dashboard `--config-dir` plumbing, conservative mixed-direction status labels, and runtime no-external-services boundaries.
