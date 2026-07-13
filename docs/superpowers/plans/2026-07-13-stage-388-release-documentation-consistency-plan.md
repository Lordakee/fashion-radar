# Stage 388 Release Documentation Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile v0.1 source-scope documentation with the optional `article`
package extra and record the Stage 386/387 user-visible ROW ONE homepage changes
under `CHANGELOG.md` `Unreleased`.

**Architecture:** This is a documentation-contract stage. A single vocabulary
distinguishes the base-install minimum core from optional article-extra
collection and opt-in social collection. Existing documentation tests become
the regression contract; no runtime code, data model, collector registration,
or package behavior changes.

**Tech Stack:** Markdown, Python pytest documentation tests, Ruff, uv frozen
verification, existing Claude Code and OpenCode review protocol.

---

## Scope And Invariants

- Minimum core means only RSS/Atom, RSSHub-compatible feeds, and GDELT.
- HTML seed-URL collection and sitemap discovery remain supported optional
  capabilities behind the existing `article` extra. Preserve their robots.txt,
  paywall, bounded-run, attribution, and no-demand-proof wording.
- Xiaohongshu, Instagram, X/Twitter, and YouTube remain opt-in, non-core, and
  disabled by default. Do not weaken their existing safety boundaries.
- Add one concise `Unreleased` `Added` entry for Stage 386/387 that accurately
  describes homepage-only generated ROW ONE behavior and explicitly avoids
  claiming new artifacts, routes, source collection, scoring, or app contracts.
- Do not modify collectors, dependencies, package extras, source packs, CLI
  behavior, schemas, generated JSON, routes, scheduling, deployment, or social
  connector behavior.

## File Map

- Modify `CHANGELOG.md`: add the Stage 386/387 `Unreleased` entry.
- Modify `AGENTS.md`: replace the contradictory core-source sentence with the
  minimum-core plus optional-article-extra statement.
- Modify `docs/PROJECT_BRIEF.md`: split minimum core sources from optional
  article-extra HTML/sitemap collection.
- Modify `docs/source-boundaries.md`: split the current Core tier into Minimum
  Core and Optional Article-Extra Collection, then keep local input/community
  handoff material in its own non-connector subsection while preserving limits.
- Modify `docs/architecture.md`: align the source-boundary description with the
  same two-tier collector contract.
- Modify `tests/test_row_one_docs.py`: add a precise changelog boundary test.
- Modify `tests/test_source_boundaries_docs.py`: test the two source tiers and
  preserve HTML/sitemap safeguards in the optional tier.
- Modify `tests/test_architecture_boundary_docs.py`: assert the two-tier
  wording instead of treating optional collectors as base core.
- Modify `tests/test_project_brief_docs.py`: add Project Brief parity coverage.
- Modify `tests/test_cli_docs.py`: assert that the documented `collect` surface
  still distinguishes minimum core, optional article-extra collection, and
  opt-in social collection.
- Create `tests/test_agents_scope_docs.py`: assert that the normative
  `AGENTS.md` Scope Boundaries section uses the same source-scope contract.
- Create Stage 388 design, plan, and credential-free review records.

## Task 1: Add RED documentation-contract tests

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_source_boundaries_docs.py`
- Modify: `tests/test_architecture_boundary_docs.py`
- Modify: `tests/test_project_brief_docs.py`
- Modify: `tests/test_cli_docs.py`
- Create: `tests/test_agents_scope_docs.py`

- [ ] **Step 1: Add a changelog contract test.**

Add a `CHANGELOG = ROOT / "CHANGELOG.md"` module constant and
`test_stage_388_changelog_records_daily_local_homepage_digests()` to
`tests/test_row_one_docs.py`. Read and normalize only the `Unreleased` /
`Added` entry, not the entire changelog:

```python
text = _read(CHANGELOG)
unreleased = text.split("## [Unreleased]", 1)[1].split("\n## [", 1)[0]
assert "### Added" in unreleased
added = _normalized(unreleased.split("### Added", 1)[1].split("\n### ", 1)[0])
for phrase in (
    "stages 386-387",
    "daily saved text takeaways",
    "daily local brand, product & people signal digest",
    "homepage-only",
    "generated row one `index.html`",
    "organizing existing current-edition saved local article text and references",
    "without changing generated data artifacts, routes, source collection, "
    "scoring, or app contracts",
):
    assert phrase in added
```

- [ ] **Step 2: Add two-tier source-boundary tests.**

In `tests/test_source_boundaries_docs.py`, add a helper that extracts a `###`
subsection from `## Connector Risk Tiers`. Assert `Minimum Core` contains GDELT,
RSS/Atom, RSSHub-compatible routes, and official RSS but excludes HTML page
collection, sitemap discovery, Xiaohongshu, Instagram, Twitter/X, and YouTube.
Replace the existing Core-scoped HTML and sitemap tests with an
`Optional Article-Extra Collection` test that retains exact assertions for
`optional `article` extra`, `robots.txt`, `does not crawl or follow links`,
`trafilatura.sitemaps`, `bounded per run`, and the no-demand-proof boundary.
Assert that the optional subsection excludes manual signal import and community
handoff text. Add a `Local Input And Community Handoff` subsection test that
requires those terms and the existing non-connector/local-only boundary.
Add an Opt-In subsection test requiring explicit user enablement, all four
social connectors, use-at-your-own-risk wording, and the existing no-demand-
proof/no-platform-coverage wording.

- [ ] **Step 3: Change architecture and Project Brief contracts.**

Remove the obsolete architecture literal that treats HTML/sitemap as core and
add both required phrases:

```python
"the minimum core collector set is rss, rsshub-compatible feeds, and gdelt",
"html seed-url collection and sitemap discovery are optional `article`-extra collectors",
```

Add a Project Brief test that verifies its source section contains the same
minimum core and optional article-extra distinction, including configured public
HTML seed URLs and allowed official newsroom/sitemap discovery. It must also
distinguish official RSS (minimum core) from newsroom/press-release HTML and
sitemap pages (optional article-extra collection). In the separate
`Recommended First Public Version` section, assert this exact positive sentence:

```md
Configured HTML seed URLs and sitemap discovery are current optional `article`-extra v0.1 capabilities.
```

Also assert the retained Google News/Trends/Reddit/social post-MVP sentence and
that `static webpage monitoring` is absent from that section.

- [ ] **Step 4: Guard the existing CLI reference wording.**

Add a focused `tests/test_cli_docs.py` assertion using the existing
`_cli_reference_command_entry("collect")` helper. Normalize only that entry and
require `RSS/RSSHub/GDELT`, `html`/`sitemap` via the optional `article` extra,
and opt-in social with Xiaohongshu, Instagram, Twitter/X, and YouTube. This is
a regression guard that should already pass; do not rewrite the CLI reference
unless it exposes an actual mismatch.

- [ ] **Step 4.5: Add an AGENTS.md source-scope contract test.**

Create `tests/test_agents_scope_docs.py`. Extract and normalize `## Scope
Boundaries` from `AGENTS.md`, then assert all of:

```python
for phrase in (
    "`v0.1.0` minimum core sources are rss/atom, rsshub-compatible feeds, and gdelt",
    "html seed-url collection and sitemap discovery are optional capabilities "
    "provided by the `article` extra",
    "google news rss is not part of `v0.1.0`",
    "social-platform connectors are opt-in",
):
    assert phrase in normalized
assert (
    "core sources are rss/atom, rsshub-compatible, gdelt, html seed-url collection, "
    "and sitemap discovery"
) not in normalized
```

- [ ] **Step 5: Run the RED documentation tests.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py \
  tests/test_source_boundaries_docs.py \
  tests/test_architecture_boundary_docs.py \
  tests/test_project_brief_docs.py \
  tests/test_cli_docs.py \
  tests/test_agents_scope_docs.py -q
```

Expected: failures for the new Unreleased Added entry assertion, the new
AGENTS.md source-scope assertion, the new Minimum Core/Optional Article-Extra/
Local Input And Community Handoff source-boundary assertions, the replacement
architecture phrases, and the Project Brief parity assertion. The existing
Opt-In and CLI `collect` entry regression guards should pass immediately against
the current documentation.

## Task 2: Reconcile the documentation surfaces

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `AGENTS.md`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Add the Unreleased entry.**

Under `## [Unreleased]`, add:

```md
### Added

- Stages 386-387 add homepage-only Daily Saved Text Takeaways and Daily Local Brand, Product & People Signal Digest sections to the generated ROW ONE `index.html`, organizing existing current-edition saved local article text and references without changing generated data artifacts, routes, source collection, scoring, or app contracts.
```

- [ ] **Step 2: State the source contract in AGENTS.md.**

Replace the single conflicting source sentence with:

```md
- `v0.1.0` minimum core sources are RSS/Atom, RSSHub-compatible feeds, and GDELT. HTML seed-URL collection and sitemap discovery are optional capabilities provided by the `article` extra.
```

Leave the Google News and social-connector bullets unchanged.

- [ ] **Step 3: Split the Project Brief source section.**

Replace the broad "Core sources" list with a `Minimum core sources` list for
RSS/RSSHub and GDELT, followed by an `Optional article-extra collection` list
for configured public HTML seed URLs and allowed official newsroom/sitemap
discovery. In the later v0.1 promise list, remove static webpage monitoring from
the post-MVP sentence and state that configured HTML seed URLs and sitemap
discovery are current optional `article`-extra v0.1 capabilities. Keep the
existing social source section and non-goals unchanged.

- [ ] **Step 4: Split the source-boundary connector tier.**

Replace `### Core` with `### Minimum Core` containing only GDELT, RSS/Atom,
RSSHub, and allowed official RSS. Add `### Optional Article-Extra Collection`
immediately after it with the existing HTML and sitemap bullets, plus allowed
official newsroom/press-release HTML pages. Split the existing mixed official
newsroom/press-release/RSS/sitemap bullet so official RSS is not reclassified
as article-extra-only. Retain all existing robots, limits, and no-demand-proof
language. Move the current manual signal import, community handoff, and related
local-only paragraphs under a new `### Local Input And Community Handoff`
heading immediately after the optional collector material; do not describe
these local inputs as connectors or article-extra collection.

- [ ] **Step 5: Align the architecture source boundary.**

Replace the obsolete one-tier sentence with a sentence that names the minimum
core collector set and a second sentence that calls HTML seed-URL collection and
sitemap discovery optional `article`-extra collectors. Retain the local import
and opt-in social statements verbatim.

- [ ] **Step 6: Run the GREEN documentation tests.**

Run the command from Task 1 Step 5. Expected: all selected tests pass.

## Task 3: Review and release the documentation-only node

**Files:**
- Create: `docs/reviews/claude-code-stage-388-plan-review.md`
- Create: `docs/reviews/opencode-stage-388-plan-review.md`
- Create: `docs/reviews/claude-code-stage-388-code-review.md`
- Create: `docs/reviews/claude-code-stage-388-release-review.md`

- [ ] **Step 1: Submit the design and plan to Claude Code before documentation edits.**

Use the required read-only primary-review command with `--effort max`, plan
mode, no session persistence, and only Read/Grep/Glob/LS/Bash tools. Ask it to
review source-scope semantics, changelog accuracy, test coverage, and scope
containment. Capture one coherent, credential-free body.

- [ ] **Step 2: Ask OpenCode to revise the plan after Claude review.**

Use `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` to assess
the Claude findings and revise the plan only when technically justified. Capture
one coherent, credential-free body. Keep the verified rejection of any claim
that the current `Unreleased` section already has an `Added` subsection: it is
empty immediately before `## [0.1.0]`.

- [ ] **Step 3: Run focused validation after implementation.**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py \
  tests/test_source_boundaries_docs.py \
  tests/test_architecture_boundary_docs.py \
  tests/test_project_brief_docs.py \
  tests/test_cli_docs.py \
  tests/test_agents_scope_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
git diff --check
```

- [ ] **Step 4: Submit the completed diff to Claude Code.**

Request a code review of the stable integrated snapshot. Resolve every critical
or important finding, rerun affected verification, and capture the completed
review without raw logs, status stubs, duplicate verdicts, or credentials.

- [ ] **Step 5: Run final release gates.**

Run full pytest, Ruff check/format, release hygiene, first-run smoke, public
lockfile validation with inherited index variables cleared, and a temporary
sdist/wheel archive check. Confirm `uv.lock` has no diff and all review records
are complete and hygienic.

- [ ] **Step 6: Request Claude Code release review, commit, and publish.**

Request a release review of the post-gate stable diff. After approval, commit
the intended Stage 388 files, publish with a non-forced refspec, and verify the
remote `main` SHA.

## Verification Checklist

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config run --frozen pytest
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config run --frozen python \
  scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config run --frozen python \
  scripts/check_first_run_smoke.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX -u UV_INDEX_URL \
  -u UV_EXTRA_INDEX_URL -u UV_FIND_LINKS \
  UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
git diff --cached --check
```
