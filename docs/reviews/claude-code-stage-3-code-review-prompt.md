# Claude Code Stage 3 Code Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 3 implementation.

Repository: `/home/ubuntu/fashion-radar`

Commit under review:

- `ac23386 feat: add stage 3 public collectors`

Reviewed range:

- `749f263..ac23386`

Stage 3 requirements:

- Public collectors for RSS/Atom and GDELT.
- Google News RSS remains rejected for `v0.1.0`.
- Collector interfaces return normalized `CollectedItem` objects and structured
  run status without direct SQLite writes.
- A serial coordinator persists items through `ItemRepository` only; no parallel
  database writers.
- SQLite schema version bumps from `1` to `2`.
- A version-1 database migrates to version 2 without dropping existing items.
- New collector status and source health tables are persisted.
- Repeated failures mark a source unhealthy and unhealthy sources are skipped
  until retention expiry or direct database reset.
- Shared HTTP client owns User-Agent, timeout, bounded retries, and per-domain
  politeness delay.
- GDELT uses the public Doc API endpoint
  `https://api.gdeltproject.org/api/v2/doc/doc`.
- GDELT uses the configured source query, lookback window, max records, and
  conservative rate-limit-derived delay.
- RSS and GDELT items use the same URL normalization and
  `ItemRepository.upsert_item()` path.
- Article extraction checks robots.txt, caches robots rules per domain within a
  run, skips disallowed or unavailable robots, skips configured paywalled
  domains, and stores only a short snippet/result.
- Full article storage, login-cookie scraping, paywall bypass, CAPTCHA bypass,
  proxy pools, and social-platform scraping remain out of scope.

Implementation notes:

- `feedparser`, `httpx`, `robotexclusionrulesparser`, and `tenacity` are core
  dependencies.
- `trafilatura` is in the optional `article` extra rather than the core install.
  Reason: both Tsinghua and Aliyun mirror installs repeatedly timed out on the
  heavier parser dependency stack (`lxml`/`babel`) during local verification.
  The article wrapper safely returns `extractor_unavailable` when trafilatura is
  absent. Please review whether this is acceptable for v0.1.0 or should be
  treated as an important plan deviation.

Fresh local verification already run:

```text
.venv/bin/python -m pytest -q
79 passed in 1.03s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
46 files already formatted

uv lock --check
Resolved 84 packages in 1ms

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build
Successfully built dist/fashion_radar-0.1.0.tar.gz
Successfully built dist/fashion_radar-0.1.0-py3-none-any.whl

Clean temporary venv wheel install via Tsinghua mirror:
fashion-radar --help displayed init and doctor commands
```

Please review:

1. Does implementation satisfy Stage 3 acceptance criteria?
2. Are there correctness bugs, data-integrity risks, or migration risks?
3. Are HTTP retry/politeness and GDELT request semantics safe and testable?
4. Are robots/article extraction boundaries conservative enough?
5. Are source/compliance boundaries preserved?
6. Are tests meaningful and sufficient for this stage?
7. Is the `trafilatura` optional-extra deviation acceptable?
8. Are there issues to fix before Stage 4?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 4 plan review
- Approved after fixes
- Do not proceed
