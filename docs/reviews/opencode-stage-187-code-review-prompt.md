# Stage 187 Code Review Prompt

Review the Stage 187 implementation for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 187 Code Review
```

Files to review:

- `tests/test_external_tool_contract_parity.py`
- `docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md`
- `docs/superpowers/plans/2026-06-24-stage-187-community-adapter-catalog-exact-table-plan.md`
- `docs/reviews/opencode-stage-187-plan-review.md`

Implementation summary:

- Added `_known_adapter_catalog_doc_table(text)` as a test-local helper that
  requires exactly one `Known adapter ids:` marker, requires the blank line
  before the table, and extracts contiguous Markdown table rows.
- Added
  `test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table`
  to compare both community docs' extracted table blocks to a registry-derived
  expected table.
- Kept the existing substring/advisory wording test intact.
- Did not change runtime source, CLI behavior, docs content, dependencies, or
  lockfiles.

TDD and focused verification already run:

- New target test initially was not collected.
- After adding only the new test, it failed with `NameError` for the missing
  helper.
- After adding the helper, the new test passed.
- A temporary stale `removed_adapter` row in
  `docs/community-signal-quality.md` made the new test fail, then removing that
  temporary row restored GREEN.
- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q -k "adapter_catalog or community_signal_docs"` passed.
- `uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q` passed.
- `uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py` passed.
- `uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py` passed.

Review questions:

1. Does the implementation close the Stage 181 M1 gap by rejecting stale extra
   adapter rows and row-order drift in the community docs adapter catalog
   tables?
2. Is `_known_adapter_catalog_doc_table(text)` appropriate for the two target
   docs and unlikely to mask marker/table drift?
3. Does the new test still derive adapter data from the live registry fixture?
4. Is the temporary stale-row RED proof meaningful, and is there any evidence
   that the temporary docs mutation remains in the working tree?
5. Does the implementation avoid source acquisition, scraping, browser
   automation, platform APIs, dependency changes, package changes, scheduling,
   ranking, demand proof, platform coverage verification, and
   compliance-review product behavior?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the
implementation is acceptable, say it is approved for release-gate verification.
