from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Final
from urllib.parse import unquote

from fashion_radar.row_one.models import (
    RowOneDisplayAccent,
    RowOneDisplayVariant,
    RowOneStory,
    RowOneStoryDisplay,
    RowOneStoryImage,
)
from fashion_radar.row_one.utils import safe_external_url

_SECTION_DISPLAY: Final[dict[str, tuple[RowOneDisplayVariant, RowOneDisplayAccent]]] = {
    "top_stories": ("editorial", "ink"),
    "brand_moves": ("editorial", "graphite"),
    "celebrity_style": ("portrait", "rose"),
    "hot_products": ("product", "cobalt"),
    "rising_radar": ("signal", "steel"),
}
_DEFAULT_DISPLAY: Final = _SECTION_DISPLAY["top_stories"]
_SAFE_ASSET_PATH_RE: Final = re.compile(
    r"^assets/(?!.*\.\.)(?:[A-Za-z0-9._~-]+/)*[A-Za-z0-9._~-]+$"
)


def display_for_section(section_key: str) -> RowOneStoryDisplay:
    variant, accent = _SECTION_DISPLAY.get(section_key, _DEFAULT_DISPLAY)
    return RowOneStoryDisplay(variant=variant, accent=accent)


def display_for_story(story: RowOneStory) -> RowOneStoryDisplay:
    if story.display is None:
        return display_for_section(story.section_key)
    return RowOneStoryDisplay(
        variant=story.display.variant,
        accent=story.display.accent,
        image=_safe_story_image(story.display.image),
    )


def safe_story_image_src(value: str | None) -> str | None:
    if value is None:
        return None
    if not value or value.strip() != value or _has_unsafe_path_chars(value):
        return None
    safe_url = safe_external_url(value)
    if safe_url is not None:
        return safe_url
    return _safe_asset_path(value)


def _safe_story_image(image: RowOneStoryImage | None) -> RowOneStoryImage | None:
    if image is None:
        return None
    src = safe_story_image_src(image.src)
    if src is None:
        return None
    return RowOneStoryImage(
        src=src,
        alt=image.alt,
        credit=image.credit,
        source_url=safe_external_url(image.source_url),
    )


def _safe_asset_path(value: str) -> str | None:
    path = PurePosixPath(value)
    decoded_value = unquote(value)
    decoded_path = PurePosixPath(decoded_value)
    if (
        path.is_absolute()
        or len(path.parts) < 2
        or path.parts[0] != "assets"
        or ".." in path.parts
        or ".." in decoded_path.parts
        or _has_unsafe_path_chars(decoded_value)
        or _SAFE_ASSET_PATH_RE.fullmatch(value) is None
    ):
        return None
    return path.as_posix()


def _has_unsafe_path_chars(value: str) -> bool:
    return "\\" in value or any(
        character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value
    )
