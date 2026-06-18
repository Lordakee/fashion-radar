I'll review Stage 80 of Fashion Radar. Let me start by understanding the scope and examining the relevant files.
Now let me look at the diffs of the modified files and the review artifacts.
Let me read the plan, review artifacts, and examine the surrounding context of the inserted sections.
Let me examine the actual files in their current state, the test helpers, and the code review artifact.
The code-review.md is capturing this session's output. Let me examine the test helpers, the CLI reference section context, and verify the split markers.
Let me verify the normalization helpers and the downstream split marker in cli-reference.
Let me verify whether the test assertions actually pin the new content vs. being satisfied by pre-existing text (test tightness), by checking the pre-Stage-80 state.
Let me check the README heading structure around the new `###` subsection and whether any test extracts the enclosing section.
Let me run the focused tests and full doc-test suite plus lint to verify the working tree is green (confirming the plan-rereview's line-wrap fix took effect).
Let me verify the CHANGELOG placement and confirm the README subsection's enclosing section.
## Stage 80 Review — Verdict

**No Critical or Important findings.** Spec is met, the required route string matches exactly, all three new docs are present with correct boundary language, and the plan-rereview's line-wrap Important finding was correctly resolved (Test 3 now asserts the multi-command chains against `_normalized_text(section)` rather than raw text, so the wrapped prose at `docs/cli-reference.md:85-87` matches). Full `tests/test_cli_docs.py` (55 passed), ruff check, ruff format, and `git diff --check` are green.

### Spec compliance — OK
- Route `external-tool-adapters -> … -> imported-review-workflow` matches the required string verbatim in README (`:184-186`) and cli-reference (`:85-87`); the community doc (`:58-74`) presents the same route as a 5-phase table that is a consistent superset.
- Boundary language present in all three docs; no capability overclaim. No `src/`, `AGENTS.md`, `REVIEW_PROTOCOL.md`, `github-upload-checklist.md`, or manifest changes.

### Markdown split hazards — OK
- New `## External Tool Import Roadmap` (`community-signal-import.md:58`) sits far above the only `_markdown_section("## Directory Manifest")` call (`:287`), so its `\n## ` bounds are unaffected.
- README's new `### External Tool Import Path` (`:179`) is level-3, so it cannot terminate level-2 `_markdown_section` splits. cli-reference adds no heading.

### Minor (optional cleanup)

1. **README drift test is loose.** `test_readme_external_tool_import_path_points_to_local_handoff_route` asserts against whole-`text`/`normalized` rather than isolating the `### External Tool Import Path` section. At least 3 of the 8 boundary phrases ("does not prove demand / rank brands / verify platform coverage") and all listed command names **pre-exist at HEAD** elsewhere in README, so those individual assertions pass even if the new paragraph's boundary sentence were deleted. The unique anchors (heading, "user-controlled external export directory", the route chains, the link) still pin the section, so this is adequate — but for a tighter guard, split on `### External Tool Import Path` to the next heading and assert within it (as the community-doc test already does well).
2. **cli-reference test, same pattern.** Boundary phrases there are checked against whole-doc `normalized` and also pre-exist in neighboring command entries; the route-chain assertions (in `normalized_section`) are the tight part. Same optional tightening applies.
3. **CHANGELOG ordering.** The Stage 80 entry is placed *above* "Python package foundation with Typer" (`CHANGELOG.md:11`), breaking the existing foundational→feature top-down narrative. Consider appending to the end of the `### Added` list.
4. **Linear route omits steps the table shows** (`external-tool-template`, `import-signals-dir --dry-run`, `imported-signals`/`candidates`/`trends`). It's a consistent compression, not a contradiction — optional to add a one-line "see table for full phase detail" pointer if you want readers of the linear route to discover the template/dry-run steps.

### Commit-time guardrail (out of review scope, but flagging)
Working-tree `uv.lock` currently carries tuna mirror URLs (`uv.lock:16,24,…`); HEAD's lockfile is clean. This is explicitly out of stage and the plan already backs up/restores it and asserts `! git diff --cached --name-only | rg -x 'uv.lock'`. Just ensure that guard holds at `git add` time so mirror URLs don't leak into the public lockfile.

Note: `docs/reviews/opencode-stage-80-code-review.md` is the live capture of this review session (per plan Task 3 Step 2); `opencode-stage-80-plan-review.md` is a correctly-marked timeout stub deferring to `opencode-stage-80-plan-rereview.md`. Both are fine as-is.
