# Claude Code Stage 45 Plan Review Prompt

You are reviewing the Stage 45 package archive and metadata readiness plan for
the `fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make the GitHub-ready package surface explicit and testable: public package
metadata should identify the project correctly, both wheel and sdist archives
should be checked for release-critical files, and installed-package smoke checks
should cover both the console script and module entrypoint.

## Proposed Technical Approach

- Add public package metadata to `pyproject.toml` without changing package name,
  version, dependencies, lockfile, or runtime behavior.
- Create a dependency-free `scripts/check_package_archives.py` script that
  inspects one built wheel and one built `.tar.gz` sdist in a supplied build
  directory.
- Require wheel checks for package entrypoints, packaged templates, dist-info
  metadata, console script metadata, and bundled license file.
- Require sdist checks for public-readiness docs, config/source/entity examples,
  community signal examples, schema, and package source entrypoints.
- Update CI and `docs/github-upload-checklist.md` to invoke the same archive
  inspection script after `uv build`.
- Add installed-wheel module-entrypoint smoke:
  `"$tmp_env/venv/bin/python" -m fashion_radar --help`.
- Add pytest guards for package metadata, archive script behavior, and
  CI/checklist package-smoke drift.
- Clarify README install modes so `uv sync --locked --dev` is described as
  source-checkout setup and the local wheel smoke is described as a pre-upload
  readiness check that does not publish to PyPI.
- Keep the node out of scraping, crawling, platform automation, source
  acquisition, runtime collection/scoring behavior, dependency changes,
  lockfile changes, generated data/report changes, and compliance-review
  functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-45-package-archive-metadata-readiness-design.md`
- `docs/superpowers/plans/2026-06-15-stage-45-package-archive-metadata-readiness-plan.md`
- Current context files likely affected by the plan:
  - `pyproject.toml`
  - `.github/workflows/ci.yml`
  - `docs/github-upload-checklist.md`
  - `README.md`
  - `tests/test_cli_docs.py`

## Specific Questions

1. Is this a good Stage 45 next node for GitHub/package readiness after Stage 44?
2. Are the archive contents being checked the right level of strictness, without
   becoming a brittle assertion of every tracked file?
3. Is the TDD sequence credible and safe, especially the RED tests?
4. Does the plan preserve the current project boundaries: no source scraping,
   no platform automation, no external service additions, no dependency or
   lockfile changes, and no compliance-review feature?
5. Are there any Critical or Important issues that must be fixed before
   implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 45 PACKAGE ARCHIVE METADATA READINESS
```
