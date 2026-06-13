# Stage 27C Release Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the approved Stage 27A code and Stage 27B docs, request final Claude Code review, commit the Stage 27 files while excluding `uv.lock`, and push the commit to GitHub.

**Architecture:** Stage 27C is a release-verification and publishing node. It does not add product behavior; it runs full verification, creates final review records, stages an explicit allowlist, commits, and pushes with a non-persistent GitHub token mechanism.

**Tech Stack:** Python/pytest, Ruff, uv, Typer CLI smoke tests, git, ripgrep, Claude Code plan/review CLI.

---

## Boundary

In scope:

- Final verification of Stage 27A `community-candidates` code and Stage 27B docs.
- Final Claude Code review prompt/result docs.
- Explicit staging of approved Stage 27 files.
- One commit and push to `origin/main`.

Out of scope:

- Editing production code or tests unless final review finds a Critical or Important issue.
- Editing user-facing docs unless final review finds a Critical or Important issue.
- Staging or committing `uv.lock`.
- Staging generated artifacts, databases, reports, caches, browser/account state, or tokens.
- Persisting the GitHub token in files, git config, shell profile, or committed docs.

## Task 1: Baseline Status And Stage 27B Approval Check

**Files:**
- No file edits.

- [ ] **Step 1: Confirm current branch and known dirty state**

Run:

```bash
git status --short --branch
git remote -v
rg -n "APPROVED FOR STAGE 27A COMPLETION" docs/reviews/claude-code-stage-27a-code-review.md
rg -n "APPROVED FOR STAGE 27B DOCS COMPLETION" docs/reviews/claude-code-stage-27b-docs-review.md
```

Expected:

- branch is `main` tracking `origin/main`;
- remote URL is token-free;
- Stage 27A and Stage 27B approval phrases are present;
- `uv.lock` may be modified but must remain unstaged.

## Task 2: Full Test, Lint, Format, And Lock Verification

**Files:**
- No file edits.

- [ ] **Step 1: Run Python tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run Ruff checks**

Run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Expected: both commands exit `0`.

- [ ] **Step 3: Run whitespace and dependency checks**

Run:

```bash
git diff --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --quiet -- pyproject.toml
tmp_lock_check="$(mktemp -d)"
git archive HEAD | tar -x -C "$tmp_lock_check"
uv lock --check --default-index https://pypi.org/simple --project "$tmp_lock_check"
```

Expected: all commands exit `0`; `uv.lock` remains unstaged. The mirror-backed
`uv sync` check verifies installability without rewriting the lockfile; the
`uv lock --check` command intentionally uses default PyPI in a clean temporary
checkout of `HEAD` because the active worktree has a known pre-existing
mirror-backed `uv.lock` diff that must remain unstaged and uncommitted. The
`pyproject.toml` diff check proves Stage 27 did not change dependency metadata,
so the committed public lockfile is the lockfile being verified.

## Task 3: Stage 27B Boundary Verification

**Files:**
- No file edits.

- [ ] **Step 1: Re-run required negative boundary phrase checks**

Run:

```bash
set -e
for phrase in \
  "not proof of demand" \
  "not platform coverage" \
  "not source ranking" \
  "not a source connector" \
  "not an acquisition workflow" \
  "not a scraper" \
  "not a watcher" \
  "not a scheduler" \
  "not a report writer" \
  "not a dashboard updater" \
  "not a database import" \
  "not an entity YAML generator"
do
  rg -n "$phrase" docs/source-boundaries.md >/dev/null
done
```

Expected: exit `0`.

- [ ] **Step 2: Re-run unsafe positive boundary classifier**

Run:

```bash
.venv/bin/python - <<'PY'
import re
import subprocess
import sys

prohibited = re.compile(
    r"platform-wide|market-wide|platform coverage|proof of demand|verified demand|"
    r"real-time monitoring|platform search|social monitoring|monitoring|"
    r"source health|source quality|source coverage|source ranking|top sources|"
    r"top-sources|scraper|scraping|watcher|watchers|watch folder|watch folders|"
    r"scheduler|scheduled|scheduling|acquisition|report generation|report writer|"
    r"reporting|generates reports|dashboard update|dashboard updates|dashboard updater|"
    r"database import|SQLite import|SQLite write|SQLite writes|entity YAML|"
    r"entity config|source connector|source connectors",
    re.IGNORECASE,
)
safe_phrases = [
    "not proof of demand",
    "not platform coverage",
    "not source ranking",
    "not a source connector",
    "not an acquisition workflow",
    "not a scraper",
    "not a watcher",
    "not a scheduler",
    "not a report writer",
    "not a dashboard updater",
    "not a database import",
    "not an entity YAML generator",
    "no SQLite writes",
]

diff = subprocess.run(
    [
        "git",
        "diff",
        "-U0",
        "--",
        "README.md",
        "CHANGELOG.md",
        "docs/community-signal-import.md",
        "docs/community-signal-quality.md",
        "docs/candidate-discovery.md",
        "docs/architecture.md",
        "docs/source-boundaries.md",
        "docs/github-upload-checklist.md",
    ],
    check=True,
    capture_output=True,
    text=True,
).stdout
violations = []
for line_number, line in enumerate(diff.splitlines(), start=1):
    if not line.startswith("+") or line.startswith("+++"):
        continue
    content = line[1:]
    scrubbed = content
    for phrase in safe_phrases:
        scrubbed = re.sub(re.escape(phrase), "", scrubbed, flags=re.IGNORECASE)
    if prohibited.search(scrubbed):
        violations.append(f"{line_number}: {content}")

if violations:
    print("Unsafe positive boundary terms in added docs lines:")
    print("\n".join(violations))
    sys.exit(1)
PY
```

Expected: no output, exit `0`.

## Task 4: Build And Installed-Wheel Smoke

**Files:**
- No file edits.

- [ ] **Step 1: Build wheel and sdist into `/tmp`**

Run:

```bash
rm -rf /tmp/fashion-radar-dist-stage27
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage27
```

Expected: build exits `0` and artifacts are only under `/tmp/fashion-radar-dist-stage27`.

- [ ] **Step 2: Install wheel into a temporary environment and smoke test CLI**

Run:

```bash
tmp_env="$(mktemp -d)"
tmp_smoke="$(mktemp -d)"
export TMP_SMOKE="$tmp_smoke"
export FASHION_RADAR_DATA_DIR="$tmp_smoke/data"
export FASHION_RADAR_REPORTS_DIR="$tmp_smoke/reports"
uv venv "$tmp_env/venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage27/*.whl
mkdir -p "$tmp_smoke/config"
printf 'version: 1\nscoring: {}\ncandidate_discovery:\n  min_current_mentions: 1\n  review_min_current_mentions: 1\n' > "$tmp_smoke/config/scoring.yaml"
printf 'url,title,published_at,summary,source_name\nhttps://example.com/a,Le Teckel bag spotted,2026-06-12T08:00:00Z,Local sanitized note,Community Tool Export\n' > "$tmp_smoke/community-signals.csv"
printf 'url,title,published_at,summary,source_weight\nhttps://private.example/secret,Private Runway Note,not-a-date,Private summary text,private-weight\n' > "$tmp_smoke/bad-community-signals.csv"
"$tmp_env/venv/bin/fashion-radar" --help >/dev/null
"$tmp_env/venv/bin/fashion-radar" community-candidates --help >/dev/null
"$tmp_env/venv/bin/fashion-radar" community-candidates "$tmp_smoke/community-signals.csv" --input-format csv --config-dir "$tmp_smoke/config" --as-of "2026-06-13T12:00:00Z" --source-name "Community Tool Export" --format json >"$tmp_smoke/community-candidates-smoke.json"
if "$tmp_env/venv/bin/fashion-radar" community-candidates "$tmp_smoke/bad-community-signals.csv" --input-format csv --config-dir "$tmp_smoke/config" --as-of "2026-06-13T12:00:00Z" >"$tmp_smoke/bad.stdout" 2>"$tmp_smoke/bad.stderr"; then exit 1; fi
"$tmp_env/venv/bin/python" - <<'PY'
import json
import os
from pathlib import Path

tmp_smoke = Path(os.environ["TMP_SMOKE"])
payload = json.loads((tmp_smoke / "community-candidates-smoke.json").read_text(encoding="utf-8"))
assert payload["input_format"] == "csv"
assert payload["source_name"] == "Community Tool Export"
assert "path" not in payload
assert "candidates" in payload

forbidden_keys = {
    "path",
    "url",
    "title",
    "summary",
    "raw_text",
    "normalized_key",
    "normalized_phrase",
    "candidate_context",
    "candidate_contexts",
    "representative_item",
    "representative_items",
}
forbidden_values = {
    str(tmp_smoke),
    str(tmp_smoke / "community-signals.csv"),
    str(tmp_smoke / "bad-community-signals.csv"),
    "https://example.com/a",
    "Le Teckel bag spotted",
    "Local sanitized note",
    "https://private.example/secret",
    "Private Runway Note",
    "Private summary text",
    "not-a-date",
    "private-weight",
}

def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            assert key not in forbidden_keys, key
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)
    elif isinstance(value, str):
        for forbidden in forbidden_values:
            assert forbidden not in value, value

walk(payload)
error_text = (tmp_smoke / "bad.stdout").read_text(encoding="utf-8") + (tmp_smoke / "bad.stderr").read_text(encoding="utf-8")
assert "input file could not be read or validated" in error_text
for forbidden in forbidden_values:
    assert forbidden not in error_text, error_text
actual_paths = {str(path.relative_to(tmp_smoke)) for path in tmp_smoke.rglob("*")}
expected_paths = {
    "config",
    "config/scoring.yaml",
    "community-signals.csv",
    "bad-community-signals.csv",
    "community-candidates-smoke.json",
    "bad.stdout",
    "bad.stderr",
}
assert actual_paths == expected_paths, actual_paths
PY
```

Expected: every command exits `0`.

## Task 5: Secret, Artifact, And Staging Boundary Scans

**Files:**
- No file edits.

- [ ] **Step 1: Scan tracked and pending files for obvious secrets**

Run before final review files are created:

```bash
.venv/bin/python - <<'PY'
import re
import subprocess
from pathlib import Path

pattern = re.compile(
    r"gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|"
    r"sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"
)
tracked = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.splitlines()
untracked = subprocess.run(
    ["git", "ls-files", "--others", "--exclude-standard"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
findings = []
for file_name in tracked + untracked:
    path = Path(file_name)
    if path.name == "uv.lock":
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        continue
    for line_number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            findings.append(f"{path}:{line_number}: secret-like pattern")
if findings:
    raise SystemExit("Secret scan findings:\n" + "\n".join(findings))
PY
```

Expected: no output, exit `0`. If the command finds a match, stop and inspect
before staging. The scan reports only file and line locations, not matched
secret-like values.

- [ ] **Step 2: Verify generated artifacts are not tracked**

Run:

```bash
if git ls-files | rg '(^|/)(\.venv|\.pytest_cache|\.ruff_cache|build|dist|reports|\.codegraph)(/|$)|\.(sqlite|sqlite-wal|sqlite-shm|db|db-wal|db-shm)$' | rg -v '^(\.codegraph/\.gitignore|reports/README\.md)$'; then exit 1; fi
if git ls-files --others --exclude-standard | rg '(^|/)(\.venv|\.pytest_cache|\.ruff_cache|build|dist|reports|\.codegraph)(/|$)|\.(sqlite|sqlite-wal|sqlite-shm|db|db-wal|db-shm)$' | rg -v '^(\.codegraph/\.gitignore|reports/README\.md)$'; then exit 1; fi
```

Expected: no output, exit `0`. The only tracked paths allowed under these
otherwise generated-artifact directories are `.codegraph/.gitignore` and
`reports/README.md`.

- [ ] **Step 3: Verify `uv.lock` is not staged**

Run:

```bash
if git diff --cached --name-only | rg '^uv\.lock$'; then exit 1; fi
```

Expected: no output, exit `0`.

## Task 6: Final Claude Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-27c-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-27c-release-review.md`

- [ ] **Step 1: Create final review prompt**

The prompt must ask Claude Code to review all Stage 27 code/docs changes, the
verification evidence, Stage 27B boundary language, output-exclusion
documentation and installed-wheel behavior, the staging boundary, and the
`uv.lock` exclusion before commit/push.

- [ ] **Step 2: Run Claude Code final review**

Run:

```bash
set -euo pipefail
tmp_release_review="$(mktemp)"
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-27c-release-review-prompt.md | tee "$tmp_release_review"
test -s "$tmp_release_review"
rg -n "^APPROVED FOR STAGE 27 RELEASE COMMIT AND PUSH$" "$tmp_release_review" >/dev/null
mv "$tmp_release_review" docs/reviews/claude-code-stage-27c-release-review.md
```

Expected: command exits `0`, review file is non-empty, and the required
approval phrase is present:

```text
APPROVED FOR STAGE 27 RELEASE COMMIT AND PUSH
```

If Claude Code reports any Critical or Important finding, stop, fix it, rerun relevant verification, and rerun this final review before staging.

## Task 7: Post-Review Scans Before Staging

**Files:**
- No file edits.

- [ ] **Step 1: Re-run secret scan including final review files**

Run:

```bash
.venv/bin/python - <<'PY'
import re
import subprocess
from pathlib import Path

pattern = re.compile(
    r"gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|"
    r"sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"
)
tracked = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.splitlines()
untracked = subprocess.run(
    ["git", "ls-files", "--others", "--exclude-standard"],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
findings = []
for file_name in tracked + untracked:
    path = Path(file_name)
    if path.name == "uv.lock":
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        continue
    for line_number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            findings.append(f"{path}:{line_number}: secret-like pattern")
if findings:
    raise SystemExit("Secret scan findings:\n" + "\n".join(findings))
PY
```

Expected: no output, exit `0`. This scan runs after
`docs/reviews/claude-code-stage-27c-release-review-prompt.md` and
`docs/reviews/claude-code-stage-27c-release-review.md` exist, so those files are
covered before staging without printing any matched secret-like values.

- [ ] **Step 2: Re-run tracked and untracked artifact scans**

Run:

```bash
if git ls-files | rg '(^|/)(\.venv|\.pytest_cache|\.ruff_cache|build|dist|reports|\.codegraph)(/|$)|\.(sqlite|sqlite-wal|sqlite-shm|db|db-wal|db-shm)$' | rg -v '^(\.codegraph/\.gitignore|reports/README\.md)$'; then exit 1; fi
if git ls-files --others --exclude-standard | rg '(^|/)(\.venv|\.pytest_cache|\.ruff_cache|build|dist|reports|\.codegraph)(/|$)|\.(sqlite|sqlite-wal|sqlite-shm|db|db-wal|db-shm)$' | rg -v '^(\.codegraph/\.gitignore|reports/README\.md)$'; then exit 1; fi
```

Expected: no output, exit `0`. The only tracked paths allowed under these
otherwise generated-artifact directories are `.codegraph/.gitignore` and
`reports/README.md`.

- [ ] **Step 3: Re-check output-exclusion docs after final review files exist**

Run:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

checks = {
    "README.md": [
        ["supplied input file path"],
        ["row URLs"],
        ["row titles"],
        ["summaries"],
        ["raw text"],
        ["normalized keys"],
        ["candidate contexts"],
        ["representative item details"],
    ],
    "docs/community-signal-import.md": [
        ["supplied input file path"],
        ["row URLs"],
        ["row titles"],
        ["summaries"],
        ["raw text"],
        ["normalized keys"],
        ["candidate contexts"],
        ["representative item details"],
    ],
    "docs/community-signal-quality.md": [
        ["supplied input file path"],
        ["row URLs"],
        ["row titles"],
        ["summaries"],
        ["raw text"],
        ["normalized keys"],
        ["candidate contexts"],
        ["representative item details"],
    ],
    "docs/source-boundaries.md": [
        ["supplied file path"],
        ["row URLs"],
        ["row titles"],
        ["summaries"],
        ["raw text"],
        ["normalized keys"],
        ["candidate contexts"],
        ["representative item details"],
    ],
    "docs/github-upload-checklist.md": [
        ["input file path"],
        ["row URL", "row URLs"],
        ["row title", "row titles"],
        ["summary", "summaries"],
        ["raw text"],
        ["normalized key", "normalized keys"],
        ["candidate context", "candidate contexts"],
        ["representative item detail", "representative item details"],
    ],
}

missing = []
for file_name, phrase_groups in checks.items():
    text = " ".join(Path(file_name).read_text(encoding="utf-8").split())
    for alternatives in phrase_groups:
        if not any(phrase in text for phrase in alternatives):
            missing.append(f"{file_name}: {' / '.join(alternatives)}")

if missing:
    raise SystemExit("Missing output-exclusion documentation:\n" + "\n".join(missing))
PY
```

Expected: no output, exit `0`.

## Task 8: Explicit Staging, Commit, And Push

**Files:**
- Stage only approved Stage 27 files.

- [ ] **Step 1: Stage an explicit allowlist**

Run:

```bash
git add \
  src/fashion_radar/community_candidates.py \
  src/fashion_radar/cli.py \
  tests/test_community_candidates.py \
  tests/test_cli.py \
  README.md \
  CHANGELOG.md \
  docs/community-signal-import.md \
  docs/community-signal-quality.md \
  docs/candidate-discovery.md \
  docs/architecture.md \
  docs/source-boundaries.md \
  docs/github-upload-checklist.md \
  docs/superpowers/specs/2026-06-13-stage-27*.md \
  docs/superpowers/plans/2026-06-13-stage-27*.md \
  docs/reviews/claude-code-stage-27*.md
```

Expected: command exits `0`.

- [ ] **Step 2: Verify staged allowlist and `uv.lock` exclusion**

Run:

```bash
if git diff --cached --name-only | rg -v '^(README\.md|CHANGELOG\.md|docs/community-signal-import\.md|docs/community-signal-quality\.md|docs/candidate-discovery\.md|docs/architecture\.md|docs/source-boundaries\.md|docs/github-upload-checklist\.md|docs/superpowers/specs/2026-06-13-stage-27.*\.md|docs/superpowers/plans/2026-06-13-stage-27.*\.md|docs/reviews/claude-code-stage-27.*\.md|src/fashion_radar/community_candidates\.py|src/fashion_radar/cli\.py|tests/test_community_candidates\.py|tests/test_cli\.py)$'; then exit 1; fi
if git diff --cached --name-only | rg '^uv\.lock$'; then exit 1; fi
git diff --cached --check
```

Expected: no output from the first two checks; every command exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "Add community candidate preview"
```

Expected: commit exits `0`.

- [ ] **Step 4: Push with non-persistent token use**

Run a single push command that injects the user-provided GitHub token through a temporary environment variable and Git extra header. Do not write the token to git remote URLs, git config, files, or docs.

Use this concrete pattern, replacing `<TOKEN_FROM_USER>` only in the in-memory
environment assignment. Run it in the non-interactive execution environment for
this release step, not through persistent git config or a token-bearing remote.
The subshell keeps the token scoped to the push and unsets it on exit:

```bash
(
  set +x
  GITHUB_TOKEN='<TOKEN_FROM_USER>'
  trap 'unset GITHUB_TOKEN' EXIT
  git -c "http.https://github.com/.extraheader=AUTHORIZATION: bearer ${GITHUB_TOKEN}" push origin HEAD:main
)
```

Do not run `git remote set-url` with the token. Do not run `git config --global`
or persistent `git config http.*.extraheader`.

Expected: push exits `0`.

- [ ] **Step 5: Verify post-push state**

Run:

```bash
git status --short --branch
head_sha="$(git rev-parse HEAD)"
origin_sha="$(git rev-parse origin/main)"
test "$head_sha" = "$origin_sha"
test "$(git remote get-url origin)" = "https://github.com/Lordakee/fashion-radar.git"
if git config --show-origin --get-regexp 'http\..*extraheader' >/dev/null; then exit 1; fi
.venv/bin/python - <<'PY'
import re
import subprocess
import sys

pattern = re.compile(r"gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|x-access-token|AUTHORIZATION", re.IGNORECASE)
config = subprocess.run(
    ["git", "config", "--show-origin", "--list"],
    check=False,
    capture_output=True,
    text=True,
).stdout
for line in config.splitlines():
    if pattern.search(line):
        raise SystemExit("Token-like value found in git config")
PY
if git remote get-url origin | rg -q 'ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|x-access-token|AUTHORIZATION|extraheader'; then exit 1; fi
if git diff --cached --name-only | rg '^uv\.lock$'; then exit 1; fi
if git ls-tree -r --name-only HEAD | rg '(^|/)(\.venv|\.pytest_cache|\.ruff_cache|build|dist|reports|\.codegraph)(/|$)|\.(sqlite|sqlite-wal|sqlite-shm|db|db-wal|db-shm)$' | rg -v '^(\.codegraph/\.gitignore|reports/README\.md)$'; then exit 1; fi
if git grep -l -E "gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY" HEAD -- . ':!uv.lock'; then exit 1; fi
```

Expected:

- `HEAD` equals `origin/main`;
- remote URL is token-free;
- no persisted GitHub `extraheader`, token-bearing URL, or token-bearing remote
  appears in git config;
- `uv.lock` is not staged;
- generated artifact scans return no matches;
- secret scans return no matches;
- any remaining uncommitted diff is only the known pre-existing `uv.lock` local diff.
