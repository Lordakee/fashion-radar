Review Stage 29 docs-only changes before commit and push.

Repository: `/home/ubuntu/fashion-radar`

Changed files to review:

- `README.md`
- `CHANGELOG.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- Stage 29 plan/review docs under `docs/superpowers/` and `docs/reviews/`

Goal:

Document the Stage 28 `fashion-radar community-candidates-dir DIRECTORY`
command accurately. The command previews aggregate candidate phrases from
local sanitized community signal files directly under one supplied directory,
before import.

Hard boundaries:

- Docs-only node.
- No code, tests, configs, dependency, or `uv.lock` changes should be required.
- The command is local and read-only.
- The command reads matched regular CSV/JSON files directly under one supplied
  local directory.
- The command does not recurse.
- The command is pre-import only.
- The command emits aggregate-only candidate phrase metrics.
- The command does not import rows, open/write SQLite, fetch URLs, log in,
  download media, write reports, update dashboards, generate entity files,
  create configs, schedule work, watch folders, add source/platform
  connectors, scrape platforms, monitor platforms, prove demand, verify
  platform coverage, rank sources, or perform source acquisition.

Review these specific risks:

1. Documentation must not imply platform coverage, proof of demand, source
   ranking, source acquisition, acquisition workflows, source collection,
   source connectors, scraping, monitoring, watching, scheduling, database
   import, database writes/state, report writing/generation, dashboard
   updates/generation, or entity YAML/entity file generation.
2. Documentation must explicitly preserve output exclusions: no supplied
   directory path, matched file paths, matched file names, row URLs, row titles,
   summaries, raw text, normalized keys, candidate contexts, raw validation
   findings, account/private fields, or representative item details.
3. Documentation should direct users to lint and dry-run import commands before
   actual import, without saying `community-candidates-dir` itself validates,
   imports, or stores rows.
4. Documentation should remain consistent with existing source-boundary
   language for community/social support as local sanitized file handoff only.
5. Confirm no code/test/config/dependency/`uv.lock` changes are part of this
   Stage 29 docs-only commit.

Verification already run:

- `git diff --name-only -- . ':!uv.lock'`
- `git diff --cached --name-only -- . ':!uv.lock'`
- `git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py`
- `git diff --cached -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py`
- `git status --short -- uv.lock`
- `git diff --cached -- uv.lock`
- `git diff --check`
- `git diff --cached --check`
- `rg -n "community-candidates-dir" README.md CHANGELOG.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md`
- `rg -n "matched regular files directly under one local directory|does not recurse|aggregate-only|supplied directory path|matched file paths|matched file names|raw validation findings" README.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md`
- unsafe implication scan over the Stage 29 docs diff for platform coverage,
  proof/source ranking/acquisition, scraping, monitoring, scheduling, database,
  report, dashboard, and entity-generation terms. Matches were negative
  boundary language only.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 29 DOCS COMMIT AND PUSH`.
