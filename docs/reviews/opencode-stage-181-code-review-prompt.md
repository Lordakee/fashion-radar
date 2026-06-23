# Stage 181 Code Review Prompt

Review the Stage 181 implementation in `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 181 Code Review
```

What changed:

- `tests/test_external_tool_contract_parity.py`
  - Adds a runtime-derived docs parity test for the external-tool adapter
    catalog in community docs.
- `docs/community-signal-import.md`
  - Adds the current `Known adapter ids` table under
    `## External Tool Adapter Registry`.
- `docs/community-signal-quality.md`
  - Adds the same table near the existing `external-tool-adapters` guidance.
- Stage 181 spec, plan, and plan-review artifacts were added.

Approved plan:

- `docs/superpowers/specs/2026-06-24-stage-181-community-docs-adapter-catalog-parity-design.md`
- `docs/superpowers/plans/2026-06-24-stage-181-community-docs-adapter-catalog-parity-plan.md`
- `docs/reviews/opencode-stage-181-plan-review.md`

Verification already run:

- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py::test_community_signal_docs_list_current_external_tool_adapter_catalog -q`
  - RED before docs edits: failed on missing `Known adapter ids:`.
  - GREEN after docs edits: 1 passed.
- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q`
  - 7 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q`
  - 69 passed.
- `uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py`
  - All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py`
  - 1 file already formatted.

Review questions:

1. Does the implementation match the approved Stage 181 plan?
2. Does the new test derive every expected adapter row from the runtime registry
   and fail when either community doc omits a current adapter row?
3. Do both docs contain the current adapter ids, display/source names, platform
   labels, input formats, and patterns exactly as runtime registry values render
   in the test?
4. Does the docs wording preserve advisory-only platform-label semantics and
   avoid implying platform coverage, demand proof, connectors, scraping, browser
   automation, platform APIs, monitoring, scheduling, source acquisition,
   ranking, or compliance-review product behavior?
5. Are there any missing tests, overbroad assertions, or maintainability issues
   before release verification?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the
implementation is acceptable, say it is approved for release verification.
