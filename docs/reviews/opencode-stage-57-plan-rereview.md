I'll start by reading the relevant documents to understand the previous review and the current plan state.
I have the previous review and the revised plan. Let me verify the key claims about the existing repo state to confirm the fixes work as intended.
Let me verify the `ENTITY_MENTION_TABS` invariant claim in the plan, since the test asserts a specific count formula.
I have verified the relevant codebase state. Let me confirm the tab-count invariant math against the actual `ENTITY_MENTION_TABS` / `DASHBOARD_TAB_LABELS` definitions before finalizing.

The current layout (`dashboard/app.py:41-47`):
- `DASHBOARD_TAB_LABELS = ("Daily Brief", "Candidate Signals", "Trend Deltas", *entity_labels, "Source Health")`
- Non-entity tabs = 4 (Daily, Candidate, Trend Deltas, Source Health) → `len == len(ENTITY_MENTION_TABS) + 4` ✓ (current)

After Stage 57 inserts "Heat Movers" before "Trend Deltas":
- Non-entity tabs = 5 (Daily, Candidate, Heat Movers, Trend Deltas, Source Health) → invariant becomes `len == len(ENTITY_MENTION_TABS) + 5`

The plan's mandated assertion `len(DASHBOARD_TAB_LABELS) == len(ENTITY_MENTION_TABS) + 4` is therefore off by one for the post-Stage-57 layout.

Here is my Stage 57 plan rereview.

---

# Stage 57 Plan Rereview — Local Heat Movers

Reviewer: `zhipuai-coding-plan/glm-5.2` (local planning reviewer)
Scope: read-only rereview of the revised spec + plan at `/home/ubuntu/fashion-radar` after fixes to C1/I1/M1–M3.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

### R1. Off-by-one in the post-Stage-57 tab-count invariant
Task 3 Step 2 mandates the routing test assert:

```python
len(DASHBOARD_TAB_LABELS) == len(ENTITY_MENTION_TABS) + 4
```

Verified against `src/fashion_radar/dashboard/app.py:38-47`: today the non-entity tabs are Daily Brief, Candidate Signals, Trend Deltas, Source Health = 4, so the current identity is `... + 4`. Stage 57 *adds* "Heat Movers" before "Trend Deltas", raising the non-entity count to 5. The post-Stage-57 invariant must be `len(DASHBOARD_TAB_LABELS) == len(ENTITY_MENTION_TABS) + 5`. As written, a faithful TDD implementer produces a correct dashboard, runs the routing test, and it fails on this single assertion — a confused-test outcome of exactly the kind the prior review's M2 objected to. Suggest the plan correct the constant to `+ 5`. Does not undermine I1's core fix (the three label/routing assertions still catch any misroute).

### R2. `_section_after_marker` uses the first occurrence of the marker
Task 4 Step 1's helper does `text.casefold().index(marker.casefold())`. If "heat-movers" appears in a TOC/anchor/inline link before the real section (very likely in `README.md` and `docs/cli-reference.md`), the slice begins at that early occurrence and ends at the next `## ` heading, which can yield a slice that is mostly TOC/link text rather than the actual section body. This makes the forbidden-claims scan *under-inclusive* in some files (the opposite problem from the original C1, which was *over-inclusive*). It does not weaken existing guardrails, so it is non-blocking. Suggest either anchoring on a heading line (`## Heat Movers` / `### heat-movers`) or documenting that TOC placement must keep the marker's first occurrence inside the intended section.

### R3. required_terms coverage in `architecture.md` / `source-boundaries.md` / `AGENTS.md` is enforced by the test but not called out in the docs step
Task 4 Step 1 requires the six phrases (including "configured sources and imported local signals", "no demand proof", "no platform coverage verification") to appear in `(readme, trend_doc, dashboard_doc, architecture, boundaries, agents)`. The prior review noted the phrase "configured sources and imported local signals" is currently absent from `architecture.md`, `source-boundaries.md`, and `AGENTS.md`. Task 4 Step 2 ("Docs must say …") does not enumerate those three files as needing new wording. The test will catch the omission, but a one-line hint in Step 2 listing which files need the new boundary vocabulary would prevent a surprise red.

### R4. Negative-limit test ownership is specified in Task 4, but the test is declared in Task 2
`test_heat_movers_command_rejects_negative_limit` is listed in Task 2 Step 1, while the assertion shape (`assert "Invalid value" in result.output`, Typer parse-time rejection) is described in Task 4 Step 2. The information is present and correct (resolves the prior M2), but the cross-task placement could be unified for clarity. Non-blocking.

## Are C1 and I1 Fixed?

**C1 — Fixed.** Task 4 Step 1 no longer runs the forbidden-claims scan over whole documents. The revised `test_heat_movers_docs_are_linked_and_bounded` extracts per-file `heat_mover_sections` via `_section_after_marker(...)` and applies `forbidden_claims` only to those slices. Verified that the legitimate negation disclaimers that triggered C1 live outside any heat-movers section:
- `docs/dashboard.md:93` — "...should not be read as platform-wide popularity or market-wide demand." (Trend Deltas section)
- `docs/trend-deltas.md:7` — "They are not verified demand, market-wide proof …" (Trend Deltas intro)

Neither falls inside a `heat-movers` / `Heat Movers` marker slice, so the test no longer pressures the implementer to weaken existing boundary copy. The plan also states this intent explicitly ("Existing repo docs may keep negated boundary wording such as 'not verified demand'; the Stage 57 test must not force those disclaimers to be removed."). The required_terms half is scoped to read-only/boundary vocabulary and is feasible.

**I1 — Fixed.** Task 3 Step 2 refactors `main()` away from the brittle positional slices (`tabs[:3]`, `tabs[3:-1]`, `tabs[-1]`, verified at `src/fashion_radar/dashboard/app.py:152-155`) to label-based routing:

```python
tab_by_label = dict(zip(DASHBOARD_TAB_LABELS, tabs, strict=True))
with tab_by_label["Heat Movers"]: render_heat_movers(...)
with tab_by_label["Trend Deltas"]: render_trend_deltas(...)
```

and adds `test_dashboard_main_routes_heat_movers_and_trend_deltas_by_label` using a fake `streamlit` module (`monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)`) that asserts (a) `fake_streamlit.labels == list(DASHBOARD_TAB_LABELS)`, (b) `render_heat_movers` runs under the "Heat Movers" label, and (c) `render_trend_deltas` runs under the "Trend Deltas" label. This catches the precise misroute the original I1 described (heat-movers tab rendering trend deltas or vice-versa). Only the secondary count invariant has a typo (R1).

## Minor Findings From Previous Review — Status

- **M1 (`REQUIRED_FLAGS_BY_COMMAND`):** Addressed. Task 4 Step 1 adds `"heat-movers": ("--config-dir", "--data-dir", "--as-of")` and asserts it.
- **M2 (negative-limit ownership):** Addressed via Task 4 Step 2's Typer parse-time assertion. Cross-task placement noted as R4.
- **M3 (CHANGELOG coverage):** Addressed. `changelog` is included in the `"heat-movers" in text` loop and Step 1 explicitly calls out CHANGELOG coverage.

## Scope Boundary Verification

Confirmed the revised plan still respects every Stage 57 exclusion:
- No platform connectors / APIs / scraping / crawling / browser automation / login / cookies / sessions / proxies / media downloads.
- No monitoring / watch loops / scheduling / notifications / webhooks.
- No DB schema, migrations, writes, report/dashboard artifacts, config/entity generation.
- No new scoring formulas, demand proof, coverage verification, source ranking, market-wide/platform-wide popularity claims.
- No compliance / legal / approval / policy / authorization / safety-review features.
- `Do not modify` list still guards `pyproject.toml`, `uv.lock`, schema/migrations, source/entity packs, report models/templates, and all collection/account code. Verification commands include `git diff --exit-code -- uv.lock pyproject.toml`, `uv lock --check`, `uv sync --locked --dev --check`, mirror-string scan, release hygiene, first-run smoke, and installed-wheel smoke.

## Final Verdict

Both prior blocking findings are resolved, all three prior minor findings are addressed, and the remaining rereview notes (R1–R4) are non-blocking refinements. The architecture remains a pure grouping/rendering layer over existing `TrendComparison`, exposed through a read-only CLI command and a dashboard tab that reuses the existing read-only trend query path. No schema, dependency, lockfile, collection, report-generation, platform, or compliance surface is added.

```text
APPROVED FOR STAGE 57 LOCAL HEAT MOVERS
```
