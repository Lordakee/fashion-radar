# Stage 358 Code Review Prompt

Review the current uncommitted Stage 358 implementation in `/home/ubuntu/fashion-radar`.

Goal: add a generated-site-only `Daily Local Signal Momentum` section to
`index.html`. The section reuses existing Stage 350
`RowOneSavedArticleDailySignalLeaderboard` data to show current-edition saved
local brand/product/theme support counts. It must remain a homepage HTML
section only.

Relevant requirements:

- Render `.daily-local-signal-momentum` only on the homepage `index.html`.
- Place it after `.daily-local-key-signals-digest` and before
  `.saved-article-content-organization`.
- Reuse Stage 350 leaderboard dataclasses and builder without mutating their
  behavior.
- Prefer `articles/<story-id>.html#local-article-digest` support links when a
  safe first-class local article page href exists.
- Fall back only to safe `details/<safe>.html#local-article-digest` links.
- Filter unsafe support links, unsafe mapping values, traversal, external
  schemes, and wrong fragments.
- Escape all display text.
- Do not create app contract, schema, runtime, manifest, sidecar, JSON, route
  family, fetching, scoring, LLM, connector, scheduling, deployment, analytics,
  personalization, recommendation, or compliance-review behavior.
- Compute the local article href mapping once in the normal
  `render_row_one_site(...)` flow and pass it to homepage rendering and local
  article writing.

Please inspect:

- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/render.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-08-stage-358-daily-local-signal-momentum-design.md`
- `docs/superpowers/plans/2026-07-08-stage-358-daily-local-signal-momentum-plan.md`

Use `git diff HEAD -- ...` as needed.

Report:

- Critical issues that must be fixed.
- Important issues that should be fixed before commit.
- Minor issues that can be left for later.
- Whether this is ready to commit after tests/gates pass.

Do not edit files.
