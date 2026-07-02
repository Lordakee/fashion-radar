I've reviewed the Stage 262 design spec, implementation plan, the current ROW ONE implementation (`models.py`, `templates.py`, `render.py`, `edition.py`), all four `tests/test_row_one_*.py` files, `docs/row-one.md`, both prior Stage 262 Claude Code plan reviews, `REVIEW_PROTOCOL.md`, `AGENTS.md`, and the release hygiene / packaging scripts. Here is the review.

---

# Claude Code Stage 262 Plan Review

Reviewer: Claude Code (`--effort max`)
Stage: 262 (ROW ONE reader orientation)
Scope: Stage 262 design spec and implementation plan before coding

## Verdict

Accept with fixes.

Stage 262 is the right next increment after 260 (static site) and 261 (editorial synthesis): it closes a real reader-navigation gap in the `collect -> match -> report -> ROW ONE` presentation path. The change is genuinely presentation-only. It stays inside `templates.py`, ROW ONE tests, and `docs/row-one.md`, and computes all orientation data at HTML render time from existing `RowOneEdition` / `RowOneSection` / `RowOneStory` fields. It adds no persisted model fields, so `data/edition.json` (`edition.model_dump()` in `render.py`) keeps its exact shape. Collection, matching, ranking, scoring, story IDs, section caps, detail-path validation, `--latest-only` cleanup, and server behavior are all untouched, and nothing approaches the frozen `external-tool-*`, `community-*`, or `imported-*` surfaces. The prior plan-review fixes (direction rationale, folding source into the orientation row, orientation-helper line-length refactor, singular/undated coverage, docs insertion point) are substantially incorporated. The fixes below are required before coding — one is a test-quality regression against the plan-rereview's own required fix, and one is a protocol-gate gap on the push step.

## Critical Findings

None.

## Important Findings

1. **Task 1 nav count assertions are not scoped to the nav and one is a false positive.** Task 1 Step 2 scopes the section-title checks to `nav_html`, but asserts the four count strings against the whole page:
   ```python
   assert "1 story" in index_html
   assert "0 stories" in index_html
   assert "1 条" in index_html
   assert "0 条" in index_html
   ```
   `"1 条"` already appears in the edition summary — the fixture sets `zh="ROW ONE 今日整理了 1 条本地时尚信号。"`, and `edition.py::_edition_summary` produces the same string in the CLI path. So `assert "1 条" in index_html` passes via the summary and never validates the nav count. This re-introduces exactly the brittleness the Stage 262 plan-rereview marked as a required fix ("scope nav ... assertions to the actual `.edition-nav` fragment"). Move all four count assertions inside `nav_html` (the counts are rendered within the `<nav>`, so the existing `nav_match` capture covers them).

2. **Task 3 Step 3's "same test" reference points at a test with no `detail_html`.** Step 1 extends `test_render_row_one_site_escapes_html_and_omits_unsafe_links` (which reads both `index_html` and `detail_html`). Step 2 defines a new test that reads only `index_html`. Step 3 then says "In the same test, add" the detail back-link assertions (`'href="../index.html#top_stories"'`, `"Back to section"`, `"回到栏目"`) against `detail_html`. Taken literally against the immediately preceding step, `detail_html` is undefined. Clarify that these assertions belong in `test_render_row_one_site_escapes_html_and_omits_unsafe_links`, not the new undated/single-link test.

3. **The pre-push gate omits the packaging smoke checks that `REVIEW_PROTOCOL.md` requires before upload.** Task 6 Step 2's "full verification" runs `pytest`, `ruff check`, `ruff format --check`, `uv lock --check`, and `check_release_hygiene.py`. But the plan owns the push (`git push origin main` in Step 6), and "Before GitHub Upload" step 3 requires "lockfile, package build, installed-wheel, packaged-resource, and optional dashboard extra smoke checks." `scripts/check_package_archives.py` (build/wheel/packaged-resource) and `scripts/check_first_run_smoke.py` are both present in the repo and are not in the gate. Since this stage modifies packaged source (`templates.py`), add `scripts/check_package_archives.py` and `scripts/check_first_run_smoke.py` to the pre-push verification (or explicitly justify their omission for a presentation-only change).

## Minor Findings

- **Task 3 Step 4 needs an `index_html` binding.** The current `test_row_one_build_command_writes_non_ascii_story_detail_path` reads the homepage inline (`... in (output_dir / "index.html").read_text(...)`) and never binds `index_html`. The plan's `assert 'class="edition-nav"' in index_html` requires introducing `index_html = (output_dir / "index.html").read_text(encoding="utf-8")` first. Note this in the step.
- **Locale-sensitive English date assertion remains.** `_published_label` uses `strftime("%b %d, %Y")` and Task 3 asserts `"Jul 02, 2026"`. The plan also asserts the locale-stable `"2026-07-02"`, which is good, but `%b` depends on `LC_TIME`; under a non-C/English locale the EN assertion can fail. Acceptable for CI, but consider hardening or dropping the EN-only assertion.
- **No ordering assertion for the nav.** The acceptance criterion says the contents block renders "before story sections," but no test checks position. An optional `index_html.index('edition-nav') < index_html.index('section-block')` would lock this in.

## Required Plan/Spec Fixes Before Coding

- Move the four Task 1 count assertions (`"1 story"`, `"0 stories"`, `"1 条"`, `"0 条"`) inside `nav_html` so they actually validate the nav and stop passing via the edition summary.
- Fix Task 3 Step 3 so the detail back-link assertions are explicitly placed in `test_render_row_one_site_escapes_html_and_omits_unsafe_links`.
- Add `scripts/check_package_archives.py` and `scripts/check_first_run_smoke.py` to the Task 6 pre-push gate, or record an explicit justification for skipping them on a presentation-only change.
- Add the `index_html = ...` binding note to Task 3 Step 4.

## Optional Follow-Ups

- Add a structural test that the number of `.edition-nav-item` entries equals `len(edition.sections)` and that every nav `href="#<key>"` has a matching section `id="<key>"`, to guard against future section/nav drift.
- Keep Stage 263 as the app-facing JSON contract work (already noted in the plan) only if the user continues the ROW ONE app/site direction; otherwise return to curated source coverage or deterministic matching quality per the release-track preference.
- `git push origin main` matches this project's established single-branch convention, so no change needed — just confirming it is intentional.
