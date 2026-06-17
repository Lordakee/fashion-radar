# Stage 71 Code Review Prompt

Review the Stage 71 implementation in `/home/ubuntu/fashion-radar`.

Use model judgment for a code-review stance. Lead with Critical or Important
findings only if they are real blockers or material quality issues. Minor notes
are acceptable after that. Do not propose adding scraping, connectors, browser
automation, platform APIs, login/cookie/session/token/proxy/CAPTCHA behavior,
media download, monitoring/scheduling, source acquisition, demand proof,
ranking, coverage verification, or compliance-review product behavior.

## Goal

Add a docs drift guard for the documented relationship between
`external-tool-adapters` and `external-tool-readiness`.

`external-tool-adapters` remains print-only. It may document
`external-tool-readiness` as an optional local read-only preflight command, but
adapter docs must not imply that `external-tool-adapters` itself runs readiness
or performs PATH lookup.

## Changed Files

- `tests/test_cli_docs.py`
- `docs/superpowers/specs/2026-06-17-stage-71-adapter-readiness-docs-guard-design.md`
- `docs/superpowers/plans/2026-06-17-stage-71-adapter-readiness-docs-guard-plan.md`
- `docs/reviews/opencode-stage-71-plan-review-prompt.md`
- `docs/reviews/opencode-stage-71-plan-review.md`
- `docs/reviews/opencode-stage-71-code-review-prompt.md`

## Implementation Summary

The implementation extends the existing
`test_external_tool_adapter_registry_docs_are_linked_and_bounded` test with a
small readiness-preflight phrase set:

- `external-tool-readiness`
- `optional local read-only preflight command`
- `itself remains print-only`
- `does not run readiness or perform PATH lookup`

The new assertions run inside the existing loop over the public adapter docs.
No runtime code was changed.

The Stage 71 spec and plan were adjusted from an earlier separate-test design
to this smaller in-test guard after read-only audits pointed out that reusing
the existing docs loop reduces duplicate constants and coverage overlap. A
previous code-review pass found only minor artifact nits; the spec variable
name and plan code fence were corrected before this final review.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded -q
# 1 passed in 0.37s before changes

uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded -q
# 1 passed in 0.48s after changes

uv --no-config run --frozen pytest tests/test_cli_docs.py -k "external_tool_adapter_registry_docs_are_linked_and_bounded or external_tool_template_docs_are_linked_and_bounded or external_tool_readiness_docs_are_linked_and_bounded or external_tool_readiness_upload_checklist_help_loop_and_smoke" -q
# 4 passed, 39 deselected in 0.51s

uv --no-config run --frozen pytest tests/test_cli_docs.py -q
# 43 passed in 0.73s

uv --no-config run --frozen ruff check tests/test_cli_docs.py
# All checks passed!

uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
# 1 file already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed.

git diff --check
# passed

uv --no-config run --frozen pytest
# 1099 passed in 29.03s after minor artifact fixes
```

## Review Questions

1. Does the test guard the intended adapter/readiness docs boundary without
   overreaching into runtime behavior?
2. Are the Stage 71 spec and plan consistent with the final implementation?
3. Are there any Critical or Important issues that must be fixed before commit?
