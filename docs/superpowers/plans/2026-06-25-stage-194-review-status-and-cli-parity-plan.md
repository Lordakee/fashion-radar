# Stage 194 Review Status And CLI Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backfill the remaining `trend-explanations` baseline date CLI coverage and correct stale current roadmap/status wording after Stages 190-193.

**Architecture:** Keep the stage test/docs-only unless focused tests reveal a real production regression. Mirror the existing `trends` `--baseline-as-of` CLI tests for `trend-explanations`, then update current direction/status documents so they point to source-liveness-backed curated public-source coverage and deterministic matching quality instead of completed source-liveness or trend-explanation work.

**Tech Stack:** Python 3.11, Typer CLI tests through `CliRunner`, pytest, Markdown docs, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`, Codex subagent cross-checks with reasoning effort `xhigh`.

---

## Files

- Modify: `tests/test_cli.py`
- Modify: `tests/test_review_protocol_docs.py`
- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `README.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`
- Add: `docs/superpowers/specs/2026-06-25-stage-194-review-status-and-cli-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-25-stage-194-review-status-and-cli-parity-plan.md`
- Add after plan review: `docs/reviews/opencode-stage-194-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-194-plan-review.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-194-plan-rereview-prompt.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-194-plan-rereview.md`
- Add after implementation: `docs/reviews/opencode-stage-194-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-194-code-review.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-194-code-rereview-prompt.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-194-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-194-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-194-release-review.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-194-release-rereview-prompt.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-194-release-rereview.md`

## Task 1: Plan Review

**Files:**

- Add: `docs/reviews/opencode-stage-194-plan-review-prompt.md`
- Add after command: `docs/reviews/opencode-stage-194-plan-review.md`
- Modify if needed: `docs/superpowers/specs/2026-06-25-stage-194-review-status-and-cli-parity-design.md`
- Modify if needed: `docs/superpowers/plans/2026-06-25-stage-194-review-status-and-cli-parity-plan.md`

- [ ] **Step 1: Create the plan-review prompt**

Create `docs/reviews/opencode-stage-194-plan-review-prompt.md` with:

```markdown
Review the Stage 194 design and implementation plan for /home/ubuntu/fashion-radar before coding.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

Read:
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/reviews/opencode-stage-193-code-rereview.md`
- `docs/reviews/opencode-stage-193-release-review.md`
- `docs/reviews/opencode-full-project-review.md`
- `docs/PROJECT_BRIEF.md`
- `README.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/architecture.md`
- `docs/superpowers/specs/2026-06-25-stage-194-review-status-and-cli-parity-design.md`
- `docs/superpowers/plans/2026-06-25-stage-194-review-status-and-cli-parity-plan.md`
- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `tests/test_review_protocol_docs.py`

Review questions:
1. Does this plan correctly treat the Stage 193 `--baseline-as-of` note as a coverage parity gap rather than a known production defect?
2. Are the two planned `trend-explanations` CLI tests the right mirrors of the existing `trends` invalid baseline and baseline ordering tests?
3. Is the plan correct to avoid production code edits unless those focused tests reveal a real regression?
4. Does the full-project review update stay limited to `Current Follow-Up Status` while preserving the historical findings and recommendations?
5. Does the updated project direction correctly mark Stage 190 source-liveness and Stage 193 trend/heat explanation work complete and redirect next work toward source-liveness-backed curated public-source coverage and deterministic matching quality without claiming demand proof or platform coverage verification?
6. Does the plan avoid new external-tool/community/imported surfaces and avoid platform collection, scraping, browser automation, platform APIs, monitoring, scheduling, ranking, demand proof, coverage verification, and compliance-review product features?

Respond with:
- Critical findings
- Important findings
- Minor findings
- Verdict

Critical or Important findings block implementation. If the plan is acceptable, say explicitly:
APPROVED FOR STAGE 194 IMPLEMENTATION
```

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-194-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-194-plan-review.md
rm -f "$tmp_review"
```

Expected: the review contains one coherent body and either
`APPROVED FOR STAGE 194 IMPLEMENTATION` or concrete Critical/Important findings.

- [ ] **Step 3: Fix plan blockers if any**

If the review reports Critical or Important findings, update the design and/or
plan directly, create `docs/reviews/opencode-stage-194-plan-rereview-prompt.md`
summarizing the fixes, rerun opencode into
`docs/reviews/opencode-stage-194-plan-rereview.md`, and do not continue until
the rereview approves implementation.

## Task 2: CLI Coverage Parity

**Files:**

- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add coverage tests for `trend-explanations --baseline-as-of`**

Add these tests after
`test_trend_explanations_command_invalid_as_of_writes_nothing`:

```python
def test_trend_explanations_command_invalid_baseline_writes_nothing(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Could not explain trend deltas: invalid --baseline-as-of" in result.output
    assert not data_dir.exists()
```

Add this immediately after it:

```python
def test_trend_explanations_command_rejects_baseline_at_or_after_as_of(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    config_dir.mkdir()
    (config_dir / "scoring.yaml").write_text("version: 1\nscoring: {}\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "trend-explanations",
            "--config-dir",
            str(config_dir),
            "--data-dir",
            str(data_dir),
            "--as-of",
            "2026-06-12T12:00:00Z",
            "--baseline-as-of",
            "2026-06-12T12:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "Could not explain trend deltas: baseline-as-of must be before as-of" in result.output
    assert not data_dir.exists()
```

- [ ] **Step 2: Run focused CLI tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli.py::test_trend_explanations_command_invalid_as_of_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_invalid_baseline_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_rejects_baseline_at_or_after_as_of \
  tests/test_cli.py::test_trend_explanations_command_invalid_config_writes_nothing \
  -q
```

Expected: all selected tests pass. If a new baseline test fails, inspect
`src/fashion_radar/cli.py::trend_explanations_command` and make the smallest
production fix needed to restore parity with `trends_command`.

## Task 3: Current Direction Guards And Documentation

**Files:**

- Modify: `tests/test_review_protocol_docs.py`
- Modify: `docs/reviews/opencode-full-project-review.md`
- Modify: `docs/PROJECT_BRIEF.md`
- Modify: `README.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update docs constants and the full-project review status guard**

In `tests/test_review_protocol_docs.py`, add these path constants after
`FULL_PROJECT_REVIEW`:

```python
PROJECT_BRIEF = ROOT / "docs" / "PROJECT_BRIEF.md"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "architecture.md"
```

In `tests/test_review_protocol_docs.py`, update
`test_full_project_review_follow_up_status_tracks_completed_stages` so the
required phrases include:

```python
        "Stage 192 polished Daily Brief source caveats",
        "Stage 193 added the read-only `trend-explanations` sidecar",
        "source-liveness evidence",
        "curated public-source coverage",
        "deterministic matching quality",
        "source coverage",
        "matching quality",
```

Remove the old required phrase:

```python
        "trend/heat explanation",
```

Add stale-phrase guards:

```python
    assert "add a local trend/heat explanation layer" not in normalized
    assert "trend/heat explanation layer without claiming demand proof" not in normalized
```

- [ ] **Step 2: Add a current-direction docs guard**

Add this test after
`test_full_project_review_follow_up_status_tracks_completed_stages`:

```python
def test_current_direction_docs_prioritize_liveness_backed_source_coverage() -> None:
    sections = {
        "docs/PROJECT_BRIEF.md##Current Review-Aligned Priorities": _section(
            _read(PROJECT_BRIEF), "Current Review-Aligned Priorities"
        ),
        "README.md##Current Roadmap Focus": _section(
            _read(README), "Current Roadmap Focus"
        ),
        "docs/REVIEW_PROTOCOL.md##During Development": _section(
            _read(REVIEW_PROTOCOL), "During Development"
        ),
        "docs/architecture.md": _read(ARCHITECTURE),
    }

    for label, text in sections.items():
        normalized = _normalized_text(text).casefold()
        for phrase in (
            "source-liveness evidence",
            "curated public-source coverage",
            "deterministic matching quality",
        ):
            assert phrase in normalized, f"{label} is missing {phrase!r}"

    stale_phrases = (
        "add read-only source-health/feed-liveness diagnostics",
        "source coverage/health",
        "source-health visibility",
        "optional summarization are improved",
        "optional summary work over",
    )
    for label, text in sections.items():
        normalized = _normalized_text(text).casefold()
        for phrase in stale_phrases:
            assert phrase not in normalized, f"{label} still has stale phrase {phrase!r}"

    assert "experimental/community handoff expansion remains frozen" in _normalized_text(
        sections["docs/PROJECT_BRIEF.md##Current Review-Aligned Priorities"]
    ).casefold()
    assert "no new external-tool, community-handoff, or imported-review" in _normalized_text(
        sections["README.md##Current Roadmap Focus"]
    ).casefold()
```

- [ ] **Step 3: Run the focused docs guards and confirm they fail before docs edits**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_review_protocol_docs.py::test_full_project_review_follow_up_status_tracks_completed_stages \
  tests/test_review_protocol_docs.py::test_current_direction_docs_prioritize_liveness_backed_source_coverage \
  -q
```

Expected before the docs edit: failures showing the Stage 192/Stage 193 status
phrases are missing from `docs/reviews/opencode-full-project-review.md` and
the current direction docs still contain stale source-health/roadmap phrasing.

- [ ] **Step 4: Update only the full-project review follow-up status**

Replace only the bullet list under `## Current Follow-Up Status` in
`docs/reviews/opencode-full-project-review.md` with:

```markdown
- Stage 188 fixed the proxy-sensitive tests and redirected roadmap docs.
- Stage 189 fixed review-capture hygiene gaps exposed by this review record and
  the Stage 188 review chain.
- Stage 190 added source-liveness diagnostics for configured public sources.
- Stage 191 added the Daily Brief Heat Narrative to generated daily reports.
- Stage 192 polished Daily Brief source caveats and refreshed this follow-up
  status.
- Stage 193 added the read-only `trend-explanations` sidecar over existing
  local trend deltas without changing trend or heat contracts.
- The next product work should use source-liveness evidence to expand curated
  public-source coverage and improve deterministic matching quality, without
  claiming demand proof or platform coverage verification.
```

- [ ] **Step 5: Update current roadmap and protocol docs**

In `docs/PROJECT_BRIEF.md`, replace the start of `## Current Review-Aligned
Priorities` and its bullet list with:

```markdown
Before expanding any experimental or community handoff surface, the remaining
roadmap priorities are:

- use read-only source-liveness evidence to expand curated public-source
  coverage, especially celebrity style, street style, designer/luxury, and
  emerging-brand monitoring;
- improve deterministic matching quality for case, diacritics, and entity
  disambiguation;
- keep further report summary or explanation refinements optional, local, and
  post-core.

Experimental/community handoff expansion remains frozen while these remaining
core gaps are addressed.
```

In `README.md`, replace the paragraph under `## Current Roadmap Focus` with:

```markdown
Near-term v0.1.x work is focused on the core pipeline: using source-liveness
evidence to broaden curated public-source coverage and improving deterministic
matching quality. Further report summary or explanation refinements should stay
optional, local, and post-core. No new external-tool, community-handoff, or
imported-review surface area is planned unless a release-blocking defect
requires maintenance.
```

In `docs/REVIEW_PROTOCOL.md`, replace the v0.1.x priority paragraph under
`## During Development` with:

```markdown
For the current v0.1.x release track, stage proposals should prioritize curated
public-source coverage using source-liveness evidence and deterministic
matching quality. Further local report summary or explanation refinements
should stay optional and contract-safe. Changes to `external-tool-*`,
`community-handoff-*`, or `imported-*` commands should be treated as frozen
unless they fix a release-blocking defect or a correctness issue in existing
behavior.
```

In `docs/architecture.md`, replace the current architecture-priority paragraph
inside the `Manual Import` section with:

```markdown
  Current architecture priority is the collect -> match -> score -> report
  pipeline. The external/community handoff path remains documented and
  supported, but near-term roadmap work is paused there while curated
  public-source coverage is expanded using source-liveness evidence and
  deterministic matching quality is improved. Optional report summary or
  explanation refinements remain post-core and contract-safe.
```

- [ ] **Step 6: Add changelog note**

In `CHANGELOG.md`, add this bullet at the top of `## [Unreleased]` →
`### Fixed`:

```markdown
- Stage 194 refreshes current roadmap and full-project review follow-up status
  after completed Stages 190-193, and backfills `trend-explanations` baseline
  date error coverage without expanding external/community/imported surfaces.
```

- [ ] **Step 7: Run focused docs/test checks**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_review_protocol_docs.py::test_full_project_review_follow_up_status_tracks_completed_stages \
  tests/test_review_protocol_docs.py::test_current_direction_docs_prioritize_liveness_backed_source_coverage \
  tests/test_cli.py::test_trend_explanations_command_invalid_baseline_writes_nothing \
  tests/test_cli.py::test_trend_explanations_command_rejects_baseline_at_or_after_as_of \
  -q
```

Expected: all selected tests pass.

## Task 4: Code Review

**Files:**

- Add: `docs/reviews/opencode-stage-194-code-review-prompt.md`
- Add after command: `docs/reviews/opencode-stage-194-code-review.md`
- Add rereview artifacts if needed.

- [ ] **Step 1: Run focused verification before code review**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py tests/test_review_protocol_docs.py -q
uv --no-config run --frozen ruff check
uv --no-config run --frozen ruff format --check
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Create code-review prompt**

Create `docs/reviews/opencode-stage-194-code-review-prompt.md` with:

```markdown
Review the Stage 194 implementation for /home/ubuntu/fashion-radar.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

Stage 194 goal:
- Backfill `trend-explanations` CLI coverage for invalid `--baseline-as-of` and `baseline-as-of >= as-of`.
- Update only the historical full-project review follow-up status so Stage 193 trend/heat explanations are marked complete.

Changed files expected:
- `tests/test_cli.py`
- `tests/test_review_protocol_docs.py`
- `docs/reviews/opencode-full-project-review.md`
- `docs/PROJECT_BRIEF.md`
- `README.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/architecture.md`
- `CHANGELOG.md`
- Stage 194 spec/plan/review artifacts.

Review questions:
1. Are the new CLI tests faithful mirrors of the existing `trends` baseline-date tests?
2. Do the tests assert command-specific error wording and no data-dir creation?
3. Did the implementation avoid production code edits unless justified by a real failing test?
4. Is the full-project review edit limited to `Current Follow-Up Status` and accurate after Stages 192 and 193?
5. Are README, PROJECT_BRIEF, REVIEW_PROTOCOL, and architecture current after Stage 190 source-liveness and Stage 193 trend-explanations?
6. Does the stage avoid new product surfaces, source acquisition, scraping, browser automation, platform APIs, monitoring, scheduling, ranking, demand proof, coverage verification, and compliance-review features?
7. Are there any Critical or Important issues before release review?

Respond with Critical, Important, Minor findings and a verdict.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-194-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-194-code-review.md
rm -f "$tmp_review"
```

Fix Critical or Important findings and rerun as
`docs/reviews/opencode-stage-194-code-rereview.md` before continuing.

## Task 5: Release Verification, Release Review, Commit, Push

**Files:**

- Add: `docs/reviews/opencode-stage-194-release-review-prompt.md`
- Add after command: `docs/reviews/opencode-stage-194-release-review.md`
- Add rereview artifacts if needed.

- [ ] **Step 1: Run release verification**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen ruff check
uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Create release-review prompt**

Create `docs/reviews/opencode-stage-194-release-review-prompt.md` with:

```markdown
Review Stage 194 for release readiness in /home/ubuntu/fashion-radar.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

Confirm:
1. No Critical or Important findings remain from plan/code review.
2. Review artifacts are coherent, complete, and free of live-capture stubs, duplicated/truncated text, empty output, tool-status messages, or duplicate verdicts.
3. The diff is limited to Stage 194 coverage/docs/status/changelog/review artifacts unless a focused test forced a production fix.
4. No source acquisition, scraping, browser automation, platform APIs, monitoring, scheduling, ranking, demand proof, platform coverage verification, compliance-review feature, or external/community/imported surface expansion was added.
5. It is acceptable to commit and push Stage 194.

Respond with Critical, Important, Minor findings and a verdict.
```

- [ ] **Step 3: Run local opencode release review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-194-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-194-release-review.md
rm -f "$tmp_review"
```

Fix Critical or Important findings and rerun as
`docs/reviews/opencode-stage-194-release-rereview.md` before committing.

- [ ] **Step 4: Secret and status checks**

Run:

```bash
git status --short
git diff --cached --name-only
rg -n "ghp_|github_pat_|Authorization:|extraheader|BEGIN [A-Z ]*PRIVATE KEY|COOKIE|SESSION" .
```

Expected: only Stage 194 intended files are unstaged/staged as appropriate;
the secret scan has no live secrets. Historical prompt examples without live
secrets may exist and should be inspected before staging if matched.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add \
  tests/test_cli.py \
  tests/test_review_protocol_docs.py \
  docs/reviews/opencode-full-project-review.md \
  docs/PROJECT_BRIEF.md \
  README.md \
  docs/REVIEW_PROTOCOL.md \
  docs/architecture.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-25-stage-194-review-status-and-cli-parity-design.md \
  docs/superpowers/plans/2026-06-25-stage-194-review-status-and-cli-parity-plan.md \
  docs/reviews/opencode-stage-194-*.md
git commit -m "fix: close trend explanation parity gap"
git push origin main
```

- [ ] **Step 6: Handoff Summary**

Report:

- repo state;
- verified commands;
- committed SHA;
- pushed remote branch;
- uncommitted files, if any;
- recommended next step.
