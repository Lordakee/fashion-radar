# Release Documentation Consistency Design

## Goal

Make the published v0.1 documentation internally consistent about source scope
and record the user-visible Stage 386 and Stage 387 ROW ONE homepage additions
under the existing `Unreleased` changelog section.

## Problem

The base install does not include the optional `article` dependency, but some
documentation calls HTML seed-URL collection and sitemap discovery "core".
Other documentation correctly describes RSS/Atom, RSSHub-compatible feeds, and
GDELT as the minimum core and HTML/sitemap support as optional. The empty
`Unreleased` section also omits two user-visible homepage sections despite the
contributor documentation requiring changelog updates for such changes.

## Decision

Use a three-tier documentation vocabulary everywhere this stage touches:

1. **Minimum core:** RSS/Atom, RSSHub-compatible feeds, and GDELT. This path
   works without the optional `article` extra. Official RSS stays in this tier.
2. **Optional article-extra collection:** configured HTML seed URLs and sitemap
   discovery, installed through the `article` extra. These retain existing
   robots.txt, paywall-skip, bounded-run, attribution, and no-demand-proof
   constraints.
3. **Opt-in social collection:** Xiaohongshu, Instagram, X/Twitter, and
   YouTube remain non-core, disabled by default, and use-at-your-own-risk.

The existing manual-input and community-handoff material remains a separate
non-connector subsection after the connector tiers. It must not be absorbed
into optional article-extra collection merely because the Markdown headings are
restructured.

The changelog entry will record the Stage 386 Daily Saved Text Takeaways and
Stage 387 Daily Local Brand, Product & People Signal Digest as homepage-only
generated ROW ONE `index.html` sections that reuse existing saved local article
text and references. It will explicitly state that no generated data artifact,
route, source collection, scoring, or app contract changed.

The Project Brief's v0.1 promise list must stop describing static webpage
monitoring as post-MVP. It will instead keep Google News, Google Trends, Reddit,
and social connectors in that post-MVP/opt-in list while stating that configured
HTML seed URLs and sitemap discovery are current optional `article`-extra v0.1
capabilities.

## Scope

Modify only documentation, documentation-contract tests, the Stage 388 design
and plan, and required review records.

Documentation targets:

- `CHANGELOG.md`
- `AGENTS.md`
- `docs/PROJECT_BRIEF.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`

Test targets:

- `tests/test_row_one_docs.py`
- `tests/test_source_boundaries_docs.py`
- `tests/test_architecture_boundary_docs.py`
- `tests/test_project_brief_docs.py`
- `tests/test_cli_docs.py`
- `tests/test_agents_scope_docs.py`

## Non-Goals

This stage does not change collectors, source types, package extras,
dependencies, source defaults, CLI behavior, source packs, data schemas,
generated-site artifacts, ROW ONE routes, scoring, scheduling, social-platform
connectors, credentials, scraping behavior, or deployment.

## Verification

The focused document tests must prove that all touched surfaces agree on the
three-tier source model and that the changelog preserves the exact Stage 386/387
homepage-only boundary. Full pytest, Ruff, release hygiene, first-run smoke,
public lockfile validation, and package archive checks remain release gates.
