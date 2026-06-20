I'll review the Stage 126 design and plan. Let me start by reading the key documents.
Now let me examine the actual files referenced in the design to verify the drift claims and check existing test helpers.
The grep is matching many files. Let me read the actual sections of the affected docs to verify the drift claims directly.
Let me read the actual affected sections in the docs to verify the drift.
Let me verify the architecture.md command flow section and the test helpers in test_cli_docs.py.
The drift claims are confirmed. Now let me verify the remaining test anchors in the import doc, the existing order test, and the runtime workflow correctness.
I've found two potential issues. Let me verify them precisely before finalizing.
Two confirmed issues. Let me verify the test names referenced in the verification commands exist (review focus #5) and confirm the runtime test pinning.
I've completed the review. All four drift claims are confirmed against the live docs, the runtime workflow order is already correctly pinned (`test_community_handoff_workflow.py:35`), and all verification test IDs/files exist. However, I found two defects in the planned regression test.

---

## Critical findings

None.

## Important findings

**I1. The "README external community tools sample" test case is unsatisfiable — it will never reach GREEN.**

The case's expected tuple ends with `imported-review-workflow` (plan lines 118-124), but the section is captured as:
```python
readme.split("External community tools can target", 1)[1].split("Inspect retained imported rows", 1)[0]
```
That range covers README lines 406-445 — only the first bash block. `imported-review-workflow` lives at README:450, inside the *separate* block introduced by the header "Inspect retained imported rows" (README:446), which is exactly where the split cuts off. The `assert_subsequence` matcher will exhaust `actual` looking for `imported-review-workflow` and fail. Task 2 Step 1 only reorders existing commands within the first block and does not add `imported-review-workflow` there, so Task 2 Step 6 ("Expected result: pass") cannot be reached.

The design prose at lines 84-85 ("...dry-run import, import, and imported review") is internally inconsistent with both the split boundary and Step 1's edit.

Fix (either): drop `imported-review-workflow` from that one expected tuple and adjust design lines 84-85 to end at "import"; or move the split's right terminator past the imported-review block. The "README configuration directory handoff sample" tuple (correctly) omits `imported-review-workflow`, so dropping it is the consistent choice.

**I2. The architecture case references a section header that does not exist.**

The plan captures:
```python
architecture_doc.split("## Command Flow", 1)[1].split("## Local Storage Layout", 1)[0]
```
but `"## Local Storage Layout"` is absent from `docs/architecture.md` (verified — no match). The next real header after `## Command Flow` (arch:265) is `## Source-Pack Quality Boundary` (arch:348). `str.split` on a missing separator returns the whole remainder, so the case accidentally captures from `## Command Flow` to EOF. The test still passes today only because of this permissiveness, which directly contradicts the design's stated "targeted named sections" rationale (design lines 73-75, 97-100) and creates a latent false-pass risk. This does not block GREEN, but it is a real test-correctness defect.

Fix: use `"## Source-Pack Quality Boundary"` as the terminator (mirrors the existing `test_community_signal_import_doc_keeps_profile_recommended_command_order` at test_cli_docs.py:2117, which splits on real headers).

## Minor findings

**M1.** Task 2 Step 1 is slightly underspecified: it lists the 6 target local commands but doesn't explicitly state which existing lines to lift *out of* the middle of the block (the current `community-handoff-check-dir` at README:428 sits before the external-tool preflight, and `community-candidates-dir`/`community-signal-lint-dir` at README:438-440 sit after). The intent is clear, but an implementer should be told to relocate the 5 directory-local lines (lint-dir, candidates-dir ×2, check-dir) to immediately before `import-signals-dir --dry-run`, leaving all external-tool-* and single-file commands in place.

**M2.** Design "Expected Behavior" line 93 says the test "fails if any named section ... moves [check-dir] ... after import." This is accurate (check-dir precedes import-signals-dir in every expected tuple, so the matcher enforces it), but worth noting the guarantee is *subsequence*-based, not full-order — additional non-`relevant` commands between them are ignored by design. No change needed; just a clarity note for future maintainers.

## Review-focus answers

1. **Addresses drift without runtime change?** Yes. All four drifts (README external sample, README config sample, quality recommended order, architecture command flow) are real and confirmed; runtime workflow is already correct and untouched.
2. **Targeted regression test?** Approach is sound (named sections + `relevant` allow-list + subsequence matcher avoids brittle global order), but two cases have defects (I1, I2).
3. **`community-handoff-workflow` stays print-only overview; standalone `community-handoff-check-dir` after preview, before dry-run/import?** Yes — confirmed for all four docs under the planned edits.
4. **Scope clean?** Yes — docs/test/review-artifact only; no runtime, CLI, dependency, `uv.lock`, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit product behavior. Aligns with AGENTS.md scope boundaries.
5. **Verification commands sufficient?** Yes — all referenced test IDs and files exist; focused + release-gate commands match AGENTS.md mirror/uv conventions. Note: I1 must be fixed or the focused GREEN command cannot pass.

## Final statement

**There IS at least one Important blocker before implementation.** Finding **I1** will prevent Task 2 Step 6 (GREEN) from passing and must be resolved in the plan before coding begins. Finding **I2** should also be fixed so the regression test is genuinely targeted as the design claims. With I1 and I2 corrected (and optionally the M1 clarification applied), the stage is safe to implement.
