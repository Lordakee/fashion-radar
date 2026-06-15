Please review Stage 52 for Critical/Important issues before commit and GitHub
upload. Use a code-review stance: findings first, with file/line references.

Objective:
Add `fashion-radar community-handoff-manifest DIRECTORY`, a local print-only
producer manifest for external tools that write sanitized community signal
directories.

Implemented behavior:
- New `src/fashion_radar/community_handoff_manifest.py` module builds a
  Pydantic manifest from `build_community_signal_profile()` and
  `build_community_handoff_workflow()`.
- New CLI command prints table or JSON output.
- The command is print-only: it does not inspect directories, read handoff
  files, validate files, import rows, open SQLite, execute subprocesses, create
  artifacts, fetch URLs, call platform APIs, automate browsers, log in, store
  cookies/sessions, schedule/monitor/watch, or provide compliance review.
- JSON manifest includes profile-derived producer fields, nested workflow,
  storage guidance that warns about `--pattern "*.json"`, and stable key order
  tests.
- Docs and release checklist describe the command and storage warning.

Review scope:
- `CHANGELOG.md`
- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/github-upload-checklist.md`
- `docs/source-boundaries.md`
- `docs/superpowers/specs/2026-06-16-stage-52-community-handoff-manifest-design.md`
- `docs/superpowers/plans/2026-06-16-stage-52-community-handoff-manifest-plan.md`
- `docs/reviews/claude-code-stage-52-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-52-plan-review.md`
- `docs/reviews/claude-code-stage-52-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-52-plan-rereview.md`
- `src/fashion_radar/community_handoff_manifest.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_handoff_manifest.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`

Important prior reviewer findings already fixed:
- `src/fashion_radar/community_handoff_manifest.py` was reformatted for Ruff.
- `uv.lock` was restored; Stage 52 has no dependency or lockfile change.
- `CHANGELOG.md` now records `community-handoff-manifest`.

Verification already run:
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q`
  -> `817 passed`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .`
  -> `All checks passed!`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .`
  -> `108 files already formatted`
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  -> resolved successfully
- `git diff --check`
  -> no whitespace errors
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev`
  -> checked packages successfully
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check`
  -> would make no changes
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .`
  -> release hygiene checks passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"`
  -> source distribution and wheel built successfully
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"`
  -> package archives contain required files
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  -> first-run sample smoke passed
- Installed-wheel smoke:
  - built wheel
  - installed wheel into temp venv using
    `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install`
  - `scripts/check_first_run_smoke.py --installed` -> passed
  - installed `fashion-radar community-handoff-manifest ... --format json`
    parsed as JSON with expected contract version, print-only mode, workflow
    step count, and JSON storage warning

Please check especially:
1. The new command is truly print-only and no test accidentally masks path
   inspection caused by Typer or helper functions.
2. The manifest does not duplicate or diverge from the profile/workflow
   contracts.
3. JSON key order and storage guidance are stable enough for external local
   producer tools.
4. Public CLI docs, changelog, source boundaries, and upload checklist are
   synchronized.
5. No scraping/crawling/browser/account/cookie/session/platform API/compliance
   behavior or guidance was added.
6. `uv.lock` and generated runtime/build artifacts remain out of the change set.
