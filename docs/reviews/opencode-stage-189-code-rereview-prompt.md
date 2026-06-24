# Stage 189 Code Rereview Prompt

Re-review the current working tree after fixing the issues raised in
`docs/reviews/opencode-stage-189-code-review.md`. Evaluate the uncommitted
changes intended for the next commit. Do not treat "not committed yet" as a
blocking finding.

Repository: `/home/ubuntu/fashion-radar`

Inspect:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `tests/test_review_protocol_docs.py`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/reviews/opencode-full-project-review.md`
- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-stage-188-code-review.md`
- `docs/reviews/opencode-stage-188-code-rereview.md`
- `docs/reviews/opencode-stage-188-release-review.md`
- `docs/reviews/opencode-stage-188-release-rereview.md`
- `tests/test_workflows.py`

Prior findings to verify:

1. C1: the Review Protocol change should no longer break
   `tests/test_review_protocol_docs.py::test_review_protocol_docs_document_capture_hygiene`.
2. The release-hygiene detector should still reject non-stage capture noise and
   staged timeout stubs, while leaving the review archive green.
3. The Stage 188 code-review artifact, code rereview, release review, and
   release rereview should now be coherent and free of capture noise.
4. The duplicate proxy-test concern should remain resolved.

Report:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A verdict stating whether the Stage 189 working tree is approved for release
  verification.

Start the response exactly with:

```text
# Stage 189 Code Rereview
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
