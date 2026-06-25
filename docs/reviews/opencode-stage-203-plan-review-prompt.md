# Stage 203 Plan Review Prompt

Review the Stage 203 implementation plan in
`docs/superpowers/plans/2026-06-25-stage-203-uv-lock-release-hygiene-plan.md`.

Goal: make release hygiene automatically reject mirror-bound or private-index
material in the public root `uv.lock`, while preserving frozen local mirror
installs through commands such as
`UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev`.

Context:

- The user explicitly wants dependencies and software installed through mirrors
  where useful.
- Public `uv.lock` must stay mirror-free for GitHub upload and global
  contributor reproducibility.
- Existing docs already say to avoid committing mirror-bound URLs in `uv.lock`.
- Existing `scripts/check_release_hygiene.py` checks forbidden local paths,
  secrets, review capture artifacts, git remote credentials, and git
  `extraheader` authorization values, but does not yet check `uv.lock` for
  mirror/private index contamination.
- This stage must not change `pyproject.toml`, `uv.lock`, runtime product
  behavior, collectors, source packs, entity packs, dashboard, scraping,
  social/platform connectors, source acquisition, demand proof, platform
  coverage verification, or compliance-review product features.

Please review:

1. Is this a reasonable next release-hygiene stage after Stage 202?
2. Does the plan correctly limit scanning to the root `uv.lock` so docs and
   local mirror setup guidance do not self-match?
3. Is the proposed allowlist of `https://pypi.org/simple` for registry URLs and
   `https://files.pythonhosted.org/...` for artifact URLs technically sound for
   the current public lockfile boundary?
4. Are the RED tests sufficient for mirror registry URLs, private registry
   URLs, mirror artifact URLs, lockfile-local index markers, public PyPI pass
   behavior, redaction, tracked/untracked states, and current-repo cleanliness?
5. Does the plan preserve frozen local mirror installs and avoid reading or
   rejecting environment variables/user-level uv config?
6. Are docs/changelog and release verification commands sufficient?
7. Does the plan avoid dependency, source, connector, scraper, platform
   coverage, demand proof, and compliance-review product behavior changes?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
