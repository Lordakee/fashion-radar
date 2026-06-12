Not approved

- `Critical:` `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`, Task 2 proposed `TrendDelta` model omits required fields from the design:
  - Missing `current_internal_baseline_mentions`
  - Missing `baseline_internal_baseline_mentions`
  - The design explicitly requires these to avoid ambiguity with `baseline_mentions`, because trend `baseline_mentions` means the baseline comparison snapshot’s current-window count, while existing scoring metrics also have internal baseline-window counts.
  - Change needed: add both fields to the model, comparator mapping, JSON behavior, any table/display decision, and tests.

- `Important:` `docs/superpowers/plans/2026-06-12-stage-10-trend-delta-plan.md`, Task 4 does not fully specify the dashboard default `as_of` behavior required by the design.
  - The design requires dashboard `as_of` to default to latest local `collected_at` when local items exist, falling back to current UTC only when the database exists but contains no items.
  - Change needed: add implementation and test steps for deriving dashboard `as_of` from local data, then computing `baseline_as_of = as_of - scoring.current_window_days`.

- `Important:` Task 2 should explicitly require comparison keys to use `normalize_alias_key()` for entities and candidates.
  - The design explicitly says not to use ad hoc lowercasing or punctuation stripping.
  - Change needed: update `_entity_key()` / `_candidate_key()` requirements and add tests proving repository normalization is used.

- `Important:` Dashboard trend error handling may be preempted by existing dashboard startup queries.
  - Current dashboard flow calls `dashboard_summary()` before tabs render; that path opens the existing DB through `create_sqlite_engine()` and lacks the proposed trend schema guard.
  - An incompatible existing DB could fail before the trend tab can show the intended concise schema error.
  - Change needed: add a task/test ensuring dashboard startup remains graceful with incompatible DBs, or that trend-tab errors are not masked by global summary failures.

- `Important:` Add a focused regression test proving `limit` is applied only after full current/baseline comparison.
  - The plan says not to pass CLI output `limit` into `discover_candidates()`, which is correct.
  - Change needed: add a test covering both current and baseline candidate discovery so baseline-only/dropped signals are not hidden before comparison.

- `Minor:` Task 1 duplicates this review gate.
  - Clarify whether this review output satisfies the Task 1 plan review artifact, or whether a separate saved review is still expected.

- `Minor:` Consider centralizing read-only SQLite URI construction.
  - The proposed `sqlite:///file:{db_path.as_posix()}?mode=ro&uri=true` matches existing style, but a helper would reduce path/URI escaping mistakes and keep CLI/dashboard behavior consistent.

- `Minor:` Runtime no-external-services wording is good, but keep it explicit in docs and tests.
  - Development verification commands using `uv`/package indexes are acceptable per the design, but Fashion Radar runtime behavior must remain fully local/read-only for trends.
