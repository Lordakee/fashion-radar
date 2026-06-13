# Stage 28B Community Candidate Directory Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review, verify, commit, and push Stage 28 `community-candidates-dir` after Claude Code reviews the added code and tests.

**Architecture:** Treat this as a release-control node. Generate a Claude Code code-review prompt, run review with `--effort max`, fix any Critical/Important findings, run full local verification, build and smoke-test a wheel from a temporary output directory, then commit/push only intended files while leaving the pre-existing `uv.lock` mirror diff unstaged.

**Tech Stack:** Python 3.11, pytest, ruff, uv with Tsinghua mirror for dependency/build operations, Typer CLI smoke tests, Git, Claude Code CLI.

---

## Stage 28B Boundary

In scope:

- create `docs/reviews/claude-code-stage-28-code-review-prompt.md`;
- create Claude Code review result files;
- run verification and build/smoke checks;
- fix Stage 28 code/tests only if review or verification finds defects;
- commit and push approved Stage 28 source/tests/docs/review artifacts.

Out of scope:

- new product features;
- broad README/user docs;
- source collectors, platform connectors, account automation, browser
  automation, watch folders, schedulers, SQLite writes, report/dashboard writes,
  or entity YAML generation;
- committing `uv.lock`;
- persisting GitHub credentials.

## Task 1: Claude Code Review Prompt

**Files:**
- Create: `docs/reviews/claude-code-stage-28-code-review-prompt.md`

- [ ] **Step 1: Create the code-review prompt**

Create a prompt that asks Claude Code to review:

```text
src/fashion_radar/community_candidates.py
src/fashion_radar/cli.py
tests/test_community_candidates.py
tests/test_cli.py
docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md
docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md
docs/reviews/claude-code-stage-28-plan-review.md
docs/reviews/claude-code-stage-28-plan-rereview.md
```

The prompt must require findings by severity and the exact approval phrase:

```text
APPROVED FOR STAGE 28 RELEASE COMMIT AND PUSH
```

It must ask Claude Code to check that `community-candidates-dir`:

- is local, read-only, non-recursive, and aggregate-only;
- does not emit directory paths, file paths, filenames, row URLs, row titles,
  summaries, raw text, normalized keys, candidate contexts, raw validation
  findings, account/private fields, or representative item details;
- uses generic error messages for invalid directories, no matching files,
  invalid files, invalid rows, and unexpected exceptions;
- validates invalid `--as-of`, invalid `--input-format`, and negative `--limit`
  before config load and directory read;
- does not add scraping, crawling, browser automation, source acquisition,
  watch folders, schedulers, platform connectors, SQLite writes, reports,
  dashboards, or entity YAML generation.

- [ ] **Step 2: Run Claude Code review**

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-28-code-review-prompt.md | tee docs/reviews/claude-code-stage-28-code-review.md
```

Expected: command exits `0`. Critical and Important findings block commit and
push.

## Task 2: Review Fix Loop

**Files:**
- Modify only Stage 28 source/test files if needed:
  - `src/fashion_radar/community_candidates.py`
  - `src/fashion_radar/cli.py`
  - `tests/test_community_candidates.py`
  - `tests/test_cli.py`
- Create rereview prompt/result files only if blocking findings exist.

- [ ] **Step 1: If Claude Code reports Critical or Important findings, fix them**

For each blocking finding:

1. identify the exact failing behavior;
2. add or adjust a focused regression test;
3. make the smallest source change;
4. run the affected test command.

- [ ] **Step 2: Request rereview if fixes were made**

If fixes were made, create a concise rereview prompt and run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-28-code-rereview-prompt.md | tee docs/reviews/claude-code-stage-28-code-rereview.md
```

Expected: no Critical or Important findings, and the approval phrase is present
before commit/push.

## Task 3: Full Verification

**Files:**
- No source edits expected.

- [ ] **Step 1: Dependency and test verification**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 2: Diff, boundary, artifact, and secret scans**

Run:

```bash
git status --short --branch
git diff --name-only -- . ':!uv.lock'
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md docs/superpowers/specs/2026-06-13-stage-28b-community-candidates-dir-release-design.md docs/superpowers/plans/2026-06-13-stage-28b-community-candidates-dir-release-plan.md docs/reviews/claude-code-stage-28-code-review-prompt.md
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md docs/superpowers/specs/2026-06-13-stage-28b-community-candidates-dir-release-design.md docs/superpowers/plans/2026-06-13-stage-28b-community-candidates-dir-release-plan.md docs/reviews/claude-code-stage-28-code-review-prompt.md | rg -n "scrap|crawler|crawl|captcha|login|cookie|account automation|watch folder|scheduler|platform API|Instagram|TikTok|小红书|X/Twitter"
git ls-files --others --exclude-standard | rg -n "(^data/|^reports/|\\.db$|\\.sqlite$|\\.sqlite3$|fashion-radar-.*\\.(json|md)$|digest|\\.eml$|latest\\.|report-index\\.json)"
```

Expected:

- `uv.lock` is not listed in the intended diff list;
- high-risk diff scan has no matches except negative boundary language in docs
  if present;
- untracked artifact scan has no matches;
- secret scan has no matches.

The `rg` scan commands exit `1` when no matches are found. Treat exit `1` with
empty output as the expected clean result for these scan-only commands.

Also run a local secret scan for common GitHub token prefixes,
authorization-header fragments, and private-key markers over the intended
source/test/docs files. Keep the exact secret-scan pattern in the shell command,
not in this tracked plan file.

- [ ] **Step 3: Build and installed-wheel smoke**

Run:

```bash
rm -rf /tmp/fashion-radar-dist-stage28
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage28
tmp_stage28_install="$(mktemp -d)"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv venv "$tmp_stage28_install/.venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple "$tmp_stage28_install/.venv/bin/python" -m pip install /tmp/fashion-radar-dist-stage28/*.whl
"$tmp_stage28_install/.venv/bin/fashion-radar" community-candidates-dir --help
```

Then create a temporary config/input fixture outside the repo and run:

```bash
mkdir -p "$tmp_stage28_install/configs" "$tmp_stage28_install/signals"
cat > "$tmp_stage28_install/configs/scoring.yaml" <<'YAML'
version: 1
scoring: {}
candidate_discovery:
  review_min_current_mentions: 1
  review_min_distinct_sources: 1
  min_single_token_mentions: 1
  min_single_token_distinct_sources: 1
YAML
cat > "$tmp_stage28_install/configs/entities.yaml" <<'YAML'
version: 1
entities: []
YAML
cat > "$tmp_stage28_install/signals/community.csv" <<'CSV'
url,title,published_at,summary,source_name,collected_at
https://example.com/private,Le Teckel bag mention,2026-06-13T09:00:00Z,Private summary,Community,2026-06-13T10:00:00Z
CSV
"$tmp_stage28_install/.venv/bin/fashion-radar" community-candidates-dir "$tmp_stage28_install/signals" --config-dir "$tmp_stage28_install/configs" --as-of 2026-06-13T12:00:00Z --format json
"$tmp_stage28_install/.venv/bin/fashion-radar" community-candidates-dir "$tmp_stage28_install/missing" --config-dir "$tmp_stage28_install/configs" --as-of 2026-06-13T12:00:00Z
```

Expected: success smoke exits `0`; missing-directory smoke exits non-zero and
does not echo the missing path.

## Task 4: Commit And Push

**Files:**
- Stage intended Stage 28/28B files only.
- Do not stage `uv.lock`.

- [ ] **Step 1: Stage and commit intended files**

Run:

```bash
git add src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md docs/reviews/claude-code-stage-28-plan-review-prompt.md docs/reviews/claude-code-stage-28-plan-review.md docs/reviews/claude-code-stage-28-plan-rereview-prompt.md docs/reviews/claude-code-stage-28-plan-rereview.md docs/superpowers/specs/2026-06-13-stage-28b-community-candidates-dir-release-design.md docs/superpowers/plans/2026-06-13-stage-28b-community-candidates-dir-release-plan.md docs/reviews/claude-code-stage-28b-plan-review-prompt.md docs/reviews/claude-code-stage-28b-plan-review.md docs/reviews/claude-code-stage-28-code-review-prompt.md docs/reviews/claude-code-stage-28-code-review.md
git status --short
git commit -m "Add community candidate directory preview"
```

Expected: `uv.lock` remains unstaged; commit succeeds.

- [ ] **Step 2: Push without persisting credentials**

Use a non-persistent Git extraheader for the push. Do not put the token into
the remote URL and do not write credential helpers or config files.

After push, run:

```bash
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
git remote get-url origin
git config --get-regexp '^http\\..*extraheader$'
git status --short --branch
git diff --quiet --cached
```

Expected:

- `HEAD` and `origin/main` match;
- remote URL is token-free;
- no persisted `http.*extraheader` values;
- only the pre-existing unstaged `uv.lock` diff may remain.

`git config --get-regexp '^http\\..*extraheader$'` exits `1` when no persisted
extraheaders exist. Treat exit `1` with empty output as the expected clean
result for that check.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.
