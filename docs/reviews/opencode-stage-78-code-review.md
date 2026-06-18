I'll review Stage 78 systematically. Let me start by examining the files in scope and verifying the acceptance criteria.
uv.lock change confirmed as mirror URL rewrites only. Now let me read the in-scope files.
Now let me verify the design/plan docs and read the source files referenced in the tests.
Now let me examine the source modules referenced by the tests to verify the contracts hold.
Now let me run the verification commands claimed in the prompt to confirm they pass.
Let me read the docs context around the new subsection and the review artifacts.
Let me verify all the review artifacts exist and check the prompts.
Let me do final confirmation that no `src/` or manifest changes are present and verify the full test suite for the parity module once more.
# Stage 78 Adapter Contract Parity Gate — Code Review

## Verdict

**No Critical findings. No Important findings.** The stage is ready to commit (excluding the out-of-scope `uv.lock`).

I verified every acceptance criterion against current `src/`: all 7 adapter IDs match (`external_tool_adapters.py:108-234`), field mappings derive from `community_signal_profile.py:14-37`, template mirrors adapter contract (`external_tool_templates.py:94-116`), workflow/readiness step commands match `recommended_commands` by index (`external_tool_workflow.py:170-423`, `external_tool_readiness.py:303-445`), and the lint result shape matches (`community_signals.py:58-84`). The prior plan-review C1 (raw-text phrase wrap, case mismatch, distributed negation) and M1 are fully resolved in the implementation.

## Verification (all pass)

- `pytest tests/test_external_tool_contract_parity.py tests/test_cli_docs.py::test_community_signal_import_docs_describe_external_tool_contract_parity` → 7 passed
- `pytest tests/test_cli_docs.py` (full) → 48 passed (the `COMMUNITY_SIGNAL_IMPORT_DOC` constant refactor is safe)
- `ruff check` + `ruff format --check` on both test files → clean
- `git diff --check` → clean
- `git diff --name-only` → only `CHANGELOG.md`, `docs/community-signal-import.md`, `tests/test_cli_docs.py`, `uv.lock` (mirror rewrite only). **No `src/`, no `pyproject.toml`, no staged `uv.lock`.**

## Acceptance criteria confirmation

- Parity tests use public builders/renderers only — no private helpers imported (`tests/test_external_tool_contract_parity.py:9-20`). ✓
- All seven adapters covered via `EXPECTED_ADAPTER_IDS` + `[adapter.id for adapter in registry.adapters] == EXPECTED_ADAPTER_IDS` (`:27-35`, `:87`). ✓
- Field mappings match profile allowed/required fields (`:92-95`). ✓
- Template metadata + command guidance mirror the registry (`:109-123`). ✓
- Rendered JSON/CSV lint cleanly, `valid_row_count == 2`, items contain only profile fields (`:138-153`). ✓
- Workflow/readiness shared steps reuse adapter commands; `--dry-run` separation asserted both directions via `shlex.split` (`:167-189`). ✓
- Dry-run import guidance separate from real import guidance (`:170-171`, `:189`). ✓
- Banned-token check is exact-whole-token after `shlex.split`, so `tiktok_api`/`'TikTok-Api Export'` cannot collide with `api`; install hints live on `checks[].install_hint` and are correctly excluded (`:192-222`). ✓
- Docs describe parity gate as local contract protection only (`docs/community-signal-import.md:189-207`). ✓
- `src/`, manifests, public `uv.lock` unchanged by this stage. ✓

## Minor (informational, non-blocking)

1. **Hardcoded command indexes are the contract by design.** `WORKFLOW_RECOMMENDED_COMMAND_STEPS`/`READINESS_RECOMMENDED_COMMAND_STEPS` (`:37-54`) pin numeric positions in `adapter.recommended_commands`. This is inherent to a parity gate — the index *is* the documented contract — but means a reorder that updates both sides consistently would pass silently. Acceptable given the stage's drift-detection intent.
2. **Workflow/readiness-only steps are intentionally not bound to `recommended_commands`.** `inspect_adapter_registry`, `print_adapter_template_json`, `preview_candidate_phrases`, `print_external_tool_workflow` reference workflow-specific entry points rather than shared handoff commands, so they are correctly omitted from the index maps. Not a coverage gap.
3. **`Path("./exports")` normalizes to `"exports"`** (leading `./` stripped), carried over from M3 of the plan review — purely cosmetic, no correctness impact since all builders receive the same value.

Stage 78 may proceed to commit with the file list in `docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md:468-477`; the dirty `uv.lock` must remain unstaged per the stage boundaries.
