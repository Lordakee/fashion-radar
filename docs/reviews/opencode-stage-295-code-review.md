# opencode Stage 295 Code Review

GLM 5.2 max variant. Read-only review of uncommitted Stage 295 changes against
base `1c4a66008b95076f427c870a2f619362eee30b5d`. No files edited.

## Findings

**No Critical findings. No Important findings.**

### Minor / informational

**M-1. Topic-mix counts distinct topics, not raw references (informational).**
`_edition_brief_topic_mix_point` counts entries in the already-deduplicated
`briefing_topics` list per type. Two stories both naming "The Row" produce one
brand topic, so the point reads "1 brand". This is consistent with the doc
phrase "explicit topic-mix counts across brands, products, designers, and
people" and matches the new contract test fixture (one distinct name per type).
No change needed; flagging in case future copy expects reference counts.

**M-2. Topic-mix type ordering relies on dict insertion order (informational).**
`EDITION_BRIEF_TOPIC_TYPE_LABELS` emits `brand, product, designer, person`,
which matches `BRIEFING_TOPIC_TYPES` in `briefing_topics.py:5`. Deterministic
and matches all test expectations. No change needed.

## Verification Performed

- `git diff --stat` confirms the change touches only the six files in the
  prompt; `tests/test_row_one_briefing_topics.py` is new.
- `_edition_brief_payload` already receives `stories` as its first parameter
  (`render.py:577`), so threading it into `_edition_brief_summary_points`
  (`render.py:613-619`) is a local signature extension with no new data flow.
- `schemas/row-one-app.schema.json:212-218` types `summary_points` as
  `array<localizedText>` with `minItems: 1` and no `maxItems`. Appending entries
  is in-contract; `app_version` remains `row-one-app/v7` with no bump needed.
- `_story_payload` emits `heat_delta` as `story.heat_delta` typed `int | None`
  (`models.py:113`, `render.py:964`). The guard
  `isinstance(heat_delta, int) and not isinstance(heat_delta, bool) and
  heat_delta > 0` (`render.py:742`) handles the bool-subclasses-int edge case
  and the `None` case (resolves plan-review M-4).
- Empty-edition path: `_edition_brief_topic_mix_point([])` and
  `_edition_brief_heat_watch_point([])` both return `None`, so
  `test_row_one_app_payload_includes_empty_edition_brief_for_clients` keeps its
  single fallback point without modification.
- HTML escaping: new points are pure `{"zh","en"}` localized text and reuse the
  existing `_render_edition_brief_points` path, which wraps both strings with
  `_esc(...)` (`templates.py:1377-1388`). No new `href`/link attributes are
  introduced, so no link-safety surface is added.
- Re-ran focused verification:
  - `pytest tests/test_row_one_briefing_topics.py
    tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_empty_edition_brief_for_clients
    tests/test_row_one_app_contract.py::test_row_one_app_payload_edition_brief_summarizes_topic_mix_and_heat_watch
    tests/test_row_one_app_contract.py::test_row_one_app_payload_includes_edition_brief_for_clients
    tests/test_row_one_render.py::test_render_row_one_site_displays_edition_brief_topic_mix_and_heat_watch
    tests/test_row_one_docs.py::test_row_one_docs_describe_stage_295_edition_brief_content_organization
    -q` → 6 passed.
  - `ruff check src/fashion_radar/row_one/render.py
    tests/test_row_one_briefing_topics.py` → All checks passed.

## Review Questions

**Q1: Is the implementation correct and narrow for the Stage 295 plan?** Yes.
The change appends two optional localized points inside
`_edition_brief_summary_points`, derived from existing `topics` and existing
per-story `heat_delta`. No collector, matcher, ranker, scheduler, app-UI,
local-article-extraction, source-acquisition, or compliance-review behavior is
touched. Scope matches the plan exactly.

**Q2: Is keeping `row-one-app/v7` safe for this payload change?** Yes. The
schema places no upper bound on `summary_points` length and the items remain
`localizedText`. The manifest constant `row-one-app/v7` and the app-schema
`const` for `version` are unchanged and still valid. The contract tests still
validate against the schema.

**Q3: Are HTML escaping and link safety preserved?** Yes. The new points reuse
the existing summary-point renderer, which `_esc()`-wraps both locales. No new
URLs, `href`s, or link shape are introduced, so the existing link-safety checks
are unaffected.

**Q4: Are the tests sufficient, including the new direct
`briefing_topics_payload` regression coverage?** Yes. The new
`tests/test_row_one_briefing_topics.py` covers per-story dedupe,
`story_count`/`evidence_count` accumulation, positive-only heat-delta clamping
(the -3 follow-up contributes 0 to the positive sum), and ref-type mapping
(`retailer`→brand, `celebrity`→person). The new app-payload test asserts the
full bilingual topic-mix and heat-watch strings plus schema validation; the
updated strict list-equality test encodes the exact insertion order
(resolves plan-review I-1); the static-render test proves the strings reach
`index.html`; the docs test guards the Stage 295 phrases. Omission paths are
covered by the existing empty-edition and unrenderable-path-link tests, both
of which still pass without modification (M-3 from the plan review remained
optional and is not blocking).

**Q5: Are any Critical or Important issues blocking commit/push?** No. No
Critical or Important findings. The implementation is approved for commit and
push as `Stage 295: deepen row one editorial briefing`.

## Verdict

Approved. No Critical or Important findings; the two informational notes above
do not block commit.
