# Opencode Stage 63 Release Review Prompt

Repository: `/home/ubuntu/fashion-radar`
Base commit before Stage 63: `cdb0535cadf9d05373b7684991d5e4ca425d48f0`

Please perform a release review for Stage 63 using model
`zhipuai-coding-plan/glm-5.2` with variant `max`.

## Objective

Stage 63 adds a local, print-only `fashion-radar external-tool-template`
command. The command prints adapter-specific template rows for user-controlled
external/community tools that need sanitized CSV/JSON local file handoff
examples.

Expected contract:

- `--adapter` is optional.
- With `--adapter`, output contains two synthetic rows for that adapter.
- Without `--adapter`, output contains two synthetic rows for each of the seven
  known adapters, so JSON has 14 importable rows.
- `--format json` outputs only importable community handoff JSON:
  `{"items": [...]}`.
- `--format csv` outputs only the eight-field community signal CSV:
  `url,title,published_at,summary,source_name,platform,source_weight,collected_at`.
- `--format table` may include local metadata, adapter ids, CSV header, item
  values, field mappings, recommended local commands, and boundaries.
- The command must not read handoff files, inspect directories, write files,
  open SQLite, run adapters, call upstream tools, scrape, use browser
  automation, call platform APIs, monitor, schedule, acquire sources, rank,
  prove demand, or verify platform coverage.

## Stage 63 Files

Modified files:

- `AGENTS.md`
- `CHANGELOG.md`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/github-upload-checklist.md`
- `docs/source-boundaries.md`
- `scripts/check_first_run_smoke.py`
- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `tests/test_first_run_smoke.py`

New files:

- `docs/reviews/opencode-stage-63-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-63-plan-rereview.md`
- `docs/reviews/opencode-stage-63-plan-review-prompt.md`
- `docs/reviews/opencode-stage-63-plan-review.md`
- `docs/reviews/opencode-stage-63-release-review-prompt.md`
- `docs/superpowers/plans/2026-06-17-stage-63-external-tool-template-plan.md`
- `docs/superpowers/specs/2026-06-17-stage-63-external-tool-template-design.md`
- `src/fashion_radar/external_tool_templates.py`
- `tests/test_external_tool_templates.py`

## Prior Review Notes

The initial opencode plan review required two fixes:

- Unfiltered output count must be 14, not 7.
- First-run smoke plan must explicitly update the fake command map, command
  order, and shifted captured-command indexes.

The opencode plan rereview approved implementation after those fixes.

Two later read-only subagent reviews found and we addressed:

- Table output omitted field mappings and default table output was too thin.
  The renderer now includes full per-adapter template detail and field mapping
  rows.
- First-run smoke fixture drifted from real synthetic Rednote rows. The test
  fixture now compares itself against the real template builder.
- A side-effect regression test now checks `external-tool-template` does not
  create supplied export/config/data directories or SQLite files.
- New Stage 63 plan docs no longer record the local token path or auth header
  construction.

## Verification Already Run

- `uv --no-config run --frozen pytest tests/test_external_tool_templates.py tests/test_first_run_smoke.py tests/test_cli.py tests/test_cli_docs.py -q`
  - Result: `358 passed`.
- `uv --no-config run --frozen ruff check .`
  - Result: passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `uv --no-config lock --check`
  - Result: passed.
- `uv --no-config run --frozen pytest -q`
  - Result: `1014 passed`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: `Release hygiene checks passed.`
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: `First-run sample smoke passed.`
- `codegraph status`
  - Result: index up to date.
- `env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv --no-config sync --frozen --dev --check`
  - Result: would make no changes.
- Exact token-pattern scan:
  `rg -n "ghp_[A-Za-z0-9_]+" . --glob '!.git/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'`
  - Result: no matches for the real repository token.
- Public lock mirror scan:
  `rg -n "pypi\\.tuna|tsinghua|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links" uv.lock`
  - Result: no matches.
- Package/installed-wheel smoke:
  - `UV_NO_CONFIG=1 uv --no-config build --out-dir "$TMP_BUILD"`
  - `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_package_archives.py "$TMP_BUILD"`
  - temporary venv install with `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`
  - installed first-run smoke
  - installed `external-tool-template --adapter instaloader --format table`
  - installed `external-tool-template --adapter instaloader --format json | python -m json.tool`
  - installed `external-tool-template --adapter instaloader --format csv`
  - `python -m fashion_radar --help`
  - Result: all passed.

## Review Request

Please review the current uncommitted Stage 63 worktree. Report findings first,
ordered by severity:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.

Focus on command contract, importable JSON/CSV output, table output, first-run
smoke integration, docs drift, release hygiene, token/mirror safety, and any
accidental platform collection or side effects.
