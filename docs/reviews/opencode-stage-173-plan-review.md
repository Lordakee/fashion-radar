# Stage 173 Plan Review

Objective:

Make XPOZ MCP / Social Data API exports discoverable in the
`external-tool-readiness` docs and guard that discoverability with a docs parity
test.

Summary

The plan is a docs/test-only stage that surfaces `xpoz_mcp` in the existing
user-facing `external-tool-readiness` known-tool prose, adds two copyable
readiness command examples (`fashion-radar ... --adapter xpoz_mcp --format json`
in CLI reference and upload checklist, plus the installed-wheel smoke variant
in the checklist), and adds a Stage 173 changelog entry. Discoverability is
guarded by one new pytest in `tests/test_cli_docs.py` that defines a narrow
`EXTERNAL_TOOL_READINESS_XPOZ_DISCOVERABILITY_DOCS` tuple (README,
cli-reference, community-signal-import, community-signal-quality,
source-boundaries, architecture, github-upload-checklist, CHANGELOG) and checks
four XPOZ-relevant phrases plus three exact command strings.

The runtime registry already contains XPOZ (adapter `xpoz_mcp` in
`src/fashion_radar/external_tool_adapters.py:217`, readiness spec in
`src/fashion_radar/external_tool_readiness.py:87`, adapter matrix rows already
in README and cli-reference). No runtime source, adapter metadata, readiness
builder behavior, payload shape, validator, command order, install hint, or
mirror hint is touched. The staged TDD flow (RED docs test, then docs updates,
then GREEN, then code review, release gate, release review, commit, push)
matches `docs/REVIEW_PROTOCOL.md`.

Findings

Critical

None.

Important

None.

Minor

1. Phrase overlap with the existing
   `test_external_tool_readiness_docs_are_linked_and_bounded` is intentional but
   worth noting: two of the four required phrases (`external-tool-readiness` and
   `sanitized csv/json local file handoff`) are already enforced by the existing
   test across a superset of docs. The new test's net new coverage is the
   `xpoz mcp` and `social data api` substrings plus the three exact command
   strings. This redundancy is harmless and keeps the discoverability test
   self-contained, but the spec could say so explicitly to prevent future
   trim attempts.
2. The wording template in Task 2 Step 1 shows a specific line wrap
   (`yt-dlp, X/search\nexports, and XPOZ MCP / Social Data API exports`). The
   eight target docs wrap the existing enumeration differently (for example,
   `docs/community-signal-import.md:130-131` wraps as `..., Instaloader,\nTikTok-Api, yt-dlp, and X/search exports,`). The implementer should adapt the
   rewriter to each doc's surrounding line breaks rather than literal-search the
   template string. The wording family is clear enough that this is mechanical.
3. The new tuple inlines path literals
   (e.g. `ROOT / "docs" / "community-signal-import.md"`,
   `ROOT / "docs" / "architecture.md"`, `ROOT / "CHANGELOG.md"`) instead of
   reusing the existing module-level constants
   (`COMMUNITY_SIGNAL_IMPORT_DOC`, `ARCHITECTURE_DOC`, `SOURCE_BOUNDARIES_DOC`,
   `CHANGELOG`). Existing tuples in this file mix both styles, so this is only a
   consistency nit, not a correctness issue.
4. The plan does not call out that the existing
   `test_external_tool_readiness_upload_checklist_help_loop_and_smoke` and
   `test_external_tool_adapter_registry_docs_are_linked_and_bounded` must
   continue to pass. They will: the xpoz_mcp adapter matrix row already exists
   (README:155, cli-reference.md:125), the help loop is command-level not
   adapter-level, and the existing instaloader/rednote_mcp adapter command
   assertions are additive with the new xpoz_mcp checks. Worth stating for the
   implementer.

Plan Assessment

1. Appropriately scoped and safe? Yes. The scope is docs/test-only, the file
   list is bounded to docs plus one test file, and the runtime adapter and
   readiness modules are explicitly out of scope. No new runtime behavior,
   payload, validator, or script change is introduced.
2. Satisfies the project boundary rules in `AGENTS.md`? Yes. The
   `external-tool-readiness` boundary rule in `AGENTS.md:112-124` permits local
   read-only command availability guidance with PATH lookup, mirror-friendly
   install hints, and handoff next steps for sanitized CSV/JSON local file
   handoff rows. The plan adds discoverability prose and copyable commands only,
   keeps the existing boundary wording intact, and does not add connectors,
   scraping, browser automation, platform APIs, account/session/cookie/token
   behavior, monitoring, scheduling, source acquisition, demand proof, ranking,
   coverage verification, or any compliance-review feature. The changelog entry
   text repeats the denial list, which is consistent with prior docs-only
   stages.
3. Docs parity test useful without being too broad or brittle? Yes. The test is
   narrow: it requires only XPOZ-specific substrings (`xpoz mcp`,
   `social data api`) in eight named docs plus three exact command strings in
   two docs. It uses the existing `_read` and `_normalized_text` helpers with
   `.casefold()`, so it survives whitespace and casing changes. It does not
   enforce a single canonical wording, does not pin line wrapping, and
   correctly excludes `AGENTS.md` (which is a future-work boundary document,
   not a known-tool list). Substring checks on raw text for the command strings
   match the pattern already used for the instaloader and rednote_mcp readiness
   commands. RED behavior before docs updates is genuine: six of the eight docs
   lack both `xpoz mcp` and `social data api`, and none of the three command
   strings exist yet.
4. Does the proposed wording avoid implying Fashion Radar runs XPOZ, calls
   external APIs, manages MCP servers, stores keys, or verifies platform
   coverage? Yes. The phrase `XPOZ MCP / Social Data API exports` describes
   sanitized local handoff exports produced outside Fashion Radar, parallel to
   the existing `X/search exports` and `Instaloader Export` entries. It matches
   the runtime `display_name` (`XPOZ MCP Export`), `upstream_tool_examples`
   (`["XPOZ MCP", "XPOZ Social Data API"]`), `description`
   (`Metadata target for sanitized XPOZ MCP / Social Data API exports created
   outside Fashion Radar.`), and `install_hint` (`Use XPOZ MCP / Social Data API
   docs to create a sanitized local JSON export.`). The surrounding readiness
   boundary prose (which the plan preserves unchanged) already denies API calls,
   MCP execution, account/cookie/token behavior, and platform coverage
   verification, and the changelog entry repeats that denial list. The plan's
   design doc also explicitly tells the implementer not to say Fashion Radar
   runs XPOZ, calls XPOZ APIs, manages MCP servers, stores API keys, validates
   access, verifies platform coverage, or collects platform data.
5. Critical or important planning findings before implementation? No. The plan
   is internally consistent, the RED-to-GREEN sequence is genuine, the
   verification command list covers the focused docs test, related runtime tests
   (`tests/test_external_tool_readiness.py::test_readiness_upstream_command_mapping`,
   `tests/test_external_tool_adapters.py::test_xpoz_mcp_adapter_has_expected_mapping_and_commands`),
   ruff, the full release gate (proxy-stripped pytest, first-run smoke, release
   hygiene, ruff, format check, `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`,
   token sweep, extraheader check), and the commit/push step. The review record
   artifacts and commit message follow the established stage convention.

Verdict

Approve. The Stage 173 plan is safe, boundary-compliant, and ready for
implementation. Proceed with Task 1 (RED test), confirm the new test fails for
the documented reason, then execute Task 2 and Task 3 as written, accounting
for the per-doc line-wrap variation noted in Minor 2.
