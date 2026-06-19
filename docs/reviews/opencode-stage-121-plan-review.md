# Stage 121 Plan Review

## Summary

The Stage 121 design and plan correctly hardening the Stage 120 Minor m-2 finding by replacing the two narrow literal-substring absence checks with a compiled regex guard. I verified the regex empirically against the 5 planned unsafe variants (all match), the safe temp-file-plus-copy workflow (no match), and all three `ACTIVE_REVIEW_DOCS` files currently in the repo (all safe / no match). The RED-GREEN TDD flow is sound, and the stage scope is strictly tests-only.

## Critical

None.

## Important

None.

## Minor

- **m-1 — Regex does not cover stderr-only or other file-descriptor redirections (`2>`, `n>`).** The alternation `(?:&>>|&>|1>>|1>|>>|>)` covers stdout (`>`, `>>`), stdout fd 1 (`1>`, `1>>`), and combined stdout+stderr (`&>`, `&>>`), but not `2>` alone. This is acceptable for a drift guard since `2>` would not capture review stdout, and the active workflow never uses it. Noting as a known gap.

- **m-2 — Regex does not catch pipe-based direct writes (`| tee docs/reviews/...`).** This is a different pattern (pipe, not redirection) and was explicitly outside Stage 120 m-2's scope. The historical `docs/superpowers/plans/2026-06-17-stage-65-imported-entity-evidence-plan.md:1609` did use `| tee`, so a future copy-paste of that older pattern would slip through. Acceptable for this stage; could be a future hygiene pass.

- **m-3 — Minor re-read inefficiency in the replacement assertion.** The new `redirect_failures` loop re-reads `REVIEW_PROTOCOL` via `_read(path)` even though `protocol_text` is already read at the top of `test_review_protocol_docs_document_capture_hygiene`. Not a correctness issue, just a trivial redundancy.

## Review-Focus Answers

1. **Does the plan address only Stage 120 Minor m-2?** Yes. The design scopes itself exclusively to hardening the direct opencode final-file redirection guard. The out-of-scope list is exhaustive (no docs prose, runtime, dependency, `uv.lock`, CI, connector, scraping, scheduling, monitoring, source acquisition, ranking, coverage verification, or compliance/audit behavior). Only `tests/test_review_protocol_docs.py` is modified; the commit step stages only the test file plus review-process artifacts.

2. **Will the RED test fail before the helper exists and pass after?** Yes. Task 1 adds `test_direct_opencode_review_redirect_regex_catches_shell_variants` referencing `_direct_opencode_review_redirect` before it is defined. Python resolves the name at call time, so pytest reports `NameError: name '_direct_opencode_review_redirect' is not defined` (a valid RED state). After Task 2 adds the helper, I verified the regex returns a truthy `Match` for all 5 unsafe examples and `None` for the safe example, so the test goes GREEN.

3. **Does the regex catch common variants without flagging the safe workflow?** Yes. I executed the planned regex against the 5 unsafe examples (all match: no-space `>`, `>>`, `1>` with `"./..."`, `&>` with single quotes, and a backslash-newline continuation ending in `> docs/...`) and the safe `> "$tmp_review"` + `cp "$tmp_review" docs/reviews/...` block (no match). I also ran the regex against the actual `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and `docs/github-upload-checklist.md` — all three return no match, so the GREEN integration assertion holds. The regex correctly handles line-continuation escaping (`(?:\\\n[^\n]*)*`), operator ordering (`&>>` before `&>`, `1>>` before `1>`, `>>` before `>`), optional quotes, and `./` prefix.

4. **Is the stage tests-only?** Yes. Files modified: only `tests/test_review_protocol_docs.py`. No `src/`, no `pyproject.toml`, no `uv.lock`, no CI workflow changes. I confirmed the `import re` placement (`from __future__` → `import re` → `from pathlib import Path`) passes ruff isort (rule `I`) and format check. The commit step stages only the test file, review artifacts, and the design/plan docs.

5. **Are the verification commands sufficient?** Yes. The plan runs: focused RED test → focused GREEN test → adjacent docs tests (`test_review_protocol_docs.py` + `test_cli_docs.py`) → ruff check/format on the changed file → local opencode code review → full release gate (`check_release_hygiene.py`, full `pytest`, ruff check/format, `uv lock --check`, mirror-URL scan, `git diff --exit-code -- uv.lock pyproject.toml`, `git diff --check`). This is comprehensive for a tests-only hardening node.

## Final Statement

**There are no Critical or Important blockers before implementation.** The design and plan faithfully address Stage 120 Minor m-2, the regex is empirically correct against both unsafe variants and the safe workflow (including the actual repo docs), the RED-GREEN flow is valid, and the stage remains strictly tests-only. The three Minor findings are non-blocking known limitations appropriate for a drift guard.
