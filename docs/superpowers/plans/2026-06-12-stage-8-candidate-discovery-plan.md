# Stage 8 Candidate Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic untracked candidate discovery so users can review observed phrases that may warrant human review for brands, designers, products, bags, shoes, and style terms found in already collected local RSS/GDELT items.

**Architecture:** Add a no-schema discovery module that reads existing SQLite `items` and `item_entities`, extracts deterministic candidate phrases from titles/summaries, filters known tracked entities, computes current/baseline metrics, and surfaces results through reports, a read-only CLI command, and a dashboard tab that reads the latest JSON report. The feature must frame outputs as candidate signals that need human review, not confirmed brands or market-wide trends.

**Tech Stack:** Python 3.11+, SQLAlchemy Core, Pydantic, Typer, pytest, ruff, uv, existing SQLite workflow, existing Streamlit dashboard extra.

---

## Scope Guard

Stage 8 must not add any collector, source type, crawler, browser automation,
network call, paid API, LLM dependency, embedding dependency, vector database,
or image recognition.

Do not implement or document recipes for Instagram, TikTok, X/Twitter,
Xiaohongshu/RedNote, Pinterest, Reddit, Google Trends, Google News RSS, static
webpage monitoring, Playwright, login cookies, account/session files, browser
profiles, proxy pools, CAPTCHA bypass, paywall bypass, fingerprint evasion,
anti-bot bypass, or private data collection.

Candidate outputs must use language such as `candidate signal`, `observed
phrase`, `needs review`, and `from configured sources`. Do not use `viral`,
`confirmed brand`, or `market-wide trend`.

Codex subagents must use `reasoning_effort: "xhigh"`. Claude Code review must
use `--effort max`.

## Files

- Create: `src/fashion_radar/discovery/__init__.py`
- Create: `src/fashion_radar/discovery/candidates.py`
- Modify: `src/fashion_radar/settings.py`
- Modify: `configs/scoring.example.yaml`
- Modify: `src/fashion_radar/templates/configs/scoring.example.yaml`
- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/templates/daily_report.md`
- Modify: `src/fashion_radar/workflows.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `src/fashion_radar/dashboard/queries.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Create: `docs/candidate-discovery.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/scoring.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- Create: `tests/test_candidate_extraction.py`
- Create: `tests/test_candidate_scoring.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_dashboard.py`
- Modify: `docs/reviews/claude-code-stage-8-plan-review-prompt.md`
- Create after plan review: `docs/reviews/claude-code-stage-8-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-8-code-review-prompt.md`
- Create after code review: `docs/reviews/claude-code-stage-8-code-review.md`

## Public Interfaces

Discovery settings:

```python
class CandidateDiscoverySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_candidates: int = Field(default=20, ge=0)
    representative_items_per_candidate: int = Field(default=3, ge=0)
    min_current_mentions: int = Field(default=2, ge=1)
    min_distinct_sources: int = Field(default=1, ge=1)
    min_single_token_mentions: int = Field(default=2, ge=1)
    min_single_token_distinct_sources: int = Field(default=2, ge=1)
    max_phrase_words: int = Field(default=5, ge=2)
    max_phrase_chars: int = Field(default=80, ge=10)
```

Discovery module dataclasses:

```python
@dataclass(frozen=True)
class CandidatePhrase:
    phrase: str
    normalized_key: str
    candidate_type: str
    contexts: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateMetric:
    phrase: str
    normalized_key: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None
    first_seen_at: datetime
    contexts: tuple[str, ...]
    representative_items: tuple[RepresentativeItem, ...]
```

`contexts` values are controlled extraction labels only, such as
`proper_name_span` or `fashion_anchor`. They must not contain raw source text,
aliases, matcher reasons, snippets, or serialized internal extraction state.

Discovery functions:

- `configured_entity_keys(entity_config: EntityConfig | None) -> set[str]`
- `extract_candidate_phrases(text: str, *, source_name: str, known_keys: set[str] | None = None, settings: CandidateDiscoverySettings | None = None) -> list[CandidatePhrase]`
- `discover_candidates(engine: Engine, *, scoring: ScoringSettings, settings: CandidateDiscoverySettings, entity_config: EntityConfig | None, as_of: datetime, limit: int | None = None) -> list[CandidateMetric]`

CLI:

```bash
fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of 2026-06-12T00:00:00Z --limit 20 --format table
fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of 2026-06-12T00:00:00Z --limit 20 --format json
```

## Task 1: Claude Code Plan Gate

- [ ] Update `docs/reviews/claude-code-stage-8-plan-review-prompt.md` with the Stage 8 goal, architecture, tech stack, implementation method, tests, docs, explicit read-only review instruction, and explicit out-of-scope boundaries.
- [ ] Run:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-8-plan-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-8-plan-review.md`.
- [ ] Fix every Critical and Important finding before Task 2.

## Task 2: Candidate Discovery Settings

**Files:**

- Modify: `src/fashion_radar/settings.py`
- Modify: `configs/scoring.example.yaml`
- Modify: `src/fashion_radar/templates/configs/scoring.example.yaml`
- Modify: `tests/test_config.py`

- [ ] Add failing config tests:

```python
def test_candidate_discovery_defaults_load_from_minimal_scoring_config(tmp_path: Path) -> None:
    path = tmp_path / "scoring.yaml"
    path.write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    config = load_scoring_config(path)

    assert config.candidate_discovery.enabled is True
    assert config.candidate_discovery.max_candidates == 20
    assert config.candidate_discovery.min_current_mentions == 2


def test_candidate_discovery_rejects_invalid_threshold(tmp_path: Path) -> None:
    path = tmp_path / "scoring.yaml"
    path.write_text(
        """
version: 1
scoring: {}
candidate_discovery:
  min_current_mentions: 0
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="candidate_discovery"):
        load_scoring_config(path)
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_config.py::test_candidate_discovery_defaults_load_from_minimal_scoring_config tests/test_config.py::test_candidate_discovery_rejects_invalid_threshold -q
```

Expected: fails because `candidate_discovery` does not exist.

- [ ] Implement `CandidateDiscoverySettings` and add it to `ScoringConfig`:

```python
class CandidateDiscoverySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_candidates: int = Field(default=20, ge=0)
    representative_items_per_candidate: int = Field(default=3, ge=0)
    min_current_mentions: int = Field(default=2, ge=1)
    min_distinct_sources: int = Field(default=1, ge=1)
    min_single_token_mentions: int = Field(default=2, ge=1)
    min_single_token_distinct_sources: int = Field(default=2, ge=1)
    max_phrase_words: int = Field(default=5, ge=2)
    max_phrase_chars: int = Field(default=80, ge=10)


class ScoringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    scoring: ScoringSettings
    candidate_discovery: CandidateDiscoverySettings = Field(
        default_factory=CandidateDiscoverySettings
    )
```

- [ ] Add the optional `candidate_discovery` block to both scoring example files and keep them byte-identical:

```yaml
candidate_discovery:
  enabled: true
  max_candidates: 20
  representative_items_per_candidate: 3
  min_current_mentions: 2
  min_distinct_sources: 1
  min_single_token_mentions: 2
  min_single_token_distinct_sources: 2
  max_phrase_words: 5
  max_phrase_chars: 80
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_config.py -q
cmp -s configs/scoring.example.yaml src/fashion_radar/templates/configs/scoring.example.yaml
```

Expected: passes.

## Task 3: Candidate Phrase Extraction

**Files:**

- Create: `src/fashion_radar/discovery/__init__.py`
- Create: `src/fashion_radar/discovery/candidates.py`
- Create: `tests/test_candidate_extraction.py`

- [ ] Add failing extraction tests:

```python
from fashion_radar.discovery.candidates import extract_candidate_phrases
from fashion_radar.settings import CandidateDiscoverySettings


def _keys(phrases):
    return {phrase.normalized_key for phrase in phrases}


def test_extracts_proper_name_and_product_phrases() -> None:
    phrases = extract_candidate_phrases(
        "Sandy Liang Mary Jane flats and Le Teckel bag searches rise.",
        source_name="Fashionista",
        known_keys=set(),
    )

    assert "sandy liang" in _keys(phrases)
    assert "mary jane flats" in _keys(phrases)
    assert "le teckel bag" in _keys(phrases)


def test_filters_known_entities_source_terms_and_generic_phrases() -> None:
    phrases = extract_candidate_phrases(
        "Fashionista reports The Row Margaux bag during Paris Fashion Week.",
        source_name="Fashionista",
        known_keys={"the row", "margaux", "paris fashion week"},
    )

    keys = _keys(phrases)
    assert "fashionista" not in keys
    assert "the row" not in keys
    assert "margaux" not in keys
    assert "paris fashion week" not in keys


def test_respects_max_phrase_words_and_chars() -> None:
    settings = CandidateDiscoverySettings(max_phrase_words=3, max_phrase_chars=24)
    phrases = extract_candidate_phrases(
        "The Very Long Designer Product Name handbag gains attention.",
        source_name="WWD",
        known_keys=set(),
        settings=settings,
    )

    assert all(len(phrase.phrase.split()) <= 3 for phrase in phrases)
    assert all(len(phrase.phrase) <= 24 for phrase in phrases)
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_extraction.py -q
```

Expected: fails because the discovery package does not exist.

- [ ] Implement `src/fashion_radar/discovery/__init__.py`:

```python
"""Local candidate discovery from already collected Fashion Radar items."""
```

- [ ] Implement phrase extraction in `src/fashion_radar/discovery/candidates.py` with these constants and helpers:

```python
FASHION_ANCHORS = {
    "bag",
    "handbag",
    "tote",
    "clutch",
    "shoe",
    "shoes",
    "sneaker",
    "sneakers",
    "boot",
    "boots",
    "loafer",
    "loafers",
    "flat",
    "flats",
    "heel",
    "heels",
    "sandal",
    "sandals",
    "pump",
    "pumps",
    "mule",
    "mules",
}

GENERIC_STOP_KEYS = {
    "fashion",
    "fashion week",
    "spring collection",
    "fall collection",
    "summer collection",
    "winter collection",
    "new york",
    "london",
    "milan",
    "paris",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}
```

Implementation rules:

- Use `normalize_text()` and `normalize_alias_key()`.
- Tokenize with a regex that keeps letters, digits, apostrophes, ampersands, and hyphens.
- Extract title-case spans of 2 to `max_phrase_words` words.
- Extract anchored phrases ending with a fashion anchor.
- Deduplicate by normalized key in insertion order.
- Remove keys in `known_keys`, source-name keys, generic stop keys, one-character keys, and values longer than `max_phrase_chars`.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_extraction.py -q
.venv/bin/python -m ruff check src/fashion_radar/discovery tests/test_candidate_extraction.py
```

Expected: passes.

## Task 4: Candidate Metrics

**Files:**

- Modify: `src/fashion_radar/discovery/candidates.py`
- Create: `tests/test_candidate_scoring.py`

- [ ] Add metric tests using existing `ItemRepository` and schema helpers:

```python
from datetime import UTC, datetime, timedelta

import pytest

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema
from fashion_radar.discovery.candidates import discover_candidates
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType
from fashion_radar.settings import (
    CandidateDiscoverySettings,
    EntityConfig,
    ScoringSettings,
)

AS_OF = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)


def _store(engine, *, title, url, source_name="Fashionista", source_weight=1.0, collected_at=None, summary=""):
    return ItemRepository(engine).upsert_item(
        CollectedItem(
            source_name=source_name,
            source_type=SourceType.RSS,
            url=url,
            title=title,
            published_at=collected_at or AS_OF,
            summary=summary,
        ),
        source_weight=source_weight,
        collected_at=collected_at or AS_OF,
    )


def test_discovers_new_candidate_from_current_window(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(engine, title="Le Teckel bag gains momentum", url="https://example.com/a", collected_at=AS_OF - timedelta(hours=1))
    _store(engine, title="Le Teckel bag appears again", url="https://example.com/b", source_name="WWD", collected_at=AS_OF - timedelta(hours=2))

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "le teckel bag")
    assert candidate.label == "new_candidate"
    assert candidate.current_mentions == 2
    assert candidate.baseline_mentions == 0
    assert candidate.distinct_sources == 2
    assert candidate.representative_items[0].title == "Le Teckel bag gains momentum"


def test_excludes_configured_and_stored_entities(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    item_id = _store(engine, title="The Row Margaux bag gains momentum", url="https://example.com/row", collected_at=AS_OF - timedelta(hours=1))
    ItemRepository(engine).replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
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

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(min_current_mentions=1),
        entity_config=entity_config,
        as_of=AS_OF,
    )

    keys = {candidate.normalized_key for candidate in candidates}
    assert "the row" not in keys
    assert "margaux" not in keys
    assert "the row margaux bag" not in keys
    assert "margaux bag" not in keys


def test_uses_collected_at_windows_and_ignores_future_items(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(engine, title="Pierced mule demand grows", url="https://example.com/current", collected_at=AS_OF - timedelta(days=1))
    _store(engine, title="Pierced mule earlier signal", url="https://example.com/baseline", collected_at=AS_OF - timedelta(days=10))
    _store(engine, title="Pierced mule future signal", url="https://example.com/future", collected_at=AS_OF + timedelta(days=1))

    candidates = discover_candidates(
        engine,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        settings=CandidateDiscoverySettings(min_current_mentions=1),
        entity_config=None,
        as_of=AS_OF,
    )

    candidate = next(item for item in candidates if item.normalized_key == "pierced mule")
    assert candidate.current_mentions == 1
    assert candidate.baseline_mentions == 1
    assert candidate.growth_ratio == pytest.approx((1 / 7) / (1 / 30))


def test_candidate_discovery_settings_control_output(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store(engine, title="Khaite boot gains attention", url="https://example.com/a", collected_at=AS_OF - timedelta(hours=1))
    _store(engine, title="Khaite boot appears again", url="https://example.com/b", source_name="WWD", collected_at=AS_OF - timedelta(hours=2))

    disabled = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(enabled=False),
        entity_config=None,
        as_of=AS_OF,
    )
    limited = discover_candidates(
        engine,
        scoring=ScoringSettings(),
        settings=CandidateDiscoverySettings(max_candidates=1, representative_items_per_candidate=1),
        entity_config=None,
        as_of=AS_OF,
    )

    assert disabled == []
    assert len(limited) == 1
    assert len(limited[0].representative_items) == 1
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_scoring.py -q
```

Expected: fails until `discover_candidates` is implemented.

- [ ] Implement `discover_candidates`:

Implementation requirements:

- Query retained `items` rows with `collected_at` in `(baseline_start, as_of]`.
- Ignore rows whose `collected_at` is later than `as_of`.
- Build known keys from `entity_config`, stored accepted `item_entities.entity_name`, and stored accepted `item_entities.alias`.
- Extract candidates from each item text.
- Count each `normalized_key` at most once per item.
- Split current and baseline windows using `collected_at`.
- Apply single-token thresholds after aggregation.
- Apply `settings.min_current_mentions`, `settings.min_distinct_sources`, and `limit`.
- If `settings.enabled` is false, return an empty list.
- Use `settings.max_candidates` when `limit is None`.
- Use `min(limit, settings.max_candidates)` when both are provided.
- Use `settings.representative_items_per_candidate` for representative item count.
- Use `settings.min_single_token_mentions` and
  `settings.min_single_token_distinct_sources` for one-token candidates.
- Reject candidate phrases that contain any configured or stored known entity key
  as a complete token span, so known entities do not leak through longer phrases
  such as `the row margaux bag` or `margaux bag`.
- Compute growth ratio from window rates:

```text
current_rate = current_mentions / scoring.current_window_days
baseline_rate = baseline_mentions / scoring.baseline_window_days
growth_ratio = current_rate / baseline_rate when baseline_mentions > 0
growth_ratio = None when baseline_mentions == 0
```

- Compute score and label with the formula in the design.
- Select representative current-window items sorted by `(collected_at, item_id)` descending.
- Return a deterministic tuple/list sorted by `(-score, -current_mentions, -distinct_sources, phrase)`.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_candidate_extraction.py tests/test_candidate_scoring.py -q
.venv/bin/python -m ruff check src/fashion_radar/discovery tests/test_candidate_extraction.py tests/test_candidate_scoring.py
```

Expected: passes.

## Task 5: Report Integration

**Files:**

- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/templates/daily_report.md`
- Modify: `src/fashion_radar/workflows.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_cli.py`

- [ ] Add report tests:

```python
def test_daily_report_includes_untracked_candidate_signals(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/le-teckel-a",
        entity_name="Tracked Placeholder",
        source_name="Fashionista",
        collected_at=AS_OF - timedelta(hours=1),
        summary="Le Teckel bag demand is accelerating.",
    )
    _store_item(
        engine,
        url="https://example.com/le-teckel-b",
        entity_name="Tracked Placeholder",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=2),
        summary="Le Teckel bag appears again.",
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)
    parsed = json.loads(render_json_report(report))

    assert "Untracked Candidate Signals" in markdown
    assert "candidate signal" in markdown.lower()
    assert "needs review" in markdown.lower()
    assert "from configured sources" in markdown.lower()
    assert "viral" not in markdown.lower()
    assert "market-wide trend" not in markdown.lower()
    assert "confirmed brand" not in markdown.lower()
    assert "Le Teckel bag" in markdown
    assert "Fashionista" in markdown
    assert "https://example.com/le-teckel-a" in markdown
    assert "Le Teckel bag demand is accelerating." in markdown
    assert parsed["candidates"][0]["phrase"] == "Le Teckel bag"
    assert parsed["candidates"][0]["representative_items"][0]["source_name"] == "Fashionista"
    assert parsed["candidates"][0]["representative_items"][0]["source_url"] == "https://example.com/le-teckel-a"
    assert "Le Teckel bag demand is accelerating." in parsed["candidates"][0]["representative_items"][0]["summary"]
    assert "content_hash" not in json.dumps(parsed["candidates"])


def test_empty_candidate_section_is_useful(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )

    assert report.candidates == []
    assert "No untracked candidate signals in this window." in render_markdown_report(report)
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_reports.py -q
```

Expected: fails because report models and renderer do not include candidates.

- [ ] Add Pydantic report models:

```python
class CandidateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None = None
    first_seen_at: datetime
    contexts: list[str] = Field(default_factory=list)
    representative_items: list[RepresentativeItem] = Field(default_factory=list)

    @field_validator("first_seen_at", mode="before")
    @classmethod
    def normalize_first_seen_at(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)
```

Only include controlled context labels in `contexts`, such as
`proper_name_span` or `fashion_anchor`. Do not include raw source text, aliases,
matcher reasons, snippets, or serialized extraction internals.

Add to `DailyReport`:

```python
candidates: list[CandidateReport] = Field(default_factory=list)
```

- [ ] Update `build_daily_report` signature:

```python
def build_daily_report(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    as_of: datetime,
    candidate_discovery: CandidateDiscoverySettings | None = None,
    entity_config: EntityConfig | None = None,
    generated_at: datetime | None = None,
    max_entities: int = 20,
    representative_items_per_entity: int = 3,
    recent_runs_limit: int = 10,
) -> DailyReport:
```

- [ ] Update `write_daily_report_files` to accept `candidate_discovery` and `entity_config`, and update `report` and `run` CLI call sites:

```python
markdown_path, json_path = write_daily_report_files(
    data_dir=data_dir,
    reports_dir=reports_dir,
    scoring=scoring_config.scoring,
    candidate_discovery=scoring_config.candidate_discovery,
    entity_config=entity_config,
    as_of=as_of,
)
```

For standalone `report`, try to load `entities.yaml`. If the file is missing,
continue with `entity_config=None` and rely on stored `item_entities` filtering.
If the file exists but is invalid, preserve the existing config validation error
behavior and do not silently continue.

- [ ] Update Markdown template:

```text
## Untracked Candidate Signals

{candidate_sections}
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_reports.py tests/test_cli.py -q
.venv/bin/python -m ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/workflows.py src/fashion_radar/cli.py tests/test_reports.py tests/test_cli.py
```

Expected: passes.

## Task 6: Read-Only `candidates` CLI

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add CLI tests:

```python
import json


def _prepare_candidate_cli_fixture(tmp_path: Path) -> tuple[Path, Path]:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    engine = create_sqlite_engine(data_dir / "fashion-radar.sqlite")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel",
            title="Le Teckel bag rises",
            published_at="2026-06-11T10:00:00Z",
            summary="Le Teckel bag appears again.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 0, tzinfo=UTC),
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/le-teckel-2",
            title="Le Teckel bag appears again",
            published_at="2026-06-11T10:30:00Z",
            summary="Another configured source mentions Le Teckel bag.",
        ),
        collected_at=datetime(2026, 6, 11, 11, 30, tzinfo=UTC),
    )
    return config_dir, data_dir


def test_candidates_command_prints_json(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_candidate_cli_fixture(tmp_path)
    scoring_before = (config_dir / "scoring.yaml").read_bytes()
    entities_before = (config_dir / "entities.yaml").read_bytes()

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["phrase"] == "Le Teckel bag"
    assert (config_dir / "scoring.yaml").read_bytes() == scoring_before
    assert (config_dir / "entities.yaml").read_bytes() == entities_before


def test_candidates_command_prints_table(tmp_path: Path) -> None:
    config_dir, data_dir = _prepare_candidate_cli_fixture(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert "Phrase" in result.output
    assert "candidate signal" in result.output.lower()
    assert "Le Teckel bag" in result.output


def test_candidates_command_is_read_only_when_database_is_missing(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    data_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "candidates",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-11T12:00:00Z",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == []
    assert not (data_dir / "fashion-radar.sqlite").exists()
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py::test_candidates_command_prints_json tests/test_cli.py::test_candidates_command_prints_table -q
```

Expected: fails until the CLI command exists.

- [ ] Implement `candidates` command:

```python
CandidateOutputFormat = Literal["table", "json"]


@app.command(name="candidates")
def candidates_command(
    config_dir: Path = CONFIG_DIR_OPTION,
    data_dir: Path = DATA_DIR_OPTION,
    as_of: str = AS_OF_OPTION,
    limit: int | None = typer.Option(None, min=0, help="Maximum candidates to print."),
    output_format: CandidateOutputFormat = typer.Option("table", "--format", help="Output format."),
) -> None:
    """Print read-only untracked candidate signals from local collected items."""
```

Implementation requirements:

- Load `scoring.yaml`.
- Try to load `entities.yaml`; continue with `None` only if the file is missing.
- If `fashion-radar.sqlite` does not exist, return an empty result without
  creating the database file.
- If the database exists, create the SQLite engine without calling
  `initialize_schema()` in this command path. The command is read-only and must
  not create tables, write `schema_metadata`, or migrate schema.
- If the existing database schema is incompatible, show a user-facing error
  rather than mutating it.
- Call `discover_candidates`.
- If `--limit` is omitted, rely on `candidate_discovery.max_candidates`.
- If `--limit` is provided, cap output with
  `min(limit, candidate_discovery.max_candidates)`.
- JSON output uses report-safe fields only.
- Table output prints a compact header and rows with phrase, type, label, score, mentions, sources.
- The command does not write reports and does not mutate config.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -q
```

Expected: passes.

## Task 7: Dashboard Candidate Tab

**Files:**

- Modify: `src/fashion_radar/dashboard/queries.py`
- Modify: `src/fashion_radar/dashboard/app.py`
- Modify: `tests/test_dashboard.py`

- [ ] Add dashboard helper tests:

```python
import json


def test_latest_candidate_rows_reads_latest_report(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-10.json").write_text('{"metadata": {"report_date": "2026-06-10T00:00:00Z"}, "candidates": []}', encoding="utf-8")
    (reports_dir / "fashion-radar-2026-06-11.json").write_text(
        json.dumps(
            {
                "metadata": {"report_date": "2026-06-11T00:00:00Z"},
                "candidates": [
                    {
                        "phrase": "Le Teckel bag",
                        "candidate_type": "bag",
                        "label": "new_candidate",
                        "score": 3.0,
                        "current_mentions": 2,
                        "baseline_mentions": 0,
                        "distinct_sources": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    rows = latest_candidate_rows(reports_dir)
    report = latest_candidate_report(reports_dir)

    assert rows == [
        {
            "phrase": "Le Teckel bag",
            "candidate_type": "bag",
            "label": "new_candidate",
            "score": 3.0,
            "current_mentions": 2,
            "baseline_mentions": 0,
            "distinct_sources": 2,
            "report_date": "2026-06-11T00:00:00Z",
        }
    ]
    assert report["report_date"] == "2026-06-11T00:00:00Z"
    assert report["candidate_count"] == 1


def test_latest_candidate_rows_returns_empty_for_missing_reports(tmp_path: Path) -> None:
    assert latest_candidate_rows(tmp_path / "reports") == []
    assert latest_candidate_report(tmp_path / "reports") == {
        "report_date": None,
        "candidate_count": 0,
        "rows": [],
    }


def test_latest_candidate_report_preserves_date_when_no_candidates(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-11.json").write_text(
        '{"metadata": {"report_date": "2026-06-11T00:00:00Z"}, "candidates": []}',
        encoding="utf-8",
    )

    assert latest_candidate_report(reports_dir) == {
        "report_date": "2026-06-11T00:00:00Z",
        "candidate_count": 0,
        "rows": [],
    }
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_dashboard.py -q
```

Expected: fails until dashboard helpers exist.

- [ ] Implement `latest_report_path`, `latest_candidate_report`, and `latest_candidate_rows` in `dashboard/queries.py`:

```python
def latest_report_path(reports_dir: Path) -> Path | None:
    if not reports_dir.exists():
        return None
    candidates = sorted(reports_dir.glob("fashion-radar-*.json"))
    return candidates[-1] if candidates else None


def latest_candidate_rows(reports_dir: Path) -> list[dict[str, Any]]:
    return latest_candidate_report(reports_dir)["rows"]


def latest_candidate_report(reports_dir: Path) -> dict[str, Any]:
    path = latest_report_path(reports_dir)
    if path is None:
        return {"report_date": None, "candidate_count": 0, "rows": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    report_date = payload.get("metadata", {}).get("report_date")
    rows = []
    for candidate in payload.get("candidates", []):
        rows.append(
            {
                "phrase": candidate.get("phrase", ""),
                "candidate_type": candidate.get("candidate_type", ""),
                "label": candidate.get("label", ""),
                "score": candidate.get("score", 0.0),
                "current_mentions": candidate.get("current_mentions", 0),
                "baseline_mentions": candidate.get("baseline_mentions", 0),
                "distinct_sources": candidate.get("distinct_sources", 0),
                "report_date": report_date,
            }
        )
    return {"report_date": report_date, "candidate_count": len(rows), "rows": rows}
```

- [ ] Add a `Candidate Signals` tab to `dashboard/app.py` that displays `latest_candidate_rows(args.reports_dir)` without triggering collection, matching, report generation, or network calls.
- [ ] In the dashboard tab, show the report date from `latest_candidate_report`
  even when there are no candidate rows.
- [ ] In the dashboard tab, include a short caption using bounded language:
  `Candidate signals are observed phrases from configured sources and need review.`
  Do not use viral, global, market-wide, or confirmed-brand/product language.
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_dashboard.py -q
.venv/bin/python -m ruff check src/fashion_radar/dashboard tests/test_dashboard.py
```

Expected: passes.

## Task 8: Documentation

**Files:**

- Create: `docs/candidate-discovery.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/scoring.md`
- Modify: `docs/dashboard.md`
- Modify: `docs/source-boundaries.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

- [ ] Create `docs/candidate-discovery.md` covering:
  - Candidate signals are observed phrases from already collected local items.
  - They are not validated real-world entities and need human review.
  - Current/baseline windows use `collected_at`.
  - `first_seen_at` is retained-history only and can change after pruning.
  - `fashion-radar candidates` examples for table and JSON.
  - Dashboard reads the latest report JSON and may be stale.
  - No new sources, scraping, social crawling, paid APIs, or LLMs.
- [ ] Update README docs list and quickstart with:

```bash
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

- [ ] Update architecture/scoring/dashboard/source-boundaries docs with one concise section each.
- [ ] Update CHANGELOG `Added` with Stage 8 candidate discovery.
- [ ] Update the main implementation plan with a Stage 8 status and links to this spec/plan.
- [ ] Run:

```bash
rg -n "(viral|globally trending|global trend|market-wide trend|confirmed (brand|product)|real brand|real product)" \
  README.md docs/candidate-discovery.md docs/architecture.md docs/scoring.md docs/dashboard.md CHANGELOG.md \
  src/fashion_radar/templates src/fashion_radar/cli.py src/fashion_radar/dashboard
```

Expected: no matches in user-facing Stage 8 additions or source files.

Then check tests explicitly assert prohibited claim language is absent:

```bash
rg -n "viral|market-wide trend|confirmed brand" tests
```

Expected: only negative assertions such as `not in` or absence checks.

## Task 9: Full Verification And Claude Code Code Review

- [ ] Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check
uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

- [ ] Run package and resource smoke:

```bash
rm -rf /tmp/fashion-radar-dist-stage8
uv build --out-dir /tmp/fashion-radar-dist-stage8
tmpdir="$(mktemp -d)"
uv venv "$tmpdir/venv"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmpdir/venv/bin/python" /tmp/fashion-radar-dist-stage8/fashion_radar-0.1.0-py3-none-any.whl
"$tmpdir/venv/bin/fashion-radar" candidates --help
"$tmpdir/venv/bin/python" - <<'PY'
from importlib import resources
assert resources.files("fashion_radar.templates").joinpath("daily_report.md").is_file()
print("installed-resource-ok")
PY
```

- [ ] Run dashboard extra smoke:

```bash
.venv/bin/python - <<'PY'
from fashion_radar.dashboard.app import parse_args
from fashion_radar.dashboard.queries import latest_candidate_rows
print(parse_args.__name__, latest_candidate_rows.__name__)
PY
```

- [ ] Check root/package scoring template sync:

```bash
cmp -s configs/scoring.example.yaml src/fashion_radar/templates/configs/scoring.example.yaml
```

- [ ] Check CodeGraph:

```bash
# MCP tool: codegraph_status(projectPath="/home/ubuntu/fashion-radar")
```

- [ ] Create `docs/reviews/claude-code-stage-8-code-review-prompt.md` with implemented files, verification output, source-boundary notes, and next-stage suggestion.
- [ ] Run:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-8-code-review-prompt.md
```

- [ ] Save output to `docs/reviews/claude-code-stage-8-code-review.md`.
- [ ] Fix all Critical and Important findings.
- [ ] Commit with:

```bash
git status --short
git add src/fashion_radar/discovery/__init__.py \
  src/fashion_radar/discovery/candidates.py \
  src/fashion_radar/settings.py \
  configs/scoring.example.yaml \
  src/fashion_radar/templates/configs/scoring.example.yaml \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  src/fashion_radar/templates/daily_report.md \
  src/fashion_radar/workflows.py \
  src/fashion_radar/cli.py \
  src/fashion_radar/dashboard/queries.py \
  src/fashion_radar/dashboard/app.py \
  docs/candidate-discovery.md \
  README.md \
  docs/architecture.md \
  docs/scoring.md \
  docs/dashboard.md \
  docs/source-boundaries.md \
  CHANGELOG.md \
  docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md \
  docs/superpowers/plans/2026-06-12-stage-8-candidate-discovery-plan.md \
  docs/superpowers/specs/2026-06-12-stage-8-candidate-discovery-design.md \
  docs/reviews/claude-code-stage-8-code-review-prompt.md \
  docs/reviews/claude-code-stage-8-code-review.md \
  tests/test_candidate_extraction.py \
  tests/test_candidate_scoring.py \
  tests/test_config.py \
  tests/test_reports.py \
  tests/test_cli.py \
  tests/test_dashboard.py
git commit -m "feat: add candidate discovery signals"
```

- [ ] Sync to GitHub using normal git push if available. If Git smart HTTP still hangs but GitHub API works, use GitHub API only when it can preserve remote `main` safely and verify remote content afterward.

## Acceptance Criteria

- Candidate discovery uses only local SQLite items already collected by existing RSS/RSSHub/GDELT workflows.
- No new source, scraper, browser automation, social crawling, paid API, LLM dependency, embedding dependency, or vector database is added.
- Same DB, same config, and same `as_of` produce identical candidate JSON ordering.
- Configured and stored tracked entities do not appear as untracked candidates.
- Candidate metrics use the same current/baseline window semantics as entity heat scoring.
- Reports include candidate signals with source attribution and no internal DB fields.
- `fashion-radar candidates` is read-only and supports table and JSON output.
- Dashboard shows candidates from the latest report JSON without collecting, matching, writing reports, network calls, or config mutation.
- Docs clearly state that candidate signals need human review and reflect configured sources only.
- Full verification passes.
- Final Claude Code review has no unfixed Critical or Important findings.
