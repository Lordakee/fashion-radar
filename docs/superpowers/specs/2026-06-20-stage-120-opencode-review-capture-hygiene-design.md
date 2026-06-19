# Stage 120 Opencode Review Capture Hygiene Design

## Goal

Prevent future local opencode review artifacts from being committed as
live-capture stubs, garbled telemetry captures, duplicated verdicts, or empty
review records.

## Reviewer Context

This design is for local opencode review before implementation. To avoid the
capture defect this stage addresses, run opencode and inspect its output before
writing the final review artifact:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-120-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-120-plan-review.md
rm -f "$tmp_review"
```

## Background

The active review protocol now uses local opencode with
`zhipuai-coding-plan/glm-5.2 --variant max`. Several historical review records
show that direct capture into the final review file can pollute audit records:

- Stage 40 review records mention `nowWrote` / `Wrote ...` tool-status text,
  duplicated verdicts, orphaned fragments, and a corrupted record that could not
  serve as audit evidence.
- Stage 74 and Stage 84 review records mention concatenated, duplicated, or
  truncated capture text.
- Stage 119 reproduced the same class of issue when a `Re-review written to ...`
  status line was spliced into prose and later had to be cleaned manually.

`docs/REVIEW_PROTOCOL.md` currently shows examples that redirect opencode output
straight into `docs/reviews/opencode-stage-N-...`. That direct final-file capture
is the pattern prior reviews identified as risky.

## Decision

Add a docs/tests-only hygiene node that documents forward-only review artifact
capture rules:

- capture local opencode output to a temporary file first;
- inspect the temporary file and copy only completed review output into the final
  `docs/reviews/opencode-stage-N-...` record;
- do not commit live-capture stubs, duplicated or truncated text, tool-status
  messages such as `Wrote`, empty output, or multiple verdict/approval phrases;
- if a review times out, record the timeout honestly instead of presenting a
  partial stream as an approval;
- keep historical review artifacts unchanged unless a future stage explicitly
  scopes a targeted cleanup.

Use `tests/test_review_protocol_docs.py` as the drift guard because it already
owns the active review protocol docs and has no application imports.

## In Scope

- Add review capture hygiene docs drift coverage to
  `tests/test_review_protocol_docs.py`.
- Add an agent-facing review artifact hygiene bullet in `AGENTS.md`.
- Replace direct-final-file opencode examples in `docs/REVIEW_PROTOCOL.md` with
  temporary-capture examples and add a `## Review Capture Hygiene` section.
- Add final-review capture hygiene guidance to `docs/github-upload-checklist.md`.
- Add Stage 120 review artifacts.

## Out of Scope

- No runtime behavior changes.
- No source code changes under `src/`.
- No dependency, `pyproject.toml`, or `uv.lock` changes.
- No CI workflow changes.
- No bulk rewrite of historical review artifacts.
- No connector, scraping, browser automation, platform API, account/session,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance/audit product feature.

## Expected User-Facing Behavior

Agents and contributors following the review protocol should see that the final
review artifact is not the raw live stream. The workflow should be:

1. run local opencode into a temporary capture;
2. inspect the capture for complete reviewer output;
3. copy only the completed review body into the final
   `docs/reviews/opencode-stage-N-...` file;
4. scan the final artifact for status-line contamination and duplicate verdicts
   before committing.

## Acceptance Criteria

- `tests/test_review_protocol_docs.py` has a failing test first that requires
  review capture hygiene wording in `docs/REVIEW_PROTOCOL.md` and
  `docs/github-upload-checklist.md`.
- `AGENTS.md` tells agents not to commit opencode review artifacts with
  live-capture stubs, duplicated/truncated text, tool-status messages, or empty
  output.
- `docs/REVIEW_PROTOCOL.md` includes a `## Review Capture Hygiene` section that
  mentions temporary capture, completed review output, active
  `opencode-stage-N-*` records, timeout handling, and duplicate verdict/approval
  avoidance.
- `docs/REVIEW_PROTOCOL.md` examples no longer redirect opencode output directly
  to final `docs/reviews/opencode-stage-N-...` paths.
- `docs/github-upload-checklist.md` final review section includes the same
  completed-output and no-live-capture-stub guardrails.
- Focused review protocol docs tests pass after implementation.
- Existing release hygiene, full tests, ruff, format, lockfile, mirror scan, and
  diff checks remain green.
