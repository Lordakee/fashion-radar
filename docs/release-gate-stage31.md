# Stage 31 Release Gate

Run timestamp: 2026-06-14 02:23:56 CST

## Scope

Release-readiness verification for the current public command surface after
Stage 30.

Stage 31 did not add runtime features, source connectors, scraping, crawling,
platform automation, watchers, schedulers, source acquisition, source ranking,
or platform coverage verification.

## Verified

- Dependency sync check with mirror-backed uv install path:
  `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
- Public lockfile checks with user-level uv config disabled:
  `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check`.
- Full pytest suite: 572 passed.
- Ruff lint and format checks.
- Git whitespace checks for unstaged and staged diffs.
- Wheel and sdist build under `/tmp/fashion-radar-dist-stage31`.
- Installed-wheel CLI help smoke for the full public command surface, including
  `community-handoff-workflow`.
- Installed-wheel `community-handoff-workflow` JSON smoke:
  `execution_mode: print_only`, `step_count: 5`, expected step names/effects,
  expected command prefixes, `--dry-run` only on the dry-run import step, and no
  creation of supplied missing/config/data directories.
- Installed-wheel `community-handoff-workflow` table smoke confirmed:
  `Commands were not executed.`
- Wheel archive content assertions for `fashion_radar/cli.py`,
  `fashion_radar/community_handoff_workflow.py`, report template, and starter
  config templates.
- Sdist archive content assertions for README, source-boundary docs,
  GitHub upload checklist, source/entity pack examples, community signal CSV
  and JSON examples, and community signal schema.
- Installed-wheel public example smoke for CSV and JSON community signal lint,
  candidate preview, directory candidate preview, and dry-run import.
- Boundary scans for prohibited platform/source-acquisition implications.
- Secret and artifact scans for token-free remote URL, persistent extraheaders,
  staged/dirty `uv.lock`, actual secret-looking values, generated artifacts,
  and `.codegraph` tracked-file hygiene.

## Notes

- Earlier stages left a local mirror rewrite in `uv.lock`; Stage 31 restored
  `uv.lock` to the committed lockfile before release checks.
- `uv.lock` is clean, unstaged, and contains no mirror URLs.
- The local machine has user-level uv config at `~/.config/uv/uv.toml` setting
  the Tsinghua mirror as the default index. Release lockfile checks used
  `UV_NO_CONFIG=1` so user-level mirror config cannot rewrite the public
  lockfile.
- Public example candidate-preview smoke uses a temp runtime config directory:
  `/tmp/fashion-radar-example-config-stage31`, populated by copying
  `configs/scoring.example.yaml` to `scoring.yaml`. This exercises the CLI
  contract without adding runtime config files to the repo.
- Public example dry-run imports used
  `/tmp/fashion-radar-import-dry-run-stage31` and created no files.
- Boundary scan output was written under `/tmp`. Broad historical scan matched
  existing boundary/review/plan language; public-surface scan matched existing
  boundary language; unstaged and staged diff-scoped boundary scans had zero
  matches.
- `data/README.md` and `reports/README.md` are intentionally tracked directory
  documentation files. The artifact gate allows only those two paths while
  continuing to reject generated data/report files.

## Review Artifacts

- `docs/reviews/claude-code-stage-31-plan-review.md`
- `docs/reviews/claude-code-stage-31-plan-rereview.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-2.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-3.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-4.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-5.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-6.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-7.md`
- `docs/reviews/claude-code-stage-31-plan-rereview-8.md`
- `docs/reviews/claude-code-stage-31-release-review-prompt.md`
- `docs/reviews/claude-code-stage-31-release-review.md`
