from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree

from fashion_radar.row_one.models import RowOneEdition
from fashion_radar.row_one.templates import (
    _safe_external_url,
    _validated_detail_relative_path,
    render_detail_html,
    render_index_html,
    row_one_css,
    row_one_js,
)

GENERATED_CHILDREN = ("index.html", ".row-one-site", "details", "assets", "data")


@dataclass(frozen=True)
class RowOneRenderResult:
    output_dir: Path
    index_path: Path
    story_count: int


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
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "edition.json").write_text(
        json.dumps(_sanitized_edition_payload(edition), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return RowOneRenderResult(
        output_dir=output_dir,
        index_path=index_path,
        story_count=len(edition.stories),
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


def _sanitized_edition_payload(edition: RowOneEdition) -> dict[str, object]:
    payload = edition.model_dump(mode="json")
    stories = payload.get("stories", [])
    if not isinstance(stories, list):
        return payload
    for story in stories:
        if not isinstance(story, dict):
            continue
        story["source_url"] = _safe_external_url(story.get("source_url"))
        evidence = story.get("evidence", [])
        if not isinstance(evidence, list):
            continue
        for link in evidence:
            if isinstance(link, dict):
                link["url"] = _safe_external_url(link.get("url"))
    return payload
