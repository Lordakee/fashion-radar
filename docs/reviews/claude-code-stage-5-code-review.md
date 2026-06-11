# Claude Code Stage 5 Code Review And Stage 6 Plan Review

Base: `103ed10` + uncommitted working tree.
Local re-verification: `pytest -q` -> 115 passed; `ruff check .` -> clean.

## Summary

Stage 5 satisfies the approved plan. All six workflow commands exist, the
dashboard extra is optional and lazy-checked, schema v4 migration is additive
and non-destructive, stable entity first-seen is persisted from accepted matches
and preferred by scoring, and `clean-old-data` prunes by `collected_at` with
explicit matcher-row deletion and dry-run support. No social scraping or
account/cookie automation is introduced. No critical or important correctness
bugs found.

## Critical

None.

## Important

1. **Dashboard tabs show raw mention counts, not Stage 4 heat/labels.**
   `dashboard/queries.top_entities()` returns `COUNT(DISTINCT item_id)` per
   `(entity_name, entity_type)` with no confidence filter and no time window,
   yet the tabs are labeled "Brand Heat" / "Product Radar" / "Celebrity Style".
   Scoring (`scoring.py`) applies `min_match_confidence` and current/baseline
   windows and produces `heat_score` + `label`. The dashboard ignores all of
   that, so a high-count low-confidence entity ranks above a genuinely hot one,
   and the numbers will not match the report. This meets the literal Stage 5
   requirement (read-only, local-only, no collection on refresh) so it is not a
   commit blocker, but it is misleading. Either relabel the tabs as "Mentions"
   or surface `score_entities()` output. Recommend addressing before/with the
   Stage 6 dashboard docs so the README does not overstate behavior.

## Minor

1. **`entity_first_seen` is never pruned and `last_seen_at` can dangle.**
   `clean-old-data` intentionally leaves `entity_first_seen` intact (correct --
   stable first-seen must survive item pruning), but this means the table grows
   unbounded and `last_seen_at` can point to an interval whose items were
   deleted. By design, not a bug. Stage 6 data-retention docs must state
   explicitly that `entity_first_seen` is not pruned and why.
2. **Dashboard query engines are never disposed.** Each `queries.py` helper
   builds a fresh `create_sqlite_engine(...)` per call and never calls
   `engine.dispose()`. On repeated Streamlit reruns this leaks connection pools.
   Low impact for a single-user local app; consider a cached engine or
   `dispose()`.
3. **Configurable dashboard host has no auth.** Default `127.0.0.1` is correct.
   `--host` lets a user bind `0.0.0.0` with no authentication layer; note this
   security implication in the dashboard docs.
4. **`dist/` not in `.gitignore`.** The Stage 6 plan builds wheels under `/tmp`,
   but adding `dist/` (and optionally `build/`) is cheap insurance against
   committing artifacts. `.codegraph/*.db*` is already OS-ignored; confirm what
   enforces that before relying on it at commit time.
5. **Micro:** `scoring.py` `stable_first_seen.get(key, min(...))` always
   evaluates the `min()` fallback even when the key is present. Negligible at
   MVP scale; ignore unless profiling says otherwise.

## Answers to review questions

1. **Plan conformance:** Yes. Commands `collect/match/report/run/dashboard/
   clean-old-data` present; core install works without the dashboard extra;
   `streamlit`/`pandas` stay under `[dashboard]`; lazy spec check with install
   hint; binds `127.0.0.1`; import/refresh does not collect or hit the network.
2. **Correctness:** v1->v2->v3->v4 chain is sequential and additive; v4 only adds
   `entity_first_seen`, preserving items and matches (covered by
   `test_schema_migrates_v3_to_v4_*`). Stable first/last seen use the item's
   `collected_at` with min/max merge and accepted matches only -- idempotent
   across re-runs. Pruning deletes `item_entities` before `items` (no reliance
   on FK cascade), supports dry-run, and leaves collector-run/source-health
   history untouched. Scoring prefers the stable first-seen row and falls back
   to retained item history only when absent. `collected_at`-string comparison
   is sound because all new timestamps are UTC `isoformat()`. No bugs found.
3. **CLI safety/determinism:** `run` is serial collect->match->report with a
   single `as_of` used for both collection timestamp and report window, so no
   parallel DB writers and deterministic output. Commands tested via
   `CliRunner`. Good.
4. **Dashboard:** Read-only and local-only by default; queries only SELECT;
   optional deps handled correctly. See Important #1 on label semantics.
5. **Source/compliance boundaries:** Preserved. Collectors unchanged
   (RSS/RSSHUB/GDELT). No scraping, cookies, account pools, or CAPTCHA logic
   added.
6. **Tests:** Meaningful and sufficient for this stage -- migration
   preservation, first/last-seen merge across out-of-order items,
   prune-without-cascade (orphan check), stable-first-seen-after-prune,
   fallback-without-stable-row, dashboard empty/populated, and CLI coverage for
   every new command including the missing-extra path.
7. **Stage 6 plan:** Concrete, safe, sufficient. Publishing boundary is explicit
   (user controls remote/push), mirror-friendly docs without polluting
   `uv.lock`, hygiene + CI/smoke contracts are clear. Ensure the retention doc
   task explicitly covers the un-pruned `entity_first_seen` (Minor #1) and add a
   `dist/` ignore task (Minor #4).
8. **Before commit/Stage 6:** Nothing blocking. Optionally relabel dashboard
   tabs (Important #1) now; otherwise carry it into Stage 6 docs so the README
   stays honest.

## Verdict

**Approved for Stage 5 commit and Stage 6 implementation.**
