## Stage 209 Plan Review

I read the plan and verified its claims against the actual code (`reports.py`, `models/report.py`, existing tests, scoring defaults, and the docs guard).

**Verdict: No Critical findings. One Important finding. Two Minor findings.**

---

### Critical
None.

---

### Important

**I-1. The Markdown RED test (Task 1, Step 2) is not genuinely RED and does not isolate the Daily Brief.**

The assertion `assert "Score components: mentions 2.00; growth 0.00; sources 1.00" in markdown` is satisfied by the **full report** candidate section, not the brief. That exact string is already emitted by `_render_candidate_sections` at `src/fashion_radar/reports.py:712-717`. Because `build_daily_report` defaults `candidate_discovery` to `CandidateDiscoverySettings()` (`reports.py:58`), the two candidate items the plan adds to `test_markdown_report_renders_daily_brief_before_top_signals` produce a full "Untracked Candidate Signals" section, so this assertion passes **before** any GREEN change. The companion assertion (`"high-weight" not in …`) only checks *absence* and also passes before/after. Net effect: the Markdown test passes without the implementation, contradicting the Task 1 Step 4 expectation ("the tests fail"), and it never positively verifies the cue appears in the brief markdown.

The component *values* are correct — they're already pinned for this exact fixture at `tests/test_reports.py:898-907`. The fix is to assert the cue *inside* the region the plan already isolates:

```python
brief_candidates = markdown.split("### Candidate Signals Needing Review", 1)[1].split("### Source Caveats", 1)[0]
assert "Score components: mentions 2.00; growth 0.00; sources 1.00" in brief_candidates
```

The JSON test and the direct `build_daily_brief` test are correctly RED and well-targeted (and the `hasattr(..., "weighted_mention_component")` guard is a good summary-only pin given `DailyBriefItem` is `extra="forbid"`).

---

### Minor

**M-1. Task 3, Step 4 (optional docs-guard phrase) is a hidden cross-doc trap.** `DAILY_BRIEF_REQUIRED_PHRASES` is asserted against *every* doc in `DAILY_BRIEF_DOCS` (`tests/test_cli_docs.py:816-819`), which spans README, cli-reference, architecture, `docs/daily-digest.md`, upload-checklist, and CHANGELOG. The plan only edits 4 of those 6. Adding `"candidate score-component cues"` to the shared tuple would break `test_daily_brief_docs_are_bounded_and_discoverable` for `daily-digest.md` and upload-checklist. Recommend not adding it to the shared tuple, editing all 6 docs, or using a narrower dedicated guard.

**M-2. Task 2, Step 2 reconstructs the entire existing summary string verbatim.** Acceptable for a one-time edit, but it couples this stage to the base wording; if the base summary is later edited elsewhere, the append must stay in sync. Consider composing base + cue rather than re-inlining the whole sentence. (Optional.)

---

### Question-by-question

1. **Report-only scope useful/correct?** Yes — closes a real first-surface explainability gap; tightly limited to `reports.py` rendering. ✓
2. **Avoiding new `DailyBriefItem` fields safest?** Yes — `daily-brief/v1` contract preserved, `extra="forbid"` + `hasattr` test enforce it, no dashboard/CLI JSON consumers break. ✓
3. **RED tests sufficient?** JSON and direct: yes. Markdown: no — see I-1.
4. **Preserves scoring/ranking/extraction/schemas/source-acquisition/dashboard/deps/lockfiles?** Yes — only reads existing `CandidateReport` fields; no formula, schema, dashboard, dependency, or lockfile change. ✓
5. **Docs/changelog local & free of demand/coverage claims?** Yes — changelog is appropriately hedged; the existing `DAILY_BRIEF_FORBIDDEN_POSITIVE_CLAIMS` guard enforces no viral/demand/coverage language. (See M-1 for the optional-phrase trap.)
6. **Release verification & review gates sufficient?** Yes — full pytest, ruff check/format, release-hygiene script, `UV_NO_CONFIG=1 uv lock --check`, `uv sync --locked --dev --check`, first-run smoke, `git diff --exit-code -- uv.lock pyproject.toml`, whitespace + secret scan, plus plan/code/release OpenCode reviews per `REVIEW_PROTOCOL.md`. ✓

Recommend addressing I-1 (and deciding M-1) before Task 1.
