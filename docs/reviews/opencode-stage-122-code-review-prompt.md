Review the Stage 122 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Exclude internal review and superpowers planning artifacts from source
  distributions.
- Make package archive checks reject those paths if they appear in any built
  archive.

Files changed:
- `pyproject.toml`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `tests/test_package_metadata.py`
- Stage 122 design/plan/review artifacts

Plan review:
- `docs/reviews/opencode-stage-122-plan-review.md`

Review focus:
1. Does the implementation match the Stage 122 design and plan?
2. Do Hatch sdist excludes cover `docs/reviews/**` and `docs/superpowers/**`
   without removing required public docs, examples, schemas, or source files?
3. Does `scripts/check_package_archives.py` reject exact internal artifact
   directory paths and child paths after archive path normalization?
4. Do the tests prove both the checker guard and the pyproject build
   configuration?
5. Does the real local build omit `docs/reviews/` and `docs/superpowers/`
   members from the sdist?
6. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
