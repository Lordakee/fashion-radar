# Stage 31 Release Gate Design

## Goal

Create a reproducible release-readiness gate for the current GitHub public
surface after Stage 30.

## Scope

Stage 31 is a verification and small-doc-fix node. It does not add runtime
features.

In scope:

- Run and document dependency, test, lint, format, diff, build, installed-wheel,
  command-help, boundary, secret, artifact, and lockfile checks.
- Preserve a pre-execution Claude Code plan-review checkpoint before release
  gate commands run.
- Add a concise release-gate checklist entry if the existing upload checklist
  misses a Stage 30 public command or verification command.
- Add review artifacts under `docs/reviews/` and plan/spec artifacts under
  `docs/superpowers/`.

Out of scope:

- New source connectors.
- Scraping, crawling, platform automation, login, browser automation, watchers,
  schedulers, source acquisition, platform coverage verification, source
  ranking, or demand proof.
- Runtime command behavior changes unless a release-gate check exposes a real
  bug.
- Dependency or `uv.lock` changes.
- Leaving a dirty or mirror-rewritten `uv.lock` in the release-gate state.

## Release Gate Checks

Required checks:

```bash
git diff -- uv.lock > /tmp/fashion-radar-stage31-uv-lock-before.diff
# Confirm any uv.lock diff is only the known mirror URL rewrite before restore.
git restore uv.lock
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff --cached --check
git status --short --branch --untracked-files=all
git status --short -- uv.lock
git diff -- uv.lock
git diff --cached -- uv.lock
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
git remote get-url origin
git config --get-regexp '^http\..*extraheader$' || true
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

Build and installed-wheel smoke:

```bash
rm -rf /tmp/fashion-radar-dist-stage31 /tmp/fashion-radar-wheel-stage31
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage31
uv venv /tmp/fashion-radar-wheel-stage31/.venv
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python /tmp/fashion-radar-wheel-stage31/.venv/bin/python /tmp/fashion-radar-dist-stage31/*.whl
```

Smoke the public command surface, including the new Stage 30 command:

```bash
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar --help
for cmd in init doctor source-pack-lint entity-pack-lint community-signal-lint community-signal-lint-dir community-candidates community-candidates-dir community-handoff-workflow import-signals-dir schedule-example dashboard report candidates trends imported-candidate-evidence imported-candidates imported-review-workflow imported-entity-deltas imported-signals-summary imported-signals import-signals collect match clean-old-data run; do
  /tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar "$cmd" --help >/dev/null
done
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-handoff-workflow "/tmp/fashion-radar-wheel-stage31/missing exports ? # & %" --input-format csv --pattern "*.csv" --config-dir "/tmp/fashion-radar-wheel-stage31/config ? # & %" --data-dir "/tmp/fashion-radar-wheel-stage31/data ? # & %" --as-of 2026-06-13T12:00:00Z --source-name "Community | Tool Export" --format json > /tmp/fashion-radar-wheel-stage31/workflow.json
```

The `community-handoff-workflow` JSON smoke must confirm:

- `execution_mode == "print_only"`;
- `step_count == 5`;
- emitted command strings are the five intended local commands;
- step 3 includes `--dry-run` and step 4 intentionally does not;
- the supplied missing directory does not need to exist;
- the supplied data directory is not created.
- the supplied config directory is not created.
- all five step names and suggested effects match the Stage 30 contract.
- table output says commands were not executed.

Package content checks:

- wheel archive membership must be asserted path-by-path for
  `fashion_radar/cli.py`, `fashion_radar/community_handoff_workflow.py`,
  report template, and starter config templates;
- sdist archive membership must be asserted path-by-path for README, key docs,
  source/entity pack examples, community signal examples, and community signal
  schema.
- public CSV and JSON community signal examples must lint and preview from the
  installed wheel;
- public CSV and JSON community signal examples must dry-run import to a temp
  data dir without leaving project artifacts.

Boundary scans:

- Scan docs and source diffs for positive scraping/source-acquisition/platform
  automation claims.
- Add diff-scoped boundary scans so Stage 31 changes are reviewed separately
  from historical plan/review files.
- Confirm any matches are negative boundary statements, review prompts, or
  existing historical context.

Secret/artifact scans:

- Confirm git remote URL is token-free.
- Confirm no persistent `http.*extraheader`.
- Confirm staged diff excludes `uv.lock`.
- Confirm staged paths are limited to Stage 31 docs/review artifacts.
- Confirm working tree `uv.lock` is clean and contains no mirror URLs.
- Confirm generated local data, reports, build output, temp virtualenvs, and
  SQLite files are not staged.

Push hygiene:

- Push only when explicitly authorized by the user for the current run.
- Use one-shot Git auth headers only; do not persist tokens in remotes or git
  config.

## Output

Stage 31 should leave one committed documentation/process node if it adds
checklist/review artifacts. If all checks pass and no docs need changing, Stage
31 can commit only its plan/review artifacts and a concise release-gate result
document.
