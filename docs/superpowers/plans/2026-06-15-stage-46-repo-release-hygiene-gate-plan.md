# Stage 46 Repo Release Hygiene Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local release hygiene checks that prevent repository and package
archives from publishing secrets, generated local artifacts, private exports,
or runtime state.

**Architecture:** A dependency-free script checks git-tracked paths, selected
high-risk untracked paths, persistent git remote/config leaks, and
high-confidence secret-like tracked content. The existing package archive
checker gains a shared forbidden-member classifier, and CI/docs/tests keep the
release hygiene and archive gates aligned.

**Tech Stack:** Python 3.11 standard library (`argparse`, `fnmatch`,
`subprocess`, `pathlib`, `re`, `zipfile`, `tarfile`), pytest, Ruff, GitHub
Actions YAML, Markdown, `uv`, local Claude Code CLI with `--effort max`.

---

## Boundaries

In scope:

- Create: `scripts/check_release_hygiene.py`
- Create: `tests/test_release_hygiene.py`
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`
- Modify: `.gitignore`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Add: `docs/reviews/claude-code-stage-46-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-46-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-46-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-46-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-46-release-review.md`

Out of scope:

- Source acquisition, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, media downloading, schedulers,
  watchers, monitors, or external services.
- Product compliance-review functionality.
- Dependency or lockfile changes.
- Runtime CLI, dashboard, database schema, collector, scoring, generated data,
  or generated report behavior.
- PyPI publishing, GitHub release creation, artifact upload, or persistent
  remote configuration changes. The user has separately authorized the node
  completion process to commit, push with a non-persistent auth header, and
  confirm CI after local verification and Claude Code release review.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-46-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-46-plan-review.md`

- [ ] **Step 1: Confirm the prompt exists**

The prompt file should contain the Stage 46 objective, technical approach,
files to review, boundaries, and approval phrase:

```text
APPROVED FOR STAGE 46 REPO RELEASE HYGIENE GATE
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-46-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-46-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 46 REPO RELEASE HYGIENE GATE`. Fix blockers before Task 0.
If fixes are needed, store follow-up prompt/results as
`docs/reviews/claude-code-stage-46-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 46 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 46 spec, plan, and Claude Code Stage 46 plan review prompt/result files.
If unrelated files appear, stop and investigate before editing.

## Task 1: Add Package Archive Forbidden-Member Guard

**Files:**

- Modify: `tests/test_package_archives.py`
- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Write failing archive denylist tests**

Add tests to `tests/test_package_archives.py` using the existing
`write_wheel`, `write_sdist`, and `run_checker` helpers.

Required sdist cases:

```python
def test_rejects_sdist_with_env_file(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [".env.local"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: .env.local" in result.stderr


def test_rejects_sdist_with_generated_database(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["data/fashion-radar.sqlite"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive contains forbidden release member: "
        "data/fashion-radar.sqlite"
    ) in result.stderr


def test_rejects_sdist_with_generated_report(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["reports/latest.json"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: reports/latest.json" in result.stderr


def test_rejects_sdist_with_generated_config(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + ["configs/sources.yaml"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: configs/sources.yaml" in result.stderr


def test_rejects_sdist_with_codegraph_runtime_database(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [".codegraph/codegraph.db"])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive contains forbidden release member: .codegraph/codegraph.db"
    ) in result.stderr


def test_rejects_sdist_with_cookie_session_or_private_export(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=SDIST_FILES
        + ["cookies.txt", "session.json", "private-source-export.csv"],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "sdist archive contains forbidden release member: cookies.txt" in result.stderr
    assert "sdist archive contains forbidden release member: session.json" in result.stderr
    assert (
        "sdist archive contains forbidden release member: private-source-export.csv"
        in result.stderr
    )
```

Required wheel cases:

```python
def test_rejects_wheel_with_bytecode_cache(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(
        build_dir,
        files=WHEEL_FILES | {"fashion_radar/__pycache__/cli.cpython-311.pyc": ""},
    )
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive contains forbidden release member: "
        "fashion_radar/__pycache__/cli.cpython-311.pyc"
    ) in result.stderr


def test_allows_release_archive_public_placeholders(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=SDIST_FILES
        + [".env.example", ".codegraph/.gitignore", "data/README.md", "reports/README.md"],
    )

    result = run_checker(build_dir)

    assert result.returncode == 0
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Expected before implementation: the new denylist tests fail because forbidden
members are not checked.

- [ ] **Step 3: Implement the archive forbidden-member classifier**

In `scripts/check_package_archives.py`, add constants and helpers near the
required-path constants:

```python
ALLOWED_RELEASE_PATHS = {
    ".env.example",
    ".codegraph/.gitignore",
    "data/README.md",
    "reports/README.md",
}

GENERATED_CONFIG_PATHS = {
    "configs/sources.yaml",
    "configs/entities.yaml",
    "configs/scoring.yaml",
}

FORBIDDEN_RELEASE_NAMES = (
    "cookies.txt",
    "cookies.json",
    "session.json",
    "storage-state.json",
    "browser-profiles",
    "private-export",
    "private-source-export",
    "private-exports",
)

LOCAL_CREDENTIAL_CONFIG_NAMES = {
    ".pypirc",
    "pip.conf",
    "pip.ini",
    "uv.toml",
    ".netrc",
    ".npmrc",
}
```

Add `forbidden_release_member(path: str) -> bool` and
`forbidden_release_members(paths: set[str], *, archive_label: str) -> list[str]`
that:

- normalizes slashes and strips leading `./`;
- returns false for `ALLOWED_RELEASE_PATHS`;
- rejects `.env` and `.env.*`;
- rejects any segment equal to `__pycache__`, `.pytest_cache`, `.ruff_cache`,
  `.venv`, `build`, `dist`, or ending in `.egg-info`;
- rejects `*.pyc`, `*.pyo`, and `*.pyd`;
- rejects `.codegraph/*` except the allowlist;
- rejects `data/**` and `reports/**` except the allowlist;
- rejects `GENERATED_CONFIG_PATHS`;
- rejects `*.sqlite`, `*.sqlite-*`, `*.sqlite3`, `*.sqlite3-*`, `*.db`, and
  `*.db-*`;
- rejects basenames or path segments that match `FORBIDDEN_RELEASE_NAMES`;
- rejects `LOCAL_CREDENTIAL_CONFIG_NAMES`;
- rejects `*.pem` and `*.key`.

Call this helper from `validate_wheel` after `paths = set(archive.namelist())`
and from `validate_sdist` after `paths = normalize_sdist_paths(...)`.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Expected: all archive tests pass.

## Task 2: Add Repository Release Hygiene Script

**Files:**

- Create: `tests/test_release_hygiene.py`
- Create: `scripts/check_release_hygiene.py`

- [ ] **Step 1: Write failing release hygiene tests**

Create `tests/test_release_hygiene.py` with temp-repo helpers and these
behaviors:

```python
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_release_hygiene.py"


def run_checker(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        text=True,
        capture_output=True,
        check=False,
    )


def git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "init")
    return repo
```

Test cases should verify:

- clean temp repo exits `0` and prints `Release hygiene checks passed.`;
- tracked `.env.local` fails with `forbidden tracked path: .env.local`;
- tracked `.codegraph/.gitignore` is allowed but tracked
  `.codegraph/codegraph.db` fails;
- unignored local `cookies.txt` fails with
  `forbidden untracked path: cookies.txt`;
- tracked `README.md` containing a fake `ghp_` token fails and redacts the
  token value;
- persistent remote URL with a token-like value fails without printing the
  token value;
- persistent `http.*.extraheader` authorization config fails without printing
  the header value;
- prefix-only examples such as `ghp_` in tracked docs/tests are not reported;
- running outside a git repository exits `1` with a clean error and no
  traceback;
- the current repository tracked file list contains no forbidden tracked paths.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_release_hygiene.py -q
```

Expected before implementation: FAIL because `scripts/check_release_hygiene.py`
does not exist.

- [ ] **Step 3: Implement `scripts/check_release_hygiene.py`**

Implement a dependency-free script with:

- `parse_args() -> argparse.Namespace`
- `main() -> int`
- `run_git(repo_root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]`
- `tracked_paths(repo_root: Path) -> list[str]`
- `untracked_paths(repo_root: Path) -> list[str]`
- `forbidden_tracked_path(path: str) -> bool`
- `forbidden_untracked_path(path: str) -> bool`
- `remote_leak_errors(repo_root: Path) -> list[str]`
- `content_leak_errors(repo_root: Path, paths: list[str]) -> list[str]`
- `is_probably_text_file(path: Path) -> bool`
- `redact_secret(text: str) -> str`

The script should:

- print every finding to stderr;
- return `1` when any finding exists;
- print `Release hygiene checks passed.` to stdout and return `0` otherwise;
- avoid printing token/header values by reporting only the path, line number,
  config key, or remote name plus `<redacted>`;
- skip binary files by reading a bounded byte sample before text decoding;
- use length-aware valid-looking GitHub token patterns, for example `ghp_`
  followed by 36 token characters, instead of prefix-only detection;
- reject tracked, untracked, and archive paths named `.pypirc`, `pip.conf`,
  `pip.ini`, `uv.toml`, `.netrc`, or `.npmrc`;
- fail cleanly when `--repo-root` is not a git repository;
- not use network access;
- not invoke external tools except git in the target repository.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_release_hygiene.py -q
```

Expected: all release hygiene tests pass.

## Task 3: Wire Release Hygiene Into Gitignore, CI, Checklist, And Drift Tests

**Files:**

- Modify: `.gitignore`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Write failing docs/CI drift tests**

In `tests/test_cli_docs.py`, extend
`test_package_archive_smoke_command_is_documented_and_in_ci` so both checklist
and CI contain:

```python
hygiene_command = "UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root ."
```

and assert `"scripts/check_release_hygiene.py"` appears in both documents.

Add a test that `docs/github-upload-checklist.md` names key excluded artifact
categories:

```python
def test_upload_checklist_documents_release_hygiene_excludes() -> None:
    text = _read(UPLOAD_CHECKLIST)

    for term in (
        ".env.local",
        "cookies",
        "account/session files",
        "private source exports",
        ".codegraph",
        "generated runtime configs",
        "local SQLite databases",
    ):
        assert term in text
```

- [ ] **Step 2: Run docs drift tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected before docs/CI updates: FAIL because the release hygiene command and
some exclude terms are not documented yet.

- [ ] **Step 3: Update `.gitignore`**

Add narrow patterns:

```gitignore
.env.*
!.env.example
.pypirc
pip.conf
pip.ini
uv.toml
.netrc
.npmrc
cookies*.txt
cookies*.json
session*.json
storage-state*.json
browser-profiles/
exports/
private-exports/
*private-export*.csv
data/private*/
data/export*.jsonl
configs/**/*.local.yaml
configs/**/private*.yaml
*.pem
*.key
```

Keep existing public example files, fixtures, docs, `data/README.md`, and
`reports/README.md` visible.

- [ ] **Step 4: Update CI and upload checklist**

In `.github/workflows/ci.yml`, add this command after dependency installation
and before lint:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
```

Also change the checkout step to avoid persisting runner credentials:

```yaml
- uses: actions/checkout@v4
  with:
    persist-credentials: false
```

In `docs/github-upload-checklist.md`, add the same command before package
smoke and expand the exclude section to explicitly name `.env.local`,
generated runtime configs, cookies/session files, private exports, key
material, local credential config files, and CodeGraph runtime files. Note that
the release hygiene script checks only unignored untracked files, so ignored
local artifacts are blocked from normal git publication by `.gitignore` rather
than reported every run.

- [ ] **Step 5: Run docs drift tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: docs drift tests pass.

## Task 4: Stage 46 Verification And Claude Code Release Review

**Files:**

- Create: `docs/reviews/claude-code-stage-46-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-46-release-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_release_hygiene.py tests/test_package_archives.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

Expected: all commands exit `0`.

- [ ] **Step 2: Run full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all commands exit `0`; `uv.lock` remains unchanged.

- [ ] **Step 3: Request Claude Code release review**

Create a release review prompt that asks Claude Code to review the Stage 46
diff, tests, docs, CI wiring, boundary adherence, and verification evidence.
Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-46-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-46-release-review.md
```

Expected: no Critical or Important blockers and the result includes:

```text
APPROVED FOR STAGE 46 COMMIT AND PUSH
```

Fix Critical and Important findings, rerun affected verification, and request a
rereview before committing.

## Task 5: User-Authorized Commit, Push, And Confirm GitHub Actions

**Files:**

- Git only.

This is a node completion step, not product release hygiene functionality. The
user has explicitly authorized committing and pushing this repository. Do not
run this step until local verification passes and Claude Code release review
has approved the Stage 46 diff.

- [ ] **Step 1: Commit Stage 46**

Run:

```bash
git status --short
git add .gitignore .github/workflows/ci.yml docs/github-upload-checklist.md \
  docs/reviews/claude-code-stage-46-*.md \
  docs/superpowers/specs/2026-06-15-stage-46-repo-release-hygiene-gate-design.md \
  docs/superpowers/plans/2026-06-15-stage-46-repo-release-hygiene-gate-plan.md \
  scripts/check_package_archives.py scripts/check_release_hygiene.py \
  tests/test_package_archives.py tests/test_release_hygiene.py tests/test_cli_docs.py
git commit -m "Harden release hygiene checks"
```

- [ ] **Step 2: Push with non-persistent token header**

Run without printing or storing the token in git config:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
BASIC="$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)"
GIT_TERMINAL_PROMPT=0 git -c http.extraHeader="Authorization: Basic ${BASIC}" push origin main
```

- [ ] **Step 3: Confirm GitHub Actions**

Run:

```bash
gh run list --repo Lordakee/fashion-radar --branch main --limit 1
```

If the latest run is in progress, poll it until success or failure. If `gh`
authentication is unavailable, use git push success plus the Actions URL from
the push output and report that local verification completed.
