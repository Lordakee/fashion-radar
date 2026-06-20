# Stage 124 Package Archive Member Path Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject unsafe wheel and sdist archive member paths in the package archive checker.

**Architecture:** Add RED tests that create malformed archive members, then add a string-based path-shape guard to `scripts/check_package_archives.py`. Run the guard on raw wheel and sdist member names before normal clean-path validation and before sdist root-prefix stripping.

**Tech Stack:** Python 3.11, pytest, stdlib `zipfile`, stdlib `tarfile`, existing package archive checker script.

---

## Files

- Modify `tests/test_package_archives.py`
  - Add helper `write_sdist_with_raw_member`.
  - Add parametrized tests for unsafe wheel member paths.
  - Add parametrized tests for unsafe sdist member paths.
- Modify `scripts/check_package_archives.py`
  - Add unsafe member path helpers.
  - Call them from `validate_wheel()` and `validate_sdist()`.
- Create `docs/reviews/opencode-stage-124-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-124-plan-review.md`.
- Create `docs/reviews/opencode-stage-124-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-124-code-review.md`.

No runtime product code, dependencies, lockfile, connectors, scraping, platform
APIs, browser automation, scheduling, source acquisition, demand proof, ranking,
coverage verification, or compliance/audit product behavior is part of this
stage.

## Task 1: Add RED unsafe member path tests

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add a raw sdist helper**

After `write_sdist`, add:

```python
def write_sdist_with_raw_member(build_dir: Path, raw_member: str) -> Path:
    path = build_dir / "fashion_radar-0.1.0.tar.gz"

    with tarfile.open(path, "w:gz") as archive:
        for relative_path in SDIST_FILES:
            data = b"fixture\n"
            info = tarfile.TarInfo(f"fashion_radar-0.1.0/{relative_path}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))

        data = b"unsafe\n"
        info = tarfile.TarInfo(raw_member)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

    return path
```

- [ ] **Step 2: Add failing wheel tests**

Add after `test_accepts_archives_with_required_files_and_metadata`:

```python
@pytest.mark.parametrize(
    ("unsafe_path", "expected_path"),
    [
        ("../outside.txt", "../outside.txt"),
        ("/absolute.txt", "/absolute.txt"),
        ("fashion_radar/../outside.txt", "fashion_radar/../outside.txt"),
        ("C:/outside.txt", "C:/outside.txt"),
        ("C:outside.txt", "C:outside.txt"),
        ("//server/share/outside.txt", "//server/share/outside.txt"),
        (r"fashion_radar\..\outside.txt", "fashion_radar/../outside.txt"),
    ],
)
def test_rejects_wheel_with_unsafe_archive_member_path(
    tmp_path: Path,
    unsafe_path: str,
    expected_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir, files=WHEEL_FILES | {unsafe_path: "unsafe\n"})
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        f"wheel archive contains unsafe archive member path: {expected_path}"
    ) in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 3: Add failing sdist tests**

Add after the wheel unsafe-member test:

```python
@pytest.mark.parametrize(
    ("unsafe_path", "expected_path"),
    [
        ("../outside.txt", "../outside.txt"),
        ("/absolute.txt", "/absolute.txt"),
        ("fashion_radar-0.1.0/../outside.txt", "fashion_radar-0.1.0/../outside.txt"),
        ("C:/outside.txt", "C:/outside.txt"),
        ("C:outside.txt", "C:outside.txt"),
        ("//server/share/outside.txt", "//server/share/outside.txt"),
        (
            r"fashion_radar-0.1.0\..\outside.txt",
            "fashion_radar-0.1.0/../outside.txt",
        ),
    ],
)
def test_rejects_sdist_with_unsafe_archive_member_path(
    tmp_path: Path,
    unsafe_path: str,
    expected_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist_with_raw_member(build_dir, unsafe_path)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        f"sdist archive contains unsafe archive member path: {expected_path}"
    ) in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "unsafe_archive_member"
```

Expected result: tests fail because the checker does not yet reject unsafe
archive member paths.

## Task 2: Add unsafe member path validation

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Update `validate_wheel`**

Replace the first lines inside the `with zipfile.ZipFile(wheel_path) as archive:`
block with:

```python
            raw_paths = archive.namelist()
            errors = unsafe_archive_member_errors(raw_paths, "wheel archive")
            paths = clean_archive_paths(raw_paths)
            errors.extend(
                missing_required_paths(
                    paths,
                    exact_paths=WHEEL_REQUIRED_PATHS,
                    archive_label="wheel archive",
                )
            )
```

Keep the following existing validation order after this block:

```python
            errors.extend(forbidden_release_member_errors(paths, "wheel archive"))
            dist_info_dir, dist_info_errors = select_wheel_dist_info_dir(paths)
```

- [ ] **Step 2: Update `validate_sdist`**

Replace:

```python
        with tarfile.open(sdist_path, "r:gz") as archive:
            paths = normalize_sdist_paths(member.name for member in archive.getmembers())
```

with:

```python
        with tarfile.open(sdist_path, "r:gz") as archive:
            raw_paths = [member.name for member in archive.getmembers()]
            unsafe_errors = unsafe_archive_member_errors(raw_paths, "sdist archive")
            paths = normalize_sdist_paths(raw_paths)
```

Then replace:

```python
    errors = missing_required_paths(
```

with:

```python
    errors = unsafe_errors + missing_required_paths(
```

- [ ] **Step 3: Add helper functions**

Add before `clean_archive_paths`:

```python
def unsafe_archive_member_errors(paths: Iterable[object], archive_label: str) -> list[str]:
    errors = []
    for raw_path in paths:
        path = clean_archive_path(raw_path)
        if path and is_unsafe_archive_path(path):
            errors.append(f"{archive_label} contains unsafe archive member path: {path}")
    return errors


def is_unsafe_archive_path(path: str) -> bool:
    if path.startswith("/"):
        return True
    if re.match(r"^[A-Za-z]:", path) is not None:
        return True
    return any(part == ".." for part in path.split("/"))
```

- [ ] **Step 4: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "unsafe_archive_member"
```

Expected result: unsafe-member tests pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-124-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-124-code-review.md`

- [ ] **Step 1: Run focused package archive tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected result: package archive tests pass.

- [ ] **Step 2: Run focused lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
```

Expected result: both commands pass.

- [ ] **Step 3: Write Stage 124 code review prompt**

Create `docs/reviews/opencode-stage-124-code-review-prompt.md` with:

```markdown
Review the Stage 124 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject unsafe wheel and sdist archive member paths in
  `scripts/check_package_archives.py`.
- Preserve existing required-file, metadata, entry-point, and forbidden-member
  package archive validation behavior.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 124 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 124 design and plan?
2. Are unsafe archive member paths rejected before sdist root-prefix stripping?
3. Are wheel and sdist unsafe path cases covered, including `..`, absolute
   paths, Windows drive paths, UNC-style paths, and backslash normalization?
4. Does the stage preserve existing package archive checks?
5. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 4: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-124-code-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-124-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 124 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n→ ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-124-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run the full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
```

Expected result: every command exits 0.

- [ ] **Step 2: Check secrets and temporary auth state**

Run:

```bash
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: no token matches in the repository and no persistent GitHub
extraheader output.

- [ ] **Step 3: Stage the Stage 124 files**

Run:

```bash
git add scripts/check_package_archives.py \
  tests/test_package_archives.py \
  docs/superpowers/specs/2026-06-20-stage-124-package-archive-member-path-safety-design.md \
  docs/superpowers/plans/2026-06-20-stage-124-package-archive-member-path-safety-plan.md \
  docs/reviews/opencode-stage-124-plan-review-prompt.md \
  docs/reviews/opencode-stage-124-plan-review.md \
  docs/reviews/opencode-stage-124-code-review-prompt.md \
  docs/reviews/opencode-stage-124-code-review.md
```

- [ ] **Step 4: Verify staged diff and commit**

Run:

```bash
git diff --cached --stat
git diff --cached | rg -n 'ghp_[A-Za-z0-9]+' || true
git commit -m "Reject unsafe package archive member paths"
```

Expected result: commit succeeds and no token scan output appears.

- [ ] **Step 5: Push with temporary GitHub auth header**

Run:

```bash
AUTH_HEADER=$(printf 'x-access-token:%s' '<token supplied by user>' | base64 -w0)
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub extraheader output
appears.

- [ ] **Step 6: Verify remote SHA and CI**

Run:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected result: both SHAs match. Then poll GitHub Actions for the pushed SHA
and require a successful CI conclusion before reporting completion.

## Self-Review

- Spec coverage: the plan covers failing tests, implementation, focused
  verification, local code review, full release gate, commit, push, and CI.
- Marker scan: no unresolved implementation markers remain. The push command
  intentionally uses `<token supplied by user>` as a non-secret stand-in.
- Type consistency: helper names, test names, command strings, and file paths
  match across tasks.
