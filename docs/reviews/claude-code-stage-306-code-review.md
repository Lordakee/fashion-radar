## Stage 306 Code Review

### Methodology

I read the full diff from `294730c`, all new test functions, the implementation in `articles.py`, both plan review artifacts, and the plan document. I traced the two audit risks end-to-end through both code and tests before assigning a verdict.

---

## Verdict: APPROVE

---

## Critical Issues

None.

---

## Important Issues

None.

Both Important issues raised in the plan reviews are resolved in the implementation:

**Regex compile-once** — The plan reviews (both Claude Code and OpenCode) flagged that the originally proposed `_local_article_signal_score` helper would recompile patterns once per paragraph per term. The implementation adopted the recommended fix: `_local_article_takeaway_indices` builds `patterns: list[re.Pattern[str]]` once from `_local_article_signal_terms`, then scores inline across paragraphs. `articles.py:298–300` confirms this.

**Appended context outranking real source paragraphs** — `_story_local_article_paragraph_sets` now returns `source_paragraph_count` as its third element (`articles.py:131`, `163`). `_local_article_takeaway_indices` uses it to restrict scoring to `paragraphs[:source_paragraph_count]` (`articles.py:293–295`). Both call sites (`_build_story_local_article:608`, `_fallback_story_summary_article:647`) propagate `source_paragraph_count` through `_local_article_content_sections` and on to `_local_article_takeaway_section`. The dedicated test `test_build_row_one_local_articles_takeaways_do_not_promote_appended_context` confirms that a signal-bearing `editorial_takeaway` appended to a two-paragraph real source does not cause those paragraphs to be outranked.

---

## Minor Notes

**1. `if source_paragraph_count else paragraphs` is functionally correct but not maximally explicit**

`articles.py:293–295`:
```python
scoring_paragraphs = (
    paragraphs[:source_paragraph_count] if source_paragraph_count else paragraphs
)
```
`source_paragraph_count=0` only occurs when the initial text yields no paragraphs, in which case the early-return at line `133` means `paragraphs=[]` too — so the falsy branch produces identical results to `paragraphs[:0]`. The behavior is correct. A future reader skimming the condition might wonder whether0 is intentionally excluded; `if source_paragraph_count is not None` would be more explicit. Not a bug; noting for awareness only.

**2. Defensive `if not paragraph_en.strip(): continue` in `_local_article_takeaway_section` is unreachable**

Noted in both plan reviews and carried into the implementation. `_local_article_takeaway_indices` already returns only non-empty indices, so the guard at `articles.py:382` is never reached under normal flow. Harmless and defensive; fine to keep.

**3. `"Row"` filter — condition phrasing is correct and worth keeping as-is**

The filter `len(term) < 3 or (" " not in term and len(term) < 4)` at `articles.py:276` correctly eliminates `"Ro"` (len2) and `"Row"` (single token, len 3 < 4) while passing `"Zendaya"` (single token, len 7 ≥ 4) and `"The Row"` (contains space). The audit risk test `test_build_row_one_local_articles_takeaways_ignore_front_row_short_ref` locks this behavior end-to-end: `"Row"` is dropped from terms, `"The Row"` generates `(?<![a-z0-9])the row(?![a-z0-9])` which does not match `"front row"`. Confirmed passing.

**4. Review artifacts are clean**

Both `claude-code-stage-306-plan-review.md` and `opencode-stage-306-plan-review.md` are structured professional documents with no terminal session chatter, stray shell output, or truncated content. The code review prompt file (`claude-code-stage-306-code-review-prompt.md`) correctly reflects the actual base SHA, changed files, and verification commands.

---

## Required Fixes Before Commit

None. All verification passes (74 scoped tests, 2001 full suite, ruff check, ruff format, hygiene, lock check). Both audit risks resolved. All Stage 306 requirements satisfied.

---

`REVIEW_COMPLETE`
