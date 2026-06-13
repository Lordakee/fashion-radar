# Claude Code Stage 31 Plan Rereview 6 Prompt

During Stage 31 public examples smoke, the single-file installed-wheel
`import-signals` dry-run commands failed because `import-signals` uses the
option name `--format`, not `--input-format`.

The plan was updated so only the `import-signals` dry-run commands use:

```bash
--format csv
--format json
```

The community lint/candidates commands still use `--input-format`, which is
their current CLI contract.

Please verify:

1. This command correction is accurate for the current CLI surface.
2. It does not change runtime behavior or scope.
3. No new Critical or Important issues are introduced.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
