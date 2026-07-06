# Stage 311 Plan Review (opencode fallback)

Verified plan against current `templates.py` and `models.py`. All proposed
helpers, signatures, anchors, and enum keys (`takeaways`, `entities`,
`product_signals`) are feasible. `_meta_description(text, limit=160)`,
`_local_article_rendered_paragraph_indices`, `_local_article_paragraph_anchor`
(0-based to 1-based), and `_render_local_article_map(article, *, include_reader)`
all exist as the plan assumes.

## Critical

None.

## Important

**I1 - Reference chip inner markup is ambiguous and test-coupled.**
`tests/test_row_one_render.py` Task 1 Step 3 asserts
`reference_html.count(">The Row<") == 1`. This requires each chip to render the
reference name only, directly inside its element, such as
`<span class="local-article-digest-chip">The Row</span>`. The existing
`_render_local_article_content_references` uses `name (type / label)`, so an
implementer following that convention would produce
`>The Row (brand / tracked)<` and the assertion would fail. Plan/spec should
state name-only.

**I2 - Read First fallback anchor link is under-specified.**
Task 1 Step 2 asserts `href="#local-article-paragraph-1"` for a plain article
whose only data is `paragraphs`. The fallback path has no stored
`paragraph_indices`. Task 2 should state that the fallback synthesizes the first
nonblank paragraph's original index and renders its
`#local-article-paragraph-N` link.

TDD will catch both, but the plan should match test intent.

## Minor

**M1 - Map-slice updates under-enumerated.** Task 1 Step 6 gives one example
replacement, but at least four existing slices need it: current structured,
brief-only, content-only/zh-mismatch, and escaping tests. Enumerate or say all
slices bounded by `id="local-article-reader"` or `class="local-article-brief"`.

**M2 - Dedupe normalization undefined.** Spec says normalized name, type, and
label but never defines normalization. State it so trailing-whitespace edge
cases are deterministic.

**M3 - `_local_article_digest_takeaway` wiring with empty valid indices.** Task
1 Step 5 requires the takeaway body to render when all `paragraph_indices` are
invalid. Prose covers the intent; add that the helper still returns the body
tuple with an empty link list so no links are rendered without suppressing the
card.

**M4 - `3 organized sections` count wording.** Source Map uses
`len(article.content_sections)`, consistent with existing provenance
`Organized sections`; this is intentional and fine.

## Boundary Compliance

All Stage 311 boundaries hold: template-only in `templates.py`; no
model/schema/contract/route/anchor changes; no
collection/scraping/LLM/scheduling/platform APIs; reuses existing
`RowOneLocalArticle` fields and sidecars; homepage coverage index explicitly
deferred. No accidental app-payload surface is introduced, and
`local-article-digest` is asserted absent from `data/edition.json`.

## Test-Assertion Soundness

Checked the main brittle assertions:

- Truncation (`…` present, long tail absent from digest): sound.
- Invalid-index filtering (`paragraph_indices=[0, 1, 99]` with paragraph 1
  blank): sound.
- Dedupe count `== 2`: sound if I1 name-only chip rendering is clarified.
- Map ordering (`brief < digest < reader`): sound.

## Verdict

Approved for implementation after applying I1 and I2 clarifications. No
Critical findings. Important findings are plan-clarification issues, not
architecture blockers.
