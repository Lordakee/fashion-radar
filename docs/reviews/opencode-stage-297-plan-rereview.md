# opencode Stage 297 Plan Rereview

**Reviewer:** opencode (GLM 5.2 max variant)
**Subject:** Revised plan at `docs/superpowers/plans/2026-07-05-stage-297-row-one-short-local-article-context-plan.md`
**Scope:** Whether opencode C1, I1, and I2 are resolved.

## Findings

### Critical

None.

### Important

None.

All three targeted findings are resolved. Details below.

## Resolution Verification

### C1 — long-extraction assertions must match cleaning/grouping — RESOLVED

The revised `test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text` (plan lines 99-128) drops the defective `len(paragraphs) == 2` and `paragraphs[1].startswith("Second extracted paragraph")` assertions. The replacements are robust to the 3-paragraph cleaning output that `group_row_one_sentences` produces from the two sentences in the first raw paragraph:

- `sum(len(p) for p in paragraphs) >= 240` — accepts the ~338-char cleaned total.
- `any(p.startswith("First extracted paragraph") ...)` — matches cleaned paragraph 1.
- `any("Second extracted paragraph" in p ...)` — matches cleaned paragraph 3.
- `"Editorial" not in paragraphs` — correctly verifies non-enrichment. Enrichment would insert the literal paragraph `"Editorial"` (confirmed by the fallback expectation at plan lines 41-48), and since `total_chars (338) >= min(500, 240)` skips enrichment, the assertion holds.

All four assertions are now consistent with existing cleaning/grouping behavior.

### I1 — must not preserve Claude Code's character-count mistake — RESOLVED

The extracted text at plan lines 105-113 is unchanged from the original draft (341 raw chars / 338 cleaned), which already exceeds the 240-char threshold. The revision does **not** adopt Claude Code's prescribed fix ("make the extracted text genuinely substantial, totalling at least 240 characters"). Instead it fixes the assertions (C1) and the guard (I2). Claude Code's 216-char miscount is not propagated anywhere in the revised plan.

### I2 — enrichment boundary must align with "short local articles" — RESOLVED

The revised guard at plan lines 159-167 drops the `len(paragraphs) >= LOCAL_ARTICLE_MIN_CONTEXT_PARAGRAPHS` clause:

```python
if total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS):
    return paragraphs
```

This is the cleanest of the three options opencode proposed. The `LOCAL_ARTICLE_MIN_CONTEXT_PARAGRAPHS` constant is gone and no longer referenced. The Architecture prose (plan line 7) — "only when the cleaned article text is below a 240-character local-content threshold" — now matches the implemented guard exactly. A single 300-character paragraph no longer triggers enrichment, removing the boundary inconsistency.

## Verdict

APPROVED. The revised plan resolves opencode C1, I1, and I2 and introduces no new Critical or Important issues. Ready for implementation.
