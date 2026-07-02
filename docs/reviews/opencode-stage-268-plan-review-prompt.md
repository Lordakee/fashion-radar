Review the Stage 268 plan before implementation.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-268-row-one-refresh-command-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-268-row-one-refresh-command-plan.md

Goal:
Add `row-one refresh` as the single local operation that runs collect, match,
daily report generation, ROW ONE latest-only site rebuild, readiness output,
and the fixed local URL message.

Review criteria:
- Plan feasibility against the current CLI/workflow code.
- Whether tests are executable as written.
- Whether the command order is collect -> match -> report -> ROW ONE site.
- Whether scheduling/local-ops snippets call `row-one refresh` instead of duplicating a shell chain.
- Whether scope avoids timer installation, daemon supervision, schema changes, new collectors, LLM calls, or compliance-review features.
- Whether docs and smoke discovery cover the new command.

Do not edit files. Return concise Critical / Important / Minor findings and a verdict.
