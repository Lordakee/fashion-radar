## Critical

None.

---

## Important

None.

---

## Minor

**1. CSS: `border-radius: 999px` absent from bridge chip styles**

The plan spec (Task 5Step 2) explicitly includes `border-radius: 999px` in `.saved-article-local-related-read-evidence-bridge-ref span, .saved-article-local-related-read-evidence-bridge-links a` to make bridge chips pill-shaped. The implementation at `templates.py:2724–2730` omits that property. The existing reference chip selector (`.saved-article-local-related-read-reference`) also lacks `border-radius`, so this keeps the bridge visually consistent with the rest of the card, but it diverges from the explicit plan spec and the plan's stated design intent. The CSS selector coverage test (`test_row_one_css_includes_saved_article_local_related_reads_styles`) checks only for class-name presence, so the omission is not caught by any test.

**2. No test for the symmetric candidate-paragraph-invalid case**

`test_saved_article_local_related_reads_omits_bridge_when_current_paragraph_invalid` exercises the path where the current article's paragraph index is out of range (index 9, article has 1 paragraph), confirming `evidence_bridges == ()`. The symmetric case — candidate paragraph index out of range while the current index is valid — has no dedicated test. The code at `saved_article_local_related_reads.py:483–486` handles both sides with `if current_index is None or candidate_index is None: continue`, so the logic is correct, but half the condition has no direct test coverage. Adding one test (e.g. valid current index 0, candidate `paragraph_indices=[9]` against a 1-paragraph candidate article) would complete the safety net.

**3. Redundant `$` anchor inside `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` used with `fullmatch`**

`_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE = re.compile(r"local-article-paragraph-[1-9][0-9]*$")` is used exclusively with `.fullmatch(...)`, which already anchors at both ends. The trailing `$` is a no-op. This is pre-existing and not introduced by Stage 380, and is harmless.

---

**Verification summary**

-557 tests, all passed (`UV_NO_CONFIG=1 uv --no-config run --frozen pytest`)
- Ruff lint: clean
- Ruff format: clean

**Correctness** — `_reference_entries_by_key` correctly implements the plan's first-entry-wins-with-valid-paragraph spec (`_first_valid_entry_paragraph` guard at `saved_article_local_related_reads.py:387–390`). Bridge indices are 0-based internally and rendered as 1-based via `local_article_paragraph_anchor`. Cap at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS` enforced in the loop. Cards without shared keys get `evidence_bridges=()` correctly.

**Href safety** — `_safe_saved_article_local_related_read_current_href` accepts only exact `#local-article-paragraph-N` fragments. Candidate hrefs reuse the existing `_safe_saved_article_local_related_read_href` guard. Both validated at render time; rows with either unsafe href are silently dropped, and the bridge shell is omitted when all rows drop.

**Escaping** — `_esc` applied to all user-content fields (`reference.name`, `reference.label`, all labels, hrefs via `_esc` on already-validated values).

**Generated-site-only boundary** — monkeypatch test correctly targets `_render_saved_article_local_related_read_evidence_bridge` (not the parent `_render_saved_article_local_related_reads` already covered by Stage 377). Full contract-payload denylist covers all class-name, snake_case, kebab-case, human-title, and render-copy variants.

**Docs** — README and `docs/row-one.md` paragraphs match the expected string in `test_row_one_docs_describe_stage_380_related_read_evidence_bridge_boundary` exactly. Stage 380 paragraph appears before Stage 379 paragraph in both files.

**No regressions** — existing related-read card structure, scoring, sort order, lane routing, reference chips, excluded-story behavior, and non-bridge cards unchanged.

END_OF_REVIEW
