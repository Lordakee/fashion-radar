# Stage 181 Plan Review Prompt

Review the Stage 181 plan for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 181 Plan Review
```

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-181-community-docs-adapter-catalog-parity-design.md`
- `docs/superpowers/plans/2026-06-24-stage-181-community-docs-adapter-catalog-parity-plan.md`
- `tests/test_external_tool_contract_parity.py`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `src/fashion_radar/external_tool_adapters.py`
- `README.md`
- `docs/cli-reference.md`

Review questions:

1. Does the plan satisfy the objective: docs/test-only parity so
   `docs/community-signal-import.md` and `docs/community-signal-quality.md`
   list the current external social/community adapter catalog?
2. Does the proposed test derive adapter rows from the runtime registry instead
   of duplicating stale constants?
3. Will the proposed RED fail before docs edits because the target docs do not
   yet contain `Known adapter ids:` and the current exact rows?
4. Do the proposed docs preserve the advisory-only meaning of platform labels
   and avoid implying platform coverage, demand proof, connectors, scraping,
   browser automation, platform APIs, monitoring, scheduling, source
   acquisition, ranking, or compliance-review product behavior?
5. Are the verification commands sufficient for this docs/test-only node before
   the full release gate?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the plan
is acceptable, say it is approved for implementation.
