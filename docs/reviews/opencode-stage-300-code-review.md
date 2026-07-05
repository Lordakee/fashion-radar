# opencode Stage 300 Code Review

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2`, variant `max`)

Artifact: uncommitted Stage 300 changes vs base `9107e3a` in
`/home/ubuntu/fashion-radar`

Changed files:

- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/articles.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`

Mode: read-only. No files were edited.

## Verdict

No Critical findings. No Important findings.

The Stage 300 change is correctly scoped as an additive, backward-compatible
sidecar field. It does not alter paragraph extraction/alignment,
app/edition/nav contracts, source extraction, social connectors, translation
services, deployment, or compliance-review behavior. Implementation is
deterministic, escaped everywhere, and well-tested. Safe to commit and push.

## Findings

### Critical

None.

### Important

None.

### Minor / Notes

1. Paragraph-index matching is consistent. `_local_article_paragraph_indices`
   normalizes search terms and matches against already-normalized saved
   paragraphs, so the substring comparison is reliable.
2. Heat-delta rendering for `0` and negatives is untested but correct by
   construction: positives get `+`, zero renders as `0`, negatives keep `-`.
3. `paragraph_indices` labels are 1-based against saved paragraph slots. This
   matches visible body order because `text_to_local_article_paragraphs` does
   not emit empty body paragraphs.
4. Test helpers `_content_section` and `_content_item` raise `StopIteration` on
   misses. This is acceptable for tests.
5. Reference item body text such as `brand / tracked` is synthetic but
   intentional and internally consistent.
6. The render implementation avoids blank-line noise by conditionally joining
   section/item parts.

## Review Questions

1. The data model is backward-compatible and correctly additive.
2. Content sections are built from existing local paragraphs and story metadata
   without changing paragraph extraction/alignment behavior.
3. Optional sections are omitted correctly. Always-present `brand_signals` is
   justified because it always contains the `Source` item.
4. Rendering stays inside the existing local article block and preserves nav,
   page, app, and edition contracts.
5. Title/body/item/reference values are escaped safely through `_esc`.
6. Tests meaningfully cover model defaults, builder behavior, sidecar JSON,
   rendering order, escaping, mismatched Chinese body behavior, and the no-body
   gate.
7. There are no Critical or Important issues blocking commit/push.

## Verification Reproduced

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q`
  -> `78 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py`
  -> `All checks passed`
- Generated-site proof confirmed:
  - 18 sidecars
  - 18 detail pages
  - every sidecar has `content_sections`
  - every sidecar has `takeaways`
  - every sidecar has `brand_signals`
  - every `takeaways` section has paragraph indices
  - every `brand_signals` section has a `Source` item
  - no empty optional sections
  - every local-article detail page includes
    `class="local-article-content-sections"`
  - `edition.json` does not contain `paragraph_indices` or
    `local-article-content-sections`
