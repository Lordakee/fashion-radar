I'll review the Stage 85 plan and design documents. Let me read all the relevant files in parallel.
Now let me read the remaining test file sections, the quality doc, the example JSON, and the schema to verify the `platform` field definition.
Let me verify a few critical details: the schema's `platform` field (no enum), any other direct model constructions that could break, and CHANGELOG expectations.
I've completed a thorough review of the Stage 85 spec, plan, and all referenced source/test/doc files. Here are my findings.

---

# Stage 85 Plan Review — Findings

Ordered by severity. **No Critical blockers.** **One Important finding** to address before implementation.

## Important

### I-1: Docs-drift test (Task 7) requires 7 verbatim phrases in *both* docs, but the `community-signal-import.md` edit instructions don't guarantee them

The test loop in `docs/.../stage-85-...-plan.md:203-215` asserts each of these terms appears in **both** `import_doc` and `quality_doc`:

- `suggested_platform_labels`
- `advisory local provenance label guidance`
- `optional handoff \`platform\` field`
- `not a schema enum`
- `not a linter restriction`
- `not platform coverage`
- `not demand proof`

The **quality-doc** paragraph at `plan.md:193-197` satisfies all seven verbatim. ✅

The **import-doc** instructions at `plan.md:174-189` only explicitly produce `suggested_platform_labels` and `advisory local provenance label guidance`, and the Producer-Profile prose says *"optional `platform` field"* (`plan.md:175`) — note the test requires the literal *"optional handoff \`platform\` field"* (with the word `handoff`). The remaining four negation phrases are **not** instructed for `import_doc` at all.

An implementer following the import-doc prose literally will fail `test_community_signal_profile_docs_are_linked` on the first verification run (backticks and spacing are matched on raw, non-normalized text — see `tests/test_cli_docs.py:1231`).

**Fix (pick one):**
1. Add the same advisory sentence set (or the equivalent paragraph) to the Producer Profile and/or Directory Manifest sections of `docs/community-signal-import.md`, ensuring all seven substrings appear verbatim — including *"optional handoff \`platform\` field"*, *"not a schema enum"*, *"not a linter restriction"*, *"not platform coverage"*, *"not demand proof"*; **or**
2. Narrow the per-doc assertion so the four "not a …" / "optional handoff" phrases are only required in `quality_doc`.

Option 1 is preferred — it keeps the import doc self-describing, consistent with how `community-signal-quality.md` is being treated.

## Minor

### M-1: No CHANGELOG entry in the plan
The repo keeps a detailed `CHANGELOG.md` and many `test_cli_docs.py` suites reference it (e.g. `tests/test_cli_docs.py:1361,1418,1459,1537,1663`). No existing test will break, but a short advisory entry would match project convention for the community-signal stage series. Not required by any gate.

### M-2: Worth stating explicitly that no CLI change is needed
JSON serialization of the new field is automatic via pydantic (`model_dump_json`), and only the two table renderers need edits. Stating this in the plan avoids an implementer needlessly touching `cli.py`. No blocker.

---

## Answers to the review questions

1. **Useful machine-readable provenance guidance without becoming schema/validation rules?** Yes. Verified `schemas/community-signals.schema.json` has **no `enum`** anywhere; `platform` stays a free string (`schema.json:64`). The new field lives only on the profile/manifest models. Parity asserts `suggested_platform_labels not in profile.allowed_fields` and `not in profile.csv_header` (`plan.md:99-100,166-167`), and `allowed_fields` is derived from `COMMUNITY_SIGNAL_CSV_HEADER` (`community_signal_profile.py:199-205`), so lint/import behavior is untouched. Advisory metadata only. ✅
2. **Profile + manifest insertion points compatible with stable key-order tests and table renderers?** Yes. Profile field after `json_envelopes` (`community_signal_profile.py:67`) and manifest field after `supported_input_formats` (`community_handoff_manifest.py:59`) are both reflected in the stable-order tests (`tests/test_community_signal_profile.py:111`, `tests/test_community_handoff_manifest.py:33`) and the renderer edits. The only direct `CommunityHandoffManifest(...)` construction in tests (`tests/test_community_handoff_manifest.py:189`) is updated in Task 5 — and since the new field has no default, that update is *required* to avoid a pydantic `Field required` error, so it's correctly flagged. No other direct constructions exist in code/tests (other matches are historical plan docs). ✅
3. **Adapter parity catches drift without circular import?** Yes. `external_tool_adapters.py:9` already imports `build_community_signal_profile`; `tests/test_external_tool_contract_parity.py:9,11-13` already imports both. Task 6 adds no new import — it reuses the in-scope `profile` and `adapter` objects. The 7 adapter labels (`external_tool_adapters.py:112,130,148,166,184,202,219`) exactly equal the 7 suggested labels, and the in-loop `adapter.platform_label in profile.suggested_platform_labels` guards future drift. ✅
4. **Docs/test updates scoped enough and advisory-worded?** Mostly yes — see **I-1** for the one wording gap. Otherwise wording is advisory ("advisory local provenance label guidance", "not a schema enum, not a linter restriction"), scope is limited to the two named docs + focused tests, and no platform-support/coverage claim is introduced. ✅ (after I-1)
5. **Verification commands sufficient?** Yes. Task 8 runs the four affected test modules + ruff check/format on the touched files; Task 9 runs full pytest, ruff, format, `UV_NO_CONFIG=1 uv lock --check`, the mirror-free `uv.lock` scan, and `git diff --check`. Covers deterministic example regen (`test_profile_example_format_is_byte_for_byte_deterministic`), parity, docs drift, and lockfile hygiene. ✅
6. **Critical/Important blockers before implementation?** **No Critical blockers.** One Important blocker (**I-1**); fix it (preferably by adding the advisory sentences to `docs/community-signal-import.md`) and the plan is safe to implement.

**Recommendation:** Address I-1 (add the seven verbatim phrases to `community-signal-import.md`, or relax the import_doc assertions), then proceed to implementation.
