# Stage 78 Code Review Prompt

You are reviewing Stage 78 of `fashion-radar`.

Repository: `/home/ubuntu/fashion-radar`

## Goal

Review the current uncommitted Stage 78 implementation before commit. This
stage adds a test/docs-only adapter contract parity gate for the external and
community tool handoff surfaces.

## In Scope

- `tests/test_external_tool_contract_parity.py`
- `tests/test_cli_docs.py`
- `docs/community-signal-import.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-18-stage-78-adapter-contract-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md`
- `docs/reviews/opencode-stage-78-plan-review-prompt.md`
- `docs/reviews/opencode-stage-78-plan-review.md`
- `docs/reviews/opencode-stage-78-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-78-plan-rereview.md`
- `docs/reviews/opencode-stage-78-code-review-prompt.md`
- `docs/reviews/opencode-stage-78-code-review.md`

## Out Of Scope

- `uv.lock` is locally dirty from a pre-existing mirror URL rewrite and must not
  be staged as part of Stage 78.
- No runtime `src/` changes should be required.
- Do not require scraping, crawling, browser automation, platform APIs, login,
  sessions, cookies, tokens, proxies, media downloads, monitoring, scheduling,
  source acquisition, demand proof, ranking, platform coverage verification, or
  compliance-review product features.

## Acceptance Criteria

- Parity tests use public builders/renderers only.
- All seven built-in adapters are covered.
- Adapter field mappings match `community-signal-profile` allowed and required
  fields.
- Template model metadata and command guidance mirror the adapter registry.
- Rendered template JSON and CSV rows lint cleanly for every adapter and remain
  importable rows only.
- Workflow/readiness shared steps reuse adapter recommended commands.
- Dry-run import guidance stays separate from real import guidance.
- Generated Fashion Radar command guidance does not contain unsupported
  acquisition/platform-operation command tokens.
- Docs describe the parity gate as local contract protection only.
- `src/`, dependency manifests, and public `uv.lock` are not changed by this
  stage.

## Prior Verification

The controller ran:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py tests/test_cli_docs.py::test_community_signal_import_docs_describe_external_tool_contract_parity -q
uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py tests/test_cli_docs.py
git diff --check
```

Please inspect the current worktree and report Critical, Important, and Minor
findings with file/line references. If there are no Critical or Important
findings, say so clearly.
