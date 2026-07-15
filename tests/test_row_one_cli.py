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
import fashion_radar.row_one.publish as row_one_publish
import fashion_radar.row_one.render as row_one_render
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
from fashion_radar.row_one.publish import (
    RowOnePublishAmbiguousStateError,
    RowOnePublishCleanupPendingError,
    RowOnePublishRollbackError,
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
_REQUIRES_SAFE_DIRECTORY_OPERATIONS = pytest.mark.skipif(
    not row_one_publish._SAFE_DIRECTORY_OPERATIONS_SUPPORTED,
    reason="safe directory-relative operations are unavailable",
)


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


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
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


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
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


@pytest.mark.parametrize("command_name", ["build", "preview"])
def test_row_one_latest_only_help_describes_recoverable_publish(command_name: str) -> None:
    result = CliRunner().invoke(app, ["row-one", command_name, "--help"])

    assert result.exit_code == 0
    normalized = " ".join(result.output.split()).lower()
    latest_only_help = normalized.split("--latest-only", 1)[1]
    end_marker = "--host" if command_name == "preview" else "--help"
    latest_only_help = latest_only_help.split(end_marker, 1)[0]
    for word in (
        "staged",
        "validated",
        "recoverable",
        "replacement",
        "preserving",
        "unrelated",
        "top-level",
        "children",
    ):
        assert word in latest_only_help
    assert "remove known row one generated children before writing" not in normalized


def test_row_one_refresh_help_describes_recoverable_site_publication() -> None:
    result = CliRunner().invoke(app, ["row-one", "refresh", "--help"])

    assert result.exit_code == 0
    normalized = " ".join(result.output.split()).lower()
    assert (
        "collect, match, report, and publish row one using recoverable staged replacement."
        in normalized
    )


_SAFE_DIRECTORY_CAPABILITY_ERROR = "ROW ONE safe directory handles are unsupported on this platform"


def _row_one_publish_artifact_paths(output_dir: Path) -> list[Path]:
    physical_output = output_dir.resolve(strict=False)
    parent = physical_output.parent
    output_name = physical_output.name
    owner_path = physical_output / "data" / ".row-one-publish-owner.json"
    artifacts = []
    if parent.is_dir():
        artifacts.extend(
            path
            for path in parent.iterdir()
            if path.name == f".{output_name}.row-one-publish.lock"
            or path.name == f".{output_name}.row-one-publish.json"
            or path.name.startswith(f".{output_name}.row-one-stage-")
            or path.name.startswith(f".{output_name}.row-one-backup-")
            or (
                path.name.startswith(f".{output_name}.row-one-publish.")
                and path.name.endswith(".tmp")
            )
        )
    if owner_path.exists() or owner_path.is_symlink():
        artifacts.append(owner_path)
    return sorted(artifacts)


@pytest.mark.parametrize(
    ("command_name", "extra_args", "failure_prefix"),
    [
        ("build", ["--latest-only"], "ROW ONE build failed:"),
        ("preview", ["--latest-only"], "ROW ONE preview failed:"),
        ("refresh", [], "ROW ONE refresh failed:"),
    ],
)
def test_row_one_latest_only_commands_report_capability_failure_before_publish_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command_name: str,
    extra_args: list[str],
    failure_prefix: str,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "absent-output-parent" / "row-one-site"
    output_parent = output_dir.parent
    physical_target = output_dir.resolve(strict=False)
    publish_token = "3914cafe3914cafe3914cafe3914cafe"
    _write_minimal_config(config_dir)
    edition = build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF)
    assert not output_parent.exists()
    refresh_calls: list[str] = []

    if command_name == "refresh":
        _patch_successful_row_one_refresh_pipeline(
            monkeypatch,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            calls=refresh_calls,
            patch_site_writer=False,
            guard_sqlite_retention=True,
        )

    site_writer_calls: list[tuple[Path, bool]] = []

    def write_site_through_real_renderer(
        *,
        config_dir: Path,
        data_dir: Path,
        reports_dir: Path,
        output_dir: Path,
        as_of: str,
        latest_only: bool,
    ):
        del config_dir, data_dir, reports_dir, as_of
        site_writer_calls.append((output_dir, latest_only))
        if command_name == "refresh":
            refresh_calls.append("_write_row_one_site_from_cli_options")
        return render_row_one_site(edition, output_dir, latest_only=latest_only)

    token_requests: list[int] = []

    def deterministic_token_hex(byte_count: int) -> str:
        token_requests.append(byte_count)
        if byte_count == 16:
            return publish_token
        return "0" * (byte_count * 2)

    asset_targets: list[Path] = []
    original_write_assets = row_one_render._write_assets

    def record_asset_write(render_output: Path) -> None:
        asset_targets.append(render_output)
        original_write_assets(render_output)

    monkeypatch.setattr(
        row_one_publish,
        "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED",
        False,
    )
    monkeypatch.setattr(row_one_publish.secrets, "token_hex", deterministic_token_hex)
    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_site_through_real_renderer,
    )
    monkeypatch.setattr(row_one_render, "_write_assets", record_asset_write)

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

    if command_name == "refresh":
        _assert_refresh_stopped_after_site_publication(
            calls=refresh_calls,
            reports_dir=reports_dir,
        )
    assert result.exit_code == 1
    assert result.output == f"{failure_prefix} {_SAFE_DIRECTORY_CAPABILITY_ERROR}\n"
    assert site_writer_calls == [(output_dir, True)]
    assert token_requests == []
    assert asset_targets == []
    assert not output_parent.exists()
    assert _row_one_publish_artifact_paths(output_dir) == []
    sensitive_paths = (
        str(physical_target),
        publish_token,
        f".{physical_target.name}.row-one-stage-{publish_token}",
    )
    for sensitive_path in sensitive_paths:
        assert sensitive_path not in result.output


@pytest.mark.parametrize(
    ("command_name", "extra_args", "failure_prefix"),
    [
        ("build", ["--latest-only"], "ROW ONE build failed:"),
        ("preview", ["--latest-only"], "ROW ONE preview failed:"),
        ("refresh", [], "ROW ONE refresh failed:"),
    ],
)
def test_row_one_latest_only_commands_prioritize_capability_for_invalid_symlink_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command_name: str,
    extra_args: list[str],
    failure_prefix: str,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    physical_target = tmp_path / "private-physical-target" / "row-one-site"
    output_dir = tmp_path / "logical-row-one-site"
    physical_target.mkdir(parents=True)
    (physical_target / "index.html").write_text("manual live content\n", encoding="utf-8")
    try:
        output_dir.symlink_to(physical_target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    _write_minimal_config(config_dir)
    edition = build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF)

    def live_tree_snapshot() -> dict[str, tuple[int, int, int, bytes | None]]:
        snapshot = {}
        for path in sorted((physical_target, *physical_target.rglob("*"))):
            metadata = path.lstat()
            relative_path = (
                "." if path == physical_target else path.relative_to(physical_target).as_posix()
            )
            snapshot[relative_path] = (
                metadata.st_mode,
                metadata.st_size,
                metadata.st_mtime_ns,
                path.read_bytes() if path.is_file() else None,
            )
        return snapshot

    live_before = live_tree_snapshot()
    refresh_calls: list[str] = []
    if command_name == "refresh":
        _patch_successful_row_one_refresh_pipeline(
            monkeypatch,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            calls=refresh_calls,
            patch_site_writer=False,
            guard_sqlite_retention=True,
        )

    site_writer_calls: list[tuple[Path, bool]] = []

    def write_site_through_real_renderer(
        *,
        config_dir: Path,
        data_dir: Path,
        reports_dir: Path,
        output_dir: Path,
        as_of: str,
        latest_only: bool,
    ):
        del config_dir, data_dir, reports_dir, as_of
        site_writer_calls.append((output_dir, latest_only))
        if command_name == "refresh":
            refresh_calls.append("_write_row_one_site_from_cli_options")
        return render_row_one_site(edition, output_dir, latest_only=latest_only)

    token_requests: list[int] = []

    def deterministic_token_hex(byte_count: int) -> str:
        token_requests.append(byte_count)
        return "0" * (byte_count * 2)

    asset_targets: list[Path] = []

    def fail_if_assets_are_written(render_output: Path) -> None:
        asset_targets.append(render_output)
        raise AssertionError("capability failure must precede rendering")

    monkeypatch.setattr(
        row_one_publish,
        "_SAFE_DIRECTORY_OPERATIONS_SUPPORTED",
        False,
    )
    monkeypatch.setattr(row_one_publish.secrets, "token_hex", deterministic_token_hex)
    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_site_through_real_renderer,
    )
    monkeypatch.setattr(row_one_render, "_write_assets", fail_if_assets_are_written)

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

    if command_name == "refresh":
        _assert_refresh_stopped_after_site_publication(
            calls=refresh_calls,
            reports_dir=reports_dir,
        )
    assert result.exit_code == 1
    assert result.output == f"{failure_prefix} {_SAFE_DIRECTORY_CAPABILITY_ERROR}\n"
    assert str(physical_target) not in result.output
    assert site_writer_calls == [(output_dir, True)]
    assert token_requests == []
    assert asset_targets == []
    assert output_dir.is_symlink()
    assert output_dir.readlink() == physical_target
    assert live_tree_snapshot() == live_before
    assert _row_one_publish_artifact_paths(output_dir) == []


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
@pytest.mark.parametrize(
    ("command_name", "extra_args", "failure_prefix"),
    [
        ("build", ["--latest-only"], "ROW ONE build failed:"),
        ("preview", ["--latest-only"], "ROW ONE preview failed:"),
        ("refresh", [], "ROW ONE refresh failed:"),
    ],
)
def test_row_one_publish_failures_hide_internal_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command_name: str,
    extra_args: list[str],
    failure_prefix: str,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    edition = build_row_one_edition(report=_empty_report(), recent_items=[], as_of=AS_OF)
    render_row_one_site(edition, output_dir)
    physical_target = output_dir.resolve(strict=True)
    publish_token = "3914cafe3914cafe3914cafe3914cafe"
    unique_underlying_message = "stage-391-task-4 private renderer failure"
    token_requests: list[int] = []
    journal_nonce = 0
    refresh_calls: list[str] = []

    def deterministic_token_hex(byte_count: int) -> str:
        nonlocal journal_nonce
        token_requests.append(byte_count)
        if byte_count == 16:
            return publish_token
        if byte_count == 8:
            nonce = f"{journal_nonce:016x}"
            journal_nonce += 1
            return nonce
        raise AssertionError(f"unexpected publisher token size: {byte_count}")

    monkeypatch.setattr(row_one_publish.secrets, "token_hex", deterministic_token_hex)

    if command_name == "refresh":
        _patch_successful_row_one_refresh_pipeline(
            monkeypatch,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            calls=refresh_calls,
            patch_site_writer=False,
            guard_sqlite_retention=True,
        )

    site_writer_calls: list[tuple[Path, bool]] = []

    def write_site_through_real_renderer(
        *,
        config_dir: Path,
        data_dir: Path,
        reports_dir: Path,
        output_dir: Path,
        as_of: str,
        latest_only: bool,
    ):
        del config_dir, data_dir, reports_dir, as_of
        site_writer_calls.append((output_dir, latest_only))
        if command_name == "refresh":
            refresh_calls.append("_write_row_one_site_from_cli_options")
        return render_row_one_site(edition, output_dir, latest_only=latest_only)

    staged_asset_targets: list[Path] = []
    underlying_messages: list[str] = []

    def fail_staged_assets(render_output: Path) -> None:
        staged_asset_targets.append(render_output)
        underlying_message = "; ".join(
            (
                f"physical_target={physical_target}",
                f"token={publish_token}",
                f"stage_basename={render_output.name}",
                f"stage_path={render_output}",
                unique_underlying_message,
            )
        )
        underlying_messages.append(underlying_message)
        raise OSError(underlying_message)

    monkeypatch.setattr(
        cli_module,
        "_write_row_one_site_from_cli_options",
        write_site_through_real_renderer,
    )
    monkeypatch.setattr(row_one_render, "_write_assets", fail_staged_assets)

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

    if command_name == "refresh":
        _assert_refresh_stopped_after_site_publication(
            calls=refresh_calls,
            reports_dir=reports_dir,
        )
    assert result.exit_code == 1
    assert site_writer_calls == [(output_dir, True)]
    assert len(staged_asset_targets) == 1
    assert len(underlying_messages) == 1
    received_stage_path = staged_asset_targets[0]
    received_stage_basename = received_stage_path.name
    internal_components = (
        str(physical_target),
        publish_token,
        received_stage_basename,
        str(received_stage_path),
        unique_underlying_message,
    )
    for component in internal_components:
        assert component in underlying_messages[0]
    assert result.output == (
        f"{failure_prefix} ROW ONE staged publish failed before commit; "
        "the live site was preserved\n"
    )
    for component in internal_components:
        assert component not in result.output
    expected_stage_path = (
        physical_target.parent / f".{physical_target.name}.row-one-stage-{publish_token}"
    )
    assert received_stage_path == expected_stage_path
    assert token_requests[0] == 16


def _patch_successful_row_one_refresh_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    *,
    config_dir: Path,
    data_dir: Path,
    reports_dir: Path,
    output_dir: Path,
    calls: list[str],
    patch_site_writer: bool = True,
    guard_sqlite_retention: bool = False,
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
        markdown_path = reports_dir / "daily.md"
        json_path = reports_dir / "daily.json"
        reports_dir.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text("# Daily report\n", encoding="utf-8")
        json_path.write_text("{}\n", encoding="utf-8")
        markdown_path.with_suffix(".html").write_text(
            "<html><body>Daily report</body></html>\n",
            encoding="utf-8",
        )
        return markdown_path, json_path

    def prune_stale_daily_report_files(**kwargs: object) -> SimpleNamespace:
        assert kwargs["reports_dir"] == reports_dir
        assert kwargs["as_of"] == AS_OF
        calls.append("prune_stale_daily_report_files")
        return SimpleNamespace(
            current_date="2026-07-02",
            removed_count=3,
            kept_current_count=3,
        )

    def clean_old_data(**_kwargs: object) -> None:
        calls.append("clean_old_data")
        raise AssertionError("SQLite retention must not run before publication succeeds")

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
        index_path = output_dir / "index.html"
        site_data_dir = output_dir / "data"
        site_data_dir.mkdir(parents=True, exist_ok=True)
        index_path.write_text("<html><body>ROW ONE</body></html>\n", encoding="utf-8")
        (site_data_dir / "edition.json").write_text("{}\n", encoding="utf-8")
        (site_data_dir / "manifest.json").write_text("{}\n", encoding="utf-8")
        return SimpleNamespace(
            index_path=index_path,
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
    if guard_sqlite_retention:
        monkeypatch.setattr(cli_module, "clean_old_data", clean_old_data)
    if patch_site_writer:
        monkeypatch.setattr(
            cli_module,
            "_write_row_one_site_from_cli_options",
            write_row_one_site_from_cli_options,
        )


def _assert_refresh_stopped_after_site_publication(
    *,
    calls: list[str],
    reports_dir: Path,
) -> None:
    assert calls == [
        "collect_configured_sources",
        "match_stored_items",
        "write_daily_report_files",
        "_write_row_one_site_from_cli_options",
    ]
    assert (reports_dir / "daily.md").read_text(encoding="utf-8") == "# Daily report\n"
    assert (reports_dir / "daily.json").read_text(encoding="utf-8") == "{}\n"
    assert (reports_dir / "daily.html").read_text(encoding="utf-8") == (
        "<html><body>Daily report</body></html>\n"
    )


@pytest.mark.parametrize(
    ("error_type", "error_label"),
    [
        (RowOnePublishRollbackError, "rollback failed"),
        (RowOnePublishAmbiguousStateError, "ambiguous state"),
        (RowOnePublishCleanupPendingError, "cleanup pending"),
    ],
)
@pytest.mark.parametrize(
    ("command_name", "extra_args", "failure_prefix"),
    [
        ("build", ["--latest-only"], "ROW ONE build failed:"),
        ("preview", ["--latest-only"], "ROW ONE preview failed:"),
        ("refresh", [], "ROW ONE refresh failed:"),
    ],
)
def test_row_one_recovery_errors_keep_operator_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
    error_label: str,
    command_name: str,
    extra_args: list[str],
    failure_prefix: str,
) -> None:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    output_dir = tmp_path / "row-one-site"
    _write_minimal_config(config_dir)
    recovery_paths = {
        "live": tmp_path / "physical-site",
        "stage": tmp_path / ".physical-site.row-one-stage-token",
        "backup": tmp_path / ".physical-site.row-one-backup-token",
        "journal": tmp_path / ".physical-site.row-one-publish.json",
    }
    refresh_calls: list[str] = []

    if command_name == "refresh":
        _patch_successful_row_one_refresh_pipeline(
            monkeypatch,
            config_dir=config_dir,
            data_dir=data_dir,
            reports_dir=reports_dir,
            output_dir=output_dir,
            calls=refresh_calls,
            patch_site_writer=False,
            guard_sqlite_retention=True,
        )

    def fail_publish(**_kwargs: object) -> None:
        if command_name == "refresh":
            refresh_calls.append("_write_row_one_site_from_cli_options")
        details = "; ".join(f"{key}={path}" for key, path in recovery_paths.items())
        raise error_type(f"ROW ONE {error_label}; {details}")

    monkeypatch.setattr(cli_module, "_write_row_one_site_from_cli_options", fail_publish)

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

    if command_name == "refresh":
        _assert_refresh_stopped_after_site_publication(
            calls=refresh_calls,
            reports_dir=reports_dir,
        )
    assert result.exit_code == 1
    assert failure_prefix in result.output
    assert error_label in result.output
    for key, path in recovery_paths.items():
        assert f"{key}={path}" in result.output


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


def test_row_one_refresh_fails_after_sqlite_retention_failure(
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

    assert result.exit_code == 1, result.output
    retention_diagnostic = "SQLite retention: failed: database locked"
    assert retention_diagnostic in result.output
    assert "ROW ONE refresh failed" not in result.output
    assert calls[-1] == "clean_old_data"
    for report_line in (
        "Markdown report:",
        "JSON report:",
        "HTML report:",
        "Latest-only reports:",
    ):
        assert result.output.index(report_line) < result.output.index(retention_diagnostic)
    for site_line in (
        "Site:",
        "JSON: ",
        "Manifest:",
        "Open: http://127.0.0.1:8787",
    ):
        assert result.output.index(retention_diagnostic) < result.output.index(site_line)
    for artifact_path in (
        reports_dir / "daily.md",
        reports_dir / "daily.json",
        reports_dir / "daily.html",
        output_dir / "index.html",
        output_dir / "data" / "edition.json",
        output_dir / "data" / "manifest.json",
    ):
        assert artifact_path.exists()


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
    normalized = " ".join(result.output.split())
    assert "Collect, match, report, and publish ROW ONE" in normalized
    assert "recoverable staged replacement" in normalized
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
            "status": "site_ready_scheduler_unverified",
            "site_dir": str(site_dir),
            "as_of": "2026-07-07T08:00:00Z",
            "freshness": {"status": "fresh"},
            "server": {"status": "serving_row_one"},
            "systemd": {
                "status": "unit_files_present",
                "verification": "filenames_only",
            },
            "local_article_routes": {"status": "ready"},
            "local_article_content": {"status": "ready"},
            "access": {
                "message": "Open locally: http://127.0.0.1:8787",
                "local_url": "http://127.0.0.1:8787",
                "lan_url_hint": "http://<LAN-IP>:8787",
            },
            "actions": [],
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
    assert '\n  "status": "site_ready_scheduler_unverified"' in result.output
    payload = json.loads(result.output)
    assert payload["status"] == "site_ready_scheduler_unverified"
    assert payload["systemd"]["status"] == "unit_files_present"
    assert payload["systemd"]["verification"] == "filenames_only"
    assert payload["actions"] == []


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
            "status": "site_ready_scheduler_unverified",
            "site_dir": str(site_dir),
            "as_of": "2026-07-07T08:00:00Z",
            "freshness": {"status": "fresh"},
            "server": {"status": "serving_row_one"},
            "systemd": {
                "status": "unit_files_present",
                "verification": "filenames_only",
            },
            "local_article_routes": {"status": "ready", "article_count": 1},
            "local_article_content": {"status": "ready", "article_count": 1},
            "access": {
                "message": (
                    "Open locally: http://127.0.0.1:8787\nOpen from LAN: http://<LAN-IP>:8787"
                ),
                "local_url": "http://127.0.0.1:8787",
                "lan_url_hint": "http://<LAN-IP>:8787",
            },
            "actions": [],
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
    assert "Status: site_ready_scheduler_unverified" in result.output
    assert "Freshness: fresh" in result.output
    assert "Server: serving_row_one" in result.output
    assert "Systemd units: unit_files_present" in result.output
    assert "Systemd verification: filenames_only" in result.output
    assert "scheduler state is not verified" in result.output
    assert "Local article routes: ready" in result.output
    assert "Local article content: ready" in result.output
    assert "Access:" in result.output
    assert "Open locally: http://127.0.0.1:8787" in result.output
    assert "Actions:" not in result.output
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


@_REQUIRES_SAFE_DIRECTORY_OPERATIONS
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


def test_row_one_status_json_includes_local_article_content_health(tmp_path: Path) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    assert (tmp_path / "articles" / f"{story['id']}.html").is_file()

    result = CliRunner().invoke(
        app,
        ["row-one", "status", "--site-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["local_article_content"] == {
        "status": "ready",
        "article_count": 1,
        "paragraph_anchor_count": 2,
        "content_section_anchor_count": 2,
        "missing_article_sections": [],
        "missing_body_containers": [],
        "missing_paragraph_anchors": [],
        "missing_content_section_anchors": [],
    }


def test_row_one_status_prints_local_article_content_health(tmp_path: Path) -> None:
    _render_status_site_with_local_article(tmp_path)

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "Local article content: ready (1 saved local article, 2 paragraph anchors)" in (
        result.output
    )


def test_row_one_status_rejects_missing_local_article_section_anchor(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    article_path = tmp_path / "articles" / f"{story['id']}.html"
    article_html = article_path.read_text(encoding="utf-8")
    article_path.write_text(
        article_html.replace('id="local-article"', 'data-id="local-article"', 1),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "local article section is missing" in result.output
    assert "#local-article" in result.output


def test_row_one_status_rejects_missing_local_article_body_container_anchor(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    article_path = tmp_path / "articles" / f"{story['id']}.html"
    article_html = article_path.read_text(encoding="utf-8")
    article_path.write_text(
        article_html.replace('id="local-article-body"', 'data-id="local-article-body"', 1),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "body container is missing" in result.output
    assert "#local-article-body" in result.output


def test_row_one_status_rejects_missing_local_article_paragraph_anchor(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    article_path = tmp_path / "articles" / f"{story['id']}.html"
    article_html = article_path.read_text(encoding="utf-8")
    article_path.write_text(
        article_html.replace(
            'id="local-article-paragraph-2"',
            'data-id="local-article-paragraph-2"',
            1,
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "paragraph anchor is missing" in result.output
    assert "#local-article-paragraph-2" in result.output


def test_row_one_status_rejects_missing_local_article_content_section_anchor(
    tmp_path: Path,
) -> None:
    story = _render_status_site_with_local_article(tmp_path)
    article_path = tmp_path / "articles" / f"{story['id']}.html"
    article_html = article_path.read_text(encoding="utf-8")
    article_path.write_text(
        article_html.replace(
            'id="local-article-content-section-2"',
            'data-id="local-article-content-section-2"',
            1,
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "content-section anchor is missing" in result.output
    assert "#local-article-content-section-2" in result.output


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


def test_row_one_schedule_systemd_preview_matches_install_local_payloads(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports" / "row-one" / "site"
    common_options = [
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
        "9876",
    ]
    schedule_result = CliRunner().invoke(
        app,
        ["row-one", "schedule", "--mode", "systemd", *common_options],
    )
    install_result = CliRunner().invoke(
        app,
        ["row-one", "install-local", "--dry-run", *common_options],
    )

    assert schedule_result.exit_code == 0, schedule_result.output
    assert install_result.exit_code == 0, install_result.output
    headings = (
        "# ~/.config/systemd/user/row-one-refresh.service",
        "# ~/.config/systemd/user/row-one-refresh.timer",
        "# ~/.config/systemd/user/row-one-serve.service",
    )
    assert [schedule_result.output.index(heading) for heading in headings] == sorted(
        schedule_result.output.index(heading) for heading in headings
    )
    assert "# ~/.config/systemd/user/row-one.service" not in schedule_result.output
    assert "# ~/.config/systemd/user/row-one.timer" not in schedule_result.output
    assert "Before enabling on a fresh install, generate the site once:" in install_result.output

    def payload_sections(output: str) -> tuple[str, ...]:
        sections: list[str] = []
        for index, heading in enumerate(headings):
            start = output.index(heading) + len(heading)
            if index + 1 < len(headings):
                end = output.index(headings[index + 1], start)
            else:
                end = output.find("\n\nBefore enabling on a fresh install", start)
                if end == -1:
                    end = len(output)
            sections.append(output[start:end].strip())
        return tuple(sections)

    assert payload_sections(schedule_result.output) == payload_sections(install_result.output)
    serve_payload = payload_sections(schedule_result.output)[2]
    assert 'Environment="ROW_ONE_HOST=0.0.0.0"' in serve_payload
    assert 'Environment="ROW_ONE_PORT=9876"' in serve_payload
    assert '--host "$ROW_ONE_HOST"' in serve_payload
    assert '--port "$ROW_ONE_PORT"' in serve_payload


def test_row_one_schedule_help_includes_host_and_port() -> None:
    result = CliRunner().invoke(app, ["row-one", "schedule", "--help"])

    assert result.exit_code == 0, result.output
    assert "--host" in result.output
    assert "--port" in result.output


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
