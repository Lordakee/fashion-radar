# Claude Code Stage 31 Plan Rereview 4 Prompt

During Stage 31 execution, `uv lock --check` and
`uv sync --locked --dev --check` failed when run bare. Investigation found the
machine has user-level uv config at `~/.config/uv/uv.toml` setting the Tsinghua
mirror as the default index, which causes uv to consider the committed
public-PyPI `uv.lock` out of date because it would rewrite registry URLs to the
mirror.

The plan/design/checklist were updated to:

- Keep `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync
  --frozen --dev --check` as the mirror-backed install/sync check.
- Use `UV_NO_CONFIG=1 uv lock --check` and
  `UV_NO_CONFIG=1 uv sync --locked --dev --check` for release lockfile checks so
  user-level mirror config cannot dirty or invalidate the public lockfile.
- Document this in `docs/github-upload-checklist.md`.

Files to review:

- `docs/superpowers/specs/2026-06-13-stage-31-release-gate-design.md`
- `docs/superpowers/plans/2026-06-13-stage-31-release-gate-plan.md`
- `docs/github-upload-checklist.md`

Please verify:

1. This is the correct fix for the observed uv behavior.
2. It still respects the user's preference to use mirrors for installs where
   practical.
3. It still prevents mirror URLs from being persisted to `uv.lock`.
4. No new Critical or Important issues are introduced.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 31 RELEASE GATE
```
