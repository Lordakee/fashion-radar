## Stage 382 Local Article Synthesis Brief — Re-Review (Final Card-Count Fix)

### Critical

None.

### Important

None.

---

### Verification of Focus Areas

**Data-model correctness.** `RowOneLocalArticleBriefKey` is `Literal["what_happened","why_it_matters","signal_context","watch_next"]` (`models.py:20-25`); the plan's Builder Rules (lines 134-137, 171-173) correctly limit brief-section lookups to those four keys and route all editorial-takeaway derivation through `story.editorial_takeaway` (`models.py:191`). `RowOneLocalArticleSynthesisBrief` declares `lead`/`thesis`/`article_adds` as required `LocalizedText` (lines 102-105), consistent with the three-card render blueprint.

**Required three-card output shape.** R1 is resolved via option 2: the builder returns `None` unless all three cards carry distinct meaningful text (lines 143-149); no partial two-card render path is supported; the HTML blueprint hardcodes exactly three `<article class="local-article-synthesis-brief-card">` elements (lines 233-236); the render rule omits the entire section on `None` (line 250). Task 2 adds `test_build_local_article_synthesis_brief_returns_none_when_dedup_leaves_fewer_than_three_cards` (lines 375-376) with matching expected behavior (lines 388-390). Builder output shape, renderer omission logic, and test coverage are aligned.

**Duplication prevention.** Consumed-source set and normalized consumed-text set are specified (lines 130-133). `lead` prefers `story.editorial_takeaway` → `story.summary` → `signal_context`/`what_happened`/`watch_next` brief sections → content sections → paragraphs, with `why_it_matters` demoted to last resort (lines 150-163); `thesis` guards against re-consuming `editorial_takeaway`/`summary` (lines 165, 170); `article_adds` excludes `editorial_takeaway`/`why_it_matters` entirely (lines 181-182). Acceptance criteria (lines 259-265) restate the distinct-text and `why_it_matters` dedup requirements.

**Href-safety reuse.** Task 5 Step 3 (lines 548-551) mandates `_render_local_article_synthesis_anchor` call `_safe_local_article_intelligence_href` (`templates.py:17666`) directly and forbids a duplicate `_safe_local_article_synthesis_href` or regex duplication. The existing helper validates `#`-prefix, inline whitespace, and both fragment regexes (`_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`/`_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` at `templates.py:194-195`), covering the synthesis anchors' allowed fragments.

**Render/workflow/docs test boundaries.** Task 4 render tests cover ordering (content segment deck → body organizer → intelligence brief → synthesis brief → saved body), escaping, unsafe-href filtering, CSS selector presence, generated-page-only placement, and a dedicated contract/artifact leak test covering `edition.json`/`manifest.json`/`runtime.json`/`data/articles/*.json` (lines 454-486). Task 6 separates the contract-content denylist from the artifact-stem tuple with explicit placement guidance (lines 588-625), and the sentinel test patches the renderer with `raising=True` and clarifies no extra fixture coupling is needed (lines 628-645). Task 7 docs test asserts paragraph presence, ordering (`stage_382_pos < stage_381_pos`), and a thorough stale-phrase list (lines 677-690).

**Generated-site-only scope.** Acceptance criteria (lines 268-272), the docs boundary paragraph (lines 670), forbidden artifact stems (lines 609-624), and the feature description (line 7: "creates no JSON artifact, route family, schema key, source collection behavior, scraping behavior, LLM behavior, scheduling behavior, connector behavior, or app-facing contract field") all align on the generated-site-only boundary with no collection, scraping, LLM, connector, scheduling, or compliance-review behavior.

---

No remaining Critical or Important findings across the checked focus areas.

END_OF_REVIEW
