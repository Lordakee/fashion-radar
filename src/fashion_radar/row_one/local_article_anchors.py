from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

LOCAL_ARTICLE_SECTION_ANCHOR = "local-article"
LOCAL_ARTICLE_BODY_CONTAINER_ANCHOR = "local-article-body"
LOCAL_ARTICLE_PARAGRAPH_ANCHOR_PREFIX = "local-article-paragraph-"
LOCAL_ARTICLE_CONTENT_SECTION_ANCHOR_PREFIX = "local-article-content-section-"


def local_article_paragraph_anchor(index: int) -> str:
    return f"{LOCAL_ARTICLE_PARAGRAPH_ANCHOR_PREFIX}{index + 1}"


def local_article_content_section_anchor(position: int) -> str:
    return f"{LOCAL_ARTICLE_CONTENT_SECTION_ANCHOR_PREFIX}{position}"


def parse_html_ids(html: str) -> set[str]:
    parser = _IdCollectingHTMLParser()
    parser.feed(html)
    return parser.ids


def html_ids(path: Path) -> set[str]:
    try:
        return parse_html_ids(path.read_text(encoding="utf-8"))
    except OSError:
        return set()


class _IdCollectingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name.lower() == "id" and value is not None:
                self.ids.add(value)
