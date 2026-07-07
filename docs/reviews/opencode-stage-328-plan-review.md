# Stage 328 Plan Re-Review

## Critical

None.

All Critical findings from Claude Code's review are addressed:
- **Paragraph index defense** (`_paragraph_excerpt`): The revised implementation at plan lines 411-425 now has explicit `isinstance(index, bool) or not isinstance(index, int)` plus `index < 0 or index >= len(...)` guards before any indexing. The hostile-indices case is covered by `test_..._falls_back_to_valid_saved_paragraph_excerpt` (plan lines 176-205) using `[True, 1, "2", 0, 0, 99]`.
- **Blank body fallback**: Covered by `test_..._falls_back_from_blank_body` (plan lines 140-173), asserting paragraph fallback wins when `body="   "`, `body_zh="  "`.

## Important

None.

All Important findings are addressed:
- **None-excerpt rendering**: Direct-render case added (plan lines 493-499) asserting `"saved-signal-index-support-excerpt" not in support_row_html` when `excerpt=None`.
- **Docs ordering**: Explicit `stage_328_pos < stage_327_pos` assertion added (plan lines 629-633).
- **Workflow positive assertion**: Conditional positive check added (plan lines 515-521) verifying excerpt surface appears when a saved signal index is generated.
- **CSS variable usage**: Revised CSS (plan lines 564-571) uses `var(--ink)` per design spec.

## Medium

1. **Type annotation drift on `paragraph_indices`** (plan lines 411-414, 428-434): Both `_paragraph_excerpt` and `_support_excerpt` annotate `paragraph_indices: Iterable[int]`, but the runtime guard rejects bool/string values and the test feeds `[True, 1, "2", 0, 0, 99]`. The annotation should be `Iterable[object]` (or `Iterable[Any]`) to reflect the actual contract. Won't fail current CI (only pytest+ruff are run), but is misleading and would trip mypy/pyright if added later.

2. **Validity-check duplication**: `_paragraph_excerpt` re-implements the bool/int/range filtering that `_strict_valid_saved_signal_paragraph_indices()` already provides. Acceptable here because the excerpt path also needs "first valid index that yields non-empty text" semantics (different from the link-building path), but a short comment or shared predicate would reduce drift risk.

## Minor

1. **No explicit `item.body is None` test**: The blank-body test covers `body="   "`; the `if item.body is None: continue` branch (plan line 403) is exercised only implicitly. A one-line test variant would close the gap.

2. **No explicit negative-index test**: `99` covers high out-of-range; no test asserts a negative int is skipped. Covered by the `index < 0` guard but not directly asserted.

3. **Stage 327 wording assumption**: The docs test (plan line 632) looks up `"stage 327 adds a generated-site only row one"` to anchor the ordering check. If the existing Stage 327 note in `README.md` / `docs/row-one.md` uses different wording or hyphenation (`generated-site-only`), `str.index` will raise `ValueError` at GREEN. Implementer should verify the anchor phrase exists before relying on the test.

4. **CSS `var(--ink)` unverified**: Plan uses `var(--ink)` (plan line 568); the design asserts it is existing, but the plan does not include a sentinel test confirming `--ink` is defined in the stylesheet. Low risk given the design references it, but worth a grep check.

5. **Review output cap unchanged**: Claude Code Minor #1 (`sed -n '1,500p'`, plan lines 755, 774) was not adjusted. Non-blocking; comprehensive reviews rarely exceed 500 lines for this scope.

6. **`item.body is None` vs blank distinction**: The `_item_body_excerpt` loop treats `None` and blank-after-normalize identically (skip). This is correct, but the design's "first matching item body with nonblank text" phrasing could be read as not covering `None`. Behavior is fine; doc clarity only.

## Verdict

**Approved.** The revised plan adequately addresses every Critical and Important finding from Claude Code's plan review (paragraph index defense, blank-body fallback, None-excerpt rendering, docs ordering, workflow positive assertions, CSS variable usage). The dataclass extension is render-only and append-only, leaving positional construction intact. Contract-safety tests reject every prohibited artifact (`saved_signal_excerpt`, `signal_excerpt`, `saved-signal-excerpts.json`, `saved-signal-excerpt.html`, v8/v2 contract bumps) and assert both JSON-payload and filesystem absence.

The plan stays within all hard boundaries:
- No new page (only `articles/index.html` is modified).
- No new JSON sidecar (explicitly negated in tests).
- No app/runtime/manifest/schema contract changes (`RowOneSavedSignalIndexSupport` is a render-only dataclass; no Pydantic model touched).
- No source collection, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, or compliance behavior (excerpts derive solely from already-saved `RowOneLocalArticle` bodies/paragraphs available during `render_row_one_site()`).

Remaining findings are Medium/Minor and do not block implementation. Recommend addressing Medium #1 (type annotation) and Minor #3 (Stage 327 anchor verification) during implementation to avoid avoidable RED/GREEN churn.
