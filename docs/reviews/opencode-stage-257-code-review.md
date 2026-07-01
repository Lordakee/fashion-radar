# Stage 257 Code Review

**Reviewer:** opencode (GLM 5.2 max) — fallback per `docs/REVIEW_PROTOCOL.md`
(Claude Code code review timed out after 180 s; see
`docs/reviews/claude-code-stage-257-code-review.md`).

**Scope:** HTML recent-news windowing, HTML escaping / URL safety, CLI + docs
consistency for the companion HTML report, the optional `buyer-brands` entity
pack quality, and package-archive guard updates.

## Verdict: ACCEPTABLE

The implementation is correct, well-tested, scope-compliant, and addresses
every CRITICAL/IMPORTANT finding from the Stage 257 plan review. No dependency,
`uv.lock`, or scope-boundary regressions. Safe to commit after the one
IMPORTANT non-code hygiene fix below.

Independent verification re-run by this reviewer:

- `pytest tests/test_reports.py::test_render_html_report_includes_recent_items_safely
  tests/test_workflows.py::test_write_daily_report_files_writes_html_with_recent_window_items
  tests/test_entity_packs.py -q` → 20 passed.
- `ruff check` + `ruff format --check` on `workflows.py`, `html_report.py`,
  `cli.py` → clean.
- `git diff --check` → clean.
- `UV_NO_CONFIG=1 uv lock --check` → clean (no lockfile changes).

Full suite (734 passed), release hygiene, and sdist inclusion of the
buyer-brands pack were already run by the implementer and are trusted.

## Critical issues

None.

## Important issues

- **Review-record hygiene for the plan-review artifact.**
  `docs/reviews/opencode-stage-257-plan-review.md` currently opens with
  live-capture narration (lines such as "Let me examine...", "Let me check...",
  "I have full context now..."). `docs/REVIEW_PROTOCOL.md` §Review Capture
  Hygiene and `AGENTS.md` forbid tool-status messages, live-capture stubs, and
  partial narration in committed review records. Strip those narration lines so
  the file opens directly at `## Verdict: ACCEPTABLE WITH REQUIRED CHANGES` and
  contains a single coherent review body. (This is a non-code artifact issue;
  the code itself is fine.)

## Focus-area findings

### 1. HTML recent-news window filtering — CORRECT
`src/fashion_radar/workflows.py:73-90` computes
`window_start = as_of_utc - timedelta(days=scoring.current_window_days)` and
filters with `window_start < collected_at <= as_of_utc` (both bounds, strict
lower / inclusive upper), mirroring the report's `_representative_items`
semantics (`src/fashion_radar/reports.py:479`). `collected_at` is stored as
ISO-8601 `String(64)` UTC strings, and `parse_datetime_utc`
(`src/fashion_radar/utils/dates.py`) always returns UTC-aware datetimes, so the
`.isoformat()` SQL string comparison produces consistent `...+00:00`
fixed-width strings that sort lexicographically. This is the same established
pattern the prune path already relies on
(`src/fashion_radar/db/repositories.py:170-175`). The integration test
correctly asserts future (`> as_of`) and stale (`< window_start`) rows are
excluded and that newest precedes older.

### 2. HTML escaping and unsafe URL behavior — CORRECT
`_render_recent_items` (`src/fashion_radar/html_report.py:179-205`) escapes
title/source/summary via `_esc` and routes URLs through the pre-existing
`_safe_url`, which rejects any scheme outside `http`/`https` (so `javascript:`,
`data:`, `vbscript:` are all dropped — `urlsplit` lowercases the scheme, so
mixed-case variants are covered too) and then applies `escape(..., quote=True)`
so `&` becomes `&amp;` and quotes are safe inside the single-quoted `href`
attribute. Empty URLs render a `news-title-nolink` span instead of an empty
anchor. The dedicated test asserts `&lt;script&gt;` escaping, `&amp;` in a
query string, `target='_blank' rel='noopener'`, and absence of `javascript:`.
`rel='noopener'` is present. No regression risk.

### 3. CLI / docs consistency for companion HTML — CORRECT
The CLI echoes the HTML path in both `report` and `run`
(`src/fashion_radar/cli.py:1442,2222`) using `markdown_path.with_suffix('.html')`,
which equals the actually-written path
`reports_dir / f"fashion-radar-{as_of_utc.date()}.html` because `with_suffix`
replaces only the final `.md`. The `report` docstring and `README.md`,
`docs/architecture.md`, `docs/cli-reference.md`, `docs/first-run.md` all
mention the companion `.html` artifact, and `test_cli.py`
asserts the exact stdout string for the no-digest default. Public return shape
of `write_daily_report_files()` is unchanged (still `(markdown_path,
json_path)`), preserving API compatibility as the plan required.

### 4. Buyer-brands entity pack quality — GOOD
`configs/entity-packs/buyer-brands.example.yaml` uses `safe_single_word: true`
with a reason for genuinely distinctive names (Lemaire, Khaite, Toteme,
Savette, Aeyde, Staffonly, Tibi...) and gates ambiguous/common names with
either `requires_context: true` (Ami Paris, Our Legacy, Acne Studios, Sandy
Liang, Hui) or entity-level `context_terms` (The Row, Joseph, Bode, Pronounce,
Stoffa...). The lint test correctly asserts `result.error_count == 0` (not
`result.ok is True`, exactly as the plan-review nit recommended) plus
`context_gated_aliases > 0`. The matcher test
`test_buyer_brands_matcher_rejects_contextless_common_aliases` verifies that
"Ami joined the dinner.", "Acne is a common skin condition.", "Joseph joined
the meeting.", "The row of seats was empty.", and "Hui Shan was mentioned at
dinner." are all rejected — strong coverage of the false-positive surface.

### 5. Package archive guard updates — CORRECT
The pack is registered in both
`scripts/check_package_archives.py:SDIST_REQUIRED_PATHS` and
`tests/test_package_archives.py:SDIST_FILES`, parallel to the existing
fashion-watchlist entry, so the synthetic fixture and the real sdist check stay
aligned. The implementer confirmed the built sdist contains the file.

### 6. Scope boundaries — MAINTAINED
No connectors, source acquisition, scraping, browser automation, platform
APIs, scheduling, compliance feature, demand proof, ranking semantics, or
coverage verification. The recent-items feature only reads the local SQLite
`items` table; no new collection. The HTML footer retains the "No demand proof
· No platform coverage verification" disclaimer and the section heading is the
neutral "Latest Collected News". No `pyproject.toml` or `uv.lock` changes
(`UV_NO_CONFIG=1 uv lock --check` clean).

## Optional nits

- `_render_recent_items` duplicates the `text[:200] + "..."` truncation idiom
  from the representative-items path. A tiny shared helper would reduce drift
  but is low priority (the plan review already flagged this).
- `_safe_url` does not strip control characters (e.g. `\n`), but with the
  `http`/`https`-only scheme gate plus `quote=True` attribute escaping this is
  not an exploitable vector, and `_safe_url` is a pre-existing helper — not a
  regression of this stage. No action needed.
- Consider pinning the public-facing section label with an exact-equality
  assertion on `<h2>Latest Collected News</h2>` (the current test uses
  substring `in`, which already guards it well enough).

## Missing verification

None. The implementer's verification (734 passed, ruff, release hygiene, sdist
contents, `git diff --check`) is comprehensive for this scope, and the
reviewer independently re-ran the windowing/escaping/entity-pack tests, lint,
and lockfile check.
