# Stage 12 Source-Pack Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local source-pack quality diagnostics and improve the public fashion starter pack so daily Fashion Radar runs start from cleaner configured RSS/GDELT inputs.

**Architecture:** Keep strict schema validation in `settings.py` and add a separate pure `fashion_radar.source_packs` lint module for advisory quality checks. Expose the module through one flat Typer command, `source-pack-lint`, and update the public source pack plus docs without changing collectors, database schema, scoring, reports, or dashboard behavior.

**Tech Stack:** Python 3.11+, Pydantic `BaseModel`, `enum.StrEnum`, pathlib, PyYAML, Typer, pytest, ruff, uv.

---

## Scope Guard

Stage 12 may read local source YAML files and print local diagnostics only. It
must not add or document social-platform connectors, web scraping, crawler
development, browser automation, Playwright, Selenium, platform login/session
handling, cookies, account automation, proxy pools, fingerprint evasion,
CAPTCHA bypass, rate-limit bypass, access-control bypass, paywall bypass,
Google News RSS, official or unofficial social platform APIs, platform search,
platform export instructions, raw comments, full post bodies, DMs, account IDs,
follower lists, profile internals, images, videos, media downloading,
reposting, LLM scoring, embeddings, vector databases, image recognition, paid
service requirements, or private data collection.

Stage 12 must not add a product-facing compliance review, audit workflow,
safety workflow, approval UI, or policy checklist. Any scope-boundary language
is for docs and internal review only; the product value is source-pack quality.

Stage 12 must not add DB migrations, persistent source-pack lint tables,
collector changes, source-health changes, report changes, dashboard changes, or
network calls.

Codex subagents must use `reasoning_effort: "xhigh"`. Claude Code review must
use `--effort max`.

## Files

- Create: `src/fashion_radar/source_packs.py`
- Create: `tests/test_source_packs.py`
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_config.py`
- Modify: `configs/source-packs/fashion-public.example.yaml`
- Create: `docs/source-pack-quality.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Create before implementation: `docs/reviews/claude-code-stage-12-plan-review-prompt.md`
- Create after plan review: `docs/reviews/claude-code-stage-12-plan-review.md`
- Create after implementation: `docs/reviews/claude-code-stage-12-code-review-prompt.md`
- Create after code review: `docs/reviews/claude-code-stage-12-code-review.md`

## Public Interface

Add one command:

```bash
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

Options:

- `path: Path`
- `--format table|json`
- `--strict`

Exit behavior:

- Exit `0` when no lint errors are present.
- Exit `1` when structural config loading fails or lint errors are present.
- Exit `1` under `--strict` when warnings are present.

## Task 1: Claude Code Plan Gate

- [ ] Create `docs/reviews/claude-code-stage-12-plan-review-prompt.md` with the Stage 12 objective, architecture, tech stack, implementation method, staged plan, scope guard, expected tests, expected docs, and read-only review instructions.
- [ ] Run Claude Code in plan/read-only mode:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-12-plan-review-prompt.md
```

- [ ] Save the review to `docs/reviews/claude-code-stage-12-plan-review.md`.
- [ ] Fix every Critical and Important finding before Task 2. If Claude Code does not approve the plan, save follow-up prompts/results as `docs/reviews/claude-code-stage-12-plan-rereview*.md` and repeat until approved.

## Task 2: Pure Source-Pack Lint Module

**Files:**

- Create: `src/fashion_radar/source_packs.py`
- Create: `tests/test_source_packs.py`

- [ ] Add failing tests in `tests/test_source_packs.py`:
  - `test_lint_repository_public_pack_has_no_errors`
  - `test_duplicate_source_names_are_errors_after_normalization`
  - `test_duplicate_feed_urls_are_warnings_after_normalization`
  - `test_url_normalization_lowercases_scheme_and_host_strips_fragment_and_trailing_slash`
  - `test_duplicate_gdelt_queries_are_warnings_after_normalization`
  - `test_missing_tags_are_warnings`
  - `test_implicit_weight_is_info`
  - `test_all_disabled_sources_are_errors`
  - `test_invalid_source_config_returns_error_finding`
  - `test_lint_result_json_shape_is_stable`

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_source_packs.py -q
```

Expected: fails because `fashion_radar.source_packs` does not exist.

- [ ] Implement `src/fashion_radar/source_packs.py` with these public models:

```python
class SourcePackFindingSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SourcePackFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: SourcePackFindingSeverity
    code: str
    message: str
    source_name: str | None = None
    field: str | None = None


class SourcePackLintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    source_count: int = 0
    enabled_count: int = 0
    disabled_count: int = 0
    type_counts: dict[str, int] = Field(default_factory=dict)
    tag_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[SourcePackFinding] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return _count_findings(self.findings, SourcePackFindingSeverity.INFO)

    @property
    def ok(self) -> bool:
        return self.error_count == 0


def _count_findings(
    findings: Sequence[SourcePackFinding],
    severity: SourcePackFindingSeverity,
) -> int:
    return sum(1 for finding in findings if finding.severity == severity)
```

- [ ] Implement these public functions:

```python
def lint_source_pack(path: Path) -> SourcePackLintResult:
    """Read and lint one local source YAML file."""


def render_source_pack_lint_table(result: SourcePackLintResult) -> list[str]:
    """Render a deterministic human-readable lint summary."""


def normalize_source_name(value: str) -> str:
    """Lowercase and collapse whitespace in a source name."""


def normalize_source_target(value: str) -> str:
    """Normalize RSS/RSSHub URL strings for duplicate detection."""


def normalize_gdelt_query(value: str) -> str:
    """Lowercase and collapse whitespace in a GDELT query."""
```

- [ ] In `lint_source_pack(path)`, first read raw YAML with `yaml.safe_load()` so the linter can detect omitted fields such as missing `weight`.
- [ ] Add a short implementation comment before raw YAML loading:

```python
# Raw YAML is read before typed validation so omitted fields can be linted.
```

- [ ] If raw YAML cannot be read, parsed, or is not a mapping, return a result with one `invalid_config` error finding and do not raise.
- [ ] Call `load_source_config(path)` for structural validation. If it raises `ConfigError`, return a result with one `invalid_config` error finding and do not raise.
- [ ] For valid configs, compute counts from typed `SourceDefinition` objects:
  - `source_count`
  - `enabled_count`
  - `disabled_count`
  - `type_counts`
  - `tag_counts`
- [ ] Add an `empty_enabled_pack` error when `enabled_count == 0`.
- [ ] Add a `duplicate_source_name` error for duplicate names after lowercasing and whitespace collapse. Report every source in each collision group, including the first source.
- [ ] Add a `duplicate_source_target` warning for duplicate RSS/RSSHub URLs after lowercasing scheme/host, removing URL fragment, and trimming a trailing slash. Preserve query strings so feeds that differ by query remain distinct. Report every source in each collision group, including the first source.
- [ ] Add a `duplicate_gdelt_query` warning for duplicate GDELT queries after lowercasing and whitespace collapse. Report every source in each collision group, including the first source.
- [ ] Add a `missing_tags` warning for any source with no tags.
- [ ] Add an `implicit_weight` info finding when a raw source mapping omits `weight`.
- [ ] Add a `disabled_source` info finding for disabled sources.
- [ ] Add an `article_extraction_enabled` info finding for RSS/RSSHub sources where `article.enabled` resolves to `true`. Keep this as a local-pack quality reminder, not a compliance or policy check.
- [ ] Sort findings deterministically by severity order `error`, `warning`, `info`, then code, source name, and field.
- [ ] Implement `render_source_pack_lint_table()` so table output includes:

```text
Source pack: <path>
Sources: <total> total, <enabled> enabled, <disabled> disabled
Types: gdelt=<n>, rss=<n>
Findings: <errors> errors, <warnings> warnings, <info> info
```

When findings exist, append:

```text
Severity | Code | Source | Field | Message
```

and one row per finding. When no findings exist, append:

```text
No source-pack quality findings.
```

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_source_packs.py -q
.venv/bin/python -m ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py
.venv/bin/python -m ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py
```

Expected: all pass.

## Task 3: CLI Wiring

**Files:**

- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add failing CLI tests:
  - `test_source_pack_lint_help_lists_format_and_strict`
  - `test_source_pack_lint_prints_table_for_public_pack`
  - `test_source_pack_lint_prints_json_for_public_pack`
  - `test_source_pack_lint_strict_exits_nonzero_on_warnings`
  - `test_source_pack_lint_invalid_config_exits_nonzero_without_traceback`
  - `test_source_pack_lint_does_not_create_default_or_explicit_config_data_report_dirs`
  - `test_source_pack_lint_does_not_create_sqlite_or_workflow_artifacts`

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -k "source_pack_lint" -q
```

Expected: fails because the command does not exist.

- [ ] In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.source_packs import (
    SourcePackFindingSeverity,
    lint_source_pack,
    render_source_pack_lint_table,
)
```

- [ ] Add a CLI output type near the existing output format aliases:

```python
SourcePackLintOutputFormat = Literal["table", "json"]
```

- [ ] Add an option constant:

```python
SOURCE_PACK_LINT_FORMAT_OPTION = typer.Option(
    "table",
    "--format",
    help="Output format.",
)
```

- [ ] Add a flat Typer command:

```python
@app.command(name="source-pack-lint")
def source_pack_lint_command(
    path: Path,
    output_format: SourcePackLintOutputFormat = SOURCE_PACK_LINT_FORMAT_OPTION,
    strict: bool = typer.Option(False, help="Exit non-zero when warnings are present."),
) -> None:
    """Lint a local source pack without collecting sources."""
```

- [ ] Command behavior:
  - call `lint_source_pack(path)`;
  - print `result.model_dump_json(indent=2)` when `--format json`;
  - otherwise print each line from `render_source_pack_lint_table(result)`;
  - exit `1` when any finding has severity `error`;
  - exit `1` when `strict` is true and any finding has severity `warning`;
  - do not create default config/data/report directories;
  - do not create explicit config/data/report directories supplied through
    `FASHION_RADAR_CONFIG_DIR`, `FASHION_RADAR_DATA_DIR`, or
    `FASHION_RADAR_REPORTS_DIR`;
  - do not create `fashion-radar.sqlite`, `*.sqlite*`, collector artifacts,
    report artifacts, digest artifacts, or workflow artifacts.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_cli.py -k "source_pack_lint" -q
.venv/bin/python -m ruff check src/fashion_radar/cli.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/cli.py tests/test_cli.py
```

Expected: all pass.

## Task 4: Public Pack And Config Tests

**Files:**

- Modify: `configs/source-packs/fashion-public.example.yaml`
- Modify: `tests/test_config.py`

- [ ] Add failing assertions to `test_public_fashion_source_pack_loads()`:
  - source count is at least 16;
  - source types are only `rss` and `gdelt`;
  - RSS article extraction remains disabled;
  - source names are unique after case/space normalization;
  - RSS URLs are unique after URL normalization;
  - GDELT queries are unique after query normalization;
  - every source has at least one tag.

- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_config.py::test_public_fashion_source_pack_loads -q
```

Expected: fails before the pack is expanded.

- [ ] Expand `configs/source-packs/fashion-public.example.yaml` with bounded GDELT lanes. Keep existing RSS entries unchanged and keep all RSS `article.enabled: false`.
- [ ] Add GDELT sources with conservative settings:

```yaml
gdelt:
  lookback_hours: 24
  max_records: 100
  rate_limit_per_second: 1.0
```

- [ ] Add category tags covering runway, designer-brand momentum, retail/resale, shoes/footwear, accessories/handbags, creative-director moves, and beauty/fashion crossover.
- [ ] Keep all new source names and query strings distinct.
- [ ] Run:

```bash
.venv/bin/python -m pytest tests/test_config.py::test_public_fashion_source_pack_loads tests/test_source_packs.py::test_lint_repository_public_pack_has_no_errors -q
.venv/bin/python -m ruff check tests/test_config.py
.venv/bin/python -m ruff format --check tests/test_config.py
```

Expected: all pass.

## Task 5: Documentation

**Files:**

- Create: `docs/source-pack-quality.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] Add `docs/source-pack-quality.md` covering:
  - `source-pack-lint` examples;
  - table and JSON output meanings;
  - severity meanings;
  - each Stage 12 finding code;
  - why duplicate names, duplicate feed URLs, duplicate queries, missing tags,
    disabled sources, implicit weights, and article extraction settings matter
    for daily signal quality;
  - how to tune tags and weights for brands, designer brands, celebrities,
    footwear, bags, runway, retail, resale, and creative-director moves;
  - the command is local and does not fetch sources or check live availability.

- [ ] Update `docs/source-packs.md` to link source-pack quality docs, mention the expanded public pack categories, and show:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
```

- [ ] Update `docs/architecture.md` flow/components to include local source-pack quality diagnostics before collection.
- [ ] Update `README.md` Configuration or Quickstart docs with one short lint command and link `docs/source-pack-quality.md`.
- [ ] Update `CHANGELOG.md` with the new source-pack lint command and expanded public pack.
- [ ] Run wording guard:

```bash
rg -n "complete social listening|platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|scraper|crawler|cookie|CAPTCHA|fingerprint|proxy pool|login session" README.md docs/source-pack-quality.md docs/source-packs.md docs/architecture.md CHANGELOG.md
```

Expected: no matches except existing boundary language in docs that explicitly says the project does not include those capabilities.

## Task 6: Final Verification And Claude Code Review

- [ ] Run focused verification:

```bash
.venv/bin/python -m pytest tests/test_source_packs.py tests/test_config.py tests/test_cli.py -k "source_pack or public_fashion_source_pack" -q
.venv/bin/python -m ruff check src/fashion_radar/source_packs.py src/fashion_radar/cli.py tests/test_source_packs.py tests/test_config.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/source_packs.py src/fashion_radar/cli.py tests/test_source_packs.py tests/test_config.py tests/test_cli.py
```

- [ ] Run full verification:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage12
```

- [ ] Run installed-wheel smoke:

```bash
tmpdir="$(mktemp -d)"
.venv/bin/python -m venv "$tmpdir/venv"
wheel="$(find /tmp/fashion-radar-dist-stage12 -name '*.whl' | head -n 1)"
test -n "$wheel"
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv pip install --python "$tmpdir/venv/bin/python" "$wheel"
source_pack="$tmpdir/fashion-public.example.yaml"
cp configs/source-packs/fashion-public.example.yaml "$source_pack"
workdir="$tmpdir/workdir"
mkdir "$workdir"
explicit_config="$tmpdir/explicit-config"
explicit_data="$tmpdir/explicit-data"
explicit_reports="$tmpdir/explicit-reports"
"$tmpdir/venv/bin/fashion-radar" source-pack-lint --help
(
  cd "$workdir"
  FASHION_RADAR_CONFIG_DIR="$explicit_config" \
  FASHION_RADAR_DATA_DIR="$explicit_data" \
  FASHION_RADAR_REPORTS_DIR="$explicit_reports" \
    "$tmpdir/venv/bin/fashion-radar" source-pack-lint "$source_pack" --format json
)
test ! -e "$workdir/config"
test ! -e "$workdir/data"
test ! -e "$workdir/reports"
test ! -e "$explicit_config"
test ! -e "$explicit_data"
test ! -e "$explicit_reports"
test ! -e "$workdir/fashion-radar.sqlite"
test -z "$(find "$workdir" -name '*.sqlite*' -print -quit)"
test -z "$(find "$workdir" \( -name 'collector-*' -o -name 'collector_runs*' \) -print -quit)"
test -z "$(find "$workdir" \( -name 'fashion-radar-*.md' -o -name 'fashion-radar-*.json' \) -print -quit)"
test -z "$(find "$workdir" \( -name 'latest.md' -o -name 'latest.json' -o -name 'report-index.json' -o -name '*.eml' \) -print -quit)"
test -z "$(find "$workdir" \( -name 'reports' -o -name 'data' -o -name 'config' \) -print -quit)"
```

- [ ] Confirm CodeGraph status is healthy:

```bash
codegraph status
```

- [ ] Run secret/generated-file sanity checks:

```bash
git status --short
git diff --stat
```

- [ ] Run local scans for token prefixes, private-key headers, session artifacts, cookie artifacts, local SQLite files, generated reports, build artifacts, and CodeGraph DB files without writing token-shaped secrets into committed docs.
- [ ] Create `docs/reviews/claude-code-stage-12-code-review-prompt.md` with changed files, behavior summary, verification results, scope guard, and next-stage plan.
- [ ] Run Claude Code review:

```bash
claude -p --effort max --allowedTools=Read,Grep,Glob < docs/reviews/claude-code-stage-12-code-review-prompt.md
```

- [ ] Save review to `docs/reviews/claude-code-stage-12-code-review.md`.
- [ ] Fix every Critical and Important finding and re-review if needed.
- [ ] Commit and push only after Claude Code approves.

## Acceptance Criteria

- `fashion-radar source-pack-lint PATH` runs locally without collecting sources,
  opening SQLite, creating directories, or making network calls.
- The CLI tests prove the command does not create default or explicit
  config/data/report directories, `fashion-radar.sqlite`, `*.sqlite*`,
  collector artifacts, report artifacts, digest artifacts, or workflow
  artifacts.
- JSON output is stable enough for CI or local automation.
- Table output is readable for daily source-pack tuning.
- Duplicate source names are errors.
- Duplicate feed URLs and duplicate GDELT queries are warnings.
- Missing tags are warnings.
- Disabled sources and implicit weights are visible as informational findings.
- Duplicate source-name, URL, and query collision groups report every member of
  the group, including the first source.
- The public fashion source pack has at least 16 sources, uses only `rss` and
  `gdelt`, keeps RSS article extraction disabled, has unique names/targets, and
  tags every source.
- Docs describe configured-source quality and avoid complete market, platform,
  or social coverage claims.
- Full verification and Claude Code review pass before commit/push.
