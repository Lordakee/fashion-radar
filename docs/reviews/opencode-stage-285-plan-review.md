**Critical Issue #1 verification**: `test_row_one_app_content_cards_mirror_story_display_fields` at `tests/test_row_one_app_contract.py:527-547` uses exact dict equality (`assert card == {...}`). The plan adds `why_it_matters` and `signal_context` to `_content_card_payload` but never updates this exact-equality test → guaranteed RED.

**Critical Issue #2 verification**: The `_edition()` fixture in `tests/test_row_one_render.py:31-99` puts `<signals>` only in `headline` (line 36). The plan's `_render_detail_information_map` renders `section_title`, `source_name`, `published`, `story_type`, `tags`, `heat_delta`, `evidence_count` — **none** contain `<signals>`. The escape test's `assert "The Row &lt;signals&gt;" in map_html` cannot pass.

---

# NOT APPROVED

The plan is well-scoped and boundary-clean, but contains two critical test bugs that guarantee RED states with no documented fix path.

## Critical Findings

### C1 — Exact-equality card test will break and is not updated
**File:** `tests/test_row_one_app_contract.py:522-547` (`test_row_one_app_content_cards_mirror_story_display_fields`)

The test asserts `card == { ... }` against a literal 18-field dict. Task 2 Step 1 adds `why_it_matters` and `signal_context` to `_content_card_payload`, making the card a 20-field dict. The plan's Files list and Task 1 never mention updating this test, so Task 2 Step 5 ("Run GREEN card tests") will fail. Required fix: add a Task 1 step (or Task 2 step) extending the expected dict with `"why_it_matters": story["why_it_matters"]` and `"signal_context": story["signal_context"]`, placed after `"summary"` to match the new payload order.

### C2 — Escape test references a value the map never renders
**File:** Plan Task 3 Step 2 (`test_render_row_one_detail_information_map_escapes_story_values`)

The test asserts `"The Row &lt;signals&gt;" in map_html`, but `_render_detail_information_map` (Task 4 Step 2) renders only `section_title` ("Top Stories"/"今日重点"), `source_name` ("Vogue Business"), `published`, `story_type`, `tags`, `heat_delta`, and `evidence` count. The `<signals>` substring lives only in `headline`, which the map intentionally excludes. The assertion is unsatisfiable. Required fix: either (a) extend the `_edition()` fixture so a map-rendered field carries markup (e.g. `source_name='Vogue <signals> Business'` and assert `"Vogue &lt;signals&gt; Business"`), or (b) drop this test and instead add an escaping assertion on `_joined_tags` / `source_name` using a fixture that sets `tags=['brand<scripts>']` or similar.

## Important Findings

### I1 — Near-duplicate published-date helper
**File:** Plan Task 4 Step 1 vs `src/fashion_radar/row_one/templates.py:1567`

`_published_label` already exists and returns `zh="%Y-%m-%d"` (iso-shaped) and `en="%b %d, %Y"`. The plan adds `_story_published_date_label` returning iso for both locales — a near-duplicate whose only difference is the en locale shape. Recommend reusing `_published_label(story).zh` for the map date, or document why the en-locale iso shape is required.

### I2 — `_safe_evidence_count` duplicated across modules
**File:** Plan Task 4 Step 2 vs `src/fashion_radar/row_one/render.py:564`

`_safe_evidence_count` already lives in `render.py`. Adding a second copy in `templates.py` is acceptable (avoids importing a private symbol), but the plan should call this out as an intentional duplication rather than implying it might already exist. If sharing is desired, promote the helper to `row_one/utils.py`.

### I3 — README change has no test coverage
**File:** Plan Task 5 Step 4

The new docs test (`test_row_one_docs_describe_card_synthesis_and_detail_information_map`) only reads `ROW_ONE_DOC`, not `README`. The README addition is therefore untested. Either add README phrase assertions to the new test, or drop the README edit from scope (it is not required by the stated goal).

## Non-blocking notes
- Schema required/properties ordering after `"summary"` is consistent with `$defs.story`. ✓
- CSS variables (`--ink`, `--panel`, `--line`, `--muted`) all exist. ✓
- `_esc`, `safe_external_url`, `RowOneLink`, `LocalizedText`, `RowOneStory` are all already imported in `templates.py`. ✓
- All four Read-Order anchors (`#summary`, `#why-it-matters`, `#signal-context`, `#evidence-trail`) exist in the current detail template. ✓
- Boundary compliance (no collection/connectors/LLM/ranking/story-ID/contract-version/scheduler/cleanup changes) holds. ✓

Fix C1 and C2 before implementation; address I1–I3 as you implement.
I'll review the revised Stage 285 plan. Let me start by reading the plan and related files.
Now let me check the previous review findings and relevant source files to verify the fixes.
Both previous Criticals appear addressed. Let me verify the fixes against the actual codebase and check for new blockers.
Let me verify the existing mirror test and the `_edition` fixture to confirm C1 and C2 fixes will actually pass.
Let me verify a critical detail: whether `_content_card_payload` receives a dict that already contains `why_it_matters` and `signal_context` keys.
I've verified both previous Criticals against the actual codebase and checked for new blockers.

**APPROVED**

## Previous Criticals — both fixed

**C1 (exact dict card test): FIXED.** Task 1 Step 5 (plan:91-99) now adds `why_it_matters`/`signal_context` to the exact-equality dict in `test_row_one_app_content_cards_mirror_story_display_fields` after `summary`. Verified the current dict at `tests/test_row_one_app_contract.py:531` has `summary` immediately before `editorial_takeaway`, and Task 2 Step 1 inserts the payload fields in the same position in `_content_card_payload` (`render.py:402`), so dict order matches. The keys resolve because `_story_payload` already emits them (`render.py:436,438`).

**C2 (escape test value not rendered): FIXED.** Task 3 Step 2 (plan:214-232) now mutates `edition.stories[0].source_name = "Vogue <signals> Business"` and asserts `"Vogue &lt;signals&gt; Business"`. The map renders `source_name` twice via `_esc` (Story Context + Evidence cards, plan:294,306), so the assertion is satisfiable. The capture regex `<section class="detail-information-map"(?P<map>.*?)</section>` is safe: the map contains no nested `<section>`.

## Important findings — all addressed
- **I1**: Plan now reuses existing `_published_label` (templates.py:1567); the duplicate helper was removed.
- **I2**: `_safe_evidence_count` duplication in templates.py is now explicitly documented as intentional (plan:266-268).
- **I3**: New docs test (plan:423-442) now reads both `ROW_ONE_DOC` and `README` and asserts phrases in both.

## New blockers — none
Spot-checked: `re` already imported in test_row_one_render.py:4; CSS vars `--ink/--panel/--line/--muted` exist (templates.py:221-224); detail anchors `summary`/`why-it-matters`/`signal-context`/`evidence-trail` all present; insertion point `{article_contents}` → `<section id="summary">` confirmed (templates.py:155-156); drift parametrization tuple shape `(mutation, match)` matches existing cases; `safe_evidence_count==1` → "1 evidence link" label correct; `published.zh` → "2026-07-02".
