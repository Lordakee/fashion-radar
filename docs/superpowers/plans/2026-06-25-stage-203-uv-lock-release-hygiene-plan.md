# Stage 203 UV Lock Release Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make release hygiene automatically reject mirror-bound or private-index material in the public root `uv.lock`, while preserving frozen local mirror installs.

**Architecture:** Add a targeted root-lockfile scanner to `scripts/check_release_hygiene.py` and call it from `collect_findings()` for tracked and untracked files. The scanner only inspects normalized path `uv.lock`, redacts offending URLs, allows the public PyPI registry and `files.pythonhosted.org` artifacts, and leaves docs, user-level uv config, environment variables, and mirror-backed frozen installs out of scope.

**Tech Stack:** Python standard library (`re`, `urllib.parse`, `pathlib`), existing subprocess-based pytest fixtures, `uv --no-config run --frozen pytest`, `ruff`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage fixes a release-hygiene gap documented in `docs/dependency-mirrors.md` and `docs/github-upload-checklist.md`: mirror installs are encouraged locally, but the public `uv.lock` must not carry mirror or private index URLs. Existing release hygiene checks paths, secrets, review capture artifacts, git remotes, and git `extraheader` values, but does not enforce that lockfile boundary.

In scope:

- Add release hygiene findings for mirror/private registry and artifact URLs in root `uv.lock`.
- Add release hygiene findings for lockfile-local index markers such as `index-url`, `extra-index-url`, and `find-links`.
- Redact offending URLs in all new findings.
- Keep normal PyPI lockfile content passing.
- Update mirror and upload docs to say the release hygiene gate now enforces the public lockfile boundary.
- Add changelog entry and Stage 203 review artifacts.

Out of scope:

- No dependency changes.
- No `uv.lock` or `pyproject.toml` regeneration.
- No runtime product behavior, collectors, source packs, entity packs, dashboard, database schema, scoring, reports, scraping, social/platform connectors, source acquisition, demand proof, platform coverage verification, or compliance-review product features.
- No repo-wide scan for the word `mirror`; only root `uv.lock` is inspected.
- No rejection of environment-based mirror use such as `UV_DEFAULT_INDEX=... uv sync --frozen --dev`.

## File Map

- Modify `scripts/check_release_hygiene.py`
  - Add URL extraction and allowlist helpers.
  - Add `find_uv_lock_hygiene_findings(repo_root, paths, path_status)`.
  - Wire the helper into `collect_findings()` for tracked and untracked files.
- Modify `tests/test_release_hygiene.py`
  - Add RED subprocess tests for tracked/untracked `uv.lock` mirror/private index findings.
  - Add pass test for public PyPI registry and `files.pythonhosted.org` artifacts.
  - Add current-repo unit test proving committed `uv.lock` has no findings.
- Modify `docs/dependency-mirrors.md`
  - Clarify that release hygiene enforces the public lockfile check, while direct `rg` remains a local diagnostic.
- Modify `docs/github-upload-checklist.md`
  - Add `scripts/check_release_hygiene.py` to the pre-upload command list and mention that it includes `uv.lock` mirror/private index checks.
- Modify `CHANGELOG.md`
  - Add Stage 203 under `### Fixed`.
- Add `docs/reviews/opencode-stage-203-plan-review-prompt.md`
  - Ask OpenCode to review this plan before implementation.
- Add `docs/reviews/opencode-stage-203-plan-review.md`
  - Store cleaned OpenCode plan review.
- Add later review artifacts:
  - `docs/reviews/opencode-stage-203-code-review-prompt.md`
  - `docs/reviews/opencode-stage-203-code-review.md`
  - `docs/reviews/opencode-stage-203-release-review-prompt.md`
  - `docs/reviews/opencode-stage-203-release-review.md`

## Detection Contract

Root `uv.lock` is clean when:

```toml
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/demo/demo-1.0.0.tar.gz", hash = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", size = 1 }
wheels = [
    { url = "https://files.pythonhosted.org/packages/demo/demo-1.0.0-py3-none-any.whl", hash = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", size = 1 },
]
```

Root `uv.lock` is rejected when it contains:

```toml
source = { registry = "https://pypi.tuna.tsinghua.edu.cn/simple" }
```

```toml
source = { registry = "https://packages.example.internal/simple" }
```

```toml
sdist = { url = "https://mirrors.aliyun.com/pypi/packages/demo.tar.gz", hash = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", size = 1 }
```

```toml
index-url = "https://packages.example.internal/simple"
extra-index-url = "https://packages.example.internal/simple"
find-links = ["https://packages.example.internal/simple"]
```

Finding format:

```text
forbidden mirror/private index in tracked file: uv.lock:6: registry URL: <redacted>
forbidden mirror/private index in untracked file: uv.lock:6: artifact URL: <redacted>
forbidden mirror/private index in tracked file: uv.lock:2: index-url: <redacted>
```

## Tasks

### Task 1: Write RED Tests For Lockfile Hygiene

**Files:**

- Modify: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add fixture constants**

Add these constants near the existing test constants:

```python
PUBLIC_UV_LOCK = """version = 1

[[package]]
name = "demo"
version = "1.0.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/demo/demo-1.0.0.tar.gz", hash = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", size = 1 }
wheels = [
    { url = "https://files.pythonhosted.org/packages/demo/demo-1.0.0-py3-none-any.whl", hash = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", size = 1 },
]
"""
```

- [ ] **Step 2: Add failing tracked mirror registry test**

Add:

```python
def test_tracked_uv_lock_with_mirror_registry_url_fails_redacted(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    mirror_url = "https://pypi.tuna.tsinghua.edu.cn/simple"
    write_tracked(
        repo_root,
        "uv.lock",
        (
            "version = 1\n\n"
            "[[package]]\n"
            'name = "demo"\n'
            'version = "1.0.0"\n'
            f'source = {{ registry = "{mirror_url}" }}\n'
        ),
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden mirror/private index in tracked file: "
        "uv.lock:6: registry URL: <redacted>"
    ) in result.stderr
    assert mirror_url not in result.stderr
```

- [ ] **Step 3: Add failing untracked mirror artifact test**

Add:

```python
def test_untracked_uv_lock_with_mirror_artifact_url_fails_redacted(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    mirror_url = "https://mirrors.aliyun.com/pypi/packages/demo.tar.gz"
    write_file(
        repo_root,
        "uv.lock",
        (
            "version = 1\n\n"
            "[[package]]\n"
            'name = "demo"\n'
            'version = "1.0.0"\n'
            'source = { registry = "https://pypi.org/simple" }\n'
            f'sdist = {{ url = "{mirror_url}", hash = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", size = 1 }}\n'
        ),
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden mirror/private index in untracked file: "
        "uv.lock:7: artifact URL: <redacted>"
    ) in result.stderr
    assert mirror_url not in result.stderr
```

- [ ] **Step 4: Add failing private registry test**

Add:

```python
def test_tracked_uv_lock_with_private_registry_url_fails_redacted(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    private_url = "https://packages.example.internal/simple"
    write_tracked(
        repo_root,
        "uv.lock",
        (
            "version = 1\n\n"
            "[[package]]\n"
            'name = "demo"\n'
            'version = "1.0.0"\n'
            f'source = {{ registry = "{private_url}" }}\n'
        ),
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden mirror/private index in tracked file: "
        "uv.lock:6: registry URL: <redacted>"
    ) in result.stderr
    assert private_url not in result.stderr
```

- [ ] **Step 5: Add failing index marker test**

Add:

```python
@pytest.mark.parametrize(
    ("line", "marker"),
    [
        ('index-url = "https://packages.example.internal/simple"', "index-url"),
        ('extra-index-url = "https://packages.example.internal/simple"', "extra-index-url"),
        ('find-links = ["https://packages.example.internal/simple"]', "find-links"),
    ],
)
def test_tracked_uv_lock_with_index_config_marker_fails_redacted(
    tmp_path: Path,
    line: str,
    marker: str,
) -> None:
    repo_root = init_repo(tmp_path)
    private_url = "https://packages.example.internal/simple"
    write_tracked(repo_root, "uv.lock", f"version = 1\n{line}\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden mirror/private index in tracked file: "
        f"uv.lock:2: {marker}: <redacted>"
    ) in result.stderr
    assert private_url not in result.stderr
```

- [ ] **Step 6: Add passing public lockfile test**

Add:

```python
def test_tracked_uv_lock_with_public_pypi_registry_and_pythonhosted_artifacts_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, "uv.lock", PUBLIC_UV_LOCK)

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 7: Add current-repo unit test**

Add near the current repository tests:

```python
def test_current_repository_tracked_uv_lock_has_no_mirror_private_index_findings() -> None:
    checker = load_checker_module()

    assert checker.find_uv_lock_hygiene_findings(REPO_ROOT, ["uv.lock"], "tracked") == []
```

- [ ] **Step 8: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "uv_lock"
```

Expected: the new failing tests fail because `find_uv_lock_hygiene_findings` does not exist and `collect_findings()` does not yet scan `uv.lock`.

### Task 2: Implement Targeted `uv.lock` Hygiene Scanner

**Files:**

- Modify: `scripts/check_release_hygiene.py`
- Test: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add URL parsing import**

Change:

```python
from pathlib import Path, PurePosixPath
```

to:

```python
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
```

- [ ] **Step 2: Add lockfile constants**

Add near the existing regex constants:

```python
UV_LOCK_PATH = "uv.lock"
PUBLIC_PYPI_REGISTRY_URL = "https://pypi.org/simple"
PUBLIC_PYPI_ARTIFACT_HOST = "files.pythonhosted.org"
UV_LOCK_REGISTRY_URL_PATTERN = re.compile(
    r'\bregistry\s*=\s*"(?P<url>https?://[^"]+)"',
    re.IGNORECASE,
)
UV_LOCK_ARTIFACT_URL_PATTERN = re.compile(
    r'\burl\s*=\s*"(?P<url>https?://[^"]+)"',
    re.IGNORECASE,
)
UV_LOCK_INDEX_MARKER_PATTERN = re.compile(
    r"\b(?P<marker>index-url|extra-index-url|find-links|default-index|extra-index)\b",
    re.IGNORECASE,
)
```

Keep the marker alternatives ordered from longest to shortest when changing
this pattern. That preserves `extra-index-url` as the reported marker instead
of shortening it to `extra-index`.

- [ ] **Step 3: Wire helper into `collect_findings()`**

Change:

```python
findings.extend(find_forbidden_path_findings(tracked_paths, "tracked"))
findings.extend(find_forbidden_path_findings(untracked_paths, "untracked"))
findings.extend(find_secret_findings(repo_root, tracked_paths, "tracked"))
findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
```

to:

```python
findings.extend(find_forbidden_path_findings(tracked_paths, "tracked"))
findings.extend(find_forbidden_path_findings(untracked_paths, "untracked"))
findings.extend(find_uv_lock_hygiene_findings(repo_root, tracked_paths, "tracked"))
findings.extend(find_uv_lock_hygiene_findings(repo_root, untracked_paths, "untracked"))
findings.extend(find_secret_findings(repo_root, tracked_paths, "tracked"))
findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
```

- [ ] **Step 4: Add scanner helpers**

Add after `is_database_or_sidecar()`:

```python
def find_uv_lock_hygiene_findings(
    repo_root: Path,
    paths: list[str],
    path_status: str,
) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if normalized != UV_LOCK_PATH:
            continue

        file_path = safe_repo_path(repo_root, normalized)
        if file_path is None or file_path.is_symlink() or not file_path.is_file():
            continue

        text = read_text_if_not_binary(file_path)
        if text is None:
            continue

        findings.extend(uv_lock_text_findings(normalized, text, path_status))
    return findings


def uv_lock_text_findings(path: str, text: str, path_status: str) -> list[str]:
    findings = []
    prefix = f"forbidden mirror/private index in {path_status} file: {path}"

    for match in UV_LOCK_INDEX_MARKER_PATTERN.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        marker = match.group("marker")
        findings.append(f"{prefix}:{line_number}: {marker}: <redacted>")

    for match in UV_LOCK_REGISTRY_URL_PATTERN.finditer(text):
        url = match.group("url")
        if not is_public_pypi_registry_url(url):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{prefix}:{line_number}: registry URL: <redacted>")

    for match in UV_LOCK_ARTIFACT_URL_PATTERN.finditer(text):
        url = match.group("url")
        if not is_public_pypi_artifact_url(url):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{prefix}:{line_number}: artifact URL: <redacted>")

    return findings


def is_public_pypi_registry_url(url: str) -> bool:
    return url.rstrip("/") == PUBLIC_PYPI_REGISTRY_URL


def is_public_pypi_artifact_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == PUBLIC_PYPI_ARTIFACT_HOST
```

- [ ] **Step 5: Run GREEN focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "uv_lock"
```

Expected: all new `uv_lock` tests pass.

- [ ] **Step 6: Run full release hygiene test file**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
```

Expected: all release hygiene tests pass.

### Task 3: Update Docs And Changelog

**Files:**

- Modify: `docs/dependency-mirrors.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update dependency mirror docs**

In `docs/dependency-mirrors.md`, keep frozen mirror install commands and `UV_NO_CONFIG=1` guidance, then change the pre-upload lockfile bullet to say:

```markdown
- Before GitHub upload, run release hygiene; it now enforces that the public
  root `uv.lock` does not contain mirror/private registry URLs, non-PyPI
  artifact URLs, or lockfile-local package index markers. The direct `rg`
  command below remains a quick diagnostic when recovering a mirror-rewritten
  lockfile:
```

Leave the recovery and regeneration `rg` diagnostic blocks in the same document
unchanged; those are still useful when fixing a mirror-rewritten lockfile.

- [ ] **Step 2: Update GitHub upload checklist**

Add this command to the pre-upload command list after `git diff --check`:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Then replace the standalone “Check the public lockfile has no mirror URLs” sentence with:

```markdown
The release hygiene command above rejects mirror/private index material in root
`uv.lock`. For direct diagnosis, the public lockfile should also have no matches
for:
```

- [ ] **Step 3: Update changelog**

Add under `## [Unreleased]` / `### Fixed`:

```markdown
- Stage 203 makes release hygiene reject mirror/private index material in the
  public root `uv.lock`, while keeping frozen local mirror installs allowed and
  avoiding dependency, source, connector, scraper, platform coverage, demand
  proof, or compliance-review behavior changes.
```

### Task 4: Review And Release Verification

**Files:**

- Add: `docs/reviews/opencode-stage-203-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-203-code-review.md`
- Add: `docs/reviews/opencode-stage-203-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-203-release-review.md`

- [ ] **Step 1: Run focused formatting and lint**

Run:

```bash
uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py
```

- [ ] **Step 2: Run release hygiene and lockfile boundary checks**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: release hygiene exits `0`; lock check exits `0`; `rg` returns no matches; dependency files unchanged; whitespace check clean.

- [ ] **Step 3: Prove frozen mirror install remains allowed**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: frozen mirror sync check exits `0` without modifying `uv.lock`; release hygiene exits `0`.

- [ ] **Step 4: Run full test and style gate**

Run:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

- [ ] **Step 5: Run OpenCode code review**

Create `docs/reviews/opencode-stage-203-code-review-prompt.md` asking OpenCode to review changed files for:

- correctness of `uv.lock` URL allowlist behavior
- redaction
- no repo-wide mirror false positives
- preservation of frozen mirror installs
- docs/changelog accuracy
- no dependency/source/social/platform/compliance scope expansion

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-203-code-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-203-code-review.md
rm -f "$tmp_review"
```

Fix any Critical or Important findings, then rerun relevant tests and rereview.

- [ ] **Step 6: Run OpenCode release review**

Create `docs/reviews/opencode-stage-203-release-review-prompt.md` asking OpenCode to review final release readiness, verification evidence, release hygiene output, dependency lockfile boundary, and git status.

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-203-release-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-203-release-review.md
rm -f "$tmp_review"
```

Fix any Critical or Important findings, then rerun relevant tests and rereview.

- [ ] **Step 7: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_release_hygiene.py tests/test_release_hygiene.py docs/dependency-mirrors.md docs/github-upload-checklist.md CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-203-uv-lock-release-hygiene-plan.md docs/reviews/opencode-stage-203-*.md
git commit -m "Stage 203: guard uv lock release hygiene"
git push origin main
git status --short --branch --untracked-files=all
```

## Self-Review

- Spec coverage: The plan covers the known gap between documented mirror policy and automated release hygiene enforcement. It also preserves the user's preference to use mirrors locally while keeping public GitHub artifacts clean.
- Placeholder scan: No `TBD`, `TODO`, “implement later”, or unspecified tests remain.
- Scope check: The stage is intentionally release hygiene only. Future source-pack composition, watchlist quality, and dashboard transparency work should be separate nodes.
