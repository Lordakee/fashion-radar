Now I have sufficient context to write the full review.

---

## Stage 379 Plan Review — Saved Local Article Cross-Surface Organization Trail

### Critical

**C1 — `_companion_fixture` is undefined and will break test collection**

Task 4, Step 3 uses `_companion_fixture(story, filing_links=...)` in `test_render_local_article_page_filters_unsafe_cross_surface_organization_trail_links`. No such helper exists anywhere in `tests/test_row_one_render.py`. This is not a RED-test failure — it is a `NameError` at collection time that will abort the entire test module before any test runs. The plan must either define `_companion_fixture` as a local factory that wraps `RowOneSavedArticleLocalReadingCompanion(...)` with sensible defaults, or replace the call with an inline constructor consistent with the pattern at line 3390of `test_row_one_render.py`.

**C2 — Workflow test patches an unverified module attribute**

Task 6, Step 2 imports `from fashion_radar.row_one import render as row_one_render` and then patches `row_one_render.build_row_one_saved_article_local_reading_companion`. All existing Stage 376–378 workflow tests (lines 1595–1658of `test_workflows.py`) patch private functions inside `fashion_radar.row_one.templates`, not a `render` module. There is no evidence in the files read that `fashion_radar.row_one.render` exists as a named module or that `build_row_one_saved_article_local_reading_companion` is re-exported there. With `raising=True`, a wrong attribute name produces `AttributeError`, not a test failure, and silently breaks the sentinel. The plan must verify the attribute path by reading the render orchestration module (whichever module calls the builder inside `render_row_one_site`) before writing this patch, or follow the established pattern of patching a template-layer rendering function (e.g., stub `_render_saved_article_local_reading_companion` to strip `filing_links` from the companion before rendering).

---

### Important

**I1 — `replace` is not imported in `test_workflows.py`**

The wrapper `_without_filing_links` calls `replace(companion, filing_links=())`. `test_workflows.py` does not import `replace` from `dataclasses` (confirmed by reading its import block at lines 1–33). The plan notes "Adjust imports if the file does not already import `replace`" — but that is a conditional instruction on a fact that is already known. The plan must unconditionally add `from dataclasses import replace` to `test_workflows.py`. Without it the sentinel test will raise `NameError`.

**I2 — Card anchor derivation path in templates is implicit and untested as a unit**

The builder uses `story.id` directly (already validated by `safe_local_article_story_id(story.id)` at companion-builder entry, line 94). The template's proposed `_saved_article_library_card_anchor_id(entry)` must re-derive the story_id from `entry.digest_path`. These two derivation paths are independent code paths. The plan's full-site test (Task 4, Step 2) will catch a mismatch end-to-end, but there is no unit test that asserts `_saved_article_library_card_anchor_id` produces the same ID that the builder puts into `filing_links`. A derivation bug (e.g., stripping the wrong suffix, or accidentally accepting `reader_path` via the multi-path helper `_saved_article_library_entry_detail_path` which tries `reader_path` first) would produce silent anchor misses rather than a test failure. Add one focused unit test: given an `_entry(story_id)` fixture, assert that `_saved_article_library_card_anchor_id(entry) == f"saved-article-library-card-{story_id}"`.

**I3 — `_filing_links` helper takes `group` but group-key regex allow-list scope is ambiguous**

The plan defines `r"[a-z0-9][a-z0-9_-]{0,63}"` as the group-key allow-list and notes "permit underscores only if existing group keys require them." The only group key in the test fixtures and the real codebase is `"entities"`, which has no underscores or hyphens. The test `test_build_local_reading_companion_omits_unsafe_organization_group_trail_link` only covers `"../bad"`. Add a test for a group key with an underscore (e.g., `"top_stories"`) to confirm the regex accepts it, and a test for a key that starts with a digit or a hyphen to confirm rejection. Without these edge-case tests the regex boundary is untested.

**I4 — `_render_saved_article_local_reading_companion_current` render target placement is ambiguous**

The plan's Template Step 4 shows `{links}{filing_trail}{refs}`. Looking at `_render_saved_article_local_reading_companion_current` (lines 9183–9209), the current template emits `{links}{refs}` inside an `<article>` element. The filing trail `<div>` needs to close correctly relative to this `<article>` before the `</article>` tag. The plan does not show a full rendering skeleton with the `</article>` position, leaving the implementer to infer correct nesting. Spell out the full updated f-string or at minimum show the closing tag boundary to prevent a malformed DOM.

---

### Minor

**m1 — CSS selector redundancy**

The proposed CSS block sets `color: var(--ink)` on the combined `strong, a` rule and then immediately overrides it with `color: var(--accent)` on `a` alone. The `color: var(--ink)` on `a` is never used. The block should set `color: var(--ink)` only on `strong` and `color: var(--accent)` only on `a`.

**m2 — `aria-label` is English-only**

`<div ... aria-label="Saved article filing trail">` is a static English string. The codebase uses `data-lang` spans throughout for bilingual display, and companion section headings use `aria-labelledby` pointing to bilingual `data-lang` children. This is consistent with other `aria-label` usages in the companion that are also English-only, so it is not a regression, but the plan should acknowledge this is intentional rather than an oversight.

**m3 — Docs paragraph says "does not alter detail pages" without the URL-path form**

The codebase consistently uses inline backtick paths for page-level non-alter statements (e.g., Stage 378: "does not alter `` `index.html` ``,`` `articles/index.html` ``, or detail pages"). Using the bare phrase "does not alter detail pages" (without `` `details/<story-id>.html` ``) is technically unambiguous in this project's vocabulary but weaker than the precedent set by Stages 365–378 doc paragraphs. Use`` `details/<story-id>.html` `` for consistency.

**m4 — No backward-compatibility render test for companions without `filing_links`**

The plan adds `filing_links: tuple[...] = ()` with a default. The plan does not include a test that explicitly renders a companion without the new field (i.e., the pre-Stage-379 shape) and asserts `saved-article-local-reading-companion-filing-trail` is absent from the output. The workflow monkeypatch test (Task 6, Step 2) exercises this path indirectly, but a small direct render test in `test_row_one_render.py` would give clearer coverage at the unit level. Existing tests at line 3387 will implicitly cover this once `filing_links` is added with default `()`, but it is not explicitly called out in the plan, so a future refactor might miss it.

---

END_OF_REVIEW
