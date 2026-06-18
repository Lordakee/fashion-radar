# Stage 101 First Run Docs Boundary Design

## Goal

Add a standalone docs drift guard for the `## Boundary` section in
`docs/first-run.md` so future edits keep first-run sample documentation framed
as deterministic local sample checks, not live collection, platform automation,
external services, demand proof, platform coverage, or source ranking.

## Scope

Stage 101 is docs-test-only. It creates one focused pytest module that reads the
existing Markdown file, extracts the `## Boundary` section, normalizes
whitespace and case, and asserts local-sample boundary phrases.

Allowed changes:

- `tests/test_first_run_docs.py`
- Stage 101 spec, plan, and review artifacts

Out of scope:

- Runtime first-run smoke behavior
- CLI behavior or command sequences
- example data, generated outputs, configs, schemas, dependencies, CI, or
  `uv.lock`
- `docs/first-run.md` source text
- optional expanded watchlist sample boundary wording outside `## Boundary`
- dashboard, scheduling, source-pack, candidate-discovery, manual import, or
  scoring behavior

## Boundary Phrases

The guard should extract only `## Boundary` and assert these phrases after
whitespace collapse and case-folding:

- `first-run sample does not run live collection`
- `` automated smoke does not run `collect`, `run`, or `dashboard` ``
- `` should not create files under repo `data/` or `reports/` ``
- `does not perform browser automation, account login, cookies/sessions`
- `source/platform connectors, scraping, platform automation, monitoring`
- `scheduling, or external services`
- `candidate and trend outputs are local sample content checks from the checked-in example`
- `not proof of demand`
- `not platform coverage`
- `not source ranking`

These phrases pin the first-run sample boundary without expanding into runtime
smoke validation, dashboard docs, scheduling docs, source acquisition, or
candidate/trend scoring behavior.

## Test Shape

Use the same lightweight pattern as the recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/first-run.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute the first-run smoke, run
CLI commands, read or write sample data, fetch network resources, or write
files.

## Verification

Focused verification should cover the new docs guard, existing first-run smoke
tests, ruff, formatting, and whitespace checks. Full verification before commit
should reuse the repository release gate: release hygiene, full pytest with
proxy vars unset, repo-wide ruff check and format check, lockfile check, mirror
URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged
secret scan.

## Risks

The boundary language includes terms that also appear in scheduling/dashboard
contexts. Section scoping keeps this stage specific to first-run sample
documentation, and the test does not assert dashboard docs or scheduling docs.

The section is short, so phrase assertions may need deliberate updates if the
docs are rewritten. That is acceptable because the goal is to catch accidental
drift from local deterministic sample framing.

`tests/test_cli_docs.py` already covers some first-run wording broadly across
the whole document. This stage is intentionally narrower: it proves the boundary
phrases remain in the `## Boundary` section and adds local sample output
non-claim phrases that the broad test does not pin.
