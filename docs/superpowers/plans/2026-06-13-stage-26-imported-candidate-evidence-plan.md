# Stage 26 Imported Candidate Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `fashion-radar imported-candidate-evidence`, a local read-only command that shows retained `manual_import` rows whose extracted candidate phrases match one requested phrase.

**Architecture:** Expose tiny public candidate-discovery helper wrappers so the evidence command can reuse the same candidate key and stored-entity suppression semantics as `discover_candidates()`. Add a focused `src/fashion_radar/imported_candidate_evidence.py` module that opens SQLite read-only, verifies the existing schema, extracts candidate phrases from retained `manual_import` rows, and returns a stable phrase-scoped evidence model. Add a thin Typer command plus docs and release checks.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, SQLAlchemy Core, pytest, ruff, uv.

---

## Process Gate

Implementation may start only after Claude Code approves this Stage 26 plan
review and every Critical or Important plan-review finding is resolved. After
implementation, Stage 26 code must be submitted to Claude Code for code review
before commit and push.

Do not include the existing uncommitted `uv.lock` mirror-url change in any
Stage 26 commit.

## File Structure

- Modify `src/fashion_radar/discovery/candidates.py`
  - Add public `candidate_key()` wrapper.
  - Add public `stored_entity_candidate_keys()` wrapper.
- Create `src/fashion_radar/imported_candidate_evidence.py`
  - Models: `ImportedCandidateEvidenceRow`, `ImportedCandidateEvidenceReview`
  - Helpers: `query_imported_candidate_evidence()`,
    `render_imported_candidate_evidence_table()`
  - Internal helpers: `_query_evidence_rows()`, `_evidence_row()`,
    `_table_cell()`
- Modify `src/fashion_radar/cli.py`
  - Import query/renderer.
  - Add `ImportedCandidateEvidenceOutputFormat`.
  - Add `imported-candidate-evidence` command.
- Modify `tests/test_candidate_scoring.py`
  - Helper wrapper tests.
- Create `tests/test_imported_candidate_evidence.py`
  - Unit tests for phrase evidence query and renderer.
- Modify `tests/test_cli.py`
  - CLI tests for help, JSON/table, invalid inputs, no artifacts, and no
    mutation.
- Modify docs/changelog/checklist:
  - `README.md`
  - `docs/candidate-discovery.md`
  - `docs/manual-signal-import.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/architecture.md`
  - `docs/source-boundaries.md`
  - `docs/github-upload-checklist.md`
  - `CHANGELOG.md`
- Create Claude Code Stage 26 plan/code review prompt/result files.

## Task 1: Candidate Discovery Public Helper Wrappers

**Files:**
- Modify: `src/fashion_radar/discovery/candidates.py`
- Modify: `tests/test_candidate_scoring.py`

- [ ] **Step 1: Write failing helper tests**

In `tests/test_candidate_scoring.py`, update the candidate import:

```python
from fashion_radar.discovery.candidates import (
    candidate_key,
    discover_candidates,
    stored_entity_candidate_keys,
)
```

Add:

```python
def test_candidate_key_uses_candidate_discovery_normalization() -> None:
    assert candidate_key("Le Teckel's Bag") == "le teckel bag"
```

Add:

```python
def test_stored_entity_candidate_keys_matches_existing_confidence_and_as_of_rules(
    tmp_path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    accepted_id = _store(
        engine,
        title="Ghost mule current mention",
        url="https://example.com/accepted",
        collected_at=AS_OF - timedelta(hours=1),
    )
    future_id = _store(
        engine,
        title="Future bag current mention",
        url="https://example.com/future",
        collected_at=AS_OF + timedelta(days=1),
    )
    repository.replace_item_matches(
        accepted_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 0.8,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    repository.replace_item_matches(
        future_id,
        [
            {
                "entity_name": "Future",
                "entity_type": "product",
                "alias": "Future",
                "confidence": 0.9,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )

    keys = stored_entity_candidate_keys(
        engine,
        min_match_confidence=0.5,
        as_of=AS_OF,
    )

    assert "ghost" in keys
    assert "future" not in keys
```

- [ ] **Step 2: Run helper tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py -q -k "candidate_key or stored_entity_candidate_keys"
```

Expected: fail because public helper wrappers do not exist.

- [ ] **Step 3: Implement helper wrappers**

In `src/fashion_radar/discovery/candidates.py`, add:

```python
def candidate_key(value: str) -> str:
    return _candidate_key(value)


def stored_entity_candidate_keys(
    engine: Engine,
    *,
    min_match_confidence: float,
    as_of: datetime,
) -> set[str]:
    return _stored_entity_keys(
        engine,
        min_match_confidence=min_match_confidence,
        as_of=parse_datetime_utc(as_of),
    )
```

- [ ] **Step 4: Run helper tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py -q -k "candidate_key or stored_entity_candidate_keys"
```

Expected: helper tests pass.

## Task 2: Imported Candidate Evidence Query And Renderer

**Files:**
- Create: `src/fashion_radar/imported_candidate_evidence.py`
- Create: `tests/test_imported_candidate_evidence.py`

- [ ] **Step 1: Write failing evidence tests**

Create `tests/test_imported_candidate_evidence.py` with fixtures that create a
local SQLite database, insert `manual_import` and RSS rows, and call
`query_imported_candidate_evidence()`.

Required tests:

```python
def test_query_imported_candidate_evidence_missing_database_returns_empty_without_creating_dir(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "fashion-radar.sqlite"

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert result.database == str(db_path)
    assert result.phrase == "Le Teckel bag"
    assert result.source_type == "manual_import"
    assert result.row_count == 0
    assert result.total_count == 0
    assert result.evidence == []
    assert not db_path.parent.exists()
```

```python
def test_query_imported_candidate_evidence_filters_manual_rows_source_and_windows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    current_id = _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/current",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    baseline_id = _store_item(
        repository,
        title="Le Teckel bag baseline mention",
        url="https://example.com/baseline",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=10),
    )
    _store_item(
        repository,
        title="Le Teckel bag other manual mention",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    _store_item(
        repository,
        title="Le Teckel bag RSS mention",
        url="https://example.com/rss",
        source_name="Fashionista",
        source_type=SourceType.RSS,
        collected_at=AS_OF - timedelta(hours=3),
    )
    _store_item(
        repository,
        title="Le Teckel bag future mention",
        url="https://example.com/future",
        source_name="Community Tool Export",
        collected_at=AS_OF + timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag old out-of-window mention",
        url="https://example.com/old",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(days=60),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        source_name="Community Tool Export",
    )

    assert result.total_count == 2
    assert result.row_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.distinct_sources == 1
    assert [row.id for row in result.evidence] == [current_id, baseline_id]
    assert [row.window for row in result.evidence] == ["current", "baseline"]
```

```python
def test_query_imported_candidate_evidence_blank_source_name_is_no_filter(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag community mention",
        url="https://example.com/community",
        source_name="Community Tool Export",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag manual mention",
        url="https://example.com/manual",
        source_name="Manual Export",
        collected_at=AS_OF - timedelta(hours=2),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        source_name="   ",
    )

    assert result.source_name is None
    assert result.total_count == 2
    assert result.current_mentions == 2
```

```python
def test_query_imported_candidate_evidence_limit_zero_preserves_counts(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/current",
        collected_at=AS_OF - timedelta(hours=1),
    )
    _store_item(
        repository,
        title="Le Teckel bag baseline mention",
        url="https://example.com/baseline",
        collected_at=AS_OF - timedelta(days=10),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
        limit=0,
    )

    assert result.row_count == 0
    assert result.total_count == 2
    assert result.current_mentions == 1
    assert result.baseline_mentions == 1
    assert result.evidence == []
```

```python
def test_query_imported_candidate_evidence_uses_candidate_extraction_not_substring(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Teckel shaped clasp appears",
        url="https://example.com/noise",
        collected_at=AS_OF - timedelta(hours=1),
    )
    expected_id = _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://example.com/match",
        collected_at=AS_OF - timedelta(hours=2),
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert [row.id for row in result.evidence] == [expected_id]
```

```python
def test_query_imported_candidate_evidence_uses_readonly_engine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    engine.dispose()
    calls: list[Path] = []
    original = imported_candidate_evidence_module.create_readonly_sqlite_engine

    def wrapped_create_readonly_sqlite_engine(path: Path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(
        imported_candidate_evidence_module,
        "create_readonly_sqlite_engine",
        wrapped_create_readonly_sqlite_engine,
    )

    query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )

    assert calls == [db_path]
```

```python
def test_query_imported_candidate_evidence_suppresses_known_entities(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Margaux bag current mention",
        url="https://example.com/configured",
        collected_at=AS_OF - timedelta(hours=1),
    )
    stored_id = _store_item(
        repository,
        title="Ghost mule current mention",
        url="https://example.com/stored",
        collected_at=AS_OF - timedelta(hours=2),
    )
    repository.replace_item_matches(
        stored_id,
        [
            {
                "entity_name": "Ghost",
                "entity_type": "product",
                "alias": "Ghost",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            }
        ],
    )
    engine.dispose()

    entity_config = EntityConfig(
        entities=[
            EntityDefinition(
                name="Margaux",
                type=EntityType.PRODUCT,
                aliases=[{"value": "Margaux"}],
                context_terms=["bag"],
            )
        ]
    )
    for phrase in ("Margaux bag", "Ghost mule"):
        result = query_imported_candidate_evidence(
            db_path,
            scoring=ScoringSettings(),
            settings=CandidateDiscoverySettings(
                min_current_mentions=1,
                review_min_current_mentions=1,
            ),
            entity_config=entity_config,
            as_of=AS_OF,
            phrase=phrase,
        )
        assert result.evidence == []
```

```python
def test_imported_candidate_evidence_json_shape_omits_summary_and_match_fields(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "fashion-radar.sqlite"
    engine = create_sqlite_engine(db_path)
    initialize_schema(engine)
    repository = ItemRepository(engine)
    _store_item(
        repository,
        title="Le Teckel bag current mention",
        url="https://private.example.com/local-path",
        collected_at=AS_OF - timedelta(hours=1),
        summary="raw private review note",
    )
    engine.dispose()

    result = query_imported_candidate_evidence(
        db_path,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=AS_OF,
        phrase="Le Teckel bag",
    )
    payload = result.model_dump(mode="json")

    assert list(payload) == [
        "database",
        "as_of",
        "phrase",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_type",
        "source_name",
        "limit",
        "row_count",
        "total_count",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "evidence",
    ]
    assert list(payload["evidence"][0]) == [
        "id",
        "window",
        "source_name",
        "title",
        "url",
        "published_at",
        "collected_at",
    ]
    forbidden = {
        "summary",
        "contexts",
        "normalized_phrase",
        "normalized_key",
        "normalized_url",
        "matches",
        "match_status",
        "source_file",
        "source_path",
        "import_path",
        "raw_comment",
        "account_id",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["evidence"][0])
```

```python
def test_render_imported_candidate_evidence_table_sanitizes_display_cells() -> None:
    review = ImportedCandidateEvidenceReview(
        database="data/fashion-radar.sqlite",
        as_of="2026-06-13T12:00:00+00:00",
        phrase="Le Teckel | bag",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        row_count=1,
        total_count=1,
        current_mentions=1,
        baseline_mentions=0,
        distinct_sources=1,
        evidence=[
            ImportedCandidateEvidenceRow(
                id=7,
                window="current",
                source_name="Community | Export",
                title="Le Teckel\nbag",
                url="https://example.com/a|b",
                published_at="2026-06-13T10:00:00+00:00",
                collected_at="2026-06-13T11:00:00+00:00",
            )
        ],
    )

    lines = render_imported_candidate_evidence_table(review)

    assert "Phrase: Le Teckel / bag" in lines
    assert (
        "current | 7 | 2026-06-13T11:00:00+00:00 | Community / Export | "
        "Le Teckel bag | https://example.com/a/b"
    ) in lines
```

- [ ] **Step 2: Run evidence tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_candidate_evidence.py -q
```

Expected: fail because `fashion_radar.imported_candidate_evidence` does not
exist.

- [ ] **Step 3: Implement evidence module**

Create `src/fashion_radar/imported_candidate_evidence.py`.

Core model fields:

```python
class ImportedCandidateEvidenceRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    window: Literal["current", "baseline"]
    source_name: str
    title: str
    url: str
    published_at: str
    collected_at: str


class ImportedCandidateEvidenceReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    as_of: str
    phrase: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_type: Literal["manual_import"] = "manual_import"
    source_name: str | None = None
    limit: int | None = 20
    row_count: int = 0
    total_count: int = 0
    current_mentions: int = 0
    baseline_mentions: int = 0
    distinct_sources: int = 0
    evidence: list[ImportedCandidateEvidenceRow] = Field(default_factory=list)
```

Core query behavior:

- reject negative `limit`;
- reject blank `phrase`;
- normalize `as_of` and phrase;
- missing DB returns empty review without creating the parent dir;
- open existing DB via `create_readonly_sqlite_engine()`;
- call `verify_imported_signals_schema(engine)`;
- if candidate discovery is disabled, return empty review;
- build known keys from `configured_entity_keys()` and
  `stored_entity_candidate_keys()`;
- read rows from `items` where `source_type == "manual_import"` and optional
  exact `source_name`;
- normalize blank `source_name` to `None` before applying the optional exact
  source-name filter;
- classify retained rows where `baseline_start < collected_at <= as_of`. In the
  current schema, retained means the row still exists in `items`; Stage 26
  applies the same review-window boundary as Stage 25 candidate discovery, so
  older out-of-window rows and future rows are excluded;
- call `extract_candidate_phrases()` on title plus summary with known keys and
  settings;
- include rows whose extracted candidate normalized key equals
  `normalized_phrase`;
- order evidence by current rows first, then collected_at descending, then id
  descending;
- compute counts before applying `limit`;
- return evidence rows after `limit`.

- [ ] **Step 4: Run evidence tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_imported_candidate_evidence.py -q
```

Expected: evidence tests pass.

## Task 3: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add CLI tests near existing imported candidate tests:

- `test_imported_candidate_evidence_command_help_lists_options`
- `test_imported_candidate_evidence_command_prints_json_with_stable_keys`
- `test_imported_candidate_evidence_command_prints_table`
- `test_imported_candidate_evidence_command_requires_phrase`
- `test_imported_candidate_evidence_command_rejects_blank_phrase_without_query`
- `test_imported_candidate_evidence_command_rejects_invalid_as_of_without_query`
- `test_imported_candidate_evidence_command_rejects_invalid_format_without_query`
- `test_imported_candidate_evidence_command_rejects_negative_limit_without_query`
- `test_imported_candidate_evidence_command_blank_source_name_is_no_filter`
- `test_imported_candidate_evidence_command_missing_database_is_read_only`
- `test_imported_candidate_evidence_command_invalid_schema_no_traceback`
- `test_imported_candidate_evidence_command_does_not_mutate_existing_database`

Reuse the Stage 25 imported-candidates fixture style and assert JSON does not
include `summary`, `contexts`, `matches`, `match_status`, `source_file`,
`source_path`, `import_path`, or account/raw fields.

- [ ] **Step 2: Run CLI tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_candidate_evidence"
```

Expected: fail because `imported-candidate-evidence` is not registered.

- [ ] **Step 3: Implement CLI command**

In `src/fashion_radar/cli.py`:

- import `query_imported_candidate_evidence` and
  `render_imported_candidate_evidence_table`;
- add `ImportedCandidateEvidenceOutputFormat = Literal["table", "json"]`;
- add `IMPORTED_CANDIDATE_EVIDENCE_AS_OF_OPTION` and
  `IMPORTED_CANDIDATE_EVIDENCE_FORMAT_OPTION`;
- add:

```python
@app.command(name="imported-candidate-evidence")
def imported_candidate_evidence_command(...):
    """Review retained imported rows behind one candidate phrase."""
```

The command must:

- parse `--as-of` before query execution;
- reject blank `--phrase` before query execution;
- load scoring config and optional entity config;
- call `query_imported_candidate_evidence(default_database_path(data_dir), ...)`;
- print JSON with `review.model_dump_json(indent=2)` or table lines.

- [ ] **Step 4: Run CLI tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k "imported_candidate_evidence"
```

Expected: CLI tests pass.

## Task 4: Documentation And Changelog

**Files:**
- Modify: `README.md`
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add bounded command examples**

Add examples near existing imported candidate review examples:

```bash
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --phrase "Le Teckel bag" --source-name "Community Tool Export" --format json
```

Use wording:

```markdown
`imported-candidate-evidence` is local and read-only. It shows retained
`manual_import` rows whose extracted candidate phrases match one requested
phrase. Evidence rows are review aids and are not verified entities, demand
proof, or platform/community coverage.
```

- [ ] **Step 2: Update upload checklist**

Add installed-wheel smoke:

```bash
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --data-dir "$tmp_run/data" --config-dir "$tmp_run/config" --as-of "2026-06-13T12:00:00Z" --phrase "Le Teckel bag" --format json
```

- [ ] **Step 3: Update changelog**

Add under `### Added`:

```markdown
- Local read-only `imported-candidate-evidence` command for reviewing retained
  `manual_import` rows behind one imported candidate phrase.
```

- [ ] **Step 4: Run docs boundary scan**

Run:

```bash
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

Expected: no new capability wording from Stage 26 product docs.

## Task 5: Review, Verification, And Release

**Files:**
- Create: `docs/reviews/claude-code-stage-26-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-26-code-review.md`
- Modify: any file needed to fix Critical or Important review findings

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py tests/test_imported_candidate_evidence.py tests/test_cli.py -q -k "candidate_key or stored_entity_candidate_keys or imported_candidate_evidence"
.venv/bin/python -m pytest tests/test_imported_candidates.py tests/test_reports.py tests/test_trends.py tests/test_dashboard.py -q -k "imported_candidates or candidate or trend or build_daily_report"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-26-code-review-prompt.md` asking Claude
Code to review the current working tree in read-only mode. Required review
focus:

- candidate evidence uses candidate extraction and normalized candidate keys,
  not naive substring matching;
- default candidate discovery behavior remains unchanged;
- evidence command is read-only and missing DB creates no dirs/files;
- evidence reads retained `manual_import` rows only;
- evidence output intentionally includes `title` and `url` for one requested
  phrase but omits summaries, contexts, match internals, raw fields, import
  paths, account/private fields, and hidden review text;
- invalid CLI inputs avoid query execution where appropriate;
- docs remain local and do not imply verified entities, demand proof, external
  coverage, source ranking, source quality, scraping, monitoring, or
  acquisition.

Run:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-26-code-review-prompt.md | tee docs/reviews/claude-code-stage-26-code-review.md
```

Fix every Critical and Important finding before continuing.

- [ ] **Step 3: Run full release checks**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
uv lock --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git status --short
git diff -- uv.lock
rm -rf /tmp/fashion-radar-dist-stage26
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage26
```

Expected: all checks pass. If current `uv.lock` still shows the pre-existing
mirror-url diff, run the lock check in a temporary clean worktree as in Stage 25,
then leave `uv.lock` unstaged and excluded from the Stage 26 commit.

- [ ] **Step 4: Run installed-wheel smoke**

Run:

```bash
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv" --python 3.11
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmp_env/venv/bin/python" /tmp/fashion-radar-dist-stage26/*.whl
mkdir -p "$tmp_env/config"
printf 'version: 1\nscoring: {}\ncandidate_discovery:\n  min_current_mentions: 1\n  review_min_current_mentions: 1\n' > "$tmp_env/config/scoring.yaml"
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --help
"$tmp_env/venv/bin/fashion-radar" imported-candidate-evidence --data-dir "$tmp_env/data" --config-dir "$tmp_env/config" --as-of "2026-06-13T12:00:00Z" --phrase "Le Teckel bag" --format json
```

Expected: both commands exit zero. The JSON command returns an empty evidence
review because the database is missing, and it does not create SQLite.

- [ ] **Step 5: Run repository hygiene scans**

Run:

```bash
rg -n "ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]+" . --glob '!uv.lock' --glob '!*.pyc' --glob '!__pycache__/**' --glob '!.venv/**' --glob '!data/**' --glob '!reports/**' --glob '!.codegraph/**'
find . \( -name '*.sqlite' -o -name '*.sqlite-*' -o -name '*.sqlite3' -o -name '*.db' -o -name '*.pyc' -o -name '__pycache__' -o -name 'dist' -o -name 'build' -o -name '*.egg-info' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -not -path './.venv/*' -not -path './.git/*' -not -path './.codegraph/*' -print
```

Expected: no secrets or generated artifacts that should be committed.

- [ ] **Step 6: Commit and push**

This repository is currently using the user-authorized direct-main upload
workflow. Do this step only after Claude Code code review has no Critical or
Important findings and all release checks pass.

Run:

```bash
current_branch="$(git branch --show-current)"
if [ "$current_branch" != "main" ]; then
  echo "Not on main; stop and adapt push target."
  exit 1
fi
git status --short --branch
git add src/fashion_radar/discovery/candidates.py src/fashion_radar/imported_candidate_evidence.py src/fashion_radar/cli.py tests/test_candidate_scoring.py tests/test_imported_candidate_evidence.py tests/test_cli.py README.md docs CHANGELOG.md
git commit -m "Add imported candidate evidence command"
git -c http.version=HTTP/1.1 -c http.curloptResolve=github.com:443:140.82.113.4 push origin main
```

Expected: branch is `main`, commit succeeds, and push updates `origin/main`.

Do not stage or commit `uv.lock` unless a later approved plan explicitly changes
dependencies or lockfile content.
