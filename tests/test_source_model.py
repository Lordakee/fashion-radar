from __future__ import annotations

import pytest
from pydantic import ValidationError

from fashion_radar.models.source import SourceDefinition, SourceType


def test_source_type_includes_html_and_sitemap_values() -> None:
    assert SourceType.HTML == "html"
    assert SourceType.SITEMAP == "sitemap"


def test_source_definition_seed_urls_defaults_to_empty_list() -> None:
    source = SourceDefinition(name="Brand X", type=SourceType.HTML, url="https://brandx.com/news")

    assert source.seed_urls == []


def test_html_source_requires_url_or_seed_urls() -> None:
    with pytest.raises(ValidationError, match="html source requires url or seed_urls"):
        SourceDefinition(name="Brand X", type=SourceType.HTML)


def test_html_source_with_only_seed_urls_is_valid() -> None:
    source = SourceDefinition(
        name="Brand X",
        type=SourceType.HTML,
        seed_urls=["https://brandx.com/press", "https://brandx.com/collections"],
    )

    assert source.url is None
    assert source.seed_urls == ["https://brandx.com/press", "https://brandx.com/collections"]


def test_html_source_with_only_url_is_valid() -> None:
    source = SourceDefinition(name="Brand X", type=SourceType.HTML, url="https://brandx.com/news")

    assert source.url == "https://brandx.com/news"
    assert source.seed_urls == []


def test_sitemap_source_requires_url() -> None:
    with pytest.raises(ValidationError, match="sitemap source requires url"):
        SourceDefinition(name="News Daily", type=SourceType.SITEMAP)


def test_sitemap_source_with_url_is_valid() -> None:
    source = SourceDefinition(
        name="News Daily",
        type=SourceType.SITEMAP,
        url="https://newsdaily.com/sitemap.xml",
    )

    assert source.url == "https://newsdaily.com/sitemap.xml"
