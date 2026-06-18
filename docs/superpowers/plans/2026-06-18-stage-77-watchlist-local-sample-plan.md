# Stage 77 Watchlist Local Sample Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional expanded local community-signal sample that exercises
the existing `fashion-watchlist` entity pack without changing runtime behavior
or default first-run expectations.

**Architecture:** Static sample, docs, and tests only. The new CSV file is a
sanitized local handoff example consumed by existing `community-signal-lint`,
`import-signals`, `match`, `report`, and `trends` commands. Tests use temporary
config/data/report directories and the existing `fashion-watchlist` entity pack;
no new collectors, adapters, platform APIs, or scheduling behavior are added.

**Tech Stack:** Python 3.11, Typer `CliRunner`, pytest, uv, ruff, Markdown, YAML,
CSV.

**Review Protocol Note:** The current stage-local review instruction is to use
local opencode with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant
max`. This is an explicit current user override for this development node. It
does not permanently change repository review-protocol documents, so Stage 77
records `opencode-stage-77-*` review artifacts as stage-local process metadata.
Public `uv.lock` must remain free of mirror-bound URLs per `AGENTS.md`; the
pre-existing local `uv.lock` mirror rewrite is not part of this stage and must
not be staged.

---

## File Map

- Add `examples/community-signals.watchlist.example.csv`
  - Sanitized optional local watchlist sample rows.
- Add `tests/test_watchlist_sample_workflow.py`
  - End-to-end local CLI workflow proof against temporary directories.
- Modify `tests/test_community_signal_lint.py`
  - Include the new sample in clean repository example lint coverage.
- Modify `tests/test_community_signal_import_contract.py`
  - Include the new sample in importer/field contract coverage.
- Modify `tests/test_entity_packs.py`
  - Prove sample text matches expected watchlist entities and type coverage.
- Modify `scripts/check_package_archives.py`
  - Require the new sample in sdist archives.
- Modify `tests/test_package_archives.py`
  - Mirror the new required sdist path and add a missing-file regression test.
- Modify `README.md`
  - Document the optional expanded watchlist sample path.
- Modify `docs/first-run.md`
  - Document the optional expanded watchlist sample after the default sample.
- Modify `docs/entity-packs.md`
  - Tie the optional sample directly to `fashion-watchlist`.
- Modify `docs/github-upload-checklist.md`
  - Mention that package archive checks require the optional watchlist sample.
- Modify `tests/test_cli_docs.py`
  - Add docs drift tests for optional sample commands and boundaries.
- Modify `CHANGELOG.md`
  - Add Stage 77 entry.
- Create review artifacts:
  - `docs/reviews/opencode-stage-77-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-77-plan-review.md`
  - `docs/reviews/opencode-stage-77-plan-rereview-prompt.md`
  - `docs/reviews/opencode-stage-77-plan-rereview.md`
  - `docs/reviews/opencode-stage-77-code-review-prompt.md`
  - `docs/reviews/opencode-stage-77-code-review.md`

## Task 1: Add Failing Sample Contract Tests

**Files:**
- Modify: `tests/test_community_signal_lint.py`
- Modify: `tests/test_community_signal_import_contract.py`
- Modify: `tests/test_entity_packs.py`

- [ ] **Step 1: Add the new sample constants to lint tests**

In `tests/test_community_signal_lint.py`, add:

```python
WATCHLIST_CSV_EXAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_EXPECTED_ROWS = 8
```

Do not add the optional sample to `COMMUNITY_SIGNAL_EXAMPLES`. That tuple is the
canonical small producer-example set, and existing tests intentionally assume
those examples have two rows.

Add a separate test near `test_repository_examples_lint_cleanly`:

```python
def test_watchlist_community_signal_example_lints_cleanly() -> None:
    result = lint_community_signal_file(WATCHLIST_CSV_EXAMPLE, input_format="csv")

    assert WATCHLIST_CSV_EXAMPLE.is_file()
    assert result.ok is True
    assert result.findings == []
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.row_count == WATCHLIST_EXPECTED_ROWS
    assert result.valid_row_count == WATCHLIST_EXPECTED_ROWS
    assert result.source_name_counts == {
        "Community Watchlist Sample": WATCHLIST_EXPECTED_ROWS
    }
    assert result.platform_counts == {"community": WATCHLIST_EXPECTED_ROWS}
```

- [ ] **Step 2: Verify the lint test fails before the sample exists**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly -q
```

Expected before implementation: the test fails because the file is missing.

- [ ] **Step 3: Add importer/field contract coverage**

In `tests/test_community_signal_import_contract.py`, add the same
`WATCHLIST_CSV_EXAMPLE` and `WATCHLIST_EXPECTED_ROWS` constants. Keep this
optional sample out of `COMMUNITY_SIGNAL_EXAMPLES`.

```python
WATCHLIST_CSV_EXAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_EXPECTED_ROWS = 8
```

Add a focused field-contract test:

```python
def test_watchlist_community_signal_csv_example_uses_allowed_fields() -> None:
    fields = _example_fields(WATCHLIST_CSV_EXAMPLE, "csv")

    assert fields <= ALLOWED_COMMUNITY_SIGNAL_FIELDS
```

Add a focused importer test:

```python
def test_watchlist_community_signal_csv_example_loads_expected_rows() -> None:
    rows = load_manual_signal_rows(
        WATCHLIST_CSV_EXAMPLE,
        input_format="csv",
        default_source_name="Community Watchlist Sample",
    )

    assert len(rows) == 8
    assert rows[0].url == "https://example.com/community-watchlist/khaite-lotus-bag"
    assert rows[0].title == "Khaite Lotus Bag local watchlist note"
    assert rows[0].source_name == "Community Watchlist Sample"
    assert rows[0].platform == "community"
    assert rows[-1].title == "Boho Revival styling watchlist note"
```

Add a focused dry-run artifact test:

```python
def test_import_signals_dry_run_validates_watchlist_sample_without_artifacts(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(WATCHLIST_CSV_EXAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ],
        env={"FASHION_RADAR_REPORTS_DIR": str(reports_dir)},
    )

    assert result.exit_code == 0
    assert f"Validated {WATCHLIST_EXPECTED_ROWS} manual signal rows" in result.output
    assert "Dry run: no rows imported" in result.output
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert list(tmp_path.rglob("*.sqlite")) == []
    assert list(tmp_path.rglob("*.sqlite*")) == []
    assert list(tmp_path.rglob("fashion-radar-*.json")) == []
    assert list(tmp_path.rglob("fashion-radar-*.md")) == []
    assert list(tmp_path.rglob("*digest*")) == []
    assert list(tmp_path.rglob("*.eml")) == []
    assert list(tmp_path.rglob("latest.*")) == []
    assert list(tmp_path.rglob("report-index.json")) == []
```

- [ ] **Step 4: Add entity-pack sample matching coverage**

In `tests/test_entity_packs.py`, import the sample loader:

```python
from fashion_radar.importers.manual_signals import load_manual_signal_rows
```

Add:

```python
WATCHLIST_SIGNAL_PATH = Path("examples/community-signals.watchlist.example.csv")
```

Then add:

```python
def test_fashion_watchlist_sample_matches_expected_entities_and_types() -> None:
    entities = _entities()
    rows = load_manual_signal_rows(
        WATCHLIST_SIGNAL_PATH,
        input_format="csv",
        default_source_name="Community Watchlist Sample",
    )
    text = " ".join(f"{row.title} {row.summary}" for row in rows)

    accepted = match_entities(text, entities)
    matched_names = {decision.entity_name for decision in accepted}
    matched_types = {decision.entity_type for decision in accepted}

    assert {
        "Khaite",
        "Khaite Lotus Bag",
        "Loewe",
        "Loewe Puzzle Bag",
        "Jonathan Anderson",
        "Bella Hadid",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "Boho Revival",
    } <= matched_names
    assert {"brand", "product", "designer", "celebrity", "category", "trend"} <= matched_types
```

- [ ] **Step 5: Verify entity/import tests fail before the sample exists**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_uses_allowed_fields tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows tests/test_community_signal_import_contract.py::test_import_signals_dry_run_validates_watchlist_sample_without_artifacts tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types -q
```

Expected before implementation: both tests fail because the sample file is
missing.

## Task 2: Add The Optional Watchlist Sample

**Files:**
- Create: `examples/community-signals.watchlist.example.csv`

- [ ] **Step 1: Create the CSV sample**

Create `examples/community-signals.watchlist.example.csv` with exactly:

```csv
url,title,published_at,summary,source_name,platform,source_weight,collected_at
https://example.com/community-watchlist/khaite-lotus-bag,Khaite Lotus Bag local watchlist note,2026-06-12T08:00:00Z,Sanitized local note about Khaite Lotus Bag and Khaite handbag styling,Community Watchlist Sample,community,1.2,2026-06-12T08:20:00Z
https://example.com/community-watchlist/loewe-puzzle-bag,Loewe Puzzle Bag local watchlist note,2026-06-12T09:00:00Z,Sanitized local note about Loewe Puzzle Bag and Loewe handbag interest,Community Watchlist Sample,community,1.2,2026-06-12T09:20:00Z
https://example.com/community-watchlist/jonathan-anderson,Jonathan Anderson creative director note,2026-06-12T10:00:00Z,Sanitized local note about Jonathan Anderson creative director coverage and Loewe fashion context,Community Watchlist Sample,community,1.1,2026-06-12T10:20:00Z
https://example.com/community-watchlist/bella-hadid,Bella Hadid street style watchlist note,2026-06-12T11:00:00Z,Sanitized local note about Bella Hadid street style and celebrity style signals,Community Watchlist Sample,community,1.1,2026-06-12T11:20:00Z
https://example.com/community-watchlist/alaia-le-teckel,Alaia Le Teckel shoulder bag note,2026-06-12T12:00:00Z,Sanitized local note about Alaia Le Teckel shoulder bag and handbag mentions,Community Watchlist Sample,community,1.3,2026-06-12T12:20:00Z
https://example.com/community-watchlist/miu-miu-arcadie,Miu Miu Arcadie handbag note,2026-06-12T13:00:00Z,Sanitized local note about Miu Miu Arcadie bag and Miu Miu handbag styling,Community Watchlist Sample,community,1.2,2026-06-12T13:20:00Z
https://example.com/community-watchlist/mary-jane-shoes,Mary Jane Shoes local watchlist note,2026-06-12T14:00:00Z,Sanitized local note about Mary Jane shoes and Mary Jane flats in runway footwear,Community Watchlist Sample,community,1.0,2026-06-12T14:20:00Z
https://example.com/community-watchlist/boho-revival,Boho Revival styling watchlist note,2026-06-12T15:00:00Z,Sanitized local note about boho revival and boho chic styling signals,Community Watchlist Sample,community,1.0,2026-06-12T15:20:00Z
```

- [ ] **Step 2: Verify sample contract tests pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_uses_allowed_fields tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows tests/test_community_signal_import_contract.py::test_import_signals_dry_run_validates_watchlist_sample_without_artifacts tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types -q
```

Expected after implementation: all selected tests pass.

## Task 3: Add Local CLI Workflow Test

**Files:**
- Create: `tests/test_watchlist_sample_workflow.py`

- [ ] **Step 1: Add the failing workflow test**

Create `tests/test_watchlist_sample_workflow.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from shutil import copyfile

from typer.testing import CliRunner

from fashion_radar.cli import app

ROOT = Path(__file__).resolve().parents[1]
WATCHLIST_SAMPLE = ROOT / "examples" / "community-signals.watchlist.example.csv"
WATCHLIST_PACK = ROOT / "configs" / "entity-packs" / "fashion-watchlist.example.yaml"
SCORING_EXAMPLE = ROOT / "configs" / "scoring.example.yaml"
AS_OF = "2026-06-13T12:00:00Z"
BASELINE_AS_OF = "2026-06-06T12:00:00Z"

EXPECTED_REPORT_ENTITIES = {
    "Khaite",
    "Khaite Lotus Bag",
    "Loewe",
    "Loewe Puzzle Bag",
    "Jonathan Anderson",
    "Bella Hadid",
    "Alaia Le Teckel",
    "Miu Miu Arcadie",
    "Mary Jane Shoes",
    "Boho Revival",
}


def invoke_ok(args: list[str]) -> str:
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    return result.output


def prepare_watchlist_config(tmp_path: Path) -> tuple[Path, Path, Path]:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    config_dir.mkdir()
    copyfile(WATCHLIST_PACK, config_dir / "entities.yaml")
    copyfile(SCORING_EXAMPLE, config_dir / "scoring.yaml")
    return config_dir, data_dir, reports_dir


def test_optional_watchlist_sample_runs_local_import_match_report_and_trends(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, reports_dir = prepare_watchlist_config(tmp_path)

    lint_payload = json.loads(
        invoke_ok(
            [
                "community-signal-lint",
                str(WATCHLIST_SAMPLE),
                "--input-format",
                "csv",
                "--source-name",
                "Community Watchlist Sample",
                "--format",
                "json",
            ]
        )
    )
    assert lint_payload["valid_row_count"] == 8
    assert lint_payload["findings"] == []

    pack_payload = json.loads(
        invoke_ok(
            [
                "entity-pack-lint",
                str(WATCHLIST_PACK),
                "--format",
                "json",
            ]
        )
    )
    assert pack_payload["error_count"] == 0

    dry_run_output = invoke_ok(
        [
            "import-signals",
            str(WATCHLIST_SAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--data-dir",
            str(data_dir),
            "--dry-run",
        ]
    )
    assert "Validated 8 manual signal rows" in dry_run_output
    assert not (data_dir / "fashion-radar.sqlite").exists()

    import_output = invoke_ok(
        [
            "import-signals",
            str(WATCHLIST_SAMPLE),
            "--format",
            "csv",
            "--source-name",
            "Community Watchlist Sample",
            "--imported-at",
            AS_OF,
            "--data-dir",
            str(data_dir),
        ]
    )
    assert "Imported 8 manual signal rows" in import_output

    match_output = invoke_ok(
        [
            "match",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
        ]
    )
    assert "Processed 8 items" in match_output

    invoke_ok(
        [
            "report",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
        ]
    )
    report_payload = json.loads(
        (reports_dir / "fashion-radar-2026-06-13.json").read_text(encoding="utf-8")
    )
    report_entities = {entity["entity_name"] for entity in report_payload["entities"]}
    assert EXPECTED_REPORT_ENTITIES <= report_entities

    trend_payload = json.loads(
        invoke_ok(
            [
                "trends",
                "--config-dir",
                str(config_dir),
                "--data-dir",
                str(data_dir),
                "--as-of",
                AS_OF,
                "--baseline-as-of",
                BASELINE_AS_OF,
                "--format",
                "json",
            ]
        )
    )
    trend_names = {delta["name"] for delta in trend_payload["deltas"]}
    assert EXPECTED_REPORT_ENTITIES <= trend_names
```

- [ ] **Step 2: Verify the workflow test fails before the sample exists**

If Task 2 has not run yet, run:

```bash
uv --no-config run --frozen pytest tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends -q
```

Expected before sample creation: fail because the sample file is missing.

If Task 2 has already created the sample, run the same command after Task 3 and
expect it to pass.

## Task 4: Add Package Archive Coverage

**Files:**
- Modify: `scripts/check_package_archives.py`
- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add the new required sdist path to the checker**

In `scripts/check_package_archives.py`, add this entry between
`examples/community-signals.example.json` and
`examples/community-signal-profile.example.json`:

```python
"examples/community-signals.watchlist.example.csv",
```

- [ ] **Step 2: Mirror the fixture path and add a missing-file test**

In `tests/test_package_archives.py`, add the same path to `SDIST_FILES` after
`examples/community-signals.example.json`.

Add:

```python
def test_rejects_sdist_without_watchlist_community_signal_sample(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(
        build_dir,
        files=[
            path
            for path in SDIST_FILES
            if path != "examples/community-signals.watchlist.example.csv"
        ],
    )

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "sdist archive missing required file: "
        "examples/community-signals.watchlist.example.csv"
    ) in result.stderr
```

- [ ] **Step 3: Verify package archive tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_accepts_archives_with_required_files_and_metadata tests/test_package_archives.py::test_rejects_sdist_without_watchlist_community_signal_sample -q
```

Expected after implementation: both pass.

## Task 5: Add Docs And Docs Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/first-run.md`
- Modify: `docs/entity-packs.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add docs drift tests first**

First add this module constant near the other documentation path constants in
`tests/test_cli_docs.py`:

```python
ENTITY_PACKS_DOC = ROOT / "docs" / "entity-packs.md"
```

Then add these tests near the first-run and entity-pack docs tests:

```python
def test_readme_documents_optional_watchlist_local_sample() -> None:
    text = _read(README)
    normalized = _normalized_doc_text(README)

    for term in (
        "Optional Expanded Watchlist Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        "cp configs/entity-packs/fashion-watchlist.example.yaml \"$tmp_watchlist/configs/entities.yaml\"",
        "community-signal-lint examples/community-signals.watchlist.example.csv",
        "import-signals examples/community-signals.watchlist.example.csv",
        "uv run fashion-radar match --config-dir \"$tmp_watchlist/configs\"",
        "uv run fashion-radar report --config-dir \"$tmp_watchlist/configs\"",
        "uv run fashion-radar trends --config-dir \"$tmp_watchlist/configs\"",
    ):
        assert term in text

    for term in (
        "optional local sample does not fetch URLs",
        "does not collect platform data",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
        "does not add connectors",
    ):
        assert term in normalized


def test_first_run_guide_documents_optional_watchlist_local_sample() -> None:
    text = _read(FIRST_RUN_DOC)
    normalized = _normalized_doc_text(FIRST_RUN_DOC)

    for term in (
        "Optional Expanded Watchlist Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        "fashion-watchlist.example.yaml",
        "Khaite",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "Boho Revival",
    ):
        assert term in text

    for term in (
        "optional local sample does not fetch URLs",
        "does not collect platform data",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
        "does not add connectors",
    ):
        assert term in normalized


def test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack() -> None:
    text = _read(ENTITY_PACKS_DOC)
    normalized = _normalized_doc_text(ENTITY_PACKS_DOC)

    for term in (
        "Try The Optional Local Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        "cp configs/entity-packs/fashion-watchlist.example.yaml \"$tmp_watchlist/configs/entities.yaml\"",
        "uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml",
        "uv run fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv",
    ):
        assert term in text

    for term in (
        "local sample rows are synthetic",
        "not a hot-list",
        "not a ranking",
        "not demand proof",
        "not platform coverage verification",
    ):
        assert term in normalized


def test_github_upload_checklist_mentions_watchlist_sample_archive_guard() -> None:
    text = _read(UPLOAD_CHECKLIST)
    normalized = _normalized_doc_text(UPLOAD_CHECKLIST)

    assert "examples/community-signals.watchlist.example.csv" in text
    assert "Package archive checks require" in text
    assert "optional watchlist sample" in normalized
```

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_first_run_guide_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack tests/test_cli_docs.py::test_github_upload_checklist_mentions_watchlist_sample_archive_guard -q
```

Expected before docs updates: fail because the docs do not mention the optional
sample yet.

- [ ] **Step 2: Update README**

Add a subsection after the automated first-run smoke section, so the default
manual flow remains a tight deterministic first-run path:

```markdown
### Optional Expanded Watchlist Sample

Use this optional local sample when you want to see the broader
`fashion-watchlist` entity pack match designer brands, named products,
categories, designers, celebrity style, and trend terms. It is separate from
the default first-run smoke and does not change generated starter configs.

```bash
tmp_watchlist="$(mktemp -d)"
AS_OF="2026-06-13T12:00:00Z"
mkdir -p "$tmp_watchlist/configs" "$tmp_watchlist/data" "$tmp_watchlist/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$tmp_watchlist/configs/entities.yaml"
cp configs/scoring.example.yaml "$tmp_watchlist/configs/scoring.yaml"

uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv run fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample"
uv run fashion-radar import-signals examples/community-signals.watchlist.example.csv --format csv --source-name "Community Watchlist Sample" --imported-at "$AS_OF" --data-dir "$tmp_watchlist/data"
uv run fashion-radar match --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data"
uv run fashion-radar report --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --reports-dir "$tmp_watchlist/reports" --as-of "$AS_OF"
uv run fashion-radar trends --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --as-of "$AS_OF" --format json
```

Expected local matches include `Khaite`, `Khaite Lotus Bag`, `Loewe`,
`Loewe Puzzle Bag`, `Jonathan Anderson`, `Bella Hadid`, `Alaia Le Teckel`,
`Miu Miu Arcadie`, `Mary Jane Shoes`, and `Boho Revival`.

The optional local sample does not fetch URLs, does not collect platform data,
does not prove demand, does not rank brands, does not verify platform coverage,
and does not add connectors.
```

- [ ] **Step 3: Update first-run and entity-pack docs**

Add this section to `docs/first-run.md` after the automated first-run smoke
description:

```markdown
## Optional Expanded Watchlist Sample

Use this optional local sample when you want to see the broader
`fashion-watchlist` entity pack match designer brands, named products,
categories, designers, celebrity style, and trend terms. It is separate from
the deterministic first-run sample and does not change generated starter
configs.

```bash
tmp_watchlist="$(mktemp -d)"
AS_OF="2026-06-13T12:00:00Z"
mkdir -p "$tmp_watchlist/configs" "$tmp_watchlist/data" "$tmp_watchlist/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$tmp_watchlist/configs/entities.yaml"
cp configs/scoring.example.yaml "$tmp_watchlist/configs/scoring.yaml"

uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv run fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample"
uv run fashion-radar import-signals examples/community-signals.watchlist.example.csv --format csv --source-name "Community Watchlist Sample" --imported-at "$AS_OF" --data-dir "$tmp_watchlist/data"
uv run fashion-radar match --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data"
uv run fashion-radar report --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --reports-dir "$tmp_watchlist/reports" --as-of "$AS_OF"
uv run fashion-radar trends --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --as-of "$AS_OF" --format json
```

Expected local matches include `Khaite`, `Khaite Lotus Bag`, `Loewe`,
`Loewe Puzzle Bag`, `Jonathan Anderson`, `Bella Hadid`, `Alaia Le Teckel`,
`Miu Miu Arcadie`, `Mary Jane Shoes`, and `Boho Revival`.

The optional local sample does not fetch URLs, does not collect platform data,
does not prove demand, does not rank brands, does not verify platform coverage,
and does not add connectors.
```

In `docs/entity-packs.md`, add a shorter `## Try The Optional Local Sample`
section after `## Use The Pack` with the same commands. Include:

```markdown
The local sample rows are synthetic. They are not a hot-list, not a ranking,
not demand proof, and not platform coverage verification.
```

- [ ] **Step 4: Update GitHub upload checklist**

In `docs/github-upload-checklist.md`, add a checklist item near the existing
package archive example checks:

```markdown
- [ ] Package archive checks require the optional watchlist sample
      [examples/community-signals.watchlist.example.csv](../examples/community-signals.watchlist.example.csv)
      as a sanitized local community-signal file for exercising the optional
      entity pack.
```

- [ ] **Step 5: Add changelog entry**

In `CHANGELOG.md` under `## [Unreleased]` / `### Added`, add:

```markdown
- Stage 77 optional expanded watchlist community-signal sample for local
  `fashion-watchlist` import, match, report, and trend walkthroughs.
```

- [ ] **Step 6: Verify docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_first_run_guide_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack tests/test_cli_docs.py::test_github_upload_checklist_mentions_watchlist_sample_archive_guard -q
```

Expected after docs updates: all pass.

## Task 6: Focused Verification And opencode Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-77-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-77-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_watchlist_community_signal_example_lints_cleanly tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_uses_allowed_fields tests/test_community_signal_import_contract.py::test_watchlist_community_signal_csv_example_loads_expected_rows tests/test_community_signal_import_contract.py::test_import_signals_dry_run_validates_watchlist_sample_without_artifacts tests/test_entity_packs.py::test_fashion_watchlist_sample_matches_expected_entities_and_types tests/test_watchlist_sample_workflow.py::test_optional_watchlist_sample_runs_local_import_match_report_and_trends tests/test_package_archives.py::test_accepts_archives_with_required_files_and_metadata tests/test_package_archives.py::test_rejects_sdist_without_watchlist_community_signal_sample tests/test_cli_docs.py::test_readme_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_first_run_guide_documents_optional_watchlist_local_sample tests/test_cli_docs.py::test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack tests/test_cli_docs.py::test_github_upload_checklist_mentions_watchlist_sample_archive_guard -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run broader touched-area verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py tests/test_entity_packs.py tests/test_watchlist_sample_workflow.py tests/test_package_archives.py tests/test_cli_docs.py
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Create and run code review prompt**

Create `docs/reviews/opencode-stage-77-code-review-prompt.md` summarizing:

- objective and scope;
- changed files;
- verification commands and results;
- boundary constraints;
- that the pre-existing `uv.lock` mirror rewrite is not part of the stage.

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-77-code-review-prompt.md)" > docs/reviews/opencode-stage-77-code-review.md
```

Fix Critical and Important findings before proceeding.

## Task 7: Full Verification, Commit, Publish, And CI

**Files:**
- Stage all Stage 77 files only.
- Do not stage the pre-existing `uv.lock` mirror rewrite.

- [ ] **Step 1: Run final verification**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
tmp_public_lock="$(mktemp)"
git show HEAD:uv.lock > "$tmp_public_lock"
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' "$tmp_public_lock"
! git diff --cached --name-only | rg -x 'uv.lock'
git diff --check
git status --short --branch
```

Expected:

- tests pass;
- ruff passes;
- public lockfile check passes and the committed/public `uv.lock` has no mirror
  URLs, verified from `HEAD:uv.lock` without reverting the unrelated worktree
  `uv.lock` change;
- only Stage 77 files are staged for commit;
- any unrelated `uv.lock` local change remains unstaged or is resolved
  separately according to `AGENTS.md`.

- [ ] **Step 2: Commit Stage 77**

Stage only:

```bash
git add examples/community-signals.watchlist.example.csv \
  tests/test_watchlist_sample_workflow.py \
  tests/test_community_signal_lint.py \
  tests/test_community_signal_import_contract.py \
  tests/test_entity_packs.py \
  scripts/check_package_archives.py \
  tests/test_package_archives.py \
  README.md docs/first-run.md docs/entity-packs.md tests/test_cli_docs.py \
  docs/github-upload-checklist.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-18-stage-77-watchlist-local-sample-design.md \
  docs/superpowers/plans/2026-06-18-stage-77-watchlist-local-sample-plan.md \
  docs/reviews/opencode-stage-77-plan-review-prompt.md \
  docs/reviews/opencode-stage-77-plan-review.md \
  docs/reviews/opencode-stage-77-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-77-plan-rereview.md \
  docs/reviews/opencode-stage-77-code-review-prompt.md \
  docs/reviews/opencode-stage-77-code-review.md
git commit -m "Add optional watchlist local sample"
```

- [ ] **Step 3: Publish with GitHub Git Data API**

Use the existing token file at
`/home/ubuntu/.config/fashion-radar/github-token`. Do not print the token and
do not store it in git remote/config. Publish the commit tree to
`Lordakee/fashion-radar` using the established GitHub Git Data API flow with
`force:false`.

- [ ] **Step 4: Verify remote and CI**

Fetch `origin/main`, align local `main` to `origin/main` if GitHub rewrites the
commit SHA but the tree matches, then wait for the GitHub Actions run for the
new remote SHA to finish successfully.

## Scope Guard

This stage must not add platform scraping, browser automation, platform APIs,
login/cookie/session/token/proxy/CAPTCHA behavior, media downloads, monitoring,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance-review product behavior.

The new sample is not a current hot-list. It is static synthetic local data
that demonstrates existing local matching and report/trend commands against an
existing optional entity pack.
