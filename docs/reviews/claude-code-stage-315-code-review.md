## Stage 315 Code Review

**No Critical issues found.** One Important issue must be fixed before commit.

---

### Strengths

- **Module purity** — `article_readiness.py` is a frozen-dataclass, no-side-effect module. No networking, no DB imports, no file writes are even possible at import time.
- **Lookup priority** — exact `source_name` match first, hostname fallback second; `safe_external_url` correctly blocks non-HTTP URLs from participating in the fallback.
- **JSON payload stability** — `row_one_article_readiness_payload()` has four fixed top-level keys with int/string leaves. No generated app/manifest/runtime contracts touched.
- **CLI hygiene** — `CONFIG_DIR_OPTION` and `ROW_ONE_OUTPUT_DIR_OPTION` reused, `json_output` avoids shadowing stdlib `json`, `--json` wired correctly.
- **Docs** — README/row-one.md/first-run.md additions describe the platformdirs mismatch accurately with no forbidden implications (no auto-migration, no connector activation, no compliance-review language).

---

### Issues

#### Important — Must Fix Before Commit

**`_source_by_story_url_host` over-filters on `row_one_article.enabled`**

`article_readiness.py:138-143` — the fallback loop has:

```python
if not source.enabled or not source.row_one_article.enabled:
    continue
```

The `row_one_article.enabled` filter should not be here. The plan says the fallback matches against *enabled* sources (`source.enabled=True`); the caller at line 110-116 is already responsible for deciding whether the matched source is article-eligible or just enabled-but-disabled-for-articles.

**Impact on the diagnostic:** A story whose `source_name` doesn't match anything by name, but whose URL hostname matches a `source.enabled=True` / `row_one_article.enabled=False` source, falls through the fallback and lands in `missing_source_count` instead of `disabled_source_count`. This is exactly the platformdirs mismatch scenario the command was built to diagnose — the user sees "missing source" and hunts for a name typo instead of "article extraction disabled" and enables `row_one_article.enabled: true`.

**Fix:**

```python
# Before
for source in sources:
    if not source.enabled or not source.row_one_article.enabled:
        continue

# After
for source in sources:
    if not source.enabled:
        continue
```

**Missing test:** There is no test covering `source_name` mismatch + URL hostname matches an article-disabled enabled source → `disabled_source_count == 1, missing_source_count == 0`. Add it to `test_row_one_article_readiness.py` when fixing.

---

#### Minor — Nice to Have

**1. Unreachable isinstance guards in CLI** (`cli.py` — within `row_one_article_readiness`)

Three `if not isinstance(..., dict): raise typer.Exit(1)` blocks inside the human-readable output path are unreachable — `row_one_article_readiness_payload()` always returns those keys as dicts. They add noise and could mislead future readers into thinking the payload might return non-dict values.

**2. Payload mutation after `row_one_article_readiness_payload()`** (`cli.py:2253-2254`)

```python
payload = row_one_article_readiness_payload(readiness)
payload["config_dir"] = str(config_dir)
payload["site_dir"] = str(site_dir)
```

Fine for the CLI. Worth noting the library function's schema and the JSON output schema are not identical (CLI adds two context keys). Not a bug, but worth a brief comment so future automation consumers know the extra keys are CLI-only.

---

### Specific Question Answers

| # | Question | Answer |
|---|----------|--------|
| 1 | Source eligibility boundary / hostname fallback | **Partially correct** — name-first ordering is right; `safe_external_url` is correct; but the `row_one_article.enabled` filter in the fallback is a deviation (see Important issue above) |
| 2 | Typer wiring (`--config-dir`, `--site-dir`, `--json`) | **Correct** — reuses existing option constants, `json_output` avoids naming collision, command registered as `"article-readiness"` consistently |
| 3 | Truly read-only / no network / no SQLite mutation | **Yes** — reads only `sources.yaml`, sidecar JSON files, and `edition.json`; all wrapped in `OSError`/`JSONDecodeError` handlers |
| 4 | JSON payload stability | **Yes** — stable four-key schema; CLI appends two context-only keys; no app/manifest/runtime contracts affected |
| 5 | Docs explain platformdirs mismatch without forbidden implications | **Yes** — diagnostic framing only; `test_row_one_docs_describe_article_readiness_boundary` checks for forbidden phrases |
| 6 | Missing tests / real risk | **One real gap** — the over-filtering bug has no regression test; the fix should be accompanied by a test for that case |

---

### Assessment

**Ready to merge: With fixes**

One behavioral fix needed (`_source_by_story_url_host` — remove `row_one_article.enabled` filter) plus an accompanying test. Everything else is correct. The fix is two lines; the test is small.
