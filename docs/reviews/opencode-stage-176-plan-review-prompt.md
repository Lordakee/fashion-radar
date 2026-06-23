# Stage 176 Plan Review Prompt

Review the Stage 176 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 176 Plan Review

Objective:

Keep `docs/source-pack-quality.md` table and JSON samples synchronized with
current `source-pack-lint` output for the checked-in public source pack.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-24-stage-176-source-pack-quality-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-24-stage-176-source-pack-quality-sample-parity-plan.md`
- `docs/source-pack-quality.md`
- `tests/test_source_pack_quality_docs.py`
- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- `tests/test_source_packs_docs.py`

Scope boundaries:

- Docs/test-only.
- Keep runtime lint behavior, source config loading, collector behavior, CLI
  behavior, payload shape, renderer behavior, exit behavior, install hints,
  mirror hints, dependency manifests, and `uv.lock` unchanged.
- Update only source-pack quality docs/tests so documented table/JSON examples
  stay aligned with `lint_source_pack(...)` for the checked-in public source
  pack.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, demand proof, ranking, coverage verification, or
  compliance-review product feature.

Planned implementation:

1. Add helpers in `tests/test_source_pack_quality_docs.py` to extract fenced
   `text` and `json` blocks from `docs/source-pack-quality.md`.
2. Add a table sample parity test that compares the documented table sample to
   the prefix of `render_source_pack_lint_table(lint_source_pack(...))` using a
   relative public pack path.
3. Add a JSON sample parity test that compares documented stable fields to
   `lint_source_pack(configs/source-packs/fashion-public.example.yaml)`.
4. Run the JSON parity test before docs updates and confirm it fails because the
   current JSON sample abbreviates `tag_counts` and shows a synthetic warning
   finding while current runtime output has `findings: []`.
5. Update `docs/source-pack-quality.md` so the JSON sample matches current
   linter output.
6. Run focused tests/lint, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Are the proposed docs parity tests useful without being too broad or brittle?
4. Does using `findings: []` for the clean checked-in public source pack strike
   the right documentation-maintenance tradeoff?
5. Did any out-of-scope runtime, lint payload, CLI, collector,
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
