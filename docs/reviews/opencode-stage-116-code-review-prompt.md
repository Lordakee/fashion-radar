# Stage 116 Code Review Prompt

Review the Stage 116 changes in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `tests/test_community_tool_handoff_directory_examples.py`
- `tests/test_cli_docs.py`
- `examples/community-tool-handoff-directory.example/README.md`
- `docs/community-signal-import.md`
- `docs/superpowers/specs/2026-06-19-stage-116-directory-readiness-samples-design.md`
- `docs/superpowers/plans/2026-06-19-stage-116-directory-readiness-samples-plan.md`
- `docs/reviews/opencode-stage-116-plan-review-prompt.md`
- `docs/reviews/opencode-stage-116-plan-review.md`

## Intended Goal

Connect the checked-in external community tool directory examples to existing
`external-tool-readiness` and `external-tool-workflow` local preflight guidance
for both CSV and JSON directories, without runtime behavior changes.

## Actual Changes

- Added a parametrized test proving both checked-in CSV and JSON directory
  examples can build `external-tool-readiness` and `external-tool-workflow`
  payloads with `generic_community_export` overrides.
- Added docs drift coverage that parses bash command blocks with `shlex.split`
  and asserts the example README and the `## External Tool Export Directory
  Examples` section include readiness/workflow commands for both directories.
  The assertions require each command flag exactly once and require the scoped
  readiness/workflow command set to be exactly the four expected CSV/JSON
  preflight commands.
- Added optional preflight commands to
  `examples/community-tool-handoff-directory.example/README.md`.
- Expanded `docs/community-signal-import.md` directory examples so readiness and
  workflow preflight commands appear before lint/import dry-run commands.
- Added Stage 116 design, plan, and plan review artifacts.

## Scope Constraints

Allowed Stage 116 changes:

- Tests and docs listed above
- Stage 116 review artifacts

Disallowed Stage 116 changes:

- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- collectors
- source packs
- entity packs
- dashboard
- import behavior
- scoring
- reports

Do not propose adding source collection, collectors, manual import behavior,
external tool runtime behavior, connectors, source acquisition, platform
coverage, demand proof, ranking, scraping, browser automation, platform APIs,
account/cookie handling, scheduling, monitoring, schema changes, dependency
changes, CI changes, new linter restrictions, or compliance-review product
features.

## Verification Already Run

RED:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_community_tool_handoff_directory_examples.py::test_directory_examples_build_external_tool_readiness_and_workflow_with_overrides tests/test_cli_docs.py::test_external_community_tool_directory_example_docs_are_linked_and_bounded -q
```

Result before docs changes: `1 failed, 2 passed`; failure was the missing
`external-tool-readiness` docs snippet.

GREEN focused:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_community_tool_handoff_directory_examples.py::test_directory_examples_build_external_tool_readiness_and_workflow_with_overrides tests/test_cli_docs.py::test_external_community_tool_directory_example_docs_are_linked_and_bounded -q
```

Result: `3 passed`.

Adjacent:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_external_tool_readiness.py tests/test_external_tool_workflow.py tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py -q
```

Result: `100 passed`.

## Review Questions

1. Do the tests correctly cover the checked-in CSV and JSON directory examples,
   including the JSON override on the CSV-default `generic_community_export`
   adapter?
2. Are the docs snippets concrete and copyable while remaining local guidance
   only?
3. Does the change avoid runtime behavior changes and avoid adding collection,
   scraping, connectors, platform APIs, scheduling, monitoring, ranking, demand
   proof, coverage verification, or compliance-review product features?
4. Are the tests robust enough around shell quoting, command ordering, and
   section scoping?
5. Are there any Critical or Important blockers before running the full release
   gate and committing?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
