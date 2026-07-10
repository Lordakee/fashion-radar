# Stage 380 Code Review - opencode

## Critical

None.

## Important

None.

## Minor

**1. Claude Code review Minor #1 is resolved.**

`templates.py` includes `border-radius: 999px;` in the `.saved-article-local-related-read-evidence-bridge-ref span, .saved-article-local-related-read-evidence-bridge-links a` rule. The implementation matches the plan spec.

**2. Claude Code review Minor #2 is resolved.**

`tests/test_row_one_saved_article_local_related_reads.py` includes `test_saved_article_local_related_reads_omits_bridge_when_candidate_paragraph_invalid`, covering the symmetric case where the current index is valid but the candidate paragraph index is out of range.

**3. Redundant `$` anchor in `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` is pre-existing and harmless.**

The regex is used with `.fullmatch(...)`, so the trailing `$` is redundant but not introduced by Stage 380 and has no behavior impact.

**4. `_evidence_bridges` has harmless defensive re-validation.**

`_reference_entries_by_key` already filters mapped entries to those with a valid paragraph, so the later `_first_valid_entry_paragraph(...)` calls are defensive. This keeps the call sites readable and is not a blocker.

## Verification Summary

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_local_related_reads.py tests/test_row_one_render.py tests/test_row_one_docs.py -q` -> 515 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -q` -> 43 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check ...` -> passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check ...` -> passed.

Bridge derivation is sound: current reference entries are built once and filtered for valid current paragraphs, candidate entries are filtered symmetrically, bridge labels are one-based and match `local_article_paragraph_anchor(...)`, and rows are capped by `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.

Href safety is sound: current hrefs accept only `#local-article-paragraph-N`, candidate hrefs reuse `_safe_saved_article_local_related_read_href(...)`, unsafe rows are dropped, and an empty bridge shell is omitted.

The generated-site-only boundary is preserved: the feature renders only inside existing related-read cards on `articles/<story-id>.html`; contract-payload and artifact denylist coverage was extended; no new JSON artifact, route family, schema field, app/manifest/runtime key, source collection, or scheduling behavior is introduced.

END_OF_REVIEW
