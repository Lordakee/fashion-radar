I'll review the Stage 116 plan. Let me read all the relevant files in parallel first.
Now let me read the rest of `test_cli_docs.py` to see the existing directory example docs test that the plan modifies.
Let me verify the adapter defaults for `generic_community_export` and check the existing readiness/workflow tests to confirm my analysis.
Let me verify the `generic_community_export` adapter definition to confirm the test assertions about default CSV and platform label.
I've completed a thorough review of the Stage 116 design and plan against the actual runtime code. Here are my findings.

---

# Stage 116 Plan Review Findings

## Verdict: No Critical or Important blockers

The plan is safe to implement. It correctly treats Stage 116 as a docs/tests-only node that pins existing runtime override contracts, stays fully within the allowed scope, and adds no runtime behavior.

## Findings (ordered by severity)

### Nit-1 — `import_doc` reuse is implicit in the docs-test snippet
`docs/superpowers/plans/2026-06-19-stage-116-directory-readiness-samples-plan.md:162-189`
The Task 1 Step 3 snippet loops over `("docs/community-signal-import.md", import_doc)` but never shows where `import_doc` is read. It already exists at `tests/test_cli_docs.py:1445` inside the same test, so the code is correct as long as the implementer *adds* this block to the existing test body rather than replacing it. Suggest the plan note "append to the existing test body; `import_doc` is already defined above." Not a blocker.

### Nit-2 — Placement instruction for the README block is mildly ambiguous
`...plan.md:209-212` ("add this block after the existing CSV/JSON bullets")
The substring docs assertions only require readiness-before-workflow *within each directory case*, which holds regardless of where the block lands in the README. Any sensible placement passes; just flagging the wording.

### Nit-3 — `which=lambda _command: None` is redundant-but-harmless for this adapter
`...plan.md:98`
`generic_community_export` has `"command": None` in `src/fashion_radar/external_tool_readiness.py:94-98`, so `_upstream_command_check` returns early at `:268-276` and never calls `which`. Passing a stub is defensive determinism, not a bug. Fine to keep.

### Nit-4 — `import shlex` placement not specified
`...plan.md:57-59`. Trivial; the implementer will place it alphabetically.

---

## Answers to the review questions

**1. Does the plan correctly rely on existing readiness/workflow override support?**
Yes. `build_external_tool_readiness(...)` at `src/fashion_radar/external_tool_readiness.py:144-210` already accepts and applies `adapter_id`, `directory`, `input_format`, `pattern`, and `source_name` overrides (`:172-174`), and `build_external_tool_workflow(...)` at `src/fashion_radar/external_tool_workflow.py:69-126` mirrors this (`:96-98`). No `src/` change is needed or proposed.

**2. Do the tests cover both CSV and JSON, including the JSON override on `generic_community_export`?**
Yes. The new parametrized test reuses `DIRECTORY_EXAMPLES` (`tests/test_community_tool_handoff_directory_examples.py:30-33`) for both directories, passes `input_format="json"`/`pattern="*.json"` for the JSON case, and asserts `payload.input_format == input_format`. Since `generic_community_export` defaults to CSV (`src/fashion_radar/external_tool_adapters.py:239`), the JSON parametrization proves the override path. It also pins `display_name`, `platform_label`, `directory`, `pattern`, `source_name`, `step_count`, `execution_mode`, and the `not_applicable`/`command is None` readiness check.

**3. Do the docs assertions guard concrete snippets without becoming brittle?**
Yes. The assertions use `_normalized_text` (whitespace-collapsing substring match) for the *exact* full command string per directory, plus an ordering check (`readiness.index < workflow.index`) per directory case. They target only the two in-scope docs and the specific preflight commands, so unrelated prose/doc edits won't trip them. I verified the other `external-tool-readiness`/`external-tool-workflow` mentions in `docs/community-signal-import.md` (e.g. `:137`, `:101`) use different adapters/flags and cannot collide with `.index()`.

**4. Are the verification commands sufficient?**
Yes. Focused targets the two directly-touched tests; adjacent adds `test_external_tool_readiness.py`, `test_external_tool_workflow.py`, and the full directory/docs suites; the release gate runs release-hygiene, full pytest, ruff check + format, `UV_NO_CONFIG=1 uv lock --check` (matching `AGENTS.md`), the mirror-URL scan, the `uv.lock`/`pyproject.toml` diff guard, and `git diff --check`. This matches project conventions.

**5. Critical/Important blockers before implementation?**
None. The plan is scope-compliant (no `src/`, schema, dependency, CI, collector, scoring, report, dashboard, or import-behavior changes; no collection/scraping/connectors/platform APIs). It only wires checked-in examples to existing local preflight guidance. Proceed to Task 1.
