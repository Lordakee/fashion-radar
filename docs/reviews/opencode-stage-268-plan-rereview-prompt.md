Review the revised Stage 268 plan before implementation.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-268-row-one-refresh-command-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-268-row-one-refresh-command-plan.md
Prior review: docs/reviews/opencode-stage-268-plan-review.md

Goal:
Add `row-one refresh` as the single local operation that runs collect, match,
daily report generation, ROW ONE latest-only site rebuild, readiness output,
and the fixed local URL message.

Please verify that the revised plan fixes the prior blocking findings:
- `scripts/check_first_run_smoke.py` is in scope and its schedule/local-ops
  assertions are updated from the old run/build chain to `row-one refresh`.
- The real first-run help loop and `expected_first_run_flow_commands(...)`
  both include `row-one refresh --help` in the same order.
- The deterministic fake schedule/local-ops outputs are updated with the new
  refresh wording.
- `tests/test_scheduling.py`, `docs/scheduling.md`, and pinned docs tests are reconciled with the new
  single-command refresh behavior.
- `--latest-only` expectations are either removed from generated schedule/local-ops snippet tests or preserved only in docs that describe internal refresh behavior.

Review criteria:
- Plan feasibility against the current CLI/workflow code.
- Whether tests are executable as written.
- Whether the command order is collect -> match -> report -> ROW ONE site.
- Whether scheduling/local-ops snippets call `row-one refresh` instead of
  duplicating a shell chain.
- Whether scope avoids timer installation, daemon supervision, schema changes,
  new collectors, LLM calls, or compliance-review features.
- Whether docs and smoke discovery cover the new command.

Do not edit files. Return concise Critical / Important / Minor findings and a verdict.
