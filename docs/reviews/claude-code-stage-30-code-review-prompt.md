Review Stage 30 implementation before commit and push.

Repository: `/home/ubuntu/fashion-radar`

Goal:

Add `fashion-radar community-handoff-workflow DIRECTORY`, a local print-only
command that prints a copyable command checklist for the directory community
signal handoff path:

1. `community-signal-lint-dir`
2. `community-candidates-dir`
3. `import-signals-dir --dry-run`
4. `import-signals-dir`
5. `imported-review-workflow`

Changed files to review:

- `src/fashion_radar/community_handoff_workflow.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_handoff_workflow.py`
- `tests/test_cli.py`
- `README.md`
- `CHANGELOG.md`
- `docs/architecture.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- Stage 30 design/plan/review files under `docs/superpowers/` and
  `docs/reviews/`

Hard boundaries:

- The new workflow command itself must be print-only.
- It must not execute generated commands.
- It must not read the supplied directory or inspect directory metadata.
- It must not validate files.
- It must not import rows.
- It must not open or write SQLite.
- It must not fetch URLs, log in, download media, run browser automation,
  scrape, monitor, watch folders, schedule work, add source/platform
  connectors, acquire sources, prove demand, verify platform coverage, rank
  sources, write reports, update dashboards, generate configs, or generate
  entity files.
- It may intentionally print supplied directory/config/data paths inside
  copyable local commands; docs/tests must make this distinction clear from
  aggregate candidate preview output.
- `uv.lock` must remain excluded.

Review focus:

1. Does the command truly only build/render a model and avoid execution/data
   access/side effects?
2. Is `directory: str` in the CLI acceptable and sufficient to avoid Typer Path
   metadata checks for this print-only command?
3. Are generated commands shell-quoted correctly, deterministic, and aligned
   with the actual CLI option names?
4. Are JSON keys stable and table output safe for pipe/newline characters?
5. Do tests prove no directory read/metadata/traversal for the supplied
   directory, no subprocess execution, no SQLite creation, no import/store,
   no source collection, no report writes, and no digest packaging?
6. Do docs avoid implying scraping, source acquisition, monitoring, scheduling,
   platform coverage, demand proof, or source ranking?
7. Is there any accidental code/test/config/dependency/`uv.lock` scope issue?

Verification already run:

- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
- `.venv/bin/python -m pytest tests/test_community_handoff_workflow.py tests/test_cli.py -q` -> `194 passed`
- `.venv/bin/python -m pytest -q` -> `572 passed`
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m ruff format --check .`
- `git diff --check`
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage30`
- Installed-wheel smoke:
  - `fashion-radar community-handoff-workflow --help`
  - `fashion-radar community-handoff-workflow /tmp/fashion-radar-wheel-stage30/missing --input-format csv --pattern "*.csv" --config-dir /tmp/fashion-radar-wheel-stage30/configs --data-dir /tmp/fashion-radar-wheel-stage30/data --as-of 2026-06-13T12:00:00Z --format json`
  - JSON assertion confirmed `execution_mode == "print_only"`, `step_count == 5`, and the data dir was not created.
- Boundary scan over Stage 30 diff for fetch/URL/login/download/browser/
  automation/scraping/monitoring/watch/schedule/source acquisition/platform
  coverage/demand/ranking/database/report/dashboard/config/entity terms; matches
  were negative boundary language or existing context.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 30 COMMIT AND PUSH`.
