# Stage 158 First-Run Community Handoff Check JSON Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate the direct `community-handoff-check-dir` JSON payload inside first-run smoke.

**Architecture:** Keep `scripts/check_first_run_smoke.py` as the integration smoke orchestrator. Add one focused validator for `community-handoff-check-dir` JSON and update the deterministic command-sequence test to require `--format json`.

**Tech Stack:** Python, pytest, Typer CLI JSON output, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_first_run_smoke.py`
  - Add `validate_community_handoff_check_dir(...)`.
  - Change the direct `community-handoff-check-dir` call in `run_first_run_flow()` to request JSON and validate it.
- Modify: `tests/test_first_run_smoke.py`
  - Add a deterministic `community_handoff_check_dir_payload(...)` helper.
  - Add focused validator tests.
  - Update `expected_first_run_flow_commands()` and fake stdout.
- Add: `docs/reviews/opencode-stage-158-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-158-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-158-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-158-code-review.md`

## Task 1: Add RED Tests For Handoff Check JSON Validation

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add a deterministic payload helper**

Add this helper near other payload helpers:

```python
def community_handoff_check_dir_payload(
    *,
    directory: str = "/tmp/export",
    config_dir: str = "configs",
) -> dict[str, object]:
    return {
        "directory": directory,
        "input_format": "csv",
        "pattern": smoke.DIR_PATTERN,
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": config_dir,
        "source_name": smoke.SOURCE_NAME,
        "execution_mode": "local_read_only",
        "strict": True,
        "limit": 50,
        "ok": True,
        "failed_check_count": 0,
        "warning_count": 0,
        "findings": [],
        "community_signal_lint": {
            "directory": directory,
            "input_format": "csv",
            "pattern": smoke.DIR_PATTERN,
            "file_count": 1,
            "row_count": 2,
            "valid_row_count": 2,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "field_counts": {
                "collected_at": 2,
                "platform": 2,
                "published_at": 2,
                "source_name": 2,
                "source_weight": 2,
                "summary": 2,
                "title": 2,
                "url": 2,
            },
            "source_name_counts": {smoke.SOURCE_NAME: 2},
            "platform_counts": {"community": 2},
            "files": [],
            "findings": [],
        },
        "candidate_preview": {
            "input_format": "csv",
            "as_of": "2026-06-13T12:00:00+00:00",
            "current_window_start": "2026-06-06T12:00:00+00:00",
            "baseline_window_start": "2026-05-07T12:00:00+00:00",
            "current_days": 7,
            "baseline_days": 30,
            "source_name": smoke.SOURCE_NAME,
            "file_count": 1,
            "row_count": 2,
            "candidate_count": 0,
            "limit": 50,
            "candidates": [],
        },
        "import_dry_run": {
            "directory": directory,
            "input_format": "csv",
            "pattern": smoke.DIR_PATTERN,
            "file_count": 1,
            "valid_file_count": 1,
            "row_count": 2,
            "source_name_counts": {smoke.SOURCE_NAME: 2},
            "platform_counts": {"community": 2},
            "error_count": 0,
            "files": [],
            "findings": [],
        },
    }
```

- [ ] **Step 2: Add acceptance and rejection tests**

Add tests near other community handoff validator tests:

```python
def test_validate_community_handoff_check_dir_accepts_first_run_payload() -> None:
    smoke.validate_community_handoff_check_dir(
        "community-handoff-check-dir",
        community_handoff_check_dir_payload(),
    )


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("execution_mode", "write_enabled", "execution_mode"),
        ("ok", False, "ok"),
        ("failed_check_count", 1, "failed_check_count"),
        ("warning_count", 1, "warning_count"),
        ("strict", False, "strict"),
    ],
)
def test_validate_community_handoff_check_dir_rejects_top_level_drift(
    field: str,
    value: object,
    match: str,
) -> None:
    payload = community_handoff_check_dir_payload()
    payload[field] = value

    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)


def test_validate_community_handoff_check_dir_rejects_nested_count_drift() -> None:
    payload = community_handoff_check_dir_payload()
    lint = payload["community_signal_lint"]
    assert isinstance(lint, dict)
    lint["row_count"] = 5

    with pytest.raises(smoke.SmokeError, match="lint row_count"):
        smoke.validate_community_handoff_check_dir("community-handoff-check-dir", payload)
```

Expected RED status before implementation: `AttributeError` because
`validate_community_handoff_check_dir` does not exist.

- [ ] **Step 3: Update the deterministic command sequence expectation**

Add `--format`, `"json"` to the `community-handoff-check-dir` tuple in
`expected_first_run_flow_commands()`:

```python
            "--strict",
            "--format",
            "json",
```

- [ ] **Step 4: Update fake stdout**

Add an entry in `stdout_by_command`:

```python
            "community-handoff-check-dir": json.dumps(
                community_handoff_check_dir_payload(
                    directory=str(context.exports_dir),
                    config_dir=str(context.config_dir),
                )
            ),
```

- [ ] **Step 5: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir or first_run_flow"
```

Expected: tests fail before implementation because the validator is missing and
the first-run command sequence lacks `--format json`.

## Task 2: Implement Community Handoff Check JSON Validation

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add the validator**

Add this function near `validate_community_candidates(...)` and related community
validators:

```python
def validate_community_handoff_check_dir(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "/tmp/export",
    expected_config_dir: str = "configs",
) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "local_read_only")
    assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "csv")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} strict", payload.get("strict"), True)
    assert_equal(f"{command_name} limit", payload.get("limit"), 50)
    assert_equal(f"{command_name} ok", payload.get("ok"), True)
    assert_equal(f"{command_name} failed_check_count", payload.get("failed_check_count"), 0)
    assert_equal(f"{command_name} warning_count", payload.get("warning_count"), 0)

    lint = payload.get("community_signal_lint")
    if not isinstance(lint, dict):
        raise SmokeError(f"{command_name} community_signal_lint must be a JSON object")
    assert_equal(f"{command_name} lint file_count", lint.get("file_count"), 1)
    assert_equal(f"{command_name} lint row_count", lint.get("row_count"), 2)
    assert_equal(f"{command_name} lint valid_row_count", lint.get("valid_row_count"), 2)
    assert_equal(f"{command_name} lint error_count", lint.get("error_count"), 0)
    assert_equal(f"{command_name} lint warning_count", lint.get("warning_count"), 0)

    candidate_preview = payload.get("candidate_preview")
    if not isinstance(candidate_preview, dict):
        raise SmokeError(f"{command_name} candidate_preview must be a JSON object")
    assert_equal(
        f"{command_name} candidate_preview candidate_count",
        candidate_preview.get("candidate_count"),
        0,
    )
    assert_equal(f"{command_name} candidate_preview row_count", candidate_preview.get("row_count"), 2)

    import_dry_run = payload.get("import_dry_run")
    if not isinstance(import_dry_run, dict):
        raise SmokeError(f"{command_name} import_dry_run must be a JSON object")
    assert_equal(f"{command_name} import dry-run file_count", import_dry_run.get("file_count"), 1)
    assert_equal(
        f"{command_name} import dry-run valid_file_count",
        import_dry_run.get("valid_file_count"),
        1,
    )
    assert_equal(f"{command_name} import dry-run row_count", import_dry_run.get("row_count"), 2)
    assert_equal(f"{command_name} import dry-run error_count", import_dry_run.get("error_count"), 0)
```

- [ ] **Step 2: Wire the validator into first-run smoke**

Replace the direct `run_cli(...)` handoff check call with:

```python
    community_handoff_check_dir = validate_json_output(
        "community-handoff-check-dir",
        run_cli(
            context,
            "community-handoff-check-dir",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--pattern",
            DIR_PATTERN,
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--strict",
            "--format",
            "json",
        ).stdout,
    )
    validate_community_handoff_check_dir(
        "community-handoff-check-dir",
        community_handoff_check_dir,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
    )
```

- [ ] **Step 3: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_check_dir or first_run_flow"
```

Expected: selected tests pass.

## Task 3: Verify Stage 158

**Files:**

- No code changes expected.

- [ ] **Step 1: Run full first-run smoke module**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run real first-run smoke**

Run:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected:

```text
First-run sample smoke passed.
```

- [ ] **Step 3: Run focused ruff**

Run:

```bash
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: both commands pass.

## Task 4: Code Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-158-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-158-code-review.md`

- [ ] **Step 1: Create the code review prompt**

Write `docs/reviews/opencode-stage-158-code-review-prompt.md` with this scope:

```text
Review Stage 158. Confirm first-run smoke now requests JSON from
community-handoff-check-dir, validates local_read_only/readiness/dry-run fields,
and does not add platform collection or write-capable directory import behavior.
```

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-158-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-158-code-review.md
rm -f "$tmp_review"
```

Expected: no critical or important findings. Fix any critical or important
findings before continuing.

- [ ] **Step 3: Run full release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected:

- Full pytest passes.
- First-run smoke prints `First-run sample smoke passed.`
- Ruff check and format check pass.
- Lock check passes.
- Diff, token, and header checks are clean.

## Task 5: Commit And Push

**Files:**

- Stage only Stage 158 implementation, tests, plan, and review artifacts.

- [ ] **Step 1: Stage exact files**

Run:

```bash
git add \
  scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-23-stage-158-first-run-community-handoff-check-json-design.md \
  docs/superpowers/plans/2026-06-23-stage-158-first-run-community-handoff-check-json-plan.md \
  docs/reviews/opencode-stage-158-plan-review-prompt.md \
  docs/reviews/opencode-stage-158-plan-review.md \
  docs/reviews/opencode-stage-158-code-review-prompt.md \
  docs/reviews/opencode-stage-158-code-review.md
```

- [ ] **Step 2: Commit**

Run:

```bash
git commit -m "test: validate handoff check smoke payload"
```

- [ ] **Step 3: Push**

Run:

```bash
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

- [ ] **Step 4: Confirm clean sync**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected: local branch clean and local HEAD matches remote `refs/heads/main`.

## Self-Review

- Spec coverage: JSON request, JSON validation, focused tests, real smoke, code
  review, release gate, and push are covered.
- Placeholder scan: No TODO/TBD placeholders remain.
- Type consistency: Function names and constants match the existing first-run
  smoke module.
