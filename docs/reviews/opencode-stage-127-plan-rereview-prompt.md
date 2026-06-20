Re-review the Stage 127 design and implementation plan after the package smoke
exposed uv's generated build-output `.gitignore` marker.

Repository: `/home/ubuntu/fashion-radar`

Initial plan review:
- `docs/reviews/opencode-stage-127-plan-review.md`

Design:
- `docs/superpowers/specs/2026-06-20-stage-127-build-dir-direct-child-hygiene-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-127-build-dir-direct-child-hygiene-plan.md`

New evidence:
- `uv --no-config build --out-dir <tmp>` with uv 0.11.7 consistently writes a
  direct `.gitignore` file containing `*` beside the wheel and sdist.
- The Stage 127 package smoke failed when the initial helper rejected that
  marker.

Revised stage intent:
- Reject unexpected direct children in the build output directory.
- Allow exactly the selected wheel, selected sdist, and uv's direct
  `.gitignore` marker.
- Keep duplicate/missing archive behavior and archive-internal validation
  unchanged.

Review focus:
1. Is allowing uv's `.gitignore` marker the correct minimal correction to the
   initial plan?
2. Do the revised tests cover both marker acceptance and rejection of other
   direct files/directories?
3. Does the revised plan remain limited to the package checker, package tests,
   and review artifacts?
4. Does the scope avoid runtime product behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before continuing implementation.
