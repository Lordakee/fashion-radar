# Stage 120 Plan Re-Review

## Summary

Both blockers from the first review are fully resolved. I traced every `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` entry through normalization + casefold against the exact Task 2 Step 3/Step 4 prose, and each phrase now resolves as a contiguous substring in **both** the `docs/REVIEW_PROTOCOL.md` `## Review Capture Hygiene` body **and** the `docs/github-upload-checklist.md` `## Final Review` body. The RED→GREEN contract is now sound.

## Critical

None.

- **C-1 (resolved).** Verified each of the 9 required phrases post-normalization in both target sections:
  - `review capture hygiene` → protocol body "This review capture hygiene rule…", checklist body "…review capture hygiene notes." ✓
  - `capture the completed reviewer output` → both bodies lead with "Capture the completed reviewer output…" (no stray `s`). ✓
  - `directly into the target review record` → present in both. ✓
  - `do not commit live-capture stubs` → present in both. ✓
  - ``do not commit tool status lines such as `Wrote` `` → present in both (backticks preserved). ✓
  - `one coherent review body` → "…only one coherent review body…" / "…copy one coherent review body…". ✓
  - `one verdict` → "…more than one verdict…". ✓
  - `do not duplicate approval phrases` → both bodies end with "…and do not duplicate approval phrases." ✓
  - `if the review times out, record the timeout honestly` → present in both. ✓
  - The `## Review Capture Hygiene` `in protocol_text` guard (test line 99) precedes the `_section` call (line 100), so RED fails cleanly with an `AssertionError` rather than an `IndexError`. ✓
  - The `> docs/reviews/opencode-stage-N-{plan,release}-review.md not in protocol_text` assertions hold because Task 2 Step 2 replaces both redirections with `cp "$tmp_review" …`. ✓
  - The AGENTS bullet assertions (5 phrases) all resolve against the Task 2 Step 1 bullet text after whitespace collapse. ✓

## Important

None.

- **I-1 (resolved).** Task 2 Step 3 now says "After the historical-record preservation sentence and before `## Optional Alternate Route`". I confirmed against `docs/REVIEW_PROTOCOL.md:71-74`: the preservation sentence ("…the active review engine changes.") stays the tail of `## Review Record Naming`, and `## Review Capture Hygiene` is inserted as a sibling before `## Optional Alternate Route`. The existing `naming_section` extraction now terminates at `\n## Review Capture Hygiene`, which still contains all six record-name entries and the preservation sentence in order — `test_active_review_protocol_documents_opencode_gate_and_claude_alternate` continues to pass.

## Minor

- **m-1 (resolved).** Design `Reviewer Context` block (`design.md:15-21`) now ends with `rm -f "$tmp_review"`, matching the plan's command blocks.
- **m-2 (resolved).** The new test asserts the five AGENTS `Review Gates` capture-hygiene phrases, so the bullet is now drift-guarded and RED triggers on its absence.
- **m-3 (new, stylistic, non-blocking).** Both new doc paragraphs read "…more than one verdict, **or duplicate approval phrases**. Do not commit tool status lines such as `Wrote`, **and do not duplicate approval phrases**." The "duplicate approval phrases" wording recurs twice within ~12 words to satisfy the `do not duplicate approval phrases` test substring. It is functionally correct but reads awkwardly in a section whose subject is avoiding duplication; a future pass could merge the two clauses once the test contract is loosened.

## Review-Focus Answers

1. **Are C-1 and I-1 fully resolved?** Yes. Both verified phrase-by-phrase and structurally against the live test helpers and current docs.
2. **Did the follow-up changes introduce any new Critical or Important blocker?** No. The additions are additive docs/test text; the existing two tests remain satisfied, and no `>`-redirection, naming, or scope boundary regressed.
3. **Is the plan internally consistent enough to start TDD implementation?** Yes. Task 1 produces a RED failure for the right reason (missing heading → missing phrases → missing AGENTS phrases), and the exact Task 2 prose makes it GREEN with no deviation required.

## Final Statement

**No Critical or Important blockers remain before implementation.** C-1 and I-1 are fully resolved, the only follow-up note (m-3) is stylistic and non-blocking, and the plan is ready to proceed to Task 1 (write failing test) → Task 2 (docs) → Task 3/Task 4 (verification and release).
