# Claude Code Stage 31 Plan Rereview 8 Prompt

During Stage 31 artifact scanning, `git ls-files` flagged `data/README.md` and
`reports/README.md`. Inspection confirmed these are intentionally tracked
directory documentation files, not generated data or report artifacts.

The plan was updated so the tracked-artifact scan allows only:

- `data/README.md`
- `reports/README.md`

It still rejects other tracked files under `data/` or `reports/`, SQLite files,
DB files, `.eml` files, cookies, sessions, browser artifacts, build/dist
artifacts, and env/config secret files.

Please verify:

1. This allowlist is appropriate for the current repo.
2. It does not permit generated runtime data/report artifacts.
3. No new Critical or Important issues are introduced.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
