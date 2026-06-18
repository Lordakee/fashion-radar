# Stage 79 Onboarding Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve first-time GitHub onboarding docs with a short README start path, first-run chooser table, CLI beginner roadmap, and entity-pack sequence note.

**Architecture:** Docs and docs drift tests only. The changes clarify existing local command flows and boundaries without changing runtime CLI behavior or adding source/platform capabilities.

**Tech Stack:** Markdown, pytest, uv, ruff.

**Review Protocol Note:** The current stage-local review instruction for Stage
79 is to use local opencode with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. Keep that instruction in Stage 79
planning and review artifacts only. Do not alter `AGENTS.md`,
`docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md`. Public
`uv.lock` must remain free of mirror-bound URLs per `AGENTS.md`; the
pre-existing local `uv.lock` mirror rewrite is not part of this stage and must
not be staged.

---

## File Map

- Modify `README.md`
  - Add `## Start Here` before `## What It Does`.
- Modify `docs/first-run.md`
  - Add a four-row chooser table under `## Choose Your First Run`.
- Modify `docs/cli-reference.md`
  - Add `## Beginner Roadmap` before `## Shared Path Options`.
- Modify `docs/entity-packs.md`
  - Clarify optional local matching-layer sequence.
- Modify `tests/test_cli_docs.py`
  - Add docs drift tests for the new onboarding sections.
- Modify `CHANGELOG.md`
  - Add Stage 79 entry.
- Create review artifacts:
  - `docs/reviews/opencode-stage-79-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-79-plan-review.md`
  - `docs/reviews/opencode-stage-79-code-review-prompt.md`
  - `docs/reviews/opencode-stage-79-code-review.md`
- Do not modify:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
  - `uv.lock`

## Task 1: Add Failing Docs Drift Tests

**Files:**
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add README start-here test**

Add near existing README first-run tests:

```python
def test_readme_start_here_points_to_recommended_first_run_path() -> None:
    text = _read(README)
    normalized = _normalized_doc_text(README).casefold()

    start_here = text.split("## Start Here", 1)[1].split("## What It Does", 1)[0]

    assert text.index("## Start Here") < text.index("## What It Does")
    for term in (
        "[docs/first-run.md](docs/first-run.md)",
        "Manual repo-local sample",
        "recommended first-time path",
        "inspectable output",
        "dashboard data",
        "Automated source-checkout smoke",
        "Installed-wheel smoke",
        "[docs/entity-packs.md](docs/entity-packs.md)",
    ):
        assert term in start_here

    for term in (
        "verification paths",
        "optional local matching layer",
        "after `init` and before `match`/`report`",
        "local-first",
        "does not add live platform collection",
        "does not add social connectors",
    ):
        assert term in normalized
```

- [ ] **Step 2: Add first-run chooser table test**

Add near `test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries`:

```python
def test_first_run_guide_has_beginner_path_chooser() -> None:
    text = _read(FIRST_RUN_DOC)
    normalized = _normalized_doc_text(FIRST_RUN_DOC).casefold()

    chooser = text.split("## Choose Your First Run", 1)[1].split(
        "## Prepare A Source Checkout",
        1,
    )[0]

    for term in (
        "| Path | Use When | Writes To | Start Here |",
        "Manual repo-local sample",
        "Recommended first-time path",
        "`data/` and `reports/` under this checkout",
        "Automated source-checkout smoke",
        "temporary config/data/report/export directories",
        "Installed-wheel smoke",
        "temporary virtual environment",
        "Reset repo-local sample",
        "generated repo-local sample files",
    ):
        assert term in chooser

    for term in (
        "manual repo-local sample when you want inspectable output",
        "automated source-checkout smoke when you want disposable verification",
        "installed-wheel smoke when you need package verification",
        "reset repo-local sample after local experiments",
        "does not run live collection",
    ):
        assert term in normalized
```

- [ ] **Step 3: Add CLI roadmap test**

Add near CLI reference docs tests:

```python
def test_cli_reference_has_beginner_roadmap_with_existing_commands() -> None:
    text = _read(CLI_REFERENCE)
    normalized = _normalized_doc_text(CLI_REFERENCE).casefold()

    roadmap = text.split("## Beginner Roadmap", 1)[1].split(
        "## Shared Path Options",
        1,
    )[0]

    for term in (
        "| Phase | Existing Commands | Where To Read Next |",
        "Setup",
        "`init`, `migrate-db`, `doctor`",
        "Local sample/import",
        "`community-signal-lint`, `import-signals`, `import-signals-dir`",
        "Match/report/review",
        "`match`, `report`, `candidates`, `trends`, `imported-signals`",
        "Dashboard",
        "`dashboard`",
        "Cleanup",
        "Reset The Repo-Local Sample",
        "[first-run.md](first-run.md)",
        "[entity-packs.md](entity-packs.md)",
    ):
        assert term in roadmap

    for term in (
        "roadmap uses existing commands only",
        "does not add live collection",
        "does not add platform automation",
        "does not add connectors",
    ):
        assert term in normalized
```

- [ ] **Step 4: Add entity-pack sequence test**

Extend `test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack` or
add a nearby focused test:

```python
def test_entity_pack_docs_describe_optional_matching_layer_sequence() -> None:
    text = _read(ENTITY_PACKS_DOC)
    normalized = _normalized_doc_text(ENTITY_PACKS_DOC).casefold()

    intro = text.split("## Lint The Pack", 1)[0]

    for term in (
        "optional local matching layer",
        "after `init`",
        "before your first `match` and `report`",
        "broader watchlist",
        "configs/entity-packs/fashion-watchlist.example.yaml",
    ):
        assert term in intro

    for term in (
        "only changes local entity matching",
        "does not add sources",
        "does not add ingestion",
        "does not add live collection",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
    ):
        assert term in normalized
```

- [ ] **Step 5: Run tests and verify they fail before docs are updated**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_readme_start_here_points_to_recommended_first_run_path \
  tests/test_cli_docs.py::test_first_run_guide_has_beginner_path_chooser \
  tests/test_cli_docs.py::test_cli_reference_has_beginner_roadmap_with_existing_commands \
  tests/test_cli_docs.py::test_entity_pack_docs_describe_optional_matching_layer_sequence \
  -q
```

Expected before docs updates: failures because the new docs sections are
missing or incomplete.

## Task 2: Add Onboarding Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/first-run.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/entity-packs.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add README Start Here section**

Insert after the opening two paragraphs and before `## What It Does`:

```markdown
## Start Here

For first-run onboarding, start with [docs/first-run.md](docs/first-run.md).
The Manual repo-local sample is the recommended first-time path when you want
inspectable output, local SQLite state, dated reports, and dashboard data.

Use Automated source-checkout smoke or Installed-wheel smoke as verification
paths when you need disposable source-tree or package checks. They are not the
main exploratory path.

Entity packs are an optional local matching layer. Copy one after `init` and
before `match`/`report` when you want a broader local watchlist; see
[docs/entity-packs.md](docs/entity-packs.md).

All onboarding paths are local-first. This does not add live platform
collection, does not add social connectors, and does not prove demand, rank
brands, or verify platform coverage.
```

- [ ] **Step 2: Add first-run chooser table**

In `docs/first-run.md`, under `## Choose Your First Run`, add:

```markdown
| Path | Use When | Writes To | Start Here |
| --- | --- | --- | --- |
| Manual repo-local sample | Recommended first-time path when you want inspectable output, local SQLite state, dated reports, and dashboard data. | `data/` and `reports/` under this checkout. | [Manual Repo-Local Sample Flow](#manual-repo-local-sample-flow) |
| Automated source-checkout smoke | Disposable verification for the current source checkout. | temporary config/data/report/export directories. | [Automated First-Run Smoke](#automated-first-run-smoke) |
| Installed-wheel smoke | Package verification when you need to test the built wheel. | Temporary build directory and temporary virtual environment. | [Installed-Wheel Smoke](#installed-wheel-smoke) |
| Reset repo-local sample | Cleanup after local experiments. | Removes generated repo-local sample files and keeps placeholder READMEs. | [Reset The Repo-Local Sample](#reset-the-repo-local-sample) |
```

Replace or extend the explanatory paragraphs below the table so the chooser text
contains these exact normalized phrases:

```markdown
Choose the manual repo-local sample when you want inspectable output, local
SQLite state, dated reports, and dashboard data.

Use automated source-checkout smoke when you want disposable verification for
the current source checkout.

Use installed-wheel smoke when you need package verification for the built
wheel.

Use reset repo-local sample after local experiments when you want to remove the
generated sample files and keep the placeholder READMEs.

This chooser does not run live collection, source acquisition, scraping,
browser automation, platform APIs, or connector behavior.
```

- [ ] **Step 3: Add CLI beginner roadmap**

In `docs/cli-reference.md`, before `## Shared Path Options`, add:

```markdown
## Beginner Roadmap

This roadmap uses existing commands only. It does not add live collection, does
not add platform automation, does not add connectors, does not add demand proof,
does not add ranking, and does not add platform coverage verification.

| Phase | Existing Commands | Where To Read Next |
| --- | --- | --- |
| Setup | `init`, `migrate-db`, `doctor` | [first-run.md](first-run.md) |
| Local sample/import | `community-signal-lint`, `import-signals`, `import-signals-dir` | [first-run.md](first-run.md) |
| Match/report/review | `match`, `report`, `candidates`, `trends`, `imported-signals` | [first-run.md](first-run.md) |
| Dashboard | `dashboard` | [first-run.md](first-run.md) |
| Cleanup | `init` for regeneration, plus the `Reset The Repo-Local Sample` commands in the first-run guide | [first-run.md](first-run.md#reset-the-repo-local-sample) |

Use [entity-packs.md](entity-packs.md) after setup if you want an optional
broader local watchlist before matching and reporting.
```

- [ ] **Step 4: Clarify entity-pack sequence**

In `docs/entity-packs.md`, update the opening paragraphs before `## Lint The
Pack` to include:

```markdown
Entity packs are an optional local matching layer. Copy one after `init` and
before your first `match` and `report` when you want a broader watchlist than
the starter `entities.yaml`.
```

Also extend the boundary paragraph near the top or `Use The Pack` section so it
contains:

```markdown
The pack only changes local entity matching. It does not add sources, does not
add ingestion, does not add live collection, does not prove demand, does not
rank brands, and does not verify platform coverage.
```

- [ ] **Step 5: Add changelog entry**

Under `### Added` in `CHANGELOG.md`, add:

```markdown
- Stage 79 onboarding roadmap docs for first-time GitHub users, with a README
  start path, first-run chooser, CLI beginner roadmap, and clearer optional
  entity-pack sequence. This is docs/test-only, does not add live platform
  collection, does not add connectors, does not add demand proof, does not add
  ranking, and does not add platform coverage verification.
```

- [ ] **Step 6: Run focused docs checks**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_readme_start_here_points_to_recommended_first_run_path \
  tests/test_cli_docs.py::test_first_run_guide_has_beginner_path_chooser \
  tests/test_cli_docs.py::test_cli_reference_has_beginner_roadmap_with_existing_commands \
  tests/test_cli_docs.py::test_entity_pack_docs_describe_optional_matching_layer_sequence \
  -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected after docs updates: all pass.

## Task 3: Review, Verification, Commit, And Publish

**Files:**
- Add: `docs/reviews/opencode-stage-79-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-79-plan-review.md`
- Add: `docs/reviews/opencode-stage-79-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-79-code-review.md`

- [x] **Step 1: Run opencode plan review before implementation**

Create `docs/reviews/opencode-stage-79-plan-review-prompt.md` summarizing this
plan, the design spec, current boundaries, and the unchanged dirty `uv.lock`
risk. Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-79-plan-review-prompt.md)" > docs/reviews/opencode-stage-79-plan-review.md
```

Fix Critical and Important findings before implementation. The stage-local
opencode plan review artifact is recorded in
`docs/reviews/opencode-stage-79-plan-review.md`; its blocking plan findings are
addressed in this plan before docs/source implementation begins.

- [ ] **Step 2: Run opencode code review after implementation**

Create `docs/reviews/opencode-stage-79-code-review-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-79-code-review-prompt.md)" > docs/reviews/opencode-stage-79-code-review.md
```

Fix Critical and Important findings before release verification.

- [ ] **Step 3: Run full verification**

Because this workspace may carry an out-of-stage mirror-rewritten `uv.lock`,
preserve that local file and temporarily restore the public HEAD lock before
running `UV_NO_CONFIG=1 uv lock --check`:

```bash
stage79_uv_lock_backup="$(mktemp)"
cp uv.lock "$stage79_uv_lock_backup"
git show HEAD:uv.lock > uv.lock
```

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
tmp_public_lock="$(mktemp)"
git show HEAD:uv.lock > "$tmp_public_lock"
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' "$tmp_public_lock"
rm -f "$tmp_public_lock"
! git diff --cached --name-only | rg -x 'uv.lock'
git diff --check
```

Restore the local mirror lock after verification and keep it unstaged:

```bash
cp "$stage79_uv_lock_backup" uv.lock
rm -f "$stage79_uv_lock_backup"
! git diff --cached --name-only | rg -x 'uv.lock'
```

- [ ] **Step 4: Stage only Stage 79 files**

Run:

```bash
git add README.md \
  docs/first-run.md \
  docs/cli-reference.md \
  docs/entity-packs.md \
  tests/test_cli_docs.py \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-18-stage-79-onboarding-roadmap-design.md \
  docs/superpowers/plans/2026-06-18-stage-79-onboarding-roadmap-plan.md \
  docs/reviews/opencode-stage-79-plan-review-prompt.md \
  docs/reviews/opencode-stage-79-plan-review.md \
  docs/reviews/opencode-stage-79-code-review-prompt.md \
  docs/reviews/opencode-stage-79-code-review.md
```

Do not stage `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`,
`docs/github-upload-checklist.md`, or `uv.lock`.

Then run:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] **Step 5: Commit and publish through GitHub Git Data API**

Commit:

```bash
git commit -m "Clarify onboarding roadmap"
```

Publish using the existing GitHub Git Data API flow with token read only from
`/home/ubuntu/.config/fashion-radar/github-token`, `force:false`, no token in
remote URLs, and no persistent `http.*.extraheader`.

- [ ] **Step 6: Verify remote and CI**

Run:

```bash
git fetch origin main
test "$(git rev-parse HEAD^{tree})" = "$(git rev-parse origin/main^{tree})"
test "$(git remote get-url origin)" = "https://github.com/Lordakee/fashion-radar.git"
git config --show-origin --get-regexp '^http\..*\.extraheader$' && exit 1 || true
git config --show-origin --list | rg -i 'gh[pousr]_|github_pat_|x-access-token|authorization' && exit 1 || true
! git diff --cached --name-only | rg -x 'uv.lock'
```

Poll the latest `main` GitHub Actions run and require `completed success`.
