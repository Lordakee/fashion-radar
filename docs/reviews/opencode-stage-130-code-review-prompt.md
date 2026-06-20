Review the Stage 130 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` derive expected project name,
  version, and console script lines from `pyproject.toml`.
- Keep archive validation behavior equivalent except for removing script-side
  metadata hardcoding.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 130 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 130 design and plan?
2. Does the checker load project name, version, and `[project.scripts]` from
   `pyproject.toml` with stdlib only?
3. Is the metadata loaded once per `validate_build_dir()` run and threaded
   through wheel validation?
4. Does entry point validation check every configured console script line
   without introducing ordering or formatting requirements beyond stripped-line
   membership?
5. Do tests prove derivation from both repo pyproject and a supplied temporary
   pyproject?
6. Does the stage avoid dependency, lockfile, CI, package filename/path,
   runtime product, connector, scraping, browser automation, platform API,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior changes?

Return:
Start with `# Stage 130 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
