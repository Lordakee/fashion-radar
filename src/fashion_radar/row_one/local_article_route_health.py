from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from fashion_radar.row_one.articles import safe_local_article_story_id

LOCAL_ARTICLE_LIBRARY_PATH = "articles/index.html"


@dataclass(frozen=True)
class RowOneLocalArticleRouteHealth:
    status: str
    article_count: int
    library_path: str
    library_present: bool
    homepage_library_link_present: bool
    missing_article_pages: tuple[str, ...]
    missing_library_links: tuple[str, ...]


def build_row_one_local_article_route_health(
    site_dir: Path,
    story_ids: Iterable[str] | None = None,
) -> RowOneLocalArticleRouteHealth:
    resolved_story_ids = _resolve_story_ids(site_dir, story_ids)
    if not resolved_story_ids:
        return RowOneLocalArticleRouteHealth(
            status="not_applicable",
            article_count=0,
            library_path=LOCAL_ARTICLE_LIBRARY_PATH,
            library_present=False,
            homepage_library_link_present=False,
            missing_article_pages=(),
            missing_library_links=(),
        )

    library_present = (site_dir / LOCAL_ARTICLE_LIBRARY_PATH).is_file()
    homepage_library_link_present = _html_contains_href(
        site_dir / "index.html",
        LOCAL_ARTICLE_LIBRARY_PATH,
    )
    missing_article_pages = tuple(
        f"articles/{story_id}.html"
        for story_id in resolved_story_ids
        if not (site_dir / "articles" / f"{story_id}.html").is_file()
    )
    missing_library_links = (
        tuple(
            f"{story_id}.html"
            for story_id in resolved_story_ids
            if not _html_contains_href(
                site_dir / LOCAL_ARTICLE_LIBRARY_PATH,
                f"{story_id}.html",
            )
        )
        if library_present
        else ()
    )
    status = (
        "ready"
        if library_present
        and homepage_library_link_present
        and not missing_article_pages
        and not missing_library_links
        else "missing"
    )
    return RowOneLocalArticleRouteHealth(
        status=status,
        article_count=len(resolved_story_ids),
        library_path=LOCAL_ARTICLE_LIBRARY_PATH,
        library_present=library_present,
        homepage_library_link_present=homepage_library_link_present,
        missing_article_pages=missing_article_pages,
        missing_library_links=missing_library_links,
    )


def row_one_local_article_route_health_payload(
    health: RowOneLocalArticleRouteHealth,
) -> dict[str, object]:
    return {
        "status": health.status,
        "article_count": health.article_count,
        "library_path": health.library_path,
        "library_present": health.library_present,
        "homepage_library_link_present": health.homepage_library_link_present,
        "missing_article_pages": list(health.missing_article_pages),
        "missing_library_links": list(health.missing_library_links),
    }


def validate_row_one_local_article_route_health(
    health: RowOneLocalArticleRouteHealth,
) -> None:
    if health.status in {"ready", "not_applicable"}:
        return
    if not health.library_present:
        raise ValueError(f"row-one local article library route is missing: {health.library_path}")
    if not health.homepage_library_link_present:
        raise ValueError(
            f"row-one local article library link is missing from index.html: {health.library_path}"
        )
    if health.missing_article_pages:
        raise ValueError(
            f"row-one local article route is missing: {health.missing_article_pages[0]}"
        )
    if health.missing_library_links:
        raise ValueError(
            "row-one local article library page is missing article link: "
            f"{health.missing_library_links[0]}"
        )
    raise ValueError("row-one local article route health is missing")


def _resolve_story_ids(
    site_dir: Path,
    story_ids: Iterable[str] | None,
) -> tuple[str, ...]:
    if story_ids is None:
        articles_dir = site_dir / "data" / "articles"
        if not articles_dir.is_dir():
            return ()
        return tuple(
            sorted(
                {
                    path.stem
                    for path in articles_dir.glob("*.json")
                    if safe_local_article_story_id(path.stem)
                }
            )
        )

    candidates = (story_ids,) if isinstance(story_ids, str) else story_ids
    safe_ids = {story_id for story_id in candidates if safe_local_article_story_id(story_id)}
    return tuple(sorted(safe_ids))


def _html_contains_href(path: Path, href: str) -> bool:
    try:
        html = path.read_text(encoding="utf-8")
    except OSError:
        return False
    parser = _HrefCollector()
    parser.feed(html)
    return _normalize_href(href) in {_normalize_href(found) for found in parser.hrefs}


def _normalize_href(href: str) -> str:
    while href.startswith("./"):
        href = href[2:]
    return href


class _HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.hrefs.append(value)
