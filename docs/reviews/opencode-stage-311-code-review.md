# Stage 311 Code Review (opencode fallback)

Acting as fallback reviewer per `docs/REVIEW_PROTOCOL.md` after Claude Code
returned 524 timeouts. Review is based only on the pasted diff.

## Critical Findings

None.

## Important Findings

**I1. `item.body.zh.strip()` may crash if `LocalizedText.zh` is `Optional[str]`**

`src/fashion_radar/row_one/templates.py`, `_local_article_digest_takeaway`:

```python
return (
    item.body.en,
    item.body.zh if item.body.zh.strip() else None,
    ...
)
```

The guard only validates `item.body.en`. If `LocalizedText.zh` is allowed to be
`None`, `item.body.zh.strip()` raises `AttributeError`. The return type
annotation (`tuple[str, str | None, list[int]]`) suggests `None` is a meaningful
value. The supplied tests always populate `zh`, so this path is untested.
Recommend `item.body.zh if item.body.zh and item.body.zh.strip() else None` to
match the defensive style used later for `aligned_zh[index]`. If the model
guarantees `zh: str`, this can be downgraded to Minor.

## Minor Findings

**M1. Indentation inconsistency in Read First card**

`_render_local_article_digest_read_first` emits `<h4>` at one indentation level
but `<p>` and `</article>` at a different level. Cosmetic only; does not affect
rendering or tests.

**M2. Triple-nested break loop in `_render_local_article_digest_references`**

Functionally correct, but the three identical reference-cap break checks are
noisy. Could be cleaned up with a small generator plus `itertools.islice`, but
not worth blocking on.

**M3. Digest skipped entirely when no rendered paragraphs**

`_render_local_article_digest` early-returns when
`_local_article_rendered_paragraph_indices(article)` is empty. This is
intentional for a saved text digest, but means an article with `content_sections`
and no paragraphs gets no People/Products/Source Map cards. Consistent with the
stage goal; awareness only.

## Coverage Assessment

Test coverage is strong and matches the stage contract:

- Full digest rendering with read-first, people/brands, products, source map,
  and ordering assertions vs. map, reader, and brief.
- Plain saved-text article gets digest without local article map.
- Escaping, dedupe, invalid paragraph filtering, truncation, and invalid-link
  body retention are covered.
- App contract stability is covered for `row-one-app/v7`,
  `row-one-manifest/v1`, and `row-one-runtime/v1`.
- CSS selector coverage and docs boundary phrases are covered.

## Scope / Boundary Check

- No `row-one-app/v7`, `data/edition.json`, `row-one-manifest/v1`, or
  `row-one-runtime/v1` changes.
- No schema/model/sidecar/story-id/route/anchor changes; implementation only
  uses existing `RowOneLocalArticle` fields.
- Static CSS only; no JavaScript changes.
- No new collection, scraping, platform APIs, scheduling, scoring, LLM, or
  compliance-review behavior.

## Contract / Link Safety

- Digest is rendered inside existing `#local-article`, after map and before
  reader/brief/content sections/body.
- Paragraph links are validated via `_valid_local_article_paragraph_indices`
  and rendered only for existing `#local-article-paragraph-N` anchors.
- `href` values and visible text pass through `_esc`; reference chip names,
  source name, count labels, and excerpt bodies are escaped.
- Dedupe key and the `LOCAL_ARTICLE_DIGEST_MAX_REFERENCES = 4` cap are
  consistent.
- `Digest / 整理` map chip is gated on `bool(digest)`.

## Verdict

Approve with the I1 fix recommended before commit. If the model confirms
`LocalizedText.zh: str`, I1 downgrades to Minor and the diff can land as-is. The
implementation otherwise stays within the approved Stage 311 plan, passes the
documented verification commands, and preserves all stated contracts.
