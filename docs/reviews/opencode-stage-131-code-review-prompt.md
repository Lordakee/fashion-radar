Review the Stage 131 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `CONTRIBUTING.md` and `.github/pull_request_template.md` verification
  sections with the local release hygiene and source-checkout first-run smoke
  commands already required by CI and the upload checklist.
- Keep the change docs/test-only.

Files changed:
- `tests/test_cli_docs.py`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- Stage 131 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 131 design and plan?
2. Do `CONTRIBUTING.md` and the PR template both include the local release
   hygiene command and the source-checkout first-run smoke command in their
   `Verification` sections?
3. Does the canonical verification-surface test now require those two commands
   on `contributing` and `pull_request_template` while keeping existing
   CI/checklist/README/first-run smoke expectations?
4. Does the stage avoid package archive behavior changes, README development
   block expansion, dependency/lockfile/CI/runtime product changes, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
Start with `# Stage 131 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
