## Stage 317 Code Review Results

### Strengths

The implementation is clean and well-executed:

- **Correct reuse of existing helpers** — `_valid_local_article_paragraph_indices`, `_local_article_paragraph_anchor`, `_esc`, etc. all leveraged without modification, no duplicated logic.
- **Clean keyword-only wiring** — `article` injected as keyword-only arg into `_render_local_article_content_item`, keeping call sites unambiguous.
- **Bilingual alignment gate is consistent** — `len(paragraphs_zh) == len(paragraphs)` mirrors the identical check in `_render_local_article_reader`. Applied once per item, not per preview.
- **Blank-paragraph filtering is correct** — `rendered_indices` derived from `_local_article_rendered_paragraph_indices(article)`, excluding blank paragraphs before any preview is emitted.
- **No new JSON artifact** — `tests/test_workflows.py:363` explicitly asserts `'"saved_paragraph_previews"' not in generated_contract_payload`.
- **Anchor security** — preview `href` values built only from integer indices through `_local_article_paragraph_anchor`, `_esc` applied consistently.

---

### Issues

#### Critical — None

#### Important — None

#### Minor

**1. Missing blank line between Stage 316 and Stage 317 paragraphs in docs**

- `README.md:202–203` and `docs/row-one.md:393–394`
- The Stage 316 paragraph runs directly into `Stage 317 adds...` with no blank line. CommonMark/GFM renders adjacent lines as a single merged paragraph on any markdown-aware surface (GitHub, docs site). Doc tests still pass because `_normalized()` collapses whitespace and slicing uses sentinel phrases — but it looks wrong rendered.
- Fix: insert one blank line between the Stage 316 closing sentence and `Stage 317 adds...` in both files.

**2. No focused test for `paragraphs_zh=[]` with content sections present**

- The mismatched-length case is covered. The empty `paragraphs_zh` path falls back correctly to monolingual via the shared alignment gate, but isn't explicitly exercised with content sections and valid `paragraph_indices`.
- Low risk given coverage on reader/digest paths. Worth a follow-up test for completeness.

**3. No `@media (max-width: 760px)` override for `.local-article-content-previews`**

- The new preview grid uses `display: grid` with `gap: 8px`. Renders correctly at narrow widths as single-column without an explicit override, consistent with existing patterns. Not broken — worth noting if the responsive policy changes.

---

### Assessment

**Ready to merge: Yes, with fixes**

The only actionable change needed before commit is the two missing blank lines in `README.md` and `docs/row-one.md`. Everything else — boundary safety, contract isolation, filtering logic, anchor hygiene, test coverage — is solid. Fix the markdown separator and this is ready to commit.
