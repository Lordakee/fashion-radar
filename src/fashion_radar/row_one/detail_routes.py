from __future__ import annotations

import re
from pathlib import PurePosixPath

DETAIL_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$")


def validated_row_one_detail_relative_path(path: str) -> PurePosixPath | None:
    pure_path = PurePosixPath(path)
    if (
        pure_path.is_absolute()
        or len(pure_path.parts) != 2
        or pure_path.parts[0] != "details"
        or pure_path.parts[1] in ("", ".", "..")
        or ".." in pure_path.parts
        or DETAIL_FILENAME_RE.fullmatch(pure_path.name) is None
    ):
        return None
    return pure_path


def is_safe_row_one_detail_path(path: str) -> bool:
    return validated_row_one_detail_relative_path(path) is not None


def safe_row_one_detail_fragment_href(href: object, fragment: str) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return None
    path, actual_fragment = href.split("#", 1)
    if actual_fragment != fragment:
        return None
    if validated_row_one_detail_relative_path(path) is None:
        return None
    return href
