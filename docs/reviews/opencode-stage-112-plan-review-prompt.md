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
