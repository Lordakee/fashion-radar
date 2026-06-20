# Stage 130 Package Archive Pyproject Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `scripts/check_package_archives.py` derive expected wheel
metadata from `pyproject.toml` instead of hardcoding project name, version, and
console script values.

**Architecture:** Add a stdlib `tomllib` loader and frozen metadata dataclass,
thread the loaded metadata through wheel validation, and cover the derivation
with focused tests.

**Tech Stack:** Python 3.11 stdlib (`tomllib`, `dataclasses`), pytest, existing
package archive checker script.

---

## Files

- Modify `scripts/check_package_archives.py`
  - Replace hardcoded project metadata constants with a pyproject loader.
  - Thread loaded expected metadata into wheel metadata and entry point checks.
- Modify `tests/test_package_archives.py`
  - Import the script module directly for loader unit tests.
  - Add tests for repo pyproject and supplied temporary pyproject derivation.
- Create `docs/reviews/opencode-stage-130-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-130-plan-review.md`.
- Create `docs/reviews/opencode-stage-130-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-130-code-review.md`.

The plan-review prompt and plan-review artifact are produced before
implementation begins; the implementation tasks create only the code-review
prompt and code-review artifact.

No dependency changes, `pyproject.toml` changes, `uv.lock` changes, CI behavior,
package filename/dist-info path/license validation changes, runtime product
behavior, connectors, scraping, browser automation, platform APIs, monitoring,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance/audit product behavior is part of this stage.

## Task 1: Add RED loader tests

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Import the checker module**

Add `import importlib.util` near the top and load the script module after
`SCRIPT` is defined:

```python
spec = importlib.util.spec_from_file_location("check_package_archives", SCRIPT)
check_package_archives = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(check_package_archives)
```

- [ ] **Step 2: Add repo pyproject derivation test**

Add:

```python
def test_expected_archive_metadata_is_derived_from_pyproject() -> None:
    metadata = check_package_archives.load_expected_project_metadata()

    assert metadata.name == "fashion-radar"
    assert metadata.version == "0.1.0"
    assert metadata.console_script_lines == frozenset(
        {"fashion-radar = fashion_radar.cli:app"}
    )
```

- [ ] **Step 3: Add supplied pyproject derivation test**

Add:

```python
def test_expected_archive_metadata_loader_uses_supplied_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "\n".join(
            [
                "[project]",
                'name = "example-package"',
                'version = "9.8.7"',
                "[project.scripts]",
                'example-cli = "example.cli:app"',
                'example-admin = "example.admin:main"',
            ]
        ),
        encoding="utf-8",
    )

    metadata = check_package_archives.load_expected_project_metadata(pyproject)

    assert metadata.name == "example-package"
    assert metadata.version == "9.8.7"
    assert metadata.console_script_lines == frozenset(
        {
            "example-cli = example.cli:app",
            "example-admin = example.admin:main",
        }
    )
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_expected_archive_metadata_is_derived_from_pyproject tests/test_package_archives.py::test_expected_archive_metadata_loader_uses_supplied_pyproject -q
```

Expected result: fail because `load_expected_project_metadata` does not exist.

## Task 2: Implement pyproject metadata loading and validation

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add metadata loader**

Add stdlib imports:

```python
import tomllib
from dataclasses import dataclass
```

Replace `PROJECT_NAME`, `PROJECT_VERSION`, and `ENTRY_POINT` with:

```python
PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


@dataclass(frozen=True)
class ExpectedProjectMetadata:
    name: str
    version: str
    console_script_lines: frozenset[str]


def load_expected_project_metadata(
    pyproject_path: Path = PYPROJECT,
) -> ExpectedProjectMetadata:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data["project"]
    scripts = project.get("scripts", {})
    return ExpectedProjectMetadata(
        name=str(project["name"]),
        version=str(project["version"]),
        console_script_lines=frozenset(
            f"{script_name} = {target}" for script_name, target in scripts.items()
        ),
    )
```

- [ ] **Step 2: Thread metadata through wheel validation**

In `validate_build_dir()`, load once:

```python
expected_metadata = load_expected_project_metadata()
```

Then call:

```python
validate_wheel(wheel_path, expected_metadata)
```

Update signatures for:

- `validate_wheel(wheel_path: Path, expected_metadata: ExpectedProjectMetadata)`
- `validate_wheel_metadata(..., expected_metadata: ExpectedProjectMetadata)`
- `validate_wheel_entry_points(..., expected_metadata: ExpectedProjectMetadata)`

- [ ] **Step 3: Use loaded metadata in checks**

Change `validate_wheel_metadata()` to compare against `expected_metadata.name`
and `expected_metadata.version`.

Change `validate_wheel_entry_points()` to return an error for each missing
script line in sorted `expected_metadata.console_script_lines`:

```python
return [
    f"entry_points.txt is missing {entry_point}"
    for entry_point in sorted(expected_metadata.console_script_lines)
    if entry_point not in entry_point_lines
]
```

- [ ] **Step 4: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_expected_archive_metadata_is_derived_from_pyproject tests/test_package_archives.py::test_expected_archive_metadata_loader_uses_supplied_pyproject -q
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-130-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-130-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_expected_archive_metadata_is_derived_from_pyproject tests/test_package_archives.py::test_expected_archive_metadata_loader_uses_supplied_pyproject -q
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen pytest tests/test_package_metadata.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"
git diff --check
```

Expected result: all focused tests, lint, package build/checker smoke, and
whitespace checks pass.

- [ ] **Step 2: Write Stage 130 code review prompt**

Create `docs/reviews/opencode-stage-130-code-review-prompt.md` with:

```markdown
Review the Stage 130 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` derive expected project name,
  version, and console script lines from `pyproject.toml`.
- Keep archive validation behavior equivalent except for removing script-side
  metadata hardcoding.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 130 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 130 design and plan?
2. Does the checker load project name, version, and `[project.scripts]` from
   `pyproject.toml` with stdlib only?
3. Is the metadata loaded once per `validate_build_dir()` run and threaded
   through wheel validation?
4. Does entry point validation check every configured console script line
   without introducing ordering or formatting requirements beyond stripped-line
   membership?
5. Do tests prove derivation from both repo pyproject and a supplied temporary
   pyproject?
6. Does the stage avoid dependency, lockfile, CI, package filename/path,
   runtime product, connector, scraping, browser automation, platform API,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior changes?

Return:
Start with `# Stage 130 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-130-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-130-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 130 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-130-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```

Expected result: release hygiene, full pytest, ruff, format, lock check,
lockfile diff, whitespace check, token absence assertion, and persistent git
auth-header absence assertion all pass.

- [ ] **Step 2: Commit Stage 130**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_package_archives.py tests/test_package_archives.py docs/superpowers/specs/2026-06-20-stage-130-package-archive-pyproject-metadata-design.md docs/superpowers/plans/2026-06-20-stage-130-package-archive-pyproject-metadata-plan.md docs/reviews/opencode-stage-130-plan-review-prompt.md docs/reviews/opencode-stage-130-plan-review.md docs/reviews/opencode-stage-130-code-review-prompt.md docs/reviews/opencode-stage-130-code-review.md
git commit -m "Derive package archive metadata from pyproject"
```

Expected result: one commit containing only Stage 130 code, tests, and review
artifacts.

- [ ] **Step 3: Push with temporary auth header**

Run the established temporary-header push pattern without storing credentials in
git config or files:

```bash
AUTH_HEADER="$(printf 'x-access-token:%s' "$GITHUB_TOKEN_FOR_PUSH" | base64 -w0)"
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub auth header remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 130 commit and CI completes
successfully.
