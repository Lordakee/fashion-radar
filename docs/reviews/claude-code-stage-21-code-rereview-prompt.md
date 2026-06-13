# Claude Code Stage 21 Code Rereview Prompt

You are rereviewing the final Stage 21 diff for `/home/ubuntu/fashion-radar`
in read-only mode. Do not edit files. Use maximum reasoning.

## Context

Claude Code previously approved Stage 21 release checks in
`docs/reviews/claude-code-stage-21-code-review.md`.

After that review, one unrelated test argument was removed from
`test_imported_signals_command_missing_database_is_read_only` so the test stays
focused on the missing-database behavior. No production code changed after the
approval.

## Review Scope

Review the current uncommitted diff against `fee145b`.

Confirm:

1. The only production behavior change remains the table label
   `Matches:` -> `Matched rows:`.
2. JSON output and query behavior are unchanged.
3. CLI validation and special-character path regressions remain valid.
4. The missing-database test still covers no data-dir creation without the
   extra `--lookback-days` argument.
5. No scope-expanding behavior or docs wording was introduced.

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 21 release checks`
- `Not approved`
