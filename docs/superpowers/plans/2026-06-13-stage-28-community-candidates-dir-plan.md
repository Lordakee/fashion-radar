# Stage 28 Community Candidate Directory Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `fashion-radar community-candidates-dir`, a local read-only command that previews aggregate candidate phrases from a non-recursive directory of user-supplied community signal CSV/JSON handoff files before import.

**Architecture:** Extend the existing `community_candidates.py` module with a shared row-scoring helper plus a directory preview model/function. Reuse `load_manual_signal_directory_rows()` for direct-child file matching and row validation, but never expose its directory paths, file paths, filenames, or raw findings from the preview command. Add a Typer command mirroring `community-candidates` validation order and output modes while keeping the public output aggregate-only.

**Tech Stack:** Python 3.11, Typer, Pydantic, existing `load_manual_signal_directory_rows()`, existing `extract_candidate_phrases()`, existing `configured_entity_keys()`, existing scoring/entity config models, pytest, ruff.

---

## Stage 28 Boundary

Stage 28 includes implementation and focused tests only.

In scope:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`

Out of scope for this node:

- README or broad docs updates;
- Claude Code code-review prompt generation/submission, which belongs to the
  next review/release node after Stage 28 implementation is complete;
- release verification, wheel build, installed-wheel smoke;
- commit and push;
- any `uv.lock` change;
- source collectors, platform connectors, account automation, browser
  automation, watch folders, schedulers, dashboards, reports, SQLite writes, or
  entity YAML generation.

## File Map

- Modify `src/fashion_radar/community_candidates.py`: add
  `CommunityCandidateDirectoryPreview`, add `preview_community_candidate_directory()`,
  factor single-file preview into a shared private row-scoring helper, and
  add a directory table renderer.
- Modify `src/fashion_radar/cli.py`: import the new helper/renderer and add
  `community-candidates-dir`.
- Modify `tests/test_community_candidates.py`: add module tests for directory
  aggregation, non-recursive matching, limits, disabled discovery, and output
  safety.
- Modify `tests/test_cli.py`: add CLI tests for help, JSON/table output,
  validation order, clean generic errors, output safety, and artifact absence.
- Do not modify or stage `uv.lock`.

## Task 1: Module-Level Directory Preview

**Files:**
- Modify: `src/fashion_radar/community_candidates.py`
- Modify: `tests/test_community_candidates.py`

- [ ] **Step 1: Add failing module tests for directory aggregation**

Add tests that create two direct-child CSV files and one nested CSV file. The
direct files include current and baseline mentions for the same phrase; the
nested file includes a unique phrase that must not appear. Call:

```python
preview = preview_community_candidate_directory(
    tmp_path,
    input_format="csv",
    pattern="*.csv",
    scoring=ScoringSettings(),
    settings=CandidateDiscoverySettings(
        review_min_current_mentions=1,
        review_min_distinct_sources=1,
        min_single_token_mentions=1,
        min_single_token_distinct_sources=1,
    ),
    entity_config=None,
    as_of=AS_OF,
    default_source_name="Community Tool Export",
    limit=50,
)
```

Expected assertions:

```python
assert preview.input_format == "csv"
assert preview.file_count == 2
assert preview.row_count == 3
assert preview.candidate_count >= 1
assert all(candidate.phrase != "Nested Only Signal" for candidate in preview.candidates)
candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")
assert candidate.current_mentions == 2
assert candidate.baseline_mentions == 1
assert candidate.distinct_sources == 2
```

- [ ] **Step 2: Add failing module tests for custom pattern and regular files**

Add a test that creates:

- `batch-a.signal.csv`, a valid direct-child file;
- `batch-b.csv`, a valid direct-child file that should not match
  `*.signal.csv`;
- `matching-dir.signal.csv/ignored.csv`, a directory whose name matches the
  pattern but must be ignored because it is not a regular file;
- `nested/nested.signal.csv`, a nested regular file that must be ignored even
  with a broad pattern such as `**/*.signal.csv`.

Call:

```python
preview = preview_community_candidate_directory(
    tmp_path,
    input_format="csv",
    pattern="*.signal.csv",
    scoring=ScoringSettings(),
    settings=CandidateDiscoverySettings(
        review_min_current_mentions=1,
        review_min_distinct_sources=1,
        min_single_token_mentions=1,
        min_single_token_distinct_sources=1,
    ),
    entity_config=None,
    as_of=AS_OF,
    default_source_name="Community Tool Export",
    limit=50,
)
```

Expected assertions:

```python
assert preview.file_count == 1
assert preview.row_count == 1
assert all(candidate.phrase != "Nested Signal" for candidate in preview.candidates)
assert all(candidate.phrase != "Unmatched Signal" for candidate in preview.candidates)
```

Then call the same helper with `pattern="**/*.signal.csv"` and assert it still
does not recurse:

```python
with pytest.raises(ManualSignalImportError) as exc_info:
    preview_community_candidate_directory(..., pattern="**/*.signal.csv")
assert str(exc_info.value) == "input directory could not be read or validated"
assert "nested.signal.csv" not in str(exc_info.value)
```

- [ ] **Step 3: Add failing module tests for row-scoring parity, labels, ordering, and limits**

Add tests proving directory preview preserves Stage 27 behavior:

```python
assert preview.source_name == "Community Tool Export"
assert preview.candidates[0].first_seen_at == AS_OF.isoformat()
assert preview.candidates[0].current_mentions == 1
```

Add a parity test that runs `preview_community_candidates()` on one file and
`preview_community_candidate_directory()` on a directory containing only that
file, with identical config. Expected assertions:

```python
single = preview_community_candidates(...)
directory = preview_community_candidate_directory(...)
assert directory.candidate_count == single.candidate_count
assert directory.candidates == single.candidates
```

Add label and score assertions:

```python
new_candidate = next(item for item in preview.candidates if item.phrase == "New Shape bag")
assert new_candidate.label == "new"
assert new_candidate.baseline_mentions == 0
assert new_candidate.growth_ratio is None
assert new_candidate.score > 0

rising_candidate = next(item for item in preview.candidates if item.phrase == "Rising Shape bag")
assert rising_candidate.label == "rising"
assert rising_candidate.baseline_mentions > 0
assert rising_candidate.growth_ratio is not None
assert rising_candidate.growth_ratio >= preview_settings.rising_growth_ratio
```

Add a deterministic tie-break test with equal score, equal current mentions,
and equal distinct sources:

```python
phrases = [candidate.phrase for candidate in preview.candidates[:2]]
assert phrases == sorted(phrases, key=str.lower)
```

Add a `limit=0` test:

```python
preview = preview_community_candidate_directory(..., limit=0)
assert preview.file_count == 1
assert preview.row_count == 1
assert preview.candidate_count >= 1
assert preview.candidates == []
```

Add a disabled-discovery test:

```python
preview = preview_community_candidate_directory(
    ...,
    settings=CandidateDiscoverySettings(enabled=False),
)
assert preview.file_count == 1
assert preview.row_count == 1
assert preview.candidate_count == 0
assert preview.candidates == []
```

- [ ] **Step 4: Add failing module tests for output safety**

Add a recursive JSON serialization check and a table-output check. Forbidden
values must include:

```python
forbidden = [
    str(tmp_path),
    "first.csv",
    "second.csv",
    "nested.csv",
    "https://example.com/private-current",
    "Private raw summary",
    "private row title",
    "le teckel bag",  # normalized key casing
    "normalized_key",
    "normalized_phrase",
    "contexts",
    "candidate_contexts",
    "representative_items",
    "source_file",
    "source_path",
    "import_path",
    "account_id",
    "findings",
]
```

Expected assertions:

```python
payload = preview.model_dump()
serialized = _serialized(payload)
for value in forbidden:
    assert value not in serialized
table = "\n".join(render_community_candidate_directory_table(preview))
for value in forbidden:
    assert value not in table
```

The candidate phrase itself may appear in display casing; the normalized key
must not appear as a separate lowercase/internal value.

- [ ] **Step 5: Implement shared row preview helper and directory model**

In `src/fashion_radar/community_candidates.py`, keep
`CommunityCandidateRow` unchanged and add:

```python
class CommunityCandidateDirectoryPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_format: ManualSignalFormat
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_name: str = "Community Tool Export"
    file_count: int = 0
    row_count: int = 0
    candidate_count: int = 0
    limit: int | None = 50
    candidates: list[CommunityCandidateRow] = Field(default_factory=list)
```

Create a private helper that accepts already-validated rows:

```python
def _build_candidate_preview(
    rows: Sequence[ManualSignalRow],
    *,
    input_format: ManualSignalFormat,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    source_name: str,
    limit: int | None,
) -> dict[str, object]:
    ...
```

Move the existing scoring body from `preview_community_candidates()` into this
helper. It must preserve:

- `limit < 0` raises `ValueError("limit must be at least 0")`;
- `as_of` parsing via `parse_datetime_utc()`;
- missing `collected_at` uses parsed `as_of`;
- configured entity suppression;
- one mention per normalized key per row;
- disabled discovery returns zero candidates with row count preserved.

Then make the existing single-file function:

```python
rows = load_manual_signal_rows(path, input_format=input_format, default_source_name=source_name)
payload = _build_candidate_preview(...)
return CommunityCandidatePreview(**payload)
```

- [ ] **Step 6: Implement directory loader wrapper**

Add:

```python
def preview_community_candidate_directory(
    directory: Path,
    *,
    input_format: ManualSignalFormat,
    pattern: str,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidateDirectoryPreview:
    source_name = default_source_name.strip() or "Community Tool Export"
    loaded = load_manual_signal_directory_rows(
        directory,
        input_format=input_format,
        pattern=pattern,
        default_source_name=source_name,
    )
    if loaded.result.error_count:
        raise ManualSignalImportError("input directory could not be read or validated")
    payload = _build_candidate_preview(...)
    return CommunityCandidateDirectoryPreview(
        **payload,
        file_count=loaded.result.file_count,
    )
```

The raised error text must stay generic and must not include `directory`,
matched filenames, raw findings, or row values.

- [ ] **Step 7: Add directory table renderer**

Add:

```python
def render_community_candidate_directory_table(
    preview: CommunityCandidateDirectoryPreview,
) -> list[str]:
    lines = [
        "Community candidate preview from local handoff files.",
        "Candidate signals are aggregate observed phrases from matched local files only.",
        f"Input format: {preview.input_format}",
        f"Current window: {preview.current_window_start} < collected_at <= {preview.as_of}",
        f"Baseline window: {preview.baseline_window_start} < collected_at <= {preview.current_window_start}",
        f"Source name: {_table_cell(preview.source_name)}",
        f"Files: {preview.file_count}",
        f"Rows: {preview.row_count}",
        f"Candidates: {len(preview.candidates)} shown, {preview.candidate_count} total",
    ]
    ...
```

Reuse the same candidate table columns as `render_community_candidates_table()`.
Do not print directory paths, file paths, filenames, raw findings, or pattern.

- [ ] **Step 8: Run focused module tests**

Run:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
.venv/bin/python -m pytest tests/test_community_candidates.py -q
```

Expected: both commands exit `0`.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI help and output tests**

Add a help test:

```python
result = runner.invoke(app, ["--help"])
assert result.exit_code == 0
assert "community-candidates-dir" in result.stdout
```

Add JSON and table tests that use a temporary `configs/` directory and a
temporary signal directory. Expected JSON assertions:

```python
payload = json.loads(result.stdout)
assert list(payload) == [
    "input_format",
    "as_of",
    "current_window_start",
    "baseline_window_start",
    "current_days",
    "baseline_days",
    "source_name",
    "file_count",
    "row_count",
    "candidate_count",
    "limit",
    "candidates",
]
assert payload["file_count"] == 2
assert payload["row_count"] == 3
assert "directory" not in payload
assert "files" not in payload
assert "pattern" not in payload
```

Add a recursive forbidden-value scan over actual CLI JSON stdout:

```python
serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
for forbidden in [
    str(directory),
    directory.name,
    "first.csv",
    "second.csv",
    "nested.csv",
    "https://example.com/private-current",
    "private row title",
    "Private raw summary",
    "normalized_key",
    "normalized_phrase",
    "contexts",
    "candidate_contexts",
    "representative_items",
    "source_file",
    "source_path",
    "import_path",
    "account_id",
    "findings",
]:
    assert forbidden not in serialized
```

Table output should contain `Files: 2`, `Rows: 3`, and candidate columns. Run
the same forbidden-value scan against `result.stdout`.

- [ ] **Step 2: Add failing CLI validation-order tests**

Patch both config-loading functions and the directory preview function for
early-failure cases. The config loaders must raise an assertion if called, and
the directory preview helper must raise an assertion if called. This proves
invalid `--as-of`, invalid `--input-format`, and negative `--limit` fail before
config load and before directory read.

Expected cases:

```python
runner.invoke(app, ["community-candidates-dir", str(directory), "--as-of", "bad"])
runner.invoke(app, ["community-candidates-dir", str(directory), "--input-format", "bad", "--as-of", AS_OF_TEXT])
runner.invoke(app, ["community-candidates-dir", str(directory), "--limit", "-1", "--as-of", AS_OF_TEXT])
```

Each case must exit non-zero without calling config loaders or the directory
preview helper.

Add a separate invalid-config case where config loading fails and the directory
preview helper raises an assertion if called:

```python
runner.invoke(app, ["community-candidates-dir", str(directory), "--config-dir", str(invalid_config_dir), "--as-of", AS_OF_TEXT])
```

Expected: the command exits non-zero because config is invalid, and the
directory preview helper is never called. This proves invalid config prevents
directory reads.

- [ ] **Step 3: Add failing CLI clean-error tests**

Add tests for:

- invalid directory;
- no matching files;
- invalid file content with private filename, URL, title, summary, invalid date,
  and invalid source weight.

Expected assertions:

```python
assert result.exit_code == 1
combined = result.stdout + result.stderr
assert "Could not preview community candidates directory" in combined
assert "Traceback" not in combined
for forbidden in [str(directory), "secret.csv", "https://example.com/private", "private title", "private summary", "bad-date", "not-a-number"]:
    assert forbidden not in combined
```

- [ ] **Step 4: Implement CLI imports and command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.community_candidates import (
    preview_community_candidate_directory,
    preview_community_candidates,
    render_community_candidate_directory_table,
    render_community_candidates_table,
)
```

Add `COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION` near the existing community
candidate options:

```python
COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION = typer.Option(
    "*.csv",
    "--pattern",
    help="Filename glob for direct child handoff files.",
)
```

Add:

```python
@app.command(name="community-candidates-dir")
def community_candidates_dir_command(
    directory: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_CANDIDATES_INPUT_FORMAT_OPTION,
    pattern: str = COMMUNITY_CANDIDATES_DIR_PATTERN_OPTION,
    as_of: str = COMMUNITY_CANDIDATES_AS_OF_OPTION,
    source_name: str = COMMUNITY_CANDIDATES_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    output_format: CommunityCandidatesOutputFormat = COMMUNITY_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Preview candidate phrases from local community signal files in one directory."""
    ...
```

Validation order must match `community_candidates_command`: parse `--as-of`,
load config, then call `preview_community_candidate_directory()`.

For `ManualSignalImportError`, print only:

```text
Could not preview community candidates directory: input directory could not be read or validated
```

For other exceptions, print the same generic input-directory text instead of
printing raw exception text. This avoids leaking directory paths, file paths,
filenames, raw loader findings, row values, or tracebacks from unexpected
exceptions.

- [ ] **Step 5: Run focused CLI tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q
```

Expected: command exits `0`.

## Task 3: Stage 28 Focused Verification

**Files:**
- No file edits.
- Do not stage `uv.lock`.

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 2: Run boundary and artifact checks**

Run:

```bash
git diff --name-only
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md
git diff -- uv.lock
rg -n "scrap|crawler|crawl|captcha|login|cookie|account automation|watch|scheduler|platform API|Instagram|TikTok|小红书|X/Twitter" src tests docs/superpowers/specs/2026-06-13-stage-28-community-candidates-dir-design.md docs/superpowers/plans/2026-06-13-stage-28-community-candidates-dir-plan.md
find . -path ./.git -prune -o -type f \( -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" -o -path "./data/*" -o -path "./reports/*" \) -print
```

Expected:

- diff names include only intended Stage 28 files plus the pre-existing
  unstaged `uv.lock`;
- `uv.lock` remains unstaged;
- unsafe boundary scan has no new source/test/docs additions implying platform
  collection or automation; the only allowed matches are negative boundary
  language in the Stage 28 design/plan if present;
- artifact scan prints no generated DB/report artifacts.

## Self-Review Checklist

- The plan builds a single command over local sanitized files only.
- The plan reuses the existing manual directory loader for direct-child matching
  and validation.
- The plan never emits directory paths, file paths, filenames, row-level raw
  values, raw validation diagnostics, or internal normalized keys.
- The plan keeps config load before directory read.
- The plan includes module and CLI tests for non-recursive matching, output
  safety, generic errors, disabled discovery, limits, and artifact absence.
- The plan does not touch `uv.lock`, collectors, schedulers, dashboards,
  reports, SQLite write paths, or platform automation.
