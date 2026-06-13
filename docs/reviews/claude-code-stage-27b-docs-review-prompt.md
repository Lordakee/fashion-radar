You are reviewing Stage 27B documentation changes after implementation.

Repository: `/home/ubuntu/fashion-radar`

Approved plan:

- `docs/reviews/claude-code-stage-27b-plan-rereview.md`
- `docs/superpowers/specs/2026-06-13-stage-27b-community-candidate-docs-design.md`
- `docs/superpowers/plans/2026-06-13-stage-27b-community-candidate-docs-plan.md`

Stage 27B scope:

- Documentation only.
- Intended user-facing files:
  - `README.md`
  - `CHANGELOG.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/candidate-discovery.md`
  - `docs/architecture.md`
  - `docs/source-boundaries.md`
  - `docs/github-upload-checklist.md`
- No production code, tests, configs, dependencies, generated artifacts, or
  lockfiles should be modified by this node.
- The active worktree also contains approved uncommitted Stage 27A code/test
  changes and a known pre-existing `uv.lock` mirror diff. Treat those as
  out-of-scope existing diffs and verify Stage 27B did not change them.

Implemented behavior being documented:

- `fashion-radar community-candidates PATH [OPTIONS]`
- Local one-file pre-import preview over a supplied community signal CSV/JSON
  handoff file and local config.
- Read-only and in-memory: no SQLite open/write, no import, no directory
  recursion, no URL fetching, no reports, no dashboard updates, no entity YAML
  generation.
- Output is aggregate-only candidate phrase metrics.
- Output must not include the supplied input file path, row URLs, row titles,
  summaries, raw text, normalized keys, candidate contexts, or representative
  item details.
- Output and docs must not imply proof of demand, platform coverage, source
  quality/ranking, source acquisition, scraping, monitoring/watchers,
  scheduling, report/dashboard generation, database import/SQLite writes,
  entity YAML/config generation, or source connectors except as explicit
  negative boundary statements.

Verification already run locally after docs edits:

```bash
for phrase in \
  "not proof of demand" \
  "not platform coverage" \
  "not source ranking" \
  "not a source connector" \
  "not an acquisition workflow" \
  "not a scraper" \
  "not a watcher" \
  "not a scheduler" \
  "not a report writer" \
  "not a dashboard updater" \
  "not a database import" \
  "not an entity YAML generator"
do
  rg -n "$phrase" docs/source-boundaries.md >/dev/null
done

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

git diff -- src/fashion_radar/community_candidates.py src/fashion_radar/cli.py tests/test_community_candidates.py tests/test_cli.py | cmp -s /tmp/fashion-radar-stage27b-nondoc-before.diff -
sha256sum -c /tmp/fashion-radar-stage27b-stage27a-untracked-before.sha256 >/dev/null
git diff -- uv.lock | cmp -s /tmp/fashion-radar-stage27b-uv-lock-before.diff -

git diff --name-only | rg -v '^(README\.md|CHANGELOG\.md|docs/community-signal-import\.md|docs/community-signal-quality\.md|docs/candidate-discovery\.md|docs/architecture\.md|docs/source-boundaries\.md|docs/github-upload-checklist\.md|docs/superpowers/specs/2026-06-13-stage-27b-community-candidate-docs-design\.md|docs/superpowers/plans/2026-06-13-stage-27b-community-candidate-docs-plan\.md|docs/reviews/claude-code-stage-27b-plan-review-prompt\.md|docs/reviews/claude-code-stage-27b-plan-review\.md|docs/reviews/claude-code-stage-27b-plan-rereview-prompt\.md|docs/reviews/claude-code-stage-27b-plan-rereview\.md|src/fashion_radar/community_candidates\.py|src/fashion_radar/cli\.py|tests/test_community_candidates\.py|tests/test_cli\.py|uv\.lock)$'
git ls-files --others --exclude-standard | rg -v '^(docs/reviews/claude-code-stage-27.*|docs/superpowers/plans/2026-06-13-stage-27.*|docs/superpowers/specs/2026-06-13-stage-27.*|src/fashion_radar/community_candidates\.py|tests/test_community_candidates\.py)$'
git diff --cached --name-only | rg '^uv\.lock$'
git diff --check
```

The expected no-match `rg` commands above were wrapped locally so exit `1`
with no matches was treated as success. All listed checks passed.

Review focus:

1. Did Stage 27B stay within documentation-only scope?
2. Do the docs accurately describe the implemented `community-candidates`
   command and its one-file local read-only aggregate-only behavior?
3. Do the docs include the required output exclusions?
4. Do added docs avoid unsafe positive claims about platform coverage, proof of
   demand, source quality/ranking, source acquisition, scraping,
   monitoring/watchers, scheduling, report/dashboard generation, database
   import/SQLite writes, entity YAML/config generation, and source connectors?
5. Are there any user-facing wording issues, command mistakes, or stale
   references that should block completion?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block completion and must be fixed before the
  release-verification node.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 27B DOCS COMPLETION`.
