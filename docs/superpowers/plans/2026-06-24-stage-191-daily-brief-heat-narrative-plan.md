# Stage 191 Daily Brief Heat Narrative Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic Daily Brief to generated Markdown and JSON reports so users can quickly review top local observed fashion signals, candidate phrases, and source caveats.

**Architecture:** Extend only the existing daily report contract. Add focused report-safe Pydantic models, derive the brief from already-built report rows, render it in Markdown, and document it as local report-derived narrative. Do not add a new CLI command, new source acquisition, new platform connectors, LLM summarization, or changes to trend/heat/dashboard contracts.

**Tech Stack:** Python 3.11, Pydantic, Typer report/run commands through existing workflows, pytest, ruff, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/templates/daily_report.md`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/daily-digest.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_trend_deltas_docs.py`
- Modify: `tests/test_daily_digest_docs.py`
- Modify: `CHANGELOG.md`
- Add: `docs/superpowers/specs/2026-06-24-stage-191-daily-brief-heat-narrative-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-191-daily-brief-heat-narrative-plan.md`
- Add after plan review: `docs/reviews/opencode-stage-191-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-191-plan-review.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-191-plan-rereview-prompt.md`
- Add after plan fixes if needed: `docs/reviews/opencode-stage-191-plan-rereview.md`
- Add after implementation: `docs/reviews/opencode-stage-191-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-191-code-review.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-191-code-rereview-prompt.md`
- Add after code fixes if needed: `docs/reviews/opencode-stage-191-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-191-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-191-release-review.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-191-release-rereview-prompt.md`
- Add after release fixes if needed: `docs/reviews/opencode-stage-191-release-rereview.md`

## Task 1: Report Model And Brief Builder

**Files:**

- Modify: `src/fashion_radar/models/report.py`
- Modify: `src/fashion_radar/reports.py`
- Modify: `tests/test_reports.py`

- [ ] **Step 1: Add RED tests for the brief JSON contract and empty-report behavior**

Add these imports in `tests/test_reports.py`:

```python
from fashion_radar.models.report import (
    REPORT_SNIPPET_MAX_CHARS,
    CandidateReport,
    DailyBrief,
    DailyBriefItem,
    DailyBriefSection,
    DailyReport,
    EntityReport,
    ReportMetadata,
    RepresentativeItem,
)
```

Add tests:

```python
def test_daily_report_includes_stable_daily_brief_json_shape(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row",
        entity_name="The Row",
        source_name="Vogue Business",
        source_weight=1.7,
        collected_at=AS_OF - timedelta(hours=1),
        summary="The Row gains local observed coverage.",
    )
    _store_item(
        engine,
        url="https://example.com/le-teckel",
        entity_name="Tracked Placeholder",
        source_name="Fashionista",
        collected_at=AS_OF - timedelta(hours=2),
        summary="Le Teckel bag appears in a local observed item.",
    )
    _store_item(
        engine,
        url="https://example.com/le-teckel-again",
        entity_name="Tracked Placeholder",
        source_name="WWD",
        collected_at=AS_OF - timedelta(hours=3),
        summary="Le Teckel bag appears again in local observed coverage.",
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        candidate_discovery=CandidateDiscoverySettings(),
        entity_config=None,
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    parsed = json.loads(render_json_report(report))

    assert list(parsed) == [
        "metadata",
        "brief",
        "entities",
        "candidates",
        "source_health",
        "recent_runs",
    ]
    assert list(parsed["brief"]) == [
        "contract_version",
        "execution_mode",
        "summary",
        "sections",
        "boundaries",
    ]
    assert parsed["brief"]["contract_version"] == "daily-brief/v1"
    assert parsed["brief"]["execution_mode"] == "local_report_derived"
    assert "Local observed brief" in parsed["brief"]["summary"]
    assert (
        "It provides no demand proof and no platform coverage verification."
        in parsed["brief"]["summary"]
    )
    assert [section["name"] for section in parsed["brief"]["sections"]] == [
        "tracked_signals",
        "candidate_signals",
        "source_caveats",
    ]
    assert parsed["brief"]["sections"][0]["items"][0]["kind"] == "tracked_entity"
    assert parsed["brief"]["sections"][0]["items"][0]["title"] == "The Row"
    assert parsed["brief"]["sections"][0]["items"][0]["reason_codes"] == [
        "new_tracked_entity",
        "current_mentions_observed",
        "high_weight_source_observed",
    ]
    assert parsed["brief"]["sections"][1]["items"][0]["kind"] == "candidate_phrase"
    assert parsed["brief"]["sections"][1]["items"][0]["needs_review"] is True
    assert parsed["brief"]["sections"][1]["items"][0]["reason_codes"] == [
        "candidate_needs_review",
        "new_candidate_phrase",
        "current_mentions_observed",
        "multiple_sources_observed",
    ]
    assert parsed["brief"]["boundaries"] == [
        "Daily Brief is derived from local report rows for configured sources and imported local signals.",
        "Daily Brief does not collect sources, search platforms, prove demand, or verify platform coverage.",
    ]


def test_empty_database_produces_useful_empty_daily_brief(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    parsed = json.loads(render_json_report(report))
    markdown = render_markdown_report(report)

    assert parsed["brief"]["summary"] == (
        "Local observed brief from configured sources and imported local signals: "
        "0 tracked signals, 0 candidate signals needing review, 0 source caveats. "
        "It provides no demand proof and no platform coverage verification."
    )
    assert all(section["items"] == [] for section in parsed["brief"]["sections"])
    assert "## Daily Brief" in markdown
    assert "- No daily brief items available." in markdown
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_daily_report_includes_stable_daily_brief_json_shape tests/test_reports.py::test_empty_database_produces_useful_empty_daily_brief -q
```

Expected: fail because `DailyBrief`, `DailyBriefItem`, and `DailyBriefSection`
do not exist and `DailyReport` has no `brief` field.

- [ ] **Step 3: Implement report models and builder**

In `src/fashion_radar/models/report.py`, add:

```python
from typing import Literal
```

Then add before `DailyReport`:

```python
DAILY_BRIEF_BOUNDARIES = (
    "Daily Brief is derived from local report rows for configured sources and imported local signals.",
    "Daily Brief does not collect sources, search platforms, prove demand, or verify platform coverage.",
)


class DailyBriefItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal[
        "tracked_entity",
        "candidate_phrase",
        "source_caveat",
        "collector_run_caveat",
    ]
    title: str
    summary: str
    reason_codes: list[str] = Field(default_factory=list)
    current_mentions: int | None = None
    baseline_mentions: int | None = None
    distinct_sources: int | None = None
    score: float | None = None
    needs_review: bool = False


class DailyBriefSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["tracked_signals", "candidate_signals", "source_caveats"]
    title: str
    items: list[DailyBriefItem] = Field(default_factory=list)


class DailyBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = "daily-brief/v1"
    execution_mode: Literal["local_report_derived"] = "local_report_derived"
    summary: str
    sections: list[DailyBriefSection] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=lambda: list(DAILY_BRIEF_BOUNDARIES))


def empty_daily_brief() -> DailyBrief:
    return DailyBrief(
        summary=(
            "Local observed brief from configured sources and imported local signals: "
            "0 tracked signals, 0 candidate signals needing review, 0 source caveats. "
            "It provides no demand proof and no platform coverage verification."
        ),
        sections=[
            DailyBriefSection(name="tracked_signals", title="Tracked Signals To Review"),
            DailyBriefSection(name="candidate_signals", title="Candidate Signals Needing Review"),
            DailyBriefSection(name="source_caveats", title="Source Caveats"),
        ],
    )
```

Change `DailyReport` to:

```python
class DailyReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: ReportMetadata
    brief: DailyBrief = Field(default_factory=empty_daily_brief)
    entities: list[EntityReport] = Field(default_factory=list)
    candidates: list[CandidateReport] = Field(default_factory=list)
    source_health: list[SourceHealthReport] = Field(default_factory=list)
    recent_runs: list[CollectorRunReport] = Field(default_factory=list)
```

In `src/fashion_radar/reports.py`, import `DailyBrief`, `DailyBriefItem`, and
`DailyBriefSection`. Build entities/candidates/source health/recent runs into
local variables, then pass:

```python
brief=build_daily_brief(
    entities=entities,
    candidates=candidates,
    source_health=source_health_reports,
    recent_runs=recent_run_reports,
),
```

Add these helpers in `src/fashion_radar/reports.py`:

```python
DAILY_BRIEF_SECTION_LIMIT = 3


def build_daily_brief(
    *,
    entities: list[EntityReport],
    candidates: list[CandidateReport],
    source_health: list[SourceHealthReport],
    recent_runs: list[CollectorRunReport],
    limit_per_section: int = DAILY_BRIEF_SECTION_LIMIT,
) -> DailyBrief:
    if limit_per_section < 0:
        raise ValueError("limit_per_section must be at least 0")

    tracked_items = [_brief_item_for_entity(entity) for entity in entities[:limit_per_section]]
    candidate_items = [
        _brief_item_for_candidate(candidate) for candidate in candidates[:limit_per_section]
    ]
    source_items = _source_caveat_items(
        source_health=source_health,
        recent_runs=recent_runs,
        limit=limit_per_section,
    )
    return DailyBrief(
        summary=_daily_brief_summary(
            tracked_count=len(tracked_items),
            candidate_count=len(candidate_items),
            source_caveat_count=len(source_items),
        ),
        sections=[
            DailyBriefSection(
                name="tracked_signals",
                title="Tracked Signals To Review",
                items=tracked_items,
            ),
            DailyBriefSection(
                name="candidate_signals",
                title="Candidate Signals Needing Review",
                items=candidate_items,
            ),
            DailyBriefSection(name="source_caveats", title="Source Caveats", items=source_items),
        ],
    )
```

Add the deterministic summary helper with exact pluralization:

```python
def _daily_brief_summary(
    *,
    tracked_count: int,
    candidate_count: int,
    source_caveat_count: int,
) -> str:
    return (
        "Local observed brief from configured sources and imported local signals: "
        f"{tracked_count} {_count_label(tracked_count, 'tracked signal', 'tracked signals')}, "
        f"{candidate_count} "
        f"{_count_label(candidate_count, 'candidate signal needing review', 'candidate signals needing review')}, "
        f"{source_caveat_count} "
        f"{_count_label(source_caveat_count, 'source caveat', 'source caveats')}. "
        "It provides no demand proof and no platform coverage verification."
    )


def _count_label(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural
```

Use these explicit item title mappings:

- tracked entity items set `title=entity.entity_name`;
- candidate phrase items set `title=candidate.phrase`;
- source-health caveat items set `title=source.source_name`;
- collector-run caveat items set `title=run.source_name`.

Add entity and candidate item helpers with stable reason-code order:

```python
def _brief_item_for_entity(entity: EntityReport) -> DailyBriefItem:
    return DailyBriefItem(
        kind="tracked_entity",
        title=entity.entity_name,
        summary=(
            f"Local observed tracked {entity.entity_type} signal from configured sources "
            f"and imported local signals: {entity.current_mentions} "
            f"{_count_label(entity.current_mentions, 'current mention', 'current mentions')}, "
            f"{entity.baseline_mentions} "
            f"{_count_label(entity.baseline_mentions, 'baseline mention', 'baseline mentions')}, "
            f"{entity.distinct_sources} "
            f"{_count_label(entity.distinct_sources, 'distinct source', 'distinct sources')}."
        ),
        reason_codes=_entity_reason_codes(entity),
        current_mentions=entity.current_mentions,
        baseline_mentions=entity.baseline_mentions,
        distinct_sources=entity.distinct_sources,
        score=entity.heat_score,
    )


def _brief_item_for_candidate(candidate: CandidateReport) -> DailyBriefItem:
    return DailyBriefItem(
        kind="candidate_phrase",
        title=candidate.phrase,
        summary=(
            "Local observed candidate phrase from configured sources and imported local "
            f"signals; needs review: {candidate.current_mentions} "
            f"{_count_label(candidate.current_mentions, 'current mention', 'current mentions')}, "
            f"{candidate.baseline_mentions} "
            f"{_count_label(candidate.baseline_mentions, 'baseline mention', 'baseline mentions')}, "
            f"{candidate.distinct_sources} "
            f"{_count_label(candidate.distinct_sources, 'distinct source', 'distinct sources')}."
        ),
        reason_codes=_candidate_reason_codes(candidate),
        current_mentions=candidate.current_mentions,
        baseline_mentions=candidate.baseline_mentions,
        distinct_sources=candidate.distinct_sources,
        score=candidate.score,
        needs_review=True,
    )


def _entity_reason_codes(entity: EntityReport) -> list[str]:
    codes: list[str] = []
    if entity.label == "new":
        codes.append("new_tracked_entity")
    if entity.label == "rising":
        codes.append("rising_tracked_entity")
    if entity.current_mentions > 0:
        codes.append("current_mentions_observed")
    if entity.baseline_mentions > 0:
        codes.append("baseline_mentions_observed")
    if entity.distinct_sources > 1:
        codes.append("multiple_sources_observed")
    if entity.growth_component > 0:
        codes.append("growth_component_observed")
    if entity.high_weight_component > 0:
        codes.append("high_weight_source_observed")
    return codes


def _candidate_reason_codes(candidate: CandidateReport) -> list[str]:
    codes = ["candidate_needs_review"]
    if candidate.label == "new_candidate":
        codes.append("new_candidate_phrase")
    if candidate.label == "rising_candidate":
        codes.append("rising_candidate_phrase")
    if candidate.current_mentions > 0:
        codes.append("current_mentions_observed")
    if candidate.baseline_mentions > 0:
        codes.append("baseline_mentions_observed")
    if candidate.distinct_sources > 1:
        codes.append("multiple_sources_observed")
    if candidate.growth_ratio is not None:
        codes.append("growth_ratio_observed")
    return codes
```

Use deterministic helper functions for source caveat summaries and reason codes.
The summary text must include `Local observed` or `Local source caveat` and must
not use `viral`, `market-wide trend`, `platform-wide popularity`,
`verified demand`, or `top social trend`.

- [ ] **Step 4: Run model/builder tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_daily_report_includes_stable_daily_brief_json_shape tests/test_reports.py::test_empty_database_produces_useful_empty_daily_brief -q
```

Expected: pass.

## Task 2: Markdown Rendering And Report/Run Smoke Coverage

**Files:**

- Modify: `src/fashion_radar/reports.py`
- Modify: `src/fashion_radar/templates/daily_report.md`
- Modify: `tests/test_reports.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add RED tests for Markdown rendering, report CLI output, and first-run fixtures**

In `tests/test_reports.py`, add:

```python
def test_markdown_report_renders_daily_brief_before_top_signals(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "fashion.db")
    initialize_schema(engine)
    _store_item(
        engine,
        url="https://example.com/the-row",
        entity_name="The Row",
        source_name="Vogue Business",
        source_weight=1.7,
        collected_at=AS_OF - timedelta(hours=1),
        summary="The Row local observed signal.",
    )

    report = build_daily_report(
        engine,
        scoring=ScoringSettings(),
        as_of=AS_OF,
        generated_at=AS_OF,
    )
    markdown = render_markdown_report(report)

    assert markdown.index("## Daily Brief") < markdown.index("## Top Signals")
    assert "### Tracked Signals To Review" in markdown
    assert "- The Row:" in markdown
    assert "Reasons:" in markdown
    assert "It provides no demand proof and no platform coverage verification." in markdown
    for forbidden in (
        "viral",
        "market-wide trend",
        "platform-wide popularity",
        "verified demand",
        "top social trend",
    ):
        assert forbidden not in markdown.lower()
```

In `tests/test_cli.py::test_report_command_writes_markdown_and_json`, add:

```python
    markdown_text = markdown_path.read_text(encoding="utf-8")
    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "## Daily Brief" in markdown_text
    assert "Local observed brief" in markdown_text
    assert json_payload["brief"]["contract_version"] == "daily-brief/v1"
    assert json_payload["brief"]["sections"][0]["items"][0]["title"] == "The Row"
    assert json_payload["brief"]["sections"][0]["items"][0]["reason_codes"] == [
        "new_tracked_entity",
        "current_mentions_observed",
        "high_weight_source_observed",
    ]
```

In `tests/test_first_run_smoke.py::report_payload`, add a `brief` object
between `metadata` and `entities` in the expected sample fixture. In
`tests/test_first_run_smoke.py::report_markdown`, add `## Daily Brief` and the
exact line `- The Row: Local observed tracked brand signal from configured
sources and imported local signals: 1 current mention, 0 baseline mentions, 1
distinct source. Reasons: new_tracked_entity, current_mentions_observed,
high_weight_source_observed.` before `## Top Signals`.

In `scripts/check_first_run_smoke.py`, extend report validation so the generated
Markdown must include `## Daily Brief`, the generated JSON must include
`brief.contract_version == "daily-brief/v1"`, and the brief must mention
`The Row`.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py::test_markdown_report_renders_daily_brief_before_top_signals tests/test_cli.py::test_report_command_writes_markdown_and_json tests/test_first_run_smoke.py -q
```

Expected: the new assertions fail until Markdown rendering and fixtures are
updated.

- [ ] **Step 3: Implement Markdown renderer and template changes**

In `src/fashion_radar/templates/daily_report.md`, add:

```markdown
## Daily Brief

{brief_section}
```

between the metadata block and `## Top Signals`.

In `render_markdown_report`, pass:

```python
brief_section=_render_daily_brief(report.brief),
```

Add:

```python
def _render_daily_brief(brief: DailyBrief) -> str:
    lines = [brief.summary]
    any_items = False
    for section in brief.sections:
        lines.extend(["", f"### {section.title}"])
        if not section.items:
            lines.append("- No daily brief items available.")
            continue
        any_items = True
        for item in section.items:
            reasons = ", ".join(item.reason_codes) if item.reason_codes else "none"
            lines.append(
                f"- {_table_cell(item.title)}: {_table_cell(item.summary)} "
                f"Reasons: {_table_cell(reasons)}."
            )
    if not any_items:
        return "\n".join([brief.summary, "", "- No daily brief items available."])
    return "\n".join(lines)
```

If no `_table_cell` helper exists in `reports.py`, add a private helper:

```python
def _table_cell(value: str) -> str:
    return " ".join(value.replace("|", "/").replace("\r", " ").replace("\n", " ").split())
```

- [ ] **Step 4: Run report/render tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py tests/test_cli.py::test_report_command_writes_markdown_and_json tests/test_first_run_smoke.py -q
```

Expected: pass.

## Task 3: Documentation And Docs Tests

**Files:**

- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/trend-deltas.md`
- Modify: `docs/daily-digest.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_trend_deltas_docs.py`
- Modify: `tests/test_daily_digest_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add RED docs tests for Daily Brief documentation**

In `tests/test_cli_docs.py`, add constants:

```python
DAILY_BRIEF_DOCS = (
    README,
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    ROOT / "docs" / "daily-digest.md",
    UPLOAD_CHECKLIST,
    CHANGELOG,
)
DAILY_BRIEF_REQUIRED_PHRASES = (
    "Daily Brief",
    "Heat Narrative",
    "local observed",
    "configured sources and imported local signals",
    "needs review",
    "no demand proof",
    "no platform coverage verification",
)
DAILY_BRIEF_FORBIDDEN_POSITIVE_CLAIMS = (
    "viral",
    "market-wide trend",
    "platform-wide popularity",
    "verified demand",
    "top social trend",
)
```

Add:

```python
def test_daily_brief_docs_are_bounded_and_discoverable() -> None:
    for path in DAILY_BRIEF_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for phrase in DAILY_BRIEF_REQUIRED_PHRASES:
            assert phrase.casefold() in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"


def test_daily_brief_docs_do_not_make_positive_scope_claims() -> None:
    for path in DAILY_BRIEF_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for claim in DAILY_BRIEF_FORBIDDEN_POSITIVE_CLAIMS:
            assert claim not in normalized, f"{path.relative_to(ROOT)} uses {claim!r}"
```

In `tests/test_daily_digest_docs.py`, add:

```python
def test_daily_digest_docs_note_brief_is_existing_report_content() -> None:
    doc = _read_daily_digest_doc()
    normalized = " ".join(doc.split()).casefold()

    assert "daily brief" in normalized
    assert "already-generated report" in normalized
    assert "not a sending or llm summarization feature" in normalized
```

In `tests/test_trend_deltas_docs.py`, add:

```python
def test_trend_deltas_docs_note_heat_narrative_remains_review_oriented() -> None:
    normalized = _normalized(_read_trend_deltas_doc())

    assert "heat narrative" in normalized
    assert "local observed" in normalized
    assert "review-oriented" in normalized
    assert "market-wide ranking" not in normalized
```

- [ ] **Step 2: Run docs tests to verify RED**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_daily_brief_docs_are_bounded_and_discoverable tests/test_cli_docs.py::test_daily_brief_docs_do_not_make_positive_scope_claims tests/test_daily_digest_docs.py::test_daily_digest_docs_note_brief_is_existing_report_content tests/test_trend_deltas_docs.py::test_trend_deltas_docs_note_heat_narrative_remains_review_oriented -q
```

Expected: fail because docs do not mention Daily Brief yet.

- [ ] **Step 3: Update docs**

Update docs with concise wording:

Every file in `DAILY_BRIEF_DOCS` must contain the exact sentence:
`It provides no demand proof and no platform coverage verification.`

- `README.md`: Generated reports include a deterministic Daily Brief summarizing
  local observed tracked signals, candidate phrases that need review, and source
  caveats from configured sources and imported local signals. Describe this as
  a Heat Narrative and include the exact sentence: `It provides no demand proof
  and no platform coverage verification.`
- `docs/architecture.md`: Reports component derives Daily Brief from
  report-safe rows; it does not collect, search, scrape, call platform APIs,
  write source health, or prove demand/coverage.
- `docs/cli-reference.md`: `report` and `run` entries say the Markdown/JSON
  report includes Daily Brief.
- `docs/trend-deltas.md`: tie Heat Narrative wording back to local observed
  trend deltas and review-oriented movement, not market-wide ranking.
- `docs/daily-digest.md`: digest packages already generated reports; Daily
  Brief is already-generated report content and not a sending or LLM
  summarization feature.
- `docs/github-upload-checklist.md`: report smoke assertions include Daily
  Brief.
- `tests/test_trend_deltas_docs.py`: add a focused docs parity check that the
  Heat Narrative remains tied to local observed trend deltas and review-oriented
  movement.
- `CHANGELOG.md`: add Stage 191 entry.

- [ ] **Step 4: Run docs tests to verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py -q
```

Expected: pass.

## Task 4: Review, Full Gate, Commit, And Push

**Files:**

- Add/modify all Stage 191 files listed above.
- Add review artifacts under `docs/reviews/`.

- [ ] **Step 1: Run focused test and formatting gate**

Run:

```bash
uv --no-config run --frozen pytest tests/test_reports.py tests/test_cli.py::test_report_command_writes_markdown_and_json tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py tests/test_reports.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/models/report.py src/fashion_radar/reports.py tests/test_reports.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py
```

Expected: pass.

- [ ] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-191-code-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-191-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-191-code-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. If there are Critical or Important
findings, fix them and create `opencode-stage-191-code-rereview-prompt.md` and
`opencode-stage-191-code-rereview.md`.

- [ ] **Step 3: Run full release gate**

Run:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then exit 1; fi
```

Expected: pass; token and extraheader checks print no matches.

- [ ] **Step 4: Request opencode release review**

Create `docs/reviews/opencode-stage-191-release-review-prompt.md` and run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-191-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-191-release-review.md
rm -f "$tmp_review"
```

Expected: no Critical or Important findings. If there are Critical or Important
findings, fix them and create release rereview artifacts.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add \
  src/fashion_radar/models/report.py \
  src/fashion_radar/reports.py \
  src/fashion_radar/templates/daily_report.md \
  tests/test_reports.py \
  tests/test_cli.py \
  tests/test_first_run_smoke.py \
  scripts/check_first_run_smoke.py \
  README.md \
  docs/architecture.md \
  docs/cli-reference.md \
  docs/trend-deltas.md \
  docs/daily-digest.md \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py \
  tests/test_trend_deltas_docs.py \
  tests/test_daily_digest_docs.py \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-24-stage-191-daily-brief-heat-narrative-design.md \
  docs/superpowers/plans/2026-06-24-stage-191-daily-brief-heat-narrative-plan.md \
  docs/reviews/opencode-stage-191-plan-review-prompt.md \
  docs/reviews/opencode-stage-191-plan-review.md \
  docs/reviews/opencode-stage-191-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-191-plan-rereview.md \
  docs/reviews/opencode-stage-191-code-review-prompt.md \
  docs/reviews/opencode-stage-191-code-review.md \
  docs/reviews/opencode-stage-191-code-rereview-prompt.md \
  docs/reviews/opencode-stage-191-code-rereview.md \
  docs/reviews/opencode-stage-191-release-review-prompt.md \
  docs/reviews/opencode-stage-191-release-review.md \
  docs/reviews/opencode-stage-191-release-rereview-prompt.md \
  docs/reviews/opencode-stage-191-release-rereview.md
git commit -m "feat: add daily brief heat narrative"
git push origin main
```

If a rereview artifact was not needed and does not exist, omit it from `git add`.
Expected: commit and push succeed.

## Self-Review

- Spec coverage: The plan covers report models, deterministic brief derivation,
  Markdown/JSON output, CLI report smoke, first-run smoke, docs, review
  artifacts, full gate, commit, and push.
- Red-flag scan: No unresolved marker text remains.
- Type consistency: Model and helper names match the Stage 191 design.
- Scope check: No new CLI command, source acquisition, platform search,
  community handoff expansion, compliance-review feature, trend/heat contract
  mutation, or dashboard projection change is included.
