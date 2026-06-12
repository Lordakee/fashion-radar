# Stage 13 Community Signal Import Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested local import contract so external community/social tools can hand sanitized CSV/JSON rows to Fashion Radar through the existing `import-signals` command.

**Architecture:** Do not add a collector or platform adapter. Add repository examples, a strict JSON schema document, focused tests, and documentation that reuse the existing Stage 9 manual importer and storage path. Keep runtime behavior unchanged: Fashion Radar reads only local files and stores sanitized rows as `manual_import`.

**Tech Stack:** Python 3.11+, standard library `csv`/`json`, existing Typer CLI, existing Pydantic manual importer, pytest, ruff, uv, Markdown docs, JSON Schema document as static repo metadata.

---

## Scope Guard

Stage 13 must not add or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, Discord,
  Telegram, WeChat, or other platform connectors.
- Web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search.
- Login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass.
- Official or unofficial social platform APIs.
- Instructions for obtaining platform exports from social platforms or
  communities.
- Raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile URLs, images, videos, media downloading, reposting, or archive
  redistribution.
- Google News RSS or any new source type.
- Complete source coverage, platform-wide coverage, community-wide coverage,
  market-wide trend proof, verified demand outside the configured source set,
  real-time social monitoring, or top social trends.
- LLM scoring, embeddings, vector databases, image recognition, paid service
  requirements, or sentiment analysis.
- DB migrations, persistent adapter tables, source-health changes, collector
  changes, dashboard changes, report semantics changes, or network calls.
- A product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature.

## Developer Operations Boundary

Dependency index checks, mirror install checks, Claude Code reviews, commits,
and GitHub pushes are development and release operations only. They are not
Fashion Radar runtime behavior and must not appear as product features,
collectors, platform tooling, or user-facing monitoring workflows.

This project has a standing user authorization to push the current repository
to GitHub after a reviewed stage is verified. If that authorization is absent
in a future run, stop after the reviewed commit and ask before pushing.

## File Structure

- Create `tests/test_community_signal_import_contract.py`: focused tests for
  the contract examples, schema shape, privacy-field exclusions, and CLI dry-run
  behavior.
- Create `examples/community-signals.example.csv`: importable CSV template for
  external community-tool handoff.
- Create `examples/community-signals.example.json`: importable JSON template
  with an `items` array.
- Create `schemas/community-signals.schema.json`: strict static JSON schema for
  external tools that can validate their output before handoff.
- Create `docs/community-signal-import.md`: user-facing contract and workflow
  docs.
- Modify `docs/manual-signal-import.md`: link the community contract and clarify
  that it is a template layer over manual import.
- Modify `docs/source-boundaries.md`: describe the contract as a local input
  pattern, not a connector or acquisition guide.
- Modify `docs/architecture.md`: mention the contract under manual import.
- Modify `README.md`: add a short pointer in Quickstart and Documentation.
- Modify `CHANGELOG.md`: record the new contract, examples, and schema.

## Task 1: Write Failing Contract Tests

**Files:**
- Create: `tests/test_community_signal_import_contract.py`

- [ ] **Step 1: Add focused failing tests**

Create `tests/test_community_signal_import_contract.py`:

```python
import json
from pathlib import Path

from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.importers.manual_signals import load_manual_signal_rows


ROOT = Path(__file__).resolve().parents[1]
CSV_EXAMPLE = ROOT / "examples" / "community-signals.example.csv"
JSON_EXAMPLE = ROOT / "examples" / "community-signals.example.json"
SCHEMA_PATH = ROOT / "schemas" / "community-signals.schema.json"


def test_community_signal_csv_example_loads_through_manual_importer() -> None:
    rows = load_manual_signal_rows(
        CSV_EXAMPLE,
        input_format="csv",
        default_source_name="Community Tool Export",
    )

    assert len(rows) == 2
    assert rows[0].url == "https://example.com/community/east-west-tote"
    assert rows[0].title == "East-west tote interest"
    assert rows[0].source_name == "Community Tool Export"
    assert rows[0].platform == "community"
    assert rows[0].source_weight == 1.3
    assert rows[1].title == "Soft ballet flats mention"
    assert rows[1].summary is not None


def test_community_signal_json_example_loads_through_manual_importer() -> None:
    rows = load_manual_signal_rows(
        JSON_EXAMPLE,
        input_format="json",
        default_source_name="Community Tool Export",
    )

    assert len(rows) == 2
    assert rows[0].url == "https://example.com/community/the-row-tote"
    assert rows[0].title == "The Row tote discussion"
    assert rows[0].source_name == "Community Tool Export"
    assert rows[0].platform == "community"
    assert rows[0].source_weight == 1.4
    assert rows[1].title == "Silver sneaker signal"


def test_community_signal_schema_documents_strict_public_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    one_of = schema["oneOf"]
    array_form = next(option for option in one_of if option.get("type") == "array")
    object_form = next(option for option in one_of if option.get("type") == "object")
    signal = schema["$defs"]["communitySignal"]
    properties = signal["properties"]

    assert len(one_of) == 2
    assert array_form["items"]["$ref"] == "#/$defs/communitySignal"
    assert object_form["required"] == ["items"]
    assert object_form["additionalProperties"] is False
    assert object_form["properties"]["items"]["items"]["$ref"] == "#/$defs/communitySignal"
    assert set(signal["required"]) == {"url", "title", "published_at"}
    assert signal["additionalProperties"] is False
    assert set(properties) == {
        "url",
        "title",
        "published_at",
        "summary",
        "source_name",
        "platform",
        "source_weight",
        "collected_at",
    }
    assert properties["source_weight"]["exclusiveMinimum"] == 0
    assert properties["source_weight"]["maximum"] == 5
    assert {
        "author_handle",
        "raw_comment",
        "account_id",
        "follower_count",
        "image_url",
        "video_url",
        "profile_url",
        "full_post_body",
        "direct_message",
        "cookie",
        "session",
        "token",
    }.isdisjoint(properties)


def test_community_examples_use_same_allowed_contract_fields() -> None:
    csv_header = CSV_EXAMPLE.read_text(encoding="utf-8").splitlines()[0].split(",")
    payload = json.loads(JSON_EXAMPLE.read_text(encoding="utf-8"))
    json_keys = set().union(*(item.keys() for item in payload["items"]))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["communitySignal"]["properties"])

    assert set(csv_header) <= allowed
    assert json_keys <= allowed


def test_import_signals_dry_run_validates_community_examples_without_artifacts(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    env = {
        "FASHION_RADAR_CONFIG_DIR": str(config_dir),
        "FASHION_RADAR_DATA_DIR": str(data_dir),
        "FASHION_RADAR_REPORTS_DIR": str(reports_dir),
    }
    csv_result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(CSV_EXAMPLE),
            "--format",
            "csv",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Community Tool Export",
            "--dry-run",
        ],
        env=env,
    )
    json_result = CliRunner().invoke(
        app,
        [
            "import-signals",
            str(JSON_EXAMPLE),
            "--format",
            "json",
            "--data-dir",
            str(data_dir),
            "--source-name",
            "Community Tool Export",
            "--dry-run",
        ],
        env=env,
    )

    assert csv_result.exit_code == 0
    assert "Validated 2 manual signal rows" in csv_result.output
    assert json_result.exit_code == 0
    assert "Validated 2 manual signal rows" in json_result.output
    assert not config_dir.exists()
    assert not data_dir.exists()
    assert not reports_dir.exists()
    assert not list(tmp_path.rglob("*.sqlite*"))
    assert not list(tmp_path.rglob("fashion-radar-*.json"))
    assert not list(tmp_path.rglob("fashion-radar-*.md"))
    assert not list(tmp_path.rglob("latest.*"))
    assert not list(tmp_path.rglob("report-index.json"))
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_import_contract.py -q
```

Expected: FAIL because `examples/community-signals.example.csv`,
`examples/community-signals.example.json`, and
`schemas/community-signals.schema.json` do not exist yet.

## Task 2: Add Importable Examples And Static JSON Schema

**Files:**
- Create: `examples/community-signals.example.csv`
- Create: `examples/community-signals.example.json`
- Create: `schemas/community-signals.schema.json`
- Test: `tests/test_community_signal_import_contract.py`

- [ ] **Step 1: Create the CSV example**

Create `examples/community-signals.example.csv`:

```csv
url,title,published_at,summary,source_name,platform,source_weight,collected_at
https://example.com/community/east-west-tote,East-west tote interest,2026-06-12T08:00:00Z,Sanitized local note from an external community digest,Community Tool Export,community,1.3,2026-06-12T08:30:00Z
https://example.com/community/soft-ballet-flats,Soft ballet flats mention,2026-06-12T09:00:00Z,Short sanitized note for local review,Community Tool Export,community,1.1,2026-06-12T09:20:00Z
```

- [ ] **Step 2: Create the JSON example**

Create `examples/community-signals.example.json`:

```json
{
  "items": [
    {
      "url": "https://example.com/community/the-row-tote",
      "title": "The Row tote discussion",
      "published_at": "2026-06-12T10:00:00Z",
      "summary": "Sanitized local note from an external community digest",
      "source_name": "Community Tool Export",
      "platform": "community",
      "source_weight": 1.4,
      "collected_at": "2026-06-12T10:30:00Z"
    },
    {
      "url": "https://example.com/community/silver-sneaker",
      "title": "Silver sneaker signal",
      "published_at": "2026-06-12T11:00:00Z",
      "summary": "Short sanitized note for local review",
      "source_name": "Community Tool Export",
      "platform": "community",
      "source_weight": 1.2,
      "collected_at": "2026-06-12T11:20:00Z"
    }
  ]
}
```

- [ ] **Step 3: Create the static JSON schema**

Create `schemas/community-signals.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Lordakee/fashion-radar/blob/main/schemas/community-signals.schema.json",
  "title": "Fashion Radar Community Signal Import",
  "description": "Strict local JSON handoff contract for sanitized community or external-tool signal rows accepted by fashion-radar import-signals.",
  "oneOf": [
    {
      "type": "array",
      "items": {
        "$ref": "#/$defs/communitySignal"
      }
    },
    {
      "type": "object",
      "required": [
        "items"
      ],
      "additionalProperties": false,
      "properties": {
        "items": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/communitySignal"
          }
        }
      }
    }
  ],
  "$defs": {
    "communitySignal": {
      "type": "object",
      "required": [
        "url",
        "title",
        "published_at"
      ],
      "additionalProperties": false,
      "properties": {
        "url": {
          "type": "string",
          "minLength": 1,
          "description": "Source URL or stable reference URL for the observed item."
        },
        "title": {
          "type": "string",
          "minLength": 1,
          "description": "Short observed text, headline, or normalized signal phrase."
        },
        "published_at": {
          "type": "string",
          "format": "date-time",
          "description": "Publication or observation timestamp."
        },
        "summary": {
          "type": "string",
          "minLength": 1,
          "description": "Short sanitized note for local review."
        },
        "source_name": {
          "type": "string",
          "minLength": 1,
          "description": "Display name for the external tool or local export."
        },
        "platform": {
          "type": "string",
          "minLength": 1,
          "description": "Short provenance label. This is not stored as platform coverage."
        },
        "source_weight": {
          "type": "number",
          "exclusiveMinimum": 0,
          "maximum": 5,
          "description": "Local score weight accepted by import-signals."
        },
        "collected_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp for when the external tool produced the row."
        }
      }
    }
  }
}
```

- [ ] **Step 4: Run focused test and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_community_signal_import_contract.py -q
```

Expected: PASS.

## Task 3: Add Community Contract Documentation

**Files:**
- Create: `docs/community-signal-import.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create `docs/community-signal-import.md`**

Add sections covering:

- Title: `# Community Signal Import`
- Intro: community signal import is a local handoff contract for sanitized
  CSV/JSON rows created by tools the user controls. It uses the existing
  `fashion-radar import-signals` command and stores accepted rows as
  `manual_import`.
- Contract files:
  - `examples/community-signals.example.csv`
  - `examples/community-signals.example.json`
  - `schemas/community-signals.schema.json`
- Required fields:
  - `url`
  - `title`
  - `published_at`
- Optional fields:
  - `summary`
  - `source_name`
  - `platform`
  - `source_weight`
  - `collected_at`
- Dry-run commands:

```bash
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.json --format json --source-name "Community Tool Export" --dry-run
```

- Import command:

```bash
uv run fashion-radar import-signals ./community-signals.csv --format csv --source-name "Community Tool Export"
```

- Review-after-import commands:

```bash
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Also state that external tools should not include raw/private fields, platform
labels are provenance only, and this document is not a source-acquisition guide.
Document CSV strictness as a recommended handoff field set: JSON producers can
validate against `schemas/community-signals.schema.json`, while CSV producers
should emit only the same allowed columns because JSON Schema does not validate
CSV. Also state that the runtime importer may ignore unknown fields for
backward-compatible manual imports, but the community contract intentionally
asks external tools to omit unknown/raw/private fields.

- [ ] **Step 2: Update existing docs**

Add short cross-links:

- `docs/manual-signal-import.md`: link to `community-signal-import.md` after the
  input format section.
- `docs/source-boundaries.md`: state that community signal import is a local
  contract layered on manual import, not a connector or source-acquisition guide.
- `docs/architecture.md`: mention the community contract under Manual Import
  without changing command flow semantics.
- `README.md`: add a Quickstart line showing dry-run against the community CSV
  example and add the doc link under Documentation.
- `CHANGELOG.md`: add an Unreleased bullet for the community signal import
  examples/schema/docs.

- [ ] **Step 3: Run documentation/scope checks**

Run:

```bash
rg -n "scraper|crawler|Playwright|Selenium|cookie|session|token|proxy|CAPTCHA|fingerprint|rate-limit bypass|platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|source-acquisition|platform export" \
  docs/community-signal-import.md docs/manual-signal-import.md docs/source-boundaries.md docs/architecture.md README.md CHANGELOG.md
```

Expected: classify every match. Negative boundary wording such as "do not
include cookies/tokens/sessions" is allowed. Positive capability claims,
source-acquisition instructions, platform export acquisition instructions, or
claims such as `platform-wide`, `market-wide`, `verified demand`, `top social
trend`, or `real-time social monitoring` must be removed.

## Task 4: Verification, Claude Code Review, Commit, Push

**Files:**
- Modify: `docs/reviews/claude-code-stage-13-code-review-prompt.md`
- Modify: `docs/reviews/claude-code-stage-13-code-review.md`

- [ ] **Step 1: Run full verification**

Run:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage13
codegraph status
```

Expected:

- All tests pass.
- Ruff passes.
- Lockfile and sync checks pass.
- Mirror sync check passes without modifying `uv.lock`.
- Build succeeds.
- CodeGraph index is up to date.

- [ ] **Step 2: Run installed-wheel smoke**

Run a temporary installed-wheel smoke using the just-built wheel and the
Tsinghua mirror for install speed. The smoke must run outside the source
checkout, copy only the example files into the temp directory, avoid editable
installs and `PYTHONPATH` leakage, and set explicit temp config/data/report
dirs.

```bash
tmpdir="$(mktemp -d)"
wheel="$(find /tmp/fashion-radar-dist-stage13 -maxdepth 1 -name 'fashion_radar-*.whl' | sort | tail -1)"
mkdir -p "$tmpdir/work/examples"
cp examples/community-signals.example.csv "$tmpdir/work/examples/"
cp examples/community-signals.example.json "$tmpdir/work/examples/"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv venv "$tmpdir/venv"
env -u PYTHONPATH UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple \
  uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
(
  cd "$tmpdir/work"
  env -u PYTHONPATH \
    FASHION_RADAR_CONFIG_DIR="$tmpdir/config" \
    FASHION_RADAR_DATA_DIR="$tmpdir/data" \
    FASHION_RADAR_REPORTS_DIR="$tmpdir/reports" \
    "$tmpdir/venv/bin/fashion-radar" import-signals --help >/tmp/fashion-radar-stage13-help.txt
  env -u PYTHONPATH \
    FASHION_RADAR_CONFIG_DIR="$tmpdir/config" \
    FASHION_RADAR_DATA_DIR="$tmpdir/data" \
    FASHION_RADAR_REPORTS_DIR="$tmpdir/reports" \
    "$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/work/examples/community-signals.example.csv" --format csv --source-name "Community Tool Export" --dry-run
  env -u PYTHONPATH \
    FASHION_RADAR_CONFIG_DIR="$tmpdir/config" \
    FASHION_RADAR_DATA_DIR="$tmpdir/data" \
    FASHION_RADAR_REPORTS_DIR="$tmpdir/reports" \
    "$tmpdir/venv/bin/fashion-radar" import-signals "$tmpdir/work/examples/community-signals.example.json" --format json --source-name "Community Tool Export" --dry-run
)
test ! -e "$tmpdir/config"
test ! -e "$tmpdir/data"
test ! -e "$tmpdir/reports"
test -z "$(find "$tmpdir/work" -name '*.sqlite*' -o -name 'fashion-radar-*.json' -o -name 'fashion-radar-*.md' -o -name 'latest.*' -o -name 'report-index.json')"
rm -rf "$tmpdir"
```

Expected: help and both dry-runs succeed from the installed wheel; no
config/data/report directories, SQLite files, collector artifacts, report
artifacts, cookies, tokens, or account/session files are created in the
explicit dirs or temp working directory.

- [ ] **Step 3: Write Claude Code code-review prompt**

Create `docs/reviews/claude-code-stage-13-code-review-prompt.md` asking Claude
Code to review only the Stage 13 diff. The prompt must state:

- Use `claude -p --effort max`.
- Review the new tests, examples, schema, and docs.
- Do not edit files, call the network, run collectors, execute platform/social
  tooling, open SQLite beyond review if avoidable, or create artifacts.
- Check that Stage 13 adds no scraping, platform connector, account automation,
  browser automation, unofficial API, or acquisition instructions.
- Check that example files load through `import-signals --dry-run`.
- Check that docs avoid platform-wide or market-wide claims.

- [ ] **Step 4: Run Claude Code code review**

Run:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-13-code-review-prompt.md | tee docs/reviews/claude-code-stage-13-code-review.md
```

Expected: no Critical or Important findings. Fix Critical/Important findings
and re-review before commit.

- [ ] **Step 5: Commit and push**

After verification and Claude Code approval, commit. Push only because the user
has explicitly authorized GitHub upload for this repository in this session:

```bash
git status --short
git add docs/superpowers/specs/2026-06-12-stage-13-community-signal-import-design.md \
  docs/superpowers/plans/2026-06-12-stage-13-community-signal-import-plan.md \
  docs/reviews/claude-code-stage-13-plan-review-prompt.md \
  docs/reviews/claude-code-stage-13-plan-review.md \
  docs/reviews/claude-code-stage-13-plan-rereview.md \
  docs/reviews/claude-code-stage-13-code-review-prompt.md \
  docs/reviews/claude-code-stage-13-code-review.md \
  tests/test_community_signal_import_contract.py \
  examples/community-signals.example.csv \
  examples/community-signals.example.json \
  schemas/community-signals.schema.json \
  docs/community-signal-import.md \
  docs/manual-signal-import.md \
  docs/source-boundaries.md \
  docs/architecture.md \
  README.md \
  CHANGELOG.md
git commit -m "Add community signal import contract"
# Run only because the user has explicitly authorized GitHub upload for this repo.
git push origin main
```

Keep the remote URL token-free. If HTTPS credentials are required, use a
temporary askpass file and delete it after push. If a future session lacks
explicit push authorization, do not run `git push`; stop after the reviewed
commit and ask for direction.

## Acceptance Criteria

- `examples/community-signals.example.csv` and
  `examples/community-signals.example.json` are valid inputs for
  `fashion-radar import-signals --dry-run`.
- `schemas/community-signals.schema.json` documents a strict sanitized JSON
  handoff contract and excludes private/raw fields.
- Docs tell external tools what local rows to produce without explaining how to
  collect from platforms.
- No production importer, collector, database schema, source pack, dashboard,
  report semantics, dependency, or lockfile changes are required.
- Tests and installed-wheel smoke prove dry-run validation does not create
  database or workflow artifacts.
- Claude Code plan review and code review records are stored in `docs/reviews/`.
