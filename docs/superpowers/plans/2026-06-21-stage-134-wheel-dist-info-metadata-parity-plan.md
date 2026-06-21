# Stage 134 Wheel Dist-Info Metadata Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject wheels whose top-level `.dist-info` directory does not match the project name and version derived from `pyproject.toml`.

**Architecture:** Add one RED test that rewrites the existing wheel fixture's `.dist-info` directory while preserving valid `METADATA`, then add small stdlib helpers in `scripts/check_package_archives.py` to derive and compare the expected directory. The check runs only after the existing exact-one-top-level `.dist-info` selector succeeds.

**Tech Stack:** Python 3.11 stdlib (`re`, `zipfile`, `tomllib`), pytest, uv frozen command runner, ruff.

---

## Files

- Modify `tests/test_package_archives.py`
  - Add a focused parametrized test beside the existing `.dist-info` layout
    tests.
- Modify `scripts/check_package_archives.py`
  - Add distribution-name normalization and expected `.dist-info` helpers.
  - Append mismatch errors from `validate_wheel()` after selecting the single
    top-level `.dist-info` directory.
- Create `docs/reviews/opencode-stage-134-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-134-plan-review.md`.
- Create `docs/reviews/opencode-stage-134-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-134-code-review.md`.

No package filename validation, sdist root validation, license-path validation,
wheel/sdist member validation, forbidden-member validation, dependency changes,
`pyproject.toml` changes, `uv.lock` changes, CI behavior changes, runtime
product behavior changes, connectors, scraping, browser automation, platform
APIs, monitoring, scheduling, source acquisition, demand proof, ranking,
coverage verification, or compliance/audit product behavior are part of this
stage.

## Task 1: Add RED wheel dist-info directory mismatch test

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add helper and parametrized RED test**

Add after `test_rejects_split_wheel_dist_info_files`:

```python
def wheel_files_with_dist_info_dir(dist_info_dir: str) -> dict[str, str]:
    return {
        (
            f"{dist_info_dir}/{path.split('/', 1)[1]}"
            if path.startswith("fashion_radar-0.1.0.dist-info/")
            else path
        ): content
        for path, content in WHEEL_FILES.items()
    }


@pytest.mark.parametrize(
    "dist_info_dir",
    [
        "wrong_name-0.1.0.dist-info",
        "fashion_radar-9.9.9.dist-info",
    ],
)
def test_rejects_wheel_with_mismatched_dist_info_directory(
    tmp_path: Path,
    dist_info_dir: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, files=wheel_files_with_dist_info_dir(dist_info_dir))
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "wheel archive dist-info directory mismatch: expected "
        f"fashion_radar-0.1.0.dist-info, found {dist_info_dir}"
    ) in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_with_mismatched_dist_info_directory -q
```

Expected result: fail because the current checker accepts a single mismatched
`.dist-info` directory when its `METADATA` content still matches the project.

## Task 2: Add expected dist-info directory validation

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add helper functions**

Add after `select_wheel_dist_info_dir()`:

```python
def validate_wheel_dist_info_dir(
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    expected_dist_info_dir = expected_wheel_dist_info_dir(expected_metadata)
    if dist_info_dir == expected_dist_info_dir:
        return []
    return [
        "wheel archive dist-info directory mismatch: "
        f"expected {expected_dist_info_dir}, found {dist_info_dir}"
    ]


def expected_wheel_dist_info_dir(expected_metadata: ExpectedProjectMetadata) -> str:
    normalized_name = normalize_distribution_name(expected_metadata.name)
    return f"{normalized_name}-{expected_metadata.version}.dist-info"


def normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "_", name).lower()
```

- [ ] **Step 2: Call the validator from `validate_wheel()`**

Inside `validate_wheel()`, in the `if dist_info_dir is not None:` block, insert
the new validation before `validate_wheel_dist_info_files()`:

```python
                errors.extend(
                    validate_wheel_dist_info_dir(dist_info_dir, expected_metadata)
                )
```

- [ ] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_wheel_with_mismatched_dist_info_directory -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-134-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-134-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "dist_info"
uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"
git diff --check
```

Expected result: focused archive tests, package metadata tests, lint, format,
live package build archive check, and whitespace check pass.

- [ ] **Step 2: Write Stage 134 code review prompt**

Create `docs/reviews/opencode-stage-134-code-review-prompt.md` with:

```markdown
Review the Stage 134 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheels whose single top-level `.dist-info` directory does not match
  the expected project distribution name and version derived from
  `pyproject.toml`.
- Preserve existing exact-one-top-level `.dist-info`, missing dist-info file,
  metadata, entry point, and forbidden-member behavior.
- Keep this release-hygiene-only with no runtime product behavior changes.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 134 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 134 design and plan?
2. Does the RED test prove that valid `METADATA` is not enough when the wheel
   `.dist-info` directory name or version is wrong?
3. Does the helper normalize `fashion-radar` to `fashion_radar` without adding
   dependencies?
4. Does the mismatch check run only after exactly one top-level `.dist-info`
   directory is selected, preserving nested/multiple/split layout behavior?
5. Does the stage avoid package filename validation, sdist root validation,
   dependency changes, `pyproject.toml`, `uv.lock`, CI changes, runtime product
   behavior changes, connectors, scraping, browser automation, platform API,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Return:
Start with `# Stage 134 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-134-code-review-prompt.md)" > "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-134-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 134 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-134-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 134 files only.

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

- [ ] **Step 2: Commit Stage 134**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_package_archives.py tests/test_package_archives.py docs/superpowers/specs/2026-06-21-stage-134-wheel-dist-info-metadata-parity-design.md docs/superpowers/plans/2026-06-21-stage-134-wheel-dist-info-metadata-parity-plan.md docs/reviews/opencode-stage-134-plan-review-prompt.md docs/reviews/opencode-stage-134-plan-review.md docs/reviews/opencode-stage-134-code-review-prompt.md docs/reviews/opencode-stage-134-code-review.md
git commit -m "Validate wheel dist-info metadata parity"
```

Expected result: one commit containing only Stage 134 package archive checker,
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

- Spec coverage: the plan includes a RED test, helper implementation, focused
  verification, opencode code review, release gate, commit, push, and CI check.
- Placeholder scan: no placeholder implementation steps are present.
- Type consistency: helper names and call sites consistently use
  `ExpectedProjectMetadata`, `dist_info_dir`, and `expected_metadata`.
