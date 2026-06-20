# Stage 128 Code Review

## Verification performed
- Inspected `docs/cli-reference.md:148-180` diff and surrounding context.
- Inspected `tests/test_cli_docs.py` diff (helper at line ~326, test at line ~2005) and confirmed imports (`re`, `CliRunner`, `app`, `CLI_REFERENCE`, `_read`) pre-exist.
- Captured live Typer `--help` for both commands: all 9 documented options (`--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`, `--input-format [csv|json]`, `--pattern`, `--source-name`, `--format [table|json]`) present and matching.
- Re-ran the verified commands: docs filter `3 passed`, CLI filter `4 passed`, parity test `1 passed`, `ruff check`/`ruff format --check`/`git diff --check` all clean.
- Read `build_external_tool_readiness` (`src/fashion_radar/external_tool_readiness.py:144`): uses `shutil.which` only; new options feed `_readiness_steps` text and metadata model — no directory inspection, no file reads, no SQLite.

## Review focus answers
1. **Matches design/plan?** Yes. Helper signature, test body, expected-option tuples, and both "Supports" sentence edits match the plan verbatim, with the 2-space continuation indent correctly preserved (addressing plan-review Minor #1).
2. **Bullet-scoped parsing + help cross-check?** Yes. `_cli_reference_command_entry` anchors on `^- \`<command>\`:` with `re.escape` and stops at the next `^- \``, `\n## `, or EOF — closes the `community-handoff-workflow` false-positive hole. Each option is asserted both in the bullet (`option in entry`) and in real Typer help (`option_name in help_result.output`).
3. **Readiness wording local read-only?** Yes. The `shutil.which`/local read-only sentence and the "does not inspect directories … validate rows" sentence are preserved verbatim. Implementation confirms it: options are rendered into printed steps/metadata only.
4. **Scope clean?** Yes. Only `docs/cli-reference.md` + `tests/test_cli_docs.py` modified; `uv.lock` untouched; no runtime/deps/connector/scrape/browser/platform-API/monitoring/schedule/source-acquisition/demand-proof/ranking/coverage/compliance changes.

## Critical findings
None.

## Important findings
None.

## Minor findings
1. **Regex assumes no nested `^- \` items in bullet body** (already flagged as plan-review Minor #3). True today for both target bullets; a future sub-list would silently over-truncate. Worth a one-line note in a future stage if bullets grow sub-items.
2. **Duplicated option tuple.** Both commands share an identical 9-element tuple; could be a single constant. Current duplication is readable and explicit — style preference only.
3. **`option_name in help_result.output` is a loose substring check**, mitigated by `COLUMNS=120` rendering each option on its own line and by distinctive names. Acceptable; no false pass observed.
4. **`docs/reviews/opencode-stage-128-code-review.md` not yet present** in untracked files — expected, since this review produces it. Ensure it is committed in the Stage 128 commit per the plan's Task 4 file list.

## Final statement
**There are no Critical or Important blockers before release.** The implementation is approved as docs/test-only scope and is consistent with the Stage 128 design, plan, and `AGENTS.md` boundaries.
