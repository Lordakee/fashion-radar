You are reviewing the current working tree for Stage 27A.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar community-candidates`, a local read-only command that
previews aggregate candidate phrases from one user-supplied community signal
CSV/JSON file before import.

Approved plan:

- `docs/reviews/claude-code-stage-27-plan-rereview.md`
- `docs/superpowers/specs/2026-06-13-stage-27-community-candidate-preview-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27-community-candidate-preview-plan.md`

Important context:

- This is Stage 27A: implementation plus focused tests only. Broad docs updates,
  final release verification, commit, and push are intentionally out of scope
  for this node.
- The current worktree still has a pre-existing `uv.lock` mirror URL diff. Treat
  `uv.lock` as out of scope unless you see a new dependency or lockfile
  requirement, which should not exist.
- Stage 27A should read one local file and local config only. It must not add
  live collection, platform APIs, account automation, directory watching,
  recursive file discovery, SQLite reads/writes, config writes, report/dashboard
  writes, candidate approval state, or entity YAML draft generation.
- The command may output aggregate candidate phrases and counts. It must not
  output local file paths, row URLs, row titles, summaries, raw text, normalized
  keys, candidate contexts, source files, import paths, account/private fields,
  or representative item details.

Relevant changed/added files:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`
- Stage 27A plan/review docs under `docs/superpowers/` and `docs/reviews/`

Review focus:

1. The new module uses `load_manual_signal_rows()`,
   `extract_candidate_phrases()`, `configured_entity_keys()`,
   `ScoringSettings`, and `CandidateDiscoverySettings` consistently with the
   approved plan.
2. The CLI validates invalid `--input-format`, invalid `--format`, negative
   `--limit`, and invalid `--as-of` before reading the input file.
3. Invalid config exits before input-file read.
4. Invalid input-file errors do not echo local file paths or file names.
5. JSON and table output do not expose local file paths, row URLs, row titles,
   summaries, raw text, normalized keys, contexts, representative items, source
   files, import paths, account/private fields, or hidden row-level values.
6. The command does not open SQLite, initialize schema, write config/data/report
   artifacts, touch dashboard state, collect sources, recurse directories, or
   call external services.
7. Candidate counts, current/baseline windows, fallback source name behavior,
   known entity suppression, review thresholds, single-token thresholds,
   disabled candidate discovery, per-row duplicate suppression, `limit=0`, and
   table sanitization are tested.
8. No broad docs/release/commit/push work was mixed into Stage 27A.

Verification already run:

```bash
.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q -k "community_candidates"
.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_manual_signal_import.py tests/test_candidate_scoring.py -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
rg -n "create_sqlite_engine|create_readonly_sqlite_engine|initialize_schema|store_manual_signal_rows|dashboard|report|schedule|watch|crawler|scrape|platform API|source acquisition" src/fashion_radar/community_candidates.py
```

The final `rg` command exits `1` because it finds no matches.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block Stage 27A completion and must be fixed.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 27A COMPLETION`.
