Review the Stage 120 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Document and test local opencode review capture hygiene so committed review
  artifacts contain completed review output rather than live-capture stubs,
  tool/status telemetry, duplicated verdicts, or empty output.
- Keep the node docs/tests-only and forward-looking; do not rewrite historical
  review artifacts outside Stage 120.

Files changed:
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/github-upload-checklist.md`
- `tests/test_review_protocol_docs.py`
- `docs/superpowers/specs/2026-06-20-stage-120-opencode-review-capture-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-120-opencode-review-capture-hygiene-plan.md`
- `docs/reviews/opencode-stage-120-plan-review-prompt.md`
- `docs/reviews/opencode-stage-120-plan-review.md`
- `docs/reviews/opencode-stage-120-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-120-plan-rereview.md`

Plan review artifacts:
- `docs/reviews/opencode-stage-120-plan-review.md`
- `docs/reviews/opencode-stage-120-plan-rereview.md`

Verification already run:
- RED: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q`
  failed as expected because `docs/REVIEW_PROTOCOL.md` had no
  `## Review Capture Hygiene` section.
- GREEN: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q`
  passed with `3 passed`.
- Adjacent docs tests: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q`
  passed with `64 passed`.
- Focused lint: `uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py`
  passed.
- Focused format: `uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py`
  passed.

Review focus:
1. Does the implementation match the reviewed Stage 120 design and plan?
2. Does `tests/test_review_protocol_docs.py` meaningfully guard the opencode
   review capture hygiene contract across protocol and upload docs, and the
   `AGENTS.md` bullet?
3. Do the active `docs/REVIEW_PROTOCOL.md` opencode examples avoid direct
   final-file redirection into `docs/reviews/opencode-stage-N-...` paths?
4. Are the Stage 120 review artifacts themselves coherent completed review
   records without live-capture stubs, `Wrote`/`Review written to` status lines,
   or obvious garbled text?
5. Does the implementation remain docs/tests-only, with no runtime, dependency,
   `uv.lock`, CI, connector, scraping, scheduling, monitoring, source
   acquisition, ranking, coverage verification, or compliance/audit product
   behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
