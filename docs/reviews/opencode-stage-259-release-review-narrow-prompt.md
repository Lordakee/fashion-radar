Narrow Stage 259 release review.

Repository: /home/ubuntu/fashion-radar

Review summary only; do not run tools.

Stage 259 is docs/tests/review-only. It updates release-facing docs to say
Markdown, JSON, and companion HTML reports; cuts CHANGELOG to
`## [0.1.0] - 2026-07-01` with Stage 256-258 notes; adds a user-controlled
Before Tagging note to the upload checklist; and adds docs guards. No runtime
code, dependencies, package metadata, `uv.lock`, or tag creation changed.

Release gate already passed locally:
- focused docs tests
- focused ruff/format
- release hygiene
- git diff --check
- lock/sync/mirror sync checks
- full ruff and format
- full pytest: 1623 passed
- source first-run smoke
- `uv.lock`/`pyproject.toml` diff guard
- package build and archive checker
- installed wheel smoke
- dashboard extra import smoke

Return concise markdown only:
- Verdict
- Critical Issues
- Important Issues
- Minor Issues
- Ready to commit and push?

Do not include tool logs or process chatter.
