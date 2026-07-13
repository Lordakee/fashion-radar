from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_BRIEF_DOC = ROOT / "docs" / "PROJECT_BRIEF.md"
README = ROOT / "README.md"


def _read_project_brief_doc() -> str:
    return PROJECT_BRIEF_DOC.read_text(encoding="utf-8")


def _read_readme() -> str:
    return README.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_project_brief_docs_keep_mvp_non_goals_boundary() -> None:
    non_goals = _section(_read_project_brief_doc(), "Non-Goals For MVP")
    normalized = _normalized(non_goals)

    for phrase in (
        "No paid API requirement.",
        "No account pool.",
        "No proxy pool.",
        "No high-frequency scraping.",
        "No automated posting.",
        "No private user data collection.",
        "No claim that the tool provides full-platform Instagram, TikTok, X, "
        "or Xiaohongshu coverage.",
        "No LLM dependency in the first core pipeline. The first version should work "
        "with deterministic extraction and scoring. Optional LLM summarization can "
        "be added later.",
        "login-based social-platform collection is opt-in and use-at-your-own-risk",
    ):
        assert phrase.casefold() in normalized


def test_project_brief_docs_split_minimum_core_from_optional_article_extra_collection() -> None:
    free_first_boundary = _section(_read_project_brief_doc(), "Free-First Boundary")
    normalized_boundary = _normalized(free_first_boundary)

    minimum_core_marker = "minimum core sources"
    article_extra_marker = "optional article-extra collection"
    optional_sources_marker = "optional sources may require"

    assert minimum_core_marker in normalized_boundary
    assert article_extra_marker in normalized_boundary
    assert optional_sources_marker in normalized_boundary

    minimum_core = normalized_boundary.split(minimum_core_marker, 1)[1].split(
        article_extra_marker,
        1,
    )[0]
    article_extra = normalized_boundary.split(article_extra_marker, 1)[1].split(
        optional_sources_marker,
        1,
    )[0]

    for phrase in (
        "rss/atom",
        "rsshub-compatible",
        "gdelt",
        "official rss",
    ):
        assert phrase in minimum_core

    for phrase in (
        "html",
        "sitemap",
        "newsroom",
        "press-release",
    ):
        assert phrase not in minimum_core

    for phrase in (
        "optional `article` extra",
        "configured public html seed urls",
        "allowed official newsroom/press-release html pages",
        "sitemap discovery",
    ):
        assert phrase in article_extra

    assert "official rss" not in article_extra

    recommended_version = _normalized(
        _section(_read_project_brief_doc(), "Recommended First Public Version"),
    )

    for phrase in (
        "configured html seed urls and sitemap discovery are current optional "
        "`article`-extra v0.1 capabilities.",
        "google news rss, google trends, reddit, and social-platform connectors "
        "should be opt-in post-mvp enhancements unless their authorization and "
        "access boundaries are clear.",
    ):
        assert phrase in recommended_version

    assert "static webpage monitoring" not in recommended_version


def test_readme_keeps_project_brief_mvp_non_goal_parity() -> None:
    readme_non_goals = _section(_read_readme(), "What It Does Not Do")
    brief_non_goals = _section(_read_project_brief_doc(), "Non-Goals For MVP")

    normalized_readme = _normalized(readme_non_goals)
    normalized_brief = _normalized(brief_non_goals)

    for brief_phrase, readme_phrase in (
        ("No paid API requirement.", "no paid api requirement"),
        ("No account pool.", "no account pool"),
        ("No proxy pool.", "no proxy pool"),
        ("No high-frequency scraping.", "no high-frequency scraping"),
        ("No automated posting.", "no automated posting"),
        ("No private user data collection.", "no private user data collection"),
        (
            "No claim that the tool provides full-platform Instagram, TikTok, X, "
            "or Xiaohongshu coverage.",
            "no full-platform instagram, tiktok, x, or xiaohongshu coverage claim",
        ),
        (
            "login-based social-platform collection is opt-in and use-at-your-own-risk",
            "login-based social-platform collection is opt-in and use-at-your-own-risk",
        ),
    ):
        assert brief_phrase.casefold() in normalized_brief
        assert readme_phrase in normalized_readme


def test_project_brief_docs_describe_current_report_outputs() -> None:
    normalized = _normalized(_read_project_brief_doc())

    for phrase in (
        "Generate a daily Markdown/JSON/HTML report.",
        "Markdown, JSON, and companion HTML report generation.",
        "Daily Markdown, JSON, and companion HTML reports.",
    ):
        assert phrase.casefold() in normalized
