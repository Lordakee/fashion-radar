# opencode Stage 293 Code Review

Scope: uncommitted changes in `src/fashion_radar/row_one/articles.py` and
`tests/test_row_one_articles.py`, plus cleanup edits to two Stage 292 review
records. Verified against `edition.py`, `collectors/article.py`,
`models/source.py`, `render.py`, `templates.py`, and the plan-review findings in
`docs/reviews/opencode-stage-293-plan-review.md`.

## Critical

None. The implementation is correct, the generated-site-only boundary is
intact, and release hygiene is clean. The review-record edits only remove
live-capture narration from Stage 292 artifacts.

## Important

**I1 - Cross-paragraph dedup scope is unpinned by any test.**
`_prepared_local_article_paragraphs` shares one `seen_sentences` set across
every `\n{2,}`-split paragraph, so dedup is whole-text, not per-paragraph. The
existing dedup test put both duplicates in a single paragraph, so a future
refactor narrowing scope to per-paragraph would pass the suite silently. Add a
test with the duplicated long sentence split across `\n\n`, plus a negative
test that a legitimately repeated short sentence survives across paragraphs.

**I2 - `<script>`/`<style>` stripping is untested.**
`_PlainTextHTMLParser` drops script/style content via `_ignored_depth`. This is
the correct defensive behavior for feed summaries that may carry inline script
after `unescape`, and it is security-relevant for generated site content. Add a
test with a `<script>`/`<style>` block in extracted text.

**I3 - Chinese boilerplate and prefix entries are untested.**
`LOCAL_ARTICLE_BOILERPLATE` includes `阅读全文。` and `点击查看全文。`, and
`LOCAL_ARTICLE_PREFIX_RE` matches `来源摘要`. The project is bilingual, so the
Chinese paths are live. Add one bilingual test pinning the Chinese prefix and
both Chinese boilerplate phrases.

## Residual Risks / Test Gaps

- `SENTENCE_RE` is simple and can split abbreviations, initials, decimals, and
  URLs into awkward pseudo-sentences. This is acceptable for the current content
  cleanup stage, but should be revisited if extracted fashion copy reads poorly.
- Boilerplate with trailing content such as `Read more: https://...` is not
  stripped because the full sentence no longer equals the standalone
  boilerplate key.
- `_extraction_buffer_chars` has coverage for the lower buffer behavior but not
  the upper `12000` cap.
- Very small `max_chars` values can drop truncated paragraphs because useful
  truncated output requires at least 24 non-ellipsis characters.

## Verdict

No Critical issues. Resolve I1-I3 before committing; they pin design decisions
the plan review explicitly asked to pin and defend a security-adjacent code
path.
