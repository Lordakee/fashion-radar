# Stage 66 Code Review Prompt

Review the uncommitted Stage 66 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with `--variant max`.

## Goal

Stage 66 adds `external-tool-readiness`, a local read-only CLI command that
reports local upstream command availability and copyable Fashion Radar handoff
next steps for known free external/community tools.

## Files To Review

- `src/fashion_radar/external_tool_readiness.py`
- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_external_tool_readiness.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `tests/test_first_run_smoke.py`
- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-17-stage-66-external-tool-readiness-design.md`
- `docs/superpowers/plans/2026-06-17-stage-66-external-tool-readiness-plan.md`

## Required Contract

- `contract_version` is `external-tool-readiness/v1`.
- `execution_mode` is `local_read_only`.
- JSON key order is stable.
- Readiness checks use keys `name`, `status`, `command`, `path`, `detail`,
  `install_hint`.
- Check statuses are only `found`, `missing`, or `not_applicable`.
- `shutil.which` is resolved lazily, so tests can monkeypatch
  `readiness_module.shutil.which`.
- Concrete mirror-friendly hints are present where specified:
  - Rednote MCP: `registry.npmmirror.com` and `npm install -g rednote-mcp`
  - Instaloader/TikTokApi/yt-dlp: `pypi.tuna.tsinghua.edu.cn/simple`
  - Xiaohongshu crawler: upstream docs plus pip mirror guidance
- The command does not run adapters, upstream tools, subprocesses, imports,
  SQLite, file reads, directory inspection, or artifact creation.
- The generated `import-signals-dir` dry-run command includes
  `--imported-at <as_of> --dry-run`.
- First-run smoke executes and validates `external-tool-readiness`.
- Docs describe this as local read-only command availability guidance for
  user-controlled external/community tools producing sanitized CSV/JSON local
  file handoff rows.
- No compliance-review product feature is added.

## Verified Commands

These passed before this review:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
uv --no-config run --frozen pytest
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

## Review Format

Return findings first, ordered by severity:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.

Use file/line references. If no issues, say so clearly and mention residual
risk.
