# Stage 202 Release Review Prompt

Review the Stage 202 release state in `/home/ubuntu/fashion-radar`.

Goal: confirm the repository is ready to commit and push after exposing local
candidate score components in daily report JSON, daily report Markdown, and
candidate CLI JSON.

Plan/code review artifacts:

- `docs/superpowers/plans/2026-06-25-stage-202-candidate-score-components-report-plan.md`
- `docs/reviews/opencode-stage-202-plan-review.md`
- `docs/reviews/opencode-stage-202-plan-rereview.md`
- `docs/reviews/opencode-stage-202-code-review.md`

Implementation summary:

- `CandidateMetric` now includes `weighted_mention_component`,
  `growth_component`, and `source_diversity_component`.
- `_score_candidate` splits the existing score formula into those three terms
  and re-sums them without changing ranking, thresholds, labels, extraction, or
  source behavior.
- `CandidateReport`, daily report construction, and `candidates --format json`
  now expose the same three fields.
- Daily Markdown candidate sections include a `Score components` line.
- Tests pin component values, JSON key order, `score == sum(components)`, docs
  wording, and no raw candidate internals.
- Docs/changelog frame the fields as local observed review aids, not demand
  proof or platform coverage verification.

Changed tracked files:

- `CHANGELOG.md`
- `docs/candidate-discovery.md`
- `docs/scoring.md`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `tests/test_candidate_discovery_docs.py`
- `tests/test_candidate_scoring.py`
- `tests/test_cli.py`
- `tests/test_reports.py`
- `tests/test_scoring_docs.py`
- Stage 202 plan/review artifacts

Verification completed:

- `git diff --check` -> passed.
- `UV_NO_CONFIG=1 uv lock --check` -> resolved 85 packages, lock current.
- `UV_NO_CONFIG=1 uv sync --locked --dev --check` -> would make no changes.
- `uv --no-config run --frozen ruff check .` -> all checks passed.
- `uv --no-config run --frozen ruff format --check .` -> 148 files already
  formatted.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  -> release hygiene checks passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  -> first-run sample smoke passed.
- `rm -rf dist && uv --no-config build` -> built
  `dist/fashion_radar-0.1.0.tar.gz` and
  `dist/fashion_radar-0.1.0-py3-none-any.whl`.
- Initial package archive check command used the wrong old shape
  `scripts/check_package_archives.py --repo-root .` and failed with argparse
  usage. The plan was corrected to the current script contract and
  `uv --no-config run --frozen python scripts/check_package_archives.py dist`
  passed with "Package archives contain required files."
- `uv --no-config run --frozen pytest tests/ -q --tb=short` -> `1484 passed`.
- High-confidence token/key scan:
  `rg -n -e "ghp_[A-Za-z0-9_]{20,}" -e "github_pat_[A-Za-z0-9_]{20,}" -e "xox[baprs]-[A-Za-z0-9-]{10,}" -e "AKIA[0-9A-Z]{16}" --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' .`
  -> no matches.
- Local DB/env/artifact scan excluding `.git`, `.venv`, `dist`, and
  `.codegraph` -> no matches.
- Review artifact chatter scan for Stage 202 review/plan files -> no matches
  with process/tool-status prefixes or ANSI/build markers.
- `pyproject.toml` and `uv.lock` are unchanged.
- `dist/` build artifacts were removed before release review.

Current `git status --short --untracked-files=all`:

```text
 M CHANGELOG.md
 M docs/candidate-discovery.md
 M docs/scoring.md
 M src/fashion_radar/cli.py
 M src/fashion_radar/discovery/candidates.py
 M src/fashion_radar/models/report.py
 M src/fashion_radar/reports.py
 M tests/test_candidate_discovery_docs.py
 M tests/test_candidate_scoring.py
 M tests/test_cli.py
 M tests/test_reports.py
 M tests/test_scoring_docs.py
?? docs/reviews/opencode-stage-202-code-review-prompt.md
?? docs/reviews/opencode-stage-202-code-review.md
?? docs/reviews/opencode-stage-202-plan-rereview-prompt.md
?? docs/reviews/opencode-stage-202-plan-rereview.md
?? docs/reviews/opencode-stage-202-plan-review-prompt.md
?? docs/reviews/opencode-stage-202-plan-review.md
?? docs/superpowers/plans/2026-06-25-stage-202-candidate-score-components-report-plan.md
```

Please review:

1. Are the implementation, tests, docs, changelog, and review artifacts ready to
   commit and push?
2. Are release verification results sufficient, including the corrected package
   archive command?
3. Are `pyproject.toml` and `uv.lock` correctly unchanged?
4. Are generated artifacts, local data files, tokens/secrets, CodeGraph DB
   files, and build outputs absent from the commit set?
5. Is there any accidental source acquisition, social/platform connector,
   scraping, dashboard, imported/community output, dependency, schema, ranking,
   demand-proof, platform coverage verification, or compliance-review behavior?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
