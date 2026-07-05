# opencode Stage 301 Plan Review (fallback reviewer)

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2 --variant max`).
Context: Claude Code plan review timed out (`docs/reviews/claude-code-stage-301-plan-review.md`
records `Verdict: UNAVAILABLE`). Per `docs/REVIEW_PROTOCOL.md`, opencode is the fallback
reviewer. Review is based on a direct read of the plan and the current codebase
(`src/fashion_radar/row_one/models.py`, `render.py`, `templates.py`, existing render/docs
tests, and `README.md`).

## Verdict: BLOCK

The goal, architecture, tech stack, free-first/local-first boundary, `row-one-app/v7`
isolation, generated-site cleanup compatibility, and deterministic-aggregation testability
are all sound. However, two Critical defects in the plan make its own prescribed TDD cycle
unimplementable as written: Task 2 RED tests cannot pass under the Task 3 GREEN specification.
Fix the Critical items (and the tied Important item #3) before implementation.

## Boundary Check

- No social scraping, platform APIs, browser automation, cookies/tokens, paywall bypass,
  platform monitoring, source acquisition, or compliance-review product features are added.
- `row-one-app/v7` remains stable, because the plan keeps local article intelligence outside
  `data/edition.json`.
- Generated-site cleanup remains compatible because the new artifact stays under the existing
  generated `data/` directory.

## Critical Issues

### C1. `#local-article` href rejection

`_validated_detail_relative_path` requires names ending in `.html`; a `#local-article`
fragment fails the regex, so `_safe_signal_detail_href` returns `None`.

Result: Task 4 Step 1 assertion
`assert 'href="details/the-row-signal-1234567890.html#local-article"' in html` will FAIL
(the href is dropped or rewritten to `"#"`).

The plan's only acknowledgment is a single line under the builder's "Required behavior":
"Add `#local-article` to safe detail paths." That is the wrong layer: the builder does not
validate paths. The plan must instead specify, under Task 5 (template/validation changes),
how to loosen validation safely. Recommended approach (pick one and pin it in the plan):

- Strip a trailing `#local-article` fragment in `_validated_detail_relative_path` (or a new
  `_validated_detail_relative_path_with_fragment`) before validating the path, and require
  the fragment to be exactly `local-article` (no arbitrary fragments, to avoid an open
  redirect / arbitrary-anchor sink); or
- Have the builder store `detail_path` without the fragment and add a separate
  `detail_fragment: str | None` field, letting the template compose
  `f"{detail_path}#local-article"` only when `detail_path` validates clean.

Either way, the Task 5 GREEN spec must list the validation update as an explicit step, and
the Task 4 RED test must be the one that drives it.

### C2. `brand_watch`/`product_watch` body assertion contradicts the specified body rule

Task 2 Step 3 RED test asserts:

```python
assert "Vogue Business, WWD" in brand_watch.items[0].body.en
```

The two saved articles' first paragraphs are `"The Row appears with Margaux in a saved
article."` and `"The Row appears again with Bare Sandal context."` — neither contains the
source names `Vogue Business` or `WWD`.

Task 3 Step 2 GREEN spec for aggregate bodies says only:

> "For entity/product aggregate bodies, prefer a saved takeaway or paragraph whose
> `paragraph_indices` match the reference item; otherwise use the article takeaway/first
> paragraph."

That rule yields a paragraph string with no source attribution, so the RED assertion cannot
pass under the GREEN specification. The plan never defines how multiple distinct source
names get composed into `body.en`.

Fix before implementation: add an explicit body-composition rule for aggregated items. For
example, pin one of:

- `body.en = f"{chosen_paragraph} — Sources: {', '.join(deduped_sources)}"` (and the `zh`
  counterpart), where sources are deduplicated in first-seen order; or
- `body.en = f"Sources: {', '.join(deduped_sources)} · {max_heat_delta:+d} local delta"` and
  drop the paragraph for aggregates; or
- keep the paragraph as `body` and move source attribution into a new meta line rendered by
  `_daily_local_intelligence_meta`, then change the RED assertion to target the meta line
  instead of `body.en`.

Whichever is chosen, update Task 3 Step 2 "Required behavior", the model fields (see I3),
and the Task 2 Step 3 assertion so they agree.

## Important Issues

### I1. (tied to C2) `RowOneDailyLocalIntelligenceItem.source_name` is single-valued

The proposed model has `source_name: str | None = None`. strongest_reads and heat_movers
each come from one article, so a single `source_name` is fine. But brand_watch /
product_watch aggregate across multiple stories/articles and therefore multiple sources
(test expects `article_count == 2` across `Vogue Business` and `WWD`).

Either:

- Add `source_names: list[str] = Field(default_factory=list)` and keep `source_name` as the
  primary/lead source for strongest_reads and heat_movers; or
- Document explicitly that `source_name` is a comma-joined, deduplicated, first-seen-order
  string for aggregates (and pin that exact format in Task 3).

This must be resolved together with C2 because the test pulls source names out of `body.en`,
which only works if the composition rule is defined.

### I2. "candidate-signal movement" in the heat_movers goal is not implemented

The Product Gap section says heat_movers covers "stories with positive local heat deltas or
candidate-signal movement". Task 3 Step 2 only sorts by `heat_delta desc` and the only
heat-like field on `RowOneStory` is `heat_delta: int | None`. There is no candidate-signal
movement signal in the model.

Either remove the "or candidate-signal movement" phrase from the goal (keep the
`AGENTS.md` heat-movers boundary wording: "local observed heat movement over one configured
source set"), or specify a deterministic rule such as
"include stories where `story_type == "candidate_signal"` even when `heat_delta is None`,
sorted after positive-`heat_delta` stories". Do not leave the goal overstated relative to
the implementation.

### I3. heat_movers' dependency on a saved article is not stated

The plan says the heat_movers body is "the saved local article takeaway as the body", which
implicitly requires a saved article. The empty-articles assertion
(`build_row_one_local_article_intelligence(_edition([story]), {}) == []`) implies that
heat_movers is omitted entirely when no articles exist, but this is not written anywhere in
the "Required behavior" list. Add an explicit rule:

> "heat_movers includes only stories that (a) have `heat_delta is not None and heat_delta >
> 0` (or the chosen candidate-signal rule from I2) and (b) have a saved local article with
> non-empty `paragraphs`."

Without this, an implementer could reasonably include heat-positive stories without saved
articles and produce items with empty bodies.

### I4. Task 7 Step 3 leaves the rebuild command flexible despite being documented

`README.md:706` already pins the command:

```
uv run fashion-radar row-one refresh --config-dir "$PWD/configs" --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF"
```

Replace the "inspect the current README/CLI tests" instruction with this exact command (or
the project's current canonical form) plus the four concrete post-conditions already listed.
The Self-Review's "flexible point" justification is no longer accurate.

## Minor Notes

- M1. The escape test assertion `assert "<script>" not in html` happens to pass only because
  the legitimate script tag is `<script src="assets/row-one.js">` (with attributes). It is
  brittle. Prefer `assert "<script>alert(" not in html` or assert against the escaped form
  only, matching the existing `test_render_row_one_site_escapes_html_and_omits_unsafe_links`.
- M2. The new docs test reads `Path("README.md").read_text(...)` directly. The rest of
  `tests/test_row_one_docs.py` uses the `_read(README)` + `_normalized(...)` helpers
  (see `test_row_one_docs_describe_stage_287_signal_synthesis`). Reuse those helpers for
  consistent whitespace/case folding.
- M3. The docs-test assertion `assert "row-one-app/v7" in readme` is already enforced by
  `test_row_one_docs_describe_versioned_app_json_contract` and others; it does not add
  coverage for this stage. Keep only the `daily local intelligence` and
  `data/local-intelligence.json` assertions, or make the `row-one-app/v7` check target the
  stability sentence this stage adds.
- M4. `_daily_local_intelligence_meta(item)` is listed as a helper but its output is
  unspecified. Pin the rendered fields (e.g., story count, article count, evidence count,
  heat delta) and their bilingual templates so the meta line is deterministic and testable.
- M5. The Task 5 Step 3 CSS selector list omits likely item-body / item-title / group-title
  selectors. Either add them or state explicitly that the six listed selectors are the full
  set and item content uses bare tags inside `.daily-local-intelligence-card`.
- M6. Add `scroll-margin-top` to `#local-article` (and any in-page anchor the new section
  links to) so fragment jumps clear the existing sticky header — matches existing detail-page
  anchor behavior and avoids a regression in jump-to-target UX.
- M7. The plan imports `dataclass` and `field` from `dataclasses` in the builder skeleton but
  the public API and described behavior use plain dicts/lists. Drop the unused import to keep
  ruff clean.
- M8. The model doc says references keep `type / label` metadata, which is good. Consider also
  documenting that aggregated `references` are deduplicated by `(normalized_name, type)` and
  that the first-seen `label` wins, so the `brand_watch` references list stays deterministic
  when "tracked" and "candidate" labels collide for the same normalized name.

## Required Changes Before Implementation

1. (C1) Add an explicit Task 5 step that updates `_validated_detail_relative_path` (or adds a
   fragment-aware variant) to accept exactly `#local-article`, and add a RED test in Task 4
   that fails until that validation exists.
2. (C2 + I1) Specify the aggregate body-composition rule and the `source_name` /
   `source_names` representation so Task 2 Step 3's `"Vogue Business, WWD"` assertion is
   achievable from the described builder behavior.
3. (I2) Reconcile the heat_movers goal with the implemented signal.
4. (I3) State the heat_movers saved-article requirement in "Required behavior".
5. (I4) Pin the Task 7 Step 3 rebuild command.

After these are addressed, the plan should be re-reviewed (recorded as
`docs/reviews/opencode-stage-301-plan-rereview.md`) before starting Task 2.
