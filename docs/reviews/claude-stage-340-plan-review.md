Now I have everything I need. Let me deliver the review.

---

## Stage 340Plan Review

**Approved.**

The plan is technically sound, well-scoped, and correctly anchored to the pipeline. Three issues worth noting — one important, two minor.

---

### Q1 — Technical feasibility

**Yes.** The actual `text_to_local_article_paragraphs()` code (articles.py:105–124) matches exactly what the plan describes: a `for` loop over `_prepared_local_article_paragraphs(text)`, normalization via `normalize_row_one_paragraph`, an empty check, and then the character-budget accounting. The predicate drops cleanly in after line 111with no structural conflicts.

---

### Q2 — Is `text_to_local_article_paragraphs()` the right insertion point?

**Yes, and the code confirms it.** Both call sites flow through this function:
- `_story_local_article_paragraph_sets()` for extracted text (called from `_build_story_local_article`)
- `_fallback_story_summary_article()` directly (with `story.summary.en` / `story.summary.zh`)

Filtering here keeps `paragraphs`, `paragraphs_zh`, `content_sections[*].items[*].paragraph_indices`, detail anchors, and library excerpts in sync automatically, since all of them are built from the return value of this function.

---

### Q3 — Are the filter rules conservative enough?

**Mostly yes, one minor risk.** The use of `re.fullmatch` on the full-text and prefix patterns is the right conservative choice — it means `"The share price rose after demand improved"` is never caught by the `share` rule because it doesn't constitute the *entire* paragraph.

One specific risk: `LOCAL_ARTICLE_NOISE_PREFIX_RE` contains `published (?:on )?.+` and `updated (?:on )?.+` with `(?:on )?` being optional. Effectively these become `published .+` / `updated .+`. A terse valid sentence like `"Published across six collections"` or `"Updated designs launched next season"` at≤ 140 characters would be a false positive. The guard `len(compact) <= 140` restricts damage, but the risk is real. Recommend tightening to `published on .+` / `published \d.+` or requiring a date digit suffix before the wildcard.

The `by [A-Z][A-Za-z .'-]{1,80}` byline pattern is fine — bylines as standalone paragraphs are metadata, not editorial content.

---

### Q4 — Fallback, paragraph-index, and `paragraphs_zh` alignment

**Fallback: fully covered.** The existing `_build_story_local_article()` at lines 636–643 already has:

```python
if not paragraphs:
    return _fallback_story_summary_article(..., reason="no_publishable_paragraphs")
```

No new fallback state is needed. The predicate correctly sits upstream of that check.

**Alignment: correct by construction.** Content-section indices and `paragraphs_zh` are derived from the return value of `text_to_local_article_paragraphs()`, so filtering upstream keeps them naturally aligned.

**One important issue in the fallback test (Task 1 Step 4):** The plan asserts:
```python
assert article.extraction_status == "summary_fallback"
```
`extraction_status` does not appear as a field on `RowOneLocalArticle` in the current code. The model uses `body_source` and `reason` as separate fields. This assertion will raise `AttributeError` at test time. It should be:
```python
assert article.body_source == "summary_fallback"
assert article.reason == "no_publishable_paragraphs"
```
This needs to be corrected before Task 1 Step 6 is run, or the test will be permanently red for the wrong reason.

---

### Q5 — Scope discipline

**Clean.** The plan adds nothing to app/runtime/manifest schemas, writes no new JSON artifacts, and does not touch scraping, extraction engines, ranking, social connectors, scheduling, deployment, or compliance review. The documentation boundary paragraph is explicit and the workflow guard tests are thorough.

---

### Q6 — Test sufficiency

**Mostly good.** The test matrix covers boilerplate filtering, budget behavior, short valid fashion-news preservation, fallback trigger, mixed extracted text, and paragraph-index alignment. The render regression pass-through in Task 4 Step 1 rounds out the coverage.

One minor note: `_publishable_local_article_paragraph()` normalizes its input internally, but the caller (`text_to_local_article_paragraphs()`) has already normalized the paragraph at line 109 before passing it in. Double normalization is harmless if `normalize_row_one_paragraph` is idempotent, but the predicate could simply accept a pre-normalized string and skip the redundant call. Not a correctness issue, but worth a clean-up note.

---

### Summary of issues

| Severity | Issue |
|---|---|
| **Important** | Task 1 Step 4 asserts `article.extraction_status` which does not exist; replace with `article.reason == "no_publishable_paragraphs"` |
| Minor | `published .+` / `updated .+` patterns in `LOCAL_ARTICLE_NOISE_PREFIX_RE` risk matching terse valid sentences; consider tightening to require a date suffix |
| Minor | Double normalization inside `_publishable_local_article_paragraph` when called from `text_to_local_article_paragraphs()` — not a correctness issue |

---

### Recommendation

Fix the `extraction_status` assertion before running the failing-tests step in Task 1. Consider tightening the `published`/`updated` prefix patterns to require a date or numeric suffix. Everything else is solid — proceed to Task 2 implementation.
