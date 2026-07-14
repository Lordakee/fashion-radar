# Stage 390 Source Liveness RSS Freshness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Add read-only RSS/RSSHub freshness evidence to `source-liveness` so a
reachable but stale feed is distinguishable from a feed publishing current
entries.

**Architecture:** Extend the existing `source-liveness/v1` result rows with
additive timestamp evidence derived from the already fetched feed. Keep the
current five statuses, classify stale non-malformed feeds as
`degraded/warning/stale_feed`, classify nonempty undated feeds as
`live/info/freshness_unknown`, and leave GDELT and all collection/report paths
unchanged.

**Tech Stack:** Python 3.11+, feedparser, standard-library datetime/calendar,
Pydantic, Typer, pytest, Ruff, uv, Markdown contract tests, Git.

---

## Fixed Interface Contract

Every worker must use these exact names and signatures:

```python
DEFAULT_SOURCE_LIVENESS_STALE_AFTER_HOURS = 72


def build_source_liveness_report(
    path: Path,
    *,
    stale_after_hours: int = DEFAULT_SOURCE_LIVENESS_STALE_AFTER_HOURS,
    client_factory: SourceHttpClientFactory | None = None,
    clock: Callable[[], datetime] | None = None,
    monotonic: Callable[[], float] | None = None,
) -> SourceLivenessReport:
    ...
```

Add these fields after `records_seen` in `SourceLivenessResult`:

```python
dated_records_seen: int | None = None
latest_entry_at: datetime | None = None
latest_entry_age_hours: int | None = None
```

The CLI option is exactly:

```text
--stale-after-hours INTEGER
```

Its default is `72`, its minimum is `1`, and the CLI passes it to the builder
as the keyword `stale_after_hours`.

## File Map

- Modify: `src/fashion_radar/source_liveness.py` - freshness evidence, RSS
  classification, additive result fields, and table output.
- Modify: `tests/test_source_liveness.py` - result contract, RSS freshness
  matrix, threshold boundaries, parser precedence, and GDELT regressions.
- Modify: `src/fashion_radar/cli.py` - threshold option and builder wiring.
- Modify: `tests/test_cli.py` - CLI help, option forwarding, validation, output,
  and exit semantics.
- Modify: `README.md`, `docs/source-packs.md`,
  `docs/source-pack-quality.md`, `docs/cli-reference.md`,
  `docs/architecture.md`, and `CHANGELOG.md` - public behavior and limits.
- Modify: `tests/test_cli_docs.py`, `tests/test_source_packs_docs.py`, and
  `tests/test_source_pack_quality_docs.py` - public documentation contracts.
- Create when Claude returns a complete review:
  `docs/reviews/claude-code-stage-390-plan-review.md`.
- Create: `docs/reviews/opencode-stage-390-plan-review.md` - OpenCode revision
  after Claude, or the formal fallback review when Claude is unavailable.
- Create if required: `docs/reviews/claude-code-stage-390-plan-rereview.md` or
  `docs/reviews/opencode-stage-390-plan-rereview.md` - plan rereview gate.
- Create: `docs/reviews/claude-code-stage-390-code-review.md` and, if required,
  `docs/reviews/claude-code-stage-390-code-rereview.md` - code gates.
- Create: `docs/reviews/claude-code-stage-390-release-review.md` or the matching
  OpenCode fallback release record - release gate.

## Parallel Ownership And Order

- Coordinator owns Task 0, integration, review records, release validation,
  conflict resolution, and publication.
- Worker A owns `src/fashion_radar/source_liveness.py` and
  `tests/test_source_liveness.py`.
- Worker B owns `src/fashion_radar/cli.py` and `tests/test_cli.py`.
- Worker C owns `README.md`, `docs/source-packs.md`,
  `docs/source-pack-quality.md`, `docs/cli-reference.md`,
  `docs/architecture.md`, `CHANGELOG.md`, `tests/test_cli_docs.py`,
  `tests/test_source_packs_docs.py`, and
  `tests/test_source_pack_quality_docs.py`.

Worker C must preserve the exact roadmap phrases asserted by
`tests/test_review_protocol_docs.py`; that test remains read-only in this stage
and is included in Worker C's focused verification.

Task 0 must finish before any implementation. Worker A and Worker C may start
in parallel. Worker B starts after Worker A completes Task 1 Step 4, which makes
the fixed constant and builder keyword available, and may then run in parallel
with Worker A's remaining RSS classification work and Worker C. Workers must
stage only owned files and must not commit while another worker has staged
content. The coordinator creates the integrated implementation commit.

## Task 0: Review And Accept The Plan

**Files:**

- Create if Claude returns a complete review:
  `docs/reviews/claude-code-stage-390-plan-review.md`
- Create: `docs/reviews/opencode-stage-390-plan-review.md`
- Create if needed: `docs/reviews/claude-code-stage-390-plan-rereview.md` or
  `docs/reviews/opencode-stage-390-plan-rereview.md`
- Modify if needed: this plan and the Stage 390 design

- [ ] **Step 1: Request the primary Claude Code plan review**

Use max effort, read-only plan mode, no persistent session, and only Read,
Grep, Glob, LS, and Bash. Give Claude Code the goal, architecture, fixed
interface, status matrix, parallel ownership, tests, non-goals, and exact files.

The completed record must contain one coherent body with exactly one verdict,
no live-capture stub, no raw tool log, no timeout text presented as approval,
and no credential material.

If Claude does not return a complete body, retry once with a narrower prompt as
required by `docs/REVIEW_PROTOCOL.md`. If that retry also fails, do not create a
Claude review record or commit timeout text; use the OpenCode review in Step 2
as the formal fallback gate.

- [ ] **Step 2: Request the OpenCode plan revision**

Run local OpenCode with `zhipuai-coding-plan/glm-5.2 --variant max` after the
primary review, or as the formal fallback when Claude is unavailable. Ask it to
verify the same current plan and revise concrete technical issues, especially
contract compatibility, datetime conversion, threshold boundaries,
malformed-feed precedence, and worker file ownership.

- [ ] **Step 3: Resolve plan findings and obtain a Claude rereview**

Fix every critical and important finding. If any plan text changes, run:

```bash
git diff --check
rg -n '\b([T]ODO|[T]BD|[F]IXME)\b' \
  docs/superpowers/specs/2026-07-14-stage-390-source-liveness-rss-freshness-design.md \
  docs/superpowers/plans/2026-07-14-stage-390-source-liveness-rss-freshness-plan.md
```

Expected: `git diff --check` exits zero and the placeholder scan prints nothing.
Request a fresh Claude Code rereview when a review-driven plan diff exists and
Claude is available; otherwise request an OpenCode GLM 5.2 max fallback
rereview. Tasks 1 through 4 must not begin until the current plan has no
critical or important finding.

## Task 1: Add The Freshness Result Contract And Helpers

**Owner:** Worker A

**Files:**

- Modify: `tests/test_source_liveness.py`
- Modify: `src/fashion_radar/source_liveness.py`

- [ ] **Step 1: Extend the exact result JSON contract test**

In `test_source_liveness_report_json_shape_is_stable`, keep the existing report
key list unchanged. Add an exact key assertion for the disabled result row:

```python
assert list(payload["results"][0]) == [
    "source_name",
    "source_type",
    "enabled",
    "target_type",
    "target",
    "status",
    "severity",
    "code",
    "message",
    "checked_at",
    "elapsed_ms",
    "records_seen",
    "dated_records_seen",
    "latest_entry_at",
    "latest_entry_age_hours",
    "error_type",
]
assert payload["results"][0]["dated_records_seen"] is None
assert payload["results"][0]["latest_entry_at"] is None
assert payload["results"][0]["latest_entry_age_hours"] is None
```

Update `test_render_source_liveness_table_includes_summary_rows_and_boundaries`
to construct a dated RSS row:

```python
dated_records_seen=2,
latest_entry_at=datetime(2026, 6, 24, 0, 0, tzinfo=UTC),
latest_entry_age_hours=2,
```

Require the new heading and cells:

```python
assert lines[9] == (
    "Source | Type | Status | Severity | Records | Dated | Latest age | Target | Message"
)
assert " | 2 | 2 | 2h | " in lines[10]
```

- [ ] **Step 2: Run the contract tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_source_liveness.py::test_source_liveness_report_json_shape_is_stable \
  tests/test_source_liveness.py::test_render_source_liveness_table_includes_summary_rows_and_boundaries \
  -q
```

Expected: failures because the three fields and table columns do not exist.

- [ ] **Step 3: Add the constant, fields, and evidence value object**

In `src/fashion_radar/source_liveness.py`, add imports:

```python
import calendar
from dataclasses import dataclass
from math import ceil
from time import struct_time
```

Add the constant beside the existing contract constants:

```python
DEFAULT_SOURCE_LIVENESS_STALE_AFTER_HOURS = 72
```

Add the three optional result fields after `records_seen` exactly as specified
in the Fixed Interface Contract.

Add this private value object after `SourceHttpClientFactory`:

```python
@dataclass(frozen=True)
class _RssFreshnessEvidence:
    dated_records_seen: int
    latest_entry_at: datetime | None
    latest_entry_age_hours: int | None
    stale: bool
```

- [ ] **Step 4: Add the builder keyword and validation before config loading**

First add this test before changing the builder:

```python
def test_source_liveness_rejects_invalid_stale_threshold_before_config_or_network(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing-sources.yaml"

    with pytest.raises(ValueError, match="stale_after_hours must be at least 1"):
        build_source_liveness_report(missing_path, stale_after_hours=0)
```

Run it and verify RED because the builder does not yet accept the keyword:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_source_liveness.py::test_source_liveness_rejects_invalid_stale_threshold_before_config_or_network \
  -q
```

Change `build_source_liveness_report` to the fixed signature. Its first lines
must be:

```python
stale_after_hours = _validate_stale_after_hours(stale_after_hours)
checked_at = _checked_at(clock)
```

Pass `stale_after_hours` only to RSS/RSSHub probes:

```python
results.append(
    _probe_rss_source(
        source,
        factory,
        checked_at,
        monotonic_clock,
        stale_after_hours,
    )
)
```

Add:

```python
def _validate_stale_after_hours(value: int) -> int:
    if value < 1:
        raise ValueError("stale_after_hours must be at least 1")
    return value
```

Rerun the same focused test. Expected: GREEN after the validation helper is
implemented, proving validation occurs before config loading or network setup.

- [ ] **Step 5: Extend `_result` and table rendering**

Add optional keyword arguments to `_result`:

```python
dated_records_seen: int | None = None,
latest_entry_at: datetime | None = None,
latest_entry_age_hours: int | None = None,
```

Forward them to `SourceLivenessResult`. Existing callers rely on the defaults.

Change the table heading to the exact string from Step 1. Before rendering each
row, derive:

```python
dated = "n/a" if result.dated_records_seen is None else str(result.dated_records_seen)
if result.latest_entry_age_hours is not None:
    latest_age = f"{result.latest_entry_age_hours}h"
elif (
    result.source_type in {SourceType.RSS, SourceType.RSSHUB}
    and result.records_seen is not None
    and result.records_seen > 0
    and result.dated_records_seen == 0
):
    latest_age = "unknown"
else:
    latest_age = "n/a"
```

Insert `dated` and `latest_age` between the existing Records and Target cells.

- [ ] **Step 6: Run the result contract tests and verify GREEN**

Run the Step 2 command. Expected: both selected tests pass.

## Task 2: Classify Fresh, Stale, Undated, And Malformed RSS Feeds

**Owner:** Worker A

**Files:**

- Modify: `tests/test_source_liveness.py`
- Modify: `src/fashion_radar/source_liveness.py`

- [ ] **Step 1: Add reusable RSS fixture helpers**

Near the existing `write_yaml` helper, add:

```python
def rss_item(
    title: str,
    *,
    published: str | None = None,
) -> str:
    published_xml = f"<pubDate>{published}</pubDate>" if published else ""
    slug = title.casefold().replace(" ", "-")
    return (
        "<item>"
        f"<title>{title}</title>"
        f"<link>https://example.com/{slug}</link>"
        f"{published_xml}"
        "</item>"
    )


def rss_feed(*items: str) -> str:
    return (
        '<?xml version="1.0"?><rss version="2.0"><channel>'
        + "".join(items)
        + "</channel></rss>"
    )


def atom_feed(
    *,
    published: str | None = None,
    updated: str | None = None,
) -> str:
    published_xml = f"<published>{published}</published>" if published else ""
    updated_xml = f"<updated>{updated}</updated>" if updated else ""
    feed_updated = updated or published or "2026-06-24T00:00:00Z"
    return (
        '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">'
        "<title>Test Feed</title><id>urn:test-feed</id>"
        f"<updated>{feed_updated}</updated>"
        "<entry><title>Atom Entry</title><id>urn:test-entry</id>"
        '<link href="https://example.com/atom-entry"/>'
        f"{published_xml}{updated_xml}"
        "</entry></feed>"
    )
```

Use RFC 822 values for `pubDate`, for example
`"Wed, 24 Jun 2026 00:00:00 GMT"`. For updated-only coverage, use a minimal Atom
1.0 `atom_feed(updated="2026-06-24T00:00:00Z")` fixture. For publication
precedence, pass both Atom `published` and `updated` values that disagree. Do
not place `<updated>` in an RSS 2.0 item.

- [ ] **Step 2: Write fresh, newest-selection, and fallback tests**

Add tests that use `FIXED_NOW` and injected clients:

```python
def test_rss_liveness_reports_fresh_newest_entry_evidence(tmp_path: Path) -> None:
    ...
    client = FakeClient(
        text=rss_feed(
            rss_item("Older", published="Mon, 22 Jun 2026 00:00:00 GMT"),
            rss_item("Newest", published="Wed, 24 Jun 2026 00:00:00 GMT"),
        )
    )
    report = build_source_liveness_report(
        path,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.LIVE
    assert result.severity == SourceLivenessSeverity.OK
    assert result.code is None
    assert result.dated_records_seen == 2
    assert result.latest_entry_at == datetime(2026, 6, 24, 0, 0, tzinfo=UTC)
    assert result.latest_entry_age_hours == 2
    assert result.message == "Feed returned 2 entries; newest dated entry is 2 hours old."
```

Add a separate Atom fixture proving `updated_parsed` is used when
`published_parsed` is absent. Add another entry containing both publication and
update timestamps that disagree; assert the publication timestamp wins for that
entry.

- [ ] **Step 3: Write stale and exact-threshold tests**

Add:

```python
def test_rss_liveness_marks_feed_beyond_threshold_degraded(tmp_path: Path) -> None:
    ...
    client = FakeClient(
        text=rss_feed(
            rss_item("Stale", published="Sat, 20 Jun 2026 00:00:00 GMT")
        )
    )
    report = build_source_liveness_report(
        path,
        stale_after_hours=72,
        client_factory=lambda *_: client,
        clock=fixed_clock,
    )

    result = report.results[0]
    assert result.status == SourceLivenessStatus.DEGRADED
    assert result.severity == SourceLivenessSeverity.WARNING
    assert result.code == "stale_feed"
    assert result.latest_entry_age_hours == 98
    assert report.warning_count == 1
    assert source_liveness_should_exit_nonzero(report, strict=False) is False
    assert source_liveness_should_exit_nonzero(report, strict=True) is True
```

Add a focused helper-level test for the exact boundary using `struct_time`
values or parsed entries:

```python
assert exact.stale is False
assert exact.latest_entry_age_hours == 72
assert one_second_over.stale is True
assert one_second_over.latest_entry_age_hours == 73
```

Add an integration test that probes the same entry approximately 49 hours old
twice with separate injected clients. Assert it is `live/ok` with
`stale_after_hours=72` and `degraded/warning/stale_feed` with
`stale_after_hours=48`. This must exercise `build_source_liveness_report`
through `_probe_rss_source`, not call the evidence helper directly.

- [ ] **Step 4: Write unknown, invalid, future, and malformed precedence tests**

Rename the existing `test_rss_liveness_live_feed_counts_entries_from_fixture`
test to `test_rss_liveness_no_date_feed_is_freshness_unknown`, then update it to
require:

```python
assert result.status == SourceLivenessStatus.LIVE
assert result.severity == SourceLivenessSeverity.INFO
assert result.code == "freshness_unknown"
assert result.dated_records_seen == 0
assert result.latest_entry_at is None
assert result.latest_entry_age_hours is None
assert report.info_count == 1
```

Add tests proving:

- an invalid timestamp is ignored while a second valid entry supplies evidence;
- a future timestamp produces age `0` and remains `live/ok`;
- the malformed feed with entries remains
  `degraded/warning/malformed_feed` even when it has a valid old timestamp;
- an empty RSS result has `dated_records_seen == 0`, both latest fields `None`,
  and remains `empty/warning/empty_feed`;
- an RSSHub result follows the same fresh/stale logic;
- GDELT result freshness fields remain `None` and its request params are
  unchanged.

- [ ] **Step 5: Run the RSS matrix and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_source_liveness.py \
  -k 'rss_liveness or rsshub_liveness or source_liveness_report_json_shape or render_source_liveness_table or rejects_invalid_stale' \
  -q
```

Expected before implementation: failures on freshness fields, messages,
classifications, and threshold behavior.

- [ ] **Step 6: Implement timestamp conversion and freshness evidence**

Add:

```python
def _entry_datetime(entry: Mapping[str, Any]) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if not isinstance(value, struct_time):
            continue
        try:
            return datetime.fromtimestamp(calendar.timegm(value), tz=UTC)
        except (OverflowError, OSError, ValueError):
            continue
    return None


def _rss_freshness_evidence(
    entries: Sequence[Mapping[str, Any]],
    *,
    checked_at: datetime,
    stale_after_hours: int,
) -> _RssFreshnessEvidence:
    timestamps = [
        timestamp
        for entry in entries
        if (timestamp := _entry_datetime(entry)) is not None
    ]
    if not timestamps:
        return _RssFreshnessEvidence(0, None, None, False)

    latest_entry_at = max(timestamps)
    age_seconds = max(0.0, (checked_at - latest_entry_at).total_seconds())
    age_hours = ceil(age_seconds / 3600) if age_seconds else 0
    return _RssFreshnessEvidence(
        dated_records_seen=len(timestamps),
        latest_entry_at=latest_entry_at,
        latest_entry_age_hours=age_hours,
        stale=age_seconds > stale_after_hours * 3600,
    )
```

Use `calendar.timegm` rather than direct tuple construction so the liveness path
matches the existing RSS collector's UTC conversion.

Unlike the collector's simple `published_parsed or updated_parsed` expression,
this helper deliberately validates and converts each key independently. An
invalid publication timestamp may therefore fall through to a valid update
timestamp, and conversion errors remain local to one entry.

- [ ] **Step 7: Implement the RSS status precedence**

Add `stale_after_hours: int` to `_probe_rss_source`. Immediately after
`records_seen` and `bozo`, compute:

```python
freshness = _rss_freshness_evidence(
    entries,
    checked_at=checked_at,
    stale_after_hours=stale_after_hours,
)
freshness_kwargs = {
    "dated_records_seen": freshness.dated_records_seen,
    "latest_entry_at": freshness.latest_entry_at,
    "latest_entry_age_hours": freshness.latest_entry_age_hours,
}
```

Preserve bozo-with-entries first and pass `**freshness_kwargs`. Then implement
the non-bozo, nonempty branches in this exact order:

```python
if records_seen > 0 and freshness.latest_entry_at is None:
    return _result(
        source,
        checked_at=checked_at,
        elapsed_ms=elapsed_ms,
        status=SourceLivenessStatus.LIVE,
        severity=SourceLivenessSeverity.INFO,
        code="freshness_unknown",
        message=(
            f"Feed returned {_record_label(records_seen, 'entry', 'entries')}; "
            "no parseable entry timestamps were available."
        ),
        records_seen=records_seen,
        **freshness_kwargs,
    )
if records_seen > 0 and freshness.stale:
    return _result(
        source,
        checked_at=checked_at,
        elapsed_ms=elapsed_ms,
        status=SourceLivenessStatus.DEGRADED,
        severity=SourceLivenessSeverity.WARNING,
        code="stale_feed",
        message=(
            f"Feed returned {_record_label(records_seen, 'entry', 'entries')}; "
            f"newest dated entry is {freshness.latest_entry_age_hours} hours old, "
            f"beyond the {stale_after_hours}-hour freshness threshold."
        ),
        records_seen=records_seen,
        **freshness_kwargs,
    )
if records_seen > 0:
    return _result(
        source,
        checked_at=checked_at,
        elapsed_ms=elapsed_ms,
        status=SourceLivenessStatus.LIVE,
        severity=SourceLivenessSeverity.OK,
        code=None,
        message=(
            f"Feed returned {_record_label(records_seen, 'entry', 'entries')}; "
            f"newest dated entry is {freshness.latest_entry_age_hours} hours old."
        ),
        records_seen=records_seen,
        **freshness_kwargs,
    )
```

For the successfully parsed non-bozo empty-feed result, pass
`dated_records_seen=0`. A bozo feed with no entries remains
`failed/error/malformed_feed` and leaves all three freshness fields `None`.
Do not alter GDELT branches.

- [ ] **Step 8: Run all source-liveness tests and verify GREEN**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_source_liveness.py -q
```

Expected: every source-liveness test passes with no real network access.

## Task 3: Wire The CLI Threshold

**Owner:** Worker B

**Start condition:** Task 1 Step 4 is integrated.

**Files:**

- Modify: `tests/test_cli.py`
- Modify: `src/fashion_radar/cli.py`

- [ ] **Step 1: Write help, forwarding, and validation tests**

Extend `test_source_liveness_help_lists_format_strict_and_network_read_only`:

```python
assert "--stale-after-hours" in result.output
assert "72" in result.output
```

Add:

```python
def test_source_liveness_forwards_custom_stale_threshold(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    seen: dict[str, object] = {}
    report = SourceLivenessReport(path=str(path), checked_at=datetime(2026, 6, 24, 2, 0, tzinfo=UTC))

    def fake_builder(value: Path, *, stale_after_hours: int):
        seen["path"] = value
        seen["stale_after_hours"] = stale_after_hours
        return report

    monkeypatch.setattr(cli_module, "build_source_liveness_report", fake_builder)

    result = CliRunner().invoke(
        app,
        ["source-liveness", str(path), "--stale-after-hours", "48"],
    )

    assert result.exit_code == 0
    assert seen == {"path": path, "stale_after_hours": 48}
```

Add an invalid-value test whose builder raises if called:

```python
def test_source_liveness_rejects_stale_threshold_below_one_before_builder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text("version: 1\nsources: []\n", encoding="utf-8")
    monkeypatch.setattr(
        cli_module,
        "build_source_liveness_report",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("builder called")),
    )

    result = CliRunner().invoke(
        app,
        ["source-liveness", str(path), "--stale-after-hours", "0"],
    )

    assert result.exit_code == 2
    assert "x>=1" in result.output
```

The assertion follows Typer's native `min=1` range error. Do not add a custom
validation callback only to change this wording.

- [ ] **Step 2: Update existing builder fakes for the new keyword**

Every `monkeypatch.setattr(cli_module, "build_source_liveness_report", ...)`
in the source-liveness CLI tests must accept `stale_after_hours`. Use a helper
when practical:

```python
def source_liveness_builder(report):
    def build(path: Path, *, stale_after_hours: int):
        assert stale_after_hours == 72
        return report

    return build
```

Do not weaken invalid-format coverage: an invalid `--format` must still reject
input before the builder runs.

- [ ] **Step 3: Run the focused CLI tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_cli.py \
  -k 'source_liveness' -q
```

Expected: failures because the option is absent and the command does not pass
the keyword.

- [ ] **Step 4: Add the CLI option and builder call**

Import `DEFAULT_SOURCE_LIVENESS_STALE_AFTER_HOURS` from
`fashion_radar.source_liveness`.

Beside `SOURCE_LIVENESS_FORMAT_OPTION`, define:

```python
SOURCE_LIVENESS_STALE_AFTER_HOURS_OPTION = typer.Option(
    DEFAULT_SOURCE_LIVENESS_STALE_AFTER_HOURS,
    "--stale-after-hours",
    min=1,
    help="Mark RSS/RSSHub feeds degraded when the newest dated entry is older than this threshold.",
)
```

Extend the command signature:

```python
stale_after_hours: int = SOURCE_LIVENESS_STALE_AFTER_HOURS_OPTION,
```

Build the report with:

```python
report = build_source_liveness_report(
    path,
    stale_after_hours=stale_after_hours,
)
```

Do not change rendering or exit logic in the CLI.

- [ ] **Step 5: Run the focused CLI tests and verify GREEN**

Run the Step 3 command. Expected: every selected CLI test passes.

## Task 4: Align Public Documentation

**Owner:** Worker C

**Files:**

- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_source_packs_docs.py`
- Modify: `tests/test_source_pack_quality_docs.py`
- Modify: `README.md`
- Modify: `docs/source-packs.md`
- Modify: `docs/source-pack-quality.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write failing public documentation contracts**

Extend `test_cli_reference_documents_source_liveness` to require:

```python
assert "--stale-after-hours" in entry
assert "rss/rsshub" in entry.casefold()
assert "newest dated entry" in entry.casefold()
```

Extend `test_readme_documents_source_liveness_public_pack_example`:

```python
assert "--stale-after-hours 72" in text
assert "reachable but stale" in text.casefold()
```

Extend `test_architecture_documents_source_liveness_boundary`:

```python
assert "entry timestamps" in text.casefold()
assert "does not filter collected items" in text.casefold()
```

Extend
`tests/test_source_packs_docs.py::test_source_packs_docs_show_source_liveness_command_examples`
to require `--stale-after-hours 72`, `stale_feed`, `freshness_unknown`, and the
`--strict` warning interpretation. Extend
`tests/test_source_pack_quality_docs.py::test_source_pack_quality_docs_route_live_checks_to_source_liveness`
to require that reachable does not imply fresh and that liveness freshness
evidence does not rank sources or prove demand or platform coverage.

- [ ] **Step 2: Run documentation tests and verify RED**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_cli_docs.py \
  tests/test_source_packs_docs.py \
  tests/test_source_pack_quality_docs.py \
  tests/test_review_protocol_docs.py \
  -q
```

Expected: the new freshness wording is absent.

- [ ] **Step 3: Update the source-liveness public guides**

Document this exact behavior consistently:

- Default threshold: 72 hours.
- `--stale-after-hours N` applies to RSS/RSSHub only.
- A non-malformed feed older than the threshold is
  `degraded/warning/stale_feed`.
- A nonempty feed with no parseable entry dates is
  `live/info/freshness_unknown`.
- Default mode does not fail for warnings; `--strict` does.
- GDELT remains query-time bounded by configured lookback.
- The command performs no additional fetch, collection, storage, scoring,
  matching, report generation, source ranking, or filtering.

Add this example to README and `docs/source-packs.md`:

```bash
uv run fashion-radar source-liveness \
  configs/source-packs/fashion-public.example.yaml \
  --stale-after-hours 72
```

- [ ] **Step 4: Add the Unreleased changelog entry**

Under `## [Unreleased]` add a Stage 390 entry that states RSS/RSSHub liveness
now exposes dated-entry count, latest entry time, age, stale warnings, and
unknown-date info using the existing feed response. Explicitly state that the
stage does not add or replace sources, filter collection, change GDELT,
matching, scoring, ROW ONE output, connectors, or dependencies.

- [ ] **Step 5: Run documentation tests and verify GREEN**

Run the Step 2 command. Expected: all documentation contracts pass.

## Task 5: Integrate, Review, Validate, And Publish

**Owner:** Coordinator

**Files:**

- Create: `docs/reviews/claude-code-stage-390-code-review.md`
- Create if required: `docs/reviews/claude-code-stage-390-code-rereview.md`
- Create: `docs/reviews/claude-code-stage-390-release-review.md` or matching
  OpenCode fallback

- [ ] **Step 1: Reconcile worker handoffs**

For each worker, collect:

- changed-file list;
- exact verification commands and outcomes;
- unresolved concerns;
- confirmation that no file outside its ownership was changed.

Run:

```bash
git status --short
git diff --check
git diff --name-only
git diff --quiet -- uv.lock
```

Expected: only Stage 390 implementation, test, docs, and review paths are
present; `uv.lock` has no diff.

- [ ] **Step 2: Run focused integrated tests**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_source_liveness.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_cli.py -k 'source_liveness' -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_cli_docs.py \
  tests/test_source_packs_docs.py \
  tests/test_source_pack_quality_docs.py \
  tests/test_review_protocol_docs.py \
  -q
```

The commands are intentionally separate because pytest applies `-k` globally
across every path in one invocation. Expected: all selected tests pass.

- [ ] **Step 3: Run the full integrated checks**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
```

Expected: all tests and Ruff checks pass.

- [ ] **Step 4: Obtain Claude Code code review**

Use max effort and read-only plan mode. Give the reviewer the Stage 390 design,
current plan, complete diff, changed files, focused/full verification results,
and these invariants:

- no new status enum;
- no GDELT change;
- no collection filtering;
- no additional network request;
- no dependency or lockfile change;
- malformed-feed precedence is preserved.

Record one coherent review body. Resolve every critical and important finding,
rerun affected checks, and obtain a rereview for any review-driven diff.

- [ ] **Step 5: Stage and commit the reviewed implementation**

Stage only intended Stage 390 files. Before commit run:

```bash
git diff --cached --check
git diff --cached --quiet -- uv.lock || {
  echo "Stage 390 must not modify uv.lock" >&2
  exit 1
}
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
  -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS \
  -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL \
  UV_NO_CONFIG=1 uv --no-config run --frozen \
  python scripts/check_release_hygiene.py --repo-root .
```

Commit with:

```text
Stage 390: add RSS freshness diagnostics
```

Capture the immutable implementation SHA in the protected release terminal:

```bash
implementation_head="$(git rev-parse HEAD)"
```

- [ ] **Step 6: Run release validation from the committed snapshot**

Define:

```bash
public_uv() {
  env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
    -u UV_PROJECT_ENVIRONMENT -u UV_INDEX -u UV_FIND_LINKS \
    -u PIP_INDEX_URL -u PIP_EXTRA_INDEX_URL \
    UV_NO_CONFIG=1 uv "$@"
}
```

Run the entire sequence in one `set -e` subshell:

```bash
(
  set -e
  public_uv lock --check
  if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then
    echo "refusing a mirror-bound public lockfile" >&2
    exit 1
  else
    mirror_scan_status=$?
  fi
  case "$mirror_scan_status" in
    1) ;;
    *) exit "$mirror_scan_status" ;;
  esac
  unset mirror_scan_status
  public_uv sync --locked --dev
  public_uv sync --locked --dev --check
  public_uv --no-config run --frozen pytest -q
  public_uv --no-config run --frozen ruff check .
  public_uv --no-config run --frozen ruff format --check .
  public_uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
  public_uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
  git diff --check

  tmp_build="$(mktemp -d)"
  public_uv --no-config build --out-dir "$tmp_build"
  public_uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
  wheel="$(find "$tmp_build" -maxdepth 1 -name '*.whl' -print -quit)"
  test -n "$wheel"
  tmp_env="$(mktemp -d)"
  public_uv venv "$tmp_env/venv"
  public_uv pip install --python "$tmp_env/venv/bin/python" "$wheel"
  tmp_run="$(mktemp -d)"
  env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" --help
  env -u PYTHONPATH "$tmp_env/venv/bin/python" -m fashion_radar --help
  env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" init \
    --config-dir "$tmp_run/config" \
    --data-dir "$tmp_run/data" \
    --reports-dir "$tmp_run/reports"
  env -u PYTHONPATH "$tmp_env/venv/bin/fashion-radar" doctor \
    --config-dir "$tmp_run/config" \
    --data-dir "$tmp_run/data" \
    --reports-dir "$tmp_run/reports"
  env -u PYTHONPATH "$tmp_env/venv/bin/python" \
    scripts/check_first_run_smoke.py \
    --repo-root . \
    --python "$tmp_env/venv/bin/python" \
    --installed
  env -u PYTHONPATH "$tmp_env/venv/bin/python" -c \
    "from importlib import resources; text = resources.files('fashion_radar.templates').joinpath('daily_report.md').read_text(encoding='utf-8'); assert 'Fashion Radar Daily Report' in text"
  tmp_dash="$(mktemp -d)"
  public_uv venv "$tmp_dash/venv"
  public_uv pip install --python "$tmp_dash/venv/bin/python" "$wheel[dashboard]"
  env -u PYTHONPATH "$tmp_dash/venv/bin/python" -c \
    "import fashion_radar.dashboard.app; import fashion_radar.dashboard.queries"
)
```

- [ ] **Step 7: Obtain and record the release review**

Pin the review to the committed implementation SHA. Claude Code is primary;
OpenCode GLM 5.2 max is fallback only when Claude Code does not return a complete
review. The reviewer must inspect committed Git objects rather than a mutable
worktree. Resolve every critical and important finding and repeat verification
and review until clean.

- [ ] **Step 8: Commit the release record and revalidate final HEAD**

Commit the clean release-review record as:

```text
Stage 390: record release review
```

Before repeating Step 6, require `implementation_head` to be an ancestor of
final HEAD and permit only Stage 390 review records plus the named Stage 390
design/plan in the post-review commit:

```bash
verify_release_record_delta() {
  test -n "${implementation_head:-}" || exit 1
  git cat-file -e "$implementation_head^{commit}" || exit 1
  git merge-base --is-ancestor "$implementation_head" HEAD || exit 1
  release_record_paths="$(git diff --name-only "$implementation_head" HEAD)" || exit 1
  test -n "$release_record_paths" || exit 1
  while IFS= read -r release_record_path; do
    case "$release_record_path" in
      docs/reviews/claude-code-stage-390-*|docs/reviews/opencode-stage-390-*|docs/superpowers/plans/2026-07-14-stage-390-source-liveness-rss-freshness-plan.md|docs/superpowers/specs/2026-07-14-stage-390-source-liveness-rss-freshness-design.md) ;;
      *) echo "refusing to publish an unreviewed non-record path" >&2; exit 1 ;;
    esac
  done <<EOF
$release_record_paths
EOF
  unset release_record_path release_record_paths
}
verify_release_record_delta
```

Require a clean worktree before and after repeating the complete Step 6 release
validation from the exact final HEAD, then run
`verify_release_record_delta` again.

- [ ] **Step 9: Publish one immutable SHA**

Verify the configured origin against the user-authorized repository without
printing the URL or credentials. Capture final `release_head`, prove the remote
`main` tip is an ancestor, push exactly:

```bash
git push origin "$release_head:refs/heads/main"
```

Do not force push. Re-read remote `main` and require exact equality with
`release_head`. Do not publish packages or other uploads.

## Handoff Summary Contract

At the end of each node, report:

- repository branch and HEAD state;
- completed review gates;
- exact verification commands and concise outcomes;
- uncommitted files;
- next task and worker ownership.

Do not paste raw model logs, full diffs, credentials, or remote URLs.
