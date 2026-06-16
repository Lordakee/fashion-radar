# Opencode Stage 55 Release Review Prompt

You are reviewing the completed Stage 55 changes in the `fashion-radar`
repository before commit and upload.

Required review mode:

- Review model: GLM 5.2 via local opencode
  (`zhipuai-coding-plan/glm-5.2`).
- This is a release review only.
- Do not edit files.
- Do not narrate tool usage or file-reading steps.
- Keep the response concise.
- Treat Critical and Important findings as blocking.

## Goal

Verify Stage 55 added checked-in external community tool export directory
examples and guardrails without adding runtime collection behavior.

## Files To Review

Review the current worktree diff and these new paths:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`
- `tests/test_community_tool_handoff_directory_examples.py`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/community-signal-import.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-16-stage-55-community-tool-directory-examples-design.md`
- `docs/superpowers/plans/2026-06-16-stage-55-community-tool-directory-examples-plan.md`
- `docs/reviews/opencode-stage-55-plan-review-prompt.md`
- `docs/reviews/opencode-stage-55-plan-review.md`
- `docs/reviews/opencode-stage-55-release-review-prompt.md`

## Required Checks

Confirm:

- the new directory examples are static, sanitized local CSV/JSON files only;
- each child CSV/JSON file contains one synthetic row/item using only existing
  community signal fields;
- sample URLs are under `https://example.com/...`, `source_name` is
  `External Community Tool`, and `platform` is `community`;
- no new CLI commands, schema fields, dependencies, lockfile changes, runtime
  connectors, scraping/crawling, browser automation, account/cookie/session
  handling, platform API clients, monitoring/scheduling, source acquisition,
  demand proof, ranking, or coverage verification functionality were added;
- docs and docs-drift tests cover the checked-in directory examples;
- the manifest docs show the current four profile `example_paths` only, and
  directory paths are documented separately;
- package archive checks require all five new directory example files in the
  sdist only;
- `uv.lock` is unchanged and mirror-free;
- no credentials, tokens, private data, generated artifacts, or `exports` path
  segment were introduced.

## Verified Commands

The following commands have been run in this workspace and exited 0:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_tool_handoff_directory_examples.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

## Required Output

Respond with:

- `## Critical Findings`
- `## Important Findings`
- `## Minor Findings`
- `## Verdict`

If and only if the release is acceptable to commit and upload, include this
exact phrase:

```text
APPROVED FOR STAGE 55 RELEASE
```
