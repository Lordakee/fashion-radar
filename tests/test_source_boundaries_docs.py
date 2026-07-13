from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BOUNDARIES_DOC = ROOT / "docs" / "source-boundaries.md"


def _read_source_boundaries_doc() -> str:
    return SOURCE_BOUNDARIES_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def _connector_risk_tier_subsection(text: str, heading: str) -> str:
    connector_risk_tiers = _section(text, "Connector Risk Tiers")
    marker = f"### {heading}"
    assert marker in connector_risk_tiers
    return connector_risk_tiers.split(marker, 1)[1].split("\n### ", 1)[0]


def _bullet_block(text: str, bullet_prefix: str) -> str:
    marker = f"- {bullet_prefix}"
    assert marker in text

    lines = text.split(marker, 1)[1].splitlines(keepends=True)
    block = [marker]
    for line_index, line in enumerate(lines):
        if line_index and line and not line[0].isspace():
            break
        block.append(line)
    return "".join(block)


def test_source_boundaries_docs_keep_storage_boundary() -> None:
    storage_boundaries = _section(
        _read_source_boundaries_doc(),
        "Storage Boundaries",
    )
    normalized = _normalized(storage_boundaries)

    for phrase in (
        "Default storage should be conservative:",
        "Store source URLs, titles, publication timestamps, source names, "
        "optional local `platform` provenance labels for imported rows, short "
        "summaries, entity matches, tags, counts, and scores.",
        "Avoid storing full article text by default.",
        "Avoid storing original images or videos.",
        "Avoid storing user comments as redistributable assets.",
        "Preserve source links so users can read original content on the source site.",
        "Display source attribution beside representative items.",
        "Add attribution footer to generated reports.",
        "Skip extraction for known paywalled domains unless the source itself provides "
        "permitted metadata.",
    ):
        assert phrase.casefold() in normalized


def test_source_boundaries_docs_keep_readme_requirements_boundary() -> None:
    readme_requirements = _section(
        _read_source_boundaries_doc(),
        "README Requirements",
    )
    normalized = _normalized(readme_requirements)

    for phrase in (
        "The public README must explain:",
        "The project does not provide full social-platform coverage.",
        "Users are responsible for respecting source terms, robots rules, and API terms.",
        "The default workflow avoids account-based collection and access-control bypasses.",
        "Manual signal import is a local input path, not a platform connector or "
        "instructions for obtaining platform exports.",
        "Community handoff check directory reports are local-only handoff readiness reports.",
    ):
        assert phrase.casefold() in normalized


def test_source_boundaries_docs_keep_output_boundary() -> None:
    output_boundaries = _section(
        _read_source_boundaries_doc(),
        "Output Boundaries",
    )
    normalized = _normalized(output_boundaries)

    for phrase in (
        "Reports and dashboards should describe signals, not assert certainty.",
        "Preferred wording:",
        "Mention count increased in this configured source set",
        "Needs human review",
        "Signal changed within this configured local source set",
        "Imported row platform provenance label",
        "Stored local provenance label, not platform coverage",
        "Avoid wording that implies complete market truth:",
        "This source-set signal proves external demand",
        "This celebrity caused the trend",
    ):
        assert phrase.casefold() in normalized


def test_source_boundaries_docs_keep_quality_boundary() -> None:
    quality_boundaries = _section(
        _read_source_boundaries_doc(),
        "Quality Boundaries",
    )
    normalized = _normalized(quality_boundaries)

    for phrase in (
        "Heat scores are local metrics based on configured sources and imported local signals.",
        "They are not rankings outside that local source set.",
        "Candidate signals are observed phrases from configured sources and imported "
        "local signals and need review.",
        "They should not be presented as validated entities.",
        "The dashboard should show:",
        "Source count.",
        "Representative links.",
        "Time window.",
        "Failed source runs.",
        "Missing data warnings.",
        "Whether a source is core, opt-in, or experimental.",
    ):
        assert phrase.casefold() in normalized


def test_source_boundaries_docs_keep_robots_and_fetching_boundary() -> None:
    robots_fetching = _section(
        _read_source_boundaries_doc(),
        "Robots And Fetching",
    )
    normalized = _normalized(robots_fetching)

    for phrase in (
        "Before fetching an article page for extraction, collectors must check robots.txt.",
        "Default fetch behavior:",
        "Use source-specific rate limits where configured.",
        "Record skipped URLs with reasons.",
        "GDELT fetch behavior:",
        "Use bounded exponential backoff.",
        "Store GDELT-provided metadata and links, not republished article bodies.",
    ):
        assert phrase.casefold() in normalized


def test_source_boundaries_docs_limit_minimum_core_to_base_sources() -> None:
    minimum_core = _connector_risk_tier_subsection(
        _read_source_boundaries_doc(),
        "Minimum Core",
    )
    normalized = _normalized(minimum_core)

    for phrase in (
        "gdelt doc api metadata and urls",
        "official rss/atom feeds",
        "rsshub-compatible routes",
        "official rss",
    ):
        assert phrase in normalized, f"missing {phrase!r}"

    for phrase in (
        "html page collection",
        "sitemap discovery",
        "manual signal import",
        "community handoff",
        "xiaohongshu",
        "instagram",
        "twitter/x",
        "youtube",
    ):
        assert phrase not in normalized, f"unexpected {phrase!r}"


def test_source_boundaries_docs_describe_optional_article_extra_collection() -> None:
    article_extra = _connector_risk_tier_subsection(
        _read_source_boundaries_doc(),
        "Optional Article-Extra Collection",
    )
    normalized = _normalized(article_extra)

    for phrase in (
        "html page collection",
        "optional `article` extra",
        "robots.txt",
        "does not crawl or follow links",
        "sitemap discovery",
        "trafilatura.sitemaps",
        "bounded per run",
        "no demand proof and no platform coverage verification",
        "official brand newsroom and press-release html pages, and sitemap pages, "
        "where automated access is allowed.",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"

    for phrase in (
        "manual signal import",
        "community handoff",
        "xiaohongshu (小红书) via xiaohongshu-mcp",
        "instagram via instaloader",
        "twitter/x via twitter-cli",
        "youtube via yt-dlp",
    ):
        assert phrase not in normalized, f"unexpected {phrase!r}"


def test_source_boundaries_docs_describe_local_input_and_community_handoff() -> None:
    local_input_and_handoff = _connector_risk_tier_subsection(
        _read_source_boundaries_doc(),
        "Local Input And Community Handoff",
    )
    normalized = _normalized(local_input_and_handoff)

    for phrase in (
        "manual signal import is a local input path",
        "it is not a connector, platform collector, source pack, or source-acquisition guide.",
        "community signal import is the same local input pattern",
        "`community-handoff-check-dir` is a local-only handoff readiness report",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"

    for phrase in (
        "html page collection",
        "sitemap discovery",
    ):
        assert phrase not in normalized, f"unexpected {phrase!r}"


def test_source_boundaries_docs_describe_opt_in_social_collection() -> None:
    opt_in = _connector_risk_tier_subsection(
        _read_source_boundaries_doc(),
        "Opt-In",
    )
    normalized = _normalized(opt_in)

    for phrase in ("must require explicit user enablement",):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"


def test_source_boundaries_docs_keep_xiaohongshu_opt_in_safety_boundary() -> None:
    xiaohongshu = _bullet_block(
        _connector_risk_tier_subsection(
            _read_source_boundaries_doc(),
            "Opt-In",
        ),
        "Xiaohongshu (小红书) via xiaohongshu-mcp",
    )
    normalized = _normalized(xiaohongshu)

    for phrase in (
        "login-required",
        "qr scan managed by the external tool",
        "use-at-your-own-risk",
        "fashion radar only reads results over its local mcp http endpoint",
        "no demand proof and no platform coverage verification",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"


def test_source_boundaries_docs_keep_instagram_opt_in_safety_boundary() -> None:
    instagram = _bullet_block(
        _connector_risk_tier_subsection(
            _read_source_boundaries_doc(),
            "Opt-In",
        ),
        "Instagram via instaloader",
    )
    normalized = _normalized(instagram)

    for phrase in (
        "login-required",
        "use-at-your-own-risk",
        "the user installs instaloader separately",
        "fashion radar only reuses the saved session (no password handling)",
        "no demand proof and no platform coverage verification",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"


def test_source_boundaries_docs_keep_twitter_opt_in_safety_boundary() -> None:
    twitter = _bullet_block(
        _connector_risk_tier_subsection(
            _read_source_boundaries_doc(),
            "Opt-In",
        ),
        "Twitter/X via twitter-cli",
    )
    normalized = _normalized(twitter)

    for phrase in (
        "logged into x.com in their browser",
        "reads that cookie session",
        "fashion radar only shells out to",
        "it never handles cookies/credentials",
        "use-at-your-own-risk",
        "no demand proof and no platform coverage verification",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"


def test_source_boundaries_docs_keep_youtube_opt_in_safety_boundary() -> None:
    youtube = _bullet_block(
        _connector_risk_tier_subsection(
            _read_source_boundaries_doc(),
            "Opt-In",
        ),
        "YouTube via yt-dlp",
    )
    normalized = _normalized(youtube)

    for phrase in (
        "no login/cookies needed",
        "use-at-your-own-risk",
        "the user installs yt-dlp separately",
        '`yt-dlp "ytsearch<n>:<query>" --dump-json`',
        "parses the metadata",
        "no demand proof and no platform coverage verification",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"

    for phrase in (
        "Opt-in connectors must document",
        "Google News RSS is not included",
    ):
        assert phrase.casefold() not in normalized, f"unexpected {phrase!r}"
