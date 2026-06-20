I'll re-review the Stage 126 design and plan after the blocker fixes. Let me read all the relevant documents in parallel.
Now let me verify the fixes against the actual live docs and existing tests to confirm the fixes work as intended.
Let me read the affected README sections and verify the existing test helper patterns referenced.
Let me verify the quality doc and import doc sections in detail.
I need to verify the import doc section between "## Preflight Lint" and "## Boundary" contains all the expected commands.
Let me verify the existing test helpers and existing similar test referenced in the plan.
Let me check the existing similar test pattern referenced in the prior review (test_cli_docs.py:2115) and the regex pattern to confirm the fix mirrors the established convention.
Let me check the existing `_fashion_radar_commands` helper to verify the new helper mirrors its conventions, and verify the README external-tool preflight commands stay after `community-handoff-workflow`.
Let me verify the new test function name doesn't collide with existing tests, and confirm the design's "Expected Behavior" matches the plan's test tuples.
All verification complete. The new test/helper names don't collide, and `community-handoff-workflow` correctly stays as a print-only overview before the standalone directory commands in all affected docs. Now I'll write the re-review artifact.
Re-review complete. Written to `docs/reviews/opencode-stage-126-plan-rereview.md`.

## Summary

**Critical findings:** None.

**Important findings:** None. Both initial Important blockers are resolved:
- **I1 fixed** — `imported-review-workflow` removed from the README external-sample tuple (plan:117-123); design lines 84-86 reconciled to end at "import before the separate post-import review block." Verified the split terminator `Inspect retained imported rows` (README:446) cuts off before `imported-review-workflow` (README:450).
- **I2 fixed** — Architecture terminator changed to the real `## Source-Pack Quality Boundary` header (arch:348, verified present), mirroring the established pattern at test_cli_docs.py:2117.

**Minor findings:** m1 (Step 4 prose edit boundary is the full paragraph — clear from context), m2 (carried-forward subsequence-vs-full-order note, intentional).

**Does the revised plan still test the drift?** Yes — I traced all 5 cases against live docs: 4 are RED today (README external, README config, quality, architecture) and flip to GREEN after Task 2 edits; case 4 (import doc) is a regression-guard control that already passes. All split anchors, helpers, constants, test IDs, and files exist.

**Scope:** Clean — docs/test/review-only. No runtime, CLI, dependency, `uv.lock`, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit product behavior.

**Final statement: There are NO Critical or Important blockers before implementation.**
