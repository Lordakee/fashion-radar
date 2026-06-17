I'll perform a release review for Stage 63. Let me start by gathering the relevant context.
Let me read the core implementation and tests in parallel.
Now let me look at the CLI integration and first-run smoke changes.
Let me check the first-run smoke test changes and the adapters registry for context.
Let me check the adapter registry to confirm it doesn't inspect directories (a key boundary), and review remaining docs.
Let me independently verify by running targeted tests and inspecting actual command output, plus confirm the smoke command ordering.
Let me run independent verification: targeted tests, token/mirror scans, and lint checks.
The token scan flagged a match in the new review-prompt doc. Let me investigate whether prior committed review docs contain this same string (established pattern vs. new leak).
The review-prompt doc contains the literal token string on line 109 while claiming "no matches" on line 110. Let me check whether the hygiene script itself scans for this token to confirm severity.
Hygiene passed because the doc is currently untracked. Let me confirm the secret scan scope and what happens once the file is tracked.
Confirmed critical issue. Let me verify git state is clean after my experiment and check the token isn't elsewhere in untracked review docs.
Git state is clean. Let me do a final sweep across all Stage 63 untracked files for any other secret/auth strings.
## Stage 63 Release Review — Findings

### Critical (must fix before commit)

**1. Literal GitHub token in the new review-prompt doc — fails the project's own release-hygiene gate once tracked.**

`docs/reviews/opencode-stage-63-release-review-prompt.md:109` contained the literal repository GitHub token inside the quoted scan command, while line 110 claimed the scan returned "no matches." The doc was itself a match, so the claim was self-contradictory.

Evidence — I simulated tracking the file and reran hygiene:

```
forbidden secret in tracked file: docs/reviews/opencode-stage-63-release-review-prompt.md:109: GitHub token: <redacted>
```

It only "passes" today because `scripts/check_release_hygiene.py:151` scans secrets over **tracked** paths and the file is still untracked. Committing Stage 63 (which lists this doc as a new file) will:
- break the release-hygiene / CI gate (`GITHUB_TOKEN_PATTERNS` matches it at `check_release_hygiene.py:72`), and
- commit a token in direct violation of `AGENTS.md` ("Do not commit ... tokens, or local account data").

This is the only Stage 63 file with a literal secret — the plan/spec/plan-review docs only contain boundary prose or generic regexes, and the prior-stage prompts (e.g. committed stage-62) carry no `ghp_` literal.

**Fix (do not commit the literal):** redact in `opencode-stage-63-release-review-prompt.md`, e.g. `rg -n "ghp_<redacted>" ...`, or reword to describe the scan without the value. After redaction the "no matches" line becomes true.

### Important

None. I independently verified the full contract holds:
- `--adapter` optional; with it → 2 rows; without → 7 adapters × 2 = 14 JSON items (`src/fashion_radar/external_tool_templates.py:107-152`, verified 14 items / 8-field header).
- `--format json` emits only `{"items": [...]}`; `--format csv` emits only the 8-field CSV; table includes metadata, adapter id, header, item values, field mappings, commands, boundaries (`external_tool_templates.py:155-228`).
- No side effects: registry only stringifies `directory`/`config_dir`/`data_dir` (`external_tool_adapters.py:100-102` — no `.exists()`/`.iterdir()`/glob), and `tests/test_cli.py` `test_external_tool_template_command_is_print_only_for_paths` asserts dirs/SQLite are not created.

### Minor (optional cleanup)

- `docs/community-signal-quality.md`: the new `external-tool-template` sentence is appended to the preceding paragraph with no blank-line separation (diff context), unlike the parallel addition in `community-signal-import.md` which sits as its own block. Cosmetic only; the docs-boundary test still passes.

### Verification performed
- Targeted suite `tests/test_external_tool_templates.py tests/test_first_run_smoke.py tests/test_cli.py tests/test_cli_docs.py`: **358 passed**.
- `ruff check .`, `ruff format --check .`, `uv lock --check`: **passed**.
- Token scan across the worktree: only the review-prompt doc match above.
- `uv.lock` mirror scan: **no matches**.
- Smoke integration (command order + shifted captured indexes `[4]`, `[16]`–`[19]`) is internally consistent and covered by the full suite.

**Recommendation:** fix the token redaction in the review-prompt doc, then this Stage is clear to commit. I did not edit anything — say the word if you want me to apply the redaction.
