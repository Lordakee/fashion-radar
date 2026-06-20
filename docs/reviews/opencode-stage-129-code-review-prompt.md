Review the Stage 129 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/pull_request_template.md` packaging verification guidance with
  CI/upload-checklist temp build and package archive checker commands.
- Keep the change docs/test-only.

Files changed:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 129 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 129 design and plan?
2. Does the PR template include `tmp_build`, `uv --no-config build --out-dir
   "$tmp_build"`, and `scripts/check_package_archives.py "$tmp_build"`?
3. Does `test_github_verification_surfaces_use_no_config_frozen_uv_run` include
   the PR template as a surface for the package archive checker and temp build
   commands?
4. Does the focused docs test avoid requiring the full upload checklist in the
   PR template?
5. Does the stage avoid runtime product behavior, package checker behavior, CI
   behavior, dependencies, lockfile, connectors, scraping, browser automation,
   platform API, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, and compliance/audit product behavior?

Return:
Start with `# Stage 129 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
