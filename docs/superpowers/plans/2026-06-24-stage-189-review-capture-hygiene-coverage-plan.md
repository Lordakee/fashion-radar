# Stage 189 Review Capture Hygiene Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make release hygiene scan non-stage local opencode review artifacts, reject timeout-stub review records, and clean the existing review archive.

**Architecture:** Keep the existing content-level review-capture checks, broaden the path predicate, and add timeout-stub detection. Add focused tests in `tests/test_release_hygiene.py`, update `scripts/check_release_hygiene.py`, clean the tracked `docs/reviews/opencode-full-project-review.md`, replace the Stage 188 timeout code-review artifact with completed scoped review output, add a Stage 188 release rereview, and document the broader review-record coverage in `docs/REVIEW_PROTOCOL.md`.

**Tech Stack:** Python standard library, pytest, Markdown docs, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Stage Boundary

This is a prerequisite maintenance node because the current review archive has
real Critical/Important follow-up gaps. It must not become another
external/community handoff-hardening loop. After this node is committed and
pushed, the next product node should be source liveness diagnostics for
configured public sources.

## Files

- Modify: `tests/test_release_hygiene.py`
- Modify: `scripts/check_release_hygiene.py`
- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `docs/reviews/opencode-stage-188-code-review.md`
- Modify: `docs/reviews/opencode-stage-188-release-review.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `CHANGELOG.md`
- Add: `docs/reviews/opencode-stage-188-release-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-188-release-rereview.md`
- Add after Stage 188 code review fixes: `docs/reviews/opencode-stage-188-code-rereview-prompt.md`
- Add after Stage 188 code review fixes: `docs/reviews/opencode-stage-188-code-rereview.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-189-review-capture-hygiene-coverage-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-189-review-capture-hygiene-coverage-plan.md`
- Add: `docs/reviews/opencode-stage-189-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-189-plan-review.md`
- Add after plan fix: `docs/reviews/opencode-stage-189-plan-rereview-prompt.md`
- Add after plan fix: `docs/reviews/opencode-stage-189-plan-rereview.md`
- Add after implementation: `docs/reviews/opencode-stage-189-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-189-code-review.md`
- Add after code-review fixes: `docs/reviews/opencode-stage-189-code-rereview-prompt.md`
- Add after code-review fixes: `docs/reviews/opencode-stage-189-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-189-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-189-release-review.md`

## Task 1: Add RED Release-Hygiene Coverage Tests

**Files:**

- Modify: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add a failing test for dirty non-stage opencode review records**

Add this test after
`test_stage_159_review_artifact_with_inline_arrow_prose_passes`:

```python
def test_non_stage_opencode_review_artifact_with_capture_noise_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-full-project-review.md",
        "I'll inspect the repository first.\n\n\x1b[32mApproved\x1b[0m\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-full-project-review.md:1: process chatter at start"
    ) in result.stderr
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-full-project-review.md:3: ANSI escape sequence"
    ) in result.stderr
```

- [ ] **Step 2: Add a failing test for staged timeout-stub review records**

Add this test immediately after the non-stage dirty-artifact test:

```python
def test_stage_159_review_artifact_with_timeout_stub_fails(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-stage-159-code-review.md",
        (
            "# Stage 159 Code Review\n\n"
            "opencode code review timed out after 600 seconds. "
            "No partial output was captured as approval.\n"
        ),
    )

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert (
        "forbidden review capture artifact in tracked file: "
        "docs/reviews/opencode-stage-159-code-review.md:3: timeout stub"
    ) in result.stderr
```

- [ ] **Step 3: Add a passing test for clean non-stage opencode review records**

Add this test immediately after the two RED tests:

```python
def test_non_stage_opencode_review_artifact_with_clean_body_passes(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(
        repo_root,
        "docs/reviews/opencode-full-project-review.md",
        "# Full Project Review\n\n## Critical\n\nNone.\n\n## Important\n\nNone.\n",
    )

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 4: Verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_release_hygiene.py::test_non_stage_opencode_review_artifact_with_capture_noise_fails \
  tests/test_release_hygiene.py::test_stage_159_review_artifact_with_timeout_stub_fails \
  tests/test_release_hygiene.py::test_non_stage_opencode_review_artifact_with_clean_body_passes \
  -q
```

Expected: the dirty non-stage artifact test fails because
`is_review_capture_artifact_path(...)` does not yet scan
`docs/reviews/opencode-full-project-review.md`, and the timeout-stub test fails
because timeout phrases are not yet recognized. The clean-body test may pass
because the non-stage path is still ignored; the RED proof is the dirty and
timeout fixtures.

## Task 2: Broaden Review Capture Detection

**Files:**

- Modify: `scripts/check_release_hygiene.py`
- Test: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add a non-stage opencode review path pattern**

Near `REVIEW_CAPTURE_ARTIFACT_PATTERN`, add:

```python
NON_STAGE_OPENCODE_REVIEW_ARTIFACT_PATTERN = re.compile(
    r"^docs/reviews/opencode-(?!stage-[0-9]+-).+\.md$"
)
```

- [ ] **Step 2: Update `is_review_capture_artifact_path`**

Replace the function body with:

```python
def is_review_capture_artifact_path(path: str) -> bool:
    lower_path = path.lower()
    match = REVIEW_CAPTURE_ARTIFACT_PATTERN.fullmatch(lower_path)
    if match is not None:
        return int(match.group("stage")) >= REVIEW_CAPTURE_MIN_STAGE
    if lower_path.endswith("-prompt.md"):
        return False
    return NON_STAGE_OPENCODE_REVIEW_ARTIFACT_PATTERN.fullmatch(lower_path) is not None
```

This keeps the Stage 158 legacy exclusion while scanning non-stage opencode
review records.

- [ ] **Step 3: Add narrow timeout-stub detection**

Near `REVIEW_CAPTURE_PROCESS_PREFIXES`, add:

```python
REVIEW_CAPTURE_TIMEOUT_STUB_PREFIXES = (
    "opencode plan review timed out",
    "opencode code review timed out",
    "opencode release review timed out",
)
```

Then add this helper near `is_review_process_chatter_start(...)`:

```python
def is_review_timeout_stub_line(line: str) -> bool:
    lower_line = line.lower()
    return any(
        lower_line.startswith(prefix)
        for prefix in REVIEW_CAPTURE_TIMEOUT_STUB_PREFIXES
    )
```

Finally, inside `review_capture_text_findings(...)`, after the tool UI marker
check, add:

```python
        if is_review_timeout_stub_line(stripped):
            findings.append(f"{prefix}:{line_number}: timeout stub")
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_release_hygiene.py::test_non_stage_opencode_review_artifact_with_capture_noise_fails \
  tests/test_release_hygiene.py::test_stage_159_review_artifact_with_timeout_stub_fails \
  tests/test_release_hygiene.py::test_non_stage_opencode_review_artifact_with_clean_body_passes \
  tests/test_release_hygiene.py::test_stage_158_legacy_review_artifact_is_not_rechecked \
  tests/test_release_hygiene.py::test_stage_159_review_artifact_prompt_with_tool_status_example_is_ignored \
  -q
```

Expected: all selected fixture tests pass. Ordinary review prose that mentions
request timeouts or historic review timeouts is not rejected unless the line
starts with one of the explicit opencode timeout-stub prefixes.

## Task 3: Clean The Current Review Archive

**Files:**

- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `docs/reviews/opencode-stage-188-code-review.md`
- Modify: `docs/reviews/opencode-stage-188-release-review.md`
- Add: `docs/reviews/opencode-stage-188-code-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-188-code-rereview.md`
- Add: `docs/reviews/opencode-stage-188-release-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-188-release-rereview.md`

- [ ] **Step 1: Replace raw full-project capture output with a clean review body**

Rewrite `docs/reviews/opencode-full-project-review.md` so it starts with:

```markdown
# Full Project Review
```

Keep the substantive findings from the original review:

- the proxy-sensitive test failure that Stage 188 later fixed;
- the effort drift into external/community handoff hardening;
- the documentation duplication concern;
- the source coverage, source-health, matching-quality, and optional-summary
  roadmap correction.

Remove raw command logs, ANSI escape sequences, tool UI markers, and process
chatter.

- [ ] **Step 2: Paraphrase the stale Stage 188 release-review timeout quote**

In `docs/reviews/opencode-stage-188-release-review.md`, change the I1 paragraph
so it no longer repeats the timeout-stub sentence verbatim. Keep the historical
finding intact, but describe the old code-review file as a timeout record plus
self-verification rather than quoting the exact stale status line.

- [ ] **Step 3: Create a scoped Stage 188 code-review prompt**

Create `/tmp/opencode-stage-188-code-review-refresh-prompt.md` with this body:

```text
Review Stage 188 after the already-committed fixes.

Repository: /home/ubuntu/fashion-radar

Files to inspect:
- tests/test_collectors_runner.py
- tests/test_workflows.py
- README.md
- docs/PROJECT_BRIEF.md
- docs/architecture.md
- docs/REVIEW_PROTOCOL.md
- CHANGELOG.md
- docs/superpowers/specs/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-design.md
- docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md
- docs/reviews/opencode-stage-188-plan-review.md

Questions:
1. Did Stage 188 resolve the proxy-sensitive injected collector/workflow tests without changing runtime proxy behavior?
2. Are the roadmap corrections scoped and consistent with the product direction?
3. Are there any Critical or Important issues in the Stage 188 code/docs changes?

Start the response exactly with:
# Stage 188 Code Review

Do not include process chatter, command logs, ANSI output, or tool-status lines.
```

- [ ] **Step 4: Run the scoped Stage 188 code review and replace the timeout stub**

Run:

```bash
tmp_review="$(mktemp)"
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat /tmp/opencode-stage-188-code-review-refresh-prompt.md)" > "$tmp_review" 2>&1
sed -n '/^# Stage 188 Code Review/,$p' "$tmp_review" > docs/reviews/opencode-stage-188-code-review.md
test -s docs/reviews/opencode-stage-188-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output, not a timeout record. If Critical or
Important findings appear, fix valid findings and continue with the code
rereview step.

- [ ] **Step 5: If the refreshed Stage 188 code review finds Critical or Important issues, fix them and add a code rereview**

If `docs/reviews/opencode-stage-188-code-review.md` reports Critical or
Important findings, fix the valid findings, then create
`docs/reviews/opencode-stage-188-code-rereview-prompt.md` and run a scoped
rereview into `docs/reviews/opencode-stage-188-code-rereview.md`. The rereview
must start with:

```text
# Stage 188 Code Rereview
```

Expected: no remaining Critical or Important findings.

- [ ] **Step 6: Add a Stage 188 release rereview prompt**

Create `docs/reviews/opencode-stage-188-release-rereview-prompt.md`:

```markdown
# Stage 188 Release Rereview Prompt

Review the current Stage 188 state after the earlier release-review blockers
were addressed.

Repository: `/home/ubuntu/fashion-radar`

Inspect:

- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-stage-188-code-review.md`
- `docs/reviews/opencode-stage-188-release-review.md`
- `docs/reviews/opencode-full-project-review.md`
- `tests/test_collectors_runner.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `docs/architecture.md`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`

Questions:

1. Are the Stage 188 proxy test-isolation changes correct and test-side only?
2. Are the Stage 188 review-chain blockers from the prior release review now
   closed?
3. Are there any remaining Critical or Important blockers to treating Stage 188
   as accepted in the repository history?

Start the response exactly with:

```text
# Stage 188 Release Rereview
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
```

- [ ] **Step 7: Run Stage 188 release rereview**

Run:

```bash
tmp_review="$(mktemp)"
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-188-release-rereview-prompt.md)" > "$tmp_review" 2>&1
sed -n '/^# Stage 188 Release Rereview/,$p' "$tmp_review" > docs/reviews/opencode-stage-188-release-rereview.md
test -s docs/reviews/opencode-stage-188-release-rereview.md
rm -f "$tmp_review"
```

Expected: completed rereview output that closes the old not-approved release
review state without rewriting that historical artifact.

- [ ] **Step 8: Verify the committed review archive is clean**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen pytest \
  tests/test_release_hygiene.py::test_current_repository_tracked_review_artifacts_have_no_capture_findings \
  -q
```

Expected: `Release hygiene checks passed.` and the current repository review
archive test passes.

## Task 4: Update Review Protocol And Changelog

**Files:**

- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Document broader review-capture coverage**

In `docs/REVIEW_PROTOCOL.md`, update the review capture hygiene paragraph so it
states that the rule applies to both staged opencode review artifacts and other
local opencode review records under `docs/reviews/`.

- [ ] **Step 2: Record Stage 189 in the changelog**

Under `## [Unreleased]` -> `### Fixed`, add:

```markdown
- Stage 189 broadens release-hygiene review-capture checks to non-stage
  opencode review records and timeout stubs, cleans the full-project review
  artifact, and adds completed Stage 188 follow-up review records.
```

## Task 5: Focused Verification And Local Code Review

**Files:**

- Add: `docs/reviews/opencode-stage-189-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-189-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -q
uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Expected: all commands exit 0.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-189-code-review-prompt.md` asking local
opencode to review only the Stage 189 changes, and require the output to start
with:

```text
# Stage 189 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-189-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '/^# Stage 189 Code Review/,$p' "$tmp_review" > docs/reviews/opencode-stage-189-code-review.md
if [ ! -s docs/reviews/opencode-stage-189-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-189-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings.

## Task 6: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-189-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-189-release-review.md`

- [ ] **Step 1: Run the release gate**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: test/check/lint/format/lock/diff commands exit 0. The secret scans
should print no matches.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-189-release-review-prompt.md`, then run:

```bash
tmp_review="$(mktemp)"
NO_COLOR=1 opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-189-release-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '/^# Stage 189 Release Review/,$p' "$tmp_review" > docs/reviews/opencode-stage-189-release-review.md
if [ ! -s docs/reviews/opencode-stage-189-release-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-189-release-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  scripts/check_release_hygiene.py \
  tests/test_release_hygiene.py \
  docs/reviews/opencode-full-project-review.md \
  docs/reviews/opencode-stage-188-code-review.md \
  docs/reviews/opencode-stage-188-code-rereview-prompt.md \
  docs/reviews/opencode-stage-188-code-rereview.md \
  docs/reviews/opencode-stage-188-release-review.md \
  docs/reviews/opencode-stage-188-release-rereview-prompt.md \
  docs/reviews/opencode-stage-188-release-rereview.md \
  docs/REVIEW_PROTOCOL.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-189-review-capture-hygiene-coverage-design.md \
  docs/superpowers/plans/2026-06-24-stage-189-review-capture-hygiene-coverage-plan.md \
  docs/reviews/opencode-stage-189-plan-review-prompt.md \
  docs/reviews/opencode-stage-189-plan-review.md \
  docs/reviews/opencode-stage-189-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-189-plan-rereview.md \
  docs/reviews/opencode-stage-189-code-review-prompt.md \
  docs/reviews/opencode-stage-189-code-review.md \
  docs/reviews/opencode-stage-189-code-rereview-prompt.md \
  docs/reviews/opencode-stage-189-code-rereview.md \
  docs/reviews/opencode-stage-189-release-review-prompt.md \
  docs/reviews/opencode-stage-189-release-review.md
git commit -m "fix: cover non-stage opencode review hygiene"
git push origin main
```

Expected: commit and push succeed.

## Self-Review

- Spec coverage: The tasks cover the release-hygiene blind spot, a clean current
  review artifact, docs, changelog, plan/code/release review, and release gate.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Type consistency: The new regex and function name match the current
  `scripts/check_release_hygiene.py` structure.
