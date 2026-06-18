# Stage 112 README Project Brief Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align README public non-goals with the project brief MVP non-goals and
guard that parity.

**Architecture:** Add one concise paragraph to README `## What It Does Not Do`
using project-brief MVP non-goal wording, then extend
`tests/test_project_brief_docs.py` with a narrow README/brief parity guard. Keep
this docs/docs-test-only and avoid runtime, collector, connector, scraping,
compliance, dependency, and CI changes.

**Tech Stack:** Markdown, Python 3.11, pytest, pathlib, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-19-stage-112-readme-project-brief-parity-design.md`
  records the Stage 112 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-19-stage-112-readme-project-brief-parity-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-112-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-112-plan-review.md` records the local
  plan review.
- Modify: `README.md` adds a concise public non-goals parity paragraph.
- Modify: `tests/test_project_brief_docs.py` adds the README/brief parity guard.
- Create: `docs/reviews/opencode-stage-112-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-112-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-112-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 112 Plan Review Prompt

Review the Stage 112 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Align the public README `## What It Does Not Do` section with
`docs/PROJECT_BRIEF.md` `## Non-Goals For MVP` and add a narrow parity guard so
GitHub readers see the same high-risk MVP non-goals: no paid API requirement,
no account/proxy pool, no high-frequency scraping, no automated posting, no
private data collection, no full-platform Instagram/TikTok/X/Xiaohongshu
coverage claim, and no default connector that needs login cookies, proxy pools,
CAPTCHA bypass, or paywall bypass.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-112-readme-project-brief-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-112-readme-project-brief-parity-plan.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `tests/test_project_brief_docs.py`
- `tests/test_cli_docs.py`
- `tests/test_source_boundaries_docs.py`

## Planned README Edit

Append this paragraph immediately after the opening paragraph in README
`## What It Does Not Do`:

```markdown
The public MVP non-goals stay aligned with the project brief: no paid API
requirement, no account pool, no proxy pool, no high-frequency scraping, no
automated posting, no private user data collection, no full-platform Instagram,
TikTok, X, or Xiaohongshu coverage claim, and no default connector that needs
login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.
```

## Planned Test

The implementation will extend `tests/test_project_brief_docs.py` with README
reading support and one parity guard. It will extract README
`## What It Does Not Do` and project brief `## Non-Goals For MVP`, normalize both
sections, and assert README coverage for:

- `no paid api requirement`
- `no account pool`
- `no proxy pool`
- `no high-frequency scraping`
- `no automated posting`
- `no private user data collection`
- `no full-platform instagram, tiktok, x, or xiaohongshu coverage claim`
- `no default connector that needs login cookies, proxy pools, captcha bypass, or paywall bypass`

## Scope Constraints

Allowed changes:

- `README.md`
- `tests/test_project_brief_docs.py`
- Stage 112 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `docs/source-boundaries.md`
- `docs/dashboard.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- `tests/test_source_boundaries_docs.py`
- runtime behavior, CLI behavior, collectors, source acquisition, connector
  behavior, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

Do not expand this stage into a three-way source-boundaries parity guard,
command docs guard, connector implementation, platform search, source
collection, schema migration, compliance feature, or README rewrite.
This stage intentionally excludes the project brief `No LLM dependency...`
bullet because it is an internal pipeline-design boundary rather than a
high-risk public source-access boundary.

## Review Questions

1. Does the planned README paragraph accurately align with the project brief MVP
   non-goals without overpromising or changing product behavior?
2. Is the planned parity guard narrow enough and present in the right test file?
3. Are the planned phrases stable, public-facing, and not already fully covered
   by existing README/source-boundaries tests?
4. Does the plan avoid runtime, connector, scraping, platform, dependency, CI,
   and compliance feature changes?
5. Are the verification commands sufficient for this docs/docs-test stage?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-112-plan-review-prompt.md)" > docs/reviews/opencode-stage-112-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-112-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Update README And Add The Guard

- [ ] Insert this paragraph immediately after the opening paragraph in README
      `## What It Does Not Do`:

```markdown
The public MVP non-goals stay aligned with the project brief: no paid API
requirement, no account pool, no proxy pool, no high-frequency scraping, no
automated posting, no private user data collection, no full-platform Instagram,
TikTok, X, or Xiaohongshu coverage claim, and no default connector that needs
login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.
```

- [ ] Add README support and the parity test to `tests/test_project_brief_docs.py`:

```python
README = ROOT / "README.md"
```

```python
def _read_readme() -> str:
    return README.read_text(encoding="utf-8")
```

```python
def test_readme_keeps_project_brief_mvp_non_goal_parity() -> None:
    readme_non_goals = _section(_read_readme(), "What It Does Not Do")
    brief_non_goals = _section(_read_project_brief_doc(), "Non-Goals For MVP")

    normalized_readme = _normalized(readme_non_goals)
    normalized_brief = _normalized(brief_non_goals)

    for brief_phrase, readme_phrase in (
        ("No paid API requirement.", "no paid api requirement"),
        ("No account pool.", "no account pool"),
        ("No proxy pool.", "no proxy pool"),
        ("No high-frequency scraping.", "no high-frequency scraping"),
        ("No automated posting.", "no automated posting"),
        ("No private user data collection.", "no private user data collection"),
        (
            "No claim that the tool provides full-platform Instagram, TikTok, X, "
            "or Xiaohongshu coverage.",
            "no full-platform instagram, tiktok, x, or xiaohongshu coverage claim",
        ),
        (
            "No default connector that needs login cookies, proxy pools, "
            "CAPTCHA bypass, or paywall bypass.",
            "no default connector that needs login cookies, proxy pools, captcha "
            "bypass, or paywall bypass",
        ),
    ):
        assert brief_phrase.casefold() in normalized_brief
        assert readme_phrase in normalized_readme
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
```

Expected: pass.

- [ ] Run adjacent README/public-scope docs tests:

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_cli_docs.py tests/test_source_boundaries_docs.py -q
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

- [ ] Create `docs/reviews/opencode-stage-112-code-review-prompt.md` with this
      review request:

```markdown
# Stage 112 Code Review Prompt

Review the Stage 112 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 112 adds one concise README public non-goals paragraph aligned with
`docs/PROJECT_BRIEF.md` `## Non-Goals For MVP`, then extends
`tests/test_project_brief_docs.py` with a narrow README/project-brief parity
guard.

## Files To Review

- `README.md`
- `tests/test_project_brief_docs.py`
- `docs/superpowers/specs/2026-06-19-stage-112-readme-project-brief-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-112-readme-project-brief-parity-plan.md`
- `docs/reviews/opencode-stage-112-plan-review-prompt.md`
- `docs/reviews/opencode-stage-112-plan-review.md`
- `docs/reviews/opencode-stage-112-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `README.md`
- `tests/test_project_brief_docs.py`
- Stage 112 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `docs/source-boundaries.md`
- `docs/dashboard.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- `tests/test_source_boundaries_docs.py`
- runtime behavior, CLI behavior, collectors, source acquisition, connector
  behavior, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_cli_docs.py tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen ruff check tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_project_brief_docs.py
git diff --check
```

## Review Questions

1. Does the README paragraph accurately reflect the project brief MVP non-goals
   without changing product behavior?
2. Does the parity guard prove README coverage while staying narrow and
   maintainable?
3. Does the implementation avoid overlap or conflict with existing README,
   source-boundaries, source-packs, and CLI docs guards?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-112-code-review-prompt.md)" > docs/reviews/opencode-stage-112-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-112-code-review.md`.
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

- [ ] Stage only Stage 112 files:

```bash
git add README.md tests/test_project_brief_docs.py \
  docs/superpowers/specs/2026-06-19-stage-112-readme-project-brief-parity-design.md \
  docs/superpowers/plans/2026-06-19-stage-112-readme-project-brief-parity-plan.md \
  docs/reviews/opencode-stage-112-plan-review-prompt.md \
  docs/reviews/opencode-stage-112-plan-review.md \
  docs/reviews/opencode-stage-112-code-review-prompt.md \
  docs/reviews/opencode-stage-112-code-review.md
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
git commit -m "Align README MVP non-goals with project brief"
```

- [ ] Push to `origin main` using only temporary credentials.
- [ ] Verify no GitHub credential was persisted:

```bash
git config --get-all http.https://github.com/.extraheader || true
git remote -v | sed -E 's#(https://)[^/@]+@#\1***@#g'
```

- [ ] Verify GitHub Actions `CI` succeeds for the pushed SHA.

## Completion Criteria

- README public non-goals explicitly align with project brief MVP non-goals.
- `tests/test_project_brief_docs.py` contains a focused README/project-brief
  parity guard.
- No runtime, dependency, config, CI, connector, scraping, platform, or
  compliance feature files changed.
- Focused, adjacent, release-gate, staged, and GitHub Actions checks pass.
