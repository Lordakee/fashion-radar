from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

ROW_ONE_TEXT_TARGET_PARAGRAPH_CHARS = 140
ROW_ONE_TEXT_DEDUPE_MIN_CHARS = 24
ROW_ONE_SUMMARY_PREFIX_RE = re.compile(
    r"^(?:original source summary|source summary|来源摘要)\s*[:：]\s*",
    re.IGNORECASE,
)
ROW_ONE_TEXT_BOILERPLATE = {
    "read the full story here.",
    "read full story here.",
    "read more.",
    "read more:",
    "阅读全文。",
    "点击查看全文。",
}
ROW_ONE_SENTENCE_RE = re.compile(r"[^.!?。！？]+[.!?。！？]?")
ROW_ONE_LITERAL_ANGLE_RE = re.compile(r"<([A-Za-z][A-Za-z0-9_-]{0,30})>")
ROW_ONE_LITERAL_ANGLE_PLACEHOLDER_RE = re.compile(
    r"__ROW_ONE_LITERAL_ANGLE_([A-Za-z][A-Za-z0-9_-]{0,30})__"
)
ROW_ONE_BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "ol",
    "p",
    "section",
    "table",
    "td",
    "th",
    "tr",
    "ul",
}
ROW_ONE_INLINE_TAGS = {
    "a",
    "abbr",
    "b",
    "bdi",
    "bdo",
    "cite",
    "code",
    "data",
    "dfn",
    "em",
    "i",
    "kbd",
    "mark",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "time",
    "u",
    "var",
}
ROW_ONE_VOID_TAGS = {
    "area",
    "base",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
ROW_ONE_KNOWN_HTML_TAGS = (
    ROW_ONE_BLOCK_TAGS | ROW_ONE_INLINE_TAGS | ROW_ONE_VOID_TAGS | {"script", "style"}
)


class PlainTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1
            return
        if tag in ROW_ONE_BLOCK_TAGS:
            self.parts.append("\n\n")
            return
        if tag in ROW_ONE_INLINE_TAGS or tag in ROW_ONE_VOID_TAGS:
            return

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if tag in ROW_ONE_BLOCK_TAGS:
            self.parts.append("\n\n")
            return
        if tag in ROW_ONE_INLINE_TAGS or tag in ROW_ONE_VOID_TAGS:
            return

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self._ignored_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._ignored_depth:
            self.parts.append(f"&#{name};")

    def text(self) -> str:
        return "".join(self.parts)


def normalize_row_one_paragraph(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_row_one_text(text: str) -> str:
    unescaped = unescape(text)
    parser = PlainTextHTMLParser()
    parser.feed(unescaped)
    parser.close()
    cleaned = parser.text()
    cleaned = ROW_ONE_SUMMARY_PREFIX_RE.sub("", cleaned.strip())
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def clean_row_one_sentences(paragraph: str, seen_sentences: set[str]) -> list[str]:
    cleaned_sentences: list[str] = []
    for raw_sentence in ROW_ONE_SENTENCE_RE.findall(paragraph):
        sentence = normalize_row_one_paragraph(raw_sentence)
        if not sentence:
            continue
        if row_one_sentence_key(sentence) in ROW_ONE_TEXT_BOILERPLATE:
            continue
        dedupe_key = row_one_sentence_key(sentence)
        if len(dedupe_key) >= ROW_ONE_TEXT_DEDUPE_MIN_CHARS:
            if dedupe_key in seen_sentences:
                continue
            seen_sentences.add(dedupe_key)
        cleaned_sentences.append(sentence)
    return cleaned_sentences


def group_row_one_sentences(
    sentences: list[str],
    *,
    target_chars: int = ROW_ONE_TEXT_TARGET_PARAGRAPH_CHARS,
) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    current_chars = 0
    for sentence in sentences:
        projected = current_chars + len(sentence) + (1 if current else 0)
        if current and projected > target_chars:
            paragraphs.append(" ".join(current))
            current = [sentence]
            current_chars = len(sentence)
            continue
        current.append(sentence)
        current_chars = projected
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def row_one_sentence_key(sentence: str) -> str:
    return re.sub(r"\s+", " ", sentence).strip().casefold()


def protect_literal_angle_tokens(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token.casefold() in ROW_ONE_KNOWN_HTML_TAGS:
            return match.group(0)
        return f"__ROW_ONE_LITERAL_ANGLE_{token}__"

    return ROW_ONE_LITERAL_ANGLE_RE.sub(replace, text)


def restore_literal_angle_tokens(text: str) -> str:
    return ROW_ONE_LITERAL_ANGLE_PLACEHOLDER_RE.sub(r"<\1>", text)
