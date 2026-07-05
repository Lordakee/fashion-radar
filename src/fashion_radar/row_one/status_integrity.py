from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urldefrag

from pydantic import ValidationError

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.display import safe_story_image_src
from fashion_radar.row_one.models import (
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneDailyLocalIntelligenceSegmentItem,
    RowOneLocalArticle,
)

_LOCAL_ARTICLE_FRAGMENT = "local-article"
_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph-"
_REQUIRED_GENERATED_FILES = (
    "index.html",
    "data/edition.json",
    "data/manifest.json",
    "data/runtime.json",
    "assets/row-one.css",
    "assets/row-one.js",
)


def validate_row_one_generated_site_integrity(
    *,
    site_dir: Path,
    edition: dict[str, object],
) -> None:
    """Validate generated ROW ONE files that schemas cannot express."""
    for relative_path in _REQUIRED_GENERATED_FILES:
        _require_file(site_dir, relative_path)

    stories = edition.get("stories")
    if not isinstance(stories, list):
        raise ValueError("row-one edition.stories must be a JSON array")

    current_story_ids: set[str] = set()
    detail_to_story_id: dict[str, str] = {}
    for story_index, story in enumerate(stories):
        if not isinstance(story, dict):
            raise ValueError(f"row-one edition.stories[{story_index}] must be a JSON object")
        story_id = story.get("id")
        if not isinstance(story_id, str) or not story_id:
            raise ValueError(
                f"row-one edition.stories[{story_index}].id must be a non-empty string"
            )
        if story_id in current_story_ids:
            raise ValueError(f"row-one edition.stories[{story_index}].id is duplicated: {story_id}")
        if not safe_local_article_story_id(story_id):
            raise ValueError(f"row-one edition.stories[{story_index}].id is not safe: {story_id}")
        current_story_ids.add(story_id)

        detail_path = _validate_story_detail_paths(
            story,
            expected_detail_path=f"details/{story_id}.html",
            story_index=story_index,
        )
        if detail_path in detail_to_story_id:
            raise ValueError(
                f"row-one edition.stories[{story_index}].detail_href is duplicated: {detail_path}"
            )
        detail_to_story_id[detail_path] = story_id
        _require_file(site_dir, detail_path)
        _validate_story_display_image(
            site_dir,
            story.get("display"),
            label=f"edition.stories[{story_index}].display",
        )

    article_sidecars = _load_article_sidecars(site_dir, current_story_ids)
    _validate_local_intelligence(
        site_dir=site_dir,
        detail_to_story_id=detail_to_story_id,
        article_sidecars=article_sidecars,
    )


def _require_file(site_dir: Path, relative_path: str) -> Path:
    path = site_dir / relative_path
    if not path.is_file():
        raise ValueError(f"row-one generated file is missing: {relative_path}")
    return path


def _read_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"row-one {label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"row-one {label} must contain a JSON object")
    return payload


def _read_json_list(path: Path, *, label: str) -> list[object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"row-one {label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise ValueError(f"row-one {label} must contain a JSON array")
    return payload


def _validate_detail_path(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"row-one {label} must be a non-empty detail path")
    if value.strip() != value or "\\" in value:
        raise ValueError(f"row-one {label} is not a safe detail path: {value!r}")
    base, fragment = urldefrag(value)
    if fragment:
        raise ValueError(f"row-one {label} must not include a fragment: {value}")
    path = PurePosixPath(base)
    if (
        path.is_absolute()
        or path.as_posix() != base
        or len(path.parts) != 2
        or path.parts[0] != "details"
        or path.parts[1] in {"", ".", ".."}
        or ".." in path.parts
        or not path.parts[1].endswith(".html")
    ):
        raise ValueError(f"row-one {label} is not a safe detail path: {value}")
    return path.as_posix()


def _validate_story_detail_paths(
    story: dict[str, object],
    *,
    expected_detail_path: str,
    story_index: int,
) -> str:
    validated: dict[str, str] = {}
    for key in ("detail_href", "detail_path", "href"):
        detail_path = _validate_detail_path(
            story.get(key),
            label=f"edition.stories[{story_index}].{key}",
        )
        if detail_path != expected_detail_path:
            raise ValueError(
                f"row-one edition.stories[{story_index}].{key} must equal {expected_detail_path!r}"
            )
        validated[key] = detail_path
    if len(set(validated.values())) != 1:
        raise ValueError(
            f"row-one edition.stories[{story_index}] detail_href, detail_path, and href must match"
        )
    return validated["detail_href"]


def _validate_local_intelligence_href(value: object, *, label: str) -> tuple[str, str]:
    if not isinstance(value, str) or not value:
        raise ValueError(f"row-one {label} must be a non-empty local-intelligence detail_path")
    base, fragment = urldefrag(value)
    detail_path = _validate_detail_path(base, label=label)
    if fragment in {"", _LOCAL_ARTICLE_FRAGMENT}:
        return detail_path, fragment
    if fragment.startswith(_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX):
        paragraph_number = fragment.removeprefix(_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX)
        if (
            paragraph_number.isdecimal()
            and paragraph_number == str(int(paragraph_number))
            and int(paragraph_number) >= 1
        ):
            return detail_path, fragment
    raise ValueError(f"row-one {label} has an unsupported local article fragment: {value}")


def _validate_story_display_image(site_dir: Path, display: object, *, label: str) -> None:
    if not isinstance(display, dict):
        return
    image = display.get("image")
    if image is None:
        return
    if not isinstance(image, dict):
        raise ValueError(f"row-one {label}.image must be a JSON object or null")
    src = image.get("src")
    if src is None:
        return
    if not isinstance(src, str):
        raise ValueError(f"row-one {label}.image.src must be a string")
    safe_src = safe_story_image_src(src)
    if safe_src is None:
        raise ValueError(f"row-one {label}.image.src is not safe: {src!r}")
    if safe_src.startswith("assets/"):
        _require_file(site_dir, safe_src)


def _load_article_sidecars(
    site_dir: Path,
    current_story_ids: set[str],
) -> dict[str, RowOneLocalArticle]:
    articles_dir = site_dir / "data" / "articles"
    if not articles_dir.exists():
        return {}
    if not articles_dir.is_dir():
        raise ValueError("row-one data/articles must be a directory")

    articles: dict[str, RowOneLocalArticle] = {}
    for article_path in sorted(articles_dir.glob("*.json")):
        relative_path = article_path.relative_to(site_dir).as_posix()
        story_id = article_path.stem
        if not safe_local_article_story_id(story_id):
            raise ValueError(f"row-one article sidecar filename is not safe: {relative_path}")
        if story_id not in current_story_ids:
            raise ValueError(
                f"row-one article sidecar references an unknown current story: {relative_path}"
            )
        payload = _read_json_object(article_path, label=relative_path)
        try:
            article = RowOneLocalArticle.model_validate(payload)
        except ValidationError as exc:
            raise ValueError(
                f"row-one {relative_path} is not a valid article sidecar: {exc}"
            ) from exc
        if article.story_id != story_id:
            raise ValueError(
                f"row-one {relative_path} story_id must match filename stem {story_id!r}"
            )
        _validate_article_paragraphs(article, label=relative_path)
        articles[story_id] = article
    return articles


def _validate_article_paragraphs(article: RowOneLocalArticle, *, label: str) -> None:
    rendered_indices = _rendered_paragraph_indices(article)
    if not rendered_indices:
        raise ValueError(f"row-one {label} must include at least one non-empty paragraph")
    if article.paragraphs_zh and len(article.paragraphs_zh) != len(article.paragraphs):
        raise ValueError(f"row-one {label}.paragraphs_zh must align with paragraphs when present")
    for section_index, section in enumerate(article.content_sections):
        for item_index, item in enumerate(section.items):
            _validate_paragraph_indices(
                item.paragraph_indices,
                rendered_indices=rendered_indices,
                label=(
                    f"{label}.content_sections[{section_index}]"
                    f".items[{item_index}].paragraph_indices"
                ),
            )


def _validate_local_intelligence(
    *,
    site_dir: Path,
    detail_to_story_id: dict[str, str],
    article_sidecars: dict[str, RowOneLocalArticle],
) -> None:
    local_intelligence_path = site_dir / "data" / "local-intelligence.json"
    if not local_intelligence_path.exists():
        return
    payload = _read_json_list(local_intelligence_path, label="data/local-intelligence.json")
    html_cache: dict[str, str] = {}
    for section_index, section_payload in enumerate(payload):
        try:
            section = RowOneDailyLocalIntelligenceSection.model_validate(section_payload)
        except ValidationError as exc:
            raise ValueError(
                f"row-one data/local-intelligence.json section[{section_index}] is not valid: {exc}"
            ) from exc
        for item_index, item in enumerate(section.items):
            _validate_local_intelligence_item(
                item,
                site_dir=site_dir,
                detail_to_story_id=detail_to_story_id,
                article_sidecars=article_sidecars,
                html_cache=html_cache,
                label=(f"data/local-intelligence.json[{section_index}].items[{item_index}]"),
            )


def _validate_local_intelligence_item(
    item: RowOneDailyLocalIntelligenceItem,
    *,
    site_dir: Path,
    detail_to_story_id: dict[str, str],
    article_sidecars: dict[str, RowOneLocalArticle],
    html_cache: dict[str, str],
    label: str,
) -> None:
    story_id: str | None = None
    detail_path: str | None = None
    if item.detail_path:
        detail_path, fragment = _validate_local_intelligence_href(
            item.detail_path,
            label=f"{label}.detail_path",
        )
        story_id = detail_to_story_id.get(detail_path)
        if story_id is None:
            raise ValueError(
                f"row-one {label}.detail_path points to an unknown current story: {detail_path}"
            )
        _require_file(site_dir, detail_path)
        article = _article_for_local_intelligence(
            article_sidecars,
            story_id,
            label=f"{label}.detail_path",
        )
        _validate_article_fragment(
            article,
            site_dir=site_dir,
            detail_path=detail_path,
            fragment=fragment,
            html_cache=html_cache,
            label=f"{label}.detail_path",
        )
        if item.source_name and item.source_names and item.source_name not in item.source_names:
            raise ValueError(f"row-one {label}.source_name must be included in source_names")
        if item.source_names and article.source_name not in item.source_names:
            raise ValueError(f"row-one {label}.source_names must include the article source_name")
    elif item.paragraph_indices:
        raise ValueError(f"row-one {label}.paragraph_indices require detail_path")

    if item.paragraph_indices:
        if story_id is None:
            raise ValueError(f"row-one {label}.paragraph_indices require a resolved story_id")
        article = _article_for_local_intelligence(
            article_sidecars,
            story_id,
            label=f"{label}.paragraph_indices",
        )
        _validate_paragraph_indices(
            item.paragraph_indices,
            rendered_indices=_rendered_paragraph_indices(article),
            label=f"{label}.paragraph_indices",
        )
        _validate_paragraph_anchors(
            site_dir,
            detail_path,
            item.paragraph_indices,
            html_cache=html_cache,
            label=f"{label}.paragraph_indices",
        )

    for segment_index, segment in enumerate(item.segments):
        for segment_item_index, segment_item in enumerate(segment.items):
            _validate_local_intelligence_segment_item(
                segment_item,
                site_dir=site_dir,
                story_id=story_id,
                detail_path=detail_path,
                article_sidecars=article_sidecars,
                html_cache=html_cache,
                label=(f"{label}.segments[{segment_index}].items[{segment_item_index}]"),
            )


def _validate_local_intelligence_segment_item(
    item: RowOneDailyLocalIntelligenceSegmentItem,
    *,
    site_dir: Path,
    story_id: str | None,
    detail_path: str | None,
    article_sidecars: dict[str, RowOneLocalArticle],
    html_cache: dict[str, str],
    label: str,
) -> None:
    if not item.paragraph_indices:
        return
    if story_id is None or detail_path is None:
        raise ValueError(f"row-one {label}.paragraph_indices require parent detail_path")
    article = _article_for_local_intelligence(
        article_sidecars,
        story_id,
        label=f"{label}.paragraph_indices",
    )
    _validate_paragraph_indices(
        item.paragraph_indices,
        rendered_indices=_rendered_paragraph_indices(article),
        label=f"{label}.paragraph_indices",
    )
    _validate_paragraph_anchors(
        site_dir,
        detail_path,
        item.paragraph_indices,
        html_cache=html_cache,
        label=f"{label}.paragraph_indices",
    )


def _article_for_local_intelligence(
    article_sidecars: dict[str, RowOneLocalArticle],
    story_id: str,
    *,
    label: str,
) -> RowOneLocalArticle:
    article = article_sidecars.get(story_id)
    if article is None:
        raise ValueError(f"row-one {label} requires data/articles/{story_id}.json")
    return article


def _validate_article_fragment(
    article: RowOneLocalArticle,
    *,
    site_dir: Path,
    detail_path: str,
    fragment: str,
    html_cache: dict[str, str],
    label: str,
) -> None:
    if fragment == "":
        return
    detail_html = html_cache.get(detail_path)
    if detail_html is None:
        detail_html = (site_dir / detail_path).read_text(encoding="utf-8")
        html_cache[detail_path] = detail_html

    if fragment == _LOCAL_ARTICLE_FRAGMENT:
        _require_html_anchor(detail_html, _LOCAL_ARTICLE_FRAGMENT, label=label)
        return

    paragraph_index = _paragraph_index_from_fragment(fragment, label=label)
    _validate_paragraph_indices(
        [paragraph_index],
        rendered_indices=_rendered_paragraph_indices(article),
        label=label,
    )
    _require_html_anchor(
        detail_html,
        f"{_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX}{paragraph_index + 1}",
        label=label,
    )


def _validate_paragraph_anchors(
    site_dir: Path,
    detail_path: str,
    paragraph_indices: list[int],
    *,
    html_cache: dict[str, str],
    label: str,
) -> None:
    detail_html = html_cache.get(detail_path)
    if detail_html is None:
        detail_html = (site_dir / detail_path).read_text(encoding="utf-8")
        html_cache[detail_path] = detail_html
    for index in paragraph_indices:
        _require_html_anchor(
            detail_html,
            f"{_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX}{index + 1}",
            label=label,
        )


def _paragraph_index_from_fragment(fragment: str, *, label: str) -> int:
    if not fragment.startswith(_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX):
        raise ValueError(f"row-one {label} has unsupported local article fragment: {fragment}")
    number = fragment.removeprefix(_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX)
    if not number.isdecimal() or int(number) < 1:
        raise ValueError(f"row-one {label} has invalid paragraph fragment: {fragment}")
    return int(number) - 1


def _validate_paragraph_indices(
    paragraph_indices: list[int],
    *,
    rendered_indices: set[int],
    label: str,
) -> None:
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError(f"row-one {label} must contain integer paragraph indices")
        if index not in rendered_indices:
            raise ValueError(f"row-one {label} references a missing rendered paragraph: {index}")


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _require_html_anchor(detail_html: str, anchor: str, *, label: str) -> None:
    if anchor not in _html_ids(detail_html):
        raise ValueError(f"row-one {label} target anchor is missing from detail HTML: {anchor}")


def _html_ids(detail_html: str) -> set[str]:
    parser = _IdCollectingHTMLParser()
    parser.feed(detail_html)
    return parser.ids


class _IdCollectingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.add(value)
