# Stage 327 opencode Plan Rereview

Reviewer: local opencode, `glm-5.2`

### Closure Check

All six prior Critical/Important findings are fixed:

1. Homepage copy mismatch is closed. `signals or sources` is used consistently
   where signal-index homepage copy is expected.
2. Top-level count semantics are closed. The spec and plan now state distinct
   article/source counts across entries and sum-of-per-entry paragraph counts.
3. Support-row grain is closed. The spec and plan now state at most one support
   per story per signal entry, with the first matching content section winning.
4. Section href validation is closed. The plan now uses
   `validated_row_one_detail_relative_path()` plus
   `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`.
5. Conditional homepage copy is closed. The new copy is gated on
   `saved_signal_index is not None`; the no-signal branch keeps source-only
   copy.
6. Raw string/bool paragraph-index rejection is closed. The plan adds a direct
   helper-level test using raw `object` values.

### Remaining Issues

#### Critical

None.

#### Important

None.

#### Minor

- The render test should also assert the `supporting paragraphs` metric label.
  This was fixed in the plan after rereview.

### Recommendation

Proceed with implementation? Yes.
