# Claude Code Review Prompt: Stage 340 Implementation

Please review the current uncommitted Stage 340 implementation for Fashion Radar / ROW ONE.

## Objective

Stage 340 adds a deterministic Saved Article Paragraph Quality Gate for local article bodies. It filters high-confidence extraction boilerplate before saved local article paragraphs are written to existing sidecars and rendered into detail pages, the saved article library, and first-class local article pages.

## Scope Boundaries

In scope:
- `src/fashion_radar/row_one/articles.py` paragraph filtering only.
- Tests in `tests/test_row_one_articles.py`.
- Documentation and contract/artifact guards in README, `docs/row-one.md`, `tests/test_row_one_docs.py`, and `tests/test_workflows.py`.

Out of scope:
- No schema or contract version changes.
- No new JSON artifacts.
- No scraping/source collection/social connector/scheduling/deployment/ranking/LLM/compliance-review feature.

## Review Focus

1. False-positive risk in `LOCAL_ARTICLE_NOISE_FULL_RE`, `LOCAL_ARTICLE_NOISE_PREFIX_RE`, URL filtering, and code-fragment filtering.
2. Whether short valid fashion-news paragraphs remain publishable, including brands beginning with "By" and words beginning with "Photo".
3. Correct fallback behavior: low-quality-only extracted text should use existing `body_source="summary_fallback"` and `reason="no_publishable_paragraphs"`.
4. Paragraph and `paragraphs_zh` alignment after filtering.
5. Content-section `paragraph_indices` alignment after filtered preface paragraphs.
6. Documentation and workflow guards do not introduce contract drift and are not overbroad.

## Files Changed

Use `git diff` and `git diff --stat` in the repository to inspect current uncommitted changes.

## Verification Already Run

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py -q` -> 48 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q` -> 74 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "local_article_page or saved_article_library"` -> 29 passed, 171 deselected

## Expected Output

Return:
- Approved / Not approved.
- Critical findings.
- Important findings.
- Minor findings.
- Recommended fixes before commit, if any.
Base: a046dd4ce82020e1a42e3928fd3bbf889b983b1b

Diff stat:
 README.md                             |   1 +
 docs/row-one.md                       |   1 +
 src/fashion_radar/row_one/articles.py |  59 +++++++++++
 tests/test_row_one_articles.py        | 178 ++++++++++++++++++++++++++++++++++
 tests/test_row_one_docs.py            |  55 +++++++++++
 tests/test_workflows.py               |  15 +++
 6 files changed, 309 insertions(+)
