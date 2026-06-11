from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from robotexclusionrulesparser import RobotExclusionRulesParser


class RobotsResponse(Protocol):
    status_code: int
    text: str


class RobotsFetcher(Protocol):
    def __call__(self, url: str) -> RobotsResponse: ...


@dataclass(frozen=True)
class _RobotsRules:
    parser: RobotExclusionRulesParser | None


class RobotsPolicyChecker:
    def __init__(self, fetcher: RobotsFetcher) -> None:
        self._fetcher = fetcher
        self._cache: dict[tuple[str, str], _RobotsRules] = {}

    def can_fetch(self, url: str, user_agent: str) -> bool:
        parsed_url = urlsplit(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False

        rules = self._rules_for(parsed_url.scheme, parsed_url.netloc)
        if rules.parser is None:
            return False

        try:
            return rules.parser.is_allowed(user_agent, url)
        except Exception:
            return False

    def _rules_for(self, scheme: str, netloc: str) -> _RobotsRules:
        cache_key = (scheme.lower(), netloc.lower())
        if cache_key not in self._cache:
            self._cache[cache_key] = self._fetch_rules(scheme, netloc)
        return self._cache[cache_key]

    def _fetch_rules(self, scheme: str, netloc: str) -> _RobotsRules:
        robots_url = urlunsplit((scheme, netloc, "/robots.txt", "", ""))
        try:
            response = self._fetcher(robots_url)
        except Exception:
            return _RobotsRules(parser=None)

        if response.status_code != 200:
            return _RobotsRules(parser=None)

        try:
            lines = response.text.splitlines()
            if not _looks_like_robots_txt(lines):
                return _RobotsRules(parser=None)
            parser = RobotExclusionRulesParser()
            parser.parse(response.text)
        except Exception:
            return _RobotsRules(parser=None)

        return _RobotsRules(parser=parser)


def _looks_like_robots_txt(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        field = stripped.split(":", 1)[0].strip().lower()
        if field in {"user-agent", "allow", "disallow", "sitemap", "crawl-delay"}:
            return True
    return False
