I'll review the revised Stage 83 plan. Let me first read the relevant files and context.
Let me verify the actual files referenced to check the plan's accuracy.
Let me look at the prior review and the existing test helpers to verify the approach.
## Verdict: acceptable — no Critical or Important blockers remain.

All four prior Important findings are resolved:
1. **Link form** → Plan line 34 / spec line 21 now use sibling-relative `[Recover A Mirror-Rewritten Lockfile](dependency-mirrors.md#recover-a-mirror-rewritten-lockfile)`. Verified: `docs/dependency-mirrors.md:74` heading exists; anchor matches.
2. **Pinned strings** → Plan lines 40-42 enumerate three exact substrings (heading literal, anchor, operational phrase).
3. **Test scope** → Plan line 37 / spec line 30 explicitly use whole-file substring, not `_markdown_section_exact_heading("Before Upload")`.
4. **Pointer vs duplication** → Plan lines 31-32 / spec lines 23-26 say "pointer, not a duplicate command block"; pinned strings contain no command text.

Cross-checks: new test name `test_upload_checklist_mentions_mirror_lockfile_recovery` does not collide (`tests/test_cli_docs.py` has no such function); the `"Recover A Mirror-Rewritten Lockfile"` literal cross-pins to the Stage 82 test at `tests/test_cli_docs.py:702`; placement target ("after the `rg ... uv.lock` block, before `Historical boundary checks`") is unambiguous (`docs/github-upload-checklist.md:43-49`).

## Minor notes

1. **Task 2 doesn't name the test function.** The name `test_upload_checklist_mentions_mirror_lockfile_recovery` appears only in the Task 3 `pytest` command (line 51); adding it to Task 2 would prevent a name drift between implementation and verification.
2. **Implementation wording is spec'd only by the test strings.** Task 2 says "one or two sentences" but never restates the pinned phrase `"If \`uv.lock\` was changed by mirror-backed local operations before upload"` as the required doc text; the implementer must infer it from the test block. Works, but worth a one-line explicit "write this sentence" in Task 2.
3. **`REVIEW_PROTOCOL.md` drift widens.** Plan continues `opencode-stage-83-*` naming and `opencode` review tooling while `docs/REVIEW_PROTOCOL.md:13-19,57-58` prescribes `claude-code-stage-N-*` with Claude Code. Carry-forward from Stage 82, explicitly out of scope, but the gap is growing.
4. **Verification command style.** Plan Task 3 uses `uv --no-config run --frozen pytest ...`; the checklist (`docs/github-upload-checklist.md:20-22`) uses bare `uv run pytest` and `UV_NO_CONFIG=1` only for lock/sync. Both work; flagging only for convention consistency.
