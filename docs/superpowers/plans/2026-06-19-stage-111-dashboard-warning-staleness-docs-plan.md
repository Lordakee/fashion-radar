# Stage 111 Dashboard Warning Staleness Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a docs drift guard for dashboard warning, empty-state, and stale
report wording.

**Architecture:** Append one pytest test to `tests/test_dashboard_docs.py` that
reuses the existing `_read_dashboard_doc()` and `_normalized()` helpers,
normalizes `docs/dashboard.md`, and asserts public dashboard warning/staleness
phrases. Keep this stage docs-test-only and avoid dashboard runtime, Streamlit,
SQLite, report loading, scoring, candidate extraction, source acquisition,
connector, social/platform scraping, compliance, dependency, and CI changes.

**Tech Stack:** Python 3.11, pytest, pathlib, Markdown text fixtures, ruff, uv.

---

## File Map

- Create:
  `docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md`
  records the Stage 111 design and scope.
- Create:
  `docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md`
  records this implementation plan.
- Create: `docs/reviews/opencode-stage-111-plan-review-prompt.md` requests the
  local plan review.
- Create: `docs/reviews/opencode-stage-111-plan-review.md` records the local
  plan review.
- Modify: `tests/test_dashboard_docs.py` appends the dashboard
  warning/staleness docs drift guard.
- Create: `docs/reviews/opencode-stage-111-code-review-prompt.md` requests the
  local code review.
- Create: `docs/reviews/opencode-stage-111-code-review.md` records the local
  code review.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-111-plan-review-prompt.md` with this
      review request:

```markdown
# Stage 111 Plan Review Prompt

Review the Stage 111 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a docs drift guard for `docs/dashboard.md` so dashboard warning,
empty-state, and stale-report expectations remain explicit: invalid trend config
warns without creating local state, Daily Brief empty states avoid creating the
data directory or database, and Candidate Signals reads the latest report JSON
and may be stale until a new report is written.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md`
- `docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md`
- `docs/dashboard.md`
- `tests/test_dashboard_docs.py`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`

## Planned Test

The implementation will append one docs-only test to
`tests/test_dashboard_docs.py`. It will normalize `docs/dashboard.md` and
assert:

- `Invalid or missing trend config shows a concise dashboard warning without creating the data directory or database.`
- `If the local database has not been initialized or has no retained items, the tab shows an empty-state message without creating the data directory or database.`
- `Reads candidate signals from the latest report JSON when that file is available.`
- `The Candidate Signals tab reads the latest generated report JSON.`
- `If the latest report was generated before the latest collection, local import, or matching run, the tab may be stale until a new report is written.`

## Scope Constraints

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 111 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`
- dashboard runtime behavior, Streamlit rendering, SQLite queries, report
  loading, candidate extraction, scoring, source collection, dashboard tab
  routing, CLI behavior, source acquisition, connectors, scraping, browser
  automation, platform APIs, monitoring, scheduling, ranking, demand proof,
  coverage verification, account/cookie/session/proxy/CAPTCHA/paywall behavior,
  or compliance/audit/legal review product features

Do not expand this stage into runtime dashboard tests, dashboard docs rewrites,
report generation behavior, candidate discovery behavior, scoring behavior,
source collection, platform search, social monitoring, schema migrations,
connector behavior, README/project-brief parity, or compliance features.

## Review Questions

1. Does the plan protect real `docs/dashboard.md` warning/staleness wording
   without changing product behavior or docs text?
2. Are the planned phrases present in `docs/dashboard.md` and suitable for the
   existing whole-doc normalized dashboard docs test pattern?
3. Does appending to `tests/test_dashboard_docs.py` fit the existing dashboard
   docs test pattern?
4. Does the plan avoid overlap with scoring docs, candidate-discovery docs,
   report behavior, dashboard runtime tests, package archive checks, and runtime
   code?
5. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-111-plan-review-prompt.md)" > docs/reviews/opencode-stage-111-plan-review.md
```

- [ ] Read `docs/reviews/opencode-stage-111-plan-review.md`.
- [ ] Fix any Critical or Important findings before Task 2.

## Task 2: Add The Docs Guard

- [ ] Append this test to `tests/test_dashboard_docs.py`:

```python
def test_dashboard_docs_keep_warning_and_staleness_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "Invalid or missing trend config shows a concise dashboard warning without "
        "creating the data directory or database.",
        "If the local database has not been initialized or has no retained items, "
        "the tab shows an empty-state message without creating the data directory "
        "or database.",
        "Reads candidate signals from the latest report JSON when that file is available.",
        "The Candidate Signals tab reads the latest generated report JSON.",
        "If the latest report was generated before the latest collection, local "
        "import, or matching run, the tab may be stale until a new report is written.",
    ):
        assert phrase.casefold() in normalized
```

- [ ] Run the focused test:

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
```

Expected: pass.

- [ ] Run adjacent docs/runtime-reference tests:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard_docs.py tests/test_dashboard.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_reports.py tests/test_cli_docs.py -q
```

Expected: pass.

- [ ] Run style checks:

```bash
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
git diff --check
```

Expected: all pass.

## Task 3: Code Review

- [ ] Create `docs/reviews/opencode-stage-111-code-review-prompt.md` with this
      review request:

```markdown
# Stage 111 Code Review Prompt

Review the Stage 111 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 111 appends a docs drift guard to `tests/test_dashboard_docs.py`, scoped
to warning, empty-state, and stale-report wording in `docs/dashboard.md`. It
asserts that dashboard docs keep local-state warning expectations and Candidate
Signals latest-report/staleness expectations explicit.

## Files To Review

- `tests/test_dashboard_docs.py`
- `docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md`
- `docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md`
- `docs/reviews/opencode-stage-111-plan-review-prompt.md`
- `docs/reviews/opencode-stage-111-plan-review.md`
- `docs/reviews/opencode-stage-111-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 111 review artifacts

Disallowed changes:

- `docs/dashboard.md`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_dashboard.py`
- `tests/test_scoring_docs.py`
- `tests/test_candidate_discovery_docs.py`
- dashboard runtime behavior, Streamlit rendering, SQLite queries, report
  loading, candidate extraction, scoring, source collection, dashboard tab
  routing, CLI behavior, source acquisition, connectors, scraping, browser
  automation, platform APIs, monitoring, scheduling, ranking, demand proof,
  coverage verification, account/cookie/session/proxy/CAPTCHA/paywall behavior,
  or compliance/audit/legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_dashboard_docs.py tests/test_dashboard.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_dashboard_docs.py
uv --no-config run --frozen ruff format --check tests/test_dashboard_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 111 plan and remain scoped to a
   docs-only drift guard?
2. Are the asserted phrases appropriate for `docs/dashboard.md`, given existing
   overlap with scoring docs, candidate-discovery docs, reports, and dashboard
   runtime tests?
3. Does the implementation fit the existing `tests/test_dashboard_docs.py`
   pattern cleanly?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
```

- [ ] Run the local code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-111-code-review-prompt.md)" > docs/reviews/opencode-stage-111-code-review.md
```

- [ ] Read `docs/reviews/opencode-stage-111-code-review.md`.
- [ ] Fix any Critical or Important findings before Task 4.

## Task 4: Release Gate, Commit, Push, And CI

- [ ] Run the full release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: all pass.

- [ ] Stage only Stage 111 files:

```bash
git add tests/test_dashboard_docs.py \
  docs/superpowers/specs/2026-06-19-stage-111-dashboard-warning-staleness-docs-design.md \
  docs/superpowers/plans/2026-06-19-stage-111-dashboard-warning-staleness-docs-plan.md \
  docs/reviews/opencode-stage-111-plan-review-prompt.md \
  docs/reviews/opencode-stage-111-plan-review.md \
  docs/reviews/opencode-stage-111-code-review-prompt.md \
  docs/reviews/opencode-stage-111-code-review.md
```

- [ ] Run staged checks:

```bash
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

Expected: all pass and no staged `uv.lock`.

- [ ] Commit:

```bash
git commit -m "Guard dashboard warning staleness docs"
```

- [ ] Push to `origin main` using only temporary credentials.
- [ ] Verify no GitHub credential was persisted:

```bash
git config --get-all http.https://github.com/.extraheader || true
git remote -v | sed -E 's#(https://)[^/@]+@#\1***@#g'
```

- [ ] Verify GitHub Actions `CI` succeeds for the pushed SHA.

## Completion Criteria

- `tests/test_dashboard_docs.py` contains a focused dashboard
  warning/staleness docs guard.
- No runtime, docs-source, dependency, config, CI, connector, scraping, platform,
  README/project-brief, or compliance feature files changed.
- Focused, adjacent, release-gate, staged, and GitHub Actions checks pass.
