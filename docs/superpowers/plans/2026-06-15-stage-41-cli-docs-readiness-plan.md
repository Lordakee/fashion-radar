# Stage 41 CLI Docs Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh public docs so current CLI commands, path flags, and release
smoke checks are easy to follow and consistent.

**Architecture:** This is a documentation-only readiness update. Add one compact
CLI reference as the reusable command map, then update existing examples so
local import/review flows consistently use the same config/data/report paths.
Keep historical gate records untouched and use local Claude Code with
`--effort max` for plan and release review.

**Tech Stack:** Markdown docs, Typer CLI help via `uv run fashion-radar`, `rg`,
`uv`, `git`, local Claude Code CLI. No Python source, dependency, lockfile, CI
YAML, schema, scraping, source-acquisition, or runtime behavior changes.

---

## Boundaries

In scope:

- Create: `docs/cli-reference.md`
- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/data-retention.md`
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/daily-digest.md`
- Modify: `docs/scheduling.md`
- Modify: `docs/entity-packs.md`
- Modify: `docs/github-upload-checklist.md`
- Add: `docs/reviews/claude-code-stage-41-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-41-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-41-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-41-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-41-release-review.md`
- Add if needed: `docs/reviews/claude-code-stage-41-release-rereview*.md`
- Maintain/update: this Stage 41 spec and plan

Out of scope:

- Modifying source code, tests, package metadata, `uv.lock`, workflow YAML,
  config templates, database schema, runtime behavior, generated reports/data,
  dashboards, or package artifacts.
- Rewriting historical `docs/reviews/claude-code-*`,
  `docs/reviews/opencode-stage-40-*`, historical specs/plans, or
  `docs/release-gate-stage31.md`.
- Adding source connectors, scraping, crawling, browser automation,
  login/cookie/account/proxy/CAPTCHA flows, platform APIs, source acquisition,
  schedulers, watchers, monitors, or external services.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-41-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-41-plan-review.md`

- [ ] **Step 1: Write plan review prompt**

Create `docs/reviews/claude-code-stage-41-plan-review-prompt.md`:

```markdown
# Claude Code Stage 41 Plan Review Prompt

You are reviewing the Stage 41 CLI docs readiness plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.
- Use Claude Code with `--effort max`.

## Goal

Refresh public documentation so current CLI commands, path flags, and release
smoke checks are consistent and easy to audit.

## Proposed Technical Approach

- Add `docs/cli-reference.md` as a compact current command map.
- Update README and scoped docs so import/review examples use matching
  `--config-dir`, `--data-dir`, and `--reports-dir` values.
- Update manual/community import docs to show current `--data-dir` and
  `--imported-at` usage.
- Update source-pack, trend, dashboard, and data-retention examples for current
  path and flag behavior.
- Update `docs/github-upload-checklist.md` installed-wheel help smoke coverage
  for the current public command surface.
- Keep `docs/release-gate-stage31.md` historical; do not rewrite it.
- Keep this stage documentation-only.
- Do not change product code, tests, dependencies, lockfiles, CI behavior,
  database schema, commands, scraping/crawling/platform automation, source
  acquisition, schedulers, watchers, or monitors.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-41-cli-docs-readiness-design.md`
- `docs/superpowers/plans/2026-06-15-stage-41-cli-docs-readiness-plan.md`

## Context

The previous temporary rule that Stage 41 review must use local opencode has
been canceled by the user. Treat any uncommitted `opencode-stage-41-*` files as
superseded review-attempt artifacts only; do not rely on them for approval.

The plan should remain documentation-only. It should not introduce source
connectors, scraping, crawling, browser automation, login/cookie/account/proxy
or CAPTCHA flows, platform APIs, source acquisition, schedulers, watchers,
monitors, or external services.

## Specific Questions

1. Is Stage 41 correctly scoped as a docs-only CLI readiness node?
2. Are the target files and boundaries complete for refreshing CLI examples
   without touching runtime behavior?
3. Does the plan now use Claude Code review gates consistently after the
   temporary opencode rule was canceled?
4. Are the path-consistency checks strong enough to catch import/review flows
   that write to `$PWD/data` but later read default user data paths?
5. Are the help-smoke and release verification steps sufficient before commit
   and push?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 41 CLI DOCS READINESS
```
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-41-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-41-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 41 CLI DOCS READINESS`. Fix blockers before Task 1. If
fixes are needed, store each follow-up prompt/result as
`docs/reviews/claude-code-stage-41-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 41 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before editing active docs: modified or untracked files are limited to
the Stage 41 spec, plan, Claude Code plan review prompt/result files, and any
superseded uncommitted opencode Stage 41 review-attempt artifacts. If unrelated
files appear, stop and investigate before editing.

## Task 1: Add Current CLI Reference

**Files:**

- Create: `docs/cli-reference.md`
- Modify: `README.md`

- [ ] **Step 1: Create `docs/cli-reference.md`**

Add a compact reference with sections:

- Shared path options
- Setup and operations
- Local import and community handoff
- Imported signal review
- Trends, dashboard, cleanup

The command map must include at least:

```text
init
migrate-db
doctor
source-pack-lint
entity-pack-lint
collect
match
report
run
schedule-example
dashboard
clean-old-data
candidates
trends
import-signals
import-signals-dir
imported-signals
imported-signals-summary
imported-entity-deltas
imported-candidates
imported-candidate-evidence
imported-review-workflow
community-signal-lint
community-signal-lint-dir
community-candidates
community-candidates-dir
community-handoff-workflow
```

Important flag details:

- `collect`: `--config-dir`, `--data-dir`, `--now`.
- `import-signals`: file argument, `--data-dir`, `--format`, `--source-name`,
  `--imported-at`, `--dry-run`.
- `import-signals-dir`: directory argument, `--data-dir`, required `--format`,
  required `--pattern`, `--imported-at`, `--dry-run`, `--output-format`,
  `--source-name`.
- Imported review commands: `--as-of`, `--lookback-days`, `--current-days`,
  `--baseline-days`, `--entity-type`, `--source-name`, `--limit`, `--format`,
  as applicable.
- Community commands: `--input-format`, `--pattern`, `--strict`, `--source-name`,
  `--limit`, `--format`, as applicable.
- `report`: required `--as-of`, `--config-dir`, `--data-dir`, `--reports-dir`,
  and digest output flags.
- `run`: required `--as-of`, `--config-dir`, `--data-dir`, `--reports-dir`, and
  digest output flags.
- `candidates`: required `--as-of`, `--config-dir`, `--data-dir`, `--limit`,
  and `--format`.
- `trends`: required `--as-of`, `--config-dir`, `--data-dir`,
  `--baseline-as-of`, `--limit`, `--format`, `--include-dropped`.
- `dashboard`: `--config-dir`, `--data-dir`, `--reports-dir`, `--host`, `--port`.
- `clean-old-data`: actual cleanup command name; `--data-dir`, `--as-of`,
  `--retention-days`, `--dry-run`.
- `schedule-example`: include the command in the map and tell users to run
  `fashion-radar schedule-example --help` for current mode/time/project flags.
  Keep the reference compact; it is a map, not a full copy of every help page.

- [ ] **Step 2: Link CLI reference from README**

In README Documentation, add `docs/cli-reference.md` near the operational docs.
Remove the README link to `docs/release-gate-stage31.md` from the current docs
list, because that file is historical evidence rather than the current reusable
release gate.

## Task 2: Fix Import/Review Path Consistency

**Files:**

- Modify: `README.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Add explicit `--data-dir "$PWD/data"` to single-file import examples**

Update every non-dry-run single-file `import-signals` example whose surrounding
workflow reviews `$PWD/data`, across all in-scope import docs (not only the
manual doc). This covers, at minimum:

- `docs/manual-signal-import.md` (csv and json single-file imports).
- `docs/community-signal-import.md` (csv and json single-file imports in the
  Import section).
- `docs/community-signal-quality.md` (the single-file `import-signals` line and
  non-dry-run `import-signals-dir` line in the recommended-order block, where
  the surrounding review commands already use `--data-dir "$PWD/data"`).

Resulting shape:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir "$PWD/data"
uv run fashion-radar import-signals ./signals.json --format json --source-name "Manual Export" --imported-at "2026-06-12T12:00:00Z" --data-dir "$PWD/data"
```

Keep existing dry-run examples, but add `--data-dir "$PWD/data"` where the
surrounding workflow is explicitly repo-local (dry run does not open SQLite,
but the flag keeps the example path-consistent).

- [ ] **Step 2: Add explicit `--data-dir "$PWD/data"` to directory import examples**

Update `import-signals-dir` import examples in README, architecture,
`docs/community-signal-import.md`, and community quality docs when the
surrounding workflow reviews `$PWD/data` or `./data`.
The non-dry-run import command should include:

```bash
--imported-at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --data-dir "$PWD/data"
```

The dry-run command may include `--data-dir "$PWD/data"` for path consistency,
while preserving that dry run does not open SQLite.

- [ ] **Step 3: Mention review tuning flags in import docs**

Add one short paragraph in `manual-signal-import.md` and
`community-signal-import.md` saying retained-row review commands can be narrowed
with `--source-name`, `--lookback-days`, `--current-days`, `--baseline-days`,
`--entity-type`, and `--limit` where supported, and JSON can be requested with
`--format json`.

- [ ] **Step 4: Carry `--data-dir`/`--config-dir` through review-sequence tails**

The design's consistency rule applies to the *whole* sequence, not only the
import line. Several in-scope docs currently run a repo-local import and
review block but then tail into bare `match` / `report` / `candidates` /
`trends` commands that silently fall back to the platform-user data directory,
so imported rows are never matched or reported. Fix every such tail:

- `docs/manual-signal-import.md`: the `match` / `report` / `candidates` /
  `trends` lines at the end of the review block must carry
  `--data-dir "$PWD/data"` and `--config-dir "$PWD/configs"` (and keep their
  existing `--as-of`).
- `docs/community-signal-import.md`: same `match` / `report` / `candidates` /
  `trends` tail after the community review block.
- `docs/community-signal-quality.md`: if any `match` / `report` / `candidates`
  / `trends` tail is added or already present in the recommended-order block,
  it must carry the same `--data-dir "$PWD/data"` and `--config-dir
  "$PWD/configs"` flags. Its current blocker is the non-dry-run import lines;
  this bullet prevents the same class of drift from being introduced while
  editing.
- `docs/architecture.md` Command Flow block: this file uses the bare
  `fashion-radar` invocation prefix and the `./configs` / `./data` path style
  consistently, so keep that local style but add `--data-dir ./data` (and
  `--config-dir ./configs` where missing) to `match`, `report`, `candidates`,
  and `trends` so the tail reads the same directory the imports and
  `imported-*` review commands use. Do not rewrite this file's invocation
  prefix or path style; only close the data-dir gap.

Resulting shape for the `$PWD`-style docs:

```bash
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Task 3: Fix Source Pack, Trend, Dashboard, And Cleanup Examples

**Files:**

- Modify: `docs/source-packs.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/data-retention.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Source pack path consistency**

In `docs/source-packs.md`, make repo-local usage explicit:

```bash
mkdir -p "$PWD/configs"
cp configs/source-packs/fashion-public.example.yaml "$PWD/configs/sources.yaml"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Also show strict lint:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

- [ ] **Step 2: Trend delta path consistency**

In `docs/trend-deltas.md`, add `--data-dir "$PWD/data"` to trend examples and
manual import flow. In flows that run `match`, include:

```bash
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

- [ ] **Step 3: Dashboard and cleanup flags**

In `docs/dashboard.md`, include one example with explicit host/port:

```bash
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --host 127.0.0.1 --port 8501
```

In `docs/data-retention.md` and README cleanup examples, add
`--data-dir "$PWD/data"` to `clean-old-data` commands.

## Task 4: Refresh GitHub Upload Checklist Smoke Coverage

**Files:**

- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Add current public command help smoke list**

In the installed-wheel smoke block, add help checks for the current public
command surface:

```bash
for cmd in \
  init migrate-db doctor source-pack-lint entity-pack-lint \
  community-signal-lint community-signal-lint-dir \
  community-candidates community-candidates-dir community-handoff-workflow \
  import-signals import-signals-dir imported-signals imported-signals-summary \
  imported-entity-deltas imported-candidates imported-candidate-evidence \
  imported-review-workflow collect match report candidates trends \
  schedule-example dashboard clean-old-data run
do
  "$tmp_env/venv/bin/fashion-radar" "$cmd" --help
done
```

Keep existing runtime smoke commands that exercise import/review behavior.

- [ ] **Step 2: Replace historical stage-specific docs gates with current docs gate**

Keep the Stage 27B/29/30 checks if still useful, but group them under a
`Historical Boundary Checks` label and add a current Stage 41 docs freshness
check:

```markdown
Stage 41 docs freshness check:

- [ ] README links `docs/cli-reference.md`.
- [ ] Import/review examples that use `$PWD/data` pass `--data-dir "$PWD/data"`
      consistently.
- [ ] Installed-wheel help smoke covers every current public command.
```

Do not edit `docs/release-gate-stage31.md`.

## Task 4B: Fix Other Current Operational Docs Found During Pre-release Audit

**Files:**

- Modify: `docs/candidate-discovery.md`
- Modify: `docs/daily-digest.md`
- Modify: `docs/scheduling.md`
- Modify: `docs/entity-packs.md`

- [ ] **Step 1: Carry repo-local path flags in current user-facing examples**

If current user-facing docs outside the original target set show the same
operational commands, keep them path-consistent too:

- `docs/candidate-discovery.md`: `candidates` examples should carry
  `--config-dir "$PWD/configs" --data-dir "$PWD/data"`.
- `docs/daily-digest.md`: `report` and `run` digest examples should carry
  `--config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir
  "$PWD/reports"`.
- `docs/scheduling.md`: scheduled `run` examples should carry
  `--config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir
  "$PWD/reports"`, `schedule-example` examples should carry the same explicit
  path flags, and cleanup should carry `--data-dir "$PWD/data"`.
- `docs/entity-packs.md`: examples that copy packs into `$PWD/configs` should
  create the local config/data/reports directories and carry the same
  `--config-dir`, `--data-dir`, and `--reports-dir` flags through
  `doctor`, `match`, `report`, `candidates`, and `trends` where applicable.

## Task 5: Verification And Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-41-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-41-release-review.md`

- [ ] **Step 1: Documentation checks**

Run:

```bash
rg -n "docs/cli-reference.md|CLI Reference|Command Reference" README.md docs/cli-reference.md
rg -n "import-signals .*--data-dir|import-signals-dir .*--data-dir|--imported-at" README.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md
rg -n "trends .*--data-dir|match .*--data-dir" docs/trend-deltas.md README.md docs/architecture.md docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md
rg -n "dashboard .*--host|dashboard .*--port|clean-old-data .*--data-dir|source-pack-lint .*--strict" README.md docs/dashboard.md docs/data-retention.md docs/source-packs.md
if rg -qn "release-gate-stage31" README.md; then
  echo "FAIL: README still presents Stage 31 release gate as current docs"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--data-dir"; then
  echo "FAIL: repo-local review tail command without --data-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " docs/manual-signal-import.md docs/community-signal-import.md docs/community-signal-quality.md docs/architecture.md | rg -v -- "--config-dir"; then
  echo "FAIL: repo-local review tail command without --config-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--data-dir"; then
  echo "FAIL: README review command without --data-dir"
  exit 1
fi
if rg -n "fashion-radar (match|report|candidates|trends) " README.md | rg -v -- "--help" | rg -v -- "--config-dir"; then
  echo "FAIL: README review command without --config-dir"
  exit 1
fi
scoped_docs=(
  README.md
  docs/cli-reference.md
  docs/manual-signal-import.md
  docs/community-signal-import.md
  docs/community-signal-quality.md
  docs/architecture.md
  docs/source-packs.md
  docs/trend-deltas.md
  docs/dashboard.md
  docs/data-retention.md
  docs/candidate-discovery.md
  docs/daily-digest.md
  docs/scheduling.md
  docs/entity-packs.md
  docs/github-upload-checklist.md
)
if rg -n "fashion-radar (report|candidates|trends|run) [^\\\\]*$" "${scoped_docs[@]}" | rg -v -- "--as-of|--help"; then
  echo "FAIL: one-line command requiring --as-of is documented without --as-of"
  exit 1
fi
rg -n -C 3 "fashion-radar (report|candidates|trends|run)( |$| \\\\)" "${scoped_docs[@]}"
rg -n "claude-code-stage-41" docs/reviews/claude-code-stage-41-*.md
git diff --check
```

- [ ] **Step 2: CLI help checks**

This docs-only stage validates CLI help coverage and keeps the existing runtime
smoke commands in `docs/github-upload-checklist.md`; it does not add new
runtime behavior checks.

Run:

```bash
UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar --help
for cmd in \
  init migrate-db doctor source-pack-lint entity-pack-lint \
  community-signal-lint community-signal-lint-dir \
  community-candidates community-candidates-dir community-handoff-workflow \
  import-signals import-signals-dir imported-signals imported-signals-summary \
  imported-entity-deltas imported-candidates imported-candidate-evidence \
  imported-review-workflow collect match report candidates trends \
  schedule-example dashboard clean-old-data run
do
  UV_NO_CONFIG=1 _TYPER_FORCE_DISABLE_TERMINAL=1 uv run fashion-radar "$cmd" --help
done
```

- [ ] **Step 3: Release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 4: Claude Code release review**

Create `docs/reviews/claude-code-stage-41-release-review-prompt.md` with the
diff summary, verification evidence, and confirmation that the change is
docs-only.
Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-41-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-41-release-review.md
```

Required approval phrase:

```text
APPROVED FOR STAGE 41 COMMIT AND PUSH
```

Fix all Critical and Important findings before commit. If fixes are needed,
store each follow-up release prompt/result as
`docs/reviews/claude-code-stage-41-release-rereview*.md`.

## Task 6: Commit, Push, And Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 41 files**

Confirm staged files are limited to the Stage 41 docs, spec/plan, and
claude-code-stage-41 review artifacts.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Refresh CLI documentation readiness"
```

Push with a token-free remote and one-shot auth only if needed. Do not persist
GitHub tokens in remote URLs or git config.

- [ ] **Step 3: Confirm GitHub Actions**

Confirm the latest pushed commit reaches GitHub and CI completes successfully.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- review artifacts produced;
- GitHub Actions result;
- uncommitted files;
- next step.
