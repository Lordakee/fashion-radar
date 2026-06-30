# Stage 252 Plan Review

**Verdict:** REQUEST_CHANGES

## Critical

**1. `search_prefix` configuration ignored in subprocess design**
`YouTubeSourceSettings.search_prefix` allows `"ytsearch"` or `"ytsearchdate"` but the plan hardcodes `"ytsearch<N>:<query>"` in the subprocess argv construction. The implementation must use `f"{settings.search_prefix}{settings.max_videos_per_run}:{source.query}"` to respect the user's configured prefix (date-sorted vs relevance-sorted results).

**2. `upload_date` YYYYMMDD parse order is backwards**
Plan says "try parse_datetime_utc, then manual YYYYMMDD slice" but yt-dlp's documented `upload_date` format IS `YYYYMMDD` (stable, not a fallback). Trying `parse_datetime_utc` first on `"20240615"` will fail since it expects ISO8601. Correct order: (1) `datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=UTC)`, (2) fallback to `started_at` on parse error. Or add fallback to `parse_datetime_utc` for robustness, but YYYYMMDD must be first.

## Important

**3. JSON-lines parse pattern differs from Twitter reference**
Plan correctly identifies yt-dlp emits "one JSON object per line" but the reference `twitter.py:97-111` uses `json.loads(stdout)` on the entire blob. YouTube implementation needs explicit line-by-line parsing:
```python
for line in stdout.strip().splitlines():
    try:
        video = json.loads(line)
        # process video dict
    except json.JSONDecodeError:
        continue  # skip malformed lines
```
The plan should clarify this divergence from the Twitter pattern.

## Nits

**4. Timeout handling not explicit**
Plan mentions "bounded timeout" but doesn't specify where it comes from. Twitter uses `source.http.timeout_seconds` (twitter.py:54, 88). YouTube should follow the same pattern for consistency.

**5. Task 1 test coverage missing upload_date edge cases**
Plan lists "published_at from upload_date + fallback" but doesn't explicitly call out testing malformed YYYYMMDD strings (e.g., `"20241399"`, `""`, `None`). Given the manual parse path, add explicit edge case coverage.

## Summary

Core architecture (subprocess + injectable runner + fail-closed + report_safe_snippet + bounding) is sound and correctly mirrors Twitter Stage 242. Three blockers: (1) missing `search_prefix` configuration usage, (2) inverted upload_date parse order (YYYYMMDD is primary format, not fallback), (3) JSON-lines parse implementation needs clarification since it differs from Twitter's single-blob approach. Fix these and the plan is solid for Stage 252.
