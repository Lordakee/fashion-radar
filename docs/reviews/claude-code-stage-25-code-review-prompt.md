You are reviewing the current working tree for Stage 25.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar imported-candidates`, a local read-only command that surfaces
candidate phrases from retained `manual_import` rows only.

Important context:

- The existing `uv.lock` mirror URL diff is pre-existing and must remain
  unstaged/excluded. Do not treat `uv.lock` as part of Stage 25 unless you see a
  new dependency or lockfile requirement, which should not exist.
- Stage 25 must not add source acquisition, platform search, scraping, crawling,
  browser automation, account automation, scheduling, external service calls,
  SQLite writes, config writes, report/dashboard writes, or compliance/audit/policy
  workflows.
- `imported-candidates` may compute aggregate candidate review metrics in memory,
  but must not persist candidate rows, write scores, run entity matching, or
  generate reports.

Review focus:

1. Default candidate discovery behavior remains unchanged for existing callers.
2. `discover_candidates()` source filters are optional and only used by
   `imported-candidates`.
3. `query_imported_candidates()` opens existing SQLite through the read-only
   engine and returns an empty review for missing DB without creating dirs/files.
4. `imported-candidates` reads retained `manual_import` rows only and respects
   optional exact `source_name`.
5. JSON/table output uses the imported-candidate-specific aggregate model and
   does not expose representative items, source URLs, titles, summaries,
   contexts, normalized keys, item IDs, match internals, aliases, import paths,
   source files, account/private/raw fields, or hidden review text.
6. CLI validation avoids query execution for invalid `--as-of`, invalid
   `--format`, and invalid `--limit` where appropriate.
7. Tests adequately cover read-only behavior, missing DB behavior, invalid
   schema no traceback, no DB mutation, stable JSON keys, table sanitization,
   and broad report/trend/dashboard compatibility.
8. Docs remain local/read-only and do not imply verified entities, demand proof,
   external/platform coverage, source ranking, source quality, scraping,
   monitoring, or acquisition.

Relevant changed/added files:

- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/imported_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_candidate_scoring.py`
- `tests/test_imported_candidates.py`
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

Verification already run after implementation:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py tests/test_imported_candidates.py tests/test_cli.py -q -k "imported_candidates or source_type or candidates_command or trends_command"
.venv/bin/python -m pytest tests/test_reports.py tests/test_trends.py tests/test_dashboard.py -q -k "candidate or trend or build_daily_report"
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
  `APPROVED FOR STAGE 25 COMMIT`.
