# Claude Code Stage 387 Release Review

## Verdict

APPROVED

## Scope

Reviewed the complete Stage 387 delivery from `1e366aa` through the current
working-tree diff after fresh full verification and isolated package gates.

## Verified Release Controls

- The feature remains generated-site-only: the builder accepts only the current
  edition, existing saved local article sidecars, and existing generated page
  hrefs. It adds no collector, route, schema, app-contract, sidecar, or data
  artifact surface.
- `render_row_one_site` wires the payload only into the existing homepage
  template path. No article/detail route registration or generated JSON output
  is added.
- The Stage 387 documentation test verifies the exact scope-exclusion paragraph
  in both `README.md` and `docs/row-one.md`.
- `/.codegraph/**` is excluded from source distributions so the local CodeGraph
  database cannot enter package archives; runtime and wheel packaging remain
  unaffected.
- The release snapshot has no lockfile diff and no generated build/cache
  artifacts.
- The Stage 387 plan, OpenCode plan-revision, Claude code review, and Claude
  code rereview records are present and clean. The code rereview approved the
  final behavior without critical or important findings.
- The release gates verified the full test suite, Ruff check and formatting,
  release hygiene, first-run smoke behavior, public lockfile validation,
  sdist/wheel archive contents, isolated wheel installation, and dashboard-extra
  imports.

## Disposition

No release-blocking finding remains. This record completes the required Claude
Code release review before Stage 387 commit and push.
