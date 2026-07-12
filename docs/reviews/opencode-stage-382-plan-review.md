# Stage 382 Local Article Synthesis Brief — opencode Plan Review

Scope, generated-site-only boundary, href safety, escaping approach, and implementation sequencing are sound and well-precedented (the builder mirrors Stage 368/369, reuses `safe_local_article_story_id`, the existing fragment regexes at `templates.py:194-195`, and the inline-build pattern at `templates.py:883-894` that needs no `render.py` wiring). The data-model fields the plan relies on (`story.editorial_takeaway`, `story.signal_context`, `story.summary`, `story.why_it_matters`) all exist (`models.py:191-192`). No Critical scope, safety, or contract violations found. Findings below.

## Critical

None.

## Important

1. **Data-model error: brief-section key `editorial_takeaway` does not exist in memory.** The plan's `lead` rule ("Prefer `local_article.brief_sections` with keys `why_it_matters`, `editorial_takeaway`, `signal_context`…") and `thesis` rule ("Fall back to local brief section `editorial_takeaway`") reference a key that can never match. `RowOneLocalArticleBriefKey` is `Literal["what_happened", "why_it_matters", "signal_context", "watch_next"]` (`models.py:20-25`, enforced on `RowOneLocalArticleBriefSection.key` at `models.py:67`), and `_local_article_brief_sections` only ever emits those four keys (`articles.py:255-280`). `editorial_takeaway` appears only as a raw-dict key in the serialized detail JSON payload (`render.py:1809`), never on the in-memory `RowOneLocalArticle.brief_sections`. Result: those branches are dead code and the documented derivation is wrong. Fix: drop `editorial_takeaway` from all brief-section key lists and source editorial-takeover text solely via `story.editorial_takeaway` (which does exist).

2. **On-page duplication of `why_it_matters`.** `lead`'s top preferences (`brief_sections[why_it_matters]` → `story.why_it_matters`) are identical to the derivation already rendered twice on the same page by Saved Article Key Signals' "Why It Matters" group (`saved_article_key_signals.py:102-125`, rendered at `templates.py:949`) and the Local Article Intelligence Brief `opening_signal` (`local_article_intelligence_brief.py:106-135`, rendered at `templates.py:952`). The synthesis brief is inserted between the intelligence brief and the saved body, so the same `why_it_matters` sentence would appear a third time within ~one screen — directly contradicting the plan's "does not duplicate" scope claim and the stated "compact synthesis" goal. Recommend reordering `lead` to prefer text not already on the page (e.g., `story.editorial_takeaway` → `story.summary` → `signal_context` brief section) and demoting `why_it_matters` to a late fallback, or explicitly de-duplicating against the intelligence brief's opening signal. Note `article_adds` ("first content-section body / first item body / first paragraph") and `reader_move` (anchors) likewise overlap Body Organizer section rows / read-first route and Intelligence Brief routes/evidence — the plan should either differentiate these or acknowledge the reframing is intentional.

## Minor

3. **HTML skeleton / CSS selector mismatch in the plan.** The Render Rules skeleton shows bare `<article>` cards and no element for `reader_move`, but the Task 5 CSS list includes `.local-article-synthesis-brief-card` and `.local-article-synthesis-brief-route`. Reconcile so `test_row_one_css_includes_local_article_synthesis_brief_styles` asserts against classes that actually appear in the rendered DOM (add `class="local-article-synthesis-brief-card"` to the cards and a `…-route` element for `reader_move`).

4. **Href-safety helper duplication.** `_safe_local_article_synthesis_href` is specified to reuse the same two regexes as `_safe_local_article_intelligence_href` (`templates.py:17666-17676`) with an identical allow-list. Prefer reusing the existing helper (or extracting a shared private validator) to prevent future drift; a second copy of the same allow-list is a latent divergence risk.

5. **Redundant `thesis` fallback.** Even ignoring Important #1, `story.editorial_takeaway` → "brief section `editorial_takeaway`" is redundant: the serialized payload builds that body from `story.editorial_takeaway` (`render.py:1811`), so even if the key existed the two would be identical. Collapse to `story.editorial_takeaway` → `signal_context` → first content-section title/body.

6. **Builder RED-test parity gap.** Task 2's named test functions omit an explicit "returns `None` when no meaningful text can be derived" case (parity with `test_build_local_article_intelligence_brief_returns_none_without_meaningful_body`) and an explicit named "unsafe story ID returns `None`" test. The expected-behavior prose lists both; add named tests so the regression net matches the builder's documented `None` paths.

7. **Render contract-leak coverage is vague.** Task 4 folds contract/artifact leakage into the site-placement test with the phrase "app contract payloads do not contain the new section." Stage 369 carries a dedicated `test_render_row_one_site_intelligence_brief_does_not_leak_contracts_or_artifacts` (`test_row_one_render.py:5084`) that checks edition/manifest/runtime JSON. Either add an equivalent dedicated test that also covers `data/articles/*.json` cached payloads, or spell those assertions out in the placement test.

8. **Task 6 denylist placement.** Step 1 and Step 2 assign the same string set to the "contract denylist" and "artifact stems" — ensure each lands in the correct structure: the payload-content assertions near `test_workflows.py:671-672` vs. the file-existence artifact-stem tuple near `test_workflows.py:1320-1443`. The values overlap but the two checks are structurally distinct; misplacing a string silently drops coverage.

END_OF_REVIEW
