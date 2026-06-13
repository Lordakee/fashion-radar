# Stage 29 Community Candidate Directory Docs Design

## Goal

Document `fashion-radar community-candidates-dir` as a local, read-only,
non-recursive, aggregate-only pre-import candidate phrase preview for batches of
community signal handoff files.

## Scope

Stage 29 is documentation only. It may update:

- `README.md`
- `CHANGELOG.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`

It must not modify production code, tests, configs, dependencies, generated
artifacts, or `uv.lock`.

## Documentation Requirements

Docs should describe `community-candidates-dir` as:

- reading matched regular files directly under one local directory;
- using `--input-format`, `--pattern`, `--config-dir`, `--as-of`,
  `--source-name`, `--limit`, and `--format`;
- non-recursive;
- local and read-only;
- pre-import and in-memory;
- aggregate-only;
- not opening SQLite;
- not importing rows;
- not writing reports/dashboards/config/entity files;
- not fetching URLs;
- not collecting sources;
- not a source connector or acquisition workflow.

Docs must state that output does not include:

- supplied directory path;
- matched file paths;
- matched file names;
- row URLs;
- row titles;
- summaries/raw text;
- normalized keys;
- candidate contexts;
- raw validation findings;
- account/private fields;
- representative item details.

Docs should position the command after `community-signal-lint-dir` and before
`import-signals-dir --dry-run` for batch pre-import review.

## Verification

Because this is docs-only, verification should prove:

- only approved docs changed;
- `uv.lock` remains unstaged/uncommitted;
- docs contain `community-candidates-dir` examples and boundary language;
- docs do not imply scraping, social-platform coverage, source acquisition,
  schedulers/watchers, database import, report/dashboard generation, or entity
  YAML generation;
- `git diff --check` passes.
