You are Claude Code performing the required Stage 47 release review for the
Fashion Radar repository at /home/ubuntu/fashion-radar.

Use maximum reasoning. Review the current uncommitted working tree for Stage 47.
Do not browse the network. Do not modify files. Focus on correctness, release
readiness, deterministic behavior, and whether this is safe to commit and push.

Stage 47 objective:
- Add a deterministic local-only first-run sample smoke for GitHub users.
- The smoke must run from a source checkout, use checked-in
  examples/community-signals.example.csv, use temporary runtime directories,
  and avoid live collection, scraping, browser automation, account/session
  tooling, schedulers, monitors, dashboards, external services, and platform
  connectors.
- The smoke must not create, modify, or delete repo-default data/ or reports/
  files.
- The public lockfile must remain mirror-free. Mirror usage is only a local
  install/sync aid.

Changed/new files to review:
- scripts/check_first_run_smoke.py
- tests/test_first_run_smoke.py
- .github/workflows/ci.yml
- README.md
- docs/community-signal-import.md
- docs/github-upload-checklist.md
- tests/test_cli_docs.py
- scripts/check_package_archives.py
- tests/test_package_archives.py
- docs/superpowers/specs/2026-06-15-stage-47-first-run-sample-smoke-design.md
- docs/superpowers/plans/2026-06-15-stage-47-first-run-sample-smoke-plan.md
- docs/reviews/claude-code-stage-47-plan-*.md

Implementation summary:
- Added scripts/check_first_run_smoke.py, stdlib-only.
- Uses AS_OF="2026-06-13T12:00:00Z" and SOURCE_NAME="Community Tool Export".
- Runs CLI as python -m fashion_radar with cwd fixed to repo root and PYTHONPATH
  prepended with repo_root/src.
- Builds temp config/data/reports/exports dirs via tempfile.TemporaryDirectory.
- Copies examples/community-signals.example.csv to temp exports for directory
  handoff checks.
- Runs local commands only: init, migrate-db, doctor, community-signal-lint,
  community-candidates --format json, import-signals --dry-run, import-signals
  with --imported-at AS_OF, imported-signals-summary --format json,
  imported-signals --format json, match, report, candidates --format json,
  trends --format json, community-handoff-workflow, community-signal-lint-dir,
  community-candidates-dir --format json, and import-signals-dir --dry-run.
- Verifies JSON outputs, at least one imported summary row, temp workspace
  directories and SQLite, non-empty generated report files, valid report JSON,
  and unchanged repo-default data/reports content.
- The repo-default data/reports guard now hashes existing files and fails on
  created, changed, or deleted default files.
- CI runs the smoke after release hygiene with:
  UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
- README now separates "Manual Repo-Local Sample Flow" from "Automated
  First-Run Smoke" so users do not confuse repo-local manual output with the
  temporary automated smoke.
- docs/community-signal-import.md now separates deterministic checked-in sample
  commands from user-owned JSON/export examples with current timestamps.
- sdist archive checks now require scripts/check_first_run_smoke.py.

Earlier plan review:
- Stage 47 plan rereview approved in
  docs/reviews/claude-code-stage-47-plan-rereview.md with:
  APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE

Review feedback already addressed before this release review:
- Default data/reports guard was upgraded from new-file-only to content hash
  comparison that detects created, changed, and deleted files.
- Added tests for created/changed/deleted default artifacts.
- Added a command-sequence unit test that monkeypatches run_cli, captures the
  exact ordered smoke commands, fakes JSON stdout, creates expected temp report
  files, and asserts fixed AS_OF/source-name/temp-path behavior.
- Added workspace artifact assertion for temp config/data/reports dirs and
  temp SQLite.
- Added sdist archive requirement for scripts/check_first_run_smoke.py.
- Strengthened docs tests around the first-run smoke command, README smoke
  boundary wording, checked-in sample import docs, and deterministic review
  commands.

Fresh verification evidence:
- UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_package_archives.py -q
  Result: 53 passed.
- UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
  Result: First-run sample smoke passed.
- UV_NO_CONFIG=1 uv run ruff check scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_package_archives.py
  Result: All checks passed.
- UV_NO_CONFIG=1 uv run ruff format --check scripts/check_first_run_smoke.py scripts/check_package_archives.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_package_archives.py
  Result: 5 files already formatted.
- UV_NO_CONFIG=1 uv run pytest -q
  Result: 753 passed.
- UV_NO_CONFIG=1 uv run ruff check .
  Result: All checks passed.
- UV_NO_CONFIG=1 uv run ruff format --check .
  Result: 104 files already formatted.
- UV_NO_CONFIG=1 uv lock --check
  Result: Resolved 84 packages; lockfile check passed.
- UV_NO_CONFIG=1 uv sync --locked --dev --check
  Result: Would make no changes.
- UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
  Result: Would make no changes.
- UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
  Result: Release hygiene checks passed.
- tmp_build="$(mktemp -d)"; UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"; UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
  Result: sdist/wheel built; package archives contain required files.
- git diff --check
  Result: passed.
- git diff --cached --check
  Result: passed.
- git diff --quiet -- uv.lock
  Result: passed; uv.lock unchanged.

Please return:
- Critical issues, Important issues, Minor issues.
- Whether any issue must block commit/push.
- If no Critical or Important issues remain, include exactly this line:
  APPROVED FOR STAGE 47 COMMIT AND PUSH
