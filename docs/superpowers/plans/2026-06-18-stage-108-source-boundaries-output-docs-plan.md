# Stage 108 Source Boundaries Output Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a section-scoped docs drift guard for source-boundary output
wording.

**Architecture:** Append one pytest test to `tests/test_source_boundaries_docs.py`
that reuses the existing helpers, extracts `docs/source-boundaries.md`
`## Output Boundaries`, normalizes whitespace/case, and asserts output wording
phrases. Keep this stage docs-test-only and avoid README, runtime, report,
dashboard, collectors, robots/fetching, source acquisition, connector,
social/platform scraping, compliance, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md`
  records the Stage 108 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-108-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-108-plan-review.md` records the local
  plan review.
- Modify: `tests/test_source_boundaries_docs.py` appends the output boundaries
  docs drift guard.
- Create: `docs/reviews/opencode-stage-108-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-108-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-108-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 108 Plan Review Prompt

Review the Stage 108 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Output Boundaries` section, so report/dashboard wording guidance
remains explicit about describing signals rather than certainty, safe
local-observed wording examples, and avoiding market-wide or verified-demand
claims.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## Output Boundaries`
and assert:

- `Reports and dashboards should describe signals, not assert certainty.`
- `Preferred wording:`
- `Mention count increased in this configured source set`
- `Needs human review`
- `Signal changed within this configured local source set`
- `Imported row platform provenance label`
- `Stored local provenance label, not platform coverage`
- `Avoid wording that implies complete market truth:`
- `This source-set signal proves external demand`
- `This celebrity caused the trend`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 108 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- dashboard, report, collector, robots/fetching, storage schema, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime wording filters, README parity checks,
robots/fetching behavior, source collection, platform search, social monitoring,
market rankings, dashboard logic, report logic, schema migrations, connector
behavior, or compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Output Boundaries
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Output Boundaries`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with full negative-claim scanning, heat movers,
   trend deltas, scoring, candidate discovery, dashboard/report behavior,
   package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-108-plan-review-prompt.md)" > docs/reviews/opencode-stage-108-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-108-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Current tree note: `tests/test_source_boundaries_docs.py` already contains
      the Stage 108 `test_source_boundaries_docs_keep_output_boundary` body in
      the working tree. Do not append it a second time. Verify that the existing
      working-tree change matches the snippet below, then proceed with focused
      verification.

- [ ] Ensure `tests/test_source_boundaries_docs.py` contains exactly this new
      test body once:

```python
def test_source_boundaries_docs_keep_output_boundary() -> None:
    output_boundaries = _section(
        _read_source_boundaries_doc(),
        "Output Boundaries",
    )
    normalized = _normalized(output_boundaries)

    for phrase in (
        "Reports and dashboards should describe signals, not assert certainty.",
        "Preferred wording:",
        "Mention count increased in this configured source set",
        "Needs human review",
        "Signal changed within this configured local source set",
        "Imported row platform provenance label",
        "Stored local provenance label, not platform coverage",
        "Avoid wording that implies complete market truth:",
        "This source-set signal proves external demand",
        "This celebrity caused the trend",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
```

Expected: pass.

- [ ] Run adjacent source/output-boundary docs/reference tests:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_cli_docs.py tests/test_trend_deltas_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-108-code-review-prompt.md` with this
      review request:

```markdown
# Stage 108 Code Review Prompt

Review the Stage 108 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 108 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Output Boundaries` section in `docs/source-boundaries.md`. It
asserts that output wording guidance remains explicit about describing signals
rather than certainty, section-specific safe wording examples, and avoiding
explicit demand-proof or celebrity-causation claims.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md`
- `docs/reviews/opencode-stage-108-plan-review-prompt.md`
- `docs/reviews/opencode-stage-108-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 108 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- dashboard, report, collector, robots/fetching, storage schema, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_cli_docs.py tests/test_trend_deltas_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 108 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## Output Boundaries` section?
3. Is appending to `tests/test_source_boundaries_docs.py` clean and consistent
   with the existing helper pattern?
4. Is the new guard independent from full negative-claim scanning, heat movers,
   trend deltas, scoring, candidate discovery, dashboard/report behavior,
   package archive checks, and runtime code?
5. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-108-code-review-prompt.md)" > docs/reviews/opencode-stage-108-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-108-code-review.md`.
- [ ] Fix any Critical or Important findings before Task 4.

## Task 4: Full Verification, Commit, Push

- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] Stage only Stage 108 files:

```bash
git add \
  docs/reviews/opencode-stage-108-code-review-prompt.md \
  docs/reviews/opencode-stage-108-code-review.md \
  docs/reviews/opencode-stage-108-plan-review-prompt.md \
  docs/reviews/opencode-stage-108-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md \
  docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md \
  tests/test_source_boundaries_docs.py
```

- [ ] Run staged checks:

```bash
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit:

```bash
git commit -m "Guard source output boundary docs"
```

- [ ] Push using a temporary git extraheader only; do not persist credentials in
      remote URLs or git config.
- [ ] Verify `git config --get-all http.https://github.com/.extraheader || true`
      is empty and `git remote -v` contains no token.
- [ ] Verify the GitHub Actions run for the pushed commit completes with
      `success`.

## Task 5: Handoff Summary

- [ ] Write a concise Handoff Summary with:
  - repo status
  - commit SHA and CI URL
  - verified commands
  - uncommitted files
  - next step candidates
