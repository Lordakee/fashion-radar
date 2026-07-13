# Claude Code Stage 388 Release Review

## Verdict

APPROVED

## Release Result

No critical or important findings.

The Unreleased changelog entry accurately limits the Stage 386-387 ROW ONE
work to homepage-only presentation. The source-tier contract is consistent:
RSS/Atom, RSSHub-compatible feeds, and GDELT are the v0.1 minimum core; HTML
seed URL collection and sitemap discovery are optional `article`-extra
collection; local/community handoff remains non-connector; and social
collection remains opt-in.

The per-connector documentation tests use scoped subsection and bullet helpers.
The final YouTube bullet retains its own indented continuation lines while
excluding later unindented opt-in policy and Google News text, so unrelated
prose cannot satisfy its safety assertions.

The release diff is limited to intended documentation, documentation-contract
tests, design/plan records, and review records. The reviewer found no
credentials, generated artifacts, runtime changes, stale review stubs, or raw
tool-output captures in the candidate release set.

## Release Verification

- Focused Stage 388 documentation contracts passed: `213 passed`.
- Full test suite passed: `2829 passed`.
- Ruff check and format check passed.
- Release hygiene, first-run smoke, and public lockfile checks passed.
- The built sdist and wheel passed archive validation.
- An installed wheel passed CLI, initialization, doctor, first-run, and package
  resource checks; an installed dashboard-extra wheel imported dashboard
  modules successfully.
