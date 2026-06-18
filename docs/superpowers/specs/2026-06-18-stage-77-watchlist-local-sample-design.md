# Stage 77 Watchlist Local Sample Design

## Goal

Add an optional expanded local community-signal sample that demonstrates the
existing `fashion-watchlist` entity pack across designer brands, named products,
categories, designers, celebrity style, and trend terms.

## Context

The default first-run sample intentionally stays small and deterministic. It
proves the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`
without changing source collection or requiring external services.

The optional entity pack already contains broader fashion coverage, including
brands such as `Khaite`, `Alaia`, `Loewe`, and `Miu Miu`; designers such as
`Jonathan Anderson`; celebrity style entities such as `Bella Hadid`; named
products such as `Alaia Le Teckel`, `Miu Miu Arcadie`, `Loewe Puzzle Bag`, and
`Khaite Lotus Bag`; categories such as `Mary Jane Shoes` and `East-West Bags`;
and trends such as `Boho Revival` and `Office Siren`.

The gap is user-facing demonstration, not runtime capability. A user can copy
the pack today, but the repo does not provide a larger checked-in local signal
file that proves the broader pack with the same deterministic import, match,
report, and trend workflow.

## Scope

In scope:

- Add one sanitized local CSV sample:
  `examples/community-signals.watchlist.example.csv`.
- Keep the default first-run sample unchanged.
- Add tests proving the new sample:
  - uses only the community-signal contract fields;
  - lints cleanly;
  - loads through the existing manual importer;
  - matches existing watchlist-pack entities across at least four entity types;
  - can be imported into a temporary local SQLite DB, matched, reported, and
    compared with `trends` using existing CLI commands.
- Add the new sample to sdist archive checks.
- Document an optional expanded watchlist sample path in `README.md`,
  `docs/first-run.md`, `docs/entity-packs.md`, and
  `docs/github-upload-checklist.md`.
- Add a changelog entry and staged review artifacts.

Out of scope:

- Any runtime CLI behavior change.
- Any change to default generated starter configs or first-run smoke
  expectations.
- Adding the optional sample to the producer profile's canonical
  `example_paths`.
- Live collection, scraping, browser automation, platform APIs, login/session/
  cookie/token/proxy behavior, media downloads, monitoring, scheduling, source
  acquisition, demand proof, ranking, coverage verification, or compliance
  review product features.
- Public lockfile or dependency changes. Local mirror installs should use
  environment variables or local config; public `uv.lock` must not gain
  mirror-bound URLs.

## Design

Create a CSV-only optional sample to minimize contract churn while following the
same field set as `examples/community-signals.example.csv`:

```text
url,title,published_at,summary,source_name,platform,source_weight,collected_at
```

Use eight synthetic `https://example.com/community-watchlist/...` rows with
`source_name` set to `Community Watchlist Sample`, `platform` set to
`community`, and UTC timestamps in June 2026. The rows should mention only
entities already present in `configs/entity-packs/fashion-watchlist.example.yaml`.

The sample should cover at least these expected matches:

- `Khaite` and `Khaite Lotus Bag`
- `Loewe` and `Loewe Puzzle Bag`
- `Jonathan Anderson`
- `Bella Hadid`
- `Alaia Le Teckel`
- `Miu Miu Arcadie`
- `Mary Jane Shoes`
- `Boho Revival`

The docs should present the sample as optional and repo-local:

1. Lint the entity pack.
2. Copy `configs/entity-packs/fashion-watchlist.example.yaml` to a temporary or
   repo-local `configs/entities.yaml`.
3. Lint `examples/community-signals.watchlist.example.csv`.
4. Import the sample locally.
5. Run `match`, `report`, and `trends` against the same local config/data/report
   directories.

Keep the wording explicit that this does not fetch URLs, collect platform data,
prove demand, rank brands, verify platform coverage, or add any connector.

## Test Strategy

Use test-first changes before adding the sample or docs:

- Add focused repository community-signal tests proving the new sample lints
  and loads cleanly. Keep the optional sample out of the canonical producer
  profile `example_paths` and out of the existing two-row example table. These
  tests should fail first because the file does not exist.
- Add a focused watchlist sample workflow test using `CliRunner` and temporary
  config/data/report directories. It should fail first because the sample file
  does not exist. After the sample is added, it proves the existing commands can
  import, match, report, and trend the optional watchlist sample without touching
  repo-local `data/` or `reports/`.
- Extend package archive required-path tests so the new sample is included in
  the sdist.
- Extend docs tests to require the optional sample commands and boundary
  language in README, first-run docs, and entity-pack docs.

## Acceptance Criteria

- `examples/community-signals.watchlist.example.csv` exists and contains only
  allowed community-signal fields.
- The sample has eight import-ready rows with source name `Community Watchlist
  Sample` and platform `community`.
- Tests prove the sample matches at least six existing watchlist-pack entities
  across at least four entity types, including at least one `product` and one
  `trend`.
- A temporary CLI workflow imports the sample, runs `match`, writes a report,
  runs `trends`, and finds expected watchlist entity names in report/trend JSON.
- The default first-run sample and first-run smoke expectations remain
  unchanged.
- The sample is present in source distributions.
- Public docs describe the optional expanded sample and its local-only boundary.
- `src/`, dependency manifests, and public `uv.lock` are not changed by this
  stage.
