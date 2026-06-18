# Stage 82 Code Review

## Verdict

No Critical or Important findings remain after correcting the regeneration
guidance and replacing the live-capture stub with this completed review
artifact. Stage 82 is docs/test-only plus lockfile cleanup: it restores the
working tree `uv.lock` to the public mirror-free version and documents the
recovery path for future local mirror rewrites.

## Findings

### Critical

None.

### Important

None.

### Minor

- The README pointer assertion in
  `test_dependency_mirror_docs_explain_lockfile_recovery` intentionally
  cross-pins README mirror guidance even though Stage 82 does not edit README.
  This is acceptable drift protection for discoverability.

## Review Notes

- `docs/dependency-mirrors.md` adds `## Recover A Mirror-Rewritten Lockfile` as
  a peer section after `## Project Practice`; the existing project-practice
  mirror scan remains in place.
- The restore path tells users not to commit a locally mirror-rewritten
  `uv.lock`, then gives `git restore -- uv.lock`, `UV_NO_CONFIG=1 uv lock
  --check`, the mirror-marker `rg` scan, and `git diff --quiet -- uv.lock`.
- The intentional dependency-change path uses `UV_NO_CONFIG=1 uv lock`, validates
  the lockfile, scans for mirror markers, and tells users to review
  `git diff -- uv.lock` before committing. It does not incorrectly use
  `git diff --quiet` for an expected lockfile update.
- `tests/test_cli_docs.py` scopes the recovery assertions to the new recovery
  section via `_markdown_section_exact_heading`.
- No runtime code, dependency manifest, CI, `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md` changes are
  part of this node.

## Verification Observed

- `git diff --exit-code -- uv.lock pyproject.toml`
- `git diff --cached --exit-code -- uv.lock pyproject.toml`
- `! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock`
- `UV_NO_CONFIG=1 uv lock --check`
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_dependency_mirror_docs_explain_lockfile_recovery -q`
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q`
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
- `git diff --check`
- `uv --no-config run --frozen pytest -q`
- `uv --no-config run --frozen ruff check .`
