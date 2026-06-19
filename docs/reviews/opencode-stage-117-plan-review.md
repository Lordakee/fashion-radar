I'll review the Stage 117 design and plan. Let me read all the relevant files first.
I've reviewed all the files. Let me verify a few critical details about the test assertions vs. the proposed pointer text before finalizing.
My analysis is confirmed. Here is my review.

---

# Stage 117 Plan Review Findings

## Summary

The scope, boundaries, and docs-only intent are sound. However, the plan's proposed pointer texts in Task 2 are **internally inconsistent with its own test assertions** in Task 1: the GREEN step (Task 2 Step 5) would fail for all four scoped sections. These must be reconciled before implementation. No Critical blockers; several Important ones.

## Important

### I1 — Test requires `generic_community_export` in README/first-run sections; proposed pointer texts omit it
`docs/superpowers/plans/2026-06-19-stage-117-discoverability-links-plan.md:108` asserts `"generic_community_export" in normalized` for **all four** sections in the loop. But:
- README proposed text (plan line 137-142) does not mention `generic_community_export`.
- first-run proposed text (plan line 160-166) does not mention `generic_community_export`.

`generic_community_export` only exists in `README.md:151` (adapter table), which is **outside** the test's scoped section (the section ends before `` `external-tool-adapters` is a local `` at README.md:129). It does not appear in `docs/first-run.md` at all.

**Fix:** Either add `generic_community_export` to the README and first-run pointer sentences, or scope that assertion to the CLI/checklist sections only.

### I2 — Test requires full command names in CLI section; proposed CLI text uses shorthand
`plan.md:105-106` asserts `"external-tool-readiness"` and `"external-tool-workflow"` (full command names) in the CLI section. The scoped CLI section (`cli-reference.md:220-231`) currently contains neither full name. The proposed CLI pointer text (plan line 149-153) says "readiness/workflow preflight commands" — the **shorthand**, not the full command names, so the assertion fails.

**Fix:** Use the full `` `external-tool-readiness` `` / `` `external-tool-workflow` `` names in the CLI pointer sentence.

### I3 — Test requires `docs/`-prefixed anchor in CLI section; proposed link omits `docs/`
`plan.md:112-114` asserts `"docs/community-signal-import.md#external-tool-export-directory-examples"` in the CLI section. But `docs/cli-reference.md` is a sibling of `community-signal-import.md`, so the correct relative link (and the proposed text at plan line 152) uses `community-signal-import.md#...` **without** `docs/`. The assertion cannot pass with a correct relative link.

**Fix:** Drop the `docs/` prefix in the assertion: assert `"community-signal-import.md#external-tool-export-directory-examples"`.

### I4 — Test requires `csv`, `json`, `generic_community_export` in first-run section; proposed text omits all three
`plan.md:108-110` asserts `"csv"`, `"json"`, and `"generic_community_export"` in the first-run section. The scoped first-run section (`first-run.md:94-99`) contains none of these, and the proposed first-run pointer (plan line 160-166) does not add them.

**Fix:** Extend the first-run pointer to mention CSV/JSON and the adapter id, e.g. reference the `generic_community_export` CSV/JSON readiness/workflow pairs.

### I5 — Checklist pointer text is underspecified; test still demands three specific tokens
`plan.md:168-172` (Task 2 Step 4) only says "add a sentence" without exact text, unlike Steps 1-3. The test loop still requires `external-tool-readiness`, `external-tool-workflow`, and `generic_community_export` in the checklist section (`github-upload-checklist.md:160-186`), none of which the existing section contains. The implementer must infer the exact wording.

**Fix:** Provide explicit checklist sentence text (as done for the other three docs) that includes the three required tokens.

## Minor

### M1 — Reviewer command diverges from AGENTS.md
The design (`...design.md:14-16`) and plan (`...plan.md:41`, `:210`) specify `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`, but `AGENTS.md` and `docs/github-upload-checklist.md:513-515` mandate `claude --effort max --permission-mode plan`. The user's prompt explicitly requested glm-5.2 max, so this is informational — but the project's documented review protocol says otherwise. Consider aligning one with the other.

### M2 — first-run link display/target mismatch
Proposed first-run text (plan line 164-165) uses display text `docs/community-signal-import.md#...` but link target `community-signal-import.md#...` (no `docs/`). Since `first-run.md` lives in `docs/`, the target is correct but the display prefix is misleading. Cosmetic.

### M3 — README pointer placement is ambiguous
Plan line 134 says "after the list of example paths". Within the scoped README section (`README.md:111-127`) there are two candidate insertion points (after line 118, or after the boundary text at line 127). Both are in-scope for the test; placement only affects readability.

## Review Answers

1. **Pointers vs. duplicating command blocks?** Yes — all four proposed edits are pointers; no Stage 116 command blocks are duplicated. ✓
2. **Right entry points?** Yes — README, cli-reference, first-run, and github-upload-checklist are the highest-visibility docs. ✓
3. **Tests narrow and section-scoped?** Yes — the `between()` helper scopes to relevant sections and does not re-parse Stage 116 commands. ✓ (but see I1-I5 on assertion/text mismatches)
4. **Verification commands sufficient?** Yes — Task 4 release gate covers hygiene, pytest, ruff, lockfile, mirror-URL scan, and diff checks, consistent with `github-upload-checklist.md`. ✓
5. **Critical/Important blockers?** No Critical blockers. **Five Important blockers (I1-I5)**: the proposed pointer texts do not satisfy the plan's own test assertions, so the GREEN step would fail. Reconcile Task 2 text with Task 1 assertions before implementing.
