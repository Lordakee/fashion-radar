Review the Stage 83 plan for Fashion Radar.

Goal:
- Add a GitHub upload checklist reminder that points to the mirror-lockfile
  recovery path.
- Add a docs drift test for that reminder.

Expected changed files:
- docs/github-upload-checklist.md
- tests/test_cli_docs.py
- Stage 83 spec/plan/review artifacts

Out of scope:
- src/
- dependency manifests
- uv.lock
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- runtime connector/scraper/platform API/ranking/demand proof behavior

Please review:
- Is the checklist placement near the existing upload/lockfile checks clear?
- Is the reminder sufficiently operational and not too verbose?
- Is the test scope adequate and non-brittle?
- Are there any Markdown split or staging risks?

Report findings by severity: Critical, Important, Minor.
