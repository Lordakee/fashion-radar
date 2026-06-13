You are reviewing the current working tree for Stage 26.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar imported-candidate-evidence`, a local read-only command that
shows retained `manual_import` rows whose extracted candidate phrases match one
requested phrase.

Important context:

- The existing `uv.lock` mirror URL diff is pre-existing and must remain
  unstaged/excluded. Do not treat `uv.lock` as part of Stage 26 unless you see a
  new dependency or lockfile requirement, which should not exist.
- Stage 26 must not add source acquisition, platform search, scraping, crawling,
  browser automation, account automation, scheduling, external service calls,
  SQLite writes, config writes, report/dashboard writes, persistent candidate
  tables, candidate approval state, or entity YAML draft generation.
- The command intentionally exposes `title` and `url` for one requested phrase
  because it is a local evidence drilldown. It must still omit summaries, raw
  comments, candidate contexts, normalized candidate internals, match reasons,
  match confidence, aliases, import paths, source files, account fields, cookies,
  sessions, and private/raw fields.

Review focus:

1. Candidate evidence uses `extract_candidate_phrases()` and `candidate_key()`
   semantics, not naive substring matching.
2. Default candidate discovery behavior remains unchanged.
3. The new public helper wrappers in `discovery/candidates.py` safely delegate
   to existing semantics.
4. `query_imported_candidate_evidence()` opens existing SQLite through the
   read-only engine and returns an empty review for missing DB without creating
   dirs/files.
5. Evidence reads retained `manual_import` rows only, applies the
   `baseline_window_start < collected_at <= as_of` review window, excludes
   future/old out-of-window rows, respects optional exact `source_name`, and
   treats blank source-name as no filter.
6. Known configured entities and stored entity matches suppress known phrases
   consistently with candidate discovery.
7. JSON/table output contracts are stable and do not expose summaries, raw
   fields, candidate contexts, match internals, import paths, source files,
   account/private fields, or hidden review text.
8. CLI validation avoids query execution for missing/blank `--phrase`, invalid
   `--as-of`, invalid `--format`, and invalid `--limit` where appropriate.
9. Docs remain local/read-only and do not imply verified entities, demand proof,
   external/platform coverage, source ranking, source quality, scraping,
   monitoring, or acquisition.

Relevant changed/added files:

- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/imported_candidate_evidence.py`
- `src/fashion_radar/cli.py`
- `tests/test_candidate_scoring.py`
- `tests/test_imported_candidate_evidence.py`
- `tests/test_cli.py`
- `README.md`
- `docs/candidate-discovery.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- Stage 26 plan/spec/review docs under `docs/superpowers/` and `docs/reviews/`

Verification already run after implementation:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py tests/test_imported_candidate_evidence.py tests/test_cli.py -q -k "candidate_key or stored_entity_candidate_keys or imported_candidate_evidence"
.venv/bin/python -m pytest tests/test_imported_candidates.py tests/test_reports.py tests/test_trends.py tests/test_dashboard.py -q -k "imported_candidates or candidate or trend or build_daily_report"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

The final command exits `1` because it finds no matches.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit/push and must be fixed.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 26 COMMIT`.
