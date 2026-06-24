# Stage 187 Plan Review Prompt

Review the Stage 187 plan for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 187 Plan Review
```

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md`
- `docs/superpowers/plans/2026-06-24-stage-187-community-adapter-catalog-exact-table-plan.md`
- `tests/test_external_tool_contract_parity.py`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/reviews/opencode-stage-181-release-review.md`

Review questions:

1. Does the plan satisfy the objective: exact-table docs parity so stale extra
   adapter rows and row-order drift cannot pass in the two community docs?
2. Does the proposed test still derive current adapter rows from the live
   runtime registry fixture instead of duplicating stale adapter constants?
3. Is the temporary stale-row mutation a meaningful RED proof for this
   test-only hardening stage, and is the plan clear that it must be reverted
   before commit?
4. Is the change appropriately limited to
   `tests/test_external_tool_contract_parity.py` plus staged review artifacts,
   with docs content changes only if real drift is found?
5. Does the plan avoid source acquisition, scraping, browser automation,
   platform APIs, dependency changes, package changes, scheduling, ranking,
   demand proof, platform coverage verification, and compliance-review product
   behavior?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the plan
is acceptable, say it is approved for implementation.
