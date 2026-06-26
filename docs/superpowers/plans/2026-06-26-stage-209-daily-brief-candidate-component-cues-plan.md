# Stage 209 Daily Brief Candidate Component Cues Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic candidate score-component cues to Daily Brief candidate summaries, so the first report surface explains why an untracked phrase needs review without changing scoring, ranking, model schemas, source acquisition, or dashboard behavior.

**Architecture:** Keep this as a report-rendering explainability change over existing `CandidateReport` fields. Stage 202 already exposes `weighted_mention_component`, `growth_component`, and `source_diversity_component` on full candidate report rows; Stage 209 will reuse those fields inside `_brief_item_for_candidate(...)` and append a compact component sentence to the existing `DailyBriefItem.summary`. It will not add new `DailyBriefItem` fields or change `daily-brief/v1` model structure.

**Tech Stack:** Python 3.11, Pydantic report models, existing daily report builder/renderers, pytest, Markdown docs, `uv --no-config run --frozen`, local OpenCode review with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Core Product Gap

This stage closes a small `collect -> match -> report` explainability gap. The
full candidate report sections already show local score components:

```text
- Score components: mentions 2.00; growth 0.00; sources 1.00
```

The Daily Brief is the first report surface, but candidate brief items currently
only summarize current mentions, baseline mentions, and distinct sources. That
forces a reviewer to scroll to the full candidate section to understand whether
the local score came from weighted mentions, growth, or source diversity.

Stage 209 should keep Daily Brief compact while making the existing local score
components visible in the candidate item summary. This is a report-explanation
improvement only; it is not a scoring formula change and not a demand,
coverage, ranking, social, or acquisition feature.

## Scope

In scope:

- Append candidate score component cues to `DailyBriefItem.summary` for
  `kind="candidate_phrase"` items.
- Use existing `CandidateReport.weighted_mention_component`,
  `CandidateReport.growth_component`, and
  `CandidateReport.source_diversity_component`.
- Keep two-decimal formatting and the existing full candidate report order:
  `mentions`, `growth`, `sources`.
- Add tests proving:
  - Daily Brief JSON candidate summary includes the component cue.
  - Daily Brief Markdown includes the same cue because Markdown renders
    `DailyBriefItem.summary`.
  - Empty / non-candidate Daily Brief sections are unchanged.
- Update docs and changelog to state Daily Brief candidate summaries can include
  local score-component cues.
- Add Stage 209 OpenCode plan/code/release review artifacts.

Out of scope:

- No new fields on `DailyBriefItem`.
- No `DailyBrief.contract_version` change.
- No `CandidateReport`, `CandidateMetric`, CLI candidate JSON, dashboard,
  scoring formula, ranking, candidate extraction, thresholds, DB schema,
  migrations, source configs, source packs, collectors, source-liveness,
  HTTP/proxy behavior, dependencies, or lockfile changes.
- No social/platform connectors, scraping, browser automation, login/cookie
  behavior, source acquisition, demand proof, platform coverage verification,
  compliance-review product features, or new network behavior.

## File Map

- Modify `src/fashion_radar/reports.py`
  - Add a small helper for candidate component cue formatting.
  - Append that helper output to `_brief_item_for_candidate(...)` summary.
- Modify `tests/test_reports.py`
  - Add RED assertions for Daily Brief JSON and Markdown candidate summaries.
  - Add a direct build_daily_brief test to pin summary-only behavior over an
    explicit `CandidateReport`.
- Modify `README.md`
  - Clarify generated Daily Brief candidate phrases can include score-component
    cues from local report rows.
- Modify `docs/cli-reference.md`
  - Clarify `report`/`run` Daily Brief content includes candidate component cues
    where available.
- Modify `docs/architecture.md`
  - Clarify the report component can include candidate score-component cues in
    Daily Brief summaries without collecting/searching.
- Modify `tests/test_cli_docs.py`
  - Extend Daily Brief docs guard wording only if docs changes need a pinned
    phrase.
- Modify `CHANGELOG.md`
  - Add Stage 209 entry.
- Add review artifacts under `docs/reviews/`.

Do not modify `pyproject.toml` or `uv.lock`.

## Task 0: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-209-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-209-plan-review.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-209-plan-review-prompt.md` asking OpenCode
to review this plan for report-only scope, Daily Brief JSON compatibility,
summary-only implementation, test coverage, docs wording, release hygiene, and
avoidance of source/social/dependency/scoring changes.

- [ ] **Step 2: Run OpenCode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-209-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-209-plan-review.md
rm -f "$tmp_review"
```

Expected: completed review artifact with no Critical or Important blockers.
Fix Critical/Important planning findings and run a rereview before Task 1.

## Task 1: RED Tests For Daily Brief Candidate Component Cues

**Files:**

- Modify: `tests/test_reports.py`

- [ ] **Step 1: Extend stable Daily Brief JSON shape test**

In `test_daily_report_includes_stable_daily_brief_json_shape`, after the
candidate item assertions, bind the candidate item:

```python
candidate_item = parsed["brief"]["sections"][1]["items"][0]
```

Add assertions:

```python
assert "Score components:" in candidate_item["summary"]
assert "mentions 2.00" in candidate_item["summary"]
assert "growth 0.00" in candidate_item["summary"]
assert "sources 1.00" in candidate_item["summary"]
assert "high-weight" not in candidate_item["summary"]
```

These assertions use the existing fixture with two current candidate mentions
from two sources, default scoring, and no baseline growth. Candidate score
components intentionally omit the tracked-entity high-weight term.

- [ ] **Step 2: Extend Daily Brief Markdown test**

In `test_markdown_report_renders_daily_brief_before_top_signals`, store two
unmatched candidate source items before building the report:

```python
repository = ItemRepository(engine)
repository.upsert_item(
    CollectedItem(
        source_name="Fashionista",
        source_type=SourceType.RSS,
        url="https://example.com/le-teckel",
        title="Le Teckel bag signal",
        published_at=AS_OF - timedelta(hours=2),
        summary="Le Teckel bag appears in local observed coverage.",
    ),
    collected_at=AS_OF - timedelta(hours=2),
)
repository.upsert_item(
    CollectedItem(
        source_name="WWD",
        source_type=SourceType.RSS,
        url="https://example.com/le-teckel-again",
        title="Le Teckel bag appears again",
        published_at=AS_OF - timedelta(hours=3),
        summary="Le Teckel bag appears again in local observed coverage.",
    ),
    collected_at=AS_OF - timedelta(hours=3),
)
```

Then add assertions scoped to the Daily Brief section, not the later full
`## Untracked Candidate Signals` section which already renders candidate score
components:

```python
daily_brief = markdown.split("## Daily Brief", 1)[1].split("## Top Signals", 1)[0]
candidate_brief = daily_brief.split("### Candidate Signals Needing Review", 1)[1].split(
    "### Source Caveats",
    1,
)[0]
assert "### Candidate Signals Needing Review" in daily_brief
assert "- Le Teckel bag:" in candidate_brief
assert "Score components: mentions 2.00; growth 0.00; sources 1.00" in candidate_brief
assert "high-weight" not in candidate_brief
```

- [ ] **Step 3: Add direct build_daily_brief summary-only test**

Add:

```python
def test_daily_brief_candidate_summary_includes_existing_score_components() -> None:
    brief = build_daily_brief(
        entities=[],
        candidates=[
            CandidateReport(
                phrase="Le Teckel bag",
                candidate_type="bag",
                label="rising_candidate",
                score=4.25,
                weighted_mention_component=2.5,
                growth_component=0.75,
                source_diversity_component=1.0,
                current_mentions=2,
                baseline_mentions=1,
                distinct_sources=3,
                growth_ratio=2.0,
                first_seen_at=AS_OF,
            )
        ],
        source_health=[],
        recent_runs=[],
    )

    candidate_item = brief.sections[1].items[0]

    assert candidate_item.kind == "candidate_phrase"
    assert candidate_item.score == 4.25
    assert "Score components: mentions 2.50; growth 0.75; sources 1.00" in (
        candidate_item.summary
    )
    assert "high-weight" not in candidate_item.summary
    assert not hasattr(candidate_item, "weighted_mention_component")
```

The final `hasattr` assertion pins summary-only behavior and prevents accidental
`DailyBriefItem` schema expansion.

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_report_includes_stable_daily_brief_json_shape \
  tests/test_reports.py::test_markdown_report_renders_daily_brief_before_top_signals \
  tests/test_reports.py::test_daily_brief_candidate_summary_includes_existing_score_components \
  -q
```

Expected: the tests fail because candidate Daily Brief summaries do not yet
include the score-component cue, and the new direct test does not exist before
the test edit.

## Task 2: GREEN Report Summary Implementation

**Files:**

- Modify: `src/fashion_radar/reports.py`

- [ ] **Step 1: Add helper for candidate component cue**

Add this helper near `_brief_item_for_candidate(...)`:

```python
def _candidate_component_summary(candidate: CandidateReport) -> str:
    return (
        "Score components: "
        f"mentions {candidate.weighted_mention_component:.2f}; "
        f"growth {candidate.growth_component:.2f}; "
        f"sources {candidate.source_diversity_component:.2f}."
    )
```

- [ ] **Step 2: Append component cue to candidate brief summary**

Change `_brief_item_for_candidate(...)` so the `summary` ends with the helper:

```python
summary=(
    "Local observed candidate phrase from configured sources and imported local "
    f"signals; needs review: {candidate.current_mentions} {current_label}, "
    f"{candidate.baseline_mentions} {baseline_label}, "
    f"{candidate.distinct_sources} {source_label}. "
    f"{_candidate_component_summary(candidate)}"
),
```

Do not change tracked entity or source caveat summaries.

- [ ] **Step 3: Run GREEN focused tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_report_includes_stable_daily_brief_json_shape \
  tests/test_reports.py::test_markdown_report_renders_daily_brief_before_top_signals \
  tests/test_reports.py::test_daily_brief_candidate_summary_includes_existing_score_components \
  -q
```

Expected: all selected tests pass.

## Task 3: Docs And Changelog

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update README Daily Brief wording**

In the generated reports Daily Brief paragraph, add that candidate phrases can
include `candidate score-component cues` for `mentions, growth, and source
diversity`.

- [ ] **Step 2: Update CLI reference report/run wording**

In `docs/cli-reference.md`, update `report` and `run` descriptions to mention
`candidate score-component cues` in the Daily Brief Heat Narrative where
available, using the phrase `mentions, growth, and source diversity`.

- [ ] **Step 3: Update architecture report component wording**

In `docs/architecture.md`, update the Reports bullet to mention Daily Brief
`candidate score-component cues` derived from existing report rows, using the
phrase `mentions, growth, and source diversity`.

- [ ] **Step 4: Add a focused docs guard**

Do not extend `DAILY_BRIEF_REQUIRED_PHRASES`; that tuple is asserted against
every file in `DAILY_BRIEF_DOCS` and would require unrelated docs such as
`docs/daily-digest.md` and `docs/github-upload-checklist.md` to mention this
narrow Stage 209 cue. Instead, add a focused docs test:

```python
def test_daily_brief_docs_describe_candidate_score_component_cues() -> None:
    for path in (README, CLI_REFERENCE, ARCHITECTURE_DOC):
        normalized = _normalized_doc_text(path).casefold()
        assert "daily brief" in normalized
        assert "candidate score-component cues" in normalized
        assert "mentions, growth, and source diversity" in normalized
```

Use the exact wording in README/CLI/architecture to avoid brittle mismatches.

- [ ] **Step 5: Add changelog entry**

Add this entry under `[Unreleased] -> Added`:

```markdown
- Stage 209 adds local candidate score-component cues to generated Daily Brief
  candidate summaries, without changing scoring, ranking, report schemas,
  source acquisition, dashboard behavior, social/platform connectors, scraping,
  demand proof, platform coverage verification, dependency files, or
  compliance-review behavior.
```

- [ ] **Step 6: Run docs-focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/reports.py tests/test_reports.py README.md docs/architecture.md docs/cli-reference.md tests/test_cli_docs.py CHANGELOG.md
uv --no-config run --frozen ruff format --check src/fashion_radar/reports.py tests/test_reports.py
```

Expected: selected tests and lint/format checks pass.

## Task 4: Code Review And Fixes

**Files:**

- Add: `docs/reviews/opencode-stage-209-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-209-code-review.md`
- Add if needed: `docs/reviews/opencode-stage-209-code-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-209-code-rereview.md`

- [ ] **Step 1: Create the code-review prompt**

Create `docs/reviews/opencode-stage-209-code-review-prompt.md` describing the
Stage 209 goal, baseline SHA, changed files, RED/GREEN evidence, and review
focus.

- [ ] **Step 2: Run OpenCode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-209-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-209-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before Task 5.

## Task 5: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-209-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-209-release-review.md`
- Add if needed: `docs/reviews/opencode-stage-209-release-rereview-prompt.md`
- Add if needed: `docs/reviews/opencode-stage-209-release-rereview.md`

- [ ] **Step 1: Run full verification**

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

Expected: every command exits 0, with no lockfile or dependency changes.

- [ ] **Step 2: Create the release-review prompt**

Create `docs/reviews/opencode-stage-209-release-review-prompt.md` summarizing
the Stage 209 changes, full verification evidence, review artifacts, and release
hygiene scope.

- [ ] **Step 3: Run OpenCode release review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-209-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-209-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and run a rereview before committing.

- [ ] **Step 4: Stage and inspect the release diff**

Run:

```bash
git add CHANGELOG.md README.md docs/architecture.md docs/cli-reference.md \
  docs/reviews/opencode-stage-209-*.md \
  docs/superpowers/plans/2026-06-26-stage-209-daily-brief-candidate-component-cues-plan.md \
  src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py
git diff --cached --check
git diff --cached | rg -n "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|xox[baprs]-[A-Za-z0-9-]{20,}|sk-[A-Za-z0-9]{20,}" || true
```

Expected: whitespace check exits 0 and the secret scan returns no matches.

- [ ] **Step 5: Commit and push**

Run:

```bash
git commit -m "Stage 209: add daily brief candidate component cues"
git push origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: local `main` and `origin/main` point to the same new Stage 209 commit,
with a clean working tree.

## Self-Review Checklist

- This plan closes a Daily Brief explainability gap in the local
  `collect -> match -> report` pipeline.
- The plan uses existing candidate score components and does not change the
  scoring formula, ranking, extraction, thresholds, or candidate report model.
- The plan is summary-only for Daily Brief and does not add new
  `DailyBriefItem` fields or change `daily-brief/v1`.
- The plan keeps language local/review-oriented and avoids demand or platform
  coverage claims.
- The plan avoids source acquisition, social/platform connectors, scraping,
  browser automation, cookies/tokens, dependency, lockfile, DB schema,
  dashboard, and compliance-review product work.
- The plan includes RED tests before production-code changes.
- The plan includes OpenCode plan/code/release review gates.
- The plan includes full release verification and secret-scan hygiene before
  push.
