# Claude Code Stage 311 Code Review

Claude Code was the primary reviewer for Stage 311 code review, but it was
unavailable during this node.

Two attempts were made with the required project settings:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-311-code-review-prompt.md)"
```

Results:

- Attempt 1 returned a server-side 524 origin response timeout before producing
  a review verdict.
- Attempt 2 was retried after the reported retry window with a narrower prompt
  and again returned a server-side 524 origin response timeout before producing
  a review verdict.

No Claude Code approval or rejection was produced. This file is an availability
record, not a review approval.

Per `docs/REVIEW_PROTOCOL.md`, Stage 311 code review proceeded through local
opencode fallback:

- `docs/reviews/opencode-stage-311-code-review.md`
- `docs/reviews/opencode-stage-311-code-rereview.md`
