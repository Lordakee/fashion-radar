## Stage 383 Plan Review

**Review date:** 2026-07-12
**Plan:** `docs/superpowers/plans/2026-07-12-stage-383-daily-local-synthesis-brief-plan.md`
**Reviewer:** Claude Opus4.8(1M context)

---

### Critical

#### 1. Href format mismatch in Builder Rules — implementation would always return None

The plan's "Eligible articles" section requires:

> Require href to start with `articles/`, end with `.html`, not equal `articles/index.html`…

And the Render Rules helper says:

> accept only relative `articles/<safe-story-id>.html`

Both rules describe the SAME value coming from `article_hrefs_by_story_id`. But that map — produced by `_local_article_page_hrefs_by_story_id` in `render.py:458` — contains bare `{story_id}.html` values (no path prefix). This is confirmed by `_local_article_page_href` at `render.py:443`:

```python
def _local_article_page_href(story_id: str) -> str | None:
    if not safe_local_article_story_id(story_id):
        return None
    return f"{story_id}.html"   # ← bare filename, no "articles/" prefix
```

And confirmed again by every `_safe_article_page_href` helper in the three nearest-analogous builders (daily_local_article_intelligence_brief, daily_local_reading_itinerary, daily_local_saved_article_organizer), all of which explicitly reject any value with a path separator:

```python
path = PurePosixPath(href)
if (
    path.is_absolute()
    or len(path.parts) != 1     # ← rejects anything with "/"
    ...
```

If the eligibility check validates that the raw map value starts with `articles/`, it will reject every legitimately-generated href. The builder will never find two eligible articles and will always return `None`. The synthesis brief section will never render.

**Correct pattern** (matching every existing builder that takes this map):

1. Input validation: apply `_safe_article_page_href`-style logic — accept bare `{story_id}.html` with no slash, no leading `.` or `/`, no `://`, one path part only, stem passes `safe_local_article_story_id`.
2. Card href construction: prepend `articles/` → `articles/{story_id}.html`.
3. Render-time validation (in `templates.py`): validate the constructed `articles/{story_id}.html` form — this is where "starts with `articles/`" is correct.

The plan must be corrected before implementation to separate input validation from card href construction. The description of the safe href helper in Render Rules is correct for its context (render time); the Builder Rules eligibility check is wrong.

---

### Important

#### 2. Test fixture format for `test_build_daily_local_synthesis_brief_filters_unsafe_or_missing_hrefs` is inconsistent with the Critical fix

The test plan feeds these values directly into `article_hrefs_by_story_id`:

> `https://example.com`, `articles/index.html`, `../unsafe.html`, `articles/story.html?x=1`, a whitespace href, and one safe article href.

After the Critical fix (input validation accepts only bare `{story_id}.html`), both `articles/index.html` and `articles/story.html?x=1` would be rejected because `len(path.parts) != 1` — the wrong reason. The test would pass but would not cover the intended boundaries:

- The reserved-name check (`not equal to articles/index.html`) needs input `index.html` (bare), not `articles/index.html`.
- Query-string rejection needs input `story-id-abc1234567.html?x=1` (bare with query), not the `articles/`-prefixed form.
- The safe input should be a valid bare `story-id-abc1234567.html`, not `articles/story-id.html`.

After fixing the Critical, update the test fixtures to match the corrected input format, with one explicit safe bare href to confirm the positive path.

#### 3. Placement validation (plan requires this answer before implementation)

The plan explicitly requests review to challenge or confirm placement after the intelligence brief vs. after the reading itinerary. **The proposed placement is validated.**

Current homepage order (verified at `templates.py:651–654`):
```
{daily_local_article_intelligence_brief_section}
{daily_local_saved_article_organizer_section}
{daily_local_reading_itinerary_section}
```

Inserting the synthesis brief between the intelligence brief and the saved article organizer is correct. The synthesis brief is editorial interpretation that extends the intelligence brief's article-backed data — placing it immediately after means the reader encounters the cross-article judgment while the per-article intelligence is fresh, then enters the organizer and itinerary as action modules. Placing it after the reading itinerary would break the editorial-content cluster, treating it as a closing footnote after two navigation-heavy sections. No change needed.

---

### Minor

#### 4. Opening read apostrophe rule adds unreachable complexity

> Use curly apostrophe only if surrounding files already use it; otherwise use ASCII `Today's`.

The existing codebase uses ASCII apostrophes exclusively throughout `templates.py` and `text.py`. This instruction imposes a file-inspection requirement that will always resolve to the same answer. Simplify to: always use ASCII apostrophe (`Today's`).

#### 5. Thesis dead-logic clause is unreachable

> Do not use `why_it_matters` directly unless it was already chosen by the Stage 382 article synthesis builder.

Stage 382's `_thesis_candidates` (`local_article_synthesis_brief.py:117–125`) never yields `why_it_matters` — it yields only `editorial_takeaway`, `signal_context`, content title/body, and `summary`. The thesis field of `RowOneLocalArticleSynthesisBrief` therefore can never be `why_it_matters`. The conditional is dead. Either remove the clause or restate it as the unconditional "do not use `why_it_matters`."

#### 6. `article_count` definition is ambiguous with respect to deduplication order

> `article_count` is the number of eligible article-level synthesis candidates before card cap.

"Eligible" is not defined at which deduplication stage. Clarify: `article_count` = the number of candidates that pass all eligibility filters (non-None synthesis brief, safe href, non-duplicate normalized title/href/read) before the cap of 3 is applied — i.e., this is the post-dedupe, pre-cap count.

---

### Summary

| # | Severity | Area | Action required |
|---|----------|------|----------------|
| 1 | **Critical** | Builder Rules + Render Rules href validation | Rewrite eligibility check to accept bare `{story_id}.html` input; add `articles/` prefix at card construction; validate `articles/…` form only at render time |
| 2 | **Important** | Test fixture format for href filter test | Update fixtures to use bare filenames consistent with the Critical fix |
| 3 | **Important** | Placement | Validated — after intelligence brief, before saved article organizer is correct |
| 4 | Minor | Apostrophe rule | Always use ASCII apostrophe; remove file-inspection check |
| 5 | Minor | Thesis dead clause | Remove or flatten the `why_it_matters` conditional |
| 6 | Minor | `article_count` definition | Clarify as post-dedupe, pre-cap count |

**Two findings require fixes before implementation (Critical + Important #2).** Finding #3 (placement) is a validation answer, not a change. Minors 4–6 can be addressed during implementation without blocking the plan-fix cycle.
