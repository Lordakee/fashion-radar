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


def test_source_boundaries_docs_describe_html_page_collection() -> None:
    core_section = _section(_read_source_boundaries_doc(), "Core")
    normalized = _normalized(core_section)

    for phrase in (
        "html page collection",
        "trafilatura",
        "optional `article` extra",
        "robots.txt",
        "does not crawl or follow links",
    ):
        assert phrase.casefold() in normalized, f"missing {phrase!r}"
