# Opencode Stage 54 Release Review Prompt

You are reviewing the Stage 54 release candidate for the `fashion-radar`
repository.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a release review only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blockers.

## Goal

Add sanitized, importable external tool handoff templates for future
user-controlled community/social tools while preserving Fashion Radar's local
CSV/JSON import boundary.

## Expected Technical Approach

- Add `examples/community-tool-handoff.example.csv`.
- Add `examples/community-tool-handoff.example.json`.
- Keep both examples synthetic, importable, `example.com`-only, and limited to
  existing community signal schema fields.
- Add those two paths to `COMMUNITY_SIGNAL_EXAMPLE_PATHS` and regenerate
  `examples/community-signal-profile.example.json`.
- Make the paths visible through existing profile/manifest surfaces only.
- Do not add a new command, schema change, dependency, lockfile change,
  connector, scraper, browser automation, platform API client, source
  acquisition, monitoring, scheduling, source ranking, demand proof, platform
  coverage verification, compliance-review feature, legal-review feature, or
  approval UI.
- Update tests, docs, package archive checks, and review artifacts.

## Files Changed Or Added In This Stage

- Modified: `AGENTS.md`
- Modified: `CHANGELOG.md`
- Modified: `README.md`
- Modified: `docs/architecture.md`
- Modified: `docs/community-signal-import.md`
- Modified: `docs/github-upload-checklist.md`
- Modified: `docs/source-boundaries.md`
- Modified: `examples/community-signal-profile.example.json`
- Modified: `scripts/check_package_archives.py`
- Modified: `src/fashion_radar/community_signal_profile.py`
- Modified: `tests/test_cli.py`
- Modified: `tests/test_cli_docs.py`
- Modified: `tests/test_community_handoff_manifest.py`
- Modified: `tests/test_community_signal_import_contract.py`
- Modified: `tests/test_community_signal_lint.py`
- Modified: `tests/test_community_signal_profile.py`
- Modified: `tests/test_package_archives.py`
- Added: `docs/superpowers/specs/2026-06-16-stage-54-external-tool-handoff-templates-design.md`
- Added: `docs/superpowers/plans/2026-06-16-stage-54-external-tool-handoff-templates-plan.md`
- Added: `docs/reviews/opencode-stage-54-plan-review-prompt.md`
- Added: `docs/reviews/opencode-stage-54-plan-review.md`
- Added: `docs/reviews/opencode-stage-54-release-review-prompt.md`
- Added after this prompt runs: `docs/reviews/opencode-stage-54-release-review.md`
- Added: `examples/community-tool-handoff.example.csv`
- Added: `examples/community-tool-handoff.example.json`

## Implementation Summary

- `COMMUNITY_SIGNAL_EXAMPLE_PATHS` now lists:
  - `examples/community-signals.example.csv`
  - `examples/community-signals.example.json`
  - `examples/community-tool-handoff.example.csv`
  - `examples/community-tool-handoff.example.json`
- The generated profile JSON was regenerated from
  `build_community_signal_profile()`.
- Contract tests cover all four examples for schema-field compatibility,
  lint-clean status, dry-run import, no artifact writes, `example.com` URLs, and
  `platform == "community"`.
- Profile/manifest/CLI tests freeze the new four-path output.
- Package archive checks require both new template files and include negative
  regressions for missing CSV and missing JSON templates.
- Docs link the templates from README, community import docs, and upload
  checklist, and describe the feature as sanitized CSV/JSON local file handoff
  only.
- Public docs use stable product wording instead of requiring users to
  understand the internal stage number.
- New Stage 54 review records use `opencode-stage-54-*`; earlier
  `claude-code-stage-54-*` draft files were removed from the worktree to avoid
  conflicting review authority for this node.

## Verification Evidence Already Run

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
# 120 passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
# 55 passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
# 895 passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
# All checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
# 108 files already formatted

git diff --check
# clean

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 84 packages

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
# Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
# Would make no changes

if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
# no matches

git diff --exit-code -- uv.lock
# clean

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed

tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
# Package archives contain required files

tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
# First-run sample smoke passed
```

## Review Questions

1. Are the two new example templates sanitized, importable, synthetic, and
   limited to existing schema fields?
2. Is profile/manifest discoverability correctly updated without adding a new
   CLI command or runtime collection behavior?
3. Do package archive checks require both new templates?
4. Do docs describe a local file handoff template without implying platform
   collection, source acquisition, scraping, browser automation, platform APIs,
   monitoring, scheduling, compliance-review features, demand proof, ranking, or
   coverage verification?
5. Is `uv.lock` unchanged and mirror-free?
6. Are there any Critical or Important issues that should block commit and push?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if this release candidate is acceptable to commit and push, include
this exact phrase:

```text
APPROVED FOR STAGE 54 COMMIT AND PUSH
```
