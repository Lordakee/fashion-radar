I'll review the Stage 90 implementation. Let me start by gathering the relevant files and checking the actual changes.
All changes are new untracked files - scope is clean. Let me read the core implementation and review artifacts in parallel.
Now let me read the actual `docs/daily-digest.md` and the related test files to verify assertions and independence.
All 18 phrases verified against `docs/daily-digest.md`. Let me check the remaining review artifacts and run the verification commands.
All verification passes. Let me check the existing code review output file to avoid clobbering, then check for any existing `*_docs.py` test naming conventions.
All checks pass. The current content of `opencode-stage-90-code-review.md` is streaming narration from this very run — my final response is the review that should land there. Here is the review.

---

# Stage 90 Code Review

## Verdict

**No Critical or Important blockers.** The implementation matches the Stage 90 plan and scope, is independent from runtime and broad CLI docs tests, and is safe for final verification, commit, and push.

## Findings (ordered by severity)

### Critical
None.

### Important
None.

### Minor / Informational

1. **Section split raises on heading rename (acceptable, intended).** `tests/test_daily_digest_docs.py:48` uses `text.split("## Review Boundary", 1)[1]`, which will raise `IndexError` if a future stage renames the `## Review Boundary` heading at `docs/daily-digest.md:118`. This is the desired hard red signal for a boundary guard (a silent skip would defeat the purpose). The plan review already flagged this as acceptable. No change needed.

2. **Helper duplication is intentional.** `_normalized()` at `tests/test_daily_digest_docs.py:13-14` and the `text.split(heading, 1)[1]` section pattern duplicate conventions already present in `tests/test_cli_docs.py:313-318` (`_normalized_doc_text`/`_normalized_text`) and `tests/test_cli_docs.py:389-406` (`_markdown_section*`). The new module must not import from another test module, so local duplication is correct. No change needed.

3. **Short boundary tokens (low risk, acceptable).** Shortest asserted phrases (`"open sqlite"`, `"send email"`, `"call webhooks"`, `"review aids"`) are anchored to a single enumeration sentence at `docs/daily-digest.md:8-10` and the Review Boundary paragraph at `docs/daily-digest.md:120-122`. They are drift detectors tied to specific boundary statements, not broad claims; adding more context would make them brittle to benign copy-edits. Same trade-off the plan review accepted. No change needed.

4. **Reviewer-runner divergence is pre-existing, project-wide.** Plan Task 3 invokes `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`, while `AGENTS.md` prescribes `claude --effort max --permission-mode plan`. This is the same carry-forward already documented for Stage 89 and is not introduced by Stage 90. Not a blocker.

## Review Question Answers

**1. Does the implementation match the Stage 90 plan and scope?**
Yes. `tests/test_daily_digest_docs.py` is byte-for-byte identical to the Task 2 code block in `docs/superpowers/plans/2026-06-18-stage-90-daily-digest-docs-boundary-plan.md:41-100` (module docstring-free, three test functions, `_normalized`/`_read_daily_digest_doc` helpers, `ROOT`/`DAILY_DIGEST_DOC` constants). Scope is test-only: the only non-review artifact is the new test file. No changes to `docs/daily-digest.md`, `src/`, schemas, dependency manifests, `uv.lock`, CI workflows, `tests/test_cli_docs.py`, `tests/test_digests.py`, or review-protocol docs/tests (confirmed via `git status --porcelain` — all changes are new untracked files in allowed paths). Boundaries section of the spec (`docs/superpowers/specs/2026-06-18-stage-90-daily-digest-docs-boundary-design.md:56-61`) is honored: no digest/network/email/webhook/browser/scheduling/source-acquisition/coverage/demand/ranking/scraping/connector/platform-API/schema-enum/linter/compliance behavior added.

**2. Are the docs assertions present, stable enough, and limited to local digest boundaries?**
Yes. All 18 phrases verified present via the same normalized casefolded substring match the test uses:
- Test 1 (8/8) — `docs/daily-digest.md:8-10,115`
- Test 2 (5/5) — `docs/daily-digest.md:50,62,125-126`
- Test 3 (5/5, scoped to post-`## Review Boundary` text) — `docs/daily-digest.md:118-122`

Each phrase is anchored to a specific local-file / manual-review / source-set statement; none make or imply demand-proof, coverage, or ranking claims. The section-scoped split in Test 3 correctly prevents the boundary phrases from matching unrelated drift elsewhere in the file.

**3. Is the new standalone test independent from runtime digest behavior tests and broad CLI docs tests?**
Yes.
- `tests/test_daily_digest_docs.py` imports only `pathlib`. It does not import `fashion_radar.*`, has no `conftest.py`/fixture dependency, and never executes digest code — fully disjoint from `tests/test_digests.py` (which exercises `fashion_radar.digests` runtime behavior).
- `tests/test_cli_docs.py:52` references `docs/daily-digest.md` only inside the generic `PATH_CONSISTENCY_DOCS` existence list; there is no phrase overlap with the new assertions.
- The `test_*_docs.py` filename convention is already established by `tests/test_review_protocol_docs.py` (Stage 89), so the new module follows repo convention without colliding.
- Focused + combined verification both pass: 3/3 new, 12/12 combined (`tests/test_digests.py` 9 + new 3). Ruff check, Ruff format check, and `git diff --check` all clean.

**4. Are there any Critical or Important issues that must be fixed before final verification, commit, and push?**
No. Proceed to Task 4 (full verification, commit, push). Recommended staging set for the commit:
- `tests/test_daily_digest_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-90-daily-digest-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-90-daily-digest-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-90-plan-review-prompt.md`
- `docs/reviews/opencode-stage-90-plan-review.md`
- `docs/reviews/opencode-stage-90-code-review-prompt.md`
- `docs/reviews/opencode-stage-90-code-review.md`
