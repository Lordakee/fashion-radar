# Stage 190 Release Review Prompt

You are reviewing the full Stage 190 release candidate in
`/home/ubuntu/fashion-radar`.

Inspect the current diff from `HEAD` after the code review fixes and full
verification.

Relevant files:

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
- `docs/reviews/opencode-stage-190-code-review.md`
- `docs/reviews/opencode-stage-190-code-rereview.md`

Release questions:

1. Is the Stage 190 feature complete and aligned with the approved plan?
2. Are there any remaining Critical or Important release-blocking issues in the
   code, tests, docs, or review artifacts?
3. Does the release gate evidence support merging and pushing this work?

Known verification already run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then exit 1; fi
```

Return Markdown starting with exactly:

`# Stage 190 Release Review`

Use sections: Critical, Important, Minor, Verdict. If the work is release-ready,
say so explicitly. If not, give concrete blockers with file/line references.
