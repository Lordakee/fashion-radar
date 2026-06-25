# Stage 202 Candidate Score Components Report Transparency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose candidate score components in JSON, Markdown, and candidate CLI JSON outputs so daily fashion signal review can explain why an untracked phrase is surfaced.

**Architecture:** This stage is an additive reporting transparency change over the existing deterministic candidate discovery score formula. It stores the existing candidate mention, growth, and source-diversity score terms on `CandidateMetric`, copies them into `CandidateReport`, renders them in daily Markdown, and documents the meaning as local observed review evidence. It does not change ranking, thresholds, extraction, source acquisition, social/platform connectors, scraping, demand proof, platform coverage verification, dashboard behavior, or compliance-review product features.

**Tech Stack:** Python 3.11+, dataclasses, Pydantic models, Typer CLI JSON rendering, pytest, Ruff, uv, local OpenCode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Core Product Gap

The `collect -> match -> report` pipeline already computes transparent score
components for configured tracked entities. Candidate signals are now central
to noticing new products, designer brands, styling terms, and repeated phrases,
but their report output currently exposes only the final candidate score. Stage
202 closes that report explainability gap by exposing the same local component
style for untracked candidates, making daily review easier without changing the
candidate discovery formula or claiming market demand.

This stage also keeps the project aligned with the full-project review
correction: spend the next node on core report value instead of expanding
frozen external/community/imported handoff surfaces.

## Scope Boundary

This stage may modify:

- candidate metric dataclass fields
- candidate report model fields
- candidate report construction in daily reports and candidate CLI JSON
- Markdown rendering for candidate sections
- focused report, candidate scoring, CLI JSON, and docs tests
- scoring/candidate-discovery docs and changelog
- Stage 202 review artifacts

Do not modify:

- candidate extraction rules or thresholds
- score formula semantics or ordering
- tracked entity scoring semantics
- source configs, source packs, collectors, source-liveness, HTTP/proxy code,
  dashboard behavior, external/community/imported command surfaces, scheduling,
  database schema, dependency files, package metadata, or lockfiles

Do not add:

- social/platform connectors, scraping, browser automation, APIs, login/cookie
  behavior, source acquisition, ranking proof, demand proof, platform coverage
  verification, compliance-review product features, or new network behavior

Candidate language must remain local and review-oriented: observed phrase,
configured sources, imported local signals, needs review, no demand proof, no
platform coverage verification.

## Files And Responsibilities

- Create `docs/reviews/opencode-stage-202-plan-review-prompt.md`: local
  OpenCode plan review prompt.
- Create `docs/reviews/opencode-stage-202-plan-review.md`: cleaned plan review
  result.
- Modify `tests/test_candidate_scoring.py`: RED test for component values and
  score sum over real discovered candidates.
- Modify `tests/test_reports.py`: RED test for JSON fields, Markdown score
  component line, and no raw internal leakage.
- Modify `tests/test_cli.py`: RED test that candidate CLI JSON includes the
  additive component keys in stable model order.
- Modify `tests/test_candidate_discovery_docs.py`: RED docs assertion for
  report output component wording.
- Modify `tests/test_scoring_docs.py`: RED docs assertion for candidate score
  component wording and local/non-proof boundary.
- Modify `src/fashion_radar/discovery/candidates.py`: compute and store the
  existing candidate score terms as named component fields.
- Modify `src/fashion_radar/models/report.py`: add component fields to
  `CandidateReport` with backward-safe defaults.
- Modify `src/fashion_radar/reports.py`: copy component fields into daily
  candidate reports and render Markdown score component lines.
- Modify `src/fashion_radar/cli.py`: copy component fields into candidate CLI
  JSON model construction.
- Modify `docs/candidate-discovery.md`: document candidate report score
  component output in local observed language.
- Modify `docs/scoring.md`: document candidate score component meanings and
  limits.
- Modify `CHANGELOG.md`: add Stage 202 entry under `[Unreleased] / ### Added`.
- Create `docs/reviews/opencode-stage-202-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-202-code-review.md`.
- Create `docs/reviews/opencode-stage-202-release-review-prompt.md`.
- Create `docs/reviews/opencode-stage-202-release-review.md`.

Do not modify `pyproject.toml` or `uv.lock`.

## Component Contract

Expose these fields on `CandidateMetric` and `CandidateReport`:

```python
weighted_mention_component: float
growth_component: float
source_diversity_component: float
```

They must be computed from the existing formula:

```python
weighted_current_mentions = sum(mention.source_weight for mention in current_mentions)
weighted_mention_component = weighted_current_mentions * scoring.weighted_mentions_7d
source_diversity_component = max(0, distinct_sources - 1) * scoring.source_diversity_bonus
growth_component = (
    max(0.0, growth_ratio - 1) * scoring.growth_bonus
    if growth_ratio
    else 0.0
)
score = weighted_mention_component + source_diversity_component + growth_component
```

The Markdown candidate section should include this line immediately after
`- Score: ...`; the default two-item/two-source report fixture should render:

```text
- Score components: mentions 2.00; growth 0.00; sources 1.00
```

Custom scoring fixtures may render other values, but tests should pin exact
two-decimal formatting and the `mentions`, `growth`, `sources` order.

Do not expose candidate internals:

- `contexts`
- `normalized_key`
- item IDs
- `content_hash`
- raw match alias/reason/context terms
- extraction reason labels such as `proper_name_span`, `fashion_anchor`, or
  `single_token`

The compact `fashion-radar candidates` table intentionally remains unchanged
and omits score components. The JSON format carries the additive fields.

## Task 0: Create Plan Review Artifacts

**Files:**
- Create: `docs/reviews/opencode-stage-202-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-202-plan-review.md`

- [ ] **Step 1: Write the plan review prompt**

Create `docs/reviews/opencode-stage-202-plan-review-prompt.md` asking local
OpenCode to review:

- whether exposing candidate score components is a useful core report-value
  stage after Stages 197-201
- whether the component contract matches the existing `_score_candidate`
  formula without changing ranking or thresholds
- whether daily JSON, daily Markdown, and candidate CLI JSON should all use the
  same `CandidateReport` fields
- whether tests should cover score sum, report JSON/Markdown, CLI JSON stable
  keys, docs wording, and internal-field non-leakage
- whether the plan avoids source acquisition, social/platform connectors,
  external/community/imported expansion, dashboard changes, dependency changes,
  and compliance-review product features
- whether release verification is sufficient without dependency or schema
  changes

- [ ] **Step 2: Run plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-202-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-202-plan-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode reports Critical or
Important findings, update this plan and rerun with
`opencode-stage-202-plan-rereview-prompt.md` /
`opencode-stage-202-plan-rereview.md` before implementation.

## Task 1: Add RED Tests For Candidate Score Components

**Files:**
- Modify: `tests/test_candidate_scoring.py`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_candidate_discovery_docs.py`
- Modify: `tests/test_scoring_docs.py`

- [ ] **Step 1: Add candidate scoring component RED test**

In `tests/test_candidate_scoring.py`, add a test that stores one baseline
mention and two current mentions for the same candidate across two sources with
different source weights. Use a custom `ScoringSettings` with explicit
component weights and assert:

- `weighted_mention_component` equals weighted current mentions multiplied by
  `weighted_mentions_7d`
- `source_diversity_component` equals the source diversity term
- `growth_component` equals the growth term
- `score` equals the sum of the three components

Run:

```bash
uv --no-config run --frozen pytest tests/test_candidate_scoring.py::test_candidate_score_exposes_components_that_sum_to_score -q
```

Expected RED: `AttributeError` for the missing component fields.

- [ ] **Step 2: Add report JSON/Markdown RED assertions**

Extend `tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals`
to assert:

- `parsed["candidates"][0]["weighted_mention_component"] > 0`
- `parsed["candidates"][0]["growth_component"] == 0`
- `parsed["candidates"][0]["source_diversity_component"] > 0`
- `parsed["candidates"][0]["score"]` equals `pytest.approx(...)` of the sum of
  the three component fields
- Markdown contains the full line
  `- Score components: mentions 2.00; growth 0.00; sources 1.00`
- the existing forbidden-output loop still excludes raw internals

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals -q
```

Expected RED: missing JSON fields and Markdown line.

- [ ] **Step 3: Add candidate CLI JSON RED assertions**

Extend `tests/test_cli.py::test_candidates_command_prints_json` to assert that
the JSON row contains the component keys after `score` and before mention
counts:

```python
assert list(payload[0]) == [
    "phrase",
    "candidate_type",
    "label",
    "score",
    "weighted_mention_component",
    "growth_component",
    "source_diversity_component",
    "current_mentions",
    "baseline_mentions",
    "distinct_sources",
    "growth_ratio",
    "first_seen_at",
    "representative_items",
]
assert payload[0]["weighted_mention_component"] > 0
assert payload[0]["growth_component"] == 0
assert payload[0]["source_diversity_component"] >= 0
assert payload[0]["score"] == pytest.approx(
    payload[0]["weighted_mention_component"]
    + payload[0]["growth_component"]
    + payload[0]["source_diversity_component"]
)
```

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_candidates_command_prints_json -q
```

Expected RED: stable key list lacks component keys.

- [ ] **Step 4: Add docs RED assertions**

In `tests/test_candidate_discovery_docs.py`, add a test for the `Reports And
Dashboard` section requiring:

- `candidate score components`
- `mentions, growth, and source-diversity terms`
- `local observed review aids`

In `tests/test_scoring_docs.py`, add a test for the `Candidate Signals` section
requiring:

- `weighted_mention_component`
- `growth_component`
- `source_diversity_component`
- `not demand proof`
- `not platform coverage verification`
- `Candidate score components intentionally omit the tracked-entity
  high-weight source term.`

Run:

```bash
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py -q
```

Expected RED: missing docs wording.

## Task 2: Implement Candidate Component Propagation

**Files:**
- Modify: `src/fashion_radar/discovery/candidates.py`
- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Add metric fields without breaking existing constructors**

In `CandidateMetric`, add these fields at the end with defaults so direct test
helpers remain backward compatible:

```python
weighted_mention_component: float = 0.0
growth_component: float = 0.0
source_diversity_component: float = 0.0
```

- [ ] **Step 2: Split `_score_candidate` formula into named terms**

Replace the inline `score = (...)` expression with named component variables
matching the Component Contract, then pass them into `CandidateMetric`.

- [ ] **Step 3: Add report model fields in stable order**

In `CandidateReport`, add the component fields immediately after `score`:

```python
weighted_mention_component: float = 0.0
growth_component: float = 0.0
source_diversity_component: float = 0.0
```

- [ ] **Step 4: Copy fields in daily reports**

In `_candidate_report`, pass the three component values from `CandidateMetric`
to `CandidateReport`.

- [ ] **Step 5: Copy fields in candidate CLI JSON model construction**

In `candidates_command`, pass the same three component values when constructing
`CandidateReport`.

- [ ] **Step 6: Render Markdown component line**

In `_render_candidate_sections`, add the `Score components` line immediately
after `- Score: ...` using two decimal places and the exact order:
mentions, growth, sources.

- [ ] **Step 7: Verify focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_candidate_scoring.py::test_candidate_score_exposes_components_that_sum_to_score \
  tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals \
  tests/test_cli.py::test_candidates_command_prints_json \
  -q
```

Expected: all selected tests pass.

## Task 3: Document Component Semantics

**Files:**
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/scoring.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update candidate discovery docs**

In `docs/candidate-discovery.md`, add or update the report section to state:

- daily report JSON, Markdown, and candidate CLI JSON expose candidate score
  components
- the components are mentions, growth, and source-diversity terms
- they are local observed review aids and not entity validation

- [ ] **Step 2: Update scoring docs**

In `docs/scoring.md` under `Candidate Signals`, document the three fields:

- `weighted_mention_component`
- `growth_component`
- `source_diversity_component`

State that these fields explain the local candidate score and are not demand
proof or platform coverage verification. Also state that candidate score
components intentionally omit the tracked-entity `high_weight_component`
because candidate scoring has no high-weight-source term.

- [ ] **Step 3: Update changelog**

Under `[Unreleased] / ### Added`, add:

```markdown
- Stage 202 exposes local candidate score components in daily report JSON,
  daily report Markdown, and candidate CLI JSON so untracked phrase review can
  see mention, growth, and source-diversity terms without changing ranking,
  source acquisition, social/platform connectors, demand proof, platform
  coverage verification, or compliance-review behavior.
```

- [ ] **Step 4: Verify docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py -q
```

Expected: docs tests pass.

## Task 4: Focused Regression Verification

**Files:**
- No file edits unless tests expose a root-cause defect.

- [ ] **Step 1: Run candidate/report regression tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_candidate_scoring.py tests/test_reports.py -q
```

Expected: pass.

- [ ] **Step 2: Run trend/imported consumers that construct or compare candidates**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_trends.py \
  tests/test_imported_candidates.py \
  tests/test_imported_candidate_evidence.py \
  -q
```

Expected: pass. The new `CandidateMetric` defaults must keep direct test
constructors compatible, and imported candidate surfaces must remain unchanged.

- [ ] **Step 3: Run focused CLI candidate/report tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "candidates_command or report"
```

Expected: pass.

- [ ] **Step 4: Run Ruff on touched files**

Run:

```bash
uv --no-config run --frozen ruff check \
  src/fashion_radar/discovery/candidates.py \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  src/fashion_radar/cli.py \
  tests/test_candidate_scoring.py \
  tests/test_reports.py \
  tests/test_cli.py \
  tests/test_candidate_discovery_docs.py \
  tests/test_scoring_docs.py
uv --no-config run --frozen ruff format --check \
  src/fashion_radar/discovery/candidates.py \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  src/fashion_radar/cli.py \
  tests/test_candidate_scoring.py \
  tests/test_reports.py \
  tests/test_cli.py \
  tests/test_candidate_discovery_docs.py \
  tests/test_scoring_docs.py
```

Expected: pass.

## Task 5: Code Review Gate

**Files:**
- Create: `docs/reviews/opencode-stage-202-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-202-code-review.md`

- [ ] **Step 1: Write code review prompt**

Create `docs/reviews/opencode-stage-202-code-review-prompt.md` summarizing:

- changed files
- additive component fields and Markdown line
- unchanged candidate ranking/threshold/source behavior
- RED/GREEN and focused verification results
- no dependency, schema, source acquisition, dashboard, external/community, or
  imported command-surface changes

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-202-code-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-202-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode reports Critical or
Important findings, fix them, rerun focused tests, and record a
`opencode-stage-202-code-rereview.md` artifact.

## Task 6: Release Verification, Release Review, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-202-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-202-release-review.md`

- [ ] **Step 1: Run release verification**

Run:

```bash
git status --short --untracked-files=all
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
rm -rf dist
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen pytest tests/ -q --tb=short
rg -n -e 'ghp_[A-Za-z0-9_]{20,}' -e 'github_pat_[A-Za-z0-9_]{20,}' \
  -e 'xox[baprs]-[A-Za-z0-9-]{10,}' -e 'AKIA[0-9A-Z]{16}' \
  --glob '!uv.lock' --glob '!dist/**' --glob '!build/**' .
find . -path ./.git -prune -o -path ./.venv -prune -o -path ./dist -prune -o -path './.codegraph' -prune -o \
  \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db-wal' -o -name '*.db-shm' -o -name '.env' \) -print
```

Expected: all commands pass or produce no forbidden findings. If package build
creates `dist/`, leave it untracked or remove it before commit according to the
project's release hygiene expectations.

- [ ] **Step 2: Write and run release review**

Create `docs/reviews/opencode-stage-202-release-review-prompt.md` with:

- implementation summary
- full verification evidence from Step 1
- current `git status --short --untracked-files=all`
- explicit note that `pyproject.toml` and `uv.lock` are unchanged
- explicit request to check release hygiene, review artifact cleanliness,
  secret/local-state absence, and no scope creep

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-202-release-review-prompt.md)" > "$tmp_review"
sed -n '1,400p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-202-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important blockers. If OpenCode reports Critical or
Important findings, fix them, rerun relevant verification, and record a
`opencode-stage-202-release-rereview.md` artifact.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add CHANGELOG.md docs/candidate-discovery.md docs/scoring.md \
  docs/superpowers/plans/2026-06-25-stage-202-candidate-score-components-report-plan.md \
  docs/reviews/opencode-stage-202-*.md \
  src/fashion_radar/discovery/candidates.py \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  src/fashion_radar/cli.py \
  tests/test_candidate_scoring.py tests/test_reports.py tests/test_cli.py \
  tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py
git commit -m "Stage 202: expose candidate score components"
git push origin main
```

Expected: commit succeeds and pushes to `origin/main`.

- [ ] **Step 4: Handoff Summary**

After push, report:

- repo status
- verified commands
- uncommitted files
- next step

Then pause because the user previously requested stopping after the next node
push.
