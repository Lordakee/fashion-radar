You are reviewing the Stage 62 release for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Repository: /home/ubuntu/fashion-radar
Base commit: dc0c8d4cebd00c174886ebe839aec80fe9d09dab

Stage 62 objective:
- Add a local, print-only `fashion-radar external-tool-adapters` command.
- The command prints an external social/community tool adapter registry and
  local producer-discovery registry for user-controlled external/community
  tools that write sanitized CSV/JSON local file handoff rows.
- The registry maps future upstream tools such as Rednote/Xiaohongshu tools,
  Instaloader, TikTok-Api, yt-dlp, X/search exports, and generic community
  exports to the existing community signal handoff fields:
  url, title, published_at, summary, source_name, platform, source_weight,
  collected_at.
- The implementation must remain print-only. It may build command strings but
  must not inspect directories, read handoff files, validate files, import
  rows, open SQLite, create artifacts, install tools, fetch URLs, log in, store
  cookies, call platform APIs, automate browsers, monitor communities,
  schedule work, acquire sources, prove demand, rank sources, verify platform
  coverage, or perform compliance review.

Changed files to review:
- src/fashion_radar/external_tool_adapters.py
- src/fashion_radar/cli.py
- scripts/check_first_run_smoke.py
- tests/test_external_tool_adapters.py
- tests/test_cli.py
- tests/test_first_run_smoke.py
- tests/test_cli_docs.py
- README.md
- docs/community-signal-import.md
- docs/community-signal-quality.md
- docs/source-boundaries.md
- docs/architecture.md
- docs/cli-reference.md
- docs/github-upload-checklist.md
- AGENTS.md
- CHANGELOG.md
- docs/superpowers/specs/2026-06-17-stage-62-external-tool-adapter-registry-design.md
- docs/superpowers/plans/2026-06-17-stage-62-external-tool-adapter-registry-plan.md
- docs/reviews/opencode-stage-62-plan-review-prompt.md
- docs/reviews/opencode-stage-62-plan-review.md
- docs/reviews/opencode-stage-62-plan-rereview-prompt.md
- docs/reviews/opencode-stage-62-plan-rereview.md
- docs/reviews/opencode-stage-62-release-review-prompt.md

Verification already run:
- `uv run pytest tests/test_external_tool_adapters.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q` -> 347 passed.
- `uv run ruff check .` -> all checks passed.
- `uv run ruff format --check .` -> 115 files already formatted.
- `uv --no-config lock --check` -> resolved 84 packages, exit 0.
- `git diff --check` -> exit 0.
- `uv run pytest -q` -> 994 passed.
- `UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py` -> release hygiene checks passed.
- `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .` -> first-run sample smoke passed.
- `codegraph status` -> index up to date.
- `uv --no-config build --out-dir "$tmp_build"` -> wheel and sdist built.
- `python3 scripts/check_package_archives.py "$tmp_build"` -> package archives contain required files.
- Installed wheel smoke:
  `"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed`
  -> first-run sample smoke passed.
- Installed wheel command smoke:
  `"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --format json | "$tmp_env/venv/bin/python" -m json.tool`
  -> valid non-empty JSON.
- `rg -n "pypi.tuna|tsinghua" uv.lock` -> no matches after restoring lockfile.

Known verification note:
- Direct `uv build` without the global `--no-config` flag can rewrite
  `uv.lock` using the user's local uv mirror config at
  `/home/ubuntu/.config/uv/uv.toml`. The working tree `uv.lock` was restored,
  and release checks used `uv --no-config ...` for build/lock validation.

Please review:
1. Does the implementation satisfy Stage 62 without adding connectors,
   scraping, platform APIs, account/session/cookie behavior, media downloads,
   schema changes, storage writes, scheduler behavior, report/dashboard writes,
   demand proof, ranking, coverage verification, or compliance-review product
   features?
2. Is `external_tool_adapters.py` deterministic, correctly bounded, and aligned
   with the existing community signal contract?
3. Does the CLI command match existing Typer patterns and preserve print-only
   behavior?
4. Are tests and docs sufficient to prevent drift and accidental scope
   expansion?
5. Are there any Critical or Important issues that must be fixed before
   commit/push?

Return exactly:
- Verdict: APPROVED FOR STAGE 62 RELEASE or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
