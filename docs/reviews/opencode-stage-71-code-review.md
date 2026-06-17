I'll review the Stage 71 implementation. Let me gather the relevant context.
Now let me read the full test function and examine the docs it covers to validate the assertions are sound.
Let me examine the normalization helper and verify each of the 9 covered docs actually contains the asserted phrases (this is the crux of whether the guard is valid).
The crux of this guard's validity is whether all 9 docs genuinely contain each of the 4 readiness phrases (the `_normalized_text` helper collapses whitespace/newlines). Let me independently verify rather than trust the summary, since the whole value of the guard depends on it — especially that `cli_reference` and `checklist` (which the existing `boundary_terms` loop deliberately excludes) actually contain phrases like "itself remains print-only".
I have independently verified the core claims. Here is the Stage 71 review.

---

## Stage 71 Code Review

**No Critical issues. No Important issues.** Clear to commit.

I independently re-ran the focused test (passes) and re-verified, using the test's own whitespace normalization, that all 4 readiness phrases are genuinely present in **all 9** covered docs — including `cli-reference.md` and `github-upload-checklist.md`, which the sibling `boundary_terms` loop deliberately excludes. Zero missing. So the guard pins existing wording without forcing doc edits, consistent with the "docs unchanged absent drift" goal.

### Review Questions

**1. Does the guard bound the adapter/readiness relationship without overreaching into runtime?** Yes.
- Test-only change (`tests/test_cli_docs.py:1032-1037, 1054-1055`); no runtime, CLI, or doc-output code touched.
- The four phrases map cleanly to the boundary: the preflight command name, its *optional/local/read-only* framing, adapters *remains print-only*, and the key negative *does not run readiness or perform PATH lookup*. This matches the stated goal precisely.
- Folding the assertions into the *existing* adapter-identity loop (rather than a new loop/constant) keeps the duplication surface small — an improvement over the earlier separate-test design.

**2. Are spec/plan consistent with the final implementation?** Yes.
- Spec Design block (`...-design.md:45-70`) and Plan Task 1 Steps 2-3 (`...-plan.md:45-85`) show the identical inline `readiness_preflight_terms` tuple and loop. Acceptance criteria's 5 bullets are covered by the 4 phrases (the last phrase carries "no readiness execution" + "no PATH lookup").

**3. Critical/Important blockers before commit?** None.

### Minor (non-blocking)

- **Stale plan-review artifact.** `docs/reviews/opencode-stage-71-plan-review.md` (minor #1, #2) references "six new phrases" and a module-level `EXTERNAL_TOOL_ADAPTER_READINESS_DISCOVERABILITY_DOCS` constant — neither exists in the final 4-phrase inline-tuple design. That review was written against the earlier draft. The spec/plan themselves are correct; only the *plan-review* artifact is stale. Optional: add a one-line note that it reviewed the pre-simplification design, so a future reader isn't confused.
- **Stricter on two operational docs.** The new guard asserts all 4 phrases against `cli-reference.md` and `github-upload-checklist.md`, which the `boundary_terms` loop excludes. This is intentional (the phrases are present and the release-checklist is a legitimate place to pin the relationship), but it does mean future edits to those two docs are now constrained by the readiness wording. Acceptable and consistent with the stage goal — flagged only for awareness.

### Constraint compliance
- Runtime/CLI/adapter-output unchanged: ✅
- Docs unchanged absent drift (verified, 0 missing): ✅
- No connectors/scraping/automation/APIs/scheduling/source-acquisition/demand-proof/ranking/coverage/compliance: ✅
- Pins concepts, not exact paragraphs; reuses existing loop: ✅
