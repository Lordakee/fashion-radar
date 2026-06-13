Critical: None.

Important: None.

Minor: None.

Reviewed staged diff only.

Verification summary:
- `git diff --cached --name-only` shows only Stage 29 documentation/review files: `CHANGELOG.md`, `README.md`, and files under `docs/`.
- No staged source, test, config, dependency, or `uv.lock` changes were present.
- `git diff --cached -- uv.lock` was empty.
- Staged Stage 29 docs continue to describe `community-candidates-dir` as local, read-only, non-recursive, pre-import/in-memory, and aggregate-only.
- Prohibited capability language appears only as negative boundary language, not as positive claims.
- Output exclusions now explicitly include `account/private fields` along with the other required exclusions.

APPROVED FOR STAGE 29 DOCS COMMIT AND PUSH
