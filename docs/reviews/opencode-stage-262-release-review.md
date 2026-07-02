# opencode Stage 262 Release Review

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2 --variant max`) — fallback release reviewer
Stage: 262 (ROW ONE reader orientation)
Scope: uncommitted Stage 262 code, tests, docs, review/plan/spec artifacts, and release gates
Route: Claude Code primary release review timed out (`docs/reviews/claude-code-stage-262-release-review.md:1-7`); opencode fallback per `docs/REVIEW_PROTOCOL.md:90-101`.

## Verdict

**Accept with fixes.** The Stage 262 code, tests, docs, and review/spec/plan artifacts are coherent and release-ready. The only required fix is commit scoping: the plan's `git add` omits the opencode review records. Fix that one command and push.

## Critical Findings

None.

## Important Findings

1. **The plan's pre-push `git add` omits every opencode review artifact.** `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md:646` runs `git add docs/reviews/claude-code-stage-262-*.md ...` but never adds `docs/reviews/opencode-stage-262-*.md`. The current untracked set includes `opencode-stage-262-code-review.md`, `opencode-stage-262-code-review-prompt.md`, `opencode-stage-262-release-review-prompt.md`, and this fallback release review (`opencode-stage-262-release-review.md`). `docs/REVIEW_PROTOCOL.md:107-111` names the `opencode-stage-N-*-review.md` set as part of the active review record convention, so following the plan literally would commit an incomplete review trail. **Fix:** add `docs/reviews/opencode-stage-262-*.md` to the `git add` before commit.

## Minor Findings

1. **Primary release-review slot is an honest timeout notice, not a completed body.** `docs/reviews/claude-code-stage-262-release-review.md:3-6` records the Claude Code timeout and routes to the opencode fallback. It does not present approval, so it does not trip the review-capture hygiene rule in `docs/REVIEW_PROTOCOL.md:134-139` or the timeout-stub detector in `scripts/check_release_hygiene.py:106-110,446-453` (which scans only `opencode-*` artifacts). The fallback (this review) carries the substantive verdict. Defensible and gate-clean; flagged only for transparency.

2. **Locale-sensitive English date assertion retained.** `tests/test_row_one_render.py:138` asserts `"Jul 02, 2026"`; `_published_label` at `src/fashion_radar/row_one/templates.py:492` uses `strftime("%b %d, %Y")`, which is `LC_TIME`-dependent. The locale-stable `"2026-07-02"` check (`tests/test_row_one_render.py:139`) guards the date, and CI is English-locale, so this is acceptable. Already noted as a minor in `docs/reviews/opencode-stage-262-code-review.md:38-41`.

3. **Fixed 5-column edition-nav grid.** `src/fashion_radar/row_one/templates.py:217` hard-codes `repeat(5, minmax(0, 1fr))`. With fewer configured sections the row has empty visual space; with more than five it would wrap. Not a correctness issue and matches the plan; the mobile rule at `templates.py:354` collapses to one column. Already noted in `docs/reviews/opencode-stage-262-code-review.md:48-50`.

4. **Safe-evidence count deviates from the plan sketch, deliberately.** The plan (`...plan.md:404`) sketched `evidence_count = len(story.evidence)`; the shipped code at `src/fashion_radar/row_one/templates.py:463` counts only links whose URL passes `_safe_external_url`, so unsafe `javascript:` evidence is not reported as a reader-facing count. This is covered by `tests/test_row_one_render.py:140-141` (fixture has one safe + one unsafe link → "1 evidence link") and was accepted by the opencode code review. No action; recorded for traceability.

## Notes

- **Boundary discipline is clean.** The diff is limited to `docs/row-one.md`, `src/fashion_radar/row_one/templates.py`, and three ROW ONE test files. No change to `models.py`, `render.py`, `edition.py`, `cli.py`, or the `data/edition.json` contract. No collection, scraping, platform APIs, login/cookie behavior, translation, LLM, image, paid-API, deployment, demand-proof, coverage-verification, compliance, `external-tool-*`, `community-handoff-*`, `imported-*`, or `heat-movers` surface is touched. Consistent with `AGENTS.md` and the presentation-only ROW ONE boundary in `docs/row-one.md:27-39,53-62`.
- **All plan-final-review required fixes are shipped:** nav count assertions scoped to `nav_html` (`tests/test_row_one_render.py:187-192`); detail back-link assertions placed in the escapes/unsafe-links test (`tests/test_row_one_render.py:146-148`); packaging smoke checks added to the pre-push gate (present in `docs/reviews/claude-code-stage-262-release-review-prompt.md:52-57` and the run results); `index_html` binding added (`tests/test_row_one_cli.py` diff). The optional ordering assertion was also added (`tests/test_row_one_render.py:179`).
- **Fresh read-only verification this run:** `scripts/check_release_hygiene.py --repo-root .` → "Release hygiene checks passed." (re-run by me, not just trusted). No secrets, cookies, tokens, `.env`, generated reports, SQLite/sidecar DBs, CodeGraph DB files, or build artifacts are tracked or untracked; `git ls-files --others --exclude-standard` shows only `docs/` artifacts.
- **Gate completeness.** The pre-push gate in `docs/reviews/claude-code-stage-262-release-review-prompt.md:43-58` and the reported run cover lock check, frozen sync, `git diff --check`, `ruff check`, `ruff format --check`, full `pytest` (1685 passed), `uv build`, `check_package_archives.py`, `check_first_run_smoke.py`, and `check_release_hygiene.py`. These are appropriate and complete for a presentation-only change to packaged source.
- **Review-record coherence.** `claude-code-stage-262-plan-review.md`, `-plan-rereview.md`, `-plan-final-review.md`, and `opencode-stage-262-code-review.md` are complete coherent bodies with single verdicts, no tool-status lines, no ANSI, no duplicated drafts, no empty output. `scripts/check_release_hygiene.py:417-485` review-capture hygiene does not flag any Stage 262 artifact.

## Push Acceptability

**Stage 262 is acceptable to push to `origin/main`** after the one commit-scoping fix in Important Finding 1: ensure the commit includes `docs/reviews/opencode-stage-262-*.md` (code review + this release review + their prompts) alongside the `claude-code-stage-262-*.md` records. No code, test, or doc change is required.
