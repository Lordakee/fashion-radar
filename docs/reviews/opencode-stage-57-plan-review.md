I'll review the Stage 57 planning documents. Let me start by reading the spec, plan, and relevant codebase context.
Now let me verify the codebase claims in the plan — models, existing trends flow, dashboard patterns, and test helpers.
Now the CLI trends command and option patterns, plus the dashboard trend helpers.
Let me verify the CLI option/type pattern, docs test helpers, test fixtures, and check whether existing docs already contain forbidden terms.
Let me check feasibility of the proposed docs tests against existing doc content, and verify the CLI test fixtures exist.
I found a potential critical issue with the forbidden-claims test. Let me verify precisely which forbidden phrases already exist in the docs that the test would check.
I now have everything needed. Let me confirm there's no pre-existing heat-movers module and verify the dashboard's existing anti-claim wording that the plan's test would collide with.
Confirmed all findings. Here is my Stage 57 plan review.

---

# Stage 57 Plan Review — Local Heat Movers

Reviewer: `zhipuai-coding-plan/glm-5.2` (local planning reviewer)
Scope: read-only review of the Stage 57 design + plan against the repo at `/home/ubuntu/fashion-radar`.

## Critical Findings

### C1. The proposed docs forbidden-claims test will fail against existing boundary docs and pressures the implementer to weaken guardrails

In `docs/superpowers/plans/2026-06-17-stage-57-local-heat-movers-plan.md` Task 4 Step 1, the `test_heat_movers_docs_are_linked_and_bounded` body asserts a naive global substring absence:

```python
forbidden_claims = ("hottest","viral","market-wide trend","platform-wide popularity",
                    "verified demand","top social trend")
for text in (readme, trend_doc, dashboard_doc, cli_reference, architecture, changelog):
    normalized = _normalized_text(text).casefold()
    for claim in forbidden_claims:
        assert claim.casefold() not in normalized
```

Verified collisions already present in the repo as legitimate *anti-claim* disclaimers:

- `docs/dashboard.md:93` — "...should not be read as **platform-wide popularity** or market-wide demand." (Trend Deltas boundary text)
- `docs/trend-deltas.md:7` — "They are not **verified demand**, market-wide proof, real-time monitoring, or complete social-platform coverage."

`_normalized_text` is `" ".join(text.split())`, so the substrings survive any whitespace/newline folding and any preceding "not". The test therefore can never go green while preserving the repo's existing negation-style boundary wording. Following the plan's mandated TDD order (write test → red → green), the implementer's only paths to green are:

1. rewrite/delete the existing `dashboard.md` and `trend-deltas.md` disclaimer lines to avoid the literal phrases, which **regresses** the project's strongest existing anti-claim guardrails; or
2. recognize the test itself is wrong.

A plan that, when followed faithfully, forces weakening of existing boundary documentation directly undermines the Stage 57 guardrail objective (review question 6). This must be fixed in the plan before implementation.

Recommended fix (pick one and bake into the plan):

- Drop the global `forbidden_claims` whole-doc scan entirely. The repo already centralizes anti-claim enumeration in `docs/source-boundaries.md` (lines 238–244 quote exactly these phrases as examples of what *not* to say), and `source-boundaries.md` is deliberately excluded from the forbidden loop — that is the right place for it.
- Or scope the forbidden check to a narrowly extracted heat-movers section only (e.g. a `## Heat Movers` slice), not whole documents.
- Or make it negation-aware (forbid the phrase only when not preceded by "not"/"no"/"without"/"neither"/"avoid"), which is fragile and not recommended.

The required-terms half of the same test is feasible but heavy: "local observed heat movement", "configured source set", "configured sources and imported local signals", "needs review", "no demand proof", "no platform coverage verification" must all appear verbatim (case-insensitively) across **six** files including `AGENTS.md`. Note "configured sources and imported local signals" already exists in README/trend-deltas/dashboard but is absent from `architecture.md`, `source-boundaries.md`, and `AGENTS.md` — the plan should call this out as required new wording so it is not missed.

## Important Findings

### I1. Dashboard `main()` tab unpacking is brittle and the plan lists no test that catches a misroute

`src/fashion_radar/dashboard/app.py:152-155` unpacks positionally:

```python
tabs = st.tabs(list(DASHBOARD_TAB_LABELS))
daily_tab, candidate_tab, trend_tab = tabs[:3]
entity_tabs = tabs[3:-1]
health_tab = tabs[-1]
```

`DASHBOARD_TAB_LABELS` currently is `(Daily Brief, Candidate Signals, Trend Deltas, *entity tabs…, Source Health)`. The plan inserts "Heat Movers" **before** "Trend Deltas" and says "Update `main()` tab unpacking" — but the only listed dashboard test touching ordering is `test_dashboard_tab_labels_include_heat_movers_before_trend_deltas`, which asserts **label order**, not that `main()` routes the correct render function to the correct tab object. If the implementer adds the label but forgets to bump `tabs[:3]` → `tabs[:4]` and `tabs[3:-1]` → `tabs[4:-1]`, the heat-movers tab will render trend deltas (or vice-versa) and entity tabs will silently receive the wrong data. Dashboard render functions are unit-tested in isolation, so a main()-routing bug would not be caught.

Recommended: add an explicit test asserting the index invariant, e.g. `DASHBOARD_TAB_LABELS.index("Heat Movers") < DASHBOARD_TAB_LABELS.index("Trend Deltas")` **and** that the count arithmetic in `main()` is consistent with `ENTITY_MENTION_TABS` (e.g. `len(DASHBOARD_TAB_LABELS) == len(ENTITY_MENTION_TABS) + 4`), or refactor `main()` to look up tabs by label rather than by fragile slice indices.

## Minor Findings

### M1. `REQUIRED_FLAGS_BY_COMMAND` not extended for `heat-movers`
`tests/test_cli_docs.py:49` maps `trends` → `("--config-dir","--data-dir","--as-of")` to enforce path-flag consistency in documented commands via `test_repo_local_operational_examples_keep_path_flags_together`. The plan documents `heat-movers` commands with those same flags but does not add `"heat-movers": ("--config-dir","--data-dir","--as-of")`. Omission won't fail tests (the check is skipped for unmapped commands) but misses the parity guardrail that exists for its sibling `trends` command.

### M2. Negative-limit CLI test vs Typer `min=0`
The CLI signature `limit: int | None = typer.Option(5, min=0, ...)` rejects negatives at parse time (Typer usage error, exit code 2) before the command body runs, so `build_heat_movers`'s `ValueError("limit_per_group must be at least 0")` is only reachable via direct module use. The listed test `test_heat_movers_command_rejects_negative_limit` should expect Typer's usage rejection, not the command's own message; the plan should state which layer owns negative rejection to avoid a confused test.

### M3. CHANGELOG coverage gap in the docs test
The proposed docs test requires `"heat-movers" in text` for `(readme, trend_doc, dashboard_doc, cli_reference, architecture, checklist)` but **not** `changelog`. The plan modifies `CHANGELOG.md`, yet no test enforces a changelog entry — a hygiene gap given the project's strict docs-drift testing style.

### M4. `execution_mode` as single-value `Literal`
`execution_mode: Literal["local_read_only"] = "local_read_only"` is a one-element Literal. It works as a frozen tag and communicates "read-only", but is functionally equivalent to `str = "local_read_only"`. Non-blocking; calling it out only for awareness.

## Answers to the Review Questions

**1. Is `heat-movers` the right next node after Stage 56?** Yes. It is a pure presentation/grouping layer over already-computed `TrendComparison` deltas, adds no data source, and directly answers the user's daily "what moved up?" question for tracked entities and candidate phrases. Strongly aligned with the free-first/local-first boundary.

**2. Separate `heat-movers` command vs a `trends` mode flag?** Separate is correct here. `trends` has a *global* `--limit` and `--include-dropped` semantics that conflict with per-group limiting; overloading it would either change `trends` output (breaking existing scripts/tests) or tangle two distinct display models. The dashboard needs its own tab regardless. Keeping `trends` untouched (verified: plan does not modify `trends.py`, `models/trend.py`, or `trends_command`) is the right call.

**3. Does the module boundary stay pure?** Yes. `heat_movers.py` needs only `models.trend` types and stdlib (`Literal`, `datetime`). No DB, no IO, no writes, no scoring, no candidate discovery. Grouping + rendering only. The plan's import list is clean (no streamlit/typer/sqlalchemy in the module). Confirmed against `models/trend.py` (all referenced types/enums exist: `TrendComparison`, `TrendDelta`, `TrendSignalKind.ENTITY/CANDIDATE`, `TrendStatus.NEW/RISING/COOLING/STABLE/DROPPED`).

**4. CLI read-only / missing-DB / invalid-input / per-group limits?** Sound. It mirrors `trends_command` (`cli.py:1192-1262`) almost exactly: parse `--as-of` first, load `scoring.yaml`, default `baseline = as_of - current_window_days`, reject `baseline >= as_of`, catch `ConfigError`, missing DB → empty report without creating files, read-only engine + `engine.dispose()`. Per-group limiting is preserved by calling `build_trend_comparison(..., include_dropped=False, limit=None)` then `build_heat_movers(...)`. Only the negative-limit test semantics need clarification (M2).

**5. Dashboard reuse of read-only query behavior?** Yes. `render_heat_movers` reuses `load_trend_comparison(...)` (`dashboard/queries.py:188`, which is read-only, returns an empty `TrendComparison` when the DB is missing, and disposes the engine) and then `build_heat_movers`. No new query path, no new artifacts. Caveat is the `main()` tab-routing brittleness (I1), not data access.

**6. Are docs guardrails strong enough?** Conceptually yes, but the **enforcement test is broken** (C1). The intended boundary vocabulary ("local observed heat movement", "configured source set", "needs review", "no demand proof", "no platform coverage verification") is appropriate and matches existing repo style. But the global forbidden-claims substring scan collides with existing legitimate negation disclaimers and must be redesigned before implementation.

**7. Are tests sufficient?** Breadth is good (pure grouping incl. `limit=0`/`None`, stable JSON key order, table sanitization, CLI help/JSON/table/missing-DB/invalid-date/invalid-config/baseline/read-only, dashboard rows/empty/warnings, docs drift, full release + ruff + lock + mirror + hygiene + first-run + installed-wheel). Gaps: (a) C1 docs test flaw; (b) no main() tab-routing test (I1); (c) `REQUIRED_FLAGS_BY_COMMAND` parity (M1); (d) negative-limit ownership (M2); (e) CHANGELOG enforcement (M3).

**8. Compatibility checks?** Adequate with one gap. `trends`, reports, candidates, and scoring are untouched (no schema/model changes — verified). Two existing tests in `tests/test_cli_docs.py` automatically enforce compatibility: `test_cli_reference_lists_every_public_command` (forces `heat-movers` into `docs/cli-reference.md`) and `test_upload_checklist_help_loop_matches_public_commands` (forces `heat-movers` into the upload-checklist help loop) — the plan acknowledges both. `check_first_run_smoke.py` is not extended; acceptable since heat-movers is a pure view over already-smoked trend data, but an optional assertion there would be cheap. The dashboard tab-routing compatibility is the one untested risk (I1).

**9. Avoids dependency/lockfile/schema/artifact churn?** Yes. No new imports (pydantic v2, typer, sqlalchemy, streamlit all already present). `pyproject.toml`/`uv.lock` explicitly untouched and guarded by `git diff --exit-code -- uv.lock pyproject.toml`, `uv lock --check`, and the mirror-string scan. No DB schema or migration files touched. No generated artifacts, configs, or entity packs. Read-only across the board.

## Final Verdict

The architecture and boundary design are correct, minimal, and faithful to the free-first/local-first scope. However, the plan as written contains one **Critical** defect (C1: the forbidden-claims docs test cannot pass without regressing existing boundary documentation) and one **Important** defect (I1: untested dashboard tab-routing after the index shift). Both are plan-level and must be fixed before implementation begins, per the project's "Fix critical and important review findings before continuing" rule in `AGENTS.md`.

Because Critical and Important findings exist, the approval line is **not** granted. Fix C1 and I1 (and ideally M1–M3), then this reviewer will re-run and approve.
