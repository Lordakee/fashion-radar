Here are my findings after reading both documents and verifying against the live codebase.

---

## Critical

### C1 — `test_first_run_docs.py` phrase mismatch will cause an immediate test failure

**Location:** Plan Task 3 Step 2 (test guard) vs. Task 3 Step 3 (docs text)

The test guard requires this exact substring in `docs/first-run.md`:

```python
"does not require live article sidecars",
```

But the proposed docs paragraph in Task 3 Step 3 says:

```md
so it does not require saved article sidecars.
```

`"live"` ≠ `"saved"`. The test will fail because `"does not require live article sidecars"` is not a substring of the proposed text. This must be reconciled before implementation. Either:

- Change the docs text to `"does not require live article sidecars"`, or
- Change the test guard to `"does not require saved article sidecars"`.

The second option is slightly more accurate (the sidecars are *saved* local files), but either works — they just have to match.

---

## Important — None

After cross-checking with the codebase, no other blocking issues were found:

- **Starter config already has `row_one_article.enabled: true` on all RSS sources** — confirmed via `configs/sources.example.yaml`. The new `test_config.py` guards (`assert any(...)` and `assert all(... if type == "rss")`) will pass without a config update step.
- **`edition.json` stories include `source_name`** — confirmed in `render.py:1023`: `"source_name": story.source_name` is written to the serialized edition payload. The `_story_coverage` source-name lookup is valid.
- **Case-sensitive source-name matching is consistent with `articles.py:685`**: `if source.name == story.source_name:` — exact same pattern. No divergence.
- **`_render_status_site_with_local_article` and `_write_minimal_config` helpers exist** in `tests/test_row_one_cli.py` and cover the test scenarios correctly. The 1-article/2-paragraph/1-story site plus empty sources list produces the expected counts.
- **No naming collision** with existing `row_one/readiness.py` (`RowOneReadiness`) — the new module is `article_readiness.py` with `RowOneArticleReadiness`. Clean.
- **All CLI imports (`CONFIG_DIR_OPTION`, `ROW_ONE_OUTPUT_DIR_OPTION`, `ConfigError`, `load_source_config`, `build_row_one_local_article_site_metrics`, `row_one_local_article_site_metrics_payload`) are already present** in `cli.py`. The plan only adds two new names from the new module.

---

## Minor / Nit

**M1 — No test for `ConfigError` path on missing `sources.yaml`**

The plan includes no test for `row-one article-readiness` when the config directory doesn't contain `sources.yaml`. The `except ConfigError` branch in the command implementation would go untested. Low risk (the error path is structurally identical to other commands), but worth noting.

**M2 — `test_row_one_docs_describe_local_article_observability_boundary` update is described in prose, not code**

Task 3 Step 2 says "update the test so the Stage 314 slice ends at `'Stage 315 adds'` instead of `'Stage 310 adds'`" and "then add a Stage 315 slice test." This leaves the exact sentinel logic implicit. A literal reader might alter the wrong sentinel or duplicate the end marker. Suggest spelling out the final assertion shape in the plan (like the other tasks do).

**M3 — Text output silently omits `organized_section_count` and `source_count`**

The human-readable output shows `article_count` and `paragraph_count` but not `organized_section_count` or `source_count` from `RowOneLocalArticleSiteMetrics`. This is a deliberate scope choice and not a bug (JSON mode includes all fields), but it means a user running text mode gets less diagnostic signal on structured content. Acceptable for Stage 315.

**M4 — Design doc dataclass signatures omit default values; implementation adds them**

The design doc shows:

```python
@dataclass(frozen=True)
class RowOneArticleReadinessSourceSummary:
    total_sources: int
    enabled_sources: int
    article_enabled_sources: int
```

The plan's implementation adds `= 0` defaults. The defaults are necessary for `RowOneLocalArticleSiteMetrics()` call patterns used in tests. No action needed — the implementation is correct; the design doc is just slightly loose.

---

## Summary

One Critical fix required before implementation: reconcile the `"does not require live article sidecars"` test phrase with the `"does not require saved article sidecars"` docs text. Fix is a one-word change in either the test or the docs.

No Important findings. The analyzer semantics, Typer wiring, JSON payload shape, test helper reuse, config guard, and scope boundary are all sound.
