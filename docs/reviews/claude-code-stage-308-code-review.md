I now have a complete picture of all changed files. Here is the review.

---

## Verdict

**Approve with Important fixes.**

The Stage 308 integrity validator is architecturally correct, read-only, and the JSON contracts are untouched. The smoke helper is properly non-blocking, uses0.1s inter-poll sleep, avoids content-level asset assertions, and the port race is handled with three retries. The two important issues below are fixable without architecture changes.

---

## Critical Findings

None.

---

## Important Findings

**1. `assert` instead of `raise` for a reachable invariant — `status_integrity.py:322`**

```python
if item.paragraph_indices:
    assert story_id is not None# ← line 322
```

The `assert` is logically safe today (the only way to reach line 321 with `paragraph_indices` truthy is via the `if item.detail_path:` branch, which either raises or sets `story_id`). But `assert` statements are silently elided under `python -O`, and every other invariant guard in this module uses an explicit `raise ValueError`. This inconsistency means a future refactor that introduces a new code path could produce a silent `None`-dereference at line 326 (`article_sidecars.get(story_id)`) instead of a clear error. The rest of the module is exemplary about this; this line should match.

Fix:
```python
if item.paragraph_indices:
    if story_id is None:
        raise ValueError(f"row-one {label}.paragraph_indices require a resolved story_id")
```

**2. Segment-level `paragraph_indices` validation is implemented but completely untested — `status_integrity.py:354–384`, `tests/test_row_one_cli.py`**

`_validate_local_intelligence_segment_item` validates `paragraph_indices` inside `item.segments[].items[]`. The plan explicitly requires: "For each item and nested segment item: validate every `paragraph_indices[]` entry against the same sidecar paragraph list." The generated `reports/row-one/site/data/local-intelligence.json` does contain items with `segments` (the plan's Task5 Step 2verifies `any(item.get("segments") for ...)`). No test mutates a segment-item's `paragraph_indices` to an out-of-range value or removes a HTML anchor it references. If this path contains a bug it will not be caught.

Fix: add two tests to `test_row_one_cli.py`:

```python
def test_row_one_status_rejects_local_intelligence_segment_missing_paragraph_index(
    tmp_path: Path,
) -> None:
    _render_status_site_with_local_article(tmp_path)
    local_intelligence_path = tmp_path / "data" / "local-intelligence.json"
    payload = json.loads(local_intelligence_path.read_text(encoding="utf-8"))
    # Find a section with segments or inject one
    for section in payload:
        for item in section.get("items", []):
            if item.get("segments"):
                item["segments"][0]["items"][0]["paragraph_indices"] = [99]
                break
    local_intelligence_path.write_text(json.dumps(payload), encoding="utf-8")
    result = CliRunner().invoke(app, ["row-one", "status", "--site-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "paragraph_indices" in result.output
```

If the rendered site does not produce segment items, use the `_render_status_site_with_local_article` fixture to inject a hand-crafted `local-intelligence.json` containing a segment item and assert that a bad index is rejected.

---

## Minor Findings

**1. `raising=False` on the `run_row_one_local_http_serve_smoke` monkeypatch — `tests/test_first_run_smoke.py:5294`**

```python
monkeypatch.setattr(
    smoke,
    "run_row_one_local_http_serve_smoke",
    fake_run_row_one_local_http_serve_smoke,raising=False,   # ← should be True (or omitted; True is the default)
)
```

`raising=False` means that if `run_row_one_local_http_serve_smoke` is ever renamed or removed from the module, the patch silently creates a new orphan attribute that nothing in `run_first_run_flow` calls. The `assert local_http_smokes == [(context, ...)]` would then fail with an empty list — but the failure message would be confusing and the test would not clearly point to the rename. With the default `raising=True`, pytest would immediately raise `AttributeError: smoke has no attribute 'run_row_one_local_http_serve_smoke'`, which is unambiguous.

Fix: remove `raising=False`.

**2. Test name says "anchor" but exercises the paragraph-index-range check — `tests/test_row_one_cli.py:1361`**

`test_row_one_status_rejects_local_intelligence_missing_paragraph_anchor` sets `paragraph_indices = [99]`. The validator rejects this at `_validate_paragraph_indices` ("references a missing rendered paragraph: 99") — the HTML anchor check (`_require_html_anchor`) is never reached. The test for the actual missing-anchor path is the correctly-named `test_row_one_status_rejects_local_intelligence_missing_rendered_anchor` at line 1376. The naming inconsistency does not affect correctness, but it makes it harder to reason about what is covered.

Fix: rename line 1361's test to `test_row_one_status_rejects_local_intelligence_out_of_range_paragraph_index`.

**3. No test for article sidecar `content_sections[].items[].paragraph_indices` out-of-range — `status_integrity.py:238–247`**

`_validate_article_paragraphs` calls `_validate_paragraph_indices` on each content-section item's `paragraph_indices`. There is no test that injects an article sidecar with an out-of-range index there. The test `test_row_one_status_rejects_article_sidecar_story_id_mismatch` covers the sidecar rejection path, but not this specific sub-check.

Fix: add a test that writes a sidecar file with `content_sections[0].items[0].paragraph_indices: [99]` and asserts `exit_code == 1` and `"paragraph_indices"` in output.

**4. `source_names` vs `source_name` cross-check is untested — `status_integrity.py:314–317`**

```python
if item.source_name and item.source_names and item.source_name not in item.source_names:
    raise ValueError(...)
if item.source_names and article.source_name not in item.source_names:
    raise ValueError(...)
```

These two guards are not exercised by any test. They are reachable only when a local-intelligence item has `detail_path` set, which requires a fixture with a sidecar. These are non-trivial constraints and should be covered.

Fix: add a test that sets `source_names` to a list that excludes the article's `source_name` and asserts rejection.

**5. `_stop_row_one_serve_process` uses `process.wait()` with pipes open — `scripts/check_first_run_smoke.py:3117–3125`**

The process is started with `stdout=subprocess.PIPE, stderr=subprocess.PIPE`. `_stop_row_one_serve_process` calls `process.terminate()` then `process.wait(timeout=5)` without draining the pipes. For the early-exit path, `_raise_row_one_serve_exited` correctly uses `process.communicate()`, which drains. For the normal-stop path, if the server writes enough to fill the OS pipe buffer before termination, `wait()` would deadlock. In practice the ROW ONE HTTP server is silent after startup, so this is harmless in the current implementation, but it is a known subprocess hazard worth a comment or an `communicate(timeout=…)` call.

Fix (optional): replace `process.wait(timeout=5)` with `process.communicate(timeout=5)` in `_stop_row_one_serve_process`, or add a comment explaining why no drain is needed.

---

**No schema/contract drift found.** `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1` are unchanged. The new integrity validator only reads files; it does not write or publish anything. The smoke changes do not alter any contract constant or compliance surface. The docs correctly describe the read-only constraint and explicitly forbid the forbidden phrases (`row-one-app/v8`, `status rebuilds the site`, etc.).
