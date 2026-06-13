# Claude Code Stage 31 Plan Rereview 7 Prompt

During Stage 31 secret/artifact scan, the planned secret regex flagged
documentation that mentions variable names and placeholders, e.g. `GITHUB_TOKEN`
and `<TOKEN_FROM_USER>`. These are not persisted secrets.

The plan was updated to scan actual secret-looking values instead:

- GitHub token prefixes with minimum value length:
  `ghp_[A-Za-z0-9_]{20,}` and `github_pat_[A-Za-z0-9_]{20,}`;
- OpenAI-style keys: `sk-[A-Za-z0-9_-]{20,}`;
- Slack token prefixes with minimum length;
- private key headers;
- AWS key variable assignments, not bare variable names.

The plan still checks:

- token-free remote URL;
- no persistent `http.*extraheader`;
- staged file allowlist;
- no tracked generated artifacts.

Please verify:

1. This avoids false positives from non-secret variable names/placeholders.
2. It still catches realistic persisted secrets for this repo's release gate.
3. No new Critical or Important issues are introduced.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
