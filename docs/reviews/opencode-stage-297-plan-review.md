# opencode Stage 297 Plan Review

**Reviewer:** opencode (GLM 5.2 max variant)
**Verdict:** CHANGES REQUIRED

## Findings

### Critical

**C1. The long-extraction non-enrichment test assertions contradict the project's
own cleaning/grouping behavior, so the test will fail even after a correct
implementation.**

`test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text`
asserts `len(paragraphs) == 2` and `paragraphs[1].startswith("Second extracted
paragraph")`. I ran the proposed text through the existing
`text_to_local_article_paragraphs` helper (with `max_chars=500`). Cleaning
produces **3 paragraphs**, not 2, because `group_row_one_sentences` splits the
long first paragraph at the sentence boundary:

1. `First extracted paragraph carries enough context for the local article body.`
2. `It is intentionally longer than a tiny feed summary and exceeds the context threshold used for fallback enrichment.`
3. `Second extracted paragraph adds source detail without requiring local editorial fallback, keeping this article substantial without ROW ONE context.`

Total cleaned length is 338 chars, so the planned guard
(`len(paragraphs) >= 2 and total_chars >= min(500, 240)`) correctly skips
enrichment. But the assertions `len == 2` and `paragraphs[1].startswith("Second
extracted paragraph")` both fail. The implementer would see GREEN tests fail and
be tempted to "fix" the implementation when the implementation is correct.

Fix before implementation: either (a) rewrite the assertion to expect 3
paragraphs matching the actual cleaned output, or (b) shorten the first raw
paragraph to a single sentence so it survives cleaning intact (still totalling
≥240 chars across the two paragraphs).

### Important

**I1. Claude Code's C1 finding contains a factual error and its prescribed fix
would not address the real problem.**

Claude Code's review claims the proposed long-extraction text "totals
approximately 216 characters" and recommends "make the extracted text genuinely
substantial, totalling at least 240 characters." The actual raw length is **341
chars** (338 after cleaning). Claude Code miscounted. If the implementer follows
Claude Code's literal advice, they will lengthen text that is already long
enough and will not fix the real assertion defect described in C1 above. The
opencode revisions should explicitly decline Claude Code's C1 fix and substitute
the C1 correction above.

**I2. The planned guard enriches any article with fewer than 2 paragraphs
regardless of total length, which contradicts the plan's stated boundary of
"supplementing only short local articles."**

The guard is:

```python
if (
    len(paragraphs) >= LOCAL_ARTICLE_MIN_CONTEXT_PARAGRAPHS
    and total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS)
):
    return paragraphs
```

Because the two conditions are AND-ed, a single 300-character paragraph
(`len(paragraphs) == 1`) fails the first clause and triggers enrichment even
though it is not "short." The Product Gap section says the goal is to supplement
*short* sidecars; the implementation also supplements *single-paragraph*
sidecars. Either:

- change the boundary description in the plan to read "supplement short or
  single-paragraph local articles," or
- change the guard to `total_chars >= min(max_chars, 240)` alone (drop the
  paragraph-count clause), or
- change to OR logic if both conditions independently indicate "substantial."

Pick one explicitly before implementation; the current AND guard plus the
"short only" language is internally inconsistent. The Stage 296 sidecar census
(8 of 18 sidecars with one short paragraph) suggests paragraph count is the
practical signal, so dropping `len(paragraphs) >= 2` is probably the cleanest
fix and would also make C1's two-paragraph expectation easier to satisfy.

### Notes (not blocking)

**N1. RED test coverage is acceptable but incomplete.** The four RED tests
cover fallback enrichment, fallback-with-cleaning enrichment, short-extraction
enrichment, and substantial-extraction non-enrichment. They do not cover: an
empty `_local_article_context_text` (all four story fields blank), the exact
threshold boundary, or a `max_chars` smaller than the enrichment budget (the
plan handles this implicitly via the `max_chars` cap inside
`text_to_local_article_paragraphs`, which I verified preserves existing
small-budget test outputs). Acceptable for stage work; the implementer should be
aware.

**N2. The constant `LOCAL_ARTICLE_MIN_CONTEXT_CHARS = 240` is introduced
without justification.** It is a reasonable default above the "some under 60
characters" sidecar census from Stage 296, but a one-line rationale in the plan
(or a comment in the module) would help future maintainers.

## Answers To Review Questions

1. **Is supplementing only short local articles with existing story context a
   correct boundary?** Directionally yes, and the scope is consistent with
   AGENTS.md (no new collection, no app-contract change, no compliance-review
   feature). But see I2 — the implemented boundary also covers
   single-paragraph articles of any length, which the plan's prose does not
   disclose. Reconcile before implementation.

2. **Is it acceptable to keep `edition.json` unchanged and write only local
   article sidecars/HTML?** Yes. `edition.json` is the app contract; the
   sidecars are derived render artifacts. Localizing the change to
   `data/articles/*.json` plus rendered HTML is the right boundary and matches
   the existing render contract verified in
   `tests/test_row_one_render.py:416-420`.

3. **Are the RED tests sufficient?** Almost. The four RED tests cover the main
   positive and negative paths, but C1 must be corrected first or the GREEN
   phase will report false failures. After fixing C1, the RED suite is
   sufficient to drive implementation; N1's missing edge cases are optional.

4. **Are there any Critical or Important issues before implementation?** Yes.
   C1 (defective long-extraction assertion) is Critical and must be fixed
   before the RED phase is trustworthy. I1 (Claude Code miscount) and I2
   (boundary-vs-guard inconsistency) are Important and should be resolved
   before implementation.

## Note On Claude Code's Review

Claude Code's verdict (CHANGES REQUIRED) is correct, but its specific finding
C1 is based on a character miscount. The opencode revisions to the plan should:

- Reject Claude Code's literal fix ("make the extracted text genuinely
  substantial, totalling at least 240 characters") because the text is already
  341 chars.
- Adopt the C1 correction above (fix the assertion count to match cleaning
  output, or use single-sentence raw paragraphs).
- Address I2 by aligning the boundary prose with the implemented guard.
