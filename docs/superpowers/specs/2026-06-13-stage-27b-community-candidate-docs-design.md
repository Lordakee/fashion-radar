# Stage 27B Community Candidate Docs Design

## Goal

Document the new `community-candidates` command added in Stage 27A so users know
how to run the local pre-import preview and understand its boundaries.

## Scope

Stage 27B is documentation only. It does not modify production code, tests,
configs, examples, schemas, dependencies, lockfiles, or generated artifacts.

Files in scope:

- `README.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/candidate-discovery.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

## Required Message

Docs should describe `community-candidates` as:

- local and read-only;
- a one-file pre-import candidate phrase preview;
- driven by the supplied CSV/JSON handoff file and local config only;
- aggregate-only output;
- not proof of demand, platform coverage, or source ranking;
- not a source connector, acquisition workflow, scraper, watcher, scheduler,
  report writer, dashboard updater, database import, or entity YAML generator.

Docs must state that command output does not include the supplied file path,
row URLs, row titles, summaries, raw text, normalized keys, candidate contexts,
or representative item details.

## Placement

- README quickstart: add `community-candidates` next to existing community
  signal lint/import commands and add a short explanatory paragraph near
  imported candidate review text.
- `docs/community-signal-import.md`: add it between preflight lint and importer
  dry-run as an optional local preview.
- `docs/community-signal-quality.md`: add it to the recommended order and
  explain when to use it.
- `docs/candidate-discovery.md`: mention pre-import community candidate preview
  as separate from database-backed `candidates` and `imported-candidates`.
- `docs/architecture.md`: add a short line in the local manual/community input
  path.
- `docs/source-boundaries.md`: add an explicit boundary entry.
- `docs/github-upload-checklist.md`: add Stage 27B doc checks and remind not to
  stage `uv.lock`.
- `CHANGELOG.md`: add a concise entry.

## Verification

Before editing docs, snapshot the existing Stage 27A non-doc diff:

```bash
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py > /tmp/fashion-radar-stage27b-nondoc-before.diff
sha256sum src/fashion_radar/community_candidates.py tests/test_community_candidates.py > /tmp/fashion-radar-stage27b-stage27a-untracked-before.sha256
git diff -- uv.lock > /tmp/fashion-radar-stage27b-uv-lock-before.diff
```

After editing docs, verify that Stage 27B did not change those non-doc files or
the pre-existing `uv.lock` diff:

```bash
git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py | cmp -s /tmp/fashion-radar-stage27b-nondoc-before.diff -
sha256sum -c /tmp/fashion-radar-stage27b-stage27a-untracked-before.sha256
git diff -- uv.lock | cmp -s /tmp/fashion-radar-stage27b-uv-lock-before.diff -
```

Expected: all commands exit `0`.

Add an explicit negative boundary sentence to `docs/source-boundaries.md` and
verify it:

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

Run an unsafe positive boundary scan after edits. The scan strips only exact
safe negative phrases before searching, so a mixed line such as "not a scraper
and provides platform coverage" still fails:

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

Run a docs-only changed-file check:

```bash
git diff --name-only | rg -v '^(README\.md|CHANGELOG\.md|docs/community-signal-import\.md|docs/community-signal-quality\.md|docs/candidate-discovery\.md|docs/architecture\.md|docs/source-boundaries\.md|docs/github-upload-checklist\.md|docs/superpowers/specs/2026-06-13-stage-27b-community-candidate-docs-design\.md|docs/superpowers/plans/2026-06-13-stage-27b-community-candidate-docs-plan\.md|docs/reviews/claude-code-stage-27b-plan-review-prompt\.md|docs/reviews/claude-code-stage-27b-plan-review\.md|docs/reviews/claude-code-stage-27b-plan-rereview-prompt\.md|docs/reviews/claude-code-stage-27b-plan-rereview\.md|src/fashion_radar/community_candidates\.py|src/fashion_radar/cli\.py|tests/test_community_candidates\.py|tests/test_cli\.py|uv\.lock)$'
git ls-files --others --exclude-standard | rg -v '^(docs/reviews/claude-code-stage-27.*|docs/superpowers/plans/2026-06-13-stage-27.*|docs/superpowers/specs/2026-06-13-stage-27.*|src/fashion_radar/community_candidates\.py|tests/test_community_candidates\.py)$'
```

Expected: both commands produce no output and exit `1`. The allowlists include
Stage 27A files, Stage 27 plan/review docs, and the known pre-existing
`uv.lock` diff only so this can run in the active combined worktree. Stage 27B
must not add production code, tests, configs, examples, schemas, generated
artifacts, or dependency changes.

Before later staging, verify `uv.lock` remains unstaged:

```bash
git diff --cached --name-only | rg '^uv\.lock$'
```

Expected: no output, exit `1`.

Run:

```bash
git diff --check
```

Expected: no whitespace errors.
