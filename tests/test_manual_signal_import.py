import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import func, select

from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import collector_runs, initialize_schema, source_health
from fashion_radar.importers.manual_signals import (
    ManualSignalImportError,
    load_manual_signal_rows,
    store_manual_signal_rows,
)
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceType


def test_loads_manual_signal_csv_rows(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,platform,source_weight\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,"
        "Short note,Manual Export,manual,1.4\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Fallback")

    assert len(rows) == 1
    assert rows[0].url == "https://example.com/a"
    assert rows[0].title == "Le Teckel bag"
    assert rows[0].summary == "Short note"
    assert rows[0].source_name == "Manual Export"
    assert rows[0].source_weight == 1.4
    assert rows[0].published_at == datetime(2026, 6, 12, 8, 0, tzinfo=UTC)


def test_loads_manual_signal_json_items_object(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "url": "https://example.com/b",
                        "title": "Mary Jane flats",
                        "published_at": "2026-06-12T09:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].source_name == "Manual Import"
    assert rows[0].summary is None


def test_loads_manual_signal_json_top_level_list(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/list",
                    "title": "East-west tote",
                    "published_at": "2026-06-12T09:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert len(rows) == 1
    assert rows[0].url == "https://example.com/list"


def test_manual_signal_import_normalizes_collected_at_to_utc(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/d",
                    "title": "Suede sneakers",
                    "published_at": "2026-06-12T09:00:00+02:00",
                    "collected_at": "2026-06-12T13:30:00+02:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].published_at == datetime(2026, 6, 12, 7, 0, tzinfo=UTC)
    assert rows[0].collected_at == datetime(2026, 6, 12, 11, 30, tzinfo=UTC)


def test_manual_signal_import_rejects_invalid_rows_atomically(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\n"
        "https://example.com/a,Valid,2026-06-12T08:00:00Z\n"
        ",Missing URL,2026-06-12T09:00:00Z\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 3"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_ignores_private_extra_fields(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/c",
                    "title": "Mesh flats",
                    "published_at": "2026-06-12T09:00:00Z",
                    "author_handle": "@private",
                    "raw_comment": "do not store",
                    "account_id": "secret",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")

    assert rows[0].model_dump() == {
        "url": "https://example.com/c",
        "title": "Mesh flats",
        "published_at": rows[0].published_at,
        "summary": None,
        "source_name": "Manual Import",
        "platform": None,
        "source_weight": 1.0,
        "collected_at": None,
    }


def test_manual_signal_import_ignores_unknown_csv_columns(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,author_handle,raw_comment,account_id\n"
        "https://example.com/e,Mesh flats,2026-06-12T09:00:00Z,"
        "@private,do not store,secret\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows[0].model_dump().keys() == {
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    }


def test_manual_signal_import_normalizes_blank_optional_csv_values(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,platform,source_name,source_weight,collected_at\n"
        'https://example.com/f,Boat shoes,2026-06-12T09:00:00Z," "," "," "," "," "\n',
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows[0].summary is None
    assert rows[0].platform is None
    assert rows[0].source_name == "Manual Import"
    assert rows[0].source_weight == 1.0
    assert rows[0].collected_at is None


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ({}, "JSON import must be a list or an object with an items list"),
        ({"items": {}}, "JSON import must be a list or an object with an items list"),
        ([1], "row 1"),
    ],
)
def test_manual_signal_import_rejects_invalid_json_shapes(
    tmp_path: Path,
    payload: object,
    match: str,
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match=match):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


def test_manual_signal_import_rejects_empty_csv_without_headers(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="CSV file must contain headers"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_allows_empty_csv_with_headers(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text("url,title,published_at\n", encoding="utf-8")

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    assert rows == []


def test_manual_signal_import_rejects_csv_rows_with_extra_cells(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Valid,2026-06-12T08:00:00Z,unexpected\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 2"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_manual_signal_import_normalizes_blank_default_source_name(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/a,Valid,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )

    rows = load_manual_signal_rows(path, input_format="csv", default_source_name=" ")

    assert rows[0].source_name == "Manual Import"


@pytest.mark.parametrize(
    "row",
    [
        {"url": "https://example.com/g", "published_at": "2026-06-12T09:00:00Z"},
        {"url": "https://example.com/g", "title": "", "published_at": "2026-06-12T09:00:00Z"},
        {"url": "https://example.com/g", "title": "No date"},
        {"url": "https://example.com/g", "title": "Blank date", "published_at": " "},
    ],
)
def test_manual_signal_import_rejects_missing_or_blank_required_fields(
    tmp_path: Path,
    row: dict[str, str],
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps([row]), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="row 1"):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


@pytest.mark.parametrize(
    "row",
    [
        {
            "url": "https://example.com/h",
            "title": "Bad published date",
            "published_at": "not-a-date",
        },
        {
            "url": "https://example.com/h",
            "title": "Bad collected date",
            "published_at": "2026-06-12T09:00:00Z",
            "collected_at": "not-a-date",
        },
    ],
)
def test_manual_signal_import_rejects_invalid_dates(
    tmp_path: Path,
    row: dict[str, str],
) -> None:
    path = tmp_path / "signals.json"
    path.write_text(json.dumps([row]), encoding="utf-8")

    with pytest.raises(ManualSignalImportError, match="row 1"):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


def test_manual_signal_import_rejects_json_null_published_at(tmp_path: Path) -> None:
    path = tmp_path / "signals.json"
    path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/null-date",
                    "title": "Null published date",
                    "published_at": None,
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 1"):
        load_manual_signal_rows(path, input_format="json", default_source_name="Manual Import")


def test_manual_signal_import_rejects_short_csv_rows(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at\nhttps://example.com/short,Short CSV row\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 2"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


@pytest.mark.parametrize("source_weight", ["0", "-0.1", "5.1", "not-a-number"])
def test_manual_signal_import_rejects_invalid_source_weight(
    tmp_path: Path,
    source_weight: str,
) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,source_weight\n"
        f"https://example.com/i,Invalid weight,2026-06-12T09:00:00Z,{source_weight}\n",
        encoding="utf-8",
    )

    with pytest.raises(ManualSignalImportError, match="row 2"):
        load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")


def test_store_manual_signal_rows_writes_sanitized_items(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,source_weight,collected_at,"
        "platform,author_handle,raw_comment,account_id\n"
        "https://example.com/a,Le Teckel bag,2026-06-12T08:00:00Z,Short note,"
        "Manual Export,1.4,2026-06-12T10:00:00Z,manual,@private,do not store,secret\n"
        "https://example.com/b,Mary Jane flats,2026-06-12T09:00:00Z,, , , ,"
        "manual,@private,do not store,secret\n",
        encoding="utf-8",
    )
    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Fallback Export")

    result = store_manual_signal_rows(
        engine,
        rows=rows,
        imported_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert result.rows_seen == 2
    assert result.rows_imported == 2
    assert result.items_added == 2

    repository = ItemRepository(engine)
    first = repository.get_item(1)
    second = repository.get_item(2)
    assert first["source_type"] == "manual_import"
    assert first["source_name"] == "Manual Export"
    assert first["source_weight"] == 1.4
    assert first["summary"] == "Short note"
    assert first["collected_at"] == "2026-06-12T10:00:00+00:00"
    assert second["source_type"] == "manual_import"
    assert second["source_name"] == "Fallback Export"
    assert second["source_weight"] == 1.0
    assert second["summary"] is None
    assert second["collected_at"] == "2026-06-12T12:00:00+00:00"
    assert "platform" not in first
    assert "author_handle" not in first
    assert "raw_comment" not in first
    assert "account_id" not in first
    with engine.connect() as connection:
        collector_run_count = connection.execute(
            select(func.count()).select_from(collector_runs)
        ).scalar_one()
        source_health_count = connection.execute(
            select(func.count()).select_from(source_health)
        ).scalar_one()
    assert collector_run_count == 0
    assert source_health_count == 0


def test_store_manual_signal_rows_preserves_existing_normalized_url_upsert(
    tmp_path: Path,
) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    repository = ItemRepository(engine)
    existing_id = repository.upsert_item(
        CollectedItem(
            source_name="Vogue",
            source_type=SourceType.RSS,
            url="https://example.com/a?utm_source=newsletter",
            title="Original coverage",
            published_at=datetime(2026, 6, 11, 8, 0, tzinfo=UTC),
            summary="Original summary",
        ),
        source_weight=1.2,
        collected_at=datetime(2026, 6, 11, 9, 0, tzinfo=UTC),
    )
    path = tmp_path / "signals.csv"
    path.write_text(
        "url,title,published_at,summary,source_name,source_weight\n"
        "https://example.com/a,Manual update,2026-06-12T08:00:00Z,"
        "Manual summary,Manual Export,1.4\n",
        encoding="utf-8",
    )
    rows = load_manual_signal_rows(path, input_format="csv", default_source_name="Manual Import")

    result = store_manual_signal_rows(
        engine,
        rows=rows,
        imported_at=datetime(2026, 6, 12, 12, 0, tzinfo=UTC),
    )

    assert result.rows_seen == 1
    assert result.rows_imported == 1
    assert result.items_added == 0
    assert repository.count_items() == 1
    item = repository.get_item(existing_id)
    assert item["source_type"] == "manual_import"
    assert item["source_name"] == "Manual Export"
    assert item["title"] == "Manual update"
