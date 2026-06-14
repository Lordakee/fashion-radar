# Claude Code Stage 37 Plan Review Prompt

You are reviewing the Stage 37 local platform provenance plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Preserve sanitized local manual/community signal `platform` provenance through
storage and local review output.

## Proposed Technical Approach

- Add nullable `items.platform` storage and bump schema version from 4 to 5.
- Add a v4-to-v5 migration that adds `platform varchar(64)` if missing.
- Add optional `ItemRepository.upsert_item(..., platform=...)` support with
  blank-to-None normalization, leaving `CollectedItem` generic.
- Persist `ManualSignalRow.platform` from local CSV/JSON handoff rows through
  that repository parameter.
- Expose `platform` in `imported-signals` review rows, table output, and
  aggregate local platform counts.
- Keep platform as provenance only: no heat-score changes, no platform spread
  scoring, no coverage proof, no connectors, no scraping/crawling/browser
  automation/login-cookie/account/proxy/CAPTCHA/source-acquisition functionality.
- Continue dropping private/raw fields such as `author_handle`, `raw_comment`,
  `account_id`, paths, cookies, session files, browser profiles, and generated
  reports.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-37-local-platform-provenance-design.md`
- `docs/superpowers/plans/2026-06-14-stage-37-local-platform-provenance-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 37 LOCAL PLATFORM PROVENANCE
```
