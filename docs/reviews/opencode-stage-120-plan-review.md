# Stage 120 Plan Review

## Summary

The design goal is sound and well-scoped: a forward-only docs/tests hygiene node that stops opencode review output from being committed as live-capture stubs / status-line telemetry, without rewriting historical artifacts. Scope boundaries (review-focus Q1, Q4) are correctly held. However, the plan's central RED→GREEN contract is **broken**: the exact docs text prescribed in Task 2 does not satisfy the assertions added in Task 1, so Task 2 Step 5 ("all review protocol docs tests pass") is unachievable as written.

## Critical

### C-1 — The GREEN test fails after applying the exact planned docs text

`tests/test_review_protocol_docs.py` Task 1 requires all 9 `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` to appear as substrings in **both** the `## Review Capture Hygiene` section of `docs/REVIEW_PROTOCOL.md` **and** the `## Final Review` section of `docs/github-upload-checklist.md`. The text prescribed in Task 2 Steps 3–4 does not satisfy this. Verified empirically against the planned text:

Missing from `REVIEW_PROTOCOL.md` body:
- `review capture hygiene` — `_section()` strips the heading, and the phrase never appears in the body.
- `do not commit tool status lines such as \`Wrote\`` — not contiguous; the body reads "do not commit live-capture stubs, … tool status lines such as `Wrote`".
- `one coherent review body` — absent from the planned text entirely.
- `do not duplicate approval phrases` — body has "or duplicate approval phrases".

Missing from `github-upload-checklist.md`:
- `capture the completed reviewer output` — text has "captures the completed reviewer output" (extra `s`).
- `one coherent review body` — absent.
- `do not duplicate approval phrases` — text has "or duplicate approval phrases".

This directly defeats review-focus Q2 ("fail before docs changes **and pass after the exact planned docs text is added**"). The RED step (Task 1.2) will pass for the right reason, but the GREEN step (Task 2.5) will still fail with an `assert not failures` listing the above. An implementer would be forced to either deviate from the planned doc text or weaken the test — neither of which is the documented contract.

**Fix (pick one and make both sides consistent before coding):**
- Rewrite the two planned doc sections so every phrase appears verbatim as a contiguous substring in *both* sections (including the literal words "review capture hygiene" inside the REVIEW_PROTOCOL body, "one coherent review body", "do not duplicate approval phrases", and "capture the completed reviewer output" with no trailing `s`), **or**
- Rewrite `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` to match the actual planned prose (e.g. `"captures the completed reviewer output"`, `"duplicate approval phrases"`, drop `"one coherent review body"`, and add a separate `assert` for the heading).

## Important

### I-1 — Insertion point orphans the historical-record preservation sentence

Task 2 Step 3 says to insert `## Review Capture Hygiene` in `docs/REVIEW_PROTOCOL.md` "before the historical-record preservation sentence" (`Keep existing review records in place…`, currently the tail of `## Review Record Naming`). Putting a new `## ` heading mid-section terminates `## Review Record Naming` early and strands the preservation sentence under the new hygiene heading. Insert it **after** the entire `## Review Record Naming` section (after the preservation sentence, before `## Optional Alternate Route`) instead. The existing `naming_section` test still passes either way, but doc structure should not be corrupted.

## Minor

- **m-1** — The design's "Reviewer Context" example (`docs/superpowers/specs/…design.md:16-20`) omits `rm -f "$tmp_review"` that the plan's Task 0/Task 2 command blocks include. Make the design example match the plan so the spec is copy-pasteable.
- **m-2** — No drift test guards the new `AGENTS.md` capture-hygiene bullet (Task 2 Step 1). Acceptance criteria call for it, but nothing enforces it, so it can silently regress. Consider asserting the bullet in `test_active_review_docs_document_local_opencode_gate` or the new test.

## Review-Focus Answers

1. **Addresses the recurring problem without rewriting history?** Yes. Out-of-Scope and Decision sections explicitly forbid bulk rewrite of historical artifacts; the fix is forward-only.
2. **Test fails before and passes after exact planned docs text?** **No** — see C-1. Fails before (good) but also fails after.
3. **Command examples avoid direct final-file redirection?** Yes. Task 2 Step 2 redirects to `$tmp_review`, then `cp` after inspection; the `> docs/reviews/opencode-stage-N-…` lines are removed, satisfying the two `not in protocol_text` assertions.
4. **Docs/tests-only, no runtime/dependency/`uv.lock`/CI/connector/scraping/etc.?** Yes. Files list and Out-of-Scope are clean; `git diff --exit-code -- uv.lock pyproject.toml` is in the release gate.
5. **Verification commands sufficient?** Yes — focused RED/GREEN, adjacent CLI-docs tests, ruff check/format, full release hygiene + full pytest + lockfile + mirror scan + `git diff --check`. Adequate for a docs/tests-only node.

## Final Statement

**There ARE Critical and Important blockers before implementation.** Critical C-1 (the prescribed docs text does not satisfy the prescribed test, so GREEN cannot pass) and Important I-1 (insertion point corrupts the Review Record Naming section) must be fixed in the design/plan before Task 1 begins.
