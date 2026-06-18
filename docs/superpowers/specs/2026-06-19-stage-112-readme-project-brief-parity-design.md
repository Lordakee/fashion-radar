# Stage 112 README Project Brief Parity Design

## Goal

Align the public README non-goals with the project brief MVP non-goals and add a
focused docs parity guard so GitHub readers see the same high-risk scope
boundaries: no paid API requirement, no account/proxy pool, no high-frequency
scraping, no automated posting, no private data collection, no full-platform
social coverage claim, and no default connector that needs login cookies,
CAPTCHA bypass, proxy pools, or paywall bypass.

## Scope

Stage 112 is docs and docs-test only. It updates the `README.md` `## What It
Does Not Do` section with a short public-scope non-goals sentence/list derived
from `docs/PROJECT_BRIEF.md` `## Non-Goals For MVP`, then adds one focused
pytest guard to `tests/test_project_brief_docs.py`.

Allowed changes:

- `README.md`
- `tests/test_project_brief_docs.py`
- Stage 112 spec, plan, and review artifacts

Out of scope:

- Runtime code, CLI behavior, collectors, source acquisition, connector
  behavior, social/platform scraping, browser automation, account/session/cookie
  handling, proxy handling, CAPTCHA/paywall behavior, monitoring, scheduling,
  coverage verification, ranking behavior, compliance/audit/legal review product
  features, `src/`, `scripts/`, `examples/`, configs, schemas, dependencies,
  CI, `uv.lock`, package metadata, release hygiene behavior, source-boundaries
  text, dashboard docs, or project brief text

## README Text

Append this paragraph immediately after the opening paragraph in README
`## What It Does Not Do`:

```markdown
The public MVP non-goals stay aligned with the project brief: no paid API
requirement, no account pool, no proxy pool, no high-frequency scraping, no
automated posting, no private user data collection, no full-platform Instagram,
TikTok, X, or Xiaohongshu coverage claim, and no default connector that needs
login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.
```

This keeps README wording concise while making brief-aligned public boundaries
visible near existing non-goals.

## Guarded Phrases

The guard should extract README `## What It Does Not Do` and
`docs/PROJECT_BRIEF.md` `## Non-Goals For MVP`, normalize whitespace and case,
and assert README coverage for these brief-aligned phrases:

- `no paid api requirement`
- `no account pool`
- `no proxy pool`
- `no high-frequency scraping`
- `no automated posting`
- `no private user data collection`
- `no full-platform instagram, tiktok, x, or xiaohongshu coverage claim`
- `no default connector that needs login cookies, proxy pools, captcha bypass, or paywall bypass`

The existing project brief test already pins the brief text itself. Stage 112
adds public README parity for the external-facing summary.
Stage 112 intentionally does not add the project brief `No LLM dependency...`
bullet to README because this node is about public source-access and collection
boundaries, not internal pipeline design constraints.

## Test Shape

Extend `tests/test_project_brief_docs.py` with:

- `README = ROOT / "README.md"`
- `_read_readme()`
- A test that extracts the existing `What It Does Not Do` README section and the
  existing `Non-Goals For MVP` project brief section.

Keep the guard narrow. Do not pull source-boundaries connector tiers, compliance
defaults, command examples, external-tool adapter tables, or the whole README
into the same assertion set.
The README side should remain scoped to the opening `What It Does Not Do`
non-goals text and the new brief-aligned paragraph, not the later
external-tool-handoff boundary matrix.

## Verification

Focused verification should cover `tests/test_project_brief_docs.py`. Adjacent
verification should cover README/CLI docs and source-boundaries docs because
those currently pin nearby public-scope wording. Full verification before
commit should reuse the repository release gate: release hygiene, full pytest
with proxy vars unset, repo-wide ruff check and format check, lockfile check,
mirror URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and
staged secret scan.

## Risks

This stage overlaps conceptually with source-boundaries README requirements and
README external-tool boundary tests. The guard is intentionally limited to MVP
non-goal parity between README and project brief, and it does not change
runtime behavior or add compliance-review product features.
