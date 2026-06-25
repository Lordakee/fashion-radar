from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import fashion_radar.dashboard.app as dashboard_app
import fashion_radar.dashboard.queries as dashboard_queries
from fashion_radar.dashboard.app import (
    CANDIDATE_SIGNAL_CAPTION,
    DASHBOARD_TAB_LABELS,
    TREND_EMPTY_MESSAGE,
    TREND_SIGNAL_CAPTION,
    parse_args,
    render_trend_deltas,
    trend_comparison_window,
    trend_delta_rows,
)
from fashion_radar.dashboard.queries import (
    dashboard_summary,
    database_path,
    latest_candidate_report,
    latest_candidate_rows,
    load_trend_comparison,
    source_health_rows,
    top_entities,
)
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import (
    CollectorRunRepository,
    ItemRepository,
    SourceHealthRepository,
)
from fashion_radar.db.schema import initialize_schema
from fashion_radar.heat_movers import build_heat_movers
from fashion_radar.models.entity import EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import REPORT_SNIPPET_MAX_CHARS, report_safe_snippet
from fashion_radar.models.source import SourceDefinition, SourceType
from fashion_radar.models.trend import TrendComparison, TrendDelta, TrendSignalKind, TrendStatus
from fashion_radar.settings import CandidateDiscoverySettings, ScoringSettings


def test_dashboard_helpers_import_without_streamlit() -> None:
    assert database_path(Path("/tmp/fashion-radar-data")) == Path(
        "/tmp/fashion-radar-data/fashion-radar.sqlite"
    )
    assert "streamlit" not in sys.modules


def test_dashboard_parse_args_ignores_unknown_streamlit_args(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "app.py",
            "--data-dir",
            "/tmp/data",
            "--reports-dir",
            "/tmp/reports",
            "--config-dir",
            "/tmp/config",
            "--theme.base",
            "light",
        ],
    )

    args = parse_args()

    assert args.data_dir == Path("/tmp/data")
    assert args.reports_dir == Path("/tmp/reports")
    assert args.config_dir == Path("/tmp/config")


def test_dashboard_candidate_caption_mentions_imported_local_signals() -> None:
    assert "configured sources and imported local signals" in CANDIDATE_SIGNAL_CAPTION
    assert "complete platform coverage" not in CANDIDATE_SIGNAL_CAPTION.lower()


def test_dashboard_trend_caption_is_local_observed() -> None:
    assert "Local observed signal deltas" in TREND_SIGNAL_CAPTION
    assert "configured RSS/web sources and imported manual signals" in TREND_SIGNAL_CAPTION
    assert "describe only this configured source set" in TREND_SIGNAL_CAPTION
    assert "Trend Deltas" in DASHBOARD_TAB_LABELS
    assert TREND_EMPTY_MESSAGE == "No local observed signal deltas in this comparison."
    combined_copy = " ".join([*DASHBOARD_TAB_LABELS, TREND_SIGNAL_CAPTION, TREND_EMPTY_MESSAGE])
    for forbidden in (
        "trending overall",
        "market trends",
        "social trends",
        "market-wide",
        "platform-wide",
        "what's hot",
    ):
        assert forbidden not in combined_copy.lower()


def test_dashboard_heat_mover_caption_is_local_observed() -> None:
    assert "Local observed heat movement" in dashboard_app.HEAT_MOVER_CAPTION
    assert (
        "configured RSS/web sources and imported manual signals" in dashboard_app.HEAT_MOVER_CAPTION
    )
    assert "describe only this configured source set" in dashboard_app.HEAT_MOVER_CAPTION
    assert "Heat Movers" in dashboard_app.DASHBOARD_TAB_LABELS
    assert (
        dashboard_app.HEAT_MOVER_EMPTY_MESSAGE
        == "No local observed heat movers in this comparison."
    )
    combined_copy = " ".join(
        [
            *dashboard_app.DASHBOARD_TAB_LABELS,
            dashboard_app.HEAT_MOVER_CAPTION,
            dashboard_app.HEAT_MOVER_EMPTY_MESSAGE,
        ]
    )
    for forbidden in (
        "trending overall",
        "market trends",
        "social trends",
        "market-wide",
        "platform-wide",
        "what's hot",
    ):
        assert forbidden not in combined_copy.lower()


def test_dashboard_tab_labels_include_all_entity_mention_tabs() -> None:
    for entity_type in EntityType:
        assert f"{entity_type.value.title()} Mentions" in DASHBOARD_TAB_LABELS


def test_dashboard_tab_labels_include_heat_movers_before_trend_deltas() -> None:
    labels = dashboard_app.DASHBOARD_TAB_LABELS

    assert labels.index("Heat Movers") < labels.index("Trend Deltas")
    assert len(labels) == len(dashboard_app.ENTITY_MENTION_TABS) + 5


def test_trend_comparison_window_defaults_from_current_window_days() -> None:
    now = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)

    as_of, baseline_as_of = trend_comparison_window(
        ScoringSettings(current_window_days=5),
        now=now,
    )

    assert as_of == now
    assert baseline_as_of == datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
    assert baseline_as_of < as_of


def test_trend_comparison_window_rejects_invalid_window_object() -> None:
    class InvalidScoring:
        current_window_days = 0

    with pytest.raises(ValueError, match="baseline"):
        trend_comparison_window(InvalidScoring(), now=datetime(2026, 6, 12, tzinfo=UTC))  # type: ignore[arg-type]


def test_dashboard_queries_handle_empty_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(database_path(data_dir))
    initialize_schema(engine)

    assert dashboard_summary(data_dir) == {
        "database_exists": True,
        "item_count": 0,
        "match_count": 0,
        "latest_collected_at": None,
    }
    assert top_entities(data_dir) == []
    assert source_health_rows(data_dir) == []


def test_dashboard_queries_return_top_entities_and_source_health(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    item_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/the-row",
            title="The Row signal",
            published_at="2026-06-11T10:00:00Z",
            summary="Short summary.",
        ),
    )
    repository.replace_item_matches(
        item_id,
        [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "alias": "The Row",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            },
            {
                "entity_name": "Margaux",
                "entity_type": "product",
                "alias": "Margaux",
                "confidence": 1.0,
                "reason": "accepted",
                "context_terms": [],
            },
        ],
    )
    source = SourceDefinition(
        name="Vogue Business",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
    )
    SourceHealthRepository(engine).record_failure(
        source,
        error_message="timeout",
        max_failures=1,
        retention_hours=24,
    )
    CollectorRunRepository(engine).record_run(
        source,
        status="failed",
        items_seen=0,
        items_stored=0,
        error_message="timeout",
    )

    assert dashboard_summary(data_dir)["item_count"] == 1
    assert top_entities(data_dir, entity_type="brand")[0]["entity_name"] == "The Row"
    assert top_entities(data_dir, entity_type="product")[0]["entity_name"] == "Margaux"
    assert source_health_rows(data_dir)[0]["last_error_message"] == "timeout"


def test_dashboard_recent_signals_missing_database_writes_nothing(tmp_path: Path) -> None:
    data_dir = tmp_path / "missing-data"

    assert dashboard_queries.recent_signals(data_dir) == []
    assert not data_dir.exists()
    assert not database_path(data_dir).exists()


def test_dashboard_recent_signals_returns_recent_items_in_review_shape(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    engine = create_sqlite_engine(database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    first_collected_at = datetime(2026, 6, 11, 11, 0, tzinfo=UTC)
    second_collected_at = datetime(2026, 6, 12, 9, 0, tzinfo=UTC)
    tied_collected_at = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    long_summary = "Lead text. " + ("detail " * 120) + "TAIL_MARKER"

    repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/old",
            title="Older signal",
            published_at="2026-06-11T10:00:00Z",
            summary="Older summary.",
        ),
        collected_at=first_collected_at,
    )
    repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/latest",
            title="Latest signal",
            published_at="2026-06-12T08:30:00Z",
            summary="Latest short summary.",
        ),
        collected_at=second_collected_at,
    )
    earlier_tie_id = repository.upsert_item(
        CollectedItem(
            source_name="Fashionista",
            source_type=SourceType.RSS,
            url="https://example.com/tie-earlier",
            title="Tie earlier id",
            published_at="2026-06-12T11:00:00Z",
            summary="Earlier tied summary.",
        ),
        collected_at=tied_collected_at,
    )
    later_tie_id = repository.upsert_item(
        CollectedItem(
            source_name="Manual Import",
            source_type=SourceType.MANUAL_IMPORT,
            url="https://example.com/tie-later",
            title="Tie later id",
            published_at="2026-06-12T11:30:00Z",
            summary=long_summary,
        ),
        collected_at=tied_collected_at,
    )
    assert later_tie_id > earlier_tie_id

    rows = dashboard_queries.recent_signals(data_dir, limit=3)

    assert [row["title"] for row in rows] == [
        "Tie later id",
        "Tie earlier id",
        "Latest signal",
    ]
    assert list(rows[0]) == [
        "collected_at",
        "published_at",
        "source_name",
        "source_type",
        "title",
        "url",
        "summary",
    ]
    assert rows[0]["summary"] == report_safe_snippet(long_summary)
    assert len(rows[0]["summary"]) <= REPORT_SNIPPET_MAX_CHARS
    assert "TAIL_MARKER" not in rows[0]["summary"]


def test_dashboard_loads_trend_deltas_from_local_database(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    as_of = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)
    engine = create_sqlite_engine(database_path(data_dir))
    initialize_schema(engine)
    repository = ItemRepository(engine)
    baseline_item_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue Business",
            source_type=SourceType.RSS,
            url="https://example.com/row-baseline",
            title="The Row baseline signal",
            published_at=as_of - timedelta(days=8),
            summary="Baseline mention.",
        ),
        collected_at=as_of - timedelta(days=8),
    )
    current_item_id = repository.upsert_item(
        CollectedItem(
            source_name="WWD",
            source_type=SourceType.RSS,
            url="https://example.com/row-current",
            title="The Row gains momentum",
            published_at=as_of - timedelta(days=1),
            summary="Current mention.",
        ),
        collected_at=as_of - timedelta(days=1),
    )
    for item_id in (baseline_item_id, current_item_id):
        repository.replace_item_matches(
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

    comparison = load_trend_comparison(
        data_dir=data_dir,
        scoring=ScoringSettings(current_window_days=7, baseline_window_days=30),
        candidate_discovery=CandidateDiscoverySettings(
            min_current_mentions=1,
            review_min_current_mentions=1,
        ),
        entity_config=None,
        as_of=as_of,
        baseline_as_of=as_of - timedelta(days=7),
    )

    assert "The Row" in {delta.name for delta in comparison.deltas}


def test_dashboard_trend_query_missing_database_writes_nothing(tmp_path: Path) -> None:
    data_dir = tmp_path / "missing-data"
    as_of = datetime(2026, 6, 12, 12, 0, tzinfo=UTC)

    comparison = load_trend_comparison(
        data_dir=data_dir,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=as_of,
        baseline_as_of=as_of - timedelta(days=7),
    )

    assert comparison == TrendComparison(
        as_of=as_of,
        baseline_as_of=as_of - timedelta(days=7),
        deltas=[],
    )
    assert not data_dir.exists()
    assert not database_path(data_dir).exists()


def test_dashboard_trend_query_uses_readonly_engine_and_disposes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db_path = database_path(data_dir)
    db_path.touch()
    events: list[str] = []
    expected = TrendComparison(
        as_of=datetime(2026, 6, 12, tzinfo=UTC),
        baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
        deltas=[],
    )

    class FakeEngine:
        def dispose(self) -> None:
            events.append("dispose")

    def fake_create_readonly_sqlite_engine(path: Path) -> FakeEngine:
        assert path == db_path
        events.append("engine")
        return FakeEngine()

    def fake_verify_readonly_trend_schema(engine: FakeEngine) -> None:
        events.append("verify")

    def fake_build_trend_comparison(engine: FakeEngine, **kwargs: object) -> TrendComparison:
        events.append("build")
        assert kwargs["limit"] == 20
        assert kwargs["include_dropped"] is False
        return expected

    monkeypatch.setattr(
        dashboard_queries,
        "create_readonly_sqlite_engine",
        fake_create_readonly_sqlite_engine,
    )
    monkeypatch.setattr(
        dashboard_queries,
        "verify_readonly_trend_schema",
        fake_verify_readonly_trend_schema,
    )
    monkeypatch.setattr(
        dashboard_queries,
        "build_trend_comparison",
        fake_build_trend_comparison,
    )

    comparison = load_trend_comparison(
        data_dir=data_dir,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=expected.as_of,
        baseline_as_of=expected.baseline_as_of,
    )

    assert comparison == expected
    assert events == ["engine", "verify", "build", "dispose"]


def test_dashboard_trend_query_disposes_on_schema_error(monkeypatch, tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    database_path(data_dir).touch()
    events: list[str] = []

    class FakeEngine:
        def dispose(self) -> None:
            events.append("dispose")

    monkeypatch.setattr(
        dashboard_queries,
        "create_readonly_sqlite_engine",
        lambda path: events.append("engine") or FakeEngine(),
    )

    def fail_schema(engine: FakeEngine) -> None:
        events.append("verify")
        raise RuntimeError("bad schema")

    monkeypatch.setattr(dashboard_queries, "verify_readonly_trend_schema", fail_schema)

    with pytest.raises(RuntimeError, match="bad schema"):
        load_trend_comparison(
            data_dir=data_dir,
            scoring=ScoringSettings(),
            candidate_discovery=CandidateDiscoverySettings(),
            entity_config=None,
            as_of=datetime(2026, 6, 12, tzinfo=UTC),
            baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
        )

    assert events == ["engine", "verify", "dispose"]


def test_dashboard_trend_query_rejects_invalid_window_before_engine(
    monkeypatch,
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    database_path(data_dir).touch()
    monkeypatch.setattr(
        dashboard_queries,
        "create_readonly_sqlite_engine",
        lambda path: pytest.fail("engine should not be created"),
    )

    with pytest.raises(ValueError, match="baseline_as_of"):
        load_trend_comparison(
            data_dir=data_dir,
            scoring=ScoringSettings(),
            candidate_discovery=CandidateDiscoverySettings(),
            entity_config=None,
            as_of=datetime(2026, 6, 12, tzinfo=UTC),
            baseline_as_of=datetime(2026, 6, 12, tzinfo=UTC),
        )


def test_dashboard_trend_delta_rows_are_serialized_and_review_oriented() -> None:
    comparison = TrendComparison(
        as_of=datetime(2026, 6, 12, tzinfo=UTC),
        baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
        deltas=[
            TrendDelta(
                signal_kind=TrendSignalKind.ENTITY,
                comparison_key="entity:brand:the row",
                name="The Row",
                signal_type="brand",
                status=TrendStatus.RISING,
                current_score=3.0,
                baseline_score=1.0,
                score_delta=2.0,
                current_mentions=3,
                baseline_mentions=1,
                mention_delta=2,
                current_growth_ratio=2.34567,
                baseline_growth_ratio=None,
                first_seen_at=datetime(2026, 6, 1, 9, 30, tzinfo=UTC),
            ),
            TrendDelta(
                signal_kind=TrendSignalKind.CANDIDATE,
                comparison_key="candidate:bag:le teckel",
                name="Le Teckel bag",
                signal_type="bag",
                status=TrendStatus.NEW,
                current_label="new_candidate",
                current_score=1.23456,
                score_delta=1.23456,
                current_mentions=2,
                mention_delta=2,
                first_seen_at=None,
            ),
        ],
    )

    rows = trend_delta_rows(comparison)

    assert rows == [
        {
            "observed_status": "rising",
            "signal_kind": "entity",
            "type": "brand",
            "name": "The Row",
            "current_score": 3.0,
            "baseline_score": 1.0,
            "score_delta": 2.0,
            "current_mentions": 3,
            "baseline_mentions": 1,
            "mention_delta": 2,
            "current_growth_ratio": 2.346,
            "baseline_growth_ratio": None,
            "current_label": None,
            "baseline_label": None,
            "first_seen_at": "2026-06-01T09:30:00+00:00",
        },
        {
            "observed_status": "new",
            "signal_kind": "candidate",
            "type": "bag",
            "name": "Le Teckel bag",
            "current_score": 1.235,
            "baseline_score": 0.0,
            "score_delta": 1.235,
            "current_mentions": 2,
            "baseline_mentions": 0,
            "mention_delta": 2,
            "current_growth_ratio": None,
            "baseline_growth_ratio": None,
            "current_label": "new_candidate",
            "baseline_label": None,
            "first_seen_at": None,
        },
    ]


def test_dashboard_trend_delta_rows_empty() -> None:
    comparison = TrendComparison(
        as_of=datetime(2026, 6, 12, tzinfo=UTC),
        baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
        deltas=[],
    )

    assert trend_delta_rows(comparison) == []


def test_dashboard_heat_mover_rows_are_serialized_and_review_oriented() -> None:
    comparison = TrendComparison(
        as_of=datetime(2026, 6, 12, tzinfo=UTC),
        baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
        deltas=[
            TrendDelta(
                signal_kind=TrendSignalKind.ENTITY,
                comparison_key="entity:brand:the row",
                name="The Row",
                signal_type="brand",
                status=TrendStatus.NEW,
                current_label="review",
                current_score=5.12345,
                baseline_score=1.0,
                score_delta=4.12345,
                current_mentions=5,
                baseline_mentions=1,
                mention_delta=4,
                first_seen_at=datetime(2026, 6, 1, 9, 30, tzinfo=UTC),
            ),
            TrendDelta(
                signal_kind=TrendSignalKind.CANDIDATE,
                comparison_key="candidate:bag:le teckel",
                name="Le Teckel bag",
                signal_type="bag",
                status=TrendStatus.RISING,
                current_label=None,
                current_score=2.0,
                baseline_score=1.0,
                score_delta=1.0,
                current_mentions=3,
                baseline_mentions=1,
                mention_delta=2,
                first_seen_at=None,
            ),
        ],
    )
    report = build_heat_movers(comparison, limit_per_group=5, include_cooling=False)

    rows = dashboard_app.heat_mover_rows(report)

    assert rows == [
        {
            "section": "New tracked entities",
            "observed_status": "new",
            "signal_kind": "entity",
            "type": "brand",
            "name": "The Row",
            "current_score": 5.123,
            "score_delta": 4.123,
            "current_mentions": 5,
            "mention_delta": 4,
            "current_label": "review",
            "first_seen_at": "2026-06-01T09:30:00+00:00",
        },
        {
            "section": "Rising candidate phrases",
            "observed_status": "rising",
            "signal_kind": "candidate",
            "type": "bag",
            "name": "Le Teckel bag",
            "current_score": 2.0,
            "score_delta": 1.0,
            "current_mentions": 3,
            "mention_delta": 2,
            "current_label": None,
            "first_seen_at": None,
        },
    ]
    assert list(rows[0]) == [
        "section",
        "observed_status",
        "signal_kind",
        "type",
        "name",
        "current_score",
        "score_delta",
        "current_mentions",
        "mention_delta",
        "current_label",
        "first_seen_at",
    ]


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.dataframes: list[list[dict[str, object]]] = []

    def caption(self, message: str) -> None:
        self.captions.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def info(self, message: str) -> None:
        self.infos.append(message)

    def dataframe(self, rows: list[dict[str, object]], use_container_width: bool) -> None:
        assert use_container_width is True
        self.dataframes.append(rows)


class FakeDashboardMainTab:
    def __init__(self, owner: FakeDashboardMainStreamlit, label: str) -> None:
        self.owner = owner
        self.label = label

    def __enter__(self) -> FakeDashboardMainTab:
        self.owner.current_tab_label = self.label
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.owner.current_tab_label = None


class FakeDashboardMainStreamlit:
    def __init__(self) -> None:
        self.labels: list[str] = []
        self.current_tab_label: str | None = None
        self.captions: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.dataframes: list[list[dict[str, object]]] = []
        self.metrics: list[tuple[str, object]] = []

    def set_page_config(self, **kwargs: object) -> None:
        pass

    def title(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        self.infos.append(message)

    def caption(self, message: str) -> None:
        self.captions.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def metric(self, label: str, value: object) -> None:
        self.metrics.append((label, value))

    def dataframe(self, rows: list[dict[str, object]], use_container_width: bool) -> None:
        assert use_container_width is True
        self.dataframes.append(rows)

    def tabs(self, labels: list[str]) -> list[FakeDashboardMainTab]:
        self.labels = labels
        return [FakeDashboardMainTab(self, label) for label in labels]


def test_render_heat_movers_warns_for_missing_scoring_without_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "missing-data"
    config_dir.mkdir()
    fake_st = FakeStreamlit()

    dashboard_app.render_heat_movers(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings
    assert "Could not load heat mover config" in fake_st.warnings[0]
    assert fake_st.dataframes == []
    assert not data_dir.exists()


def test_render_heat_movers_warns_for_invalid_entities_config(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: nope\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    dashboard_app.render_heat_movers(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings
    assert "Could not load heat mover config" in fake_st.warnings[0]
    assert fake_st.dataframes == []


def test_render_heat_movers_warns_for_query_errors(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    def fail_query(**kwargs: object) -> TrendComparison:
        raise RuntimeError("bad heat read")

    monkeypatch.setattr(dashboard_app, "load_trend_comparison", fail_query)

    dashboard_app.render_heat_movers(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings == ["Could not read heat movers: bad heat read"]
    assert fake_st.dataframes == []


def test_render_heat_movers_shows_empty_state(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    def empty_query(**kwargs: object) -> TrendComparison:
        return TrendComparison(
            as_of=datetime(2026, 6, 12, tzinfo=UTC),
            baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
            deltas=[],
        )

    monkeypatch.setattr(dashboard_app, "load_trend_comparison", empty_query)

    dashboard_app.render_heat_movers(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings == []
    assert dashboard_app.HEAT_MOVER_EMPTY_MESSAGE in fake_st.infos


def test_render_heat_movers_shows_grouped_rows(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    fake_st = FakeStreamlit()
    captured_kwargs: dict[str, object] = {}

    def grouped_query(**kwargs: object) -> TrendComparison:
        captured_kwargs.update(kwargs)
        return TrendComparison(
            as_of=datetime(2026, 6, 12, tzinfo=UTC),
            baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
            deltas=[
                TrendDelta(
                    signal_kind=TrendSignalKind.ENTITY,
                    comparison_key="entity:brand:the row",
                    name="The Row",
                    signal_type="brand",
                    status=TrendStatus.NEW,
                    current_score=3.0,
                    score_delta=3.0,
                    current_mentions=3,
                    mention_delta=3,
                ),
                TrendDelta(
                    signal_kind=TrendSignalKind.CANDIDATE,
                    comparison_key="candidate:bag:le teckel",
                    name="Le Teckel",
                    signal_type="bag",
                    status=TrendStatus.RISING,
                    current_score=2.0,
                    baseline_score=1.0,
                    score_delta=1.0,
                    current_mentions=2,
                    baseline_mentions=1,
                    mention_delta=1,
                ),
                TrendDelta(
                    signal_kind=TrendSignalKind.ENTITY,
                    comparison_key="entity:brand:cooling",
                    name="Cooling Brand",
                    signal_type="brand",
                    status=TrendStatus.COOLING,
                    current_score=1.0,
                    baseline_score=2.0,
                    score_delta=-1.0,
                    current_mentions=1,
                    baseline_mentions=2,
                    mention_delta=-1,
                ),
            ],
        )

    monkeypatch.setattr(dashboard_app, "load_trend_comparison", grouped_query)

    dashboard_app.render_heat_movers(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert captured_kwargs["include_dropped"] is False
    assert captured_kwargs["limit"] is None
    assert fake_st.warnings == []
    assert fake_st.infos == []
    assert fake_st.dataframes == [
        [
            {
                "section": "New tracked entities",
                "observed_status": "new",
                "signal_kind": "entity",
                "type": "brand",
                "name": "The Row",
                "current_score": 3.0,
                "score_delta": 3.0,
                "current_mentions": 3,
                "mention_delta": 3,
                "current_label": None,
                "first_seen_at": None,
            },
            {
                "section": "Rising candidate phrases",
                "observed_status": "rising",
                "signal_kind": "candidate",
                "type": "bag",
                "name": "Le Teckel",
                "current_score": 2.0,
                "score_delta": 1.0,
                "current_mentions": 2,
                "mention_delta": 1,
                "current_label": None,
                "first_seen_at": None,
            },
        ]
    ]


def test_dashboard_main_routes_heat_movers_and_trend_deltas_by_label(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    heat_calls: list[str | None] = []
    trend_calls: list[str | None] = []
    fake_streamlit = FakeDashboardMainStreamlit()

    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
    monkeypatch.setattr(
        dashboard_app,
        "parse_args",
        lambda: dashboard_app.argparse.Namespace(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
        ),
    )
    monkeypatch.setattr(
        dashboard_app,
        "dashboard_summary",
        lambda data_dir: {
            "database_exists": True,
            "item_count": 0,
            "match_count": 0,
            "latest_collected_at": None,
        },
    )
    monkeypatch.setattr(
        dashboard_app,
        "latest_candidate_report",
        lambda reports_dir: {"report_date": None, "candidate_count": 0, "rows": []},
    )
    monkeypatch.setattr(dashboard_app, "recent_signals", lambda data_dir: [])
    monkeypatch.setattr(
        dashboard_app,
        "top_entities",
        lambda data_dir, *, entity_type: [],
    )
    monkeypatch.setattr(dashboard_app, "source_health_rows", lambda data_dir: [])

    def fake_render_heat_movers(
        st: FakeDashboardMainStreamlit,
        *,
        config_dir: Path,
        data_dir: Path,
    ) -> None:
        heat_calls.append(st.current_tab_label)

    def fake_render_trend_deltas(
        st: FakeDashboardMainStreamlit,
        *,
        config_dir: Path,
        data_dir: Path,
    ) -> None:
        trend_calls.append(st.current_tab_label)

    monkeypatch.setattr(
        dashboard_app,
        "render_heat_movers",
        fake_render_heat_movers,
        raising=False,
    )
    monkeypatch.setattr(dashboard_app, "render_trend_deltas", fake_render_trend_deltas)

    dashboard_app.main()

    assert fake_streamlit.labels == list(dashboard_app.DASHBOARD_TAB_LABELS)
    assert heat_calls == ["Heat Movers"]
    assert trend_calls == ["Trend Deltas"]
    assert len(dashboard_app.DASHBOARD_TAB_LABELS) == len(dashboard_app.ENTITY_MENTION_TABS) + 5


def test_candidate_report_stale_warning_returns_none_without_both_timestamps() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at=None,
            report_generated_at="2026-06-11T00:00:00Z",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at=None,
        )
        is None
    )


def test_candidate_report_stale_warning_returns_warning_when_collection_is_newer() -> None:
    warning = dashboard_app.candidate_report_stale_warning(
        latest_collected_at="2026-06-12T09:00:00Z",
        report_generated_at="2026-06-11T00:00:00Z",
    )

    assert warning is not None
    assert "stale" in warning.lower()
    assert "fashion-radar report" in warning


def test_candidate_report_stale_warning_returns_none_when_report_is_current() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at="2026-06-12T09:00:00Z",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T09:00:00Z",
            report_generated_at="2026-06-12T10:00:00Z",
        )
        is None
    )


def test_candidate_report_stale_warning_normalizes_naive_and_offset_datetimes() -> None:
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T12:00:00Z",
            report_generated_at="2026-06-12T08:00:00-04:00",
        )
        is None
    )
    assert (
        dashboard_app.candidate_report_stale_warning(
            latest_collected_at="2026-06-12T12:00:00",
            report_generated_at="2026-06-12T12:00:00Z",
        )
        is None
    )


def test_dashboard_main_warns_when_candidate_report_is_stale(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    fake_streamlit = FakeDashboardMainStreamlit()
    candidate_rows = [
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

    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
    monkeypatch.setattr(
        dashboard_app,
        "parse_args",
        lambda: dashboard_app.argparse.Namespace(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
        ),
    )
    monkeypatch.setattr(
        dashboard_app,
        "dashboard_summary",
        lambda data_dir: {
            "database_exists": True,
            "item_count": 1,
            "match_count": 1,
            "latest_collected_at": "2026-06-12T09:00:00Z",
        },
    )
    monkeypatch.setattr(
        dashboard_app,
        "latest_candidate_report",
        lambda reports_dir: {
            "report_date": "2026-06-11T00:00:00Z",
            "generated_at": None,
            "candidate_count": 1,
            "rows": candidate_rows,
        },
    )
    monkeypatch.setattr(dashboard_app, "recent_signals", lambda data_dir: [])
    monkeypatch.setattr(dashboard_app, "top_entities", lambda data_dir, *, entity_type: [])
    monkeypatch.setattr(dashboard_app, "source_health_rows", lambda data_dir: [])
    monkeypatch.setattr(dashboard_app, "render_heat_movers", lambda *args, **kwargs: None)
    monkeypatch.setattr(dashboard_app, "render_trend_deltas", lambda *args, **kwargs: None)

    dashboard_app.main()

    assert len(fake_streamlit.warnings) == 1
    assert "stale" in fake_streamlit.warnings[0].lower()
    assert "fashion-radar report" in fake_streamlit.warnings[0]
    assert candidate_rows in fake_streamlit.dataframes


def test_dashboard_main_parse_error_does_not_emit_extra_stale_warning(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    fake_streamlit = FakeDashboardMainStreamlit()

    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
    monkeypatch.setattr(
        dashboard_app,
        "parse_args",
        lambda: dashboard_app.argparse.Namespace(
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
        ),
    )
    monkeypatch.setattr(
        dashboard_app,
        "dashboard_summary",
        lambda data_dir: {
            "database_exists": True,
            "item_count": 1,
            "match_count": 1,
            "latest_collected_at": "2026-06-12T09:00:00Z",
        },
    )
    monkeypatch.setattr(
        dashboard_app,
        "latest_candidate_report",
        lambda reports_dir: {
            "report_date": None,
            "generated_at": None,
            "candidate_count": 0,
            "rows": [],
            "error": "Could not parse latest report JSON fashion-radar-2026-06-11.json: bad json",
        },
    )
    monkeypatch.setattr(dashboard_app, "recent_signals", lambda data_dir: [])
    monkeypatch.setattr(dashboard_app, "top_entities", lambda data_dir, *, entity_type: [])
    monkeypatch.setattr(dashboard_app, "source_health_rows", lambda data_dir: [])
    monkeypatch.setattr(dashboard_app, "render_heat_movers", lambda *args, **kwargs: None)
    monkeypatch.setattr(dashboard_app, "render_trend_deltas", lambda *args, **kwargs: None)

    dashboard_app.main()

    assert fake_streamlit.warnings == [
        "Could not parse latest report JSON fashion-radar-2026-06-11.json: bad json"
    ]
    assert "No untracked candidate signals in the latest report." in fake_streamlit.infos


def test_render_trend_deltas_warns_for_missing_scoring_without_data_dir_creation(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "missing-data"
    config_dir.mkdir()
    fake_st = FakeStreamlit()

    render_trend_deltas(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings
    assert "Could not load trend config" in fake_st.warnings[0]
    assert fake_st.dataframes == []
    assert not data_dir.exists()


def test_render_trend_deltas_warns_for_invalid_entities_config(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: nope\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    render_trend_deltas(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings
    assert "Could not load trend config" in fake_st.warnings[0]
    assert fake_st.dataframes == []


def test_render_trend_deltas_warns_for_query_errors(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    def fail_query(**kwargs: object) -> TrendComparison:
        raise RuntimeError("bad trend read")

    monkeypatch.setattr(dashboard_app, "load_trend_comparison", fail_query)

    render_trend_deltas(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings == ["Could not read trend deltas: bad trend read"]
    assert fake_st.dataframes == []


def test_render_trend_deltas_shows_empty_state(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")
    fake_st = FakeStreamlit()

    def empty_query(**kwargs: object) -> TrendComparison:
        return TrendComparison(
            as_of=datetime(2026, 6, 12, tzinfo=UTC),
            baseline_as_of=datetime(2026, 6, 5, tzinfo=UTC),
            deltas=[],
        )

    monkeypatch.setattr(dashboard_app, "load_trend_comparison", empty_query)

    render_trend_deltas(
        fake_st,
        config_dir=config_dir,
        data_dir=data_dir,
        now=datetime(2026, 6, 12, tzinfo=UTC),
    )

    assert fake_st.warnings == []
    assert TREND_EMPTY_MESSAGE in fake_st.infos


def test_latest_candidate_rows_reads_latest_report(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-10.json").write_text(
        '{"metadata": {"report_date": "2026-06-10T00:00:00Z"}, "candidates": []}',
        encoding="utf-8",
    )
    (reports_dir / "fashion-radar-2026-06-11.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "generated_at": "2026-06-11T00:15:00Z",
                    "report_date": "2026-06-11T00:00:00Z",
                },
                "candidates": [
                    {
                        "phrase": "Le Teckel bag",
                        "candidate_type": "bag",
                        "label": "new_candidate",
                        "score": 3.0,
                        "weighted_mention_component": 2.0,
                        "growth_component": 0.5,
                        "source_diversity_component": 1.0,
                        "current_mentions": 2,
                        "baseline_mentions": 0,
                        "growth_ratio": None,
                        "distinct_sources": 2,
                        "first_seen_at": "2026-06-11T00:00:00Z",
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
            "weighted_mention_component": 2.0,
            "growth_component": 0.5,
            "source_diversity_component": 1.0,
            "current_mentions": 2,
            "baseline_mentions": 0,
            "growth_ratio": None,
            "distinct_sources": 2,
            "first_seen_at": "2026-06-11T00:00:00Z",
            "report_date": "2026-06-11T00:00:00Z",
        }
    ]
    assert report["report_date"] == "2026-06-11T00:00:00Z"
    assert report["generated_at"] == "2026-06-11T00:15:00Z"
    assert report["candidate_count"] == 1


def test_latest_candidate_rows_defaults_score_components_for_legacy_report(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
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

    assert latest_candidate_rows(reports_dir) == [
        {
            "phrase": "Le Teckel bag",
            "candidate_type": "bag",
            "label": "new_candidate",
            "score": 3.0,
            "weighted_mention_component": 0.0,
            "growth_component": 0.0,
            "source_diversity_component": 0.0,
            "current_mentions": 2,
            "baseline_mentions": 0,
            "growth_ratio": None,
            "distinct_sources": 2,
            "first_seen_at": None,
            "report_date": "2026-06-11T00:00:00Z",
        }
    ]


def test_latest_candidate_rows_preserves_legacy_growth_fields_without_components(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
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
                        "baseline_mentions": 1,
                        "growth_ratio": 2.0,
                        "distinct_sources": 2,
                        "first_seen_at": "2026-06-10T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    row = latest_candidate_rows(reports_dir)[0]

    assert row["weighted_mention_component"] == 0.0
    assert row["growth_component"] == 0.0
    assert row["source_diversity_component"] == 0.0
    assert row["growth_ratio"] == 2.0
    assert row["first_seen_at"] == "2026-06-10T00:00:00Z"


def test_latest_candidate_rows_returns_empty_for_missing_reports(tmp_path: Path) -> None:
    assert latest_candidate_rows(tmp_path / "reports") == []
    assert latest_candidate_report(tmp_path / "reports") == {
        "report_date": None,
        "generated_at": None,
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
        "generated_at": None,
        "candidate_count": 0,
        "rows": [],
    }


def test_latest_candidate_report_returns_error_metadata_for_malformed_json(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-11.json").write_text("{not-json", encoding="utf-8")

    report = latest_candidate_report(reports_dir)

    assert report["report_date"] is None
    assert report["candidate_count"] == 0
    assert report["rows"] == []
    assert report["error"].startswith("Could not parse latest report JSON")
