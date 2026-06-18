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
        "No default connector that needs login cookies, proxy pools, CAPTCHA bypass, "
        "or paywall bypass.",
    ):
        assert phrase.casefold() in normalized


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
            "No default connector that needs login cookies, proxy pools, "
            "CAPTCHA bypass, or paywall bypass.",
            "no default connector that needs login cookies, proxy pools, captcha "
            "bypass, or paywall bypass",
        ),
    ):
        assert brief_phrase.casefold() in normalized_brief
        assert readme_phrase in normalized_readme
