# Claude Code Stage 5 Code Rereview

Base: `103ed10 feat: add stage 4 scoring and reports` + post-review working tree.
Scope: post-review fixes only; approved Stage 5 scope not re-litigated.

## Summary

All five fix areas from the rereview prompt were verified against the tree. Four
are fully landed in code and/or the Stage 6 plan. One claimed Stage 6 doc
requirement -- "dashboard host/security behavior, including no auth if bound
beyond `127.0.0.1`" -- is **not** present in the Stage 6 documentation contract.
That gap is a future-stage planning omission, not a Stage 5 code defect, so it
does not block the Stage 5 commit. Stage 5 code remains correct and the dashboard
still defaults to `127.0.0.1`.

## Critical

None.

## Important

1. **Claimed Stage 6 host/no-auth doc requirement is missing from the plan.**
   The prompt lists, among the applied fixes, that the Stage 6 plan now requires
   documenting "dashboard host/security behavior, including no auth if bound
   beyond `127.0.0.1`." It does not. The Stage 6 "Documentation contract"
   dashboard bullet (plan lines 733-736) covers only read-only / local-only /
   mention-count semantics. The only host reference is the Stage 5 design note
   (line 578: "Dashboard binds to `127.0.0.1` by default. Any host override must
   be explicit."), which is not a Stage 6 doc deliverable. This is the prior
   review's Minor #3 carried forward; it was reported as fixed but was not. The
   underlying risk is low (code defaults to localhost; `--host` lets a user opt
   into binding `0.0.0.0` with no auth), so this is not a Stage 5 commit blocker
   -- but the Stage 6 doc contract should gain a bullet such as: "Dashboard docs
   must state there is no authentication layer and that binding any host other
   than `127.0.0.1` exposes the dashboard on the network at the user's own risk."
   Add it now or as the first Stage 6 dashboard-doc task.

## Minor

1. **Scoring `min()` fallback still always evaluates (prior Minor #5).**
   `scoring.py:84-87` still computes `min(mention.collected_at ...)` as the
   `dict.get` default even when the stable-first-seen key is present. Negligible
   at MVP scale and explicitly deferred in the prior review. No action required.

## Fix verification

- **Dashboard tab relabel (prior Important #1):** Done. `dashboard/app.py:39-47`
  shows `Brand Mentions` / `Product Mentions` / `Celebrity Mentions`. No
  `Brand Heat` / `Product Radar` / `Celebrity Style` strings remain anywhere in
  `src/` or `tests/`. Also honestly carried into the Stage 6 dashboard doc bullet
  (mention-count, not heat-score ranking).
- **Engine disposal (prior Minor #2):** Done. All three `queries.py` helpers
  (`dashboard_summary`, `top_entities`, `source_health_rows`) now wrap their
  connection use in `try/finally` with `engine.dispose()`.
- **`.gitignore` build/dist (prior Minor #4):** Done. `.gitignore` lines 5-6 add
  `build/` and `dist/`; Stage 6 hygiene contract (plan line 749-750) restates
  both, and `.codegraph/*.db*` exclusion is named in the hygiene contract.
- **`entity_first_seen` retention (prior Minor #1):** Carried in. Stage 6
  retention task (plan lines 794-796) explicitly states `entity_first_seen` is
  retained across item pruning and that `last_seen_at` may refer to pruned item
  history.
- **Publishing boundary / mirror-friendly install:** Present. Plan lines 711-714
  (user controls remote creation and push) and 721-724 / 746 (mirror-friendly
  commands without writing mirror URLs into `uv.lock`).

## Answers

1. **Previous findings fixed or carried into Stage 6 docs?** Yes, except the
   dashboard host/no-auth doc requirement (Important #1), which was reported as
   carried in but is absent from the Stage 6 doc contract.
2. **Is Stage 5 ready to commit?** Yes. The code is correct, fixes are landed,
   and fresh verification (115 passed, ruff clean, lock/sync/build/install smoke)
   holds. The one open item is a Stage 6 planning bullet, not Stage 5 code.
3. **Is the updated Stage 6 plan safe to begin?** Yes, with the one-line
   documentation-contract addition above. Everything else (publishing boundary,
   hygiene, mirror, retention, scoring, CI/smoke) is concrete and safe.

## Verdict

**Approved for Stage 5 commit and Stage 6 implementation.**

Add the dashboard host/no-auth bullet to the Stage 6 documentation contract
before writing the dashboard docs so the plan matches what was reported fixed.
