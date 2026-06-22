# Stage 159 Review Artifact Hygiene Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make release hygiene reject malformed Stage 159+ local review capture artifacts before commit or GitHub upload.

**Architecture:** Keep the guard inside `scripts/check_release_hygiene.py`, alongside the existing secret/path/git-config checks. Add one focused review-artifact scanner that only inspects completed opencode review output files under `docs/reviews/`, with a Stage 159 enforcement floor to avoid historical churn.

**Tech Stack:** Python standard library, pytest, existing git-backed release-hygiene fixtures, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_release_hygiene.py`
  - Add review artifact path matching.
  - Add line-level capture hygiene checks.
  - Wire the new scanner into `collect_findings(...)`.
- Modify: `tests/test_release_hygiene.py`
  - Add RED tests for Stage 159+ completed review output files.
  - Add exclusions for prompt files and Stage 158 legacy files.
- Add: `docs/reviews/opencode-stage-159-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-159-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-159-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-159-code-review.md`

## Task 1: Add RED Tests For Review Capture Hygiene

**Files:**

- Modify: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add a clean review artifact fixture constant**

Add near the other module-level constants:

```python
CLEAN_REVIEW_ARTIFACT = """## Verdict

No critical findings. No important findings.

## Critical
None.

## Important
None.
"""
```

- [ ] **Step 2: Add a clean Stage 159 review output acceptance test**

Add after `test_clean_temp_repo_passes(...)`:

```python
def test_stage_159_review_artifact_with_clean_body_passes(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        CLEAN_REVIEW_ARTIFACT,
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 3: Add a tool-status rejection test**

Add:

```python
def test_stage_159_review_artifact_with_tool_status_line_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-159-code-review.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert result.stdout == ""
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-review.md:3: tool-status line"
    ) in result.stderr


def test_stage_159_review_artifact_with_review_completed_prose_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\nReview completed on 2026-06-23 with no blocking findings.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 4: Add prompt-file and legacy-stage exclusions**

Add:

```python
def test_stage_159_review_artifact_prompt_with_tool_status_example_is_ignored(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review-prompt.md",
        "Review this stage. Reject output containing Wrote lines.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""


def test_stage_158_legacy_review_artifact_is_not_rechecked(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-158-code-review.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-158-code-review.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 5: Add untracked ANSI-output rejection test**

Add:

```python
def test_untracked_stage_159_review_artifact_with_ansi_escape_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(
        repo_root,
        "docs/reviews/opencode-stage-159-release-review.md",
        "## Verdict\n\n\x1b[32mApproved\x1b[0m\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in untracked file: "
        "docs/reviews/opencode-stage-159-release-review.md:3: ANSI escape sequence"
    ) in result.stderr
```

- [ ] **Step 6: Add first-line process-chatter rejection test**

Add:

```python
def test_stage_159_review_artifact_with_process_chatter_start_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-plan-review.md",
        "I'll inspect the repository first.\n\n## Verdict\nNo blocking findings.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-plan-review.md:1: process chatter at start"
    ) in result.stderr
```

- [ ] **Step 7: Add opencode UI marker rejection and false-positive tests**

Add:

```python
def test_stage_159_review_artifact_with_tool_ui_marker_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-release-rereview.md",
        "## Verdict\n\nbuild \u00b7 running\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-release-rereview.md:3: tool UI marker"
    ) in result.stderr


def test_stage_159_review_artifact_with_inline_arrow_prose_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        "## Verdict\n\n- `pytest -q` \u2192 1300 passed\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 8: Add empty-output and numbered-rereview tests**

Add:

```python
def test_stage_159_review_artifact_with_empty_output_fails(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-release-review.md",
        "   \n\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-release-review.md: empty output"
    ) in result.stderr


def test_stage_159_numbered_rereview_artifact_is_checked(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-rereview-2.md",
        "## Verdict\n\nWrote docs/reviews/opencode-stage-159-code-rereview-2.md\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-rereview-2.md:3: tool-status line"
    ) in result.stderr
```

- [ ] **Step 9: Add a current-repository compatibility guard**

Add:

```python
def test_current_repository_tracked_review_artifacts_have_no_capture_findings() -> None:
    checker = load_checker_module()
    result = git(REPO_ROOT, "ls-files", "docs/reviews")
    tracked_paths = result.stdout.splitlines()

    assert (
        checker.find_review_capture_hygiene_findings(
            REPO_ROOT,
            tracked_paths,
            "tracked",
        )
        == []
    )
```

- [ ] **Step 10: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "review_artifact or review_capture"
```

Expected before implementation: rejection tests fail because the release-hygiene
script does not yet scan review artifacts for capture hygiene.

## Task 2: Implement Review Capture Hygiene Scanner

**Files:**

- Modify: `scripts/check_release_hygiene.py`

- [ ] **Step 1: Add constants and patterns**

Add near the existing regex constants:

```python
REVIEW_CAPTURE_MIN_STAGE = 159
REVIEW_CAPTURE_ARTIFACT_PATTERN = re.compile(
    r"^docs/reviews/"
    r"opencode-stage-(?P<stage>[0-9]+)-"
    r"(?:plan|code|release)-(?:review|rereview(?:-[0-9]+)?)\.md$"
)
ANSI_ESCAPE_PATTERN = re.compile(
    r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\)|.)"
)
REVIEW_CAPTURE_TOOL_STATUS_PREFIXES = (
    "Review written to ",
    "Wrote ",
)
REVIEW_CAPTURE_PROCESS_PREFIXES = (
    "I'll ",
    "I will ",
    "Let me ",
    "Now let me ",
)
```

- [ ] **Step 2: Wire scanner into `collect_findings(...)`**

Update `collect_findings(...)` after the existing secret checks:

```python
    findings.extend(find_secret_findings(repo_root, tracked_paths, "tracked"))
    findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
    findings.extend(find_review_capture_hygiene_findings(repo_root, tracked_paths, "tracked"))
    findings.extend(find_review_capture_hygiene_findings(repo_root, untracked_paths, "untracked"))
    findings.extend(find_remote_credential_findings(repo_root))
```

- [ ] **Step 3: Add the scanner helpers**

Add before `find_remote_credential_findings(...)`:

```python
def find_review_capture_hygiene_findings(
    repo_root: Path,
    paths: list[str],
    path_status: str,
) -> list[str]:
    findings = []
    for path in paths:
        normalized = normalize_git_path(path)
        if not normalized or not is_review_capture_artifact_path(normalized):
            continue

        file_path = safe_repo_path(repo_root, normalized)
        if file_path is None or file_path.is_symlink() or not file_path.is_file():
            continue

        text = read_text_if_not_binary(file_path)
        if text is None:
            continue

        findings.extend(
            review_capture_text_findings(
                normalized,
                text,
                path_status,
            )
        )
    return findings


def is_review_capture_artifact_path(path: str) -> bool:
    match = REVIEW_CAPTURE_ARTIFACT_PATTERN.fullmatch(path.lower())
    if match is None:
        return False
    return int(match.group("stage")) >= REVIEW_CAPTURE_MIN_STAGE


def review_capture_text_findings(
    path: str,
    text: str,
    path_status: str,
) -> list[str]:
    prefix = f"forbidden review capture artifact in {path_status} file: {path}"
    if not text.strip():
        return [f"{prefix}: empty output"]

    findings = []
    first_nonblank: tuple[int, str] | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and first_nonblank is None:
            first_nonblank = (line_number, stripped)
        if ANSI_ESCAPE_PATTERN.search(line):
            findings.append(f"{prefix}:{line_number}: ANSI escape sequence")
        if is_review_tool_status_line(stripped):
            findings.append(f"{prefix}:{line_number}: tool-status line")
        if has_review_tool_ui_marker(line):
            findings.append(f"{prefix}:{line_number}: tool UI marker")

    if first_nonblank is not None:
        line_number, stripped = first_nonblank
        if is_review_process_chatter_start(stripped):
            findings.append(f"{prefix}:{line_number}: process chatter at start")

    return findings


def is_review_tool_status_line(line: str) -> bool:
    return (
        line == "Review complete"
        or line.startswith(("Review complete.", "Review complete:"))
        or any(line.startswith(prefix) for prefix in REVIEW_CAPTURE_TOOL_STATUS_PREFIXES)
    )


def has_review_tool_ui_marker(line: str) -> bool:
    stripped = line.lstrip()
    return (
        stripped.startswith(("\u2192", "\u2731"))
        or stripped.startswith("build \u00b7")
    )


def is_review_process_chatter_start(line: str) -> bool:
    return any(line.startswith(prefix) for prefix in REVIEW_CAPTURE_PROCESS_PREFIXES)
```

- [ ] **Step 4: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q -k "review_artifact or review_capture"
```

Expected after implementation: all selected tests pass.

- [ ] **Step 5: Run the full release-hygiene module**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: tests pass and the current repository passes release hygiene.

## Task 3: Local Code Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-159-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-159-code-review.md`
- Add after release review: `docs/reviews/opencode-stage-159-release-review-prompt.md`
- Add after release review: `docs/reviews/opencode-stage-159-release-review.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-159-code-review-prompt.md` with:

```markdown
# Stage 159 Code Review Prompt

Review the Stage 159 implementation for Fashion Radar.

Changed files:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/superpowers/specs/2026-06-23-stage-159-review-artifact-hygiene-gate-design.md`
- `docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md`
- `docs/reviews/opencode-stage-159-plan-review-prompt.md`
- `docs/reviews/opencode-stage-159-plan-review.md`

Objective:

Add an automated release-hygiene guard for Stage 159+ completed review capture
artifacts under `docs/reviews/`.

Review questions:

1. Does the scanner correctly inspect only completed Stage 159+ review output
   artifacts and ignore prompt files plus Stage 158 legacy files?
2. Are the blocked markers narrow enough to avoid likely false positives while
   catching live-capture/tool-output mistakes?
3. Do the tests prove tracked and untracked review artifacts are covered?
4. Does the change preserve product scope boundaries, with no runtime/social
   collection, scheduling, scraping, platform API, or compliance-review product
   behavior?
5. Are there any critical or important findings that must be fixed before
   commit?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
```

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-159-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-159-code-review.md
rm -f "$tmp_review"
```

Expected: review output contains no critical or important findings. If it does,
fix them and request rereview.

- [ ] **Step 3: Run the full release gate**

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

Expected: pytest, smoke, ruff, format, lock, whitespace, secret, and extraheader
checks all pass. The token grep should not report committed token text.

- [ ] **Step 4: Run local opencode release review**

Create `docs/reviews/opencode-stage-159-release-review-prompt.md` with:

```markdown
# Stage 159 Release Review Prompt

Review the Stage 159 final working tree for Fashion Radar before GitHub upload.

Scope:

- Review artifact hygiene scanner in `scripts/check_release_hygiene.py`.
- Tests in `tests/test_release_hygiene.py`.
- Stage 159 spec, plan, plan review, code review, and release-review prompt.

Verification already run:

- Full pytest.
- First-run smoke.
- Release hygiene script.
- Ruff check and format check.
- Lock check.
- Whitespace, token, and persistent extraheader checks.

Review questions:

1. Are there any critical or important issues in the Stage 159 code, tests, or
   review artifacts?
2. Are the review artifacts clean completed review bodies with no live-capture
   stubs, tool-status lines, ANSI output, duplicated/truncated output, or empty
   output?
3. Is the change still process-only with no product/runtime/social collection,
   scraping, platform API, scheduling, monitoring, or compliance-review product
   behavior?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
```

Then run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-159-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-159-release-review.md
rm -f "$tmp_review"
```

Expected: release review output contains no critical or important findings. If
it does, fix them and request rereview.

- [ ] **Step 5: Re-run release hygiene after release review**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: the release-review artifact also passes the new review-capture hygiene
scanner before commit.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add scripts/check_release_hygiene.py tests/test_release_hygiene.py \
  docs/superpowers/specs/2026-06-23-stage-159-review-artifact-hygiene-gate-design.md \
  docs/superpowers/plans/2026-06-23-stage-159-review-artifact-hygiene-gate-plan.md \
  docs/reviews/opencode-stage-159-plan-review-prompt.md \
  docs/reviews/opencode-stage-159-plan-review.md \
  docs/reviews/opencode-stage-159-code-review-prompt.md \
  docs/reviews/opencode-stage-159-code-review.md \
  docs/reviews/opencode-stage-159-release-review-prompt.md \
  docs/reviews/opencode-stage-159-release-review.md
git commit -m "chore: guard review capture artifacts"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

Expected: commit succeeds and push updates `origin/main`.

## Self-Review Notes

- Spec coverage: the plan covers review-artifact path scope, Stage 159 floor,
  prompt exclusion, tracked and untracked files, tests, code review, and release
  gate.
- Placeholder scan: no `TBD`, `TODO`, or unspecified test/code steps remain.
- Type consistency: helper names in tests match helper names in the planned
  implementation.
