from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from fashion_radar.row_one.local_article_route_health import (
    RowOneLocalArticleRouteHealth,
    build_row_one_local_article_route_health,
    row_one_local_article_route_health_payload,
    validate_row_one_local_article_route_health,
)


def _write_base_site(site_dir: Path) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text(
        '<a href="articles/index.html">Saved article library</a>',
        encoding="utf-8",
    )


def _write_article_sidecar(site_dir: Path, story_id: str) -> None:
    articles_dir = site_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / f"{story_id}.json").write_text("{}", encoding="utf-8")


def _write_article_routes(site_dir: Path, story_id: str) -> None:
    articles_dir = site_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "index.html").write_text(
        f'<a href="{story_id}.html">Read local article</a>',
        encoding="utf-8",
    )
    (articles_dir / f"{story_id}.html").write_text(
        "<!doctype html><title>ROW ONE article</title>",
        encoding="utf-8",
    )


def test_route_health_is_not_applicable_without_saved_article_sidecars(
    tmp_path: Path,
) -> None:
    _write_base_site(tmp_path)

    health = build_row_one_local_article_route_health(tmp_path)

    assert health == RowOneLocalArticleRouteHealth(
        status="not_applicable",
        article_count=0,
        library_path="articles/index.html",
        library_present=False,
        homepage_library_link_present=False,
        missing_article_pages=(),
        missing_library_links=(),
    )


def test_route_health_reports_ready_for_linked_library_and_article_pages(
    tmp_path: Path,
) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "story-0000000001")
    _write_article_routes(tmp_path, "story-0000000001")

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.library_path == "articles/index.html"
    assert health.library_present is True
    assert health.homepage_library_link_present is True
    assert health.missing_article_pages == ()
    assert health.missing_library_links == ()


def test_route_health_reports_missing_library_route(tmp_path: Path) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "story-0000000001")

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "missing"
    assert health.article_count == 1
    assert health.library_present is False
    assert health.homepage_library_link_present is True
    assert health.missing_article_pages == ("articles/story-0000000001.html",)
    assert health.missing_library_links == ()


def test_route_health_reports_missing_homepage_library_link(tmp_path: Path) -> None:
    _write_base_site(tmp_path)
    (tmp_path / "index.html").write_text(
        '<a href="details/index.html">Saved article library</a>',
        encoding="utf-8",
    )
    _write_article_sidecar(tmp_path, "story-0000000001")
    _write_article_routes(tmp_path, "story-0000000001")

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "missing"
    assert health.library_present is True
    assert health.homepage_library_link_present is False
    assert health.missing_article_pages == ()
    assert health.missing_library_links == ()


def test_route_health_reports_missing_article_pages_and_library_links_deterministically(
    tmp_path: Path,
) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "story-000000000c")
    _write_article_sidecar(tmp_path, "story-000000000a")
    _write_article_sidecar(tmp_path, "story-000000000b")
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir(parents=True)
    (articles_dir / "index.html").write_text(
        '<a href="story-000000000b.html">Read local article</a>',
        encoding="utf-8",
    )
    (articles_dir / "story-000000000b.html").write_text(
        "<!doctype html><title>ROW ONE article</title>",
        encoding="utf-8",
    )

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "missing"
    assert health.article_count == 3
    assert health.missing_article_pages == (
        "articles/story-000000000a.html",
        "articles/story-000000000c.html",
    )
    assert health.missing_library_links == (
        "story-000000000a.html",
        "story-000000000c.html",
    )


def test_route_health_uses_supplied_story_ids_exactly(tmp_path: Path) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "ignored-sidecar-0000000001")
    _write_article_routes(tmp_path, "supplied-0000000001")
    library_path = tmp_path / "articles" / "index.html"
    library_path.write_text(
        "<a href='supplied-0000000001.html'>Read local article</a>",
        encoding="utf-8",
    )

    health = build_row_one_local_article_route_health(
        tmp_path,
        "supplied-0000000001",
    )

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.missing_article_pages == ()
    assert health.missing_library_links == ()

    list_health = build_row_one_local_article_route_health(
        tmp_path,
        [
            "z-story-000000000f",
            "../unsafe",
            "a-story-000000000a",
            "z-story-000000000f",
        ],
    )
    assert list_health.article_count == 2
    assert list_health.missing_article_pages == (
        "articles/a-story-000000000a.html",
        "articles/z-story-000000000f.html",
    )
    assert list_health.missing_library_links == (
        "a-story-000000000a.html",
        "z-story-000000000f.html",
    )


def test_route_health_accepts_html_href_variants(tmp_path: Path) -> None:
    story_id = "story-0000000001"
    (tmp_path / "index.html").write_text(
        '<a HREF = "./articles/index.html">Saved article library</a>',
        encoding="utf-8",
    )
    _write_article_sidecar(tmp_path, story_id)
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    (articles_dir / "index.html").write_text(
        f"<a HREF = './{story_id}.html'>Read local article</a>",
        encoding="utf-8",
    )
    (articles_dir / f"{story_id}.html").write_text(
        "<!doctype html><title>ROW ONE article</title>",
        encoding="utf-8",
    )

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "ready"
    assert health.homepage_library_link_present is True
    assert health.missing_library_links == ()


def test_route_health_payload_is_stable(tmp_path: Path) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "story-0000000001")
    _write_article_routes(tmp_path, "story-0000000001")

    payload = row_one_local_article_route_health_payload(
        build_row_one_local_article_route_health(tmp_path)
    )

    assert payload == {
        "status": "ready",
        "article_count": 1,
        "library_path": "articles/index.html",
        "library_present": True,
        "homepage_library_link_present": True,
        "missing_article_pages": [],
        "missing_library_links": [],
    }

    not_applicable_payload = row_one_local_article_route_health_payload(
        build_row_one_local_article_route_health(tmp_path / "empty-site")
    )

    assert not_applicable_payload == {
        "status": "not_applicable",
        "article_count": 0,
        "library_path": "articles/index.html",
        "library_present": False,
        "homepage_library_link_present": False,
        "missing_article_pages": [],
        "missing_library_links": [],
    }


def test_validate_route_health_raises_clear_errors() -> None:
    ready = RowOneLocalArticleRouteHealth(
        status="ready",
        article_count=1,
        library_path="articles/index.html",
        library_present=True,
        homepage_library_link_present=True,
        missing_article_pages=(),
        missing_library_links=(),
    )
    validate_row_one_local_article_route_health(ready)
    validate_row_one_local_article_route_health(
        replace(ready, status="not_applicable", article_count=0)
    )

    with pytest.raises(ValueError, match="articles/index.html"):
        validate_row_one_local_article_route_health(
            replace(ready, status="missing", library_present=False)
        )
    with pytest.raises(ValueError, match="library link is missing from index.html"):
        validate_row_one_local_article_route_health(
            replace(ready, status="missing", homepage_library_link_present=False)
        )
    with pytest.raises(ValueError, match="library link is missing from index.html"):
        validate_row_one_local_article_route_health(
            replace(
                ready,
                status="missing",
                homepage_library_link_present=False,
                missing_article_pages=("articles/story-0000000001.html",),
                missing_library_links=("story-0000000001.html",),
            )
        )
    with pytest.raises(ValueError, match="local article route is missing: articles/"):
        validate_row_one_local_article_route_health(
            replace(
                ready,
                status="missing",
                missing_article_pages=("articles/story-0000000001.html",),
            )
        )
    with pytest.raises(ValueError, match="library page is missing article link"):
        validate_row_one_local_article_route_health(
            replace(
                ready,
                status="missing",
                missing_library_links=("story-0000000001.html",),
            )
        )


def test_route_health_discovery_ignores_unsafe_sidecar_stems(tmp_path: Path) -> None:
    _write_base_site(tmp_path)
    _write_article_sidecar(tmp_path, "safe-story-0000000001")
    _write_article_routes(tmp_path, "safe-story-0000000001")
    articles_dir = tmp_path / "data" / "articles"
    (articles_dir / "../unsafe.json").write_text("{}", encoding="utf-8")
    (articles_dir / "unsafe story.json").write_text("{}", encoding="utf-8")
    (articles_dir / "unsafe.html").write_text("{}", encoding="utf-8")

    health = build_row_one_local_article_route_health(tmp_path)

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.missing_article_pages == ()
    assert health.missing_library_links == ()
