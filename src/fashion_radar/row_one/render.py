from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree

from fashion_radar.row_one.models import RowOneEdition, RowOneLink, RowOneSection, RowOneStory
from fashion_radar.row_one.templates import (
    _validated_detail_relative_path,
    render_detail_html,
    render_index_html,
    row_one_css,
    row_one_js,
)
from fashion_radar.row_one.utils import isoformat_z, safe_external_url, utc_datetime

GENERATED_CHILDREN = ("index.html", ".row-one-site", "details", "assets", "data")
ROW_ONE_APP_CONTRACT_VERSION = "row-one-app/v1"
ROW_ONE_MANIFEST_CONTRACT_VERSION = "row-one-manifest/v1"
ROW_ONE_MANIFEST_SCHEMA_PATH = "schemas/row-one-manifest.schema.json"


@dataclass(frozen=True)
class RowOneRenderResult:
    output_dir: Path
    index_path: Path
    story_count: int
    edition: RowOneEdition


def render_row_one_site(
    edition: RowOneEdition,
    output_dir: Path,
    *,
    latest_only: bool = False,
) -> RowOneRenderResult:
    if latest_only:
        clean_row_one_site_children(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".row-one-site").write_text("ROW ONE generated site\n", encoding="utf-8")
    _write_assets(output_dir)
    index_path = output_dir / "index.html"
    index_path.write_text(render_index_html(edition), encoding="utf-8")
    _write_detail_pages(edition, output_dir / "details")
    app_payload = build_row_one_app_payload(edition)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "edition.json").write_text(
        json.dumps(app_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_payload = build_row_one_manifest_payload(edition, app_payload)
    (data_dir / "manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return RowOneRenderResult(
        output_dir=output_dir,
        index_path=index_path,
        story_count=len(edition.stories),
        edition=edition,
    )


def clean_row_one_site_children(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    marker = output_dir / ".row-one-site"
    generated_children = [output_dir / child_name for child_name in GENERATED_CHILDREN]
    has_generated_children = any(child.exists() for child in generated_children if child != marker)
    if has_generated_children and not marker.exists():
        raise ValueError(f"ROW ONE output directory is not marked as generated: {output_dir}")
    for child_name in GENERATED_CHILDREN:
        child = output_dir / child_name
        if child.is_dir():
            rmtree(child)
        elif child.exists():
            child.unlink()


def _write_assets(output_dir: Path) -> None:
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "row-one.css").write_text(row_one_css(), encoding="utf-8")
    (assets_dir / "row-one.js").write_text(row_one_js(), encoding="utf-8")


def _write_detail_pages(edition: RowOneEdition, details_dir: Path) -> None:
    details_dir.mkdir(parents=True, exist_ok=True)
    for story in edition.stories:
        pure_path = _validated_detail_relative_path(story.detail_path)
        if pure_path is None:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path = details_dir.parent / Path(*pure_path.parts)
        if detail_path.parent != details_dir:
            raise ValueError(f"Invalid ROW ONE detail path: {story.detail_path}")
        detail_path.write_text(render_detail_html(edition, story), encoding="utf-8")


def build_row_one_app_payload(edition: RowOneEdition) -> dict[str, object]:
    stories = [_story_payload(edition, story) for story in edition.stories]
    return {
        "contract_version": ROW_ONE_APP_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": isoformat_z(edition.generated_at),
        "edition_date": isoformat_z(edition.edition_date),
        "summary": edition.summary.model_dump(mode="json"),
        "sections": [_section_payload(edition, section) for section in edition.sections],
        "stories": stories,
        "story_count": len(stories),
        "evidence_count": sum(_safe_evidence_count(story.evidence) for story in edition.stories),
    }


def build_row_one_manifest_payload(
    edition: RowOneEdition,
    app_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    app_payload = app_payload or build_row_one_app_payload(edition)
    story_count = int(app_payload["story_count"])
    return {
        "contract_version": ROW_ONE_MANIFEST_CONTRACT_VERSION,
        "brand": edition.brand,
        "generated_at": app_payload["generated_at"],
        "edition_date": app_payload["edition_date"],
        "manifest_schema_path": ROW_ONE_MANIFEST_SCHEMA_PATH,
        "app_contract": {
            "version": ROW_ONE_APP_CONTRACT_VERSION,
            "path": "data/edition.json",
            "schema_path": "schemas/row-one-app.schema.json",
        },
        "site": {
            "index_path": "index.html",
            "data_path": "data/edition.json",
            "manifest_path": "data/manifest.json",
            "assets_path": "assets/",
            "details_path": "details/",
        },
        "counts": {
            "story_count": story_count,
            "section_count": len(edition.sections),
            "evidence_count": app_payload["evidence_count"],
        },
        "readiness": {
            "status": "ready" if story_count > 0 else "empty",
        },
        "capabilities": {
            "bilingual": True,
            "static_site": True,
            "detail_pages": True,
            "sanitized_external_urls": True,
            "latest_only_cleanup": True,
            "seo_metadata": True,
        },
    }


def _section_payload(edition: RowOneEdition, section: RowOneSection) -> dict[str, object]:
    return {
        "key": section.key,
        "title": section.title.model_dump(mode="json"),
        "dek": section.dek.model_dump(mode="json"),
        "href": f"#{section.key}",
        "story_count": len(edition.section_stories(section.key)),
    }


def _story_payload(edition: RowOneEdition, story: RowOneStory) -> dict[str, object]:
    section = _section_for_story(edition, story.section_key)
    detail_href = _app_detail_href(story.detail_path)
    published_at_utc = utc_datetime(story.published_at) if story.published_at else None
    return {
        "id": story.id,
        "section_key": story.section_key,
        "section": {
            "key": section.key,
            "title": section.title.model_dump(mode="json"),
            "href": f"#{section.key}",
        },
        "headline": story.headline,
        "summary": story.summary.model_dump(mode="json"),
        "why_it_matters": story.why_it_matters.model_dump(mode="json"),
        "editorial_takeaway": story.editorial_takeaway.model_dump(mode="json"),
        "signal_context": story.signal_context.model_dump(mode="json"),
        "reader_path": story.reader_path.model_dump(mode="json"),
        "source_name": story.source_name,
        "source_url": safe_external_url(story.source_url),
        "published_at": isoformat_z(published_at_utc) if published_at_utc else None,
        "published_date": published_at_utc.date().isoformat() if published_at_utc else None,
        "detail_path": detail_href,
        "href": detail_href,
        "detail_href": detail_href,
        "tags": list(story.tags),
        "evidence_count": _safe_evidence_count(story.evidence),
        "evidence": [_evidence_payload(link) for link in story.evidence],
    }


def _section_for_story(edition: RowOneEdition, section_key: str) -> RowOneSection:
    for section in edition.sections:
        if section.key == section_key:
            return section
    return RowOneSection(
        key=section_key,
        title=type(edition.summary)(zh=section_key, en=section_key.replace("_", " ").title()),
        dek=type(edition.summary)(zh="", en=""),
    )


def _evidence_payload(link: RowOneLink) -> dict[str, object]:
    safe_url = safe_external_url(link.url)
    return {
        "title": link.title,
        "url": safe_url,
        "href": safe_url,
        "source_name": link.source_name,
    }


def _safe_evidence_count(evidence: list[RowOneLink]) -> int:
    return sum(1 for link in evidence if safe_external_url(link.url) is not None)


def _app_detail_href(detail_path: str) -> str:
    pure_path = _validated_detail_relative_path(detail_path)
    if pure_path is None:
        raise ValueError(f"Invalid ROW ONE detail path: {detail_path}")
    return str(pure_path)
