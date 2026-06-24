[0m
> build · glm-5.2
[0m
[0m→ [0mRead .
[0m→ [0mRead README.md
[0m→ [0mRead docs/PROJECT_BRIEF.md
[0m→ [0mRead docs/architecture.md
I'll review the project thoroughly. Let me start by exploring the structure and key documents in parallel.
[0m
[0m$ [0mgit -C /home/ubuntu/fashion-radar log --oneline -30
98653c5 test: pin community adapter catalog tables
e48ca03 test: guard readiness parity skip marks
c6efbe7 test: reject malformed trends deltas
a3b4f7f test: cover lint count label edge cases
02e7351 test: guard console script name case
2b98522 test: guard first-run config artifacts
3a0775e docs: list adapter catalog in community docs
f6af70e test: cover package archive dual utf8 errors
6ad4bb3 test: guard source pack quality json keys
d2384e1 test: guard community handoff renderer summaries
5ecb5bf docs: align upload checklist smoke contracts
4f1328f docs: sync source pack quality samples
2216410 docs: sync entity pack quality samples
89ccb88 docs: clarify first-run external tool smoke
10b2b40 docs: surface xpoz readiness guidance
1737b32 test: require external readiness smoke import
d0ee373 fix: singularize handoff check count labels
aa3cdbc fix: singularize community signal file rows
879fff0 fix: singularize manual dry-run file counts
cdede83 docs: sync public source pack lanes
6c79614 fix: singularize handoff check error labels
f0e9763 test: harden community handoff check smoke
b9c9150 test: cover lint finding formatting helper
6f8e9d3 fix: share lint finding count grammar
09cd599 fix: report invalid wheel text-member UTF-8
72bc97f fix: singularize source-pack lint finding counts
24745d5 feat: show source pack tag counts
eca52fd test: validate wheel console entry points
413db22 chore: guard review capture artifacts
82475b5 test: validate handoff check smoke payload
[0m
[0m→ [0mRead src/fashion_radar
[0m→ [0mRead tests
[0m→ [0mRead docs
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && git log --oneline | wc -l && echo "---" && git log --oneline -50 | tail -40
110
---
5ecb5bf docs: align upload checklist smoke contracts
4f1328f docs: sync source pack quality samples
2216410 docs: sync entity pack quality samples
89ccb88 docs: clarify first-run external tool smoke
10b2b40 docs: surface xpoz readiness guidance
1737b32 test: require external readiness smoke import
d0ee373 fix: singularize handoff check count labels
aa3cdbc fix: singularize community signal file rows
879fff0 fix: singularize manual dry-run file counts
cdede83 docs: sync public source pack lanes
6c79614 fix: singularize handoff check error labels
f0e9763 test: harden community handoff check smoke
b9c9150 test: cover lint finding formatting helper
6f8e9d3 fix: share lint finding count grammar
09cd599 fix: report invalid wheel text-member UTF-8
72bc97f fix: singularize source-pack lint finding counts
24745d5 feat: show source pack tag counts
eca52fd test: validate wheel console entry points
413db22 chore: guard review capture artifacts
82475b5 test: validate handoff check smoke payload
3ec3086 test: run strict community handoff smoke chain
37b0d33 feat: pin external tool workflow paths
565ae7b test: derive package archive fixture metadata
5eea5b1 feat: pin imported review top-level fields
c633b69 feat: pin community handoff top-level fields
acaee74 feat: pin community handoff step metadata
3472b34 feat: pin imported review step metadata
c42f764 Pin external tool display names
e4a59d0 Pin external tool template items
46f646b Pin readiness detail and boundary validation
5fc8053 Pin external workflow boundary validation
d814214 Pin workflow smoke metadata validation
3b7960e Harden community handoff step shape validation
d98d812 Harden imported review workflow commands
22deb60 Harden community handoff workflow commands
9b8cd5e Tighten readiness install hint validation
894af43 Align workflow smoke fixtures with builders
91cc24f Pin first-run command sequence assertions
4ad41b4 Harden remaining workflow command validators
969a0b9 Harden external tool readiness step commands
[0m
[0m→ [0mRead pyproject.toml
Let me explore the source code structure, tests, and remaining docs in parallel.
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && wc -l src/fashion_radar/*.py src/fashion_radar/*/*.py 2>/dev/null | sort -rn | head -50
14308 total
  2246 src/fashion_radar/cli.py
   675 src/fashion_radar/discovery/candidates.py
   674 src/fashion_radar/entity_packs.py
   585 src/fashion_radar/community_signals.py
   515 src/fashion_radar/external_tool_adapters.py
   469 src/fashion_radar/imported_signals.py
   467 src/fashion_radar/external_tool_readiness.py
   462 src/fashion_radar/importers/manual_signals.py
   452 src/fashion_radar/db/repositories.py
   432 src/fashion_radar/external_tool_workflow.py
   394 src/fashion_radar/community_candidates.py
   340 src/fashion_radar/source_packs.py
   327 src/fashion_radar/reports.py
   293 src/fashion_radar/dashboard/app.py
   290 src/fashion_radar/digests.py
   285 src/fashion_radar/imported_entity_deltas.py
   274 src/fashion_radar/trends.py
   272 src/fashion_radar/external_tool_templates.py
   266 src/fashion_radar/scoring.py
   261 src/fashion_radar/heat_movers.py
   246 src/fashion_radar/imported_candidate_evidence.py
   239 src/fashion_radar/dashboard/queries.py
   234 src/fashion_radar/imported_review_workflow.py
   234 src/fashion_radar/imported_entity_evidence.py
   229 src/fashion_radar/community_handoff_check.py
   223 src/fashion_radar/community_handoff_workflow.py
   217 src/fashion_radar/community_signal_profile.py
   190 src/fashion_radar/collectors/runner.py
   189 src/fashion_radar/community_handoff_manifest.py
   187 src/fashion_radar/settings.py
   185 src/fashion_radar/db/schema_inspection.py
   174 src/fashion_radar/db/schema.py
   145 src/fashion_radar/imported_candidates.py
   140 src/fashion_radar/scheduling.py
   137 src/fashion_radar/models/report.py
   121 src/fashion_radar/workflows.py
   115 src/fashion_radar/extract/entities.py
   113 src/fashion_radar/collectors/base.py
   107 src/fashion_radar/collectors/gdelt.py
   105 src/fashion_radar/utils/http.py
    96 src/fashion_radar/collectors/robots.py
    95 src/fashion_radar/collectors/article.py
    91 src/fashion_radar/models/source.py
    90 src/fashion_radar/collectors/rss.py
    80 src/fashion_radar/models/entity.py
    65 src/fashion_radar/models/trend.py
    64 src/fashion_radar/utils/hashing.py
    35 src/fashion_radar/extract/text.py
    34 src/fashion_radar/models/__init__.py
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && echo "=== external/community/imported cluster ===" && wc -l src/fashion_radar/external_*.py src/fashion_radar/community_*.py src/fashion_radar/imported*.py src/fashion_radar/importers/*.py 2>/dev/null | tail -1 && echo "=== core product cluster ===" && wc -l src/fashion_radar/collectors/*.py src/fashion_radar/scoring.py src/fashion_radar/reports.py src/fashion_radar/trends.py src/fashion_radar/heat_movers.py src/fashion_radar/discovery/*.py src/fashion_radar/models/*.py src/fashion_radar/db/*.py 2>/dev/null | tail -1 && echo "=== external cluster tests ===" && wc -l tests/test_external_*.py tests/test_community_*.py tests/test_imported*.py 2>/dev/null | tail -1 && echo "=== core product tests ===" && wc -l tests/test_collectors*.py tests/test_scoring*.py tests/test_matcher.py tests/test_trends.py tests/test_reports.py tests/test_heat_movers.py tests/test_candidate*.py 2>/dev/null | tail -1
=== external/community/imported cluster ===
  5599 total
=== core product cluster ===
  3799 total
=== external cluster tests ===
  8208 total
=== core product tests ===
  3084 total
[0m
Let me examine the core product modules and measure where code effort has gone, plus read the key remaining docs.
[0m$ [0mcd /home/ubuntu/fashion-radar && git log --oneline | grep -iE "external|community|handoff|imported|readiness|adapter|template|workflow" | wc -l && echo "--- external/community/handoff related commits ---" && git log --oneline | grep -ivE "external|community|handoff|imported|readiness|adapter|template|workflow" | head -40
44
--- external/community/handoff related commits ---
c6efbe7 test: reject malformed trends deltas
a3b4f7f test: cover lint count label edge cases
02e7351 test: guard console script name case
2b98522 test: guard first-run config artifacts
f6af70e test: cover package archive dual utf8 errors
6ad4bb3 test: guard source pack quality json keys
5ecb5bf docs: align upload checklist smoke contracts
4f1328f docs: sync source pack quality samples
2216410 docs: sync entity pack quality samples
879fff0 fix: singularize manual dry-run file counts
cdede83 docs: sync public source pack lanes
b9c9150 test: cover lint finding formatting helper
6f8e9d3 fix: share lint finding count grammar
09cd599 fix: report invalid wheel text-member UTF-8
72bc97f fix: singularize source-pack lint finding counts
24745d5 feat: show source pack tag counts
eca52fd test: validate wheel console entry points
413db22 chore: guard review capture artifacts
565ae7b test: derive package archive fixture metadata
91cc24f Pin first-run command sequence assertions
1edadc3 Validate package archive naming parity
c99ce31 Validate wheel dist-info metadata parity
6f3661d Scan untracked files for release hygiene secrets
4523c68 Align contributor verification surfaces
c48770f Derive package archive metadata from pyproject
ff1db6c Reject unexpected build directory artifacts
ae64fe3 Reject unsafe package archive member paths
587dcbc Align verification commands with frozen uv runs
a353a0f Exclude internal artifacts from sdist
d84f1fe Harden review redirect guard
ece52e6 Document opencode review capture hygiene
0ff4dc9 Align review protocol with local opencode
e716f4a Document agent uv run hygiene
3b34302 Document directory preflight discoverability
fb6df49 Expand watchlist sample coverage
05d176e Add dashboard candidate stale warning
fc11353 Align README MVP non-goals with project brief
6672a0f Guard dashboard warning staleness docs
157b5ac Guard source robots fetching docs
a140c68 Guard source quality boundary docs
[0m
[0m→ [0mRead docs/community-signal-import.md
[0m→ [0mRead docs/candidate-discovery.md
[0m→ [0mRead docs/trend-deltas.md
[0m→ [0mRead docs/dashboard.md
[0m→ [0mRead docs/scheduling.md
Now let me read the core product docs and key implementation modules to assess actual product quality.
[0m→ [0mRead docs/community-signal-quality.md
[0m→ [0mRead src/fashion_radar/scoring.py
[0m→ [0mRead src/fashion_radar/extract/entities.py
Now let me examine the core implementation quality and verify the project's actual functional health.
[0m→ [0mRead src/fashion_radar/collectors/runner.py
[0m→ [0mRead CHANGELOG.md
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && uv --no-config run --frozen ruff check . 2>&1 | tail -5
All checks passed!
[0m
Let me run the test suite and inspect the largest "external" module to confirm the drift assessment, plus check the CHANGELOG.
[0m→ [0mRead src/fashion_radar/external_tool_adapters.py[90m [limit=90][0m
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && uv --no-config run --frozen pytest -q 2>&1 | tail -20
http2=http2,
                socket_options=socket_options,
            )
        elif proxy.url.scheme in ("socks5", "socks5h"):
            try:
                import socksio  # noqa
            except ImportError:  # pragma: no cover
>               raise ImportError(
                    "Using SOCKS proxy, but the 'socksio' package is not installed. "
                    "Make sure to install httpx using `pip install httpx[socks]`."
                ) from None
E               ImportError: Using SOCKS proxy, but the 'socksio' package is not installed. Make sure to install httpx using `pip install httpx[socks]`.

.venv/lib/python3.11/site-packages/httpx/_transports/default.py:191: ImportError
=========================== short test summary info ============================
FAILED tests/test_collectors_runner.py::test_collect_sources_records_failure_and_continues_to_next_source
FAILED tests/test_collectors_runner.py::test_collect_sources_passes_started_at_to_timing_aware_collectors
FAILED tests/test_collectors_runner.py::test_collect_sources_stores_source_weight_and_collected_at
FAILED tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors
4 failed, 1385 passed in 34.76s
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && echo "=== last 30 commits by type ===" && git log --oneline -30 | awk -F': ' '{print $1}' | awk '{print $1}' | sort | uniq -c | sort -rn && echo "" && echo "=== fix commit subjects (last 40) ===" && git log --oneline -40 --grep='^fix' | grep -iE 'singular|count|label|grammar|utf|grammar' | wc -l && echo "=== proxy env in test env ===" && env | grep -iE 'proxy|ALL_PROXY' | head
=== last 30 commits by type ===
      1 f6af70e
      1 f0e9763
      1 eca52fd
      1 e48ca03
      1 d2384e1
      1 d0ee373
      1 cdede83
      1 c6efbe7
      1 b9c9150
      1 aa3cdbc
      1 a3b4f7f
      1 98653c5
      1 89ccb88
      1 879fff0
      1 82475b5
      1 72bc97f
      1 6f8e9d3
      1 6c79614
      1 6ad4bb3
      1 5ecb5bf
      1 4f1328f
      1 413db22
      1 3a0775e
      1 2b98522
      1 24745d5
      1 2216410
      1 1737b32
      1 10b2b40
      1 09cd599
      1 02e7351

=== fix commit subjects (last 40) ===
7
=== proxy env in test env ===
no_proxy=localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,169.254.0.0/16,169.254.169.254,154.89.153.24
ftp_proxy=http://127.0.0.1:8080
https_proxy=http://127.0.0.1:8080
NO_PROXY=localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,169.254.0.0/16,169.254.169.254,154.89.153.24
FTP_PROXY=http://127.0.0.1:8080
GOPROXY=https://mirrors.tencent.com/go,direct
HTTPS_PROXY=http://127.0.0.1:8080
HTTP_PROXY=http://127.0.0.1:8080
http_proxy=http://127.0.0.1:8080
ALL_PROXY=socks5h://127.0.0.1:1080
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && echo "=== source-packs shipped ===" && ls configs/source-packs/ 2>/dev/null && echo "=== public source pack feed count ===" && grep -cE '^\s*-\s*(url|name):' configs/source-packs/fashion-public.example.yaml 2>/dev/null; grep -E '^\s*name:\s' configs/source-packs/fashion-public.example.yaml 2>/dev/null | head -30
=== source-packs shipped ===
fashion-public.example.yaml
=== public source pack feed count ===
16
[0m
Let me quantify the commit trajectory precisely to ground the drift assessment, and confirm the test failures are environmental.
[0m$ [0mcd /home/ubuntu/fashion-radar && git -C . log --oneline --since="2026-06-01" --until="2026-06-25" 2>/dev/null | head -5; echo "---commit date range---"; git log --format='%ci' | tail -1; git log --format='%ci' | head -1
98653c5 test: pin community adapter catalog tables
e48ca03 test: guard readiness parity skip marks
c6efbe7 test: reject malformed trends deltas
a3b4f7f test: cover lint count label edge cases
02e7351 test: guard console script name case
---commit date range---
2026-06-18 09:09:55 +0800
2026-06-24 09:43:07 +0800
[0m
[0m$ [0mcd /home/ubuntu/fashion-radar && echo "=== commit type counts (all 110) ===" && git log --format='%s' | sed 's/:.*//' | sort | uniq -c | sort -rn && echo "" && echo "=== 'test'/'fix' subjects mentioning singularize/pin/guard/harden/pin/parity ===" && git log --format='%s' | grep -iE 'singular|pin |guard|harden|parity|validate|reject' | wc -l && echo "(out of 110 total)"
=== commit type counts (all 110) ===
     16 test
      7 fix
      7 docs
      6 feat
      1 Validate wheel dist-info metadata parity
      1 Validate package archive naming parity
      1 Tighten readiness install hint validation
      1 Tighten external import docs tests
      1 Scope roadmap boundary docs test
      1 Scan untracked files for release hygiene secrets
      1 Route PR template to upload checklist
      1 Reject unsafe package archive member paths
      1 Reject unexpected build directory artifacts
      1 Pin workflow smoke metadata validation
      1 Pin readiness detail and boundary validation
      1 Pin first-run command sequence assertions
      1 Pin external workflow boundary validation
      1 Pin external tool template items
      1 Pin external tool display names
      1 Harden suggested platform label boundaries
      1 Harden review redirect guard
      1 Harden remaining workflow command validators
      1 Harden imported review workflow commands
      1 Harden external tool workflow step commands
      1 Harden external tool readiness step commands
      1 Harden external tool command shape smoke checks
      1 Harden community handoff workflow commands
      1 Harden community handoff step shape validation
      1 Guard trend delta comparison docs
      1 Guard source storage boundary docs
      1 Guard source robots fetching docs
      1 Guard source README requirements docs
      1 Guard source quality boundary docs
      1 Guard source packs public docs
      1 Guard source pack quality docs boundaries
      1 Guard source output boundary docs
      1 Guard security redaction docs
      1 Guard scoring docs limits
      1 Guard scheduling docs boundaries
      1 Guard project brief MVP non-goals
      1 Guard manual signal import privacy docs
      1 Guard first run docs boundary
      1 Guard entity packs docs boundaries
      1 Guard entity pack quality docs boundaries
      1 Guard data retention docs boundaries
      1 Guard dashboard warning staleness docs
      1 Guard dashboard docs boundaries
      1 Guard daily digest docs boundaries
      1 Guard candidate discovery docs boundaries
      1 Guard architecture source boundary docs
      1 Expand watchlist sample coverage
      1 Exclude internal artifacts from sdist
      1 Document upload checklist mirror recovery
      1 Document opencode review capture hygiene
      1 Document mirror lockfile recovery
      1 Document external tool import path
      1 Document directory readiness preflight samples
      1 Document directory preflight discoverability
      1 Document code review record names
      1 Document agent uv run hygiene
      1 Derive package archive metadata from pyproject
      1 Clarify onboarding roadmap
      1 Clarify adapter platform labels
      1 chore
      1 Align workflow smoke fixtures with builders
      1 Align verification commands with frozen uv runs
      1 Align review protocol with local opencode
      1 Align README MVP non-goals with project brief
      1 Align PR template package smoke guidance
      1 Align issue template verification commands
      1 Align external tool CLI reference options
      1 Align contributor verification surfaces
      1 Align community handoff documentation order
      1 Add XPOZ external tool adapter metadata
      1 Add suggested platform label guidance
      1 Add readiness installed smoke coverage
      1 Add dashboard candidate stale warning
      1 Add adapter contract parity gate

=== 'test'/'fix' subjects mentioning singularize/pin/guard/harden/pin/parity ===
63
(out of 110 total)
[0m
I have everything needed. Here is the review.

---

# Full Project Review

## 1. Findings (by severity)

### Critical

**C1 — Tests fail in any environment with an ambient proxy.** `uv --no-config run --frozen pytest` → **4 failed, 1385 passed**. The failures (`tests/test_collectors_runner.py::test_collect_sources_*`, `tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors`) come from `httpx` picking up `ALL_PROXY=socks5h://...` and raising `ImportError: socksio not installed`. These tests instantiate real `FashionHttpClient`/httpx clients without isolating proxy env vars, so they break on any developer/CI machine with a corporate or mirror proxy. This is a test-isolation bug, not a product bug, but it means the green-build claim is fragile. The collector tests must scrub proxy env (`monkeypatch.delenv`/`httpx.MockTransport`) or use the injected-collector seam they already expose.

### Important

**I1 — Severe effort drift into a non-functional surface.** The "external tool handoff" cluster — `external_tool_adapters.py` (515 LOC), `external_tool_readiness.py` (467), `external_tool_workflow.py` (432), `external_tool_templates.py` (272), `community_signals.py` (585), `community_handoff_*.py` (~640), `imported_*.py` (~1,400) — totals **~5,600 LOC source + ~8,200 LOC tests (~13,800 LOC)**. The actual core product (collectors + scoring + matcher + reports + trends + heat-movers + discovery + models + db) is **~3,800 LOC source + ~3,100 LOC tests (~6,900 LOC)**. So a print-only, explicitly-non-functional scaffolding is **2× the size of the product that fulfills the brief**. The git history confirms the trajectory: of 110 commits (all within **6 days, 2026-06-18→06-24**), only **6 are `feat:`** while **63 (57%)** are `Pin/Harden/Guard/Validate/Reject/Singularize/Align` churn, almost all against the external-tool and doc-boundary surface. The CHANGELOG is on "Stage 173" (`CHANGELOG.md:11`) and stages ~53–173 are dominated by this same axis.

**I2 — Documentation is collapsing under repetitive boundary disclaimers.** The same multi-sentence "It is not platform collection and has no connectors, no scraping, no browser automation, no platform APIs, no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, and no coverage verification" block is duplicated **verbatim 20+ times** across `README.md` (911 lines), `docs/architecture.md` (428), `docs/community-signal-import.md` (825), and `docs/community-signal-quality.md` (471). README's Quickstart is buried below hundreds of lines of handoff-command exposition. This actively harms onboarding for the core use case ("monitor timely fashion information") that the brief leads with.

**I3 — Product-critical gaps relative to the brief are unaddressed.** The brief (`docs/PROJECT_BRIEF.md:5-15`) prioritizes *celebrity outfits/street style, brand heat changes, trend terms, emerging designers*. Current state:
- Only **one** source pack ships (`configs/source-packs/fashion-public.example.yaml`, 16 RSS/GDELT entries). No validation that these feeds are live/healthy, no curated celebrity-style or street-style sources.
- Matching is single-alias substring (`extract/entities.py:41` `alias_pattern(alias.value).search(text)`); no fuzzy, no normalization for case/diacritics beyond `normalize_alias_key`, no disambiguation when two entities share text. Fine for v0.1, but no work has gone toward the matching-quality the target entities (celebrity names, product lines) demand.
- No LLM summarization even as an opt-in (brief allowed it later; `PROJECT_BRIEF.md:72`). The daily report is pure snippet concatenation.

### Minor

**M1 — `_label_entity` returns `"stable"` on both terminal branches** (`scoring.py:264-266`). Harmless but the final `if/return "stable"` pair is redundant.

**M2 — `external_tool_adapters.py:18-30` hardcodes boundary strings as module constants** then re-asserts them in tests; this is the engine driving I1's churn (every boundary rewording ripples through tests + 4 docs).

## 2. Overall Assessment

**The core is genuinely well-built.** `scoring.py` is transparent and correctly typed (`extra="forbid"`, explicit components, stable first-seen). The collector runner (`collectors/runner.py`) has proper health circuit-breakers, robots.txt gating, and graceful article-extraction degradation. The matcher's context-gate design (`extract/entities.py:63-87`) is a thoughtful answer to common-alias false positives. SQLite schema is versioned (v5) with read-only `doctor`. Test coverage breadth is high (1385 passing).

**But the trajectory is incoherent with the product goal.** The project has spent ~57% of its commits and ~2× its code mass hardening a *print-only registry* of adapters that, by its own repeated insistence, does nothing functional — while the actual "fashion intelligence" pipeline has had **zero feature commits** in the recent window. The review-gated stage process (`docs/REVIEW_PROTOCOL.md`, "Stage 173") has become a forcing function for low-value boundary-polishing rather than product capability. The architecture and testing strategy are technically reasonable *in isolation*; the *allocation* of them is not.

**Strong:** scoring transparency, collector robustness, deterministic matcher, schema versioning, free-first boundary discipline.
**Missing:** source breadth/health validation, matching quality for real fashion entity names, any summarization, and any user-visible capability added recently.

## 3. Recommended Roadmap Corrections

1. **Freeze the external-tool/handoff surface.** No new `external-tool-*` / `community-handoff-*` / `imported-*` commands, boundary-string edits, or parity tests until after v0.1.0 ships. Consider consolidating the 8 adapters + 4 handoff commands into 1–2 commands; the print-only registry is over-built for an MVP that explicitly excludes platform collection.
2. **De-duplicate the boundary disclaimer** into a single `docs/source-boundaries.md` section and reference it; trim README to <300 lines focused on collect→match→report→dashboard.
3. **Fix C1 before any release** — the suite must pass under a proxy env.
4. **Redirect stages to product value:** source-pack breadth + a `source-health`/feed-liveness check, matching-quality iteration (diacritics/case/entity disambiguation), and an opt-in summary step.

## 4. Top 3 Next Steps

1. **Fix the 4 proxy-env test failures** (isolate proxy env in `tests/test_collectors_runner.py` and `tests/test_workflows.py`) so `pytest` is green independent of host proxy config.
2. **Curate and validate real source coverage:** expand `fashion-public.example.yaml` with live celebrity-style/street-style/designer RSS feeds and add a read-only feed-liveness diagnostic so the core "monitor timely fashion information" promise is demonstrably true.
3. **Stop the handoff-surface hardening loop** and move the next review stage to matching quality + optional report summarization — the two highest-unclosed gaps between the current build and the brief's stated user outcomes.
