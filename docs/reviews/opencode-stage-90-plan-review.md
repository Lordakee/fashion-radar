I have the four primary files. Let me check for overlap with existing docs tests and verify environment specifics before finalizing findings.
`test_cli_docs.py` already references `docs/daily-digest.md`. Let me inspect it for overlap, plus check the docs reviews directory and Stage 89/91/92 boundaries.
`test_cli_docs.py` only uses `docs/daily-digest.md` in a generic path-consistency list — no phrase overlap with the proposed test. Let me verify Stage 89 boundary and check existing standalone docs test conventions, plus do a final phrase-by-phrase validation.
All 18 proposed phrases verify present in current docs. Stage 89 has zero overlap. No `*_docs.py` collision. Here is the review.

---

# Stage 90 Plan Review

## Verdict

**No Critical or Important blockers.** The plan is safe to implement as written.

## Findings (ordered by severity)

### Critical
None.

### Important
None.

### Minor / Informational

1. **Short boundary tokens (low risk, acceptable).** Several asserted phrases are short substrings of a single enumeration sentence in `docs/daily-digest.md:9-10` — `"open sqlite"`, `"send email"`, `"call webhooks"`, `"open a browser"`, `"install a notification daemon"` — and `"review aids"` (`docs/daily-digest.md:121`), `"configured source set"` (`docs/daily-digest.md:120-122`), `"local observed signals"` (`docs/daily-digest.md:120`). These are drift detectors anchored to specific boundary statements, not broad claims. Adding more surrounding context would make them brittle to benign copy-edits; current specificity/sensitivity trade-off is reasonable. No change needed.

2. **Section split is exact-string dependent (acceptable).** `tests/test_daily_digest_docs.py` (plan lines 89) uses `text.split("## Review Boundary", 1)[1]`. The header exists verbatim at `docs/daily-digest.md:118`. If a future stage renames the heading the test will raise `IndexError` rather than fail softly. This is the desired red signal for a boundary guard, so it's fine.

3. **Review-runner divergence is pre-existing, not introduced here.** Plan Task 1/Task 3 invoke `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`, while `AGENTS.md` prescribes `claude --effort max --permission-mode plan`. This is the same explicit carry-forward already documented in `docs/superpowers/specs/2026-06-18-stage-89-review-protocol-code-record-design.md:50-55`. Not a Stage 90 blocker; tracked project-wide.

4. **Task 4 `git push` via temporary extraheader** (plan line 153) is the repo's established staged-push pattern. No scope concern, just noting it relies on a stored token in the local environment.

## Review Question Answers

**1. Are the proposed docs assertions present in current `docs/daily-digest.md`?**
Yes. All 18 phrases verified present via normalized casefolded substring match:
- Test 1 (8/8): `docs/daily-digest.md:8-10,115`
- Test 2 (5/5): `docs/daily-digest.md:50,62,125`
- Test 3 (5/5): `docs/daily-digest.md:118-122`

**2. Are the phrases stable enough and not overly broad?**
Yes. Each phrase is anchored to a specific local-file / manual-review / source-set statement. None are so broad that they could match unrelated drift (e.g., none assert single common words in isolation outside the bounded Review Boundary section). Shortest tokens (`send email`, `open sqlite`, `review aids`) are still tightly scoped to their host sentences.

**3. Is the scope safely test-only and independent from Stages 89, 91, and 92?**
Yes.
- Creates only `tests/test_daily_digest_docs.py` and review artifacts.
- Does not touch `docs/daily-digest.md`, `src/`, schemas, manifests, `uv.lock`, CI, `tests/test_cli_docs.py` (`docs/daily-digest.md` only appears there in the generic `PATH_CONSISTENCY_DOCS` list at `tests/test_cli_docs.py:52` — no phrase overlap), `tests/test_digests.py`, or review-protocol docs/tests.
- Stage 89 modifies `docs/REVIEW_PROTOCOL.md` + `tests/test_review_protocol_docs.py` — disjoint from digest docs.
- Stages 91/92 are not yet on disk; the plan has no forward dependency on them.

**4. Are the verification commands sufficient?**
Yes. Task 3 runs focused + combined pytest, ruff check, ruff format check, `git diff --check`. Task 4 adds full `check_release_hygiene.py`, full pytest, full ruff, `UV_NO_CONFIG=1 uv lock --check`, mirror-leak `rg` against `uv.lock`, `git diff --exit-code -- uv.lock pyproject.toml`, staged-hygiene re-run, and secret-pattern grep on staged content. Covers behavior, docs, lint/format, lock integrity, mirror hygiene, and secret hygiene.

**5. Are there any Critical or Important blockers before implementation?**
No. Proceed with Task 2 implementation.
