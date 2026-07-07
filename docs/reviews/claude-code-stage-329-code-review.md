---

## Stage 329 Code Review

### Critical

**None.**

All hard boundaries are upheld: no writes, no `systemctl`, no `SO_REUSEADDR`, no server starts, no schema/contract changes. The bind probe correctly catches all `Exception` subclasses so socket errors never crash the diagnostic.

---

### Important

**1. `_overall_status` silently tightens the `ready` spec.**

The design spec (`row-one-local-ops-check-design.md`) defines `ready` as: site present + runtime fresh + server `serving_row_one`. Systemd is not listed as a requirement; missing units should yield `attention`, not block `ready`.

The implementation (`ops_check.py:248–253`) adds `systemd.get("status") == "present"` to the `ready` condition, so a machine with a fresh site, a running ROW ONE server, and no systemd units installed would get `attention` instead of `ready`. The test suite doesn't have a case that distinguishes these two outcomes (no test with fresh + serving_row_one + missing units). The behaviour is conservative and arguably better ops practice, but it diverges from the written spec without documentation.

**Recommendation:** Either update the spec sentence in both docs to say `ready` requires systemd, or add a comment in `_overall_status` explaining the deliberate tightening, and add a test covering `fresh + serving_row_one + missing units → attention`.

---

**2. Duplicate noisy action when site is missing.**

When the site directory is absent, `_load_runtime` returns `None`, so `_freshness_payload` sets `status="unknown"`. `_actions` then appends **both**:

- `"Generate the ROW ONE site at {site_dir}."` (site missing)
- `"Regenerate ROW ONE runtime metadata with \`fashion-radar row-one refresh\`."` (freshness unknown)

The second action is redundant — refreshing produces the site, not just the metadata. The test at `test_ops_check_reports_missing_site_without_writing_files` doesn't check the `actions` list, so this is untested.

**Recommendation:** Guard the freshness-unknown action: only emit it when the site is present but runtime is corrupt/missing, not when the entire site is absent.

---

### Medium

**1. Human-readable output omits `site_dir` and `as_of`.**

The design output table lists Status/Freshness/Server/Systemd/Access/Actions — the implementation matches. However, `site_dir` and `as_of` are in the JSON payload but absent from human output, which can make a `--json`-less run harder to interpret when non-default paths or times are used. This is within spec but is a minor ergonomic gap. No test exercises a non-default `site_dir` in human output.

**2. `_freshness_payload` compares `edition_date` as a date, not `generated_at`.**

The spec says both `generated_at` and `edition_date` are parsed; freshness is checked on `edition_date`. The implementation uses `edition_date.date().isoformat() == expected_date` (line 162), which is correct. But `generated_at` is parsed and reported without being checked for freshness, so a site with a past `generated_at` but today's `edition_date` still reports `fresh`. This matches the spec, but the distinction is not called out in comments.

**3. Probe `urlopen` is module-attribute patched in tests.**

`test_probe_row_one_server_classifies_row_one_content` monkeypatches `ops_check.urlopen`. This only works because the module does `from urllib.request import urlopen` and the tests patch the name in the module's namespace — which is the correct pattern. However, `probe_row_one_server` is a public function with no injection parameter; all real-port tests rely on this monkeypatch. If the import style ever changes to `urllib.request.urlopen(...)` the tests silently stop patching. Worth noting for future contributors.

**4. Missing coverage: `stale` + `serving_row_one` + `present` units → `attention`.**

The test suite covers `stale + serving_other + missing` and `fresh + serving_row_one + present`. There is no test asserting that stale freshness alone forces `attention` (systemd present, server running). The logic is correct by inspection but the gap means a future refactor of `_overall_status` could regress silently.

---

### Minor

**1. `test_row_one_cli_docs_list_build_preview_serve_and_schedule_commands` function name is now stale** — it doesn't mention `ops_check` despite covering it. Cosmetic only.

**2. `_actions` emits `fashion-radar row-one refresh` without `--output-dir` for the `freshness == "unknown"` case**, but does include `--output-dir {site_dir}` for the `stale` case. If the user has a non-default `site_dir`, the unknown-freshness action message is incomplete guidance.

**3. The `"not-a-date"` rejection test in `test_row_one_cli.py` checks `result.output`** (stdout+stderr combined under Typer CliRunner) for `"must be an ISO datetime"`. The CLI writes to `err=True` (stderr). In mostCliRunner setups `mix_stderr=True` by default, so the assertion works, but if a caller switches to `mix_stderr=False` the assertion would silently miss. Low risk — this is a test style note.

**4. Docs boundary sentence in `row-one.md` ends with a separate inline paragraph** immediately after the `## Ops Check` section body, which breaks the visual flow. Both the full-sentence boundary note and the Ops Check prose describe non-mutating behavior; the boundary sentence reads as duplicative to the section body. Not a correctness issue.

---

### Verdict

**Approve with one recommended fix before merge (Important #2) and one documentation clarification (Important #1).**

The core implementation is correct, safe, and well-tested. All hard boundaries hold. The injectable probe pattern is properly used, `SO_REUSEADDR` absence is explicitly tested, and the CLI correctly separates `--as-of` parse failure from diagnostic failure. The main gap is the duplicate noisy action when the site is absent, which a single guard in `_actions` fixes. The spec/implementation divergence on what constitutes `ready` vs `attention` for systemd should be documented even if the stricter behavior is kept.
