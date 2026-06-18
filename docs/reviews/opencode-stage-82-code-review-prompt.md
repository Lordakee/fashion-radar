Review Stage 82 of Fashion Radar.

Goal:
- Document the safe recovery path for a locally mirror-rewritten `uv.lock`.
- Add a docs drift test for that recovery guidance.
- Restore the working tree `uv.lock` to the public mirror-free version.

Expected changed files:
- docs/dependency-mirrors.md
- tests/test_cli_docs.py
- Stage 82 spec/plan/review artifacts

Expected current state:
- `uv.lock` has no working tree diff and no mirror URL markers.
- No runtime code or dependency manifest changes.

Review focus:
- The new `## Recover A Mirror-Rewritten Lockfile` section should be additive
  to `## Project Practice`.
- The docs should tell users not to commit locally mirror-rewritten `uv.lock`.
- Recovery commands should include `git restore -- uv.lock`,
  `UV_NO_CONFIG=1 uv lock --check`, mirror-marker `rg` scan, and
  `git diff --quiet -- uv.lock`.
- The docs drift test should scope assertions to the new recovery section and
  keep the README pointer check.
- No connector, scraper, platform API, ranking, demand proof, or runtime
  behavior should be introduced.

Checks already run:
- git restore -- uv.lock
- git diff --exit-code -- uv.lock pyproject.toml
- git diff --cached --exit-code -- uv.lock pyproject.toml
- ! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
- UV_NO_CONFIG=1 uv lock --check
- uv --no-config run --frozen pytest tests/test_cli_docs.py::test_dependency_mirror_docs_explain_lockfile_recovery -q
- uv --no-config run --frozen pytest tests/test_cli_docs.py -q
- uv --no-config run --frozen ruff check tests/test_cli_docs.py
- uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
- git diff --check over changed Stage 82 files

Report findings by severity:
- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.
