# Stage 84 Code Review

## Findings

**No Critical findings.**

**No Important findings.**

**Minor:**

1. **Review artifact capture needed cleanup** —
   `docs/reviews/opencode-stage-84-code-review.md` initially contained
   duplicated and truncated capture text from the review run. This artifact
   has been replaced with the completed review content before publication.
   This is housekeeping only and does not affect the docs/test change under
   review.

## Verification Performed By Review

- **Scope respected:** only `docs/github-upload-checklist.md` and
  `tests/test_cli_docs.py` are tracked modifications; the remaining untracked
  files are Stage 84 spec/plan/review artifacts. No `src/`, dependency
  manifest, `uv.lock`, CI workflow, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`
  changes were present.
- **Smoke block order:** the installed-wheel smoke block has
  `external-tool-readiness --help`, then
  `external-tool-readiness --adapter instaloader --format table`, then
  `external-tool-readiness --adapter instaloader --format json`, then
  `external-tool-readiness --adapter rednote_mcp --format json`.
- **Documented claim closed:** the upload checklist readiness prose already
  names the `instaloader` table and JSON pair, and the CLI reference already
  lists both. The installed-wheel smoke block now matches that claim.
- **Drift test strengthened:** `test_external_tool_readiness_upload_checklist_help_loop_and_smoke`
  preserves the help-loop, exact `--help`, `rednote_mcp`, and
  `scripts/check_first_run_smoke.py` assertions while adding exact
  installed-path checks for both `instaloader --format table` and
  `instaloader --format json`.
- **No runtime behavior added:** this is a docs/test-only change that exercises
  an existing documented command. It does not add source/platform acquisition,
  scraping, connector, browser/API/login/cookie/session/token, media download,
  monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product behavior.
- **Review commands observed clean:** focused readiness docs tests passed,
  `tests/test_cli_docs.py` passed, `ruff check` and `ruff format --check` for
  `tests/test_cli_docs.py` passed, and `git diff --check` for the two changed
  files passed.

Stage 84 satisfies the goal and intended scope.
