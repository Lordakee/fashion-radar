## Stage 311 Code Rereview (opencode fallback)

### 1. I1 Fix Confirmation - Fixed

The previously flagged `AttributeError` risk on `item.body.zh.strip()` is
resolved in `_local_article_digest_takeaway`:

```python
item.body.zh if item.body.zh and item.body.zh.strip() else None,
```

The short-circuit `item.body.zh and ...` guarantees `.strip()` is only
evaluated when `item.body.zh` is truthy. When `zh` is `None` or whitespace-only,
the expression yields `None`, matching the `str | None` return contract. The
downstream `_render_local_article_digest_read_first` then selects the
English-only body branch via `if body_zh is not None`, so rendering remains
consistent.

The paragraph fallback branch also uses a guarded pattern:

```python
zh = aligned_zh[index] if aligned_zh and aligned_zh[index].strip() else None
```

Coverage is reinforced by
`test_render_row_one_detail_digest_keeps_takeaway_body_without_valid_links`,
which exercises a takeaway whose `paragraph_indices` are all invalid; the body
is still rendered, confirming the takeaway path is not gated on link validity.

### 2. New Critical / Important Issues - None

The fix is minimal, targeted, and behavior-preserving for the `zh=None` case
that previously risked raising. No new control flow, mutation, schema surface,
or contract surface was added. The M1 indentation alignment in the Read First
card is also consistent with the surrounding `local-article-digest-card` markup.

### 3. Verdict

No Critical or Important findings remain on the pasted diff. Trailing whitespace
and 2-card vs 4-card grid layout choices are cosmetic/non-blocking only.
