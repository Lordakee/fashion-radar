from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"
STAGE_391_MUTATION_FREE_CAVEAT = (
    "the mutation-free promise covers only the publisher-owned row one site output parent "
    "and publisher transaction artifacts. `row-one refresh` may already have collected, "
    "matched, and stored data and written the current dated report before site publication "
    "reaches the capability gate. the gate does not skip or roll back that completed source, "
    "sqlite, and report work."
)
STAGE_391_UNSUPPORTED_PLATFORM_CAVEAT = (
    "unsupported platforms fail before creating output or transaction artifacts. "
    + STAGE_391_MUTATION_FREE_CAVEAT
)


def _read_architecture_doc() -> str:
    return ARCHITECTURE_DOC.read_text(encoding="utf-8")


def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    assert marker in f"\n{text}"
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _component_item(text: str, component: str) -> str:
    marker = f"- **{component}:**"
    assert marker in text
    item_and_rest = text.split(marker, 1)[1]
    assert "\n- **" in item_and_rest
    return marker + item_and_rest.split("\n- **", 1)[0]


def test_architecture_source_boundary_keeps_tiered_scope_and_local_import_limits() -> None:
    section = _markdown_section(_read_architecture_doc(), "## Source Boundary")
    normalized = _normalized(section)

    for phrase in (
        "the minimum core collector set is rss, rsshub-compatible feeds, and gdelt",
        "html seed-url collection and sitemap discovery are optional `article`-extra collectors",
        "manual signal import is a local input path",
        "user-provided csv/json files",
        "not a connector or platform collector",
        (
            "opt-in social-platform collection (phase 2-5: xiaohongshu, "
            "instagram, twitter/x, youtube) is use-at-your-own-risk"
        ),
        "source-boundaries.md",
    ):
        assert phrase in normalized

    assert (
        "the core collector set is rss, rsshub-compatible feeds, gdelt, html "
        "seed-url collection, and sitemap discovery"
    ) not in normalized


def test_architecture_describes_stage_391_recoverable_latest_only_publish() -> None:
    components = _markdown_section(_read_architecture_doc(), "## Components")
    row_one_component = _component_item(components, "ROW ONE")
    normalized = _normalized(row_one_component)

    for phrase in (
        "failure-safe recoverable publish",
        "latest_only=true",
        "same-filesystem staging site",
        "recoverable latest-only publication requires safe directory-relative filesystem "
        "operations",
        "current standard windows python lacks the safe directory-handle capability for "
        "recoverable latest-only",
        "unsupported platforms fail before creating output or transaction artifacts",
        "`row one safe directory handles are unsupported on this platform`",
        "before creating the output parent, lock, journal, stage, backup, or owner marker",
        "before invoking render",
        "never falls back to delete-and-render",
        "feature-level boundary",
        "package remains os-independent",
        "ordinary non-latest build and preview rendering remains available",
        "`row-one refresh` is latest-only and therefore fails at this gate on unsupported "
        "platforms",
        "same-filesystem backup and journal paths",
        "stable sibling lock file",
        "recovers an interrupted owned transaction before the next latest-only render",
        "preserves unrelated top-level output children",
        "keeps the public output path, generated urls, and result paths unchanged",
        "short live-path gap",
        "not fully atomic",
        "does not claim zero-downtime publication or power-loss durability",
    ):
        assert phrase in normalized

    assert (
        normalized.count("does not claim zero-downtime publication or power-loss durability") == 1
    )
    assert STAGE_391_UNSUPPORTED_PLATFORM_CAVEAT in normalized
    assert STAGE_391_MUTATION_FREE_CAVEAT in normalized
    assert normalized.count(STAGE_391_MUTATION_FREE_CAVEAT) == 1
    for redundant_phrase in (
        "does not promise zero downtime",
        "does not guarantee universal power-loss durability",
    ):
        assert redundant_phrase not in normalized
