Review the updated Stage 132 design and implementation plan before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Extend `scripts/check_release_hygiene.py` so unignored untracked files are
  scanned for secret content, not only forbidden paths.
- Preserve symlink skip behavior for newly scanned untracked paths, so an
  untracked symlink is not followed to an ignored token-bearing target.
- Keep existing secret patterns, redaction, path policy, and runtime/product
  behavior unchanged.

Design:
- `docs/superpowers/specs/2026-06-21-stage-132-untracked-secret-hygiene-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-132-untracked-secret-hygiene-plan.md`

Proposed implementation scope:
- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- Stage 132 review artifacts only

Review focus:
1. Does the design address the untracked-secret hygiene gap without changing
   secret patterns, forbidden path policy, docs verification surfaces, or
   runtime/product behavior?
2. Is the planned RED test specific enough to prove untracked publishable-looking
   files with valid GitHub tokens are rejected, redacted, and line-numbered?
3. Is the implementation plan appropriately minimal and limited to reusing
   `find_secret_findings()` for `untracked_paths`, while preserving symlink
   skip behavior by skipping original untracked symlink paths before
   resolved-path containment?
4. Is the symlink regression test specific enough to prove an untracked symlink
   to an ignored token-bearing target is skipped rather than followed?
5. Does the plan avoid dependency/lockfile changes, package archive checker
   changes, connectors, scraping, browser automation, platform APIs,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
6. Are the verification commands sufficient?

Return:
Start with `# Stage 132 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
