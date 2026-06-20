# Stage 126 Community Handoff Order Docs Design

## Objective

Align user-facing community handoff command sequences with the canonical local
handoff order:

1. `community-signal-lint-dir`
2. `community-candidates-dir`
3. `community-handoff-check-dir`
4. `import-signals-dir --dry-run`
5. `import-signals-dir`
6. `imported-review-workflow`

## Problem

Runtime workflow generation already uses the correct order. The
`community-handoff-workflow` builder emits lint, candidate preview,
`review_handoff_readiness`, dry-run import, import, and post-import review, and
its tests pin that sequence.

Several user-facing command blocks drifted from that sequence:

- `README.md` shows the standalone directory readiness check before the
  directory lint and candidate-preview commands in the external community tool
  sample.
- `README.md` shows the standalone directory readiness check before the
  directory lint command in the configuration handoff sample, and the same block
  omits `community-candidates-dir`.
- `docs/community-signal-quality.md` recommended order omits
  `community-handoff-check-dir` between candidate preview and dry-run import.
- `docs/architecture.md` command flow shows the standalone directory readiness
  check before lint and candidate preview.

This can teach users to run the readiness summary before the lint and candidate
preview checks it is meant to summarize.

## Scope

In scope:

- Reorder the affected `README.md` community handoff command blocks.
- Add the missing `community-candidates-dir` command to the README directory
  handoff sample.
- Add the missing `community-handoff-check-dir` command to the
  `docs/community-signal-quality.md` recommended order.
- Reword the quality prose so readiness is described after preview and before
  importer dry-run.
- Reorder the affected `docs/architecture.md` command flow lines.
- Add a docs-only regression test that checks the named sections keep the
  canonical subsequence.

Out of scope:

- No runtime product behavior changes.
- No CLI behavior changes.
- No external adapter or profile command generation changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.
- No dependency changes.
- No `uv.lock` changes.

## Architecture

This is a documentation drift node:

1. `tests/test_cli_docs.py` gets a targeted helper/test that parses only the
   named README, quality, import, and architecture sections.
2. The test extracts `fashion-radar` command names from fenced bash blocks using
   the existing `_bash_blocks`, `_shell_commands`, and
   `FASHION_RADAR_COMMAND_RE` helpers.
3. The assertion checks a subsequence instead of global document order so
   producer-facing external-tool preflight sections can keep their intentional
   order.
4. The docs edits reorder only the affected command blocks and add the missing
   local commands.

## Expected Behavior

After implementation:

- The README external community tool sample keeps print-only and external
  preflight commands, then shows the local directory sequence as lint,
  candidates, readiness, dry-run import, and import before the separate
  post-import review block.
- The README directory handoff sample shows manifest/workflow first, then lint,
  candidates, readiness, dry-run import, and import.
- The quality recommended order shows lint, candidates, readiness, dry-run
  import, import, and imported review before the detailed review commands.
- The architecture command flow shows directory lint and candidates before
  `community-handoff-check-dir`.
- The new docs test fails if any named section removes
  `community-handoff-check-dir` or moves it before preview or after import.

## Risks

- A global command-order assertion would be brittle because producer-facing
  external preflight examples intentionally list profile/readiness/manifest
  commands before local handoff execution commands. The test must target named
  sections.
- `community-handoff-workflow` is print-only, so it can remain before the
  standalone local commands as an overview.
- Adding `community-candidates-dir` to the README handoff sample expands the
  visible local validation sequence, but it matches the canonical workflow and
  does not change behavior.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_handoff_check_dir_docs_are_linked_and_bounded tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_community_handoff_workflow.py::test_build_community_handoff_workflow_returns_deterministic_steps tests/test_community_signal_profile.py::test_profile_recommended_commands_keep_directory_handoff_sequence tests/test_external_tool_adapters.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
```
