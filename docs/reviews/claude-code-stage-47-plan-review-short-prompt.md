# Claude Code Stage 47 Plan Review Short Prompt

Review the Stage 47 first-run sample smoke plan. This is a plan review only;
do not edit files. Use maximum effort. Treat Critical and Important findings as
blockers.

## Goal

Add a tested, deterministic, local-only first-run smoke for GitHub users:
checked-in example CSV -> temp init/migrate/doctor -> lint/candidates preview
-> import dry-run/import -> imported summary/signals -> match -> report ->
candidates/trends JSON. No live collection or external platform access.

## Files

- `docs/superpowers/specs/2026-06-15-stage-47-first-run-sample-smoke-design.md`
- `docs/superpowers/plans/2026-06-15-stage-47-first-run-sample-smoke-plan.md`
- `docs/reviews/claude-code-stage-47-plan-review-prompt.md`

## Key Plan Points

- Add `scripts/check_first_run_smoke.py` using only Python standard library.
- Run the source checkout via `python -m fashion_radar`.
- Use `AS_OF="2026-06-13T12:00:00Z"` and
  `examples/community-signals.example.csv`.
- Assert generated SQLite DB, Markdown report, JSON report, imported rows, and
  parseable JSON outputs.
- Copy the checked-in CSV into a temp `exports/` directory for directory
  handoff smoke.
- Wire `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  into CI and `docs/github-upload-checklist.md`.
- Update README and `docs/community-signal-import.md` so first-run docs use
  checked-in examples instead of nonexistent local files.
- No live `collect`, RSS/GDELT fetches, scraping, crawling, browser
  automation, login/cookie/session tooling, platform connectors, external
  services, product compliance-review feature, dependency changes, lockfile
  changes, schema/scoring changes, or committed generated artifacts.

## Questions

1. Is this safe and useful as the next node after Stage 46?
2. Are the planned commands deterministic and fully local/offline?
3. Are the assertions strong enough without requiring non-empty candidate/trend
   business results?
4. Is the TDD/docs/CI plan credible?
5. Any Critical or Important blockers before implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If acceptable, include exactly:

```text
APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE
```
