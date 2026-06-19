I'll review the Stage 116 changes. Let me start by exploring the repository state and the changed files.
Now let me see the actual diffs for the modified files and read the supporting docs/specs.
Now let me read the example README, the relevant doc sections, the source modules referenced, and the new design/plan/review artifacts.
Now let me examine the source modules being tested to verify test correctness, and look at the design/plan/review artifacts.
Let me read the design/plan/review artifacts and check the CLI command signatures for `--format` flag support.
Now let me check the CLI command signatures to verify the documented flags are actually supported, and read the review prompt and plan review.
Let me verify the CLI command signatures accept all the documented flags (`--format`, `--directory`, `--input-format`, `--pattern`, `--source-name`, `--adapter`).
Let me run the focused and adjacent tests myself to verify the claimed state, and check whether a code-review output file already exists.
There's an existing 7-line code-review.md. Let me check its content and verify scope compliance (no stray changes to src/lockfiles).
Let me confirm the `generic_community_export` adapter defaults to CSV (so the JSON parametrization genuinely exercises the override path), and run ruff/lint on the changed test files.
## Stage 116 Code Review Findings

### Verdict: No Critical or Important blockers

Scope is clean — `git diff` confirms changes are limited to the two test files, the example README, `docs/community-signal-import.md`, and the new review/spec/plan artifacts. No `src/`, `uv.lock`, `pyproject.toml`, schema, CI, collector, or dashboard changes. I re-ran the adjacent suite (100 passed) and `ruff check`/`ruff format --check` on the changed tests (clean).

### Findings (ordered by severity)

**Nit-1 — Docs test pins a stricter global command order than the design requires**
`tests/test_cli_docs.py:1538-1549`
`preflight_keys == expected_preflight_keys` asserts the exact 4-tuple sequence `csv-readiness, csv-workflow, json-readiness, json-workflow`. The design (`...design.md:49-50`) only mandates readiness-before-workflow *per directory*. The stricter global order is sensible drift prevention, but an editor who later groups all readiness commands before all workflow commands would fail the test despite preserving the per-directory invariant. The per-directory `readiness_index < workflow_index` checks at `:1577` are then fully redundant (subsumed by the tuple-equality). Defensible as-is; just flagging the over-constraint.

**Nit-2 — Unused `expected_names` parameter in the new builder test**
`tests/test_community_tool_handoff_directory_examples.py:157`
`expected_names` is destructured but never referenced in the test body. This is intentional for parametrize-tuple consistency with the sibling directory tests and ruff accepts it; no action required.

**Nit-3 — `which` stub is never invoked for this adapter (carried from plan review)**
`tests/test_community_tool_handoff_directory_examples.py:175` / `src/fashion_radar/external_tool_readiness.py:94-98, 268-276`
`generic_community_export` has `command: None`, so `_upstream_command_check` returns `not_applicable` before ever calling `which`. The `which=lambda _command: None` stub is therefore defensive determinism. Harmless.

### Answers to the review questions

1. **CSV + JSON coverage incl. JSON override on the CSV-default adapter?** Yes. `DIRECTORY_EXAMPLES` (`tests/test_community_tool_handoff_directory_examples.py:33-36`) parametrizes both directories. `generic_community_export` defaults to `csv`/`*.csv` (`src/fashion_radar/external_tool_adapters.py:239-240`), so the JSON parametrization with `input_format="json"` genuinely exercises the override path — proven by `assert payload.input_format == input_format` at `:189`, which would fail for JSON without the override. Also pins `display_name`, `platform_label` (`community`), `directory`, `pattern`, `source_name`, `step_count`, `execution_mode`, and the `not_applicable`/`command is None` check shape.

2. **Concrete/copyable docs that stay local-guidance-only?** Yes. Both `examples/community-tool-handoff-directory.example/README.md:11-16` and `docs/community-signal-import.md:171-178` contain runnable `uv run fashion-radar ...` lines with `--format table`. Every flag (`--adapter`, `--directory`, `--input-format`, `--pattern`, `--source-name`, `--format`) maps to a real Typer option at `src/fashion_radar/cli.py:757-848`. Boundary prose is preserved in both files.

3. **Avoids runtime behavior changes and prohibited additions?** Yes. Verified by `git diff --name-only` against `src/|^uv\.lock|^pyproject\.toml|^\.github/|^schemas/` → NONE. No collection, scraping, connectors, platform APIs, scheduling, monitoring, ranking, demand proof, coverage verification, or compliance-review features introduced — only docs/tests pinning the existing override contract.

4. **Robustness around shell quoting, ordering, scoping?** Strong. Commands are tokenized via `shlex.split` (`tests/test_cli_docs.py:1470, 1490`), so quoted values like `"*.csv"` and `"External Community Tool"` parse correctly and `_flag_value` counts whole tokens (no substring false positives). Each required flag is asserted exactly once per command (`:1474`). Section scoping uses `_markdown_section(import_doc, "## External Tool Export Directory Examples")` (`:1529`), which excludes the unrelated `instaloader`/`rednote_mcp` readiness examples in the earlier `## External Tool Readiness` section. Import/lint commands in the same block are filtered out by the `name in {"external-tool-readiness", "external-tool-workflow"}` guard (`:1536`).

5. **Critical/Important blockers before the full release gate and commit?** None. Proceed to the full release gate (`scripts/check_release_hygiene.py`, full `pytest`, `ruff check`, `ruff format --check`, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `git diff --check`).
