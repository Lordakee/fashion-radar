# Stage 103 Project Brief Non-Goals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone docs drift guard for MVP non-goal wording in the project brief.

**Architecture:** Create one pytest module that reads `docs/PROJECT_BRIEF.md`,
extracts the `## Non-Goals For MVP` section, normalizes whitespace/case, and
asserts MVP non-goal boundary phrases. Keep this stage docs-test-only and avoid
runtime connector, platform, scraping, scoring, dashboard, CLI, schema,
dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md`
  records the Stage 103 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-103-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-103-plan-review.md` records the local
  plan review.
- Create: `tests/test_project_brief_docs.py` contains the standalone docs drift
  guard.
- Create: `docs/reviews/opencode-stage-103-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-103-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-103-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 103 Plan Review Prompt

Review the Stage 103 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/PROJECT_BRIEF.md`, scoped only to
the `## Non-Goals For MVP` section, so the MVP remains documented as free-first,
local-first, deterministic, and not dependent on paid APIs, account/proxy pools,
high-frequency scraping, private data, full-platform social coverage claims, LLM
dependency, or default connectors requiring login cookies, CAPTCHA bypass, or
paywall bypass.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md`
- `docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md`
- `docs/PROJECT_BRIEF.md`

## Planned Test

The implementation will add `tests/test_project_brief_docs.py` with one
docs-only test that extracts `## Non-Goals For MVP` and asserts:

- `No paid API requirement.`
- `No account pool.`
- `No proxy pool.`
- `No high-frequency scraping.`
- `No automated posting.`
- `No private user data collection.`
- `No claim that the tool provides full-platform Instagram, TikTok, X, or Xiaohongshu coverage.`
- `No LLM dependency in the first core pipeline. The first version should work with deterministic extraction and scoring. Optional LLM summarization can be added later.`
- `No default connector that needs login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.`

## Scope Constraints

Allowed changes:

- `tests/test_project_brief_docs.py`
- Stage 103 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source acquisition, connector, scraping, browser automation, account,
  cookie, session, proxy, CAPTCHA, paywall, social platform, scoring, dashboard,
  report, or CLI tests
- scoring, first-run, source-pack, entity-pack, scheduling, dashboard,
  manual-import, candidate-discovery, community-signal, trend-delta, or security
  docs guards

Do not expand this stage into connector behavior, platform search, social
monitoring, scraping automation, browser/account/proxy/CAPTCHA/paywall flows,
generated data, scoring algorithm changes, dashboard/report behavior,
compliance/audit/legal review product features, or runtime validation.

This guard must not claim that future opt-in social/community/external-tool
integrations are prohibited; it only pins MVP non-goals.

## Review Questions

1. Does the plan protect a real `docs/PROJECT_BRIEF.md` MVP non-goals boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/PROJECT_BRIEF.md` and scoped
   narrowly enough to `## Non-Goals For MVP`?
3. Does the plan avoid over-pinning `## Free-First Boundary`,
   `## Recommended First Public Version`, current connector docs, and future
   opt-in social/community/external-tool expansion?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-103-plan-review-prompt.md)" > docs/reviews/opencode-stage-103-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-103-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Create `tests/test_project_brief_docs.py` with exactly:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_BRIEF_DOC = ROOT / "docs" / "PROJECT_BRIEF.md"


def _read_project_brief_doc() -> str:
    return PROJECT_BRIEF_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_project_brief_docs_keep_mvp_non_goals_boundary() -> None:
    non_goals = _section(_read_project_brief_doc(), "Non-Goals For MVP")
    normalized = _normalized(non_goals)

    for phrase in (
        "No paid API requirement.",
        "No account pool.",
        "No proxy pool.",
        "No high-frequency scraping.",
        "No automated posting.",
        "No private user data collection.",
        "No claim that the tool provides full-platform Instagram, TikTok, X, "
        "or Xiaohongshu coverage.",
        "No LLM dependency in the first core pipeline. The first version should work "
        "with deterministic extraction and scoring. Optional LLM summarization can "
        "be added later.",
        "No default connector that needs login cookies, proxy pools, CAPTCHA bypass, "
        "or paywall bypass.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
```

Expected: pass.

- [ ] Run adjacent docs boundary tests:

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_scoring_docs.py tests/test_architecture_boundary_docs.py tests/test_source_packs_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_project_brief_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-103-code-review-prompt.md` with this
      review request:

```markdown
# Stage 103 Code Review Prompt

Review the Stage 103 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 103 adds `tests/test_project_brief_docs.py`, a standalone docs drift guard
for the `## Non-Goals For MVP` section in `docs/PROJECT_BRIEF.md`. It asserts
that the MVP remains documented as having no paid API requirement, no account or
proxy pool, no high-frequency scraping, no automated posting, no private user
data collection, no full-platform social coverage claim, no required LLM in the
first core pipeline, and no default connector that needs login cookies, proxy
pools, CAPTCHA bypass, or paywall bypass.

## Files To Review

- `tests/test_project_brief_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md`
- `docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md`
- `docs/reviews/opencode-stage-103-plan-review-prompt.md`
- `docs/reviews/opencode-stage-103-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_project_brief_docs.py`
- Stage 103 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source acquisition, connector, scraping, browser automation, account,
  cookie, session, proxy, CAPTCHA, paywall, social platform, scoring, dashboard,
  report, or CLI tests

Do not propose connector behavior, platform search, social monitoring, scraping
automation, browser/account/proxy/CAPTCHA/paywall flows, generated data, scoring
algorithm changes, dashboard/report behavior, compliance/audit/legal review
product features, or runtime validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_scoring_docs.py tests/test_architecture_boundary_docs.py tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_project_brief_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 103 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/PROJECT_BRIEF.md` `## Non-Goals For MVP` section?
3. Is the new standalone test independent from broad CLI docs tests, source
   boundary tests, and runtime source/connector/scoring behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-103-code-review-prompt.md)" > docs/reviews/opencode-stage-103-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-103-code-review.md`.
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

- [ ] Stage only Stage 103 files:

```bash
git add \
  docs/reviews/opencode-stage-103-code-review-prompt.md \
  docs/reviews/opencode-stage-103-code-review.md \
  docs/reviews/opencode-stage-103-plan-review-prompt.md \
  docs/reviews/opencode-stage-103-plan-review.md \
  docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md \
  docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md \
  tests/test_project_brief_docs.py
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
git commit -m "Guard project brief MVP non-goals"
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
