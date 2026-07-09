from __future__ import annotations

import http.client
import json
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import func, select
from typer.testing import CliRunner

import fashion_radar.cli as cli_module
from fashion_radar.cli import app
from fashion_radar.db.engine import create_sqlite_engine
from fashion_radar.db.repositories import ItemRepository
from fashion_radar.db.schema import initialize_schema, item_entities, items
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import (
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
    empty_daily_brief,
)
from fashion_radar.models.source import SourceType
from fashion_radar.row_one.edition import build_row_one_edition
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
)
from fashion_radar.row_one.render import render_row_one_site
from fashion_radar.row_one.server import (
    create_row_one_http_server,
    format_row_one_site_access_message,
    format_row_one_site_url,
)
from fashion_radar.row_one.site_metrics import RowOneLocalArticleSiteMetrics
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.workflows import default_database_path

AS_OF = "2026-07-02T04:00:00Z"
ROOT = Path(__file__).resolve().parents[1]
ROW_ONE_APP_SCHEMA = ROOT / "schemas" / "row-one-app.schema.json"


def _row_one_app_schema_validator() -> Draft202012Validator:
    schema = json.loads(ROW_ONE_APP_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _write_minimal_config(config_dir: Path) -> None:
    config_dir.mkdir(parents=True)
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")
    (config_dir / "entities.yaml").write_text("version: 1\nentities: []\n", encoding="utf-8")
    (config_dir / "scoring.yaml").write_text(
        "version: 1\n"
        "scoring:\n"
        "  current_window_days: 7\n"
        "  baseline_window_days: 30\n"
        "candidate_discovery:\n"
        "  enabled: true\n"
        "  max_candidates: 20\n",
        encoding="utf-8",
    )


def _empty_report() -> DailyReport:
    return DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        brief=empty_daily_brief(),
        entities=[],
        candidates=[],
    )


def _story_ref_report() -> DailyReport:
    return DailyReport(
        metadata=ReportMetadata(generated_at=AS_OF, report_date=AS_OF, item_count=1),
        brief=empty_daily_brief(),
        entities=[
            EntityReport(
                entity_name="The Row",
                entity_type="brand",
                label="rising",
                heat_score=6.2,
                current_mentions=4,
                baseline_mentions=1,
                distinct_sources=1,
                representative_items=[
                    RepresentativeItem(
                        source_name="Local Desk",
                        source_url="https://example.com/status-story-refs",
                        published_at=AS_OF,
                        title="The Row showroom appointment demand rises",
                        summary="Local desk notes rising interest in The Row appointments.",
                    )
                ],
            )
        ],
        candidates=[],
    )


def _render_status_fixture_site(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(
            report=_story_ref_report(),
            recent_items=[],
            as_of=AS_OF,
        ),
        tmp_path,
    )


def _render_populated_status_site(tmp_path: Path) -> dict[str, object]:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/status-integrity",
                "title": "The Row local article evidence strengthens",
                "summary": "Local desk notes a concrete product and brand signal.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    return payload["stories"][0]


def _render_status_site_with_local_article(tmp_path: Path) -> dict[str, object]:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/local-article",
                "title": "The Row and Margaux local source strengthens",
                "summary": "Local desk notes The Row and Margaux are moving together.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    story = edition.stories[0]
    story.entity_refs = [RowOneReference(name="The Row", type="brand", label="tracked")]
    story.product_refs = [RowOneReference(name="Margaux", type="bag", label="product")]
    story.heat_delta = 5
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row local source",
        url="https://example.com/local-article",
        source_name="Local Desk",
        extracted_at=AS_OF,
        paragraphs=[
            "The Row source paragraph.",
            "Margaux product paragraph.",
        ],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="正文重点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="来源导语", en="Source lead"),
                        body=LocalizedText(
                            zh="The Row 来源段落。",
                            en="The Row source paragraph.",
                        ),
                        paragraph_indices=[0],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品信号", en="Product Signals"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="Margaux", en="Margaux"),
                        body=LocalizedText(
                            zh="Margaux 产品段落。",
                            en="Margaux product paragraph.",
                        ),
                        paragraph_indices=[1],
                    )
                ],
            ),
        ],
    )
    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )
    payload = json.loads((tmp_path / "data" / "edition.json").read_text(encoding="utf-8"))
    return payload["stories"][0]


def _write_stale_local_article_sidecar(output_dir: Path) -> Path:
    articles_dir = output_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    article = RowOneLocalArticle(
        story_id="stale-row-one-story-1234567890",
        title="Stale article",
        url="https://example.com/stale-article",
        source_name="Old Source",
        extracted_at=AS_OF,
        paragraphs=["Stale paragraph that should not count for this render."],
    )
    article_path = articles_dir / "stale-row-one-story-1234567890.json"
    article_path.write_text(
        json.dumps(article.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )
    return article_path


def _seed_collected_item(data_dir: Path, *, title: str, url: str) -> None:
    engine = create_sqlite_engine(default_database_path(data_dir))
    try:
        initialize_schema(engine)
        ItemRepository(engine).upsert_item(
            CollectedItem(
                source_name="Local Desk",
                source_type=SourceType.RSS,
                url=url,
                title=title,
                published_at=AS_OF,
                summary="国内设计师品牌热度上升。",
            ),
            collected_at=parse_datetime_utc(AS_OF),
        )
    finally:
        engine.dispose()


def test_row_one_build_command_writes_empty_state_site(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "build",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
            "--output-dir",
            str(output_dir),
            "--latest-only",
        ],
    )

    assert result.exit_code == 0
    assert "Wrote ROW ONE site" in result.output
    assert "0 stories" in result.output
    assert "Saved local articles: 0" in result.output
    assert "Saved local paragraphs: 0" in result.output
    assert "Extracted local articles: 0" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "edition.json").exists()
    assert "No ROW ONE stories" in (output_dir / "index.html").read_text(encoding="utf-8")


def test_row_one_preview_builds_site_and_prints_readiness(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "preview",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--latest-only",
            "--dry-run-serve-url",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "edition.json").exists()
    assert "ROW ONE preview" in result.output
    assert f"Site: {output_dir / 'index.html'}" in result.output
    assert f"JSON: {output_dir / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {output_dir / 'data' / 'manifest.json'}" in result.output
    assert "Stories:" in result.output
    assert "Sections:" in result.output
    assert "Evidence links:" in result.output
    assert "Saved local articles: 0" in result.output
    assert "Saved local paragraphs: 0" in result.output
    assert "Extracted local articles: 0" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output
    assert "Empty sections:" in result.output
    assert "Generated at:" in result.output
    assert "Readiness:" in result.output
    assert "Open:" in result.output


@pytest.mark.parametrize(
    ("command_name", "extra_args"),
    [
        ("build", []),
        ("preview", ["--dry-run-serve-url"]),
    ],
)
def test_row_one_build_and_preview_metrics_ignore_stale_sidecars_without_latest_only(
    tmp_path: Path,
    command_name: str,
    extra_args: list[str],
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    stale_article_path = _write_stale_local_article_sidecar(output_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            command_name,
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            *extra_args,
        ],
    )

    assert result.exit_code == 0, result.output
    assert stale_article_path.exists()
    assert "Saved local articles: 0" in result.output
    assert "Saved local paragraphs: 0" in result.output
    assert "Extracted local articles: 0" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output


def test_row_one_preview_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "preview", "--help"])

    assert result.exit_code == 0
    assert "Build a ROW ONE preview" in result.output
    assert "dry-run" in result.output
    assert "Print the local" in result.output


def _patch_successful_row_one_refresh_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    calls: list[str],
) -> None:
    class StoredMatches:
        matches_stored = 4

    def collect_configured_sources(**kwargs: object) -> None:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["sources"] == []
        assert kwargs["now"] == AS_OF
        calls.append("collect_configured_sources")

    def match_stored_items(**kwargs: object) -> StoredMatches:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["entities"] == []
        calls.append("match_stored_items")
        return StoredMatches()

    def write_daily_report_files(**kwargs: object) -> tuple[Path, Path]:
        assert kwargs["data_dir"] == data_dir
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        assert kwargs["scoring"] is not None
        assert kwargs["candidate_discovery"] is not None
        assert kwargs["entity_config"] is not None
        calls.append("write_daily_report_files")
        return reports_dir / "daily.md", reports_dir / "daily.json"

    def prune_stale_daily_report_files(**kwargs: object) -> SimpleNamespace:
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("prune_stale_daily_report_files")
        return SimpleNamespace(
            current_date="2026-07-02",
            removed_count=3,
            kept_current_count=3,
        )

    def write_row_one_site_from_cli_options(**kwargs: object) -> SimpleNamespace:
        assert kwargs == {
            "config_dir": config_dir,
            "data_dir": data_dir,
            "reports_dir": reports_dir,
            "output_dir": output_dir,
            "as_of": AS_OF,
            "latest_only": True,
        }
        calls.append("_write_row_one_site_from_cli_options")
        return SimpleNamespace(
            index_path=output_dir / "index.html",
            output_dir=output_dir,
            story_count=0,
            edition=build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
            local_article_metrics=RowOneLocalArticleSiteMetrics(),
        )

    monkeypatch.setattr(cli_module, "collect_configured_sources", collect_configured_sources)
    monkeypatch.setattr(cli_module, "match_stored_items", match_stored_items)
    monkeypatch.setattr(cli_module, "write_daily_report_files", write_daily_report_files)
    monkeypatch.setattr(
        cli_module,
        "prune_stale_daily_report_files",
        prune_stale_daily_report_files,
    )
    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_row_one_site_from_cli_options,
    )


def test_row_one_refresh_runs_pipeline_and_writes_site(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )

    def clean_old_data(**kwargs: object) -> SimpleNamespace:
        assert kwargs == {
            "data_dir": data_dir,
            "as_of": AS_OF,
            "retention_days": 1,
        }
        calls.append("clean_old_data")
        return SimpleNamespace(items_deleted=5, item_entities_deleted=7, dry_run=False)

    monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == [
        "collect_configured_sources",
        "match_stored_items",
        "write_daily_report_files",
        "_write_row_one_site_from_cli_options",
        "prune_stale_daily_report_files",
        "clean_old_data",
    ]
    assert "ROW ONE refresh" in result.output
    assert "Stored matches: 4" in result.output
    assert f"Markdown report: {reports_dir / 'daily.md'}" in result.output
    assert f"JSON report: {reports_dir / 'daily.json'}" in result.output
    assert f"HTML report: {reports_dir / 'daily.html'}" in result.output
    assert "Latest-only reports: removed 3 stale files for 2026-07-02; kept 3 current files" in (
        result.output
    )
    assert (
        "SQLite retention: pruned 5 old items and 7 item/entity matches; retention window 1 days"
        in result.output
    )
    assert f"Site: {output_dir / 'index.html'}" in result.output
    assert f"JSON: {output_dir / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {output_dir / 'data' / 'manifest.json'}" in result.output
    assert "Stories:" in result.output
    assert "Evidence links:" in result.output
    assert "Saved local articles: 0" in result.output
    assert "Saved local paragraphs: 0" in result.output
    assert "Extracted local articles: 0" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output
    assert "Readiness:" in result.output
    assert "Open: http://127.0.0.1:8787" in result.output


def test_row_one_refresh_can_skip_sqlite_retention(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )

    def clean_old_data(**_kwargs: object) -> object:
        raise AssertionError("clean_old_data must not run with --skip-data-retention")

    monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
            "--skip-data-retention",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "SQLite retention: skipped" in result.output
    assert "clean_old_data" not in calls


def test_row_one_refresh_warns_when_sqlite_retention_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    calls: list[str] = []
    _patch_successful_row_one_refresh_pipeline(
        monkeypatch,
        config_dir=config_dir,
        data_dir=data_dir,
        reports_dir=reports_dir,
        output_dir=output_dir,
        calls=calls,
    )

    def clean_old_data(**_kwargs: object) -> object:
        calls.append("clean_old_data")
        raise RuntimeError("database locked")

    monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "refresh",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--as-of",
            AS_OF,
        ],
    )

    assert result.exit_code == 0, result.output
    assert "SQLite retention: failed: database locked" in result.output
    assert "ROW ONE refresh failed" not in result.output
    assert calls[-1] == "clean_old_data"


def test_row_one_refresh_prunes_old_sqlite_items_after_successful_refresh(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    engine = create_sqlite_engine(default_database_path(data_dir))
    try:
        initialize_schema(engine)
        repository = ItemRepository(engine)
        old_id = repository.upsert_item(
            CollectedItem(
                source_name="Old Source",
                source_type=SourceType.RSS,
                url="https://example.com/old",
                title="Old signal",
                published_at="2026-07-01T00:00:00Z",
                summary="old",
            ),
            collected_at=parse_datetime_utc("2026-07-01T00:00:00Z"),
        )
        repository.replace_item_matches(
            old_id,
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
        current_id = repository.upsert_item(
            CollectedItem(
                source_name="Current Source",
                source_type=SourceType.RSS,
                url="https://example.com/current",
                title="Current signal",
                published_at=AS_OF,
                summary="current",
            ),
            collected_at=parse_datetime_utc(AS_OF),
        )

        calls: list[str] = []
        _patch_successful_row_one_refresh_pipeline(
            monkeypatch,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            calls=calls,
        )

        result = CliRunner().invoke(
            app,
            [
                "row-one",
                "refresh",
                "--config-dir",
                str(config_dir),
                "--data-dir",
                str(data_dir),
                "--reports-dir",
                str(reports_dir),
                "--output-dir",
                str(output_dir),
                "--as-of",
                AS_OF,
                "--retention-days",
                "1",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "SQLite retention: pruned 1 old items and 1 item/entity matches" in result.output
        assert repository.count_items() == 1
        with engine.connect() as conn:
            remaining_items = conn.execute(select(items.c.id, items.c.url)).mappings().all()
            remaining_matches = conn.execute(
                select(func.count()).select_from(item_entities)
            ).scalar_one()
        assert [(row["id"], row["url"]) for row in remaining_items] == [
            (current_id, "https://example.com/current")
        ]
        assert remaining_matches == 0
    finally:
        engine.dispose()


def test_row_one_refresh_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "refresh", "--help"])

    assert result.exit_code == 0
    assert "Refresh ROW ONE" in result.output
    assert "--output-dir" in result.output
    assert "--host" in result.output
    assert "--port" in result.output
    assert "--retention-days" in result.output
    assert "--skip-data-retention" in result.output


def test_row_one_local_ops_command_prints_runbook(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "local-ops",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local daily ops" in result.output
    assert "fashion-radar row-one refresh" in result.output
    assert "Source checkout commands:" in result.output
    assert f"cd {tmp_path}" in result.output
    assert "uv run fashion-radar row-one refresh" in result.output
    assert "uv run fashion-radar row-one preview" in result.output
    assert "uv run fashion-radar row-one status" in result.output
    assert "uv run fashion-radar row-one serve" in result.output
    assert "fashion-radar row-one preview" in result.output
    assert "fashion-radar row-one status" in result.output
    assert "fashion-radar row-one serve" in result.output
    assert "fashion-radar run" not in result.output
    assert "fashion-radar row-one build" not in result.output
    assert not re.search(r"fashion-radar row-one refresh\b[^\n]*--latest-only", result.output)
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "0 4 * * *" in result.output
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not output_dir.exists()


def test_row_one_local_ops_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "local-ops", "--help"])

    assert result.exit_code == 0
    assert "Print ROW ONE local daily ops runbook" in result.output
    assert "--time" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_row_one_ops_check_json_forwards_options_and_as_of(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"
    captured: dict[str, object] = {}

    def build_payload(
        *,
        site_dir: Path,
        host: str,
        port: int,
        unit_dir: Path,
        as_of: object,
    ) -> dict[str, object]:
        captured.update(
            {
                "site_dir": site_dir,
                "host": host,
                "port": port,
                "unit_dir": unit_dir,
                "as_of": as_of,
            }
        )
        return {
            "ok": True,
            "status": "attention",
            "site_dir": str(site_dir),
            "as_of": "2026-07-07T08:00:00Z",
            "freshness": {"status": "stale"},
            "server": {"status": "serving_other"},
            "systemd": {"status": "missing"},
            "access": {
                "message": "Open locally: http://127.0.0.1:8787",
                "local_url": "http://127.0.0.1:8787",
                "lan_url_hint": "http://<LAN-IP>:8787",
            },
            "actions": ["检查本地 ROW ONE 服务。"],
        }

    monkeypatch.setattr(
        cli_module,
        "build_row_one_ops_check_payload",
        build_payload,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(site_dir),
            "--unit-dir",
            str(unit_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--as-of",
            "2026-07-07T08:00:00Z",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured == {
        "site_dir": site_dir,
        "host": "127.0.0.1",
        "port": 8787,
        "unit_dir": unit_dir,
        "as_of": parse_datetime_utc("2026-07-07T08:00:00Z"),
    }
    assert '\n  "status": "attention"' in result.output
    assert "检查本地 ROW ONE 服务。" in result.output
    payload = json.loads(result.output)
    assert payload["freshness"]["status"] == "stale"
    assert payload["systemd"]["status"] == "missing"
    assert payload["access"]["local_url"] == "http://127.0.0.1:8787"


def test_row_one_ops_check_human_output_is_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    site_dir = tmp_path / "site"
    unit_dir = tmp_path / "units"

    def build_payload(
        *,
        site_dir: Path,
        host: str,
        port: int,
        unit_dir: Path,
        as_of: object,
    ) -> dict[str, object]:
        return {
            "ok": True,
            "status": "ready",
            "site_dir": str(site_dir),
            "as_of": "2026-07-07T08:00:00Z",
            "freshness": {"status": "fresh"},
            "server": {"status": "serving_row_one"},
            "systemd": {"status": "present"},
            "local_article_routes": {"status": "missing", "article_count": 1},
            "access": {
                "message": (
                    "Open locally: http://127.0.0.1:8787\nOpen from LAN: http://<LAN-IP>:8787"
                ),
                "local_url": "http://127.0.0.1:8787",
                "lan_url_hint": "http://<LAN-IP>:8787",
            },
            "actions": ["Review user systemd units."],
        }

    monkeypatch.setattr(
        cli_module,
        "build_row_one_ops_check_payload",
        build_payload,
        raising=False,
    )
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(site_dir),
            "--unit-dir",
            str(unit_dir),
            "--as-of",
            "2026-07-07T08:00:00Z",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE ops check" in result.output
    assert "Status: ready" in result.output
    assert "Freshness: fresh" in result.output
    assert "Server: serving_row_one" in result.output
    assert "Systemd units: present" in result.output
    assert "Local article routes: missing" in result.output
    assert "Access:" in result.output
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Actions:" in result.output
    assert "- Review user systemd units." in result.output
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert after == before


def test_row_one_ops_check_rejects_malformed_as_of(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def build_payload(**_kwargs: object) -> dict[str, object]:
        raise AssertionError("diagnostic builder must not run for malformed --as-of")

    monkeypatch.setattr(
        cli_module,
        "build_row_one_ops_check_payload",
        build_payload,
        raising=False,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "ops-check",
            "--site-dir",
            str(tmp_path / "site"),
            "--as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code != 0
    assert "must be an ISO datetime" in result.output


def test_row_one_install_local_dry_run_prints_systemd_files(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--dry-run",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local install dry run" in result.output
    assert f"Target unit directory: {Path.home() / '.config' / 'systemd' / 'user'}" in result.output
    assert "# ~/.config/systemd/user/row-one-refresh.service" in result.output
    assert "# ~/.config/systemd/user/row-one-refresh.timer" in result.output
    assert "# ~/.config/systemd/user/row-one-serve.service" in result.output
    assert "Description=ROW ONE daily site refresh" in result.output
    assert "Description=ROW ONE fixed local web server" in result.output
    assert "OnCalendar=*-*-* 04:00:00" in result.output
    assert "uv run fashion-radar row-one refresh" in result.output
    assert "uv run fashion-radar row-one serve" in result.output
    assert '--host "$ROW_ONE_HOST"' in result.output
    assert "systemctl --user daemon-reload" in result.output
    assert "systemctl --user enable --now row-one-refresh.timer" in result.output
    assert "systemctl --user enable --now row-one-serve.service" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert not (tmp_path / ".config" / "systemd" / "user").exists()


def test_row_one_install_local_dry_run_prints_custom_unit_dir(tmp_path: Path) -> None:
    unit_dir = tmp_path / "custom-systemd-user"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--dry-run",
            "--project-dir",
            str(tmp_path),
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert f"Target unit directory: {unit_dir}" in result.output
    assert f"# {unit_dir / 'row-one-refresh.service'}" in result.output
    assert f"# {unit_dir / 'row-one-refresh.timer'}" in result.output
    assert f"# {unit_dir / 'row-one-serve.service'}" in result.output
    assert not unit_dir.exists()


def test_row_one_install_local_writes_user_systemd_units(tmp_path: Path) -> None:
    unit_dir = tmp_path / "systemd-user"
    output_dir = tmp_path / "reports" / "row-one" / "site"

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--project-dir",
            str(tmp_path),
            "--config-dir",
            str(tmp_path / "configs"),
            "--data-dir",
            str(tmp_path / "data"),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--output-dir",
            str(output_dir),
            "--time",
            "04:00",
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE local install" in result.output
    assert f"Wrote units to: {unit_dir}" in result.output
    assert "Before enabling on a fresh install, generate the site once:" in result.output
    refresh_service = (unit_dir / "row-one-refresh.service").read_text(encoding="utf-8")
    refresh_timer = (unit_dir / "row-one-refresh.timer").read_text(encoding="utf-8")
    serve_service = (unit_dir / "row-one-serve.service").read_text(encoding="utf-8")
    assert "uv run fashion-radar row-one refresh" in refresh_service
    assert f'Environment="ROW_ONE_OUTPUT_DIR={output_dir}"' in refresh_service
    assert "OnCalendar=*-*-* 04:00:00" in refresh_timer
    assert "uv run fashion-radar row-one serve" in serve_service
    assert f'Environment="ROW_ONE_SITE_DIR={output_dir}"' in serve_service
    assert 'Environment="ROW_ONE_HOST=0.0.0.0"' in serve_service
    assert 'Environment="ROW_ONE_PORT=8787"' in serve_service
    assert (
        'Environment="PATH=%h/.local/bin:%h/.cargo/bin:/usr/local/bin:/usr/bin:/bin"'
        in serve_service
    )


def test_row_one_install_local_refuses_existing_unit_without_force(tmp_path: Path) -> None:
    unit_dir = tmp_path / "systemd-user"
    unit_dir.mkdir()
    (unit_dir / "row-one-serve.service").write_text("custom user service\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "install-local",
            "--project-dir",
            str(tmp_path),
            "--unit-dir",
            str(unit_dir),
        ],
    )

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert "Use --force" in result.output
    assert (unit_dir / "row-one-serve.service").read_text(
        encoding="utf-8"
    ) == "custom user service\n"


def test_row_one_install_local_help_is_discoverable() -> None:
    result = CliRunner().invoke(app, ["row-one", "install-local", "--help"])

    assert result.exit_code == 0
    assert "Render or install ROW ONE user systemd units" in result.output
    assert "--dry-run" in result.output
    assert "--time" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_row_one_build_command_writes_non_ascii_story_detail_path(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _seed_collected_item(
        data_dir,
        title="上海新锐设计师品牌升温",
        url="https://example.com/row-one-cli-cn",
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "build",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--reports-dir",
            str(reports_dir),
            "--as-of",
            AS_OF,
            "--output-dir",
            str(output_dir),
            "--latest-only",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads((output_dir / "data" / "edition.json").read_text(encoding="utf-8"))
    assert payload["contract_version"] == "row-one-app/v7"
    assert payload["signal_synthesis"]["boundaries"] == {
        "zh": "本地观察，需人工复核。",
        "en": "Local observed signals; review required.",
    }
    story = next(
        story for story in payload["stories"] if story["headline"] == "上海新锐设计师品牌升温"
    )
    detail_path = story["detail_path"]
    assert story["detail_href"] == detail_path
    assert story["href"] == detail_path
    assert detail_path.startswith("details/story-")
    assert detail_path.endswith(".html")
    assert detail_path.isascii()
    assert "%" not in detail_path
    assert payload["story_directory"]["story_count"] == payload["story_count"]
    assert story["id"] in payload["story_directory"]["story_ids"]
    route = next(
        route for route in payload["story_directory"]["routes"] if route["story_id"] == story["id"]
    )
    assert route == {
        "story_id": story["id"],
        "detail_href": detail_path,
        "section_key": story["section_key"],
        "section_href": story["section"]["href"],
        "published_date": story["published_date"],
    }
    assert (output_dir / detail_path).exists()
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="edition-nav"' in index_html
    assert 'class="edition-rail"' in index_html
    assert 'class="edition-nav-item edition-rail-item"' in index_html
    assert 'href="#top_stories"' in index_html
    assert "上海新锐设计师品牌升温" in index_html


def test_row_one_serve_dry_run_prints_url(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "http://127.0.0.1:8787" in result.output


def test_row_one_serve_dry_run_guides_wildcard_host(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output
    assert "Bound to 0.0.0.0:8787" in result.output
    assert "no authentication" in result.output
    assert "http://0.0.0.0:8787" not in result.output


def test_row_one_serve_dry_run_rejects_unmarked_directory(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "site marker" in result.output


def test_row_one_serve_dry_run_does_not_bind_requested_port(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html>ROW ONE</html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        occupied_port = int(listener.getsockname()[1])

        result = CliRunner().invoke(
            app,
            [
                "row-one",
                "serve",
                "--site-dir",
                str(site_dir),
                "--host",
                "127.0.0.1",
                "--port",
                str(occupied_port),
                "--dry-run",
            ],
        )

    assert result.exit_code == 0
    assert f"http://127.0.0.1:{occupied_port}" in result.output


def test_row_one_serve_dry_run_rejects_marked_directory_without_index(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            "8787",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "index.html" in result.output


def test_row_one_status_prints_generated_site_readiness(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "status",
            "--site-dir",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE status" in result.output
    assert f"Site: {tmp_path}" in result.output
    assert f"Runtime: {tmp_path / 'data' / 'runtime.json'}" in result.output
    assert f"JSON: {tmp_path / 'data' / 'edition.json'}" in result.output
    assert f"Manifest: {tmp_path / 'data' / 'manifest.json'}" in result.output
    assert "Stories: 0" in result.output
    assert "Sections: 5" in result.output
    assert "Evidence links: 0" in result.output
    assert "Saved local articles: 0" in result.output
    assert "Saved local paragraphs: 0" in result.output
    assert "Extracted local articles: 0" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output
    assert "Refresh time: 04:00" in result.output
    assert "Generated at: 2026-07-02T04:00:00Z" in result.output
    assert "Readiness: empty" in result.output
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Open from LAN: http://<LAN-IP>:8787" in result.output


def test_row_one_status_json_outputs_machine_readable_payload(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["site_dir"] == str(tmp_path)
    assert payload["paths"] == {
        "manifest": "data/manifest.json",
        "edition": "data/edition.json",
        "runtime": "data/runtime.json",
    }
    assert payload["runtime"]["contract_version"] == "row-one-runtime/v1"
    assert payload["manifest"]["contract_version"] == "row-one-manifest/v1"
    assert payload["contracts"] == {
        "app": "row-one-app/v7",
        "manifest": "row-one-manifest/v1",
        "runtime": "row-one-runtime/v1",
    }
    assert payload["story_count"] == 0
    assert payload["site"] == {
        "index_path": "index.html",
        "manifest_path": "data/manifest.json",
        "edition_path": "data/edition.json",
        "runtime_path": "data/runtime.json",
    }
    assert payload["serve"] == {
        "default_host": "127.0.0.1",
        "default_port": 8787,
        "local_url": "http://127.0.0.1:8787",
        "lan_url_hint": "http://<LAN-IP>:8787",
    }
    assert payload["refresh"]["recommended_time"] == "04:00"
    assert payload["refresh"]["latest_only_cleanup"] is True
    assert payload["counts"] == {
        "story_count": 0,
        "section_count": 5,
        "evidence_count": 0,
    }
    assert payload["local_articles"] == {
        "article_count": 0,
        "paragraph_count": 0,
        "organized_section_count": 0,
        "source_count": 0,
        "extracted_article_count": 0,
        "summary_fallback_article_count": 0,
        "skipped_article_count": 0,
    }
    assert payload["local_article_count"] == 0
    assert payload["local_article_paragraph_count"] == 0
    assert payload["readiness"] == {
        "status": "empty",
        "en": "empty",
        "zh": "暂无故事",
    }
    assert payload["refresh_time"] == "04:00"
    assert payload["local_url"] == "http://127.0.0.1:8787"
    assert payload["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert payload["edition_path"] == "data/edition.json"
    assert payload["manifest_path"] == "data/manifest.json"
    assert payload["runtime_path"] == "data/runtime.json"
    assert payload["story_count"] == payload["runtime"]["counts"]["story_count"]
    assert payload["section_count"] == payload["runtime"]["counts"]["section_count"]
    assert payload["evidence_count"] == payload["runtime"]["counts"]["evidence_count"]
    assert payload["readiness_status"] == payload["runtime"]["readiness"]["status"]
    assert payload["generated_at"] == payload["runtime"]["generated_at"]
    assert payload["edition_date"] == payload["runtime"]["edition_date"]
    assert payload["site"] == payload["runtime"]["site"]
    assert payload["serve"] == payload["runtime"]["serve"]
    assert payload["refresh"] == payload["runtime"]["refresh"]


def test_row_one_status_json_includes_local_article_metrics(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["local_articles"] == {
        "article_count": 1,
        "paragraph_count": 2,
        "organized_section_count": 2,
        "source_count": 1,
        "extracted_article_count": 1,
        "summary_fallback_article_count": 0,
        "skipped_article_count": 0,
    }
    assert payload["local_article_count"] == 1
    assert payload["local_article_paragraph_count"] == 2
    assert story["id"] in (tmp_path / "data" / "articles" / f"{story['id']}.json").read_text(
        encoding="utf-8"
    )


def test_row_one_status_json_includes_local_article_route_health(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    assert (tmp_path / "articles" / "index.html").is_file()
    assert (tmp_path / "articles" / f"{story['id']}.html").is_file()
    assert 'href="articles/index.html"' in (tmp_path / "index.html").read_text(encoding="utf-8")
    assert f'href="{story["id"]}.html"' in (tmp_path / "articles" / "index.html").read_text(
        encoding="utf-8"
    )

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["local_article_routes"] == {
        "status": "ready",
        "article_count": 1,
        "library_path": "articles/index.html",
        "library_present": True,
        "homepage_library_link_present": True,
        "missing_article_pages": [],
        "missing_library_links": [],
    }


def test_row_one_status_prints_local_article_route_health(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    assert (tmp_path / "articles" / "index.html").is_file()
    assert (tmp_path / "articles" / f"{story['id']}.html").is_file()
    assert 'href="articles/index.html"' in (tmp_path / "index.html").read_text(encoding="utf-8")
    assert f'href="{story["id"]}.html"' in (tmp_path / "articles" / "index.html").read_text(
        encoding="utf-8"
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Local article routes: ready (1 saved local article)" in result.output


def test_row_one_article_readiness_prints_config_and_site_counts(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _render_status_site_with_local_article(output_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "article-readiness",
            "--config-dir",
            str(config_dir),
            "--site-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ROW ONE article readiness" in result.output
    assert f"Config: {config_dir}" in result.output
    assert f"Site: {output_dir}" in result.output
    assert "ROW ONE article-enabled sources: 0" in result.output
    assert "Saved local articles: 1" in result.output
    assert "Saved local paragraphs: 2" in result.output
    assert "Extracted local articles: 1" in result.output
    assert "Summary fallback local articles: 0" in result.output
    assert "Skipped local articles: 0" in result.output
    assert "Story source coverage: 0/1 eligible" in result.output
    assert "row_one_article.enabled: true" in result.output


def test_row_one_article_readiness_json_is_machine_readable(tmp_path: Path) -> None:
    config_dir = tmp_path / "configs"
    output_dir = tmp_path / "site"
    _write_minimal_config(config_dir)
    _render_status_site_with_local_article(output_dir)

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "article-readiness",
            "--config-dir",
            str(config_dir),
            "--site-dir",
            str(output_dir),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["config_dir"] == str(config_dir)
    assert payload["site_dir"] == str(output_dir)
    assert payload["local_articles"]["article_count"] == 1
    assert payload["local_articles"]["paragraph_count"] == 2
    assert payload["local_articles"]["extracted_article_count"] == 1
    assert payload["local_articles"]["summary_fallback_article_count"] == 0
    assert payload["local_articles"]["skipped_article_count"] == 0
    assert payload["story_coverage"]["story_count"] == 1
    assert payload["story_coverage"]["eligible_story_count"] == 0
    assert payload["recommendations"]


def test_row_one_status_json_keeps_fixed_runtime_urls_for_wildcard_host(
    tmp_path: Path,
) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )

    result = CliRunner().invoke(
        app,
        [
            "row-one",
            "status",
            "--site-dir",
            str(tmp_path),
            "--host",
            "0.0.0.0",
            "--port",
            "8787",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "Open locally: http://127.0.0.1:8787" in payload["access"]
    assert "Open from LAN: http://<LAN-IP>:8787" in payload["access"]
    assert payload["local_url"] == "http://127.0.0.1:8787"
    assert payload["lan_url_hint"] == "http://<LAN-IP>:8787"
    assert "http://0.0.0.0:8787" not in json.dumps(payload)


def test_row_one_status_json_reports_ready_counts_for_populated_site(
    tmp_path: Path,
) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/status-ready",
                "title": "The Row showroom appointment demand rises",
                "summary": "Local desk notes rising interest in quiet luxury appointments.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["story_count"] == 1
    assert payload["counts"]["story_count"] == 1
    assert payload["readiness_status"] == "ready"
    assert payload["readiness"]["status"] == "ready"
    assert payload["readiness"]["en"] == "ready"
    assert payload["counts"] == payload["runtime"]["counts"]
    assert payload["readiness"] == payload["runtime"]["readiness"]


def test_row_one_status_rejects_missing_runtime_payload(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )
    (tmp_path / "data" / "runtime.json").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "data/runtime.json" in result.output


def test_row_one_status_rejects_semantic_story_refs_drift_that_schema_cannot_express(
    tmp_path: Path,
) -> None:
    _render_status_fixture_site(tmp_path)
    edition_path = tmp_path / "data" / "edition.json"
    edition = json.loads(edition_path.read_text(encoding="utf-8"))
    edition["signal_synthesis"]["groups"][0]["signals"][0]["story_refs"][0]["headline"] = (
        "Schema-valid but wrong story headline"
    )

    _row_one_app_schema_validator().validate(edition)
    edition_path.write_text(json.dumps(edition), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "story_refs[0].headline" in result.output


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (
            lambda runtime, _manifest, _edition: runtime.update(
                {"contract_version": "row-one-runtime/v2"}
            ),
            "runtime contract_version",
        ),
        (
            lambda _runtime, _manifest, edition: edition.update(
                {"contract_version": "row-one-app/v3"}
            ),
            "edition contract_version",
        ),
        (
            lambda _runtime, _manifest, edition: edition.pop("edition_brief"),
            "edition.edition_brief",
        ),
        (
            lambda _runtime, _manifest, edition: edition.pop("signal_synthesis"),
            "edition.signal_synthesis",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"]["boundaries"].update(
                {"en": "Verified platform heat."}
            ),
            "edition.signal_synthesis.boundaries.en",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"].update(
                {"signal_count": 99}
            ),
            "edition.signal_synthesis.signal_count",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"]["groups"][0][
                "signals"
            ][0].pop("story_refs"),
            "story_refs",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"]["groups"][0][
                "signals"
            ][0]["story_refs"][0].update({"story_id": "unknown-story-9999999999"}),
            "story_refs ids",
        ),
        (
            lambda _runtime, _manifest, edition: edition["signal_synthesis"]["groups"][0][
                "signals"
            ][0]["story_refs"][0].update({"detail_href": "details/drift.html"}),
            "story_refs[0].detail_href",
        ),
        (
            lambda _runtime, _manifest, edition: edition["edition_brief"].update(
                {"story_directory_story_count": 99}
            ),
            "edition.edition_brief.story_directory_story_count",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["site"].update(
                {"runtime_path": "runtime.json"}
            ),
            "runtime.site.runtime_path",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["serve"].update({"default_port": 9999}),
            "runtime.serve.default_port",
        ),
        (
            lambda runtime, _manifest, _edition: runtime.update(
                {"generated_at": "2026-07-03T04:00:00Z"}
            ),
            "runtime generated_at",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["counts"].update({"story_count": 7}),
            "runtime counts",
        ),
        (
            lambda runtime, _manifest, _edition: runtime["readiness"].update({"en": "empty"}),
            "runtime.readiness.en",
        ),
    ],
)
def test_row_one_status_rejects_runtime_contract_drift(
    tmp_path: Path,
    mutation: object,
    expected_error: str,
) -> None:
    _render_status_fixture_site(tmp_path)
    manifest_path = tmp_path / "data" / "manifest.json"
    edition_path = tmp_path / "data" / "edition.json"
    runtime_path = tmp_path / "data" / "runtime.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    edition = json.loads(edition_path.read_text(encoding="utf-8"))
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    mutation(runtime, manifest, edition)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    edition_path.write_text(json.dumps(edition), encoding="utf-8")
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert expected_error in result.output


def test_row_one_status_rejects_story_directory_route_drift(tmp_path: Path) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/story-directory",
                "title": "The Row route index demand rises",
                "summary": "Local desk notes route index drift should be rejected.",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    edition_path = tmp_path / "data" / "edition.json"
    payload = json.loads(edition_path.read_text(encoding="utf-8"))
    payload["story_directory"]["routes"][0]["detail_href"] = "details/drifted-route.html"
    edition_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "edition.story_directory.routes[0].detail_href" in result.output


def test_row_one_status_rejects_missing_generated_asset(tmp_path: Path) -> None:
    _render_populated_status_site(tmp_path)
    (tmp_path / "assets" / "row-one.css").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "assets/row-one.css" in result.output


def test_row_one_status_rejects_missing_current_detail_page(tmp_path: Path) -> None:
    story = _render_populated_status_site(tmp_path)
    detail_href = str(story["detail_href"])
    assert not detail_href.startswith("/")
    (tmp_path / detail_href).unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert detail_href in result.output


def test_row_one_status_rejects_story_detail_route_not_matching_story_id(
    tmp_path: Path,
) -> None:
    story = _render_populated_status_site(tmp_path)
    original_href = str(story["detail_href"])
    stale_href = "details/stale-story.html"
    (tmp_path / stale_href).write_text("<!doctype html><title>Stale</title>", encoding="utf-8")
    edition_path = tmp_path / "data" / "edition.json"
    payload = json.loads(edition_path.read_text(encoding="utf-8"))

    def replace_href(value: object) -> object:
        if value == original_href:
            return stale_href
        if isinstance(value, dict):
            return {key: replace_href(nested) for key, nested in value.items()}
        if isinstance(value, list):
            return [replace_href(nested) for nested in value]
        return value

    edition_path.write_text(json.dumps(replace_href(payload)), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert f"details/{story['id']}.html" in result.output


def test_row_one_status_checks_only_local_story_image_assets(tmp_path: Path) -> None:
    _render_populated_status_site(tmp_path)
    edition_path = tmp_path / "data" / "edition.json"
    payload = json.loads(edition_path.read_text(encoding="utf-8"))
    payload["stories"][0]["display"]["image"] = {
        "src": "assets/story-card.jpg",
        "alt": {"en": "Story card", "zh": "故事卡片"},
    }
    local_asset = tmp_path / "assets" / "story-card.jpg"
    local_asset.write_bytes(b"image")
    edition_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output

    local_asset.unlink()
    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "assets/story-card.jpg" in result.output

    payload["stories"][0]["display"]["image"]["src"] = "https://example.com/remote.jpg"
    edition_path.write_text(json.dumps(payload), encoding="utf-8")
    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output


def test_row_one_status_rejects_stale_article_sidecar(tmp_path: Path) -> None:
    _render_populated_status_site(tmp_path)
    articles_dir = tmp_path / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "old-story.json").write_text(
        json.dumps(
            {
                "story_id": "old-story",
                "url": "https://example.com/old",
                "source_name": "Archive",
                "extracted_at": AS_OF,
                "paragraphs": ["Stale paragraph."],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "old-story" in result.output


def test_row_one_status_rejects_article_sidecar_story_id_mismatch(tmp_path: Path) -> None:
    story = _render_populated_status_site(tmp_path)
    article_path = tmp_path / "data" / "articles" / f"{story['id']}.json"
    article_path.parent.mkdir(parents=True, exist_ok=True)
    article_path.write_text(
        json.dumps(
            {
                "story_id": "mismatched-story",
                "url": "https://example.com/current",
                "source_name": "Local Desk",
                "extracted_at": AS_OF,
                "paragraphs": ["Current paragraph."],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "story_id" in result.output


def test_row_one_status_rejects_missing_saved_article_library_route(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    (tmp_path / "articles" / "index.html").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "articles/index.html" in result.output


def test_row_one_status_rejects_missing_saved_article_page_route(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    (tmp_path / "articles" / f"{story['id']}.html").unlink()

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert f"articles/{story['id']}.html" in result.output


def test_row_one_status_rejects_missing_homepage_saved_article_library_link(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    index_path = tmp_path / "index.html"
    index_path.write_text(
        index_path.read_text(encoding="utf-8").replace(
            'href="articles/index.html"',
            'href="details/index.html"',
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "library link is missing from index.html" in result.output


def test_row_one_status_rejects_missing_saved_article_library_page_link(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    library_path = tmp_path / "articles" / "index.html"
    library_path.write_text(
        library_path.read_text(encoding="utf-8").replace(
            f'href="{story["id"]}.html"',
            'href="missing.html"',
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert f"{story['id']}.html" in result.output


def test_row_one_status_rejects_unsafe_local_intelligence_detail_path(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["detail_path"] = "../escape.html#local-article"
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "local-intelligence" in result.output
    assert "detail_path" in result.output


def test_row_one_status_rejects_unknown_local_intelligence_detail_route(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["detail_path"] = "details/unknown-story.html#local-article"
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "unknown-story" in result.output


def test_row_one_status_rejects_local_intelligence_out_of_range_paragraph_index(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["paragraph_indices"] = [99]
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "paragraph_indices" in result.output


def test_row_one_status_rejects_article_sidecar_out_of_range_content_paragraph_index(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    article_path = tmp_path / "data" / "articles" / f"{story['id']}.json"
    payload = json.loads(article_path.read_text(encoding="utf-8"))
    payload["content_sections"][0]["items"][0]["paragraph_indices"] = [99]
    article_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "paragraph_indices" in result.output


def test_row_one_status_rejects_local_intelligence_segment_out_of_range_paragraph_index(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["segments"][0]["items"][0]["paragraph_indices"] = [99]
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "paragraph_indices" in result.output


def test_row_one_status_rejects_local_intelligence_source_names_without_article_source(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    payload[0]["items"][0]["source_name"] = "Local Desk"
    payload[0]["items"][0]["source_names"] = ["Other Desk"]
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "source_names" in result.output


def test_row_one_status_rejects_local_intelligence_missing_rendered_anchor(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    detail_path = tmp_path / str(story["detail_href"])
    detail_html = detail_path.read_text(encoding="utf-8")
    detail_html = detail_html.replace(
        'id="local-article-paragraph-1"', 'data-id="local-article-paragraph-1"'
    )
    detail_path.write_text(detail_html, encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "local-article-paragraph-1" in result.output


def test_row_one_status_rejects_noncanonical_local_intelligence_paragraph_fragment(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    detail_path = str(payload[0]["items"][0]["detail_path"]).split("#", 1)[0]
    payload[0]["items"][0]["detail_path"] = f"{detail_path}#local-article-paragraph-01"
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "local-article-paragraph-01" in result.output


def test_row_one_schedule_prints_refresh_command() -> None:
    result = CliRunner().invoke(app, ["row-one", "schedule", "--time", "04:00"])

    assert result.exit_code == 0
    assert "04:00" in result.output
    assert "fashion-radar row-one refresh" in result.output
    assert "fashion-radar run" not in result.output
    assert "fashion-radar row-one build" not in result.output
    assert "--latest-only" not in result.output


def test_row_one_server_serves_index_on_ephemeral_port(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><body>ROW ONE</body></html>", encoding="utf-8")
    (site_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    server = create_row_one_http_server(site_dir=site_dir, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)

    try:
        thread.start()
        port = int(server.server_address[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 200
    assert "ROW ONE" in body


def test_row_one_server_rejects_unmarked_directory(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><body>ROW ONE</body></html>", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="site marker"):
        create_row_one_http_server(site_dir=site_dir, host="127.0.0.1", port=0)


def test_row_one_server_serves_generated_chinese_detail_link(tmp_path: Path) -> None:
    edition = build_row_one_edition(
        report=_empty_report(),
        recent_items=[
            {
                "source_name": "Local Desk",
                "url": "https://example.com/cn",
                "title": "上海新锐设计师品牌升温",
                "summary": "国内设计师品牌热度上升。",
                "collected_at": AS_OF,
            }
        ],
        as_of=AS_OF,
    )
    render_row_one_site(edition, tmp_path)
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    detail_href_match = re.search(r'href="(?P<href>details/[^"]+\.html)"', index_html)
    assert detail_href_match is not None
    detail_href = detail_href_match.group("href")

    server = create_row_one_http_server(site_dir=tmp_path, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)

    try:
        thread.start()
        port = int(server.server_address[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("GET", f"/{detail_href}")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert response.status == 200
    assert "上海新锐设计师品牌升温" in body


def test_row_one_serve_cli_process_serves_generated_site(tmp_path: Path) -> None:
    render_row_one_site(
        build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF),
        tmp_path,
    )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "fashion_radar",
            "row-one",
            "serve",
            "--site-dir",
            str(tmp_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        fetched: dict[str, str] = {}
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and len(fetched) < 6:
            try:
                fetched = {
                    path: _fetch_row_one_cli_process_path(port, path)
                    for path in (
                        "/",
                        "/data/manifest.json",
                        "/data/edition.json",
                        "/data/runtime.json",
                        "/assets/row-one.css",
                        "/assets/row-one.js",
                    )
                }
            except OSError:
                time.sleep(0.1)

        assert len(fetched) == 6
        assert "ROW ONE" in fetched["/"]
        assert '"contract_version": "row-one-manifest/v1"' in fetched["/data/manifest.json"]
        assert '"contract_version": "row-one-app/v7"' in fetched["/data/edition.json"]
        assert '"contract_version": "row-one-runtime/v1"' in fetched["/data/runtime.json"]
        assert "RowOneSerif" in fetched["/assets/row-one.css"]
        assert "row-one:language" in fetched["/assets/row-one.js"]
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _fetch_row_one_cli_process_path(port: int, path: str) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    if response.status != 200:
        raise OSError(f"{path} returned HTTP {response.status}")
    return body


def test_format_row_one_site_url() -> None:
    assert format_row_one_site_url("127.0.0.1", 8787) == "http://127.0.0.1:8787"
    assert format_row_one_site_url("localhost", 8787) == "http://localhost:8787"
    assert format_row_one_site_url("192.168.1.20", 8787) == "http://192.168.1.20:8787"
    assert format_row_one_site_url("0.0.0.0", 8787) == "http://127.0.0.1:8787"
    assert format_row_one_site_url("::1", 8787) == "http://[::1]:8787"
    assert format_row_one_site_url("::", 8787) == "http://[::1]:8787"
    assert format_row_one_site_url("2001:db8::1", 8787) == "http://[2001:db8::1]:8787"


def test_format_row_one_site_access_message_for_wildcard_host() -> None:
    message = format_row_one_site_access_message("0.0.0.0", 8787)

    assert "Open locally: http://127.0.0.1:8787" in message
    assert "Open from LAN: http://<LAN-IP>:8787" in message
    assert "Bound to 0.0.0.0:8787" in message
    assert "no authentication" in message
