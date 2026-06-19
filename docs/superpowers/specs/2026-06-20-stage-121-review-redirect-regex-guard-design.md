# Stage 121 Review Redirect Regex Guard Design

## Goal

Harden the review protocol docs drift test so it catches direct shell
redirection from `opencode run` into final `docs/reviews/opencode-stage-N-...`
review records, including common variants that the current literal substring
checks miss.

## Reviewer Context

This design is for local opencode review before implementation. Use the Stage
120 temporary-capture workflow for review artifacts:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-121-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-121-plan-review.md
rm -f "$tmp_review"
```

## Background

Stage 120 added review capture hygiene docs and replaced direct final-file
redirection examples with a temporary-capture workflow. The Stage 120 code
review left one non-blocking Minor: the tests only assert that two exact
substrings are absent:

```python
"> docs/reviews/opencode-stage-N-plan-review.md"
"> docs/reviews/opencode-stage-N-release-review.md"
```

That misses nearby shell variants such as `>docs/...`, `>> docs/...`,
`1>docs/...`, `&> docs/...`, quoted paths, `./docs/...`, code-review records,
and rereview records.

## Decision

Make Stage 121 a tests-only hardening node:

- add `re` to `tests/test_review_protocol_docs.py`;
- add a compiled regex that matches an `opencode run` command followed by a
  direct redirection operator targeting an active final review record under
  `docs/reviews/opencode-stage-N-...`;
- replace the two literal substring absence assertions with a loop that scans
  the active review docs and reports any direct final-file redirection match;
- keep the current safe `> "$tmp_review"` then `cp "$tmp_review" docs/reviews/...`
  workflow allowed.

## In Scope

- Modify only `tests/test_review_protocol_docs.py`.
- Add Stage 121 review artifacts.

## Out of Scope

- No docs prose changes unless plan review finds a test incompatibility.
- No runtime behavior changes.
- No source code changes under `src/`.
- No dependency, `pyproject.toml`, or `uv.lock` changes.
- No CI workflow changes.
- No historical review artifact scans or rewrites.
- No connector, scraping, browser automation, platform API, account/session,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance/audit product feature.

## Expected Behavior

The test should continue passing for the current protocol, because the active
examples redirect to `$tmp_review` and then copy the reviewed temporary output
into final review artifacts. The same test should fail for direct final-file
redirection variants such as:

- `opencode run ... >docs/reviews/opencode-stage-N-plan-review.md`
- `opencode run ... >> docs/reviews/opencode-stage-N-code-rereview.md`
- `opencode run ... 1> "./docs/reviews/opencode-stage-N-release-review.md"`
- `opencode run ... &> 'docs/reviews/opencode-stage-N-plan-rereview.md'`

## Acceptance Criteria

- A test-first check demonstrates the new regex catches direct final-file
  redirection variants and ignores the safe temp-file-plus-copy flow.
- `tests/test_review_protocol_docs.py` scans all `ACTIVE_REVIEW_DOCS`, not only
  `docs/REVIEW_PROTOCOL.md`.
- `tests/test_review_protocol_docs.py` no longer relies on the two exact literal
  substring absence checks.
- Focused review protocol docs tests pass.
- Existing release hygiene, full tests, ruff, format, lockfile, mirror scan, and
  diff checks remain green.
