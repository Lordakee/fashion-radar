# opencode Stage 260 Code Rereview

Reviewer: opencode (GLM 5.2 max), fallback rereviewer after post-review fixes
Stage: 260 (ROW ONE daily site)
Scope: final uncommitted Stage 260 ROW ONE diff and post-review fixes

## Verdict

Accept.

All six post-review fixes are correctly implemented, tested, and consistent with
the reported fresh verification. The reviewer independently confirmed all 45
ROW ONE tests passed.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

- The URL-safety helper is duplicated as `_safe_url` in
  `src/fashion_radar/row_one/edition.py` and `_safe_external_url` in
  `src/fashion_radar/row_one/templates.py` with identical logic. This is
  acceptable defense-in-depth because JSON output re-sanitizes already sanitized
  values idempotently, but the duplication could drift over time.

## Verification Of Required Fixes

1. Serve marker: `_validate_site_dir` requires both `.row-one-site` and
   `index.html`; `create_row_one_http_server` calls it; the unmarked-directory
   regression test confirms the behavior. Dry-run intentionally skips
   validation, consistent with print-only URL semantics.
2. Top-story backfill: `_top_stories` iterates recent items until the limit and
   skips duplicates with `add_story`; the regression test proves it fills to six
   stories after duplicate entity and candidate stories collapse.
3. Detail-path safety: `_validated_detail_relative_path` and
   `_DETAIL_FILENAME_RE` reject absolute paths, `..`, extra parts, encoded
   separators, control characters, and malformed names while accepting generated
   ASCII slug/hash paths.
4. JSON URL sanitization: `_sanitized_edition_payload` applies the same
   `http`/`https` plus `netloc` gate used by HTML rendering to story
   `source_url` and evidence URLs.
5. Review-artifact hygiene: Stage 260 review records are coherent opencode
   artifacts with no incomplete primary-review stubs, raw tool traces, or ANSI
   garbage.
6. Plan/spec wording: the plan task list is complete, and the spec/plan state
   default `127.0.0.1` serving with explicit `0.0.0.0` LAN opt-in.

## Prior Findings

Resolved:

- Serving arbitrary directories that only contain `index.html`.
- Top-story underfill after duplicate entity/candidate stories collapse.
- Detail-path acceptance of encoded separators and control-character filenames.
- Raw unsafe URLs in `data/edition.json`.
- Stage 260 review artifact unavailable-review stubs and stale plan/spec wording.

Accepted as non-blocking:

- `row-one serve --dry-run` prints access guidance without validating the site
  directory.
- `row-one schedule` supports cron and systemd but not GitHub Actions mode.
- The recent-items SQL query is duplicated between daily report generation and
  ROW ONE generation.
- The defensive section-title fallback in templates uses an unusual but
  effectively unreachable construction.

## Recommended Next Action

Proceed to commit the Stage 260 work and advance to the next stage. No fixes are
required for this node.
