# Claude Code Stage 41 Plan Review Prompt

You are reviewing the Stage 41 CLI docs readiness plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Refresh public documentation so current CLI commands, path flags, and release
smoke checks are consistent, easy to audit, and ready for GitHub users.

## Proposed Technical Approach

- Add `docs/cli-reference.md` as a compact current command map.
- Update README and scoped docs so import/review examples use matching
  `--config-dir`, `--data-dir`, and `--reports-dir` values.
- Update manual/community import docs to show current `--data-dir` and
  `--imported-at` usage.
- Update source-pack, trend, dashboard, and data-retention examples for current
  path and flag behavior.
- Update `docs/github-upload-checklist.md` installed-wheel help smoke coverage
  for the current public command surface.
- Keep `docs/release-gate-stage31.md` historical; do not rewrite it.
- Keep this stage documentation-only.
- Use Claude Code with `--effort max` for plan and release review.
- Do not change product code, tests, dependencies, lockfiles, CI behavior,
  database schema, commands, scraping/crawling/platform automation, source
  acquisition, schedulers, watchers, or monitors.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-41-cli-docs-readiness-design.md`
- `docs/superpowers/plans/2026-06-15-stage-41-cli-docs-readiness-plan.md`

## Context

The previous temporary rule that Stage 41 review must use local opencode has
been canceled by the user. Treat any uncommitted `opencode-stage-41-*` files as
superseded review-attempt artifacts only; do not rely on them for approval.

The plan should remain documentation-only. It should not introduce source
connectors, scraping, crawling, browser automation, login/cookie/account/proxy
or CAPTCHA flows, platform APIs, source acquisition, schedulers, watchers,
monitors, or external services.

## Specific Questions

1. Is Stage 41 correctly scoped as a docs-only CLI readiness node?
2. Are the target files and boundaries complete for refreshing CLI examples
   without touching runtime behavior?
3. Does the plan now use Claude Code review gates consistently after the
   temporary opencode rule was canceled?
4. Are the path-consistency checks strong enough to catch import/review flows
   that write to `$PWD/data` but later read default user data paths?
5. Are the help-smoke and release verification steps sufficient before commit
   and push?

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 41 CLI DOCS READINESS
```
