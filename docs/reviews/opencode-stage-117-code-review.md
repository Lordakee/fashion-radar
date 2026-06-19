I'll review the Stage 117 implementation. Let me start by reading the relevant files in parallel.
Let me read the rest of the test file, focusing on the Stage 117 test, and the stage review artifacts.
Now let me read the review artifacts and check git status for scope violations, plus the example directory README.
Let me run the new test to confirm it passes, verify the anchor exists, and confirm the test fails for the right reason by temporarily reverting one pointer.
Test passes (GREEN). Now let me verify the RED behavior by temporarily removing the README pointer and re-running, then revert.
The test fails for the right reason when the README pointer is removed (fails on `external-tool-readiness` in the README scoped section). Let me confirm the first-run end marker and run the full docs suite + ruff to confirm no regressions.
All 60 docs tests pass and ruff is clean. The scope is correct: only the 5 intended docs/test files are modified (no `uv.lock`, `pyproject.toml`, or `src/` changes), plus untracked review/spec/plan artifacts.

## Stage 117 Review

### Critical Findings
None.

### Important Findings
None.

### Minor Findings
- **M1 (carried over, informational):** The design/plan/review-prompt artifacts still specify `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` for review, while `AGENTS.md` and `docs/github-upload-checklist.md:519` mandate `claude --effort max --permission-mode plan`. Consistent with the user's explicit glm-5.2 request; not a blocker.
- **M2 (trivial redundancy):** The trailing standalone assertion at `tests/test_cli_docs.py:1664-1667` re-checks the CLI section anchor that the loop at `:1662` already verifies. Harmless but redundant.

### Verification Of The 6 Requested Points
1. **Point to checked-in example README** — all four summary docs link `examples/community-tool-handoff-directory.example/README.md` within their scoped sections (`README.md:113`, `cli-reference.md:225`, `first-run.md:102`, `github-upload-checklist.md:163,172`). ✓
2. **`generic_community_export` CSV/JSON preflight examples** — present in all four scoped sections. ✓
3. **Reference `external-tool-readiness` / `external-tool-workflow`** — present in all four scoped sections. ✓
4. **CLI sibling-relative anchor link** — `cli-reference.md:234` uses `community-signal-import.md#external-tool-export-directory-examples` (no `docs/` prefix), correct for a sibling file. ✓
5. **Test section-scoped + fails for right reason** — `test_external_community_tool_directory_preflight_examples_are_discoverable` uses `between()` to scope four sections, then asserts 9 tokens each. Confirmed RED: removing the README pointer fails the test on `external-tool-readiness` in the *README section specifically* (not elsewhere); confirmed GREEN after restore. ✓
6. **No scope violations** — `git status` shows only the 5 intended files modified; `git diff --exit-code -- uv.lock pyproject.toml` exits 0; no `src/` edits. The change adds discoverability pointers only — no connector/scraping/scheduling/monitoring/ranking/source-acquisition behavior. ✓

### Final Statement
**The Stage 117 change is ready to ship.** It is a clean docs/tests-only node that matches the reviewed and rereviewed plan (all five prior Important findings I1–I5 are resolved in the implementation), passes the full `tests/test_cli_docs.py` suite (60 passed) and ruff, stays within the `AGENTS.md` scope boundaries, and the new test genuinely gates the four discoverability pointers.
