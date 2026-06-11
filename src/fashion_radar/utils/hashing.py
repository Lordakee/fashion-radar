from __future__ import annotations

import hashlib
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fashion_radar.extract.text import normalize_text
from fashion_radar.utils.dates import parse_datetime_utc

TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "msclkid",
    "ref",
    "ref_src",
}
TRACKING_PREFIXES = ("utm_",)


def normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    query_pairs = []
    for key, raw_value in parse_qsl(parts.query, keep_blank_values=True):
        normalized_key = key.lower()
        if not raw_value:
            continue
        if normalized_key in TRACKING_PARAMS:
            continue
        if any(normalized_key.startswith(prefix) for prefix in TRACKING_PREFIXES):
            continue
        query_pairs.append((key, raw_value))

    query = urlencode(sorted(query_pairs, key=lambda pair: (pair[0].lower(), pair[1])))
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path,
            query,
            "",
        )
    )


def content_hash(
    *,
    title: str,
    published_at: str | datetime,
    source_name: str,
    summary: str | None = None,
) -> str:
    published = parse_datetime_utc(published_at).isoformat()
    payload = "\x1f".join(
        [
            normalize_text(title),
            published,
            normalize_text(source_name),
            normalize_text(summary or ""),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
