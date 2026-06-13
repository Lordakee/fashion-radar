# Stage 27B Community Candidate Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document `fashion-radar community-candidates` as a local one-file pre-import candidate phrase preview with clear output and boundary constraints.

**Architecture:** Documentation-only update across existing user docs. Reuse the established local-first/manual-import language and keep the command positioned as an optional pre-import preview between community file linting and manual import dry runs.

**Tech Stack:** Markdown docs, existing CLI command behavior from Stage 27A, `rg` boundary checks, Python stdlib diff classification, `git diff --check`.

---

## Stage 27B Boundary

In scope:

- README and docs updates listed in the design.
- Changelog entry.
- Documentation-only verification.

Out of scope:

- production code changes;
- test changes;
- config/example/schema changes;
- dependency or `uv.lock` changes;
- release build, wheel smoke, commit, or push.

Because Stage 27A code/test changes are intentionally still uncommitted in the
same worktree, Stage 27B verification must snapshot those non-doc diffs before
editing docs and prove they did not change.

## Task 0: Snapshot Existing Non-Doc And Lockfile Diffs

**Files:**
- No file edits.

- [ ] **Step 1: Snapshot Stage 27A code/test and lockfile diffs before docs edits**

Run:

```bash
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py > /tmp/fashion-radar-stage27b-nondoc-before.diff
sha256sum src/fashion_radar/community_candidates.py tests/test_community_candidates.py > /tmp/fashion-radar-stage27b-stage27a-untracked-before.sha256
git diff -- uv.lock > /tmp/fashion-radar-stage27b-uv-lock-before.diff
```

Expected: all commands exit `0`. These files are outside the repository and are
used only to prove Stage 27B does not change Stage 27A code/test diffs,
approved untracked Stage 27A file contents, or the pre-existing `uv.lock` diff.

## Task 1: README And Changelog

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add README quickstart command**

In the community signal command block near `community-signal-lint`, add:

```bash
uv run fashion-radar community-candidates ./community-signals.csv --input-format csv --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar community-candidates ./community-signals.csv --input-format csv --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

- [ ] **Step 2: Add README explanatory paragraph**

Add near the imported/community candidate explanations:

```markdown
`community-candidates` is local and read-only. It previews aggregate candidate
phrase metrics from one supplied community signal CSV/JSON file before import.
It does not store rows, open SQLite, fetch URLs, print the supplied input file
path, or expose row URLs, row titles, summaries, raw text, normalized keys,
candidate contexts, or representative item details. The output is not proof of
demand, not platform coverage, and not source ranking.
```

- [ ] **Step 3: Add changelog entry**

Add:

```markdown
- Added `community-candidates` for local pre-import candidate phrase previews
  from one supplied community signal CSV/JSON handoff file.
```

## Task 2: Community Signal Docs

**Files:**
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`

- [ ] **Step 1: Update import docs**

Add `community-candidates` after preflight lint and before importer dry-run:

```bash
uv run fashion-radar community-candidates ./community-signals.csv --input-format csv --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
uv run fashion-radar community-candidates ./community-signals.json --input-format json --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

Add prose:

```markdown
`community-candidates` reads one local handoff file and local config, then
prints aggregate-only candidate phrase metrics before import. It does not
import rows, open SQLite, recurse directories, fetch URLs, or expose the
supplied input file path, row URLs, row titles, summaries, raw text, normalized
keys, candidate contexts, or representative item details.
```

- [ ] **Step 2: Update quality docs recommended order**

Insert `community-candidates` after strict lint:

```bash
uv run fashion-radar community-candidates ./community-signals.csv --input-format csv --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export"
```

Add prose:

```markdown
Use `community-candidates` when a single local handoff file passes lint and you
want an aggregate preview of candidate phrases before import. It reports only
aggregate candidate phrase metrics and keeps the supplied input file path, row
URLs, row titles, summaries, raw text, normalized keys, candidate contexts, and
representative item details out of output.
```

## Task 3: Candidate Discovery, Architecture, And Boundaries

**Files:**
- Modify: `docs/candidate-discovery.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`

- [ ] **Step 1: Candidate discovery doc**

Add a short section:

```markdown
## Community Candidate Preview

`community-candidates` previews candidate phrases from one supplied community
signal CSV/JSON file before import. It uses the same deterministic candidate
phrase extraction and configured-entity suppression, but it does not open
SQLite, consult stored matches, write reports, or expose representative items.
The preview is aggregate-only and is limited to the supplied file.
```

- [ ] **Step 2: Architecture doc**

Add a short note in the manual/community input area:

```markdown
`community-candidates` is an in-memory pre-import preview over one local handoff
file. It sits before manual import and does not write database, report, config,
or dashboard state.
```

- [ ] **Step 3: Source boundaries doc**

Add:

```markdown
`community-candidates` reads one local CSV/JSON handoff file plus local config
and prints aggregate candidate phrases. It does not import rows, open SQLite,
fetch URLs, recurse directories, log in, write reports, update dashboards, or
generate entity files. It does not output the supplied file path, row URLs,
row titles, summaries, raw text, normalized keys, candidate contexts, or
representative item details.

`community-candidates` is not proof of demand, not platform coverage, not source ranking, not a source connector, not an acquisition workflow, not a scraper, not a watcher, not a scheduler, not a report writer, not a dashboard updater, not a database import, and not an entity YAML generator.
```

## Task 4: Checklist And Verification

**Files:**
- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Update checklist**

Add a Stage 27B checklist item:

```markdown
- [ ] `community-candidates` docs describe one-file local pre-import preview,
      aggregate-only output, no SQLite writes, no URL fetching, and no supplied
      input file path, row URL, row title, summary, raw text, normalized key,
      candidate context, or representative item detail exposure.
```

Add or preserve the existing reminder that `uv.lock` mirror diffs must not be
staged.

- [ ] **Step 2: Run required negative boundary phrase checks**

Run:

```bash
rg -n "not proof of demand" docs/source-boundaries.md
rg -n "not platform coverage" docs/source-boundaries.md
rg -n "not source ranking" docs/source-boundaries.md
rg -n "not a source connector" docs/source-boundaries.md
rg -n "not an acquisition workflow" docs/source-boundaries.md
rg -n "not a scraper" docs/source-boundaries.md
rg -n "not a watcher" docs/source-boundaries.md
rg -n "not a scheduler" docs/source-boundaries.md
rg -n "not a report writer" docs/source-boundaries.md
rg -n "not a dashboard updater" docs/source-boundaries.md
rg -n "not a database import" docs/source-boundaries.md
rg -n "not an entity YAML generator" docs/source-boundaries.md
```

Expected: every command exits `0`.

- [ ] **Step 3: Run unsafe positive boundary scan**

Run:

```bash
.venv/bin/python - <<'PY'
import re
import subprocess
import sys

prohibited = re.compile(
    r"platform-wide|market-wide|platform coverage|proof of demand|verified demand|"
    r"real-time monitoring|platform search|social monitoring|monitoring|"
    r"source health|source quality|source coverage|source ranking|top sources|"
    r"top-sources|scraper|scraping|watcher|watchers|watch folder|watch folders|"
    r"scheduler|scheduled|scheduling|acquisition|report generation|report writer|"
    r"reporting|generates reports|dashboard update|dashboard updates|dashboard updater|"
    r"database import|SQLite import|SQLite write|SQLite writes|entity YAML|"
    r"entity config|source connector|source connectors",
    re.IGNORECASE,
)
safe_phrases = [
    "not proof of demand",
    "not platform coverage",
    "not source ranking",
    "not a source connector",
    "not an acquisition workflow",
    "not a scraper",
    "not a watcher",
    "not a scheduler",
    "not a report writer",
    "not a dashboard updater",
    "not a database import",
    "not an entity YAML generator",
    "no SQLite writes",
]

diff = subprocess.run(
    [
        "git",
        "diff",
        "-U0",
        "--",
        "README.md",
        "CHANGELOG.md",
        "docs/community-signal-import.md",
        "docs/community-signal-quality.md",
        "docs/candidate-discovery.md",
        "docs/architecture.md",
        "docs/source-boundaries.md",
        "docs/github-upload-checklist.md",
    ],
    check=True,
    capture_output=True,
    text=True,
).stdout
violations = []
for line_number, line in enumerate(diff.splitlines(), start=1):
    if not line.startswith("+") or line.startswith("+++"):
        continue
    content = line[1:]
    scrubbed = content
    for phrase in safe_phrases:
        scrubbed = re.sub(re.escape(phrase), "", scrubbed, flags=re.IGNORECASE)
    if prohibited.search(scrubbed):
        violations.append(f"{line_number}: {content}")

if violations:
    print("Unsafe positive boundary terms in added docs lines:")
    print("\n".join(violations))
    sys.exit(1)
PY
```

Expected: no output, exit `0`.

- [ ] **Step 4: Run docs-only changed-file check**

First prove the Stage 27A non-doc diff and the pre-existing `uv.lock` diff did
not change during Stage 27B. The `sha256sum` command covers approved untracked
Stage 27A files because `git diff` does not include untracked file contents:

```bash
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py | cmp -s /tmp/fashion-radar-stage27b-nondoc-before.diff -
sha256sum -c /tmp/fashion-radar-stage27b-stage27a-untracked-before.sha256
git diff -- uv.lock | cmp -s /tmp/fashion-radar-stage27b-uv-lock-before.diff -
```

Expected: all commands exit `0`.

Run:

```bash
git diff --name-only | rg -v '^(README\.md|CHANGELOG\.md|docs/community-signal-import\.md|docs/community-signal-quality\.md|docs/candidate-discovery\.md|docs/architecture\.md|docs/source-boundaries\.md|docs/github-upload-checklist\.md|docs/superpowers/specs/2026-06-13-stage-27b-community-candidate-docs-design\.md|docs/superpowers/plans/2026-06-13-stage-27b-community-candidate-docs-plan\.md|docs/reviews/claude-code-stage-27b-plan-review-prompt\.md|docs/reviews/claude-code-stage-27b-plan-review\.md|docs/reviews/claude-code-stage-27b-plan-rereview-prompt\.md|docs/reviews/claude-code-stage-27b-plan-rereview\.md|src/fashion_radar/community_candidates\.py|src/fashion_radar/cli\.py|tests/test_community_candidates\.py|tests/test_cli\.py|uv\.lock)$'
git ls-files --others --exclude-standard | rg -v '^(docs/reviews/claude-code-stage-27.*|docs/superpowers/plans/2026-06-13-stage-27.*|docs/superpowers/specs/2026-06-13-stage-27.*|src/fashion_radar/community_candidates\.py|tests/test_community_candidates\.py)$'
```

Expected: both commands exit `1` with no matches. The allowlists include Stage
27A files, Stage 27 plan/review docs, and the known pre-existing `uv.lock` diff
only so the checks work in this combined active worktree. There must be no
unexpected untracked production code, tests, configs, examples, schemas,
generated artifacts, dependencies, or lockfile-related files. Before final
staging in a later node, `uv.lock` must remain unstaged.

Run:

```bash
git diff --cached --name-only | rg '^uv\.lock$'
```

Expected: exit `1` with no matches.

- [ ] **Step 5: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output, exit `0`.

## Stage 27B Completion

Stage 27B is complete when:

- all listed docs are updated;
- required negative boundary phrase checks pass;
- unsafe positive boundary scan has no matches;
- the Stage 27A non-doc diff, Stage 27A untracked file hash, and `uv.lock` diff
  snapshot comparisons pass;
- changed-file verification shows no unexpected code, test, config, example,
  schema, generated artifact, dependency, or lockfile changes beyond the
  allowlisted Stage 27A files and known pre-existing `uv.lock` diff;
- `git diff --check` passes;
- no production code, tests, configs, dependencies, or lockfiles were changed in
  this node.

The next node should perform final code/docs review, full release verification,
secret/artifact scans, explicit staging excluding `uv.lock`, commit, and push.
