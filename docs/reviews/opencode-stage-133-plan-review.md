# Stage 133 Plan Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Test phrase anchoring is section-scoped, not link-scoped.**
   `tests/test_cli_docs.py` (proposed) asserts `_assert_markdown_link_to_path(...)`,
   `"github upload"`, and `"package smoke gate"` independently over the whole
   `Verification` section. A future edit could place the link on one line and the
   framing words elsewhere in the section and still pass. Not blocking — the
   section is small and the existing
   `test_pull_request_template_package_smoke_uses_temp_build_archive_checker`
   follows the same section-scoped style. If a tighter guard is wanted later,
   extract the bullet containing the link and assert the phrases on that line.

2. **Plan-review artifact creation is implicit.**
   The plan lists `docs/reviews/opencode-stage-133-plan-review-prompt.md` and
   `docs/reviews/opencode-stage-133-plan-review.md` under Files but no task step
   creates them. This matches prior stages that rely on
   `docs/REVIEW_PROTOCOL.md` for the plan-review handoff, so it is consistent,
   but worth noting for traceability.

3. **Token scan covers only classic PATs.**
   The release-gate check `rg -n 'ghp_[A-Za-z0-9]+' .` does not cover
   fine-grained `github_pat_` tokens. This is the established project-wide
   pattern, not a Stage 133 regression.

## Scope and design checks

1. **Routing gap addressed without duplication.** The design adds one concise
   pointer line to `.github/pull_request_template.md` and explicitly avoids
   copying `docs/github-upload-checklist.md` content. Confirmed by design
   lines 22-28 and plan Task 2 Step 1.

2. **RED test specificity.** The proposed test extracts the `Verification`
   section via `_markdown_section_exact_heading`, requires a markdown link to
   `docs/github-upload-checklist.md`, and ties the link to upload/package-smoke
   framing via `"github upload"` and `"package smoke gate"` substring checks
   (`tests/test_cli_docs.py:337`, `:439`). The current template at
   `.github/pull_request_template.md:48-63` contains neither phrase and no such
   link, so the test will fail RED as planned.

3. **No link-spelling overfit.** `_assert_markdown_link_to_path` uses
   `(?:\.\./)?{re.escape(path)}`, accepting both `docs/...` and
   `../docs/...`. The plan calls it positionally with
   `"docs/github-upload-checklist.md"`, matching the existing call style.

4. **Scope boundaries respected.** Touched files are limited to
   `.github/pull_request_template.md`, `tests/test_cli_docs.py`, and Stage 133
   review artifacts. No CI, upload-checklist content, package checker, runtime
   behavior, dependency, `uv.lock`, README/CONTRIBUTING, release-hygiene, or any
   connector/scraping/platform-API/monitoring/scheduling/source-acquisition/
   demand-proof/ranking/coverage-verification/compliance-auditing changes.

5. **Verification commands sufficient.** Focused verification (new test, the
   two related PR/CONTRIBUTING tests, `ruff check`/`format --check` on
   `tests/test_cli_docs.py`, live
   `scripts/check_release_hygiene.py --repo-root .`, `git diff --check`) plus
   the full release gate (full pytest, full ruff, `UV_NO_CONFIG=1 uv lock
   --check`, `git diff --exit-code -- uv.lock`, token/header scans) cover RED,
   GREEN, lint/format, hygiene, lockfile stability, and credential hygiene.

## Blocker statement
There are **no Critical or Important blockers** before implementation may
proceed.
