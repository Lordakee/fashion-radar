# Stage 168 Plan Review Prompt

Review the Stage 168 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 168 Plan Review

Objective:

Synchronize `docs/source-packs.md` with the checked-in public starter source
pack so the documentation names the actual 10 GDELT lanes and shows current
source-pack lint count output.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-design.md`
- `docs/superpowers/plans/2026-06-23-stage-168-source-pack-public-gdelt-doc-sync-plan.md`
- `docs/source-packs.md`
- `tests/test_source_packs_docs.py`
- `configs/source-packs/fashion-public.example.yaml`

Scope boundaries:

- Documentation and documentation-test drift guard only.
- No changes to `configs/source-packs/fashion-public.example.yaml`.
- No source-pack linter behavior changes.
- No CLI changes.
- No collector changes.
- No network availability probing.
- No Google News RSS, Google Trends, source acquisition expansion, scraping,
  browser automation, platform APIs, login, cookies, monitoring, scheduling,
  demand proof, ranking, coverage verification, or compliance-review product
  features.

Planned implementation:

1. Add tests in `tests/test_source_packs_docs.py` that:
   - parse the public source pack and require every `type: gdelt` source name
     to appear in the "GDELT Queries" docs section;
   - parse the docs example JSON block after "Example JSON shape:" and compare
     `source_count`, `enabled_count`, `disabled_count`, `type_counts`,
     `tag_counts`, and `findings` with `lint_source_pack(...)`.
2. Update `docs/source-packs.md` to:
   - expand the example `tag_counts` to current linter output;
   - list all 10 current GDELT source names with concise lane descriptions.
3. Run focused tests and ruff checks.
4. Run local opencode code review, release gate, release review, commit, and
   push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Are the planned tests strong enough to prevent the documented drift?
4. Is comparing linter count fields, but not `path`, the right stability
   choice?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
