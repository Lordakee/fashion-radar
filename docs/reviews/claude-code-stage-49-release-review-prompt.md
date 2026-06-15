You are Claude Code performing the required Stage 49 release review for
/home/ubuntu/fashion-radar.

Use maximum reasoning. Do not browse the network. Do not modify files.

Stage 49 objective:
- Add a tested first-run onboarding guide and tighten public docs so new GitHub
  users can choose between source checkout smoke, installed-wheel smoke,
  manual repo-local sample output, dashboard inspection, and reset.

Changed files:
- docs/first-run.md
- README.md
- docs/cli-reference.md
- docs/github-upload-checklist.md
- tests/test_cli_docs.py
- docs/superpowers/specs/2026-06-16-stage-49-first-run-onboarding-guide-design.md
- docs/superpowers/plans/2026-06-16-stage-49-first-run-onboarding-guide-plan.md
- docs/reviews/claude-code-stage-49-plan-review-prompt.md
- docs/reviews/claude-code-stage-49-plan-review.md
- docs/reviews/claude-code-stage-49-plan-rereview-prompt.md
- docs/reviews/claude-code-stage-49-plan-rereview.md

Implementation summary:
- Added `docs/first-run.md` as the canonical first-run onboarding guide.
- README now links the first-run guide, includes a chooser, states repository
  root preconditions, documents manual sample expected artifacts, clarifies
  automated smoke purpose/output, and points reset users to the guide.
- `docs/cli-reference.md` now links the first-run guide, explains consistent
  repo-local path flags, documents deterministic dated report paths, and states
  `scripts/check_first_run_smoke.py` is a checkout/release helper rather than a
  public `fashion-radar` CLI command.
- `docs/github-upload-checklist.md` now documents first-run smoke local-only
  boundaries and expected success line.
- `tests/test_cli_docs.py` now guards:
  - README links `docs/first-run.md`;
  - source checkout and installed-wheel smoke command strings appear in README,
    CI, upload checklist, and first-run guide;
  - first-run setup commands use repo-local paths and smoke through Typer;
  - first-run guide documents expected paths, dashboard command, reset warning,
    smoke boundaries, and no platform/browser/account/external service scope;
  - reset commands are a fixed narrow `rm -f` file list after a cheap repo-root
    guard;
  - upload checklist preserves the first-run smoke boundary paragraph.

Boundaries:
- Docs/tests only.
- No runtime code, dependency, lockfile, CI behavior, dashboard behavior,
  source/social connector, scraping/browser/account/session automation,
  external service, or compliance-review feature.
- No broad reset commands; reset uses exact file targets and warns about
  generated config edits.
- Process docs/review artifacts are intentionally part of Stage 49 scope because
  the user requires plan/review handoff records for each node.

Independent reviewer feedback already addressed:
- Important: reset guidance omitted SQLite sidecars and did not clearly say
  reset deletes local experiment state. Fixed in `docs/first-run.md`; added
  tests for `data/fashion-radar.sqlite-wal`,
  `data/fashion-radar.sqlite-shm`, and the local experiment state warning.
- Important: upload checklist boundary/success output lacked a focused drift
  guard. Added `test_upload_checklist_documents_first_run_smoke_boundary`.
- Important: first-run/reset commands needed explicit repository-root
  precondition. Added root-precondition text to README and `docs/first-run.md`,
  plus a reset guard command in the guide.
- Minor: first-run setup command helper was not section-scoped. Fixed by parsing
  only the `## Prepare A Source Checkout` section.
- Minor: reset command shape was under-tested. Added exact reset command list
  assertion that rejects broad directory deletion.

Claude Code release review feedback already addressed:
- Important: the reset root guard was initially a standalone command, so later
  `rm -f` commands would still run if the guard failed in a normal shell. Fixed
  `docs/first-run.md` so reset is one guarded compound command:
  `test -f pyproject.toml && test -d examples && { ... }`.
- Updated `test_first_run_guide_reset_commands_are_narrow_file_deletions` to
  assert that guarded compound command shape instead of a standalone guard.
- Important: dashboard first-run path flags were correct in docs but not fully
  tested. Added `test_first_run_guide_dashboard_command_uses_repo_local_paths`
  to assert the dashboard command includes `--config-dir "$PWD/configs"`,
  `--data-dir "$PWD/data"`, `--reports-dir "$PWD/reports"`,
  `--host 127.0.0.1`, and `--port 8501`.
- Minor: README first-run chooser omitted reset. Added a reset chooser bullet.
- Minor: upload checklist boundary test is now a normalized full-sentence
  assertion for the temporary-directory and no-collection/no-dashboard
  boundary.

Verification evidence:
- `UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_first_run_guide_reset_commands_are_narrow_file_deletions -q`
  Result: 1 passed.
- `UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q`
  Result: 20 passed.
- `UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py`
  Result: All checks passed.
- `UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py`
  Result: 1 file already formatted.
- `UV_NO_CONFIG=1 uv run pytest -q`
  Result: 778 passed.
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
- `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  Result: First-run sample smoke passed.
- Installed wheel verification:
  ```
  tmp_build="$(mktemp -d)"
  tmp_env="$(mktemp -d)"
  UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
  UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
  uv venv "$tmp_env/venv"
  uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
  "$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
  ```
  Result: package archives contain required files; installed smoke printed
  `First-run sample smoke passed.`
- `git diff --check`
  Result: passed.
- `git diff --cached --check`
  Result: passed.
- `git diff --quiet -- uv.lock`
  Result: passed; `uv.lock` unchanged.

Please return:
- Critical issues, Important issues, Minor issues.
- Whether any issue must block commit/push.
- If no Critical or Important issues remain, include exactly:
APPROVED FOR STAGE 49 COMMIT AND PUSH
