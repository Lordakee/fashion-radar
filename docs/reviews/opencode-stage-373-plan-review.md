# Stage 373 Plan Review Findings

opencode independently verified the revised Stage 373 plan/spec against the codebase. Claude Code's C1/C2/I1/I2/I3/M1 findings are resolved: `story` is in scope at `render_local_article_page_html`, `include_body_filing_cues=True` is local-article-page-only, both existing fragment regexes are available in `templates.py`, and the direct import pattern makes the planned monkeypatch target correct.

## Critical

None remain.

## Important

**I1: Marker collides with existing Stage 366 body filing cues on section-opening paragraphs.**

Stage 366 already renders an inline filing cue inside every cited paragraph, including the first paragraph cited by a content section. Stage 373 planned to render a block marker immediately before that same paragraph with the section title and a same-page content-section link. Without an interaction rule, the reader would see the same section name and section link twice in adjacent elements.

Recommended fix: suppress the inline Stage 366 body filing cue on paragraphs that carry a Stage 373 marker. This keeps both features' distinct value: Stage 373 provides the block section-start marker, while Stage 366 keeps per-paragraph filed/unfiled cues on non-marker paragraphs.

## Minor

**M1: Existing strict-index validator duplication is larger than the Claude review stated.**

The codebase already has multiple live copies of strict local-article paragraph index validation. The plan's alignment-comment approach is acceptable for this stage, but a future shared helper extraction would be reasonable.

**M2: Model-level tests may not independently exercise non-int rejection.**

`RowOneLocalArticleContentItem.paragraph_indices: list[int]` may coerce string values before the builder sees them. The planned invalid-index test still covers the user-visible outcome, but direct helper-level coverage would be needed to prove the defensive non-int branch.

**M3: Support fallback should scan for the first non-empty item body.**

The plan said "first item body"; for multi-item sections, this should be the first non-empty item body before falling back to saved paragraph text.

**M4: Render tests should assert the target content-section anchor exists on the page.**

The marker links upward to existing `#local-article-content-section-N` anchors rendered before `#local-article-body`. Add a test assertion so future reorderings do not silently break the same-page marker links.
