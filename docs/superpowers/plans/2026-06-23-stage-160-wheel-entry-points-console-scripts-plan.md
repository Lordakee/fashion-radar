# Stage 160 Wheel Entry Points Console Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the package archive checker require wheel entry points under the `[console_scripts]` group.

**Architecture:** Keep archive validation centralized in `scripts/check_package_archives.py`. Replace line-based `entry_points.txt` validation with section-aware parsing using `configparser.ConfigParser(interpolation=None)` while preserving deterministic checker errors and no-traceback behavior.

**Tech Stack:** Python standard library, pytest, existing archive fixture helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_package_archives.py`
  - Import `configparser`.
  - Parse `entry_points.txt` as INI-style metadata.
  - Add a small parser helper for expected `name = target` console-script lines.
- Modify: `tests/test_package_archives.py`
  - Add RED tests for expected scripts outside `[console_scripts]`.
  - Add a target-mismatch test.
  - Update the existing missing-script assertion to the new section-aware error.
- Add: `docs/reviews/opencode-stage-160-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-160-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-160-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-160-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-160-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-160-release-review.md`

## Task 1: Add RED Tests For Section-Aware Entry Points

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Update missing-console-script expectation**

Change `test_rejects_wheel_entry_points_without_console_script(...)` to assert:

```python
for console_script_line in EXPECTED_METADATA.console_script_lines:
    assert (
        f"entry_points.txt is missing console_scripts entry: {console_script_line}"
        in result.stderr
    )
```

Expected before implementation: this test fails because the current checker
returns `entry_points.txt is missing fashion-radar = fashion_radar.cli:app`.

- [ ] **Step 2: Add wrong-group RED test**

Add after `test_rejects_wheel_entry_points_without_console_script(...)`:

```python
def test_rejects_wheel_entry_points_console_script_outside_console_scripts_section(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
            "[gui_scripts]\n"
            + "\n".join(sorted(EXPECTED_METADATA.console_script_lines))
            + "\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    for console_script_line in EXPECTED_METADATA.console_script_lines:
        assert (
            f"entry_points.txt is missing console_scripts entry: {console_script_line}"
            in result.stderr
        )
```

Expected before implementation: this test fails because the current checker
passes when the expected line appears under `[gui_scripts]`.

- [ ] **Step 3: Add wrong-target test**

Add:

```python
def test_rejects_wheel_entry_points_console_script_wrong_target(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
            "[console_scripts]\nfashion-radar = fashion_radar.other:app\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "entry_points.txt console_scripts entry mismatch: "
        "expected fashion-radar = fashion_radar.cli:app, "
        "found fashion-radar = fashion_radar.other:app"
    ) in result.stderr
```

Expected before implementation: this test fails with the old missing-line error,
not the target-mismatch error.

- [ ] **Step 4: Add malformed entry-points no-traceback test**

Add:

```python
def test_rejects_wheel_entry_points_malformed_without_traceback(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
            "fashion-radar = fashion_radar.cli:app\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "entry_points.txt is invalid:" in result.stderr
    assert "Traceback" not in result.stderr
```

Expected before implementation: this test fails because the old checker accepts
the line and exits successfully.

- [ ] **Step 5: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "entry_points"
```

Expected before implementation: the updated and new tests fail for the reasons
listed above.

## Task 2: Implement Section-Aware Entry Point Validation

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add the import**

At the top of `scripts/check_package_archives.py`, add:

```python
import configparser
```

- [ ] **Step 2: Replace `validate_wheel_entry_points(...)`**

Replace the function body with:

```python
def validate_wheel_entry_points(
    archive: zipfile.ZipFile,
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    entry_points_path = f"{dist_info_dir}/entry_points.txt"
    entry_points = read_zip_text(archive, entry_points_path)
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    try:
        parser.read_string(entry_points)
    except configparser.Error as exc:
        return [f"entry_points.txt is invalid: {exc}"]

    errors = []
    console_scripts = parser["console_scripts"] if parser.has_section("console_scripts") else {}
    for entry_point in sorted(expected_metadata.console_script_lines):
        script_name, expected_target = split_console_script_line(entry_point)
        actual_target = console_scripts.get(script_name)
        if actual_target is None:
            errors.append(f"entry_points.txt is missing console_scripts entry: {entry_point}")
        elif actual_target != expected_target:
            errors.append(
                "entry_points.txt console_scripts entry mismatch: "
                f"expected {entry_point}, found {script_name} = {actual_target}"
            )
    return errors
```

- [ ] **Step 3: Add helper `split_console_script_line(...)`**

Add below `validate_wheel_entry_points(...)`:

```python
def split_console_script_line(entry_point: str) -> tuple[str, str]:
    script_name, separator, target = entry_point.partition(" = ")
    if not separator:
        return entry_point, ""
    return script_name, target
```

The helper is intentionally minimal because `console_script_lines` is generated
internally from `[project.scripts]` as `name = target`.

- [ ] **Step 4: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "entry_points"
```

Expected after implementation: focused tests pass.

- [ ] **Step 5: Run package archive verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
```

Expected: tests, lint, format, build, and archive checker pass.

## Task 3: Local Code Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-160-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-160-code-review.md`
- Add: `docs/reviews/opencode-stage-160-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-160-release-review.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-160-code-review-prompt.md` with:

```markdown
# Stage 160 Code Review Prompt

Review the Stage 160 implementation for Fashion Radar.

Changed files:

- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `docs/superpowers/specs/2026-06-23-stage-160-wheel-entry-points-console-scripts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-160-wheel-entry-points-console-scripts-plan.md`
- `docs/reviews/opencode-stage-160-plan-review-prompt.md`
- `docs/reviews/opencode-stage-160-plan-review.md`

Objective:

Make the package archive checker require expected wheel entry points under the
`[console_scripts]` group.

Review questions:

1. Does the implementation reject expected scripts under the wrong entry-point
   group?
2. Does it preserve case-sensitive script names by setting `optionxform = str`?
3. Does it fail malformed `entry_points.txt` without a traceback?
4. Are tests sufficient and scoped to package archive validation?
5. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
```

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-160-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-160-code-review.md
rm -f "$tmp_review"
```

Expected: no critical or important findings. If any appear, fix and request
rereview.

- [ ] **Step 3: Run full release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all checks pass.

- [ ] **Step 4: Run local opencode release review**

Create `docs/reviews/opencode-stage-160-release-review-prompt.md` summarizing the
Stage 160 changes and full release-gate results, then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-160-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-160-release-review.md
rm -f "$tmp_review"
```

Expected: no critical or important findings.

- [ ] **Step 5: Re-run release hygiene after release review**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: the release-review artifact passes release hygiene.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add scripts/check_package_archives.py tests/test_package_archives.py \
  docs/superpowers/specs/2026-06-23-stage-160-wheel-entry-points-console-scripts-design.md \
  docs/superpowers/plans/2026-06-23-stage-160-wheel-entry-points-console-scripts-plan.md \
  docs/reviews/opencode-stage-160-plan-review-prompt.md \
  docs/reviews/opencode-stage-160-plan-review.md \
  docs/reviews/opencode-stage-160-code-review-prompt.md \
  docs/reviews/opencode-stage-160-code-review.md \
  docs/reviews/opencode-stage-160-release-review-prompt.md \
  docs/reviews/opencode-stage-160-release-review.md
git commit -m "test: validate wheel console entry points"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

Expected: commit succeeds and push updates `origin/main`.

## Self-Review Notes

- Spec coverage: covers wrong group, missing script, wrong target, malformed
  entry-point metadata, no traceback, focused and full verification.
- Placeholder scan: no placeholder steps remain.
- Type consistency: helper names and expected error strings are consistent
  across tests, implementation, and review prompts.
