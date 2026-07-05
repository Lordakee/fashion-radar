# opencode Stage 300 Plan Review

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2`, variant `max`)

Artifact:
`docs/superpowers/plans/2026-07-05-stage-300-row-one-local-article-content-sections-plan.md`

Base commit: `9107e3a` (`Stage 299: add row one local article brief sections`)

Mode: read-only. No files were edited.

## Verdict

No Critical findings. No Important findings.

The plan is technically compatible with the current `RowOneLocalArticle` and
Pydantic setup. It is correctly scoped as an additive sidecar field with no
app/edition contract changes, no source/social/translation/deployment impact,
and the local-article gate preserved. RED/GREEN test coverage is strong across
builder behavior, JSON persistence, rendering, escaping, position, and backward
compatibility.

## Minor Findings

1. Task 4 Step 1 import list is slightly imprecise about `RowOneReference`.
   `tests/test_row_one_render.py` already imports it, so the implementer should
   only add `RowOneLocalArticleContentItem` and
   `RowOneLocalArticleContentSection`.
2. HTML output may contain cosmetic blank lines when optional body/paragraph/ref
   fields are empty. This is non-blocking; the implementer can build joined
   line lists during GREEN if convenient.
3. The plan's rationale for moving `RowOneReference` is mildly overstated.
   Because the module uses `from __future__ import annotations`, moving the
   class is a clarity improvement rather than a strict compatibility fix.
4. Task 6 describes generated-site proof requirements but does not inline the
   proof script. This is acceptable, but the implementer should provide a
   concrete proof command during verification.
5. Heat-delta sign rendering for `0` and negative values is untested. Optional
   coverage can be added during implementation.
6. Reference item body text such as `brand / tracked` is synthetic but
   internally consistent and non-blocking.

## Review Questions

1. The proposed `content_sections/items` model is technically compatible with
   current `RowOneLocalArticle` and Pydantic usage.
2. Moving `RowOneReference` earlier is safe and behavior-preserving, but best
   described as definition-order clarity rather than risk avoidance.
3. The deterministic builder helpers are reasonable and free of unnecessary
   dependencies.
4. Optional `entities` and `product_signals` sections are omitted correctly
   when no refs/products exist; `brand_signals` is intentionally always present
   because it always includes the source.
5. The render strategy is correctly limited to the existing `#local-article`
   block without nav/app/edition contract changes.
6. Proposed tests are strong enough; escaping assertions should be written
   explicitly line by line during implementation.
7. There are no Critical or Important plan issues blocking implementation.
