# Stage 29 Community Candidate Directory Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document `fashion-radar community-candidates-dir` as a local, read-only, non-recursive, aggregate-only pre-import candidate phrase preview for batches of community signal handoff files.

**Architecture:** Documentation-only update across existing user docs. Add the directory preview command next to the existing single-file `community-candidates`, directory lint, and directory import dry-run docs. Preserve the local-first/source-boundary language and avoid suggesting platform collection or source acquisition.

**Tech Stack:** Markdown docs, existing CLI behavior from Stage 28, `rg` boundary checks, `git diff --check`.

---

## Stage 29 Boundary

In scope:

- README and changelog docs.
- Community signal import/quality docs.
- Candidate discovery, architecture, source-boundary docs.
- GitHub upload checklist.
- Docs-only verification.

Out of scope:

- production code changes;
- test changes;
- config/example/schema changes;
- dependency or `uv.lock` changes;
- release build, wheel smoke, commit, or push.

## Task 0: Read-Only Preflight State Check

**Files:**
- No file edits.

- [ ] **Step 1: Check current source/test/lock diffs without writing snapshots**

Run:

```bash
git status --short --branch
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py
git status --short -- uv.lock
git diff -- uv.lock
git diff --cached -- uv.lock
```

Expected: commands exit `0`. Source/test diff should be empty because Stage 28
was committed and pushed. `uv.lock` may still contain the known mirror diff and
must not be staged. `git diff --cached -- uv.lock` must be empty.

## Task 1: README And Changelog

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add README quickstart examples**

In the community tool command block, add:

```bash
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

- [ ] **Step 2: Add README explanatory paragraph**

Add near the `community-candidates` paragraph:

```markdown
`community-candidates-dir` is local and read-only. It previews aggregate
candidate phrase metrics from matched regular CSV/JSON handoff files directly
under one supplied directory before import. It does not recurse, import rows,
open SQLite, fetch URLs, print the supplied directory path, expose matched file
paths, expose matched file names, or expose row URLs, row titles, summaries,
raw text, normalized keys, candidate contexts, raw validation findings,
account/private fields, or representative item details. The output is not proof
of demand, not platform coverage, and not source ranking.
```

- [ ] **Step 3: Add changelog entry**

Add:

```markdown
- Added `community-candidates-dir` for local non-recursive pre-import candidate
  phrase previews from matched community signal handoff files in one directory.
```

## Task 2: Community Signal Docs

**Files:**
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`

- [ ] **Step 1: Update import docs**

After the single-file `community-candidates` examples, add:

```bash
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir ./exports --input-format json --pattern "*.json" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Add prose:

```markdown
`community-candidates-dir` reads matched regular files directly under one local
directory and local config, then prints aggregate-only candidate phrase metrics
before import. It does not recurse, import rows, open SQLite, fetch URLs, print
the supplied directory path, expose matched file paths, expose matched file
names, or expose row URLs, row titles, summaries, raw text, normalized keys,
candidate contexts, raw validation findings, account/private fields, or
representative item details.
```

- [ ] **Step 2: Update quality docs recommended order**

Insert `community-candidates-dir` after strict directory lint and before
`import-signals-dir --dry-run`:

```bash
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
```

Add prose:

```markdown
Use `community-candidates-dir` when a local directory batch passes strict lint
and you want an aggregate preview of candidate phrases before import. It reports
only aggregate candidate phrase metrics and keeps the supplied directory path,
matched file paths, matched file names, row URLs, row titles, summaries, raw
text, normalized keys, candidate contexts, raw validation findings,
account/private fields, and representative item details out of output.
```

## Task 3: Candidate Discovery, Architecture, Boundaries, Checklist

**Files:**
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Candidate discovery doc**

Extend the Community Candidate Preview section:

```markdown
`community-candidates-dir` is the batch counterpart for matched regular
CSV/JSON files directly under one local directory. It uses the same in-memory
candidate extraction and configured-entity suppression, but it does not recurse,
open SQLite, consult stored matches, import rows, write reports, expose matched
file paths, expose matched file names, expose account/private fields, or expose
representative items. The preview is aggregate-only and is limited to the
matched local files.
```

- [ ] **Step 2: Architecture doc**

Add `community-candidates-dir` to the command-flow example between
`community-signal-lint-dir` and `import-signals-dir --dry-run`:

```bash
fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
```

Add a short architecture note:

```markdown
`community-candidates-dir` is an in-memory pre-import preview over matched
regular files directly under one local directory. It sits before manual
directory import and does not write database, report, config, entity, or
dashboard state.
```

- [ ] **Step 3: Source boundaries doc**

Add:

```markdown
`community-candidates-dir` reads matched regular CSV/JSON handoff files directly
under one local directory plus local config and prints aggregate candidate
phrase metrics. It does not recurse, import rows, open SQLite, fetch URLs, log
in, write reports, update dashboards, generate entity files, print the supplied
directory path, expose matched file paths, expose matched file names, or expose
row URLs, row titles, summaries, raw text, normalized keys, candidate contexts,
raw validation findings, account/private fields, or representative item details.

`community-candidates-dir` is not proof of demand, not platform coverage, not
source ranking, not a source connector, not an acquisition workflow, not a
scraper, not a watcher, not a scheduler, not a report writer, not a dashboard
updater, not a database import, and not an entity YAML generator.
```

- [ ] **Step 4: Upload checklist**

Add:

```markdown
- [ ] `community-candidates-dir` docs describe local non-recursive directory
      preview, aggregate-only output, no SQLite writes, no URL fetching, and no
      supplied directory path, matched file path, matched file name, row URL,
      row title, summary, raw text, normalized key, candidate context, raw
      validation finding, account/private field, or representative item detail
      exposure.
```

## Task 4: Docs-Only Verification

**Files:**
- No source edits.

- [ ] **Step 1: Prove only docs changed**

Run:

```bash
git diff --name-only -- . ':!uv.lock'
git diff --cached --name-only -- . ':!uv.lock'
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py
git diff --cached -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py
git status --short -- uv.lock
git diff -- uv.lock
git diff --cached -- uv.lock
```

Expected: only approved docs are listed outside `uv.lock`, whether staged or
unstaged; source/test diffs are empty. Stage 29 must not stage or commit
`uv.lock`. Any pre-existing unstaged `uv.lock` mirror diff must remain untouched
and be called out in the handoff.

- [ ] **Step 2: Required docs checks**

Run:

```bash
rg -n "community-candidates-dir" README.md CHANGELOG.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md
rg -n "matched regular files directly under one local directory|does not recurse|aggregate-only|supplied directory path|matched file paths|matched file names|raw validation findings" README.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md
git diff --check
git diff --cached --check
```

Expected: every command exits `0`.

- [ ] **Step 3: Unsafe implication scan**

Run:

```bash
git diff -- README.md CHANGELOG.md docs/community-signal-import.md docs/community-signal-quality.md docs/candidate-discovery.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md | rg -n "platform coverage|proof of demand|source ranking|source acquisition|acquisition workflow|source collection|collect sources|collecting sources|source connector|scrape|scrapes|scraped|scraper|scraping|monitor|monitors|monitored|monitoring|watcher|watchers|schedule|scheduled|scheduler|schedulers|scheduling|database import|write database|writes database|database writes|database state|SQLite writes|report writer|report generation|write reports|writes reports|wrote reports|generate reports|generates reports|dashboard updater|dashboard updates|update dashboards|updates dashboards|updated dashboards|dashboard generation|dashboard generator|generate dashboards|generates dashboards|entity YAML generator|entity YAML generation|entity generation|entity file generation|generate entity files|generates entity files"
```

Expected: matches are only negative boundary statements such as `not platform
coverage` or `not a scheduler`; no positive capability claims.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- uncommitted files;
- next step.
