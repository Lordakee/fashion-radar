# Stage 175 Plan Review Prompt

Review the Stage 175 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 175 Plan Review

Objective:

Keep `docs/entity-pack-quality.md` table and JSON samples synchronized with
current `entity-pack-lint` output for the checked-in starter watchlist pack.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-175-entity-pack-quality-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-23-stage-175-entity-pack-quality-sample-parity-plan.md`
- `docs/entity-pack-quality.md`
- `tests/test_entity_pack_quality_docs.py`
- `src/fashion_radar/entity_packs.py`
- `tests/test_entity_pack_lint.py`
- `tests/test_source_packs_docs.py`

Scope boundaries:

- Docs/test-only.
- Keep runtime lint behavior, entity config loading, matcher behavior, scoring
  behavior, CLI behavior, payload shape, renderer behavior, exit behavior,
  install hints, mirror hints, dependency manifests, and `uv.lock` unchanged.
- Update only entity-pack quality docs/tests so documented table/JSON examples
  stay aligned with `lint_entity_pack(...)` for the checked-in starter watchlist
  pack.
- The JSON docs may stay abbreviated, but they must explicitly say the findings
  list is an abbreviated representative excerpt and not the full findings list.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

Planned implementation:

1. Add helpers in `tests/test_entity_pack_quality_docs.py` to extract fenced
   `text` and `json` blocks from `docs/entity-pack-quality.md`.
2. Add a table sample parity test that compares the documented table sample to
   the prefix of `render_entity_pack_lint_table(lint_entity_pack(...))`.
3. Add a JSON sample parity test that compares documented stable count fields to
   `lint_entity_pack(configs/entity-packs/fashion-watchlist.example.yaml)`.
4. Run the JSON parity test before docs updates and confirm it fails because the
   current JSON sample abbreviates `tag_counts` / `category_tag_counts`, uses a
   non-current representative finding, and does not state the findings list is
   abbreviated.
5. Update `docs/entity-pack-quality.md` so the JSON sample's count fields match
   current linter output and the sample explicitly says it is an abbreviated
   representative excerpt, not the full findings list.
6. Run focused tests/lint, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Are the proposed docs parity tests useful without being too broad or brittle?
4. Does abbreviating the long findings list while testing exact counts and one
   first finding strike the right documentation-maintenance tradeoff?
5. Did any out-of-scope runtime, lint payload, CLI, matcher, scoring,
   source-acquisition, ranking, coverage-verification, install-hint,
   mirror-hint, dependency, lockfile, or compliance-review behavior slip into
   the plan?
6. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
