# Stage 136 Package Archive Filename And Sdist Root Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject wheel/sdist archive files whose outer filenames or sdist root directory do not match the project name and version derived from `pyproject.toml`.

**Architecture:** Extend the existing package archive checker after single-archive selection and before content checks. Reuse Stage 134 distribution-name normalization, add small expected filename/root helpers, validate selected archive basenames in `validate_build_dir()`, and validate raw sdist root names before `normalize_sdist_paths()` strips them.

**Tech Stack:** Python 3.11 stdlib (`pathlib`, existing `re`/`tomllib`), pytest, uv frozen command runner, ruff.

---

## Files

- Modify `tests/test_package_archives.py`
  - Add optional filename arguments to `write_wheel()` and `write_sdist()`.
  - Add an optional `root_dir` argument to `write_sdist()`.
  - Add RED tests for mismatched wheel filename, sdist filename, and sdist
    root directory.
- Modify `scripts/check_package_archives.py`
  - Add expected filename and sdist-root helpers.
  - Add archive filename mismatch validation in `validate_build_dir()`.
  - Thread metadata into `validate_sdist()` and validate raw sdist root names
    before path normalization.
- Create `docs/reviews/opencode-stage-136-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-136-plan-review.md`.
- Create `docs/reviews/opencode-stage-136-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-136-code-review.md`.

No wheel tag parsing, platform wheel support, wheel `.dist-info` path changes,
wheel/sdist required-member validation changes, license-path validation
changes, forbidden-member validation changes, build backend changes, CI
changes, dependency changes, `pyproject.toml` changes, `uv.lock` changes,
runtime product behavior changes, connectors, scraping, browser automation,
platform APIs, monitoring, scheduling, source acquisition, demand proof,
ranking, coverage verification, or compliance/audit product behavior are part
of this stage.

## Task 1: Add RED package filename and sdist root mismatch tests

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add optional filename and root parameters to archive fixture writers**

Change `write_wheel()` to:

```python
def write_wheel(
    build_dir: Path,
    *,
    files: dict[str, str] | None = None,
    filename: str = "fashion_radar-0.1.0-py3-none-any.whl",
) -> Path:
    path = build_dir / filename
    archive_files = WHEEL_FILES if files is None else files

    with zipfile.ZipFile(path, "w") as archive:
        for archive_path, content in archive_files.items():
            archive.writestr(archive_path, content)

    return path
```

Change `write_sdist()` to:

```python
def write_sdist(
    build_dir: Path,
    *,
    files: list[str] | None = None,
    filename: str = "fashion_radar-0.1.0.tar.gz",
    root_dir: str = "fashion_radar-0.1.0",
) -> Path:
    path = build_dir / filename
    archive_files = SDIST_FILES if files is None else files

    with tarfile.open(path, "w:gz") as archive:
        for relative_path in archive_files:
            data = b"fixture\n"
            info = tarfile.TarInfo(f"{root_dir}/{relative_path}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))

    return path
```

- [ ] **Step 2: Add parametrized filename mismatch test**

Add after `test_allowed_gitignore_marker_does_not_hide_unexpected_direct_child`:

```python
@pytest.mark.parametrize(
    ("wheel_filename", "sdist_filename", "expected_error"),
    [
        (
            "wrong_name-0.1.0-py3-none-any.whl",
            "fashion_radar-0.1.0.tar.gz",
            (
                "wheel archive filename mismatch: expected "
                "fashion_radar-0.1.0-py3-none-any.whl, "
                "found wrong_name-0.1.0-py3-none-any.whl"
            ),
        ),
        (
            "fashion_radar-9.9.9-py3-none-any.whl",
            "fashion_radar-0.1.0.tar.gz",
            (
                "wheel archive filename mismatch: expected "
                "fashion_radar-0.1.0-py3-none-any.whl, "
                "found fashion_radar-9.9.9-py3-none-any.whl"
            ),
        ),
        (
            "fashion_radar-0.1.0-py3-none-any.whl",
            "wrong_name-0.1.0.tar.gz",
            (
                "sdist archive filename mismatch: expected "
                "fashion_radar-0.1.0.tar.gz, found wrong_name-0.1.0.tar.gz"
            ),
        ),
        (
            "fashion_radar-0.1.0-py3-none-any.whl",
            "fashion_radar-9.9.9.tar.gz",
            (
                "sdist archive filename mismatch: expected "
                "fashion_radar-0.1.0.tar.gz, found fashion_radar-9.9.9.tar.gz"
            ),
        ),
    ],
)
def test_rejects_package_archives_with_mismatched_filenames(
    tmp_path: Path,
    wheel_filename: str,
    sdist_filename: str,
    expected_error: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, filename=wheel_filename)
    write_sdist(build_dir, filename=sdist_filename)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert expected_error in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 3: Add sdist root mismatch test**

Add after the filename mismatch test:

```python
@pytest.mark.parametrize(
    "root_dir",
    [
        "wrong_name-0.1.0",
        "fashion_radar-9.9.9",
    ],
)
def test_rejects_sdist_with_mismatched_root_directory(
    tmp_path: Path,
    root_dir: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, root_dir=root_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive root directory mismatch: expected "
        f"fashion_radar-0.1.0, found {root_dir}"
    ) in result.stderr
    assert "sdist archive missing required file" not in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_package_archives_with_mismatched_filenames tests/test_package_archives.py::test_rejects_sdist_with_mismatched_root_directory -q
```

Expected result: fail because the current checker accepts any single `*.whl`,
any single `*.tar.gz`, and any single sdist root that normalizes to required
files when archive contents are otherwise valid.

## Task 2: Add archive filename and sdist root parity validation

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add expected filename and root helper functions**

Add after `normalize_distribution_name()`:

```python
def expected_archive_base_name(expected_metadata: ExpectedProjectMetadata) -> str:
    normalized_name = normalize_distribution_name(expected_metadata.name)
    return f"{normalized_name}-{expected_metadata.version}"


def expected_wheel_archive_name(expected_metadata: ExpectedProjectMetadata) -> str:
    return f"{expected_archive_base_name(expected_metadata)}-py3-none-any.whl"


def expected_sdist_archive_name(expected_metadata: ExpectedProjectMetadata) -> str:
    return f"{expected_archive_base_name(expected_metadata)}.tar.gz"


def expected_sdist_root_dir(expected_metadata: ExpectedProjectMetadata) -> str:
    return expected_archive_base_name(expected_metadata)
```

Keep `expected_wheel_dist_info_dir()` using the same base:

```python
def expected_wheel_dist_info_dir(expected_metadata: ExpectedProjectMetadata) -> str:
    return f"{expected_archive_base_name(expected_metadata)}.dist-info"
```

- [ ] **Step 2: Add archive filename validator**

Add after the expected-name helpers:

```python
def validate_archive_filename(
    archive_path: Path,
    archive_label: str,
    expected_name: str,
) -> list[str]:
    if archive_path.name == expected_name:
        return []
    return [
        f"{archive_label} archive filename mismatch: "
        f"expected {expected_name}, found {archive_path.name}"
    ]
```

- [ ] **Step 3: Add sdist root validator**

Add near `normalize_sdist_paths()`:

```python
def validate_sdist_root_dir(
    paths: Iterable[object],
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    cleaned_paths = [clean_archive_path(path) for path in paths]
    cleaned_paths = [path for path in cleaned_paths if path]
    roots = {path.split("/", 1)[0] for path in cleaned_paths if "/" in path}
    expected_root = expected_sdist_root_dir(expected_metadata)
    if len(roots) != 1:
        found = ", ".join(sorted(roots)) or "none"
        return [
            "sdist archive root directory mismatch: "
            f"expected {expected_root}, found {found}"
        ]
    root = next(iter(roots))
    if root == expected_root:
        return []
    return [
        "sdist archive root directory mismatch: "
        f"expected {expected_root}, found {root}"
    ]
```

- [ ] **Step 4: Call filename validators from `validate_build_dir()`**

In `validate_build_dir()`, after the `wheel_path is None or sdist_path is None`
guard and before `unexpected_build_dir_child_errors()`, add:

```python
    filename_errors = (
        validate_archive_filename(
            wheel_path,
            "wheel",
            expected_wheel_archive_name(expected_metadata),
        )
        + validate_archive_filename(
            sdist_path,
            "sdist",
            expected_sdist_archive_name(expected_metadata),
        )
    )
```

Then include `filename_errors` in the returned error list:

```python
    return (
        filename_errors
        + build_dir_errors
        + validate_wheel(wheel_path, expected_metadata)
        + validate_sdist(sdist_path, expected_metadata)
    )
```

- [ ] **Step 5: Thread metadata into `validate_sdist()` and validate roots before normalization**

Change the signature:

```python
def validate_sdist(
    sdist_path: Path,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
```

Inside the `with tarfile.open(...)` block, add root validation after unsafe
errors and before normalization:

```python
            root_errors = validate_sdist_root_dir(raw_paths, expected_metadata)
            paths = normalize_sdist_paths(raw_paths)
```

Then include `root_errors` in the final error list:

```python
    errors = unsafe_errors + root_errors + missing_required_paths(
        paths,
        exact_paths=SDIST_REQUIRED_PATHS,
        archive_label="sdist archive",
    )
```

- [ ] **Step 6: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_package_archives_with_mismatched_filenames tests/test_package_archives.py::test_rejects_sdist_with_mismatched_root_directory -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-136-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-136-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "filename or sdist_root or dist_info"
uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"
git diff --check
```

Expected result: focused filename/root/dist-info tests, package archive tests,
package metadata tests, lint, format, live package build archive check, and
whitespace check pass.

- [ ] **Step 2: Write Stage 136 code review prompt**

Create `docs/reviews/opencode-stage-136-code-review-prompt.md` with:

```markdown
Review the Stage 136 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheel/sdist archive files whose outer filenames or sdist root
  directory do not match the project distribution name and version derived from
  `pyproject.toml`.
- Keep existing archive required-file and forbidden-member checks unchanged.
- Keep this release-hygiene-only with no runtime product behavior changes.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 136 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 136 design and plan?
2. Do the RED tests prove that valid archive contents are not enough when the
   outer wheel filename, outer sdist filename, or sdist root directory is
   wrong?
3. Does the checker derive expected filenames and sdist root from
   `ExpectedProjectMetadata` and the existing normalized distribution name
   helper?
4. Does filename validation run only after exactly one wheel and exactly one
   sdist are selected, preserving existing missing/multiple archive behavior?
5. Does sdist root validation inspect raw member names before
   `normalize_sdist_paths()` strips the root?
6. Does the stage avoid wheel tag parsing, `.dist-info` changes, dependency
   changes, `pyproject.toml`, `uv.lock`, CI, runtime product behavior,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Return:
Start with `# Stage 136 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-136-code-review-prompt.md)" > "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-136-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 136 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-136-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 136 files only.

- [ ] **Step 1: Run release gate**

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

Expected result: all commands pass.

- [ ] **Step 2: Commit Stage 136**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_package_archives.py tests/test_package_archives.py docs/superpowers/specs/2026-06-21-stage-136-package-archive-filename-parity-design.md docs/superpowers/plans/2026-06-21-stage-136-package-archive-filename-parity-plan.md docs/reviews/opencode-stage-136-plan-review-prompt.md docs/reviews/opencode-stage-136-plan-review.md docs/reviews/opencode-stage-136-code-review-prompt.md docs/reviews/opencode-stage-136-code-review.md
git commit -m "Validate package archive naming parity"
```

Expected result: one commit containing only Stage 136 package archive checker,
tests, design, plan, and review artifacts.

- [ ] **Step 3: Push with ephemeral credentials**

Use the established one-shot push pattern from the operator shell, deriving the
credential header only in process memory and passing it through `git -c` for
that single command. Do not write the token, derived header, or push command
containing credentials into files, git config, shell profile, or review
artifacts. Clear the temporary shell variable immediately after the push, then
verify no persistent GitHub credential header remains:

```bash
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub credential header
remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Expected result: remote `main` points to the new commit. Poll GitHub Actions for
that SHA until CI completes.

## Self-Review

- Spec coverage: the plan covers RED tests, helper implementation, focused
  verification, opencode code review, release gate, commit, push, and CI check.
- Placeholder scan: no placeholder implementation steps are present.
- Type consistency: helper names, labels, and expected filenames/root names are
  consistent across tasks.
