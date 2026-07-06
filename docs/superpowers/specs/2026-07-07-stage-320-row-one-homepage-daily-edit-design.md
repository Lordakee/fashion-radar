# Stage 320 ROW ONE Homepage Daily Edit Design

## Goal

Stage 320 adds a generated-site-only `Daily Edit / 今日编辑简报` section to the
ROW ONE homepage. The section turns existing ROW ONE story, digest, signal, and
optional saved-article information into a scan-first editorial briefing surface
so the homepage reads like organized fashion intelligence rather than a set of
links.

## User Value

The user wants ROW ONE to show the newest fashion information in a professional
site and to organize the information locally instead of only sending readers to
external links. Stage 319 improved individual detail pages with a Signal
Briefing panel. Stage 320 brings the same idea to the homepage: the first screen
after the top overview should explain what matters today, which signals are
warming, what to read next, and where the evidence comes from.

## Scope

Stage 320 is homepage-only and generated-site-only.

It may read existing in-memory inputs already available to the homepage
renderer:

- `RowOneEdition`
- the existing `row-one-app/v7` `app_payload`
- existing `edition_brief`
- existing `signal_synthesis`
- existing `daily_digest.briefing_topics`
- existing `daily_digest.blocks`
- existing `story_directory`
- optional existing homepage sidecar summaries already passed into
  `render_index_html()`

It must not write a new JSON artifact, add a new app payload field, or change
any public JSON contract.

## Non-Goals

Stage 320 does not:

- change `row-one-app/v7`
- change `data/edition.json`
- change `row-one-manifest/v1`
- change `data/manifest.json`
- change `row-one-runtime/v1`
- change `data/runtime.json`
- change schemas
- change story IDs
- change detail routes
- change paragraph anchors
- add source collection
- fetch article pages
- add scoring or ranking
- add social/community connectors
- call LLMs
- call image-generation tools
- add translation workflow
- prove demand or trend certainty
- add compliance-review product behavior

## Recommended Approach

Use a small homepage-only builder in `templates.py` rather than adding new
serialized data. The builder creates a private view model from existing
`app_payload` objects and renders it immediately into HTML.

This keeps the change deterministic and local:

- no app contract drift
- no schema updates
- no new files under `data/`
- no new collection/fetching responsibilities
- no dependency changes

## Homepage Placement

`Daily Edit / 今日编辑简报` should appear after the existing `edition_brief` and
`signal_synthesis` sections and before the local article / saved article blocks
and lead story. This makes it a reader-facing synthesis layer without replacing
the existing overview, signal synthesis, local intelligence, saved article
modules, or story rails.

Target order:

1. edition nav
2. edition brief
3. signal synthesis
4. daily edit
5. daily local intelligence
6. saved article modules
7. lead story
8. briefing topics/path
9. story rails

## Content Structure

The section renders up to four deterministic cards:

1. `What To Know / 今日重点`
   - Source: existing `edition_brief.summary_points` and lead story headline.
   - Purpose: summarize the strongest editorial read in one scan-first block.

2. `Signals To Watch / 值得关注`
   - Source: existing `signal_synthesis.groups[].signals[]` first usable cards,
     falling back to `daily_digest.briefing_topics`.
   - Purpose: show brand, product, designer, or person signals with count/evidence
     metadata.

3. `Read Next / 阅读路径`
   - Source: existing `daily_digest.blocks` for `key_takeaways` and
     `signals_to_watch`, excluding the read-first story when possible.
   - Purpose: give readers a deterministic local reading path.

4. `Evidence Note / 线索边界`
   - Source: existing edition/digest evidence counts and boundaries from
     `signal_synthesis`.
   - Purpose: make clear the brief is based on existing local evidence and still
     needs editorial review.

The section should omit empty cards. If no usable cards remain, omit the whole
Daily Edit section rather than rendering an empty shell.

## Link Safety

All links in the section must be internal and validated:

- detail links must pass existing detail path validation
- in-page links may target existing homepage anchors such as `#briefing-topics`,
  `#briefing-path`, or `#main-content`
- no external URLs
- no `javascript:` URLs
- invalid links render as text or fall back to `#main-content`

## Escaping

All rendered text must pass `_esc()` at render time. The section may read
strings from existing payload dictionaries, but it must not interpolate raw
payload values into HTML attributes or text nodes.

## Styling

Use ROW ONE's existing professional editorial visual language:

- paper/ink/chrome palette from `row_one_css()`
- black or line borders
- compact grid/cards
- `story-section` kicker pattern
- bilingual `data-lang` spans
- mobile collapse under the existing `@media (max-width: 760px)` block

Avoid new color systems, decorative gradients, or app-like rounded cards.

## Testing Requirements

Add render tests proving:

- Daily Edit appears on a populated generated homepage.
- It renders bilingual section title and card titles.
- It uses existing lead/summary/signal/path/evidence data.
- It is ordered after `edition-brief` and `signal-synthesis`, and before
  `lead-story`.
- It omits safely when no usable payload exists.
- It escapes hostile payload values.
- It rejects unsafe links.
- It exercises the `Signals To Watch` fallback from empty signal synthesis to
  `daily_digest.briefing_topics`.
- It exercises the `Read Next` card from `daily_digest.blocks`.
- CSS selectors exist and mobile grids collapse.

Add workflow/contract tests proving:

- generated HTML includes the Daily Edit section
- `edition.json`, `manifest.json`, and `runtime.json` contract versions remain
  unchanged
- generated contract payloads do not contain `daily_edit` or
  `daily_information_layer`
- no new top-level JSON artifact is written

Add docs tests proving:

- README and `docs/row-one.md` describe Stage 320 as generated-site-only
- docs state it reuses existing payload/sidecar data
- docs state it does not add collection, fetching, scoring, LLMs, connectors,
  schemas, or compliance-review behavior

## Risks

- Duplicating existing `edition_brief` / `signal_synthesis` content too directly.
  The section should synthesize and organize, not simply copy whole cards.
- Accidentally adding a `daily_edit` field to `data/edition.json`. Tests must
  guard against this.
- Rendering unsafe links from dictionary payloads. Use existing route validators
  and conservative fallback behavior.
- Making empty data look like confident fashion intelligence. Empty cards should
  be omitted; evidence language should remain bounded.

## Definition Of Done

- Plan review passes with no Critical or Important issues.
- New tests fail before implementation and pass after implementation.
- Focused render/workflow/docs tests pass.
- `ruff check`, `ruff format --check`, `git diff --check`, full `pytest -q`,
  `uv lock --check`, and `scripts/check_release_hygiene.py` pass.
- Claude Code code review reports no Critical or Important issues, or all such
  findings are fixed and re-reviewed.
- Changes are committed and pushed to `origin/main`.
