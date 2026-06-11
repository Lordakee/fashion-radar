# Claude Code Stage 8 Plan Rereview 2 Prompt

Review the Stage 8 plan fixes made after the latest Claude Code result
`Approved after fixes`.

Repo: `/home/ubuntu/fashion-radar`

User rules:

- This review must use `--effort max`.
- This is a read-only planning review. Do not edit files, run collectors, add
  dependencies, access social platforms, scrape/crawl websites, mutate config,
  or perform network source collection. Return review findings only.
- Codex subagents used during implementation must use
  `reasoning_effort: "xhigh"`.
- Claude Code plan review must approve before implementation starts.
- After implementation, code must be reviewed by Claude Code before commit and
  next-stage planning.

Files to review:

- Design: `docs/superpowers/specs/2026-06-12-stage-8-candidate-discovery-design.md`
- Plan: `docs/superpowers/plans/2026-06-12-stage-8-candidate-discovery-plan.md`
- Previous rereview:
  `docs/reviews/claude-code-stage-8-plan-rereview.md`

Stage 8 goal:

Add deterministic "Untracked Candidate Signals" from already collected local
RSS/GDELT items, using only local SQLite data, without adding new source
collection, scraping, paid APIs, LLMs, embeddings, or social-platform access.

Latest fixes to verify:

- Strengthened the `run` acceptance test:
  - Seeds a configured phrase `The Row Margaux bag`, expected absent.
  - Seeds an unconfigured phrase `Le Teckel bag`, expected present.
  - Monkeypatches collect and match as no-ops so the test proves loaded
    `entities.yaml` is passed into report candidate discovery, not merely stored
    `item_entities`.
- Strengthened serialization safety tests:
  - Captures the existing report fixture's sentinel `item_entities` alias,
    reason, and context terms.
  - Asserts those exact sentinel values are absent from candidate JSON and
    Markdown.
  - Asserts candidate contexts are only controlled labels.
- Strengthened stored-entity predicate tests:
  - Low-confidence stored entity does not filter.
  - High-confidence stored entity with reason
    `manual_review_sentinel_not_accepted` still filters, locking in the rule
    that `reason == "accepted"` is not required.
- Strengthened read-only CLI coverage:
  - Missing DB does not create a DB file.
  - Missing data directory is not created.
  - Existing empty SQLite file returns a non-zero schema error and remains with
    no tables.

Please verify whether the remaining prior Important findings are resolved and
whether Stage 8 implementation may begin.

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 8 implementation
- Approved after fixes
- Do not proceed
