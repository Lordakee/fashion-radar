# Stage 190 Code Review Prompt

You are reviewing the current uncommitted Stage 190 implementation in
`/home/ubuntu/fashion-radar`.

Please inspect the diff from `HEAD` and the relevant files:

- `src/fashion_radar/source_liveness.py`
- `src/fashion_radar/cli.py`
- `tests/test_source_liveness.py`
- `tests/test_cli.py`
- `tests/test_source_packs_docs.py`
- `tests/test_source_pack_quality_docs.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/architecture.md`
- `docs/source-packs.md`
- `docs/source-pack-quality.md`
- `docs/cli-reference.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`

Review against the approved Stage 190 goal:

- Add `fashion-radar source-liveness PATH --format table|json [--strict]`.
- Keep it read-only: no SQLite, no artifacts, no report writes, no source-health
  mutation, no article-page fetching, no matching/scoring/collection.
- Probe only enabled `rss`, `rsshub`, and `gdelt` sources; include schema-valid
  disabled sources as skipped rows without network calls.
- RSS/RSSHub must parse only fetched response bytes and must not let
  `feedparser` dereference URL/path strings.
- GDELT must use `GDELT_DOC_API`, `gdelt_http_settings(source)`,
  `timespan=<lookback_hours>h`, and `maxrecords=1`.
- CLI must print output before exit-code evaluation; errors exit 1; warnings
  exit 1 only with `--strict`; invalid format must not call the builder.
- Tests must not perform live network access.

Known focused verification already run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest tests/test_source_liveness.py tests/test_cli.py -q -k "source_liveness or source_pack_lint"
uv --no-config run --frozen pytest tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/source_liveness.py src/fashion_radar/cli.py tests/test_source_liveness.py tests/test_cli.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/source_liveness.py src/fashion_radar/cli.py tests/test_source_liveness.py tests/test_cli.py tests/test_source_packs_docs.py tests/test_source_pack_quality_docs.py tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Return Markdown starting with exactly:

`# Stage 190 Code Review`

Use sections: Critical, Important, Minor, Verdict. Include file/line references
for every finding. If there are no Critical or Important findings, say so.
