# Community Tool Directory Examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add checked-in external community tool export directory examples and guardrails so future user-controlled tools can copy a local CSV or JSON directory layout and run existing directory handoff commands.

**Architecture:** Keep existing schema and CLI behavior unchanged. Add static directory examples under `examples/`, test them through existing importer/linter/CLI directory commands, update docs and package checks, and add docs drift guards for the manifest example and directory links.

**Tech Stack:** Python 3.11+, pytest, Typer `CliRunner`, existing community signal importer/linter, existing package archive checker, Markdown docs. No new dependencies.

---

## File Structure

- Add `examples/community-tool-handoff-directory.example/README.md`
  - Producer-facing notes for the checked-in CSV/JSON export directories.
- Add `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
  - First one-row sanitized CSV directory handoff sample.
- Add `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
  - Second one-row sanitized CSV directory handoff sample.
- Add `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
  - First one-row sanitized JSON directory handoff sample.
- Add `examples/community-tool-handoff-directory.example/json/community-tool-b.json`
  - Second one-row sanitized JSON directory handoff sample.
- Add `tests/test_community_tool_handoff_directory_examples.py`
  - Focused tests for the checked-in directory samples.
- Modify `scripts/check_package_archives.py`
  - Require the new directory example files in sdists.
- Modify `tests/test_package_archives.py`
  - Mirror package requirements and add missing-file regressions.
- Modify `tests/test_cli_docs.py`
  - Add docs drift coverage for directory example links and manifest example paths.
- Modify docs:
  - `README.md`
  - `docs/community-signal-import.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Add review artifacts:
  - `docs/reviews/opencode-stage-55-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-55-plan-review.md`
  - `docs/reviews/opencode-stage-55-release-review-prompt.md`
  - `docs/reviews/opencode-stage-55-release-review.md`

### Task 1: Add Directory Example Files

**Files:**
- Create: `examples/community-tool-handoff-directory.example/README.md`
- Create: `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- Create: `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- Create: `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- Create: `examples/community-tool-handoff-directory.example/json/community-tool-b.json`

- [ ] **Step 1: Create the directory README**

Create `examples/community-tool-handoff-directory.example/README.md`:

```markdown
# Community Tool Handoff Directory Example

This directory shows a local export layout for a user-controlled external
community tool.

- Use `csv/*.csv` with `--input-format csv --pattern "*.csv"`.
- Use `json/*.json` with `--input-format json --pattern "*.json"`.

The `csv/` and `json/` directories are separate because Fashion Radar reads one
input format and one matched filename pattern per directory command. The
directory commands read matching regular files directly under the supplied
directory; they do not recurse into nested directories.

Do not save a `community-handoff-manifest --format json` output as a matched
handoff file inside `json/`. Save manifests outside the matched export
directory, or use an excluded filename or pattern.

These examples are sanitized local CSV/JSON handoff files only. They are not
platform collection and do not add connectors, scraping, browser automation,
platform APIs, monitoring, scheduling, source acquisition, demand proof,
ranking, or coverage verification.
```

- [ ] **Step 2: Create the first CSV directory sample**

Create `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`:

```csv
url,title,published_at,summary,source_name,platform,source_weight,collected_at
https://example.com/community-directory/the-row-sandal-signal,The Row sandal observed signal,2026-06-12T14:00:00Z,Synthetic sanitized observation about The Row sandal interest from a user-controlled tool,External Community Tool,community,1.2,2026-06-12T14:15:00Z
```

- [ ] **Step 3: Create the second CSV directory sample**

Create `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`:

```csv
url,title,published_at,summary,source_name,platform,source_weight,collected_at
https://example.com/community-directory/mesh-flat-signal,Mesh flat observed signal,2026-06-12T15:00:00Z,Synthetic sanitized observation about mesh flat styling from a user-controlled tool,External Community Tool,community,1.1,2026-06-12T15:10:00Z
```

- [ ] **Step 4: Create the first JSON directory sample**

Create `examples/community-tool-handoff-directory.example/json/community-tool-a.json`:

```json
{
  "items": [
    {
      "url": "https://example.com/community-directory/slim-sneaker-signal",
      "title": "Slim sneaker observed signal",
      "published_at": "2026-06-12T16:00:00Z",
      "summary": "Synthetic sanitized observation about slim sneaker interest from a user-controlled tool.",
      "source_name": "External Community Tool",
      "platform": "community",
      "source_weight": 1.2,
      "collected_at": "2026-06-12T16:10:00Z"
    }
  ]
}
```

- [ ] **Step 5: Create the second JSON directory sample**

Create `examples/community-tool-handoff-directory.example/json/community-tool-b.json`:

```json
{
  "items": [
    {
      "url": "https://example.com/community-directory/soft-shoulder-bag-signal",
      "title": "Soft shoulder bag observed signal",
      "published_at": "2026-06-12T17:00:00Z",
      "summary": "Synthetic sanitized observation about soft shoulder bag styling from a user-controlled tool.",
      "source_name": "External Community Tool",
      "platform": "community",
      "source_weight": 1.1,
      "collected_at": "2026-06-12T17:20:00Z"
    }
  ]
}
```

### Task 2: Add Directory Example Tests

**Files:**
- Create: `tests/test_community_tool_handoff_directory_examples.py`

- [ ] **Step 1: Add test module skeleton and constants**

Create `tests/test_community_tool_handoff_directory_examples.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.community_signals import lint_community_signal_file
from fashion_radar.importers.manual_signals import load_manual_signal_rows

ROOT = Path(__file__).resolve().parents[1]
CSV_DIRECTORY = ROOT / "examples" / "community-tool-handoff-directory.example" / "csv"
JSON_DIRECTORY = ROOT / "examples" / "community-tool-handoff-directory.example" / "json"
CSV_FILES = ("community-tool-a.csv", "community-tool-b.csv")
JSON_FILES = ("community-tool-a.json", "community-tool-b.json")
DIRECTORY_EXAMPLES = (
    (CSV_DIRECTORY, CSV_FILES, "csv", "*.csv"),
    (JSON_DIRECTORY, JSON_FILES, "json", "*.json"),
)


def _example_ids() -> list[str]:
    return [input_format for _directory, _files, input_format, _pattern in DIRECTORY_EXAMPLES]


def _signal_paths(directory: Path, names: tuple[str, ...]) -> list[Path]:
    return [directory / name for name in names]
```

- [ ] **Step 2: Test checked-in directory shape**

Add:

```python
@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_example_shape_has_two_matched_handoff_files(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    matched = sorted(path.name for path in directory.glob(pattern))

    assert directory.exists()
    assert matched == sorted(expected_names)
    for signal_file in _signal_paths(directory, expected_names):
        assert signal_file.exists()
        assert signal_file.is_file()
    assert not any(path.name.startswith("community-handoff-manifest") for path in directory.iterdir())
```

- [ ] **Step 3: Test each child file lints and loads cleanly**

Add:

```python
@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_example_signal_files_lint_and_load_cleanly(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    rows = []

    for signal_file in _signal_paths(directory, expected_names):
        result = lint_community_signal_file(signal_file, input_format=input_format)
        loaded_rows = load_manual_signal_rows(
            signal_file,
            input_format=input_format,
            default_source_name="External Community Tool",
        )

        assert result.ok is True
        assert result.findings == []
        assert result.row_count == 1
        assert result.valid_row_count == 1
        assert len(loaded_rows) == 1
        rows.extend(loaded_rows)

    assert len(rows) == 2
    assert all(row.url.startswith("https://example.com/") for row in rows)
    assert {row.source_name for row in rows} == {"External Community Tool"}
    assert {row.platform for row in rows} == {"community"}
```

- [ ] **Step 4: Test directory linter CLI**

Add:

```python
@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_examples_pass_community_signal_lint_dir(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    result = CliRunner().invoke(
        app,
        [
            "community-signal-lint-dir",
            str(directory),
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--format",
            "json",
            "--source-name",
            "External Community Tool",
            "--strict",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["valid_row_count"] == 2
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["platform_counts"] == {"community": 2}
```

- [ ] **Step 5: Test directory dry-run import CLI**

Add:

```python
@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_examples_pass_import_signals_dir_dry_run_without_artifacts(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    result = CliRunner().invoke(
        app,
        [
            "import-signals-dir",
            str(directory),
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--data-dir",
            str(data_dir),
            "--source-name",
            "External Community Tool",
            "--dry-run",
            "--output-format",
            "json",
        ],
        env={
            "FASHION_RADAR_CONFIG_DIR": str(config_dir),
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["valid_file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["error_count"] == 0
    assert payload["platform_counts"] == {"community": 2}
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
```

- [ ] **Step 6: Test candidate directory preview smoke stays read-only**

Add:

```python
def test_directory_examples_pass_community_candidates_dir_limit_zero_without_artifacts(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring: {}\n"
        "candidate_discovery:\n"
        "  review_min_current_mentions: 1\n"
        "  review_min_distinct_sources: 1\n"
        "  min_single_token_mentions: 1\n"
        "  min_single_token_distinct_sources: 1\n",
        encoding="utf-8",
    )
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates-dir",
            str(CSV_DIRECTORY),
            "--input-format",
            "csv",
            "--pattern",
            "*.csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-16T00:00:00Z",
            "--source-name",
            "External Community Tool",
            "--limit",
            "0",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["file_count"] == 2
    assert payload["row_count"] == 2
    assert payload["limit"] == 0
    assert payload["candidates"] == []
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not (tmp_path / "fashion-radar.sqlite").exists()
```

- [ ] **Step 7: Run targeted directory example tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_tool_handoff_directory_examples.py -q
```

Expected: all tests pass.

### Task 3: Package Archive And Docs Drift

**Files:**
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add package archive requirements**

Add these paths to `SDIST_REQUIRED_PATHS` in `scripts/check_package_archives.py`
and `SDIST_FILES` in `tests/test_package_archives.py`:

```python
"examples/community-tool-handoff-directory.example/README.md",
"examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
"examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
"examples/community-tool-handoff-directory.example/json/community-tool-a.json",
"examples/community-tool-handoff-directory.example/json/community-tool-b.json",
```

- [ ] **Step 2: Add missing-directory-example package regressions**

In `tests/test_package_archives.py`, add:

```python
@pytest.mark.parametrize(
    "missing_path",
    [
        "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
        "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    ],
)
def test_rejects_sdist_without_community_tool_handoff_directory_example(
    tmp_path: Path,
    missing_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[path for path in SDIST_FILES if path != missing_path],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert f"sdist archive missing required file: {missing_path}" in result.stderr
```

Also add `import pytest` if the file does not already import it.

- [ ] **Step 3: Add docs drift constants**

In `tests/test_cli_docs.py`, add:

```python
COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS = (
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
)
COMMUNITY_SIGNAL_PROFILE_EXAMPLE_PATHS = (
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json",
)
```

- [ ] **Step 4: Add directory docs drift test**

In `tests/test_cli_docs.py`, add:

```python
def test_external_tool_directory_examples_are_documented_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")

    for text in (readme, import_doc, checklist):
        for path in COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS:
            assert path in text

    for text in (readme, import_doc, boundaries, architecture, agents):
        normalized = _normalized_text(text).casefold()
        assert "external community tool export director" in normalized
        assert "sanitized csv/json" in normalized
        assert "not platform collection" in normalized
        for term in (
            "connectors",
            "scraping",
            "browser automation",
            "platform apis",
            "monitoring",
            "scheduling",
            "source acquisition",
            "demand proof",
            "ranking",
            "coverage verification",
        ):
            assert term in normalized
```

- [ ] **Step 5: Add manifest example path drift test**

In `tests/test_cli_docs.py`, add:

```python
def test_community_handoff_manifest_docs_show_current_example_paths() -> None:
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    manifest_section = import_doc.split("## Directory Manifest", 1)[1].split(
        "The manifest describes the target directory",
        1,
    )[0]

    for path in COMMUNITY_SIGNAL_PROFILE_EXAMPLE_PATHS:
        assert path in manifest_section
```

- [ ] **Step 6: Run targeted package/docs tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
```

Expected: all tests pass.

### Task 4: Documentation Updates

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update README**

Add a compact note near the external community tool section that points to:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`

State that these are sanitized CSV/JSON local export directory examples and are
not platform collection, connectors, scraping, browser automation, platform
APIs, monitoring, scheduling, source acquisition, demand proof, ranking, or
coverage verification.

- [ ] **Step 2: Update community import docs**

In `docs/community-signal-import.md`:

- add the directory example paths under Contract Files;
- update the `Directory Manifest` JSON example `example_paths` to include all
  four current profile example paths:

```json
"example_paths": [
  "examples/community-signals.example.csv",
  "examples/community-signals.example.json",
  "examples/community-tool-handoff.example.csv",
  "examples/community-tool-handoff.example.json"
]
```

- add a section or paragraph showing:

```bash
uv run fashion-radar community-signal-lint-dir examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --strict
uv run fashion-radar import-signals-dir examples/community-tool-handoff-directory.example/json --format json --pattern "*.json" --source-name "External Community Tool" --data-dir "$PWD/data" --dry-run --output-format json
```

- state that the checked-in `csv/` and `json/` directories are separate
  non-recursive examples for one input format and one pattern per run.

- [ ] **Step 3: Update boundary and architecture docs**

Add one compact sentence or bullet to `docs/source-boundaries.md` and
`docs/architecture.md` stating that external community tool export directory
examples are sanitized local CSV/JSON samples and are not platform collection,
connectors, scraping, browser automation, platform APIs, monitoring,
scheduling, source acquisition, demand proof, ranking, or coverage
verification.

- [ ] **Step 4: Update upload checklist, AGENTS, and changelog**

Update:

- `docs/github-upload-checklist.md`: require directory example links and package
  inclusion.
- `AGENTS.md`: extend the handoff guardrail to include directory examples.
- `CHANGELOG.md`: add an Unreleased bullet.

### Task 5: Verification, Review, Commit, And Upload

**Files:**
- Add: `docs/reviews/opencode-stage-55-release-review-prompt.md`
- Add after review: `docs/reviews/opencode-stage-55-release-review.md`
- Modify if needed: files changed by Tasks 1-4 only.

- [ ] **Step 1: Run full verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock
```

Expected: each command exits 0.

- [ ] **Step 2: Run release hygiene and smoke checks**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: each command exits 0.

- [ ] **Step 3: Request local opencode release review**

Create `docs/reviews/opencode-stage-55-release-review-prompt.md` asking local
opencode with GLM 5.2 to review:

- the new directory examples are sanitized, importable, and local-only;
- no new commands/schema/dependencies/connectors/platform collection were added;
- docs and docs drift tests cover the checked-in directory examples;
- manifest docs show the current four example paths;
- package archives require the new directory files;
- `uv.lock` is unchanged and mirror-free.

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-55-release-review-prompt.md)" > docs/reviews/opencode-stage-55-release-review.md 2> /tmp/opencode-stage55-release-review.err
```

Expected: no Critical or Important findings remain and the review approves
commit/push.

- [ ] **Step 4: Commit and upload**

Run:

```bash
git status --short
git add examples/community-tool-handoff-directory.example/README.md examples/community-tool-handoff-directory.example/csv/community-tool-a.csv examples/community-tool-handoff-directory.example/csv/community-tool-b.csv examples/community-tool-handoff-directory.example/json/community-tool-a.json examples/community-tool-handoff-directory.example/json/community-tool-b.json tests/test_community_tool_handoff_directory_examples.py scripts/check_package_archives.py tests/test_package_archives.py tests/test_cli_docs.py README.md docs/community-signal-import.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-16-stage-55-community-tool-directory-examples-design.md docs/superpowers/plans/2026-06-16-stage-55-community-tool-directory-examples-plan.md docs/reviews/opencode-stage-55-plan-review-prompt.md docs/reviews/opencode-stage-55-plan-review.md docs/reviews/opencode-stage-55-release-review-prompt.md docs/reviews/opencode-stage-55-release-review.md
git commit -m "Add community tool directory examples"
```

Upload to `origin/main`. If normal `git push` fails, use the saved token with
the GitHub Git Data API, verify the remote tree matches the local tree, fetch
the remote commit, and align local `main`/`origin/main` to the API-created
commit.

- [ ] **Step 5: Confirm GitHub Actions**

Use the GitHub API to confirm the workflow run for the uploaded commit completes
successfully.
