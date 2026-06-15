# Community Handoff Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Stage 53 test and documentation guardrails that freeze community handoff prohibited-field lint behavior, producer recommended command semantics, docs command-order drift, and `community-candidates-dir` parser rejection.

**Architecture:** This is a test/docs-only guardrail stage. Existing production modules remain the source of truth; tests import constants/builders and verify public contracts without introducing platform connectors or runtime side effects.

**Tech Stack:** Python 3.11+, pytest, Typer `CliRunner`, existing Fashion Radar CLI/docs helpers, Ruff. No new dependencies.

---

## File Structure

- Modify `tests/test_community_signal_lint.py`
  - Add parameterized prohibited-field coverage for CSV and JSON row envelopes.
  - Add CSV/JSON trap tests that document envelope behavior.
- Modify `tests/test_community_signal_profile.py`
  - Add `shlex`-based assertions over `recommended_commands`.
- Modify `tests/test_cli_docs.py`
  - Add a docs drift test for community import command-name order.
- Modify `tests/test_cli.py`
  - Add `community-candidates-dir --format xml` parser rejection coverage.
- Modify `docs/community-signal-import.md`
  - Clarify exact profile command sequence versus prose examples.
- Modify `CHANGELOG.md`
  - Add a Stage 53 guardrail bullet.
- Add review records under `docs/reviews/`.

### Task 1: Lint Prohibited Field Guardrails

**Files:**
- Modify: `tests/test_community_signal_lint.py`

- [ ] **Step 1: Add imports for parameterization and constants**

At the top of `tests/test_community_signal_lint.py`, add `import pytest` and import
`PROHIBITED_COMMUNITY_SIGNAL_FIELDS` from `fashion_radar.community_signals`:

```python
import json
from pathlib import Path
from textwrap import dedent

import pytest

from fashion_radar.community_signals import (
    CommunitySignalFindingSeverity,
    PROHIBITED_COMMUNITY_SIGNAL_FIELDS,
    lint_community_signal_directory,
    lint_community_signal_file,
    render_community_signal_directory_lint_table,
    render_community_signal_lint_table,
)
```

- [ ] **Step 2: Add a raw-row helper and prohibited-field parameterized test**

Add this helper and test after `test_unknown_and_prohibited_csv_fields_are_errors`:

```python
def _valid_community_signal_row() -> dict[str, str]:
    return {
        "url": "https://example.com/a",
        "title": "Signal",
        "published_at": "2026-06-12T08:00:00Z",
        "summary": "Sanitized note",
        "source_name": "Community Tool Export",
        "platform": "community",
        "source_weight": "1.0",
        "collected_at": "2026-06-12T08:30:00Z",
    }


@pytest.mark.parametrize("field", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
@pytest.mark.parametrize(
    ("case_name", "input_format", "expected_row"),
    [
        ("csv", "csv", 2),
        ("json_array", "json", 1),
        ("json_items", "json", 1),
    ],
)
def test_all_prohibited_fields_are_lint_errors_for_supported_raw_rows(
    tmp_path: Path,
    field: str,
    case_name: str,
    input_format: str,
    expected_row: int,
) -> None:
    base = _valid_community_signal_row()
    if case_name == "csv":
        path = tmp_path / f"{field}.csv"
        path.write_text(
            ",".join([*base, field])
            + "\n"
            + ",".join([*base.values(), "redacted"])
            + "\n",
            encoding="utf-8",
        )
    else:
        path = tmp_path / f"{field}.json"
        row = {**base, field: "redacted"}
        payload = [row] if case_name == "json_array" else {"items": [row]}
        path.write_text(json.dumps(payload), encoding="utf-8")

    result = lint_community_signal_file(path, input_format=input_format)

    prohibited = findings_by_code(result, "prohibited_field")
    assert result.error_count == 1
    assert result.warning_count == 0
    assert result.valid_row_count == 1
    assert [(finding.row, finding.field, finding.severity) for finding in prohibited] == [
        (expected_row, field, CommunitySignalFindingSeverity.ERROR)
    ]
```

- [ ] **Step 3: Add CSV and JSON trap tests**

Add these tests near the existing CSV extra-cells and JSON envelope tests:

```python
@pytest.mark.parametrize("extra_cell", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
def test_csv_extra_cell_values_are_not_treated_as_raw_field_names(
    tmp_path: Path,
    extra_cell: str,
) -> None:
    path = write_text(
        tmp_path / "signals.csv",
        f"""
        url,title,published_at,summary,source_name,platform,source_weight,collected_at
        https://example.com/a,Signal,2026-06-12T08:00:00Z,Note,Tool,community,1.0,2026-06-12T08:30:00Z,{extra_cell}
        """,
    )

    result = lint_community_signal_file(path, input_format="csv")

    assert [finding.code for finding in result.findings] == ["csv_extra_cells"]
    assert findings_by_code(result, "prohibited_field") == []


@pytest.mark.parametrize("field", sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS))
def test_json_top_level_prohibited_keys_are_invalid_file_not_raw_field_findings(
    tmp_path: Path,
    field: str,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "url": "https://example.com/a",
                        "title": "Signal",
                        "published_at": "2026-06-12T08:00:00Z",
                    }
                ],
                field: "redacted",
            }
        ),
        encoding="utf-8",
    )

    result = lint_community_signal_file(path, input_format="json")

    assert [finding.code for finding in result.findings] == ["invalid_file"]
    assert findings_by_code(result, "prohibited_field") == []
```

- [ ] **Step 4: Run targeted lint tests**

Run:

```bash
uv run pytest tests/test_community_signal_lint.py -q
```

Expected: all tests in the file pass.

### Task 2: Producer Profile Recommended Command Guardrails

**Files:**
- Modify: `tests/test_community_signal_profile.py`

- [ ] **Step 1: Add `shlex` import**

At the top of `tests/test_community_signal_profile.py`, add:

```python
import shlex
```

- [ ] **Step 2: Add recommended command sequence test**

Add this test after `test_profile_has_stable_json_key_order`:

```python
def test_profile_recommended_commands_keep_directory_handoff_sequence() -> None:
    commands = build_community_signal_profile().recommended_commands
    parsed = [shlex.split(command) for command in commands]

    assert [parts[:2] for parts in parsed] == [
        ["fashion-radar", "community-signal-lint-dir"],
        ["fashion-radar", "community-candidates-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "imported-review-workflow"],
    ]
    assert all("./exports" in parts for parts in parsed[:4])
    assert "--strict" in parsed[0]
    assert "--config-dir" in parsed[1]
    assert "--as-of" in parsed[1]
    assert "--dry-run" in parsed[2]
    assert "--imported-at" not in parsed[2]
    assert "--dry-run" not in parsed[3]
    assert "--imported-at" in parsed[3]
    assert "--data-dir" in parsed[4]
    source_name_values = [
        parts[parts.index("--source-name") + 1]
        for parts in parsed
        if "--source-name" in parts
    ]
    assert source_name_values == ["Community Tool Export"] * 5
```

- [ ] **Step 3: Run targeted profile tests**

Run:

```bash
uv run pytest tests/test_community_signal_profile.py -q
```

Expected: all tests in the file pass.

### Task 3: CLI And Documentation Drift Guardrails

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `docs/community-signal-import.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add `community-candidates-dir` invalid output-format parser test**

Add this test after
`test_community_candidates_dir_invalid_input_format_does_not_enter_command_body`:

```python
def test_community_candidates_dir_invalid_output_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, directory = _prepare_community_candidates_dir_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("directory should not be loaded")

    monkeypatch.setattr(cli_module, "load_scoring_config", fail_load_config)
    monkeypatch.setattr(cli_module, "load_entity_config", fail_load_config)
    monkeypatch.setattr(
        cli_module,
        "preview_community_candidate_directory",
        fail_preview,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(directory),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output
```

- [ ] **Step 2: Add docs command-order drift test**

Add imports to `tests/test_cli_docs.py`:

```python
from fashion_radar.community_signal_profile import build_community_signal_profile
```

Add this test after `test_community_import_docs_keep_deterministic_review_commands_fixed`:

```python
def test_community_signal_import_doc_keeps_profile_recommended_command_order() -> None:
    profile_command_names = [
        FASHION_RADAR_COMMAND_RE.search(command).group("name")
        for command in build_community_signal_profile().recommended_commands
    ]
    documented_names = [
        FASHION_RADAR_COMMAND_RE.search(command).group("name")
        for command in _fashion_radar_commands(ROOT / "docs" / "community-signal-import.md")
        if FASHION_RADAR_COMMAND_RE.search(command).group("name") in profile_command_names
    ]

    position = 0
    for expected in profile_command_names:
        while position < len(documented_names) and documented_names[position] != expected:
            position += 1
        assert position < len(documented_names), (
            f"{expected!r} from profile recommended_commands is missing or out of order"
        )
        position += 1
```

- [ ] **Step 3: Clarify producer profile documentation**

In `docs/community-signal-import.md`, update the producer profile paragraph to
include:

```markdown
The JSON profile's `recommended_commands` list is the exact producer-facing
sequence. Prose examples in this guide may add `uv run` and temporary paths for
source-checkout smoke tests, but they should preserve the same lint, preview,
dry-run import, import, and review order.
```

- [ ] **Step 4: Add changelog bullet**

In `CHANGELOG.md`, add a bullet under `Unreleased`:

```markdown
- Added Stage 53 guardrail tests for community prohibited-field lint coverage,
  producer profile recommended command order, documentation drift, and
  `community-candidates-dir` invalid output-format parsing.
```

- [ ] **Step 5: Run targeted CLI/docs tests**

Run:

```bash
uv run pytest tests/test_cli.py::test_community_candidates_dir_invalid_output_format_does_not_enter_command_body tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order -q
```

Expected: both tests pass.

### Task 4: Verification, Review, Commit, And Upload

**Files:**
- Add: `docs/reviews/claude-code-stage-53-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-53-release-review.md`
- Modify if needed: files changed by Tasks 1-3 only.

- [ ] **Step 1: Run targeted Stage 53 verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_profile.py tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_cli.py::test_community_candidates_dir_invalid_output_format_does_not_enter_command_body -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Expected: each command exits 0.

- [ ] **Step 3: Run release hygiene and smoke checks**

Run the existing release checks used in prior stages:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: each command exits 0.

- [ ] **Step 4: Request Claude Code release review**

Create `docs/reviews/claude-code-stage-53-release-review-prompt.md` with:

```markdown
Review Stage 53 community handoff guardrails in `/home/ubuntu/fashion-radar`.

Focus on:
- whether the changes are test/docs-only unless a real bug was found;
- whether prohibited-field lint coverage exercises every prohibited field for
  CSV and supported JSON row envelopes;
- whether producer profile recommended command assertions are useful without
  overfitting to prose docs;
- whether `community-candidates-dir --format xml` is rejected before command
  body work;
- whether documentation/changelog wording is accurate;
- whether no scraping, browser automation, login, cookies/sessions, platform
  APIs, monitoring, scheduling, media download, connector code, or compliance
  review feature was added.

Report Critical, Important, and Minor findings. Treat Critical/Important as
blocking.
```

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "$(cat docs/reviews/claude-code-stage-53-release-review-prompt.md)" > docs/reviews/claude-code-stage-53-release-review.md
```

Expected: no Critical or Important findings remain. If any are found, fix and
rerun review before committing.

- [ ] **Step 5: Commit and upload**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-16-stage-53-community-handoff-guardrails-design.md docs/superpowers/plans/2026-06-16-stage-53-community-handoff-guardrails-plan.md docs/reviews/claude-code-stage-53-plan-review-prompt.md docs/reviews/claude-code-stage-53-plan-review.md docs/reviews/claude-code-stage-53-plan-rereview-prompt.md docs/reviews/claude-code-stage-53-plan-rereview.md docs/reviews/claude-code-stage-53-release-review-prompt.md docs/reviews/claude-code-stage-53-release-review.md tests/test_community_signal_lint.py tests/test_community_signal_profile.py tests/test_cli_docs.py tests/test_cli.py docs/community-signal-import.md CHANGELOG.md
git commit -m "Add community handoff guardrails"
```

Upload to `origin/main`. If normal `git push` fails due TLS/network, use the
existing GitHub API upload path with the saved token file and align local
`main`/`origin/main` to the API-created commit only after verifying the remote
tree matches the local tree.

- [ ] **Step 6: Confirm GitHub Actions**

Use GitHub API or CLI to confirm the workflow run for the uploaded commit
completes successfully.

Expected: completed success.
