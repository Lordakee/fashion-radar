# Stage 190 Release Review

## Critical

No critical findings. The Stage 190 `source-liveness` implementation is
read-only and boundary-correct:

- Network probes are bounded to enabled RSS/RSSHub/GDELT sources; disabled
  sources become `skipped` rows with no client creation
  (`src/fashion_radar/source_liveness.py:152-157`).
- Schema-invalid sources (including invalid *disabled* sources) surface as a
  report-level `invalid_config` finding because `load_source_config` validates
  the whole file before per-source iteration (`source_liveness.py:127-146`,
  `tests/test_source_liveness.py:208-238`).
- RSS bytes flow through `BytesIO` so `feedparser` cannot dereference a path/URL
  string (`source_liveness.py:300`), explicitly guarded by
  `test_rss_liveness_parses_fetched_text_without_dereferencing_path_text`
  (`tests/test_source_liveness.py:516-544`).
- GDELT uses `GDELT_DOC_API` + `gdelt_http_settings(source)` +
  `timespan=<lookback_hours>h` + `maxrecords=1` (`source_liveness.py:368-369`,
  `413-420`).
- The CLI prints output before evaluating the exit code, and invalid `--format`
  values are rejected by Typer's `Literal` choice before the builder runs
  (`src/fashion_radar/cli.py:652-668`). Exit semantics match the spec (errors →
  1; warnings → 1 only with `--strict`).
- No writes: the no-artifact CLI test asserts no config/data/report dirs and no
  SQLite (`tests/test_cli.py`), and the spec "no live network tests" rule holds
  (fake clients injected + a module-level `FashionHttpClient` guard).

## Important

- **Stale commit manifest in the plan.** The `git add` list in
  `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md:1466-1491`
  omits five files that are currently modified/untracked and belong to this
  stage. Running Task 5 Step 5 verbatim would produce an **incomplete** commit:

  - `docs/github-upload-checklist.md` (modified — adds `source-liveness` to the
    upload smoke command loop).
  - `docs/reviews/opencode-stage-190-plan-rereview-3-prompt.md` +
    `.../opencode-stage-190-plan-rereview-3.md` (plan rereview #3 artifacts).
  - `docs/reviews/opencode-stage-190-code-rereview-prompt.md` +
    `.../opencode-stage-190-code-rereview.md` (the code rereview that records the
    two Minor findings as resolved).

  Omitting the code-rereview artifact would break the AGENTS.md requirement to
  "Record ... rereview artifacts under `docs/reviews/`" and would leave the
  `github-upload-checklist.md` change dangling (uncommitted) on `main`. Fix
  before committing: stage the full set, e.g. add
  `docs/github-upload-checklist.md` and stage the review trio with
  `git add docs/reviews/opencode-stage-190-*.md`. This is a manifest/process
  fix only — no code, test, or doc content change is required.

## Minor

- `_record_label` is now a one-line pass-through to
  `lint_formatting.format_count_label` (`source_liveness.py:539-540`). This was
  the resolved Minor #2 from the code rereview; keeping it as a domain alias is
  fine, as already noted there. No action required.
- No other minor issues. The prior source-packs.md placement concern is
  resolved (the `## Check Source Liveness` section sits after the
  `source-pack-lint` JSON-shape block at `docs/source-packs.md:88`).

## Verdict

Approve with one Important follow-up. Stage 190 is feature-complete, aligned
with the approved spec/plan, read-only, boundary-correct, and fully tested with
no live network. I independently re-verified the release gate on the working
tree and it is green: focused `source_liveness`/`source_pack_lint` tests → 37
passed; docs tests → 82 passed; `ruff check` clean; `ruff format --check` clean
(146 files); `check_release_hygiene.py` passed; `uv lock --check` passed;
`git diff --check` clean; no `ghp_` tokens and no `extraheader`. Review
artifacts contain completed output with no stubs/truncation/live-capture
markers.

Before merging/pushing, fix the stale `git add` manifest so the commit includes
`docs/github-upload-checklist.md` and all five `docs/reviews/opencode-stage-190-*`
rereview artifacts. Once staged completely, the work is release-ready to merge
and push.
