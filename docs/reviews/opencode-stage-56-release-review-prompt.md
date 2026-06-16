# Stage 56 Release Review Prompt

You are the local release reviewer for `/home/ubuntu/fashion-radar`.

Model requested by the project owner: `zhipuai-coding-plan/glm-5.2`.

Do not edit files. Review the uncommitted Stage 56 changes only.

## Objective

Stage 56 adds a public local-only command:

```text
fashion-radar community-handoff-check-dir
```

The command should provide a single readiness report over an external community tool export directory by aggregating existing local operations:

- `community-signal-lint-dir`
- `community-candidates-dir`
- `import-signals-dir --dry-run`

It must not import rows, create SQLite files, write reports/dashboards/digests, create config/data artifacts, fetch URLs, call platform APIs, use accounts/cookies/sessions, use browser automation, scrape/crawl, monitor/watch/schedule, perform ranking/coverage proof, generate entities, or implement compliance/legal/approval/safety-review features.

## Expected Scope

Production changes should be limited to:

- `src/fashion_radar/community_handoff_check.py`
- `src/fashion_radar/cli.py`

Tests and docs changed for this feature:

- `tests/test_community_handoff_check.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/community-signal-import.md`
- `docs/cli-reference.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

Plan and review records:

- `docs/superpowers/specs/2026-06-17-stage-56-community-handoff-check-design.md`
- `docs/superpowers/plans/2026-06-17-stage-56-community-handoff-check-plan.md`
- `docs/reviews/opencode-stage-56-plan-review-prompt.md`
- `docs/reviews/opencode-stage-56-plan-review.md`

## Required Checks

Please inspect the diff and verify:

1. The command builds a read-only result from existing local helpers and does not introduce side effects.
2. Error handling is clean for invalid `--as-of`, missing/invalid config, invalid input directories, lint errors, strict warnings, and candidate-preview validation failures.
3. JSON/table output contracts are deterministic enough for tests and docs.
4. `community-signal-profile`, `community-handoff-workflow`, and `community-handoff-manifest` behavior and ordering did not gain `community-handoff-check-dir`.
5. Docs present the command as a local-only readiness report and do not imply unsupported platform or compliance features.
6. Tests include direct builder coverage, CLI coverage, docs drift coverage, no-side-effect coverage, and manifest/profile negative guards.
7. Dependency and lockfile state is unchanged and mirror-free.

## Fresh Verification Already Run by Codex

These commands have passed locally after formatting:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_check.py tests/test_cli.py tests/test_cli_docs.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_handoff_check.py src/fashion_radar/cli.py tests/test_community_handoff_check.py tests/test_cli.py tests/test_cli_docs.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_handoff_check.py tests/test_community_handoff_check.py tests/test_cli_docs.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Installed wheel smoke also passed using a temporary config directory copied from `configs/scoring.example.yaml` and `configs/entities.example.yaml`, including:

```bash
fashion-radar --help
fashion-radar community-handoff-check-dir --help
fashion-radar community-handoff-check-dir examples/community-tool-handoff-directory.example/csv --config-dir "$tmp_configs" --input-format csv --pattern '*.csv' --as-of 2026-06-13T12:00:00Z --source-name 'Community Tool Export' --limit 10 --format json
```

Two Codex read-only subagents also reviewed the release risk and found no Critical or Important issues. One docs reviewer noted a non-blocking Minor: the docs drift test could also lock boundary wording in `docs/cli-reference.md`, `docs/github-upload-checklist.md`, and `CHANGELOG.md`; current docs are correctly bounded.

## Output Format

Return:

- Critical findings
- Important findings
- Minor findings
- Verification commands you ran
- Final verdict

If there are no Critical or Important findings, include this exact approval line:

```text
APPROVED FOR STAGE 56 RELEASE
```
