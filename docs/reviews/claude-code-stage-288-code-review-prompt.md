# Stage 288 Code Review Prompt

Review the current uncommitted Stage 288 changes in `/home/ubuntu/fashion-radar`.

Context:
- Product: ROW ONE static daily fashion intelligence website.
- Stage 288 goal: polish Signal Synthesis by localizing visible signal meta labels and adding same-group ordering regression coverage.
- Scope should remain narrow: `src/fashion_radar/row_one/templates.py`, `tests/test_row_one_app_contract.py`, `tests/test_row_one_render.py`, and review/plan artifacts.
- Do not recommend compliance-review product features.
- Do not require changes to `uv.lock` or `pyproject.toml`.

Please inspect:
1. Whether `_signal_synthesis_meta_label()` preserves escaping and language-toggle conventions.
2. Whether `test_row_one_app_contract_orders_signal_synthesis_within_group` actually covers positive heat sum, evidence count, story count, and name tie-break ordering.
3. Whether the implementation changes are minimal and compatible with existing schema contract `row-one-app/v6`.
4. Whether any Critical or Important issues must be fixed before commit.

Return findings grouped as Critical, Important, Minor, or None. Include concise file/line references when useful.
