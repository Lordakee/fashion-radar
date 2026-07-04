# Stage 286 Code Review (opencode fallback, GLM-5.2 max)

**Reviewer:** opencode (Claude Code auth failed with `401 API key is disabled`)
**Verification reproduced:** ruff check ✓, ruff format ✓, json.tool on both schemas ✓, full pytest **1879 passed** (prompt stated 1876; count drifted as parallel-review fixes added tests), `uv lock --check` ✓, `git diff --check` ✓, no `uv.lock`/`pyproject.toml` drift, no leaked report/data/cookie/token artifacts.

## Critical Findings

None. Contract bump to `row-one-app/v5` is consistently applied across `render.py:29`, `schemas/row-one-app.schema.json:24`, `schemas/row-one-manifest.schema.json:30`, `cli.py:1800,1810`, `scripts/check_first_run_smoke.py:1134,1188`, README, `docs/row-one.md`, and all tests. `edition_brief` is deterministic, derived only from existing stories/sections/digest/topics/routes/evidence counts, and is correctly present for empty editions (verified by direct payload dump). All five parallel-review fixes are implemented and tested.

## Important Findings

1. **README duplication regression** — `README.md:121-122`:
   ```
   App clients can render section rails and app clients can render section rails
   and a daily briefing from `data/edition.json` without scraping HTML.
   ```
   "App clients can render section rails" is written twice — a visible copy-paste defect in the project's primary README that the Stage 286 edit introduced. It undermines the editorial polish ROW ONE aims for and is the kind of thing a reader/screens-scrape test catches immediately.
   - Smallest fix: collapse the two lines into one sentence: `App clients can render section rails and a daily briefing from \`data/edition.json\` without scraping HTML.`

## Minor Findings

1. **Duplicated path-block filter logic** — `render.py:386-421` (`_edition_brief_path_blocks` + `_read_first_digest_story_ids` + `_digest_block_cards`) and `templates.py:1366-1497` (`_render_briefing_path` + `_read_first_story_ids` + `_block_cards`) implement the exact same dedup-against-`read_first` algorithm under different helper names. Behavior is currently consistent, but the two copies can drift independently. Consider extracting a shared helper in `fashion_radar.row_one.utils` (or similar) that both modules call.

2. **Latent schema strictness gap (pre-existing)** — `schemas/row-one-app.schema.json:822-832` types `dailyDigest.lead_story_id` as `anyOf [{string minLength 1}, {null}]`, while `editionBrief.lead_story_id` (line 162) uses the strict `$defs/storyId` pattern. The renderer copies `daily_digest.lead_story_id` straight into `edition_brief.lead_story_id` (`render.py:350`), so a third-party v5 producer emitting a free-form `daily_digest.lead_story_id` would pass `dailyDigest` validation but fail `editionBrief` validation. The in-repo producer always emits valid story IDs so this is latent only; flag for a future tightening of `dailyDigest.lead_story_id` to `$ref storyId`.

3. **Untested schema rejection** — drift cases cover `metrics[0].key` mutations, `metrics` truncation, top-level `edition_brief` extra props, and `summary_points[0]` extra props, but no case asserts `edition_brief.metrics[0]` rejects an unknown property. The `editionBriefMetric.additionalProperties: false` guard exists, so this is coverage gap only, not a bug. One-line addition to the parametrized drift list.

4. **Review-prompt verification count stale** — prompt says "1876 passed"; actual is "1879 passed". Cosmetic, but if the prompt text is committed to a review artifact verbatim, the number should be updated or hedged ("~1876 passed").

## Verdict

**APPROVED with one Important fix recommended before commit:** collapse the duplicated README sentence at `README.md:121-122`. Everything else is minor/follow-up. The Stage 286 contract bump is internally consistent, the `edition_brief` payload is deterministic and empty-edition-safe, homepage rendering/placement/escaping/anchor guards are correct, the CLI and first-run smoke validators reject missing or drifted `edition_brief` values, and release hygiene is clean. The five previously-applied parallel-review fixes all verify correctly.
