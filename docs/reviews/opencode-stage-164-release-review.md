# Stage 164 Release Review

## Summary

Stage 164 meets its objective of making human-readable lint table finding-count
labels consistent across the source-pack, entity-pack, and community-signal lint
surfaces. A new leaf module `src/fashion_radar/lint_formatting.py` exposes
`format_count_label` and `format_finding_counts`, and all three renderers
(source-pack, entity-pack, community-signal single-file and directory aggregate +
per-file) now route through it. The local `_format_finding_count` is removed from
`source_packs.py`, and the entity/community renderers that previously emitted
fixed plural labels now singularize `1 error` / `1 warning`.

Stage 162 behavior is exactly preserved: the new `format_count_label` logic
(`label = singular if count == 1 else plural; f"{count} {label}"`) is identical
to the removed helper, and the pre-existing source-pack regression assertions at
`tests/test_source_packs.py:298` (`0 errors, 0 warnings, 0 info`) and `:326`
(`0 errors, 1 warning, 0 info`) plus the Stage 162 singular/plural assertions at
`:360`/`:407` continue to pass unchanged (test_source_packs.py was not modified
by this stage).

I reproduced the full release gate against the current working tree: 1333 passed,
`ruff check .` clean, `ruff format --check .` clean (143 files),
`uv lock --check` resolved 84 packages, first-run smoke passed, release hygiene
passed, `git diff --check` clean, no `ghp_` secret matches, and no configured
github extraheader. The directory per-file line and the docs example keep
`{row_count} rows` / `1 rows` row-count grammar, so only finding-count grammar
changed.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Adjacent non-lint count grammar intentionally left as-is (out of scope, no
   action required for this release). `src/fashion_radar/community_handoff_check.py`
   and `src/fashion_radar/importers/manual_signals.py` still emit unconditional
   `{count} errors`. The Stage 164 scope explicitly limits work to source/entity/
   community lint tables, so this is correct. Flagged only as a future-stage
   consistency candidate.

2. `lint_formatting` has no direct unit test. It is exercised transitively
   through all three renderer suites (entity singular/plural, community single-file
   singular/plural, community directory singular/plural for both aggregate and
   per-file lines, and the docs grammar regression), plus the existing source-pack
   regression coverage. Coverage is adequate; a direct edge-case test would be a
   low-cost future hardening addition, not a blocker.

## Verification Assessment

I independently reproduced the release gate:

- `uv --no-config run --frozen pytest -q`: 1333 passed in 33.61s.
- `uv --no-config run --frozen ruff check .`: All checks passed.
- `uv --no-config run --frozen ruff format --check .`: 143 files already formatted.
- `UV_NO_CONFIG=1 uv lock --check`: Resolved 84 packages.
- `scripts/check_first_run_smoke.py`: First-run sample smoke passed.
- `scripts/check_release_hygiene.py`: Release hygiene checks passed.
- `git diff --check`: clean.
- `rg -n 'ghp_[A-Za-z0-9]+' .`: no matches.
- `git config --get-all http.https://github.com/.extraheader`: no configured
  extraheader.

Scope adherence verified by diff inspection:

- Source-pack renderer output is byte-for-byte equivalent to Stage 162; the
  shared helper is a pure rename/move of the prior private function.
- Entity-pack and community-signal single-file and directory aggregate `Findings:`
  lines now singularize correctly.
- Directory per-file line changes only finding-count grammar; `{file.row_count} rows`
  and `{file.valid_row_count} import-ready` are preserved.
- The docs example keeps `1 rows` (row-count grammar intentionally untouched) and
  only changes `1 errors` to `1 error`.
- No JSON output, lint model, severity, sorting, strict-mode, or CLI command-flow
  changes; no social connectors, scraping, browser automation, platform APIs, or
  other prohibited scope.
- Review artifacts (spec 174 lines, plan 729 lines, plan review 135 lines, plan
  rereview 203 lines, code review 92 lines) are present, non-stub, and contain
  completed review output with no live-capture placeholders or truncation.

## Verdict

Approved for commit and push.

The final diff meets the Stage 164 objective. Tests are sufficient across all
three lint surfaces for singular and plural behavior and for source-pack
regression risk (Stage 162 assertions plus 7 new focused tests). Directory
per-file output changed only finding-count grammar, not row-count grammar. Docs
changes and review artifacts are clean and complete. No out-of-scope behavior
changed. No critical or important findings.
