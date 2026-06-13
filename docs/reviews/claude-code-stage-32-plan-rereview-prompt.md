# Claude Code Stage 32 Plan Rereview Prompt

Review the Stage 32 CI release hygiene plan after fixes from the first plan
review and read-only subagent audit.

Changes:

- Fixed the Critical CI issue by combining build, installed CLI smoke, and
  dashboard extra smoke into one GitHub Actions step so `tmp_build` does not
  need to cross step boundaries.
- Updated contributor verification to use
  `UV_NO_CONFIG=1 uv sync --locked --dev --check` for release checks.
- Added AGENTS.md guidance updates.
- Added README documentation index and development-note updates.
- Added `docs/release-gate-stage31.md` artifact summary cleanup.
- Kept Stage 32 as docs/CI-only; no runtime feature changes.

Files to review:

- `docs/superpowers/specs/2026-06-14-stage-32-ci-release-hygiene-design.md`
- `docs/superpowers/plans/2026-06-14-stage-32-ci-release-hygiene-plan.md`
- `docs/reviews/claude-code-stage-32-plan-review.md`

Please verify:

1. The prior Critical CI blocker is resolved.
2. The added docs-only scope is appropriate and complete for Stage 32.
3. The plan remains executable and sufficiently verified.
4. The plan avoids runtime feature creep and prohibited platform/source
   acquisition implications.

If acceptable, include exactly:

```text
APPROVED FOR STAGE 32 CI RELEASE HYGIENE
```
