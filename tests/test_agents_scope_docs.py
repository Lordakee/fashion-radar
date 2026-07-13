from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DOC = ROOT / "AGENTS.md"


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_agents_scope_boundaries_keep_two_tier_source_contract() -> None:
    scope_boundaries = _section(
        AGENTS_DOC.read_text(encoding="utf-8"),
        "Scope Boundaries",
    )
    normalized = _normalized(scope_boundaries)

    for phrase in (
        "`v0.1.0` minimum core sources are rss/atom, rsshub-compatible feeds, and gdelt",
        "html seed-url collection and sitemap discovery are optional capabilities "
        "provided by the `article` extra",
        "google news rss is not part of `v0.1.0`",
        "social-platform connectors are opt-in",
    ):
        assert phrase in normalized

    assert (
        "core sources are rss/atom, rsshub-compatible, gdelt, html seed-url collection, "
        "and sitemap discovery"
    ) not in normalized
