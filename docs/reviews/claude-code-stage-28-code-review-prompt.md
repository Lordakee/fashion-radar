Review Stage 28 before release commit and push.

Repository: `/home/ubuntu/fashion-radar`

Changed files to review:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`
- Stage 28/28B docs under `docs/superpowers/` and `docs/reviews/`

Goal:

`fashion-radar community-candidates-dir DIRECTORY` previews aggregate candidate
phrases from local sanitized community signal files directly under one supplied
directory, before import.

Hard boundaries:

- Local files and local config only.
- Read-only preview only.
- Non-recursive direct-child matching only.
- No source collectors, platform APIs, browser automation, account automation,
  watch folders, schedulers, SQLite writes, reports, dashboards, or entity YAML
  generation.
- No `uv.lock` commit.

Review these specific risks:

1. JSON/table output must not emit directory paths, file paths, filenames, row
   URLs, row titles, summaries, raw text, normalized keys, candidate contexts,
   validation findings, source paths, import paths, account/private fields, or
   representative item details.
2. Invalid directory, no matching files, invalid files/rows, and unexpected
   exceptions must use generic errors without leaking paths, filenames, row
   values, validation internals, or tracebacks.
3. Invalid `--as-of`, invalid `--input-format`, and negative `--limit` must
   fail before config load and directory read; invalid config must fail before
   directory read.
4. Tests should cover multi-file aggregation, direct-child matching, custom
   pattern behavior, matching directories ignored, no recursion, parity with
   single-file preview, source fallback, missing `collected_at`, duplicate
   phrase suppression per row, configured entity suppression, thresholds,
   disabled discovery, `limit=0`, labels/scores/tie-breaks, CLI output safety,
   clean errors, and no artifacts.

Verification already run:

- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
- `.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q` -> `200 passed`
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m ruff format --check .`
- `git diff --check`
- diff-based high-risk keyword scan
- untracked artifact scan

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit and push.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 28 RELEASE COMMIT AND PUSH`.
