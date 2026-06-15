# Stage 51 First-Run Sample Output Quality Gate Design

## Objective

Stage 51 makes the deterministic first-run sample prove that Fashion Radar can
turn a checked-in local community handoff file into useful review, report, and
trend output. The current smoke path proves commands run and JSON parses, but a
valid empty or skeletal payload can still pass. This stage raises the gate so a
release fails when the sample rows no longer survive import, match starter
entities, or appear in the generated local report.

## Architecture

The design keeps the existing local-first smoke helper as the single release
gate. It uses the checked-in CSV sample, temporary config/data/report/export
directories, and existing CLI commands. The sample rows will be adjusted to
match the starter entity config without loosening entity matching rules or
changing scoring thresholds.

The smoke script will add small semantic validators around outputs it already
produces:

- sample CSV contract
- community candidate previews
- import command stdout
- imported signal summary and review JSON
- daily report JSON and Markdown
- candidates JSON
- trends JSON
- directory handoff preview and import dry-run stdout

The validators will assert deterministic facts from the sample, not broad
production behavior. They will prefer content-based checks such as expected
titles, URLs, entity names, row counts, platform counts, and report/trend
presence over brittle implementation details such as SQLite row IDs or complete
serialized payload equality.

## Tech Stack

- Python 3.11+
- Typer CLI through `python -m fashion_radar`
- Existing Pydantic output models where helpful:
  - `DailyReport`
  - `TrendComparison`
- Existing local SQLite pipeline:
  - `init`
  - `migrate-db`
  - `import-signals`
  - `match`
  - `report`
  - read-only review commands
- `pytest` for focused validator and contract tests
- `ruff` for lint and formatting
- `uv` with public lock validation via `UV_NO_CONFIG=1`

No new dependency is required.

## Sample Contract

`examples/community-signals.example.csv` remains a two-row sanitized local
handoff example. The rows will become:

- `The Row Margaux tote interest`
- `Ballet flats footwear mention`

The first row will include `The Row Margaux`, `handbag`, and `tote` context so
it matches both the starter `The Row` brand and `The Row Margaux` product. The
second row will include `ballet flats`, `shoes`, and `footwear` context so it
matches the starter `Ballet Flats` category. This keeps starter entity matching
strict while making first-run output useful.

Expected first-run semantic output:

- exactly two sample rows are linted, dry-run validated, and imported
- after the local `match` command runs, imported summary reports
  `row_count == 2`, `matched_count == 2`, `unmatched_count == 0`, and
  `platform_counts == {"community": 2}`
- after the local `match` command runs, imported signal review contains the two
  sample rows in newest-first order and marks both rows as matched
- the report contains exactly these sample entity signals:
  - `The Row`
  - `The Row Margaux`
  - `Ballet Flats`
- report metadata has `item_count == 3`
- report Markdown includes the expected entity sections and does not say
  `No entity signals in this window.`
- candidates remain an empty list because both sample phrases are configured
  starter entities, not new untracked candidates
- trends include entity deltas for the same three sample entities
- directory handoff preview sees one file and two rows
- directory import dry-run reports one valid file, two import-ready rows,
  community platform counts, and zero errors

## Implementation Method

The implementation should be small and release-gate focused:

1. Update the checked-in CSV sample and its contract test expectations.
2. Add validator helpers in `scripts/check_first_run_smoke.py`.
3. Wire validators into `run_first_run_flow()` at the points where payloads are
   already parsed or stdout is already available.
4. Update unit tests with passing and failing fixtures for the new validators.
5. Update docs so README, first-run guide, upload checklist, and CLI reference
   describe the strengthened sample-output contract.
6. Run source and installed first-run smoke checks to prove the new gate works
   in both modes.

The smoke helper must remain deterministic and local. It must not run
`collect`, `run`, `dashboard`, scraping/crawling, browser automation, account
login, cookies/sessions, source/platform connectors, platform automation, or
external services.

Repository publishing is outside the smoke helper and outside the product
runtime. If this implementation node is uploaded to GitHub, that upload is a
separate user-authorized release step after local verification and local Claude
Code review, not a requirement of the first-run smoke itself.

## Error Handling

Each validator should raise `SmokeError` with a specific command or artifact
name and a concise explanation. Examples:

- `sample CSV must contain exactly two rows`
- `imported-signals must contain sample title: The Row Margaux tote interest`
- `report JSON must contain sample entity: Ballet Flats`
- `trends must contain entity delta: The Row Margaux`

The smoke script should preserve its existing behavior of checking that default
repo-local `data/` and `reports/` artifacts are unchanged even if the flow
fails.

## Test Strategy

Focused tests:

- sample CSV validator accepts the checked-in sample shape and rejects missing
  titles or wrong row counts
- import stdout validators reject missing dry-run or import row lines
- imported summary validator rejects empty or unmatched summaries
- imported signals validator rejects missing sample rows or unmatched rows
- report validator rejects parseable but empty reports
- candidates validator rejects non-empty candidates for this starter-entity
  sample
- trends validator rejects missing entity deltas
- directory validators reject wrong file/row counts and missing dry-run lines
- command-sequence test stubs realistic payloads that satisfy semantic
  validators
- community signal import contract test updates expected sample titles and URLs

Release verification:

- focused pytest for first-run and community-signal contract tests
- source first-run smoke
- full pytest
- ruff check and format check
- public lock check
- mirror sync and no-config sync check
- release hygiene
- package build and archive check
- installed-wheel first-run smoke

## Scope Boundaries

This stage does not add social-platform ingestion, scraping, crawling, browser
automation, platform API calls, account/session/cookie handling, proxy use,
anti-bot bypass, or a compliance-review feature. It only strengthens the local
deterministic first-run sample gate and documentation.
