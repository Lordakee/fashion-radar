# Stage 110 Source Boundaries Robots Fetching Docs Design

## Goal

Add a section-scoped docs drift guard for the `## Robots And Fetching` section in
`docs/source-boundaries.md` so future edits keep fetching guidance explicit:
article extraction checks robots.txt first, skipped URLs preserve reasons,
source-specific rate limits remain documented, and GDELT guidance keeps
separate metadata/link storage and backoff boundaries explicit.

## Scope

Stage 110 is docs-test-only. It appends one focused pytest test to the existing
`tests/test_source_boundaries_docs.py` module. The test reads
`docs/source-boundaries.md`, extracts the `## Robots And Fetching` section,
normalizes whitespace and case, and asserts stable robots/fetching boundary
phrases.

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 110 spec, plan, and review artifacts

Out of scope:

- `docs/source-boundaries.md` source text
- `README.md`
- collector behavior, HTTP behavior, robots parser behavior, source fetching,
  article extraction, GDELT runtime behavior, dashboard/report behavior, CLI
  behavior, scheduling, monitoring, source acquisition, connector behavior,
  social/platform scraping, browser automation, account/session/cookie/proxy
  handling, coverage verification, ranking behavior, compliance/audit/legal
  review product features, `src/`, `scripts/`, `examples/`, configs, schemas,
  dependencies, CI, `uv.lock`, package metadata, or release hygiene behavior

## Boundary Phrases

The guard should extract only `## Robots And Fetching` and assert these phrases
after whitespace collapse and case-folding:

- `Before fetching an article page for extraction, collectors must check robots.txt.`
- `Default fetch behavior:`
- `Use source-specific rate limits where configured.`
- `Record skipped URLs with reasons.`
- `GDELT fetch behavior:`
- `Use bounded exponential backoff.`
- `Store GDELT-provided metadata and links, not republished article bodies.`

These phrases pin the public fetching-boundary wording without adding runtime
collector checks, HTTP policy changes, robots parser assertions, or source
collection behavior.

Stage 110 deliberately does not freeze the numeric GDELT throttle sentence
(`near 1 request per second`) because that default is a likely legitimate future
doc edit and is already described elsewhere in project specs.

## Test Shape

Reuse the helpers already present in `tests/test_source_boundaries_docs.py`:

- `_read_source_boundaries_doc()`
- `_normalized()`
- `_section()`

Append one test function with a focused phrase loop. The test must not import
application modules, execute CLI commands, open SQLite, read or write
data/report/dashboard files, fetch network resources, render dashboards/reports,
run collectors, inspect robots.txt, or write files.

## Verification

Focused verification should cover `tests/test_source_boundaries_docs.py` and
adjacent docs/runtime-reference tests that already touch collectors, robots,
source boundaries, project brief docs, and CLI docs, then ruff, formatting, and
whitespace checks. Full verification before commit should reuse the repository
release gate: release hygiene, full pytest with proxy vars unset, repo-wide ruff
check and format check, lockfile check, mirror URL scan, `uv.lock`/
`pyproject.toml` diff guard, staged hygiene, and staged secret scan.

Because adjacent collector tests may instantiate HTTP clients, Stage 110 should
unset `ALL_PROXY` and `all_proxy` for the adjacent pytest bundle just like the
repo-wide release gate already does for full pytest.

## Risks

The `## Robots And Fetching` section overlaps conceptually with collector and
HTTP runtime tests. Stage 110 deliberately pins only source-boundaries document
wording and does not change collectors, HTTP clients, robots policy behavior,
GDELT fetching, or runtime source collection.
