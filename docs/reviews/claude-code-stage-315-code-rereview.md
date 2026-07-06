**Prior Important issue: Fixed.**

`_source_by_story_url_host()` (`article_readiness.py:138-143`) now loops with only `if not source.enabled: continue` — the `row_one_article.enabled` guard is gone. The caller at lines 118-121 correctly classifies the matched source as eligible or disabled. The regression test `test_article_readiness_counts_host_matched_article_disabled_source_as_disabled` directly covers the platformdirs-mismatch scenario (name miss + URL hostname match + `row_one_article.enabled=False` → `disabled_source_count=1`, `missing_source_count=0`). All137 tests pass.

No new Critical or Important issues.

---

**Minor items** (carried from the original review, not introduced by the fix):

1. **Unreachable isinstance guards in CLI** — the three `if not isinstance(..., dict): raise typer.Exit(1)` blocks in the human-readable output path of `row_one_article_readiness` are dead code; `row_one_article_readiness_payload()` always returns those keys as dicts. Low noise risk, but they could mislead future readers.

2. **CLI-only keys on the payload** — `payload["config_dir"]` and `payload["site_dir"]` are appended after `row_one_article_readiness_payload()` returns. A short inline comment marking those as CLI-context-only would prevent a future consumer from treating them as part of the library schema.

Both are genuinely nice-to-have; neither affects correctness. **Ready to merge.**
