# Stage 128 Plan Review

## Verification performed
- Ran `external-tool-workflow --help` and `external-tool-readiness --help`: both expose exactly the 9 options the design claims (`--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`, `--input-format [csv|json]`, `--pattern`, `--source-name`, `--format [table|json]`). Design's option set is accurate and complete.
- Confirmed current docs are stale exactly as described: `cli-reference.md:151` (workflow) misses `--input-format/--pattern/--source-name`; `cli-reference.md:166` (readiness) documents only `--adapter`/`--format`.
- Confirmed the RED regex anchors on the exact command bullet; both target bullet bodies contain no nested `^- ` items, so extraction is scoped correctly.
- No existing test pins the old "Supports" sentences; only an unrelated smoke match in `test_first_run_smoke.py:1797`.
- No markdown linter (prettier/markdownlint/mdformat) enforces wrap width.
- All verification-referenced test names exist; no name collision for the new helper/test.

## Review focus answers

1. **Addresses drift without runtime change?** Yes. Pure docs edit + a docs-only test. No CLI code touched.
2. **RED test specific enough?** Yes. `_cli_reference_command_entry` extracts one bullet via a command-name-anchored regex and asserts each option string inside that bullet, cross-checking the option name against Typer help. A whole-file search would false-pass (e.g. `community-handoff-workflow` shares the same flags); bullet-scoping closes that hole.
3. **Readiness wording stays local read-only?** Yes. The plan explicitly preserves the `shutil.which`/local read-only sentence and the "does not inspect directories… validate rows" sentence, so listing the extra options does not imply directory inspection or file validation.
4. **Scope clean?** Yes. Explicit exclusion list matches `AGENTS.md` boundaries — no runtime CLI, deps, lockfile, connectors, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit behavior.
5. **Verification sufficient?** Yes. Focused docs/CLI tests + ruff check/format, then full release gate (release hygiene, full pytest, ruff, format, `UV_NO_CONFIG=1 uv lock --check`, `git diff --exit-code -- uv.lock`, whitespace, token scan, auth-header scan). Follows `AGENTS.md` mirror/lock conventions.

## Critical findings
None.

## Important findings
None.

## Minor findings
1. **Task 2 "Replace" blocks drop indentation.** The plan shows the old/new "Supports …" strings without the 2-space indent that the actual continuation lines carry (`cli-reference.md:151,166`). The implementer must match the indented text when editing; flag this so the agent doesn't copy the plan block verbatim into `oldString`.
2. **Readiness option semantics (optional polish).** The readiness "Supports" sentence will now list `--directory/--config-dir/--data-dir/--input-format/--pattern/--source-name`. The preserved "does not inspect directories" wording prevents a misread, but mirroring the help text (e.g. noting these are "used in printed commands only" / overrides) would make the intent clearer. Not required.
3. **Implicit regex assumption (nit).** `_cli_reference_command_entry` assumes the target bullet body has no nested `^- ` list items. True today for both commands; worth a one-line note so future bullets with sub-lists don't silently over-truncate.

## Final statement
**No Critical or Important blockers.** The design and plan are approved for implementation as docs/test-only scope. Proceed to Task 1 (RED test).
