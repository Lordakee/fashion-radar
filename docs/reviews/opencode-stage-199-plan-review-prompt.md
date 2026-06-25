# Stage 199 Plan Review Prompt

Review the Stage 199 implementation plan:

`docs/superpowers/plans/2026-06-25-stage-199-aggregate-match-evidence-report-plan.md`

## Context

Current repo: `/home/ubuntu/fashion-radar`

Stage 197 expanded the optional public source pack. Stage 198 expanded optional deterministic entity watchlist coverage. Current roadmap says v0.1.x product work should prioritize curated public-source coverage using source-liveness evidence and deterministic matching quality, while keeping experimental/community handoff expansion frozen.

Three read-only candidate explorations were run:

- Source coverage agent recommended one optional Footwear News RSS source, but noted live source-liveness in this sandbox is currently blocked by SOCKS/socksio environment noise and should be advisory.
- Matcher/report agent recommended aggregate match-evidence summaries in daily reports.
- Release/tooling agent recommended installed-wheel parity as a secondary release-hardening option, but explicitly ranked product source/matcher work higher.

The selected plan is Stage 199 aggregate match evidence because it advances deterministic matching quality, is fully local/offline testable, and avoids source-liveness proxy-environment dependence.

## Review Questions

1. Is this a reasonable Stage 199 product node after Stage 198, or should it be redirected to the one-source footwear RSS expansion instead?
2. Does the plan preserve aggregate-only evidence and avoid leaking raw aliases, context terms, item ids, normalized URLs, raw matcher rows, or per-row matcher internals?
3. Are the proposed reason buckets (`accepted`, `context`, `parent_brand`, `safe_alias`, other) aligned with current matcher semantics and safe for stored unknown reasons?
4. Is the duplicate-row rule technically sound: dedupe by `(entity_name, entity_type, item_id)`, choose highest confidence, tie-break lexicographically by reason?
5. Does the evidence window align with scoring and representative items: `current_start < collected_at <= as_of` and `confidence >= min_match_confidence`?
6. Are docs/smoke/CLI tests scoped enough without causing unnecessary docs sprawl?
7. Does the plan avoid source collection, source-pack changes, social connectors, scraping/crawling/browser automation, login/cookie/session/token/proxy behavior, ranking/hotness/demand proof, platform coverage verification, and compliance-review product features?
8. Are any plan steps impossible, brittle, missing necessary imports/files, or likely to fail with existing tests?

Start the response exactly with:

```markdown
# Stage 199 Plan Review
```

Then include:

- Verdict
- Critical findings
- Important findings
- Minor findings
- Answers to the review questions
- Required plan changes before implementation

Do not include tool-status chatter, live command transcripts, duplicated drafts, or process narration.
