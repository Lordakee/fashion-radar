# Stage 31 Release Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run and document a reproducible GitHub release-readiness gate for the current public command surface.

**Architecture:** This is a verification-first node. It runs local checks, build/smoke commands, boundary scans, and secret/artifact checks; it only edits docs/checklists if the verification finds drift.

**Tech Stack:** uv, pytest, ruff, git, installed-wheel CLI smoke, Markdown process docs. No new runtime dependencies.

---

## Boundaries

In scope:

- Release-gate verification commands.
- A concise `docs/release-gate-stage31.md` result document if checks pass.
- Small docs/checklist corrections if checks reveal drift.
- Stage 31 review artifacts.

Out of scope:

- New runtime features.
- Source connectors, scraping, crawling, platform automation, login, browser
  automation, watchers, schedulers, source acquisition, platform coverage
  verification, source ranking, or demand proof.
- Dependency or `uv.lock` changes.
- Leaving a dirty or mirror-rewritten `uv.lock` in the release-gate state.

## Task -1: Claude Code Plan Review Gate

**Files:**
- Add: `docs/reviews/claude-code-stage-31-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-31-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Write `docs/reviews/claude-code-stage-31-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 31 Plan Review Prompt

You are reviewing the Stage 31 release-gate plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Verify that Stage 31 will produce a reproducible GitHub release-readiness gate
for the current public command surface after Stage 30.

## Proposed Technical Approach

- Tech stack: Python package managed by `uv`, pytest, ruff, git, Markdown
  process docs, installed-wheel CLI smoke checks.
- Stage 31 is a verification/documentation node, not a runtime feature node.
- It must not add source connectors, scraping, crawling, platform automation,
  login/browser automation, watchers, schedulers, source acquisition, source
  ranking, demand proof, or platform coverage verification.
- It should run dependency checks with a mirror through
  `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple` where practical,
  but must not persist mirror URLs in `uv.lock`.
- It should confirm any `uv.lock` diff is only the known mirror URL rewrite,
  restore `uv.lock`, and then verify it is clean before claiming release
  readiness.
- It should build wheel/sdist, install the wheel into a temp venv, smoke the
  public CLI command surface, and specifically verify the Stage 30
  `community-handoff-workflow` command remains print-only and does not create
  supplied missing directories.
- It should run boundary scans, secret scans, artifact scans, package content
  checks, and public examples smoke checks.
- It should add concise release-gate evidence docs and review artifacts, then
  commit/push only Stage 31 files with no staged `uv.lock`. Push is allowed in
  this run because the user explicitly authorized it in the current thread; if
  this plan is reused later, push only after explicit user approval.

## Files To Review

- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`

## Output Required

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact approval
phrase:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS -p "$(cat docs/reviews/claude-code-stage-31-plan-review-prompt.md)" > docs/reviews/claude-code-stage-31-plan-review.md
```

Expected: Claude Code either reports no Critical/Important blockers and includes
`APPROVED FOR STAGE 31 RELEASE GATE`, or Stage 31 pauses to fix the blockers and
rereview before Task 0 begins.

## Task 0: Preflight

**Files:**
- No edits.

- [ ] **Step 1: Check repository state**

Run:

```bash
git status --short --branch
git status --short --branch --untracked-files=all
git log --oneline -5
git status --short -- uv.lock
git diff -- uv.lock
git diff --numstat -- uv.lock
git diff -- uv.lock > /tmp/fashion-radar-stage31-uv-lock-before.diff
git diff --cached --name-only
```

Expected:

- `main` tracks `origin/main`.
- No staged changes before Stage 31 plan artifacts are staged.
- `uv.lock` may have the known unstaged mirror diff before the gate runs.
  Stage 31 must clean it before release-gate success can be claimed.
- the pre-restore `uv.lock` diff snapshot is written under `/tmp`, not the repo.

- [ ] **Step 2: Restore mirror-rewritten lockfile before release checks**

Run:

```bash
.venv/bin/python - <<'PY'
import subprocess
import sys

diff = subprocess.run(
    ["git", "diff", "--unified=0", "--", "uv.lock"],
    check=True,
    text=True,
    capture_output=True,
).stdout

bad_lines = []
for line in diff.splitlines():
    if line.startswith(("diff --git", "index ", "--- ", "+++ ", "@@")):
        continue
    if line.startswith("-"):
        if (
            "https://pypi.org/simple" not in line
            and "https://files.pythonhosted.org/" not in line
        ):
            bad_lines.append(line)
    elif line.startswith("+"):
        if "https://pypi.tuna.tsinghua.edu.cn/" not in line:
            bad_lines.append(line)
    elif line:
        bad_lines.append(line)

if bad_lines:
    print("uv.lock has non-mirror-rewrite diff lines:", file=sys.stderr)
    for line in bad_lines[:50]:
        print(line, file=sys.stderr)
    raise SystemExit(1)
PY
git restore uv.lock
git status --short -- uv.lock
git diff -- uv.lock
git diff --cached -- uv.lock
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
```

Expected:

- the Python guard exits `0`, proving any pre-restore diff only rewrites
  committed PyPI/files.pythonhosted URLs to the local Tsinghua mirror;
- `git status --short -- uv.lock` prints nothing;
- `git diff -- uv.lock` prints nothing;
- `git diff --cached -- uv.lock` prints nothing;
- mirror scan exits with no matches.

## Task 1: Core Verification

**Files:**
- No edits unless a check exposes drift.

- [ ] **Step 1: Dependency, tests, lint, format, diff**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff --cached --check
```

Expected: every command exits `0`. The mirror-backed sync check verifies the
local install path can use the configured mirror, while `UV_NO_CONFIG=1` keeps
release lock checks pinned to the public lockfile URLs instead of user-level
mirror config.

- [ ] **Step 2: Build and installed-wheel smoke**

Run:

```bash
rm -rf /tmp/fashion-radar-dist-stage31 /tmp/fashion-radar-wheel-stage31
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage31
uv venv /tmp/fashion-radar-wheel-stage31/.venv
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python /tmp/fashion-radar-wheel-stage31/.venv/bin/python /tmp/fashion-radar-dist-stage31/*.whl
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar --help
for cmd in init doctor source-pack-lint entity-pack-lint community-signal-lint community-signal-lint-dir community-candidates community-candidates-dir community-handoff-workflow import-signals-dir schedule-example dashboard report candidates trends imported-candidate-evidence imported-candidates imported-review-workflow imported-entity-deltas imported-signals-summary imported-signals import-signals collect match clean-old-data run; do
  /tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar "$cmd" --help >/dev/null
done
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-handoff-workflow "/tmp/fashion-radar-wheel-stage31/missing exports ? # & %" --input-format csv --pattern "*.csv" --config-dir "/tmp/fashion-radar-wheel-stage31/config ? # & %" --data-dir "/tmp/fashion-radar-wheel-stage31/data ? # & %" --as-of 2026-06-13T12:00:00Z --source-name "Community | Tool Export" --format json > /tmp/fashion-radar-wheel-stage31/workflow.json
```

Then assert:

```bash
/tmp/fashion-radar-wheel-stage31/.venv/bin/python - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path("/tmp/fashion-radar-wheel-stage31/workflow.json").read_text())
assert payload["execution_mode"] == "print_only"
assert payload["step_count"] == 5
assert [step["name"] for step in payload["steps"]] == [
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert [step["suggested_effect"] for step in payload["steps"]] == [
    "read_only",
    "read_only",
    "read_only",
    "updates_local_imports",
    "print_only",
]
commands = [step["command"] for step in payload["steps"]]
assert commands[0].startswith("fashion-radar community-signal-lint-dir ")
assert commands[1].startswith("fashion-radar community-candidates-dir ")
assert commands[2].startswith("fashion-radar import-signals-dir ")
assert " --dry-run" in commands[2]
assert commands[3].startswith("fashion-radar import-signals-dir ")
assert " --dry-run" not in commands[3]
assert commands[4].startswith("fashion-radar imported-review-workflow ")
assert not Path("/tmp/fashion-radar-wheel-stage31/missing exports ? # & %").exists()
assert not Path("/tmp/fashion-radar-wheel-stage31/config ? # & %").exists()
assert not Path("/tmp/fashion-radar-wheel-stage31/data ? # & %").exists()
PY
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-handoff-workflow "/tmp/fashion-radar-wheel-stage31/missing exports table ? # & %" --input-format csv --pattern "*.csv" --config-dir "/tmp/fashion-radar-wheel-stage31/config table ? # & %" --data-dir "/tmp/fashion-radar-wheel-stage31/data table ? # & %" --as-of 2026-06-13T12:00:00Z --source-name "Community | Tool Export" --format table > /tmp/fashion-radar-wheel-stage31/workflow-table.txt
rg -n 'Commands were not executed\.' /tmp/fashion-radar-wheel-stage31/workflow-table.txt
```

If redirecting JSON output to `workflow.json`, keep it under `/tmp`, not the
repo.

- [ ] **Step 3: Package content and public examples smoke**

Run:

```bash
.venv/bin/python - <<'PY'
import tarfile
import zipfile
from pathlib import Path

dist = Path("/tmp/fashion-radar-dist-stage31")
wheel = next(dist.glob("*.whl"))
sdist = next(dist.glob("*.tar.gz"))

wheel_expected = {
    "fashion_radar/cli.py",
    "fashion_radar/community_handoff_workflow.py",
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
}
with zipfile.ZipFile(wheel) as archive:
    wheel_names = set(archive.namelist())
missing_wheel = sorted(wheel_expected - wheel_names)
if missing_wheel:
    raise SystemExit(f"Missing wheel paths: {missing_wheel}")

sdist_expected_suffixes = {
    "README.md",
    "docs/source-boundaries.md",
    "docs/github-upload-checklist.md",
    "configs/source-packs/fashion-public.example.yaml",
    "configs/entity-packs/fashion-watchlist.example.yaml",
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "schemas/community-signals.schema.json",
}
with tarfile.open(sdist) as archive:
    sdist_names = set(archive.getnames())

missing_sdist = []
for suffix in sorted(sdist_expected_suffixes):
    if not any(name.endswith(f"/{suffix}") for name in sdist_names):
        missing_sdist.append(suffix)
if missing_sdist:
    raise SystemExit(f"Missing sdist paths: {missing_sdist}")
PY
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json >/tmp/source-pack-stage31.json
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml --format json >/tmp/entity-pack-stage31.json
rm -rf /tmp/fashion-radar-example-config-stage31
mkdir -p /tmp/fashion-radar-example-config-stage31
cp configs/scoring.example.yaml /tmp/fashion-radar-example-config-stage31/scoring.yaml
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export" --strict
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir /tmp/fashion-radar-example-config-stage31 --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json >/tmp/community-candidates-stage31.json
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-candidates-dir examples --input-format csv --pattern "community-signals.example.csv" --config-dir /tmp/fashion-radar-example-config-stage31 --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json >/tmp/community-candidates-dir-stage31.json
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-signal-lint examples/community-signals.example.json --input-format json --source-name "Community Tool Export" --strict
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-candidates examples/community-signals.example.json --input-format json --config-dir /tmp/fashion-radar-example-config-stage31 --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json >/tmp/community-candidates-json-stage31.json
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar community-candidates-dir examples --input-format json --pattern "community-signals.example.json" --config-dir /tmp/fashion-radar-example-config-stage31 --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json >/tmp/community-candidates-dir-json-stage31.json
rm -rf /tmp/fashion-radar-import-dry-run-stage31
mkdir -p /tmp/fashion-radar-import-dry-run-stage31/csv /tmp/fashion-radar-import-dry-run-stage31/json
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir /tmp/fashion-radar-import-dry-run-stage31/csv --dry-run
/tmp/fashion-radar-wheel-stage31/.venv/bin/fashion-radar import-signals examples/community-signals.example.json --format json --source-name "Community Tool Export" --data-dir /tmp/fashion-radar-import-dry-run-stage31/json --dry-run
find /tmp/fashion-radar-import-dry-run-stage31 -type f -print
```

Expected: every command exits `0`, the temporary example config is created
under `/tmp`, and the final `find` command prints no files.

## Task 2: Boundary And Secret Checks

**Files:**
- No edits unless a check exposes drift.

- [ ] **Step 1: Boundary scan**

Run:

```bash
rg -n "scrape|scraper|scraping|crawler|platform automation|browser automation|login|account automation|source acquisition|platform coverage|proof of demand|rank sources|source ranking|monitoring|watcher|scheduler" README.md docs src tests
rg -n 'scrap|crawler|platform automation|browser automation|login|account automation|source acquisition|platform coverage|proof of demand|rank sources|source ranking|monitor|watch folders|scheduler|connector' README.md CHANGELOG.md docs/source-boundaries.md docs/github-upload-checklist.md docs/architecture.md docs/community-signal-import.md docs/community-signal-quality.md src/fashion_radar/cli.py src/fashion_radar/community_handoff_workflow.py
git diff -U0 -- README.md CHANGELOG.md docs src tests | rg -n 'scrap|crawl|crawler|Playwright|Selenium|browser automation|login|cookie|account automation|proxy|CAPTCHA|platform API|unofficial API|source acquisition|platform coverage|proof of demand|source ranking|rank sources|monitor|watcher|watch folder|scheduler|connector|Google News RSS|social-platform' || true
git diff --cached -U0 -- README.md CHANGELOG.md docs src tests | rg -n 'scrap|crawl|crawler|Playwright|Selenium|browser automation|login|cookie|account automation|proxy|CAPTCHA|platform API|unofficial API|source acquisition|platform coverage|proof of demand|source ranking|rank sources|monitor|watcher|watch folder|scheduler|connector|Google News RSS|social-platform' || true
```

Expected: matches are existing boundary statements, review prompts/plans, or
negative language. No new positive capability claims. Diff-scoped matches, if
any, are manually reviewed and summarized in the release-gate result doc.

- [ ] **Step 2: Secret and artifact scan**

Run:

```bash
git remote get-url origin
git remote -v
git config --get-regexp '^http\..*extraheader$' || true
git status --short -- uv.lock
git diff -- uv.lock
git diff --cached -- uv.lock
git status --short -- data reports .venv dist build '*.sqlite' '*.db' || true
git diff --cached --name-only
rg -n 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY|AWS_SECRET_ACCESS_KEY\\s*=|AWS_ACCESS_KEY_ID\\s*=' . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
git ls-files \
  | rg -v '^(data|reports)/README\.md$' \
  | rg -n '(^|/)(\.env|\.env\..*|\.pypirc|pip\.conf|uv\.toml|build|dist|data|reports)/|\.sqlite($|-)|\.sqlite3($|-)|\.db($|-)|\.eml$|cookie|session|browser'
git ls-files .codegraph | rg -v '^.codegraph/.gitignore$'
```

Expected:

- remote URL is token-free;
- no persistent extraheader;
- no staged `uv.lock`;
- no dirty `uv.lock`;
- no generated local DB/report/build/venv artifacts staged.
- no token/private-key hits;
- no tracked generated artifacts; `data/README.md` and `reports/README.md` are
  allowed tracked directory documentation files;
- `.codegraph/.gitignore` is the only tracked `.codegraph` file.

After staging Stage 31 files in Task 5, run this allowlist check:

```bash
git diff --cached --name-only \
  | rg -v '^(docs/release-gate-stage31\.md|docs/github-upload-checklist\.md|docs/superpowers/(specs|plans)/2026-06-13-stage-31-release-gate-(design|plan)\.md|docs/reviews/claude-code-stage-31-.*\.md)$'
```

Expected: no output.

## Task 3: Release Gate Result Doc

**Files:**
- Create: `docs/release-gate-stage31.md`
- Modify: `docs/github-upload-checklist.md` only if checklist drift is found.

- [ ] **Step 1: Write concise result doc**

Create `docs/release-gate-stage31.md` with:

```markdown
# Stage 31 Release Gate

Date: 2026-06-13

## Scope

Release-readiness verification for the current public command surface after
Stage 30.

## Verified

- Dependency check with mirror-backed uv sync check.
- Public-lockfile check with `UV_NO_CONFIG=1` so user-level mirror config cannot
  rewrite `uv.lock`.
- Full pytest suite.
- Ruff lint and format checks.
- Git whitespace checks.
- Wheel build.
- Installed-wheel command smoke, including `community-handoff-workflow`.
- CSV and JSON public community signal example lint/preview smoke.
- CSV and JSON public community signal dry-run import smoke with no temp data
  files created.
- Boundary scan for prohibited platform/source-acquisition implications.
- Secret/artifact checks for remote URL, persistent extraheaders, staged
  `uv.lock`, and generated local artifacts.

## Notes

- Earlier stages left a known local mirror rewrite in `uv.lock`; Stage 31
  restored `uv.lock` to the committed lockfile before the gate.
- `uv.lock` is clean, unstaged, and contains no mirror URLs.
- The local machine has user-level uv mirror config; release lock checks used
  `UV_NO_CONFIG=1` to keep the publishable lockfile registry-neutral.
- `community-handoff-workflow` installed-wheel JSON smoke confirmed
  `execution_mode: print_only`, `step_count: 5`, expected command strings, and
  `--dry-run` only on the dry-run import step without creating the supplied
  missing directory, config directory, or data directory.
- `community-handoff-workflow` table smoke confirmed commands were not executed.
- Diff-scoped boundary matches were reviewed as negative boundary language,
  review prompts, or release-gate instructions.
```

- [ ] **Step 2: Verify result doc**

Run:

```bash
git diff --check -- docs/release-gate-stage31.md docs/github-upload-checklist.md
```

Expected: exits `0`.

## Task 4: Claude Code Review

**Files:**
- Add: `docs/reviews/claude-code-stage-31-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-31-release-review.md`

- [ ] **Step 1: Request review**

Prompt Claude Code to review:

- release-gate evidence;
- no runtime feature creep;
- no positive scraping/source-acquisition/platform automation claims;
- no staged `uv.lock`;
- no secrets or generated local artifacts;
- installed-wheel smoke coverage;
- staged file allowlist;
- current-thread explicit push authorization and one-shot auth hygiene.

Required approval phrase:

```text
APPROVED FOR STAGE 31 COMMIT AND PUSH
```

Run with max effort:

```bash
claude --effort max --permission-mode plan -p "$(cat docs/reviews/claude-code-stage-31-release-review-prompt.md)" > docs/reviews/claude-code-stage-31-release-review.md
```

Fix Critical/Important findings and rereview before commit.

## Task 5: Commit, Push, Handoff

**Files:**
- Git only.

- [ ] **Step 1: Stage only Stage 31 files**

Run:

```bash
git add docs/release-gate-stage31.md docs/github-upload-checklist.md docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md docs/reviews/claude-code-stage-31-*.md
git diff --cached --name-only
git diff --cached -- uv.lock
git diff --cached --name-only \
  | rg -v '^(docs/release-gate-stage31\.md|docs/github-upload-checklist\.md|docs/superpowers/(specs|plans)/2026-06-13-stage-31-release-gate-(design|plan)\.md|docs/reviews/claude-code-stage-31-.*\.md)$'
```

Expected: no staged `uv.lock`; the allowlist rejection command prints no
output.

- [ ] **Step 2: Commit and push**

Run:

```bash
git commit -m "Add release gate verification"
```

Push with temporary `http.extraheader`; do not persist token.

This push step is authorized for the current run because the user explicitly
provided the GitHub remote and authorized push in this thread. If this plan is
reused later, stop after commit unless the user explicitly approves pushing.

- [ ] **Step 3: Post-push checks**

Run:

```bash
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
git remote get-url origin
git config --get-regexp '^http\..*extraheader$' || true
git status --short --branch
git diff --quiet --cached
```

Expected: `HEAD` and `origin/main` match; remote URL is token-free; no
extraheader is persisted; staged diff is empty; `uv.lock` is clean.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.
