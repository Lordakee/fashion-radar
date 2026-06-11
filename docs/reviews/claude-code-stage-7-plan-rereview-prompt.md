# Claude Code Stage 7 Plan Rereview Prompt

You are Claude Code rereviewing Fashion Radar Stage 7 after fixes to
`docs/reviews/claude-code-stage-7-plan-review.md`.

Repository: `/home/ubuntu/fashion-radar`

Previous verdict:

- `Approved after fixes`

Files to review:

- `docs/superpowers/specs/2026-06-12-stage-7-daily-operations-design.md`
- `docs/superpowers/plans/2026-06-12-stage-7-daily-operations-plan.md`
- `docs/reviews/claude-code-stage-7-plan-review.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

Fixes applied:

- Replaced shared `daily_as_of_shell()` with per-context helpers:
  - `raw_as_of_shell()`
  - `cron_as_of_shell()`
  - `systemd_as_of_shell()`
- Tests now expect:
  - raw `%` for GitHub Actions
  - `\%` for cron command fields
  - `%%` for systemd unit files
- Cron snippet now includes:
  - `PATH=/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$HOME/.cargo/bin`
- Scheduling docs requirements now include:
  - cron/systemd use local machine timezone
  - GitHub Actions schedule uses UTC
  - manual snippets must preserve `%` escaping
  - `run --as-of` uses a run-time UTC timestamp for collection and report time
- Plan now explicitly modifies `tests/test_stage1_hardening.py` to expect the
  new default source name instead of `Vogue Business RSS`.
- Main implementation plan Stage 7 was re-scoped away from optional collectors
  and toward scheduling/source packs only.

Please review:

1. Are the previous Critical and Important findings fixed in the plan?
2. Are there any remaining blockers before Stage 7 implementation?
3. Does the Stage 7 plan remain safely scoped, with no new collectors or risky
   scraping?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 7 implementation
- Approved after fixes
- Do not proceed
