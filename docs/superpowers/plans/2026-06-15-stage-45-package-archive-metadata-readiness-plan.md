# Stage 45 Package Archive And Metadata Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make package metadata, wheel/sdist archive contents, CI package smoke,
and the GitHub upload checklist agree on the release-critical package surface.

**Architecture:** This is a package-readiness and docs-test node. A small
dependency-free archive inspection script centralizes wheel/sdist content
expectations, CI and the upload checklist invoke that script, and pytest guards
metadata plus drift between docs and CI. Runtime collection and scoring behavior
remain unchanged.

**Tech Stack:** Python 3.11 standard library (`zipfile`, `tarfile`, `tomllib`,
`subprocess`), pytest, `uv build`, hatchling, GitHub Actions YAML, Markdown,
Ruff, local Claude Code CLI with `--effort max`.

---

## Boundaries

In scope:

- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`
- Modify: `README.md`
- Modify: `tests/test_cli_docs.py`
- Create: `scripts/check_package_archives.py`
- Create: `tests/test_package_metadata.py`
- Create: `tests/test_package_archives.py`
- Add: `docs/reviews/claude-code-stage-45-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-45-plan-review.md`
- Add if needed: `docs/reviews/claude-code-stage-45-plan-rereview*.md`
- Add: `docs/reviews/claude-code-stage-45-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-45-release-review.md`
- Maintain/update: this Stage 45 spec and plan.

Out of scope:

- PyPI publishing, GitHub release creation, artifact upload, or remote
  configuration changes.
- Dependency additions, dependency upgrades, lockfile changes, package version
  bumps, runtime CLI behavior changes, database schema changes, dashboard
  changes, or generated report/data changes.
- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.
- Compliance-review functionality inside the tool.
- Rewriting historical release-gate or review records.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Create: `docs/reviews/claude-code-stage-45-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-45-plan-review.md`

- [ ] **Step 1: Confirm the prompt exists**

The prompt file should contain the Stage 45 objective, technical approach,
files to review, boundaries, and approval phrase:

```text
APPROVED FOR STAGE 45 PACKAGE ARCHIVE METADATA READINESS
```

- [ ] **Step 2: Request Claude Code plan review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-45-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-45-plan-review.md
```

Expected: the review has no Critical or Important blockers and includes
`APPROVED FOR STAGE 45 PACKAGE ARCHIVE METADATA READINESS`. Fix blockers before
Task 0. If fixes are needed, store follow-up prompt/results as
`docs/reviews/claude-code-stage-45-plan-rereview*.md`.

## Task 0: Pre-flight Cleanliness Check

**Files:**

- Git only.

- [ ] **Step 1: Confirm only Stage 45 planning files are dirty**

Run:

```bash
git status --short --branch
```

Expected before implementation: modified or untracked files are limited to the
Stage 45 spec, plan, and Claude Code Stage 45 plan review prompt/result files.
If unrelated files appear, stop and investigate before editing.

## Task 1: Add Package Metadata Guard And Public Metadata

**Files:**

- Create: `tests/test_package_metadata.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing package metadata tests**

Create `tests/test_package_metadata.py`:

```python
from __future__ import annotations

import tomllib
from pathlib import Path

import fashion_radar

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
LICENSE = ROOT / "LICENSE"


def _project_metadata() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]


def test_package_core_metadata_matches_runtime_version() -> None:
    project = _project_metadata()

    assert project["name"] == "fashion-radar"
    assert project["version"] == fashion_radar.__version__
    assert project["readme"] == "README.md"
    assert project["requires-python"] == ">=3.11"
    assert project["license"] == {"text": "MIT"}
    assert README.exists()
    assert LICENSE.exists()


def test_package_script_and_wheel_package_are_declared() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert data["project"]["scripts"]["fashion-radar"] == "fashion_radar.cli:app"
    assert data["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == [
        "src/fashion_radar"
    ]


def test_public_package_metadata_is_complete() -> None:
    project = _project_metadata()

    assert {
        "fashion",
        "trend-analysis",
        "local-first",
        "rss",
        "gdelt",
        "community-signals",
    }.issubset(set(project["keywords"]))
    assert {
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Indexing",
    }.issubset(set(project["classifiers"]))
    assert project["urls"] == {
        "Homepage": "https://github.com/Lordakee/fashion-radar",
        "Repository": "https://github.com/Lordakee/fashion-radar",
        "Documentation": "https://github.com/Lordakee/fashion-radar/tree/main/docs",
        "Issues": "https://github.com/Lordakee/fashion-radar/issues",
        "Changelog": "https://github.com/Lordakee/fashion-radar/blob/main/CHANGELOG.md",
        "Security": "https://github.com/Lordakee/fashion-radar/blob/main/SECURITY.md",
    }
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py -q
```

Expected before `pyproject.toml` edits: FAIL because `keywords`,
`classifiers`, and `urls` are missing.

- [ ] **Step 3: Add public metadata to `pyproject.toml`**

Add these fields inside `[project]`, after `authors`:

```toml
keywords = [
  "community-signals",
  "fashion",
  "gdelt",
  "local-first",
  "rss",
  "trend-analysis",
]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Intended Audience :: End Users/Desktop",
  "License :: OSI Approved :: MIT License",
  "Natural Language :: English",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
  "Topic :: Office/Business :: News/Diary",
  "Topic :: Text Processing :: Indexing",
]
```

Add this table before `[project.optional-dependencies]`:

```toml
[project.urls]
Homepage = "https://github.com/Lordakee/fashion-radar"
Repository = "https://github.com/Lordakee/fashion-radar"
Documentation = "https://github.com/Lordakee/fashion-radar/tree/main/docs"
Issues = "https://github.com/Lordakee/fashion-radar/issues"
Changelog = "https://github.com/Lordakee/fashion-radar/blob/main/CHANGELOG.md"
Security = "https://github.com/Lordakee/fashion-radar/blob/main/SECURITY.md"
```

Do not edit dependencies or `uv.lock`.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py -q
```

Expected: PASS.

## Task 2: Add Archive Inspection Script With Tests

**Files:**

- Create: `scripts/check_package_archives.py`
- Create: `tests/test_package_archives.py`

- [ ] **Step 1: Write failing archive script tests**

Create `tests/test_package_archives.py`:

```python
from __future__ import annotations

import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_package_archives.py"

WHEEL_REQUIRED = [
    "fashion_radar/cli.py",
    "fashion_radar/__main__.py",
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
    "fashion_radar-0.1.0.dist-info/METADATA",
    "fashion_radar-0.1.0.dist-info/WHEEL",
    "fashion_radar-0.1.0.dist-info/entry_points.txt",
    "fashion_radar-0.1.0.dist-info/licenses/LICENSE",
]

SDIST_REQUIRED = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "docs/cli-reference.md",
    "docs/github-upload-checklist.md",
    "docs/source-boundaries.md",
    "docs/dependency-mirrors.md",
    "docs/community-signal-import.md",
    "docs/source-packs.md",
    "docs/entity-packs.md",
    "configs/sources.example.yaml",
    "configs/entities.example.yaml",
    "configs/scoring.example.yaml",
    "configs/source-packs/fashion-public.example.yaml",
    "configs/entity-packs/fashion-watchlist.example.yaml",
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "schemas/community-signals.schema.json",
    "src/fashion_radar/cli.py",
    "src/fashion_radar/__main__.py",
    "src/fashion_radar/templates/daily_report.md",
    "src/fashion_radar/templates/configs/sources.example.yaml",
    "src/fashion_radar/templates/configs/entities.example.yaml",
    "src/fashion_radar/templates/configs/scoring.example.yaml",
]


def _write_fixture_archives(
    build_dir: Path,
    *,
    wheel_paths: list[str] | None = None,
    sdist_paths: list[str] | None = None,
) -> None:
    with zipfile.ZipFile(build_dir / "fashion_radar-0.1.0-py3-none-any.whl", "w") as wheel:
        for name in wheel_paths or WHEEL_REQUIRED:
            wheel.writestr(name, "fixture")

    with tarfile.open(build_dir / "fashion_radar-0.1.0.tar.gz", "w:gz") as sdist:
        for name in sdist_paths or SDIST_REQUIRED:
            file_path = build_dir / name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("fixture", encoding="utf-8")
            sdist.add(file_path, arcname=f"fashion_radar-0.1.0/{name}")


def _run_script(build_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(build_dir)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_check_package_archives_accepts_required_wheel_and_sdist_files(
    tmp_path: Path,
) -> None:
    _write_fixture_archives(tmp_path)

    result = _run_script(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Package archives contain required files" in result.stdout


def test_check_package_archives_reports_missing_wheel_file(tmp_path: Path) -> None:
    _write_fixture_archives(
        tmp_path,
        wheel_paths=[path for path in WHEEL_REQUIRED if path != "fashion_radar/__main__.py"],
    )

    result = _run_script(tmp_path)

    assert result.returncode == 1
    assert "Missing wheel files" in result.stderr
    assert "fashion_radar/__main__.py" in result.stderr


def test_check_package_archives_reports_missing_sdist_file(tmp_path: Path) -> None:
    _write_fixture_archives(
        tmp_path,
        sdist_paths=[path for path in SDIST_REQUIRED if path != "docs/source-boundaries.md"],
    )

    result = _run_script(tmp_path)

    assert result.returncode == 1
    assert "Missing sdist files" in result.stderr
    assert "docs/source-boundaries.md" in result.stderr
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Expected before creating the script: FAIL because
`scripts/check_package_archives.py` does not exist.

- [ ] **Step 3: Implement `scripts/check_package_archives.py`**

Create `scripts/check_package_archives.py`:

```python
from __future__ import annotations

import argparse
import fnmatch
import tarfile
import zipfile
from pathlib import Path

REQUIRED_WHEEL_PATHS = (
    "fashion_radar/cli.py",
    "fashion_radar/__main__.py",
    "fashion_radar/templates/daily_report.md",
    "fashion_radar/templates/configs/sources.example.yaml",
    "fashion_radar/templates/configs/entities.example.yaml",
    "fashion_radar/templates/configs/scoring.example.yaml",
)

REQUIRED_WHEEL_PATTERNS = (
    "*.dist-info/METADATA",
    "*.dist-info/WHEEL",
    "*.dist-info/entry_points.txt",
    "*.dist-info/licenses/LICENSE",
)

REQUIRED_SDIST_PATHS = (
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "docs/cli-reference.md",
    "docs/github-upload-checklist.md",
    "docs/source-boundaries.md",
    "docs/dependency-mirrors.md",
    "docs/community-signal-import.md",
    "docs/source-packs.md",
    "docs/entity-packs.md",
    "configs/sources.example.yaml",
    "configs/entities.example.yaml",
    "configs/scoring.example.yaml",
    "configs/source-packs/fashion-public.example.yaml",
    "configs/entity-packs/fashion-watchlist.example.yaml",
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "schemas/community-signals.schema.json",
    "src/fashion_radar/cli.py",
    "src/fashion_radar/__main__.py",
    "src/fashion_radar/templates/daily_report.md",
    "src/fashion_radar/templates/configs/sources.example.yaml",
    "src/fashion_radar/templates/configs/entities.example.yaml",
    "src/fashion_radar/templates/configs/scoring.example.yaml",
)


def _single_archive(build_dir: Path, pattern: str) -> Path:
    matches = sorted(build_dir.glob(pattern))
    if len(matches) != 1:
        names = ", ".join(path.name for path in matches) or "none"
        raise SystemExit(f"Expected exactly one {pattern} archive in {build_dir}; found {names}")
    return matches[0]


def _missing_exact(required: tuple[str, ...], names: set[str]) -> list[str]:
    return sorted(path for path in required if path not in names)


def _missing_patterns(required: tuple[str, ...], names: set[str]) -> list[str]:
    return sorted(pattern for pattern in required if not any(fnmatch.fnmatch(name, pattern) for name in names))


def _sdist_names(sdist_path: Path) -> set[str]:
    with tarfile.open(sdist_path) as sdist:
        raw_names = [name for name in sdist.getnames() if "/" in name]
    return {name.split("/", 1)[1] for name in raw_names}


def check_archives(build_dir: Path) -> None:
    wheel_path = _single_archive(build_dir, "*.whl")
    sdist_path = _single_archive(build_dir, "*.tar.gz")

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = set(wheel.namelist())
    missing_wheel = _missing_exact(REQUIRED_WHEEL_PATHS, wheel_names)
    missing_wheel.extend(_missing_patterns(REQUIRED_WHEEL_PATTERNS, wheel_names))
    if missing_wheel:
        raise SystemExit("Missing wheel files: " + ", ".join(sorted(missing_wheel)))

    sdist_names = _sdist_names(sdist_path)
    missing_sdist = _missing_exact(REQUIRED_SDIST_PATHS, sdist_names)
    if missing_sdist:
        raise SystemExit("Missing sdist files: " + ", ".join(missing_sdist))


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Fashion Radar wheel and sdist contents.")
    parser.add_argument("build_dir", type=Path)
    args = parser.parse_args()

    check_archives(args.build_dir)
    print("Package archives contain required files.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py -q
```

Expected: PASS.

## Task 3: Align CI And Upload Checklist Package Smoke

**Files:**

- Modify: `tests/test_cli_docs.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Write failing docs/CI drift guard**

In `tests/test_cli_docs.py`, add this constant near the other document path
constants:

```python
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
```

Add this test after `test_upload_checklist_help_loop_matches_public_commands`:

```python
def test_package_archive_smoke_command_is_documented_and_in_ci() -> None:
    checklist = _read(UPLOAD_CHECKLIST)
    ci_workflow = _read(CI_WORKFLOW)
    build_command = 'UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"'
    archive_command = 'UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"'
    module_help_command = '"$tmp_env/venv/bin/python" -m fashion_radar --help'

    for text in (checklist, ci_workflow):
        assert build_command in text
        assert archive_command in text
        assert module_help_command in text
        assert "scripts/check_package_archives.py" in text
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci -q
```

Expected before CI/checklist edits: FAIL because the archive command and module
entrypoint smoke are absent.

- [ ] **Step 3: Update CI package smoke**

In `.github/workflows/ci.yml`, replace the inline wheel template `uv run python
- "$tmp_build"/*.whl <<'PY' ... PY` block with:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

After:

```bash
"$tmp_env/venv/bin/fashion-radar" --help
```

add:

```bash
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

- [ ] **Step 4: Update GitHub upload checklist package smoke**

In `docs/github-upload-checklist.md`, replace the current `uv run python -m
zipfile -l ... | rg ...` wheel-template check with:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
```

After:

```bash
"$tmp_env/venv/bin/fashion-radar" --help
```

add:

```bash
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

- [ ] **Step 5: Run test to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci -q
```

Expected: PASS.

## Task 4: Clarify README Install Modes

**Files:**

- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing README install-mode guard**

Add this test after `test_readme_links_current_cli_reference_not_historical_release_gate`:

```python
def test_readme_distinguishes_source_checkout_from_package_smoke() -> None:
    text = _read(README)

    assert "source checkout" in text
    assert "local wheel" in text
    assert "does not publish to PyPI" in text
    assert "[docs/github-upload-checklist.md](docs/github-upload-checklist.md)" in text
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_distinguishes_source_checkout_from_package_smoke -q
```

Expected before README edits: FAIL because the quickstart does not yet contain
the required install-mode language.

- [ ] **Step 3: Update README Quickstart language**

Replace the sentence:

```markdown
Install dependencies with uv:
```

with:

```markdown
For a source checkout, install dependencies with uv:
```

After the mirror paragraph and dependency-mirrors link, add:

```markdown
Package readiness is checked separately before upload by building and smoking a
local wheel from this checkout; that check does not publish to PyPI. See
[docs/github-upload-checklist.md](docs/github-upload-checklist.md).
```

- [ ] **Step 4: Run test to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py::test_readme_distinguishes_source_checkout_from_package_smoke -q
```

Expected: PASS.

## Task 5: Run Archive Smoke And Focused Verification

**Files:**

- No new edits expected unless tests reveal a defect.

- [ ] **Step 1: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Run archive build smoke**

Run:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

Expected: build succeeds, archive script prints
`Package archives contain required files.`, both help commands exit 0.

- [ ] **Step 3: Run formatting, lock, and mirror checks**

Run:

```bash
UV_NO_CONFIG=1 uv run ruff check scripts/check_package_archives.py tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py
UV_NO_CONFIG=1 uv run ruff format --check scripts/check_package_archives.py tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Expected: all pass; `uv.lock` remains unchanged and public-lock checks are not
mirror-bound.

## Task 6: Claude Code Release Review, Commit, Push, And Handoff

**Files:**

- Create: `docs/reviews/claude-code-stage-45-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-45-release-review.md`

- [ ] **Step 1: Create the release review prompt**

The prompt must summarize the implemented Stage 45 files, verification commands,
and boundaries. It must ask local Claude Code to inspect code/docs/tests and to
include this phrase only if acceptable:

```text
APPROVED FOR STAGE 45 COMMIT AND PUSH
```

- [ ] **Step 2: Run Claude Code release review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-45-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-45-release-review.md
```

Expected: no Critical or Important findings and approval phrase present. Fix
blockers before committing. If fixes are needed, store follow-up
`claude-code-stage-45-release-rereview*.md` records.

- [ ] **Step 3: Commit Stage 45**

Run:

```bash
git status --short
git add pyproject.toml .github/workflows/ci.yml README.md docs/github-upload-checklist.md tests/test_cli_docs.py scripts/check_package_archives.py tests/test_package_metadata.py tests/test_package_archives.py docs/superpowers/specs/2026-06-15-stage-45-package-archive-metadata-readiness-design.md docs/superpowers/plans/2026-06-15-stage-45-package-archive-metadata-readiness-plan.md docs/reviews/claude-code-stage-45-*.md
git diff --cached --check
git commit -m "Harden package archive readiness"
```

Expected: commit succeeds with only Stage 45 files staged.

- [ ] **Step 4: Push and confirm CI**

Try normal `git push origin main`. If the known Git HTTPS TLS failure recurs,
use the repository's established non-persistent GitHub API fallback without
storing the token in git config or printing it.

After push, confirm GitHub Actions completes successfully for the pushed commit.

- [ ] **Step 5: Write Handoff Summary**

Include:

- Repo status.
- Verified commands.
- Uncommitted files.
- Next step.

Do not paste large diffs or logs.
