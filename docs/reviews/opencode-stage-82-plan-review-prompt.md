Review the Stage 82 plan for Fashion Radar.

Goal:
- Document the safe recovery path for a locally mirror-rewritten `uv.lock`.
- Add a docs drift test for that recovery guidance.
- Restore the working tree `uv.lock` to the public mirror-free version.

Expected changed files:
- docs/dependency-mirrors.md
- tests/test_cli_docs.py
- Stage 82 spec/plan/review artifacts

Out of scope:
- src/
- dependency manifests
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/github-upload-checklist.md
- CI
- runtime connector/scraper/platform API/ranking/demand proof behavior

Please review:
- Is restoring `uv.lock` from HEAD safe and aligned with the public lockfile
  boundary?
- Is the planned documentation precise enough to prevent accidental mirror URL
  commits?
- Are the tests and verification commands sufficient?
- Are there any Markdown split hazards or staging risks?

Report findings by severity: Critical, Important, Minor.
