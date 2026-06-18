# Stage 103 Project Brief Non-Goals Design

## Goal

Add a standalone docs drift guard for the `## Non-Goals For MVP` section in
`docs/PROJECT_BRIEF.md` so future edits keep the MVP framed as free-first,
local-first, deterministic, and not dependent on paid APIs, account/proxy pools,
high-frequency scraping, private data, full-platform social coverage claims,
LLM dependency, or default connectors that need login cookies, CAPTCHA bypass,
or paywall bypass.

## Scope

Stage 103 is docs-test-only. It creates one focused pytest module that reads the
existing project brief, extracts the `## Non-Goals For MVP` section, normalizes
whitespace and case, and asserts MVP non-goal phrases.

Allowed changes:

- `tests/test_project_brief_docs.py`
- Stage 103 spec, plan, and review artifacts

Out of scope:

- `docs/PROJECT_BRIEF.md` source text
- runtime source acquisition, connector behavior, scraping, browser automation,
  account/cookie/session handling, proxy handling, CAPTCHA/paywall bypass,
  social platform coverage, scoring, dashboard behavior, CLI behavior, schemas,
  configs, dependencies, CI, or `uv.lock`
- broad project-brief parity checks across multiple sections
- blocking future optional, explicit opt-in social/community/external-tool
  integrations that have clear authorization and access boundaries
- compliance/audit/legal review product features

## Boundary Phrases

The guard should extract only `## Non-Goals For MVP` and assert these phrases
after whitespace collapse and case-folding:

- `No paid API requirement.`
- `No account pool.`
- `No proxy pool.`
- `No high-frequency scraping.`
- `No automated posting.`
- `No private user data collection.`
- `No claim that the tool provides full-platform Instagram, TikTok, X, or Xiaohongshu coverage.`
- `No LLM dependency in the first core pipeline. The first version should work with deterministic extraction and scoring. Optional LLM summarization can be added later.`
- `No default connector that needs login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.`

These phrases pin MVP non-goals without asserting that future opt-in connectors
or externally supplied community data cannot be added later.

## Test Shape

Use the same lightweight pattern as recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/PROJECT_BRIEF.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute CLI commands, run
scrapers/connectors, read or write data/report files, fetch network resources,
or write files.

## Verification

Focused verification should cover the new docs guard, adjacent boundary-docs
guards, ruff, formatting, and whitespace checks. Full verification before commit
should reuse the repository release gate: release hygiene, full pytest with
proxy vars unset, repo-wide ruff check and format check, lockfile check, mirror
URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged
secret scan.

## Risks

The project brief also contains `## Free-First Boundary`, the immediately
following `## Recommended MVP`, and downstream `## Recommended First Public
Version`. Stage 103 deliberately scopes to `## Non-Goals For MVP` only so the
guard does not over-pin future source/tool examples, positive MVP contents, or
social-platform extension wording.

The section includes terms that would be suspicious in implementation diffs
(`cookies`, `proxy`, `CAPTCHA`, `paywall`, and platform names). In this stage
they are allowed only as negative boundary wording inside docs and tests.

Phrase assertions may need deliberate updates if the MVP non-goals are rewritten
or if the project moves beyond MVP. That is acceptable because the goal is to
catch accidental drift from the public MVP boundary.
