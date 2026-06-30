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


def test_source_type_includes_xiaohongshu_value() -> None:
    assert SourceType.XIAOHONGSHU == "xiaohongshu"


def test_xiaohongshu_source_requires_query() -> None:
    with pytest.raises(ValidationError, match="xiaohongshu source requires query"):
        SourceDefinition(name="XHS", type=SourceType.XIAOHONGSHU)


def test_xiaohongshu_source_with_query_is_valid() -> None:
    source = SourceDefinition(name="XHS", type=SourceType.XIAOHONGSHU, query="the row")

    assert source.query == "the row"
    assert source.xiaohongshu.endpoint == "http://localhost:18060/mcp"
    assert source.xiaohongshu.max_notes_per_run == 20


def test_source_type_includes_instagram_value() -> None:
    assert SourceType.INSTAGRAM == "instagram"


def test_instagram_source_requires_query() -> None:
    with pytest.raises(ValidationError, match="instagram source requires query"):
        SourceDefinition(name="IG", type=SourceType.INSTAGRAM)


def test_instagram_source_with_query_is_valid() -> None:
    source = SourceDefinition(name="IG", type=SourceType.INSTAGRAM, query="therow")

    assert source.query == "therow"
    assert source.instagram.target_type == "hashtag"
    assert source.instagram.max_posts_per_run == 20


def test_source_type_includes_twitter_value() -> None:
    assert SourceType.TWITTER == "twitter"


def test_twitter_source_requires_query() -> None:
    with pytest.raises(ValidationError, match="twitter source requires query"):
        SourceDefinition(name="X", type=SourceType.TWITTER)


def test_twitter_source_with_query_is_valid() -> None:
    source = SourceDefinition(name="X", type=SourceType.TWITTER, query="therow")

    assert source.query == "therow"
    assert source.twitter.output_format == "json"
    assert source.twitter.max_tweets_per_run == 20


def test_source_type_includes_youtube_value() -> None:
    assert SourceType.YOUTUBE == "youtube"


def test_youtube_source_requires_query() -> None:
    with pytest.raises(ValidationError, match="youtube source requires query"):
        SourceDefinition(name="YT", type=SourceType.YOUTUBE)


def test_youtube_source_with_query_is_valid() -> None:
    source = SourceDefinition(name="YT", type=SourceType.YOUTUBE, query="fashion week")

    assert source.query == "fashion week"
    assert source.youtube.search_prefix == "ytsearch"
    assert source.youtube.max_videos_per_run == 20
