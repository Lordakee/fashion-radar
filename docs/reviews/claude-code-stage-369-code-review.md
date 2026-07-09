# Claude Code Stage 369 Code Review

Claude Code review command did not return usable output within the local capture window.

- Command: `printf <review prompt> | claude -p --effort max --permission-mode bypassPermissions --tools "Read,Bash"`
- Exit status: `124`
- stderr tail:

```text
```

Fallback review coverage was provided by the Stage 369 xhigh Codex review subagent and the verification gates in this node.
