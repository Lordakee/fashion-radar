Having read all seven files, here is the re-review.

---

## Stage 382 Local Article Synthesis Brief — Re-Review (Post Card-Count Fix)

### Scope checked

Data-model correctness, required three-card output shape, duplication prevention, href-safety reuse, render/workflow/docs test boundaries, generated-site-only scope.

---

### Critical

None.

---

### Important

None.

The opencode re-review raised **R1** — that the C1 fix introduced a two-card partial-render path that is incompatible with the required-fields data contract. That finding does not match the current plan text.

The relevant plan section (Builder Rules, lines 143–149) reads verbatim:

> All three synthesis cards are required by the data contract. If `lead`, `thesis`, and `article_adds` cannot each be populated with distinct meaningful text after source/text deduplication, return `None` instead of emitting a partial, one-card, two-card, empty-card, or repeated brief.
> Do not support a partial two-card render path in Stage 382; keeping the required-field model and three-card HTML blueprint aligned is more important than rendering sparse ambiguous inputs.

Every layer of the spec is consistent with this:

- **Data contract** — all three fields (`lead`, `thesis`, `article_adds`) are non-optional on `RowOneLocalArticleSynthesisBrief`.
- **Builder** — returns `None` when fewer than three distinct cards are derivable; no intermediate partial-emit path exists.
- **Render rule** — "Omit the entire section if the builder returns `None`."
- **Acceptance criteria** — "The builder returns `None` unless `lead`, `thesis`, and `article_adds` all contain distinct meaningful text after consumed-source and normalized-text deduplication."
- **RED test** — `test_build_local_article_synthesis_brief_returns_none_when_dedup_leaves_fewer_than_three_cards` is named in Task 2.

The opencode rereview's claim that lines 146–149 permit a two-card partial render ("render the available distinct cards and keep the section") is inconsistent with those lines in the current plan. R1 does not require a fix.

All other areas are also clean: consumed-source/normalized-text deduplication is fully specified; `_render_local_article_synthesis_anchor` is required to call `_safe_local_article_intelligence_href` directly with no duplicate helper; sentinel test wiring is explicit; denylist placement separates content strings from artifact stems; docs paragraph and stale-phrase assertions mirror Stage 369 and381 precedent; no routes, JSON artifacts, schema fields, or collection/scraping/LLM/connector/scheduling behavior are introduced.

---

No remaining Critical or Important findings.

END_OF_REVIEW
