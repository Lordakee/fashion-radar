# Stage 109 Source Boundaries Quality Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a section-scoped docs drift guard for source-boundary quality
wording.

**Architecture:** Append one pytest test to `tests/test_source_boundaries_docs.py`
that reuses the existing helpers, extracts `docs/source-boundaries.md`
`## Quality Boundaries`, normalizes whitespace/case, and asserts public
quality-boundary phrases. Keep this stage docs-test-only and avoid README,
runtime, dashboard/report behavior, collectors, source acquisition, connector,
social/platform scraping, compliance, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md`
  records the Stage 109 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-109-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-109-plan-review.md` records the local
  plan review.
- Modify: `tests/test_source_boundaries_docs.py` appends the quality boundaries
  docs drift guard.
- Create: `docs/reviews/opencode-stage-109-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-109-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-109-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 109 Plan Review Prompt

Review the Stage 109 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Quality Boundaries` section, so quality-boundary guidance
remains explicit about heat scores being local metrics, candidate signals
needing review rather than validation, and the dashboard showing a small set of
local diagnostic fields.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## Quality Boundaries`
and assert:

- `Heat scores are local metrics based on configured sources and imported local signals.`
- `They are not rankings outside that local source set.`
- `Candidate signals are observed phrases from configured sources and imported local signals and need review.`
- `They should not be presented as validated entities.`
- `The dashboard should show:`
- `Source count.`
- `Representative links.`
- `Time window.`
- `Failed source runs.`
- `Missing data warnings.`
- `Whether a source is core, opt-in, or experimental.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 109 review artifacts

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
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime scoring checks, candidate validation
logic, dashboard/report behavior, README parity checks, source collection,
platform search, social monitoring, schema migrations, connector behavior, or
compliance features.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Quality Boundaries
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Quality Boundaries`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with scoring, candidate discovery, dashboard,
   report behavior, package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-109-plan-review-prompt.md)" > docs/reviews/opencode-stage-109-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-109-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Append this test to `tests/test_source_boundaries_docs.py`:

```python
def test_source_boundaries_docs_keep_quality_boundary() -> None:
    quality_boundaries = _section(
        _read_source_boundaries_doc(),
        "Quality Boundaries",
    )
    normalized = _normalized(quality_boundaries)

    for phrase in (
        "Heat scores are local metrics based on configured sources and imported local signals.",
        "They are not rankings outside that local source set.",
        "Candidate signals are observed phrases from configured sources and imported "
        "local signals and need review.",
        "They should not be presented as validated entities.",
        "The dashboard should show:",
        "Source count.",
        "Representative links.",
        "Time window.",
        "Failed source runs.",
        "Missing data warnings.",
        "Whether a source is core, opt-in, or experimental.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
```

Expected: pass.

- [ ] Run adjacent source/quality-boundary docs/reference tests:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_dashboard_docs.py tests/test_reports.py tests/test_cli_docs.py -q
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

- [ ] Create `docs/reviews/opencode-stage-109-code-review-prompt.md` with this
      review request:

```markdown
# Stage 109 Code Review Prompt

Review the Stage 109 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 109 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Quality Boundaries` section in `docs/source-boundaries.md`. It
asserts that quality-boundary guidance remains explicit about heat scores being
local metrics, candidate signals needing review rather than validation, and the
dashboard showing a small set of local diagnostic fields.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md`
- `docs/reviews/opencode-stage-109-plan-review-prompt.md`
- `docs/reviews/opencode-stage-109-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 109 review artifacts

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
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_dashboard_docs.py tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 109 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## Quality Boundaries` section?
3. Is appending to `tests/test_source_boundaries_docs.py` clean and consistent
   with the existing helper pattern?
4. Is the new guard independent from scoring, candidate discovery, dashboard,
   report behavior, package archive checks, and runtime code?
5. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-109-code-review-prompt.md)" > docs/reviews/opencode-stage-109-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-109-code-review.md`.
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

- [ ] Stage only Stage 109 files:

```bash
git add \
  docs/reviews/opencode-stage-109-code-review-prompt.md \
  docs/reviews/opencode-stage-109-code-review.md \
  docs/reviews/opencode-stage-109-plan-review-prompt.md \
  docs/reviews/opencode-stage-109-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md \
  docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md \
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
git commit -m "Guard source quality boundary docs"
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
