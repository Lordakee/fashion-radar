# Stage 191 Daily Brief Heat Narrative Design

## Objective

Add a deterministic `Daily Brief` section to generated Markdown and JSON daily
reports so users can quickly see what deserves review today: top tracked
signals, candidate phrases that need review, and source caveats from the local
configured source set.

## Background

The full-project review before Stage 188 found that the repository's core
collect -> match -> score -> report pipeline is coherent, but the product still
needs to answer the user's daily question more directly: "what should I notice
today?" Stage 190 closed the source-liveness diagnostics gap. The next useful
product node should improve the report artifact itself rather than opening
another external/community handoff surface.

The existing daily report already contains deterministic ingredients:

- scored tracked entities with heat score, labels, score components, mention
  counts, source counts, and representative items;
- untracked candidate phrase reports with score, labels, mention counts, source
  counts, growth ratio, first-seen time, and representative items;
- source-health rows;
- recent collector-run rows.

Those sections are useful but scan-heavy. Stage 191 adds a compact report-level
brief built from the same local data so the dated Markdown/JSON report becomes a
stronger daily intelligence artifact.

## Scope

In scope:

- Add report-safe Pydantic models for deterministic brief output:
  - `DailyBrief`
  - `DailyBriefSection`
  - `DailyBriefItem`
- Add a pure report-layer builder that derives the brief from existing
  `EntityReport`, `CandidateReport`, `SourceHealthReport`, and
  `CollectorRunReport` values.
- Add `brief` to `DailyReport` JSON output with stable key order.
- Render a `## Daily Brief` section near the top of the Markdown report.
- Keep brief language conservative:
  - `local observed`
  - `configured sources and imported local signals`
  - `needs review`
  - no demand proof
  - no platform coverage verification
- Use this canonical scope sentence anywhere docs/tests require both scope
  phrases contiguously: `It provides no demand proof and no platform coverage
  verification.`
- Add focused unit tests for:
  - stable JSON shape;
  - deterministic section order and row limits;
  - entity, candidate, source-health, and recent-run reason codes;
  - empty report brief behavior;
  - Markdown rendering;
  - internal-field/privacy safety.
- Update first-run smoke expectations so sample reports include the new brief.
- Update user-facing docs and docs tests where daily reports are described.
- Record opencode plan/code/release reviews under `docs/reviews/`.

Out of scope:

- No new CLI command.
- No new source acquisition, scraping, browser automation, platform APIs,
  monitoring, scheduling, or connectors.
- No social-platform search implementation.
- No compliance-review product feature.
- No LLM summarization.
- No changes to `TrendDelta`, `TrendComparison`, `HeatMover`,
  `HeatMoversReport`, dashboard trend/heat row projections, scoring formulas,
  candidate scoring formulas, or matching behavior.
- No item-level evidence drilldown beyond existing representative items already
  present in the report.
- No writes beyond the already existing `report` and `run` report-file writes.

## Architecture

Stage 191 changes the report contract intentionally and narrowly.

The implementation stays inside the existing report pipeline:

```text
SQLite -> score entities -> discover candidates -> build DailyReport
      -> build DailyBrief from report-safe model rows
      -> render Markdown and JSON report files
```

The brief is derived after entity, candidate, source-health, and recent-run
rows are available. It does not query SQLite directly and does not call trend,
heat-mover, collector, source-liveness, external-tool, community-handoff, or
imported-review modules.

This intentionally avoids changing public trend/heat contracts while still
putting the product value where users already look: the daily report produced by
`fashion-radar report` and `fashion-radar run`.

## Data Model

Use Pydantic models with `ConfigDict(extra="forbid")`.

```python
class DailyBriefItem(BaseModel):
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
    name: Literal[
        "tracked_signals",
        "candidate_signals",
        "source_caveats",
    ]
    title: str
    items: list[DailyBriefItem] = Field(default_factory=list)


class DailyBrief(BaseModel):
    contract_version: str = "daily-brief/v1"
    execution_mode: Literal["local_report_derived"] = "local_report_derived"
    summary: str
    sections: list[DailyBriefSection] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
```

`DailyReport` gains:

```python
brief: DailyBrief = Field(default_factory=empty_daily_brief)
```

The default factory preserves constructability for existing tests that build a
`DailyReport` directly.

## Brief Derivation Rules

The brief builder must be deterministic:

- section order:
  1. tracked signals
  2. candidate signals
  3. source caveats
- default item limit per section: 3;
- tracked entities keep the existing report entity order;
- candidate phrases keep the existing report candidate order;
- source caveats order source-health rows by:
  1. highest `consecutive_failures`;
  2. source name;
  3. source type;
- recent failed collector runs are included only if there is remaining room in
  the source-caveats section after source-health caveats.
- item title mapping:
  - tracked entity items use `title = entity.entity_name`;
  - candidate phrase items use `title = candidate.phrase`;
  - source caveat items use `title = source.source_name`;
  - collector-run caveat items use `title = run.source_name`.

Tracked entity reason codes:

- `new_tracked_entity` when `label == "new"`;
- `rising_tracked_entity` when `label == "rising"`;
- `current_mentions_observed` when `current_mentions > 0`;
- `baseline_mentions_observed` when `baseline_mentions > 0`;
- `multiple_sources_observed` when `distinct_sources > 1`;
- `growth_component_observed` when `growth_component > 0`;
- `high_weight_source_observed` when `high_weight_component > 0`.

Candidate phrase reason codes:

- `candidate_needs_review` always;
- `new_candidate_phrase` when `label == "new_candidate"`;
- `rising_candidate_phrase` when `label == "rising_candidate"`;
- `current_mentions_observed` when `current_mentions > 0`;
- `baseline_mentions_observed` when `baseline_mentions > 0`;
- `multiple_sources_observed` when `distinct_sources > 1`;
- `growth_ratio_observed` when `growth_ratio is not None`.

Source caveat reason codes:

- `source_health_failure` when `consecutive_failures > 0`;
- `source_unhealthy_until_set` when `unhealthy_until is not None`;
- `recent_collection_failed` for failed collector-run caveats.

Summary text examples:

- Entity: `Local observed tracked brand signal from configured sources and
  imported local signals: 2 current mentions, 1 baseline mention, 2 distinct
  sources.`
- Candidate: `Local observed candidate phrase from configured sources and
  imported local signals; needs review: 2 current mentions, 0 baseline mentions,
  2 distinct sources.`
- Source caveat: `Local source caveat: Vogue Business has 2 consecutive
  failures.`

The report-level summary is also deterministic:

```text
Local observed brief from configured sources and imported local signals: 3
tracked signals, 1 candidate signal needing review, 1 source caveat. It provides
no demand proof and no platform coverage verification.
```

Pluralization rules:

- `tracked signal` for 1, `tracked signals` for every other count;
- `candidate signal needing review` for 1, `candidate signals needing review`
  for every other count;
- `source caveat` for 1, `source caveats` for every other count;
- the summary format is exactly:
  `Local observed brief from configured sources and imported local signals:
  {tracked_count} {tracked_label}, {candidate_count} {candidate_label},
  {source_caveat_count} {source_caveat_label}. It provides no demand proof and
  no platform coverage verification.`

## Markdown Rendering

The Markdown template gets this top-level section after metadata and before
`## Top Signals`:

```markdown
## Daily Brief

{brief_section}
```

Empty reports render:

```text
Local observed brief from configured sources and imported local signals: 0
tracked signals, 0 candidate signals needing review, 0 source caveats. It
provides no demand proof and no platform coverage verification.

- No daily brief items available.
```

For non-empty reports, render each section title and items:

```markdown
### Tracked Signals To Review

- The Row: Local observed tracked brand signal from configured sources and
  imported local signals: 2 current mentions, 0 baseline mentions, 2 distinct
  sources. Reasons: new_tracked_entity, current_mentions_observed,
  multiple_sources_observed.
```

Markdown rendering must sanitize pipe/newline characters in titles and summaries
using the same table-cell style already used elsewhere in the repo.

## Documentation

Update:

- `README.md`: mention that generated reports now start with a deterministic
  Daily Brief.
- `docs/architecture.md`: report component notes that Daily Brief is derived
  from local report-safe rows and does not collect/source/search.
- `docs/cli-reference.md`: the `report`/`run` entries mention that Markdown and
  JSON outputs include the Daily Brief.
- `docs/trend-deltas.md`: note that the generated report Heat Narrative reuses
  local observed heat-movement boundaries and remains review-oriented.
- `docs/daily-digest.md`: digest packaging forwards already generated reports;
  the brief is report content, not a sending or summarization feature.
- `docs/github-upload-checklist.md`: installed/sample report smoke should
  inspect the new Daily Brief section.
- `CHANGELOG.md`: Stage 191 entry.

Add docs tests that pin the conservative scope phrases and reject positive scope
claims such as `viral`, `market-wide trend`, `platform-wide popularity`,
`verified demand`, and `top social trend` in Daily Brief documentation sections.

## Review And Release Gates

Plan, code, and release reviews use local opencode:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-191-plan-review-prompt.md)"
```

Review records:

- `docs/reviews/opencode-stage-191-plan-review-prompt.md`
- `docs/reviews/opencode-stage-191-plan-review.md`
- rereview prompt/result if Critical or Important findings are fixed
- `docs/reviews/opencode-stage-191-code-review-prompt.md`
- `docs/reviews/opencode-stage-191-code-review.md`
- rereview prompt/result if needed
- `docs/reviews/opencode-stage-191-release-review-prompt.md`
- `docs/reviews/opencode-stage-191-release-review.md`
- rereview prompt/result if needed

Release gate:

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

## Next Stage Direction

After Stage 191, the best next candidates are:

1. local trend/heat explanation sidecar over `TrendComparison`, without
   changing `TrendDelta` or `HeatMover` JSON contracts;
2. item-level evidence drilldown for local observed movers;
3. a focused public source-pack coverage increment validated with
   `source-liveness`;
4. diacritic/punctuation matching quality improvements for fashion names.
