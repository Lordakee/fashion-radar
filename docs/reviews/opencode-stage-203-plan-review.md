# Stage 203 Plan Review

## Verdict

No Critical findings. No Important findings. The plan is a sound, well-scoped
release-hygiene stage and is ready for implementation after the minor notes
below.

## Critical

None.

## Important

None.

## Answers To The Review Questions

1. Reasonable next stage after 202: yes. Stage 202 added candidate score
   components. Stage 203 closes a documented but unenforced gap between the
   mirror policy and the hygiene gate. Sequencing is correct, and the plan
   reuses the existing `collect_findings()` extension pattern established by
   the review-capture scanner.

2. Correctly limited to root `uv.lock`: yes. The planned helper gates on
   `normalize_git_path(path) != UV_LOCK_PATH`, so `docs/...`, mirror setup
   guidance, the plan file itself, and the upload checklist all correctly
   self-skip.

3. Allowlist technically sound for the current boundary: yes. The committed
   `uv.lock` uses `https://pypi.org/simple` registry sources and
   `files.pythonhosted.org` artifact URLs. The editable local project source
   contains neither `registry =` nor `url =`, so it is correctly ignored.

4. RED tests sufficient: yes for the core contract. The tests cover mirror
   registry URLs, private registry URLs, mirror artifact URLs, index markers,
   public PyPI pass behavior, redaction, tracked/untracked states, and
   current-repo cleanliness.

5. Preserves frozen mirror installs and ignores environment/user config: yes.
   The scanner is a pure text check over one file and never reads environment
   variables or user-level uv configuration.

6. Docs/changelog and release verification sufficient: yes. The changelog
   entry lands under the existing `## [Unreleased]` / `### Fixed` section.
   Docs keep `rg` as a diagnostic while promoting the automated gate.

7. Avoids dependency/source/connector/scraper/coverage/demand-proof/compliance
   changes: yes. The file map touches release hygiene, tests, docs, changelog,
   and review artifacts only.

## Minor

1. `UV_LOCK_INDEX_MARKER_PATTERN` is slightly defensive. `default-index` and
   bare `extra-index` are uv/pip configuration concepts, not current `uv.lock`
   fields. They are harmless if included because the current clean lockfile has
   no matches.

2. Keep the marker regex alternatives ordered from longest to shortest so
   `extra-index-url` is not shortened to `extra-index` if the pattern is later
   reordered.

3. Optional extra tests could cover an untracked mirror registry URL, a direct
   `source = { url = "..." }` mirror source, and a trailing-slash
   `https://pypi.org/simple/` pass case. These are non-blocking because the
   core contract is already covered.

4. In `docs/dependency-mirrors.md`, only the pre-upload lockfile bullet should
   change. The recovery and regeneration `rg` diagnostics should remain.

5. The scanner intentionally inspects root `uv.lock` only. `[tool.uv]` index
   config in `pyproject.toml` remains outside this stage's scope; future mirror
   lock regeneration would be caught by the lockfile gate.

## Verified Context

- Current `uv.lock` registry sources use `https://pypi.org/simple`.
- Current `uv.lock` artifact URLs use `files.pythonhosted.org`.
- Current `uv.lock` has no `index-url`, `extra-index-url`, `find-links`,
  `default-index`, or `extra-index` markers.
- `pyproject.toml` has no index or mirror config.
- `CHANGELOG.md` has the target `### Fixed` section.
