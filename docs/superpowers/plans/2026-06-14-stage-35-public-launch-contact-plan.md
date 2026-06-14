# Stage 35 Public Launch Contact Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Make public security/conduct reporting paths actionable and align CI
package smoke with the release checklist before public launch.

**Architecture:** Docs/repository-settings/CI-only release hygiene node. Use
GitHub private vulnerability reporting for sensitive security issues, a
dedicated public moderation contact issue template for conduct reports, a
complete CI wheel archive assertion for packaged templates, and a gated
private-to-public repository visibility switch after the private repository
commit has passed local and GitHub Actions verification.

**Tech Stack:** GitHub REST API, GitHub Actions YAML, Markdown docs/templates,
uv, pytest, ruff. No runtime dependency or source-code changes.

---

## Boundaries

In scope:

- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `.github/ISSUE_TEMPLATE/conduct_report.yml`
- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- Stage 35 plan/review artifacts.
- GitHub repository visibility setting.
- GitHub repository private vulnerability reporting setting.

Out of scope:

- Runtime code changes.
- Dependency or `uv.lock` changes.
- Source connectors, scraping, crawling, platform automation, browser
  automation, login/cookie flows, watchers, schedulers, source acquisition,
  source ranking, demand proof, platform coverage verification, or social
  platform functionality.
- PyPI publishing or artifact uploads.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Add: `docs/reviews/claude-code-stage-35-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-35-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-35-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 35 Plan Review Prompt

You are reviewing the Stage 35 public launch contact plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make the repository's public security and conduct reporting paths actionable
before public GitHub launch, without changing runtime behavior.

## Proposed Technical Approach

- Because the repository may still be private, defer GitHub private
  vulnerability reporting enablement until after the private-repo commit is
  pushed and CI succeeds. Then switch the repository public, immediately enable
  PVR with the dedicated GitHub REST endpoint, and verify `{"enabled": true}`.
- Update `SECURITY.md` to point sensitive reports to the repository Security tab
  private vulnerability reporting path.
- Update `CODE_OF_CONDUCT.md` to point conduct reports to a dedicated GitHub
  conduct/moderation issue template.
- Add `.github/ISSUE_TEMPLATE/conduct_report.yml` with redaction warnings and
  no request for secrets, private security details, local databases, generated
  reports, or doxxing material.
- Add a complete wheel archive content assertion to CI after `uv build --out-dir
  "$tmp_build"` so CI verifies all required packaged templates/configs and
  matches `docs/github-upload-checklist.md`.
- If public visibility or PVR enablement fails after the visibility switch,
  immediately attempt to restore private visibility and block the stage.
- Keep Stage 35 docs/CI/settings-only: no runtime code, dependencies, `uv.lock`,
  source connectors, scraping/crawling/platform automation, watchers,
  schedulers, source acquisition, ranking, demand proof, platform coverage, or
  social-platform functionality.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-35-public-launch-contact-design.md`
- `docs/superpowers/plans/2026-06-14-stage-35-public-launch-contact-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 35 PUBLIC LAUNCH CONTACT
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-35-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-35-plan-review.md
```

Expected: approval phrase appears, or the plan is revised and rereviewed before
Task 1.

## Task 1: GitHub Visibility And PVR Preflight

**Files:**

- Repository setting only.

- [ ] **Step 1: Check current repository visibility and permissions**

Run with the user-authorized GitHub token stored only in a temporary shell
variable. Do not persist the token:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import json
import os
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    data = json.load(response)
print(json.dumps({
    "full_name": data.get("full_name"),
    "private": data.get("private"),
    "permissions": data.get("permissions"),
}, ensure_ascii=True))
PY
unset TOKEN
```

Expected: output confirms the repository and admin permission. If `private` is
`true`, continue with local docs/CI changes, but defer PVR verification to Task
6 after the repository is made public.

- [ ] **Step 2: Record the private-repository PVR limitation**

If the repository is private, do not treat a current PVR endpoint `404` as a
docs blocker. Record that the dedicated endpoint is expected to be verified only
after public visibility is enabled in Task 6. If the repository is already
public, run the dedicated check now:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import json
import os
import urllib.error
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar/private-vulnerability-reporting",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
    },
)
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", "replace")[:500]
    raise SystemExit(json.dumps({"status": exc.code, "error": body}, ensure_ascii=True))

enabled = data.get("enabled")
if not isinstance(enabled, bool):
    raise SystemExit(f"Ambiguous private vulnerability reporting response: {data!r}")
print(json.dumps({"private_vulnerability_reporting_enabled": enabled}, ensure_ascii=True))
PY
unset TOKEN
```

Expected for an already public repository: the endpoint returns a boolean
`enabled` value. If already public and the endpoint cannot be checked, stop
before relying on PVR.

## Task 2: Security And Conduct Docs

**Files:**

- Modify: `SECURITY.md`
- Modify: `CODE_OF_CONDUCT.md`
- Add: `.github/ISSUE_TEMPLATE/conduct_report.yml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update `SECURITY.md` reporting path**

Replace the deferred reporting paragraph with concrete GitHub private reporting
guidance:

```markdown
Use GitHub private vulnerability reporting from this repository's
**Security** tab for sensitive security reports. Do not include sensitive
details in public issues.

If the Security tab is unavailable, open a minimal public issue that says a
private security contact is needed, without sensitive details.
```

Keep the existing redaction and scope guidance.

- [ ] **Step 2: Update `CODE_OF_CONDUCT.md` enforcement contact**

Replace the deferred launch sentence with:

```markdown
For conduct or moderation concerns, use the **Conduct or moderation contact**
issue template. Do not include secrets, private security details, private source
exports, local databases, generated reports, or doxxing material in public
issues. For highly sensitive matters, open a minimal moderation-contact issue
and wait for maintainer instructions.
```

- [ ] **Step 3: Add conduct report issue template**

Create `.github/ISSUE_TEMPLATE/conduct_report.yml`:

```yaml
name: Conduct or moderation contact
description: Ask maintainers for moderation help without posting sensitive details.
title: "[Conduct]: "
body:
  - type: markdown
    attributes:
      value: |
        Do not include secrets, cookies, session files, browser profiles, private source exports, local databases, generated reports, private security details, or doxxing material.
        If this is a sensitive security issue, use GitHub private vulnerability reporting from the Security tab instead.
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: Briefly describe the moderation concern without sensitive details.
    validations:
      required: true
  - type: dropdown
    id: area
    attributes:
      label: Area
      options:
        - issue or discussion
        - pull request
        - documentation
        - project boundary pressure
        - other
    validations:
      required: true
  - type: textarea
    id: requested_action
    attributes:
      label: Requested maintainer action
      description: What do you need maintainers to review or moderate?
    validations:
      required: true
  - type: checkboxes
    id: boundaries
    attributes:
      label: Safety checks
      options:
        - label: I did not include secrets, cookies, session files, browser profiles, private source exports, local databases, generated reports, private security details, or doxxing material.
          required: true
        - label: This is not a request for social scraping, login-cookie use, proxy/account pools, CAPTCHA bypass, or paywall bypass.
          required: true
        - label: If this is a sensitive security issue, I will use GitHub private vulnerability reporting instead of this public issue.
          required: true
```

- [ ] **Step 4: Update changelog**

Add:

```markdown
- Added concrete GitHub security and conduct reporting paths for public launch.
```

## Task 3: CI Package Smoke Alignment

**Files:**

- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add wheel archive assertion**

After `uv build --out-dir "$tmp_build"`, add a complete wheel content
assertion:

```yaml
          uv run python - "$tmp_build"/*.whl <<'PY'
          import sys
          import zipfile

          expected = {
              "fashion_radar/templates/daily_report.md",
              "fashion_radar/templates/configs/sources.example.yaml",
              "fashion_radar/templates/configs/entities.example.yaml",
              "fashion_radar/templates/configs/scoring.example.yaml",
          }
          with zipfile.ZipFile(sys.argv[1]) as wheel:
              names = set(wheel.namelist())
          missing = sorted(expected - names)
          if missing:
              raise SystemExit("Missing wheel template files: " + ", ".join(missing))
          print("Wheel template files present:", ", ".join(sorted(expected)))
          PY
```

- [ ] **Step 2: Verify CI snippet**

Run:

```bash
rg -n 'uv build --out-dir|Wheel template files present|fashion_radar/templates' .github/workflows/ci.yml
```

Expected: the zipfile assertion appears after build and before wheel install.

## Task 4: Verification

**Files:**

- No runtime files.

- [ ] **Step 1: Full local verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 2: CI package smoke command**

Run the build command block locally:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python - "$tmp_build"/*.whl <<'PY'
import sys
import zipfile

expected = {
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
}
with zipfile.ZipFile(sys.argv[1]) as wheel:
    names = set(wheel.namelist())
missing = sorted(expected - names)
if missing:
    raise SystemExit("Missing wheel template files: " + ", ".join(missing))
print("Wheel template files present:", ", ".join(sorted(expected)))
PY
```

- [ ] **Step 3: Boundary and secret scans**

Run diff-scoped scans for prohibited platform/source-acquisition implications,
secrets, `uv.lock`, dependency, runtime, data, report, and build artifact
changes:

```bash
git diff --name-only
if git diff --name-only | rg '^(uv\.lock|pyproject\.toml|src/|tests/|data/|reports/|dist/|build/)'; then
    echo "Unexpected Stage 35 file scope"
    exit 1
fi
git diff -U0 -- . ':!docs/reviews/claude-code-stage-35-plan-review.md' | rg -ni 'scrap|crawl|crawler|Playwright|Selenium|browser automation|login|cookie|account automation|proxy|CAPTCHA|platform API|unofficial API|source acquisition|proof of demand|source ranking|watcher|scheduler|connector' || true
if git diff -U0 -- .github/workflows/ci.yml pyproject.toml uv.lock src tests | rg -ni 'playwright|selenium|snscrape|instaloader|tiktok-api|rednote|xiaohongshu|crawler|scraper|login cookie|cookie jar|proxy pool|captcha'; then
    echo "Unexpected platform automation tooling in Stage 35 executable surfaces"
    exit 1
fi
if git diff -U0 -- . | rg -n 'ghp_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}|sk-[A-Za-z0-9_-]{32,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY'; then
    echo "Secret-like content found in Stage 35 diff"
    exit 1
fi
```

Before any public visibility switch, also run a history-scoped secret scan:

```bash
if git grep -n -I -E 'ghp_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}|sk-[A-Za-z0-9_-]{32,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY' $(git rev-list --all) -- .; then
    echo "Secret-like content found in tracked history"
    exit 1
fi
```

## Task 5: Claude Code Release Review

**Files:**

- Add: `docs/reviews/claude-code-stage-35-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-35-release-review.md`

- [ ] **Step 1: Request release review**

Ask Claude Code to review the Stage 35 diff, GitHub setting/visibility evidence,
verification evidence, pre-public secret/history scan evidence, and scope
boundaries.

Required approval phrase:

```text
APPROVED FOR STAGE 35 COMMIT, PUSH, PUBLIC VISIBILITY, AND PVR
```

Fix Critical/Important findings before commit.

## Task 6: Commit, Push, CI, Public Visibility, And PVR

**Files:**

- Git and repository settings only.

- [ ] **Step 1: Stage only Stage 35 files**

Run:

```bash
git add SECURITY.md CODE_OF_CONDUCT.md .github/ISSUE_TEMPLATE/conduct_report.yml .github/workflows/ci.yml CHANGELOG.md docs/superpowers/specs/2026-06-14-stage-35-public-launch-contact-design.md docs/superpowers/plans/2026-06-14-stage-35-public-launch-contact-plan.md docs/reviews/claude-code-stage-35-*.md
git diff --cached --name-only
git diff --cached -- uv.lock pyproject.toml src tests data reports
git diff --cached --check
```

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Finalize public launch contact paths" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Before commit, confirm the current execution context contains explicit user
authorization to commit and push to `https://github.com/Lordakee/fashion-radar`.
If that authorization is absent after context compaction or tool handoff, stop
and ask the user. If authorization is present, commit and push with a one-shot
HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions while the repository is still private**

Poll the latest GitHub Actions run for the pushed commit until it completes.
If it fails, return to systematic debugging with job logs.

- [ ] **Step 4: Final pre-public checks**

Before changing repository visibility, confirm:

```bash
git status --short --branch
git diff --quiet
git diff --cached --quiet
git remote -v
git config --get-all http.https://github.com/.extraheader || true
if git grep -n -I -E 'ghp_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}|sk-[A-Za-z0-9_-]{32,}|BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY' $(git rev-list --all) -- .; then
    echo "Secret-like content found in tracked history"
    exit 1
fi
```

Expected: clean worktree, token-free remote/config output, no secret matches in
tracked history.

- [ ] **Step 5: Switch the repository to public visibility**

Only do this if the current execution context still contains explicit user
authorization to make `https://github.com/Lordakee/fashion-radar` public. If
authorization is absent after context compaction or tool handoff, stop and ask
the user.

Run with a temporary token variable only:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import json
import os
import urllib.request

payload = json.dumps({"private": False}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar",
    data=payload,
    method="PATCH",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
        "Content-Type": "application/json",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    data = json.load(response)
if data.get("private") is not False:
    raise SystemExit(f"Repository did not become public: {data!r}")
print(json.dumps({"full_name": data.get("full_name"), "private": data.get("private")}, ensure_ascii=True))
PY
unset TOKEN
```

Expected: `private` is `false`. If the visibility switch fails, stop without
attempting PVR.

- [ ] **Step 6: Enable and verify private vulnerability reporting**

After public visibility is confirmed, enable PVR:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import os
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar/private-vulnerability-reporting",
    method="PUT",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    print(response.status)
PY
unset TOKEN
```

Then verify with the dedicated endpoint:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import json
import os
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar/private-vulnerability-reporting",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    data = json.load(response)
enabled = data.get("enabled")
if enabled is not True:
    raise SystemExit(f"Private vulnerability reporting not enabled: {data!r}")
print(json.dumps({"private_vulnerability_reporting_enabled": True}, ensure_ascii=True))
PY
unset TOKEN
```

Expected: enable returns HTTP `200` or `204`, and verify prints
`private_vulnerability_reporting_enabled: true`.

If PVR enablement or verification fails after the repository becomes public,
immediately attempt to restore private visibility:

```bash
export TOKEN='[USER_PROVIDED_TOKEN]'
python3 - <<'PY'
import json
import os
import urllib.request

payload = json.dumps({"private": True}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/Lordakee/fashion-radar",
    data=payload,
    method="PATCH",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "fashion-radar-stage35",
        "Content-Type": "application/json",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    data = json.load(response)
if data.get("private") is not True:
    raise SystemExit(f"Repository did not return to private visibility: {data!r}")
print(json.dumps({"full_name": data.get("full_name"), "private": data.get("private")}, ensure_ascii=True))
PY
unset TOKEN
```

Then stop Stage 35 and report the API response.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub repository visibility status;
- GitHub private vulnerability reporting status;
- GitHub Actions result;
- uncommitted files;
- next step.
