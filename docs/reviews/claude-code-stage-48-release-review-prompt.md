You are Claude Code performing the required Stage 48 release review for
/home/ubuntu/fashion-radar.

Use maximum reasoning. Do not browse the network. Do not modify files.

Stage 48 objective:
- Add an installed-wheel mode to the deterministic first-run smoke so the
  release gate proves the packaged CLI can run the same local sample flow as the
  source checkout.

Changed files:
- scripts/check_first_run_smoke.py
- tests/test_first_run_smoke.py
- .github/workflows/ci.yml
- README.md
- docs/github-upload-checklist.md
- tests/test_cli_docs.py
- docs/superpowers/specs/2026-06-15-stage-48-installed-wheel-first-run-smoke-design.md
- docs/superpowers/plans/2026-06-15-stage-48-installed-wheel-first-run-smoke-plan.md
- docs/reviews/claude-code-stage-48-plan-review*.md

Implementation summary:
- `SmokeContext` now records `source_checkout`.
- Source-checkout mode still prepends `repo_root/src` to `PYTHONPATH`.
- Installed mode does not prepend `repo_root/src`.
- Installed mode removes inherited `repo_root/src` from `PYTHONPATH`, including
  relative `src` entries resolved against `repo_root`, before subprocesses run.
- `run_cli()` now passes `context.source_checkout` to environment construction.
- `--installed` CLI flag builds a context with `source_checkout=False`.
- Installed mode preflights import origin with the target Python using
  structured JSON stdout and fails if `fashion_radar.__file__` resolves under
  `repo_root/src`.
- The first-run flow remains deterministic and local-only: checked-in
  `examples/community-signals.example.csv`, fixed
  `AS_OF=2026-06-13T12:00:00Z`, fixed source name, temp config/data/reports/
  exports dirs, and default repo data/reports hash guard.
- CI's installed-wheel step now runs:
  `"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed`
- README documents source-checkout smoke and installed-wheel smoke separately.
- Upload checklist documents the installed-wheel smoke command and source-tree
  import guard.
- Docs tests assert the source smoke command and installed smoke command appear
  in README, CI, and upload checklist.

Boundaries:
- No scraping, crawling, browser automation, account/cookie/session tooling,
  platform connectors, source acquisition, live collect, dashboard server
  launch, scheduler, monitor, external services, publishing, dependency changes,
  lockfile changes, schema changes, scoring changes, entity/source config
  changes, or compliance-review feature.

Plan review:
- First Claude Code plan review found one Important issue: installed mode could
  be source-contaminated via inherited `PYTHONPATH`.
- Plan was updated to remove inherited repo `src` and add import-origin
  preflight.
- Claude Code rereview approved the plan with:
  `APPROVED FOR STAGE 48 INSTALLED-WHEEL FIRST-RUN SMOKE`.

Independent subagent review feedback already addressed:
- Medium: relative `PYTHONPATH=src` contamination could be missed when invoked
  outside repo. Fixed by resolving relative PYTHONPATH entries against
  `repo_root`; added regression test.
- Medium: import-origin preflight trusted all stdout as one path. Fixed by
  emitting and parsing exactly one JSON line; added failure tests for empty,
  extra-line, invalid-JSON, and command-failure output.
- Low: `main --installed` wiring was not unit-tested. Added monkeypatched main
  test asserting preflight runs before smoke and context mode is false.
- Low: docs drift test did not assert installed command in README. Added README
  to the installed-command assertion loop.

Verification evidence:
- `UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q`
  Result: 43 passed.
- `UV_NO_CONFIG=1 uv run ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py`
  Result: All checks passed.
- `UV_NO_CONFIG=1 uv run ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py`
  Result: 3 files already formatted.
- `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  Result: First-run sample smoke passed.
- Installed wheel verification:
  ```
  tmp_build="$(mktemp -d)"
  UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
  UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
  tmp_env="$(mktemp -d)"
  uv venv "$tmp_env/venv"
  uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
  "$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
  ```
  Result: package archives contain required files; installed smoke printed
  `First-run sample smoke passed.`
- `UV_NO_CONFIG=1 uv run pytest -q`
  Result: 771 passed.
- `UV_NO_CONFIG=1 uv run ruff check .`
  Result: All checks passed.
- `UV_NO_CONFIG=1 uv run ruff format --check .`
  Result: 104 files already formatted.
- `UV_NO_CONFIG=1 uv lock --check`
  Result: passed.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check`
  Result: would make no changes.
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
  Result: would make no changes.
- `UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .`
  Result: Release hygiene checks passed.
- `git diff --check`
  Result: passed.
- `git diff --cached --check`
  Result: passed.
- `git diff --quiet -- uv.lock`
  Result: passed; uv.lock unchanged.
- `UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"` plus
  `UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"`
  Result: sdist/wheel built; package archives contain required files.

Please return:
- Critical issues, Important issues, Minor issues.
- Whether any issue must block commit/push.
- If no Critical or Important issues remain, include exactly:
  APPROVED FOR STAGE 48 COMMIT AND PUSH
