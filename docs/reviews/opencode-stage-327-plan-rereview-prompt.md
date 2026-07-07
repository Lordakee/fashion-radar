You are opencode rereviewing the Stage 327 plan fixes for
`/home/ubuntu/fashion-radar`.

Use model `glm-5.2` with maximum reasoning. Do not edit files.

Review only whether the prior Stage 327 plan-review findings were fixed.

Files:

- `docs/superpowers/specs/2026-07-07-stage-327-row-one-saved-signal-index-design.md`
- `docs/superpowers/plans/2026-07-07-stage-327-row-one-saved-signal-index-plan.md`
- `docs/reviews/opencode-stage-327-plan-review.md`

Prior findings to verify:

1. Homepage copy mismatch is fixed: English uses `signals or sources`
   consistently where signal-index copy is expected.
2. Top-level `supporting_article_count`, `source_count`, and
   `supporting_paragraph_count` semantics are explicit.
3. Support-row grain is explicit, including how same-story repeated signals are
   handled.
4. Section href validation guidance uses `validated_row_one_detail_relative_path`
   plus `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`, not
   `safe_row_one_detail_fragment_href()` with a variable fragment.
5. Homepage entry copy is conditional on `saved_signal_index is not None`; the
   no-signal branch keeps source-only copy.
6. Raw string/bool paragraph-index rejection is covered by a direct helper-level
   test.

Output exactly:

### Closure Check

### Remaining Issues

#### Critical

#### Important

#### Minor

### Recommendation

Proceed with implementation? Yes | No | With fixes

Return only the requested review body. Do not include tool logs or process
chatter.
