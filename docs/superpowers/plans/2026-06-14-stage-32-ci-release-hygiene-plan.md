# Stage 32 CI Release Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align GitHub CI, contributor docs, PR/issue templates, and upload smoke commands with the Stage 31 release-gate lockfile and artifact hygiene.

**Architecture:** This is a docs/CI-only hygiene node. CI gains explicit public lockfile validation and mirror-marker rejection, while docs/templates describe mirror-backed local installs separately from public lockfile checks.

**Tech Stack:** GitHub Actions YAML, Markdown docs/templates, uv, pytest, ruff, shell smoke commands. No new runtime dependencies.

---

## Boundaries

In scope:

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `AGENTS.md`
- `README.md`
- `CONTRIBUTING.md`
- `docs/dependency-mirrors.md`
- `docs/github-upload-checklist.md`
- `docs/release-gate-stage31.md`
- `CHANGELOG.md`
- Stage 32 plan/review artifacts.

Out of scope:

- Runtime code changes.
- Source connectors, scraping, crawling, platform automation, browser
  automation, login/cookie flows, watchers, schedulers, source acquisition,
  source ranking, demand proof, or platform coverage verification.
- Dependency or `uv.lock` changes.
- PyPI publishing or build artifact upload.

## Task -1: Claude Code Plan Review Gate

**Files:**
- Add: `docs/reviews/claude-code-stage-32-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-32-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-32-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 32 Plan Review Prompt

You are reviewing the Stage 32 CI release hygiene plan for the `fashion-radar`
repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Stage 32 should align GitHub CI, contributor docs, PR/issue templates, and upload
smoke commands with the Stage 31 release-gate findings.

## Proposed Technical Approach

- CI should run `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check` before the normal install.
- CI should reject mirror/index URL markers in `uv.lock`.
- CI build/dashboard smoke should build to a temp directory and install the
  wheel from that temp directory in the same GitHub Actions step, not from
  repository `dist/`.
- Contributor docs/templates should use `UV_NO_CONFIG=1` for public lockfile
  checks and keep `UV_DEFAULT_INDEX=... uv sync --frozen ...` for mirror-backed
  local installs.
- Upload package smoke docs should avoid a bare `python` command and use
  `uv run python` or a temp venv interpreter.
- Stage 32 must not add runtime features, platform connectors, scraping,
  crawling, browser automation, source acquisition, watchers, schedulers,
  source ranking, demand proof, or platform coverage claims.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md`
- `docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 32 CI RELEASE HYGIENE
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS -p "$(cat docs/reviews/claude-code-stage-32-plan-review-prompt.md)" > docs/reviews/claude-code-stage-32-plan-review.md
```

Expected: Claude Code reports no Critical/Important blockers and includes
`APPROVED FOR STAGE 32 CI RELEASE HYGIENE`, or Stage 32 pauses to fix blockers
and rerun review before Task 1.

## Task 1: CI Workflow Hygiene

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Update CI lockfile and build smoke**

Change `.github/workflows/ci.yml` so the test job has these steps before lint:

```yaml
      - name: Public lockfile check
        run: |
          UV_NO_CONFIG=1 uv lock --check
          UV_NO_CONFIG=1 uv sync --locked --dev --check
          if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
            exit 1
          fi
      - name: Install dependencies
        run: UV_NO_CONFIG=1 uv sync --locked --dev
```

Replace the separate build and dashboard extra smoke steps with one combined
step so `tmp_build` remains in the same shell process:

```yaml
      - name: Build, installed CLI smoke, and dashboard extra smoke
        run: |
          tmp_build="$(mktemp -d)"
          uv build --out-dir "$tmp_build"
          tmp_env="$(mktemp -d)"
          uv venv "$tmp_env/venv"
          uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
          tmp_run="$(mktemp -d)"
          "$tmp_env/venv/bin/fashion-radar" --help
          "$tmp_env/venv/bin/fashion-radar" init --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
          "$tmp_env/venv/bin/fashion-radar" doctor --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
          "$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
          tmp_dash="$(mktemp -d)"
          uv venv "$tmp_dash/venv"
          wheel_path="$(ls "$tmp_build"/*.whl | head -n 1)"
          uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
          "$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

- [ ] **Step 2: Verify CI YAML content**

Run:

```bash
sed -n '1,140p' .github/workflows/ci.yml
rg -n 'UV_NO_CONFIG=1 uv lock --check|UV_NO_CONFIG=1 uv sync --locked --dev --check|tmp_build|dist/\*\.whl' .github/workflows/ci.yml
```

Expected:

- `UV_NO_CONFIG=1 uv lock --check` is present.
- mirror URL scan is present.
- install uses `UV_NO_CONFIG=1 uv sync --locked --dev`.
- build smoke uses `tmp_build`.
- no `dist/*.whl` references remain.
- dashboard extra smoke uses `"$tmp_build"` in the same step as `uv build`.

## Task 2: Contributor And Upload Docs

**Files:**
- Modify: `CONTRIBUTING.md`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `.github/pull_request_template.md`
- Modify: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Modify: `docs/dependency-mirrors.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `docs/release-gate-stage31.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update contributor verification commands**

In `CONTRIBUTING.md`, replace:

```bash
uv lock --check
uv sync --locked --dev
```

with:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Add one short sentence below the block:

```markdown
`UV_NO_CONFIG=1` keeps release lockfile checks independent of user-level mirror configuration.
```

Keep the setup command near the top of `CONTRIBUTING.md` as plain
`uv sync --locked --dev`; this change is for verification, not ordinary install
setup.

- [ ] **Step 2: Update PR and issue templates**

In `.github/pull_request_template.md`, replace:

```markdown
- [ ] `uv sync --locked --dev`
- [ ] `uv lock --check`
```

with:

```markdown
- [ ] `UV_NO_CONFIG=1 uv sync --locked --dev --check`
- [ ] `UV_NO_CONFIG=1 uv lock --check`
```

In `.github/ISSUE_TEMPLATE/bug_report.yml`, replace the verification placeholder
line:

```text
uv lock --check
```

with:

```text
UV_NO_CONFIG=1 uv lock --check
```

- [ ] **Step 3: Update agent and README guidance**

In `AGENTS.md`, replace the dependency guidance bullet:

```markdown
- Use `uv sync --locked --dev` and `uv lock --check` without mirror env vars for
  CI, verification, and committed lockfile checks.
```

with:

```markdown
- Use `UV_NO_CONFIG=1 uv sync --locked --dev --check` and
  `UV_NO_CONFIG=1 uv lock --check` for CI, verification, and committed lockfile
  checks, so user-level uv mirror config cannot affect the public lockfile.
```

In the README documentation list, add:

```markdown
- [docs/dependency-mirrors.md](docs/dependency-mirrors.md)
- [docs/release-gate-stage31.md](docs/release-gate-stage31.md)
```

near `docs/github-upload-checklist.md`.

After the README development command block, add:

```markdown
For PR/release verification, use [CONTRIBUTING.md](CONTRIBUTING.md) or
[docs/github-upload-checklist.md](docs/github-upload-checklist.md); public
lockfile checks should use `UV_NO_CONFIG=1`.
```

- [ ] **Step 4: Update dependency mirror docs**

In `docs/dependency-mirrors.md`, update the project practice bullet:

```markdown
- Use `UV_NO_CONFIG=1 uv sync --locked --dev` and `UV_NO_CONFIG=1 uv lock --check` for CI and release checks, so user-level mirror config cannot rewrite or invalidate the public lockfile.
```

Add a short note after the mirror warning:

```markdown
If `~/.config/uv/uv.toml` sets a mirror as the default index, run public lockfile checks with `UV_NO_CONFIG=1`.
```

- [ ] **Step 5: Update upload checklist package smoke**

In `docs/github-upload-checklist.md`, replace the bare Python package listing
command:

```bash
python -m zipfile -l "$tmp_build"/*.whl | rg 'fashion_radar/templates/(daily_report.md|configs/(sources|entities|scoring)\.example\.yaml)'
```

with:

```bash
uv run python -m zipfile -l "$tmp_build"/*.whl | rg 'fashion_radar/templates/(daily_report.md|configs/(sources|entities|scoring)\.example\.yaml)'
```

The rest of the installed-wheel smoke should keep using the temp venv
interpreter.

- [ ] **Step 6: Update Stage 31 artifact summary**

In `docs/release-gate-stage31.md`, replace the explicit artifact list with:

```markdown
- All Stage 31 Claude Code review artifacts are stored under
  `docs/reviews/claude-code-stage-31-*.md`.
```

This avoids stale partial lists while preserving the artifact location.

- [ ] **Step 7: Update changelog**

Add this `Changed` bullet:

```markdown
- Aligned CI, contribution docs, PR/issue templates, and upload smoke commands with release lockfile checks that ignore user-level uv mirror config.
```

## Task 3: Verification And Boundary Review

**Files:**
- No new runtime files.

- [ ] **Step 1: Run focused docs/CI checks**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

paths = [
    Path("README.md"),
    Path("AGENTS.md"),
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path(".github/pull_request_template.md"),
    Path(".github/ISSUE_TEMPLATE/bug_report.yml"),
    Path("docs/dependency-mirrors.md"),
    Path("docs/github-upload-checklist.md"),
    Path("docs/release-gate-stage31.md"),
]
missing = []
for path in paths:
    for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("#"):
            continue
        target_path = target.split("#", 1)[0]
        if target_path and not (path.parent / target_path).exists():
            missing.append(f"{path}: {target}")
if missing:
    raise SystemExit("\n".join(missing))
PY
rg -n 'uv lock --check|uv sync --locked --dev|UV_NO_CONFIG=1|UV_DEFAULT_INDEX|python -m zipfile|dist/\*\.whl' AGENTS.md README.md CONTRIBUTING.md .github docs/dependency-mirrors.md docs/github-upload-checklist.md .github/workflows/ci.yml
git diff --check
git diff --cached --check
```

Expected:

- link checker exits `0`;
- current public docs/templates and AGENTS guidance use `UV_NO_CONFIG=1` for
  public lockfile checks;
- no bare `python -m zipfile` in `docs/github-upload-checklist.md`;
- no `dist/*.whl` in `.github/workflows/ci.yml`;
- diff checks pass.

- [ ] **Step 2: Run full local verification**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Expected: every command exits `0`.

- [ ] **Step 3: Run build smoke matching CI**

Run:

```bash
tmp_build="$(mktemp -d)"
uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
tmp_run="$(mktemp -d)"
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/fashion-radar" init --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/fashion-radar" doctor --config-dir "$tmp_run/config" --data-dir "$tmp_run/data" --reports-dir "$tmp_run/reports"
"$tmp_env/venv/bin/python" -c "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
tmp_dash="$(mktemp -d)"
uv venv "$tmp_dash/venv"
wheel_path="$(ls "$tmp_build"/*.whl | head -n 1)"
uv pip install --python "$tmp_dash/venv/bin/python" "${wheel_path}[dashboard]"
"$tmp_dash/venv/bin/python" -c "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
```

Expected: every command exits `0`; generated build and venv artifacts stay in
`/tmp`.

- [ ] **Step 4: Boundary scan**

Run:

```bash
git diff -U0 -- .github README.md CONTRIBUTING.md CHANGELOG.md docs \
  | rg -n 'scrap|crawl|crawler|Playwright|Selenium|browser automation|login|cookie|account automation|proxy|CAPTCHA|platform API|unofficial API|source acquisition|platform coverage|proof of demand|source ranking|rank sources|monitor|watcher|watch folder|scheduler|connector|Google News RSS|social-platform' || true
```

Expected: matches, if any, are negative boundary language or existing template
checkboxes, not new positive capability claims.

## Task 4: Claude Code Release Review

**Files:**
- Add: `docs/reviews/claude-code-stage-32-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-32-release-review.md`

- [ ] **Step 1: Request release review**

Ask Claude Code to review:

- changed CI and docs/templates;
- verification evidence;
- no `uv.lock` changes;
- no runtime feature changes;
- no prohibited platform/source-acquisition implications;
- no secrets/generated artifacts;
- push hygiene.

Required approval phrase:

```text
APPROVED FOR STAGE 32 COMMIT AND PUSH
```

Run with max effort. To avoid self-referential empty review artifacts, write the
Claude output to `/tmp` first, then copy it into
`docs/reviews/claude-code-stage-32-release-review.md` after Claude exits.

Fix Critical/Important findings and rerun review before commit.

## Task 5: Commit, Push, Handoff

**Files:**
- Git only.

- [ ] **Step 1: Stage only Stage 32 files**

Run:

```bash
git add .github/workflows/ci.yml .github/pull_request_template.md .github/ISSUE_TEMPLATE/bug_report.yml AGENTS.md README.md CONTRIBUTING.md CHANGELOG.md docs/dependency-mirrors.md docs/github-upload-checklist.md docs/release-gate-stage31.md docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md docs/reviews/claude-code-stage-32-*.md
git diff --cached --name-only
git diff --cached -- uv.lock
git diff --cached --check
```

Expected: no staged `uv.lock`.

- [ ] **Step 2: Commit and push**

Run:

```bash
git commit -m "Align CI release hygiene"
```

Push with a temporary `http.extraheader`; do not persist the token.

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
extraheader is persisted; staged diff is empty; working tree is clean.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.
