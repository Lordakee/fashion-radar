Review the Stage 124 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject unsafe wheel and sdist archive member paths in
  `scripts/check_package_archives.py`.
- Preserve existing required-file, metadata, entry-point, and forbidden-member
  package archive validation behavior.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 124 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 124 design and plan?
2. Are unsafe archive member paths rejected before sdist root-prefix stripping?
3. Are wheel and sdist unsafe path cases covered, including `..`, absolute
   paths, Windows drive paths, UNC-style paths, and backslash normalization?
4. Does the stage preserve existing package archive checks?
5. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
