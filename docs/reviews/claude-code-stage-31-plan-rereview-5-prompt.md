# Claude Code Stage 31 Plan Rereview 5 Prompt

During Stage 31 public examples smoke, the installed-wheel
`community-candidates` command failed when using `--config-dir "$PWD/configs"`
because the repository publishes `configs/scoring.example.yaml`, not a runtime
`configs/scoring.yaml`.

The plan was updated so public example smoke:

- creates `/tmp/fashion-radar-example-config-stage31`;
- copies `configs/scoring.example.yaml` to
  `/tmp/fashion-radar-example-config-stage31/scoring.yaml`;
- uses that temp config directory for CSV and JSON `community-candidates` and
  `community-candidates-dir` installed-wheel smokes.

Please verify:

1. This is the correct release-gate smoke approach.
2. It does not dirty the repository or imply runtime config generation features.
3. It remains compatible with the package content check that asserts
   `configs/scoring.example.yaml` is included in the sdist.
4. No new Critical or Important issues are introduced.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
