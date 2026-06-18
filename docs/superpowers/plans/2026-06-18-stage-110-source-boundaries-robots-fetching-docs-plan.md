# Stage 110 Source Boundaries Robots Fetching Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a section-scoped docs drift guard for source-boundary robots and
fetching wording.

**Architecture:** Append one pytest test to `tests/test_source_boundaries_docs.py`
that reuses the existing helpers, extracts `docs/source-boundaries.md`
`## Robots And Fetching`, normalizes whitespace/case, and asserts public
robots/fetching boundary phrases. Keep this stage docs-test-only and avoid
README, runtime collectors, HTTP policy, robots parser behavior, source
acquisition, connector, social/platform scraping, compliance, dependency, and CI
changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md`
  records the Stage 110 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-110-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-110-plan-review.md` records the local
  plan review.
- Modify: `tests/test_source_boundaries_docs.py` appends the robots/fetching
  docs drift guard.
- Create: `docs/reviews/opencode-stage-110-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-110-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-110-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 110 Plan Review Prompt

Review the Stage 110 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a section-scoped docs drift guard for `docs/source-boundaries.md`, scoped
only to the `## Robots And Fetching` section, so robots/fetching guidance
remains explicit about robots.txt checks before article extraction, skipped URL
reasons, source-specific rate limits, and GDELT metadata/link storage and
backoff boundaries.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md`
- `docs/source-boundaries.md`
- `tests/test_source_boundaries_docs.py`
- `tests/test_collectors_robots.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_source_boundaries_docs.py`. It will extract `## Robots And Fetching`
and assert:

- `Before fetching an article page for extraction, collectors must check robots.txt.`
- `Default fetch behavior:`
- `Use source-specific rate limits where configured.`
- `Record skipped URLs with reasons.`
- `GDELT fetch behavior:`
- `Use bounded exponential backoff.`
- `Store GDELT-provided metadata and links, not republished article bodies.`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 110 review artifacts

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
- `tests/test_collectors_robots.py`
- `tests/test_cli_docs.py`
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- HTTP client behavior, robots parser behavior, article extraction behavior,
  GDELT runtime behavior, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into runtime collector tests, HTTP/robots policy
changes, GDELT fetching behavior, source collection, platform search, social
monitoring, schema migrations, connector behavior, or compliance features.

This stage intentionally does not freeze the numeric GDELT throttling sentence
(`near 1 request per second`) and avoids generic fetch-policy bullets already
covered more directly by runtime collector tests.

## Review Questions

1. Does the plan protect a real `docs/source-boundaries.md` Robots And Fetching
   section without changing product behavior or docs text?
2. Are the planned phrases present in `docs/source-boundaries.md` and scoped
   narrowly enough to `## Robots And Fetching`?
3. Does appending to `tests/test_source_boundaries_docs.py` fit the existing
   source-boundaries docs test pattern?
4. Does the plan avoid overlap with collector runtime tests, HTTP/robots policy,
   GDELT fetching behavior, package archive checks, and runtime code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-110-plan-review-prompt.md)" > docs/reviews/opencode-stage-110-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-110-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Append this test to `tests/test_source_boundaries_docs.py`:

```python
def test_source_boundaries_docs_keep_robots_and_fetching_boundary() -> None:
    robots_fetching = _section(
        _read_source_boundaries_doc(),
        "Robots And Fetching",
    )
    normalized = _normalized(robots_fetching)

    for phrase in (
        "Before fetching an article page for extraction, collectors must check robots.txt.",
        "Default fetch behavior:",
        "Use source-specific rate limits where configured.",
        "Record skipped URLs with reasons.",
        "GDELT fetch behavior:",
        "Use bounded exponential backoff.",
        "Store GDELT-provided metadata and links, not republished article bodies.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
```

Expected: pass.

- [ ] Run adjacent docs/runtime-reference tests:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_collectors_robots.py tests/test_collectors_article.py tests/test_collectors_runner.py tests/test_project_brief_docs.py tests/test_cli_docs.py -q
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

- [ ] Create `docs/reviews/opencode-stage-110-code-review-prompt.md` with this
      review request:

```markdown
# Stage 110 Code Review Prompt

Review the Stage 110 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 110 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Robots And Fetching` section in `docs/source-boundaries.md`.
It asserts that robots/fetching guidance remains explicit about robots.txt
checks before article extraction, skipped URL reasons, source-specific rate
limits, and GDELT metadata/link storage and backoff boundaries.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md`
- `docs/reviews/opencode-stage-110-plan-review-prompt.md`
- `docs/reviews/opencode-stage-110-plan-review.md`
- `docs/reviews/opencode-stage-110-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 110 review artifacts

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
- `tests/test_collectors_robots.py`
- `tests/test_cli_docs.py`
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- HTTP client behavior, robots parser behavior, article extraction behavior,
  GDELT runtime behavior, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_collectors_robots.py tests/test_collectors_article.py tests/test_collectors_runner.py tests/test_project_brief_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 110 plan and remain scoped to a
   docs-only drift guard?
2. Are the asserted phrases appropriate for the `## Robots And Fetching`
   section, given existing overlap with collector runtime and HTTP/robots tests?
3. Does the implementation fit the existing `tests/test_source_boundaries_docs.py`
   pattern cleanly?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-110-code-review-prompt.md)" > docs/reviews/opencode-stage-110-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-110-code-review.md`.
- [ ] Fix any Critical or Important findings before Task 4.

## Task 4: Release Gate, Commit, Push, And CI

- [ ] Run the full release gate:

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

Expected: all pass.

- [ ] Stage only Stage 110 files:

```bash
git add tests/test_source_boundaries_docs.py \
  docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md \
  docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md \
  docs/reviews/opencode-stage-110-plan-review-prompt.md \
  docs/reviews/opencode-stage-110-plan-review.md \
  docs/reviews/opencode-stage-110-code-review-prompt.md \
  docs/reviews/opencode-stage-110-code-review.md
```

- [ ] Run staged checks:

```bash
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

Expected: all pass and no staged `uv.lock`.

- [ ] Commit:

```bash
git commit -m "Guard source robots fetching docs"
```

- [ ] Push to `origin main` using only temporary credentials.
- [ ] Verify no GitHub credential was persisted:

```bash
git config --get-all http.https://github.com/.extraheader || true
git remote -v | sed -E 's#(https://)[^/@]+@#\1***@#g'
```

- [ ] Verify GitHub Actions `CI` succeeds for the pushed SHA.

## Completion Criteria

- `tests/test_source_boundaries_docs.py` contains a section-scoped
  `## Robots And Fetching` docs guard.
- No runtime, docs-source, dependency, config, CI, connector, scraping, platform,
  or compliance feature files changed.
- Focused, adjacent, release-gate, staged, and GitHub Actions checks pass.
