Review the Stage 268 implementation before commit.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-268-row-one-refresh-command-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-268-row-one-refresh-command-plan.md

Goal:
Add `row-one refresh` as a single local operation that runs collect, match,
report generation, and ROW ONE latest-only site rebuild, then prints readiness
and the fixed local URL.

Review criteria:
- The command reuses existing workflow helpers and does not shell out to the CLI.
- The command order is collect -> match -> report -> ROW ONE site.
- The command always rebuilds ROW ONE with latest-only cleanup.
- Scheduling/local-ops snippets call `row-one refresh` instead of duplicating a shell chain.
- Smoke tests and deterministic first-run command ordering are updated consistently.
- Docs do not show unsupported `row-one refresh --latest-only`.
- No timer install, daemon supervision, schema changes, new collectors, LLM calls, or compliance-review features.
- Tests and docs cover the new entrypoint.

Return Critical / Important / Minor findings and verdict. Do not edit files.
