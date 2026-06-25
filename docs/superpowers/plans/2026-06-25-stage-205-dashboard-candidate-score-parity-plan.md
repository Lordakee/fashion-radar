# Stage 205 Dashboard Candidate Score Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the dashboard Candidate Signals table preserve Stage 202 candidate score-component fields from the latest report JSON, while staying backward-compatible with older reports.

**Architecture:** `latest_candidate_report()` already reads the latest report JSON and projects candidate dictionaries into dashboard rows. Add the report-backed component fields to that projection with safe defaults, then update dashboard tests and docs to pin the read-only report-backed transparency contract. `app.py` already passes rows directly to `st.dataframe`, so no Streamlit rendering change is required.

**Tech Stack:** Python standard library JSON parsing, existing dashboard query helpers, pytest, Markdown docs, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Scope

This stage closes a report-to-dashboard transparency gap in the local `collect -> match -> report -> inspect` path. Stage 202 exposed candidate score components in report JSON/Markdown and candidate CLI JSON, but the dashboard query projection still drops those fields before rendering the Candidate Signals table.

In scope:

- Preserve these candidate fields from latest report JSON into dashboard rows:
  - `weighted_mention_component`
  - `growth_component`
  - `source_diversity_component`
  - `growth_ratio`
  - `first_seen_at`
- Use backward-compatible defaults for older report JSON:
  - components default to `0.0`
  - `growth_ratio` defaults to `None`
  - `first_seen_at` defaults to `None`
- Update dashboard tests to prove new reports preserve the fields, old reports
  get safe defaults, and older reports that already contain `growth_ratio` /
  `first_seen_at` preserve those values.
- Update dashboard docs to say Candidate Signals show report-backed candidate
  score components, growth ratio, and first-seen timestamps from the latest
  generated report JSON.
- Update changelog and add Stage 205 review artifacts.

Out of scope:

- No entity dashboard parity work.
- No `representative_items` dashboard expansion in this node.
- No Streamlit UI layout changes beyond the existing dataframe receiving more row fields.
- No report schema changes, report generation changes, scoring changes, candidate ranking changes, source acquisition, collectors, source packs, entity packs, social/platform connectors, scraping, demand proof, platform coverage verification, dependency changes, or compliance-review product behavior.

## File Map

- Modify `src/fashion_radar/dashboard/queries.py`
  - Add the five report-backed candidate transparency fields to each row.
- Modify `tests/test_dashboard.py`
  - Extend the latest-report fixture to include Stage 202 component fields and assert they survive.
  - Add a legacy-report test that omits the fields and asserts safe defaults.
  - Add a partial legacy-report test that preserves `growth_ratio` and `first_seen_at`
    while defaulting missing Stage 202 score components.
- Modify `docs/dashboard.md`
  - Mention Candidate Signals show report-backed score components from latest report JSON.
- Modify `tests/test_dashboard_docs.py`
  - Pin the new dashboard docs wording.
- Modify `CHANGELOG.md`
  - Add Stage 205 entry under `### Added`.
- Add `docs/reviews/opencode-stage-205-plan-review-prompt.md`
- Add `docs/reviews/opencode-stage-205-plan-review.md`
- Later add code/release review prompts and bodies.

## Tasks

### Task 1: Write RED Dashboard Query Tests

**Files:**

- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Extend latest report fixture**

In `test_latest_candidate_rows_reads_latest_report()`, add the Stage 202 fields to the candidate fixture:

```python
"weighted_mention_component": 2.0,
"growth_component": 0.0,
"source_diversity_component": 1.0,
"growth_ratio": None,
"first_seen_at": "2026-06-11T00:00:00Z",
```

Add the same keys and values to the expected row.

- [ ] **Step 2: Add legacy compatibility test**

Add near the latest-candidate tests:

```python
def test_latest_candidate_rows_defaults_score_components_for_legacy_report(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-11.json").write_text(
        json.dumps(
            {
                "metadata": {"report_date": "2026-06-11T00:00:00Z"},
                "candidates": [
                    {
                        "phrase": "Le Teckel bag",
                        "candidate_type": "bag",
                        "label": "new_candidate",
                        "score": 3.0,
                        "current_mentions": 2,
                        "baseline_mentions": 0,
                        "distinct_sources": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    assert latest_candidate_rows(reports_dir) == [
        {
            "phrase": "Le Teckel bag",
            "candidate_type": "bag",
            "label": "new_candidate",
            "score": 3.0,
            "weighted_mention_component": 0.0,
            "growth_component": 0.0,
            "source_diversity_component": 0.0,
            "current_mentions": 2,
            "baseline_mentions": 0,
            "growth_ratio": None,
            "distinct_sources": 2,
            "first_seen_at": None,
            "report_date": "2026-06-11T00:00:00Z",
        }
    ]
```

- [ ] **Step 3: Run RED tests**

Add one more test:

```python
def test_latest_candidate_rows_preserves_legacy_growth_fields_without_components(
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "fashion-radar-2026-06-11.json").write_text(
        json.dumps(
            {
                "metadata": {"report_date": "2026-06-11T00:00:00Z"},
                "candidates": [
                    {
                        "phrase": "Le Teckel bag",
                        "candidate_type": "bag",
                        "label": "new_candidate",
                        "score": 3.0,
                        "current_mentions": 2,
                        "baseline_mentions": 1,
                        "growth_ratio": 2.0,
                        "distinct_sources": 2,
                        "first_seen_at": "2026-06-10T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    row = latest_candidate_rows(reports_dir)[0]

    assert row["weighted_mention_component"] == 0.0
    assert row["growth_component"] == 0.0
    assert row["source_diversity_component"] == 0.0
    assert row["growth_ratio"] == 2.0
    assert row["first_seen_at"] == "2026-06-10T00:00:00Z"
```

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_dashboard.py::test_latest_candidate_rows_reads_latest_report \
  tests/test_dashboard.py::test_latest_candidate_rows_defaults_score_components_for_legacy_report \
  tests/test_dashboard.py::test_latest_candidate_rows_preserves_legacy_growth_fields_without_components \
  -q
```

Expected: FAIL because `latest_candidate_report()` currently drops the new fields and the legacy expected row includes defaults that are not projected.

### Task 2: Implement Dashboard Candidate Row Projection

**Files:**

- Modify: `src/fashion_radar/dashboard/queries.py`
- Test: `tests/test_dashboard.py`

- [ ] **Step 1: Add fields to projection**

Change the candidate row dictionary in `latest_candidate_report()` from:

```python
{
    "phrase": candidate.get("phrase", ""),
    "candidate_type": candidate.get("candidate_type", ""),
    "label": candidate.get("label", ""),
    "score": candidate.get("score", 0.0),
    "current_mentions": candidate.get("current_mentions", 0),
    "baseline_mentions": candidate.get("baseline_mentions", 0),
    "distinct_sources": candidate.get("distinct_sources", 0),
    "report_date": report_date,
}
```

to:

```python
{
    "phrase": candidate.get("phrase", ""),
    "candidate_type": candidate.get("candidate_type", ""),
    "label": candidate.get("label", ""),
    "score": candidate.get("score", 0.0),
    "weighted_mention_component": candidate.get("weighted_mention_component", 0.0),
    "growth_component": candidate.get("growth_component", 0.0),
    "source_diversity_component": candidate.get("source_diversity_component", 0.0),
    "current_mentions": candidate.get("current_mentions", 0),
    "baseline_mentions": candidate.get("baseline_mentions", 0),
    "growth_ratio": candidate.get("growth_ratio"),
    "distinct_sources": candidate.get("distinct_sources", 0),
    "first_seen_at": candidate.get("first_seen_at"),
    "report_date": report_date,
}
```

- [ ] **Step 2: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_dashboard.py::test_latest_candidate_rows_reads_latest_report \
  tests/test_dashboard.py::test_latest_candidate_rows_defaults_score_components_for_legacy_report \
  tests/test_dashboard.py::test_latest_candidate_rows_preserves_legacy_growth_fields_without_components \
  -q
```

Expected: both tests pass.

- [ ] **Step 3: Run dashboard tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_dashboard.py -q
```

Expected: all dashboard tests pass.

### Task 3: Update Dashboard Docs

**Files:**

- Modify: `docs/dashboard.md`
- Modify: `tests/test_dashboard_docs.py`

- [ ] **Step 1: Update docs copy**

In `docs/dashboard.md`, replace the behavior bullet:

```markdown
- Reads candidate signals from the latest report JSON when that file is
  available.
```

with:

```markdown
- Reads candidate signals and report-backed candidate score components from the
  latest report JSON when that file is available.
```

In the Candidate Signals section, change:

```markdown
The Candidate Signals tab reads the latest generated report JSON. Candidate
signals are observed phrases from configured sources and imported local signals
and need review.
```

to:

```markdown
The Candidate Signals tab reads the latest generated report JSON. Candidate
signals are observed phrases from configured sources and imported local signals
and need review. The table includes report-backed score components for mentions,
growth, and source diversity when the report was generated by a Stage 202 or
newer version.
It also preserves report-backed growth ratio and first-seen timestamps when
they are present in the report JSON.
```

- [ ] **Step 2: Update docs tests**

In `test_dashboard_docs_keep_warning_and_staleness_boundary()`, update the candidate-signals phrase to:

```python
"Reads candidate signals and report-backed candidate score components from the "
"latest report JSON when that file is available.",
```

Add:

```python
"The table includes report-backed score components for mentions, growth, and "
"source diversity",
"growth ratio and first-seen timestamps",
```

- [ ] **Step 3: Run docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_dashboard_docs.py -q
```

Expected: all dashboard docs tests pass.

### Task 4: Changelog, Code Review, And Focused Verification

**Files:**

- Modify: `CHANGELOG.md`
- Add: `docs/reviews/opencode-stage-205-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-205-code-review.md`

- [ ] **Step 1: Add changelog entry**

Prepend under `## [Unreleased]` / `### Added`:

```markdown
- Stage 205 carries candidate score components from latest report JSON into the
  dashboard Candidate Signals table with legacy-report defaults, without
  changing scoring, report generation, dashboard writes, sources, connectors,
  scraping, demand proof, platform coverage verification, dependency files, or
  compliance-review behavior.
```

- [ ] **Step 2: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py docs/dashboard.md tests/test_dashboard_docs.py CHANGELOG.md
uv --no-config run --frozen ruff format --check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py tests/test_dashboard_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
git diff --exit-code -- uv.lock pyproject.toml
```

- [ ] **Step 3: Run OpenCode code review**

Create `docs/reviews/opencode-stage-205-code-review-prompt.md`, run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-205-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-205-code-review.md
rm -f "$tmp_review"
```

Clean the review artifact and fix any Critical or Important findings.

### Task 5: Release Verification, Release Review, Commit, Push

**Files:**

- All Stage 205 files.

- [ ] **Step 1: Run release verification**

Run:

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] **Step 2: Run release review**

Create `docs/reviews/opencode-stage-205-release-review-prompt.md`, run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-205-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-205-release-review.md
rm -f "$tmp_review"
```

Clean the review artifact and fix any Critical or Important findings.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short --untracked-files=all
git add src/fashion_radar/dashboard/queries.py tests/test_dashboard.py docs/dashboard.md tests/test_dashboard_docs.py CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md docs/reviews/opencode-stage-205-*.md
git commit -m "Stage 205: show candidate score components in dashboard"
git push origin main
git status --short --branch --untracked-files=all
```

## Self-Review

- Spec coverage: The plan covers dashboard query projection, backward compatibility for old reports, docs wording, tests, review artifacts, and release verification.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Scope check: This is one narrow dashboard/report transparency parity stage. It deliberately avoids entity dashboard changes, representative item expansion, scoring/report generation changes, source acquisition, connectors, scraping, dependency changes, and compliance-review behavior.
