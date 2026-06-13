# Claude Code Stage 22 Code Review Prompt

You are reviewing Stage 22 for `/home/ubuntu/fashion-radar` in read-only mode.
Do not edit files. Use maximum reasoning.

## Goal

Stage 22 adds `fashion-radar imported-signals-summary`, a local read-only
command that summarizes currently retained `manual_import` rows by stored
source-name label.

## Current Working Tree

Review the current working tree, including untracked Stage 22 process docs.
Useful commands:

```bash
git status --short
git diff -- src/fashion_radar/imported_signals.py src/fashion_radar/cli.py tests/test_imported_signals.py tests/test_cli.py README.md docs CHANGELOG.md
```

## Scope Guard

Keep review recommendations inside the local SQLite imported-signal summary
boundary. Do not propose new ingestion paths, background workflows, external
integrations, scoring/report/dashboard changes, migrations, or dependencies.

## Review Focus

Check:

1. The command reads only existing local SQLite and `manual_import` rows.
2. Missing database and invalid CLI format do not create data/config/report
   artifacts.
3. Existing databases are opened read-only and are not initialized, migrated,
   imported, matched, scored, reported, or otherwise mutated.
4. Source summaries count retained local rows by source-name label and
   item-level stored match presence; multiple entity matches for one item do
   not inflate matched-row counts.
5. Source rows are sorted by stored `source_name`, not by count or rank.
6. Table and JSON contracts are deterministic and do not expose URLs, titles,
   summaries, imported source file paths, raw rows, or internal match fields;
   the existing-style top-level `database` field is allowed.
7. Docs remain bounded to retained local rows and stored source-name labels.
8. Tests are focused and deterministic.

Recent local checks already run:

```bash
.venv/bin/python -m pytest tests/test_imported_signals.py tests/test_cli.py tests/test_db.py -q -k "imported_signals_summary or imported_signals or readonly"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 22 release checks`
- `Not approved`
