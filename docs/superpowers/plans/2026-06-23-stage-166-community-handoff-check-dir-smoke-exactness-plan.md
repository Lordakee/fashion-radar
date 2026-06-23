# Stage 166 Community Handoff Check Dir Smoke Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten the first-run smoke validator for `community-handoff-check-dir` JSON output so stable nested detail drift is caught.

**Architecture:** Add focused drift tests in `tests/test_first_run_smoke.py`, then add exact `assert_equal(...)` checks in `scripts/check_first_run_smoke.py`. Keep all product code under `src/` unchanged.

**Tech Stack:** Python standard library, pytest, existing first-run smoke script, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_first_run_smoke.py`
  - Add `community-handoff-check-dir` top-level detail drift coverage.
  - Add nested identity/path drift coverage.
  - Add lint field-count and source/platform count drift coverage.
  - Add candidate-preview nested detail drift coverage.
  - Add import-dry-run source/platform count drift coverage.
- Modify: `scripts/check_first_run_smoke.py`
  - Extend `validate_community_handoff_check_dir(...)` with exact assertions
    for the fields covered by the tests.
- Add: `docs/superpowers/specs/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-plan.md`
- Add: `docs/reviews/opencode-stage-166-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-166-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-166-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-166-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-166-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-166-release-review.md`

## Task 1: Add RED Drift Tests For Unpinned Stable Details

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Extend top-level drift coverage**

In `tests/test_first_run_smoke.py`, extend the parameter list in
`test_validate_community_handoff_check_dir_rejects_top_level_drift(...)` by
adding this tuple:

```python
        ("findings", [{"code": "unexpected"}], "findings"),
```

The full parameter list should include:

```python
    [
        ("execution_mode", "write_enabled", "execution_mode"),
        ("ok", False, "ok"),
        ("failed_check_count", 1, "failed_check_count"),
        ("warning_count", 1, "warning_count"),
        ("strict", False, "strict"),
        ("findings", [{"code": "unexpected"}], "findings"),
    ],
```

- [ ] **Step 2: Add nested identity/path drift test**

Add after `test_validate_community_handoff_check_dir_rejects_nested_count_drift(...)`:

```python
@pytest.mark.parametrize(
    ("section", "field", "value", "match"),
    [
        ("community_signal_lint", "directory", "/tmp/other-export", "lint directory"),
        ("community_signal_lint", "input_format", "json", "lint input_format"),
        ("community_signal_lint", "pattern", "*.json", "lint pattern"),
        ("import_dry_run", "directory", "/tmp/other-export", "import dry-run directory"),
        ("import_dry_run", "input_format", "json", "import dry-run input_format"),
        ("import_dry_run", "pattern", "*.json", "import dry-run pattern"),
    ],
)
def test_validate_community_handoff_check_dir_rejects_nested_identity_drift(
    section: str,
    field: str,
    value: object,
    match: str,
) -> None:
    payload = community_handoff_check_dir_payload()
    nested = payload[section]
    assert isinstance(nested, dict)
    nested[field] = value

    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)
```

- [ ] **Step 3: Add nested source/platform count drift test**

Add:

```python
@pytest.mark.parametrize(
    ("section", "field", "value", "match"),
    [
        (
            "community_signal_lint",
            "source_name_counts",
            {"Other Source": 2},
            "lint source_name_counts",
        ),
        ("community_signal_lint", "platform_counts", {"other": 2}, "lint platform_counts"),
        (
            "import_dry_run",
            "source_name_counts",
            {"Other Source": 2},
            "import dry-run source_name_counts",
        ),
        ("import_dry_run", "platform_counts", {"other": 2}, "import dry-run platform_counts"),
    ],
)
def test_validate_community_handoff_check_dir_rejects_nested_source_platform_count_drift(
    section: str,
    field: str,
    value: object,
    match: str,
) -> None:
    payload = community_handoff_check_dir_payload()
    nested = payload[section]
    assert isinstance(nested, dict)
    nested[field] = value

    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)
```

- [ ] **Step 4: Add lint field-count drift test**

Add:

```python
def test_validate_community_handoff_check_dir_rejects_lint_field_count_drift() -> None:
    payload = community_handoff_check_dir_payload()
    lint = payload["community_signal_lint"]
    assert isinstance(lint, dict)
    field_counts = lint["field_counts"]
    assert isinstance(field_counts, dict)
    field_counts["url"] = 1

    with pytest.raises(smoke.SmokeError, match="lint field_counts"):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)
```

- [ ] **Step 5: Add candidate-preview metadata drift test**

Add:

```python
@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("source_name", "Other Source", "candidate_preview source_name"),
        ("as_of", "2026-06-14T12:00:00+00:00", "candidate_preview as_of"),
        ("file_count", 2, "candidate_preview file_count"),
        ("limit", 99, "candidate_preview limit"),
        ("candidates", [{"name": "Unexpected"}], "candidate_preview candidates"),
    ],
)
def test_validate_community_handoff_check_dir_rejects_candidate_preview_detail_drift(
    field: str,
    value: object,
    match: str,
) -> None:
    payload = community_handoff_check_dir_payload()
    candidate_preview = payload["candidate_preview"]
    assert isinstance(candidate_preview, dict)
    candidate_preview[field] = value

    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)
```

- [ ] **Step 6: Run RED check**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"
```

Expected before implementation: the newly added drift cases fail because
`validate_community_handoff_check_dir(...)` does not yet assert the changed
fields. Existing cases should continue to pass.

## Task 2: Pin Community Handoff Check Dir Nested Details

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Pin top-level findings**

In `validate_community_handoff_check_dir(...)`, after:

```python
    assert_equal(f"{command_name} failed_check_count", payload.get("failed_check_count"), 0)
    assert_equal(f"{command_name} warning_count", payload.get("warning_count"), 0)
```

add:

```python
    assert_equal(f"{command_name} findings", payload.get("findings"), [])
```

- [ ] **Step 2: Pin community-signal lint identity and provenance details**

In the `community_signal_lint` section, after the existing `warning_count`
assertion, add:

```python
    assert_equal(f"{command_name} lint directory", lint.get("directory"), expected_directory)
    assert_equal(f"{command_name} lint input_format", lint.get("input_format"), "csv")
    assert_equal(f"{command_name} lint pattern", lint.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} lint info_count", lint.get("info_count"), 0)
    assert_equal(
        f"{command_name} lint field_counts",
        lint.get("field_counts"),
        {field: len(EXPECTED_SAMPLE_ROWS) for field in EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS},
    )
    assert_equal(
        f"{command_name} lint source_name_counts",
        lint.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} lint platform_counts",
        lint.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
```

- [ ] **Step 3: Pin candidate-preview metadata and empty candidates**

In the `candidate_preview` section, after the existing `row_count` assertion,
add:

```python
    assert_equal(
        f"{command_name} candidate_preview input_format",
        candidate_preview.get("input_format"),
        "csv",
    )
    assert_equal(
        f"{command_name} candidate_preview as_of",
        candidate_preview.get("as_of"),
        "2026-06-13T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview current_window_start",
        candidate_preview.get("current_window_start"),
        "2026-06-06T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview baseline_window_start",
        candidate_preview.get("baseline_window_start"),
        "2026-05-07T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview current_days",
        candidate_preview.get("current_days"),
        7,
    )
    assert_equal(
        f"{command_name} candidate_preview baseline_days",
        candidate_preview.get("baseline_days"),
        30,
    )
    assert_equal(
        f"{command_name} candidate_preview source_name",
        candidate_preview.get("source_name"),
        SOURCE_NAME,
    )
    assert_equal(
        f"{command_name} candidate_preview file_count",
        candidate_preview.get("file_count"),
        1,
    )
    assert_equal(
        f"{command_name} candidate_preview limit",
        candidate_preview.get("limit"),
        50,
    )
    assert_equal(
        f"{command_name} candidate_preview candidates",
        candidate_preview.get("candidates"),
        [],
    )
```

- [ ] **Step 4: Pin import dry-run metadata and provenance maps**

In the `import_dry_run` section, after the existing `error_count` assertion,
add:

```python
    assert_equal(
        f"{command_name} import dry-run directory",
        import_dry_run.get("directory"),
        expected_directory,
    )
    assert_equal(
        f"{command_name} import dry-run input_format",
        import_dry_run.get("input_format"),
        "csv",
    )
    assert_equal(
        f"{command_name} import dry-run pattern",
        import_dry_run.get("pattern"),
        DIR_PATTERN,
    )
    assert_equal(
        f"{command_name} import dry-run source_name_counts",
        import_dry_run.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} import dry-run platform_counts",
        import_dry_run.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
```

Do not add exact assertions for nested `files` or nested `findings` lists in
this stage.

- [ ] **Step 5: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-166-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-166-code-review.md`
- Add: `docs/reviews/opencode-stage-166-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-166-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-166-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-design.md`
- `docs/superpowers/plans/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

The prompt must require the response to start with:

```text
# Stage 166 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-166-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-166-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Fix
any critical or important findings before continuing.

- [ ] **Step 3: Run release gate**

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

Expected: all commands pass; token and extraheader checks report no secrets.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-166-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 166 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for prior stages, copying the completed review
to `docs/reviews/opencode-stage-166-release-review.md`.

Expected: completed review output with no critical or important findings.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-design.md \
  docs/superpowers/plans/2026-06-23-stage-166-community-handoff-check-dir-smoke-exactness-plan.md \
  docs/reviews/opencode-stage-166-plan-review-prompt.md \
  docs/reviews/opencode-stage-166-plan-review.md \
  docs/reviews/opencode-stage-166-code-review-prompt.md \
  docs/reviews/opencode-stage-166-code-review.md \
  docs/reviews/opencode-stage-166-release-review-prompt.md \
  docs/reviews/opencode-stage-166-release-review.md
git commit -m "test: harden community handoff check smoke"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.
