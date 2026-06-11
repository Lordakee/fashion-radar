# Claude Code Stage 7 Plan Rereview

Reviewed against local head `eb52d36`.

## Summary

Claude Code rereviewed the Stage 7 design and plan after fixes to the initial
plan review findings. The prior Critical and Important issues are resolved, and
Stage 7 is approved for implementation.

## Verification

- Confirmed `%` escaping is now mode-specific:
  - raw `%` for GitHub Actions
  - `\%` for cron
  - `%%` for systemd
- Confirmed the plan updates `tests/test_stage1_hardening.py` when replacing
  the dead default source name.
- Confirmed cron snippets include a `PATH` line.
- Confirmed timezone semantics are required in snippets/docs:
  - cron/systemd use machine local time
  - GitHub Actions schedule uses UTC
  - `--as-of` is evaluated at run time in UTC for collection and report time
- Confirmed a representative source-pack YAML slice parses through the real
  `load_source_config()` and uses only `rss`/`gdelt` with RSS article extraction
  off.
- Confirmed the main implementation plan Stage 7 is re-scoped to scheduling and
  source packs only.

## Critical

None.

## Important

None.

## Minor

1. The design options list omits `--project-dir`; add it so design and plan
   agree.
2. The new source-template sync test duplicates existing hardening coverage.
3. GitHub Actions scheduling docs should mention that config files must exist in
   the checkout and generated reports are ephemeral unless users commit/upload
   them.

## Verdict

**Approved for Stage 7 implementation.**

Address the Minor items inline during implementation; no further plan gate is
required.
