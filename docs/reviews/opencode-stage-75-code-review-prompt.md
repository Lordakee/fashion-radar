# Stage 75 Code Review Prompt

Review the current Stage 75 implementation in `/home/ubuntu/fashion-radar`.

Use a code-review stance. Lead with Critical or Important findings if present;
include Minor notes after. Do not propose adding scraping, connectors, browser
automation, platform APIs, login/cookie/session/token/proxy behavior, CAPTCHA
handling, media download, monitoring/scheduling, source acquisition, demand
proof, ranking, coverage verification, or compliance-review product behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Stage 75 documents the complete external-tool adapter matrix in public docs,
documents that the automated first-run smoke validates the adapter registry
JSON contract from `external-tool-adapters --format json` across all seven
adapters, and guards both with CLI docs tests.

## Expected Scope

- `README.md`: complete adapter matrix plus first-run smoke registry-contract
  sentence.
- `docs/cli-reference.md`: complete adapter matrix.
- `docs/first-run.md`: first-run smoke registry-contract sentence.
- `CHANGELOG.md`: Stage 75 docs/test-only entry.
- `docs/reviews/opencode-stage-74-code-review.md`: correction note for stale M1
  wording about the Stage 74 plan-review artifact.
- `tests/test_cli_docs.py`: full-row matrix assertions for README and CLI
  reference, plus first-run smoke phrase assertions for README and first-run
  guide.
- Stage 75 design/plan/plan-review artifacts.

Runtime files, `scripts/`, dependency manifests, and lockfiles should be
unchanged.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q
# 3 passed

uv --no-config run --frozen pytest tests/test_cli_docs.py -q
# 43 passed

uv --no-config run --frozen ruff check tests/test_cli_docs.py
# All checks passed

uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
# 1 file already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed

git diff --check
# passed

uv --no-config run --frozen pytest
# 1100 passed
```

## Review Questions

1. Does the docs matrix match the current runtime adapter registry exactly?
2. Are the docs tests strong enough to catch missing/changed matrix rows and
   first-run smoke contract wording?
3. Is the Stage 74 correction note factually supported by the current
   Stage 74 plan-review artifact?
4. Is the changelog entry scoped correctly as docs/test-only?
5. Are runtime behavior, dependencies, and external-platform behavior unchanged?
6. Are there any Critical or Important issues to fix before commit?
