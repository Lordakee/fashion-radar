# Stage 366 Local Article Body Filing Cues Code Review

## Scope

Reviewed current Stage 366 changes across:

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- Stage 366 plan/spec/review artifacts

## Spec Review

Finding:

- Medium: `tests/test_workflows.py` was missing Stage 366 contract and artifact denylist entries in the centralized generated-site-only guard. The new wrapper monkeypatched `_render_local_article_body_filing_cue`, but the workflow contract assertions did not yet include `local_article_body_filing_cues`, `article_body_filing_cues`, `body_filing_cues`, `paragraph_filing_cues`, kebab-case variants, or `Body Filing Cues`.

Resolution:

- Fixed by adding Stage 366 snake-case, kebab-case, title-case, JSON, and HTML artifact denylist entries to the centralized workflow guard.

Spec-approved areas:

- Rendering is gated to `render_local_article_page_html(...)`.
- Cues are inserted inside `#local-article-body` paragraphs.
- Labels and anchors are escaped.
- Invalid `item.paragraph_indices` are filtered with the strict helper.
- Section-title fallback is present.
- Section-level `paragraph_indices` are not accessed.

## Quality Review

Findings:

- Low: `_local_article_body_filing_contexts` duplicates some traversal and filtering logic from `_local_article_paragraph_contexts`.
- Low: `_local_article_body_filing_contexts` stores `_LocalArticleParagraphContextCue.excerpt`, although the body filing cue renderer only reads `anchor` and `label`.

Resolution:

- Deferred as non-blocking cleanup. The current implementation intentionally reuses the existing cue dataclass and validation helpers to keep the Stage 366 patch narrow. A future refactor can extract a shared collector or introduce a smaller cue dataclass if this area changes again.

## Review Status

Approved after workflow guard fix and verification.
