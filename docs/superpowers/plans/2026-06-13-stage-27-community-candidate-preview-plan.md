# Stage 27A Community Candidate Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `fashion-radar community-candidates`, a local read-only command that previews aggregate candidate phrases from one user-supplied community signal CSV/JSON file before import.

**Architecture:** Add a focused `community_candidates.py` module that loads rows through the existing manual signal importer, extracts candidate phrases with existing candidate extraction settings, aggregates in-memory mentions over current/baseline windows, and renders table/JSON output without exposing file paths or row-level data. Add a Typer command that validates `--as-of` before config/file access, lets Typer reject invalid format/limit before command execution, loads local config before reading the input file, and prints the module output without opening SQLite or writing artifacts.

**Tech Stack:** Python 3.11, Typer, Pydantic, existing `load_manual_signal_rows()`, existing `extract_candidate_phrases()`, existing `configured_entity_keys()`, existing scoring/entity config models, pytest, ruff.

---

## Stage 27A Boundary

Stage 27A includes implementation and focused tests only.

In scope:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`

Out of scope for this node:

- README or broad docs updates;
- release verification, wheel build, installed-wheel smoke;
- Claude Code code-review prompt generation;
- commit and push;
- any `uv.lock` change.

Follow-up nodes can handle docs, final code review, release verification, commit,
and push after Stage 27A implementation passes focused tests.

## File Map

- Create `src/fashion_radar/community_candidates.py`: output models, preview aggregation helper, local scoring/label helper, table renderer.
- Modify `src/fashion_radar/cli.py`: import the new helper, add output format type/options, add `community-candidates` command.
- Create `tests/test_community_candidates.py`: module tests for parsing, aggregation, thresholds, output safety, and table rendering.
- Modify `tests/test_cli.py`: CLI tests for help, JSON/table output, validation order, clean errors, and artifact absence.
- Do not modify or stage `uv.lock`.

## Task 1: Module Tests For Local Candidate Preview

**Files:**
- Create: `tests/test_community_candidates.py`
- Do not modify production code in this task.

- [ ] **Step 1: Write failing module tests and helpers**

Create `tests/test_community_candidates.py`:

```python
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fashion_radar.community_candidates import (
    CommunityCandidatePreview,
    preview_community_candidates,
    render_community_candidates_table,
)
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings

AS_OF = datetime(2026, 6, 13, 12, 0, tzinfo=UTC)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = [
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    ]
    lines = [",".join(headers)]
    for row in rows:
        values = [json.dumps(row.get(header, ""))[1:-1] for header in headers]
        lines.append(",".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _preview(
    path: Path,
    *,
    settings: CandidateDiscoverySettings | None = None,
    scoring: ScoringSettings | None = None,
    entity_config: EntityConfig | None = None,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidatePreview:
    return preview_community_candidates(
        path,
        input_format="csv",
        scoring=scoring or ScoringSettings(),
        settings=settings
        or CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
        entity_config=entity_config,
        as_of=AS_OF,
        default_source_name=default_source_name,
        limit=limit,
    )


def _serialized(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
```

- [ ] **Step 2: Add current/baseline aggregation test**

Append:

```python
def test_preview_community_candidates_counts_current_baseline_and_sources(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current-a",
                "title": "Le Teckel bag spotted",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community A",
                "source_weight": "1.5",
                "collected_at": "2026-06-13T10:00:00Z",
            },
            {
                "url": "https://example.com/current-b",
                "title": "Le Teckel bag street style",
                "published_at": "2026-06-12T09:00:00Z",
                "source_name": "Community B",
                "source_weight": "1",
                "collected_at": "2026-06-12T10:00:00Z",
            },
            {
                "url": "https://example.com/baseline",
                "title": "Le Teckel bag early mention",
                "published_at": "2026-06-01T09:00:00Z",
                "source_name": "Community A",
                "source_weight": "1",
                "collected_at": "2026-06-01T10:00:00Z",
            },
        ],
    )

    preview = _preview(path)

    assert preview.input_format == "csv"
    assert preview.row_count == 3
    assert preview.candidate_count >= 1
    candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")
    assert candidate.current_mentions == 2
    assert candidate.baseline_mentions == 1
    assert candidate.distinct_sources == 2
    assert candidate.growth_ratio is not None
    assert candidate.score > 0
```

- [ ] **Step 3: Add fallback, known-entity, duplicate, threshold, and disabled tests**

Append:

```python
def test_preview_community_candidates_uses_as_of_for_missing_collected_at(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Slim sneaker appears",
                "published_at": "2026-06-10T09:00:00Z",
                "source_name": "",
            }
        ],
    )

    preview = _preview(path, default_source_name="   ")

    assert preview.source_name == "Community Tool Export"
    assert preview.row_count == 1
    assert preview.candidates[0].first_seen_at == AS_OF.isoformat()
    assert preview.candidates[0].distinct_sources == 1


def test_preview_community_candidates_suppresses_configured_entities(tmp_path: Path) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/margaux",
                "title": "Margaux bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )
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

    preview = _preview(path, entity_config=entity_config)

    assert preview.candidates == []


def test_preview_community_candidates_counts_duplicate_phrase_once_per_row(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/repeated",
                "title": "Le Teckel bag Le Teckel bag Le Teckel bag",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path)
    candidate = next(item for item in preview.candidates if item.phrase == "Le Teckel bag")

    assert candidate.current_mentions == 1


def test_preview_community_candidates_review_thresholds_filter_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(
        path,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=2,
            review_min_distinct_sources=1,
            min_single_token_mentions=1,
            min_single_token_distinct_sources=1,
        ),
    )

    assert preview.row_count == 1
    assert preview.candidate_count == 0
    assert preview.candidates == []


def test_preview_community_candidates_single_token_threshold_filters_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Orion",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(
        path,
        settings=CandidateDiscoverySettings(
            review_min_current_mentions=1,
            review_min_distinct_sources=1,
            min_single_token_mentions=2,
            min_single_token_distinct_sources=1,
        ),
    )

    assert preview.candidate_count == 0
    assert preview.candidates == []


def test_preview_community_candidates_disabled_returns_rows_without_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path, settings=CandidateDiscoverySettings(enabled=False))

    assert preview.row_count == 1
    assert preview.candidate_count == 0
    assert preview.candidates == []
```

- [ ] **Step 4: Add limit and recursive output safety tests**

Append:

```python
def test_preview_community_candidates_limit_zero_preserves_candidate_count(
    tmp_path: Path,
) -> None:
    path = tmp_path / "community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://example.com/current",
                "title": "Le Teckel bag current mention",
                "published_at": "2026-06-13T09:00:00Z",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path, limit=0)

    assert preview.row_count == 1
    assert preview.candidate_count == 1
    assert preview.candidates == []


def test_preview_community_candidates_output_omits_paths_raw_values_and_internals(
    tmp_path: Path,
) -> None:
    path = tmp_path / "private-community.csv"
    _write_csv(
        path,
        [
            {
                "url": "https://private.example.com/local-path",
                "title": "Le Teckel bag current mention",
                "published_at": "2026-06-13T09:00:00Z",
                "summary": "raw private review note",
                "source_name": "Community",
                "collected_at": "2026-06-13T10:00:00Z",
            }
        ],
    )

    preview = _preview(path)
    payload = preview.model_dump(mode="json")
    serialized = _serialized(payload)
    table = "\n".join(render_community_candidates_table(preview))

    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert list(payload["candidates"][0]) == [
        "phrase",
        "candidate_type",
        "label",
        "score",
        "current_mentions",
        "baseline_mentions",
        "distinct_sources",
        "growth_ratio",
        "first_seen_at",
    ]

    forbidden_fragments = {
        str(path),
        path.name,
        "https://private.example.com/local-path",
        "current mention",
        "raw private review note",
        "normalized_key",
        "normalized_phrase",
        "contexts",
        "representative_items",
        "source_file",
        "source_path",
        "import_path",
        "account_id",
    }
    for fragment in forbidden_fragments:
        assert fragment not in serialized
        assert fragment not in table
```

- [ ] **Step 5: Add table sanitization test**

Append:

```python
def test_render_community_candidates_table_sanitizes_cells() -> None:
    preview = CommunityCandidatePreview(
        input_format="csv",
        as_of="2026-06-13T12:00:00+00:00",
        current_window_start="2026-06-06T12:00:00+00:00",
        baseline_window_start="2026-05-07T12:00:00+00:00",
        source_name="Community | Export",
        row_count=1,
        candidate_count=1,
        candidates=[
            {
                "phrase": "Le Teckel | bag\nprivate",
                "candidate_type": "product",
                "label": "new",
                "score": 1.0,
                "current_mentions": 1,
                "baseline_mentions": 0,
                "distinct_sources": 1,
                "growth_ratio": None,
                "first_seen_at": "2026-06-13T10:00:00+00:00",
            }
        ],
    )

    lines = render_community_candidates_table(preview)
    rendered = "\n".join(lines)

    assert "Source name: Community / Export" in rendered
    assert "Le Teckel / bag private" in rendered
```

- [ ] **Step 6: Run module tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_candidates.py -q
```

Expected: fail because `fashion_radar.community_candidates` does not exist yet.

## Task 2: Implement `community_candidates.py`

**Files:**
- Create: `src/fashion_radar/community_candidates.py`
- Test: `tests/test_community_candidates.py`

- [ ] **Step 1: Add output models and local mention type**

Create `src/fashion_radar/community_candidates.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.discovery.candidates import (
    configured_entity_keys,
    extract_candidate_phrases,
)
from fashion_radar.importers.manual_signals import ManualSignalFormat, load_manual_signal_rows
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc


class CommunityCandidateRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: Literal["new", "rising", "observed"]
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: str


class CommunityCandidatePreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_format: ManualSignalFormat
    as_of: str
    current_window_start: str
    baseline_window_start: str
    current_days: int = 7
    baseline_days: int = 30
    source_name: str = "Community Tool Export"
    row_count: int = 0
    candidate_count: int = 0
    limit: int | None = 50
    candidates: list[CommunityCandidateRow] = Field(default_factory=list)


@dataclass(frozen=True)
class _PreviewMention:
    normalized_key: str
    phrase: str
    candidate_type: str
    source_name: str
    source_weight: float
    collected_at: datetime
```

- [ ] **Step 2: Add preview helper**

Append:

```python
def preview_community_candidates(
    path: Path,
    *,
    input_format: ManualSignalFormat,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: str | datetime,
    default_source_name: str = "Community Tool Export",
    limit: int | None = 50,
) -> CommunityCandidatePreview:
    if limit is not None and limit < 0:
        raise ValueError("limit must be at least 0")
    as_of_value = parse_datetime_utc(as_of)
    current_window_start = as_of_value - timedelta(days=scoring.current_window_days)
    baseline_window_start = current_window_start - timedelta(days=scoring.baseline_window_days)
    source_name = default_source_name.strip() or "Community Tool Export"
    rows = load_manual_signal_rows(
        path,
        input_format=input_format,
        default_source_name=source_name,
    )
    preview_base = {
        "input_format": input_format,
        "as_of": as_of_value.isoformat(),
        "current_window_start": current_window_start.isoformat(),
        "baseline_window_start": baseline_window_start.isoformat(),
        "current_days": scoring.current_window_days,
        "baseline_days": scoring.baseline_window_days,
        "source_name": source_name,
        "row_count": len(rows),
        "limit": limit,
    }
    if not settings.enabled:
        return CommunityCandidatePreview(**preview_base)

    known_keys = configured_entity_keys(entity_config, as_of=as_of_value)
    mentions: list[_PreviewMention] = []
    for row in rows:
        collected_at = parse_datetime_utc(row.collected_at or as_of_value)
        if not (baseline_window_start < collected_at <= as_of_value):
            continue
        text = " ".join(value for value in (row.title, row.summary) if isinstance(value, str))
        seen_row_keys: set[str] = set()
        for phrase in extract_candidate_phrases(
            text,
            source_name=row.source_name,
            known_keys=known_keys,
            settings=settings,
        ):
            if phrase.normalized_key in seen_row_keys:
                continue
            seen_row_keys.add(phrase.normalized_key)
            mentions.append(
                _PreviewMention(
                    normalized_key=phrase.normalized_key,
                    phrase=phrase.phrase,
                    candidate_type=phrase.candidate_type,
                    source_name=row.source_name,
                    source_weight=row.source_weight,
                    collected_at=collected_at,
                )
            )

    candidates = _score_preview_mentions(
        mentions,
        scoring=scoring,
        settings=settings,
        current_window_start=current_window_start,
    )
    visible_candidates = candidates[:limit] if limit is not None else candidates
    return CommunityCandidatePreview(
        **preview_base,
        candidate_count=len(candidates),
        candidates=visible_candidates,
    )
```

- [ ] **Step 3: Add scoring and rendering helpers**

Append:

```python
def _score_preview_mentions(
    mentions: list[_PreviewMention],
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    current_window_start: datetime,
) -> list[CommunityCandidateRow]:
    by_key: dict[str, list[_PreviewMention]] = {}
    for mention in mentions:
        by_key.setdefault(mention.normalized_key, []).append(mention)

    candidates: list[CommunityCandidateRow] = []
    for candidate_mentions in by_key.values():
        current_mentions = [
            mention for mention in candidate_mentions if mention.collected_at > current_window_start
        ]
        if not current_mentions:
            continue
        baseline_mentions = [
            mention for mention in candidate_mentions if mention.collected_at <= current_window_start
        ]
        current_count = len(current_mentions)
        distinct_sources = len({mention.source_name for mention in current_mentions})
        if current_count < settings.review_min_current_mentions:
            continue
        if distinct_sources < settings.review_min_distinct_sources:
            continue
        key = current_mentions[0].normalized_key
        if len(key.split()) == 1 and (
            current_count < settings.min_single_token_mentions
            or distinct_sources < settings.min_single_token_distinct_sources
        ):
            continue
        baseline_count = len(baseline_mentions)
        current_rate = current_count / scoring.current_window_days
        baseline_rate = baseline_count / scoring.baseline_window_days if baseline_count else 0
        growth_ratio = current_rate / baseline_rate if baseline_rate > 0 else None
        weighted_current_mentions = sum(mention.source_weight for mention in current_mentions)
        score = (
            weighted_current_mentions * scoring.weighted_mentions_7d
            + max(0, distinct_sources - 1) * scoring.source_diversity_bonus
            + (max(0.0, growth_ratio - 1) * scoring.growth_bonus if growth_ratio else 0.0)
        )
        ordered_current = sorted(current_mentions, key=lambda mention: mention.collected_at, reverse=True)
        all_mentions = [*current_mentions, *baseline_mentions]
        candidates.append(
            CommunityCandidateRow(
                phrase=ordered_current[0].phrase,
                candidate_type=ordered_current[0].candidate_type,
                label=_preview_label(
                    baseline_count=baseline_count,
                    growth_ratio=growth_ratio,
                    settings=settings,
                ),
                score=score,
                current_mentions=current_count,
                baseline_mentions=baseline_count,
                distinct_sources=distinct_sources,
                growth_ratio=growth_ratio,
                first_seen_at=min(mention.collected_at for mention in all_mentions).isoformat(),
            )
        )

    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate.score,
            -candidate.current_mentions,
            -candidate.distinct_sources,
            candidate.phrase.lower(),
        ),
    )


def _preview_label(
    *,
    baseline_count: int,
    growth_ratio: float | None,
    settings: CandidateDiscoverySettings,
) -> Literal["new", "rising", "observed"]:
    if baseline_count == 0:
        return "new"
    if growth_ratio is not None and growth_ratio >= settings.rising_growth_ratio:
        return "rising"
    return "observed"


def render_community_candidates_table(preview: CommunityCandidatePreview) -> list[str]:
    lines = [
        "Community candidate preview from one local handoff file.",
        "Candidate signals are aggregate observed phrases from the supplied file only.",
        f"Input format: {preview.input_format}",
        f"Current window: {preview.current_window_start} < collected_at <= {preview.as_of}",
        (
            f"Baseline window: {preview.baseline_window_start} < collected_at <= "
            f"{preview.current_window_start}"
        ),
        f"Source name: {_table_cell(preview.source_name)}",
        f"Rows: {preview.row_count}",
        f"Candidates: {len(preview.candidates)} shown, {preview.candidate_count} total",
    ]
    if not preview.candidates:
        lines.append("No community candidate signals found.")
        return lines
    lines.append(
        "Phrase | Type | Label | Score | Current Mentions | Baseline Mentions | "
        "Distinct Sources | First Seen At"
    )
    for candidate in preview.candidates:
        lines.append(
            f"{_table_cell(candidate.phrase)} | {_table_cell(candidate.candidate_type)} | "
            f"{candidate.label} | {candidate.score:.2f} | {candidate.current_mentions} | "
            f"{candidate.baseline_mentions} | {candidate.distinct_sources} | "
            f"{candidate.first_seen_at}"
        )
    return lines


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
```

- [ ] **Step 4: Run module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_candidates.py -q
```

Expected: all module tests pass.

## Task 3: CLI Tests For Command And Validation Order

**Files:**
- Modify: `tests/test_cli.py`
- Do not modify production code in this task.

- [ ] **Step 1: Add CLI fixture helper and JSON/table/help tests**

Append to `tests/test_cli.py`:

```python
def _prepare_community_candidates_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
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
    data_dir = tmp_path / "data"
    path = tmp_path / "private-community.csv"
    path.write_text(
        "url,title,published_at,source_name,collected_at\n"
        "https://private.example.com/a,Le Teckel bag mention,"
        "2026-06-13T09:00:00Z,Community,2026-06-13T10:00:00Z\n",
        encoding="utf-8",
    )
    return config_dir, data_dir, path
```

Append:

```python
def test_community_candidates_help_lists_command() -> None:
    result = CliRunner().invoke(app, ["community-candidates", "--help"])

    assert result.exit_code == 0
    assert "--as-of" in result.output
    assert "--input-format" in result.output
    assert "--format" in result.output


def test_community_candidates_command_prints_json_without_paths_or_raw_values(
    tmp_path: Path,
) -> None:
    config_dir, data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--input-format",
            "csv",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert list(payload) == [
        "input_format",
        "as_of",
        "current_window_start",
        "baseline_window_start",
        "current_days",
        "baseline_days",
        "source_name",
        "row_count",
        "candidate_count",
        "limit",
        "candidates",
    ]
    assert payload["row_count"] == 1
    assert payload["candidate_count"] == 1
    assert payload["candidates"][0]["phrase"] == "Le Teckel bag"
    serialized = json.dumps(payload, sort_keys=True)
    assert str(path) not in serialized
    assert path.name not in serialized
    assert "https://private.example.com/a" not in serialized
    assert "mention" not in payload["candidates"][0]
    assert not (data_dir / "fashion-radar.sqlite").exists()


def test_community_candidates_command_prints_table_without_path(tmp_path: Path) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Community candidate preview from one local handoff file." in result.output
    assert "Le Teckel bag" in result.output
    assert str(path) not in result.output
    assert path.name not in result.output
```

- [ ] **Step 2: Add validation-order tests**

Append:

```python
def test_community_candidates_invalid_as_of_does_not_load_config_or_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_load_config(*args, **kwargs):
        raise AssertionError("config should not be loaded")

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr("fashion_radar.cli.load_scoring_config", fail_load_config)
    monkeypatch.setattr("fashion_radar.cli.preview_community_candidates", fail_preview)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "invalid --as-of" in result.output


def test_community_candidates_invalid_format_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr("fashion_radar.cli.preview_community_candidates", fail_preview)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--input-format",
            "xml",
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_negative_limit_does_not_enter_command_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr("fashion_radar.cli.preview_community_candidates", fail_preview)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--limit",
            "-1",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_community_candidates_invalid_config_does_not_read_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: bad\n", encoding="utf-8")

    def fail_preview(*args, **kwargs):
        raise AssertionError("file should not be loaded")

    monkeypatch.setattr("fashion_radar.cli.preview_community_candidates", fail_preview)
    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid community candidate config" in result.output
```

- [ ] **Step 3: Add clean input-file error and artifact absence tests**

Append:

```python
def test_community_candidates_invalid_file_has_clean_error_without_path_echo(
    tmp_path: Path,
) -> None:
    config_dir, _data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    missing = path.parent / "missing-private-file.csv"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(missing),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not preview community candidates" in result.output
    assert "Traceback" not in result.output
    assert str(missing) not in result.output
    assert missing.name not in result.output


def test_community_candidates_command_does_not_create_artifacts(tmp_path: Path) -> None:
    config_dir, data_dir, path = _prepare_community_candidates_fixture(tmp_path)
    reports_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        app,
        [
            "community-candidates",
            str(path),
            "--config-dir",
            str(config_dir),
            "--as-of",
            "2026-06-13T12:00:00Z",
            "--format",
            "json",
        ],
        env={
            "FASHION_RADAR_DATA_DIR": str(data_dir),
            "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
        },
    )

    assert result.exit_code == 0
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not (tmp_path / "dashboard").exists()
```

- [ ] **Step 4: Run CLI tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q -k community_candidates
```

Expected: fail because CLI command is missing.

## Task 4: Add CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_cli.py`, `tests/test_community_candidates.py`

- [ ] **Step 1: Add imports and type alias**

Modify `src/fashion_radar/cli.py`:

```python
from fashion_radar.community_candidates import (
    preview_community_candidates,
    render_community_candidates_table,
)
```

Add near output format aliases:

```python
CommunityCandidatesOutputFormat = Literal["table", "json"]
```

- [ ] **Step 2: Add option constants**

Add near community signal option constants:

```python
COMMUNITY_CANDIDATES_AS_OF_OPTION = typer.Option(
    ...,
    "--as-of",
    help="UTC community candidate preview timestamp, for example 2026-06-13T12:00:00Z.",
)
COMMUNITY_CANDIDATES_FORMAT_OPTION = typer.Option("table", "--format", help="Output format.")
```

- [ ] **Step 3: Add command**

Add after `community_signal_lint_dir_command`:

```python
@app.command(name="community-candidates")
def community_candidates_command(
    path: Path,
    config_dir: Path = CONFIG_DIR_OPTION,
    input_format: ManualSignalInputFormat = COMMUNITY_SIGNAL_INPUT_FORMAT_OPTION,
    as_of: str = COMMUNITY_CANDIDATES_AS_OF_OPTION,
    source_name: str = COMMUNITY_SIGNAL_SOURCE_NAME_OPTION,
    limit: int | None = typer.Option(50, min=0, help="Maximum candidates to print."),
    output_format: CommunityCandidatesOutputFormat = COMMUNITY_CANDIDATES_FORMAT_OPTION,
) -> None:
    """Preview candidate phrases from one local community signal file."""
    try:
        try:
            as_of_value = parse_datetime_utc(as_of)
        except (TypeError, ValueError) as exc:
            typer.echo(
                f"Could not preview community candidates: invalid --as-of: {exc}",
                err=True,
            )
            raise typer.Exit(1) from exc
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
    except typer.Exit:
        raise
    except ConfigError as exc:
        typer.echo(f"Invalid community candidate config: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        preview = preview_community_candidates(
            path,
            input_format=input_format,
            scoring=scoring_config.scoring,
            settings=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of_value,
            default_source_name=source_name,
            limit=limit,
        )
    except Exception as exc:
        # Keep the local input path out of user-facing errors.
        message = str(exc)
        if str(path) in message or path.name in message:
            message = "input file could not be read or validated"
        typer.echo(f"Could not preview community candidates: {message}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(preview.model_dump_json(indent=2))
        return
    for line in render_community_candidates_table(preview):
        typer.echo(line)
```

- [ ] **Step 4: Run focused CLI/module tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q -k "community_candidates"
```

Expected: all Stage 27A tests pass.

## Task 5: Focused Verification Only

**Files:**
- No new files.

- [ ] **Step 1: Run adjacent regression tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_lint.py tests/test_manual_signal_import.py tests/test_candidate_scoring.py -q
```

Expected: all pass.

- [ ] **Step 2: Run static checks**

Run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Run local boundary scans**

Run:

```bash
rg -n "create_sqlite_engine|create_readonly_sqlite_engine|initialize_schema|store_manual_signal_rows|dashboard|report|schedule|watch|crawler|scrape|platform API|source acquisition" src/fashion_radar/community_candidates.py
```

Expected: exit `1` with no matches.

Run:

```bash
git diff --name-only | rg '^uv\.lock$'
```

Expected: exit `1`; Stage 27A should not touch `uv.lock`.

## Stage 27A Completion

Stage 27A is complete when:

- module tests pass;
- CLI tests pass;
- adjacent regression tests pass;
- ruff and `git diff --check` pass;
- boundary scans pass;
- no docs/release/commit/push work has been mixed into this node.

The next node should submit the Stage 27A code to Claude Code for review and
then plan Stage 27B docs/release work if the review approves.
