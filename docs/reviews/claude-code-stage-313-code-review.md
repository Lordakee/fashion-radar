# Claude Code Stage 313 Code Review

## Critical

No findings.

## Important

No findings.

## Minor

- **Dead-code guard in `build_row_one_saved_article_briefs`**
  (`saved_article_briefs.py:56-57`). The `if lead is None: continue` check can
  never fire: `_has_nonblank_paragraph` is verified two lines earlier, and
  `_first_paragraph_text` is guaranteed to return a `LocalizedText` whenever
  there is at least one nonblank paragraph. The guard is safe but misleading.

- **Untested: zh-only takeaway fallback** (`saved_article_briefs.py:97-99`).
  `_takeaway_text` returns `LocalizedText(zh=zh, en=zh)` when `en` is blank but
  `zh` is nonblank. The test suite does not cover this case. Not a correctness
  concern given the current data model, but worth a targeted test if zh-only
  article bodies become a real input.

- **`RowOneSavedArticleBriefs.items` is `list` in a `frozen=True` dataclass**
  (`saved_article_briefs.py:33-34`). The outer container is frozen, but the
  list itself remains mutable after construction. This is consistent with the
  established `RowOneSavedArticleCoverage` pattern, so it is not a regression.

## Verdict

Approve. All specified requirements are satisfied: the builder correctly
filters unsafe IDs, mismatched sidecars, blank articles, and invalid detail
paths; `article_count` counts all publishable articles while cards are capped at
four; the takeaway/paragraph lead priority and `paragraphs_zh` alignment logic
are correct; entity/product chips are deduped and capped via `_references`; the
template validates only `#local-article-digest` fragment hrefs, escapes every
dynamic field, emits no external URLs, and applies excerpt truncation at render
time without mutating sidecars; section ordering is correctly implemented and
test-verified; saved article coverage behavior is unaffected by the route-helper
extraction; and docs accurately describe the Stage 313 boundary with all
required negative assertions and forbidden-phrase checks passing.
