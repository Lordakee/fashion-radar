# Claude Code Stage 370 Code Review

Status: timed out.

Command:

```bash
claude --print --effort max --dangerously-skip-permissions "You are reviewing Stage 370 in /home/ubuntu/fashion-radar. Review only the currently staged changes (use git diff --cached and git status --short). Do not edit files. Focus on bugs, behavioral regressions, missing tests, unsafe href handling, generated-site-only boundary, app contract changes, and whether the implementation matches the Stage 370 plan. Output findings first, ordered by severity with file/line references. If no Critical or Important issues, say so clearly and list residual risks. Keep under 120 lines."
```

Result: no usable output before the 600 second timeout.

Follow-up: use opencode GLM 5.2 and an xhigh Codex reviewer as the usable Stage 370 code review gates.
