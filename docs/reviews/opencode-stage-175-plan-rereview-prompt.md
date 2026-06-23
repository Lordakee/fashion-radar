# Stage 175 Plan Rereview Prompt

Rereview the Stage 175 plan after fixes for the first plan-review findings.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 175 Plan Rereview

Objective:

Keep `docs/entity-pack-quality.md` table and JSON samples synchronized with
current `entity-pack-lint` output for the checked-in starter watchlist pack.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/reviews/opencode-stage-175-plan-review.md`
- `docs/superpowers/specs/2026-06-23-stage-175-entity-pack-quality-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-23-stage-175-entity-pack-quality-sample-parity-plan.md`
- `docs/entity-pack-quality.md`
- `tests/test_entity_pack_quality_docs.py`
- `src/fashion_radar/entity_packs.py`

First plan-review finding to verify:

- Important: the planned table parity test used absolute
  `WATCHLIST_ENTITY_PACK`, causing `render_entity_pack_lint_table(...)` to print
  an absolute path while the documented sample uses
  `configs/entity-packs/fashion-watchlist.example.yaml`.

Applied fixes:

- The design now states that the table parity test must pass
  `WATCHLIST_ENTITY_PACK.relative_to(ROOT)` into `lint_entity_pack(...)`.
- The plan's table parity test now uses:

```python
relative_pack_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT)
rendered_lines = render_entity_pack_lint_table(lint_entity_pack(relative_pack_path))
```

- The design and plan now both describe `_json_ready_first_finding(result)` as a
  helper that receives the already-computed lint result.
- The RED-step description now says the table parity test should pass before
  docs updates while the JSON parity test should fail.

Scope boundaries remain:

- Docs/test-only.
- Keep runtime lint behavior, entity config loading, matcher behavior, scoring
  behavior, CLI behavior, payload shape, renderer behavior, exit behavior,
  install hints, mirror hints, dependency manifests, and `uv.lock` unchanged.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

Review questions:

1. Were the important path-handling issue and minor spec/plan alignment issues
   fixed?
2. Is the plan now implementable with a credible RED/GREEN path?
3. Are there any remaining critical or important findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Fix Assessment
- Verdict
