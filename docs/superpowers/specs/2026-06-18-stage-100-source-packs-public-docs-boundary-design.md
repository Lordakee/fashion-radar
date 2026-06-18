# Stage 100 Source Packs Public Docs Boundary Design

## Goal

Add a standalone docs drift guard for the `## Public Fashion Pack` section in
`docs/source-packs.md` so future edits keep the starter pack framed around
existing public source types and explicit excluded acquisition categories.

## Scope

Stage 100 is docs-test-only. It creates one focused pytest module that reads the
existing Markdown file, extracts the `## Public Fashion Pack` section,
normalizes whitespace and case, and asserts public-pack source-boundary phrases.

Allowed changes:

- `tests/test_source_packs_docs.py`
- Stage 100 spec, plan, and review artifacts

Out of scope:

- Runtime source-pack behavior
- source-pack YAML contents
- source-pack lint behavior or `docs/source-pack-quality.md`
- collectors, adapters, schemas, dependencies, CI, or `uv.lock`
- `docs/source-packs.md` source text
- source acquisition workflows, social scraping, platform search, or connector
  behavior

## Boundary Phrases

The guard should extract only `## Public Fashion Pack` and assert these phrases
after whitespace collapse and case-folding:

- `configs/source-packs/fashion-public.example.yaml`
- `it uses only existing v0.1.0 source types`
- `` `rss` ``
- `` `gdelt` ``
- `keeps the rss entries conservative`
- `bounded gdelt lanes`
- `inside the configured source set`
- `it does not include google news rss, google trends, account-based source access, browser automation, access-control bypasses, paywall bypass, or private data collection.`

These phrases pin the starter pack's allowed source types and explicit
exclusions without expanding into lint quality, source availability checks,
article extraction, source acquisition, or runtime source configuration.

## Test Shape

Use the same lightweight pattern as the recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/source-packs.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, parse YAML, run the CLI, fetch
network resources, or write files.

## Verification

Focused verification should cover the new docs guard, the existing source-pack
tests, ruff, formatting, and whitespace checks. Full verification before commit
should reuse the repository release gate: release hygiene, full pytest with
proxy vars unset, repo-wide ruff check and format check, lockfile check, mirror
URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged
secret scan.

## Risks

The full exclusion sentence is intentionally somewhat brittle because it
preserves the negation around source/acquisition categories. That is acceptable
for a boundary guard.

This stage is adjacent to Stage 92 because both involve source packs, but the
target is different: Stage 92 guarded `docs/source-pack-quality.md` linter
semantics, while this stage guards `docs/source-packs.md` starter-pack scope.
The test intentionally does not assert `## Check Pack Quality`, article
extraction, source-pack lint output, or source availability language.
