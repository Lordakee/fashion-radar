# Stage 159 Review Artifact Hygiene Gate Design

## Objective

Add an automated release-hygiene guard that rejects malformed local review
capture artifacts created for Stage 159 and later.

## Current Gap

`docs/REVIEW_PROTOCOL.md` and `AGENTS.md` already require completed opencode
review records to contain one coherent review body and no live-capture stubs,
tool-status messages, ANSI escape output, duplicated/truncated text, or empty
output. That rule is currently enforced manually before each commit.

Stage 158 required manual cleanup of opencode output before commit. A small
automated guard in `scripts/check_release_hygiene.py` will catch the most common
capture mistakes before upload.

## Scope

In scope:

- Extend `scripts/check_release_hygiene.py` to scan Stage 159 and newer completed
  opencode review output files under `docs/reviews/`.
- Check both tracked and untracked review output files.
- Ignore review prompt files.
- Ignore historical Stage 158 and older review records so legacy capture
  artifacts do not block the current release.
- Reject only low-false-positive capture hygiene markers:
  - empty review output;
  - ANSI escape/control output;
  - tool-status lines such as `Wrote ...`, `Review written to ...`, and
    `Review complete ...`;
  - opencode UI marker lines where the stripped line starts with rendered
    arrow/star status glyphs or `build middle-dot` status text;
  - process chatter at the first nonblank line such as `I'll ...`,
    `I will ...`, or `Let me ...`.

Out of scope:

- No product/runtime feature changes.
- No social platform connectors, scraping, browser automation, platform APIs,
  login/cookie/token behavior, monitoring, scheduling, source acquisition,
  demand proof, ranking, coverage verification, or compliance-review product
  features.
- No historical rewrite of existing review records.
- No broad natural-language validation of review quality, verdict correctness,
  or duplicate approval semantics.
- No optional Claude Code review artifact scanning in this stage; the active
  review engine is local opencode.
- No changes to package metadata, lockfiles, collectors, CLI commands, reports,
  dashboards, or external/community handoff behavior.

## Architecture

Reuse the existing release-hygiene script because it already scans tracked and
untracked repository files before GitHub upload.

Add a narrow review-artifact pass to `collect_findings(...)`:

```text
find_review_capture_hygiene_findings(repo_root, tracked_paths, "tracked")
find_review_capture_hygiene_findings(repo_root, untracked_paths, "untracked")
```

Only paths matching completed review output names are scanned:

```text
docs/reviews/opencode-stage-N-plan-review.md
docs/reviews/opencode-stage-N-code-review.md
docs/reviews/opencode-stage-N-release-review.md
docs/reviews/opencode-stage-N-plan-rereview.md
docs/reviews/opencode-stage-N-plan-rereview-2.md
docs/reviews/opencode-stage-N-code-rereview.md
docs/reviews/opencode-stage-N-code-rereview-2.md
docs/reviews/opencode-stage-N-release-rereview.md
docs/reviews/opencode-stage-N-release-rereview-2.md
```

The initial enforcement floor is Stage 159. The floor keeps the new rule useful
for all future work while avoiding churn from historical review records that were
created before the automated guard existed.

## Tech Stack

- Python standard library only.
- Existing `scripts/check_release_hygiene.py`.
- Existing pytest module `tests/test_release_hygiene.py`.
- Local opencode plan/code review with
  `zhipuai-coding-plan/glm-5.2 --variant max`.
- `uv --no-config run --frozen` for tests and lint.

## Implementation Method

Use test-first changes:

1. Add failing tests in `tests/test_release_hygiene.py` for Stage 159 review
   artifacts with tool-status lines, ANSI output, process chatter, prompt-file
   exclusion, and legacy Stage 158 exclusion.
2. Run the focused tests and verify RED failures.
3. Implement the minimal scanner and helper functions in
   `scripts/check_release_hygiene.py`.
4. Run focused tests, the full release-hygiene test module, local opencode code
   review, and the full release gate.

## Expected Behavior

This should fail:

```text
docs/reviews/opencode-stage-159-code-review.md
Wrote docs/reviews/opencode-stage-159-code-review.md
```

This should pass:

```text
docs/reviews/opencode-stage-159-code-review-prompt.md
Wrote docs/reviews/opencode-stage-159-code-review.md
```

because prompt files intentionally contain review instructions and examples, not
completed reviewer output.

This should pass:

```text
docs/reviews/opencode-stage-158-code-review.md
Wrote docs/reviews/opencode-stage-158-code-review.md
```

because Stage 158 and older files are historical records outside the enforcement
floor.

## Risks

- Overly broad textual checks could reject legitimate review analysis. The first
  version should target line-level capture artifacts and first-line process
  chatter, not arbitrary occurrences inside quoted examples. Ordinary review
  prose like `pytest -q -> passed` must remain allowed.
- Historical review records contain mixed capture styles. Stage-floor gating
  prevents unrelated cleanup work from blocking this node.
- Future review engines may emit different status markers. The scanner can be
  extended later if new capture artifacts appear.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "review_artifact or review_capture"
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
