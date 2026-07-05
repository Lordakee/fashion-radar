# opencode Stage 297 Code Review

**Reviewer:** opencode (GLM 5.2 max variant)
**Subject:** Uncommitted Stage 297 changes vs. base `8c99c53061a0a91b03234e45bf2cf48292969bd0`
**Scope:** `src/fashion_radar/row_one/articles.py`, `tests/test_row_one_articles.py`
**Verdict:** APPROVED

## Findings

### Critical

None.

### Important

None.

### Minor

**M1. Empty-context story path is handled but not explicitly tested.**
`_story_local_article_paragraphs` short-circuits when
`_local_article_context_text(story)` returns an empty string, correctly
preserving source paragraphs unchanged. This defensive path is not exercised by
the existing fixture because `_edition()` always populates all four context
fields. A unit test with all four context fields empty would lock in the
contract. Not blocking.

**M2. Boundary cases at the threshold are not explicitly tested.**
The guard `total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS)` is
exercised well below 240 and well above 240, but the exact boundary is not
asserted. Current behavior is correct; a boundary test would guard against
future off-by-one drift. Not blocking.

**M3. Enrichment call runs even when residual budget cannot fit any useful
context paragraph.**
When `total_chars` is just under `max_chars`, the helper still calls
`text_to_local_article_paragraphs(context_text, max_chars=remaining)`, which may
return `[]` after `_useful_truncated_paragraph` rejects an unusable placeholder.
The result is correct, but the extra call is wasted work. Acceptable for a
static site builder.

## Verification Performed

Independent re-runs matched the prompt's claims:

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q` -> 69 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py` -> All checks passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py` -> 2 files already formatted
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> 1960 passed

Model inspection confirms `RowOneStory.editorial_takeaway`,
`why_it_matters`, `signal_context`, and `reader_path` are all `LocalizedText`
with required `en: str`. These four fields are already rendered on the detail
page and serialized in the app contract, so reusing them as enrichment
introduces no new schema or contract requirement.

## Review Questions

1. **Does enrichment preserve extracted source paragraphs and only add ROW ONE
   context when local content is short?** Yes. Source paragraphs are computed
   first and returned unchanged when substantial or when no context text exists;
   otherwise context is appended after accepted source paragraphs.
2. **Does clean-empty extracted text correctly fall back to stored summary?**
   Yes. When cleaning yields zero paragraphs, the helper returns `[]`, which
   routes `_build_story_local_article` to `_fallback_story_summary_article`.
   Title reverts to `story.headline`.
3. **Does the implementation respect `row_one_article.max_chars`, including low
   budgets?** Yes. Source paragraphs cap at `max_chars`; context caps at
   `max_chars - total_chars`. The unusable-tail test asserts the 38-character
   budget.
4. **Are substantial extracted articles protected from unwanted enrichment?**
   Yes. The guard returns source paragraphs unchanged once they reach 240
   characters or fill the per-source budget, whichever is smaller. The
   non-enrichment test verifies none of `Editorial`, `Important`, `Context`, or
   `Path` appears.
5. **Are tests sufficient for fallback, short extraction, empty cleaning,
   unusable tail, and non-enrichment boundaries?** Yes. All five scenarios are
   covered, and the cleaned-fallback mutation guard is preserved.
6. **Are any Critical or Important issues blocking commit/push?** No.

## Scope And Contract Check

- `RowOneLocalArticle` schema and app contract version unchanged.
- `edition.json` untouched; no new dependencies, scraping, connectors,
  platform APIs, monitoring, scheduling, or app UI changes.
- Plan matches implementation, including the `LOCAL_ARTICLE_MIN_CONTEXT_CHARS =
  240` constant and clean-empty fallback wiring.

## Verdict

APPROVED. No Critical or Important findings. The implementation is correct,
test coverage is comprehensive across the required scenarios, and verification
is reproducible. The three Minor notes are non-blocking polish opportunities.
