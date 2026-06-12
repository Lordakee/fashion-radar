from __future__ import annotations

import json
from pathlib import Path

from fashion_radar.dashboard.app import CANDIDATE_SIGNAL_CAPTION, parse_args
from fashion_radar.dashboard.queries import (
    dashboard_summary,
    database_path,
    latest_candidate_report,
    latest_candidate_rows,
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
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType


def test_dashboard_helpers_import_without_streamlit() -> None:
    assert database_path(Path("/tmp/fashion-radar-data")) == Path(
        "/tmp/fashion-radar-data/fashion-radar.sqlite"
    )


def test_dashboard_parse_args_ignores_unknown_streamlit_args(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "app.py",
            "--data-dir",
            "/tmp/data",
            "--reports-dir",
            "/tmp/reports",
            "--theme.base",
            "light",
        ],
    )

    args = parse_args()

    assert args.data_dir == Path("/tmp/data")
    assert args.reports_dir == Path("/tmp/reports")


def test_dashboard_candidate_caption_mentions_imported_local_signals() -> None:
    assert "configured sources and imported local signals" in CANDIDATE_SIGNAL_CAPTION
    assert "complete platform coverage" not in CANDIDATE_SIGNAL_CAPTION.lower()


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
