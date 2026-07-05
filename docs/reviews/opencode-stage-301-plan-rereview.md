# opencode Stage 301 Plan Rereview (fallback reviewer)

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2 --variant max`).
Context: This is the rereview of the Stage 301 plan after the first fallback review
(`docs/reviews/opencode-stage-301-plan-review.md`) returned `Verdict: BLOCK`.
Claude Code's plan review remains unavailable
(`docs/reviews/claude-code-stage-301-plan-review.md` records `Verdict: UNAVAILABLE`),
so opencode is the fallback reviewer per `docs/REVIEW_PROTOCOL.md`. The rereview
focuses on whether the previous BLOCK findings (C1, C2, I1, I2, I3, I4) are resolved
and whether the plan edits introduced any new Critical or Important issues.

Reviewed artifacts:
- Plan: `docs/superpowers/plans/2026-07-05-stage-301-row-one-daily-local-intelligence-plan.md`
- Prior review: `docs/reviews/opencode-stage-301-plan-review.md`
- Codebase cross-check: `src/fashion_radar/row_one/templates.py` (validation helpers,
  `render_index_html`, `{signal_synthesis}` insertion point), `README.md:706`
  (canonical `row-one refresh` command).

## Verdict: APPROVE_WITH_NOTES

All five required changes from the prior review's "Required Changes Before
Implementation" list are addressed in the plan text. The TDD cycle prescribed by the
plan is now internally consistent: every Task 2 RED assertion is achievable under the
Task 3 GREEN specification, and every Task 4 RED assertion is achievable under the
Task 5 GREEN specification. No new Critical or Important issues were introduced by the
edits. The remaining notes are minor, inferable from the tests, and self-correcting
through the prescribed TDD cycle. The plan may proceed to Task 2.

## Resolution Check For Previous BLOCK Findings

### C1. `#local-article` fragment handling — RESOLVED

Prior finding: the only mention of `#local-article` was under the builder's "Required
behavior" (the wrong layer), so the Task 4 RED assertion
`href="details/...#local-article"` would fail because
`_validated_detail_relative_path` (templates.py:2553) rejects fragments.

Plan edit resolution: Task 5 Step 2 now explicitly specifies a dedicated validation
helper:

> Add `_safe_daily_local_intelligence_href(href)` that accepts normal detail paths
> through `_validated_detail_relative_path(...)` and also accepts the exact
> `#local-article` fragment after a valid `.html` detail path. It must reject every
> other fragment and every unsafe path.

This is the right layer and the right scope:
- It is a new helper, so it does not weaken the existing `_safe_signal_detail_href`
  (templates.py:1636) or the shared `_validated_detail_relative_path` validator — no
  regression risk for existing detail-page / signal-synthesis links.
- It accepts only the exact `local-article` fragment, so there is no open-redirect or
  arbitrary-anchor sink.
- The Task 4 Step 1 RED test (`'href="details/the-row-signal-1234567890.html#local-article"'`)
  drives this helper, and the Task 4 Step 1 omit-test confirms the section is absent
  without saved articles.

Codebase cross-check confirms `_validated_detail_relative_path` exists at
templates.py:2553 and `render_index_html` renders `{signal_synthesis}` at line 116,
so the prescribed insertion point ("after `{signal_synthesis}`") is feasible.

### C2. Aggregate body composition — RESOLVED

Prior finding: Task 2 Step 3 asserted `"Vogue Business, WWD" in body.en`, but the
Task 3 body rule ("use the article takeaway/first paragraph") yields a paragraph with
no source names, so the RED assertion could not pass under the GREEN spec.

Plan edit resolution: Task 3 Step 2 "Required behavior" now pins the exact
body-composition rule:

> Compose aggregate entity/product `body.en` as `"{chosen_source_text} Sources:
> {source_names}."` and `body.zh` as `"{chosen_source_text_zh} 来源：{source_names}。"`,
> with `source_names` deduplicated in first-seen order.

The Task 2 Step 3 assertion was updated to match exactly:

```python
assert brand_watch.items[0].body.en == (
    "The Row appears with Margaux in a saved article. Sources: Vogue Business, WWD."
)
```

story-a's first paragraph is `"The Row appears with Margaux in a saved article."`,
and the two deduplicated sources in first-seen order are `["Vogue Business", "WWD"]`,
so the composed body is achievable from the specified rule. Test and rule now agree.

### I1. `source_name` / `source_names` representation — RESOLVED

Prior finding: the model only had `source_name: str | None`, which is insufficient for
multi-source aggregates.

Plan edit resolution: Task 3 Step 1 model now carries both fields:

```python
source_name: str | None = None
source_names: list[str] = Field(default_factory=list)
```

Task 2 Step 2 covers the single-source case
(`source_name == "Vogue Business"`, `source_names == ["Vogue Business"]`) and
Task 2 Step 3 covers the multi-source aggregate case
(`source_names == ["Vogue Business", "WWD"]`). The representation is internally
consistent and testable.

### I2. heat_movers goal — RESOLVED

Prior finding: the Product Gap section overclaimed "candidate-signal movement" with no
implementing signal in the model.

Plan edit resolution: the "or candidate-signal movement" phrase is removed. Line 20
now reads "stories with positive local heat deltas and saved local article bodies".
Task 3 Step 2 states the deterministic inclusion rule:

> `heat_movers` includes only stories that have `heat_delta > 0` and a saved local
> article with non-empty `paragraphs`.

The goal no longer overclaims relative to the implementation, and the wording is now
consistent with the `AGENTS.md` heat-movers boundary ("local observed heat movement
over one configured source set").

### I3. heat_movers saved-article requirement — RESOLVED

Prior finding: the heat_movers saved-article dependency was implicit only.

Plan edit resolution: Task 3 Step 2 "Required behavior" states it explicitly (see I2
quote). Combined with the general rule "Include only local articles with non-empty
`paragraphs`" and the empty-articles assertion in Task 2 Step 4, the dependency is
now unambiguous.

### I4. Pinned rebuild command — RESOLVED

Prior finding: Task 7 Step 3 left the rebuild command flexible ("inspect the current
README/CLI tests") despite `README.md:706` already pinning it.

Plan edit resolution: Task 7 Step 3 now pins the exact command:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one refresh \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data" \
  --reports-dir "$PWD/reports" \
  --output-dir reports/row-one/site \
  --as-of "$AS_OF"
```

Codebase cross-check confirms this matches `README.md:706`
(`uv run fashion-radar row-one refresh --config-dir "$PWD/configs" --data-dir
"$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of
"$AS_OF"`) with the `AGENTS.md`-required `UV_NO_CONFIG=1 uv --no-config run --frozen`
prefix for agent-run verification. The Self-Review "Placeholder scan" item was
updated accordingly and no longer calls the command flexible.

## Previously Minor Notes — Status

- M1 (brittle `<script>` escape assertion) — RESOLVED. The escape test now asserts
  the escaped form directly (`"&lt;script&gt;alert(&quot;body&quot;)&lt;/script&gt;"
  in html`) plus the negative form (`'<script>alert("body")</script>' not in html`),
  matching the existing `test_render_row_one_site_escapes_html_and_omits_unsafe_links`
  style.
- M2 (docs test should reuse `_read(README)` + `_normalized(...)`) — RESOLVED. The
  docs test now calls `_normalized(_read(README))`.
- M3 (redundant `row-one-app/v7` assertion) — RESOLVED. The assertion now targets
  `"row-one-app/v7 remains stable"`, the stability sentence this stage adds.
- M4 (unspecified meta helper output) — RESOLVED. Task 5 Step 2 pins the rendered
  meta fields: article count, story count, evidence count, positive heat delta when
  present, and comma-joined `source_names`.
- M5 (CSS selector list gaps) — RESOLVED. Task 5 Step 3 now lists nine selectors
  including `.daily-local-intelligence-group-title`, `.daily-local-intelligence-card
  h3`, `.daily-local-intelligence-card p`, and `.daily-local-intelligence-meta`.
- M6 (`scroll-margin-top` for `#local-article`) — STILL OPEN. See minor note n6
  below. Not blocking.
- M7 (unused `dataclass`/`field` imports) — RESOLVED. The builder skeleton imports
  only `defaultdict`, `Mapping`, and `Sequence`.
- M8 (reference dedup tiebreak) — PARTIALLY RESOLVED. The plan states "Aggregate
  refs case-insensitively while preserving the first display name" and "Deduplicate
  sources and references," which covers the common case. The first-seen `label`
  tiebreak for the same normalized name and same type is still implicit (see n5).

## New Issues Introduced By Plan Edits

None Critical. None Important.

The plan edits are confined to the previously flagged areas (validation helper,
body-composition rule, model fields, heat_movers rule, rebuild command, minor test
refinements). The edits do not expand scope, do not add a new top-level
`row-one-app/v7` field, do not introduce platform-collection behavior, and do not
weaken existing validation. The boundary check continues to pass: free-first /
local-first preserved, source-grounded, deterministic, no scraping / platform APIs /
browser automation / cookies / paywall bypass / compliance-review features.

## Minor Notes (non-blocking)

n1. **Body-source selection for multi-article aggregates is implied, not stated.**
Task 3 Step 2 says: "prefer a saved takeaway or paragraph whose `paragraph_indices`
match the reference item; otherwise use the article takeaway/first paragraph."
`RowOneReference` carries no `paragraph_indices`, so the "prefer" clause never fires
for aggregates and the fallback always applies — but "the article" is ambiguous when
multiple articles contain the same normalized ref. The Task 2 Step 3 test expects
story-a's paragraph (`"The Row appears with Margaux in a saved article."`), which is
the first-seen story in edition order, not story-b (which has the higher
`heat_delta=8`). The implementer must infer "first-seen story in edition order, then
first takeaway / first paragraph." Recommend adding one sentence to Task 3 Step 2 to
pin this explicitly and avoid a RED-test trial cycle. The test itself is correct.

n2. **heat_movers body fallback when an article has paragraphs but no takeaways is
unspecified.** The Product Gap section says heat_movers uses "the saved local article
takeaway as the body," but the inclusion rule only requires non-empty `paragraphs`
(not takeaways), so an article with paragraphs and no `takeaways` content section has
no specified body. The strongest_reads fallback rule ("use `content_sections[*].key
== "takeaways"` first; fallback to the first non-empty paragraph") should be reused
for heat_movers. The Task 2 Step 2 test only asserts `heat_delta == 9` for heat_movers
and does not exercise this case, so it is untested today. Recommend reusing the
strongest_reads fallback rule in Task 3 Step 2 for heat_movers bodies.

n3. **Aggregate item `detail_path` is unspecified.** `brand_watch` and
`product_watch` items aggregate across stories. The model allows
`detail_path: str | None = None`, but Task 3 does not state whether an aggregate item
links to the first-seen story's `#local-article` detail path or leaves `detail_path`
as `None`. The Task 2 Step 3 test does not assert `detail_path` for aggregates, so
this is untested. Recommend pinning the behavior (first-seen story detail path with
`#local-article`, or `None`) for determinism.

n4. **Aggregate `evidence_count` aggregation rule is unspecified.** The model has
`evidence_count: int = 0`, and Task 5 Step 2 renders it in the meta line, but Task 3
does not state how to compute it for aggregate items (sum across matching stories?
sum across matched articles? max?). No test pins the aggregate `evidence_count` value
today. Recommend stating the rule (e.g., sum of `len(story.evidence)` across the
matched stories).

n5. **Reference `label` tiebreak for the same normalized name is still implicit.**
When two refs share a normalized name but have different labels (Task 2 Step 3 uses
`"tracked"` for story-a's "The Row" and `"candidate"` for story-b's "the row"), the
aggregated `references` list should keep the first-seen label deterministically. The
plan says "preserving the first display name," which implies first-seen-wins for the
label too, but a one-clause note ("first-seen `label` wins on tie") would make this
explicit and match the test fixture.

n6. **`scroll-margin-top` for `#local-article` is still not addressed (carried from
M6).** The generated site has a sticky header. Fragment jumps to
`details/...html#local-article` may hide the target under the header, regressing the
in-page anchor UX versus existing detail-page anchors. Recommend adding
`scroll-margin-top` to the `#local-article` target (and any new in-page anchor) in
Task 5 Step 3 CSS, matching the existing detail-page anchor behavior.

n7. **Section title strings are pinned by the test but not by the plan body.**
Task 4 Step 1 asserts `'<span data-lang="en">Daily Local Intelligence</span>'` and
`'<span data-lang="zh">每日本地情报</span>'`, but Task 5 Step 2 does not state these
exact strings. The implementer will infer them from the RED test (which is fine under
TDD), but listing them in Task 5 Step 2 alongside the existing bilingual-text pattern
reference would keep the plan self-documenting.

## Required Changes Before Implementation

None. All previous BLOCK findings are resolved and no new Critical or Important
issues were introduced. The minor notes above can be addressed at the implementer's
discretion during the Task 2–Task 5 TDD cycle (each is either self-correcting via the
prescribed tests or purely cosmetic/UX).

## Conclusion

The plan is approved for implementation with notes. Proceed to Task 2 (RED local
intelligence builder tests). After Task 7 code-review, record
`docs/reviews/opencode-stage-301-code-review.md` (and attempt
`docs/reviews/claude-code-stage-301-code-review.md` with `--effort max` first).
