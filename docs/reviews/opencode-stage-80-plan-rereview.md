Now let me verify the target anchors exist and check the existing test helpers.
Let me verify a couple more details — the reviews directory naming and CHANGELOG structure.
# Stage 80 Plan Rereview — Verdict

Implementation may proceed **after fixing the one Important finding below**. No Critical findings.

## Direct answers to the four questions

1. **Tests satisfiable by planned prose?** Mostly yes, **except one term in Test 3** (see Important #1). Tests 1 and 2 are fully satisfiable; their multi-token terms each land on a single prose/table line.
2. **Risk of poisoning `_markdown_section` via inline `## ...` literals?** **No.** The new `## External Tool Import Roadmap` heading is inserted between line 12 (`## Contract Files`) and line 58 (`## External Tool Handoff Templates`); the only `_markdown_section` call against `community-signal-import.md` targets `## Directory Manifest` (line 269), far below the insertion point, so its section bounds are unaffected (`tests/test_cli_docs.py:1114`, helper at `:388`). The README addition is a `###` level-3 heading, which does not match the helper's `\n## ` terminator. The CLI-reference addition introduces no new heading. The new tests split on real heading strings, not inline literals.
3. **Docs/test-only and local-only?** **Yes.** File map is limited to `README.md`, `docs/community-signal-import.md`, `docs/cli-reference.md`, `tests/test_cli_docs.py`, `CHANGELOG.md`, plus spec/plan/review artifacts. `src/`, `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, dependency manifests, and `uv.lock` are explicitly excluded. Boundary language is repeated and correct.
4. **Dirty `uv.lock` handled safely?** **Yes.** Task 3 Step 3 backs up the local mirror-rewritten lock to `mktemp`, restores `HEAD:uv.lock` for `UV_NO_CONFIG=1 uv lock --check`, scans the public lock for mirror URLs, asserts `uv.lock` is never staged (`! git diff --cached --name-only | rg -x 'uv.lock'`), then restores the local mirror lock and leaves it unstaged. This matches the `AGENTS.md` lockfile rules.

## Important

1. **Test 3 prose/test mismatch on a line-wrapped substring.** `test_cli_reference_local_import_section_has_external_tool_route` (plan Task 1 Step 3) asserts `"community-signal-lint-dir -> community-candidates-dir -> community-handoff-check-dir"` against raw, non-normalized `section` text, but the planned CLI-reference prose (Task 2 Step 3, plan lines 247-249) wraps the line after `community-candidates-dir ->`, placing `community-handoff-check-dir` on the next line. The substring spans a newline and will not be found in raw text, so the red→green gate cannot pass with the prose inserted verbatim. Fix by either (a) re-wrapping the prose so the three `community-*` commands share one line (3/3/2 grouping instead of 3/2/3), or (b) asserting against `_normalized_text(section)` for the multi-command substrings. The other two multi-command substrings in the same test (`external-tool-adapters -> external-tool-readiness -> external-tool-workflow` and `import-signals-dir -> imported-review-workflow`) each fit on one prose line and are fine.

## Minor

- The File Map lists `docs/reviews/opencode-stage-80-plan-review-prompt.md` and `opencode-stage-80-plan-review.md` under "Add", but both already exist in the workspace (only the `*-code-review-*` pair is genuinely new). Not a blocker; the implementer should treat them as already-present rather than creating fresh.
- The proposed test literals include long single-line strings (e.g., the Validate-row table cell). The plan's `ruff check` / `ruff format --check` gates will catch any line-length regression; no action needed beyond running those gates.
