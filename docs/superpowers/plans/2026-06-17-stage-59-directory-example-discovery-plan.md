# Stage 59 Directory Example Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add machine-readable directory example paths to the producer profile and handoff manifest contracts.

**Architecture:** Extend the existing Pydantic contract models with a static `directory_example_paths` list. Keep all builders print-only/static and let existing CLI JSON/table rendering expose the new model fields naturally.

**Tech Stack:** Python 3.11+, Pydantic models, Typer CLI, pytest, ruff, checked-in JSON examples, Markdown docs.

---

## File Structure

Modify:

- `src/fashion_radar/community_signal_profile.py`
  - Add `COMMUNITY_SIGNAL_DIRECTORY_EXAMPLE_PATHS`.
  - Add `directory_example_paths` to `CommunitySignalProducerProfile`.
  - Populate and render the new field.
- `src/fashion_radar/community_handoff_manifest.py`
  - Add `directory_example_paths` to `CommunityHandoffManifest`.
  - Copy it from `build_community_signal_profile()`.
  - Render it in manifest table output.
- `examples/community-signal-profile.example.json`
  - Regenerate from `build_community_signal_profile().model_dump_json(indent=2)`.
- `tests/test_community_signal_profile.py`
  - Freeze the new field, key order, example JSON, and table output.
- `tests/test_community_handoff_manifest.py`
  - Freeze manifest key order, copied field value, and table output.
- `tests/test_cli.py`
  - Freeze CLI JSON/table output for profile and manifest.
- `tests/test_community_tool_handoff_directory_examples.py`
  - Prove profile-discoverable directory paths exist and still match the locked example layout.
- `tests/test_cli_docs.py`
  - Add docs drift coverage for `directory_example_paths`.
- `README.md`, `docs/community-signal-import.md`, `docs/community-signal-quality.md`,
  `docs/cli-reference.md`, `docs/source-boundaries.md`, `docs/architecture.md`,
  `docs/github-upload-checklist.md`, `CHANGELOG.md`
  - Describe the new machine-readable directory example pointer.

Do not modify:

- `community_handoff_workflow.py`
- `community_handoff_check.py`
- `uv.lock`
- `pyproject.toml`
- Database schema or migration files

Implementation split:

- Execute tasks sequentially: Task 1 profile, then Task 2 manifest/CLI, then
  Task 3 docs/guardrails.
- Do not run these implementation tasks in parallel. Task 2 copies the new
  profile field, and Task 3 calls both builders.
- It is still acceptable to use subagents, but dispatch only one code-editing
  worker at a time for this node.

---

### Task 1: Producer Profile Contract

**Files:**

- Modify: `src/fashion_radar/community_signal_profile.py`
- Modify: `tests/test_community_signal_profile.py`
- Modify: `examples/community-signal-profile.example.json`

- [ ] **Step 1: Write failing profile tests**

In `tests/test_community_signal_profile.py`, update
`test_profile_contract_matches_schema_csv_header_and_constants()` to expect:

```python
assert profile.directory_example_paths == [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]
```

Update `test_profile_has_stable_json_key_order()` to insert
`"directory_example_paths"` immediately after `"example_paths"`:

```python
assert list(payload) == [
    "contract_version",
    "execution_mode",
    "schema_path",
    "example_paths",
    "directory_example_paths",
    "supported_input_formats",
    "csv_header",
    "required_fields",
    "optional_fields",
    "allowed_fields",
    "prohibited_fields",
    "json_envelopes",
    "field_notes",
    "field_rules",
    "unsupported_capabilities",
    "recommended_commands",
    "boundaries",
]
```

Add a targeted existence/layout test:

```python
def test_profile_directory_example_paths_exist_without_replacing_single_file_examples() -> None:
    profile = build_community_signal_profile()

    assert profile.directory_example_paths == [
        "examples/community-tool-handoff-directory.example/README.md",
        "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
        "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
        "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
        "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
    ]
    assert all((ROOT / relative_path).is_file() for relative_path in profile.directory_example_paths)
    assert all(
        not relative_path.startswith("examples/community-tool-handoff-directory.example/")
        for relative_path in profile.example_paths
    )
```

Update `test_profile_table_includes_contract_commands_and_boundaries()`:

```python
assert "Directory example paths: examples/community-tool-handoff-directory.example/README.md" in text
```

- [ ] **Step 2: Run profile tests and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py -q
```

Expected: failures for missing `directory_example_paths` field and stale example JSON.

- [ ] **Step 3: Implement profile model field**

In `src/fashion_radar/community_signal_profile.py`, add:

```python
COMMUNITY_SIGNAL_DIRECTORY_EXAMPLE_PATHS = [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]
```

Add the model field immediately after `example_paths`:

```python
directory_example_paths: list[str]
```

Populate it in `build_community_signal_profile()` immediately after
`example_paths`:

```python
directory_example_paths=[*COMMUNITY_SIGNAL_DIRECTORY_EXAMPLE_PATHS],
```

Render it immediately after `Example paths`:

```python
f"Directory example paths: {', '.join(profile.directory_example_paths)}",
```

- [ ] **Step 4: Regenerate profile example JSON**

Use the repo model to regenerate the checked-in example:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python - <<'PY'
from pathlib import Path
from fashion_radar.community_signal_profile import build_community_signal_profile

Path("examples/community-signal-profile.example.json").write_text(
    build_community_signal_profile().model_dump_json(indent=2) + "\n",
    encoding="utf-8",
)
PY
```

- [ ] **Step 5: Verify profile tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_signal_profile.py tests/test_community_signal_profile.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_signal_profile.py tests/test_community_signal_profile.py
```

Expected: all pass.

---

### Task 2: Handoff Manifest Contract

**Files:**

- Modify: `src/fashion_radar/community_handoff_manifest.py`
- Modify: `tests/test_community_handoff_manifest.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing manifest and CLI tests**

In `tests/test_community_handoff_manifest.py`, insert
`"directory_example_paths"` immediately after `"example_paths"` in the stable
payload key assertion. Add:

```python
assert manifest.directory_example_paths == [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]
```

In the manual `CommunityHandoffManifest(...)` fixture for
`test_render_community_handoff_manifest_table_sanitizes_cells()`, add:

```python
directory_example_paths=[
    "examples/community-tool-handoff-directory.example/README.md",
],
```

And add the expected table line immediately after `Example paths`:

```python
"Directory example paths: examples/community-tool-handoff-directory.example/README.md",
```

Because that test asserts exact list equality, update the expected list itself
in lockstep, not just a separate substring assertion.

In `tests/test_cli.py`, update `test_community_signal_profile_prints_json()` and
`test_community_handoff_manifest_command_prints_json_with_stable_keys()` to
include the new key and expected list. Update profile/manifest table tests to
assert `"Directory example paths:"` appears.

- [ ] **Step 2: Run tests and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py tests/test_cli.py -q -k "community_signal_profile or community_handoff_manifest"
```

Expected: failures for missing manifest/profile CLI field.

- [ ] **Step 3: Implement manifest field**

In `src/fashion_radar/community_handoff_manifest.py`, add the field immediately
after `example_paths`:

```python
directory_example_paths: list[str]
```

Copy it from the profile in `build_community_handoff_manifest()` immediately
after `example_paths`:

```python
directory_example_paths=[*profile.directory_example_paths],
```

Render it immediately after `Example paths`:

```python
f"Directory example paths: {', '.join(manifest.directory_example_paths)}",
```

- [ ] **Step 4: Verify manifest and CLI tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_manifest.py tests/test_cli.py -q -k "community_signal_profile or community_handoff_manifest"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_handoff_manifest.py tests/test_community_handoff_manifest.py tests/test_cli.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_handoff_manifest.py tests/test_community_handoff_manifest.py tests/test_cli.py
```

Expected: all pass.

---

### Task 3: Directory Example Guardrail And Docs Drift

**Files:**

- Modify: `tests/test_community_tool_handoff_directory_examples.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add failing directory/example guardrail tests**

In `tests/test_community_tool_handoff_directory_examples.py`, import
`build_community_signal_profile` and add:

```python
from fashion_radar.community_signal_profile import build_community_signal_profile
```

Add:

```python
def test_profile_directory_example_paths_match_checked_in_directory_examples() -> None:
    profile = build_community_signal_profile()

    assert tuple(profile.directory_example_paths) == (
        "examples/community-tool-handoff-directory.example/README.md",
        "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
        "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
        "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
        "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
    )
    assert [ROOT / path for path in profile.directory_example_paths] == [
        EXAMPLE_ROOT / "README.md",
        CSV_DIRECTORY / "community-tool-a.csv",
        CSV_DIRECTORY / "community-tool-b.csv",
        JSON_DIRECTORY / "community-tool-a.json",
        JSON_DIRECTORY / "community-tool-b.json",
    ]
```

`tests/test_cli_docs.py` already imports `build_community_signal_profile` and
`build_community_handoff_manifest`. Add a docs drift test:

```python
def test_directory_example_paths_are_machine_readable_and_documented() -> None:
    profile = build_community_signal_profile()
    manifest = build_community_handoff_manifest(
        directory=Path("exports"),
        config_dir=Path("configs"),
        data_dir=Path("data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )

    assert profile.directory_example_paths == manifest.directory_example_paths

    field_docs = (
        README,
        ROOT / "docs" / "community-signal-import.md",
        ROOT / "docs" / "community-signal-quality.md",
        CLI_REFERENCE,
        SOURCE_BOUNDARIES_DOC,
        ARCHITECTURE_DOC,
        UPLOAD_CHECKLIST,
        CHANGELOG,
    )
    path_docs = (
        README,
        ROOT / "docs" / "community-signal-import.md",
        ROOT / "docs" / "community-signal-quality.md",
        CLI_REFERENCE,
        UPLOAD_CHECKLIST,
        CHANGELOG,
    )

    for path in field_docs:
        normalized = _normalized_doc_text(path).casefold()
        assert "directory_example_paths" in normalized

    for path in path_docs:
        normalized = _normalized_doc_text(path).casefold()
        for relative_path in profile.directory_example_paths:
            assert relative_path.casefold() in normalized
```

- [ ] **Step 2: Run docs/example tests and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py -q -k "directory_example or external_community_tool_directory"
```

Expected: failures until docs and model field are updated.

- [ ] **Step 3: Update docs**

Update docs with concise wording:

- `README.md`: say `community-signal-profile --format json` and
  `community-handoff-manifest --format json` now expose
  `directory_example_paths`.
- `docs/community-signal-import.md`: replace the existing sentence that says
  directory examples are documented separately from `example_paths` with a
  sentence that `directory_example_paths` carries those directory-layout
  pointers while `example_paths` remains single-file import examples.
- Manifest JSON excerpt in `docs/community-signal-import.md`: add
  `directory_example_paths` immediately after `example_paths`.
- `docs/community-signal-quality.md`, `docs/cli-reference.md`,
  `docs/source-boundaries.md`, `docs/architecture.md`,
  `docs/github-upload-checklist.md`, `CHANGELOG.md`: add the new field name and
  the five relative paths in the existing community-directory-example sections.

Do not claim that the profile or manifest reads directories or verifies the
examples at runtime.

- [ ] **Step 4: Verify docs/example tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py
```

Expected: all pass.

---

### Task 4: Verification, Review, Commit, Push

**Files:**

- Create: `docs/reviews/opencode-stage-59-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-59-plan-review.md`
- Create: `docs/reviews/opencode-stage-59-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-59-release-review.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py tests/test_cli.py -q -k "community_signal_profile or community_handoff_manifest or directory_example or external_community_tool_directory"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_signal_profile.py src/fashion_radar/community_handoff_manifest.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py tests/test_cli.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_signal_profile.py src/fashion_radar/community_handoff_manifest.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_community_tool_handoff_directory_examples.py tests/test_cli_docs.py tests/test_cli.py
git diff --check
```

- [ ] **Step 2: Run full release verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

- [ ] **Step 3: Installed-wheel smoke**

Build a wheel into a temp directory, install it into a temp venv with a mirror for
downloads only, then verify:

```bash
fashion-radar community-signal-profile --format json
fashion-radar community-handoff-manifest ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --data-dir ./data --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json
```

Expected JSON assertions:

```python
assert payload["directory_example_paths"] == [
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
]
```

- [ ] **Step 4: Run opencode release review**

Create `docs/reviews/opencode-stage-59-release-review-prompt.md` and run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-59-release-review-prompt.md)" \
  > docs/reviews/opencode-stage-59-release-review.md \
  2> /tmp/opencode-stage59-release-review.err
```

Fix any Critical or Important findings before proceeding.

- [ ] **Step 5: Commit and push**

Before commit:

```bash
if rg -q 'ghp_[A-Za-z0-9_]+' .; then exit 1; fi
git status --short
git diff --cached --check
```

Commit:

```bash
git add <stage-59-files>
git commit -m "Expose community directory example paths"
```

Push with the saved token through a temporary header only:

```bash
basic_auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)
git -c http.version=HTTP/1.1 -c http.extraHeader="AUTHORIZATION: basic $basic_auth" push origin main
```

Verify remote SHA and GitHub Actions success through the GitHub API.

- [ ] **Step 6: Handoff Summary**

Write a node-end summary with:

- Repo state
- Verified commands
- Uncommitted files
- Next step
